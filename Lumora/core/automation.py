"""
LUMORA Automation Engine

Handles system automation including:
- Keyboard and mouse simulation
- Window management
- Application control
- File system operations
- Clipboard management
"""

import asyncio
import logging
import time
import ctypes
import ctypes.wintypes
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import threading
import queue

class ActionType(Enum):
    """Types of automation actions."""
    KEYBOARD_INPUT = "keyboard_input"
    MOUSE_CLICK = "mouse_click"
    MOUSE_MOVE = "mouse_move"
    WINDOW_FOCUS = "window_focus"
    WINDOW_MINIMIZE = "window_minimize"
    WINDOW_MAXIMIZE = "window_maximize"
    WINDOW_CLOSE = "window_close"
    APP_LAUNCH = "app_launch"
    APP_TERMINATE = "app_terminate"
    FILE_OPEN = "file_open"
    FILE_SAVE = "file_save"
    CLIPBOARD_COPY = "clipboard_copy"
    CLIPBOARD_PASTE = "clipboard_paste"
    SYSTEM_COMMAND = "system_command"
    NOTIFICATION = "notification"
    WAIT = "wait"

class ActionStatus(Enum):
    """Status of automation actions."""
    PENDING = "pending"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REQUIRES_CONFIRMATION = "requires_confirmation"

@dataclass
class AutomationAction:
    """Represents an automation action to be executed."""
    id: str
    action_type: ActionType
    parameters: Dict[str, Any]
    status: ActionStatus = ActionStatus.PENDING
    risk_level: int = 1  # 1-5 scale
    created_at: float = 0.0
    executed_at: Optional[float] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    requires_confirmation: bool = False
    
    def __post_init__(self):
        if self.created_at == 0.0:
            self.created_at = time.time()

class AutomationEngine:
    """
    Automation engine for Lumora that safely executes system actions
    based on AI decisions and user preferences.
    """
    
    def __init__(self, config_manager, context_manager):
        self.config = config_manager
        self.context = context_manager
        self.logger = logging.getLogger(__name__)
        
        # Action queue and processing
        self.action_queue = queue.Queue()
        self.confirmation_queue = queue.Queue()
        self.executing_actions = {}
        self.action_history = []
        self.max_history = 1000
        
        # Safety and control
        self.enabled = True
        self.emergency_stop = False
        self.max_concurrent_actions = 3
        self.action_timeout = 30.0
        
        # Event handlers
        self.on_action_completed: Optional[Callable] = None
        self.on_action_failed: Optional[Callable] = None
        self.on_confirmation_required: Optional[Callable] = None
        
        # Windows API
        self.user32 = ctypes.windll.user32
        self.kernel32 = ctypes.windll.kernel32
        
        # Worker thread
        self.worker_thread = None
        self.stop_worker = False
        
        # Performance tracking
        self.stats = {
            'total_actions': 0,
            'successful_actions': 0,
            'failed_actions': 0,
            'actions_by_type': {},
            'avg_execution_time': 0.0
        }
    
    async def initialize(self):
        """Initialize the automation engine."""
        try:
            self.logger.info("Initializing Automation Engine...")
            
            # Start worker thread
            self.worker_thread = threading.Thread(
                target=self._worker_loop,
                daemon=True
            )
            self.worker_thread.start()
            
            self.logger.info("Automation Engine initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Automation Engine: {e}")
            return False
    
    def _worker_loop(self):
        """Main worker loop for processing actions."""
        while not self.stop_worker:
            try:
                # Process pending actions
                self._process_action_queue()
                
                # Check for timeouts
                self._check_action_timeouts()
                
                # Brief sleep to prevent busy waiting
                time.sleep(0.1)
                
            except Exception as e:
                self.logger.error(f"Worker loop error: {e}")
                time.sleep(1)  # Error recovery
    
    def _process_action_queue(self):
        """Process actions from the queue."""
        while not self.action_queue.empty() and len(self.executing_actions) < self.max_concurrent_actions:
            try:
                action = self.action_queue.get_nowait()
                
                if self._should_execute_action(action):
                    self._execute_action_async(action)
                else:
                    action.status = ActionStatus.CANCELLED
                    self._complete_action(action)
                    
            except queue.Empty:
                break
            except Exception as e:
                self.logger.error(f"Error processing action queue: {e}")
    
    def _should_execute_action(self, action: AutomationAction) -> bool:
        """Determine if action should be executed."""
        if not self.enabled or self.emergency_stop:
            return False
        
        # Check risk level
        max_risk = self.config.get('automation.max_risk_level', 3)
        if action.risk_level > max_risk:
            action.status = ActionStatus.REQUIRES_CONFIRMATION
            self.confirmation_queue.put(action)
            if self.on_confirmation_required:
                self.on_confirmation_required(action)
            return False
        
        # Check system state
        if self._is_system_busy():
            return False
        
        return True
    
    def _is_system_busy(self) -> bool:
        """Check if system is too busy for automation."""
        try:
            import psutil
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory_percent = psutil.virtual_memory().percent
            
            # Don't automate during high system load
            if cpu_percent > 80 or memory_percent > 90:
                return True
            
            # Check if user is actively typing
            if self.context and self.context.get_activity_level() > 0.8:
                return True
                
        except:
            pass
        
        return False
    
    def _execute_action_async(self, action: AutomationAction):
        """Execute action asynchronously."""
        action.status = ActionStatus.EXECUTING
        action.executed_at = time.time()
        self.executing_actions[action.id] = action
        
        # Execute in thread pool to avoid blocking
        execution_thread = threading.Thread(
            target=self._execute_action_impl,
            args=(action,),
            daemon=True
        )
        execution_thread.start()
    
    def _execute_action_impl(self, action: AutomationAction):
        """Execute action implementation."""
        start_time = time.time()
        
        try:
            self.logger.debug(f"Executing action {action.id}: {action.action_type.value}")
            
            if action.action_type == ActionType.KEYBOARD_INPUT:
                self._execute_keyboard_input(action)
            elif action.action_type == ActionType.MOUSE_CLICK:
                self._execute_mouse_click(action)
            elif action.action_type == ActionType.MOUSE_MOVE:
                self._execute_mouse_move(action)
            elif action.action_type == ActionType.WINDOW_FOCUS:
                self._execute_window_focus(action)
            elif action.action_type == ActionType.WINDOW_MINIMIZE:
                self._execute_window_minimize(action)
            elif action.action_type == ActionType.WINDOW_MAXIMIZE:
                self._execute_window_maximize(action)
            elif action.action_type == ActionType.WINDOW_CLOSE:
                self._execute_window_close(action)
            elif action.action_type == ActionType.APP_LAUNCH:
                self._execute_app_launch(action)
            elif action.action_type == ActionType.APP_TERMINATE:
                self._execute_app_terminate(action)
            elif action.action_type == ActionType.FILE_OPEN:
                self._execute_file_open(action)
            elif action.action_type == ActionType.CLIPBOARD_COPY:
                self._execute_clipboard_copy(action)
            elif action.action_type == ActionType.CLIPBOARD_PASTE:
                self._execute_clipboard_paste(action)
            elif action.action_type == ActionType.SYSTEM_COMMAND:
                self._execute_system_command(action)
            elif action.action_type == ActionType.NOTIFICATION:
                self._execute_notification(action)
            elif action.action_type == ActionType.WAIT:
                self._execute_wait(action)
            else:
                raise ValueError(f"Unknown action type: {action.action_type}")
            
            action.status = ActionStatus.COMPLETED
            execution_time = time.time() - start_time
            self._update_stats(action, execution_time, success=True)
            
        except Exception as e:
            action.status = ActionStatus.FAILED
            action.error_message = str(e)
            execution_time = time.time() - start_time
            self._update_stats(action, execution_time, success=False)
            
            # Retry logic
            if action.retry_count < action.max_retries:
                action.retry_count += 1
                action.status = ActionStatus.PENDING
                time.sleep(1)  # Brief delay before retry
                self.action_queue.put(action)
                return
            
            self.logger.error(f"Action {action.id} failed: {e}")
            
        finally:
            self._complete_action(action)
    
    def _complete_action(self, action: AutomationAction):
        """Complete action processing."""
        # Remove from executing actions
        self.executing_actions.pop(action.id, None)
        
        # Add to history
        self.action_history.append(action)
        if len(self.action_history) > self.max_history:
            self.action_history.pop(0)
        
        # Notify handlers
        if action.status == ActionStatus.COMPLETED and self.on_action_completed:
            self.on_action_completed(action)
        elif action.status == ActionStatus.FAILED and self.on_action_failed:
            self.on_action_failed(action)
    
    def _check_action_timeouts(self):
        """Check for and handle action timeouts."""
        current_time = time.time()
        
        for action_id, action in list(self.executing_actions.items()):
            if current_time - action.executed_at > self.action_timeout:
                action.status = ActionStatus.FAILED
                action.error_message = "Action timed out"
                self._complete_action(action)
                self.logger.warning(f"Action {action_id} timed out")
    
    # Action execution methods
    def _execute_keyboard_input(self, action: AutomationAction):
        """Execute keyboard input action."""
        text = action.parameters.get('text', '')
        keys = action.parameters.get('keys', [])
        
        if text:
            # Type text
            for char in text:
                self._send_key_input(ord(char))
                time.sleep(0.01)  # Small delay between characters
        
        if keys:
            # Send special keys
            for key in keys:
                vk_code = self._get_virtual_key_code(key)
                if vk_code:
                    self._send_key_input(vk_code)
                    time.sleep(0.05)
    
    def _execute_mouse_click(self, action: AutomationAction):
        """Execute mouse click action."""
        x = action.parameters.get('x', 0)
        y = action.parameters.get('y', 0)
        button = action.parameters.get('button', 'left')
        double_click = action.parameters.get('double_click', False)
        
        # Move to position
        self.user32.SetCursorPos(x, y)
        time.sleep(0.1)
        
        # Perform click
        if button == 'left':
            self.user32.mouse_event(0x0002, 0, 0, 0, 0)  # LEFTDOWN
            time.sleep(0.05)
            self.user32.mouse_event(0x0004, 0, 0, 0, 0)  # LEFTUP
            
            if double_click:
                time.sleep(0.05)
                self.user32.mouse_event(0x0002, 0, 0, 0, 0)  # LEFTDOWN
                time.sleep(0.05)
                self.user32.mouse_event(0x0004, 0, 0, 0, 0)  # LEFTUP
                
        elif button == 'right':
            self.user32.mouse_event(0x0008, 0, 0, 0, 0)  # RIGHTDOWN
            time.sleep(0.05)
            self.user32.mouse_event(0x0010, 0, 0, 0, 0)  # RIGHTUP
    
    def _execute_mouse_move(self, action: AutomationAction):
        """Execute mouse move action."""
        x = action.parameters.get('x', 0)
        y = action.parameters.get('y', 0)
        smooth = action.parameters.get('smooth', True)
        
        if smooth:
            # Smooth movement
            current_x, current_y = self._get_cursor_position()
            steps = 20
            for i in range(steps + 1):
                new_x = current_x + (x - current_x) * i / steps
                new_y = current_y + (y - current_y) * i / steps
                self.user32.SetCursorPos(int(new_x), int(new_y))
                time.sleep(0.01)
        else:
            # Direct movement
            self.user32.SetCursorPos(x, y)
    
    def _execute_window_focus(self, action: AutomationAction):
        """Execute window focus action."""
        window_title = action.parameters.get('window_title', '')
        process_name = action.parameters.get('process_name', '')
        window_handle = action.parameters.get('window_handle', 0)
        
        hwnd = None
        
        if window_handle:
            hwnd = window_handle
        elif window_title:
            hwnd = self.user32.FindWindowW(None, window_title)
        elif process_name:
            # Find window by process name
            hwnd = self._find_window_by_process(process_name)
        
        if hwnd:
            self.user32.SetForegroundWindow(hwnd)
            self.user32.ShowWindow(hwnd, 9)  # SW_RESTORE
        else:
            raise Exception(f"Window not found: title='{window_title}', process='{process_name}'")
    
    def _execute_window_minimize(self, action: AutomationAction):
        """Execute window minimize action."""
        hwnd = self._get_window_handle(action.parameters)
        if hwnd:
            self.user32.ShowWindow(hwnd, 6)  # SW_MINIMIZE
    
    def _execute_window_maximize(self, action: AutomationAction):
        """Execute window maximize action."""
        hwnd = self._get_window_handle(action.parameters)
        if hwnd:
            self.user32.ShowWindow(hwnd, 3)  # SW_MAXIMIZE
    
    def _execute_window_close(self, action: AutomationAction):
        """Execute window close action."""
        hwnd = self._get_window_handle(action.parameters)
        if hwnd:
            self.user32.PostMessageW(hwnd, 0x0010, 0, 0)  # WM_CLOSE
    
    def _execute_app_launch(self, action: AutomationAction):
        """Execute application launch action."""
        app_path = action.parameters.get('app_path', '')
        arguments = action.parameters.get('arguments', '')
        working_dir = action.parameters.get('working_dir', '')
        
        import subprocess
        
        if not app_path:
            raise Exception("App path is required")
        
        # Launch application
        command = [app_path]
        if arguments:
            command.extend(arguments.split())
        
        process = subprocess.Popen(
            command,
            cwd=working_dir if working_dir else None,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait briefly to ensure it started
        time.sleep(2)
        
        if process.poll() is not None and process.returncode != 0:
            stderr = process.stderr.read().decode('utf-8', errors='ignore')
            raise Exception(f"Failed to launch app: {stderr}")
    
    def _execute_app_terminate(self, action: AutomationAction):
        """Execute application termination action."""
        process_name = action.parameters.get('process_name', '')
        process_id = action.parameters.get('process_id', 0)
        force = action.parameters.get('force', False)
        
        import psutil
        
        if process_id:
            try:
                process = psutil.Process(process_id)
                if force:
                    process.kill()
                else:
                    process.terminate()
            except psutil.NoSuchProcess:
                pass  # Process already gone
        elif process_name:
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'].lower() == process_name.lower():
                    try:
                        if force:
                            proc.kill()
                        else:
                            proc.terminate()
                    except psutil.NoSuchProcess:
                        pass
    
    def _execute_file_open(self, action: AutomationAction):
        """Execute file open action."""
        file_path = action.parameters.get('file_path', '')
        application = action.parameters.get('application', '')
        
        if not file_path:
            raise Exception("File path is required")
        
        import os
        
        if application:
            os.system(f'"{application}" "{file_path}"')
        else:
            os.startfile(file_path)  # Use default application
    
    def _execute_clipboard_copy(self, action: AutomationAction):
        """Execute clipboard copy action."""
        text = action.parameters.get('text', '')
        
        if not text:
            raise Exception("Text is required for clipboard copy")
        
        import win32clipboard
        
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardText(text)
        win32clipboard.CloseClipboard()
    
    def _execute_clipboard_paste(self, action: AutomationAction):
        """Execute clipboard paste action."""
        # Send Ctrl+V
        self._send_key_combination(['ctrl', 'v'])
    
    def _execute_system_command(self, action: AutomationAction):
        """Execute system command action."""
        command = action.parameters.get('command', '')
        shell = action.parameters.get('shell', True)
        capture_output = action.parameters.get('capture_output', True)
        
        if not command:
            raise Exception("Command is required")
        
        import subprocess
        
        result = subprocess.run(
            command,
            shell=shell,
            capture_output=capture_output,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            raise Exception(f"Command failed with code {result.returncode}: {result.stderr}")
        
        action.parameters['output'] = result.stdout
    
    def _execute_notification(self, action: AutomationAction):
        """Execute notification action."""
        title = action.parameters.get('title', 'Lumora')
        message = action.parameters.get('message', '')
        duration = action.parameters.get('duration', 5000)
        
        # Use Windows toast notification
        try:
            import win10toast
            toaster = win10toast.ToastNotifier()
            toaster.show_toast(title, message, duration=duration)
        except ImportError:
            # Fallback to message box
            self.user32.MessageBoxW(0, message, title, 0x40)  # MB_ICONINFORMATION
    
    def _execute_wait(self, action: AutomationAction):
        """Execute wait action."""
        duration = action.parameters.get('duration', 1.0)
        time.sleep(duration)
    
    # Helper methods
    def _send_key_input(self, vk_code: int):
        """Send a key input."""
        self.user32.keybd_event(vk_code, 0, 0, 0)  # Key down
        time.sleep(0.01)
        self.user32.keybd_event(vk_code, 0, 0x0002, 0)  # Key up
    
    def _send_key_combination(self, keys: List[str]):
        """Send key combination (e.g., Ctrl+C)."""
        vk_codes = [self._get_virtual_key_code(key) for key in keys]
        
        # Press all keys down
        for vk_code in vk_codes:
            if vk_code:
                self.user32.keybd_event(vk_code, 0, 0, 0)
                time.sleep(0.01)
        
        # Release all keys
        for vk_code in reversed(vk_codes):
            if vk_code:
                self.user32.keybd_event(vk_code, 0, 0x0002, 0)
                time.sleep(0.01)
    
    def _get_virtual_key_code(self, key: str) -> int:
        """Get virtual key code for key name."""
        key_codes = {
            'ctrl': 0x11, 'alt': 0x12, 'shift': 0x10,
            'enter': 0x0D, 'space': 0x20, 'tab': 0x09,
            'escape': 0x1B, 'backspace': 0x08, 'delete': 0x2E,
            'home': 0x24, 'end': 0x23, 'pageup': 0x21, 'pagedown': 0x22,
            'left': 0x25, 'up': 0x26, 'right': 0x27, 'down': 0x28,
            'f1': 0x70, 'f2': 0x71, 'f3': 0x72, 'f4': 0x73,
            'f5': 0x74, 'f6': 0x75, 'f7': 0x76, 'f8': 0x77,
            'f9': 0x78, 'f10': 0x79, 'f11': 0x7A, 'f12': 0x7B,
            'a': 0x41, 'b': 0x42, 'c': 0x43, 'd': 0x44,
            'e': 0x45, 'f': 0x46, 'g': 0x47, 'h': 0x48,
            'i': 0x49, 'j': 0x4A, 'k': 0x4B, 'l': 0x4C,
            'm': 0x4D, 'n': 0x4E, 'o': 0x4F, 'p': 0x50,
            'q': 0x51, 'r': 0x52, 's': 0x53, 't': 0x54,
            'u': 0x55, 'v': 0x56, 'w': 0x57, 'x': 0x58,
            'y': 0x59, 'z': 0x5A
        }
        
        return key_codes.get(key.lower(), 0)
    
    def _get_cursor_position(self) -> tuple:
        """Get current cursor position."""
        point = ctypes.wintypes.POINT()
        self.user32.GetCursorPos(ctypes.byref(point))
        return point.x, point.y
    
    def _get_window_handle(self, parameters: Dict[str, Any]) -> int:
        """Get window handle from parameters."""
        window_handle = parameters.get('window_handle', 0)
        if window_handle:
            return window_handle
        
        window_title = parameters.get('window_title', '')
        if window_title:
            return self.user32.FindWindowW(None, window_title)
        
        process_name = parameters.get('process_name', '')
        if process_name:
            return self._find_window_by_process(process_name)
        
        # Default to foreground window
        return self.user32.GetForegroundWindow()
    
    def _find_window_by_process(self, process_name: str) -> int:
        """Find window by process name."""
        import psutil
        
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'].lower() == process_name.lower():
                # Find window for this process
                def enum_windows_callback(hwnd, windows):
                    pid = ctypes.wintypes.DWORD()
                    self.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
                    if pid.value == proc.info['pid']:
                        windows.append(hwnd)
                    return True
                
                windows = []
                enum_proc = ctypes.WINFUNCTYPE(
                    ctypes.wintypes.BOOL,
                    ctypes.wintypes.HWND,
                    ctypes.wintypes.LPARAM
                )(enum_windows_callback)
                
                self.user32.EnumWindows(enum_proc, windows)
                
                if windows:
                    return windows[0]
        
        return 0
    
    def _update_stats(self, action: AutomationAction, execution_time: float, success: bool):
        """Update performance statistics."""
        self.stats['total_actions'] += 1
        
        if success:
            self.stats['successful_actions'] += 1
        else:
            self.stats['failed_actions'] += 1
        
        action_type = action.action_type.value
        if action_type not in self.stats['actions_by_type']:
            self.stats['actions_by_type'][action_type] = {'count': 0, 'avg_time': 0.0}
        
        type_stats = self.stats['actions_by_type'][action_type]
        type_stats['count'] += 1
        type_stats['avg_time'] = (type_stats['avg_time'] * (type_stats['count'] - 1) + execution_time) / type_stats['count']
        
        # Update overall average
        total_time = self.stats['avg_execution_time'] * (self.stats['total_actions'] - 1) + execution_time
        self.stats['avg_execution_time'] = total_time / self.stats['total_actions']
    
    # Public interface
    async def execute_action(self, action: Dict[str, Any]) -> str:
        """Queue an action for execution."""
        if not self.enabled:
            raise Exception("Automation engine is disabled")
        
        # Create action object
        automation_action = AutomationAction(
            id=f"action_{int(time.time() * 1000)}_{len(self.action_history)}",
            action_type=ActionType(action['type']),
            parameters=action.get('parameters', {}),
            risk_level=action.get('risk_level', 1),
            requires_confirmation=action.get('requires_confirmation', False)
        )
        
        # Add to queue
        self.action_queue.put(automation_action)
        
        self.logger.info(f"Queued action {automation_action.id}: {automation_action.action_type.value}")
        return automation_action.id
    
    async def queue_for_confirmation(self, action_request: Dict[str, Any]) -> str:
        """Queue action for user confirmation."""
        automation_action = AutomationAction(
            id=f"confirm_{int(time.time() * 1000)}",
            action_type=ActionType(action_request['type']),
            parameters=action_request.get('parameters', {}),
            status=ActionStatus.REQUIRES_CONFIRMATION,
            risk_level=action_request.get('risk_level', 3),
            requires_confirmation=True
        )
        
        self.confirmation_queue.put(automation_action)
        
        if self.on_confirmation_required:
            self.on_confirmation_required(automation_action)
        
        return automation_action.id
    
    async def confirm_action(self, action_id: str, approved: bool) -> bool:
        """Confirm or reject a pending action."""
        # Find action in confirmation queue
        confirmed_action = None
        temp_queue = queue.Queue()
        
        while not self.confirmation_queue.empty():
            action = self.confirmation_queue.get()
            if action.id == action_id:
                confirmed_action = action
                break
            else:
                temp_queue.put(action)
        
        # Put remaining actions back
        while not temp_queue.empty():
            self.confirmation_queue.put(temp_queue.get())
        
        if confirmed_action:
            if approved:
                confirmed_action.status = ActionStatus.PENDING
                confirmed_action.requires_confirmation = False
                self.action_queue.put(confirmed_action)
                return True
            else:
                confirmed_action.status = ActionStatus.CANCELLED
                self._complete_action(confirmed_action)
                return True
        
        return False
    
    async def cancel_action(self, action_id: str) -> bool:
        """Cancel a pending or executing action."""
        # Check executing actions
        if action_id in self.executing_actions:
            action = self.executing_actions[action_id]
            action.status = ActionStatus.CANCELLED
            self._complete_action(action)
            return True
        
        # Check action queue (more complex for thread-safe queue)
        # For simplicity, we'll let it execute and check cancellation status
        return False
    
    def get_action_status(self, action_id: str) -> Optional[ActionStatus]:
        """Get status of an action."""
        # Check executing actions
        if action_id in self.executing_actions:
            return self.executing_actions[action_id].status
        
        # Check history
        for action in reversed(self.action_history):
            if action.id == action_id:
                return action.status
        
        return None
    
    def get_last_action(self) -> Optional[str]:
        """Get description of last action performed."""
        if self.action_history:
            last_action = self.action_history[-1]
            return f"{last_action.action_type.value} ({last_action.status.value})"
        return None
    
    def has_pending_actions(self) -> bool:
        """Check if there are pending actions."""
        return not self.action_queue.empty() or len(self.executing_actions) > 0
    
    def enable_automation(self):
        """Enable automation engine."""
        self.enabled = True
        self.emergency_stop = False
        self.logger.info("Automation engine enabled")
    
    def disable_automation(self):
        """Disable automation engine."""
        self.enabled = False
        self.logger.info("Automation engine disabled")
    
    def emergency_stop_all(self):
        """Emergency stop all automation."""
        self.emergency_stop = True
        self.enabled = False
        
        # Cancel all executing actions
        for action in self.executing_actions.values():
            action.status = ActionStatus.CANCELLED
        
        # Clear queues
        while not self.action_queue.empty():
            try:
                action = self.action_queue.get_nowait()
                action.status = ActionStatus.CANCELLED
                self._complete_action(action)
            except queue.Empty:
                break
        
        self.logger.warning("EMERGENCY STOP: All automation halted")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get automation statistics."""
        return self.stats.copy()
    
    async def on_app_switch(self, from_app: str, to_app: str):
        """Handle application switch events."""
        # Could trigger app-specific automations
        pass
    
    async def shutdown(self):
        """Shutdown automation engine."""
        self.logger.info("Shutting down Automation Engine...")
        
        # Stop worker thread
        self.stop_worker = True
        if self.worker_thread and self.worker_thread.is_alive():
            self.worker_thread.join(timeout=5)
        
        # Cancel all pending actions
        self.emergency_stop_all()
        
        self.logger.info("Automation Engine shutdown complete")
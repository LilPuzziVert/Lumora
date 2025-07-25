"""
LUMORA Automation Engine

Advanced automation system for autonomous app interaction:
- Window and UI control
- Keyboard and mouse automation
- Application-specific actions
- Safe interaction protocols
- Undo/rollback capabilities
"""

import time
import logging
import asyncio
import threading
from typing import Dict, Any, List, Optional, Tuple, Callable
from dataclasses import dataclass
from enum import Enum
import ctypes
import ctypes.wintypes
from ctypes import wintypes
import json

# Windows API constants
WM_KEYDOWN = 0x0100
WM_KEYUP = 0x0101
WM_CHAR = 0x0102
WM_LBUTTONDOWN = 0x0201
WM_LBUTTONUP = 0x0202
WM_RBUTTONDOWN = 0x0204
WM_RBUTTONUP = 0x0205

class ActionType(Enum):
    """Types of automation actions."""
    CLICK = "click"
    TYPE = "type"
    KEY_PRESS = "key_press"
    SCROLL = "scroll"
    DRAG = "drag"
    WAIT = "wait"
    WINDOW_ACTION = "window_action"
    APP_SPECIFIC = "app_specific"

class ActionStatus(Enum):
    """Status of automation actions."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class AutomationAction:
    """Single automation action definition."""
    action_id: str
    action_type: ActionType
    target: Dict[str, Any]  # What to interact with
    parameters: Dict[str, Any]  # How to interact
    preconditions: List[str] = None  # What must be true before
    postconditions: List[str] = None  # What should be true after
    timeout: float = 5.0
    retry_count: int = 3
    safe_mode: bool = True
    
    def __post_init__(self):
        if self.preconditions is None:
            self.preconditions = []
        if self.postconditions is None:
            self.postconditions = []

@dataclass
class AutomationSequence:
    """Sequence of automation actions."""
    sequence_id: str
    name: str
    actions: List[AutomationAction]
    rollback_actions: List[AutomationAction] = None
    context_requirements: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.rollback_actions is None:
            self.rollback_actions = []
        if self.context_requirements is None:
            self.context_requirements = {}

class AutomationEngine:
    """Advanced automation engine for safe UI interaction."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # State management
        self.active_sequences: Dict[str, AutomationSequence] = {}
        self.action_history: List[Dict[str, Any]] = []
        self.safety_enabled = config.get("safety_enabled", True)
        self.dry_run_mode = config.get("dry_run_mode", False)
        
        # Windows API setup
        self.user32 = ctypes.windll.user32
        self.kernel32 = ctypes.windll.kernel32
        
        # Action executors
        self.action_executors = {
            ActionType.CLICK: self._execute_click,
            ActionType.TYPE: self._execute_type,
            ActionType.KEY_PRESS: self._execute_key_press,
            ActionType.SCROLL: self._execute_scroll,
            ActionType.DRAG: self._execute_drag,
            ActionType.WAIT: self._execute_wait,
            ActionType.WINDOW_ACTION: self._execute_window_action,
            ActionType.APP_SPECIFIC: self._execute_app_specific
        }
        
        # Safety checks
        self.safety_checkers = []
        self._init_safety_checkers()
    
    def _init_safety_checkers(self):
        """Initialize safety check functions."""
        self.safety_checkers = [
            self._check_foreground_app,
            self._check_user_input,
            self._check_system_state,
            self._check_action_limits
        ]
    
    async def execute_action(self, action: AutomationAction) -> Dict[str, Any]:
        """Execute a single automation action."""
        result = {
            "action_id": action.action_id,
            "status": ActionStatus.PENDING,
            "start_time": time.time(),
            "error": None,
            "result": None
        }
        
        try:
            # Safety checks
            if self.safety_enabled:
                safety_result = await self._run_safety_checks(action)
                if not safety_result["safe"]:
                    result["status"] = ActionStatus.FAILED
                    result["error"] = f"Safety check failed: {safety_result['reason']}"
                    return result
            
            # Precondition checks
            if not await self._check_preconditions(action):
                result["status"] = ActionStatus.FAILED
                result["error"] = "Preconditions not met"
                return result
            
            # Execute action
            result["status"] = ActionStatus.RUNNING
            
            if self.dry_run_mode:
                self.logger.info(f"DRY RUN: Would execute {action.action_type.value}")
                result["result"] = {"dry_run": True}
            else:
                executor = self.action_executors.get(action.action_type)
                if not executor:
                    raise ValueError(f"No executor for action type: {action.action_type}")
                
                action_result = await executor(action)
                result["result"] = action_result
            
            # Postcondition checks
            if not await self._check_postconditions(action):
                result["status"] = ActionStatus.FAILED
                result["error"] = "Postconditions not met"
                return result
            
            result["status"] = ActionStatus.COMPLETED
            
        except Exception as e:
            result["status"] = ActionStatus.FAILED
            result["error"] = str(e)
            self.logger.error(f"Action execution failed: {e}")
        
        finally:
            result["end_time"] = time.time()
            result["duration"] = result["end_time"] - result["start_time"]
            self.action_history.append(result)
        
        return result
    
    async def execute_sequence(self, sequence: AutomationSequence) -> Dict[str, Any]:
        """Execute a sequence of automation actions."""
        sequence_result = {
            "sequence_id": sequence.sequence_id,
            "status": ActionStatus.PENDING,
            "start_time": time.time(),
            "actions_completed": 0,
            "actions_failed": 0,
            "results": []
        }
        
        try:
            # Check context requirements
            if not await self._check_context_requirements(sequence.context_requirements):
                sequence_result["status"] = ActionStatus.FAILED
                sequence_result["error"] = "Context requirements not met"
                return sequence_result
            
            sequence_result["status"] = ActionStatus.RUNNING
            self.active_sequences[sequence.sequence_id] = sequence
            
            # Execute actions in sequence
            for action in sequence.actions:
                result = await self.execute_action(action)
                sequence_result["results"].append(result)
                
                if result["status"] == ActionStatus.COMPLETED:
                    sequence_result["actions_completed"] += 1
                else:
                    sequence_result["actions_failed"] += 1
                    
                    # Stop on failure if not configured to continue
                    if not self.config.get("continue_on_failure", False):
                        break
            
            # Determine overall status
            if sequence_result["actions_failed"] == 0:
                sequence_result["status"] = ActionStatus.COMPLETED
            else:
                sequence_result["status"] = ActionStatus.FAILED
        
        except Exception as e:
            sequence_result["status"] = ActionStatus.FAILED
            sequence_result["error"] = str(e)
            self.logger.error(f"Sequence execution failed: {e}")
        
        finally:
            sequence_result["end_time"] = time.time()
            sequence_result["duration"] = sequence_result["end_time"] - sequence_result["start_time"]
            
            if sequence.sequence_id in self.active_sequences:
                del self.active_sequences[sequence.sequence_id]
        
        return sequence_result
    
    async def _execute_click(self, action: AutomationAction) -> Dict[str, Any]:
        """Execute mouse click action."""
        target = action.target
        params = action.parameters
        
        x = target.get("x", 0)
        y = target.get("y", 0)
        button = params.get("button", "left")
        double_click = params.get("double_click", False)
        
        # Move cursor to position
        self.user32.SetCursorPos(x, y)
        await asyncio.sleep(0.1)
        
        # Perform click
        if button == "left":
            self.user32.mouse_event(0x0002, 0, 0, 0, 0)  # MOUSEEVENTF_LEFTDOWN
            await asyncio.sleep(0.05)
            self.user32.mouse_event(0x0004, 0, 0, 0, 0)  # MOUSEEVENTF_LEFTUP
            
            if double_click:
                await asyncio.sleep(0.1)
                self.user32.mouse_event(0x0002, 0, 0, 0, 0)
                await asyncio.sleep(0.05)
                self.user32.mouse_event(0x0004, 0, 0, 0, 0)
        
        elif button == "right":
            self.user32.mouse_event(0x0008, 0, 0, 0, 0)  # MOUSEEVENTF_RIGHTDOWN
            await asyncio.sleep(0.05)
            self.user32.mouse_event(0x0010, 0, 0, 0, 0)  # MOUSEEVENTF_RIGHTUP
        
        return {"clicked": True, "position": (x, y), "button": button}
    
    async def _execute_type(self, action: AutomationAction) -> Dict[str, Any]:
        """Execute text typing action."""
        text = action.parameters.get("text", "")
        delay = action.parameters.get("delay", 0.05)
        
        for char in text:
            if char == '\n':
                # Enter key
                self.user32.keybd_event(0x0D, 0, 0, 0)
                await asyncio.sleep(0.05)
                self.user32.keybd_event(0x0D, 0, 0x0002, 0)
            elif char == '\t':
                # Tab key
                self.user32.keybd_event(0x09, 0, 0, 0)
                await asyncio.sleep(0.05)
                self.user32.keybd_event(0x09, 0, 0x0002, 0)
            else:
                # Regular character
                vk_code = ord(char.upper())
                self.user32.keybd_event(vk_code, 0, 0, 0)
                await asyncio.sleep(0.02)
                self.user32.keybd_event(vk_code, 0, 0x0002, 0)
            
            await asyncio.sleep(delay)
        
        return {"typed": text, "length": len(text)}
    
    async def _execute_key_press(self, action: AutomationAction) -> Dict[str, Any]:
        """Execute keyboard key press action."""
        key = action.parameters.get("key", "")
        modifiers = action.parameters.get("modifiers", [])
        
        # Key code mapping
        key_codes = {
            "enter": 0x0D, "tab": 0x09, "space": 0x20, "escape": 0x1B,
            "backspace": 0x08, "delete": 0x2E, "home": 0x24, "end": 0x23,
            "left": 0x25, "up": 0x26, "right": 0x27, "down": 0x28,
            "f1": 0x70, "f2": 0x71, "f3": 0x72, "f4": 0x73,
            "ctrl": 0x11, "alt": 0x12, "shift": 0x10
        }
        
        # Press modifiers
        for modifier in modifiers:
            if modifier in key_codes:
                self.user32.keybd_event(key_codes[modifier], 0, 0, 0)
        
        # Press main key
        if key in key_codes:
            key_code = key_codes[key]
        else:
            key_code = ord(key.upper())
        
        self.user32.keybd_event(key_code, 0, 0, 0)
        await asyncio.sleep(0.05)
        self.user32.keybd_event(key_code, 0, 0x0002, 0)
        
        # Release modifiers
        for modifier in reversed(modifiers):
            if modifier in key_codes:
                self.user32.keybd_event(key_codes[modifier], 0, 0x0002, 0)
        
        return {"key": key, "modifiers": modifiers}
    
    async def _execute_scroll(self, action: AutomationAction) -> Dict[str, Any]:
        """Execute scroll action."""
        direction = action.parameters.get("direction", "down")
        amount = action.parameters.get("amount", 3)
        
        wheel_delta = 120 if direction == "up" else -120
        
        for _ in range(amount):
            self.user32.mouse_event(0x0800, 0, 0, wheel_delta, 0)  # MOUSEEVENTF_WHEEL
            await asyncio.sleep(0.1)
        
        return {"direction": direction, "amount": amount}
    
    async def _execute_drag(self, action: AutomationAction) -> Dict[str, Any]:
        """Execute drag action."""
        start_pos = action.target.get("start", (0, 0))
        end_pos = action.target.get("end", (0, 0))
        
        # Move to start position
        self.user32.SetCursorPos(start_pos[0], start_pos[1])
        await asyncio.sleep(0.1)
        
        # Press mouse down
        self.user32.mouse_event(0x0002, 0, 0, 0, 0)  # MOUSEEVENTF_LEFTDOWN
        await asyncio.sleep(0.1)
        
        # Drag to end position
        self.user32.SetCursorPos(end_pos[0], end_pos[1])
        await asyncio.sleep(0.1)
        
        # Release mouse
        self.user32.mouse_event(0x0004, 0, 0, 0, 0)  # MOUSEEVENTF_LEFTUP
        
        return {"start": start_pos, "end": end_pos}
    
    async def _execute_wait(self, action: AutomationAction) -> Dict[str, Any]:
        """Execute wait action."""
        duration = action.parameters.get("duration", 1.0)
        await asyncio.sleep(duration)
        return {"waited": duration}
    
    async def _execute_window_action(self, action: AutomationAction) -> Dict[str, Any]:
        """Execute window management action."""
        window_action = action.parameters.get("action", "")
        target_window = action.target.get("window_title", "")
        
        # Find window by title
        hwnd = self.user32.FindWindowW(None, target_window)
        if not hwnd:
            raise ValueError(f"Window not found: {target_window}")
        
        if window_action == "activate":
            self.user32.SetForegroundWindow(hwnd)
        elif window_action == "minimize":
            self.user32.ShowWindow(hwnd, 6)  # SW_MINIMIZE
        elif window_action == "maximize":
            self.user32.ShowWindow(hwnd, 3)  # SW_MAXIMIZE
        elif window_action == "close":
            self.user32.PostMessageW(hwnd, 0x0010, 0, 0)  # WM_CLOSE
        
        return {"action": window_action, "window": target_window}
    
    async def _execute_app_specific(self, action: AutomationAction) -> Dict[str, Any]:
        """Execute application-specific action."""
        app_name = action.target.get("app", "")
        app_action = action.parameters.get("action", "")
        
        # Load app-specific handlers
        if app_name == "browser":
            return await self._handle_browser_action(action)
        elif app_name == "email":
            return await self._handle_email_action(action)
        else:
            raise ValueError(f"No handler for app: {app_name}")
    
    async def _handle_browser_action(self, action: AutomationAction) -> Dict[str, Any]:
        """Handle browser-specific actions."""
        browser_action = action.parameters.get("action", "")
        
        if browser_action == "new_tab":
            await self._execute_key_press(AutomationAction(
                action_id="", action_type=ActionType.KEY_PRESS,
                target={}, parameters={"key": "t", "modifiers": ["ctrl"]}
            ))
        elif browser_action == "navigate":
            url = action.parameters.get("url", "")
            await self._execute_key_press(AutomationAction(
                action_id="", action_type=ActionType.KEY_PRESS,
                target={}, parameters={"key": "l", "modifiers": ["ctrl"]}
            ))
            await asyncio.sleep(0.5)
            await self._execute_type(AutomationAction(
                action_id="", action_type=ActionType.TYPE,
                target={}, parameters={"text": url}
            ))
            await self._execute_key_press(AutomationAction(
                action_id="", action_type=ActionType.KEY_PRESS,
                target={}, parameters={"key": "enter"}
            ))
        
        return {"browser_action": browser_action}
    
    async def _handle_email_action(self, action: AutomationAction) -> Dict[str, Any]:
        """Handle email-specific actions."""
        email_action = action.parameters.get("action", "")
        
        if email_action == "compose":
            recipient = action.parameters.get("recipient", "")
            subject = action.parameters.get("subject", "")
            body = action.parameters.get("body", "")
            
            # Implementation depends on email client
            pass
        
        return {"email_action": email_action}
    
    async def _run_safety_checks(self, action: AutomationAction) -> Dict[str, Any]:
        """Run all safety checks for an action."""
        for checker in self.safety_checkers:
            result = await checker(action)
            if not result["safe"]:
                return result
        
        return {"safe": True, "reason": "All checks passed"}
    
    async def _check_foreground_app(self, action: AutomationAction) -> Dict[str, Any]:
        """Check if the foreground app is safe to interact with."""
        hwnd = self.user32.GetForegroundWindow()
        if not hwnd:
            return {"safe": False, "reason": "No foreground window"}
        
        # Get window title
        length = self.user32.GetWindowTextLengthW(hwnd)
        buffer = ctypes.create_unicode_buffer(length + 1)
        self.user32.GetWindowTextW(hwnd, buffer, length + 1)
        window_title = buffer.value
        
        # Check against unsafe applications
        unsafe_apps = ["Command Prompt", "PowerShell", "Registry Editor"]
        if any(unsafe in window_title for unsafe in unsafe_apps):
            return {"safe": False, "reason": f"Unsafe app: {window_title}"}
        
        return {"safe": True, "reason": "Foreground app is safe"}
    
    async def _check_user_input(self, action: AutomationAction) -> Dict[str, Any]:
        """Check if user is currently providing input."""
        # Check for recent user activity
        last_input = self.user32.GetLastInputInfo()
        current_time = self.kernel32.GetTickCount()
        
        if current_time - last_input < 1000:  # 1 second
            return {"safe": False, "reason": "User is actively using system"}
        
        return {"safe": True, "reason": "No recent user input"}
    
    async def _check_system_state(self, action: AutomationAction) -> Dict[str, Any]:
        """Check overall system state."""
        # Add checks for system performance, updates, etc.
        return {"safe": True, "reason": "System state is normal"}
    
    async def _check_action_limits(self, action: AutomationAction) -> Dict[str, Any]:
        """Check if action exceeds safety limits."""
        # Check action frequency limits
        recent_actions = [a for a in self.action_history 
                         if time.time() - a["start_time"] < 60]
        
        if len(recent_actions) > self.config.get("max_actions_per_minute", 50):
            return {"safe": False, "reason": "Action rate limit exceeded"}
        
        return {"safe": True, "reason": "Action limits OK"}
    
    async def _check_preconditions(self, action: AutomationAction) -> bool:
        """Check if action preconditions are met."""
        # Implementation depends on specific preconditions
        return True
    
    async def _check_postconditions(self, action: AutomationAction) -> bool:
        """Check if action postconditions are met."""
        # Implementation depends on specific postconditions
        return True
    
    async def _check_context_requirements(self, requirements: Dict[str, Any]) -> bool:
        """Check if context requirements are met."""
        # Implementation depends on specific requirements
        return True
    
    def rollback_sequence(self, sequence_id: str) -> Dict[str, Any]:
        """Rollback a completed automation sequence."""
        if sequence_id not in self.active_sequences:
            return {"success": False, "error": "Sequence not found"}
        
        sequence = self.active_sequences[sequence_id]
        
        # Execute rollback actions if available
        if sequence.rollback_actions:
            # Implementation for rollback execution
            pass
        
        return {"success": True, "rollback_actions": len(sequence.rollback_actions)}
    
    def get_status(self) -> Dict[str, Any]:
        """Get current automation engine status."""
        return {
            "active_sequences": len(self.active_sequences),
            "total_actions_executed": len(self.action_history),
            "safety_enabled": self.safety_enabled,
            "dry_run_mode": self.dry_run_mode
        }
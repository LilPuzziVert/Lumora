"""
LUMORA Context Manager

Handles all system monitoring including:
- Screen awareness and OCR
- Application monitoring
- Input tracking (keyboard/mouse)
- Window management
- System resource monitoring
"""

import asyncio
import time
import logging
import threading
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from enum import Enum
import ctypes
import ctypes.wintypes
from ctypes import wintypes

@dataclass
class AppInfo:
    """Information about a running application."""
    name: str
    title: str
    pid: int
    handle: int
    is_foreground: bool
    memory_usage: float
    cpu_usage: float
    window_rect: tuple
    is_visible: bool

@dataclass
class ScreenContent:
    """Screen content information."""
    timestamp: float
    ocr_text: str
    image_hash: str
    active_window: str
    regions: List[Dict[str, Any]] = field(default_factory=list)
    ui_elements: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class InputEvent:
    """Input event information."""
    timestamp: float
    event_type: str  # 'keyboard' or 'mouse'
    data: Dict[str, Any]
    
@dataclass
class SystemContext:
    """Complete system context snapshot."""
    timestamp: float
    active_app: AppInfo
    all_apps: List[AppInfo]
    screen_content: ScreenContent
    recent_inputs: List[InputEvent]
    system_stats: Dict[str, float]
    network_activity: Dict[str, Any]
    activity_level: float

class ContextManager:
    """
    Manages system-wide context monitoring and awareness.
    
    This is Lumora's eyes and ears into the system, providing
    real-time information about what's happening.
    """
    
    def __init__(self, config, privacy_guardian):
        self.config = config
        self.privacy = privacy_guardian
        self.logger = logging.getLogger(__name__)
        
        # Monitoring state
        self.is_monitoring = False
        self.is_paused = False
        self.monitoring_thread = None
        
        # Context tracking
        self.current_context = None
        self.context_history = []
        self.max_history = 100
        
        # Change detection
        self.last_active_window = None
        self.last_screen_hash = None
        self.last_input_time = 0
        self.changes_pending = False
        
        # Activity tracking
        self.activity_buffer = []
        self.activity_window_size = 60  # seconds
        
        # Event handlers
        self.on_context_change: Optional[Callable] = None
        self.on_app_switch: Optional[Callable] = None
        self.on_screen_change: Optional[Callable] = None
        self.on_input_activity: Optional[Callable] = None
        
        # Win32 API setup
        self._setup_win32_hooks()
        
        # OCR and screen capture
        self.ocr_engine = None
        self.screen_capturer = None
        
    def _setup_win32_hooks(self):
        """Setup Windows API hooks for system monitoring."""
        try:
            # Define constants
            self.WH_KEYBOARD_LL = 13
            self.WH_MOUSE_LL = 14
            self.WM_KEYDOWN = 0x0100
            self.WM_SYSKEYDOWN = 0x0104
            
            # Hook procedures
            self.keyboard_hook = None
            self.mouse_hook = None
            
            # Window tracking
            self.user32 = ctypes.windll.user32
            self.kernel32 = ctypes.windll.kernel32
            
        except Exception as e:
            self.logger.error(f"Failed to setup Win32 hooks: {e}")
    
    async def initialize(self):
        """Initialize the context manager."""
        try:
            self.logger.info("Initializing Context Manager...")
            
            # Initialize OCR engine
            await self._initialize_ocr()
            
            # Initialize screen capture
            await self._initialize_screen_capture()
            
            # Setup input hooks
            await self._setup_input_hooks()
            
            self.logger.info("Context Manager initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Context Manager: {e}")
            return False
    
    async def _initialize_ocr(self):
        """Initialize OCR engine for screen text recognition."""
        # Simple OCR implementation using Windows OCR API
        try:
            import winrt.windows.media.ocr as ocr
            import winrt.windows.graphics.imaging as imaging
            
            self.ocr_engine = ocr.OcrEngine.try_create_from_user_profile_languages()
            if not self.ocr_engine:
                # Fallback to English
                language = winrt.windows.globalization.Language("en-US")
                self.ocr_engine = ocr.OcrEngine.try_create_from_language(language)
                
        except Exception as e:
            self.logger.warning(f"OCR initialization failed, using fallback: {e}")
            self.ocr_engine = None
    
    async def _initialize_screen_capture(self):
        """Initialize screen capture capabilities."""
        try:
            # Use Windows Graphics Capture API
            self.screen_capturer = ScreenCapturer()
            await self.screen_capturer.initialize()
            
        except Exception as e:
            self.logger.error(f"Screen capture initialization failed: {e}")
            self.screen_capturer = None
    
    async def _setup_input_hooks(self):
        """Setup low-level input hooks."""
        if not self.privacy.is_input_monitoring_allowed():
            return
            
        try:
            # Keyboard hook
            self.keyboard_hook = self._install_keyboard_hook()
            
            # Mouse hook
            self.mouse_hook = self._install_mouse_hook()
            
        except Exception as e:
            self.logger.error(f"Input hook setup failed: {e}")
    
    def _install_keyboard_hook(self):
        """Install low-level keyboard hook."""
        def low_level_keyboard_proc(nCode, wParam, lParam):
            if nCode >= 0:
                if wParam in [self.WM_KEYDOWN, self.WM_SYSKEYDOWN]:
                    vk_code = ctypes.cast(lParam, ctypes.POINTER(ctypes.c_int)).contents.value
                    asyncio.create_task(self._handle_keyboard_input(vk_code))
            
            return self.user32.CallNextHookExW(self.keyboard_hook, nCode, wParam, lParam)
        
        # Convert to callable
        keyboard_proc = ctypes.WINFUNCTYPE(
            ctypes.c_int,
            ctypes.c_int,
            wintypes.WPARAM,
            wintypes.LPARAM
        )(low_level_keyboard_proc)
        
        # Install hook
        hook = self.user32.SetWindowsHookExW(
            self.WH_KEYBOARD_LL,
            keyboard_proc,
            self.kernel32.GetModuleHandleW(None),
            0
        )
        
        return hook
    
    def _install_mouse_hook(self):
        """Install low-level mouse hook."""
        def low_level_mouse_proc(nCode, wParam, lParam):
            if nCode >= 0:
                asyncio.create_task(self._handle_mouse_input(wParam, lParam))
            
            return self.user32.CallNextHookExW(self.mouse_hook, nCode, wParam, lParam)
        
        # Convert to callable
        mouse_proc = ctypes.WINFUNCTYPE(
            ctypes.c_int,
            ctypes.c_int,
            wintypes.WPARAM,
            wintypes.LPARAM
        )(low_level_mouse_proc)
        
        # Install hook
        hook = self.user32.SetWindowsHookExW(
            self.WH_MOUSE_LL,
            mouse_proc,
            self.kernel32.GetModuleHandleW(None),
            0
        )
        
        return hook
    
    async def start_monitoring(self, interactive=False, minimal=False):
        """Start context monitoring."""
        if self.is_monitoring:
            return
            
        self.logger.info(f"Starting context monitoring (interactive={interactive}, minimal={minimal})")
        
        self.is_monitoring = True
        self.is_paused = False
        
        # Start monitoring thread
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            args=(interactive, minimal),
            daemon=True
        )
        self.monitoring_thread.start()
    
    def _monitoring_loop(self, interactive=False, minimal=False):
        """Main monitoring loop running in separate thread."""
        asyncio.set_event_loop(asyncio.new_event_loop())
        loop = asyncio.get_event_loop()
        
        try:
            loop.run_until_complete(self._async_monitoring_loop(interactive, minimal))
        except Exception as e:
            self.logger.error(f"Monitoring loop error: {e}")
        finally:
            loop.close()
    
    async def _async_monitoring_loop(self, interactive=False, minimal=False):
        """Async monitoring loop."""
        while self.is_monitoring:
            try:
                if not self.is_paused and self.privacy.is_monitoring_allowed():
                    # Gather context
                    context = await self._gather_context(minimal)
                    
                    if context:
                        # Check for changes
                        if await self._detect_changes(context):
                            await self._handle_context_update(context)
                        
                        # Update current context
                        self.current_context = context
                        
                        # Maintain history
                        self.context_history.append(context)
                        if len(self.context_history) > self.max_history:
                            self.context_history.pop(0)
                
                # Adaptive sleep based on activity
                sleep_time = self._calculate_monitoring_interval()
                await asyncio.sleep(sleep_time)
                
            except Exception as e:
                self.logger.error(f"Monitoring cycle error: {e}")
                await asyncio.sleep(1)  # Error recovery
    
    async def _gather_context(self, minimal=False) -> Optional[SystemContext]:
        """Gather current system context."""
        try:
            timestamp = time.time()
            
            # Get active application
            active_app = await self._get_active_application()
            if not active_app:
                return None
            
            # Get all applications (if not minimal)
            all_apps = []
            if not minimal:
                all_apps = await self._get_all_applications()
            
            # Get screen content (if privacy allows and not minimal)
            screen_content = None
            if not minimal and self.privacy.is_screen_reading_allowed():
                screen_content = await self._capture_screen_content()
            
            # Get recent input events
            recent_inputs = self._get_recent_inputs()
            
            # Get system stats
            system_stats = await self._get_system_stats()
            
            # Get network activity
            network_activity = await self._get_network_activity()
            
            # Calculate activity level
            activity_level = self._calculate_activity_level()
            
            return SystemContext(
                timestamp=timestamp,
                active_app=active_app,
                all_apps=all_apps,
                screen_content=screen_content,
                recent_inputs=recent_inputs,
                system_stats=system_stats,
                network_activity=network_activity,
                activity_level=activity_level
            )
            
        except Exception as e:
            self.logger.error(f"Failed to gather context: {e}")
            return None
    
    async def _get_active_application(self) -> Optional[AppInfo]:
        """Get information about the currently active application."""
        try:
            # Get foreground window
            hwnd = self.user32.GetForegroundWindow()
            if not hwnd:
                return None
            
            # Get process ID
            pid = wintypes.DWORD()
            self.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            
            # Get window title
            title_length = self.user32.GetWindowTextLengthW(hwnd)
            title_buffer = ctypes.create_unicode_buffer(title_length + 1)
            self.user32.GetWindowTextW(hwnd, title_buffer, title_length + 1)
            title = title_buffer.value
            
            # Get process name
            process_name = await self._get_process_name(pid.value)
            
            # Get window rectangle
            rect = wintypes.RECT()
            self.user32.GetWindowRect(hwnd, ctypes.byref(rect))
            window_rect = (rect.left, rect.top, rect.right, rect.bottom)
            
            # Get process stats
            memory_usage = await self._get_process_memory(pid.value)
            cpu_usage = await self._get_process_cpu(pid.value)
            
            return AppInfo(
                name=process_name,
                title=title,
                pid=pid.value,
                handle=hwnd,
                is_foreground=True,
                memory_usage=memory_usage,
                cpu_usage=cpu_usage,
                window_rect=window_rect,
                is_visible=True
            )
            
        except Exception as e:
            self.logger.error(f"Failed to get active application: {e}")
            return None
    
    async def _get_all_applications(self) -> List[AppInfo]:
        """Get information about all running applications with windows."""
        apps = []
        
        def enum_windows_proc(hwnd, lParam):
            try:
                if self.user32.IsWindowVisible(hwnd):
                    # Get process ID
                    pid = wintypes.DWORD()
                    self.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
                    
                    # Get window title
                    title_length = self.user32.GetWindowTextLengthW(hwnd)
                    if title_length > 0:
                        title_buffer = ctypes.create_unicode_buffer(title_length + 1)
                        self.user32.GetWindowTextW(hwnd, title_buffer, title_length + 1)
                        title = title_buffer.value
                        
                        if title.strip():  # Only include windows with titles
                            # Get additional info
                            process_name = self._get_process_name_sync(pid.value)
                            
                            # Get window rectangle
                            rect = wintypes.RECT()
                            self.user32.GetWindowRect(hwnd, ctypes.byref(rect))
                            window_rect = (rect.left, rect.top, rect.right, rect.bottom)
                            
                            app_info = AppInfo(
                                name=process_name,
                                title=title,
                                pid=pid.value,
                                handle=hwnd,
                                is_foreground=False,
                                memory_usage=0.0,  # Calculated separately for performance
                                cpu_usage=0.0,
                                window_rect=window_rect,
                                is_visible=True
                            )
                            apps.append(app_info)
            except:
                pass  # Skip problematic windows
            
            return True  # Continue enumeration
        
        # Convert to callable
        enum_proc = ctypes.WINFUNCTYPE(
            wintypes.BOOL,
            wintypes.HWND,
            wintypes.LPARAM
        )(enum_windows_proc)
        
        # Enumerate all windows
        self.user32.EnumWindows(enum_proc, 0)
        
        return apps
    
    async def _capture_screen_content(self) -> Optional[ScreenContent]:
        """Capture and analyze screen content."""
        if not self.screen_capturer:
            return None
            
        try:
            # Capture screen
            screenshot = await self.screen_capturer.capture()
            if not screenshot:
                return None
            
            # Calculate image hash for change detection
            image_hash = self._calculate_image_hash(screenshot)
            
            # OCR text extraction
            ocr_text = ""
            if self.ocr_engine:
                ocr_text = await self._extract_text_from_image(screenshot)
            
            # Get active window name
            active_app = await self._get_active_application()
            active_window = active_app.name if active_app else "unknown"
            
            # Analyze UI elements (basic implementation)
            ui_elements = await self._analyze_ui_elements(screenshot)
            
            return ScreenContent(
                timestamp=time.time(),
                ocr_text=ocr_text,
                image_hash=image_hash,
                active_window=active_window,
                regions=[],  # Could implement region detection
                ui_elements=ui_elements
            )
            
        except Exception as e:
            self.logger.error(f"Failed to capture screen content: {e}")
            return None
    
    async def _extract_text_from_image(self, image) -> str:
        """Extract text from image using OCR."""
        try:
            if not self.ocr_engine:
                return ""
            
            # Convert image to format suitable for OCR
            # This is a simplified implementation
            # In practice, you'd need proper image conversion
            
            # For now, return empty string
            return ""
            
        except Exception as e:
            self.logger.error(f"OCR failed: {e}")
            return ""
    
    async def _analyze_ui_elements(self, image) -> List[Dict[str, Any]]:
        """Analyze UI elements in the screenshot."""
        # This would implement computer vision to detect:
        # - Buttons
        # - Text fields
        # - Menus
        # - Icons
        # For now, return empty list
        return []
    
    def _calculate_image_hash(self, image) -> str:
        """Calculate hash of image for change detection."""
        import hashlib
        # Simplified hash - in practice you'd use perceptual hashing
        return hashlib.md5(str(id(image)).encode()).hexdigest()
    
    async def _detect_changes(self, context: SystemContext) -> bool:
        """Detect if significant changes occurred."""
        changes_detected = False
        
        # Check for app switch
        if self.last_active_window != context.active_app.name:
            changes_detected = True
            if self.on_app_switch:
                await self.on_app_switch(self.last_active_window, context.active_app.name)
            self.last_active_window = context.active_app.name
        
        # Check for screen changes
        if context.screen_content:
            if self.last_screen_hash != context.screen_content.image_hash:
                changes_detected = True
                if self.on_screen_change:
                    await self.on_screen_change(context.screen_content)
                self.last_screen_hash = context.screen_content.image_hash
        
        # Check for recent input activity
        if context.recent_inputs:
            changes_detected = True
            if self.on_input_activity:
                await self.on_input_activity(context.recent_inputs)
        
        return changes_detected
    
    async def _handle_context_update(self, context: SystemContext):
        """Handle context update with change notification."""
        self.changes_pending = True
        
        if self.on_context_change:
            await self.on_context_change(context)
    
    # Input handling methods
    async def _handle_keyboard_input(self, vk_code):
        """Handle keyboard input event."""
        if not self.privacy.is_input_monitoring_allowed():
            return
            
        input_event = InputEvent(
            timestamp=time.time(),
            event_type='keyboard',
            data={'vk_code': vk_code}
        )
        
        self._record_input_event(input_event)
    
    async def _handle_mouse_input(self, wParam, lParam):
        """Handle mouse input event."""
        if not self.privacy.is_input_monitoring_allowed():
            return
            
        input_event = InputEvent(
            timestamp=time.time(),
            event_type='mouse',
            data={'wParam': wParam, 'lParam': lParam}
        )
        
        self._record_input_event(input_event)
    
    def _record_input_event(self, event: InputEvent):
        """Record input event for activity tracking."""
        self.last_input_time = event.timestamp
        
        # Add to activity buffer
        self.activity_buffer.append(event.timestamp)
        
        # Clean old entries
        cutoff_time = event.timestamp - self.activity_window_size
        self.activity_buffer = [t for t in self.activity_buffer if t > cutoff_time]
    
    def _get_recent_inputs(self) -> List[InputEvent]:
        """Get recent input events."""
        # Return sanitized input events (without sensitive data)
        # This is a simplified implementation
        return []
    
    def _calculate_activity_level(self) -> float:
        """Calculate current activity level (0.0 to 1.0)."""
        if not self.activity_buffer:
            return 0.0
        
        # Calculate activity based on input frequency
        current_time = time.time()
        recent_activity = len([
            t for t in self.activity_buffer 
            if current_time - t < 10  # Last 10 seconds
        ])
        
        # Normalize to 0-1 scale (assuming max 50 events per 10 seconds)
        return min(recent_activity / 50.0, 1.0)
    
    def _calculate_monitoring_interval(self) -> float:
        """Calculate adaptive monitoring interval."""
        base_interval = 0.5  # 500ms base
        
        # Reduce frequency during low activity
        activity = self.get_activity_level()
        if activity < 0.1:
            return base_interval * 2.0  # 1 second
        elif activity > 0.8:
            return base_interval * 0.5  # 250ms
        
        return base_interval
    
    # System information methods
    async def _get_process_name(self, pid: int) -> str:
        """Get process name from PID."""
        try:
            import psutil
            process = psutil.Process(pid)
            return process.name()
        except:
            return "unknown"
    
    def _get_process_name_sync(self, pid: int) -> str:
        """Get process name synchronously."""
        try:
            import psutil
            process = psutil.Process(pid)
            return process.name()
        except:
            return "unknown"
    
    async def _get_process_memory(self, pid: int) -> float:
        """Get process memory usage in MB."""
        try:
            import psutil
            process = psutil.Process(pid)
            return process.memory_info().rss / 1024 / 1024
        except:
            return 0.0
    
    async def _get_process_cpu(self, pid: int) -> float:
        """Get process CPU usage percentage."""
        try:
            import psutil
            process = psutil.Process(pid)
            return process.cpu_percent()
        except:
            return 0.0
    
    async def _get_system_stats(self) -> Dict[str, float]:
        """Get system statistics."""
        try:
            import psutil
            return {
                'cpu_percent': psutil.cpu_percent(),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_usage': psutil.disk_usage('/').percent,
                'boot_time': psutil.boot_time()
            }
        except:
            return {}
    
    async def _get_network_activity(self) -> Dict[str, Any]:
        """Get network activity information."""
        try:
            import psutil
            net_io = psutil.net_io_counters()
            return {
                'bytes_sent': net_io.bytes_sent,
                'bytes_recv': net_io.bytes_recv,
                'packets_sent': net_io.packets_sent,
                'packets_recv': net_io.packets_recv
            }
        except:
            return {}
    
    # Public interface
    def has_changes(self) -> bool:
        """Check if there are pending changes to process."""
        return self.changes_pending
    
    def get_activity_level(self) -> float:
        """Get current activity level."""
        return self._calculate_activity_level()
    
    async def get_current_context(self) -> Optional[SystemContext]:
        """Get current system context."""
        if self.changes_pending:
            self.changes_pending = False
            return self.current_context
        return None
    
    async def pause_monitoring(self):
        """Pause monitoring."""
        self.is_paused = True
        self.logger.info("Context monitoring paused")
    
    async def resume_monitoring(self):
        """Resume monitoring."""
        self.is_paused = False
        self.logger.info("Context monitoring resumed")
    
    async def shutdown(self):
        """Shutdown the context manager."""
        self.logger.info("Shutting down Context Manager...")
        
        self.is_monitoring = False
        
        # Unhook input handlers
        if self.keyboard_hook:
            self.user32.UnhookWindowsHookEx(self.keyboard_hook)
        if self.mouse_hook:
            self.user32.UnhookWindowsHookEx(self.mouse_hook)
        
        # Wait for monitoring thread to finish
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=5)
        
        self.logger.info("Context Manager shutdown complete")

class ScreenCapturer:
    """Screen capture functionality."""
    
    def __init__(self):
        self.initialized = False
    
    async def initialize(self):
        """Initialize screen capture."""
        # Implementation would setup Windows Graphics Capture API
        self.initialized = True
    
    async def capture(self):
        """Capture current screen."""
        if not self.initialized:
            return None
        
        # This would implement actual screen capture
        # For now, return None to avoid dependency issues
        return None
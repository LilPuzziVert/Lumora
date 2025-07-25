"""
LUMORA Privacy Guardian

Complete privacy and security control system that gives users granular
control over what Lumora can access and how it behaves.
"""

import time
import logging
import hashlib
from typing import Dict, Any, List, Optional, Callable, Set
from dataclasses import dataclass, field
from enum import Enum
import json

class PrivacyLevel(Enum):
    """Privacy levels from most permissive to most restrictive."""
    FULL_ACCESS = "full_access"
    BALANCED = "balanced"
    RESTRICTED = "restricted"
    PRIVATE = "private"
    PARANOID = "paranoid"

class DataType(Enum):
    """Types of data that can be monitored."""
    SCREEN_CONTENT = "screen_content"
    KEYBOARD_INPUT = "keyboard_input"
    MOUSE_INPUT = "mouse_input"
    WINDOW_TITLES = "window_titles"
    APP_USAGE = "app_usage"
    CLIPBOARD = "clipboard"
    NETWORK_ACTIVITY = "network_activity"
    FILE_ACCESS = "file_access"
    MICROPHONE = "microphone"
    CAMERA = "camera"
    SYSTEM_STATS = "system_stats"

@dataclass
class PrivacySettings:
    """Complete privacy configuration."""
    level: PrivacyLevel = PrivacyLevel.BALANCED
    
    # Global toggles
    monitoring_enabled: bool = True
    private_mode: bool = False
    stealth_mode: bool = False
    
    # Data type permissions
    allowed_data_types: Set[DataType] = field(default_factory=lambda: {
        DataType.SCREEN_CONTENT,
        DataType.WINDOW_TITLES,
        DataType.APP_USAGE,
        DataType.SYSTEM_STATS
    })
    
    # Action permissions
    require_confirmation_for_actions: bool = True
    auto_actions_enabled: bool = False
    max_automation_level: int = 2  # 0-5 scale
    
    # Data retention
    store_interactions: bool = True
    data_retention_days: int = 30
    auto_delete_sensitive: bool = True
    
    # Application-specific settings
    blocked_apps: Set[str] = field(default_factory=set)
    sensitive_apps: Set[str] = field(default_factory=lambda: {
        "banking", "password", "crypto", "medical"
    })
    
    # Content filtering
    blocked_keywords: Set[str] = field(default_factory=set)
    sensitive_patterns: List[str] = field(default_factory=lambda: [
        r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b",  # Credit cards
        r"\b\d{3}-\d{2}-\d{4}\b",  # SSN
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"  # Email
    ])
    
    # Time-based restrictions
    active_hours_start: int = 6  # 6 AM
    active_hours_end: int = 22   # 10 PM
    respect_dnd_mode: bool = True
    
    # Sharing and export
    allow_data_export: bool = False
    allow_sharing: bool = False
    encryption_required: bool = True

class PrivacyGuardian:
    """
    Privacy and security control system for Lumora.
    
    Provides granular control over what data can be accessed,
    how it's processed, and what actions can be taken.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Current settings
        self.settings = PrivacySettings()
        
        # Runtime state
        self.session_start_time = time.time()
        self.privacy_violations = []
        self.blocked_attempts = []
        
        # Event handlers
        self.on_privacy_change: Optional[Callable] = None
        self.on_violation: Optional[Callable] = None
        
        # Temporary sessions
        self.temp_permissions = {}
        self.session_overrides = {}
        
        # Password protection
        self.is_unlocked = False
        self.unlock_timestamp = 0
        self.auto_lock_timeout = 300  # 5 minutes
        
    def set_privacy_level(self, level: PrivacyLevel):
        """Set overall privacy level with predefined configurations."""
        self.settings.level = level
        
        if level == PrivacyLevel.FULL_ACCESS:
            self.settings.allowed_data_types = set(DataType)
            self.settings.require_confirmation_for_actions = False
            self.settings.auto_actions_enabled = True
            self.settings.max_automation_level = 5
            
        elif level == PrivacyLevel.BALANCED:
            self.settings.allowed_data_types = {
                DataType.SCREEN_CONTENT,
                DataType.WINDOW_TITLES,
                DataType.APP_USAGE,
                DataType.SYSTEM_STATS,
                DataType.MOUSE_INPUT
            }
            self.settings.require_confirmation_for_actions = True
            self.settings.auto_actions_enabled = True
            self.settings.max_automation_level = 2
            
        elif level == PrivacyLevel.RESTRICTED:
            self.settings.allowed_data_types = {
                DataType.WINDOW_TITLES,
                DataType.APP_USAGE,
                DataType.SYSTEM_STATS
            }
            self.settings.require_confirmation_for_actions = True
            self.settings.auto_actions_enabled = False
            self.settings.max_automation_level = 1
            
        elif level == PrivacyLevel.PRIVATE:
            self.settings.allowed_data_types = {
                DataType.SYSTEM_STATS
            }
            self.settings.require_confirmation_for_actions = True
            self.settings.auto_actions_enabled = False
            self.settings.max_automation_level = 0
            self.settings.store_interactions = False
            
        elif level == PrivacyLevel.PARANOID:
            self.settings.allowed_data_types = set()
            self.settings.monitoring_enabled = False
            self.settings.require_confirmation_for_actions = True
            self.settings.auto_actions_enabled = False
            self.settings.max_automation_level = 0
            self.settings.store_interactions = False
        
        self._notify_privacy_change("level", level.value)
        self.logger.info(f"Privacy level set to {level.value}")
    
    def enable_private_mode(self, duration_minutes: Optional[int] = None):
        """Enable private mode temporarily or permanently."""
        self.settings.private_mode = True
        
        if duration_minutes:
            # Set up automatic disable
            import threading
            def disable_private_mode():
                time.sleep(duration_minutes * 60)
                self.disable_private_mode()
            
            threading.Thread(target=disable_private_mode, daemon=True).start()
        
        self._notify_privacy_change("private_mode", True)
        self.logger.info(f"Private mode enabled{f' for {duration_minutes} minutes' if duration_minutes else ''}")
    
    def disable_private_mode(self):
        """Disable private mode."""
        self.settings.private_mode = False
        self._notify_privacy_change("private_mode", False)
        self.logger.info("Private mode disabled")
    
    def is_monitoring_allowed(self) -> bool:
        """Check if monitoring is currently allowed."""
        if not self.settings.monitoring_enabled:
            return False
            
        if self.settings.private_mode:
            return False
            
        # Check time restrictions
        if not self._is_within_active_hours():
            return False
            
        # Check DND mode
        if self.settings.respect_dnd_mode and self._is_dnd_active():
            return False
            
        return True
    
    def is_data_type_allowed(self, data_type: DataType) -> bool:
        """Check if a specific data type is allowed."""
        if not self.is_monitoring_allowed():
            return False
            
        return data_type in self.settings.allowed_data_types
    
    def is_screen_reading_allowed(self) -> bool:
        """Check if screen reading is allowed."""
        return self.is_data_type_allowed(DataType.SCREEN_CONTENT)
    
    def is_input_monitoring_allowed(self) -> bool:
        """Check if input monitoring is allowed."""
        return (self.is_data_type_allowed(DataType.KEYBOARD_INPUT) or 
                self.is_data_type_allowed(DataType.MOUSE_INPUT))
    
    def is_app_allowed(self, app_name: str) -> bool:
        """Check if monitoring a specific app is allowed."""
        if not self.is_monitoring_allowed():
            return False
            
        # Check blocked apps
        if app_name.lower() in [app.lower() for app in self.settings.blocked_apps]:
            return False
            
        # Check sensitive apps
        for sensitive_term in self.settings.sensitive_apps:
            if sensitive_term.lower() in app_name.lower():
                # Require additional confirmation for sensitive apps
                return self._request_sensitive_app_permission(app_name)
                
        return True
    
    def is_action_allowed(self, action: Dict[str, Any]) -> bool:
        """Check if a specific action is allowed."""
        if not self.settings.auto_actions_enabled:
            return False
            
        action_type = action.get('type', '')
        risk_level = action.get('risk_level', 1)
        
        # Check automation level limits
        if risk_level > self.settings.max_automation_level:
            return False
            
        # Check for sensitive actions
        if self._is_sensitive_action(action):
            return self.settings.require_confirmation_for_actions
            
        return True
    
    def require_confirmation_for_actions(self) -> bool:
        """Check if actions require user confirmation."""
        return self.settings.require_confirmation_for_actions
    
    def filter_context(self, context: Any) -> Any:
        """Filter context data based on privacy settings."""
        if not context:
            return context
            
        # Create filtered copy
        filtered_context = self._deep_copy_context(context)
        
        # Apply content filtering
        if hasattr(filtered_context, 'screen_content') and filtered_context.screen_content:
            filtered_context.screen_content = self._filter_screen_content(
                filtered_context.screen_content
            )
        
        # Filter sensitive app data
        if hasattr(filtered_context, 'active_app') and filtered_context.active_app:
            if not self.is_app_allowed(filtered_context.active_app.name):
                filtered_context.active_app = self._sanitize_app_info(filtered_context.active_app)
        
        # Filter input events
        if hasattr(filtered_context, 'recent_inputs') and filtered_context.recent_inputs:
            filtered_context.recent_inputs = self._filter_input_events(
                filtered_context.recent_inputs
            )
        
        return filtered_context
    
    def _filter_screen_content(self, screen_content):
        """Filter sensitive information from screen content."""
        if not screen_content:
            return screen_content
        
        # Filter OCR text
        if hasattr(screen_content, 'ocr_text'):
            screen_content.ocr_text = self._filter_sensitive_text(screen_content.ocr_text)
        
        return screen_content
    
    def _filter_sensitive_text(self, text: str) -> str:
        """Filter sensitive patterns from text."""
        if not text:
            return text
            
        import re
        filtered_text = text
        
        # Apply sensitive pattern filtering
        for pattern in self.settings.sensitive_patterns:
            filtered_text = re.sub(pattern, "[REDACTED]", filtered_text)
        
        # Apply keyword filtering
        for keyword in self.settings.blocked_keywords:
            filtered_text = filtered_text.replace(keyword, "[BLOCKED]")
        
        return filtered_text
    
    def _filter_input_events(self, input_events: List[Any]) -> List[Any]:
        """Filter input events based on privacy settings."""
        if not self.is_input_monitoring_allowed():
            return []
        
        filtered_events = []
        for event in input_events:
            if self._is_input_event_safe(event):
                filtered_events.append(self._sanitize_input_event(event))
        
        return filtered_events
    
    def _is_input_event_safe(self, event) -> bool:
        """Check if input event is safe to record."""
        # Don't record keyboard input in password fields
        if hasattr(event, 'event_type') and event.event_type == 'keyboard':
            # This would need integration with accessibility APIs
            # to detect password fields
            return False
        
        return True
    
    def _sanitize_input_event(self, event):
        """Sanitize input event data."""
        # Remove actual key data, keep only timing and type
        sanitized = type(event)(
            timestamp=event.timestamp,
            event_type=event.event_type,
            data={'sanitized': True}
        )
        return sanitized
    
    def _sanitize_app_info(self, app_info):
        """Sanitize app information for blocked apps."""
        sanitized = type(app_info)(
            name="[BLOCKED]",
            title="[BLOCKED]",
            pid=0,
            handle=0,
            is_foreground=app_info.is_foreground,
            memory_usage=0,
            cpu_usage=0,
            window_rect=(0, 0, 0, 0),
            is_visible=False
        )
        return sanitized
    
    def _is_sensitive_action(self, action: Dict[str, Any]) -> bool:
        """Check if action involves sensitive operations."""
        sensitive_types = {
            'file_access', 'network_request', 'system_command',
            'clipboard_access', 'password_field', 'financial_data'
        }
        
        return action.get('type') in sensitive_types
    
    def _is_within_active_hours(self) -> bool:
        """Check if current time is within active hours."""
        import datetime
        current_hour = datetime.datetime.now().hour
        
        if self.settings.active_hours_start <= self.settings.active_hours_end:
            return self.settings.active_hours_start <= current_hour <= self.settings.active_hours_end
        else:
            # Handles cases like 22:00 to 06:00
            return current_hour >= self.settings.active_hours_start or current_hour <= self.settings.active_hours_end
    
    def _is_dnd_active(self) -> bool:
        """Check if Do Not Disturb mode is active."""
        try:
            # Check Windows Focus Assist status
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\CloudStore\Store\Cache\DefaultAccount\$$windows.data.notifications.quiethourssettings"
            )
            # This is simplified - actual DND detection is more complex
            return False
        except:
            return False
    
    def _request_sensitive_app_permission(self, app_name: str) -> bool:
        """Request permission for sensitive app access."""
        # This would show a permission dialog
        # For now, default to denied
        self.logger.warning(f"Sensitive app access requested: {app_name}")
        return False
    
    def _deep_copy_context(self, context):
        """Create a deep copy of context for filtering."""
        # Simplified copy - in practice you'd use proper deep copy
        return context
    
    def _notify_privacy_change(self, setting: str, value: Any):
        """Notify about privacy setting changes."""
        if self.on_privacy_change:
            self.on_privacy_change(setting, value)
    
    def record_privacy_violation(self, violation_type: str, details: Dict[str, Any]):
        """Record a privacy violation."""
        violation = {
            'timestamp': time.time(),
            'type': violation_type,
            'details': details,
            'session_id': self._get_session_id()
        }
        
        self.privacy_violations.append(violation)
        
        if self.on_violation:
            self.on_violation(violation)
        
        self.logger.warning(f"Privacy violation recorded: {violation_type}")
    
    def get_privacy_report(self) -> Dict[str, Any]:
        """Get comprehensive privacy report."""
        session_duration = time.time() - self.session_start_time
        
        return {
            'session_duration': session_duration,
            'current_level': self.settings.level.value,
            'private_mode': self.settings.private_mode,
            'monitoring_enabled': self.settings.monitoring_enabled,
            'allowed_data_types': [dt.value for dt in self.settings.allowed_data_types],
            'violations_count': len(self.privacy_violations),
            'blocked_attempts': len(self.blocked_attempts),
            'last_violation': self.privacy_violations[-1] if self.privacy_violations else None
        }
    
    def export_settings(self) -> str:
        """Export privacy settings to JSON."""
        settings_dict = {
            'level': self.settings.level.value,
            'monitoring_enabled': self.settings.monitoring_enabled,
            'private_mode': self.settings.private_mode,
            'allowed_data_types': [dt.value for dt in self.settings.allowed_data_types],
            'require_confirmation_for_actions': self.settings.require_confirmation_for_actions,
            'auto_actions_enabled': self.settings.auto_actions_enabled,
            'max_automation_level': self.settings.max_automation_level,
            'data_retention_days': self.settings.data_retention_days,
            'blocked_apps': list(self.settings.blocked_apps),
            'sensitive_apps': list(self.settings.sensitive_apps),
            'active_hours_start': self.settings.active_hours_start,
            'active_hours_end': self.settings.active_hours_end
        }
        
        return json.dumps(settings_dict, indent=2)
    
    def import_settings(self, settings_json: str) -> bool:
        """Import privacy settings from JSON."""
        try:
            settings_dict = json.loads(settings_json)
            
            # Validate and apply settings
            if 'level' in settings_dict:
                level = PrivacyLevel(settings_dict['level'])
                self.set_privacy_level(level)
            
            if 'monitoring_enabled' in settings_dict:
                self.settings.monitoring_enabled = settings_dict['monitoring_enabled']
            
            if 'allowed_data_types' in settings_dict:
                self.settings.allowed_data_types = {
                    DataType(dt) for dt in settings_dict['allowed_data_types']
                }
            
            # Apply other settings...
            
            self.logger.info("Privacy settings imported successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to import privacy settings: {e}")
            return False
    
    def is_private_mode(self) -> bool:
        """Check if private mode is active."""
        return self.settings.private_mode
    
    def get_current_settings(self) -> PrivacySettings:
        """Get current privacy settings."""
        return self.settings
    
    def _get_session_id(self) -> str:
        """Get unique session identifier."""
        session_data = f"{self.session_start_time}-{id(self)}"
        return hashlib.md5(session_data.encode()).hexdigest()[:8]
    
    # Emergency controls
    def panic_mode(self):
        """Activate panic mode - maximum privacy."""
        self.logger.warning("PANIC MODE ACTIVATED")
        
        # Set to most restrictive settings
        self.set_privacy_level(PrivacyLevel.PARANOID)
        self.enable_private_mode()
        
        # Clear any stored data
        self.privacy_violations.clear()
        self.blocked_attempts.clear()
        
        # Notify all systems to stop immediately
        self._notify_privacy_change("panic_mode", True)
    
    def emergency_shutdown(self):
        """Emergency shutdown of all monitoring."""
        self.settings.monitoring_enabled = False
        self.settings.private_mode = True
        self._notify_privacy_change("emergency_shutdown", True)
        self.logger.critical("EMERGENCY SHUTDOWN ACTIVATED")
    
    # Quick privacy toggles
    def toggle_monitoring(self) -> bool:
        """Toggle monitoring on/off."""
        self.settings.monitoring_enabled = not self.settings.monitoring_enabled
        self._notify_privacy_change("monitoring_enabled", self.settings.monitoring_enabled)
        return self.settings.monitoring_enabled
    
    def toggle_screen_reading(self) -> bool:
        """Toggle screen reading on/off."""
        if DataType.SCREEN_CONTENT in self.settings.allowed_data_types:
            self.settings.allowed_data_types.remove(DataType.SCREEN_CONTENT)
            enabled = False
        else:
            self.settings.allowed_data_types.add(DataType.SCREEN_CONTENT)
            enabled = True
        
        self._notify_privacy_change("screen_reading", enabled)
        return enabled
    
    def toggle_input_monitoring(self) -> bool:
        """Toggle input monitoring on/off."""
        input_types = {DataType.KEYBOARD_INPUT, DataType.MOUSE_INPUT}
        
        if input_types.issubset(self.settings.allowed_data_types):
            self.settings.allowed_data_types -= input_types
            enabled = False
        else:
            self.settings.allowed_data_types |= input_types
            enabled = True
        
        self._notify_privacy_change("input_monitoring", enabled)
        return enabled
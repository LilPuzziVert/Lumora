"""
LUMORA Configuration Manager

Handles all configuration and settings for Lumora including:
- System settings
- User preferences
- Plugin configurations
- Performance tuning
- Backup and restore
"""

import os
import json
import yaml
import logging
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
from dataclasses import dataclass, asdict
import configparser

@dataclass
class LumoraConfig:
    """Main Lumora configuration structure."""
    
    # Application settings
    app_name: str = "Lumora"
    version: str = "2.0.0"
    debug_mode: bool = False
    log_level: str = "INFO"
    
    # Paths
    data_dir: str = "data"
    logs_dir: str = "logs"
    plugins_dir: str = "plugins"
    models_dir: str = "data/models"
    cache_dir: str = "data/cache"
    
    # Core system settings
    max_memory_usage_mb: int = 1024
    max_cpu_usage_percent: float = 25.0
    monitoring_interval_ms: int = 500
    context_history_size: int = 1000
    
    # AI settings
    local_ai_enabled: bool = True
    ai_response_timeout_sec: int = 30
    ai_model_path: str = "data/models/lumora_base.bin"
    ai_temperature: float = 0.7
    ai_max_tokens: int = 1024
    
    # Privacy settings
    privacy_level: str = "balanced"
    data_retention_days: int = 30
    auto_delete_logs: bool = True
    encrypt_stored_data: bool = True
    
    # Performance settings
    adaptive_performance: bool = True
    power_save_mode: bool = False
    gaming_mode_detection: bool = True
    high_performance_apps: List[str] = None
    
    # UI settings
    show_notifications: bool = True
    minimize_to_tray: bool = True
    start_with_windows: bool = True
    hotkey_combination: str = "Ctrl+Alt+L"
    theme: str = "dark"
    
    # Plugin settings
    enable_plugins: bool = True
    auto_update_plugins: bool = False
    plugin_security_level: str = "medium"
    
    # Automation settings
    automation_enabled: bool = True
    max_automation_risk_level: int = 2
    confirm_high_risk_actions: bool = True
    
    # Network settings
    allow_network_access: bool = False
    proxy_settings: Dict[str, Any] = None
    offline_mode: bool = True
    
    def __post_init__(self):
        if self.high_performance_apps is None:
            self.high_performance_apps = ["gaming", "video", "streaming"]
        if self.proxy_settings is None:
            self.proxy_settings = {}

class ConfigManager:
    """
    Configuration management system for Lumora.
    
    Handles loading, saving, validation, and management of all
    configuration settings across the application.
    """
    
    def __init__(self, config_dir: Optional[str] = None):
        self.logger = logging.getLogger(__name__)
        
        # Set up paths
        self.config_dir = Path(config_dir) if config_dir else Path.cwd() / "config"
        self.config_dir.mkdir(exist_ok=True)
        
        self.main_config_file = self.config_dir / "settings.yaml"
        self.user_config_file = self.config_dir / "user_preferences.yaml"
        self.system_config_file = self.config_dir / "system.yaml"
        self.backup_dir = self.config_dir / "backups"
        self.backup_dir.mkdir(exist_ok=True)
        
        # Configuration data
        self.config = LumoraConfig()
        self.user_preferences = {}
        self.system_settings = {}
        self.runtime_overrides = {}
        
        # Configuration history
        self.config_history = []
        self.max_history = 10
        
        # Load configurations
        self._load_all_configs()
    
    def _load_all_configs(self):
        """Load all configuration files."""
        try:
            # Load main configuration
            if self.main_config_file.exists():
                self._load_main_config()
            else:
                self._create_default_config()
            
            # Load user preferences
            if self.user_config_file.exists():
                self._load_user_preferences()
            
            # Load system settings
            if self.system_config_file.exists():
                self._load_system_settings()
            
            self.logger.info("Configuration loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
            self._create_default_config()
    
    def _load_main_config(self):
        """Load main configuration from YAML file."""
        try:
            with open(self.main_config_file, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
            
            # Validate and merge with defaults
            self.config = self._merge_config_data(self.config, config_data)
            
        except Exception as e:
            self.logger.error(f"Failed to load main config: {e}")
            raise
    
    def _load_user_preferences(self):
        """Load user preferences."""
        try:
            with open(self.user_config_file, 'r', encoding='utf-8') as f:
                self.user_preferences = yaml.safe_load(f) or {}
                
        except Exception as e:
            self.logger.error(f"Failed to load user preferences: {e}")
            self.user_preferences = {}
    
    def _load_system_settings(self):
        """Load system-specific settings."""
        try:
            with open(self.system_config_file, 'r', encoding='utf-8') as f:
                self.system_settings = yaml.safe_load(f) or {}
                
        except Exception as e:
            self.logger.error(f"Failed to load system settings: {e}")
            self.system_settings = {}
    
    def _create_default_config(self):
        """Create default configuration files."""
        try:
            # Create main config
            config_dict = asdict(self.config)
            with open(self.main_config_file, 'w', encoding='utf-8') as f:
                yaml.dump(config_dict, f, default_flow_style=False, indent=2)
            
            # Create empty user preferences
            with open(self.user_config_file, 'w', encoding='utf-8') as f:
                yaml.dump({}, f)
            
            # Create system settings with auto-detected values
            system_config = self._detect_system_settings()
            with open(self.system_config_file, 'w', encoding='utf-8') as f:
                yaml.dump(system_config, f, default_flow_style=False, indent=2)
            
            self.logger.info("Default configuration created")
            
        except Exception as e:
            self.logger.error(f"Failed to create default config: {e}")
            raise
    
    def _detect_system_settings(self) -> Dict[str, Any]:
        """Auto-detect system-specific settings."""
        import platform
        import psutil
        
        system_info = {
            'os': platform.system(),
            'os_version': platform.version(),
            'architecture': platform.architecture()[0],
            'processor': platform.processor(),
            'total_memory_gb': round(psutil.virtual_memory().total / (1024**3), 1),
            'cpu_count': psutil.cpu_count(),
            'screen_resolution': self._get_screen_resolution(),
            'install_path': str(Path.cwd()),
            'user_name': os.getenv('USERNAME', 'user'),
            'machine_id': self._generate_machine_id()
        }
        
        # Adjust settings based on system capabilities
        if system_info['total_memory_gb'] < 8:
            self.config.max_memory_usage_mb = 512
        elif system_info['total_memory_gb'] > 16:
            self.config.max_memory_usage_mb = 2048
        
        if system_info['cpu_count'] <= 4:
            self.config.max_cpu_usage_percent = 15.0
        
        return system_info
    
    def _get_screen_resolution(self) -> str:
        """Get screen resolution."""
        try:
            import ctypes
            user32 = ctypes.windll.user32
            screensize = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
            return f"{screensize[0]}x{screensize[1]}"
        except:
            return "1920x1080"  # Default
    
    def _generate_machine_id(self) -> str:
        """Generate unique machine identifier."""
        import hashlib
        import uuid
        
        try:
            # Use MAC address and system info
            mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) 
                           for elements in range(0,2*6,2)][::-1])
            system_id = f"{platform.node()}-{mac}"
            return hashlib.md5(system_id.encode()).hexdigest()[:16]
        except:
            return "unknown"
    
    def _merge_config_data(self, base_config: LumoraConfig, new_data: Dict[str, Any]) -> LumoraConfig:
        """Merge new configuration data with base config."""
        config_dict = asdict(base_config)
        
        # Recursively merge dictionaries
        def merge_dicts(base, new):
            for key, value in new.items():
                if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                    merge_dicts(base[key], value)
                else:
                    base[key] = value
        
        merge_dicts(config_dict, new_data)
        
        # Recreate config object
        return LumoraConfig(**config_dict)
    
    # Public interface methods
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation."""
        try:
            # Check runtime overrides first
            if key in self.runtime_overrides:
                return self.runtime_overrides[key]
            
            # Parse key path
            keys = key.split('.')
            value = asdict(self.config)
            
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    # Check user preferences
                    user_value = self.user_preferences
                    for uk in keys:
                        if isinstance(user_value, dict) and uk in user_value:
                            user_value = user_value[uk]
                        else:
                            return default
                    return user_value
            
            return value
            
        except Exception:
            return default
    
    def set(self, key: str, value: Any, save: bool = True):
        """Set configuration value using dot notation."""
        try:
            keys = key.split('.')
            
            # Update config object
            config_dict = asdict(self.config)
            current = config_dict
            
            for k in keys[:-1]:
                if k not in current:
                    current[k] = {}
                current = current[k]
            
            current[keys[-1]] = value
            
            # Recreate config object
            self.config = LumoraConfig(**config_dict)
            
            if save:
                self.save()
                
            self.logger.debug(f"Config updated: {key} = {value}")
            
        except Exception as e:
            self.logger.error(f"Failed to set config {key}: {e}")
            raise
    
    def set_user_preference(self, key: str, value: Any, save: bool = True):
        """Set user-specific preference."""
        keys = key.split('.')
        current = self.user_preferences
        
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        
        current[keys[-1]] = value
        
        if save:
            self.save_user_preferences()
    
    def get_user_preference(self, key: str, default: Any = None) -> Any:
        """Get user-specific preference."""
        keys = key.split('.')
        current = self.user_preferences
        
        try:
            for k in keys:
                current = current[k]
            return current
        except (KeyError, TypeError):
            return default
    
    def set_runtime_override(self, key: str, value: Any):
        """Set temporary runtime override (not saved)."""
        self.runtime_overrides[key] = value
    
    def clear_runtime_override(self, key: str):
        """Clear runtime override."""
        self.runtime_overrides.pop(key, None)
    
    def save(self):
        """Save main configuration to file."""
        try:
            # Create backup
            self._create_backup()
            
            # Save main config
            config_dict = asdict(self.config)
            with open(self.main_config_file, 'w', encoding='utf-8') as f:
                yaml.dump(config_dict, f, default_flow_style=False, indent=2)
            
            self.logger.debug("Configuration saved")
            
        except Exception as e:
            self.logger.error(f"Failed to save configuration: {e}")
            raise
    
    def save_user_preferences(self):
        """Save user preferences to file."""
        try:
            with open(self.user_config_file, 'w', encoding='utf-8') as f:
                yaml.dump(self.user_preferences, f, default_flow_style=False, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to save user preferences: {e}")
            raise
    
    def _create_backup(self):
        """Create backup of current configuration."""
        try:
            import shutil
            import datetime
            
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.backup_dir / f"settings_backup_{timestamp}.yaml"
            
            if self.main_config_file.exists():
                shutil.copy2(self.main_config_file, backup_file)
            
            # Clean old backups (keep last 10)
            backups = sorted(self.backup_dir.glob("settings_backup_*.yaml"))
            while len(backups) > self.max_history:
                oldest = backups.pop(0)
                oldest.unlink()
                
        except Exception as e:
            self.logger.warning(f"Failed to create config backup: {e}")
    
    def restore_backup(self, backup_filename: str) -> bool:
        """Restore configuration from backup."""
        try:
            backup_file = self.backup_dir / backup_filename
            if not backup_file.exists():
                return False
            
            # Create current backup first
            self._create_backup()
            
            # Restore backup
            import shutil
            shutil.copy2(backup_file, self.main_config_file)
            
            # Reload configuration
            self._load_main_config()
            
            self.logger.info(f"Configuration restored from {backup_filename}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to restore backup: {e}")
            return False
    
    def get_backups(self) -> List[str]:
        """Get list of available backup files."""
        try:
            backups = sorted(self.backup_dir.glob("settings_backup_*.yaml"))
            return [backup.name for backup in backups]
        except:
            return []
    
    def validate_config(self) -> Dict[str, List[str]]:
        """Validate current configuration and return issues."""
        issues = {
            'errors': [],
            'warnings': [],
            'info': []
        }
        
        # Validate paths
        for path_key in ['data_dir', 'logs_dir', 'plugins_dir', 'models_dir']:
            path_value = getattr(self.config, path_key)
            full_path = Path(path_value)
            
            if not full_path.is_absolute():
                full_path = Path.cwd() / path_value
                
            if not full_path.exists():
                try:
                    full_path.mkdir(parents=True, exist_ok=True)
                    issues['info'].append(f"Created directory: {full_path}")
                except Exception as e:
                    issues['errors'].append(f"Cannot create {path_key}: {full_path} - {e}")
        
        # Validate numeric ranges
        if self.config.max_memory_usage_mb < 128:
            issues['warnings'].append("Memory limit is very low (< 128MB)")
        elif self.config.max_memory_usage_mb > 4096:
            issues['warnings'].append("Memory limit is very high (> 4GB)")
        
        if self.config.max_cpu_usage_percent < 5:
            issues['warnings'].append("CPU limit is very low (< 5%)")
        elif self.config.max_cpu_usage_percent > 80:
            issues['warnings'].append("CPU limit is very high (> 80%)")
        
        if self.config.monitoring_interval_ms < 100:
            issues['warnings'].append("Monitoring interval is very fast (< 100ms)")
        elif self.config.monitoring_interval_ms > 5000:
            issues['warnings'].append("Monitoring interval is very slow (> 5s)")
        
        # Validate AI settings
        if self.config.local_ai_enabled:
            model_path = Path(self.config.ai_model_path)
            if not model_path.exists():
                issues['warnings'].append(f"AI model not found: {model_path}")
        
        return issues
    
    def reset_to_defaults(self):
        """Reset configuration to default values."""
        self.config = LumoraConfig()
        self.user_preferences = {}
        self.runtime_overrides = {}
        self.save()
        self.save_user_preferences()
        self.logger.info("Configuration reset to defaults")
    
    def export_config(self, export_path: str) -> bool:
        """Export configuration to file."""
        try:
            import time
            export_data = {
                'lumora_config': asdict(self.config),
                'user_preferences': self.user_preferences,
                'system_settings': self.system_settings,
                'export_timestamp': time.time(),
                'export_version': self.config.version
            }
            
            export_file = Path(export_path)
            with open(export_file, 'w', encoding='utf-8') as f:
                yaml.dump(export_data, f, default_flow_style=False, indent=2)
            
            self.logger.info(f"Configuration exported to {export_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export configuration: {e}")
            return False
    
    def import_config(self, import_path: str) -> bool:
        """Import configuration from file."""
        try:
            import time
            import_file = Path(import_path)
            if not import_file.exists():
                return False
            
            with open(import_file, 'r', encoding='utf-8') as f:
                import_data = yaml.safe_load(f)
            
            # Validate import data
            if 'lumora_config' not in import_data:
                self.logger.error("Invalid import file format")
                return False
            
            # Create backup first
            self._create_backup()
            
            # Import configuration
            if 'lumora_config' in import_data:
                self.config = self._merge_config_data(LumoraConfig(), import_data['lumora_config'])
            
            if 'user_preferences' in import_data:
                self.user_preferences = import_data['user_preferences']
            
            # Save imported configuration
            self.save()
            self.save_user_preferences()
            
            self.logger.info(f"Configuration imported from {import_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to import configuration: {e}")
            return False
    
    def get_sections(self) -> List[str]:
        """Get list of configuration sections."""
        config_dict = asdict(self.config)
        return list(config_dict.keys())
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """Get entire configuration section."""
        config_dict = asdict(self.config)
        return config_dict.get(section, {})
    
    def update_section(self, section: str, data: Dict[str, Any], save: bool = True):
        """Update entire configuration section."""
        config_dict = asdict(self.config)
        if section in config_dict:
            config_dict[section].update(data)
            self.config = LumoraConfig(**config_dict)
            
            if save:
                self.save()
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get summary of current configuration."""
        return {
            'app_name': self.config.app_name,
            'version': self.config.version,
            'debug_mode': self.config.debug_mode,
            'privacy_level': self.config.privacy_level,
            'local_ai_enabled': self.config.local_ai_enabled,
            'automation_enabled': self.config.automation_enabled,
            'total_settings': len(asdict(self.config)),
            'user_preferences_count': len(self.user_preferences),
            'runtime_overrides_count': len(self.runtime_overrides)
        }
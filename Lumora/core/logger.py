"""
LUMORA Logging System

Privacy-aware logging system with multiple output formats,
log rotation, and configurable privacy levels.
"""

import logging
import logging.handlers
import os
import sys
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import threading

class PrivacyLogFilter(logging.Filter):
    """Filter sensitive information from log messages."""
    
    def __init__(self, privacy_guardian=None):
        super().__init__()
        self.privacy_guardian = privacy_guardian
        self.sensitive_patterns = [
            r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',  # Credit cards
            r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
            r'\bpassword[:\s=]+\S+',  # Passwords
            r'\btoken[:\s=]+\S+',     # Tokens
            r'\bapi[_-]?key[:\s=]+\S+',  # API keys
        ]
    
    def filter(self, record):
        """Filter sensitive information from log record."""
        if self.privacy_guardian and self.privacy_guardian.is_private_mode():
            # In private mode, only allow system logs
            if record.levelno < logging.WARNING:
                return False
        
        # Filter sensitive patterns from message
        if hasattr(record, 'msg') and isinstance(record.msg, str):
            import re
            filtered_msg = record.msg
            for pattern in self.sensitive_patterns:
                filtered_msg = re.sub(pattern, '[REDACTED]', filtered_msg, flags=re.IGNORECASE)
            record.msg = filtered_msg
        
        return True

class LumoraFormatter(logging.Formatter):
    """Custom formatter for Lumora logs."""
    
    def __init__(self, include_context=True, privacy_mode=False):
        self.include_context = include_context
        self.privacy_mode = privacy_mode
        
        # Color codes for console output
        self.colors = {
            'DEBUG': '\033[36m',    # Cyan
            'INFO': '\033[32m',     # Green
            'WARNING': '\033[33m',  # Yellow
            'ERROR': '\033[31m',    # Red
            'CRITICAL': '\033[35m', # Magenta
            'RESET': '\033[0m'      # Reset
        }
        
        format_string = self._build_format_string()
        super().__init__(format_string)
    
    def _build_format_string(self):
        """Build format string based on configuration."""
        if self.privacy_mode:
            return '%(asctime)s | %(levelname)s | %(name)s | [PRIVACY MODE]'
        
        base_format = '%(asctime)s | %(levelname)s | %(name)s'
        
        if self.include_context:
            base_format += ' | %(funcName)s:%(lineno)d'
        
        base_format += ' | %(message)s'
        return base_format
    
    def format(self, record):
        """Format log record with optional colors."""
        if hasattr(record, 'color') and record.color:
            # Add colors for console output
            levelname = record.levelname
            if levelname in self.colors:
                record.levelname = f"{self.colors[levelname]}{levelname}{self.colors['RESET']}"
        
        return super().format(record)

class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""
    
    def format(self, record):
        """Format record as JSON."""
        log_data = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'thread': record.thread,
            'process': record.process
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        # Add custom fields
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                          'filename', 'module', 'exc_info', 'exc_text', 'stack_info',
                          'lineno', 'funcName', 'created', 'msecs', 'relativeCreated',
                          'thread', 'threadName', 'processName', 'process', 'message']:
                log_data[key] = value
        
        return json.dumps(log_data)

class LumoraLogger:
    """
    Advanced logging system for Lumora with privacy controls,
    multiple outputs, and structured logging.
    """
    
    def __init__(self, config_manager=None, privacy_guardian=None):
        self.config = config_manager
        self.privacy = privacy_guardian
        self.loggers = {}
        self.handlers = {}
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)
        
        # Logging statistics
        self.stats = {
            'total_logs': 0,
            'logs_by_level': {'DEBUG': 0, 'INFO': 0, 'WARNING': 0, 'ERROR': 0, 'CRITICAL': 0},
            'start_time': time.time(),
            'last_log_time': 0
        }
        
        # Thread safety
        self._lock = threading.Lock()
        
        self._setup_root_logger()
    
    def _setup_root_logger(self):
        """Setup root logger configuration."""
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        
        # Clear existing handlers
        root_logger.handlers.clear()
        
        # Setup handlers
        self._setup_console_handler()
        self._setup_file_handlers()
        
        # Add privacy filter
        if self.privacy:
            privacy_filter = PrivacyLogFilter(self.privacy)
            for handler in root_logger.handlers:
                handler.addFilter(privacy_filter)
    
    def _setup_console_handler(self):
        """Setup console logging handler."""
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self._get_console_log_level())
        
        # Use colored formatter for console
        formatter = LumoraFormatter(
            include_context=self._get_config('logging.include_context', True),
            privacy_mode=self.privacy.is_private_mode() if self.privacy else False
        )
        console_handler.setFormatter(formatter)
        
        # Add custom filter to add color attribute
        def add_color_attribute(record):
            record.color = True
            return True
        
        console_handler.addFilter(add_color_attribute)
        
        logging.getLogger().addHandler(console_handler)
        self.handlers['console'] = console_handler
    
    def _setup_file_handlers(self):
        """Setup file logging handlers with rotation."""
        # Main log file with rotation
        main_log_file = self.log_dir / "lumora.log"
        file_handler = logging.handlers.RotatingFileHandler(
            main_log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(self._get_file_log_level())
        
        formatter = LumoraFormatter(
            include_context=True,
            privacy_mode=False
        )
        file_handler.setFormatter(formatter)
        
        logging.getLogger().addHandler(file_handler)
        self.handlers['file'] = file_handler
        
        # Error log file
        error_log_file = self.log_dir / "errors.log"
        error_handler = logging.handlers.RotatingFileHandler(
            error_log_file,
            maxBytes=5*1024*1024,  # 5MB
            backupCount=3
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        
        logging.getLogger().addHandler(error_handler)
        self.handlers['error'] = error_handler
        
        # JSON structured log file
        json_log_file = self.log_dir / "lumora.json"
        json_handler = logging.handlers.RotatingFileHandler(
            json_log_file,
            maxBytes=20*1024*1024,  # 20MB
            backupCount=3
        )
        json_handler.setLevel(logging.INFO)
        json_handler.setFormatter(JSONFormatter())
        
        logging.getLogger().addHandler(json_handler)
        self.handlers['json'] = json_handler
    
    def _get_console_log_level(self):
        """Get console log level from configuration."""
        if self.config:
            level_str = self.config.get('logging.console_level', 'INFO')
        else:
            level_str = 'INFO'
        
        return getattr(logging, level_str.upper(), logging.INFO)
    
    def _get_file_log_level(self):
        """Get file log level from configuration."""
        if self.config:
            level_str = self.config.get('logging.file_level', 'DEBUG')
        else:
            level_str = 'DEBUG'
        
        return getattr(logging, level_str.upper(), logging.DEBUG)
    
    def _get_config(self, key, default):
        """Get configuration value."""
        if self.config:
            return self.config.get(key, default)
        return default
    
    def get_logger(self, name: str) -> logging.Logger:
        """Get or create logger for specific module."""
        if name not in self.loggers:
            logger = logging.getLogger(name)
            
            # Add custom log methods
            self._add_custom_methods(logger)
            
            self.loggers[name] = logger
        
        return self.loggers[name]
    
    def _add_custom_methods(self, logger):
        """Add custom logging methods to logger."""
        def log_context(level, message, context=None, **kwargs):
            """Log with additional context information."""
            extra = {'context': context or {}}
            extra.update(kwargs)
            logger.log(level, message, extra=extra)
        
        def log_performance(message, duration, **kwargs):
            """Log performance information."""
            extra = {'performance': True, 'duration': duration}
            extra.update(kwargs)
            logger.info(f"[PERF] {message} (took {duration:.3f}s)", extra=extra)
        
        def log_privacy(message, **kwargs):
            """Log privacy-related events."""
            extra = {'privacy': True}
            extra.update(kwargs)
            logger.warning(f"[PRIVACY] {message}", extra=extra)
        
        def log_security(message, **kwargs):
            """Log security-related events."""
            extra = {'security': True}
            extra.update(kwargs)
            logger.error(f"[SECURITY] {message}", extra=extra)
        
        def log_user_action(action, details=None, **kwargs):
            """Log user actions."""
            extra = {'user_action': True, 'action': action, 'details': details or {}}
            extra.update(kwargs)
            logger.info(f"[USER] {action}", extra=extra)
        
        def log_ai_interaction(message, model=None, tokens=None, **kwargs):
            """Log AI interactions."""
            extra = {'ai_interaction': True, 'model': model, 'tokens': tokens}
            extra.update(kwargs)
            logger.info(f"[AI] {message}", extra=extra)
        
        # Add methods to logger
        logger.log_context = log_context
        logger.log_performance = log_performance
        logger.log_privacy = log_privacy
        logger.log_security = log_security
        logger.log_user_action = log_user_action
        logger.log_ai_interaction = log_ai_interaction
    
    def update_stats(self, record):
        """Update logging statistics."""
        with self._lock:
            self.stats['total_logs'] += 1
            self.stats['logs_by_level'][record.levelname] += 1
            self.stats['last_log_time'] = time.time()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get logging statistics."""
        with self._lock:
            uptime = time.time() - self.stats['start_time']
            return {
                **self.stats.copy(),
                'uptime_seconds': uptime,
                'logs_per_minute': self.stats['total_logs'] / (uptime / 60) if uptime > 0 else 0
            }
    
    def set_privacy_mode(self, enabled: bool):
        """Enable or disable privacy mode for logging."""
        for handler in self.handlers.values():
            if hasattr(handler, 'formatter'):
                handler.formatter.privacy_mode = enabled
    
    def rotate_logs(self):
        """Manually trigger log rotation."""
        for name, handler in self.handlers.items():
            if hasattr(handler, 'doRollover'):
                handler.doRollover()
                logging.getLogger().info(f"Log rotation triggered for {name}")
    
    def clean_old_logs(self, days: int = 30):
        """Clean log files older than specified days."""
        import glob
        import datetime
        
        cutoff_time = time.time() - (days * 24 * 60 * 60)
        
        log_patterns = [
            str(self.log_dir / "*.log*"),
            str(self.log_dir / "*.json*")
        ]
        
        removed_count = 0
        for pattern in log_patterns:
            for log_file in glob.glob(pattern):
                try:
                    if os.path.getmtime(log_file) < cutoff_time:
                        os.remove(log_file)
                        removed_count += 1
                except Exception as e:
                    logging.getLogger().warning(f"Failed to remove old log file {log_file}: {e}")
        
        if removed_count > 0:
            logging.getLogger().info(f"Cleaned {removed_count} old log files")
    
    def export_logs(self, output_file: str, start_time: Optional[float] = None, 
                   end_time: Optional[float] = None, level: str = 'INFO') -> bool:
        """Export logs to file with optional filtering."""
        try:
            log_level = getattr(logging, level.upper(), logging.INFO)
            
            with open(output_file, 'w', encoding='utf-8') as out_file:
                # Read from JSON log file for structured export
                json_log_file = self.log_dir / "lumora.json"
                
                if json_log_file.exists():
                    with open(json_log_file, 'r', encoding='utf-8') as json_file:
                        for line in json_file:
                            try:
                                log_entry = json.loads(line.strip())
                                
                                # Apply time filtering
                                if start_time or end_time:
                                    log_time = time.mktime(
                                        datetime.fromisoformat(log_entry['timestamp']).timetuple()
                                    )
                                    if start_time and log_time < start_time:
                                        continue
                                    if end_time and log_time > end_time:
                                        continue
                                
                                # Apply level filtering
                                if log_level <= getattr(logging, log_entry['level'], logging.INFO):
                                    out_file.write(json.dumps(log_entry) + '\n')
                                    
                            except json.JSONDecodeError:
                                continue
                
                logging.getLogger().info(f"Logs exported to {output_file}")
                return True
                
        except Exception as e:
            logging.getLogger().error(f"Failed to export logs: {e}")
            return False
    
    def get_recent_logs(self, count: int = 100, level: str = 'INFO') -> List[Dict[str, Any]]:
        """Get recent log entries."""
        log_level = getattr(logging, level.upper(), logging.INFO)
        recent_logs = []
        
        try:
            json_log_file = self.log_dir / "lumora.json"
            
            if json_log_file.exists():
                with open(json_log_file, 'r', encoding='utf-8') as json_file:
                    lines = json_file.readlines()
                    
                    # Get last N lines
                    for line in lines[-count:]:
                        try:
                            log_entry = json.loads(line.strip())
                            if log_level <= getattr(logging, log_entry['level'], logging.INFO):
                                recent_logs.append(log_entry)
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            logging.getLogger().error(f"Failed to get recent logs: {e}")
        
        return recent_logs
    
    def search_logs(self, query: str, case_sensitive: bool = False) -> List[Dict[str, Any]]:
        """Search logs for specific content."""
        results = []
        
        try:
            json_log_file = self.log_dir / "lumora.json"
            
            if json_log_file.exists():
                with open(json_log_file, 'r', encoding='utf-8') as json_file:
                    for line in json_file:
                        try:
                            log_entry = json.loads(line.strip())
                            message = log_entry.get('message', '')
                            
                            if case_sensitive:
                                if query in message:
                                    results.append(log_entry)
                            else:
                                if query.lower() in message.lower():
                                    results.append(log_entry)
                                    
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            logging.getLogger().error(f"Failed to search logs: {e}")
        
        return results
    
    def shutdown(self):
        """Shutdown logging system gracefully."""
        logging.getLogger().info("Shutting down logging system")
        
        # Close all handlers
        for handler in logging.getLogger().handlers:
            handler.close()
        
        # Clear handlers
        logging.getLogger().handlers.clear()

# Global logger instance
_lumora_logger = None

def setup_logging(level='INFO', config_manager=None, privacy_guardian=None):
    """Setup Lumora logging system."""
    global _lumora_logger
    
    _lumora_logger = LumoraLogger(config_manager, privacy_guardian)
    
    # Set root logger level
    logging.getLogger().setLevel(getattr(logging, level.upper(), logging.INFO))
    
    return _lumora_logger

def get_logger(name: str) -> logging.Logger:
    """Get logger instance."""
    if _lumora_logger:
        return _lumora_logger.get_logger(name)
    else:
        return logging.getLogger(name)

def get_logging_stats() -> Dict[str, Any]:
    """Get logging statistics."""
    if _lumora_logger:
        return _lumora_logger.get_stats()
    return {}

def set_privacy_mode(enabled: bool):
    """Set privacy mode for logging."""
    if _lumora_logger:
        _lumora_logger.set_privacy_mode(enabled)

def cleanup_logs(days: int = 30):
    """Clean up old log files."""
    if _lumora_logger:
        _lumora_logger.clean_old_logs(days)
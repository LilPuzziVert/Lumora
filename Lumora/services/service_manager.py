"""
LUMORA Service Manager

Handles Windows service installation, management, and lifecycle.
Allows Lumora to run as a background system service.
"""

import asyncio
import logging
import os
import sys
import time
import subprocess
from typing import Optional
from pathlib import Path

class ServiceManager:
    """
    Windows service management for Lumora.
    
    Handles installation, removal, and control of Lumora
    as a Windows background service.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.service_name = "LumoraService"
        self.service_display_name = "Lumora AI Assistant"
        self.service_description = "Lumora - Full-Access AI OS Companion"
        
        # Service paths
        self.script_dir = Path(__file__).parent.parent
        self.service_script = self.script_dir / "src" / "main.py"
        
    async def install_service(self) -> bool:
        """Install Lumora as a Windows service."""
        try:
            self.logger.info("Installing Lumora as Windows service...")
            
            # Create service installation script
            await self._create_service_script()
            
            # Use sc.exe to create service
            cmd = [
                "sc.exe", "create", self.service_name,
                f"binpath={sys.executable} {self.service_script} service",
                f"displayname={self.service_display_name}",
                "start=auto",
                "type=own"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Set service description
                await self._set_service_description()
                
                # Configure service recovery
                await self._configure_service_recovery()
                
                self.logger.info("Lumora service installed successfully")
                return True
            else:
                self.logger.error(f"Service installation failed: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to install service: {e}")
            return False
    
    async def uninstall_service(self) -> bool:
        """Uninstall Lumora Windows service."""
        try:
            self.logger.info("Uninstalling Lumora service...")
            
            # Stop service first
            await self.stop_service()
            
            # Delete service
            cmd = ["sc.exe", "delete", self.service_name]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.logger.info("Lumora service uninstalled successfully")
                return True
            else:
                self.logger.error(f"Service uninstallation failed: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to uninstall service: {e}")
            return False
    
    async def start_service(self) -> bool:
        """Start the Lumora service."""
        try:
            cmd = ["sc.exe", "start", self.service_name]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.logger.info("Lumora service started")
                return True
            else:
                self.logger.error(f"Failed to start service: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to start service: {e}")
            return False
    
    async def stop_service(self) -> bool:
        """Stop the Lumora service."""
        try:
            cmd = ["sc.exe", "stop", self.service_name]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.logger.info("Lumora service stopped")
                return True
            else:
                # Service might not be running
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to stop service: {e}")
            return False
    
    async def get_service_status(self) -> Optional[str]:
        """Get current service status."""
        try:
            cmd = ["sc.exe", "query", self.service_name]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                output = result.stdout
                if "RUNNING" in output:
                    return "running"
                elif "STOPPED" in output:
                    return "stopped"
                elif "PENDING" in output:
                    return "pending"
                else:
                    return "unknown"
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to get service status: {e}")
            return None
    
    async def _create_service_script(self):
        """Create Windows service wrapper script."""
        service_script_content = f'''
import sys
import time
import logging
import win32serviceutil
import win32service
import win32event
import servicemanager
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

class LumoraService(win32serviceutil.ServiceFramework):
    _svc_name_ = "{self.service_name}"
    _svc_display_name_ = "{self.service_display_name}"
    _svc_description_ = "{self.service_description}"
    
    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.running = True
        
    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.running = False
        
    def SvcDoRun(self):
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, '')
        )
        
        try:
            from src.main import LumoraLauncher
            import asyncio
            
            # Run Lumora in service mode
            launcher = LumoraLauncher()
            asyncio.run(launcher.run_service_mode())
            
        except Exception as e:
            servicemanager.LogErrorMsg(f"Service error: {{e}}")
        
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STOPPED,
            (self._svc_name_, '')
        )

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(LumoraService)
'''
        
        service_file = self.script_dir / "lumora_service.py"
        with open(service_file, 'w', encoding='utf-8') as f:
            f.write(service_script_content)
    
    async def _set_service_description(self):
        """Set service description."""
        try:
            cmd = [
                "sc.exe", "description", self.service_name,
                f'"{self.service_description}"'
            ]
            subprocess.run(cmd, capture_output=True, text=True)
        except Exception as e:
            self.logger.warning(f"Failed to set service description: {e}")
    
    async def _configure_service_recovery(self):
        """Configure service recovery options."""
        try:
            # Configure service to restart on failure
            cmd = [
                "sc.exe", "failure", self.service_name,
                "reset=86400",  # Reset failure count after 24 hours
                "actions=restart/30000/restart/60000/restart/120000"  # Restart with delays
            ]
            subprocess.run(cmd, capture_output=True, text=True)
        except Exception as e:
            self.logger.warning(f"Failed to configure service recovery: {e}")
    
    def is_admin(self) -> bool:
        """Check if running with administrator privileges."""
        try:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
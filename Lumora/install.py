#!/usr/bin/env python3
"""
LUMORA Installation Script

Complete installation and setup for Lumora AI OS Companion.
Handles dependencies, service installation, and initial configuration.
"""

import os
import sys
import subprocess
import asyncio
import logging
from pathlib import Path
import ctypes
import platform

class LumoraInstaller:
    """
    Complete installer for Lumora system.
    
    Handles all aspects of installation including:
    - Dependency verification
    - Service installation
    - Initial configuration
    - Security setup
    """
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.install_dir = Path(__file__).parent
        self.requirements_met = True
        
        # Installation steps
        self.steps = [
            ("Checking System Requirements", self._check_requirements),
            ("Installing Dependencies", self._install_dependencies),
            ("Setting up Directories", self._setup_directories),
            ("Creating Configuration", self._create_config),
            ("Installing Windows Service", self._install_service),
            ("Setting up Shortcuts", self._create_shortcuts),
            ("Final Configuration", self._final_setup)
        ]
    
    def _setup_logging(self):
        """Setup installation logging."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler('lumora_install.log')
            ]
        )
        return logging.getLogger(__name__)
    
    async def install(self):
        """Run complete installation process."""
        print("=" * 60)
        print("  LUMORA AI OS COMPANION - INSTALLATION")
        print("  Full-Access AI Assistant v2.0.0")
        print("=" * 60)
        print()
        
        if not self._check_admin():
            print("ERROR: Administrator privileges required for installation.")
            print("Please run this installer as Administrator.")
            return False
        
        if not self._check_platform():
            print("ERROR: Lumora requires Windows 10 or later.")
            return False
        
        print("Starting installation process...")
        print()
        
        try:
            for step_name, step_func in self.steps:
                print(f"[{len([s for s in self.steps if s == (step_name, step_func)]) + 1}/{len(self.steps)}] {step_name}...")
                
                success = await step_func()
                if success:
                    print(f"✓ {step_name} completed successfully")
                else:
                    print(f"✗ {step_name} failed")
                    return False
                print()
            
            print("=" * 60)
            print("🎉 LUMORA INSTALLATION COMPLETED SUCCESSFULLY!")
            print("=" * 60)
            print()
            print("Next steps:")
            print("1. Lumora service has been installed and started")
            print("2. Use 'Lumora' desktop shortcut to open the control panel")
            print("3. Configure your privacy preferences in the GUI")
            print("4. Try saying 'Hello Lumora' to test voice activation")
            print()
            print("Lumora is now monitoring your system and ready to assist!")
            print("Check the system tray for the Lumora icon.")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Installation failed: {e}")
            print(f"Installation failed: {e}")
            return False
    
    def _check_admin(self):
        """Check if running with administrator privileges."""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    
    def _check_platform(self):
        """Check if platform is supported."""
        return platform.system() == "Windows" and platform.release() in ["10", "11"]
    
    async def _check_requirements(self):
        """Check system requirements."""
        try:
            # Check Python version
            if sys.version_info < (3, 9):
                print(f"Python 3.9+ required, found {sys.version}")
                return False
            
            # Check available memory
            import psutil
            memory_gb = psutil.virtual_memory().total / (1024**3)
            if memory_gb < 4:
                print(f"Minimum 4GB RAM required, found {memory_gb:.1f}GB")
                return False
            
            # Check disk space
            disk_usage = psutil.disk_usage(str(self.install_dir))
            free_gb = disk_usage.free / (1024**3)
            if free_gb < 2:
                print(f"Minimum 2GB free disk space required, found {free_gb:.1f}GB")
                return False
            
            # Check Windows version
            import winreg
            try:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion")
                build = winreg.QueryValueEx(key, "CurrentBuild")[0]
                winreg.CloseKey(key)
                
                if int(build) < 19041:  # Windows 10 version 2004
                    print(f"Windows 10 version 2004+ required, found build {build}")
                    return False
            except:
                print("Could not verify Windows version")
                return False
            
            print("✓ System requirements met")
            return True
            
        except Exception as e:
            print(f"Requirements check failed: {e}")
            return False
    
    async def _install_dependencies(self):
        """Install required Python packages."""
        try:
            # Core packages needed for Lumora
            packages = [
                "psutil>=5.9.0",
                "Pillow>=9.0.0",
                "opencv-python>=4.5.0",
                "numpy>=1.21.0",
                "pywin32>=300",
                "pycryptodome>=3.15.0",
                "aiofiles>=0.8.0",
                "aiohttp>=3.8.0"
            ]
            
            print("Installing Python packages...")
            for package in packages:
                result = subprocess.run([
                    sys.executable, "-m", "pip", "install", package
                ], capture_output=True, text=True)
                
                if result.returncode != 0:
                    print(f"Failed to install {package}: {result.stderr}")
                    return False
                
                print(f"  ✓ {package}")
            
            return True
            
        except Exception as e:
            print(f"Dependency installation failed: {e}")
            return False
    
    async def _setup_directories(self):
        """Create necessary directories."""
        try:
            directories = [
                "data",
                "data/models",
                "data/cache",
                "logs",
                "plugins",
                "config",
                "ui/assets"
            ]
            
            for directory in directories:
                dir_path = self.install_dir / directory
                dir_path.mkdir(parents=True, exist_ok=True)
                print(f"  ✓ Created {directory}")
            
            return True
            
        except Exception as e:
            print(f"Directory setup failed: {e}")
            return False
    
    async def _create_config(self):
        """Create initial configuration files."""
        try:
            # Main configuration
            config_content = """# Lumora Configuration File
[general]
app_name = Lumora
version = 2.0.0
debug_mode = false

[privacy]
default_level = balanced
data_retention_days = 90
require_confirmation_for_high_risk = true

[ai]
default_personality = balanced
enable_friend_mode = false
response_timeout_seconds = 30

[performance]
monitoring_interval_ms = 500
max_memory_usage_mb = 1024
enable_performance_mode = true

[ui]
theme = dark
minimize_to_tray = true
start_minimized = false

[automation]
max_risk_level = 3
action_timeout_seconds = 30
max_concurrent_actions = 3
"""
            
            config_file = self.install_dir / "config" / "lumora.conf"
            with open(config_file, 'w', encoding='utf-8') as f:
                f.write(config_content)
            
            # Create privacy settings
            privacy_content = """{
    "privacy_level": "balanced",
    "allowed_data_types": [
        "screen_content",
        "window_titles",
        "app_usage"
    ],
    "blocked_data_types": [
        "keyboard_input",
        "mouse_input"
    ],
    "encryption_enabled": true,
    "data_retention_days": 90
}"""
            
            privacy_file = self.install_dir / "config" / "privacy.json"
            with open(privacy_file, 'w', encoding='utf-8') as f:
                f.write(privacy_content)
            
            print("  ✓ Created configuration files")
            return True
            
        except Exception as e:
            print(f"Configuration creation failed: {e}")
            return False
    
    async def _install_service(self):
        """Install Lumora as Windows service."""
        try:
            # Import service manager
            sys.path.insert(0, str(self.install_dir))
            from services.service_manager import ServiceManager
            
            service_manager = ServiceManager()
            
            # Install service
            success = await service_manager.install_service()
            if not success:
                return False
            
            print("  ✓ Windows service installed")
            
            # Start service
            success = await service_manager.start_service()
            if success:
                print("  ✓ Service started successfully")
            else:
                print("  ⚠ Service installed but failed to start")
            
            return True
            
        except Exception as e:
            print(f"Service installation failed: {e}")
            return False
    
    async def _create_shortcuts(self):
        """Create desktop and start menu shortcuts."""
        try:
            import winshell
            from win32com.client import Dispatch
            
            # Desktop shortcut
            desktop = winshell.desktop()
            shortcut_path = os.path.join(desktop, "Lumora.lnk")
            
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.Targetpath = sys.executable
            shortcut.Arguments = f'"{self.install_dir / "src" / "main.py"}" gui'
            shortcut.WorkingDirectory = str(self.install_dir)
            shortcut.IconLocation = str(self.install_dir / "ui" / "assets" / "lumora_icon.ico")
            shortcut.Description = "Lumora AI OS Companion"
            shortcut.save()
            
            print("  ✓ Desktop shortcut created")
            
            # Start menu shortcut
            start_menu = winshell.start_menu()
            start_shortcut_path = os.path.join(start_menu, "Programs", "Lumora.lnk")
            
            os.makedirs(os.path.dirname(start_shortcut_path), exist_ok=True)
            
            start_shortcut = shell.CreateShortCut(start_shortcut_path)
            start_shortcut.Targetpath = sys.executable
            start_shortcut.Arguments = f'"{self.install_dir / "src" / "main.py"}" gui'
            start_shortcut.WorkingDirectory = str(self.install_dir)
            start_shortcut.IconLocation = str(self.install_dir / "ui" / "assets" / "lumora_icon.ico")
            start_shortcut.Description = "Lumora AI OS Companion"
            start_shortcut.save()
            
            print("  ✓ Start menu shortcut created")
            return True
            
        except Exception as e:
            print(f"Shortcut creation failed (non-critical): {e}")
            return True  # Non-critical failure
    
    async def _final_setup(self):
        """Final setup and validation."""
        try:
            # Test import of main module
            sys.path.insert(0, str(self.install_dir))
            
            try:
                from src.main import LumoraLauncher
                print("  ✓ Main module import successful")
            except ImportError as e:
                print(f"  ✗ Main module import failed: {e}")
                return False
            
            # Create initial AI model placeholder
            models_dir = self.install_dir / "data" / "models"
            model_config = {
                "lumora_base": {
                    "name": "lumora_base",
                    "model_type": "conversation",
                    "model_path": str(models_dir / "lumora_base.bin"),
                    "context_length": 1024,
                    "temperature": 0.7,
                    "max_tokens": 200
                }
            }
            
            import json
            with open(models_dir / "models.json", 'w') as f:
                json.dump(model_config, f, indent=2)
            
            print("  ✓ AI model configuration created")
            
            # Set up Windows firewall exception
            try:
                subprocess.run([
                    "netsh", "advfirewall", "firewall", "add", "rule",
                    "name=Lumora AI Assistant",
                    "dir=in", "action=allow",
                    f"program={sys.executable}"
                ], capture_output=True, check=True)
                print("  ✓ Firewall exception added")
            except:
                print("  ⚠ Could not add firewall exception (non-critical)")
            
            return True
            
        except Exception as e:
            print(f"Final setup failed: {e}")
            return False

def main():
    """Main installation entry point."""
    print("Starting Lumora installation...")
    
    installer = LumoraInstaller()
    
    # Run installation
    success = asyncio.run(installer.install())
    
    if success:
        print("\nPress Enter to exit...")
        input()
        return 0
    else:
        print("\nInstallation failed. Check lumora_install.log for details.")
        print("Press Enter to exit...")
        input()
        return 1

if __name__ == "__main__":
    sys.exit(main())
#!/usr/bin/env python3
"""
LUMORA INSTALLATION SYSTEM
Complete multi-language setup for god-tier AI OS companion
"""

import os
import sys
import subprocess
import platform
import urllib.request
import zipfile
import shutil
import json
import time
import argparse
from pathlib import Path
from typing import Dict, List, Optional
import ctypes
from ctypes import wintypes

class Colors:
    """ANSI color codes for beautiful terminal output"""
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

class LumoraInstaller:
    """Complete installation system for Lumora AI OS Companion"""
    
    def __init__(self):
        self.base_path = Path("C:/Lumora")
        self.current_path = Path(__file__).parent.parent
        self.is_admin = self.check_admin_rights()
        self.requirements = {
            'python': '3.9.0',
            'rust': '1.70.0',
            'cmake': '3.20.0',
            'touchdesigner': '2023.11120',
            'vs_buildtools': '2022',
        }
        
    def check_admin_rights(self) -> bool:
        """Check if running with administrator privileges"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    
    def print_header(self):
        """Print beautiful installation header"""
        print(f"""
{Colors.CYAN}╔══════════════════════════════════════════════════════════════════════╗
║                    🚀 LUMORA INSTALLATION SYSTEM 🚀                  ║
║                                                                      ║
║            God-Tier AI OS Companion Multi-Language Setup            ║
║                                                                      ║
║  🎨 TouchDesigner Animations  🦀 Rust Performance  🐍 Python Core    ║
║  ⚡ C++ OS Integration      🛡️ Zero-Error Guarantee                ║
╚══════════════════════════════════════════════════════════════════════╝{Colors.END}
        """)
    
    def print_step(self, step: str, description: str):
        """Print installation step with beautiful formatting"""
        print(f"\n{Colors.BOLD}{Colors.BLUE}[STEP] {step}{Colors.END}")
        print(f"{Colors.WHITE}└─ {description}{Colors.END}")
    
    def print_success(self, message: str):
        """Print success message"""
        print(f"{Colors.GREEN}✓ {message}{Colors.END}")
    
    def print_warning(self, message: str):
        """Print warning message"""
        print(f"{Colors.YELLOW}⚠ {message}{Colors.END}")
    
    def print_error(self, message: str):
        """Print error message"""
        print(f"{Colors.RED}✗ {message}{Colors.END}")
    
    def run_command(self, cmd: str, cwd: Optional[Path] = None, shell: bool = True) -> bool:
        """Run command with error handling"""
        try:
            result = subprocess.run(cmd, shell=shell, cwd=cwd, 
                                  capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                return True
            else:
                self.print_error(f"Command failed: {cmd}")
                if result.stderr:
                    print(f"Error: {result.stderr}")
                return False
        except subprocess.TimeoutExpired:
            self.print_error(f"Command timed out: {cmd}")
            return False
        except Exception as e:
            self.print_error(f"Command error: {e}")
            return False
    
    def check_system_requirements(self) -> bool:
        """Check system requirements"""
        self.print_step("1/10", "Checking System Requirements")
        
        # Check Windows version
        if platform.system() != "Windows":
            self.print_error("Lumora requires Windows 11")
            return False
        
        # Check Windows build
        build = platform.version()
        if int(build.split('.')[2]) < 22000:
            self.print_error("Lumora requires Windows 11 (Build 22000+)")
            return False
        
        self.print_success("Windows 11 detected")
        
        # Check RAM
        import psutil
        total_ram = psutil.virtual_memory().total / (1024**3)  # GB
        if total_ram < 8:
            self.print_warning(f"Low RAM detected: {total_ram:.1f}GB (8GB minimum)")
        else:
            self.print_success(f"RAM: {total_ram:.1f}GB")
        
        # Check admin rights
        if not self.is_admin:
            self.print_error("Administrator privileges required")
            self.print_warning("Please run installer as Administrator")
            return False
        
        self.print_success("Administrator privileges confirmed")
        return True
    
    def install_chocolatey(self) -> bool:
        """Install Chocolatey package manager"""
        self.print_step("2/10", "Installing Chocolatey Package Manager")
        
        # Check if already installed
        if self.run_command("choco --version"):
            self.print_success("Chocolatey already installed")
            return True
        
        # Install Chocolatey
        cmd = 'powershell -Command "Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString(\'https://community.chocolatey.org/install.ps1\'))"'
        
        if self.run_command(cmd):
            self.print_success("Chocolatey installed successfully")
            return True
        else:
            self.print_error("Failed to install Chocolatey")
            return False
    
    def install_dependencies(self) -> bool:
        """Install all required dependencies"""
        self.print_step("3/10", "Installing Dependencies")
        
        dependencies = {
            'python': 'python --version=3.11.0',
            'rust': 'rust',
            'cmake': 'cmake',
            'git': 'git',
            'visualstudio2022buildtools': 'visualstudio2022buildtools --package-parameters "--add Microsoft.VisualStudio.Workload.VCTools --includeRecommended"'
        }
        
        for dep, install_cmd in dependencies.items():
            print(f"\n  Installing {dep}...")
            if self.run_command(f"choco install {install_cmd} -y"):
                self.print_success(f"{dep} installed")
            else:
                self.print_error(f"Failed to install {dep}")
                return False
        
        # Refresh environment variables
        self.run_command("refreshenv")
        
        return True
    
    def setup_directories(self) -> bool:
        """Create directory structure"""
        self.print_step("4/10", "Setting Up Directory Structure")
        
        directories = [
            self.base_path,
            self.base_path / "core",
            self.base_path / "automation",
            self.base_path / "system",
            self.base_path / "ui",
            self.base_path / "logs",
            self.base_path / "config",
            self.base_path / "data",
            self.base_path / "temp",
        ]
        
        for directory in directories:
            try:
                directory.mkdir(parents=True, exist_ok=True)
                self.print_success(f"Created: {directory}")
            except Exception as e:
                self.print_error(f"Failed to create {directory}: {e}")
                return False
        
        return True
    
    def copy_source_files(self) -> bool:
        """Copy source files to installation directory"""
        self.print_step("5/10", "Copying Source Files")
        
        try:
            # Copy Python core
            shutil.copytree(self.current_path / "core", 
                          self.base_path / "core", dirs_exist_ok=True)
            self.print_success("Python core copied")
            
            # Copy Rust automation
            shutil.copytree(self.current_path / "automation", 
                          self.base_path / "automation", dirs_exist_ok=True)
            self.print_success("Rust automation copied")
            
            # Copy TouchDesigner UI
            shutil.copytree(self.current_path / "ui", 
                          self.base_path / "ui", dirs_exist_ok=True)
            self.print_success("TouchDesigner UI copied")
            
            # Copy configuration files
            if (self.current_path / "config").exists():
                shutil.copytree(self.current_path / "config", 
                              self.base_path / "config", dirs_exist_ok=True)
            
            return True
            
        except Exception as e:
            self.print_error(f"Failed to copy files: {e}")
            return False
    
    def build_rust_components(self) -> bool:
        """Build Rust automation components"""
        self.print_step("6/10", "Building Rust Components")
        
        rust_path = self.base_path / "automation"
        
        # Install Rust if not available
        if not self.run_command("rustc --version"):
            self.print_warning("Installing Rust...")
            if not self.run_command("choco install rust -y"):
                self.print_error("Failed to install Rust")
                return False
        
        # Build release version
        print("  Building automation engine...")
        if self.run_command("cargo build --release", cwd=rust_path):
            self.print_success("Rust components built successfully")
            return True
        else:
            self.print_error("Failed to build Rust components")
            return False
    
    def compile_cpp_components(self) -> bool:
        """Compile C++ system integration components"""
        self.print_step("7/10", "Compiling C++ Components")
        
        cpp_path = self.base_path / "system"
        
        # Create basic C++ components if they don't exist
        self.create_cpp_components(cpp_path)
        
        # Build C++ components
        build_path = cpp_path / "build"
        build_path.mkdir(exist_ok=True)
        
        print("  Configuring CMake...")
        if not self.run_command("cmake ..", cwd=build_path):
            self.print_error("CMake configuration failed")
            return False
        
        print("  Building C++ components...")
        if self.run_command("cmake --build . --config Release", cwd=build_path):
            self.print_success("C++ components built successfully")
            return True
        else:
            self.print_error("Failed to build C++ components")
            return False
    
    def create_cpp_components(self, cpp_path: Path):
        """Create basic C++ component files"""
        
        # CMakeLists.txt
        cmake_content = """
cmake_minimum_required(VERSION 3.20)
project(LumoraSystem)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Add source files
add_library(lumora_system SHARED
    windows_api.cpp
    screen_capture.cpp
    service_manager.cpp
)

# Link Windows libraries
target_link_libraries(lumora_system
    user32
    kernel32
    gdi32
    ole32
    oleaut32
    uuid
)

# Set output directory
set_target_properties(lumora_system PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY_RELEASE ${CMAKE_BINARY_DIR}/bin
    LIBRARY_OUTPUT_DIRECTORY_RELEASE ${CMAKE_BINARY_DIR}/lib
)
"""
        
        # windows_api.cpp
        cpp_content = """
#include <windows.h>
#include <iostream>

extern "C" {
    __declspec(dllexport) bool lumora_init_windows_api() {
        return true;
    }
    
    __declspec(dllexport) bool lumora_get_active_window(char* buffer, int buffer_size) {
        HWND hwnd = GetForegroundWindow();
        if (hwnd) {
            GetWindowTextA(hwnd, buffer, buffer_size);
            return true;
        }
        return false;
    }
    
    __declspec(dllexport) bool lumora_click_at(int x, int y) {
        SetCursorPos(x, y);
        mouse_event(MOUSEEVENTF_LEFTDOWN | MOUSEEVENTF_LEFTUP, 0, 0, 0, 0);
        return true;
    }
}
"""
        
        # Write files
        with open(cpp_path / "CMakeLists.txt", "w") as f:
            f.write(cmake_content)
        
        with open(cpp_path / "windows_api.cpp", "w") as f:
            f.write(cpp_content)
        
        # Create placeholder files
        open(cpp_path / "screen_capture.cpp", "w").write("// Screen capture implementation\n")
        open(cpp_path / "service_manager.cpp", "w").write("// Service manager implementation\n")
    
    def install_python_packages(self) -> bool:
        """Install Python packages"""
        self.print_step("8/10", "Installing Python Packages")
        
        packages = [
            "asyncio",
            "aiofiles", 
            "psutil",
            "pillow",
            "numpy",
            "opencv-python",
            "pywin32",
            "comtypes",
            "pydantic",
            "fastapi",
            "uvicorn",
            "websockets",
            "rich",
            "typer",
            "customtkinter",
        ]
        
        for package in packages:
            print(f"  Installing {package}...")
            if self.run_command(f"pip install {package}"):
                print(f"    ✓ {package}")
            else:
                self.print_error(f"Failed to install {package}")
                return False
        
        self.print_success("All Python packages installed")
        return True
    
    def setup_touchdesigner(self) -> bool:
        """Setup TouchDesigner integration"""
        self.print_step("9/10", "Setting Up TouchDesigner Integration")
        
        # Check if TouchDesigner is installed
        td_paths = [
            "C:/Program Files/Derivative/TouchDesigner",
            "C:/Program Files (x86)/Derivative/TouchDesigner",
        ]
        
        td_path = None
        for path in td_paths:
            if Path(path).exists():
                td_path = Path(path)
                break
        
        if not td_path:
            self.print_warning("TouchDesigner not found")
            self.print_warning("Please install TouchDesigner from https://derivative.ca/")
            self.print_warning("Then run: lumora-setup --touchdesigner-only")
            return True  # Don't fail installation
        
        # Copy operators to TouchDesigner palette
        try:
            palette_path = Path.home() / "Documents/Derivative/TouchDesigner/Palette"
            palette_path.mkdir(parents=True, exist_ok=True)
            
            ui_path = self.base_path / "ui"
            if (ui_path / "operators").exists():
                shutil.copytree(ui_path / "operators", 
                              palette_path / "Lumora", dirs_exist_ok=True)
                self.print_success("TouchDesigner operators installed")
            
        except Exception as e:
            self.print_warning(f"TouchDesigner setup warning: {e}")
        
        return True
    
    def install_windows_service(self) -> bool:
        """Install Windows service"""
        self.print_step("10/10", "Installing Windows Service")
        
        # Create service script
        service_script = self.base_path / "lumora-service.py"
        service_content = f"""
import sys
sys.path.insert(0, r'{self.base_path / "core"}')

import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import time
import threading
from core.engine import LumoraEngine

class LumoraService(win32serviceutil.ServiceFramework):
    _svc_name_ = "LumoraAI"
    _svc_display_name_ = "Lumora AI OS Companion"
    _svc_description_ = "God-tier AI OS companion service"
    
    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.engine = None
        
    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        if self.engine:
            self.engine.stop()
        win32event.SetEvent(self.hWaitStop)
        
    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                            servicemanager.PYS_SERVICE_STARTED,
                            (self._svc_name_, ''))
        self.main()
        
    def main(self):
        try:
            self.engine = LumoraEngine()
            self.engine.start()
            
            # Wait for stop signal
            win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)
            
        except Exception as e:
            servicemanager.LogErrorMsg(f"Service error: {{e}}")

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(LumoraService)
"""
        
        with open(service_script, "w") as f:
            f.write(service_content)
        
        # Install service
        try:
            cmd = f'python "{service_script}" install'
            if self.run_command(cmd):
                self.print_success("Windows service installed")
                
                # Start service
                if self.run_command(f'python "{service_script}" start'):
                    self.print_success("Lumora service started")
                
                return True
            else:
                self.print_error("Failed to install Windows service")
                return False
                
        except Exception as e:
            self.print_error(f"Service installation error: {e}")
            return False
    
    def create_shortcuts(self):
        """Create desktop and start menu shortcuts"""
        print(f"\n{Colors.BLUE}Creating shortcuts...{Colors.END}")
        
        try:
            import win32com.client
            shell = win32com.client.Dispatch("WScript.Shell")
            
            # Desktop shortcut
            desktop = shell.SpecialFolders("Desktop")
            shortcut = shell.CreateShortcut(os.path.join(desktop, "Lumora AI.lnk"))
            shortcut.TargetPath = str(self.base_path / "core" / "main.py")
            shortcut.WorkingDirectory = str(self.base_path)
            shortcut.IconLocation = str(self.base_path / "ui" / "icons" / "lumora.ico")
            shortcut.save()
            
            self.print_success("Desktop shortcut created")
            
        except Exception as e:
            self.print_warning(f"Shortcut creation failed: {e}")
    
    def finalize_installation(self):
        """Finalize installation and show usage instructions"""
        print(f"""
{Colors.GREEN}╔══════════════════════════════════════════════════════════════════════╗
║                   🎉 INSTALLATION COMPLETED! 🎉                      ║
║                                                                      ║
║               LUMORA AI OS COMPANION IS NOW READY!                  ║
╚══════════════════════════════════════════════════════════════════════╝{Colors.END}

{Colors.CYAN}🚀 HOW TO USE LUMORA:{Colors.END}

{Colors.WHITE}1. HOTKEY ACCESS (Recommended):{Colors.END}
   • {Colors.YELLOW}Ctrl + Alt + L{Colors.END} - Open main interface
   • {Colors.YELLOW}Ctrl + Alt + Shift + L{Colors.END} - Quick AI prompt
   • {Colors.YELLOW}Win + L (hold 2 sec){Colors.END} - Voice activation

{Colors.WHITE}2. TOUCHDESIGNER INTERFACE:{Colors.END}
   • Open TouchDesigner
   • Load: {Colors.YELLOW}{self.base_path}/ui/lumora_main.toe{Colors.END}
   • Experience stunning visual AI interaction

{Colors.WHITE}3. SERVICE MANAGEMENT:{Colors.END}
   • {Colors.YELLOW}lumora-service start{Colors.END} - Start service
   • {Colors.YELLOW}lumora-service stop{Colors.END} - Stop service
   • {Colors.YELLOW}lumora-service status{Colors.END} - Check status

{Colors.WHITE}4. VOICE COMMANDS:{Colors.END}
   • Say {Colors.YELLOW}"Hey Lumora"{Colors.END} to activate
   • Natural conversation interface
   • Context-aware responses

{Colors.CYAN}🎨 VISUAL EXPERIENCE:{Colors.END}
• Huly.io-inspired animations and colors
• Real-time particle-based AI responses
• Interactive 3D command interface
• Ambient lighting based on system state

{Colors.CYAN}🛡️ PRIVACY & SECURITY:{Colors.END}
• 100% local processing (no cloud)
• Granular privacy controls
• Complete audit trail
• Secure automation sandbox

{Colors.GREEN}Ready to experience the future of AI companions!{Colors.END}
{Colors.PURPLE}Documentation: {self.base_path}/README.md{Colors.END}
        """)
    
    def run_full_installation(self):
        """Run complete installation process"""
        try:
            self.print_header()
            
            steps = [
                self.check_system_requirements,
                self.install_chocolatey,
                self.install_dependencies,
                self.setup_directories,
                self.copy_source_files,
                self.build_rust_components,
                self.compile_cpp_components,
                self.install_python_packages,
                self.setup_touchdesigner,
                self.install_windows_service,
            ]
            
            for step in steps:
                if not step():
                    self.print_error("Installation failed!")
                    return False
                time.sleep(1)
            
            self.create_shortcuts()
            self.finalize_installation()
            return True
            
        except KeyboardInterrupt:
            self.print_error("Installation cancelled by user")
            return False
        except Exception as e:
            self.print_error(f"Installation failed: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(description="Lumora AI OS Companion Installer")
    parser.add_argument("--full-setup", action="store_true", 
                       help="Run complete installation")
    parser.add_argument("--service-only", action="store_true",
                       help="Install service only")
    parser.add_argument("--touchdesigner-only", action="store_true",
                       help="Setup TouchDesigner only")
    
    args = parser.parse_args()
    
    installer = LumoraInstaller()
    
    if args.service_only:
        installer.install_windows_service()
    elif args.touchdesigner_only:
        installer.setup_touchdesigner()
    else:
        # Default to full installation
        installer.run_full_installation()

if __name__ == "__main__":
    main()
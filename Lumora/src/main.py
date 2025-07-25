#!/usr/bin/env python3
"""
LUMORA - Full-Access AI OS Companion
Main Entry Point

This is the primary entry point for Lumora. It can run in multiple modes:
- Service mode (background Windows service)
- Interactive mode (GUI application)
- Console mode (command-line interface)
"""

import sys
import os
import argparse
import logging
import asyncio
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.engine import LumoraEngine
from core.privacy import PrivacyGuardian
from core.config import ConfigManager
from services.service_manager import ServiceManager
from ui.gui_manager import GUIManager
from core.logger import setup_logging

class LumoraLauncher:
    """Main launcher for Lumora application."""
    
    def __init__(self):
        self.config = ConfigManager()
        self.privacy = PrivacyGuardian()
        self.engine = None
        self.gui = None
        self.service_manager = None
        
    async def initialize(self):
        """Initialize Lumora systems."""
        try:
            # Setup logging
            setup_logging(self.config.get('logging.level', 'INFO'))
            logging.info("Initializing Lumora...")
            
            # Check permissions
            if not self._check_permissions():
                logging.error("Administrator privileges required")
                return False
                
            # Initialize core components
            self.engine = LumoraEngine(self.config, self.privacy)
            self.service_manager = ServiceManager()
            
            logging.info("Lumora initialized successfully")
            return True
            
        except Exception as e:
            logging.error(f"Failed to initialize Lumora: {e}")
            return False
    
    def _check_permissions(self):
        """Check if running with administrator privileges."""
        try:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    
    async def run_service_mode(self):
        """Run Lumora as a Windows service."""
        logging.info("Starting Lumora in service mode...")
        
        if not await self.initialize():
            return 1
            
        try:
            await self.service_manager.install_service()
            await self.engine.start_background_mode()
            
            # Keep service running
            while True:
                await asyncio.sleep(1)
                if not self.engine.is_running():
                    break
                    
        except KeyboardInterrupt:
            logging.info("Service interrupted, shutting down...")
        except Exception as e:
            logging.error(f"Service error: {e}")
            return 1
        finally:
            if self.engine:
                await self.engine.shutdown()
                
        return 0
    
    async def run_interactive_mode(self):
        """Run Lumora with GUI interface."""
        logging.info("Starting Lumora in interactive mode...")
        
        if not await self.initialize():
            return 1
            
        try:
            self.gui = GUIManager(self.engine, self.config, self.privacy)
            await self.gui.initialize()
            
            # Start engine in interactive mode
            await self.engine.start_interactive_mode()
            
            # Run GUI event loop
            await self.gui.run()
            
        except Exception as e:
            logging.error(f"Interactive mode error: {e}")
            return 1
        finally:
            if self.gui:
                await self.gui.shutdown()
            if self.engine:
                await self.engine.shutdown()
                
        return 0
    
    async def run_console_mode(self):
        """Run Lumora in console mode."""
        logging.info("Starting Lumora in console mode...")
        
        if not await self.initialize():
            return 1
            
        try:
            await self.engine.start_console_mode()
            
            print("Lumora Console Mode")
            print("Type 'help' for commands, 'exit' to quit")
            
            while True:
                try:
                    command = input("lumora> ").strip()
                    if command.lower() in ['exit', 'quit']:
                        break
                    elif command.lower() == 'help':
                        self._show_console_help()
                    else:
                        result = await self.engine.process_command(command)
                        if result:
                            print(result)
                except KeyboardInterrupt:
                    break
                except EOFError:
                    break
                    
        except Exception as e:
            logging.error(f"Console mode error: {e}")
            return 1
        finally:
            if self.engine:
                await self.engine.shutdown()
                
        return 0
    
    def _show_console_help(self):
        """Show console mode help."""
        help_text = """
Lumora Console Commands:
  status          - Show system status
  privacy         - Privacy controls
  config          - Configuration management
  memory          - Memory and learning info
  plugins         - Plugin management
  ai              - AI interaction
  help            - Show this help
  exit/quit       - Exit Lumora
        """
        print(help_text)

def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Lumora - Full-Access AI OS Companion",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        'mode',
        choices=['service', 'interactive', 'console'],
        default='interactive',
        nargs='?',
        help='Run mode: service (background), interactive (GUI), console (CLI)'
    )
    
    parser.add_argument(
        '--install-service',
        action='store_true',
        help='Install Lumora as Windows service'
    )
    
    parser.add_argument(
        '--uninstall-service',
        action='store_true',
        help='Uninstall Lumora Windows service'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )
    
    args = parser.parse_args()
    
    # Handle service installation/uninstallation
    if args.install_service:
        service_manager = ServiceManager()
        return asyncio.run(service_manager.install_service())
    
    if args.uninstall_service:
        service_manager = ServiceManager()
        return asyncio.run(service_manager.uninstall_service())
    
    # Create launcher
    launcher = LumoraLauncher()
    
    # Set debug mode if requested
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Run in specified mode
    try:
        if args.mode == 'service':
            return asyncio.run(launcher.run_service_mode())
        elif args.mode == 'interactive':
            return asyncio.run(launcher.run_interactive_mode())
        elif args.mode == 'console':
            return asyncio.run(launcher.run_console_mode())
        else:
            print(f"Unknown mode: {args.mode}")
            return 1
            
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
        return 0
    except Exception as e:
        print(f"Fatal error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
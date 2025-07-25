#!/usr/bin/env python3
"""
LUMORA LAUNCHER - GOD-TIER AI OS COMPANION
Main launcher script for the complete Lumora system
"""

import asyncio
import sys
import os
import argparse
import signal
from pathlib import Path
from typing import Optional

# Add core modules to path
sys.path.insert(0, str(Path(__file__).parent / "core"))

# Import core components
from core.engine import LumoraEngine
from installation.installer import LumoraInstaller

class Colors:
    """ANSI color codes for beautiful output"""
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

class LumoraLauncher:
    """Main launcher for Lumora AI OS Companion"""
    
    def __init__(self):
        self.engine: Optional[LumoraEngine] = None
        self.is_running = False
        
    def print_banner(self):
        """Print stunning Lumora banner"""
        print(f"""
{Colors.CYAN}
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║  ██╗     ██╗   ██╗███╗   ███╗ ██████╗ ██████╗  █████╗                ║
║  ██║     ██║   ██║████╗ ████║██╔═══██╗██╔══██╗██╔══██╗               ║
║  ██║     ██║   ██║██╔████╔██║██║   ██║██████╔╝███████║               ║
║  ██║     ██║   ██║██║╚██╔╝██║██║   ██║██╔══██╗██╔══██║               ║
║  ███████╗╚██████╔╝██║ ╚═╝ ██║╚██████╔╝██║  ██║██║  ██║               ║
║  ╚══════╝ ╚═════╝ ╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝               ║
║                                                                      ║
║              🚀 GOD-TIER AI OS COMPANION v2.0 🚀                     ║
║                                                                      ║
║   "The Only AI You'll Ever Need - PowerToys × Jarvis × TouchDesigner" ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
{Colors.END}

{Colors.WHITE}🎨 Features:{Colors.END}
• {Colors.YELLOW}Multi-Language Architecture{Colors.END}: Python + Rust + C++ + TouchDesigner
• {Colors.YELLOW}Stunning Visual Interface{Colors.END}: Huly.io-inspired animations & effects
• {Colors.YELLOW}Advanced AI Brain{Colors.END}: Context-aware, learning, personality-driven
• {Colors.YELLOW}High-Performance Automation{Colors.END}: Rust-powered system integration
• {Colors.YELLOW}100% Local & Private{Colors.END}: No cloud dependencies, full control
• {Colors.YELLOW}Zero-Error Guarantee{Colors.END}: Comprehensive safety & error handling

{Colors.CYAN}Ready to experience the future of AI companions!{Colors.END}
        """)
    
    async def check_installation(self) -> bool:
        """Check if Lumora is properly installed"""
        required_paths = [
            Path("C:/Lumora"),
            Path("C:/Lumora/core"),
            Path("C:/Lumora/automation"),
            Path("C:/Lumora/ui"),
        ]
        
        for path in required_paths:
            if not path.exists():
                print(f"{Colors.RED}✗ Missing: {path}{Colors.END}")
                return False
        
        print(f"{Colors.GREEN}✓ Installation verified{Colors.END}")
        return True
    
    async def start_engine(self, config_path: Optional[Path] = None) -> bool:
        """Start the Lumora engine"""
        try:
            print(f"\n{Colors.BLUE}🚀 Starting Lumora Engine...{Colors.END}")
            
            # Initialize engine
            self.engine = LumoraEngine(config_path)
            
            # Start engine
            if await self.engine.start():
                self.is_running = True
                print(f"{Colors.GREEN}✓ Lumora Engine started successfully!{Colors.END}")
                
                # Print status
                await self.print_status()
                return True
            else:
                print(f"{Colors.RED}✗ Failed to start Lumora Engine{Colors.END}")
                return False
                
        except Exception as e:
            print(f"{Colors.RED}✗ Engine startup error: {e}{Colors.END}")
            return False
    
    async def stop_engine(self) -> bool:
        """Stop the Lumora engine"""
        if self.engine and self.is_running:
            print(f"\n{Colors.YELLOW}🛑 Stopping Lumora Engine...{Colors.END}")
            
            try:
                await self.engine.stop()
                self.is_running = False
                print(f"{Colors.GREEN}✓ Lumora Engine stopped successfully{Colors.END}")
                return True
            except Exception as e:
                print(f"{Colors.RED}✗ Error stopping engine: {e}{Colors.END}")
                return False
        
        return True
    
    async def print_status(self):
        """Print current Lumora status"""
        if not self.engine:
            print(f"{Colors.RED}Engine not initialized{Colors.END}")
            return
        
        try:
            status = await self.engine.get_status()
            
            print(f"""
{Colors.CYAN}📊 LUMORA STATUS:{Colors.END}

{Colors.WHITE}Engine State:{Colors.END}
  • Running: {Colors.GREEN if status['state']['is_running'] else Colors.RED}{status['state']['is_running']}{Colors.END}
  • Mode: {Colors.YELLOW}{status['state']['active_mode']}{Colors.END}
  • Personality: {Colors.PURPLE}{status['state']['ai_personality']}{Colors.END}
  • Performance: {Colors.BLUE}{status['state']['performance_mode']}{Colors.END}

{Colors.WHITE}Statistics:{Colors.END}
  • Interactions: {Colors.GREEN}{status['state']['total_interactions']}{Colors.END}
  • Automations: {Colors.GREEN}{status['state']['total_automations']}{Colors.END}
  • User Presence: {Colors.YELLOW}{status['state']['user_presence']}{Colors.END}

{Colors.WHITE}System Metrics:{Colors.END}
  • CPU: {Colors.YELLOW}{status['metrics']['cpu_percent']:.1f}%{Colors.END}
  • Memory: {Colors.YELLOW}{status['metrics']['memory_percent']:.1f}%{Colors.END}
  • Automation Queue: {Colors.CYAN}{status['metrics']['automation_queue_size']}{Colors.END}
  • AI Response Time: {Colors.PURPLE}{status['metrics']['ai_response_time_ms']:.1f}ms{Colors.END}

{Colors.WHITE}Component Health:{Colors.END}""")
            
            for component, health in status['components'].items():
                color = Colors.GREEN if health else Colors.RED
                icon = "✓" if health else "✗"
                print(f"  • {component.replace('_', ' ').title()}: {color}{icon} {health}{Colors.END}")
                
        except Exception as e:
            print(f"{Colors.RED}Error getting status: {e}{Colors.END}")
    
    async def interactive_mode(self):
        """Run Lumora in interactive mode"""
        self.print_banner()
        
        print(f"\n{Colors.WHITE}Welcome to Lumora Interactive Mode!{Colors.END}")
        print(f"{Colors.CYAN}Type 'help' for commands, 'exit' to quit{Colors.END}")
        
        while self.is_running:
            try:
                # Get user input
                user_input = input(f"\n{Colors.PURPLE}Lumora> {Colors.END}").strip()
                
                if not user_input:
                    continue
                
                # Handle commands
                if user_input.lower() in ['exit', 'quit', 'q']:
                    break
                elif user_input.lower() == 'help':
                    await self.show_help()
                elif user_input.lower() == 'status':
                    await self.print_status()
                elif user_input.lower() == 'restart':
                    await self.restart_engine()
                elif user_input.lower() == 'diagnostics':
                    await self.run_diagnostics()
                elif user_input.startswith('ai '):
                    await self.process_ai_command(user_input[3:])
                elif user_input.startswith('automation '):
                    await self.process_automation_command(user_input[11:])
                else:
                    # Send to AI for natural language processing
                    await self.process_natural_command(user_input)
                    
            except KeyboardInterrupt:
                print(f"\n{Colors.YELLOW}Interrupt received{Colors.END}")
                break
            except Exception as e:
                print(f"{Colors.RED}Error: {e}{Colors.END}")
    
    async def show_help(self):
        """Show available commands"""
        print(f"""
{Colors.CYAN}🔧 LUMORA COMMANDS:{Colors.END}

{Colors.WHITE}General:{Colors.END}
  • {Colors.YELLOW}help{Colors.END} - Show this help message
  • {Colors.YELLOW}status{Colors.END} - Show current system status
  • {Colors.YELLOW}restart{Colors.END} - Restart the Lumora engine
  • {Colors.YELLOW}diagnostics{Colors.END} - Run system diagnostics
  • {Colors.YELLOW}exit{Colors.END} - Exit Lumora

{Colors.WHITE}AI Commands:{Colors.END}
  • {Colors.PURPLE}ai <message>{Colors.END} - Send message to AI brain
  • {Colors.PURPLE}"Hello Lumora"{Colors.END} - Natural conversation
  • {Colors.PURPLE}"What can you see?"{Colors.END} - Context awareness
  • {Colors.PURPLE}"Help me with this task"{Colors.END} - Task assistance

{Colors.WHITE}Automation Commands:{Colors.END}
  • {Colors.BLUE}automation click 100 200{Colors.END} - Click at coordinates
  • {Colors.BLUE}automation type "Hello World"{Colors.END} - Type text
  • {Colors.BLUE}automation key ctrl+c{Colors.END} - Press key combination

{Colors.WHITE}Examples:{Colors.END}
  • {Colors.GREEN}"Summarize my current screen"{Colors.END}
  • {Colors.GREEN}"Open calculator and compute 2+2"{Colors.END}
  • {Colors.GREEN}"What apps are running?"{Colors.END}
  • {Colors.GREEN}"How's my system performance?"{Colors.END}
        """)
    
    async def process_ai_command(self, message: str):
        """Process AI command"""
        try:
            if self.engine:
                result = await self.engine.execute_command(f"ai.chat", {"message": message})
                
                if result.get("success"):
                    response = result.get("response", "No response")
                    print(f"{Colors.GREEN}🤖 Lumora: {response}{Colors.END}")
                else:
                    print(f"{Colors.RED}AI Error: {result.get('error', 'Unknown error')}{Colors.END}")
            else:
                print(f"{Colors.RED}Engine not running{Colors.END}")
                
        except Exception as e:
            print(f"{Colors.RED}Error processing AI command: {e}{Colors.END}")
    
    async def process_automation_command(self, command: str):
        """Process automation command"""
        try:
            parts = command.split()
            if not parts:
                print(f"{Colors.RED}No automation command specified{Colors.END}")
                return
            
            action = parts[0]
            
            if action == "click" and len(parts) >= 3:
                x, y = int(parts[1]), int(parts[2])
                result = await self.engine.execute_command("automation.click", {"x": x, "y": y})
            elif action == "type" and len(parts) >= 2:
                text = " ".join(parts[1:]).strip('"')
                result = await self.engine.execute_command("automation.type", {"text": text})
            elif action == "key" and len(parts) >= 2:
                key = parts[1]
                result = await self.engine.execute_command("automation.key", {"key": key})
            else:
                print(f"{Colors.RED}Unknown automation command: {action}{Colors.END}")
                return
            
            if result.get("success"):
                print(f"{Colors.GREEN}✓ Automation executed successfully{Colors.END}")
            else:
                print(f"{Colors.RED}Automation failed: {result.get('error', 'Unknown error')}{Colors.END}")
                
        except Exception as e:
            print(f"{Colors.RED}Error processing automation command: {e}{Colors.END}")
    
    async def process_natural_command(self, message: str):
        """Process natural language command"""
        try:
            if self.engine:
                # Send to AI for natural language processing
                result = await self.engine.execute_command(message)
                
                if "ai_response" in result:
                    response = result["ai_response"].get("text", "No response")
                    print(f"{Colors.GREEN}🤖 Lumora: {response}{Colors.END}")
                    
                    # Show automation results if any
                    if result.get("automation_results"):
                        print(f"{Colors.BLUE}⚡ Performed {len(result['automation_results'])} automation(s){Colors.END}")
                else:
                    print(f"{Colors.YELLOW}Command processed: {result}{Colors.END}")
            else:
                print(f"{Colors.RED}Engine not running{Colors.END}")
                
        except Exception as e:
            print(f"{Colors.RED}Error processing command: {e}{Colors.END}")
    
    async def restart_engine(self):
        """Restart the Lumora engine"""
        print(f"{Colors.YELLOW}🔄 Restarting Lumora Engine...{Colors.END}")
        
        await self.stop_engine()
        await asyncio.sleep(2)
        await self.start_engine()
    
    async def run_diagnostics(self):
        """Run system diagnostics"""
        try:
            if self.engine:
                result = await self.engine.execute_command("engine.diagnostics")
                
                print(f"\n{Colors.CYAN}🔍 SYSTEM DIAGNOSTICS:{Colors.END}")
                print(f"Engine: {Colors.GREEN if result['engine'] == 'healthy' else Colors.RED}{result['engine']}{Colors.END}")
                print(f"Performance: {Colors.YELLOW}{result['performance']}{Colors.END}")
                
                if result.get('uptime'):
                    print(f"Uptime: {Colors.BLUE}{result['uptime']}{Colors.END}")
                
                print(f"\n{Colors.WHITE}Components:{Colors.END}")
                for component, status in result['components'].items():
                    color = Colors.GREEN if status == "healthy" else Colors.RED
                    print(f"  • {component}: {color}{status}{Colors.END}")
                
                if result.get('recommendations'):
                    print(f"\n{Colors.YELLOW}Recommendations:{Colors.END}")
                    for rec in result['recommendations']:
                        print(f"  • {rec}")
                        
            else:
                print(f"{Colors.RED}Engine not running{Colors.END}")
                
        except Exception as e:
            print(f"{Colors.RED}Diagnostics error: {e}{Colors.END}")
    
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            print(f"\n{Colors.YELLOW}Shutdown signal received{Colors.END}")
            asyncio.create_task(self.stop_engine())
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Lumora AI OS Companion")
    parser.add_argument("--mode", choices=["interactive", "service", "install"], 
                       default="interactive", help="Launch mode")
    parser.add_argument("--config", type=Path, help="Configuration file path")
    parser.add_argument("--install", action="store_true", help="Run installation")
    
    args = parser.parse_args()
    
    # Handle installation
    if args.install or args.mode == "install":
        installer = LumoraInstaller()
        success = installer.run_full_installation()
        sys.exit(0 if success else 1)
    
    # Create launcher
    launcher = LumoraLauncher()
    launcher.setup_signal_handlers()
    
    try:
        # Check installation
        if not await launcher.check_installation():
            print(f"\n{Colors.RED}Lumora not properly installed!{Colors.END}")
            print(f"{Colors.YELLOW}Run: python lumora_launcher.py --install{Colors.END}")
            sys.exit(1)
        
        # Start engine
        if not await launcher.start_engine(args.config):
            sys.exit(1)
        
        # Run in specified mode
        if args.mode == "interactive":
            await launcher.interactive_mode()
        elif args.mode == "service":
            print(f"{Colors.GREEN}🎯 Lumora running in service mode{Colors.END}")
            print(f"{Colors.CYAN}Press Ctrl+C to stop{Colors.END}")
            
            # Keep running until interrupted
            while launcher.is_running:
                await asyncio.sleep(1)
    
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Shutdown requested{Colors.END}")
    except Exception as e:
        print(f"\n{Colors.RED}Fatal error: {e}{Colors.END}")
        sys.exit(1)
    finally:
        await launcher.stop_engine()
        print(f"{Colors.CYAN}Thank you for using Lumora! 🚀{Colors.END}")

if __name__ == "__main__":
    # Run the launcher
    asyncio.run(main())
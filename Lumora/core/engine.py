"""
LUMORA Core Engine

This is the heart of Lumora - orchestrates all subsystems and provides
the main intelligence layer that coordinates between monitoring, AI, and actions.
"""

import asyncio
import logging
import time
import threading
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

from .context_manager import ContextManager
from .privacy import PrivacyGuardian
from .config import ConfigManager
from .memory_bank import MemoryBank
from .automation import AutomationEngine
from ai.brain import AIBrain
from ai.models import LocalModelManager
from plugins.plugin_manager import PluginManager

class EngineState(Enum):
    """Engine operational states."""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPING = "stopping"
    ERROR = "error"

@dataclass
class SystemStatus:
    """Current system status information."""
    state: EngineState
    uptime: float
    memory_usage: float
    cpu_usage: float
    active_contexts: int
    privacy_mode: bool
    ai_active: bool
    last_action: Optional[str]
    performance_mode: str

class LumoraEngine:
    """
    The central orchestration engine for Lumora.
    
    Coordinates all subsystems:
    - Context monitoring and screen awareness
    - AI processing and decision making
    - Automation and system interaction
    - Memory and learning
    - Privacy and security
    - Plugin management
    """
    
    def __init__(self, config: ConfigManager, privacy: PrivacyGuardian):
        self.config = config
        self.privacy = privacy
        self.state = EngineState.STOPPED
        self.start_time = 0
        
        # Core subsystems
        self.context_manager = None
        self.memory_bank = None
        self.ai_brain = None
        self.automation_engine = None
        self.plugin_manager = None
        self.model_manager = None
        
        # Runtime tracking
        self.last_context_change = 0
        self.last_action_time = 0
        self.performance_stats = {}
        self.active_tasks = set()
        
        # Smart loop control
        self.smart_loop_running = False
        self.smart_loop_task = None
        self.loop_interval = 0.5  # Base interval
        self.adaptive_interval = True
        
        self.logger = logging.getLogger(__name__)
        
    async def initialize_subsystems(self):
        """Initialize all core subsystems."""
        try:
            self.logger.info("Initializing Lumora subsystems...")
            
            # Initialize in dependency order
            self.memory_bank = MemoryBank(self.config)
            await self.memory_bank.initialize()
            
            self.model_manager = LocalModelManager(self.config)
            await self.model_manager.initialize()
            
            self.ai_brain = AIBrain(self.config, self.memory_bank, self.model_manager)
            await self.ai_brain.initialize()
            
            self.context_manager = ContextManager(self.config, self.privacy)
            await self.context_manager.initialize()
            
            self.automation_engine = AutomationEngine(self.config, self.context_manager)
            await self.automation_engine.initialize()
            
            self.plugin_manager = PluginManager(self.config)
            await self.plugin_manager.initialize()
            
            # Register event handlers
            self._register_event_handlers()
            
            self.logger.info("All subsystems initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize subsystems: {e}")
            self.state = EngineState.ERROR
            return False
    
    def _register_event_handlers(self):
        """Register event handlers between subsystems."""
        # Context changes trigger AI analysis
        self.context_manager.on_context_change = self._handle_context_change
        self.context_manager.on_app_switch = self._handle_app_switch
        self.context_manager.on_screen_change = self._handle_screen_change
        self.context_manager.on_input_activity = self._handle_input_activity
        
        # AI decisions trigger automations
        self.ai_brain.on_suggestion = self._handle_ai_suggestion
        self.ai_brain.on_action_request = self._handle_action_request
        
        # Privacy events
        self.privacy.on_privacy_change = self._handle_privacy_change
        
    async def start_background_mode(self):
        """Start engine in background service mode."""
        if self.state != EngineState.STOPPED:
            return False
            
        self.state = EngineState.STARTING
        self.start_time = time.time()
        
        try:
            if not await self.initialize_subsystems():
                return False
                
            # Start monitoring subsystems
            await self.context_manager.start_monitoring()
            
            # Start smart loop
            await self._start_smart_loop()
            
            self.state = EngineState.RUNNING
            self.logger.info("Lumora engine started in background mode")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start background mode: {e}")
            self.state = EngineState.ERROR
            return False
    
    async def start_interactive_mode(self):
        """Start engine in interactive mode with GUI support."""
        if self.state != EngineState.STOPPED:
            return False
            
        self.state = EngineState.STARTING
        self.start_time = time.time()
        
        try:
            if not await self.initialize_subsystems():
                return False
                
            # Start monitoring with GUI integration
            await self.context_manager.start_monitoring(interactive=True)
            
            # Start smart loop with GUI updates
            await self._start_smart_loop(interactive=True)
            
            self.state = EngineState.RUNNING
            self.logger.info("Lumora engine started in interactive mode")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start interactive mode: {e}")
            self.state = EngineState.ERROR
            return False
    
    async def start_console_mode(self):
        """Start engine in console mode."""
        if self.state != EngineState.STOPPED:
            return False
            
        self.state = EngineState.STARTING
        self.start_time = time.time()
        
        try:
            if not await self.initialize_subsystems():
                return False
                
            # Start minimal monitoring for console
            await self.context_manager.start_monitoring(minimal=True)
            
            self.state = EngineState.RUNNING
            self.logger.info("Lumora engine started in console mode")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start console mode: {e}")
            self.state = EngineState.ERROR
            return False
    
    async def _start_smart_loop(self, interactive=False):
        """Start the intelligent monitoring loop."""
        if self.smart_loop_running:
            return
            
        self.smart_loop_running = True
        self.smart_loop_task = asyncio.create_task(
            self._smart_loop(interactive)
        )
        
    async def _smart_loop(self, interactive=False):
        """
        Intelligent monitoring loop that adapts based on activity.
        Only processes when there are actual changes to analyze.
        """
        self.logger.info("Starting smart monitoring loop")
        
        while self.smart_loop_running and self.state == EngineState.RUNNING:
            try:
                # Check if we should process
                should_process = await self._should_process_cycle()
                
                if should_process:
                    await self._process_cycle(interactive)
                    
                # Adaptive sleep based on activity
                sleep_time = self._calculate_adaptive_interval()
                await asyncio.sleep(sleep_time)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Smart loop error: {e}")
                await asyncio.sleep(1)  # Error recovery
                
        self.logger.info("Smart monitoring loop stopped")
    
    async def _should_process_cycle(self) -> bool:
        """Determine if we should process this cycle."""
        # Always process if privacy allows
        if not self.privacy.is_monitoring_allowed():
            return False
            
        # Check for context changes
        if self.context_manager.has_changes():
            return True
            
        # Check for pending AI tasks
        if self.ai_brain.has_pending_tasks():
            return True
            
        # Check for automation triggers
        if self.automation_engine.has_pending_actions():
            return True
            
        # Periodic health check
        current_time = time.time()
        if current_time - self.last_action_time > 30:  # 30 seconds
            return True
            
        return False
    
    async def _process_cycle(self, interactive=False):
        """Process one cycle of monitoring and analysis."""
        cycle_start = time.time()
        
        try:
            # 1. Gather context information
            context = await self.context_manager.get_current_context()
            
            if not context:
                return
                
            # 2. Privacy filtering
            filtered_context = self.privacy.filter_context(context)
            
            # 3. AI analysis and decision making
            ai_response = await self.ai_brain.process_context(filtered_context)
            
            # 4. Execute any recommended actions
            if ai_response and ai_response.actions:
                await self._execute_ai_actions(ai_response.actions)
                
            # 5. Update memory and learning
            await self.memory_bank.store_interaction(
                context=filtered_context,
                ai_response=ai_response,
                timestamp=cycle_start
            )
            
            # 6. Plugin processing
            await self.plugin_manager.process_context(filtered_context)
            
            self.last_action_time = time.time()
            
        except Exception as e:
            self.logger.error(f"Process cycle error: {e}")
    
    def _calculate_adaptive_interval(self) -> float:
        """Calculate adaptive sleep interval based on system activity."""
        if not self.adaptive_interval:
            return self.loop_interval
            
        base_interval = self.loop_interval
        
        # Reduce interval during high activity
        if self.context_manager.get_activity_level() > 0.8:
            return base_interval * 0.5
            
        # Increase interval during low activity
        if self.context_manager.get_activity_level() < 0.2:
            return base_interval * 2.0
            
        # Check system resources
        cpu_usage = self._get_cpu_usage()
        if cpu_usage > 80:
            return base_interval * 1.5
            
        return base_interval
    
    async def _execute_ai_actions(self, actions: List[Dict[str, Any]]):
        """Execute actions recommended by AI."""
        for action in actions:
            try:
                if not self.privacy.is_action_allowed(action):
                    continue
                    
                await self.automation_engine.execute_action(action)
                
            except Exception as e:
                self.logger.error(f"Failed to execute action {action}: {e}")
    
    # Event Handlers
    async def _handle_context_change(self, context):
        """Handle context change events."""
        self.last_context_change = time.time()
        await self.ai_brain.on_context_change(context)
    
    async def _handle_app_switch(self, from_app, to_app):
        """Handle application switch events."""
        await self.ai_brain.on_app_switch(from_app, to_app)
        await self.automation_engine.on_app_switch(from_app, to_app)
    
    async def _handle_screen_change(self, screen_data):
        """Handle screen content change events."""
        if self.privacy.is_screen_reading_allowed():
            await self.ai_brain.on_screen_change(screen_data)
    
    async def _handle_input_activity(self, input_data):
        """Handle input activity events."""
        if self.privacy.is_input_monitoring_allowed():
            await self.ai_brain.on_input_activity(input_data)
    
    async def _handle_ai_suggestion(self, suggestion):
        """Handle AI suggestions."""
        # Log suggestion for user review
        await self.memory_bank.store_suggestion(suggestion)
    
    async def _handle_action_request(self, action_request):
        """Handle AI action requests."""
        if self.privacy.require_confirmation_for_actions():
            # Queue for user confirmation
            await self.automation_engine.queue_for_confirmation(action_request)
        else:
            # Execute immediately
            await self.automation_engine.execute_action(action_request)
    
    async def _handle_privacy_change(self, privacy_setting, value):
        """Handle privacy setting changes."""
        if privacy_setting == "monitoring_enabled" and not value:
            await self.pause()
        elif privacy_setting == "monitoring_enabled" and value:
            await self.resume()
    
    # Control Methods
    async def pause(self):
        """Pause engine operations."""
        if self.state == EngineState.RUNNING:
            self.state = EngineState.PAUSED
            await self.context_manager.pause_monitoring()
            self.logger.info("Lumora engine paused")
    
    async def resume(self):
        """Resume engine operations."""
        if self.state == EngineState.PAUSED:
            self.state = EngineState.RUNNING
            await self.context_manager.resume_monitoring()
            self.logger.info("Lumora engine resumed")
    
    async def shutdown(self):
        """Shutdown the engine and all subsystems."""
        if self.state == EngineState.STOPPED:
            return
            
        self.state = EngineState.STOPPING
        self.logger.info("Shutting down Lumora engine...")
        
        try:
            # Stop smart loop
            self.smart_loop_running = False
            if self.smart_loop_task:
                self.smart_loop_task.cancel()
                try:
                    await self.smart_loop_task
                except asyncio.CancelledError:
                    pass
            
            # Shutdown subsystems in reverse order
            if self.plugin_manager:
                await self.plugin_manager.shutdown()
            if self.automation_engine:
                await self.automation_engine.shutdown()
            if self.context_manager:
                await self.context_manager.shutdown()
            if self.ai_brain:
                await self.ai_brain.shutdown()
            if self.model_manager:
                await self.model_manager.shutdown()
            if self.memory_bank:
                await self.memory_bank.shutdown()
                
            self.state = EngineState.STOPPED
            self.logger.info("Lumora engine shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")
            self.state = EngineState.ERROR
    
    # Status and Information
    def is_running(self) -> bool:
        """Check if engine is running."""
        return self.state == EngineState.RUNNING
    
    def get_status(self) -> SystemStatus:
        """Get current system status."""
        uptime = time.time() - self.start_time if self.start_time > 0 else 0
        
        return SystemStatus(
            state=self.state,
            uptime=uptime,
            memory_usage=self._get_memory_usage(),
            cpu_usage=self._get_cpu_usage(),
            active_contexts=len(self.active_tasks),
            privacy_mode=self.privacy.is_private_mode(),
            ai_active=self.ai_brain.is_active() if self.ai_brain else False,
            last_action=self._get_last_action(),
            performance_mode=self._get_performance_mode()
        )
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage percentage."""
        try:
            import psutil
            return psutil.virtual_memory().percent
        except:
            return 0.0
    
    def _get_cpu_usage(self) -> float:
        """Get current CPU usage percentage."""
        try:
            import psutil
            return psutil.cpu_percent(interval=0.1)
        except:
            return 0.0
    
    def _get_last_action(self) -> Optional[str]:
        """Get description of last action performed."""
        if hasattr(self, 'automation_engine') and self.automation_engine:
            return self.automation_engine.get_last_action()
        return None
    
    def _get_performance_mode(self) -> str:
        """Get current performance mode."""
        cpu_usage = self._get_cpu_usage()
        if cpu_usage > 80:
            return "high_performance"
        elif cpu_usage < 20:
            return "power_save"
        else:
            return "balanced"
    
    # Command Processing
    async def process_command(self, command: str) -> Optional[str]:
        """Process a command and return response."""
        try:
            parts = command.strip().split()
            if not parts:
                return None
                
            cmd = parts[0].lower()
            args = parts[1:] if len(parts) > 1 else []
            
            if cmd == "status":
                return self._format_status()
            elif cmd == "privacy":
                return await self._handle_privacy_command(args)
            elif cmd == "config":
                return await self._handle_config_command(args)
            elif cmd == "memory":
                return await self._handle_memory_command(args)
            elif cmd == "plugins":
                return await self._handle_plugins_command(args)
            elif cmd == "ai":
                return await self._handle_ai_command(args)
            else:
                # Try AI processing
                response = await self.ai_brain.process_natural_language(command)
                return response.text if response else "I don't understand that command."
                
        except Exception as e:
            return f"Error processing command: {e}"
    
    def _format_status(self) -> str:
        """Format status information for display."""
        status = self.get_status()
        return f"""
Lumora Status:
  State: {status.state.value}
  Uptime: {status.uptime:.1f}s
  Memory: {status.memory_usage:.1f}%
  CPU: {status.cpu_usage:.1f}%
  Privacy Mode: {status.privacy_mode}
  AI Active: {status.ai_active}
  Performance: {status.performance_mode}
  Last Action: {status.last_action or 'None'}
        """.strip()
    
    async def _handle_privacy_command(self, args) -> str:
        """Handle privacy-related commands."""
        if not args:
            return str(self.privacy.get_current_settings())
        # Additional privacy command handling...
        return "Privacy command processed"
    
    async def _handle_config_command(self, args) -> str:
        """Handle configuration commands."""
        if not args:
            return "Available config sections: " + ", ".join(self.config.get_sections())
        # Additional config command handling...
        return "Config command processed"
    
    async def _handle_memory_command(self, args) -> str:
        """Handle memory-related commands."""
        stats = await self.memory_bank.get_statistics()
        return f"Memory: {stats}"
    
    async def _handle_plugins_command(self, args) -> str:
        """Handle plugin commands."""
        plugins = await self.plugin_manager.list_plugins()
        return f"Loaded plugins: {', '.join(plugins)}"
    
    async def _handle_ai_command(self, args) -> str:
        """Handle AI interaction commands."""
        if not args:
            return "AI is ready for interaction"
        
        query = " ".join(args)
        response = await self.ai_brain.process_natural_language(query)
        return response.text if response else "No response from AI"
"""
TOUCHDESIGNER BRIDGE - VISUAL INTERFACE INTEGRATION
Bridge for connecting Lumora with TouchDesigner visual interface
"""

import asyncio
import json
import socket
import time
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
import logging

@dataclass
class VisualEffect:
    """Visual effect configuration"""
    effect_type: str
    intensity: float = 1.0
    color: tuple = (1.0, 1.0, 1.0)
    duration_ms: int = 1000
    parameters: Dict[str, Any] = None

@dataclass
class ParticleConfig:
    """Particle system configuration"""
    count: int = 100
    life_span: float = 2.0
    velocity: tuple = (0.0, 1.0, 0.0)
    color_start: tuple = (1.0, 1.0, 1.0, 1.0)
    color_end: tuple = (1.0, 1.0, 1.0, 0.0)
    size_start: float = 1.0
    size_end: float = 0.5

class TouchDesignerBridge:
    """
    Bridge for TouchDesigner visual interface integration
    Provides real-time visual feedback and stunning animations
    """
    
    def __init__(self, td_host: str = "localhost", td_port: int = 7001):
        self.td_host = td_host
        self.td_port = td_port
        self.is_connected = False
        self.socket = None
        self.is_running = False
        self.logger = logging.getLogger(__name__)
        
        # Visual state tracking
        self.current_effects = {}
        self.particle_systems = {}
        self.ambient_state = {
            "performance_glow": 1.0,
            "activity_pulse": 0.0,
            "ai_confidence": 0.8,
            "user_presence": "unknown"
        }
        
        # Color palette (Huly.io inspired)
        self.color_palette = {
            "electric_blue": (0.0, 0.85, 1.0),
            "neon_purple": (0.55, 0.36, 0.96),
            "bright_green": (0.0, 1.0, 0.53),
            "warning_orange": (1.0, 0.42, 0.21),
            "error_red": (1.0, 0.2, 0.4),
            "dark_charcoal": (0.1, 0.1, 0.1),
            "accent_dark": (0.2, 0.2, 0.2),
            "pure_white": (1.0, 1.0, 1.0),
        }
    
    async def start(self) -> bool:
        """Start TouchDesigner bridge connection"""
        try:
            await self._connect_to_touchdesigner()
            
            if self.is_connected:
                self.is_running = True
                # Start background tasks
                asyncio.create_task(self._heartbeat_loop())
                asyncio.create_task(self._animation_loop())
                
                self.logger.info("TouchDesigner bridge started successfully")
                return True
            else:
                self.logger.warning("TouchDesigner not available - continuing without visuals")
                return True  # Don't fail startup if TD not available
                
        except Exception as e:
            self.logger.error(f"Failed to start TouchDesigner bridge: {e}")
            return True  # Don't fail startup
    
    async def stop(self) -> bool:
        """Stop TouchDesigner bridge"""
        try:
            self.is_running = False
            
            if self.socket:
                self.socket.close()
                self.socket = None
            
            self.is_connected = False
            self.logger.info("TouchDesigner bridge stopped")
            return True
            
        except Exception as e:
            self.logger.error(f"Error stopping TouchDesigner bridge: {e}")
            return False
    
    async def _connect_to_touchdesigner(self) -> bool:
        """Establish connection to TouchDesigner"""
        try:
            # Try to connect via TCP socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(2.0)  # 2 second timeout
            
            await asyncio.get_event_loop().run_in_executor(
                None, self.socket.connect, (self.td_host, self.td_port)
            )
            
            # Send initialization message
            init_msg = {
                "type": "init",
                "source": "lumora_core",
                "version": "2.0.0",
                "timestamp": time.time()
            }
            
            await self._send_message(init_msg)
            self.is_connected = True
            self.logger.info(f"Connected to TouchDesigner at {self.td_host}:{self.td_port}")
            return True
            
        except Exception as e:
            self.logger.warning(f"Could not connect to TouchDesigner: {e}")
            self.is_connected = False
            return False
    
    async def _send_message(self, message: Dict[str, Any]) -> bool:
        """Send message to TouchDesigner"""
        if not self.is_connected or not self.socket:
            return False
        
        try:
            json_data = json.dumps(message)
            data = json_data.encode('utf-8')
            
            await asyncio.get_event_loop().run_in_executor(
                None, self.socket.send, data + b'\n'
            )
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send message to TouchDesigner: {e}")
            self.is_connected = False
            return False
    
    async def _heartbeat_loop(self):
        """Background heartbeat to maintain connection"""
        while self.is_running:
            try:
                if self.is_connected:
                    heartbeat = {
                        "type": "heartbeat",
                        "timestamp": time.time()
                    }
                    
                    if not await self._send_message(heartbeat):
                        self.logger.warning("Lost connection to TouchDesigner")
                        await self._reconnect()
                
                await asyncio.sleep(5)  # 5 second intervals
                
            except Exception as e:
                self.logger.error(f"Heartbeat error: {e}")
                await asyncio.sleep(5)
    
    async def _animation_loop(self):
        """Background animation updates"""
        while self.is_running:
            try:
                # Update ambient animations
                await self._update_ambient_effects()
                
                # Update particle systems
                await self._update_particle_systems()
                
                await asyncio.sleep(1/60)  # 60 FPS
                
            except Exception as e:
                self.logger.error(f"Animation loop error: {e}")
                await asyncio.sleep(1)
    
    async def _reconnect(self):
        """Attempt to reconnect to TouchDesigner"""
        self.is_connected = False
        if self.socket:
            self.socket.close()
            self.socket = None
        
        await asyncio.sleep(2)  # Wait before reconnecting
        await self._connect_to_touchdesigner()
    
    # Visual update methods
    
    async def update_engine_state(self, state: Any) -> bool:
        """Update TouchDesigner with engine state"""
        if not self.is_connected:
            return False
        
        try:
            message = {
                "type": "engine_state",
                "data": {
                    "is_running": getattr(state, 'is_running', False),
                    "active_mode": getattr(state, 'active_mode', 'idle'),
                    "ai_personality": getattr(state, 'ai_personality', 'assistant'),
                    "performance_mode": getattr(state, 'performance_mode', 'balanced'),
                    "total_interactions": getattr(state, 'total_interactions', 0),
                    "total_automations": getattr(state, 'total_automations', 0),
                    "user_presence": getattr(state, 'user_presence', 'unknown'),
                },
                "timestamp": time.time()
            }
            
            return await self._send_message(message)
            
        except Exception as e:
            self.logger.error(f"Error updating engine state: {e}")
            return False
    
    async def update_metrics(self, metrics: Any) -> bool:
        """Update TouchDesigner with system metrics"""
        if not self.is_connected:
            return False
        
        try:
            message = {
                "type": "system_metrics",
                "data": {
                    "cpu_percent": getattr(metrics, 'cpu_percent', 0.0),
                    "memory_percent": getattr(metrics, 'memory_percent', 0.0),
                    "automation_queue_size": getattr(metrics, 'automation_queue_size', 0),
                    "ai_response_time_ms": getattr(metrics, 'ai_response_time_ms', 0.0),
                    "frame_rate": getattr(metrics, 'frame_rate', 60.0),
                    "gpu_usage": getattr(metrics, 'gpu_usage', 0.0),
                },
                "timestamp": time.time()
            }
            
            return await self._send_message(message)
            
        except Exception as e:
            self.logger.error(f"Error updating metrics: {e}")
            return False
    
    async def update_context(self, context: Dict[str, Any]) -> bool:
        """Update TouchDesigner with context information"""
        if not self.is_connected:
            return False
        
        try:
            message = {
                "type": "context_update",
                "data": context,
                "timestamp": time.time()
            }
            
            return await self._send_message(message)
            
        except Exception as e:
            self.logger.error(f"Error updating context: {e}")
            return False
    
    async def update_ai_responses(self, responses: List[Dict[str, Any]]) -> bool:
        """Update TouchDesigner with AI responses for particle visualization"""
        if not self.is_connected:
            return False
        
        try:
            # Convert responses to particle configurations
            particle_configs = []
            
            for response in responses:
                config = self._create_response_particles(response)
                if config:
                    particle_configs.append(config)
            
            message = {
                "type": "ai_responses",
                "data": {
                    "responses": responses,
                    "particle_configs": particle_configs
                },
                "timestamp": time.time()
            }
            
            return await self._send_message(message)
            
        except Exception as e:
            self.logger.error(f"Error updating AI responses: {e}")
            return False
    
    async def update_automation_activity(self, results: List[Any]) -> bool:
        """Update TouchDesigner with automation activity"""
        if not self.is_connected:
            return False
        
        try:
            activity_data = []
            
            for result in results:
                activity_data.append({
                    "success": getattr(result, 'success', False),
                    "action_id": getattr(result, 'action_id', ''),
                    "execution_time_ms": getattr(result, 'execution_time_ms', 0),
                    "timestamp": time.time()
                })
            
            message = {
                "type": "automation_activity",
                "data": activity_data,
                "timestamp": time.time()
            }
            
            return await self._send_message(message)
            
        except Exception as e:
            self.logger.error(f"Error updating automation activity: {e}")
            return False
    
    async def update_visual_effects(self, effects: Dict[str, Any]) -> bool:
        """Update visual effects based on system state"""
        if not self.is_connected:
            return False
        
        try:
            # Update ambient state
            self.ambient_state.update(effects)
            
            message = {
                "type": "visual_effects",
                "data": effects,
                "timestamp": time.time()
            }
            
            return await self._send_message(message)
            
        except Exception as e:
            self.logger.error(f"Error updating visual effects: {e}")
            return False
    
    async def show_interaction(self, user_input: Dict[str, Any], ai_response: Dict[str, Any]) -> bool:
        """Show user interaction with stunning visual feedback"""
        if not self.is_connected:
            return False
        
        try:
            # Create interaction visualization
            interaction_viz = {
                "input_type": user_input.get("type", "unknown"),
                "input_content": user_input.get("content", ""),
                "response_confidence": ai_response.get("confidence", 0.8),
                "response_emotion": ai_response.get("emotion", "neutral"),
                "visual_effects": self._create_interaction_effects(user_input, ai_response)
            }
            
            message = {
                "type": "user_interaction",
                "data": interaction_viz,
                "timestamp": time.time()
            }
            
            return await self._send_message(message)
            
        except Exception as e:
            self.logger.error(f"Error showing interaction: {e}")
            return False
    
    # Visual effect creation methods
    
    def _create_response_particles(self, response: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create particle configuration for AI response"""
        try:
            confidence = response.get("confidence", 0.8)
            emotion = response.get("emotion", "neutral")
            
            # Map emotion to color
            color_map = {
                "happy": self.color_palette["bright_green"],
                "excited": self.color_palette["electric_blue"],
                "confident": self.color_palette["neon_purple"],
                "warning": self.color_palette["warning_orange"],
                "error": self.color_palette["error_red"],
                "neutral": self.color_palette["pure_white"],
            }
            
            color = color_map.get(emotion, self.color_palette["pure_white"])
            
            return {
                "count": int(50 + confidence * 100),  # More particles for higher confidence
                "life_span": 1.0 + confidence * 2.0,
                "velocity": (0.0, confidence * 2.0, 0.0),
                "color_start": color + (1.0,),  # Add alpha
                "color_end": color + (0.0,),
                "size_start": confidence * 2.0,
                "size_end": 0.1,
                "emission_rate": confidence * 50
            }
            
        except Exception as e:
            self.logger.error(f"Error creating response particles: {e}")
            return None
    
    def _create_interaction_effects(self, user_input: Dict[str, Any], ai_response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create visual effects for user interaction"""
        effects = []
        
        try:
            input_type = user_input.get("type", "unknown")
            
            # Input ripple effect
            effects.append({
                "type": "ripple",
                "origin": "input",
                "color": self.color_palette["electric_blue"],
                "intensity": 1.0,
                "duration_ms": 500
            })
            
            # Response glow effect
            confidence = ai_response.get("confidence", 0.8)
            effects.append({
                "type": "glow",
                "origin": "ai",
                "color": self.color_palette["neon_purple"],
                "intensity": confidence,
                "duration_ms": 1000
            })
            
            # Voice visualization for voice input
            if input_type == "voice":
                effects.append({
                    "type": "waveform",
                    "origin": "voice",
                    "color": self.color_palette["bright_green"],
                    "intensity": 0.8,
                    "duration_ms": 2000
                })
            
            return effects
            
        except Exception as e:
            self.logger.error(f"Error creating interaction effects: {e}")
            return []
    
    async def _update_ambient_effects(self):
        """Update ambient visual effects"""
        if not self.is_connected:
            return
        
        try:
            # Calculate ambient glow based on performance
            performance_glow = self.ambient_state.get("performance_glow", 1.0)
            activity_pulse = self.ambient_state.get("activity_pulse", 0.0)
            
            # Create pulsing effect during high activity
            pulse_intensity = 0.5 + 0.5 * activity_pulse
            
            ambient_data = {
                "background_glow": performance_glow,
                "activity_pulse": pulse_intensity,
                "timestamp": time.time()
            }
            
            message = {
                "type": "ambient_update",
                "data": ambient_data,
                "timestamp": time.time()
            }
            
            await self._send_message(message)
            
        except Exception as e:
            self.logger.error(f"Error updating ambient effects: {e}")
    
    async def _update_particle_systems(self):
        """Update active particle systems"""
        if not self.is_connected:
            return
        
        try:
            # Clean up expired particle systems
            current_time = time.time()
            expired_systems = [
                sys_id for sys_id, system in self.particle_systems.items()
                if current_time - system.get("start_time", 0) > system.get("duration", 5.0)
            ]
            
            for sys_id in expired_systems:
                del self.particle_systems[sys_id]
            
            # Send active particle systems
            if self.particle_systems:
                message = {
                    "type": "particle_update",
                    "data": self.particle_systems,
                    "timestamp": time.time()
                }
                
                await self._send_message(message)
                
        except Exception as e:
            self.logger.error(f"Error updating particle systems: {e}")
    
    # Public API methods
    
    async def create_particle_explosion(self, position: tuple = (0, 0, 0), color: tuple = None) -> str:
        """Create particle explosion effect"""
        if color is None:
            color = self.color_palette["electric_blue"]
        
        system_id = f"explosion_{int(time.time() * 1000)}"
        
        self.particle_systems[system_id] = {
            "type": "explosion",
            "position": position,
            "color": color,
            "count": 200,
            "life_span": 3.0,
            "velocity_range": (-5.0, 5.0),
            "start_time": time.time(),
            "duration": 3.0
        }
        
        return system_id
    
    async def create_text_flow(self, text: str, style: str = "flowing") -> str:
        """Create flowing text animation"""
        system_id = f"text_{int(time.time() * 1000)}"
        
        self.particle_systems[system_id] = {
            "type": "text_flow",
            "text": text,
            "style": style,
            "color": self.color_palette["pure_white"],
            "start_time": time.time(),
            "duration": 5.0
        }
        
        return system_id
    
    async def set_ambient_mood(self, mood: str) -> bool:
        """Set overall ambient mood"""
        mood_configs = {
            "calm": {
                "base_color": self.color_palette["electric_blue"],
                "intensity": 0.3,
                "pulse_rate": 0.5
            },
            "active": {
                "base_color": self.color_palette["bright_green"],
                "intensity": 0.8,
                "pulse_rate": 2.0
            },
            "focused": {
                "base_color": self.color_palette["neon_purple"],
                "intensity": 0.6,
                "pulse_rate": 1.0
            },
            "alert": {
                "base_color": self.color_palette["warning_orange"],
                "intensity": 1.0,
                "pulse_rate": 3.0
            }
        }
        
        config = mood_configs.get(mood, mood_configs["calm"])
        
        message = {
            "type": "ambient_mood",
            "data": config,
            "timestamp": time.time()
        }
        
        return await self._send_message(message)
    
    # Health and status
    
    async def is_healthy(self) -> bool:
        """Check if TouchDesigner bridge is healthy"""
        return self.is_connected and self.is_running
    
    async def get_status(self) -> Dict[str, Any]:
        """Get TouchDesigner bridge status"""
        return {
            "is_connected": self.is_connected,
            "is_running": self.is_running,
            "host": self.td_host,
            "port": self.td_port,
            "active_effects": len(self.current_effects),
            "active_particles": len(self.particle_systems),
            "ambient_state": self.ambient_state.copy()
        }
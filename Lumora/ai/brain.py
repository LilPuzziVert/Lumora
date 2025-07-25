"""
LUMORA AI Brain

The central AI intelligence system that processes context,
makes decisions, and provides intelligent responses.
"""

import asyncio
import logging
import time
import json
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum

@dataclass
class AIResponse:
    """AI response structure."""
    text: str
    confidence: float
    actions: List[Dict[str, Any]] = None
    suggestions: List[str] = None
    reasoning: str = ""
    model_used: str = ""
    processing_time: float = 0.0
    
    def __post_init__(self):
        if self.actions is None:
            self.actions = []
        if self.suggestions is None:
            self.suggestions = []

class ContextType(Enum):
    """Types of contexts for AI processing."""
    APP_SWITCH = "app_switch"
    SCREEN_CHANGE = "screen_change"
    INPUT_ACTIVITY = "input_activity"
    IDLE_DETECTION = "idle_detection"
    NATURAL_LANGUAGE = "natural_language"
    SYSTEM_EVENT = "system_event"

class AIBrain:
    """
    Central AI intelligence system for Lumora.
    
    Processes context information, makes intelligent decisions,
    and coordinates responses using local AI models.
    """
    
    def __init__(self, config_manager, memory_bank, model_manager):
        self.config = config_manager
        self.memory = memory_bank
        self.models = model_manager
        self.logger = logging.getLogger(__name__)
        
        # AI state and processing
        self.is_active = False
        self.processing_queue = asyncio.Queue()
        self.current_context = None
        self.conversation_history = []
        self.max_conversation_history = 50
        
        # Event handlers
        self.on_suggestion: Optional[Callable] = None
        self.on_action_request: Optional[Callable] = None
        
        # Processing statistics
        self.stats = {
            'total_requests': 0,
            'successful_responses': 0,
            'failed_responses': 0,
            'avg_response_time': 0.0,
            'contexts_by_type': {},
            'active_models': []
        }
        
        # Context processors
        self.context_processors = {
            ContextType.APP_SWITCH: self._process_app_switch,
            ContextType.SCREEN_CHANGE: self._process_screen_change,
            ContextType.INPUT_ACTIVITY: self._process_input_activity,
            ContextType.IDLE_DETECTION: self._process_idle_detection,
            ContextType.NATURAL_LANGUAGE: self._process_natural_language,
            ContextType.SYSTEM_EVENT: self._process_system_event
        }
        
        # AI personalities and modes
        self.current_personality = "balanced"  # balanced, professional, casual, technical
        self.friend_mode_enabled = False
        self.proactive_mode = True
        
    async def initialize(self):
        """Initialize the AI brain."""
        try:
            self.logger.info("Initializing AI Brain...")
            
            # Load user profile for personalization
            user_profile = await self.memory.get_user_profile()
            self.current_personality = user_profile.communication_style
            
            # Start processing task
            asyncio.create_task(self._processing_loop())
            
            self.is_active = True
            self.logger.info("AI Brain initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize AI Brain: {e}")
            return False
    
    async def _processing_loop(self):
        """Main processing loop for AI requests."""
        while True:
            try:
                # Get next processing request
                request = await self.processing_queue.get()
                
                # Process the request
                await self._handle_processing_request(request)
                
                # Mark task as done
                self.processing_queue.task_done()
                
            except Exception as e:
                self.logger.error(f"Processing loop error: {e}")
                await asyncio.sleep(1)  # Error recovery
    
    async def _handle_processing_request(self, request: Dict[str, Any]):
        """Handle a processing request."""
        start_time = time.time()
        request_type = request.get('type')
        context = request.get('context')
        
        try:
            # Update statistics
            self.stats['total_requests'] += 1
            
            if request_type not in self.stats['contexts_by_type']:
                self.stats['contexts_by_type'][request_type] = 0
            self.stats['contexts_by_type'][request_type] += 1
            
            # Process based on type
            if request_type in self.context_processors:
                processor = self.context_processors[request_type]
                response = await processor(context)
                
                if response:
                    # Handle the response
                    await self._handle_ai_response(response, request_type)
                    
            self.stats['successful_responses'] += 1
            
        except Exception as e:
            self.logger.error(f"Failed to process request {request_type}: {e}")
            self.stats['failed_responses'] += 1
        finally:
            # Update timing statistics
            processing_time = time.time() - start_time
            total_time = self.stats['avg_response_time'] * (self.stats['total_requests'] - 1) + processing_time
            self.stats['avg_response_time'] = total_time / self.stats['total_requests']
    
    async def _handle_ai_response(self, response: AIResponse, context_type: str):
        """Handle AI response and trigger appropriate actions."""
        # Store in conversation history
        self.conversation_history.append({
            'timestamp': time.time(),
            'context_type': context_type,
            'response': asdict(response)
        })
        
        # Trim history if too long
        if len(self.conversation_history) > self.max_conversation_history:
            self.conversation_history.pop(0)
        
        # Handle suggestions
        if response.suggestions and self.on_suggestion:
            for suggestion in response.suggestions:
                await self.on_suggestion({
                    'text': suggestion,
                    'type': 'ai_suggestion',
                    'confidence': response.confidence,
                    'context_type': context_type
                })
        
        # Handle action requests
        if response.actions and self.on_action_request:
            for action in response.actions:
                await self.on_action_request(action)
    
    # Context Processors
    async def _process_app_switch(self, context: Any) -> Optional[AIResponse]:
        """Process application switch context."""
        if not hasattr(context, 'from_app') or not hasattr(context, 'to_app'):
            return None
        
        from_app = context.from_app
        to_app = context.to_app
        
        # Get relevant memories
        memories = await self.memory.get_contextual_memory(context, limit=5)
        user_profile = await self.memory.get_user_profile()
        
        # Check if this is a common switch
        app_preference = user_profile.app_preferences.get(to_app, 0.0)
        
        # Generate response based on app switch patterns
        suggestions = []
        actions = []
        
        # Productivity suggestions
        if self._is_productivity_app(to_app) and self._is_distraction_app(from_app):
            suggestions.append("Great! Back to productive work. Stay focused!")
        elif self._is_distraction_app(to_app) and self._is_productivity_app(from_app):
            if self._is_work_hours():
                suggestions.append("Taking a break? Try to keep it short!")
        
        # Common workflow suggestions
        if to_app.lower() in ['chrome', 'firefox', 'edge'] and from_app.lower() in ['notepad', 'code', 'word']:
            actions.append({
                'type': 'suggestion',
                'text': 'Research mode detected. Want me to help organize your findings?'
            })
        
        # Build response
        if suggestions or actions:
            return AIResponse(
                text=suggestions[0] if suggestions else "",
                confidence=0.7,
                suggestions=suggestions,
                actions=actions,
                reasoning=f"App switch from {from_app} to {to_app}",
                model_used="rule_based"
            )
        
        return None
    
    async def _process_screen_change(self, context: Any) -> Optional[AIResponse]:
        """Process screen content change context."""
        if not hasattr(context, 'screen_content') or not context.screen_content:
            return None
        
        screen_content = context.screen_content
        ocr_text = screen_content.ocr_text
        
        if not ocr_text or len(ocr_text.strip()) < 10:
            return None
        
        # Get context from local model
        prompt = self._build_screen_analysis_prompt(ocr_text, context)
        
        try:
            # Use local model for analysis
            model_response = await self.models.generate_response(
                prompt=prompt,
                model_type="text_analysis",
                max_tokens=200
            )
            
            # Parse model response
            response_data = self._parse_model_response(model_response)
            
            return AIResponse(
                text=response_data.get('text', ''),
                confidence=response_data.get('confidence', 0.5),
                suggestions=response_data.get('suggestions', []),
                actions=response_data.get('actions', []),
                reasoning="Screen content analysis",
                model_used=model_response.get('model_name', 'local'),
                processing_time=model_response.get('processing_time', 0.0)
            )
            
        except Exception as e:
            self.logger.error(f"Screen analysis failed: {e}")
            return None
    
    async def _process_input_activity(self, context: Any) -> Optional[AIResponse]:
        """Process input activity context."""
        if not hasattr(context, 'recent_inputs') or not context.recent_inputs:
            return None
        
        # Analyze input patterns
        typing_speed = self._calculate_typing_speed(context.recent_inputs)
        activity_level = getattr(context, 'activity_level', 0.0)
        
        suggestions = []
        
        # Typing speed feedback
        if typing_speed > 80:  # Fast typing
            if self.friend_mode_enabled:
                suggestions.append("Wow, you're typing fast! You're on fire today! 🔥")
        elif typing_speed < 20:  # Slow typing
            if self._is_work_hours():
                suggestions.append("Take your time. Quality over speed!")
        
        # Activity level suggestions
        if activity_level > 0.9:  # Very high activity
            suggestions.append("You seem very active. Don't forget to take breaks!")
        
        if suggestions:
            return AIResponse(
                text=suggestions[0],
                confidence=0.6,
                suggestions=suggestions,
                reasoning="Input activity analysis",
                model_used="rule_based"
            )
        
        return None
    
    async def _process_idle_detection(self, context: Any) -> Optional[AIResponse]:
        """Process idle detection context."""
        idle_time = getattr(context, 'idle_time', 0)
        
        if idle_time < 300:  # Less than 5 minutes
            return None
        
        suggestions = []
        actions = []
        
        # Get user's work patterns
        user_profile = await self.memory.get_user_profile()
        
        if idle_time > 600:  # 10+ minutes
            if self._is_work_hours():
                suggestions.append("You've been away for a while. Ready to get back to work?")
                
                # Suggest resuming last activity
                memories = await self.memory.get_contextual_memory(context, limit=3)
                if memories:
                    last_context = memories[0]
                    if 'active_app' in last_context.get('context_data', {}):
                        app_name = last_context['context_data']['active_app'].get('name', '')
                        if app_name:
                            actions.append({
                                'type': 'window_focus',
                                'parameters': {'process_name': app_name},
                                'risk_level': 1
                            })
        
        if suggestions or actions:
            return AIResponse(
                text=suggestions[0] if suggestions else "Welcome back!",
                confidence=0.8,
                suggestions=suggestions,
                actions=actions,
                reasoning=f"Idle for {idle_time} seconds",
                model_used="rule_based"
            )
        
        return None
    
    async def _process_natural_language(self, context: Any) -> Optional[AIResponse]:
        """Process natural language input."""
        query = getattr(context, 'query', '') or str(context)
        
        if not query.strip():
            return None
        
        # Build conversation prompt
        prompt = self._build_conversation_prompt(query)
        
        try:
            # Use local conversational model
            model_response = await self.models.generate_response(
                prompt=prompt,
                model_type="conversation",
                max_tokens=300,
                temperature=0.7
            )
            
            # Parse and format response
            response_text = model_response.get('text', '').strip()
            
            # Apply personality adjustments
            response_text = self._apply_personality(response_text)
            
            return AIResponse(
                text=response_text,
                confidence=model_response.get('confidence', 0.8),
                reasoning="Natural language conversation",
                model_used=model_response.get('model_name', 'local'),
                processing_time=model_response.get('processing_time', 0.0)
            )
            
        except Exception as e:
            self.logger.error(f"Natural language processing failed: {e}")
            return AIResponse(
                text="I'm having trouble processing that right now. Could you try rephrasing?",
                confidence=0.3,
                reasoning="Fallback response due to processing error",
                model_used="fallback"
            )
    
    async def _process_system_event(self, context: Any) -> Optional[AIResponse]:
        """Process system event context."""
        event_type = getattr(context, 'event_type', '')
        
        if not event_type:
            return None
        
        suggestions = []
        
        if event_type == 'low_battery':
            suggestions.append("Your battery is running low. Consider plugging in your charger.")
        elif event_type == 'high_cpu':
            suggestions.append("Your system is running high CPU usage. Close some applications if possible.")
        elif event_type == 'low_memory':
            suggestions.append("Memory usage is high. Consider closing unused applications.")
        elif event_type == 'network_disconnected':
            suggestions.append("Network connection lost. Check your internet connection.")
        
        if suggestions:
            return AIResponse(
                text=suggestions[0],
                confidence=0.9,
                suggestions=suggestions,
                reasoning=f"System event: {event_type}",
                model_used="rule_based"
            )
        
        return None
    
    # Helper Methods
    def _build_screen_analysis_prompt(self, ocr_text: str, context: Any) -> str:
        """Build prompt for screen content analysis."""
        user_profile = self.memory.current_user_profile
        
        prompt = f"""Analyze this screen content and provide helpful insights:

Screen Text: {ocr_text[:1000]}  # Limit text length

User Context:
- Communication style: {user_profile.communication_style if user_profile else 'balanced'}
- Current time: {time.strftime('%H:%M')}

Provide:
1. Brief analysis of what the user is doing
2. Any helpful suggestions
3. Possible actions to assist

Keep response concise and helpful."""
        
        return prompt
    
    def _build_conversation_prompt(self, query: str) -> str:
        """Build prompt for natural language conversation."""
        user_profile = self.memory.current_user_profile
        
        # Build conversation history context
        recent_history = []
        for entry in self.conversation_history[-5:]:  # Last 5 exchanges
            if entry['context_type'] == 'natural_language':
                recent_history.append(entry['response']['text'])
        
        history_context = "\n".join(recent_history[-3:]) if recent_history else ""
        
        prompt = f"""You are Lumora, an intelligent AI assistant. Respond naturally and helpfully.

User Profile:
- Communication style: {user_profile.communication_style if user_profile else 'balanced'}
- Interests: {', '.join(user_profile.interests) if user_profile and user_profile.interests else 'general'}

Recent conversation:
{history_context}

User: {query}
Lumora:"""
        
        return prompt
    
    def _parse_model_response(self, model_response: Dict[str, Any]) -> Dict[str, Any]:
        """Parse model response into structured format."""
        text = model_response.get('text', '')
        
        # Try to parse structured response
        try:
            # Look for JSON in response
            if '{' in text and '}' in text:
                start = text.find('{')
                end = text.rfind('}') + 1
                json_part = text[start:end]
                parsed = json.loads(json_part)
                return parsed
        except:
            pass
        
        # Fallback to simple text response
        return {
            'text': text,
            'confidence': model_response.get('confidence', 0.5),
            'suggestions': [],
            'actions': []
        }
    
    def _apply_personality(self, text: str) -> str:
        """Apply personality adjustments to response text."""
        if self.current_personality == "casual":
            # Make more casual
            text = text.replace("I would suggest", "I'd say")
            text = text.replace("However,", "But")
            if not text.endswith(('!', '?')):
                text += "!"
        elif self.current_personality == "professional":
            # Make more formal
            text = text.replace("I'd", "I would")
            text = text.replace("can't", "cannot")
        elif self.current_personality == "friendly":
            # Add friendliness
            if self.friend_mode_enabled:
                friendly_starters = ["Hey! ", "Hi there! ", "Hello! "]
                if not any(text.startswith(starter) for starter in friendly_starters):
                    text = "Hey! " + text
        
        return text
    
    def _is_productivity_app(self, app_name: str) -> bool:
        """Check if app is considered productive."""
        productive_apps = [
            'code', 'visual studio', 'notepad', 'word', 'excel', 'powerpoint',
            'photoshop', 'illustrator', 'blender', 'figma', 'slack', 'teams'
        ]
        return any(prod_app in app_name.lower() for prod_app in productive_apps)
    
    def _is_distraction_app(self, app_name: str) -> bool:
        """Check if app is considered distracting."""
        distraction_apps = [
            'youtube', 'netflix', 'games', 'steam', 'twitch', 'tiktok',
            'instagram', 'facebook', 'twitter', 'reddit', 'discord'
        ]
        return any(dist_app in app_name.lower() for dist_app in distraction_apps)
    
    def _is_work_hours(self) -> bool:
        """Check if current time is within work hours."""
        user_profile = self.memory.current_user_profile
        if user_profile and user_profile.productivity_hours:
            current_hour = time.localtime().tm_hour
            return current_hour in user_profile.productivity_hours
        
        # Default work hours
        return 9 <= time.localtime().tm_hour <= 17
    
    def _calculate_typing_speed(self, input_events: List[Any]) -> float:
        """Calculate typing speed from input events."""
        if not input_events:
            return 0.0
        
        # Count keyboard events in recent time window
        current_time = time.time()
        recent_events = [
            event for event in input_events
            if hasattr(event, 'timestamp') and 
               hasattr(event, 'event_type') and
               event.event_type == 'keyboard' and
               current_time - event.timestamp < 60  # Last minute
        ]
        
        if len(recent_events) < 2:
            return 0.0
        
        # Calculate characters per minute
        time_span = recent_events[-1].timestamp - recent_events[0].timestamp
        if time_span > 0:
            chars_per_second = len(recent_events) / time_span
            return chars_per_second * 60  # Convert to per minute
        
        return 0.0
    
    # Public Interface
    async def process_context(self, context: Any) -> Optional[AIResponse]:
        """Process context and return AI response."""
        if not self.is_active:
            return None
        
        # Determine context type
        context_type = self._determine_context_type(context)
        
        # Queue for processing
        await self.processing_queue.put({
            'type': context_type,
            'context': context
        })
        
        return None  # Processing is async
    
    async def process_natural_language(self, query: str) -> Optional[AIResponse]:
        """Process natural language query directly."""
        if not self.is_active:
            return None
        
        # Create context object
        context = type('Context', (), {'query': query})()
        
        # Process directly for immediate response
        return await self._process_natural_language(context)
    
    def _determine_context_type(self, context: Any) -> ContextType:
        """Determine the type of context."""
        if hasattr(context, 'query'):
            return ContextType.NATURAL_LANGUAGE
        elif hasattr(context, 'from_app') and hasattr(context, 'to_app'):
            return ContextType.APP_SWITCH
        elif hasattr(context, 'screen_content'):
            return ContextType.SCREEN_CHANGE
        elif hasattr(context, 'recent_inputs'):
            return ContextType.INPUT_ACTIVITY
        elif hasattr(context, 'idle_time'):
            return ContextType.IDLE_DETECTION
        elif hasattr(context, 'event_type'):
            return ContextType.SYSTEM_EVENT
        else:
            return ContextType.SYSTEM_EVENT
    
    # Event Handlers
    async def on_context_change(self, context: Any):
        """Handle context change events."""
        await self.process_context(context)
    
    async def on_app_switch(self, from_app: str, to_app: str):
        """Handle application switch events."""
        context = type('Context', (), {
            'from_app': from_app,
            'to_app': to_app
        })()
        await self.process_context(context)
    
    async def on_screen_change(self, screen_data: Any):
        """Handle screen change events."""
        context = type('Context', (), {
            'screen_content': screen_data
        })()
        await self.process_context(context)
    
    async def on_input_activity(self, input_data: Any):
        """Handle input activity events."""
        context = type('Context', (), {
            'recent_inputs': input_data
        })()
        await self.process_context(context)
    
    # Control Methods
    def has_pending_tasks(self) -> bool:
        """Check if there are pending AI tasks."""
        return not self.processing_queue.empty()
    
    def is_active(self) -> bool:
        """Check if AI brain is active."""
        return self.is_active
    
    def set_personality(self, personality: str):
        """Set AI personality mode."""
        valid_personalities = ["balanced", "professional", "casual", "friendly", "technical"]
        if personality in valid_personalities:
            self.current_personality = personality
            self.logger.info(f"AI personality set to {personality}")
    
    def enable_friend_mode(self, enabled: bool = True):
        """Enable or disable friend mode."""
        self.friend_mode_enabled = enabled
        if enabled:
            self.current_personality = "friendly"
        self.logger.info(f"Friend mode {'enabled' if enabled else 'disabled'}")
    
    def set_proactive_mode(self, enabled: bool = True):
        """Enable or disable proactive suggestions."""
        self.proactive_mode = enabled
        self.logger.info(f"Proactive mode {'enabled' if enabled else 'disabled'}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get AI brain statistics."""
        return {
            **self.stats,
            'is_active': self.is_active,
            'current_personality': self.current_personality,
            'friend_mode': self.friend_mode_enabled,
            'proactive_mode': self.proactive_mode,
            'conversation_length': len(self.conversation_history),
            'queue_size': self.processing_queue.qsize()
        }
    
    async def shutdown(self):
        """Shutdown AI brain."""
        self.logger.info("Shutting down AI Brain...")
        self.is_active = False
        
        # Wait for processing queue to clear
        await self.processing_queue.join()
        
        self.logger.info("AI Brain shutdown complete")
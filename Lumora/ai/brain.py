"""
LUMORA AI Brain

Central AI intelligence system that provides:
- Natural language understanding
- Intent recognition and classification
- Context-aware responses
- Conversation management
- Learning and adaptation
"""

import time
import json
import logging
import asyncio
import re
from typing import Dict, Any, List, Optional, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
import hashlib

class ConversationMode(Enum):
    """Different conversation modes for the AI."""
    ASSISTANT = "assistant"  # Professional helper
    FRIEND = "friend"       # Casual companion
    EXPERT = "expert"       # Technical advisor
    SILENT = "silent"       # Minimal interaction

class IntentType(Enum):
    """Types of user intents."""
    INFORMATION = "information"
    ACTION = "action"
    AUTOMATION = "automation"
    CONFIGURATION = "configuration"
    CONVERSATION = "conversation"
    EMERGENCY = "emergency"

@dataclass
class Intent:
    """Recognized user intent."""
    intent_type: IntentType
    confidence: float
    entities: Dict[str, Any]
    parameters: Dict[str, Any]
    context: Dict[str, Any]
    timestamp: float = field(default_factory=time.time)

@dataclass
class ConversationContext:
    """Current conversation context."""
    user_id: str
    session_id: str
    mode: ConversationMode
    history: List[Dict[str, Any]]
    current_topic: str
    user_preferences: Dict[str, Any]
    system_context: Dict[str, Any]

class AIBrain:
    """Advanced AI brain for natural language processing and conversation."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Conversation management
        self.conversations: Dict[str, ConversationContext] = {}
        self.current_session = None
        
        # Intent recognition
        self.intent_patterns = self._load_intent_patterns()
        self.entity_extractors = self._init_entity_extractors()
        
        # Response generation
        self.response_templates = self._load_response_templates()
        self.personality_traits = config.get("personality", {})
        
        # Learning system
        self.learned_patterns = {}
        self.user_preferences = {}
        self.conversation_history = []
        
        # Model management
        self.local_models = {}
        self.model_config = config.get("models", {})
        
        self._init_conversation_modes()
    
    def _load_intent_patterns(self) -> Dict[str, List[str]]:
        """Load intent recognition patterns."""
        return {
            IntentType.INFORMATION: [
                r"what is|tell me about|explain|describe|show me",
                r"how do I|how to|how can|what's the way",
                r"where is|where can I find|locate",
                r"when did|when will|what time"
            ],
            IntentType.ACTION: [
                r"open|launch|start|run|execute",
                r"close|quit|exit|stop|end",
                r"click|press|type|send|submit",
                r"copy|paste|cut|delete|move"
            ],
            IntentType.AUTOMATION: [
                r"automate|automatically|set up automation",
                r"repeat this|do this again|remember this",
                r"schedule|remind me|notify me",
                r"whenever I|if I|when I"
            ],
            IntentType.CONFIGURATION: [
                r"settings|preferences|configuration|options",
                r"change|modify|update|adjust|configure",
                r"enable|disable|turn on|turn off",
                r"privacy|security|permissions"
            ],
            IntentType.CONVERSATION: [
                r"hello|hi|hey|good morning|good evening",
                r"how are you|what's up|how's it going",
                r"thank you|thanks|appreciate",
                r"goodbye|bye|see you|talk later"
            ],
            IntentType.EMERGENCY: [
                r"emergency|urgent|critical|important",
                r"stop everything|cancel all|abort",
                r"help|assistance|support|problem"
            ]
        }
    
    def _init_entity_extractors(self) -> Dict[str, Callable]:
        """Initialize entity extraction functions."""
        return {
            "time": self._extract_time_entities,
            "application": self._extract_app_entities,
            "file": self._extract_file_entities,
            "contact": self._extract_contact_entities,
            "location": self._extract_location_entities,
            "number": self._extract_number_entities
        }
    
    def _load_response_templates(self) -> Dict[str, List[str]]:
        """Load response templates for different situations."""
        return {
            "greeting": [
                "Hello! I'm Lumora, your AI companion. How can I help you today?",
                "Hi there! Ready to get some work done together?",
                "Good to see you! What would you like to accomplish?"
            ],
            "confirmation": [
                "Got it! I'll {action} for you.",
                "Sure thing! {action} coming right up.",
                "Absolutely! Let me {action} right away."
            ],
            "clarification": [
                "I want to make sure I understand - you'd like me to {action}?",
                "Just to confirm, should I {action}?",
                "Let me verify - you want me to {action}, correct?"
            ],
            "error": [
                "I encountered an issue: {error}. Let me try a different approach.",
                "Something went wrong: {error}. Would you like me to try again?",
                "Oops! {error}. How would you like me to proceed?"
            ],
            "learning": [
                "I noticed you often {pattern}. Would you like me to automate this?",
                "I see a pattern in your workflow. Want me to set up an automation?",
                "You've done this {count} times. Should I remember this for next time?"
            ],
            "encouragement": [
                "Great work! You're making good progress on {task}.",
                "Looking good! Keep up the momentum with {task}.",
                "Nice! You're really focused on {task} today."
            ]
        }
    
    def _init_conversation_modes(self):
        """Initialize different conversation modes."""
        self.conversation_modes = {
            ConversationMode.ASSISTANT: {
                "tone": "professional",
                "verbosity": "detailed",
                "proactivity": "moderate",
                "formality": "formal"
            },
            ConversationMode.FRIEND: {
                "tone": "casual",
                "verbosity": "conversational",
                "proactivity": "high",
                "formality": "informal"
            },
            ConversationMode.EXPERT: {
                "tone": "technical",
                "verbosity": "comprehensive",
                "proactivity": "low",
                "formality": "professional"
            },
            ConversationMode.SILENT: {
                "tone": "minimal",
                "verbosity": "brief",
                "proactivity": "very_low",
                "formality": "neutral"
            }
        }
    
    async def process_input(self, text: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process natural language input and generate response."""
        if context is None:
            context = {}
        
        start_time = time.time()
        
        try:
            # Preprocess input
            processed_text = self._preprocess_text(text)
            
            # Recognize intent
            intent = await self._recognize_intent(processed_text, context)
            
            # Extract entities
            entities = await self._extract_entities(processed_text, intent)
            
            # Generate response
            response = await self._generate_response(intent, entities, context)
            
            # Update conversation context
            await self._update_conversation_context(text, intent, response, context)
            
            # Learn from interaction
            await self._learn_from_interaction(text, intent, response, context)
            
            result = {
                "input": text,
                "intent": {
                    "type": intent.intent_type.value,
                    "confidence": intent.confidence,
                    "entities": entities,
                    "parameters": intent.parameters
                },
                "response": response,
                "processing_time": time.time() - start_time,
                "context_updated": True
            }
            
            self.logger.debug(f"Processed input: {text[:50]}... -> {intent.intent_type.value}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error processing input: {e}")
            return {
                "input": text,
                "error": str(e),
                "response": {
                    "text": "I'm sorry, I encountered an error processing your request.",
                    "actions": [],
                    "suggestions": ["Could you try rephrasing that?"]
                }
            }
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess input text for better understanding."""
        # Basic text cleaning
        text = text.strip()
        text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
        text = re.sub(r'[^\w\s\?\!\.\,\-\']', '', text)  # Remove special chars
        
        # Expand contractions
        contractions = {
            "I'm": "I am", "you're": "you are", "it's": "it is",
            "that's": "that is", "what's": "what is", "where's": "where is",
            "how's": "how is", "I'll": "I will", "you'll": "you will",
            "won't": "will not", "can't": "cannot", "shouldn't": "should not"
        }
        
        for contraction, expansion in contractions.items():
            text = text.replace(contraction, expansion)
        
        return text
    
    async def _recognize_intent(self, text: str, context: Dict[str, Any]) -> Intent:
        """Recognize user intent from processed text."""
        text_lower = text.lower()
        intent_scores = {}
        
        # Pattern-based intent recognition
        for intent_type, patterns in self.intent_patterns.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    score += 1
            
            if score > 0:
                intent_scores[intent_type] = score / len(patterns)
        
        # Context-based adjustments
        if context.get("current_app"):
            app_name = context["current_app"].lower()
            if "settings" in app_name or "preferences" in app_name:
                intent_scores[IntentType.CONFIGURATION] = intent_scores.get(IntentType.CONFIGURATION, 0) + 0.3
        
        # Emergency detection
        emergency_keywords = ["emergency", "urgent", "critical", "stop", "cancel", "abort"]
        if any(keyword in text_lower for keyword in emergency_keywords):
            intent_scores[IntentType.EMERGENCY] = 1.0
        
        # Determine highest scoring intent
        if intent_scores:
            best_intent = max(intent_scores.items(), key=lambda x: x[1])
            confidence = best_intent[1]
            intent_type = best_intent[0]
        else:
            # Default to conversation if no clear intent
            intent_type = IntentType.CONVERSATION
            confidence = 0.3
        
        return Intent(
            intent_type=intent_type,
            confidence=confidence,
            entities={},
            parameters=self._extract_parameters(text, intent_type),
            context=context
        )
    
    async def _extract_entities(self, text: str, intent: Intent) -> Dict[str, Any]:
        """Extract entities from text based on intent."""
        entities = {}
        
        for entity_type, extractor in self.entity_extractors.items():
            extracted = extractor(text, intent)
            if extracted:
                entities[entity_type] = extracted
        
        return entities
    
    def _extract_time_entities(self, text: str, intent: Intent) -> Optional[Dict[str, Any]]:
        """Extract time-related entities."""
        time_patterns = {
            "now": r"\bnow\b|\bright now\b|\bimmediately\b",
            "later": r"\blater\b|\bin a while\b|\bafter\b",
            "tomorrow": r"\btomorrow\b",
            "today": r"\btoday\b|\bthis day\b",
            "hour": r"(\d+)\s*hours?\b",
            "minute": r"(\d+)\s*minutes?\b",
            "specific_time": r"(\d{1,2}):(\d{2})\s*(am|pm)?"
        }
        
        entities = {}
        for entity, pattern in time_patterns.items():
            match = re.search(pattern, text.lower())
            if match:
                entities[entity] = match.groups() if match.groups() else match.group()
        
        return entities if entities else None
    
    def _extract_app_entities(self, text: str, intent: Intent) -> Optional[Dict[str, Any]]:
        """Extract application-related entities."""
        common_apps = {
            "browser": ["browser", "chrome", "firefox", "edge", "safari"],
            "email": ["email", "mail", "outlook", "gmail", "thunderbird"],
            "editor": ["notepad", "word", "editor", "vscode", "sublime"],
            "file_manager": ["explorer", "files", "finder", "file manager"],
            "calculator": ["calculator", "calc"],
            "settings": ["settings", "control panel", "preferences"]
        }
        
        text_lower = text.lower()
        for app_type, keywords in common_apps.items():
            if any(keyword in text_lower for keyword in keywords):
                return {"type": app_type, "keywords": keywords}
        
        return None
    
    def _extract_file_entities(self, text: str, intent: Intent) -> Optional[Dict[str, Any]]:
        """Extract file-related entities."""
        file_patterns = {
            "filename": r'"([^"]+\.[a-zA-Z0-9]+)"',
            "extension": r'\.([a-zA-Z0-9]+)\b',
            "path": r'[A-Za-z]:\\[^\\/:*?"<>|\r\n]*'
        }
        
        entities = {}
        for entity, pattern in file_patterns.items():
            matches = re.findall(pattern, text)
            if matches:
                entities[entity] = matches
        
        return entities if entities else None
    
    def _extract_contact_entities(self, text: str, intent: Intent) -> Optional[Dict[str, Any]]:
        """Extract contact-related entities."""
        # Email pattern
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        
        # Phone pattern (basic)
        phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        phones = re.findall(phone_pattern, text)
        
        if emails or phones:
            return {"emails": emails, "phones": phones}
        
        return None
    
    def _extract_location_entities(self, text: str, intent: Intent) -> Optional[Dict[str, Any]]:
        """Extract location-related entities."""
        location_keywords = ["folder", "directory", "desktop", "documents", "downloads"]
        
        for keyword in location_keywords:
            if keyword in text.lower():
                return {"type": keyword}
        
        return None
    
    def _extract_number_entities(self, text: str, intent: Intent) -> Optional[Dict[str, Any]]:
        """Extract numeric entities."""
        numbers = re.findall(r'\b\d+\b', text)
        if numbers:
            return {"numbers": [int(n) for n in numbers]}
        
        return None
    
    def _extract_parameters(self, text: str, intent_type: IntentType) -> Dict[str, Any]:
        """Extract parameters specific to intent type."""
        parameters = {}
        
        if intent_type == IntentType.ACTION:
            # Extract action verbs
            action_verbs = ["open", "close", "click", "type", "send", "copy", "paste"]
            for verb in action_verbs:
                if verb in text.lower():
                    parameters["action"] = verb
                    break
        
        elif intent_type == IntentType.AUTOMATION:
            # Extract automation triggers
            if "when" in text.lower():
                parameters["trigger_type"] = "conditional"
            elif "every" in text.lower():
                parameters["trigger_type"] = "scheduled"
        
        return parameters
    
    async def _generate_response(self, intent: Intent, entities: Dict[str, Any], 
                               context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate appropriate response based on intent and context."""
        conversation_mode = context.get("conversation_mode", ConversationMode.ASSISTANT)
        mode_config = self.conversation_modes[conversation_mode]
        
        response = {
            "text": "",
            "actions": [],
            "suggestions": [],
            "confidence": intent.confidence,
            "followup_questions": []
        }
        
        # Generate response based on intent type
        if intent.intent_type == IntentType.INFORMATION:
            response = await self._generate_information_response(intent, entities, context)
        
        elif intent.intent_type == IntentType.ACTION:
            response = await self._generate_action_response(intent, entities, context)
        
        elif intent.intent_type == IntentType.AUTOMATION:
            response = await self._generate_automation_response(intent, entities, context)
        
        elif intent.intent_type == IntentType.CONFIGURATION:
            response = await self._generate_configuration_response(intent, entities, context)
        
        elif intent.intent_type == IntentType.CONVERSATION:
            response = await self._generate_conversation_response(intent, entities, context)
        
        elif intent.intent_type == IntentType.EMERGENCY:
            response = await self._generate_emergency_response(intent, entities, context)
        
        # Adjust response based on conversation mode
        response = self._adjust_response_for_mode(response, mode_config)
        
        return response
    
    async def _generate_information_response(self, intent: Intent, entities: Dict[str, Any], 
                                           context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate response for information requests."""
        return {
            "text": "I'd be happy to help you with that information. Let me gather what you need.",
            "actions": ["search", "analyze"],
            "suggestions": ["Would you like me to show you the details?"],
            "confidence": intent.confidence
        }
    
    async def _generate_action_response(self, intent: Intent, entities: Dict[str, Any], 
                                      context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate response for action requests."""
        action = intent.parameters.get("action", "perform the action")
        
        return {
            "text": f"I'll {action} for you right away.",
            "actions": [action],
            "suggestions": [],
            "confidence": intent.confidence
        }
    
    async def _generate_automation_response(self, intent: Intent, entities: Dict[str, Any], 
                                          context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate response for automation requests."""
        return {
            "text": "I can set up that automation for you. Let me configure the triggers and actions.",
            "actions": ["create_automation"],
            "suggestions": ["Would you like to test it first?"],
            "confidence": intent.confidence
        }
    
    async def _generate_configuration_response(self, intent: Intent, entities: Dict[str, Any], 
                                             context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate response for configuration requests."""
        return {
            "text": "I can help you adjust those settings. What specifically would you like to change?",
            "actions": ["open_settings"],
            "suggestions": ["Show me privacy settings", "Change notification preferences"],
            "confidence": intent.confidence
        }
    
    async def _generate_conversation_response(self, intent: Intent, entities: Dict[str, Any], 
                                            context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate response for conversational input."""
        templates = self.response_templates.get("greeting", ["Hello! How can I help you?"])
        text = templates[hash(context.get("session_id", "")) % len(templates)]
        
        return {
            "text": text,
            "actions": [],
            "suggestions": ["What would you like to work on?", "Need help with anything?"],
            "confidence": intent.confidence
        }
    
    async def _generate_emergency_response(self, intent: Intent, entities: Dict[str, Any], 
                                         context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate response for emergency situations."""
        return {
            "text": "I'm stopping all current actions immediately. How can I help?",
            "actions": ["emergency_stop", "cancel_all"],
            "suggestions": [],
            "confidence": 1.0,
            "priority": "high"
        }
    
    def _adjust_response_for_mode(self, response: Dict[str, Any], 
                                mode_config: Dict[str, Any]) -> Dict[str, Any]:
        """Adjust response based on conversation mode."""
        # Adjust verbosity
        if mode_config["verbosity"] == "brief":
            # Shorten the response
            response["text"] = response["text"].split('.')[0] + '.'
        elif mode_config["verbosity"] == "detailed":
            # Add more context
            response["followup_questions"] = response.get("followup_questions", [])
        
        # Adjust tone
        if mode_config["tone"] == "casual":
            response["text"] = response["text"].replace("I will", "I'll")
            response["text"] = response["text"].replace("I would", "I'd")
        
        return response
    
    async def _update_conversation_context(self, input_text: str, intent: Intent, 
                                         response: Dict[str, Any], context: Dict[str, Any]):
        """Update conversation context with new interaction."""
        session_id = context.get("session_id", "default")
        
        if session_id not in self.conversations:
            self.conversations[session_id] = ConversationContext(
                user_id=context.get("user_id", "default"),
                session_id=session_id,
                mode=context.get("conversation_mode", ConversationMode.ASSISTANT),
                history=[],
                current_topic="",
                user_preferences={},
                system_context={}
            )
        
        conversation = self.conversations[session_id]
        
        # Add interaction to history
        interaction = {
            "timestamp": time.time(),
            "input": input_text,
            "intent": intent.intent_type.value,
            "response": response["text"],
            "confidence": intent.confidence
        }
        
        conversation.history.append(interaction)
        
        # Limit history size
        if len(conversation.history) > 100:
            conversation.history = conversation.history[-50:]  # Keep last 50
        
        # Update current topic
        if intent.intent_type != IntentType.CONVERSATION:
            conversation.current_topic = intent.intent_type.value
    
    async def _learn_from_interaction(self, input_text: str, intent: Intent, 
                                    response: Dict[str, Any], context: Dict[str, Any]):
        """Learn from user interactions to improve future responses."""
        # Create learning entry
        learning_entry = {
            "input_hash": hashlib.md5(input_text.encode()).hexdigest(),
            "intent_type": intent.intent_type.value,
            "confidence": intent.confidence,
            "context": context,
            "timestamp": time.time()
        }
        
        # Store for pattern analysis
        input_pattern = self._extract_pattern(input_text)
        if input_pattern:
            if input_pattern not in self.learned_patterns:
                self.learned_patterns[input_pattern] = []
            
            self.learned_patterns[input_pattern].append(learning_entry)
        
        # Update user preferences
        user_id = context.get("user_id", "default")
        if user_id not in self.user_preferences:
            self.user_preferences[user_id] = {}
        
        # Learn from successful interactions
        if intent.confidence > 0.8:
            prefs = self.user_preferences[user_id]
            prefs["preferred_response_length"] = len(response["text"])
            prefs["common_intents"] = prefs.get("common_intents", [])
            if intent.intent_type.value not in prefs["common_intents"]:
                prefs["common_intents"].append(intent.intent_type.value)
    
    def _extract_pattern(self, text: str) -> Optional[str]:
        """Extract reusable patterns from input text."""
        # Normalize text for pattern extraction
        normalized = re.sub(r'\b\d+\b', '[NUMBER]', text.lower())
        normalized = re.sub(r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b', '[EMAIL]', normalized)
        normalized = re.sub(r'\b\w+\.(com|org|net|edu)\b', '[URL]', normalized)
        
        # Extract meaningful patterns (sequences of words)
        words = normalized.split()
        if len(words) >= 3:
            return ' '.join(words[:3])  # First 3 words as pattern
        
        return None
    
    def set_conversation_mode(self, session_id: str, mode: ConversationMode):
        """Set conversation mode for a session."""
        if session_id in self.conversations:
            self.conversations[session_id].mode = mode
        
        self.logger.info(f"Set conversation mode to {mode.value} for session {session_id}")
    
    def get_conversation_stats(self, session_id: str = None) -> Dict[str, Any]:
        """Get conversation statistics."""
        if session_id and session_id in self.conversations:
            conversation = self.conversations[session_id]
            return {
                "session_id": session_id,
                "total_interactions": len(conversation.history),
                "current_topic": conversation.current_topic,
                "mode": conversation.mode.value,
                "recent_confidence": [i["confidence"] for i in conversation.history[-10:]]
            }
        else:
            return {
                "total_sessions": len(self.conversations),
                "total_patterns_learned": len(self.learned_patterns),
                "total_users": len(self.user_preferences)
            }
    
    def get_suggestions(self, context: Dict[str, Any]) -> List[str]:
        """Get contextual suggestions for the user."""
        suggestions = []
        
        # Based on current context
        current_app = context.get("current_app", "")
        if current_app:
            suggestions.append(f"Need help with {current_app}?")
        
        # Based on time of day
        current_hour = time.localtime().tm_hour
        if 9 <= current_hour <= 17:
            suggestions.append("Ready to tackle your work tasks?")
        elif current_hour >= 18:
            suggestions.append("Time to wrap up the day?")
        
        # Based on learned patterns
        user_id = context.get("user_id", "default")
        if user_id in self.user_preferences:
            common_intents = self.user_preferences[user_id].get("common_intents", [])
            if "action" in common_intents:
                suggestions.append("Want me to automate something?")
        
        return suggestions[:3]  # Limit to 3 suggestions
"""
LUMORA Memory Bank

Long-term memory and learning system that stores interactions,
builds user profiles, and provides contextual knowledge to the AI brain.
"""

import sqlite3
import json
import time
import logging
import hashlib
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import threading

@dataclass
class Interaction:
    """Represents a single interaction with the system."""
    id: Optional[int] = None
    timestamp: float = 0.0
    context_type: str = ""
    context_data: Dict[str, Any] = None
    ai_response: Dict[str, Any] = None
    user_feedback: Optional[str] = None
    session_id: str = ""
    importance_score: float = 0.5
    
    def __post_init__(self):
        if self.context_data is None:
            self.context_data = {}
        if self.timestamp == 0.0:
            self.timestamp = time.time()

@dataclass
class UserProfile:
    """User behavior and preference profile."""
    user_id: str
    created_at: float
    updated_at: float
    
    # Application usage patterns
    app_preferences: Dict[str, float] = None
    productivity_hours: List[int] = None
    work_patterns: Dict[str, Any] = None
    
    # Communication style
    communication_style: str = "balanced"  # formal, casual, technical, friendly
    preferred_response_length: str = "medium"  # short, medium, long
    humor_level: float = 0.5
    
    # Learning preferences
    learning_topics: Dict[str, float] = None
    skill_levels: Dict[str, str] = None
    interests: List[str] = None
    
    # Privacy preferences
    privacy_level: str = "balanced"
    data_sharing_consent: bool = False
    
    def __post_init__(self):
        if self.app_preferences is None:
            self.app_preferences = {}
        if self.productivity_hours is None:
            self.productivity_hours = list(range(9, 17))  # 9 AM to 5 PM
        if self.work_patterns is None:
            self.work_patterns = {}
        if self.learning_topics is None:
            self.learning_topics = {}
        if self.skill_levels is None:
            self.skill_levels = {}
        if self.interests is None:
            self.interests = []

@dataclass
class MemoryStats:
    """Memory bank statistics."""
    total_interactions: int = 0
    total_size_mb: float = 0.0
    oldest_record: Optional[float] = None
    newest_record: Optional[float] = None
    avg_importance_score: float = 0.0
    top_apps: List[Tuple[str, int]] = None
    
    def __post_init__(self):
        if self.top_apps is None:
            self.top_apps = []

class MemoryBank:
    """
    Long-term memory and learning system for Lumora.
    
    Stores interactions, builds user profiles, and provides
    contextual knowledge for intelligent responses.
    """
    
    def __init__(self, config_manager):
        self.config = config_manager
        self.logger = logging.getLogger(__name__)
        
        # Database setup
        self.db_path = Path(self.config.get('data_dir', 'data')) / 'memory_bank.db'
        self.db_path.parent.mkdir(exist_ok=True)
        
        # Thread safety
        self._lock = threading.RLock()
        self._connection_cache = threading.local()
        
        # Memory management
        self.max_memory_size_mb = self.config.get('memory.max_size_mb', 500)
        self.retention_days = self.config.get('memory.retention_days', 90)
        self.importance_threshold = 0.3
        
        # User profile
        self.current_user_profile = None
        self.session_id = self._generate_session_id()
        
        # Performance tracking
        self.stats = MemoryStats()
        
    async def initialize(self):
        """Initialize the memory bank."""
        try:
            self.logger.info("Initializing Memory Bank...")
            
            # Create database schema
            await self._create_schema()
            
            # Load user profile
            await self._load_user_profile()
            
            # Update statistics
            await self._update_stats()
            
            # Clean old data
            await self._cleanup_old_data()
            
            self.logger.info("Memory Bank initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Memory Bank: {e}")
            return False
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get thread-local database connection."""
        if not hasattr(self._connection_cache, 'connection'):
            self._connection_cache.connection = sqlite3.connect(
                self.db_path,
                check_same_thread=False,
                timeout=30.0
            )
            # Enable foreign keys and WAL mode for better performance
            self._connection_cache.connection.execute("PRAGMA foreign_keys = ON")
            self._connection_cache.connection.execute("PRAGMA journal_mode = WAL")
            
        return self._connection_cache.connection
    
    async def _create_schema(self):
        """Create database schema."""
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Interactions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    context_type TEXT NOT NULL,
                    context_data TEXT NOT NULL,
                    ai_response TEXT,
                    user_feedback TEXT,
                    session_id TEXT NOT NULL,
                    importance_score REAL DEFAULT 0.5,
                    created_at REAL DEFAULT (strftime('%s', 'now'))
                )
            """)
            
            # User profiles table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_profiles (
                    user_id TEXT PRIMARY KEY,
                    profile_data TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL
                )
            """)
            
            # App usage patterns table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS app_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    app_name TEXT NOT NULL,
                    timestamp REAL NOT NULL,
                    duration_seconds REAL,
                    context_type TEXT,
                    session_id TEXT NOT NULL
                )
            """)
            
            # Learning data table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS learning_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    topic TEXT NOT NULL,
                    data_type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    confidence_score REAL DEFAULT 0.5,
                    created_at REAL DEFAULT (strftime('%s', 'now')),
                    updated_at REAL DEFAULT (strftime('%s', 'now'))
                )
            """)
            
            # Suggestions and feedback table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS suggestions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    suggestion_text TEXT NOT NULL,
                    suggestion_type TEXT NOT NULL,
                    context_hash TEXT,
                    user_response TEXT,
                    effectiveness_score REAL,
                    timestamp REAL NOT NULL,
                    session_id TEXT NOT NULL
                )
            """)
            
            # Create indexes for better performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_interactions_timestamp ON interactions(timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_interactions_session ON interactions(session_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_interactions_importance ON interactions(importance_score)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_app_usage_app ON app_usage(app_name)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_app_usage_timestamp ON app_usage(timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_learning_topic ON learning_data(topic)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_suggestions_type ON suggestions(suggestion_type)")
            
            conn.commit()
    
    async def store_interaction(self, context: Any, ai_response: Any = None, 
                              timestamp: float = None) -> int:
        """Store an interaction in memory."""
        if timestamp is None:
            timestamp = time.time()
        
        # Calculate importance score
        importance_score = self._calculate_importance(context, ai_response)
        
        # Skip storing low-importance interactions if memory is full
        if not await self._should_store_interaction(importance_score):
            return -1
        
        interaction = Interaction(
            timestamp=timestamp,
            context_type=self._get_context_type(context),
            context_data=self._serialize_context(context),
            ai_response=self._serialize_response(ai_response),
            session_id=self.session_id,
            importance_score=importance_score
        )
        
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO interactions 
                (timestamp, context_type, context_data, ai_response, session_id, importance_score)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                interaction.timestamp,
                interaction.context_type,
                json.dumps(interaction.context_data),
                json.dumps(interaction.ai_response) if interaction.ai_response else None,
                interaction.session_id,
                interaction.importance_score
            ))
            
            interaction_id = cursor.lastrowid
            conn.commit()
            
            # Update app usage tracking
            if hasattr(context, 'active_app') and context.active_app:
                await self._record_app_usage(context.active_app, timestamp)
            
            self.logger.debug(f"Stored interaction {interaction_id} with importance {importance_score:.3f}")
            return interaction_id
    
    async def store_suggestion(self, suggestion: Dict[str, Any]) -> int:
        """Store an AI suggestion for tracking effectiveness."""
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO suggestions 
                (suggestion_text, suggestion_type, context_hash, timestamp, session_id)
                VALUES (?, ?, ?, ?, ?)
            """, (
                suggestion.get('text', ''),
                suggestion.get('type', 'general'),
                suggestion.get('context_hash', ''),
                time.time(),
                self.session_id
            ))
            
            suggestion_id = cursor.lastrowid
            conn.commit()
            
            return suggestion_id
    
    async def record_user_feedback(self, interaction_id: int, feedback: str, 
                                 effectiveness_score: float = None):
        """Record user feedback for an interaction or suggestion."""
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Update interaction feedback
            cursor.execute("""
                UPDATE interactions 
                SET user_feedback = ? 
                WHERE id = ?
            """, (feedback, interaction_id))
            
            # If effectiveness score provided, update suggestion
            if effectiveness_score is not None:
                cursor.execute("""
                    UPDATE suggestions 
                    SET user_response = ?, effectiveness_score = ?
                    WHERE id = ?
                """, (feedback, effectiveness_score, interaction_id))
            
            conn.commit()
            
            # Learn from feedback
            await self._learn_from_feedback(interaction_id, feedback, effectiveness_score)
    
    async def get_contextual_memory(self, context: Any, limit: int = 10) -> List[Dict[str, Any]]:
        """Get relevant memories based on current context."""
        context_type = self._get_context_type(context)
        app_name = None
        
        if hasattr(context, 'active_app') and context.active_app:
            app_name = context.active_app.name
        
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Get similar contexts from recent history
            query = """
                SELECT id, timestamp, context_type, context_data, ai_response, importance_score
                FROM interactions
                WHERE context_type = ? 
                AND timestamp > ?
                ORDER BY importance_score DESC, timestamp DESC
                LIMIT ?
            """
            
            recent_cutoff = time.time() - (7 * 24 * 3600)  # Last 7 days
            cursor.execute(query, (context_type, recent_cutoff, limit))
            
            memories = []
            for row in cursor.fetchall():
                memory = {
                    'id': row[0],
                    'timestamp': row[1],
                    'context_type': row[2],
                    'context_data': json.loads(row[3]),
                    'ai_response': json.loads(row[4]) if row[4] else None,
                    'importance_score': row[5]
                }
                memories.append(memory)
            
            # If app-specific, get app-related memories
            if app_name:
                cursor.execute("""
                    SELECT id, timestamp, context_type, context_data, ai_response, importance_score
                    FROM interactions
                    WHERE context_data LIKE ?
                    AND timestamp > ?
                    ORDER BY importance_score DESC, timestamp DESC
                    LIMIT ?
                """, (f'%{app_name}%', recent_cutoff, limit // 2))
                
                for row in cursor.fetchall():
                    memory = {
                        'id': row[0],
                        'timestamp': row[1],
                        'context_type': row[2],
                        'context_data': json.loads(row[3]),
                        'ai_response': json.loads(row[4]) if row[4] else None,
                        'importance_score': row[5]
                    }
                    if memory not in memories:
                        memories.append(memory)
            
            return memories[:limit]
    
    async def get_user_profile(self) -> UserProfile:
        """Get current user profile."""
        if self.current_user_profile is None:
            await self._load_user_profile()
        
        return self.current_user_profile
    
    async def update_user_profile(self, updates: Dict[str, Any]):
        """Update user profile with new information."""
        if self.current_user_profile is None:
            await self._load_user_profile()
        
        # Apply updates
        for key, value in updates.items():
            if hasattr(self.current_user_profile, key):
                setattr(self.current_user_profile, key, value)
        
        self.current_user_profile.updated_at = time.time()
        
        # Save to database
        await self._save_user_profile()
    
    async def _load_user_profile(self):
        """Load user profile from database."""
        user_id = self._get_user_id()
        
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT profile_data FROM user_profiles WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            
            if row:
                profile_data = json.loads(row[0])
                self.current_user_profile = UserProfile(**profile_data)
            else:
                # Create new profile
                self.current_user_profile = UserProfile(
                    user_id=user_id,
                    created_at=time.time(),
                    updated_at=time.time()
                )
                await self._save_user_profile()
    
    async def _save_user_profile(self):
        """Save user profile to database."""
        profile_data = asdict(self.current_user_profile)
        
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO user_profiles (user_id, profile_data, created_at, updated_at)
                VALUES (?, ?, ?, ?)
            """, (
                self.current_user_profile.user_id,
                json.dumps(profile_data),
                self.current_user_profile.created_at,
                self.current_user_profile.updated_at
            ))
            
            conn.commit()
    
    async def _record_app_usage(self, app_info: Any, timestamp: float):
        """Record application usage for pattern learning."""
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO app_usage (app_name, timestamp, session_id)
                VALUES (?, ?, ?)
            """, (app_info.name, timestamp, self.session_id))
            
            conn.commit()
            
            # Update user profile app preferences
            if self.current_user_profile:
                current_score = self.current_user_profile.app_preferences.get(app_info.name, 0.0)
                self.current_user_profile.app_preferences[app_info.name] = min(current_score + 0.1, 1.0)
    
    async def learn_from_patterns(self):
        """Analyze stored data to learn user patterns."""
        await self._analyze_productivity_patterns()
        await self._analyze_app_preferences()
        await self._analyze_communication_style()
        await self._update_user_profile({})  # Save changes
    
    async def _analyze_productivity_patterns(self):
        """Analyze when user is most productive."""
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Get activity by hour
            cursor.execute("""
                SELECT strftime('%H', datetime(timestamp, 'unixepoch')) as hour, COUNT(*) as activity
                FROM interactions
                WHERE timestamp > ?
                GROUP BY hour
                ORDER BY activity DESC
            """, (time.time() - (30 * 24 * 3600),))  # Last 30 days
            
            hourly_activity = {}
            for row in cursor.fetchall():
                hourly_activity[int(row[0])] = row[1]
            
            # Update productivity hours
            if hourly_activity:
                top_hours = sorted(hourly_activity.keys(), key=hourly_activity.get, reverse=True)[:8]
                self.current_user_profile.productivity_hours = sorted(top_hours)
    
    async def _analyze_app_preferences(self):
        """Analyze application usage preferences."""
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT app_name, COUNT(*) as usage_count
                FROM app_usage
                WHERE timestamp > ?
                GROUP BY app_name
                ORDER BY usage_count DESC
            """, (time.time() - (30 * 24 * 3600),))  # Last 30 days
            
            total_usage = 0
            app_counts = {}
            
            for row in cursor.fetchall():
                app_counts[row[0]] = row[1]
                total_usage += row[1]
            
            # Normalize to preferences (0-1 scale)
            if total_usage > 0:
                for app, count in app_counts.items():
                    preference_score = count / total_usage
                    self.current_user_profile.app_preferences[app] = preference_score
    
    async def _analyze_communication_style(self):
        """Analyze user's communication and response preferences."""
        # This would analyze user feedback and responses to determine
        # preferred communication style, response length, etc.
        # For now, we'll use basic heuristics
        
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Analyze feedback sentiment
            cursor.execute("""
                SELECT user_feedback
                FROM interactions
                WHERE user_feedback IS NOT NULL
                AND timestamp > ?
            """, (time.time() - (30 * 24 * 3600),))
            
            feedback_samples = [row[0] for row in cursor.fetchall()]
            
            if feedback_samples:
                # Simple analysis - count positive/negative words
                positive_words = ['good', 'great', 'helpful', 'perfect', 'excellent', 'thanks']
                negative_words = ['bad', 'wrong', 'annoying', 'useless', 'stop']
                
                positive_count = sum(
                    sum(word in feedback.lower() for word in positive_words)
                    for feedback in feedback_samples
                )
                negative_count = sum(
                    sum(word in feedback.lower() for word in negative_words)
                    for feedback in feedback_samples
                )
                
                total_feedback = len(feedback_samples)
                if total_feedback > 0:
                    satisfaction_ratio = positive_count / (positive_count + negative_count + 1)
                    
                    # Adjust communication style based on satisfaction
                    if satisfaction_ratio > 0.7:
                        self.current_user_profile.communication_style = "friendly"
                    elif satisfaction_ratio < 0.3:
                        self.current_user_profile.communication_style = "formal"
                    else:
                        self.current_user_profile.communication_style = "balanced"
    
    def _calculate_importance(self, context: Any, ai_response: Any = None) -> float:
        """Calculate importance score for an interaction."""
        importance = 0.5  # Base importance
        
        # Context-based importance
        if hasattr(context, 'activity_level'):
            importance += context.activity_level * 0.2
        
        if hasattr(context, 'screen_content') and context.screen_content:
            if context.screen_content.ocr_text:
                importance += min(len(context.screen_content.ocr_text) / 1000, 0.2)
        
        # Response-based importance
        if ai_response:
            if hasattr(ai_response, 'actions') and ai_response.actions:
                importance += len(ai_response.actions) * 0.1
            
            if hasattr(ai_response, 'confidence') and ai_response.confidence:
                importance += ai_response.confidence * 0.2
        
        # Time-based importance (recent events more important)
        current_hour = datetime.now().hour
        if self.current_user_profile and current_hour in self.current_user_profile.productivity_hours:
            importance += 0.1
        
        return min(max(importance, 0.0), 1.0)
    
    async def _should_store_interaction(self, importance_score: float) -> bool:
        """Determine if interaction should be stored based on importance and memory limits."""
        # Always store high-importance interactions
        if importance_score > 0.8:
            return True
        
        # Check memory usage
        current_size_mb = await self._get_database_size_mb()
        if current_size_mb > self.max_memory_size_mb:
            # Only store if above threshold
            return importance_score > self.importance_threshold
        
        return True
    
    async def _get_database_size_mb(self) -> float:
        """Get current database size in MB."""
        try:
            size_bytes = self.db_path.stat().st_size
            return size_bytes / (1024 * 1024)
        except:
            return 0.0
    
    async def _cleanup_old_data(self):
        """Clean up old, low-importance data."""
        cutoff_time = time.time() - (self.retention_days * 24 * 3600)
        
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Delete old, low-importance interactions
            cursor.execute("""
                DELETE FROM interactions
                WHERE timestamp < ? AND importance_score < ?
            """, (cutoff_time, self.importance_threshold))
            
            # Clean up orphaned app usage records
            cursor.execute("DELETE FROM app_usage WHERE timestamp < ?", (cutoff_time,))
            
            # Clean up old suggestions
            cursor.execute("DELETE FROM suggestions WHERE timestamp < ?", (cutoff_time,))
            
            deleted_count = cursor.rowcount
            conn.commit()
            
            if deleted_count > 0:
                self.logger.info(f"Cleaned up {deleted_count} old memory records")
            
            # Optimize database
            cursor.execute("VACUUM")
    
    async def _update_stats(self):
        """Update memory bank statistics."""
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Get basic stats
            cursor.execute("SELECT COUNT(*) FROM interactions")
            self.stats.total_interactions = cursor.fetchone()[0]
            
            cursor.execute("SELECT MIN(timestamp), MAX(timestamp) FROM interactions")
            row = cursor.fetchone()
            self.stats.oldest_record = row[0]
            self.stats.newest_record = row[1]
            
            cursor.execute("SELECT AVG(importance_score) FROM interactions")
            avg_importance = cursor.fetchone()[0]
            self.stats.avg_importance_score = avg_importance if avg_importance else 0.0
            
            # Get database size
            self.stats.total_size_mb = await self._get_database_size_mb()
            
            # Get top apps
            cursor.execute("""
                SELECT app_name, COUNT(*) as usage_count
                FROM app_usage
                GROUP BY app_name
                ORDER BY usage_count DESC
                LIMIT 10
            """)
            self.stats.top_apps = cursor.fetchall()
    
    def _get_context_type(self, context: Any) -> str:
        """Determine context type from context object."""
        if hasattr(context, 'active_app') and context.active_app:
            return f"app_{context.active_app.name}"
        elif hasattr(context, 'screen_content') and context.screen_content:
            return "screen_analysis"
        elif hasattr(context, 'input_events') and context.input_events:
            return "input_monitoring"
        else:
            return "general"
    
    def _serialize_context(self, context: Any) -> Dict[str, Any]:
        """Serialize context object for storage."""
        if context is None:
            return {}
        
        # Convert context to dictionary, handling special objects
        if hasattr(context, '__dict__'):
            context_dict = {}
            for key, value in context.__dict__.items():
                try:
                    json.dumps(value)  # Test if JSON serializable
                    context_dict[key] = value
                except (TypeError, ValueError):
                    context_dict[key] = str(value)  # Fallback to string
            return context_dict
        else:
            return {'raw_context': str(context)}
    
    def _serialize_response(self, response: Any) -> Dict[str, Any]:
        """Serialize AI response for storage."""
        if response is None:
            return {}
        
        if hasattr(response, '__dict__'):
            response_dict = {}
            for key, value in response.__dict__.items():
                try:
                    json.dumps(value)
                    response_dict[key] = value
                except (TypeError, ValueError):
                    response_dict[key] = str(value)
            return response_dict
        else:
            return {'raw_response': str(response)}
    
    async def _learn_from_feedback(self, interaction_id: int, feedback: str, 
                                 effectiveness_score: float = None):
        """Learn from user feedback to improve future responses."""
        # Update learning data based on feedback
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Get the interaction
            cursor.execute("""
                SELECT context_type, context_data, ai_response
                FROM interactions
                WHERE id = ?
            """, (interaction_id,))
            
            row = cursor.fetchone()
            if row:
                context_type, context_data, ai_response = row
                
                # Store learning data
                learning_content = {
                    'feedback': feedback,
                    'effectiveness_score': effectiveness_score,
                    'context_type': context_type,
                    'original_response': ai_response
                }
                
                cursor.execute("""
                    INSERT INTO learning_data (topic, data_type, content, confidence_score)
                    VALUES (?, ?, ?, ?)
                """, (
                    context_type,
                    'user_feedback',
                    json.dumps(learning_content),
                    effectiveness_score if effectiveness_score else 0.5
                ))
                
                conn.commit()
    
    def _get_user_id(self) -> str:
        """Get or generate user ID."""
        import os
        import platform
        
        # Create user ID based on system info
        system_info = f"{platform.node()}-{os.getenv('USERNAME', 'user')}"
        return hashlib.md5(system_info.encode()).hexdigest()[:16]
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID."""
        session_data = f"{time.time()}-{id(self)}"
        return hashlib.md5(session_data.encode()).hexdigest()[:12]
    
    async def get_statistics(self) -> MemoryStats:
        """Get current memory bank statistics."""
        await self._update_stats()
        return self.stats
    
    async def export_data(self, output_file: str) -> bool:
        """Export memory data to file."""
        try:
            with self._lock:
                conn = self._get_connection()
                
                export_data = {
                    'export_timestamp': time.time(),
                    'user_profile': asdict(self.current_user_profile) if self.current_user_profile else None,
                    'interactions': [],
                    'learning_data': [],
                    'statistics': asdict(self.stats)
                }
                
                # Export interactions
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM interactions ORDER BY timestamp DESC LIMIT 1000")
                
                for row in cursor.fetchall():
                    interaction = {
                        'id': row[0],
                        'timestamp': row[1],
                        'context_type': row[2],
                        'context_data': json.loads(row[3]),
                        'ai_response': json.loads(row[4]) if row[4] else None,
                        'user_feedback': row[5],
                        'session_id': row[6],
                        'importance_score': row[7]
                    }
                    export_data['interactions'].append(interaction)
                
                # Export learning data
                cursor.execute("SELECT * FROM learning_data ORDER BY created_at DESC LIMIT 500")
                
                for row in cursor.fetchall():
                    learning_item = {
                        'id': row[0],
                        'topic': row[1],
                        'data_type': row[2],
                        'content': json.loads(row[3]),
                        'confidence_score': row[4],
                        'created_at': row[5],
                        'updated_at': row[6]
                    }
                    export_data['learning_data'].append(learning_item)
                
                # Write to file
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, default=str)
                
                self.logger.info(f"Memory data exported to {output_file}")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to export memory data: {e}")
            return False
    
    async def shutdown(self):
        """Shutdown memory bank gracefully."""
        self.logger.info("Shutting down Memory Bank...")
        
        # Final cleanup and stats update
        await self._cleanup_old_data()
        await self._update_stats()
        
        # Close database connections
        with self._lock:
            if hasattr(self._connection_cache, 'connection'):
                self._connection_cache.connection.close()
        
        self.logger.info("Memory Bank shutdown complete")
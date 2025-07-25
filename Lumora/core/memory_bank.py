"""
LUMORA Memory Bank

Advanced memory management system that stores and retrieves:
- User behavior patterns
- Context history
- Learning data
- Automation memories
- Conversation history
"""

import sqlite3
import json
import time
import logging
import hashlib
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import threading
from datetime import datetime, timedelta

@dataclass
class MemoryEntry:
    """Single memory entry in the bank."""
    id: Optional[str] = None
    timestamp: float = 0.0
    category: str = ""
    data: Dict[str, Any] = None
    importance: float = 0.5
    context_hash: str = ""
    tags: List[str] = None
    expires_at: Optional[float] = None

class MemoryCategory:
    """Memory categories for organization."""
    USER_ACTION = "user_action"
    SYSTEM_EVENT = "system_event"
    AI_DECISION = "ai_decision"
    AUTOMATION = "automation"
    CONVERSATION = "conversation"
    PATTERN = "pattern"
    PREFERENCE = "preference"
    ERROR = "error"

class MemoryBank:
    """Advanced memory management system."""
    
    def __init__(self, data_dir: Path):
        self.data_dir = Path(data_dir)
        self.db_path = self.data_dir / "memory.db"
        self.logger = logging.getLogger(__name__)
        self._lock = threading.RLock()
        
        # Memory limits
        self.max_entries = 1000000  # 1M entries max
        self.max_age_days = 365  # Keep for 1 year max
        self.cleanup_interval = 3600  # Cleanup every hour
        
        self._initialize_database()
        self._last_cleanup = time.time()
    
    def _initialize_database(self):
        """Initialize the SQLite database."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    timestamp REAL NOT NULL,
                    category TEXT NOT NULL,
                    data TEXT NOT NULL,
                    importance REAL NOT NULL DEFAULT 0.5,
                    context_hash TEXT,
                    tags TEXT,
                    expires_at REAL,
                    created_at REAL DEFAULT (julianday('now'))
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp ON memories(timestamp)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_category ON memories(category)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_importance ON memories(importance)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_context_hash ON memories(context_hash)
            """)
    
    def store_memory(self, category: str, data: Dict[str, Any], 
                    importance: float = 0.5, tags: List[str] = None,
                    expires_in_days: Optional[int] = None) -> str:
        """Store a new memory entry."""
        with self._lock:
            entry_id = hashlib.sha256(
                f"{time.time()}{category}{json.dumps(data, sort_keys=True)}".encode()
            ).hexdigest()[:16]
            
            expires_at = None
            if expires_in_days:
                expires_at = time.time() + (expires_in_days * 24 * 3600)
            
            context_hash = self._generate_context_hash(data)
            tags_json = json.dumps(tags or [])
            data_json = json.dumps(data)
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO memories 
                    (id, timestamp, category, data, importance, context_hash, tags, expires_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (entry_id, time.time(), category, data_json, importance, 
                     context_hash, tags_json, expires_at))
            
            self._maybe_cleanup()
            return entry_id
    
    def retrieve_memories(self, category: Optional[str] = None,
                         since: Optional[float] = None,
                         limit: int = 100,
                         min_importance: float = 0.0) -> List[MemoryEntry]:
        """Retrieve memories matching criteria."""
        with self._lock:
            query = "SELECT * FROM memories WHERE 1=1"
            params = []
            
            if category:
                query += " AND category = ?"
                params.append(category)
            
            if since:
                query += " AND timestamp >= ?"
                params.append(since)
            
            query += " AND importance >= ?"
            params.append(min_importance)
            
            query += " AND (expires_at IS NULL OR expires_at > ?)"
            params.append(time.time())
            
            query += " ORDER BY importance DESC, timestamp DESC LIMIT ?"
            params.append(limit)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(query, params)
                rows = cursor.fetchall()
            
            memories = []
            for row in rows:
                try:
                    memory = MemoryEntry(
                        id=row[0],
                        timestamp=row[1],
                        category=row[2],
                        data=json.loads(row[3]),
                        importance=row[4],
                        context_hash=row[5],
                        tags=json.loads(row[6]) if row[6] else [],
                        expires_at=row[7]
                    )
                    memories.append(memory)
                except Exception as e:
                    self.logger.error(f"Error parsing memory {row[0]}: {e}")
            
            return memories
    
    def find_similar_memories(self, data: Dict[str, Any], 
                            threshold: float = 0.8,
                            limit: int = 10) -> List[MemoryEntry]:
        """Find memories similar to the given data."""
        context_hash = self._generate_context_hash(data)
        
        # First try exact context match
        memories = self.retrieve_memories(limit=limit * 2)
        similar = []
        
        for memory in memories:
            if memory.context_hash == context_hash:
                similar.append(memory)
            elif self._calculate_similarity(data, memory.data) >= threshold:
                similar.append(memory)
        
        return sorted(similar, key=lambda m: m.importance, reverse=True)[:limit]
    
    def update_importance(self, memory_id: str, importance: float):
        """Update the importance of a memory."""
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "UPDATE memories SET importance = ? WHERE id = ?",
                    (importance, memory_id)
                )
    
    def delete_memory(self, memory_id: str):
        """Delete a specific memory."""
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get memory bank statistics."""
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT COUNT(*) FROM memories")
                total_count = cursor.fetchone()[0]
                
                cursor = conn.execute("""
                    SELECT category, COUNT(*) 
                    FROM memories 
                    GROUP BY category
                """)
                by_category = dict(cursor.fetchall())
                
                cursor = conn.execute("""
                    SELECT AVG(importance), MIN(importance), MAX(importance)
                    FROM memories
                """)
                importance_stats = cursor.fetchone()
        
        return {
            "total_memories": total_count,
            "by_category": by_category,
            "average_importance": importance_stats[0] or 0.0,
            "min_importance": importance_stats[1] or 0.0,
            "max_importance": importance_stats[2] or 0.0,
            "db_size_mb": self.db_path.stat().st_size / (1024 * 1024)
        }
    
    def _generate_context_hash(self, data: Dict[str, Any]) -> str:
        """Generate a hash for similar context detection."""
        # Extract key context elements
        context_keys = ["app_name", "window_title", "action_type", "text_content"]
        context_data = {k: v for k, v in data.items() if k in context_keys}
        
        context_str = json.dumps(context_data, sort_keys=True)
        return hashlib.md5(context_str.encode()).hexdigest()[:16]
    
    def _calculate_similarity(self, data1: Dict[str, Any], 
                            data2: Dict[str, Any]) -> float:
        """Calculate similarity between two data objects."""
        # Simple similarity based on common keys and values
        all_keys = set(data1.keys()) | set(data2.keys())
        if not all_keys:
            return 0.0
        
        matches = 0
        for key in all_keys:
            if key in data1 and key in data2:
                if data1[key] == data2[key]:
                    matches += 1
                elif isinstance(data1[key], str) and isinstance(data2[key], str):
                    # String similarity
                    common_words = set(data1[key].lower().split()) & set(data2[key].lower().split())
                    if common_words:
                        matches += len(common_words) / max(len(data1[key].split()), len(data2[key].split()))
        
        return matches / len(all_keys)
    
    def _maybe_cleanup(self):
        """Perform cleanup if needed."""
        now = time.time()
        if now - self._last_cleanup > self.cleanup_interval:
            self._cleanup()
            self._last_cleanup = now
    
    def _cleanup(self):
        """Clean up old and expired memories."""
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                # Delete expired memories
                conn.execute(
                    "DELETE FROM memories WHERE expires_at IS NOT NULL AND expires_at <= ?",
                    (time.time(),)
                )
                
                # Delete old memories if we're over the limit
                cursor = conn.execute("SELECT COUNT(*) FROM memories")
                count = cursor.fetchone()[0]
                
                if count > self.max_entries:
                    # Keep the most important recent memories
                    conn.execute("""
                        DELETE FROM memories WHERE id NOT IN (
                            SELECT id FROM memories 
                            ORDER BY importance DESC, timestamp DESC 
                            LIMIT ?
                        )
                    """, (self.max_entries,))
                
                # Delete very old memories
                old_threshold = time.time() - (self.max_age_days * 24 * 3600)
                conn.execute(
                    "DELETE FROM memories WHERE timestamp < ? AND importance < 0.8",
                    (old_threshold,)
                )
                
                # Vacuum to reclaim space
                conn.execute("VACUUM")
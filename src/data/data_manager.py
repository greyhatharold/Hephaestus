from datetime import datetime
from pathlib import Path
import sqlite3
from typing import List, Optional, Dict, Any
from dataclasses import asdict
import json

from src.data.chat_history import ChatMessage
from src.core.idea import Idea, AgentResponse

class DataManager:
    def __init__(self, database_path: str = "app_data.db"):
        self.db_path = Path(database_path)
        self._init_database()

    def _init_database(self):
        """Initialize database tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Chat messages table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS chat_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sender TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    domain TEXT NOT NULL,
                    session_id TEXT NOT NULL
                )
            ''')
            
            # Ideas table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ideas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    concept TEXT NOT NULL,
                    domain TEXT NOT NULL,
                    keywords TEXT NOT NULL,
                    development_stage TEXT NOT NULL,
                    timestamp TEXT NOT NULL
                )
            ''')
            
            # Diagrams table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS diagrams (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    idea_id INTEGER NOT NULL,
                    image_data TEXT NOT NULL,
                    gpt_response TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    FOREIGN KEY (idea_id) REFERENCES ideas (id)
                )
            ''')
            
            conn.commit()

    # Chat History Methods
    def add_chat_message(self, message: ChatMessage, session_id: str) -> None:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO chat_messages (sender, content, timestamp, domain, session_id)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                message.sender,
                message.content,
                message.timestamp.isoformat(),
                message.domain,
                session_id
            ))
            conn.commit()

    def get_chat_session(self, session_id: str) -> List[ChatMessage]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT sender, content, timestamp, domain
                FROM chat_messages
                WHERE session_id = ?
                ORDER BY timestamp
            ''', (session_id,))
            
            return [
                ChatMessage(
                    sender=row[0],
                    content=row[1],
                    timestamp=datetime.fromisoformat(row[2]),
                    domain=row[3]
                )
                for row in cursor.fetchall()
            ]

    # Idea Processing Methods
    def save_idea(self, idea: Idea, response: AgentResponse) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO ideas (concept, domain, keywords, development_stage, timestamp)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                idea.concept,
                idea.domain.value,
                json.dumps(idea.keywords),
                idea.development_stage,
                datetime.now().isoformat()
            ))
            return cursor.lastrowid

    def get_idea_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM ideas
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))
            
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    # Diagram Methods
    def save_diagram(self, idea_id: int, image_data: str, gpt_response: str) -> None:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO diagrams (idea_id, image_data, gpt_response, timestamp)
                VALUES (?, ?, ?, ?)
            ''', (
                idea_id,
                image_data,
                gpt_response,
                datetime.now().isoformat()
            ))
            conn.commit()

    def get_diagram(self, idea_id: int) -> Optional[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT image_data, gpt_response, timestamp
                FROM diagrams
                WHERE idea_id = ?
                ORDER BY timestamp DESC
                LIMIT 1
            ''', (idea_id,))
            
            row = cursor.fetchone()
            if row:
                return {
                    'image_data': row[0],
                    'gpt_response': row[1],
                    'timestamp': row[2]
                }
            return None 
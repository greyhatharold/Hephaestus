from dataclasses import dataclass
from datetime import datetime
from typing import List
from uuid import uuid4

@dataclass
class ChatMessage:
    sender: str
    content: str
    timestamp: datetime
    domain: str
    
    def to_dict(self) -> dict:
        return {
            'sender': self.sender,
            'content': self.content,
            'timestamp': self.timestamp.isoformat(),
            'domain': self.domain
        }

class ChatHistoryManager:
    def __init__(self, data_manager):
        self.data_manager = data_manager
        self.current_session_id = str(uuid4())
        
    def add_message(self, sender: str, content: str, domain: str) -> ChatMessage:
        """Add a new message to the current session."""
        message = ChatMessage(
            sender=sender,
            content=content,
            timestamp=datetime.now(),
            domain=domain
        )
        self.data_manager.add_chat_message(message, self.current_session_id)
        return message
    
    def get_session_history(self) -> List[ChatMessage]:
        """Get all messages from current session."""
        return self.data_manager.get_chat_session(self.current_session_id)
    
    def new_session(self):
        """Start a new chat session."""
        self.current_session_id = str(uuid4()) 
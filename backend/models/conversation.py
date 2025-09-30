"""
Data models for conversations and messages.

This module defines the core data structures used throughout the application
for managing conversations, messages, and related metadata.
"""

from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any
from enum import Enum


class MessageType(Enum):
    """Enumeration of message types in conversations."""
    USER = "user"
    ASSISTANT_TEXT = "assistant_text"
    ASSISTANT_CHART = "assistant_chart"
    ASSISTANT_ERROR = "assistant_error"


class MessageStatus(Enum):
    """Enumeration of message processing statuses."""
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Message:
    """Represents a single message in a conversation."""
    id: str
    conversation_id: str
    type: str  # MessageType value
    content: str
    timestamp: str
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary representation."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """Create message from dictionary representation."""
        return cls(**data)


@dataclass
class Conversation:
    """Represents a complete conversation with Genie."""
    id: str
    title: str
    created_at: str
    updated_at: str
    messages: List[Message]
    is_active: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert conversation to dictionary representation."""
        return {
            'id': self.id,
            'title': self.title,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'is_active': self.is_active,
            'messages': [msg.to_dict() for msg in self.messages],
            'message_count': len(self.messages)
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Conversation':
        """Create conversation from dictionary representation."""
        messages = [Message.from_dict(msg) for msg in data.get('messages', [])]
        return cls(
            id=data['id'],
            title=data['title'],
            created_at=data['created_at'],
            updated_at=data['updated_at'],
            is_active=data.get('is_active', True),
            messages=messages
        )


@dataclass
class ConversationSummary:
    """Lightweight representation of a conversation for listing purposes."""
    id: str
    title: str
    created_at: str
    updated_at: str
    message_count: int
    is_active: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert conversation summary to dictionary representation."""
        return asdict(self)


@dataclass
class QueuedMessage:
    """Represents a message in the processing queue."""
    id: str
    conversation_id: str
    session_id: str
    user_message: str
    timestamp: str
    status: MessageStatus
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    processing_started_at: Optional[str] = None
    processing_completed_at: Optional[str] = None

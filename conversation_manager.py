"""
Conversation Management for Genie to Chart POC

This module handles conversation sessions, message history, and context management
for continuous conversations with Databricks Genie.
"""

import json
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from loguru import logger


@dataclass
class Message:
    """Represents a single message in a conversation"""
    id: str
    conversation_id: str
    type: str  # 'user', 'assistant_text', 'assistant_chart', 'assistant_error'
    content: str
    timestamp: str
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        return cls(**data)


@dataclass
class Conversation:
    """Represents a complete conversation with Genie"""
    id: str
    title: str
    created_at: str
    updated_at: str
    messages: List[Message]
    is_active: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
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
        messages = [Message.from_dict(msg) for msg in data.get('messages', [])]
        return cls(
            id=data['id'],
            title=data['title'],
            created_at=data['created_at'],
            updated_at=data['updated_at'],
            is_active=data.get('is_active', True),
            messages=messages
        )


class ConversationManager:
    """Manages conversations and message history"""
    
    def __init__(self):
        # In-memory storage for demo (in production, use Redis or database)
        self.conversations: Dict[str, Conversation] = {}
        self.active_conversations: Dict[str, str] = {}  # session_id -> conversation_id
        logger.info("ConversationManager initialized")
    
    def create_conversation(self, title: Optional[str] = None, session_id: Optional[str] = None) -> str:
        """Create a new conversation"""
        conversation_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()
        
        # Generate title from first message or use default
        if not title:
            title = f"Conversation {len(self.conversations) + 1}"
        
        conversation = Conversation(
            id=conversation_id,
            title=title,
            created_at=timestamp,
            updated_at=timestamp,
            messages=[]
        )
        
        self.conversations[conversation_id] = conversation
        
        # Set as active conversation for this session
        if session_id:
            self.active_conversations[session_id] = conversation_id
        
        logger.info(f"Created new conversation: {conversation_id} - '{title}'")
        return conversation_id
    
    def add_message(self, conversation_id: str, message_type: str, content: str, 
                   metadata: Optional[Dict[str, Any]] = None) -> str:
        """Add a message to a conversation"""
        if conversation_id not in self.conversations:
            raise ValueError(f"Conversation {conversation_id} not found")
        
        message_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()
        
        message = Message(
            id=message_id,
            conversation_id=conversation_id,
            type=message_type,
            content=content,
            timestamp=timestamp,
            metadata=metadata
        )
        
        self.conversations[conversation_id].messages.append(message)
        self.conversations[conversation_id].updated_at = timestamp
        
        # Update conversation title if this is the first user message
        if message_type == 'user' and len(self.conversations[conversation_id].messages) == 1:
            # Use first 50 characters of the question as title
            title = content[:50] + "..." if len(content) > 50 else content
            self.conversations[conversation_id].title = title
        
        logger.info(f"Added {message_type} message to conversation {conversation_id}")
        return message_id
    
    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Get a conversation by ID"""
        return self.conversations.get(conversation_id)
    
    def get_conversation_history(self, conversation_id: str, limit: Optional[int] = None) -> List[Message]:
        """Get message history for a conversation"""
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            return []
        
        messages = conversation.messages
        if limit:
            messages = messages[-limit:]  # Get last N messages
        
        return messages
    
    def get_all_conversations(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get all conversations (metadata only, not full messages)"""
        conversations = list(self.conversations.values())
        conversations.sort(key=lambda x: x.updated_at, reverse=True)
        
        if limit:
            conversations = conversations[:limit]
        
        # Return minimal conversation info for sidebar
        return [{
            'id': conv.id,
            'title': conv.title,
            'created_at': conv.created_at,
            'updated_at': conv.updated_at,
            'message_count': len(conv.messages),
            'is_active': conv.is_active
        } for conv in conversations]
    
    def get_active_conversation(self, session_id: str) -> Optional[str]:
        """Get the active conversation ID for a session"""
        return self.active_conversations.get(session_id)
    
    def set_active_conversation(self, session_id: str, conversation_id: str):
        """Set the active conversation for a session"""
        if conversation_id in self.conversations:
            self.active_conversations[session_id] = conversation_id
            logger.info(f"Set active conversation for session {session_id}: {conversation_id}")
        else:
            raise ValueError(f"Conversation {conversation_id} not found")
    
    def delete_conversation(self, conversation_id: str):
        """Delete a conversation"""
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
            
            # Remove from active conversations
            for session_id, active_id in list(self.active_conversations.items()):
                if active_id == conversation_id:
                    del self.active_conversations[session_id]
            
            logger.info(f"Deleted conversation: {conversation_id}")
        else:
            raise ValueError(f"Conversation {conversation_id} not found")
    
    def get_context_for_genie(self, conversation_id: str, context_limit: int = 5) -> str:
        """Get recent conversation context for Genie to maintain conversational flow"""
        messages = self.get_conversation_history(conversation_id, limit=context_limit * 2)
        
        context_parts = []
        for msg in messages[-context_limit:]:  # Get last N messages for context
            if msg.type == 'user':
                context_parts.append(f"User: {msg.content}")
            elif msg.type in ['assistant_text', 'assistant_chart']:
                # For chart responses, include the summary from metadata
                if msg.metadata and 'ai_summary' in msg.metadata:
                    context_parts.append(f"Assistant: {msg.metadata['ai_summary']}")
                else:
                    context_parts.append(f"Assistant: {msg.content[:200]}...")
        
        if context_parts:
            return "Previous conversation context:\n" + "\n".join(context_parts) + "\n\nCurrent question:"
        
        return ""


# Global conversation manager instance
conversation_manager = ConversationManager()


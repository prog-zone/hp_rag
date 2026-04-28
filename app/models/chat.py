from datetime import datetime
from typing import List, Optional
from uuid import uuid4
from sqlmodel import Field, Relationship, SQLModel

class Session(SQLModel, table=True):
    """Represents a unique user session stored in local storage."""
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    chats: List["Chat"] = Relationship(back_populates="session")

class Chat(SQLModel, table=True):
    """Represents an individual chat thread within a session."""
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(default="New Chat")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    session_id: str = Field(foreign_key="session.id")
    session: Session = Relationship(back_populates="chats")
    
    messages: List["Message"] = Relationship(back_populates="chat")

class Message(SQLModel, table=True):
    """Individual messages within a chat thread."""
    id: Optional[int] = Field(default=None, primary_key=True)
    role: str  # "user" or "assistant"
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    chat_id: int = Field(foreign_key="chat.id")
    chat: Chat = Relationship(back_populates="messages")
"""Internal data models for the RAG Chatbot."""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
import uuid


class Chunk(BaseModel):
    """A text chunk from a document."""
    chunk_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    document_id: str
    document_title: str
    source: str
    chunk_index: int
    text: str
    token_count: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)


class RetrievedChunk(BaseModel):
    """A chunk retrieved during similarity search."""
    chunk_id: str
    document_title: str
    source: str
    chunk_index: int
    text: str
    similarity_score: float


class Document(BaseModel):
    """Metadata for an ingested document."""
    document_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    source: str
    file_type: str
    file_size: int = 0
    chunk_count: int = 0
    ingested_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = "pending"  # pending, processing, completed, failed


class Message(BaseModel):
    """A single message in a conversation."""
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class Session(BaseModel):
    """A chat session with conversation history."""
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    messages: list[Message] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_activity: datetime = Field(default_factory=datetime.utcnow)

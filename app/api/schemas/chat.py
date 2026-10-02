"""Pydantic models for chat API request/response."""
from pydantic import BaseModel, Field
from typing import Optional


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    query: str = Field(..., min_length=1, description="User's question")
    session_id: Optional[str] = Field(None, description="Session ID for conversation continuity")
    history: list[dict] = Field(default_factory=list, description="Previous conversation messages")


class SourceInfo(BaseModel):
    """Information about a source document."""
    document_title: str
    source: str
    chunk_index: int
    similarity_score: float


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    response: str
    sources: list[SourceInfo]
    session_id: str

"""Pydantic models for document API request/response."""
from pydantic import BaseModel


class IngestResponse(BaseModel):
    """Response model for document ingestion."""
    document_id: str
    title: str
    chunks_ingested: int
    status: str


class DocumentInfo(BaseModel):
    """Information about an ingested document."""
    document_id: str
    title: str
    source: str
    file_type: str
    file_size: int
    chunk_count: int
    ingested_at: str
    status: str


class DocumentListResponse(BaseModel):
    """Response model for document list."""
    documents: list[DocumentInfo]
    total: int


class DeleteResponse(BaseModel):
    """Response model for document deletion."""
    status: str
    message: str

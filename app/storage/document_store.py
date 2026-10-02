"""SQLite-based document metadata storage."""
import sqlite3
import os
from typing import Optional
from app.models.schemas import Document
from app.config import settings


class DocumentStore:
    """Manages document metadata in SQLite."""

    def __init__(self, db_path: str = None):
        self.db_path = db_path or settings.document_store_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _init_db(self):
        """Initialize the database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    document_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    source TEXT NOT NULL,
                    file_type TEXT NOT NULL,
                    file_size INTEGER DEFAULT 0,
                    chunk_count INTEGER DEFAULT 0,
                    ingested_at TEXT NOT NULL,
                    status TEXT DEFAULT 'pending'
                )
            """)
            conn.commit()

    def add_document(self, document: Document) -> Document:
        """Add a new document to the store."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """INSERT INTO documents
                   (document_id, title, source, file_type, file_size, chunk_count, ingested_at, status)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (document.document_id, document.title, document.source,
                 document.file_type, document.file_size, document.chunk_count,
                 document.ingested_at.isoformat(), document.status)
            )
            conn.commit()
        return document

    def get_document(self, document_id: str) -> Optional[Document]:
        """Retrieve a document by ID."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT * FROM documents WHERE document_id = ?",
                (document_id,)
            ).fetchone()
            if row:
                return Document(**dict(row))
            return None

    def list_documents(self) -> list[Document]:
        """List all documents."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT * FROM documents ORDER BY ingested_at DESC"
            ).fetchall()
            return [Document(**dict(row)) for row in rows]

    def update_status(self, document_id: str, status: str, chunk_count: int = None):
        """Update document status and optionally chunk count."""
        with sqlite3.connect(self.db_path) as conn:
            if chunk_count is not None:
                conn.execute(
                    "UPDATE documents SET status = ?, chunk_count = ? WHERE document_id = ?",
                    (status, chunk_count, document_id)
                )
            else:
                conn.execute(
                    "UPDATE documents SET status = ? WHERE document_id = ?",
                    (status, document_id)
                )
            conn.commit()

    def delete_document(self, document_id: str) -> bool:
        """Delete a document from the store."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "DELETE FROM documents WHERE document_id = ?",
                (document_id,)
            )
            conn.commit()
            return cursor.rowcount > 0

# Implementation Guide

## Groww RAG Chatbot — Phase-Wise Implementation Plan

| Field | Detail |
|---|---|
| **Document Title** | Implementation Guide — Groww RAG Chatbot |
| **Version** | 1.0 |
| **Date** | 2026-09-27 |
| **Author** | Pooja Jaiswal |
| **Status** | Draft |
| **References** | PRD.md (v1.0), architecture.md (v1.0) |

---

## 1. How to Use This Document

This document breaks down the implementation of the Groww RAG Chatbot into **6 sequential phases**, each with concrete tasks, files to create, and acceptance criteria. Each phase produces a working, testable increment of the system.

**Instructions for AI-Assisted Implementation:**
1. Start with Phase 1 and complete all tasks in order.
2. After each phase, verify all acceptance criteria are met before proceeding.
3. Use the architecture.md as the source of truth for component interfaces and data models.
4. Follow the project structure defined in architecture.md Section 6.2.

---

## 2. Implementation Overview

| Phase | Name | Duration | Deliverable |
|---|---|---|---|
| **Phase 1** | Project Setup & Configuration | 2–3 hours | Scaffolded project with dependencies, config, and folder structure |
| **Phase 2** | Data Models & Storage Layer | 3–4 hours | Pydantic models, SQLite document store, ChromaDB vector store |
| **Phase 3** | Ingestion Pipeline | 4–5 hours | Document upload, text extraction, chunking, embedding, vector storage |
| **Phase 4** | Query Pipeline & LLM Integration | 4–5 hours | Query embedding, retrieval, prompt building, LLM client, response formatting |
| **Phase 5** | API Layer | 3–4 hours | FastAPI endpoints for chat, ingest, health, documents |
| **Phase 6** | UI & End-to-End Integration | 3–4 hours | Streamlit chat UI, end-to-end testing, demo preparation |

**Total Estimated Effort:** 19–25 hours

---

## 3. Phase 1: Project Setup & Configuration

### 3.1 Goal

Create the project scaffold with all dependencies, configuration management, and folder structure in place.

### 3.2 Tasks

#### Task 1.1: Create Project Directory Structure

Create the following folder structure:

```
groww-rag-chatbot/
├── app/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   └── __init__.py
│   │   └── schemas/
│   │       └── __init__.py
│   ├── pipeline/
│   │   ├── __init__.py
│   │   └── components/
│   │       └── __init__.py
│   ├── storage/
│   │   └── __init__.py
│   ├── models/
│   │   └── __init__.py
│   └── ui/
│       └── __init__.py
├── data/
│   ├── chroma/
│   └── documents/
├── documents/
├── tests/
├── .env
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── PRD.md
├── architecture.md
├── implementation.md
└── README.md
```

#### Task 1.2: Create `requirements.txt`

```txt
# Web Framework
fastapi>=0.110.0
uvicorn[standard]>=0.29.0
python-multipart>=0.0.9

# UI
streamlit>=1.32.0

# RAG & LLM
langchain>=0.1.0
langchain-community>=0.0.10
langchain-chroma>=0.1.0
openai>=1.12.0
ollama>=0.1.0

# Embeddings
sentence-transformers>=2.5.0
torch>=2.2.0

# Vector DB
chromadb>=0.4.24

# Document Parsing
PyPDF2>=3.0.1
python-docx>=1.1.0

# Configuration
pydantic>=2.6.0
pydantic-settings>=2.2.0
python-dotenv>=1.0.0

# Utilities
python-json-logger>=2.0.7
tenacity>=8.2.3

# Testing
pytest>=8.0.0
pytest-asyncio>=0.23.0
httpx>=0.27.0
```

#### Task 1.3: Create `.env.example`

```env
# Embedding Model
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# LLM Provider: 'openai' or 'ollama'
LLM_PROVIDER=openai

# OpenAI Settings (required if LLM_PROVIDER=openai)
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o-mini

# Ollama Settings (required if LLM_PROVIDER=ollama)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3:8b

# Chunking Parameters
CHUNK_SIZE=400
CHUNK_OVERLAP=80

# Retrieval Parameters
TOP_K=5
SIMILARITY_THRESHOLD=0.5

# Session Management
MAX_HISTORY=10
SESSION_TTL_MINUTES=30

# Storage Paths
VECTOR_DB_PATH=./data/chroma
DOCUMENT_STORE_PATH=./data/documents.db
UPLOAD_DIR=./data/documents

# Logging
LOG_LEVEL=INFO
```

#### Task 1.4: Create `.env`

Copy `.env.example` to `.env` and fill in actual values (especially `OPENAI_API_KEY`).

#### Task 1.5: Create `.gitignore`

```gitignore
# Environment
.env

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
.venv/
env/

# Data
data/chroma/
data/documents/
data/documents.db

# IDE
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db

# Logs
*.log
```

#### Task 1.6: Create `app/config.py`

```python
"""Central configuration management using Pydantic Settings."""
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Embedding Model
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"

    # LLM Provider
    llm_provider: str = "openai"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3:8b"

    # Chunking Parameters
    chunk_size: int = 400
    chunk_overlap: int = 80

    # Retrieval Parameters
    top_k: int = 5
    similarity_threshold: float = 0.5

    # Session Management
    max_history: int = 10
    session_ttl_minutes: int = 30

    # Storage Paths
    vector_db_path: str = "./data/chroma"
    document_store_path: str = "./data/documents.db"
    upload_dir: str = "./data/documents"

    # Logging
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
```

#### Task 1.7: Create `app/__init__.py`

```python
"""Groww RAG Chatbot Application."""
__version__ = "1.0.0"
```

#### Task 1.8: Create `Dockerfile`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directories
RUN mkdir -p data/chroma data/documents

EXPOSE 8000 8501

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Task 1.9: Create `docker-compose.yml`

```yaml
version: "3.9"

services:
  api:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - LLM_PROVIDER=${LLM_PROVIDER}
    volumes:
      - ./data:/app/data
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000

  ui:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8501:8501"
    environment:
      - API_URL=http://api:8000
    depends_on:
      - api
    command: streamlit run app/ui/streamlit_app.py --server.port 8501 --server.address 0.0.0.0

  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    profiles:
      - local-llm

volumes:
  ollama_data:
```

### 3.3 Acceptance Criteria

- [ ] All folders and `__init__.py` files exist
- [ ] `requirements.txt` is created with all dependencies
- [ ] `.env` and `.env.example` are created
- [ ] `app/config.py` loads settings without errors
- [ ] `python -c "from app.config import settings; print(settings)"` runs successfully
- [ ] `Dockerfile` and `docker-compose.yml` are valid YAML/Docker syntax

---

## 4. Phase 2: Data Models & Storage Layer

### 4.1 Goal

Define all internal data models (Pydantic classes) and implement the storage layer (SQLite document store + ChromaDB vector store).

### 4.2 Tasks

#### Task 2.1: Create `app/models/schemas.py`

Define all internal data models:

```python
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
```

#### Task 2.2: Create `app/storage/document_store.py`

Implement SQLite-based document metadata store:

```python
"""SQLite-based document metadata storage."""
import sqlite3
import os
from datetime import datetime
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
```

#### Task 2.3: Create `app/storage/vector_store.py`

Implement ChromaDB-based vector storage:

```python
"""ChromaDB-based vector storage for document chunks."""
import os
import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import Optional
from app.models.schemas import Chunk, RetrievedChunk
from app.config import settings


class VectorStore:
    """Manages chunk embeddings in ChromaDB."""

    def __init__(self, persist_path: str = None, embedding_model=None):
        self.persist_path = persist_path or settings.vector_db_path
        os.makedirs(self.persist_path, exist_ok=True)

        self.client = chromadb.PersistentClient(
            path=self.persist_path,
            settings=ChromaSettings(anonymized_telemetry=False)
        )

        self.collection = self.client.get_or_create_collection(
            name="groww_knowledge_base",
            metadata={"hnsw:space": "cosine"}
        )

        self._embedding_model = embedding_model

    def set_embedding_model(self, embedding_model):
        """Set the embedding model (called after model is loaded)."""
        self._embedding_model = embedding_model

    def add_chunks(self, chunks: list[Chunk]):
        """Add chunks with their embeddings to the vector store."""
        if not chunks:
            return

        embeddings = self._embedding_model.encode(
            [chunk.text for chunk in chunks],
            batch_size=32,
            show_progress_bar=False
        )

        self.collection.add(
            ids=[chunk.chunk_id for chunk in chunks],
            embeddings=embeddings.tolist(),
            documents=[chunk.text for chunk in chunks],
            metadatas=[{
                "document_id": chunk.document_id,
                "document_title": chunk.document_title,
                "source": chunk.source,
                "chunk_index": chunk.chunk_index,
                "token_count": chunk.token_count,
                "created_at": chunk.created_at.isoformat()
            } for chunk in chunks]
        )

    def search(self, query_embedding: list[float], top_k: int = None,
               threshold: float = None) -> list[RetrievedChunk]:
        """Search for similar chunks given a query embedding."""
        top_k = top_k or settings.top_k
        threshold = threshold or settings.similarity_threshold

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )

        retrieved = []
        if results["ids"] and results["ids"][0]:
            for i, chunk_id in enumerate(results["ids"][0]):
                # ChromaDB returns distance; convert to similarity score
                distance = results["distances"][0][i]
                similarity = 1.0 - distance  # cosine distance to similarity

                if similarity < threshold:
                    continue

                metadata = results["metadatas"][0][i]
                retrieved.append(RetrievedChunk(
                    chunk_id=chunk_id,
                    document_title=metadata.get("document_title", "Unknown"),
                    source=metadata.get("source", ""),
                    chunk_index=metadata.get("chunk_index", 0),
                    text=results["documents"][0][i],
                    similarity_score=similarity
                ))

        return retrieved

    def delete_by_document(self, document_id: str):
        """Delete all chunks belonging to a document."""
        self.collection.delete(
            where={"document_id": document_id}
        )

    def count(self) -> int:
        """Return total number of chunks in the store."""
        return self.collection.count()
```

#### Task 2.4: Create `app/storage/__init__.py`

```python
"""Storage layer for the RAG Chatbot."""
from app.storage.document_store import DocumentStore
from app.storage.vector_store import VectorStore

__all__ = ["DocumentStore", "VectorStore"]
```

### 4.3 Acceptance Criteria

- [ ] `from app.models.schemas import Chunk, Document, RetrievedChunk` works
- [ ] `DocumentStore` can create, read, update, and delete documents in SQLite
- [ ] `VectorStore` initializes ChromaDB with persistent storage
- [ ] `VectorStore.add_chunks()` stores embeddings with metadata
- [ ] `VectorStore.search()` returns `RetrievedChunk` objects with similarity scores
- [ ] `VectorStore.delete_by_document()` removes all chunks for a document
- [ ] All models validate correctly with Pydantic

---

## 5. Phase 3: Ingestion Pipeline

### 5.1 Goal

Implement the full document ingestion pipeline: text extraction, chunking, embedding generation, and vector storage.

### 5.2 Tasks

#### Task 3.1: Create `app/pipeline/components/extractor.py`

```python
"""Text extraction from various document formats."""
import os
from pathlib import Path


class DocumentParseException(Exception):
    """Raised when a document cannot be parsed."""
    pass


class TextExtractor:
    """Extracts raw text from PDF, TXT, MD, and DOCX files."""

    SUPPORTED_FORMATS = {".pdf", ".txt", ".md", ".docx"}

    def extract(self, file_path: str) -> str:
        """Extract text from a file based on its extension."""
        ext = Path(file_path).suffix.lower()

        if ext not in self.SUPPORTED_FORMATS:
            raise DocumentParseException(f"Unsupported file format: {ext}")

        if not os.path.exists(file_path):
            raise DocumentParseException(f"File not found: {file_path}")

        if ext == ".pdf":
            return self._extract_pdf(file_path)
        elif ext == ".docx":
            return self._extract_docx(file_path)
        else:
            return self._extract_text(file_path)

    def _extract_pdf(self, file_path: str) -> str:
        """Extract text from PDF using PyPDF2."""
        try:
            from PyPDF2 import PdfReader
            reader = PdfReader(file_path)
            text_parts = []
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
            return "\n\n".join(text_parts)
        except Exception as e:
            raise DocumentParseException(f"Failed to parse PDF: {e}")

    def _extract_docx(self, file_path: str) -> str:
        """Extract text from DOCX using python-docx."""
        try:
            from docx import Document as DocxDocument
            doc = DocxDocument(file_path)
            text_parts = []
            for para in doc.paragraphs:
                if para.text.strip():
                    text_parts.append(para.text)
            return "\n\n".join(text_parts)
        except Exception as e:
            raise DocumentParseException(f"Failed to parse DOCX: {e}")

    def _extract_text(self, file_path: str) -> str:
        """Extract text from plain text files (TXT, MD)."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except UnicodeDecodeError:
            with open(file_path, "r", encoding="latin-1") as f:
                return f.read()
        except Exception as e:
            raise DocumentParseException(f"Failed to read text file: {e}")
```

#### Task 3.2: Create `app/pipeline/components/chunker.py`

```python
"""Text chunking for document segmentation."""
from typing import Optional
from app.models.schemas import Chunk
from app.config import settings


class Chunker:
    """Splits text into overlapping chunks using LangChain."""

    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        self.chunk_size = chunk_size or settings.chunk_size
        self.chunk_overlap = chunk_overlap or settings.chunk_overlap

        from langchain.text_splitter import RecursiveCharacterTextSplitter
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

    def chunk_text(self, text: str, document_id: str,
                  document_title: str, source: str) -> list[Chunk]:
        """Split text into chunks and return Chunk objects."""
        raw_chunks = self.splitter.split_text(text)

        chunks = []
        for i, chunk_text in enumerate(raw_chunks):
            chunks.append(Chunk(
                document_id=document_id,
                document_title=document_title,
                source=source,
                chunk_index=i,
                text=chunk_text.strip(),
                token_count=len(chunk_text.split())
            ))

        return chunks
```

#### Task 3.3: Create `app/pipeline/components/embedder.py`

```python
"""Embedding generation using sentence-transformers."""
from typing import Optional
import numpy as np
from app.config import settings


class Embedder:
    """Generates embeddings using a sentence-transformers model."""

    def __init__(self, model_name: str = None):
        self.model_name = model_name or settings.embedding_model
        self._model = None

    def _load_model(self):
        """Lazy-load the embedding model."""
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.model_name)
        return self._model

    def encode(self, texts: list[str], batch_size: int = 32) -> np.ndarray:
        """Encode a list of texts into embedding vectors."""
        model = self._load_model()
        return model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=False,
            normalize_embeddings=True
        )

    def encode_query(self, query: str) -> list[float]:
        """Encode a single query string."""
        embedding = self.encode([query])
        return embedding[0].tolist()
```

#### Task 3.4: Create `app/pipeline/ingestion.py`

```python
"""Document ingestion pipeline orchestrator."""
import os
import uuid
from pathlib import Path
from datetime import datetime
from app.models.schemas import Document
from app.storage.document_store import DocumentStore
from app.storage.vector_store import VectorStore
from app.pipeline.components.extractor import TextExtractor, DocumentParseException
from app.pipeline.components.chunker import Chunker
from app.pipeline.components.embedder import Embedder
from app.config import settings


class IngestionPipeline:
    """Orchestrates the full document ingestion flow."""

    def __init__(self, document_store: DocumentStore, vector_store: VectorStore):
        self.document_store = document_store
        self.vector_store = vector_store
        self.extractor = TextExtractor()
        self.chunker = Chunker()
        self.embedder = Embedder()

        # Set embedding model on vector store
        self.vector_store.set_embedding_model(self.embedder)

    def ingest_file(self, file_path: str, title: str = None) -> Document:
        """Ingest a single file into the knowledge base."""
        file_path = str(file_path)
        ext = Path(file_path).suffix.lower().lstrip(".")
        file_size = os.path.getsize(file_path)
        title = title or Path(file_path).stem

        # Create document record
        doc = Document(
            title=title,
            source=file_path,
            file_type=ext,
            file_size=file_size,
            status="processing"
        )
        self.document_store.add_document(doc)

        try:
            # Step 1: Extract text
            text = self.extractor.extract(file_path)

            if not text.strip():
                raise DocumentParseException("Extracted text is empty")

            # Step 2: Chunk text
            chunks = self.chunker.chunk_text(
                text=text,
                document_id=doc.document_id,
                document_title=doc.title,
                source=doc.source
            )

            # Step 3: Generate embeddings and store
            self.vector_store.add_chunks(chunks)

            # Step 4: Update document status
            self.document_store.update_status(
                doc.document_id, "completed", len(chunks)
            )
            doc.status = "completed"
            doc.chunk_count = len(chunks)

        except Exception as e:
            self.document_store.update_status(doc.document_id, "failed")
            doc.status = "failed"
            raise

        return doc

    def ingest_directory(self, directory: str) -> list[Document]:
        """Ingest all supported files from a directory."""
        results = []
        for file_path in Path(directory).iterdir():
            if file_path.suffix.lower() in TextExtractor.SUPPORTED_FORMATS:
                try:
                    doc = self.ingest_file(str(file_path))
                    results.append(doc)
                except Exception as e:
                    print(f"Failed to ingest {file_path}: {e}")
        return results
```

#### Task 3.5: Create `app/pipeline/__init__.py`

```python
"""RAG Pipeline components."""
from app.pipeline.ingestion import IngestionPipeline

__all__ = ["IngestionPipeline"]
```

### 5.3 Acceptance Criteria

- [ ] `TextExtractor` can extract text from PDF, TXT, MD, and DOCX files
- [ ] `TextExtractor` raises `DocumentParseException` for unsupported formats
- [ ] `Chunker` splits text into chunks with correct overlap
- [ ] `Embedder` loads the MiniLM model and generates 384-dimensional embeddings
- [ ] `IngestionPipeline.ingest_file()` processes a file end-to-end
- [ ] `IngestionPipeline.ingest_directory()` batch-processes a folder
- [ ] Ingested documents appear in `DocumentStore.list_documents()`
- [ ] Chunks are searchable in `VectorStore` after ingestion

---

## 6. Phase 4: Query Pipeline & LLM Integration

### 6.1 Goal

Implement the runtime RAG query pipeline: query embedding, retrieval, prompt building, LLM client, and response formatting.

### 6.2 Tasks

#### Task 4.1: Create `app/pipeline/components/retriever.py`

```python
"""Vector similarity search for query retrieval."""
from app.storage.vector_store import VectorStore
from app.pipeline.components.embedder import Embedder
from app.config import settings


class Retriever:
    """Retrieves relevant chunks for a given query."""

    def __init__(self, vector_store: VectorStore, embedder: Embedder):
        self.vector_store = vector_store
        self.embedder = embedder

    def retrieve(self, query: str, top_k: int = None,
                 threshold: float = None):
        """Retrieve top-K relevant chunks for a query."""
        query_embedding = self.embedder.encode_query(query)
        return self.vector_store.search(query_embedding, top_k, threshold)
```

#### Task 4.2: Create `app/pipeline/components/prompt_builder.py`

```python
"""Prompt construction for LLM generation."""
from app.models.schemas import RetrievedChunk, Message
from app.config import settings


class PromptBuilder:
    """Builds prompts from retrieved chunks and conversation history."""

    SYSTEM_PROMPT = (
        "You are a helpful assistant for the Groww investment platform. "
        "Answer the user's question based on the provided context. "
        "If the context does not contain enough information, say "
        "\"I don't have enough information to answer that question.\""
    )

    def build_messages(self, query: str, chunks: list[RetrievedChunk],
                       history: list[Message] = None) -> list[dict]:
        """Build a list of chat messages for the LLM."""
        messages = [{"role": "system", "content": self.SYSTEM_PROMPT}]

        # Add conversation history (limited)
        if history:
            for msg in history[-settings.max_history:]:
                messages.append({"role": msg.role, "content": msg.content})

        # Build context from retrieved chunks
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            context_parts.append(
                f"--- Context {i} ---\n{chunk.text}\n"
                f"(Source: {chunk.document_title})"
            )

        context_str = "\n\n".join(context_parts) if context_parts else "No relevant context found."

        # Build user message with context
        user_message = (
            f"CONTEXT:\n{context_str}\n\n"
            f"USER QUESTION: {query}\n\n"
            f"ANSWER:"
        )
        messages.append({"role": "user", "content": user_message})

        return messages
```

#### Task 4.3: Create `app/pipeline/components/llm_client.py`

```python
"""LLM client abstraction for OpenAI and Ollama."""
from abc import ABC, abstractmethod
from typing import Optional
from tenacity import retry, stop_after_attempt, wait_exponential
from app.config import settings


class LLMClient(ABC):
    """Abstract base class for LLM clients."""

    @abstractmethod
    def generate(self, messages: list[dict]) -> str:
        """Generate a response given a list of chat messages."""
        pass


class OpenAIClient(LLMClient):
    """OpenAI API client."""

    def __init__(self, model: str = None, api_key: str = None):
        from openai import OpenAI
        self.model = model or settings.openai_model
        self.client = OpenAI(api_key=api_key or settings.openai_api_key)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    def generate(self, messages: list[dict]) -> str:
        """Generate response using OpenAI API."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.1,
            max_tokens=512,
            top_p=0.9
        )
        return response.choices[0].message.content


class OllamaClient(LLMClient):
    """Ollama local LLM client."""

    def __init__(self, model: str = None, base_url: str = None):
        import ollama
        self.model = model or settings.ollama_model
        self.base_url = base_url or settings.ollama_base_url
        self.client = ollama.Client(host=self.base_url)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    def generate(self, messages: list[dict]) -> str:
        """Generate response using Ollama."""
        response = self.client.chat(
            model=self.model,
            messages=messages,
            options={
                "temperature": 0.1,
                "num_predict": 512,
                "top_p": 0.9
            }
        )
        return response["message"]["content"]


def create_llm_client() -> LLMClient:
    """Factory function to create the appropriate LLM client."""
    if settings.llm_provider == "ollama":
        return OllamaClient()
    return OpenAIClient()
```

#### Task 4.4: Create `app/pipeline/query.py`

```python
"""Query processing pipeline orchestrator."""
from app.models.schemas import RetrievedChunk, Message
from app.storage.vector_store import VectorStore
from app.pipeline.components.embedder import Embedder
from app.pipeline.components.retriever import Retriever
from app.pipeline.components.prompt_builder import PromptBuilder
from app.pipeline.components.llm_client import LLMClient, create_llm_client


class QueryPipeline:
    """Orchestrates the full RAG query flow."""

    def __init__(self, vector_store: VectorStore, embedder: Embedder,
                 llm_client: LLMClient = None):
        self.retriever = Retriever(vector_store, embedder)
        self.prompt_builder = PromptBuilder()
        self.llm_client = llm_client or create_llm_client()

    def process(self, query: str, history: list[Message] = None) -> dict:
        """Process a user query and return response with sources."""
        # Step 1: Retrieve relevant chunks
        chunks = self.retriever.retrieve(query)

        # Step 2: Handle no results
        if not chunks:
            return {
                "response": (
                    "I'm sorry, I couldn't find relevant information "
                    "in my knowledge base. Could you rephrase your question?"
                ),
                "sources": []
            }

        # Step 3: Build prompt
        messages = self.prompt_builder.build_messages(query, chunks, history)

        # Step 4: Generate response
        try:
            response_text = self.llm_client.generate(messages)
        except Exception as e:
            response_text = (
                "I'm having trouble generating a response right now. "
                "Please try again in a moment."
            )

        # Step 5: Format sources
        sources = [
            {
                "document_title": chunk.document_title,
                "source": chunk.source,
                "chunk_index": chunk.chunk_index,
                "similarity_score": round(chunk.similarity_score, 4)
            }
            for chunk in chunks
        ]

        return {
            "response": response_text,
            "sources": sources
        }
```

### 6.3 Acceptance Criteria

- [ ] `Retriever.retrieve()` returns relevant chunks for a test query
- [ ] `PromptBuilder.build_messages()` produces correctly formatted messages
- [ ] `OpenAIClient.generate()` returns a response from the API
- [ ] `OllamaClient.generate()` returns a response from local Ollama
- [ ] `create_llm_client()` returns the correct client based on config
- [ ] `QueryPipeline.process()` returns `{"response": str, "sources": list}`
- [ ] Fallback response is returned when no chunks are retrieved
- [ ] LLM errors are caught and return a user-friendly message

---

## 7. Phase 5: API Layer

### 7.1 Goal

Implement the FastAPI application with all endpoints: chat, ingest, health, and document management.

### 7.2 Tasks

#### Task 5.1: Create `app/api/schemas/chat.py`

```python
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
```

#### Task 5.2: Create `app/api/schemas/document.py`

```python
"""Pydantic models for document API request/response."""
from pydantic import BaseModel, Field
from typing import Optional


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
```

#### Task 5.3: Create `app/api/routes/chat.py`

```python
"""Chat API endpoint."""
import uuid
from fastapi import APIRouter, Depends
from app.api.schemas.chat import ChatRequest, ChatResponse
from app.pipeline.query import QueryPipeline
from app.models.schemas import Message

router = APIRouter()

# In-memory session store
_sessions: dict[str, list[Message]] = {}


def get_query_pipeline() -> QueryPipeline:
    """Dependency to get the query pipeline (set in main.py)."""
    from app.main import query_pipeline
    return query_pipeline


@router.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, pipeline: QueryPipeline = Depends(get_query_pipeline)):
    """Process a user query and return a generated response."""
    # Get or create session
    session_id = request.session_id or str(uuid.uuid4())

    # Get conversation history
    history = _sessions.get(session_id, [])

    # Process query
    result = pipeline.process(request.query, history)

    # Update session history
    history.append(Message(role="user", content=request.query))
    history.append(Message(role="assistant", content=result["response"]))

    # Trim history to max length
    max_history = 10
    if len(history) > max_history * 2:
        history = history[-max_history * 2:]

    _sessions[session_id] = history

    return ChatResponse(
        response=result["response"],
        sources=result["sources"],
        session_id=session_id
    )
```

#### Task 5.4: Create `app/api/routes/ingest.py`

```python
"""Document ingestion API endpoint."""
import os
import shutil
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.api.schemas.document import IngestResponse
from app.pipeline.ingestion import IngestionPipeline
from app.config import settings

router = APIRouter()


def get_ingestion_pipeline() -> IngestionPipeline:
    """Dependency to get the ingestion pipeline."""
    from app.main import ingestion_pipeline
    return ingestion_pipeline


@router.post("/api/ingest", response_model=IngestResponse)
async def ingest_document(
    file: UploadFile = File(...),
    title: str = Form(None),
    pipeline: IngestionPipeline = Depends(get_ingestion_pipeline)
):
    """Upload and ingest a document into the knowledge base."""
    # Validate file type
    ext = os.path.splitext(file.filename)[1].lower()
    allowed = {".pdf", ".txt", ".md", ".docx"}
    if ext not in allowed:
        raise HTTPException(
            status_code=422,
            detail=f"Unsupported file format. Allowed: {', '.join(allowed)}"
        )

    # Validate file size (10MB max)
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File too large (max 10MB)")

    # Save file
    os.makedirs(settings.upload_dir, exist_ok=True)
    file_path = os.path.join(settings.upload_dir, file.filename)
    with open(file_path, "wb") as f:
        f.write(content)

    # Ingest
    try:
        doc = pipeline.ingest_file(file_path, title)
        return IngestResponse(
            document_id=doc.document_id,
            title=doc.title,
            chunks_ingested=doc.chunk_count,
            status=doc.status
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")
```

#### Task 5.5: Create `app/api/routes/documents.py`

```python
"""Document management API endpoints."""
from fastapi import APIRouter, HTTPException
from app.api.schemas.document import DocumentListResponse, DeleteResponse

router = APIRouter()


def get_ingestion_pipeline():
    """Dependency to get the ingestion pipeline."""
    from app.main import ingestion_pipeline
    return ingestion_pipeline


@router.get("/api/documents", response_model=DocumentListResponse)
async def list_documents(pipeline=Depends(get_ingestion_pipeline)):
    """List all ingested documents."""
    documents = pipeline.document_store.list_documents()
    return DocumentListResponse(
        documents=documents,
        total=len(documents)
    )


@router.delete("/api/documents/{document_id}", response_model=DeleteResponse)
async def delete_document(document_id: str, pipeline=Depends(get_ingestion_pipeline)):
    """Delete a document and its chunks."""
    doc = pipeline.document_store.get_document(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Delete from vector store
    pipeline.vector_store.delete_by_document(document_id)

    # Delete from document store
    pipeline.document_store.delete_document(document_id)

    # Delete file
    import os
    if os.path.exists(doc.source):
        os.remove(doc.source)

    return DeleteResponse(
        status="success",
        message=f"Document '{doc.title}' deleted successfully"
    )
```

#### Task 5.6: Create `app/main.py`

```python
"""FastAPI application entry point."""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.storage.document_store import DocumentStore
from app.storage.vector_store import VectorStore
from app.pipeline.components.embedder import Embedder
from app.pipeline.ingestion import IngestionPipeline
from app.pipeline.query import QueryPipeline
from app.api.routes import chat, ingest, documents

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global instances (initialized on startup)
document_store: DocumentStore = None
vector_store: VectorStore = None
embedder: Embedder = None
ingestion_pipeline: IngestionPipeline = None
query_pipeline: QueryPipeline = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize components on startup."""
    global document_store, vector_store, embedder, ingestion_pipeline, query_pipeline

    logger.info("Initializing Groww RAG Chatbot...")

    # Initialize storage
    document_store = DocumentStore()
    vector_store = VectorStore()
    embedder = Embedder()

    # Initialize pipelines
    ingestion_pipeline = IngestionPipeline(document_store, vector_store)
    query_pipeline = QueryPipeline(vector_store, embedder)

    logger.info(f"Vector store contains {vector_store.count()} chunks")
    logger.info("Initialization complete.")

    yield

    logger.info("Shutting down...")


app = FastAPI(
    title="Groww RAG Chatbot",
    description="RAG-powered chatbot for Groww investment platform queries",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router)
app.include_router(ingest.router)
app.include_router(documents.router)


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "components": {
            "vector_db": "connected",
            "llm": settings.llm_provider,
            "document_store": "connected"
        },
        "documents_count": len(document_store.list_documents()) if document_store else 0,
        "chunks_count": vector_store.count() if vector_store else 0
    }
```

### 7.3 Acceptance Criteria

- [ ] `uvicorn app.main:app --reload` starts the server on port 8000
- [ ] `GET /api/health` returns healthy status with component info
- [ ] `POST /api/chat` with a test query returns a response with sources
- [ ] `POST /api/ingest` with a test file ingests and returns document info
- [ ] `GET /api/documents` lists all ingested documents
- [ ] `DELETE /api/documents/{id}` removes a document and its chunks
- [ ] Invalid file types return 422 error
- [ ] Session continuity works across multiple chat requests
- [ ] API docs available at `/docs` (Swagger UI)

---

## 8. Phase 6: UI & End-to-End Integration

### 8.1 Goal

Build the Streamlit chat interface and perform end-to-end testing with real documents.

### 8.2 Tasks

#### Task 6.1: Create `app/ui/streamlit_app.py`

```python
"""Streamlit chat interface for the Groww RAG Chatbot."""
import os
import requests
import streamlit as st

# Page config
st.set_page_config(
    page_title="Groww RAG Chatbot",
    page_icon="📈",
    layout="centered"
)

# API URL
API_URL = os.environ.get("API_URL", "http://localhost:8000")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_id" not in st.session_state:
    st.session_state.session_id = None


def call_chat_api(query: str) -> dict:
    """Call the chat API endpoint."""
    payload = {
        "query": query,
        "session_id": st.session_state.session_id,
        "history": [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages
        ]
    }
    try:
        response = requests.post(f"{API_URL}/api/chat", json=payload, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        return {"response": "Cannot connect to the API server. Please check if it's running.", "sources": []}
    except requests.exceptions.Timeout:
        return {"response": "The request timed out. Please try again.", "sources": []}
    except Exception as e:
        return {"response": f"An error occurred: {str(e)}", "sources": []}


def main():
    """Main Streamlit app."""
    st.title("📈 Groww RAG Chatbot")
    st.caption("Ask me anything about Groww or investing!")

    # Sidebar
    with st.sidebar:
        st.header("About")
        st.info(
            "This is a RAG-powered chatbot for the Groww investment platform. "
            "It uses retrieval-augmented generation to answer questions based on "
            "a curated knowledge base."
        )

        if st.button("Clear Chat"):
            st.session_state.messages = []
            st.session_state.session_id = None
            st.rerun()

        # Document management
        st.header("Add Documents")
        uploaded_file = st.file_uploader(
            "Upload a document",
            type=["pdf", "txt", "md", "docx"]
        )
        if uploaded_file and st.button("Ingest Document"):
            with st.spinner("Ingesting..."):
                files = {"file": uploaded_file.getvalue()}
                data = {"title": uploaded_file.name}
                try:
                    resp = requests.post(
                        f"{API_URL}/api/ingest",
                        files={"file": (uploaded_file.name, uploaded_file.getvalue())},
                        data=data,
                        timeout=60
                    )
                    if resp.status_code == 200:
                        result = resp.json()
                        st.success(f"Ingested '{result['title']}' ({result['chunks_ingested']} chunks)")
                    else:
                        st.error(f"Ingestion failed: {resp.text}")
                except Exception as e:
                    st.error(f"Error: {e}")

    # Chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask a question..."):
        # Display user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get bot response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                result = call_chat_api(prompt)

            st.markdown(result["response"])

            # Display sources
            if result.get("sources"):
                with st.expander("📚 Sources"):
                    for source in result["sources"]:
                        st.write(f"**{source['document_title']}** (score: {source['similarity_score']})")

        # Save to session
        st.session_state.messages.append({
            "role": "assistant",
            "content": result["response"]
        })
        if result.get("session_id"):
            st.session_state.session_id = result["session_id"]


if __name__ == "__main__":
    main()
```

#### Task 6.2: Create Sample Test Documents

Create 3–5 sample documents in the `documents/` folder for testing:

**`documents/groww_getting_started.md`:**
```markdown
# Getting Started with Groww

## Account Setup
To start investing on Groww, you need to create an account. Visit groww.in or download the app. You will need your PAN card, Aadhaar card, and bank account details for KYC verification.

## KYC Verification
KYC (Know Your Customer) is mandatory for trading in India. Groww supports video KYC, which can be completed in minutes. You will need your PAN, Aadhaar, and a selfie.

## Adding Funds
You can add funds to your Groww account via UPI, net banking, or IMPS. Funds are credited instantly in most cases.

## Your First Stock
Once your account is set up and funded, you can search for any stock listed on NSE or BSE. Click "Buy" and enter the quantity. Market orders execute immediately, while limit orders execute at your specified price.
```

**`documents/groww_mutual_funds.md`:**
```markdown
# Mutual Funds on Groww

## What are Mutual Funds?
Mutual funds pool money from multiple investors to invest in a diversified portfolio of stocks, bonds, or other securities. They are managed by professional fund managers.

## Types of Mutual Funds
- Equity Funds: Invest primarily in stocks. Higher risk, higher potential returns.
- Debt Funds: Invest in bonds and fixed-income securities. Lower risk, stable returns.
- Hybrid Funds: Invest in a mix of equity and debt.
- Index Funds: Track a market index like Nifty 50. Passively managed, low fees.

## SIP (Systematic Investment Plan)
SIP allows you to invest a fixed amount regularly (monthly/quarterly) in a mutual fund. It promotes disciplined investing and benefits from rupee cost averaging.

## Groww's Mutual Fund Platform
Groww offers direct plans of mutual funds with zero commission. You can start a SIP with as little as Rs. 100. The platform provides detailed fund analysis, portfolio tracking, and goal-based investing.
```

**`documents/stock_market_basics.md`:**
```markdown
# Stock Market Basics

## What is a Stock?
A stock represents ownership in a company. When you buy a stock, you own a small piece of that company. Stocks are traded on stock exchanges like the National Stock Exchange (NSE) and Bombay Stock Exchange (BSE) in India.

## Bull and Bear Markets
A bull market is when stock prices are rising and investor sentiment is positive. A bear market is when prices are falling and sentiment is negative.

## Key Terms
- IPO (Initial Public Offering): When a company first sells shares to the public.
- Dividend: A portion of company profits distributed to shareholders.
- P/E Ratio: Price-to-Earnings ratio, a valuation metric comparing stock price to earnings per share.
- Market Cap: Total value of a company's outstanding shares.

## How to Analyze Stocks
- Fundamental Analysis: Examining financial statements, earnings, industry position.
- Technical Analysis: Studying price charts and trading volumes.
- Qualitative Analysis: Evaluating management quality, brand strength, competitive advantage.
```

#### Task 6.3: Create `tests/test_ingestion.py`

```python
"""Tests for the ingestion pipeline."""
import os
import pytest
from app.storage.document_store import DocumentStore
from app.storage.vector_store import VectorStore
from app.pipeline.ingestion import IngestionPipeline


@pytest.fixture
def doc_store(tmp_path):
    return DocumentStore(str(tmp_path / "test.db"))


@pytest.fixture
def vector_store(tmp_path):
    return VectorStore(str(tmp_path / "chroma"))


@pytest.fixture
def pipeline(doc_store, vector_store):
    return IngestionPipeline(doc_store, vector_store)


def test_ingest_markdown_file(pipeline, doc_store):
    """Test ingesting a markdown file."""
    test_file = "documents/groww_getting_started.md"
    if not os.path.exists(test_file):
        pytest.skip("Test document not found")

    doc = pipeline.ingest_file(test_file)
    assert doc.status == "completed"
    assert doc.chunk_count > 0

    # Verify document is in store
    stored = doc_store.get_document(doc.document_id)
    assert stored is not None
    assert stored.title == doc.title


def test_ingest_unsupported_format(pipeline):
    """Test that unsupported formats raise an error."""
    with pytest.raises(Exception):
        pipeline.ingest_file("test.xyz")
```

#### Task 6.4: Create `tests/test_query.py`

```python
"""Tests for the query pipeline."""
import pytest
from app.storage.vector_store import VectorStore
from app.pipeline.components.embedder import Embedder
from app.pipeline.query import QueryPipeline


@pytest.fixture
def embedder():
    return Embedder()


@pytest.fixture
def vector_store():
    return VectorStore()


@pytest.fixture
def pipeline(vector_store, embedder):
    return QueryPipeline(vector_store, embedder)


def test_query_returns_dict(pipeline):
    """Test that query processing returns correct structure."""
    result = pipeline.process("What is Groww?")
    assert "response" in result
    assert "sources" in result
    assert isinstance(result["response"], str)
    assert isinstance(result["sources"], list)


def test_fallback_on_empty_kb(pipeline):
    """Test fallback response when knowledge base is empty."""
    result = pipeline.process("What is a stock?")
    assert "couldn't find" in result["response"].lower() or "don't have enough" in result["response"].lower()
```

#### Task 6.5: Create `tests/test_api.py`

```python
"""Tests for the API endpoints."""
import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    from app.main import app
    return TestClient(app)


def test_health_check(client):
    """Test health endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_chat_endpoint(client):
    """Test chat endpoint."""
    response = client.post("/api/chat", json={"query": "What is Groww?"})
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "sources" in data
    assert "session_id" in data


def test_chat_empty_query(client):
    """Test chat endpoint with empty query."""
    response = client.post("/api/chat", json={"query": ""})
    assert response.status_code == 422
```

### 8.3 Acceptance Criteria

- [ ] `streamlit run app/ui/streamlit_app.py` starts the UI on port 8501
- [ ] Chat interface displays messages in bubble format
- [ ] User can type a question and receive a response
- [ ] Sources are displayed in an expandable section
- [ ] "Clear Chat" button resets the conversation
- [ ] Document upload sidebar works
- [ ] All pytest tests pass
- [ ] End-to-end flow works: ingest documents → ask questions → get cited answers
- [ ] Response time is under 5 seconds for typical queries

---

## 9. End-to-End Testing Checklist

After completing all phases, verify the following:

### 9.1 Functional Testing

| # | Test | Expected Result |
|---|---|---|
| 1 | Start API server (`uvicorn app.main:app`) | Server starts on :8000 |
| 2 | Start UI (`streamlit run app/ui/streamlit_app.py`) | UI starts on :8501 |
| 3 | Open browser to `http://localhost:8501` | Chat interface loads |
| 4 | Type "What is Groww?" | Response appears within 5 seconds |
| 5 | Check sources section | At least 1 source listed |
| 6 | Ask follow-up "How do I start investing?" | Context-aware response |
| 7 | Upload a PDF via sidebar | Document ingested successfully |
| 8 | Ask about uploaded document topic | Response references new document |
| 9 | Click "Clear Chat" | Conversation resets |
| 10 | Ask off-topic question "What's the weather?" | Fallback response triggered |

### 9.2 API Testing (via Swagger UI at `/docs`)

| # | Test | Expected Result |
|---|---|---|
| 1 | `GET /api/health` | Returns healthy status |
| 2 | `POST /api/chat` with valid query | Returns response + sources |
| 3 | `POST /api/chat` with empty query | Returns 422 validation error |
| 4 | `POST /api/ingest` with PDF file | Returns document_id + chunk count |
| 5 | `POST /api/ingest` with .xyz file | Returns 422 error |
| 6 | `GET /api/documents` | Lists all ingested documents |
| 7 | `DELETE /api/documents/{id}` | Deletes document, returns success |

### 9.3 Performance Testing

| # | Test | Target |
|---|---|---|
| 1 | Query response time (P95) | < 5 seconds |
| 2 | Embedding generation | < 200ms |
| 3 | Vector search | < 100ms |
| 4 | Document ingestion (10-page PDF) | < 30 seconds |

---

## 10. Demo Preparation Checklist

### 10.1 Pre-Demo Setup

- [ ] Ensure all documents are ingested and searchable
- [ ] Test the full flow at least 3 times
- [ ] Verify API key / Ollama is working
- [ ] Clear browser cache and restart services
- [ ] Prepare 5–10 demo questions (see below)
- [ ] Have a backup plan (screenshots of key outputs)

### 10.2 Suggested Demo Questions

1. "What is Groww and how does it work?"
2. "How do I create an account on Groww?"
3. "What is KYC and why is it needed?"
4. "How do I buy my first stock?"
5. "What is a SIP and how do I start one?"
6. "What is the difference between equity and debt funds?"
7. "What is an IPO?"
8. "How do I add funds to my Groww account?"
9. "What is a bull market?"
10. "What is a P/E ratio?"

### 10.3 Demo Script (5-Minute Flow)

| Time | Action |
|---|---|
| 0:00 | Open UI, show clean chat interface |
| 0:30 | Ask "What is Groww?" — show response + sources |
| 1:30 | Ask "How do I buy my first stock?" — show step-by-step answer |
| 2:30 | Ask "What is a SIP?" — show explanation |
| 3:30 | Show document upload sidebar, upload a sample PDF |
| 4:00 | Ask a question about the uploaded document |
| 4:30 | Show API docs at `/docs` |
| 5:00 | Wrap up, take questions |

---

## 11. Troubleshooting Guide

| Issue | Solution |
|---|---|
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` |
| ChromaDB lock error | Delete `./data/chroma/` and restart |
| OpenAI API error | Check `OPENAI_API_KEY` in `.env` |
| Ollama connection refused | Run `ollama serve` or `ollama pull llama3:8b` |
| Streamlit can't connect to API | Verify API is running on port 8000, check `API_URL` env var |
| Slow first query | Embedding model is loading (one-time ~30s) |
| Empty responses | Check if documents are ingested: `GET /api/documents` |
| Port already in use | Kill process on port 8000/8501 or change ports |

---

## 12. File Creation Order Summary

For reference, here is the exact order files should be created:

```
Phase 1: Setup
├── requirements.txt
├── .env.example
├── .env
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── app/__init__.py
├── app/config.py
└── (all __init__.py files for subpackages)

Phase 2: Models & Storage
├── app/models/schemas.py
├── app/storage/document_store.py
├── app/storage/vector_store.py
└── app/storage/__init__.py

Phase 3: Ingestion Pipeline
├── app/pipeline/components/extractor.py
├── app/pipeline/components/chunker.py
├── app/pipeline/components/embedder.py
├── app/pipeline/ingestion.py
└── app/pipeline/__init__.py

Phase 4: Query Pipeline
├── app/pipeline/components/retriever.py
├── app/pipeline/components/prompt_builder.py
├── app/pipeline/components/llm_client.py
└── app/pipeline/query.py

Phase 5: API Layer
├── app/api/schemas/chat.py
├── app/api/schemas/document.py
├── app/api/routes/chat.py
├── app/api/routes/ingest.py
├── app/api/routes/documents.py
└── app/main.py

Phase 6: UI & Testing
├── app/ui/streamlit_app.py
├── documents/groww_getting_started.md
├── documents/groww_mutual_funds.md
├── documents/stock_market_basics.md
├── tests/test_ingestion.py
├── tests/test_query.py
└── tests/test_api.py
```

---

*End of Document*

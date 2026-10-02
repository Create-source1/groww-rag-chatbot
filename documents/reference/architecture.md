# Architecture Document

## Groww RAG Chatbot — System Architecture

| Field | Detail |
|---|---|
| **Document Title** | System Architecture — Groww RAG Chatbot |
| **Version** | 1.0 |
| **Date** | 2026-09-27 |
| **Author** | Pooja Jaiswal |
| **Status** | Draft |
| **References** | PRD.md (v1.0) |

---

## 1. Overview

This document describes the system architecture for the Groww RAG Chatbot — a Retrieval-Augmented Generation (RAG) application that answers user queries about the Groww investment platform and stock market concepts. The architecture follows a modular pipeline design separating document ingestion, vector storage, retrieval, and response generation into independent, testable components.

---

## 2. Architectural Principles

| Principle | Description |
|---|---|
| **Modularity** | Each pipeline stage (ingest, embed, store, retrieve, generate) is an independent module with a well-defined interface. |
| **Separation of Concerns** | Frontend, backend API, RAG pipeline, and vector storage are decoupled. |
| **Configurability** | Embedding model, LLM, chunk parameters, and retrieval settings are configurable via a central config file or environment variables. |
| **Local-First** | All components can run locally without external cloud dependencies, ensuring the demo works in offline or restricted-network environments. |
| **Extensibility** | New document types, embedding models, or LLMs can be added without refactoring the core pipeline. |

---

## 3. High-Level Architecture

### 3.1 Component Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        PRESENTATION LAYER                           │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │              Web UI (Streamlit / React)                        │  │
│  │  ┌─────────────┐  ┌──────────────┐  ┌─────────────────────┐  │  │
│  │  │ Chat Window │  │ Source Panel │  │ Admin / Ingest Panel│  │  │
│  │  └──────┬──────┘  └──────┬───────┘  └──────────┬──────────┘  │  │
│  └─────────┼─────────────────┼────────────────────┼─────────────┘  │
└────────────┼─────────────────┼────────────────────┼────────────────┘
             │                 │                    │
             ▼                 ▼                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         API LAYER (FastAPI)                          │
│                                                                     │
│  ┌──────────────┐  ┌───────────────┐  ┌──────────────────────────┐ │
│  │ POST /chat   │  │ POST /ingest  │  │ GET /health, /documents  │ │
│  └──────┬───────┘  └───────┬───────┘  └──────────────────────────┘ │
│         │                  │                                        │
│  ┌──────┴──────────────────┴────────────────────────────────────┐  │
│  │                    Request Router / Dispatcher                 │  │
│  └──────┬──────────────────┬────────────────────────────────────┘  │
└─────────┼──────────────────┼───────────────────────────────────────┘
          │                  │
          ▼                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      RAG PIPELINE LAYER                              │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                   Query Pipeline (Runtime)                     │  │
│  │                                                               │  │
│  │  User Query ──► Query Embedder ──► Retriever ──► Prompt       │  │
│  │                                     │              Builder    │  │
│  │                                     │                 │        │  │
│  │                                     ▼                 ▼        │  │
│  │                              Vector DB           LLM Client   │  │
│  │                              (Top-K chunks)    (Generate)     │  │
│  │                                                   │            │  │
│  │                                                   ▼            │  │
│  │                                            Response + Sources  │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                 Ingestion Pipeline (Offline/Batch)              │  │
│  │                                                               │  │
│  │  Raw Document ──► Text Extractor ──► Chunker ──► Embedder     │  │
│  │                                                        │      │  │
│  │                                                        ▼      │  │
│  │                                                 Vector DB Store │  │
│  └───────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
          │                  │                    │
          ▼                  ▼                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        DATA LAYER                                    │
│                                                                     │
│  ┌──────────────────────┐  ┌──────────────────────────────────────┐ │
│  │   Vector Database    │  │   Document Store                     │ │
│  │   (ChromaDB)         │  │   (Local FS / SQLite)                │ │
│  │                      │  │                                      │ │
│  │  - Embeddings        │  │  - Original documents                │ │
│  │  - Chunk text        │  │  - Metadata (title, source, date)    │ │
│  │  - Metadata          │  │  - Ingestion logs                    │ │
│  └──────────────────────┘  └──────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     EXTERNAL SERVICES LAYER                          │
│                                                                     │
│  ┌────────────────────┐  ┌────────────────────────────────────────┐ │
│  │  Embedding Model   │  │  LLM Provider (Local)                  │ │
│  │  (Local)           │  │  Ollama + Llama 3 8B                   │ │
│  │                    │  │                                        │ │
│  │  sentence-         │  │  Free, open-source, offline            │ │
│  │  transformers/     │  │  No API keys required                  │ │
│  │  all-MiniLM-L6-v2  │  │                                        │ │
│  └────────────────────┘  └────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

### 3.2 Layer Responsibilities

| Layer | Responsibility |
|---|---|
| **Presentation Layer** | Render chat interface, display responses with sources, handle user input, show loading states. |
| **API Layer** | Route HTTP requests, validate inputs, manage sessions, return structured JSON responses. |
| **RAG Pipeline Layer** | Orchestrate the core RAG flow: embed query, retrieve context, build prompt, call LLM, format response. |
| **Data Layer** | Persist vector embeddings, chunk metadata, and original documents. |
| **External Services Layer** | Provide embedding computation and LLM text generation capabilities. |

---

## 4. Detailed Component Design

### 4.1 Document Ingestion Pipeline

```
┌─────────────┐     ┌──────────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│ Raw Document │────►│ Text         │────►│ Chunker  │────►│ Embedder │────►│ Vector   │
│ (PDF/TXT/MD) │     │ Extractor    │     │          │     │          │     │ DB Store │
└─────────────┘     └──────────────┘     └──────────┘     └──────────┘     └──────────┘
```

#### 4.1.1 Text Extractor

| Aspect | Detail |
|---|---|
| **Input** | File path or uploaded file object (PDF, TXT, MD) |
| **Output** | Raw text string |
| **Libraries** | PyPDF2 (PDF), python-docx (DOCX), pathlib (TXT/MD) |
| **Error Handling** | Raises `DocumentParseException` on corrupt or unsupported files |

#### 4.1.2 Chunker

| Aspect | Detail |
|---|---|
| **Input** | Raw text string |
| **Output** | List of `Chunk` objects (text, index, metadata) |
| **Strategy** | Recursive character splitting with overlap |
| **Parameters** | `chunk_size=400` tokens, `chunk_overlap=80` tokens (20%) |
| **Library** | LangChain `RecursiveCharacterTextSplitter` |

**Chunk Data Model:**
```python
class Chunk:
    chunk_id: str          # UUID
    document_id: str       # Parent document UUID
    document_title: str    # Human-readable title
    source: str            # File path or URL
    chunk_index: int       # Position within document
    text: str              # Chunk content
    token_count: int       # Approximate token count
    created_at: datetime   # Ingestion timestamp
```

#### 4.1.3 Embedder

| Aspect | Detail |
|---|---|
| **Input** | List of `Chunk` objects |
| **Output** | List of embedding vectors (384-dimensional) |
| **Model** | `sentence-transformers/all-MiniLM-L6-v2` |
| **Batch Size** | 32 chunks per batch |
| **Device** | CPU (default) or CUDA (if available) |
| **Caching** | Embeddings cached in vector DB; re-ingestion skips existing chunks |

#### 4.1.4 Vector DB Store

| Aspect | Detail |
|---|---|
| **Database** | ChromaDB (persistent, local) |
| **Collection** | `groww_knowledge_base` |
| **Storage** | `./data/chroma/` (local filesystem) |
| **Index Type** | Cosine similarity (default HNSW) |
| **Metadata Filtering** | By `document_id`, `document_title`, `source` |

---

### 4.2 Query Pipeline (Runtime RAG Flow)

```
┌──────────┐    ┌──────────────┐    ┌───────────┐    ┌───────────┐    ┌──────────┐
│ User     │───►│ Query        │───►│ Retriever │───►│ Prompt    │───►│ LLM      │
│ Query    │    │ Embedder     │    │           │    │ Builder   │    │ Client   │
└──────────┘    └──────────────┘    └─────┬─────┘    └───────────┘    └────┬─────┘
                                          │                                  │
                                          ▼                                  ▼
                                   ┌─────────────┐                  ┌──────────────┐
                                   │ Vector DB   │                  │ Response +   │
                                   │ (Top-K)     │                  │ Sources      │
                                   └─────────────┘                  └──────────────┘
```

#### 4.2.1 Query Embedder

| Aspect | Detail |
|---|---|
| **Input** | User query string |
| **Output** | Query embedding vector (384-dimensional) |
| **Model** | Same as ingestion embedder (consistency requirement) |
| **Preprocessing** | Lowercase, strip whitespace, no special tokenization |

#### 4.2.2 Retriever

| Aspect | Detail |
|---|---|
| **Input** | Query embedding vector |
| **Output** | List of `RetrievedChunk` objects (chunk text, metadata, similarity score) |
| **Search Type** | Cosine similarity |
| **Top-K** | 5 (configurable) |
| **Score Threshold** | 0.5 (chunks below this are discarded) |
| **Filter** | Optional metadata filters (by document type, date range) |

**RetrievedChunk Data Model:**
```python
class RetrievedChunk:
    chunk_id: str
    document_title: str
    source: str
    chunk_index: int
    text: str
    similarity_score: float
```

#### 4.2.3 Prompt Builder

| Aspect | Detail |
|---|---|
| **Input** | User query + list of `RetrievedChunk` + conversation history |
| **Output** | Formatted prompt string (or message list for chat models) |
| **Template** | See below |
| **Token Budget** | Max 2000 tokens for context chunks; truncate oldest history if needed |

**Prompt Template:**
```
You are a helpful assistant for the Groww investment platform. Answer the user's question based on the provided context. If the context does not contain enough information, say "I don't have enough information to answer that question."

CONTEXT:
---
{chunk_1_text}
(Source: {document_title_1})
---
{chunk_2_text}
(Source: {document_title_2})
---
...

CONVERSATION HISTORY:
{history}

USER QUESTION: {query}

ANSWER:
```

#### 4.2.4 LLM Client

| Aspect | Detail |
|---|---|
| **Provider** | OpenAI API (GPT-4o-mini) or Ollama (Llama 3 8B) |
| **Interface** | Unified `LLMClient` abstract class with `generate(prompt, context) → str` |
| **Parameters** | `temperature=0.1`, `max_tokens=512`, `top_p=0.9` |
| **Fallback** | If primary LLM fails, return error message to user |
| **Streaming** | Optional token-by-token streaming (Phase 2) |

**LLM Client Interface:**
```python
class LLMClient(ABC):
    @abstractmethod
    def generate(self, messages: list[dict]) -> str:
        """Generate a response given a list of chat messages."""
        pass

class OpenAIClient(LLMClient):
    def __init__(self, model="gpt-4o-mini", api_key=None):
        ...

class OllamaClient(LLMClient):
    def __init__(self, model="llama3:8b", base_url="http://localhost:11434"):
        ...
```

---

### 4.3 API Layer

#### 4.3.1 Endpoint Specifications

| Endpoint | Method | Request Body | Response | Description |
|---|---|---|---|---|
| `/api/chat` | POST | `{query, session_id, history}` | `{response, sources, session_id}` | Main chat endpoint |
| `/api/ingest` | POST | Multipart form (file + metadata) | `{document_id, chunks_ingested}` | Upload and ingest document |
| `/api/health` | GET | None | `{status, components}` | Health check |
| `/api/documents` | GET | None | `{documents: [...]}` | List ingested documents |
| `/api/documents/{id}` | DELETE | None | `{status}` | Remove document and chunks |

#### 4.3.2 Session Management

| Aspect | Detail |
|---|---|
| **Session Store** | In-memory dictionary (Python `dict`) |
| **Session ID** | UUID generated on first request |
| **History Limit** | Last 10 messages per session |
| **TTL** | Sessions expire after 30 minutes of inactivity |
| **Persistence** | Not persisted to disk (session-only, per PRD) |

---

### 4.4 Data Layer

#### 4.4.1 Vector Database Schema (ChromaDB)

**Collection: `groww_knowledge_base`**

| Field | Type | Description |
|---|---|---|
| `id` | `str` | UUID for each chunk embedding |
| `embedding` | `list[float]` | 384-dimensional vector |
| `document` | `str` | Chunk text content |
| `metadata.document_id` | `str` | Parent document UUID |
| `metadata.document_title` | `str` | Human-readable title |
| `metadata.source` | `str` | File path or URL |
| `metadata.chunk_index` | `int` | Position in document |
| `metadata.token_count` | `int` | Approximate tokens |
| `metadata.created_at` | `str` | ISO 8601 timestamp |

#### 4.4.2 Document Store

**Storage: SQLite database at `./data/documents.db`**

**Table: `documents`**

| Column | Type | Description |
|---|---|---|
| `document_id` | `TEXT (PK)` | UUID |
| `title` | `TEXT` | Document title |
| `source` | `TEXT` | File path or URL |
| `file_type` | `TEXT` | pdf, txt, md, docx |
| `file_size` | `INTEGER` | Size in bytes |
| `chunk_count` | `INTEGER` | Number of chunks generated |
| `ingested_at` | `TEXT` | ISO 8601 timestamp |
| `status` | `TEXT` | pending, processing, completed, failed |

---

## 5. Data Flow

### 5.1 Ingestion Flow

```
User/Admin                 API Layer                Ingestion Pipeline           Vector DB
    │                         │                            │                        │
    │  POST /api/ingest       │                            │                        │
    │  (file + metadata)      │                            │                        │
    │────────────────────────►│                            │                        │
    │                         │  Save file to disk         │                        │
    │                         │───────────────────────────►│                        │
    │                         │                            │  Extract text          │
    │                         │                            │  Chunk text            │
    │                         │                            │  Generate embeddings   │
    │                         │                            │───────────────────────►│
    │                         │                            │  (store embeddings +   │
    │                         │                            │   metadata)            │
    │                         │                            │                        │
    │                         │  Return document_id        │                        │
    │                         │◄───────────────────────────│                        │
    │  200 OK                 │                            │                        │
    │◄────────────────────────│                            │                        │
```

### 5.2 Query Flow (Runtime RAG)

```
User                   API Layer              RAG Pipeline              Vector DB         LLM
  │                       │                        │                        │               │
  │  POST /api/chat       │                        │                        │               │
  │  {query, session_id}  │                        │                        │               │
  │──────────────────────►│                        │                        │               │
  │                       │  embed_query(query)    │                        │               │
  │                       │───────────────────────►│                        │               │
  │                       │                        │  similarity_search     │               │
  │                       │                        │───────────────────────►│               │
  │                       │                        │  top-K chunks          │               │
  │                       │                        │◄───────────────────────│               │
  │                       │                        │                        │               │
  │                       │                        │  build_prompt(query,   │               │
  │                       │                        │    chunks, history)    │               │
  │                       │                        │───────────────────────────────────────►│
  │                       │                        │  generated response    │               │
  │                       │                        │◄───────────────────────────────────────│
  │                       │                        │                        │               │
  │                       │  format_response(      │                        │               │
  │                       │    response, chunks)   │                        │               │
  │                       │◄───────────────────────│                        │               │
  │  200 OK               │                        │                        │               │
  │  {response, sources}  │                        │                        │               │
  │◄──────────────────────│                        │                        │               │
```

---

## 6. Technology Stack

### 6.1 Technology Selection Matrix

| Layer | Technology | Version | Justification |
|---|---|---|---|
| **Frontend** | Streamlit | ≥1.30 | Rapid prototyping, built-in chat components, minimal frontend code |
| **Backend** | FastAPI | ≥0.110 | Async support, automatic OpenAPI docs, Pydantic validation |
| **Orchestration** | LangChain | ≥0.1 | Pre-built RAG abstractions, text splitters, document loaders |
| **Embedding Model** | sentence-transformers/all-MiniLM-L6-v2 | 22M params | 384-dim, 80MB model, CPU-friendly, good semantic quality |
| **Vector DB** | ChromaDB | ≥0.4 | Local persistence, Python-native, simple API, HNSW indexing |
| **LLM** | Ollama + Llama 3 8B (or Mistral 7B) | — | Free, open-source, offline, no API keys needed |
| **Document Parsing** | PyPDF2, python-docx | — | Mature libraries for PDF/DOCX extraction |
| **Database** | SQLite | — | Lightweight, zero-config, local document metadata storage |
| **Server** | Uvicorn | — | ASGI server for FastAPI |
| **Containerization** | Docker | — | Reproducible deployment, easy demo setup |

### 6.2 Project Structure

```
groww-rag-chatbot/
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI application entry point
│   ├── config.py                # Central configuration (env vars, defaults)
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── chat.py          # POST /api/chat endpoint
│   │   │   ├── ingest.py        # POST /api/ingest endpoint
│   │   │   └── documents.py     # GET/DELETE /api/documents endpoints
│   │   └── schemas/
│   │       ├── __init__.py
│   │       ├── chat.py          # Pydantic models for chat request/response
│   │       └── document.py      # Pydantic models for document metadata
│   ├── pipeline/
│   │   ├── __init__.py
│   │   ├── ingestion.py         # Document ingestion pipeline
│   │   ├── query.py             # Query processing pipeline
│   │   └── components/
│   │       ├── __init__.py
│   │       ├── extractor.py     # Text extraction from documents
│   │       ├── chunker.py       # Text chunking logic
│   │       ├── embedder.py      # Embedding generation
│   │       ├── retriever.py     # Vector similarity search
│   │       ├── prompt_builder.py # Prompt construction
│   │       └── llm_client.py    # LLM API abstraction
│   ├── storage/
│   │   ├── __init__.py
│   │   ├── vector_store.py     # ChromaDB wrapper
│   │   └── document_store.py   # SQLite document metadata store
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py           # Internal data models (Chunk, Document, etc.)
│   └── ui/
│       ├── __init__.py
│       └── streamlit_app.py     # Streamlit chat interface
├── data/
│   ├── chroma/                  # ChromaDB persistent storage
│   ├── documents/               # Uploaded original documents
│   └── documents.db             # SQLite metadata database
├── documents/                   # Source documents for knowledge base
├── tests/
│   ├── test_ingestion.py
│   ├── test_query.py
│   ├── test_api.py
│   └── test_evaluation.py
├── .env                         # Environment variables (not in git)
├── .env.example                 # Template for environment variables
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── PRD.md
├── architecture.md              # This file
└── README.md
```

---

## 7. Configuration

### 7.1 Environment Variables

| Variable | Default | Description |
|---|---|---|
| `EMBEDDING_MODEL` | `sentence-transformers/all-MiniLM-L6-v2` | HuggingFace model ID |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL |
| `OLLAMA_MODEL` | `llama3:8b` | Ollama model name (llama3:8b, mistral:7b, phi3:mini) |
| `CHUNK_SIZE` | `400` | Tokens per chunk |
| `CHUNK_OVERLAP` | `80` | Overlap between chunks (tokens) |
| `TOP_K` | `5` | Number of chunks to retrieve |
| `SIMILARITY_THRESHOLD` | `0.5` | Minimum cosine similarity score |
| `MAX_HISTORY` | `10` | Max conversation messages per session |
| `SESSION_TTL_MINUTES` | `30` | Session expiration time |
| `VECTOR_DB_PATH` | `./data/chroma` | ChromaDB storage path |
| `DOCUMENT_STORE_PATH` | `./data/documents.db` | SQLite database path |
| `UPLOAD_DIR` | `./data/documents` | Uploaded files directory |
| `LOG_LEVEL` | `INFO` | Logging verbosity |

### 7.2 Configuration Loading

```python
# app/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3:8b"
    chunk_size: int = 400
    chunk_overlap: int = 80
    top_k: int = 5
    similarity_threshold: float = 0.5
    max_history: int = 10
    session_ttl_minutes: int = 30
    vector_db_path: str = "./data/chroma"
    document_store_path: str = "./data/documents.db"
    upload_dir: str = "./data/documents"
    log_level: str = "INFO"

    class Config:
        env_file = ".env"

settings = Settings()
```

---

## 8. Deployment Architecture

### 8.1 Local Development Deployment

```
┌─────────────────────────────────────────────┐
│              Local Machine                   │
│                                             │
│  ┌─────────────┐    ┌───────────────────┐  │
│  │  Streamlit  │    │   FastAPI Server  │  │
│  │  UI :8501   │◄──►│   :8000           │  │
│  └─────────────┘    └─────────┬─────────┘  │
│                               │            │
│                     ┌─────────┴─────────┐  │
│                     │   RAG Pipeline    │  │
│                     │  (LangChain)      │  │
│                     └─────────┬─────────┘  │
│                               │            │
│              ┌────────────────┼────────┐   │
│              │                │        │   │
│              ▼                ▼        ▼   │
│       ┌───────────┐  ┌──────────┐ ┌─────┐ │
│       │ ChromaDB  │  │ SQLite   │ │ LLM │ │
│       │ :8001     │  │ :file    │ │ API │ │
│       └───────────┘  └──────────┘ └─────┘ │
└─────────────────────────────────────────────┘
```

### 8.2 Docker Deployment

```yaml
# docker-compose.yml
version: "3.9"

services:
  api:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - OLLAMA_BASE_URL=http://ollama:11434
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
    command: streamlit run app/ui/streamlit_app.py --server.port 8501

  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    command: >
      sh -c "ollama serve & sleep 2 && ollama pull llama3:8b && wait"

volumes:
  ollama_data:
```

### 8.3 Deployment Scenarios

| Scenario | Components | Use Case |
|---|---|---|
| **Minimal Local** | FastAPI + ChromaDB + Ollama | Developer machine, fully free, no API keys |
| **Docker** | All containers via docker-compose (API + UI + Ollama) | Reproducible demo environment |
| **Cloud VM** | FastAPI + ChromaDB + Ollama | Remote demo for larger audience |

---

## 9. Security Considerations

| Concern | Mitigation |
|---|---|
| API key exposure | Keys stored in `.env` file, never in source code; `.env` in `.gitignore` |
| File upload validation | Validate file type (whitelist: PDF, TXT, MD, DOCX), max file size (10MB) |
| Prompt injection | System prompt instructs LLM to only use retrieved context; input sanitization |
| Session data | In-memory only, no PII stored, sessions expire after 30 min |
| CORS | Restrict to localhost or specific origins in production |
| Dependency scanning | Pin versions in `requirements.txt`, use `pip-audit` |

---

## 10. Performance & Scalability

### 10.1 Performance Targets (from PRD)

| Metric | Target | Measurement |
|---|---|---|
| End-to-end response latency | < 5s (P95) | Time from POST /api/chat to response |
| Embedding generation | < 200ms per query | Local MiniLM model |
| Vector search | < 100ms for top-5 | ChromaDB HNSW index |
| LLM generation | < 3s for 512 tokens | GPT-4o-mini or Llama 3 8B |
| Concurrent users | 1–5 | Demo scenario |

### 10.2 Scalability Considerations

| Aspect | Current | Future |
|---|---|---|
| Vector DB | ChromaDB (local, single-node) | Pinecone/Weaviated (cloud, distributed) |
| Embedding | CPU-based MiniLM | GPU-accelerated or API-based embeddings |
| LLM | Single request/response | Streaming, batch processing |
| Sessions | In-memory dict | Redis for distributed session storage |
| Documents | 25–50 documents | 1000+ with metadata filtering and hybrid search |

---

## 11. Monitoring & Observability

### 11.1 Logging

| Log Level | Events |
|---|---|
| `INFO` | Request received, document ingested, response generated |
| `WARNING` | Low similarity scores, fallback triggered, retry attempts |
| `ERROR` | LLM API failure, document parse failure, vector DB unavailable |
| `DEBUG` | Chunk details, embedding vectors, prompt content |

### 11.2 Key Metrics to Track

| Metric | Description |
|---|---|
| `requests_total` | Total API requests |
| `request_latency_seconds` | Response time histogram |
| `retrieval_score_avg` | Average similarity score of retrieved chunks |
| `fallback_count` | Number of times fallback response was triggered |
| `documents_ingested_total` | Total documents in knowledge base |
| `chunks_stored_total` | Total chunks in vector DB |

### 11.3 Health Check Response

```json
{
  "status": "healthy",
  "components": {
    "vector_db": "connected",
    "llm": "connected",
    "document_store": "connected"
  },
  "documents_count": 35,
  "chunks_count": 420,
  "uptime_seconds": 3600
}
```

---

## 12. Error Handling Strategy

### 12.1 Error Categories

| Category | Examples | Handling |
|---|---|---|
| **Client Errors** | Invalid query, missing session_id | Return 400 with descriptive message |
| **Document Errors** | Corrupt file, unsupported format | Return 422, log error, skip document |
| **Retrieval Errors** | Vector DB unavailable, no results | Return fallback response, log warning |
| **LLM Errors** | API timeout, rate limit, invalid key | Return 503, suggest retry, log error |
| **System Errors** | Out of memory, disk full | Return 500, alert admin, log critical |

### 12.2 Fallback Behavior

```
User Query
    │
    ▼
Embed Query ──► Retrieve Top-K Chunks
    │                    │
    │              ┌─────┴─────┐
    │              │           │
    │         Score > 0.5   Score ≤ 0.5
    │              │           │
    │              ▼           ▼
    │         Build Prompt   Return Fallback:
    │         Call LLM       "I couldn't find
    │              │          relevant information.
    │              ▼          Could you rephrase?"
    │         Format Response
    │              │
    ▼              ▼
Return Response + Sources to User
```

---

## 13. Testing Architecture

### 13.1 Test Pyramid

```
            ┌─────────┐
            │   E2E   │  (5 tests)  — Full pipeline via API
           ┌┴─────────┴┐
           │ Integration│  (15 tests) — Pipeline components together
          ┌┴───────────┴┐
          │    Unit      │  (50+ tests) — Individual functions
         ┌┴─────────────┴┐
         │  Evaluation   │  (30 queries) — Quality metrics
         └───────────────┘
```

### 13.2 Test Data

| Dataset | Description |
|---|---|
| `test_documents/` | 5–10 sample documents for ingestion testing |
| `test_queries.json` | 30 curated queries with expected topics/keywords |
| `test_sessions.py` | Simulated multi-turn conversations |

### 13.3 Evaluation Framework

```python
# Evaluation metrics computed on test query set
metrics = {
    "answer_relevance": 0.85,      # % of answers covering expected topic
    "source_accuracy": 0.92,       # % of cited sources actually relevant
    "fallback_precision": 0.95,    # % of fallbacks correctly triggered
    "avg_latency_seconds": 3.2,    # Mean response time
    "p95_latency_seconds": 4.8,    # 95th percentile response time
}
```

---

## 14. Sequence Diagrams

### 14.1 Chat Interaction Sequence

```
User          UI (Streamlit)       API (FastAPI)         RAG Pipeline          Vector DB        LLM
 │                  │                    │                      │                    │              │
 │  Type query      │                    │                      │                    │              │
 │─────────────────►│                    │                      │                    │              │
 │                  │  POST /api/chat    │                      │                    │              │
 │                  │  {query, session}  │                      │                    │              │
 │                  │───────────────────►│                      │                    │              │
 │                  │                    │  process_query()     │                    │              │
 │                  │                    │─────────────────────►│                    │              │
 │                  │                    │                      │  embed(query)      │              │
 │                  │                    │                      │  search(top_k=5)   │              │
 │                  │                    │                      │───────────────────►│              │
 │                  │                    │                      │  chunks + scores   │              │
 │                  │                    │                      │◄───────────────────│              │
 │                  │                    │                      │                    │              │
 │                  │                    │                      │  build_prompt()    │              │
 │                  │                    │                      │  generate()        │              │
 │                  │                    │                      │──────────────────────────────────►│
 │                  │                    │                      │  response text     │              │
 │                  │                    │                      │◄──────────────────────────────────│
 │                  │                    │                      │                    │              │
 │                  │                    │  {response, sources} │                    │              │
 │                  │                    │◄─────────────────────│                    │              │
 │                  │  200 OK            │                      │                    │              │
 │                  │◄───────────────────│                      │                    │              │
 │  Display        │                    │                      │                    │              │
 │  response +     │                    │                      │                    │              │
 │  sources        │                    │                      │                    │              │
 │◄─────────────────│                    │                      │                    │              │
```

### 14.2 Document Ingestion Sequence

```
Admin           UI (Streamlit)       API (FastAPI)         Ingestion Pipeline     Vector DB
 │                  │                    │                      │                    │
 │  Upload file     │                    │                      │                    │
 │─────────────────►│                    │                      │                    │
 │                  │  POST /api/ingest  │                      │                    │
 │                  │  (multipart form)  │                      │                    │
 │                  │───────────────────►│                      │                    │
 │                  │                    │  save_file()         │                    │
 │                  │                    │  extract_text()      │                    │
 │                  │                    │  chunk_text()        │                    │
 │                  │                    │  embed_chunks()      │                    │
 │                  │                    │─────────────────────►│                    │
 │                  │                    │                      │  store_embeddings()│
 │                  │                    │                      │───────────────────►│
 │                  │                    │                      │  success           │
 │                  │                    │                      │◄───────────────────│
 │                  │                    │  {document_id,       │                    │
 │                  │                    │   chunks_ingested}   │                    │
 │                  │                    │◄─────────────────────│                    │
 │                  │  200 OK            │                      │                    │
 │                  │◄───────────────────│                      │                    │
 │  Show success   │                    │                      │                    │
 │◄─────────────────│                    │                      │                    │
```

---

## 15. Design Patterns Used

| Pattern | Application |
|---|---|
| **Pipeline Pattern** | Both ingestion and query processing follow a staged pipeline with clear inputs/outputs. |
| **Strategy Pattern** | LLM client uses strategy pattern to switch between OpenAI and Ollama implementations. |
| **Repository Pattern** | Vector store and document store abstract data access behind repository interfaces. |
| **Factory Pattern** | LLM client factory creates the appropriate client based on configuration. |
| **Singleton Pattern** | Vector DB connection and embedding model are loaded once and reused across requests. |
| **Dependency Injection** | FastAPI's dependency injection provides pipeline components to route handlers. |

---

## 16. Key Design Decisions

| Decision | Rationale | Trade-off |
|---|---|---|
| **ChromaDB over Pinecone** | Free, local, zero-config; sufficient for demo scale | Limited scalability; no cloud hosting |
| **MiniLM-L6-v2 embeddings** | Small (80MB), fast on CPU, good semantic quality | Lower accuracy than larger models (e.g., BERT-large) |
| **LangChain for orchestration** | Pre-built abstractions speed up development | Adds dependency; less control over internals |
| **Streamlit for UI** | Fastest path to a functional chat UI | Less customizable than React |
| **SQLite for metadata** | Zero-config, file-based, sufficient for demo | Not suitable for high-concurrency production |
| **Ollama as sole LLM** | Free, no API keys, fully offline, open-source | Llama 3 8B requires ~5GB RAM; may be slow on low-end machines |
| **In-memory session store** | Simple, no external dependency needed | Sessions lost on restart; not horizontally scalable |

---

## 17. Risks & Mitigations (Technical)

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| ChromaDB corruption or data loss | Low | High | Backup `./data/chroma/` regularly; re-ingestion script |
| Ollama model too slow on demo machine | Medium | Medium | Use smaller model (Llama 3 8B → Mistral 7B or phi3:mini) |
| Ollama model not pulled | Medium | High | Auto-pull on startup via docker-compose; manual `ollama pull` for local dev |
| Embedding model download fails (offline) | Medium | High | Pre-download model; bundle in Docker image |
| Prompt injection via user query | Low | Medium | System prompt guardrails; input length limits |
| Large documents cause OOM | Low | High | Stream processing; chunk size limits; file size validation |

---

## 18. Future Architecture Evolution

### 18.1 Phase 2 Enhancements

```
Current (Phase 1)                    Future (Phase 2)
─────────────────                    ────────────────
Single embedding model        →      Hybrid search (BM25 + Dense)
Top-K flat retrieval           →      Re-ranked with cross-encoder
Single LLM                     →      Multi-model routing (complex vs simple)
In-memory sessions             →      Redis-backed sessions
Static documents               →      Auto-refresh from Groww help center
No feedback loop               →      Thumbs up/down → fine-tuning data
```

### 18.2 Scalability Roadmap

| Stage | Users | Architecture Changes |
|---|---|---|
| **Demo (Now)** | 1–5 | Single machine, local everything |
| **Classroom** | 20–30 | Docker on cloud VM, shared instance |
| **Department** | 100+ | Separate API server, Pinecone cloud, Redis sessions |
| **Production** | 10,000+ | Kubernetes, CDN, multi-region, monitoring |

---

## 19. Appendix

### 19.1 API OpenAPI Specification

The FastAPI application auto-generates OpenAPI docs at `/docs` (Swagger UI) and `/redoc` (ReDoc) when running.

### 19.2 Data Models Summary

```
Document
├── document_id: str (PK)
├── title: str
├── source: str
├── file_type: str
├── file_size: int
├── chunk_count: int
├── ingested_at: datetime
└── status: str

Chunk
├── chunk_id: str (PK)
├── document_id: str (FK)
├── document_title: str
├── source: str
├── chunk_index: int
├── text: str
├── token_count: int
└── created_at: datetime

Session
├── session_id: str (PK)
├── messages: list[Message]
├── created_at: datetime
└── last_activity: datetime

Message
├── role: str (user | assistant)
├── content: str
└── timestamp: datetime
```

### 19.3 Glossary

| Term | Definition |
|---|---|
| **RAG** | Retrieval-Augmented Generation — combining information retrieval with LLM generation |
| **Embedding** | Numerical vector representation of text capturing semantic meaning |
| **Chunk** | A segment of text from a document, used as the unit of retrieval |
| **Vector DB** | Database optimized for storing and searching high-dimensional vectors |
| **Top-K** | The K most similar items returned by a similarity search |
| **LLM** | Large Language Model — AI model trained to generate human-like text |
| **HNSW** | Hierarchical Navigable Small World — approximate nearest neighbor search algorithm |
| **TTL** | Time To Live — expiration time for cached or session data |

---

*End of Document*

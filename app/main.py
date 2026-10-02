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

    logger.info("Vector store contains {} chunks".format(vector_store.count()))
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
            "llm": "groq",
            "document_store": "connected"
        },
        "documents_count": len(document_store.list_documents()) if document_store else 0,
        "chunks_count": vector_store.count() if vector_store else 0
    }

"""Central configuration management using Pydantic Settings."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Embedding Model
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"

    # Groq Settings (LLM via Groq API)
    groq_api_key: str = ""
    groq_model: str = "qwen/qwen3.8-27b"

    # Hugging Face (optional token for model downloads)
    hf_token: str = ""

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

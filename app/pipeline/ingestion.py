"""Document ingestion pipeline orchestrator."""
import os
from pathlib import Path
from app.models.schemas import Document
from app.storage.document_store import DocumentStore
from app.storage.vector_store import VectorStore
from app.pipeline.components.extractor import TextExtractor, DocumentParseException
from app.pipeline.components.chunker import Chunker
from app.pipeline.components.embedder import Embedder


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

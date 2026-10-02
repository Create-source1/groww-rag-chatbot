"""ChromaDB-based vector storage for document chunks."""
import os
import chromadb
from chromadb.config import Settings as ChromaSettings
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
            batch_size=32
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
               threshold: float = None, where: dict = None) -> list[RetrievedChunk]:
        """Search for similar chunks given a query embedding, optionally filtered."""
        top_k = top_k or settings.top_k
        threshold = threshold or settings.similarity_threshold

        query_kwargs = {
            "query_embeddings": [query_embedding],
            "n_results": top_k,
            "include": ["documents", "metadatas", "distances"],
        }
        if where:
            query_kwargs["where"] = where

        results = self.collection.query(**query_kwargs)

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

"""Vector similarity search for query retrieval."""
from app.storage.vector_store import VectorStore
from app.pipeline.components.embedder import Embedder


class Retriever:
    """Retrieves relevant chunks for a given query."""

    def __init__(self, vector_store: VectorStore, embedder: Embedder):
        self.vector_store = vector_store
        self.embedder = embedder

    def retrieve(self, query: str, top_k: int = None,
                 threshold: float = None, where: dict = None):
        """Retrieve top-K relevant chunks for a query."""
        query_embedding = self.embedder.encode_query(query)
        return self.vector_store.search(query_embedding, top_k, threshold, where)

    def retrieve_literal(self, keyword: str, where: dict = None, limit: int = 10):
        """Return chunks whose text literally contains the keyword (BM25-style)."""
        from app.models.schemas import RetrievedChunk
        results = self.vector_store.collection.get(
            where=where,
            where_document={"$contains": keyword},
            include=["documents", "metadatas"],
            limit=limit,
        )
        chunks = []
        for chunk_id, text, metadata in zip(results["ids"], results["documents"], results["metadatas"]):
            chunks.append(RetrievedChunk(
                chunk_id=chunk_id,
                document_title=metadata.get("document_title", "Unknown"),
                source=metadata.get("source", ""),
                chunk_index=metadata.get("chunk_index", 0),
                text=text,
                similarity_score=0.5,  # neutral score; ranking is by coverage
            ))
        return chunks

"""Quick manual test for the retrieval pipeline."""
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from app.storage.vector_store import VectorStore
from app.pipeline.components.embedder import Embedder
from app.pipeline.components.retriever import Retriever

vector_store = VectorStore()
embedder = Embedder()
retriever = Retriever(vector_store, embedder)

print(f"Chunks in vector store: {vector_store.count()}\n")

queries = [
    "How do I start investing on Groww?",
    "What is a SIP?",
    "How to complete KYC verification?",
]

for query in queries:
    chunks = retriever.retrieve(query, top_k=3)
    print(f"=== Query: {query!r} — {len(chunks)} chunks found ===")
    for i, c in enumerate(chunks, 1):
        print(f"  {i}. score={c.similarity_score:.4f} | {c.document_title} | chunk {c.chunk_index}")
        print(f"     {c.text[:150].replace(chr(10), ' ')}...")
    print()

"""Interactive terminal chat to test the full RAG pipeline (retrieval + Groq LLM)."""
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from app.storage.document_store import DocumentStore
from app.storage.vector_store import VectorStore
from app.pipeline.components.embedder import Embedder
from app.pipeline.query import QueryPipeline

print("Loading components (first run may take a moment)...")
vector_store = VectorStore()
embedder = Embedder()
pipeline = QueryPipeline(vector_store, embedder)
print(f"Ready. {vector_store.count()} chunks indexed. Type 'quit' to exit.\n")

history = []
while True:
    try:
        query = input("You: ").strip()
    except (EOFError, KeyboardInterrupt):
        break
    if query.lower() in {"quit", "exit"}:
        break
    if not query:
        continue

    result = pipeline.process(query, history)
    print(f"\nBot: {result['response']}\n")

    if result["sources"]:
        print("Sources:")
        for s in result["sources"]:
            print(f"  - {s['source']} (score: {s['similarity_score']})")
        print()

    from app.models.schemas import Message
    history.append(Message(role="user", content=query))
    history.append(Message(role="assistant", content=result["response"]))

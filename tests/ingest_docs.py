"""Re-ingest everything in documents/ from scratch (wipes existing vector store + doc store)."""
import os
import shutil
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from pathlib import Path

from app.config import settings

# Wipe existing stores so we rebuild cleanly (avoids duplicate/stale chunks)
if os.path.exists(settings.vector_db_path):
    shutil.rmtree(settings.vector_db_path)
if os.path.exists(settings.document_store_path):
    os.remove(settings.document_store_path)

from app.storage.document_store import DocumentStore
from app.storage.vector_store import VectorStore
from app.pipeline.ingestion import IngestionPipeline

print("Initializing stores...")
document_store = DocumentStore()
vector_store = VectorStore()
pipeline = IngestionPipeline(document_store, vector_store)

print(f"Ingesting all files in ./documents ...")
docs = pipeline.ingest_directory("documents")
print(f"\nIngested {len(docs)} documents:")
for d in docs:
    print(f"  - {d.title} ({d.chunk_count} chunks, {d.status})")
print(f"\nTotal chunks in vector store: {vector_store.count()}")

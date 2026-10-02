# -*- coding: utf-8 -*-
"""Script to ingest documents and dump chunks + embeddings to a text file."""
from __future__ import print_function
import os
import sys
import json
import numpy as np

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.storage.document_store import DocumentStore
from app.storage.vector_store import VectorStore
from app.pipeline.components.extractor import TextExtractor
from app.pipeline.components.chunker import Chunker
from app.pipeline.components.embedder import Embedder
from app.config import settings


def main():
    print("=" * 80)
    print("GROWW RAG CHATBOT - CHUNK & EMBEDDING DUMP")
    print("=" * 80)

    # Initialize components
    doc_store = DocumentStore()
    vector_store = VectorStore()
    embedder = Embedder()
    vector_store.set_embedding_model(embedder)

    # Ingest all documents from the documents/ folder
    docs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "documents")
    print("\nIngesting documents from: {}".format(docs_dir))
    print("-" * 80)

    extractor = TextExtractor()
    chunker = Chunker()

    all_chunks = []
    for filename in sorted(os.listdir(docs_dir)):
        file_path = os.path.join(docs_dir, filename)
        ext = os.path.splitext(filename)[1].lower()
        if ext not in extractor.SUPPORTED_FORMATS:
            continue

        print("\nProcessing: {}".format(filename))
        try:
            text = extractor.extract(file_path)
            print("  Extracted text length: {} characters".format(len(text)))

            chunks = chunker.chunk_text(
                text=text,
                document_id="doc-{}".format(filename),
                document_title=filename,
                source=file_path
            )
            print("  Generated {} chunks".format(len(chunks)))
            all_chunks.extend(chunks)
        except Exception as e:
            print("  ERROR: {}".format(e))

    # Generate embeddings
    print("\n" + "=" * 80)
    print("GENERATING EMBEDDINGS")
    print("=" * 80)
    print("Model: {}".format(settings.embedding_model))
    print("Total chunks to embed: {}".format(len(all_chunks)))

    embeddings = None
    if all_chunks:
        embeddings = embedder.encode([c.text for c in all_chunks])
        print("Embedding shape: {}".format(embeddings.shape))
        print("Embedding dimension: {}".format(embeddings.shape[1]))

        # Store in vector DB
        vector_store.add_chunks(all_chunks)
        print("Stored {} chunks in ChromaDB".format(vector_store.count()))

    # Write output file
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "chunks_and_embeddings.txt")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("GROWW RAG CHATBOT - CHUNKS & EMBEDDINGS DUMP\n")
        f.write("=" * 80 + "\n\n")

        f.write("Total documents processed: {}\n".format(len([x for x in os.listdir(docs_dir) if x.endswith(('.md', '.txt', '.pdf', '.docx'))])))
        f.write("Total chunks generated: {}\n".format(len(all_chunks)))
        f.write("Embedding model: {}\n".format(settings.embedding_model))
        f.write("Embedding dimension: {}\n".format(embeddings.shape[1] if embeddings is not None else 0))
        f.write("Chunk size: {} tokens\n".format(settings.chunk_size))
        f.write("Chunk overlap: {} tokens\n\n".format(settings.chunk_overlap))

        f.write("=" * 80 + "\n")
        f.write("CHUNKS\n")
        f.write("=" * 80 + "\n\n")

        for i, chunk in enumerate(all_chunks):
            f.write("--- Chunk {}/{} ---\n".format(i + 1, len(all_chunks)))
            f.write("  Document: {}\n".format(chunk.document_title))
            f.write("  Source: {}\n".format(chunk.source))
            f.write("  Chunk Index: {}\n".format(chunk.chunk_index))
            f.write("  Token Count: {}\n".format(chunk.token_count))
            f.write("  Text:\n")
            for line in chunk.text.split("\n"):
                f.write("    {}\n".format(line))
            f.write("\n")

        if embeddings is not None:
            f.write("=" * 80 + "\n")
            f.write("EMBEDDINGS (first 10 dimensions per chunk)\n")
            f.write("=" * 80 + "\n\n")

            for i, (chunk, embedding) in enumerate(zip(all_chunks, embeddings)):
                f.write("--- Embedding for Chunk {} ---\n".format(i + 1))
                f.write("  Document: {}\n".format(chunk.document_title))
                f.write("  Chunk Index: {}\n".format(chunk.chunk_index))
                f.write("  Full dimension: {}\n".format(len(embedding)))
                f.write("  First 10 values: {}\n".format(embedding[:10].tolist()))
                f.write("  L2 Norm: {:.6f}\n".format(np.linalg.norm(embedding)))
                f.write("\n")

    print("\nOutput written to: {}".format(output_path))
    print("Done!")


if __name__ == "__main__":
    main()

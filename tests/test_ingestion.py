"""Tests for the ingestion pipeline."""
import os
import pytest

from app.storage.document_store import DocumentStore
from app.storage.vector_store import VectorStore
from app.pipeline.ingestion import IngestionPipeline


@pytest.fixture
def doc_store(tmp_path):
    return DocumentStore(str(tmp_path / "test.db"))


@pytest.fixture
def vector_store(tmp_path):
    return VectorStore(str(tmp_path / "chroma"))


@pytest.fixture
def pipeline(doc_store, vector_store):
    return IngestionPipeline(doc_store, vector_store)


def test_ingest_markdown_file(pipeline, doc_store):
    """Test ingesting a markdown file."""
    test_file = os.path.join("documents", "hdfc_large_cap_fund.md")
    if not os.path.exists(test_file):
        pytest.skip("Test document not found")

    doc = pipeline.ingest_file(test_file)
    assert doc.status == "completed"
    assert doc.chunk_count > 0

    stored = doc_store.get_document(doc.document_id)
    assert stored is not None
    assert stored.title == doc.title


def test_ingest_unsupported_format(pipeline):
    """Test that unsupported formats raise an error."""
    with pytest.raises(Exception):
        pipeline.ingest_file("test.xyz")


def test_chunk_count_matches_vector_store(pipeline):
    """Ingested chunks should be searchable/counted in the vector store."""
    test_file = os.path.join("documents", "hdfc_large_cap_fund.md")
    if not os.path.exists(test_file):
        pytest.skip("Test document not found")

    before = pipeline.vector_store.count()
    doc = pipeline.ingest_file(test_file)
    assert pipeline.vector_store.count() == before + doc.chunk_count

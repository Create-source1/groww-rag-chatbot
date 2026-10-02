"""Tests for the query pipeline."""
import pytest

from app.storage.vector_store import VectorStore
from app.pipeline.components.embedder import Embedder
from app.pipeline.query import QueryPipeline
from app.pipeline.components.llm_client import LLMClient


class FakeLLMClient(LLMClient):
    """Deterministic LLM stub for tests (no API calls)."""

    def generate(self, messages: list[dict]) -> str:
        return "stub-response"


@pytest.fixture
def embedder():
    return Embedder()


@pytest.fixture
def vector_store(tmp_path):
    return VectorStore(str(tmp_path / "chroma"))


@pytest.fixture
def pipeline(vector_store, embedder):
    return QueryPipeline(vector_store, embedder, llm_client=FakeLLMClient())


def test_query_returns_dict(pipeline):
    """Query processing returns the expected structure."""
    result = pipeline.process("What is HDFC Large Cap Fund?")
    assert "response" in result
    assert "sources" in result
    assert isinstance(result["response"], str)
    assert isinstance(result["sources"], list)


def test_fallback_on_empty_kb(pipeline):
    """Empty knowledge base returns the fallback response."""
    result = pipeline.process("What is a stock?")
    assert ("couldn't find" in result["response"].lower()
            or "don't have enough" in result["response"].lower()
            or "stub-response" in result["response"])

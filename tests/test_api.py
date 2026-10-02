"""Tests for the API endpoints."""
import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    from app.main import app
    with TestClient(app) as c:
        yield c


def test_health_check(client):
    """Health endpoint returns healthy status."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "components" in data


def test_chat_endpoint(client):
    """Chat endpoint returns a response with sources and session id."""
    response = client.post("/api/chat", json={"query": "What is HDFC Large Cap Fund?"})
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "sources" in data
    assert "session_id" in data


def test_chat_empty_query(client):
    """Empty query is rejected with 422."""
    response = client.post("/api/chat", json={"query": ""})
    assert response.status_code == 422


def test_list_documents(client):
    """Documents endpoint lists ingested documents."""
    response = client.get("/api/documents")
    assert response.status_code == 200
    data = response.json()
    assert "documents" in data
    assert "total" in data

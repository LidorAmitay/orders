"""
Tests for the /health endpoint.
"""
import pytest
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_health_endpoint():
    """Test that the /health endpoint returns a valid JSON response."""
    response = client.get("/health")
    
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    
    data = response.json()
    assert "status" in data
    assert data["status"] == "ok"


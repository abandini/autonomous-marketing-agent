import os
import pytest
from fastapi.testclient import TestClient

from core.orchestrator.resolver import app

# Initialize TestClient for A2A resolver with mounted MCP stubs
client = TestClient(app)

def test_semrush_mcp_stub_mount():
    payload = {"params": {"keyword": "example"}}
    response = client.post("/mcp/semrush/search_products", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["agent"] == "mcp.semrush"
    assert data["capability"] == "search_products"
    assert data["data"] == payload["params"]

def test_invoke_semrush_mcp_integration():
    payload = {"agent": "mcp.semrush", "capability": "search_products", "params": {"keyword": "test"}}
    response = client.post("/invoke", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["agent"] == "mcp.semrush"
    assert data["capability"] == "search_products"
    assert data["data"] == payload["params"]

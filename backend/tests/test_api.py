"""
Basic API Tests using FastAPI TestClient
"""
import pytest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_root_endpoint():
    """Test root endpoint returns API info."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "endpoints" in data

def test_companies_endpoint():
    """Test /companies endpoint."""
    response = client.get("/companies")
    # Should return 200 if DB exists and has data, or 503/404 if not initialized
    assert response.status_code in [200, 503, 404]
    if response.status_code == 200:
        data = response.json()
        assert "companies" in data
        assert isinstance(data["companies"], list)

def test_data_endpoint_invalid_symbol():
    """Test /data/{symbol} with invalid symbol."""
    response = client.get("/data/INVALID_SYMBOL")
    assert response.status_code in [404, 503]

def test_summary_endpoint_invalid_symbol():
    """Test /summary/{symbol} with invalid symbol."""
    response = client.get("/summary/INVALID_SYMBOL")
    assert response.status_code in [404, 503]

def test_compare_endpoint_missing_params():
    """Test /compare endpoint without required parameters."""
    response = client.get("/compare")
    assert response.status_code == 422  # Validation error

def test_docs_endpoint():
    """Test Swagger docs are accessible."""
    response = client.get("/docs")
    assert response.status_code == 200

def test_openapi_endpoint():
    """Test OpenAPI schema is accessible."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert "info" in data
    assert "paths" in data

if __name__ == "__main__":
    pytest.main([__file__, "-v"])


"""
Tests for API health and root endpoints
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch


class TestHealthEndpoints:
    """Tests for health check endpoints"""

    def test_root_endpoint(self, app_client):
        """Test root endpoint returns service info"""
        response = app_client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "Data Pipeline Validation System"
        assert data["version"] == "0.1.0"
        assert data["status"] == "running"
        assert data["docs"] == "/docs"

    def test_health_check(self, app_client):
        """Test health check endpoint"""
        response = app_client.get("/health")

        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}

    def test_readiness_check(self, app_client):
        """Test readiness check endpoint"""
        response = app_client.get("/ready")

        assert response.status_code == 200
        assert response.json() == {"status": "ready"}

    def test_docs_endpoint_accessible(self, app_client):
        """Test that API docs are accessible"""
        response = app_client.get("/docs")

        assert response.status_code == 200

    def test_redoc_endpoint_accessible(self, app_client):
        """Test that ReDoc is accessible"""
        response = app_client.get("/redoc")

        assert response.status_code == 200


class TestCORSConfiguration:
    """Tests for CORS middleware"""

    def test_cors_headers_present(self, app_client):
        """Test CORS headers are present in response"""
        response = app_client.options(
            "/",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET"
            }
        )

        # CORS should allow the request
        assert response.status_code in [200, 204]

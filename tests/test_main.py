"""Tests for main application endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestMainEndpoints:
    """Tests for main application endpoints."""
    
    async def test_root_endpoint(self, client: AsyncClient) -> None:
        """Test root endpoint returns API information."""
        response = await client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "docs" in data
        assert data["docs"] == "/docs"
        assert data["redoc"] == "/redoc"
    
    async def test_health_endpoint(self, client: AsyncClient) -> None:
        """Test health check endpoint."""
        response = await client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "app" in data
        assert "version" in data
        assert "debug" in data
    
    async def test_ready_endpoint(self, client: AsyncClient) -> None:
        """Test readiness check endpoint."""
        response = await client.get("/ready")
        
        assert response.status_code == 200
        data = response.json()
        assert data["ready"] is True
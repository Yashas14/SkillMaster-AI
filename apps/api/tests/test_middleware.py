# ════════════════════════════════════════════════════════════
# Middleware Tests
# ════════════════════════════════════════════════════════════

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestMiddleware:
    """Tests for custom middleware."""

    async def test_timing_header(self, client: AsyncClient):
        """All responses should include X-Process-Time header."""
        response = await client.get("/health")
        assert "X-Process-Time" in response.headers
        # Should be a valid float
        process_time = float(response.headers["X-Process-Time"])
        assert process_time >= 0

    async def test_security_headers(self, client: AsyncClient):
        """All responses should include security headers."""
        response = await client.get("/health")
        assert response.headers.get("X-Content-Type-Options") == "nosniff"
        assert response.headers.get("X-Frame-Options") == "DENY"
        assert response.headers.get("X-XSS-Protection") == "1; mode=block"

    async def test_request_id_header(self, client: AsyncClient):
        """All responses should include X-Request-ID header."""
        response = await client.get("/health")
        assert "X-Request-ID" in response.headers
        assert len(response.headers["X-Request-ID"]) > 0

    async def test_request_id_forwarded(self, client: AsyncClient):
        """Custom X-Request-ID should be forwarded."""
        custom_id = "test-request-123"
        response = await client.get(
            "/health", headers={"X-Request-ID": custom_id}
        )
        assert response.headers.get("X-Request-ID") == custom_id


@pytest.mark.asyncio
class TestHealthEndpoint:
    """Tests for /health endpoint."""

    async def test_health_returns_ok(self, client: AsyncClient):
        """Health endpoint should return healthy status."""
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "timestamp" in data

    async def test_health_includes_service_info(self, client: AsyncClient):
        """Health endpoint should include service information."""
        response = await client.get("/health")
        data = response.json()
        assert "environment" in data or "status" in data

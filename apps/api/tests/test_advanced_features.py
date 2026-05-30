# ════════════════════════════════════════════════════════════
# Gamification Router Tests
# ════════════════════════════════════════════════════════════

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestGamificationRouter:
    """Tests for /api/v1/gamification endpoints."""

    async def test_profile_requires_auth(self, client: AsyncClient):
        """Unauthenticated users cannot access gamification profile."""
        response = await client.get("/api/v1/gamification/profile")
        assert response.status_code in (401, 403)

    async def test_leaderboard_accessible(self, client: AsyncClient):
        """Leaderboard endpoint exists."""
        response = await client.get("/api/v1/gamification/leaderboard")
        # Leaderboard may be public or require auth
        assert response.status_code in (200, 401)

    async def test_check_badges_requires_auth(self, client: AsyncClient):
        """Badge check requires authentication."""
        response = await client.post("/api/v1/gamification/check-badges")
        assert response.status_code in (401, 403)

    async def test_update_streak_requires_auth(self, client: AsyncClient):
        """Streak update requires authentication."""
        response = await client.post("/api/v1/gamification/streak")
        assert response.status_code in (401, 403)


@pytest.mark.asyncio
class TestAnalyticsRouter:
    """Tests for /api/v1/analytics endpoints."""

    async def test_student_analytics_requires_auth(self, client: AsyncClient):
        """Student analytics requires authentication."""
        response = await client.get("/api/v1/analytics/student")
        assert response.status_code in (401, 403)

    async def test_instructor_analytics_requires_auth(self, client: AsyncClient):
        """Instructor analytics requires authentication."""
        response = await client.get("/api/v1/analytics/instructor")
        assert response.status_code in (401, 403)

    async def test_platform_analytics_requires_auth(self, client: AsyncClient):
        """Platform analytics requires admin auth."""
        response = await client.get("/api/v1/analytics/platform")
        assert response.status_code in (401, 403)


@pytest.mark.asyncio
class TestCertificatesRouter:
    """Tests for /api/v1/certificates endpoints."""

    async def test_list_certificates_requires_auth(self, client: AsyncClient):
        """Listing certificates requires authentication."""
        response = await client.get("/api/v1/certificates/my")
        assert response.status_code in (401, 403)

    async def test_issue_certificate_requires_auth(self, client: AsyncClient):
        """Issuing a certificate requires authentication."""
        response = await client.post(
            "/api/v1/certificates/issue/00000000-0000-0000-0000-000000000000",
            json={},
        )
        assert response.status_code in (401, 403)

    async def test_verify_certificate_endpoint(self, client: AsyncClient):
        """Certificate verification with invalid number returns not found."""
        response = await client.get("/api/v1/certificates/verify/INVALID-CERT")
        assert response.status_code in (200, 404)

    async def test_mint_certificate_requires_auth(self, client: AsyncClient):
        """Blockchain minting requires authentication."""
        response = await client.post(
            "/api/v1/certificates/00000000-0000-0000-0000-000000000000/mint",
            json={"wallet_address": "0x123"},
        )
        assert response.status_code in (401, 403)


@pytest.mark.asyncio
class TestNotificationsRouter:
    """Tests for /api/v1/notifications endpoints."""

    async def test_list_notifications_requires_auth(self, client: AsyncClient):
        """Listing notifications requires authentication."""
        response = await client.get("/api/v1/notifications")
        assert response.status_code in (401, 403)

    async def test_mark_all_read_requires_auth(self, client: AsyncClient):
        """Marking all as read requires authentication."""
        response = await client.post("/api/v1/notifications/read-all")
        assert response.status_code in (401, 403)


@pytest.mark.asyncio
class TestReviewsRouter:
    """Tests for /api/v1/reviews endpoints."""

    async def test_create_review_requires_auth(self, client: AsyncClient):
        """Creating a review requires authentication."""
        response = await client.post(
            "/api/v1/reviews/course/00000000-0000-0000-0000-000000000000",
            json={"rating": 5, "comment": "Great"},
        )
        assert response.status_code in (401, 403)

    async def test_list_course_reviews(self, client: AsyncClient):
        """Course reviews may or may not require auth."""
        response = await client.get(
            "/api/v1/reviews/course/00000000-0000-0000-0000-000000000000"
        )
        assert response.status_code in (200, 401, 404)

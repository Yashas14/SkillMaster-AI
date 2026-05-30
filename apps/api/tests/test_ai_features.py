# ════════════════════════════════════════════════════════════
# Quiz Router Tests
# ════════════════════════════════════════════════════════════

import pytest
import pytest_asyncio
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock


@pytest.mark.asyncio
class TestQuizRouter:
    """Tests for /api/v1/quizzes endpoints."""

    async def test_generate_quiz_requires_auth(self, client: AsyncClient):
        """Unauthenticated users cannot generate quizzes."""
        response = await client.post(
            "/api/v1/quizzes/generate",
            json={"course_id": "some-id", "num_questions": 5},
        )
        assert response.status_code in (401, 403)

    async def test_list_quiz_attempts_requires_auth(self, client: AsyncClient):
        """Unauthenticated users cannot list quiz attempts."""
        response = await client.get("/api/v1/quizzes/attempts")
        assert response.status_code in (401, 403)

    async def test_get_quiz_not_found(self, client: AsyncClient):
        """Non-existent quiz returns 404."""
        response = await client.get(
            "/api/v1/quizzes/00000000-0000-0000-0000-000000000000"
        )
        assert response.status_code in (401, 404)


@pytest.mark.asyncio
class TestCodeRouter:
    """Tests for /api/v1/code endpoints."""

    async def test_execute_code_requires_auth(self, client: AsyncClient):
        """Unauthenticated users cannot execute code."""
        response = await client.post(
            "/api/v1/code/execute",
            json={"code": "print('hello')", "language": "python"},
        )
        assert response.status_code in (401, 403)

    async def test_code_review_requires_auth(self, client: AsyncClient):
        """Unauthenticated users cannot request code reviews."""
        response = await client.post(
            "/api/v1/code/review",
            json={"code": "x = 1", "language": "python"},
        )
        assert response.status_code in (401, 403)

    async def test_code_explain_requires_auth(self, client: AsyncClient):
        """Unauthenticated users cannot request code explanations."""
        response = await client.post(
            "/api/v1/code/explain",
            json={"code": "x = 1", "language": "python"},
        )
        assert response.status_code in (401, 403)


@pytest.mark.asyncio
class TestLearningPathRouter:
    """Tests for /api/v1/learning-paths endpoints."""

    async def test_list_paths_requires_auth(self, client: AsyncClient):
        """Unauthenticated users cannot list learning paths."""
        response = await client.get("/api/v1/learning-paths")
        assert response.status_code in (401, 403)

    async def test_create_path_requires_auth(self, client: AsyncClient):
        """Unauthenticated users cannot create learning paths."""
        response = await client.post(
            "/api/v1/learning-paths",
            json={
                "goal": "Learn machine learning",
                "current_skills": ["Python"],
                "target_skills": ["TensorFlow"],
                "weekly_hours": 10,
            },
        )
        assert response.status_code in (401, 403)


@pytest.mark.asyncio
class TestSearchRouter:
    """Tests for /api/v1/search endpoints."""

    async def test_semantic_search_requires_auth(self, client: AsyncClient):
        """Unauthenticated users cannot perform semantic search."""
        response = await client.post(
            "/api/v1/search/semantic",
            json={"query": "react hooks"},
        )
        assert response.status_code in (401, 403)

    async def test_course_search_public(self, client: AsyncClient):
        """Course search may be accessible without auth."""
        response = await client.get("/api/v1/search/courses?q=react")
        # Course search could be public or require auth
        assert response.status_code in (200, 401)

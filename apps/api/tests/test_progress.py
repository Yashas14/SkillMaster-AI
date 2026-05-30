# ════════════════════════════════════════════════════════════
# Progress API Tests
# ════════════════════════════════════════════════════════════

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_course_progress_unauthenticated(client: AsyncClient):
    response = await client.get("/api/v1/progress/course/fake-course-id")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_lesson_progress_unauthenticated(client: AsyncClient):
    response = await client.put(
        "/api/v1/progress/lesson/fake-lesson-id",
        json={"status": "completed", "time_spent_seconds": 300},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_lesson_progress_invalid_status(client: AsyncClient, sample_user_data):
    # Register a user
    reg = await client.post("/api/v1/auth/register", json=sample_user_data)
    token = reg.json()["access_token"]

    response = await client.put(
        "/api/v1/progress/lesson/fake-lesson-id",
        json={"status": "invalid_status", "time_spent_seconds": 300},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 422

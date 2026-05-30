# ════════════════════════════════════════════════════════════
# Courses API Tests
# ════════════════════════════════════════════════════════════

import pytest
from httpx import AsyncClient


async def create_instructor(client: AsyncClient) -> dict:
    """Helper to create an instructor and return tokens."""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": f"instructor-{id(client)}@test.com",
            "name": "Test Instructor",
            "password": "InstructorPass123!",
            "role": "instructor",
        },
    )
    return response.json()


@pytest.mark.asyncio
async def test_create_course(client: AsyncClient, sample_course_data):
    instructor = await create_instructor(client)
    token = instructor["access_token"]

    response = await client.post(
        "/api/v1/courses",
        json=sample_course_data,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == sample_course_data["title"]
    assert data["category"] == "programming"
    assert data["difficulty"] == "beginner"
    assert data["status"] == "draft"
    assert "slug" in data


@pytest.mark.asyncio
async def test_list_courses(client: AsyncClient):
    response = await client.get("/api/v1/courses")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "meta" in data
    assert isinstance(data["data"], list)


@pytest.mark.asyncio
async def test_list_courses_with_filters(client: AsyncClient):
    response = await client.get(
        "/api/v1/courses",
        params={"category": "programming", "difficulty": "beginner", "limit": 5},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["meta"]["limit"] == 5


@pytest.mark.asyncio
async def test_create_course_student_forbidden(client: AsyncClient, sample_course_data):
    # Register as student (default role)
    reg = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "student-forbidden@test.com",
            "name": "Student",
            "password": "StudentPass123!",
        },
    )
    token = reg.json()["access_token"]

    response = await client.post(
        "/api/v1/courses",
        json=sample_course_data,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403

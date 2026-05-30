# ════════════════════════════════════════════════════════════
# Extended Courses API Tests
# ════════════════════════════════════════════════════════════

import uuid

import pytest
from httpx import AsyncClient


async def create_instructor_with_course(client: AsyncClient) -> dict:
    """Helper to create an instructor with a published course."""
    resp = await client.post(
        "/api/v1/auth/register",
        json={
            "email": f"instr-{uuid.uuid4().hex[:8]}@test.com",
            "name": "Test Instructor",
            "password": "InstructorPass123!",
            "role": "instructor",
        },
    )
    instructor = resp.json()
    token = instructor["access_token"]

    course_resp = await client.post(
        "/api/v1/courses",
        json={
            "title": f"Course {uuid.uuid4().hex[:8]}",
            "description": "Detailed description of test course",
            "short_description": "Short desc",
            "category": "programming",
            "difficulty": "beginner",
            "tags": ["python", "testing"],
            "learning_outcomes": ["Learn testing"],
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    course = course_resp.json()

    # Publish
    await client.patch(
        f"/api/v1/courses/{course['id']}",
        json={"status": "published"},
        headers={"Authorization": f"Bearer {token}"},
    )

    return {"token": token, "course": course, "instructor": instructor}


@pytest.mark.asyncio
async def test_get_course_by_id(client: AsyncClient):
    """Test getting a single course by ID."""
    data = await create_instructor_with_course(client)
    course_id = data["course"]["id"]

    response = await client.get(f"/api/v1/courses/{course_id}")
    assert response.status_code == 200
    result = response.json()
    assert result["id"] == course_id
    assert result["title"] == data["course"]["title"]


@pytest.mark.asyncio
async def test_get_course_by_slug(client: AsyncClient):
    """Test getting a course by slug."""
    data = await create_instructor_with_course(client)
    slug = data["course"]["slug"]

    response = await client.get(f"/api/v1/courses/slug/{slug}")
    assert response.status_code == 200
    result = response.json()
    assert result["slug"] == slug


@pytest.mark.asyncio
async def test_get_course_not_found(client: AsyncClient):
    """Test 404 for non-existent course."""
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = await client.get(f"/api/v1/courses/{fake_id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_course(client: AsyncClient):
    """Test updating a course."""
    data = await create_instructor_with_course(client)
    course_id = data["course"]["id"]
    token = data["token"]

    response = await client.patch(
        f"/api/v1/courses/{course_id}",
        json={"title": "Updated Title", "description": "Updated description"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Title"


@pytest.mark.asyncio
async def test_update_course_unauthorized(client: AsyncClient):
    """Test that non-owner cannot update a course."""
    data = await create_instructor_with_course(client)
    course_id = data["course"]["id"]

    # Register different instructor
    resp = await client.post(
        "/api/v1/auth/register",
        json={
            "email": f"other-{uuid.uuid4().hex[:8]}@test.com",
            "name": "Other Instructor",
            "password": "OtherPass123!",
            "role": "instructor",
        },
    )
    other_token = resp.json()["access_token"]

    response = await client.patch(
        f"/api/v1/courses/{course_id}",
        json={"title": "Hacked"},
        headers={"Authorization": f"Bearer {other_token}"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_delete_course(client: AsyncClient):
    """Test soft-deleting a course."""
    data = await create_instructor_with_course(client)
    course_id = data["course"]["id"]
    token = data["token"]

    response = await client.delete(
        f"/api/v1/courses/{course_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code in (200, 204)

    # Verify course is no longer accessible
    get_resp = await client.get(f"/api/v1/courses/{course_id}")
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_list_courses_pagination(client: AsyncClient):
    """Test course listing with pagination."""
    response = await client.get("/api/v1/courses", params={"page": 1, "limit": 5})
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "meta" in data
    assert data["meta"]["page"] == 1
    assert data["meta"]["limit"] == 5


@pytest.mark.asyncio
async def test_list_courses_category_filter(client: AsyncClient):
    """Test filtering courses by category."""
    data = await create_instructor_with_course(client)

    response = await client.get(
        "/api/v1/courses", params={"category": "programming"}
    )
    assert response.status_code == 200
    result = response.json()
    for course in result["data"]:
        assert course["category"] == "programming"

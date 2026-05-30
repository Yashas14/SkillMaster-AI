# ════════════════════════════════════════════════════════════
# Enrollments API Tests
# ════════════════════════════════════════════════════════════

import pytest
from httpx import AsyncClient


async def setup_course_and_users(client: AsyncClient) -> dict:
    """Helper to create instructor, course, and student."""
    # Create instructor
    instructor_resp = await client.post(
        "/api/v1/auth/register",
        json={
            "email": f"enroll-instructor-{id(client)}@test.com",
            "name": "Instructor",
            "password": "InstructorPass123!",
            "role": "instructor",
        },
    )
    instructor = instructor_resp.json()

    # Create course
    course_resp = await client.post(
        "/api/v1/courses",
        json={
            "title": f"Enrollment Test Course {id(client)}",
            "description": "Test course for enrollment testing",
            "short_description": "Enrollment test",
            "category": "programming",
            "difficulty": "beginner",
            "tags": ["test"],
        },
        headers={"Authorization": f"Bearer {instructor['access_token']}"},
    )
    course = course_resp.json()

    # Publish the course so enrollment works
    await client.patch(
        f"/api/v1/courses/{course['id']}",
        json={"status": "published"},
        headers={"Authorization": f"Bearer {instructor['access_token']}"},
    )

    # Create student
    student_resp = await client.post(
        "/api/v1/auth/register",
        json={
            "email": f"enroll-student-{id(client)}@test.com",
            "name": "Student",
            "password": "StudentPass123!",
        },
    )
    student = student_resp.json()

    return {"instructor": instructor, "course": course, "student": student}


@pytest.mark.asyncio
async def test_enroll_in_course(client: AsyncClient):
    setup = await setup_course_and_users(client)
    token = setup["student"]["access_token"]
    course_id = setup["course"]["id"]

    response = await client.post(
        "/api/v1/enrollments",
        json={"course_id": course_id},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["course_id"] == course_id
    assert data["status"] == "active"


@pytest.mark.asyncio
async def test_list_my_enrollments(client: AsyncClient):
    setup = await setup_course_and_users(client)
    token = setup["student"]["access_token"]
    course_id = setup["course"]["id"]

    # Enroll
    await client.post(
        "/api/v1/enrollments",
        json={"course_id": course_id},
        headers={"Authorization": f"Bearer {token}"},
    )

    # List
    response = await client.get(
        "/api/v1/enrollments",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["meta"]["total"] >= 1


@pytest.mark.asyncio
async def test_enroll_unauthenticated(client: AsyncClient):
    response = await client.post("/api/v1/enrollments", json={"course_id": "fake-id"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_duplicate_enrollment(client: AsyncClient):
    setup = await setup_course_and_users(client)
    token = setup["student"]["access_token"]
    course_id = setup["course"]["id"]

    # First enrollment
    await client.post(
        "/api/v1/enrollments",
        json={"course_id": course_id},
        headers={"Authorization": f"Bearer {token}"},
    )

    # Duplicate
    response = await client.post(
        "/api/v1/enrollments",
        json={"course_id": course_id},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 409

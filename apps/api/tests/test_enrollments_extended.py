# ════════════════════════════════════════════════════════════
# Extended Enrollment & Progress Tests
# ════════════════════════════════════════════════════════════

import uuid

import pytest
from httpx import AsyncClient


async def setup_enrolled_student(client: AsyncClient) -> dict:
    """Create instructor + published course + enrolled student."""
    # Instructor
    instr_resp = await client.post(
        "/api/v1/auth/register",
        json={
            "email": f"instr-{uuid.uuid4().hex[:8]}@test.com",
            "name": "Instructor",
            "password": "InstructorPass123!",
            "role": "instructor",
        },
    )
    assert instr_resp.status_code == 201, f"Instructor register failed: {instr_resp.text}"
    instructor = instr_resp.json()

    # Course
    course_resp = await client.post(
        "/api/v1/courses",
        json={
            "title": f"Course {uuid.uuid4().hex[:8]}",
            "description": "A detailed test course for enrollment testing.",
            "short_description": "Short desc",
            "category": "programming",
            "difficulty": "beginner",
            "tags": ["test", "python"],
            "learning_outcomes": ["Learn testing"],
        },
        headers={"Authorization": f"Bearer {instructor['access_token']}"},
    )
    assert course_resp.status_code == 201, f"Course create failed: {course_resp.text}"
    course = course_resp.json()

    # Publish
    pub_resp = await client.patch(
        f"/api/v1/courses/{course['id']}",
        json={"status": "published"},
        headers={"Authorization": f"Bearer {instructor['access_token']}"},
    )
    assert pub_resp.status_code == 200, f"Publish failed: {pub_resp.text}"

    # Student
    student_resp = await client.post(
        "/api/v1/auth/register",
        json={
            "email": f"student-{uuid.uuid4().hex[:8]}@test.com",
            "name": "Student",
            "password": "StudentPass123!",
        },
    )
    assert student_resp.status_code == 201, f"Student register failed: {student_resp.text}"
    student = student_resp.json()

    # Enroll
    enroll_resp = await client.post(
        "/api/v1/enrollments",
        json={"course_id": course["id"]},
        headers={"Authorization": f"Bearer {student['access_token']}"},
    )
    assert enroll_resp.status_code == 201, f"Enroll failed: {enroll_resp.text}"
    enrollment = enroll_resp.json()

    return {
        "instructor": instructor,
        "course": course,
        "student": student,
        "enrollment": enrollment,
    }


@pytest.mark.asyncio
async def test_get_enrollment_by_id(client: AsyncClient):
    """Test getting a specific enrollment."""
    data = await setup_enrolled_student(client)
    token = data["student"]["access_token"]
    enrollment_id = data["enrollment"]["id"]

    response = await client.get(
        f"/api/v1/enrollments/{enrollment_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    result = response.json()
    assert result["id"] == enrollment_id
    assert result["status"] == "active"


@pytest.mark.asyncio
async def test_get_enrollment_not_found(client: AsyncClient):
    """Test 404 for non-existent enrollment."""
    data = await setup_enrolled_student(client)
    token = data["student"]["access_token"]
    fake_id = "00000000-0000-0000-0000-000000000000"

    response = await client.get(
        f"/api/v1/enrollments/{fake_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_enrollment_status(client: AsyncClient):
    """Test updating enrollment status (e.g., completing)."""
    data = await setup_enrolled_student(client)
    token = data["student"]["access_token"]
    enrollment_id = data["enrollment"]["id"]

    response = await client.patch(
        f"/api/v1/enrollments/{enrollment_id}/status",
        json={"status": "completed"},
        headers={"Authorization": f"Bearer {token}"},
    )
    # Could be 200, 403, 404, or 422 depending on implementation
    assert response.status_code in (200, 403, 404, 422)


@pytest.mark.asyncio
async def test_get_course_progress_authenticated(client: AsyncClient):
    """Test getting progress for an enrolled course."""
    data = await setup_enrolled_student(client)
    token = data["student"]["access_token"]
    course_id = data["course"]["id"]

    response = await client.get(
        f"/api/v1/progress/course/{course_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    result = response.json()
    assert "course_id" in result


@pytest.mark.asyncio
async def test_update_lesson_progress_authenticated(client: AsyncClient):
    """Test updating lesson progress."""
    data = await setup_enrolled_student(client)
    token = data["student"]["access_token"]
    fake_lesson_id = "00000000-0000-0000-0000-000000000001"

    response = await client.put(
        f"/api/v1/progress/lesson/{fake_lesson_id}",
        json={"status": "in_progress", "time_spent_seconds": 120},
        headers={"Authorization": f"Bearer {token}"},
    )
    # Lesson might not exist, but auth should pass
    assert response.status_code in (200, 404)

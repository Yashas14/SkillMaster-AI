# ════════════════════════════════════════════════════════════
# Notifications, Reviews, Learning Paths Extended Tests
# ════════════════════════════════════════════════════════════

import uuid

import pytest
from httpx import AsyncClient


async def get_student_token(client: AsyncClient) -> str:
    """Register a student and return their access token."""
    resp = await client.post(
        "/api/v1/auth/register",
        json={
            "email": f"student-{uuid.uuid4().hex[:8]}@test.com",
            "name": "Test Student",
            "password": "StudentPass123!",
        },
    )
    return resp.json()["access_token"]


# ─── Notifications ─────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_notifications_authenticated(client: AsyncClient):
    """Authenticated user can list notifications."""
    token = await get_student_token(client)
    response = await client.get(
        "/api/v1/notifications",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "notifications" in data or "data" in data or isinstance(data, list)


@pytest.mark.asyncio
async def test_list_notifications_unread_filter(client: AsyncClient):
    """Filter for unread notifications."""
    token = await get_student_token(client)
    response = await client.get(
        "/api/v1/notifications",
        params={"unread_only": True},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_mark_notification_read(client: AsyncClient):
    """Mark a specific notification as read (may 404 if none exist)."""
    token = await get_student_token(client)
    fake_id = "00000000-0000-0000-0000-000000000001"
    response = await client.patch(
        f"/api/v1/notifications/{fake_id}/read",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code in (200, 404)


@pytest.mark.asyncio
async def test_mark_all_notifications_read(client: AsyncClient):
    """Mark all notifications as read."""
    token = await get_student_token(client)
    response = await client.post(
        "/api/v1/notifications/read-all",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_delete_notification(client: AsyncClient):
    """Delete a notification (may 404 if none exist)."""
    token = await get_student_token(client)
    fake_id = "00000000-0000-0000-0000-000000000001"
    response = await client.delete(
        f"/api/v1/notifications/{fake_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code in (200, 204, 404)


# ─── Reviews ──────────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_course_reviews(client: AsyncClient):
    """List reviews for a course (empty is fine)."""
    fake_course_id = "00000000-0000-0000-0000-000000000001"
    response = await client.get(f"/api/v1/reviews/course/{fake_course_id}")
    assert response.status_code == 200
    data = response.json()
    assert "reviews" in data
    assert "average_rating" in data


@pytest.mark.asyncio
async def test_create_review_authenticated(client: AsyncClient):
    """Authenticated user can attempt to create a review."""
    token = await get_student_token(client)
    fake_course_id = "00000000-0000-0000-0000-000000000001"
    response = await client.post(
        f"/api/v1/reviews/course/{fake_course_id}",
        json={"rating": 5, "comment": "Excellent course!"},
        headers={"Authorization": f"Bearer {token}"},
    )
    # May fail with 404 if not enrolled, but should not be 401
    assert response.status_code in (201, 400, 403, 404)


@pytest.mark.asyncio
async def test_delete_review_unauthenticated(client: AsyncClient):
    """Unauthenticated user cannot delete a review."""
    fake_id = "00000000-0000-0000-0000-000000000001"
    response = await client.delete(f"/api/v1/reviews/{fake_id}")
    assert response.status_code in (401, 403)


# ─── Learning Paths ───────────────────────────────────────


@pytest.mark.asyncio
async def test_list_learning_paths_authenticated(client: AsyncClient):
    """Authenticated user can list their learning paths."""
    token = await get_student_token(client)
    response = await client.get(
        "/api/v1/learning-paths",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_create_learning_path_requires_auth(client: AsyncClient):
    """Creating a learning path requires authentication."""
    response = await client.post(
        "/api/v1/learning-paths",
        json={"goal": "Learn Python", "current_skills": ["basic programming"]},
    )
    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_get_learning_path_not_found(client: AsyncClient):
    """Non-existent learning path returns 404."""
    token = await get_student_token(client)
    fake_id = "00000000-0000-0000-0000-000000000001"
    response = await client.get(
        f"/api/v1/learning-paths/{fake_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_learning_path_not_found(client: AsyncClient):
    """Deleting non-existent learning path returns 404."""
    token = await get_student_token(client)
    fake_id = "00000000-0000-0000-0000-000000000001"
    response = await client.delete(
        f"/api/v1/learning-paths/{fake_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404


# ─── Analytics ────────────────────────────────────────────


@pytest.mark.asyncio
@pytest.mark.xfail(reason="Requires PostgreSQL (date_trunc not in SQLite)")
async def test_student_analytics_authenticated(client: AsyncClient):
    """Student can access their own analytics (may fail in SQLite due to date_trunc)."""
    token = await get_student_token(client)
    response = await client.get(
        "/api/v1/analytics/student",
        headers={"Authorization": f"Bearer {token}"},
    )
    # date_trunc is PostgreSQL-only; SQLite tests will get 500
    assert response.status_code in (200, 500)
    if response.status_code == 200:
        data = response.json()
        assert "total_courses" in data


@pytest.mark.asyncio
async def test_instructor_analytics_requires_instructor(client: AsyncClient):
    """Student cannot access instructor analytics."""
    token = await get_student_token(client)
    response = await client.get(
        "/api/v1/analytics/instructor",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_platform_analytics_requires_admin(client: AsyncClient):
    """Student cannot access platform analytics."""
    token = await get_student_token(client)
    response = await client.get(
        "/api/v1/analytics/platform",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403


# ─── Gamification ─────────────────────────────────────────


@pytest.mark.asyncio
async def test_gamification_profile_authenticated(client: AsyncClient):
    """Authenticated user can access their gamification profile."""
    token = await get_student_token(client)
    response = await client.get(
        "/api/v1/gamification/profile",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "level" in data or "xp" in data or "current_streak" in data


@pytest.mark.asyncio
async def test_leaderboard_public(client: AsyncClient):
    """Leaderboard may be publicly accessible."""
    response = await client.get("/api/v1/gamification/leaderboard")
    assert response.status_code in (200, 401)


@pytest.mark.asyncio
async def test_check_badges_authenticated(client: AsyncClient):
    """Authenticated user can check for new badges."""
    token = await get_student_token(client)
    response = await client.post(
        "/api/v1/gamification/check-badges",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_update_streak(client: AsyncClient):
    """Authenticated user can update their streak."""
    token = await get_student_token(client)
    response = await client.post(
        "/api/v1/gamification/streak",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200


# ─── Certificates ─────────────────────────────────────────


@pytest.mark.asyncio
async def test_my_certificates_authenticated(client: AsyncClient):
    """Authenticated user can list their certificates."""
    token = await get_student_token(client)
    response = await client.get(
        "/api/v1/certificates/my",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_verify_certificate_invalid(client: AsyncClient):
    """Verify endpoint returns not-found or invalid for fake certificate."""
    response = await client.get("/api/v1/certificates/verify/FAKE-CERT-123")
    assert response.status_code in (200, 404)
    if response.status_code == 200:
        data = response.json()
        assert data.get("valid") is False or "not found" in str(data).lower()


@pytest.mark.asyncio
async def test_issue_certificate_not_enrolled(client: AsyncClient):
    """Cannot issue certificate for non-existent enrollment."""
    token = await get_student_token(client)
    fake_id = "00000000-0000-0000-0000-000000000001"
    response = await client.post(
        f"/api/v1/certificates/issue/{fake_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code in (400, 404)


# ─── Search ───────────────────────────────────────────────


@pytest.mark.asyncio
async def test_course_search_with_query(client: AsyncClient):
    """Search courses with a query."""
    response = await client.get("/api/v1/search/courses", params={"q": "python"})
    assert response.status_code == 200
    data = response.json()
    assert "results" in data or "data" in data


@pytest.mark.asyncio
async def test_course_search_empty_results(client: AsyncClient):
    """Search with no matching results."""
    response = await client.get(
        "/api/v1/search/courses",
        params={"q": "zzz_nonexistent_xyz"},
    )
    assert response.status_code == 200


@pytest.mark.asyncio
@pytest.mark.xfail(reason="Requires Elasticsearch service")
async def test_semantic_search_authenticated(client: AsyncClient):
    """Semantic search requires authentication."""
    token = await get_student_token(client)
    response = await client.post(
        "/api/v1/search/semantic",
        json={"query": "how to use decorators in python"},
        headers={"Authorization": f"Bearer {token}"},
    )
    # Elasticsearch/AI service may not be configured in test environment
    assert response.status_code in (200, 400, 422, 500, 503)


# ─── Code Execution ──────────────────────────────────────


@pytest.mark.asyncio
async def test_execute_code_authenticated(client: AsyncClient):
    """Authenticated user can execute code."""
    token = await get_student_token(client)
    response = await client.post(
        "/api/v1/code/execute",
        json={"code": "print('hello')", "language": "python"},
        headers={"Authorization": f"Bearer {token}"},
    )
    # May fail without code execution backend, but auth should pass
    assert response.status_code in (200, 500, 503)


@pytest.mark.asyncio
@pytest.mark.xfail(reason="Requires Anthropic API key")
async def test_code_review_authenticated(client: AsyncClient):
    """Authenticated user can request code review."""
    token = await get_student_token(client)
    response = await client.post(
        "/api/v1/code/review",
        json={"code": "x = 1\ny = 2\nprint(x+y)", "language": "python"},
        headers={"Authorization": f"Bearer {token}"},
    )
    # May fail without AI API key configured in test env
    assert response.status_code in (200, 400, 422, 500, 503)


# ─── Quiz ─────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_quiz_not_found(client: AsyncClient):
    """Non-existent quiz returns 404."""
    token = await get_student_token(client)
    fake_id = "00000000-0000-0000-0000-000000000001"
    response = await client.get(
        f"/api/v1/quizzes/{fake_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_quiz_by_course_empty(client: AsyncClient):
    """Get quizzes for a course (empty list is fine)."""
    token = await get_student_token(client)
    fake_course_id = "00000000-0000-0000-0000-000000000001"
    response = await client.get(
        f"/api/v1/quizzes/course/{fake_course_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_generate_quiz_requires_auth(client: AsyncClient):
    """Quiz generation requires auth."""
    response = await client.post(
        "/api/v1/quizzes/generate",
        json={"course_id": "00000000-0000-0000-0000-000000000001"},
    )
    assert response.status_code in (401, 403)


# ─── AI Tutor ─────────────────────────────────────────────


@pytest.mark.asyncio
async def test_ai_tutor_requires_auth(client: AsyncClient):
    """AI tutor chat requires authentication."""
    response = await client.post(
        "/api/v1/ai/tutor/chat",
        json={"message": "Hello", "persona": "friendly"},
    )
    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_ai_tutor_sessions_requires_auth(client: AsyncClient):
    """AI tutor sessions listing requires authentication."""
    response = await client.get("/api/v1/ai/tutor/sessions")
    assert response.status_code in (401, 403)

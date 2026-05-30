# ════════════════════════════════════════════════════════════
# Auth API Tests
# ════════════════════════════════════════════════════════════

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "skillmaster-api"


@pytest.mark.asyncio
async def test_register_success(client: AsyncClient, sample_user_data):
    response = await client.post("/api/v1/auth/register", json=sample_user_data)
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["user"]["email"] == sample_user_data["email"]
    assert data["user"]["name"] == sample_user_data["name"]
    assert data["user"]["role"] == "student"


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient, sample_user_data):
    # First registration
    await client.post("/api/v1/auth/register", json=sample_user_data)
    # Duplicate
    response = await client.post("/api/v1/auth/register", json=sample_user_data)
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_register_invalid_email(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "invalid", "name": "Test", "password": "TestPass123!"},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_short_password(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "name": "Test", "password": "short"},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, sample_user_data):
    # Register first
    await client.post("/api/v1/auth/register", json=sample_user_data)

    # Login
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": sample_user_data["email"], "password": sample_user_data["password"]},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == sample_user_data["email"]


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient, sample_user_data):
    await client.post("/api/v1/auth/register", json=sample_user_data)

    response = await client.post(
        "/api/v1/auth/login",
        json={"email": sample_user_data["email"], "password": "WrongPass123!"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_me_authenticated(client: AsyncClient, sample_user_data):
    # Register
    reg_response = await client.post("/api/v1/auth/register", json=sample_user_data)
    token = reg_response.json()["access_token"]

    # Get me
    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["email"] == sample_user_data["email"]


@pytest.mark.asyncio
async def test_get_me_unauthenticated(client: AsyncClient):
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401

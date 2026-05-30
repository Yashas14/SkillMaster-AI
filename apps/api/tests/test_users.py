# ════════════════════════════════════════════════════════════
# Users API Tests
# ════════════════════════════════════════════════════════════

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import create_access_token, hash_password
from app.models import User


async def create_admin_directly(test_db: AsyncSession) -> tuple[User, str]:
    """Create an admin user directly in DB (admins can't self-register)."""
    user = User(
        email=f"admin-{uuid.uuid4().hex[:8]}@test.com",
        name="Admin User",
        password_hash=hash_password("AdminPass123!"),
        role="admin",
        provider="email",
        preferences={},
        profile={},
    )
    test_db.add(user)
    await test_db.flush()
    token = create_access_token(user.id, user.role, user.email)
    return user, token


@pytest.mark.asyncio
async def test_list_users_as_admin(client: AsyncClient, test_db: AsyncSession):
    _, token = await create_admin_directly(test_db)

    response = await client.get(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert isinstance(data["data"], list)


@pytest.mark.asyncio
async def test_list_users_forbidden_for_student(client: AsyncClient, sample_user_data):
    reg = await client.post("/api/v1/auth/register", json=sample_user_data)
    token = reg.json()["access_token"]

    response = await client.get(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_user_by_id(client: AsyncClient, test_db: AsyncSession):
    user, token = await create_admin_directly(test_db)

    response = await client.get(
        f"/api/v1/users/{user.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["id"] == str(user.id)


@pytest.mark.asyncio
async def test_update_user_profile(client: AsyncClient, sample_user_data):
    reg = await client.post("/api/v1/auth/register", json=sample_user_data)
    token = reg.json()["access_token"]
    user_id = reg.json()["user"]["id"]

    response = await client.patch(
        f"/api/v1/users/{user_id}",
        json={"name": "Updated Name", "bio": "Updated bio text"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Name"


@pytest.mark.asyncio
async def test_soft_delete_user(client: AsyncClient, test_db: AsyncSession):
    _, token = await create_admin_directly(test_db)

    # Create a user to delete
    target = await client.post(
        "/api/v1/auth/register",
        json={
            "email": f"delete-target-{uuid.uuid4().hex[:8]}@test.com",
            "name": "Delete Target",
            "password": "TargetPass123!",
        },
    )
    target_id = target.json()["user"]["id"]

    response = await client.delete(
        f"/api/v1/users/{target_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code in (200, 204)

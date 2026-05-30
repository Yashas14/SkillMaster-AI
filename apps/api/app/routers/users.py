# ════════════════════════════════════════════════════════════
# Users Router
# ════════════════════════════════════════════════════════════

from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user, require_role
from app.database import get_db
from app.models import User
from app.schemas import (
    PaginatedResponse,
    PaginationMeta,
    UpdateUserRequest,
    UserDetailResponse,
    UserResponse,
)

router = APIRouter()


@router.get("/me", response_model=UserDetailResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
):
    """Get the currently authenticated user's profile."""
    return UserDetailResponse.model_validate(current_user)


@router.get("", response_model=PaginatedResponse)
async def list_users(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    role: str | None = None,
    search: str | None = None,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(require_role("admin", "super_admin")),
):
    """List all users (admin only)."""
    query = select(User).where(User.deleted_at.is_(None))

    if role:
        query = query.where(User.role == role)
    if search:
        query = query.where(User.name.ilike(f"%{search}%") | User.email.ilike(f"%{search}%"))

    # Count
    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar() or 0

    # Paginate
    query = query.offset((page - 1) * limit).limit(limit).order_by(User.created_at.desc())
    result = await db.execute(query)
    users = result.scalars().all()

    total_pages = (total + limit - 1) // limit

    return PaginatedResponse(
        data=[UserResponse.model_validate(u) for u in users],
        meta=PaginationMeta(
            total=total,
            page=page,
            limit=limit,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1,
        ),
    )


@router.get("/{user_id}", response_model=UserDetailResponse)
async def get_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    """Get a user by ID."""
    result = await db.execute(
        select(User).where(User.id == user_id, User.deleted_at.is_(None))
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return UserDetailResponse.model_validate(user)


@router.patch("/{user_id}", response_model=UserDetailResponse)
async def update_user(
    user_id: UUID,
    data: UpdateUserRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a user profile."""
    if current_user.id != user_id and current_user.role not in ("admin", "super_admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot update another user")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    await db.flush()
    return UserDetailResponse.model_validate(user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Soft-delete a user."""
    if current_user.id != user_id and current_user.role not in ("admin", "super_admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot delete another user")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.deleted_at = datetime.now(UTC)
    user.is_active = False
    await db.flush()

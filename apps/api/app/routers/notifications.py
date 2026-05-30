# ════════════════════════════════════════════════════════════
# Notifications Router
# ════════════════════════════════════════════════════════════

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.database import get_db
from app.models import Notification, User
from app.schemas import NotificationResponse

router = APIRouter()


@router.get("")
async def list_notifications(
    unread_only: bool = False,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """List notifications for the current user."""
    query = select(Notification).where(Notification.user_id == user.id)

    if unread_only:
        query = query.where(Notification.is_read.is_(False))

    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar() or 0

    query = query.offset((page - 1) * limit).limit(limit).order_by(Notification.created_at.desc())
    result = await db.execute(query)
    notifications = result.scalars().all()

    # Unread count
    unread_result = await db.execute(
        select(func.count())
        .select_from(Notification)
        .where(Notification.user_id == user.id, Notification.is_read.is_(False))
    )
    unread_count = unread_result.scalar() or 0

    return {
        "notifications": [NotificationResponse.model_validate(n) for n in notifications],
        "total": total,
        "unread_count": unread_count,
    }


@router.patch("/{notification_id}/read")
async def mark_as_read(
    notification_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Mark a notification as read."""
    result = await db.execute(
        select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == user.id,
        )
    )
    notification = result.scalar_one_or_none()

    if not notification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")

    notification.is_read = True
    await db.flush()
    return NotificationResponse.model_validate(notification)


@router.post("/read-all")
async def mark_all_read(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Mark all notifications as read."""
    await db.execute(
        update(Notification)
        .where(Notification.user_id == user.id, Notification.is_read.is_(False))
        .values(is_read=True)
    )
    await db.flush()
    return {"message": "All notifications marked as read"}


@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(
    notification_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Delete a notification."""
    result = await db.execute(
        select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == user.id,
        )
    )
    notification = result.scalar_one_or_none()
    if not notification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")

    await db.delete(notification)
    await db.flush()

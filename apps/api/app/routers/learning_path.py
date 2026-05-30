# ════════════════════════════════════════════════════════════
# Learning Path Router
# ════════════════════════════════════════════════════════════

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.database import get_db
from app.models import LearningPath, User
from app.schemas import CreateLearningPathRequest, UpdatePathItemRequest
from app.services.learning_path import learning_path_engine

router = APIRouter()


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_learning_path(
    data: CreateLearningPathRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Generate a personalized learning path using AI."""
    result = await learning_path_engine.generate_path(
        user_id=str(user.id),
        goal=data.goal,
        db=db,
        current_skills=data.current_skills,
        target_skills=data.target_skills,
        weekly_hours=data.weekly_hours,
    )
    return result


@router.get("")
async def list_learning_paths(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """List all learning paths for the current user."""
    result = await db.execute(
        select(LearningPath)
        .where(LearningPath.user_id == user.id)
        .order_by(LearningPath.created_at.desc())
    )
    paths = result.scalars().all()

    return [
        {
            "id": str(p.id),
            "title": p.title,
            "goal": p.goal,
            "status": p.status,
            "progress": p.progress,
            "estimated_weeks": p.estimated_duration_weeks,
            "weekly_hours": p.weekly_hours,
            "total_items": len(p.items),
            "created_at": p.created_at.isoformat(),
        }
        for p in paths
    ]


@router.get("/recommendations")
async def get_recommendations(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get next recommended action based on active learning path."""
    return await learning_path_engine.get_next_recommendation(str(user.id), db)


@router.get("/{path_id}")
async def get_learning_path(
    path_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get detailed learning path with items."""
    result = await db.execute(
        select(LearningPath).where(
            LearningPath.id == path_id,
            LearningPath.user_id == user.id,
        )
    )
    path = result.scalar_one_or_none()

    if not path:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Learning path not found")

    return {
        "id": str(path.id),
        "title": path.title,
        "description": path.description,
        "goal": path.goal,
        "status": path.status,
        "progress": path.progress,
        "estimated_weeks": path.estimated_duration_weeks,
        "weekly_hours": path.weekly_hours,
        "metadata": path.extra_data,
        "items": [
            {
                "id": str(i.id),
                "order": i.order,
                "type": i.item_type,
                "title": i.title,
                "description": i.description,
                "status": i.status,
                "estimated_hours": i.estimated_hours,
                "required": i.is_required,
                "course_id": str(i.course_id) if i.course_id else None,
                "completed_at": i.completed_at.isoformat() if i.completed_at else None,
            }
            for i in path.items
        ],
        "created_at": path.created_at.isoformat(),
    }


@router.patch("/{path_id}/items/{item_id}")
async def update_path_item(
    path_id: UUID,
    item_id: UUID,
    data: UpdatePathItemRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Update a learning path item's status."""
    # Verify ownership
    path_result = await db.execute(
        select(LearningPath).where(
            LearningPath.id == path_id,
            LearningPath.user_id == user.id,
        )
    )
    if not path_result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Learning path not found")

    result = await learning_path_engine.update_progress(
        user_id=str(user.id),
        path_id=str(path_id),
        item_id=str(item_id),
        status=data.status,
        db=db,
    )
    return result


@router.delete("/{path_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_learning_path(
    path_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Delete a learning path."""
    result = await db.execute(
        select(LearningPath).where(
            LearningPath.id == path_id,
            LearningPath.user_id == user.id,
        )
    )
    path = result.scalar_one_or_none()
    if not path:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Learning path not found")

    await db.delete(path)
    await db.flush()

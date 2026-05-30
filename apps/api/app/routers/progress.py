# ════════════════════════════════════════════════════════════
# Progress Router
# ════════════════════════════════════════════════════════════

from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.database import get_db
from app.models import Enrollment, Lesson, LessonProgress, User
from app.schemas import ProgressResponse, UpdateProgressRequest

router = APIRouter()


@router.get("/course/{course_id}")
async def get_course_progress(
    course_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get all lesson progress for a course."""
    result = await db.execute(
        select(LessonProgress).where(
            LessonProgress.user_id == user.id,
            LessonProgress.course_id == course_id,
        )
    )
    progress_records = result.scalars().all()

    return {
        "course_id": str(course_id),
        "user_id": str(user.id),
        "lessons": [ProgressResponse.model_validate(p) for p in progress_records],
        "total_completed": sum(1 for p in progress_records if p.status == "completed"),
        "total_in_progress": sum(1 for p in progress_records if p.status == "in_progress"),
    }


@router.put("/lesson/{lesson_id}", response_model=ProgressResponse)
async def update_lesson_progress(
    lesson_id: UUID,
    data: UpdateProgressRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Update or create lesson progress."""
    # Get the lesson to find course/module info
    lesson_result = await db.execute(select(Lesson).where(Lesson.id == lesson_id))
    lesson = lesson_result.scalar_one_or_none()

    if not lesson:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found")

    # Check enrollment
    enrollment_result = await db.execute(
        select(Enrollment).where(
            Enrollment.user_id == user.id,
            Enrollment.course_id == lesson.course_id,
            Enrollment.status.in_(["active", "completed"]),
        )
    )
    enrollment = enrollment_result.scalar_one_or_none()

    if not enrollment:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enrolled in this course")

    # Get or create progress
    result = await db.execute(
        select(LessonProgress).where(
            LessonProgress.user_id == user.id,
            LessonProgress.lesson_id == lesson_id,
        )
    )
    progress = result.scalar_one_or_none()

    if not progress:
        progress = LessonProgress(
            user_id=user.id,
            lesson_id=lesson_id,
            course_id=lesson.course_id,
            module_id=lesson.module_id,
        )
        db.add(progress)

    # Apply updates
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(progress, field, value)

    # Mark as completed if progress is 100%
    if progress.progress_percent >= 100 and progress.status != "completed":
        progress.status = "completed"
        progress.completed_at = datetime.now(UTC)

    elif progress.progress_percent > 0 and progress.status == "not_started":
        progress.status = "in_progress"

    # Update enrollment last accessed
    enrollment.last_accessed_at = datetime.now(UTC)

    # Recalculate course progress
    all_lessons_result = await db.execute(
        select(Lesson).where(Lesson.course_id == lesson.course_id, Lesson.is_required.is_(True))
    )
    total_required = len(all_lessons_result.scalars().all())

    completed_result = await db.execute(
        select(LessonProgress).where(
            LessonProgress.user_id == user.id,
            LessonProgress.course_id == lesson.course_id,
            LessonProgress.status == "completed",
        )
    )
    total_completed = len(completed_result.scalars().all())

    if total_required > 0:
        enrollment.progress = round((total_completed / total_required) * 100, 1)

        if enrollment.progress >= 100:
            enrollment.status = "completed"
            enrollment.completed_at = datetime.now(UTC)

    await db.flush()
    return ProgressResponse.model_validate(progress)

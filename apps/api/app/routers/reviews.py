# ════════════════════════════════════════════════════════════
# Course Reviews Router
# ════════════════════════════════════════════════════════════

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user, get_optional_user
from app.database import get_db
from app.models import Course, CourseReview, Enrollment, User
from app.schemas import CreateReviewRequest, ReviewResponse

router = APIRouter()


@router.get("/course/{course_id}")
async def list_course_reviews(
    course_id: UUID,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    _user: User | None = Depends(get_optional_user),
):
    """List reviews for a course."""
    query = select(CourseReview).where(CourseReview.course_id == course_id)

    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar() or 0

    query = query.offset((page - 1) * limit).limit(limit).order_by(CourseReview.created_at.desc())
    result = await db.execute(query)
    reviews = result.scalars().all()

    # Average rating
    avg_result = await db.execute(
        select(func.avg(CourseReview.rating)).where(CourseReview.course_id == course_id)
    )
    avg_rating = round(float(avg_result.scalar() or 0), 2)

    return {
        "reviews": [ReviewResponse.model_validate(r) for r in reviews],
        "total": total,
        "average_rating": avg_rating,
    }


@router.post("/course/{course_id}", status_code=status.HTTP_201_CREATED)
async def create_review(
    course_id: UUID,
    data: CreateReviewRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Create a review for a course (must be enrolled)."""
    # Check enrollment
    enroll_result = await db.execute(
        select(Enrollment).where(
            Enrollment.user_id == user.id,
            Enrollment.course_id == course_id,
        )
    )
    enrollment = enroll_result.scalar_one_or_none()
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Must be enrolled in the course to review it",
        )

    # Check existing review
    existing = await db.execute(
        select(CourseReview).where(
            CourseReview.user_id == user.id,
            CourseReview.course_id == course_id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You have already reviewed this course",
        )

    review = CourseReview(
        course_id=course_id,
        user_id=user.id,
        rating=data.rating,
        title=data.title,
        content=data.content,
        is_verified=enrollment.status == "completed",
    )
    db.add(review)

    # Update course rating
    course_result = await db.execute(select(Course).where(Course.id == course_id))
    course = course_result.scalar_one()

    all_ratings = await db.execute(
        select(func.avg(CourseReview.rating), func.count())
        .where(CourseReview.course_id == course_id)
    )
    row = all_ratings.fetchone()
    avg = float(row[0]) if row[0] is not None else 0.0
    count = int(row[1]) if row[1] is not None else 0
    course.rating = round(avg, 2)
    course.total_ratings = count

    await db.flush()
    return ReviewResponse.model_validate(review)


@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(
    review_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Delete your own review."""
    result = await db.execute(
        select(CourseReview).where(
            CourseReview.id == review_id,
            CourseReview.user_id == user.id,
        )
    )
    review = result.scalar_one_or_none()
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")

    await db.delete(review)
    await db.flush()

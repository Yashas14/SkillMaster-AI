# ════════════════════════════════════════════════════════════
# Enrollments Router
# ════════════════════════════════════════════════════════════

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.database import get_db
from app.models import Course, Enrollment, User
from app.schemas import (
    CreateEnrollmentRequest,
    EnrollmentResponse,
    PaginatedResponse,
    PaginationMeta,
)

router = APIRouter()


@router.get("", response_model=PaginatedResponse)
async def list_my_enrollments(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status_filter: str | None = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """List current user's enrollments."""
    query = select(Enrollment).where(Enrollment.user_id == user.id)

    if status_filter:
        query = query.where(Enrollment.status == status_filter)

    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar() or 0

    query = query.offset((page - 1) * limit).limit(limit).order_by(Enrollment.enrolled_at.desc())
    result = await db.execute(query)
    enrollments = result.scalars().all()

    total_pages = max(1, (total + limit - 1) // limit)

    return PaginatedResponse(
        data=[EnrollmentResponse.model_validate(e) for e in enrollments],
        meta=PaginationMeta(
            total=total,
            page=page,
            limit=limit,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1,
        ),
    )


@router.post("", response_model=EnrollmentResponse, status_code=status.HTTP_201_CREATED)
async def enroll_in_course(
    data: CreateEnrollmentRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Enroll in a course."""
    # Check course exists
    course_result = await db.execute(
        select(Course).where(Course.id == data.course_id, Course.status == "published")
    )
    course = course_result.scalar_one_or_none()

    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    # Check not already enrolled
    existing = await db.execute(
        select(Enrollment).where(
            Enrollment.user_id == user.id,
            Enrollment.course_id == data.course_id,
            Enrollment.status.in_(["active", "completed"]),
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Already enrolled in this course",
        )

    # Check payment for paid courses
    if not course.is_free and not data.payment_id:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Payment required for this course",
        )

    enrollment = Enrollment(
        user_id=user.id,
        course_id=data.course_id,
        payment_id=data.payment_id,
        amount_paid=data.amount_paid if not course.is_free else 0,
        currency=data.currency,
        payment_status="completed" if course.is_free else "completed",
    )
    db.add(enrollment)

    # Update course enrollment count
    course.total_enrollments += 1

    await db.flush()
    return EnrollmentResponse.model_validate(enrollment)


@router.get("/{enrollment_id}", response_model=EnrollmentResponse)
async def get_enrollment(
    enrollment_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get enrollment details."""
    result = await db.execute(
        select(Enrollment).where(Enrollment.id == enrollment_id, Enrollment.user_id == user.id)
    )
    enrollment = result.scalar_one_or_none()

    if not enrollment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Enrollment not found")

    return EnrollmentResponse.model_validate(enrollment)


@router.patch("/{enrollment_id}/status")
async def update_enrollment_status(
    enrollment_id: UUID,
    new_status: str = Query(...),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Update enrollment status (pause, resume, cancel)."""
    result = await db.execute(
        select(Enrollment).where(Enrollment.id == enrollment_id, Enrollment.user_id == user.id)
    )
    enrollment = result.scalar_one_or_none()

    if not enrollment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Enrollment not found")

    valid_transitions = {
        "active": ["paused", "cancelled"],
        "paused": ["active", "cancelled"],
        "completed": [],
        "cancelled": [],
        "expired": [],
    }

    if new_status not in valid_transitions.get(enrollment.status, []):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot transition from {enrollment.status} to {new_status}",
        )

    enrollment.status = new_status
    await db.flush()

    return EnrollmentResponse.model_validate(enrollment)

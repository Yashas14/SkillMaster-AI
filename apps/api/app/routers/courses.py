# ════════════════════════════════════════════════════════════
# Courses Router
# ════════════════════════════════════════════════════════════

from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from slugify import slugify
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user, get_optional_user, require_role
from app.database import get_db
from app.models import Course, User
from app.schemas import (
    CourseDetailResponse,
    CourseResponse,
    CreateCourseRequest,
    PaginatedResponse,
    PaginationMeta,
    UpdateCourseRequest,
)

router = APIRouter()


@router.get("", response_model=PaginatedResponse)
async def list_courses(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    category: str | None = None,
    difficulty: str | None = None,
    search: str | None = None,
    instructor_id: UUID | None = None,
    is_free: bool | None = None,
    sort_by: str = "created_at",
    db: AsyncSession = Depends(get_db),
    _user: User | None = Depends(get_optional_user),
):
    """List published courses with filtering."""
    query = select(Course).where(
        Course.status == "published",
        Course.deleted_at.is_(None),
    )

    if category:
        query = query.where(Course.category == category)
    if difficulty:
        query = query.where(Course.difficulty == difficulty)
    if instructor_id:
        query = query.where(Course.instructor_id == instructor_id)
    if is_free is not None:
        query = query.where(Course.is_free == is_free)
    if search:
        query = query.where(
            Course.title.ilike(f"%{search}%") | Course.short_description.ilike(f"%{search}%")
        )

    # Count
    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar() or 0

    # Sort
    sort_column = {
        "created_at": Course.created_at,
        "rating": Course.rating,
        "enrollments": Course.total_enrollments,
        "price": Course.price,
        "title": Course.title,
    }.get(sort_by, Course.created_at)

    query = query.offset((page - 1) * limit).limit(limit).order_by(sort_column.desc())
    result = await db.execute(query)
    courses = result.scalars().all()

    total_pages = max(1, (total + limit - 1) // limit)

    return PaginatedResponse(
        data=[CourseResponse.model_validate(c) for c in courses],
        meta=PaginationMeta(
            total=total,
            page=page,
            limit=limit,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1,
        ),
    )


@router.get("/{course_id}", response_model=CourseDetailResponse)
async def get_course(
    course_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get course details by ID."""
    result = await db.execute(
        select(Course).where(Course.id == course_id, Course.deleted_at.is_(None))
    )
    course = result.scalar_one_or_none()

    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    return CourseDetailResponse.model_validate(course)


@router.get("/slug/{slug}", response_model=CourseDetailResponse)
async def get_course_by_slug(
    slug: str,
    db: AsyncSession = Depends(get_db),
):
    """Get course details by slug."""
    result = await db.execute(
        select(Course).where(Course.slug == slug, Course.deleted_at.is_(None))
    )
    course = result.scalar_one_or_none()

    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    return CourseDetailResponse.model_validate(course)


@router.post("", response_model=CourseDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_course(
    data: CreateCourseRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("instructor", "admin", "super_admin")),
):
    """Create a new course."""
    # Generate unique slug
    base_slug = slugify(data.title)
    slug = base_slug
    counter = 1
    while True:
        result = await db.execute(select(Course).where(Course.slug == slug))
        if not result.scalar_one_or_none():
            break
        slug = f"{base_slug}-{counter}"
        counter += 1

    course = Course(
        title=data.title,
        slug=slug,
        description=data.description,
        short_description=data.short_description,
        instructor_id=user.id,
        category=data.category,
        subcategory=data.subcategory,
        tags=data.tags,
        difficulty=data.difficulty,
        language=data.language,
        price=data.price,
        currency=data.currency,
        is_free=data.price == 0,
        prerequisites=data.prerequisites,
        learning_outcomes=data.learning_outcomes,
        target_audience=data.target_audience,
    )
    db.add(course)
    await db.flush()

    return CourseDetailResponse.model_validate(course)


@router.patch("/{course_id}", response_model=CourseDetailResponse)
async def update_course(
    course_id: UUID,
    data: UpdateCourseRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Update a course."""
    result = await db.execute(select(Course).where(Course.id == course_id))
    course = result.scalar_one_or_none()

    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    if course.instructor_id != user.id and user.role not in ("admin", "super_admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not the course instructor")

    update_data = data.model_dump(exclude_unset=True)

    if "title" in update_data:
        update_data["slug"] = slugify(update_data["title"])

    if "price" in update_data:
        update_data["is_free"] = update_data["price"] == 0

    for field, value in update_data.items():
        setattr(course, field, value)

    await db.flush()
    return CourseDetailResponse.model_validate(course)


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course(
    course_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Soft-delete a course."""
    result = await db.execute(select(Course).where(Course.id == course_id))
    course = result.scalar_one_or_none()

    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    if course.instructor_id != user.id and user.role not in ("admin", "super_admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not the course instructor")

    course.deleted_at = datetime.now(UTC)
    course.status = "archived"
    await db.flush()

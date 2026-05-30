# ════════════════════════════════════════════════════════════
# Search Router — Semantic + keyword search via RAG pipeline
# ════════════════════════════════════════════════════════════


from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user, get_optional_user
from app.database import get_db
from app.models import Course, User
from app.schemas import SearchRequest
from app.services.rag import rag_pipeline

router = APIRouter()


@router.post("/semantic")
async def semantic_search(
    data: SearchRequest,
    _user: User = Depends(get_current_user),
):
    """Perform semantic search across course content using vector embeddings."""
    results = await rag_pipeline.semantic_search(
        query=data.query,
        course_id=str(data.course_id) if data.course_id else None,
        top_k=data.top_k,
        min_score=0.5,
    )
    return {"query": data.query, "results": results, "total": len(results)}


@router.get("/courses")
async def search_courses(
    q: str = Query(min_length=2, max_length=200),
    category: str | None = None,
    difficulty: str | None = None,
    is_free: bool | None = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    _user: User | None = Depends(get_optional_user),
):
    """Search courses with text matching and filters."""
    query = select(Course).where(
        Course.status == "published",
        Course.deleted_at.is_(None),
        Course.title.ilike(f"%{q}%")
        | Course.short_description.ilike(f"%{q}%")
        | Course.description.ilike(f"%{q}%"),
    )

    if category:
        query = query.where(Course.category == category)
    if difficulty:
        query = query.where(Course.difficulty == difficulty)
    if is_free is not None:
        query = query.where(Course.is_free == is_free)

    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar() or 0

    query = query.offset((page - 1) * limit).limit(limit).order_by(Course.rating.desc())
    result = await db.execute(query)
    courses = result.scalars().all()

    return {
        "query": q,
        "total": total,
        "results": [
            {
                "id": str(c.id),
                "title": c.title,
                "slug": c.slug,
                "short_description": c.short_description,
                "category": c.category,
                "difficulty": c.difficulty,
                "rating": c.rating,
                "total_enrollments": c.total_enrollments,
                "is_free": c.is_free,
                "price": c.price,
                "thumbnail_url": c.thumbnail_url,
            }
            for c in courses
        ],
    }


@router.post("/ingest/lesson")
async def ingest_lesson_content(
    lesson_id: str,
    course_id: str,
    module_id: str,
    title: str,
    content: str,
    _user: User = Depends(get_current_user),
):
    """Ingest lesson content into the RAG vector store (instructor/admin)."""
    count = await rag_pipeline.ingest_lesson(
        lesson_id=lesson_id,
        course_id=course_id,
        module_id=module_id,
        title=title,
        content=content,
    )
    return {"ingested_chunks": count, "lesson_id": lesson_id}

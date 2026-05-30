# ════════════════════════════════════════════════════════════
# Quiz Router — Adaptive quiz generation and grading
# ════════════════════════════════════════════════════════════

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.database import get_db
from app.models import Quiz, QuizAttempt, User
from app.schemas import GenerateQuizRequest, SubmitQuizRequest
from app.services.quiz_generator import quiz_generator

router = APIRouter()


@router.post("/generate", status_code=status.HTTP_201_CREATED)
async def generate_quiz(
    data: GenerateQuizRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Generate an adaptive quiz for a lesson using AI."""
    result = await quiz_generator.generate_quiz(
        lesson_id=str(data.lesson_id),
        course_id=str(data.course_id),
        user_id=str(user.id),
        db=db,
        num_questions=data.num_questions,
        difficulty=data.difficulty,
    )
    return result


@router.get("/{quiz_id}")
async def get_quiz(
    quiz_id: UUID,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    """Get quiz details with questions (answers hidden)."""
    result = await db.execute(select(Quiz).where(Quiz.id == quiz_id))
    quiz = result.scalar_one_or_none()

    if not quiz:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz not found")

    questions = [
        {
            "id": str(q.id),
            "type": q.question_type,
            "question": q.question_text,
            "options": q.options,
            "bloom_level": q.bloom_level,
            "points": q.points,
            "order": q.order,
        }
        for q in quiz.questions
    ]

    return {
        "id": str(quiz.id),
        "title": quiz.title,
        "description": quiz.description,
        "quiz_type": quiz.quiz_type,
        "difficulty": quiz.difficulty,
        "total_questions": quiz.total_questions,
        "time_limit_minutes": quiz.time_limit_minutes,
        "passing_score": quiz.passing_score,
        "max_attempts": quiz.max_attempts,
        "questions": questions,
    }


@router.post("/{quiz_id}/submit")
async def submit_quiz(
    quiz_id: UUID,
    data: SubmitQuizRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Submit quiz answers and get graded results."""
    # Check attempt limit
    attempt_count_result = await db.execute(
        select(QuizAttempt).where(
            QuizAttempt.quiz_id == quiz_id,
            QuizAttempt.user_id == user.id,
        )
    )
    existing_attempts = len(attempt_count_result.scalars().all())

    quiz_result = await db.execute(select(Quiz).where(Quiz.id == quiz_id))
    quiz = quiz_result.scalar_one_or_none()
    if not quiz:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz not found")

    if existing_attempts >= quiz.max_attempts:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Maximum attempts ({quiz.max_attempts}) reached",
        )

    result = await quiz_generator.grade_attempt(
        quiz_id=str(quiz_id),
        user_id=str(user.id),
        answers=data.answers,
        db=db,
    )
    return result


@router.get("/{quiz_id}/attempts")
async def list_attempts(
    quiz_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """List all attempts for a quiz by the current user."""
    result = await db.execute(
        select(QuizAttempt)
        .where(QuizAttempt.quiz_id == quiz_id, QuizAttempt.user_id == user.id)
        .order_by(QuizAttempt.created_at.desc())
    )
    attempts = result.scalars().all()

    return [
        {
            "id": str(a.id),
            "score": a.score,
            "passed": a.passed,
            "earned_points": a.earned_points,
            "total_points": a.total_points,
            "time_taken_seconds": a.time_taken_seconds,
            "bloom_analysis": a.bloom_analysis,
            "created_at": a.created_at.isoformat(),
        }
        for a in attempts
    ]


@router.get("/course/{course_id}")
async def list_course_quizzes(
    course_id: UUID,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    """List all quizzes for a course."""
    result = await db.execute(
        select(Quiz).where(Quiz.course_id == course_id).order_by(Quiz.created_at)
    )
    quizzes = result.scalars().all()

    return [
        {
            "id": str(q.id),
            "title": q.title,
            "quiz_type": q.quiz_type,
            "difficulty": q.difficulty,
            "total_questions": q.total_questions,
            "time_limit_minutes": q.time_limit_minutes,
            "passing_score": q.passing_score,
        }
        for q in quizzes
    ]

# ════════════════════════════════════════════════════════════
# Analytics Router — Student + Instructor dashboards
# ════════════════════════════════════════════════════════════

from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user, require_role
from app.database import get_db
from app.models import (
    Course,
    Enrollment,
    LearningStreak,
    LessonProgress,
    QuizAttempt,
    User,
    UserXP,
)

router = APIRouter()


@router.get("/student")
async def student_analytics(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get comprehensive analytics for the current student."""
    uid = user.id

    # Enrollment stats
    enroll_result = await db.execute(
        select(
            func.count().label("total"),
            func.sum(case((Enrollment.status == "completed", 1), else_=0)).label("completed"),
        )
        .select_from(Enrollment)
        .where(Enrollment.user_id == uid)
    )
    enroll_row = enroll_result.fetchone()
    total_courses = enroll_row.total or 0
    completed_courses = enroll_row.completed or 0

    # Lesson progress
    lesson_result = await db.execute(
        select(
            func.count().label("total"),
            func.sum(LessonProgress.time_spent_seconds).label("time"),
        )
        .select_from(LessonProgress)
        .where(LessonProgress.user_id == uid, LessonProgress.status == "completed")
    )
    lesson_row = lesson_result.fetchone()
    total_lessons = lesson_row.total or 0
    total_seconds = lesson_row.time or 0

    # Quiz scores
    quiz_result = await db.execute(
        select(func.avg(QuizAttempt.score))
        .where(QuizAttempt.user_id == uid)
    )
    avg_quiz = round(float(quiz_result.scalar() or 0), 1)

    # Streak & XP
    streak_result = await db.execute(
        select(LearningStreak).where(LearningStreak.user_id == uid)
    )
    streak = streak_result.scalar_one_or_none()

    # Weekly activity (last 7 days)
    week_ago = datetime.now(UTC) - timedelta(days=7)
    weekly_result = await db.execute(
        select(func.date(UserXP.created_at).label("day"), func.sum(UserXP.amount))
        .where(UserXP.user_id == uid, UserXP.created_at >= week_ago)
        .group_by(func.date(UserXP.created_at))
        .order_by(func.date(UserXP.created_at))
    )
    weekly_activity = [
        {"date": str(row[0]), "xp": row[1]}
        for row in weekly_result.fetchall()
    ]

    # Category breakdown
    cat_result = await db.execute(
        select(Course.category, func.count())
        .join(Enrollment, Enrollment.course_id == Course.id)
        .where(Enrollment.user_id == uid)
        .group_by(Course.category)
    )
    categories = [{"category": row[0], "count": row[1]} for row in cat_result.fetchall()]

    # Monthly progress (last 6 months)
    six_months_ago = datetime.now(UTC) - timedelta(days=180)
    progress_result = await db.execute(
        select(
            func.date_trunc("month", LessonProgress.completed_at).label("month"),
            func.count().label("lessons"),
        )
        .where(
            LessonProgress.user_id == uid,
            LessonProgress.status == "completed",
            LessonProgress.completed_at >= six_months_ago,
        )
        .group_by("month")
        .order_by("month")
    )
    progress_over_time = [
        {"month": row[0].isoformat()[:7] if row[0] else "", "lessons": row[1]}
        for row in progress_result.fetchall()
    ]

    return {
        "total_courses": total_courses,
        "completed_courses": completed_courses,
        "total_lessons_completed": total_lessons,
        "total_study_hours": round(total_seconds / 3600, 1),
        "average_quiz_score": avg_quiz,
        "current_streak": streak.current_streak if streak else 0,
        "total_xp": streak.total_xp if streak else 0,
        "level": streak.level if streak else 1,
        "weekly_activity": weekly_activity,
        "category_breakdown": categories,
        "progress_over_time": progress_over_time,
    }


@router.get("/instructor")
async def instructor_analytics(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("instructor", "admin", "super_admin")),
):
    """Get analytics for an instructor's courses."""
    uid = user.id

    # Course stats
    course_result = await db.execute(
        select(Course).where(Course.instructor_id == uid, Course.deleted_at.is_(None))
    )
    courses = course_result.scalars().all()

    total_students = 0
    total_revenue = 0.0
    course_stats = []

    for course in courses:
        enroll_result = await db.execute(
            select(
                func.count().label("total"),
                func.sum(case((Enrollment.status == "completed", 1), else_=0)).label("completed"),
                func.sum(Enrollment.amount_paid).label("revenue"),
            )
            .select_from(Enrollment)
            .where(Enrollment.course_id == course.id)
        )
        row = enroll_result.fetchone()
        students = row.total or 0
        completed = row.completed or 0
        revenue = float(row.revenue or 0)

        total_students += students
        total_revenue += revenue

        course_stats.append({
            "course_id": str(course.id),
            "title": course.title,
            "students": students,
            "completed": completed,
            "completion_rate": round((completed / students * 100) if students > 0 else 0, 1),
            "rating": course.rating,
            "revenue": revenue,
            "status": course.status,
        })

    avg_rating = sum(c.rating for c in courses) / len(courses) if courses else 0

    # Enrollment trend (last 30 days)
    thirty_days_ago = datetime.now(UTC) - timedelta(days=30)
    trend_result = await db.execute(
        select(
            func.date(Enrollment.enrolled_at).label("day"),
            func.count().label("count"),
        )
        .join(Course, Course.id == Enrollment.course_id)
        .where(
            Course.instructor_id == uid,
            Enrollment.enrolled_at >= thirty_days_ago,
        )
        .group_by("day")
        .order_by("day")
    )
    enrollment_trend = [
        {"date": str(row[0]), "enrollments": row[1]}
        for row in trend_result.fetchall()
    ]

    return {
        "total_courses": len(courses),
        "total_students": total_students,
        "total_revenue": round(total_revenue, 2),
        "average_rating": round(avg_rating, 2),
        "course_stats": course_stats,
        "enrollment_trend": enrollment_trend,
    }


@router.get("/platform")
async def platform_analytics(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_role("admin", "super_admin")),
):
    """Get platform-wide analytics (admin only)."""
    users_count = await db.execute(
        select(func.count()).select_from(User).where(User.is_active.is_(True))
    )
    courses_count = await db.execute(
        select(func.count()).select_from(Course).where(Course.deleted_at.is_(None))
    )
    enrollments_count = await db.execute(
        select(func.count()).select_from(Enrollment)
    )
    revenue_result = await db.execute(
        select(func.sum(Enrollment.amount_paid))
    )

    return {
        "total_users": users_count.scalar() or 0,
        "total_courses": courses_count.scalar() or 0,
        "total_enrollments": enrollments_count.scalar() or 0,
        "total_revenue": round(float(revenue_result.scalar() or 0), 2),
    }

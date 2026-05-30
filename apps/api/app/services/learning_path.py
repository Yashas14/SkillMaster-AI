# ════════════════════════════════════════════════════════════
# Learning Path Engine — Personalized learning recommendations
# ════════════════════════════════════════════════════════════

from __future__ import annotations

import json
import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models import (
    Course,
    Enrollment,
    LearningPath,
    LearningPathItem,
    LessonProgress,
    QuizAttempt,
)

settings = get_settings()


class LearningPathEngine:
    """Generate and manage personalized learning paths using AI analysis."""

    async def generate_path(
        self,
        user_id: str,
        goal: str,
        db: AsyncSession,
        current_skills: list[str] | None = None,
        target_skills: list[str] | None = None,
        weekly_hours: int = 10,
    ) -> dict[str, Any]:
        """Generate a personalized learning path based on goals and current knowledge."""
        import anthropic

        # Gather user context
        user_context = await self._gather_user_context(user_id, db)

        # Get available courses
        courses = await self._get_available_courses(db)

        prompt = self._build_path_prompt(
            goal=goal,
            user_context=user_context,
            courses=courses,
            current_skills=current_skills or [],
            target_skills=target_skills or [],
            weekly_hours=weekly_hours,
        )

        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=4096,
            system="""You are a learning path architect. Design optimal, personalized learning journeys.
Return JSON with the learning path structure.""",
            messages=[{"role": "user", "content": prompt}],
        )

        path_data = self._parse_response(response.content[0].text)

        # Save to DB
        learning_path = LearningPath(
            user_id=uuid.UUID(user_id),
            title=path_data.get("title", f"Learning Path: {goal}"),
            description=path_data.get("description", ""),
            goal=goal,
            estimated_duration_weeks=path_data.get("estimated_weeks", 4),
            weekly_hours=weekly_hours,
            difficulty_progression=path_data.get("difficulty_progression", "gradual"),
            status="active",
            extra_data={
                "current_skills": current_skills or [],
                "target_skills": target_skills or [],
                "generated_by": "claude-opus-4-6",
                "generated_at": datetime.now(UTC).isoformat(),
            },
        )
        db.add(learning_path)
        await db.flush()

        # Save path items
        items_data = path_data.get("items", [])
        saved_items: list[dict[str, Any]] = []
        for i, item in enumerate(items_data):
            path_item = LearningPathItem(
                learning_path_id=learning_path.id,
                order=i,
                item_type=item.get("type", "course"),
                title=item.get("title", ""),
                description=item.get("description", ""),
                course_id=uuid.UUID(item["course_id"]) if item.get("course_id") else None,
                estimated_hours=item.get("estimated_hours", 2),
                is_required=item.get("required", True),
                extra_data={
                    "skills": item.get("skills", []),
                    "reason": item.get("reason", ""),
                },
            )
            db.add(path_item)
            saved_items.append({
                "order": i,
                "type": path_item.item_type,
                "title": path_item.title,
                "description": path_item.description,
                "estimated_hours": path_item.estimated_hours,
                "required": path_item.is_required,
                "skills": item.get("skills", []),
            })

        await db.flush()

        return {
            "path_id": str(learning_path.id),
            "title": learning_path.title,
            "description": learning_path.description,
            "goal": goal,
            "estimated_weeks": learning_path.estimated_duration_weeks,
            "weekly_hours": weekly_hours,
            "items": saved_items,
            "total_items": len(saved_items),
        }

    async def get_next_recommendation(
        self, user_id: str, db: AsyncSession
    ) -> dict[str, Any]:
        """Get the next recommended action for a user."""
        # Find active learning path
        path_result = await db.execute(
            select(LearningPath)
            .where(LearningPath.user_id == uuid.UUID(user_id), LearningPath.status == "active")
            .order_by(LearningPath.created_at.desc())
            .limit(1)
        )
        path = path_result.scalar_one_or_none()

        if not path:
            return {
                "type": "no_path",
                "message": "No active learning path. Create one to get personalized recommendations.",
            }

        # Find next incomplete item
        items_result = await db.execute(
            select(LearningPathItem)
            .where(
                LearningPathItem.learning_path_id == path.id,
                LearningPathItem.status != "completed",
            )
            .order_by(LearningPathItem.order)
            .limit(1)
        )
        next_item = items_result.scalar_one_or_none()

        if not next_item:
            path.status = "completed"
            path.completed_at = datetime.now(UTC)
            await db.flush()
            return {
                "type": "path_completed",
                "message": "Congratulations! You've completed your learning path.",
                "path_id": str(path.id),
            }

        return {
            "type": "next_item",
            "path_id": str(path.id),
            "item": {
                "id": str(next_item.id),
                "order": next_item.order,
                "type": next_item.item_type,
                "title": next_item.title,
                "description": next_item.description,
                "estimated_hours": next_item.estimated_hours,
                "course_id": str(next_item.course_id) if next_item.course_id else None,
            },
        }

    async def update_progress(
        self, user_id: str, path_id: str, item_id: str, status: str, db: AsyncSession
    ) -> dict[str, Any]:
        """Update progress on a learning path item."""
        result = await db.execute(
            select(LearningPathItem).where(
                LearningPathItem.id == uuid.UUID(item_id),
                LearningPathItem.learning_path_id == uuid.UUID(path_id),
            )
        )
        item = result.scalar_one_or_none()
        if not item:
            raise ValueError("Learning path item not found")

        item.status = status
        if status == "completed":
            item.completed_at = datetime.now(UTC)

        # Recalculate path progress
        path_result = await db.execute(
            select(LearningPath).where(LearningPath.id == uuid.UUID(path_id))
        )
        path = path_result.scalar_one()

        all_items = await db.execute(
            select(LearningPathItem).where(LearningPathItem.learning_path_id == path.id)
        )
        items = all_items.scalars().all()
        completed = sum(1 for i in items if i.status == "completed")
        path.progress = round((completed / len(items)) * 100, 1) if items else 0

        await db.flush()

        return {
            "item_id": item_id,
            "status": status,
            "path_progress": path.progress,
        }

    # ─── Helpers ───────────────────────────────────────────

    async def _gather_user_context(self, user_id: str, db: AsyncSession) -> dict[str, Any]:
        """Gather user's learning history for personalization."""
        uid = uuid.UUID(user_id)

        # Enrollments
        enroll_result = await db.execute(
            select(Enrollment).where(Enrollment.user_id == uid).limit(20)
        )
        enrollments = enroll_result.scalars().all()

        # Quiz performance
        quiz_result = await db.execute(
            select(func.avg(QuizAttempt.score))
            .where(QuizAttempt.user_id == uid)
        )
        avg_score = quiz_result.scalar() or 0

        # Completed lessons count
        completed_result = await db.execute(
            select(func.count())
            .select_from(LessonProgress)
            .where(LessonProgress.user_id == uid, LessonProgress.status == "completed")
        )
        completed_lessons = completed_result.scalar() or 0

        return {
            "enrollments_count": len(enrollments),
            "completed_courses": sum(1 for e in enrollments if e.status == "completed"),
            "average_quiz_score": round(float(avg_score), 1),
            "completed_lessons": completed_lessons,
            "course_categories": list({e.course.category for e in enrollments if e.course}),
        }

    async def _get_available_courses(self, db: AsyncSession) -> list[dict[str, str]]:
        """Get list of published courses for path planning."""
        result = await db.execute(
            select(Course)
            .where(Course.status == "published", Course.deleted_at.is_(None))
            .order_by(Course.total_enrollments.desc())
            .limit(50)
        )
        courses = result.scalars().all()
        return [
            {
                "id": str(c.id),
                "title": c.title,
                "category": c.category,
                "difficulty": c.difficulty,
                "duration_minutes": str(c.estimated_duration_minutes),
                "rating": str(c.rating),
            }
            for c in courses
        ]

    def _build_path_prompt(
        self,
        goal: str,
        user_context: dict[str, Any],
        courses: list[dict[str, str]],
        current_skills: list[str],
        target_skills: list[str],
        weekly_hours: int,
    ) -> str:
        return f"""Design a personalized learning path.

Student Goal: {goal}
Current Skills: {', '.join(current_skills) if current_skills else 'Beginner'}
Target Skills: {', '.join(target_skills) if target_skills else 'Based on goal'}
Weekly Study Hours: {weekly_hours}

Student Context:
- Completed courses: {user_context.get('completed_courses', 0)}
- Completed lessons: {user_context.get('completed_lessons', 0)}
- Average quiz score: {user_context.get('average_quiz_score', 'N/A')}%
- Studied categories: {', '.join(user_context.get('course_categories', []))}

Available Courses:
{json.dumps(courses[:20], indent=2)}

Return JSON:
{{
  "title": "Learning Path: ...",
  "description": "...",
  "estimated_weeks": 4,
  "difficulty_progression": "gradual",
  "items": [
    {{
      "type": "course",
      "title": "...",
      "description": "Why this is recommended...",
      "course_id": "uuid-if-matching",
      "estimated_hours": 10,
      "required": true,
      "skills": ["skill1"],
      "reason": "Why this step"
    }}
  ]
}}"""

    def _parse_response(self, raw: str) -> dict[str, Any]:
        text = raw.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1]
        if text.endswith("```"):
            text = text[:-3]
        try:
            return json.loads(text.strip())
        except json.JSONDecodeError:
            start = text.find("{")
            end = text.rfind("}") + 1
            if start != -1 and end > start:
                return json.loads(text[start:end])
            return {"title": "Custom Learning Path", "items": []}


learning_path_engine = LearningPathEngine()

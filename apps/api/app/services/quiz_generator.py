# ════════════════════════════════════════════════════════════
# Adaptive Quiz Generator — Claude-powered quiz engine
# ════════════════════════════════════════════════════════════

from __future__ import annotations

import json
import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models import Lesson, Quiz, QuizAttempt, QuizQuestion

settings = get_settings()

BLOOM_LEVELS = ["remember", "understand", "apply", "analyze", "evaluate", "create"]

DIFFICULTY_MAP = {
    "beginner": ["remember", "understand"],
    "intermediate": ["understand", "apply", "analyze"],
    "advanced": ["analyze", "evaluate", "create"],
    "expert": ["evaluate", "create"],
}


class QuizGenerator:
    """Generate adaptive quizzes using Claude Opus 4.6 based on lesson content and student performance."""

    async def generate_quiz(
        self,
        lesson_id: str,
        course_id: str,
        user_id: str,
        db: AsyncSession,
        num_questions: int = 10,
        difficulty: str = "intermediate",
    ) -> dict[str, Any]:
        """Generate an adaptive quiz for a lesson."""
        import anthropic

        # Get lesson content
        lesson_result = await db.execute(select(Lesson).where(Lesson.id == uuid.UUID(lesson_id)))
        lesson = lesson_result.scalar_one_or_none()
        if not lesson:
            raise ValueError(f"Lesson {lesson_id} not found")

        # Analyze past performance for adaptive difficulty
        bloom_levels = await self._get_adaptive_levels(user_id, course_id, db, difficulty)

        # Get lesson content text
        content_text = self._extract_lesson_text(lesson)

        # Generate quiz via Claude
        prompt = self._build_quiz_prompt(
            title=lesson.title,
            content=content_text,
            num_questions=num_questions,
            bloom_levels=bloom_levels,
            difficulty=difficulty,
        )

        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=4096,
            system="You are an expert assessment designer. Generate high-quality quiz questions in strict JSON format. Always return valid JSON.",
            messages=[{"role": "user", "content": prompt}],
        )

        raw_text = response.content[0].text
        questions_data = self._parse_quiz_response(raw_text)

        # Save quiz to DB
        quiz = Quiz(
            course_id=uuid.UUID(course_id),
            lesson_id=uuid.UUID(lesson_id),
            title=f"Quiz: {lesson.title}",
            description=f"Adaptive quiz for {lesson.title}",
            quiz_type="adaptive",
            difficulty=difficulty,
            total_questions=len(questions_data),
            time_limit_minutes=max(len(questions_data) * 2, 10),
            passing_score=70.0,
            max_attempts=3,
            settings={
                "shuffle_questions": True,
                "shuffle_options": True,
                "show_correct_after": True,
                "bloom_levels": bloom_levels,
            },
        )
        db.add(quiz)
        await db.flush()

        # Save questions
        saved_questions = []
        for i, q_data in enumerate(questions_data):
            question = QuizQuestion(
                quiz_id=quiz.id,
                question_type=q_data.get("type", "multiple_choice"),
                question_text=q_data["question"],
                options=q_data.get("options", []),
                correct_answer=q_data["correct_answer"],
                explanation=q_data.get("explanation", ""),
                bloom_level=q_data.get("bloom_level", "understand"),
                points=q_data.get("points", 10),
                order=i,
                extra_data={"generated_by": "claude-opus-4-6", "difficulty": difficulty},
            )
            db.add(question)
            saved_questions.append(question)

        await db.flush()

        return {
            "quiz_id": str(quiz.id),
            "title": quiz.title,
            "total_questions": quiz.total_questions,
            "time_limit_minutes": quiz.time_limit_minutes,
            "passing_score": quiz.passing_score,
            "difficulty": difficulty,
            "bloom_levels": bloom_levels,
            "questions": [
                {
                    "id": str(q.id),
                    "type": q.question_type,
                    "question": q.question_text,
                    "options": q.options,
                    "bloom_level": q.bloom_level,
                    "points": q.points,
                }
                for q in saved_questions
            ],
        }

    async def grade_attempt(
        self,
        quiz_id: str,
        user_id: str,
        answers: dict[str, str],
        db: AsyncSession,
    ) -> dict[str, Any]:
        """Grade a quiz attempt and return detailed results."""
        # Load questions
        result = await db.execute(
            select(QuizQuestion).where(QuizQuestion.quiz_id == uuid.UUID(quiz_id)).order_by(QuizQuestion.order)
        )
        questions = result.scalars().all()

        total_points = 0
        earned_points = 0
        results: list[dict[str, Any]] = []

        for q in questions:
            total_points += q.points
            user_answer = answers.get(str(q.id), "")
            is_correct = self._check_answer(q, user_answer)

            if is_correct:
                earned_points += q.points

            results.append({
                "question_id": str(q.id),
                "question": q.question_text,
                "your_answer": user_answer,
                "correct_answer": q.correct_answer,
                "is_correct": is_correct,
                "explanation": q.explanation,
                "bloom_level": q.bloom_level,
                "points_earned": q.points if is_correct else 0,
                "points_possible": q.points,
            })

        score = round((earned_points / total_points) * 100, 1) if total_points > 0 else 0

        # Bloom level breakdown
        bloom_analysis: dict[str, dict[str, int]] = {}
        for r in results:
            level = r["bloom_level"]
            if level not in bloom_analysis:
                bloom_analysis[level] = {"correct": 0, "total": 0}
            bloom_analysis[level]["total"] += 1
            if r["is_correct"]:
                bloom_analysis[level]["correct"] += 1

        # Save attempt
        quiz_result = await db.execute(select(Quiz).where(Quiz.id == uuid.UUID(quiz_id)))
        quiz = quiz_result.scalar_one()

        attempt = QuizAttempt(
            quiz_id=quiz.id,
            user_id=uuid.UUID(user_id),
            score=score,
            total_points=total_points,
            earned_points=earned_points,
            time_taken_seconds=0,
            answers=answers,
            results=results,
            passed=score >= quiz.passing_score,
            bloom_analysis=bloom_analysis,
        )
        db.add(attempt)
        await db.flush()

        return {
            "attempt_id": str(attempt.id),
            "score": score,
            "passed": attempt.passed,
            "earned_points": earned_points,
            "total_points": total_points,
            "bloom_analysis": bloom_analysis,
            "results": results,
            "recommendations": self._generate_recommendations(bloom_analysis, score),
        }

    async def _get_adaptive_levels(
        self, user_id: str, course_id: str, db: AsyncSession, default_difficulty: str
    ) -> list[str]:
        """Determine Bloom levels based on past performance."""
        # Check past quiz attempts
        result = await db.execute(
            select(QuizAttempt)
            .join(Quiz)
            .where(
                QuizAttempt.user_id == uuid.UUID(user_id),
                Quiz.course_id == uuid.UUID(course_id),
            )
            .order_by(QuizAttempt.created_at.desc())
            .limit(5)
        )
        attempts = result.scalars().all()

        if not attempts:
            return DIFFICULTY_MAP.get(default_difficulty, ["understand", "apply"])

        avg_score = sum(a.score for a in attempts) / len(attempts)

        if avg_score >= 90:
            return ["apply", "analyze", "evaluate", "create"]
        elif avg_score >= 75:
            return ["understand", "apply", "analyze"]
        elif avg_score >= 60:
            return ["remember", "understand", "apply"]
        else:
            return ["remember", "understand"]

    def _extract_lesson_text(self, lesson: Lesson) -> str:
        """Extract readable text from lesson content JSON."""
        content = lesson.content or {}
        parts = [lesson.title, lesson.description or ""]

        if isinstance(content, dict):
            for key in ("body", "text", "markdown", "html", "content"):
                if key in content:
                    parts.append(str(content[key]))
            if "blocks" in content and isinstance(content["blocks"], list):
                for block in content["blocks"]:
                    if isinstance(block, dict) and "text" in block:
                        parts.append(block["text"])

        return "\n\n".join(p for p in parts if p)

    def _build_quiz_prompt(
        self,
        title: str,
        content: str,
        num_questions: int,
        bloom_levels: list[str],
        difficulty: str,
    ) -> str:
        return f"""Generate {num_questions} quiz questions for the lesson "{title}".

Content:
{content[:6000]}

Requirements:
- Difficulty: {difficulty}
- Bloom taxonomy levels to target: {', '.join(bloom_levels)}
- Mix question types: multiple_choice, true_false, short_answer
- For multiple_choice: provide exactly 4 options labeled A, B, C, D
- Each question must test genuine understanding, not just recall
- Include detailed explanations for each correct answer

Return ONLY a JSON array. Each element:
{{
  "type": "multiple_choice" | "true_false" | "short_answer",
  "question": "...",
  "options": ["A. ...", "B. ...", "C. ...", "D. ..."],
  "correct_answer": "A" | "B" | "C" | "D" | "true" | "false" | "free text",
  "explanation": "Why this is correct...",
  "bloom_level": "{bloom_levels[0]}",
  "points": 10
}}"""

    def _parse_quiz_response(self, raw: str) -> list[dict[str, Any]]:
        """Parse Claude's JSON response, handling markdown code fences."""
        text = raw.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1] if "\n" in text else text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

        try:
            parsed = json.loads(text)
            if isinstance(parsed, list):
                return parsed
            if isinstance(parsed, dict) and "questions" in parsed:
                return parsed["questions"]
            return [parsed]
        except json.JSONDecodeError:
            # Fallback: extract JSON array
            start = text.find("[")
            end = text.rfind("]") + 1
            if start != -1 and end > start:
                return json.loads(text[start:end])
            return []

    def _check_answer(self, question: QuizQuestion, answer: str) -> bool:
        """Check if an answer is correct."""
        correct = str(question.correct_answer).strip().lower()
        given = answer.strip().lower()

        if question.question_type == "true_false":
            return given == correct

        if question.question_type == "multiple_choice":
            return given == correct or given.startswith(correct)

        # Short answer: fuzzy comparison
        return correct in given or given in correct

    def _generate_recommendations(
        self, bloom_analysis: dict[str, dict[str, int]], score: float
    ) -> list[str]:
        """Generate study recommendations based on quiz results."""
        recs: list[str] = []

        weak_levels = []
        for level, stats in bloom_analysis.items():
            pct = (stats["correct"] / stats["total"] * 100) if stats["total"] > 0 else 0
            if pct < 60:
                weak_levels.append(level)

        if score < 60:
            recs.append("Review the lesson material thoroughly before retaking.")
        elif score < 80:
            recs.append("Good effort! Focus on the areas where you scored lower.")

        for level in weak_levels:
            guidance = {
                "remember": "Practice recalling key definitions and facts.",
                "understand": "Try explaining concepts in your own words.",
                "apply": "Work through more practice problems.",
                "analyze": "Break down complex problems into components.",
                "evaluate": "Practice comparing and contrasting different approaches.",
                "create": "Try building original solutions or explanations.",
            }
            recs.append(guidance.get(level, f"Focus on improving {level}-level skills."))

        if score >= 90:
            recs.append("Excellent! Consider moving to the next lesson or exploring advanced topics.")

        return recs


quiz_generator = QuizGenerator()

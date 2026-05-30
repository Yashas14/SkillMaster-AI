# ════════════════════════════════════════════════════════════
# Gamification Service — XP, badges, streaks, levels
# ════════════════════════════════════════════════════════════

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Badge, LearningStreak, User, UserBadge, UserXP

# XP rewards for actions
XP_REWARDS = {
    "lesson_completed": 25,
    "quiz_passed": 50,
    "quiz_perfect": 100,
    "course_completed": 200,
    "streak_7_days": 75,
    "streak_30_days": 300,
    "first_course_enrolled": 10,
    "review_posted": 15,
    "code_submitted": 10,
    "learning_path_completed": 250,
}

# Level thresholds (cumulative XP)
LEVEL_THRESHOLDS = [
    0, 100, 300, 600, 1000, 1500, 2200, 3000, 4000, 5200,
    6500, 8000, 10000, 12500, 15500, 19000, 23000, 27500, 32500, 38000,
    44000, 50500, 57500, 65000, 73000, 81500, 90500, 100000, 110000, 121000,
]

# Badge definitions
BADGE_DEFINITIONS = [
    {"name": "First Steps", "description": "Complete your first lesson", "icon": "footprints", "category": "milestone", "criteria_type": "lessons_completed", "criteria_value": 1, "xp_reward": 25, "rarity": "common"},
    {"name": "Quick Learner", "description": "Complete 10 lessons", "icon": "zap", "category": "milestone", "criteria_type": "lessons_completed", "criteria_value": 10, "xp_reward": 50, "rarity": "common"},
    {"name": "Knowledge Seeker", "description": "Complete 50 lessons", "icon": "book-open", "category": "milestone", "criteria_type": "lessons_completed", "criteria_value": 50, "xp_reward": 100, "rarity": "uncommon"},
    {"name": "Scholar", "description": "Complete 100 lessons", "icon": "graduation-cap", "category": "milestone", "criteria_type": "lessons_completed", "criteria_value": 100, "xp_reward": 200, "rarity": "rare"},
    {"name": "Course Conqueror", "description": "Complete your first course", "icon": "trophy", "category": "achievement", "criteria_type": "courses_completed", "criteria_value": 1, "xp_reward": 50, "rarity": "common"},
    {"name": "Polymath", "description": "Complete 5 courses", "icon": "star", "category": "achievement", "criteria_type": "courses_completed", "criteria_value": 5, "xp_reward": 150, "rarity": "uncommon"},
    {"name": "Master Learner", "description": "Complete 10 courses", "icon": "crown", "category": "achievement", "criteria_type": "courses_completed", "criteria_value": 10, "xp_reward": 300, "rarity": "rare"},
    {"name": "Quiz Ace", "description": "Score 100% on a quiz", "icon": "target", "category": "quiz", "criteria_type": "perfect_quiz", "criteria_value": 1, "xp_reward": 50, "rarity": "uncommon"},
    {"name": "Quiz Master", "description": "Pass 20 quizzes", "icon": "award", "category": "quiz", "criteria_type": "quizzes_passed", "criteria_value": 20, "xp_reward": 100, "rarity": "rare"},
    {"name": "Week Warrior", "description": "Maintain a 7-day streak", "icon": "flame", "category": "streak", "criteria_type": "streak_days", "criteria_value": 7, "xp_reward": 75, "rarity": "common"},
    {"name": "Month Master", "description": "Maintain a 30-day streak", "icon": "fire", "category": "streak", "criteria_type": "streak_days", "criteria_value": 30, "xp_reward": 300, "rarity": "rare"},
    {"name": "Code Warrior", "description": "Submit 50 code solutions", "icon": "code", "category": "coding", "criteria_type": "code_submissions", "criteria_value": 50, "xp_reward": 150, "rarity": "uncommon"},
    {"name": "Helpful Reviewer", "description": "Write 5 course reviews", "icon": "message-circle", "category": "community", "criteria_type": "reviews_posted", "criteria_value": 5, "xp_reward": 75, "rarity": "common"},
    {"name": "AI Explorer", "description": "Have 100 AI tutor conversations", "icon": "bot", "category": "ai", "criteria_type": "ai_chats", "criteria_value": 100, "xp_reward": 100, "rarity": "uncommon"},
    {"name": "Legendary", "description": "Reach level 30", "icon": "sparkles", "category": "milestone", "criteria_type": "level_reached", "criteria_value": 30, "xp_reward": 500, "rarity": "legendary"},
]


class GamificationService:
    """Manage XP, badges, streaks, and levels."""

    def _get_level(self, total_xp: int) -> int:
        for i in range(len(LEVEL_THRESHOLDS) - 1, -1, -1):
            if total_xp >= LEVEL_THRESHOLDS[i]:
                return i + 1
        return 1

    def _next_level_xp(self, current_level: int) -> int:
        if current_level < len(LEVEL_THRESHOLDS):
            return LEVEL_THRESHOLDS[current_level]
        return LEVEL_THRESHOLDS[-1] + (current_level - len(LEVEL_THRESHOLDS) + 1) * 12000

    async def award_xp(
        self,
        user_id: str,
        amount: int,
        source: str,
        source_id: str = "",
        description: str = "",
        db: AsyncSession = None,
    ) -> dict[str, Any]:
        """Award XP to a user and check for level-up."""
        uid = uuid.UUID(user_id)

        xp_entry = UserXP(
            user_id=uid,
            amount=amount,
            source=source,
            source_id=source_id,
            description=description,
        )
        db.add(xp_entry)

        # Update streak record
        streak = await self._get_or_create_streak(uid, db)
        streak.total_xp += amount
        old_level = streak.level
        streak.level = self._get_level(streak.total_xp)
        leveled_up = streak.level > old_level

        await db.flush()

        return {
            "xp_awarded": amount,
            "total_xp": streak.total_xp,
            "level": streak.level,
            "leveled_up": leveled_up,
            "next_level_xp": self._next_level_xp(streak.level),
        }

    async def update_streak(self, user_id: str, db: AsyncSession) -> dict[str, Any]:
        """Update the user's learning streak."""
        uid = uuid.UUID(user_id)
        streak = await self._get_or_create_streak(uid, db)

        now = datetime.now(UTC)
        today = now.date()

        if streak.last_activity_date:
            last_date = streak.last_activity_date.date() if hasattr(streak.last_activity_date, 'date') else streak.last_activity_date
            delta = (today - last_date).days

            if delta == 0:
                pass  # Already active today
            elif delta == 1:
                streak.current_streak += 1
                if streak.current_streak > streak.longest_streak:
                    streak.longest_streak = streak.current_streak
            else:
                streak.current_streak = 1
        else:
            streak.current_streak = 1

        streak.last_activity_date = now
        await db.flush()

        return {
            "current_streak": streak.current_streak,
            "longest_streak": streak.longest_streak,
        }

    async def check_and_award_badges(
        self, user_id: str, db: AsyncSession
    ) -> list[dict[str, Any]]:
        """Check all badge criteria and award any newly earned badges."""
        uid = uuid.UUID(user_id)

        # Get existing badges
        existing_result = await db.execute(
            select(UserBadge.badge_id).where(UserBadge.user_id == uid)
        )
        existing_badge_ids = {row[0] for row in existing_result.fetchall()}

        # Get all badges
        badge_result = await db.execute(select(Badge).where(Badge.is_active.is_(True)))
        all_badges = badge_result.scalars().all()

        # Gather user stats
        stats = await self._gather_user_stats(uid, db)
        streak = await self._get_or_create_streak(uid, db)

        newly_earned: list[dict[str, Any]] = []

        for badge in all_badges:
            if badge.id in existing_badge_ids:
                continue

            earned = self._check_criteria(badge, stats, streak)
            if earned:
                user_badge = UserBadge(
                    user_id=uid,
                    badge_id=badge.id,
                    extra_data={"auto_awarded": True},
                )
                db.add(user_badge)

                # Award badge XP
                await self.award_xp(
                    user_id=user_id,
                    amount=badge.xp_reward,
                    source="badge_earned",
                    source_id=str(badge.id),
                    description=f"Earned badge: {badge.name}",
                    db=db,
                )

                newly_earned.append({
                    "badge_id": str(badge.id),
                    "name": badge.name,
                    "description": badge.description,
                    "icon": badge.icon,
                    "rarity": badge.rarity,
                    "xp_reward": badge.xp_reward,
                })

        await db.flush()
        return newly_earned

    async def get_profile(self, user_id: str, db: AsyncSession) -> dict[str, Any]:
        """Get full gamification profile for a user."""
        uid = uuid.UUID(user_id)
        streak = await self._get_or_create_streak(uid, db)

        # Badges
        badge_result = await db.execute(
            select(Badge, UserBadge.earned_at)
            .join(UserBadge, UserBadge.badge_id == Badge.id)
            .where(UserBadge.user_id == uid)
            .order_by(UserBadge.earned_at.desc())
        )
        badges = [
            {
                "id": str(b.id),
                "name": b.name,
                "description": b.description,
                "icon": b.icon,
                "category": b.category,
                "rarity": b.rarity,
                "xp_reward": b.xp_reward,
                "earned_at": earned_at.isoformat() if earned_at else None,
            }
            for b, earned_at in badge_result.fetchall()
        ]

        # Rank
        rank_result = await db.execute(
            select(func.count())
            .select_from(LearningStreak)
            .where(LearningStreak.total_xp > streak.total_xp)
        )
        rank = (rank_result.scalar() or 0) + 1

        return {
            "user_id": user_id,
            "total_xp": streak.total_xp,
            "level": streak.level,
            "current_streak": streak.current_streak,
            "longest_streak": streak.longest_streak,
            "next_level_xp": self._next_level_xp(streak.level),
            "badges": badges,
            "total_badges": len(badges),
            "rank": rank,
        }

    async def get_leaderboard(
        self, db: AsyncSession, limit: int = 20
    ) -> list[dict[str, Any]]:
        """Get the top users by XP."""
        result = await db.execute(
            select(LearningStreak, User.name, User.avatar_url)
            .join(User, User.id == LearningStreak.user_id)
            .order_by(desc(LearningStreak.total_xp))
            .limit(limit)
        )
        rows = result.fetchall()

        return [
            {
                "rank": i + 1,
                "user_id": str(streak.user_id),
                "name": name,
                "avatar_url": avatar,
                "total_xp": streak.total_xp,
                "level": streak.level,
                "current_streak": streak.current_streak,
            }
            for i, (streak, name, avatar) in enumerate(rows)
        ]

    async def seed_badges(self, db: AsyncSession) -> int:
        """Seed badge definitions into the database."""
        count = 0
        for defn in BADGE_DEFINITIONS:
            existing = await db.execute(select(Badge).where(Badge.name == defn["name"]))
            if existing.scalar_one_or_none():
                continue
            badge = Badge(**defn)
            db.add(badge)
            count += 1
        await db.flush()
        return count

    # ─── Internal helpers ──────────────────────────────────

    async def _get_or_create_streak(self, user_id: uuid.UUID, db: AsyncSession) -> LearningStreak:
        result = await db.execute(
            select(LearningStreak).where(LearningStreak.user_id == user_id)
        )
        streak = result.scalar_one_or_none()
        if not streak:
            streak = LearningStreak(user_id=user_id)
            db.add(streak)
            await db.flush()
        return streak

    async def _gather_user_stats(self, user_id: uuid.UUID, db: AsyncSession) -> dict[str, int]:
        """Gather stats needed for badge criteria checks."""
        from app.models import ChatSession, CourseReview, Enrollment, LessonProgress, QuizAttempt

        lessons_result = await db.execute(
            select(func.count()).select_from(LessonProgress)
            .where(LessonProgress.user_id == user_id, LessonProgress.status == "completed")
        )
        courses_result = await db.execute(
            select(func.count()).select_from(Enrollment)
            .where(Enrollment.user_id == user_id, Enrollment.status == "completed")
        )
        quizzes_result = await db.execute(
            select(func.count()).select_from(QuizAttempt)
            .where(QuizAttempt.user_id == user_id, QuizAttempt.passed.is_(True))
        )
        perfect_result = await db.execute(
            select(func.count()).select_from(QuizAttempt)
            .where(QuizAttempt.user_id == user_id, QuizAttempt.score >= 100)
        )
        reviews_result = await db.execute(
            select(func.count()).select_from(CourseReview)
            .where(CourseReview.user_id == user_id)
        )
        chats_result = await db.execute(
            select(func.count()).select_from(ChatSession)
            .where(ChatSession.user_id == user_id)
        )

        return {
            "lessons_completed": lessons_result.scalar() or 0,
            "courses_completed": courses_result.scalar() or 0,
            "quizzes_passed": quizzes_result.scalar() or 0,
            "perfect_quiz": perfect_result.scalar() or 0,
            "reviews_posted": reviews_result.scalar() or 0,
            "ai_chats": chats_result.scalar() or 0,
        }

    def _check_criteria(self, badge: Badge, stats: dict[str, int], streak: LearningStreak) -> bool:
        ct = badge.criteria_type
        cv = badge.criteria_value

        if ct == "streak_days":
            return streak.current_streak >= cv or streak.longest_streak >= cv
        elif ct == "level_reached":
            return streak.level >= cv
        elif ct in stats:
            return stats[ct] >= cv
        return False


gamification_service = GamificationService()

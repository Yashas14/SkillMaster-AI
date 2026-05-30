# ════════════════════════════════════════════════════════════
# Gamification Router — XP, badges, streaks, leaderboard
# ════════════════════════════════════════════════════════════

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user, require_role
from app.database import get_db
from app.models import User
from app.services.gamification import gamification_service

router = APIRouter()


@router.get("/profile")
async def get_gamification_profile(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get the current user's gamification profile."""
    return await gamification_service.get_profile(str(user.id), db)


@router.get("/leaderboard")
async def get_leaderboard(
    limit: int = Query(20, ge=5, le=100),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    """Get the global XP leaderboard."""
    return await gamification_service.get_leaderboard(db, limit=limit)


@router.post("/check-badges")
async def check_badges(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Check and award any newly earned badges."""
    newly_earned = await gamification_service.check_and_award_badges(str(user.id), db)
    return {"newly_earned": newly_earned, "count": len(newly_earned)}


@router.post("/streak")
async def update_streak(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Record daily activity and update streak."""
    streak = await gamification_service.update_streak(str(user.id), db)

    # Also check for streak-related badges
    await gamification_service.check_and_award_badges(str(user.id), db)

    return streak


@router.post("/seed-badges")
async def seed_badges(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_role("admin", "super_admin")),
):
    """Seed badge definitions (admin only)."""
    count = await gamification_service.seed_badges(db)
    return {"seeded": count}

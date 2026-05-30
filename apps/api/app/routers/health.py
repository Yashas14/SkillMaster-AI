# ════════════════════════════════════════════════════════════
# Health Check Router
# ════════════════════════════════════════════════════════════

from datetime import UTC, datetime

from fastapi import APIRouter

router = APIRouter()


@router.get("/health", summary="Health check")
async def health_check():
    return {
        "status": "healthy",
        "service": "skillmaster-api",
        "version": "1.0.0",
        "timestamp": datetime.now(UTC).isoformat(),
        "environment": "production",
    }


@router.get("/", summary="API root")
async def root():
    return {
        "name": "SkillMaster AI API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }

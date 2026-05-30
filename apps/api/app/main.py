# ════════════════════════════════════════════════════════════
# FastAPI Main Application
# ════════════════════════════════════════════════════════════

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.database import Base, engine
from app.middleware import (
    CacheControlMiddleware,
    RequestIDMiddleware,
    SecurityHeadersMiddleware,
    TimingMiddleware,
    TrailingSlashMiddleware,
)
from app.routers import (
    ai_tutor,
    analytics,
    auth,
    certificates,
    code,
    courses,
    enrollments,
    gamification,
    health,
    learning_path,
    notifications,
    progress,
    quiz,
    reviews,
    search,
    users,
    websocket,
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """Application startup and shutdown events."""
    settings = get_settings()
    print(f"🚀 Starting {settings.app_name} v{settings.app_version}")
    print(f"📊 Environment: {settings.environment}")

    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("✅ Database tables created/verified")

    yield

    # Cleanup
    await engine.dispose()
    print("🛑 Application shutdown complete")


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="World-class AI-native learning platform API",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
        redirect_slashes=False,
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Performance & security middleware
    app.add_middleware(TimingMiddleware)
    app.add_middleware(CacheControlMiddleware)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(TrailingSlashMiddleware)

    # Include routers
    app.include_router(health.router, tags=["Health"])
    app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
    app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
    app.include_router(courses.router, prefix="/api/v1/courses", tags=["Courses"])
    app.include_router(enrollments.router, prefix="/api/v1/enrollments", tags=["Enrollments"])
    app.include_router(progress.router, prefix="/api/v1/progress", tags=["Progress"])
    app.include_router(ai_tutor.router, prefix="/api/v1/ai/tutor", tags=["AI Tutor"])
    app.include_router(quiz.router, prefix="/api/v1/quizzes", tags=["Quizzes"])
    app.include_router(code.router, prefix="/api/v1/code", tags=["Code Execution"])
    app.include_router(learning_path.router, prefix="/api/v1/learning-paths", tags=["Learning Paths"])
    app.include_router(search.router, prefix="/api/v1/search", tags=["Search"])
    app.include_router(gamification.router, prefix="/api/v1/gamification", tags=["Gamification"])
    app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["Analytics"])
    app.include_router(certificates.router, prefix="/api/v1/certificates", tags=["Certificates"])
    app.include_router(notifications.router, prefix="/api/v1/notifications", tags=["Notifications"])
    app.include_router(reviews.router, prefix="/api/v1/reviews", tags=["Reviews"])
    app.include_router(websocket.router, prefix="/ws", tags=["WebSocket"])

    @app.exception_handler(Exception)
    async def global_exception_handler(request, exc):
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred",
                },
            },
        )

    return app


app = create_app()

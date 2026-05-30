# ════════════════════════════════════════════════════════════
# Pydantic Schemas
# ════════════════════════════════════════════════════════════

from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator

# ─── Base ──────────────────────────────────────────────────

class SuccessResponse(BaseModel):
    success: bool = True
    data: Any = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ErrorResponse(BaseModel):
    success: bool = False
    error: dict[str, Any]
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class PaginationMeta(BaseModel):
    total: int
    page: int
    limit: int
    total_pages: int
    has_next: bool
    has_prev: bool


class PaginatedResponse(BaseModel):
    data: list[Any]
    meta: PaginationMeta


# ─── Auth ──────────────────────────────────────────────────

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


class RegisterRequest(BaseModel):
    email: EmailStr
    name: str = Field(min_length=2, max_length=255)
    password: str = Field(min_length=8)
    role: str = "student"

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        if v not in ("student", "instructor"):
            raise ValueError("Role must be student or instructor")
        return v


class OAuthRequest(BaseModel):
    provider: str
    provider_id: str
    email: EmailStr
    name: str
    avatar_url: str | None = None


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: "UserResponse"


class RefreshTokenRequest(BaseModel):
    refresh_token: str


# ─── User ──────────────────────────────────────────────────

class UserResponse(BaseModel):
    id: UUID
    email: str
    name: str
    display_name: str | None = None
    avatar_url: str | None = None
    role: str
    bio: str | None = None
    headline: str | None = None
    is_verified: bool
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UserDetailResponse(UserResponse):
    website: str | None = None
    location: str | None = None
    timezone: str | None = None
    language: str
    onboarding_completed: bool
    preferences: dict = {}
    profile: dict = {}
    last_login_at: datetime | None = None


class UpdateUserRequest(BaseModel):
    name: str | None = None
    display_name: str | None = None
    bio: str | None = None
    headline: str | None = None
    avatar_url: str | None = None
    website: str | None = None
    location: str | None = None
    timezone: str | None = None
    language: str | None = None
    preferences: dict | None = None
    profile: dict | None = None


# ─── Course ────────────────────────────────────────────────

class CreateCourseRequest(BaseModel):
    title: str = Field(min_length=3, max_length=500)
    description: str = Field(min_length=10)
    short_description: str = Field(min_length=10, max_length=500)
    category: str
    subcategory: str | None = None
    tags: list[str] = []
    difficulty: str = "beginner"
    language: str = "en"
    price: float = 0
    currency: str = "USD"
    prerequisites: list[str] = []
    learning_outcomes: list[str] = []
    target_audience: list[str] = []

    @field_validator("difficulty")
    @classmethod
    def validate_difficulty(cls, v: str) -> str:
        if v not in ("beginner", "intermediate", "advanced", "expert"):
            raise ValueError("Invalid difficulty level")
        return v


class UpdateCourseRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    short_description: str | None = None
    category: str | None = None
    subcategory: str | None = None
    tags: list[str] | None = None
    difficulty: str | None = None
    language: str | None = None
    price: float | None = None
    status: str | None = None
    thumbnail_url: str | None = None
    preview_video_url: str | None = None
    prerequisites: list[str] | None = None
    learning_outcomes: list[str] | None = None
    target_audience: list[str] | None = None


class CourseResponse(BaseModel):
    id: UUID
    title: str
    slug: str
    short_description: str
    instructor_id: UUID
    thumbnail_url: str | None = None
    category: str
    difficulty: str
    language: str
    status: str
    price: float
    currency: str
    is_free: bool
    estimated_duration_minutes: int
    total_lessons: int
    total_modules: int
    rating: float
    total_ratings: int
    total_enrollments: int
    tags: list = []
    published_at: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True, "populate_by_name": True}


class CourseDetailResponse(CourseResponse):
    description: str
    preview_video_url: str | None = None
    subcategory: str | None = None
    prerequisites: list = []
    learning_outcomes: list = []
    target_audience: list = []
    extra_data: dict = Field(default={}, serialization_alias="metadata")


# ─── Enrollment ────────────────────────────────────────────

class CreateEnrollmentRequest(BaseModel):
    course_id: UUID
    payment_id: str | None = None
    amount_paid: float = 0
    currency: str = "USD"


class EnrollmentResponse(BaseModel):
    id: UUID
    user_id: UUID
    course_id: UUID
    status: str
    progress: float
    enrolled_at: datetime
    completed_at: datetime | None = None
    last_accessed_at: datetime | None = None
    payment_status: str
    amount_paid: float
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Progress ──────────────────────────────────────────────

class UpdateProgressRequest(BaseModel):
    status: str | None = None
    progress_percent: float | None = None
    video_watched_seconds: int | None = None
    last_position: int | None = None
    time_spent_seconds: int | None = None
    notes: str | None = None


class ProgressResponse(BaseModel):
    id: UUID
    user_id: UUID
    lesson_id: UUID
    course_id: UUID
    module_id: UUID
    status: str
    progress_percent: float
    video_watched_seconds: int | None = None
    last_position: int | None = None
    completed_at: datetime | None = None
    time_spent_seconds: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ─── AI Tutor ──────────────────────────────────────────────

class TutorChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=10000)
    session_id: UUID | None = None
    user_id: str | None = None
    course_id: UUID | None = None
    lesson_id: UUID | None = None
    persona: str = "socratic_guide"
    context: str | None = None


# ─── Quiz ──────────────────────────────────────────────────

class GenerateQuizRequest(BaseModel):
    lesson_id: UUID
    course_id: UUID
    num_questions: int = Field(default=10, ge=3, le=30)
    difficulty: str = "intermediate"

    @field_validator("difficulty")
    @classmethod
    def validate_difficulty(cls, v: str) -> str:
        if v not in ("beginner", "intermediate", "advanced", "expert"):
            raise ValueError("Invalid difficulty")
        return v


class SubmitQuizRequest(BaseModel):
    answers: dict[str, str]


class QuizResponse(BaseModel):
    quiz_id: str
    title: str
    total_questions: int
    time_limit_minutes: int
    passing_score: float
    difficulty: str
    questions: list[dict]


class QuizResultResponse(BaseModel):
    attempt_id: str
    score: float
    passed: bool
    earned_points: int
    total_points: int
    bloom_analysis: dict
    results: list[dict]
    recommendations: list[str]


# ─── Code Execution ───────────────────────────────────────

class ExecuteCodeRequest(BaseModel):
    code: str = Field(min_length=1, max_length=50000)
    language: str = "python"
    stdin: str = ""
    timeout: int | None = None

    @field_validator("language")
    @classmethod
    def validate_language(cls, v: str) -> str:
        if v not in ("python", "javascript", "typescript"):
            raise ValueError("Unsupported language")
        return v


class CodeReviewRequest(BaseModel):
    code: str = Field(min_length=1, max_length=50000)
    language: str = "python"
    context: str = ""
    review_type: str = "comprehensive"


class CodeExplainRequest(BaseModel):
    code: str = Field(min_length=1, max_length=50000)
    language: str = "python"


# ─── Learning Path ─────────────────────────────────────────

class CreateLearningPathRequest(BaseModel):
    goal: str = Field(min_length=3, max_length=1000)
    current_skills: list[str] = []
    target_skills: list[str] = []
    weekly_hours: int = Field(default=10, ge=1, le=60)


class UpdatePathItemRequest(BaseModel):
    status: str

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        if v not in ("not_started", "in_progress", "completed", "skipped"):
            raise ValueError("Invalid status")
        return v


class LearningPathResponse(BaseModel):
    path_id: str
    title: str
    description: str
    goal: str
    estimated_weeks: int
    weekly_hours: int
    items: list[dict]
    total_items: int


# ─── Search ────────────────────────────────────────────────

class SearchRequest(BaseModel):
    query: str = Field(min_length=2, max_length=500)
    course_id: UUID | None = None
    top_k: int = Field(default=10, ge=1, le=50)


# ─── Gamification ─────────────────────────────────────────

class BadgeResponse(BaseModel):
    id: UUID
    name: str
    description: str
    icon: str
    category: str
    rarity: str
    xp_reward: int
    earned_at: datetime | None = None

    model_config = {"from_attributes": True}


class LeaderboardEntry(BaseModel):
    rank: int
    user_id: UUID
    name: str
    avatar_url: str | None = None
    total_xp: int
    level: int
    current_streak: int


class GamificationProfileResponse(BaseModel):
    user_id: UUID
    total_xp: int
    level: int
    current_streak: int
    longest_streak: int
    badges: list[BadgeResponse]
    rank: int | None = None
    next_level_xp: int


# ─── Certificate ──────────────────────────────────────────

class CertificateResponse(BaseModel):
    id: UUID
    certificate_number: str
    title: str
    description: str
    course_id: UUID
    issued_at: datetime
    blockchain_tx_hash: str | None = None
    verification_url: str | None = None
    status: str

    model_config = {"from_attributes": True}


class VerifyCertificateResponse(BaseModel):
    valid: bool
    certificate: CertificateResponse | None = None
    blockchain_verified: bool = False
    message: str


# ─── Analytics ─────────────────────────────────────────────

class UserAnalyticsResponse(BaseModel):
    total_courses: int
    completed_courses: int
    total_lessons_completed: int
    total_study_hours: float
    average_quiz_score: float
    current_streak: int
    total_xp: int
    level: int
    weekly_activity: list[dict]
    category_breakdown: list[dict]
    progress_over_time: list[dict]


class InstructorAnalyticsResponse(BaseModel):
    total_courses: int
    total_students: int
    total_revenue: float
    average_rating: float
    course_stats: list[dict]
    enrollment_trend: list[dict]
    completion_rates: list[dict]


# ─── Notifications ─────────────────────────────────────────

class NotificationResponse(BaseModel):
    id: UUID
    type: str
    title: str
    message: str
    data: dict = {}
    is_read: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Course Review ─────────────────────────────────────────

class CreateReviewRequest(BaseModel):
    rating: int = Field(ge=1, le=5)
    title: str = ""
    content: str = ""


class ReviewResponse(BaseModel):
    id: UUID
    course_id: UUID
    user_id: UUID
    rating: int
    title: str
    content: str
    is_verified: bool
    helpful_count: int
    created_at: datetime

    model_config = {"from_attributes": True}

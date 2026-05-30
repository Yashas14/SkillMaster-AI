# ════════════════════════════════════════════════════════════
# SQLAlchemy Models
# ════════════════════════════════════════════════════════════

import uuid
import uuid as _uuid_mod
from datetime import UTC, datetime

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy import (
    Enum as SAEnum,
)
from sqlalchemy.orm import relationship
from sqlalchemy.types import CHAR, TypeDecorator

from app.database import Base


class GUID(TypeDecorator):
    """Platform-independent UUID type. Uses CHAR(36) for SQLite, native UUID for PostgreSQL."""
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            from sqlalchemy.dialects.postgresql import UUID as PG_UUID
            return dialect.type_descriptor(PG_UUID(as_uuid=True))
        return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if isinstance(value, _uuid_mod.UUID):
            return str(value) if dialect.name != "postgresql" else value
        return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if not isinstance(value, _uuid_mod.UUID):
            return _uuid_mod.UUID(str(value))
        return value


# Use JSON (portable) instead of JSONB
JSONB = JSON


def utcnow():
    return datetime.now(UTC)


class User(Base):
    __tablename__ = "users"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    display_name = Column(String(255))
    password_hash = Column(Text)
    avatar_url = Column(Text)
    role = Column(
        SAEnum("student", "instructor", "admin", "super_admin", name="user_role"),
        nullable=False,
        default="student",
    )
    provider = Column(
        SAEnum("email", "google", "github", name="auth_provider"),
        nullable=False,
        default="email",
    )
    provider_id = Column(String(255))
    bio = Column(Text)
    headline = Column(String(500))
    website = Column(Text)
    location = Column(String(255))
    timezone = Column(String(100), default="UTC")
    language = Column(String(10), default="en")
    is_verified = Column(Boolean, nullable=False, default=False)
    is_active = Column(Boolean, nullable=False, default=True)
    onboarding_completed = Column(Boolean, nullable=False, default=False)
    last_login_at = Column(DateTime(timezone=True))
    preferences = Column(JSONB, nullable=False, default=dict)
    profile = Column(JSONB, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)
    deleted_at = Column(DateTime(timezone=True))

    # Relationships
    courses_created = relationship("Course", back_populates="instructor", lazy="selectin")
    enrollments = relationship("Enrollment", back_populates="user", lazy="selectin")
    chat_sessions = relationship("ChatSession", back_populates="user", lazy="selectin")


class Course(Base):
    __tablename__ = "courses"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    title = Column(String(500), nullable=False)
    slug = Column(String(600), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=False)
    short_description = Column(String(500), nullable=False)
    instructor_id = Column(GUID(), ForeignKey("users.id"), nullable=False, index=True)
    thumbnail_url = Column(Text)
    preview_video_url = Column(Text)
    category = Column(String(50), nullable=False)
    subcategory = Column(String(255))
    tags = Column(JSONB, nullable=False, default=list)
    difficulty = Column(String(20), nullable=False, default="beginner")
    language = Column(String(10), nullable=False, default="en")
    status = Column(String(20), nullable=False, default="draft", index=True)
    price = Column(Float, nullable=False, default=0)
    currency = Column(String(3), nullable=False, default="USD")
    is_free = Column(Boolean, nullable=False, default=True)
    estimated_duration_minutes = Column(Integer, nullable=False, default=0)
    total_lessons = Column(Integer, nullable=False, default=0)
    total_modules = Column(Integer, nullable=False, default=0)
    rating = Column(Float, nullable=False, default=0)
    total_ratings = Column(Integer, nullable=False, default=0)
    total_enrollments = Column(Integer, nullable=False, default=0)
    prerequisites = Column(JSONB, nullable=False, default=list)
    learning_outcomes = Column(JSONB, nullable=False, default=list)
    target_audience = Column(JSONB, nullable=False, default=list)
    extra_data = Column("metadata", JSONB, nullable=False, default=dict)
    published_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)
    deleted_at = Column(DateTime(timezone=True))

    # Relationships
    instructor = relationship("User", back_populates="courses_created")
    modules = relationship("CourseModule", back_populates="course", lazy="selectin", order_by="CourseModule.order")
    enrollments = relationship("Enrollment", back_populates="course", lazy="selectin")


class CourseModule(Base):
    __tablename__ = "course_modules"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    course_id = Column(GUID(), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, default="")
    order = Column(Integer, nullable=False)
    estimated_duration_minutes = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)

    # Relationships
    course = relationship("Course", back_populates="modules")
    lessons = relationship("Lesson", back_populates="module", lazy="selectin", order_by="Lesson.order")


class Lesson(Base):
    __tablename__ = "lessons"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    module_id = Column(GUID(), ForeignKey("course_modules.id", ondelete="CASCADE"), nullable=False, index=True)
    course_id = Column(GUID(), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, default="")
    content_type = Column(String(20), nullable=False)
    order = Column(Integer, nullable=False)
    estimated_duration_minutes = Column(Integer, nullable=False, default=0)
    is_free = Column(Boolean, nullable=False, default=False)
    is_required = Column(Boolean, nullable=False, default=True)
    bloom_level = Column(String(20), nullable=False, default="remember")
    content = Column(JSONB, nullable=False, default=dict)
    resources = Column(JSONB, nullable=False, default=list)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)

    # Relationships
    module = relationship("CourseModule", back_populates="lessons")


class Enrollment(Base):
    __tablename__ = "enrollments"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    course_id = Column(GUID(), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(20), nullable=False, default="active")
    enrolled_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)
    completed_at = Column(DateTime(timezone=True))
    expires_at = Column(DateTime(timezone=True))
    progress = Column(Float, nullable=False, default=0)
    last_accessed_at = Column(DateTime(timezone=True))
    payment_status = Column(String(20), nullable=False, default="completed")
    payment_id = Column(String(255))
    amount_paid = Column(Float, nullable=False, default=0)
    currency = Column(String(3), nullable=False, default="USD")
    certificate_id = Column(GUID())
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)

    # Relationships
    user = relationship("User", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")


class LessonProgress(Base):
    __tablename__ = "lesson_progress"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    lesson_id = Column(GUID(), ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False, index=True)
    course_id = Column(GUID(), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    module_id = Column(GUID(), nullable=False)
    status = Column(String(20), nullable=False, default="not_started")
    progress_percent = Column(Float, nullable=False, default=0)
    video_watched_seconds = Column(Integer)
    last_position = Column(Integer)
    completed_at = Column(DateTime(timezone=True))
    time_spent_seconds = Column(Integer, nullable=False, default=0)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    course_id = Column(GUID(), ForeignKey("courses.id", ondelete="SET NULL"))
    lesson_id = Column(GUID(), ForeignKey("lessons.id", ondelete="SET NULL"))
    title = Column(String(500), nullable=False, default="New Chat")
    persona = Column(String(50), nullable=False, default="socratic_guide")
    summary = Column(Text)
    is_active = Column(Boolean, nullable=False, default=True)
    message_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)

    # Relationships
    user = relationship("User", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session", lazy="selectin", order_by="ChatMessage.created_at")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    session_id = Column(GUID(), ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    content_type = Column(String(20), nullable=False, default="text")
    extra_data = Column("metadata", JSONB, default=dict)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)

    # Relationships
    session = relationship("ChatSession", back_populates="messages")


# ─── Phase 2: Quizzes & Learning Paths ────────────────────

class Quiz(Base):
    __tablename__ = "quizzes"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    course_id = Column(GUID(), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)
    lesson_id = Column(GUID(), ForeignKey("lessons.id", ondelete="SET NULL"))
    title = Column(String(500), nullable=False)
    description = Column(Text, default="")
    quiz_type = Column(String(30), nullable=False, default="standard")
    difficulty = Column(String(20), nullable=False, default="intermediate")
    total_questions = Column(Integer, nullable=False, default=0)
    time_limit_minutes = Column(Integer, nullable=False, default=30)
    passing_score = Column(Float, nullable=False, default=70.0)
    max_attempts = Column(Integer, nullable=False, default=3)
    is_published = Column(Boolean, nullable=False, default=False)
    settings = Column(JSONB, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)

    questions = relationship("QuizQuestion", back_populates="quiz", lazy="selectin", order_by="QuizQuestion.order")
    attempts = relationship("QuizAttempt", back_populates="quiz", lazy="selectin")


class QuizQuestion(Base):
    __tablename__ = "quiz_questions"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    quiz_id = Column(GUID(), ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False, index=True)
    question_type = Column(String(30), nullable=False, default="multiple_choice")
    question_text = Column(Text, nullable=False)
    options = Column(JSONB, nullable=False, default=list)
    correct_answer = Column(Text, nullable=False)
    explanation = Column(Text, default="")
    bloom_level = Column(String(20), nullable=False, default="understand")
    points = Column(Integer, nullable=False, default=10)
    order = Column(Integer, nullable=False, default=0)
    extra_data = Column("metadata", JSONB, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)

    quiz = relationship("Quiz", back_populates="questions")


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    quiz_id = Column(GUID(), ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    score = Column(Float, nullable=False, default=0)
    total_points = Column(Integer, nullable=False, default=0)
    earned_points = Column(Integer, nullable=False, default=0)
    time_taken_seconds = Column(Integer, nullable=False, default=0)
    answers = Column(JSONB, nullable=False, default=dict)
    results = Column(JSONB, nullable=False, default=list)
    passed = Column(Boolean, nullable=False, default=False)
    bloom_analysis = Column(JSONB, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)

    quiz = relationship("Quiz", back_populates="attempts")


class LearningPath(Base):
    __tablename__ = "learning_paths"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, default="")
    goal = Column(Text, nullable=False)
    estimated_duration_weeks = Column(Integer, nullable=False, default=4)
    weekly_hours = Column(Integer, nullable=False, default=10)
    difficulty_progression = Column(String(30), nullable=False, default="gradual")
    status = Column(String(20), nullable=False, default="active")
    progress = Column(Float, nullable=False, default=0)
    completed_at = Column(DateTime(timezone=True))
    extra_data = Column("metadata", JSONB, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)

    items = relationship("LearningPathItem", back_populates="learning_path", lazy="selectin", order_by="LearningPathItem.order")


class LearningPathItem(Base):
    __tablename__ = "learning_path_items"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    learning_path_id = Column(GUID(), ForeignKey("learning_paths.id", ondelete="CASCADE"), nullable=False, index=True)
    order = Column(Integer, nullable=False, default=0)
    item_type = Column(String(30), nullable=False, default="course")
    title = Column(String(500), nullable=False)
    description = Column(Text, default="")
    course_id = Column(GUID(), ForeignKey("courses.id", ondelete="SET NULL"))
    estimated_hours = Column(Float, nullable=False, default=2)
    is_required = Column(Boolean, nullable=False, default=True)
    status = Column(String(20), nullable=False, default="not_started")
    completed_at = Column(DateTime(timezone=True))
    extra_data = Column("metadata", JSONB, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)

    learning_path = relationship("LearningPath", back_populates="items")


# ─── Phase 3: Gamification ────────────────────────────────

class Badge(Base):
    __tablename__ = "badges"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=False)
    icon = Column(String(100), nullable=False, default="award")
    category = Column(String(50), nullable=False, default="achievement")
    criteria_type = Column(String(50), nullable=False)
    criteria_value = Column(Integer, nullable=False, default=1)
    xp_reward = Column(Integer, nullable=False, default=50)
    rarity = Column(String(20), nullable=False, default="common")
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)


class UserBadge(Base):
    __tablename__ = "user_badges"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    badge_id = Column(GUID(), ForeignKey("badges.id", ondelete="CASCADE"), nullable=False, index=True)
    earned_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)
    extra_data = Column("metadata", JSONB, nullable=False, default=dict)


class UserXP(Base):
    __tablename__ = "user_xp"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    amount = Column(Integer, nullable=False)
    source = Column(String(50), nullable=False)
    source_id = Column(String(255))
    description = Column(Text, default="")
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)


class LearningStreak(Base):
    __tablename__ = "learning_streaks"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    current_streak = Column(Integer, nullable=False, default=0)
    longest_streak = Column(Integer, nullable=False, default=0)
    last_activity_date = Column(DateTime(timezone=True))
    total_xp = Column(Integer, nullable=False, default=0)
    level = Column(Integer, nullable=False, default=1)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)


# ─── Phase 4: Blockchain Credentials ─────────────────────

class Certificate(Base):
    __tablename__ = "certificates"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    course_id = Column(GUID(), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)
    enrollment_id = Column(GUID(), ForeignKey("enrollments.id", ondelete="SET NULL"))
    certificate_number = Column(String(50), unique=True, nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text, default="")
    issued_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)
    expires_at = Column(DateTime(timezone=True))
    blockchain_tx_hash = Column(String(255))
    blockchain_network = Column(String(50))
    ipfs_hash = Column(String(255))
    verification_url = Column(Text)
    extra_data = Column("metadata", JSONB, nullable=False, default=dict)
    status = Column(String(20), nullable=False, default="issued")
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(String(50), nullable=False)
    title = Column(String(500), nullable=False)
    message = Column(Text, nullable=False)
    data = Column(JSONB, nullable=False, default=dict)
    is_read = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)


class CourseReview(Base):
    __tablename__ = "course_reviews"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    course_id = Column(GUID(), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    rating = Column(Integer, nullable=False)
    title = Column(String(500), default="")
    content = Column(Text, default="")
    is_verified = Column(Boolean, nullable=False, default=False)
    helpful_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)

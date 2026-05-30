# ════════════════════════════════════════════════════════════
# Pytest Configuration & Fixtures
# ════════════════════════════════════════════════════════════

import asyncio
import uuid
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.database import Base, get_db
from app.main import app

# Use a test database
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def test_db(test_engine) -> AsyncGenerator[AsyncSession]:
    session_factory = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client(test_db: AsyncSession) -> AsyncGenerator[AsyncClient]:
    async def override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
def sample_user_data():
    return {
        "email": f"test-{uuid.uuid4().hex[:8]}@example.com",
        "name": "Test User",
        "password": "TestPass123!",
        "role": "student",
    }


@pytest.fixture
def sample_course_data():
    return {
        "title": f"Test Course {uuid.uuid4().hex[:8]}",
        "description": "A comprehensive test course for validation.",
        "short_description": "Test course description",
        "category": "programming",
        "difficulty": "beginner",
        "tags": ["test", "python"],
        "prerequisites": ["Basic programming"],
        "learning_outcomes": ["Learn testing"],
    }

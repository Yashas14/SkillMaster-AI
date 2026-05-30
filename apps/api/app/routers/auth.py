# ════════════════════════════════════════════════════════════
# Authentication Router
# ════════════════════════════════════════════════════════════

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_user,
    hash_password,
    verify_password,
)
from app.config import get_settings
from app.database import get_db
from app.models import User
from app.schemas import (
    LoginRequest,
    OAuthRequest,
    RefreshTokenRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)

router = APIRouter()
settings = get_settings()


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """Register a new user account."""
    # Check existing user
    result = await db.execute(select(User).where(User.email == data.email))
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    # Create user
    user = User(
        email=data.email,
        name=data.name,
        password_hash=hash_password(data.password),
        role=data.role,
        provider="email",
        preferences={
            "theme": "system",
            "emailNotifications": True,
            "pushNotifications": True,
            "weeklyDigest": True,
            "learningReminders": True,
            "language": "en",
            "accessibility": {
                "reducedMotion": False,
                "highContrast": False,
                "fontSize": "medium",
                "screenReader": False,
                "captions": False,
            },
        },
        profile={
            "skills": [],
            "interests": [],
            "learningGoals": [],
            "experienceLevel": "beginner",
        },
    )
    db.add(user)
    await db.flush()

    # Generate tokens
    access_token = create_access_token(user.id, user.role, user.email)
    refresh_token = create_refresh_token(user.id)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.access_token_expire_minutes * 60,
        user=UserResponse.model_validate(user),
    )


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Authenticate and get access tokens."""
    result = await db.execute(
        select(User).where(User.email == data.email, User.is_active.is_(True))
    )
    user = result.scalar_one_or_none()

    if not user or not user.password_hash or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Update last login
    user.last_login_at = datetime.now(UTC)
    await db.flush()

    access_token = create_access_token(user.id, user.role, user.email)
    refresh_token = create_refresh_token(user.id)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.access_token_expire_minutes * 60,
        user=UserResponse.model_validate(user),
    )


@router.post("/oauth", response_model=TokenResponse)
async def oauth_login(data: OAuthRequest, db: AsyncSession = Depends(get_db)):
    """Handle OAuth login/registration."""
    # Check for existing user by provider
    result = await db.execute(
        select(User).where(User.provider == data.provider, User.provider_id == data.provider_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        # Check by email
        result = await db.execute(select(User).where(User.email == data.email))
        user = result.scalar_one_or_none()

        if user:
            # Link provider
            user.provider = data.provider
            user.provider_id = data.provider_id
            if data.avatar_url:
                user.avatar_url = data.avatar_url
        else:
            # Create new user
            user = User(
                email=data.email,
                name=data.name,
                provider=data.provider,
                provider_id=data.provider_id,
                avatar_url=data.avatar_url,
                is_verified=True,
                preferences={
                    "theme": "system",
                    "emailNotifications": True,
                    "pushNotifications": True,
                    "weeklyDigest": True,
                    "learningReminders": True,
                    "language": "en",
                    "accessibility": {
                        "reducedMotion": False,
                        "highContrast": False,
                        "fontSize": "medium",
                        "screenReader": False,
                        "captions": False,
                    },
                },
                profile={
                    "skills": [],
                    "interests": [],
                    "learningGoals": [],
                    "experienceLevel": "beginner",
                },
            )
            db.add(user)

    user.last_login_at = datetime.now(UTC)
    await db.flush()

    access_token = create_access_token(user.id, user.role, user.email)
    refresh_token = create_refresh_token(user.id)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.access_token_expire_minutes * 60,
        user=UserResponse.model_validate(user),
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(data: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    """Refresh access token."""
    payload = decode_token(data.refresh_token)
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    user_id = payload.get("sub")
    result = await db.execute(select(User).where(User.id == user_id, User.is_active.is_(True)))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    access_token = create_access_token(user.id, user.role, user.email)
    new_refresh = create_refresh_token(user.id)

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh,
        expires_in=settings.access_token_expire_minutes * 60,
        user=UserResponse.model_validate(user),
    )


@router.get("/me", response_model=UserResponse)
async def get_me(user: User = Depends(get_current_user)):
    """Get current authenticated user."""
    return UserResponse.model_validate(user)

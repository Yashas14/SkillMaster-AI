# ════════════════════════════════════════════════════════════
# AI Tutor Router (Claude Opus 4.6 Integration)
# ════════════════════════════════════════════════════════════

import json
import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.config import get_settings
from app.database import get_db
from app.models import ChatMessage, ChatSession, User
from app.schemas import TutorChatRequest

router = APIRouter()
settings = get_settings()

PERSONA_PROMPTS = {
    "socratic_guide": """You are a Socratic AI tutor. Your primary method is asking thought-provoking questions
that guide the student to discover answers themselves. Never give direct answers initially.
Instead:
1. Ask a clarifying question to understand their current knowledge level
2. Guide them step by step with increasingly specific questions
3. When they're close to the answer, ask them to synthesize their reasoning
4. Only provide the direct answer after the student has engaged with at least 2-3 questions
5. Always encourage and validate their thinking process
Use code blocks, equations (KaTeX notation), and diagrams when helpful.
Be warm, encouraging, and patient.""",

    "strict_professor": """You are a demanding but fair university professor. You have high standards
and expect precise, well-reasoned answers. Your approach:
1. Challenge vague or imprecise statements
2. Ask students to cite evidence or reasoning
3. Point out logical fallacies or gaps in understanding
4. Demand clarity and rigor in communication
5. Praise excellent reasoning when it appears
Use formal academic language. Reference established scholarship when relevant.
Include equations, code examples, and formal proofs when appropriate.""",

    "friendly_peer": """You are a friendly study buddy who explains concepts in casual,
relatable language. Your approach:
1. Use everyday analogies and real-world examples
2. Break complex topics into bite-sized pieces
3. Share mnemonics and memory tricks
4. Relate concepts to popular culture, games, or everyday life
5. Be encouraging and use humor when appropriate
Use emojis sparingly. Include code snippets with comments explaining each line.
Make learning feel fun and accessible.""",

    "debate_partner": """You are a debate partner who helps students think critically by
arguing both sides of topics. Your approach:
1. Present argument FOR the student's position
2. Then play devil's advocate with counter-arguments
3. Ask the student to refute the counter-arguments
4. Introduce nuance and edge cases
5. Help them develop a more sophisticated understanding
Always be respectful and intellectual. Use evidence-based reasoning.
Cite relevant research or historical examples.""",
}


async def stream_ai_response(
    message: str,
    session_id: str,
    persona: str,
    chat_history: list[dict],
    db: AsyncSession,
):
    """Stream AI response using Claude Opus 4.6."""
    import anthropic

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    system_prompt = PERSONA_PROMPTS.get(persona, PERSONA_PROMPTS["socratic_guide"])
    system_prompt += """

Additional context about the student's environment:
- Platform: SkillMaster AI Learning Platform
- Features available: Code execution, quizzes, flashcards, diagrams
- Always be helpful, accurate, and educational
- Use markdown formatting for structure
- Use ```language blocks for code snippets
- Use $...$ for inline math and $$...$$ for block equations"""

    # Build message history for context window
    messages = []
    for msg in chat_history[-20:]:  # Last 20 messages for context
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": message})

    try:
        full_response = ""

        with client.messages.stream(
            model="claude-opus-4-6",
            max_tokens=4096,
            system=system_prompt,
            messages=messages,
        ) as stream:
            for text in stream.text_stream:
                full_response += text
                chunk = json.dumps({"type": "text", "content": text})
                yield f"data: {chunk}\n\n"

        # Save assistant message to DB
        assistant_msg = ChatMessage(
            session_id=uuid.UUID(session_id),
            role="assistant",
            content=full_response,
            content_type="text",
            extra_data={"model": "claude-opus-4-6", "persona": persona},
        )
        db.add(assistant_msg)

        # Update session
        session_result = await db.execute(
            select(ChatSession).where(ChatSession.id == uuid.UUID(session_id))
        )
        session = session_result.scalar_one_or_none()
        if session:
            session.message_count += 2  # user + assistant
            session.updated_at = datetime.now(UTC)

        await db.commit()

        done_chunk = json.dumps({"type": "done", "session_id": session_id})
        yield f"data: {done_chunk}\n\n"

    except Exception as e:
        error_chunk = json.dumps({"type": "error", "content": str(e)})
        yield f"data: {error_chunk}\n\n"


@router.post("/chat")
async def tutor_chat(
    data: TutorChatRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Stream AI tutor response."""
    if not settings.anthropic_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service not configured. Set ANTHROPIC_API_KEY.",
        )

    user_id = str(user.id)

    # Get or create session
    if data.session_id:
        result = await db.execute(
            select(ChatSession).where(ChatSession.id == data.session_id)
        )
        session = result.scalar_one_or_none()
        if not session:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    else:
        session = ChatSession(
            user_id=uuid.UUID(user_id) if user_id else uuid.uuid4(),
            course_id=data.course_id,
            lesson_id=data.lesson_id,
            title=data.message[:100],
            persona=data.persona,
        )
        db.add(session)
        await db.flush()

    # Save user message
    user_msg = ChatMessage(
        session_id=session.id,
        role="user",
        content=data.message,
        content_type="text",
    )
    db.add(user_msg)
    await db.flush()

    # Get chat history
    history_result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session.id)
        .order_by(ChatMessage.created_at)
    )
    history = [
        {"role": msg.role, "content": msg.content}
        for msg in history_result.scalars().all()
    ]

    return StreamingResponse(
        stream_ai_response(
            message=data.message,
            session_id=str(session.id),
            persona=data.persona,
            chat_history=history[:-1],  # Exclude the message we just added
            db=db,
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/sessions")
async def list_sessions(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """List chat sessions for the authenticated user."""
    result = await db.execute(
        select(ChatSession)
        .where(ChatSession.user_id == user.id, ChatSession.is_active.is_(True))
        .order_by(ChatSession.updated_at.desc())
        .limit(50)
    )
    sessions = result.scalars().all()
    return [
        {
            "id": str(s.id),
            "title": s.title,
            "persona": s.persona,
            "message_count": s.message_count,
            "created_at": s.created_at.isoformat(),
            "updated_at": s.updated_at.isoformat(),
        }
        for s in sessions
    ]

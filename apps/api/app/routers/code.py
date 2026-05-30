# ════════════════════════════════════════════════════════════
# Code Execution & Review Router
# ════════════════════════════════════════════════════════════

from fastapi import APIRouter, Depends

from app.auth import get_current_user
from app.models import User
from app.schemas import CodeExplainRequest, CodeReviewRequest, ExecuteCodeRequest
from app.services.code_executor import code_executor, code_reviewer

router = APIRouter()


@router.post("/execute")
async def execute_code(
    data: ExecuteCodeRequest,
    _user: User = Depends(get_current_user),
):
    """Execute code in a sandboxed environment."""
    result = await code_executor.execute(
        code=data.code,
        language=data.language,
        stdin=data.stdin,
        timeout=data.timeout,
    )
    return result


@router.post("/review")
async def review_code(
    data: CodeReviewRequest,
    _user: User = Depends(get_current_user),
):
    """Get an AI-powered code review."""
    result = await code_reviewer.review(
        code=data.code,
        language=data.language,
        context=data.context,
        review_type=data.review_type,
    )
    return result


@router.post("/explain")
async def explain_code(
    data: CodeExplainRequest,
    _user: User = Depends(get_current_user),
):
    """Get a line-by-line explanation of code."""
    result = await code_reviewer.explain_code(
        code=data.code,
        language=data.language,
    )
    return result

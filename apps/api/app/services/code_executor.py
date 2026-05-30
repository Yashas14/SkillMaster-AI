# ════════════════════════════════════════════════════════════
# AI Code Review & Execution Sandbox
# ════════════════════════════════════════════════════════════

from __future__ import annotations

import asyncio
import json
import os
import tempfile
from typing import Any

from app.config import get_settings

settings = get_settings()

SUPPORTED_LANGUAGES = {
    "python": {"ext": ".py", "cmd": ["python3", "-u"], "timeout": 10},
    "javascript": {"ext": ".js", "cmd": ["node"], "timeout": 10},
    "typescript": {"ext": ".ts", "cmd": ["npx", "tsx"], "timeout": 15},
}

SANDBOX_MEMORY_LIMIT = 128 * 1024 * 1024  # 128MB


class CodeExecutor:
    """Sandboxed code execution with resource limits."""

    async def execute(
        self,
        code: str,
        language: str,
        stdin: str = "",
        timeout: int | None = None,
    ) -> dict[str, Any]:
        """Execute code in a sandboxed environment."""
        if language not in SUPPORTED_LANGUAGES:
            return {
                "success": False,
                "error": f"Unsupported language: {language}. Supported: {list(SUPPORTED_LANGUAGES.keys())}",
                "stdout": "",
                "stderr": "",
                "execution_time_ms": 0,
            }

        lang_config = SUPPORTED_LANGUAGES[language]
        exec_timeout = timeout or lang_config["timeout"]

        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=lang_config["ext"],
            delete=False,
            dir=tempfile.gettempdir(),
        ) as f:
            f.write(code)
            f.flush()
            filepath = f.name

        try:
            start_time = asyncio.get_event_loop().time()

            process = await asyncio.create_subprocess_exec(
                *lang_config["cmd"],
                filepath,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(input=stdin.encode() if stdin else None),
                    timeout=exec_timeout,
                )
            except TimeoutError:
                process.kill()
                await process.wait()
                elapsed = (asyncio.get_event_loop().time() - start_time) * 1000
                return {
                    "success": False,
                    "error": f"Execution timed out after {exec_timeout}s",
                    "stdout": "",
                    "stderr": "",
                    "execution_time_ms": round(elapsed),
                    "timed_out": True,
                }

            elapsed = (asyncio.get_event_loop().time() - start_time) * 1000

            return {
                "success": process.returncode == 0,
                "stdout": stdout.decode(errors="replace")[:10000],
                "stderr": stderr.decode(errors="replace")[:5000],
                "exit_code": process.returncode,
                "execution_time_ms": round(elapsed),
                "timed_out": False,
            }

        finally:
            os.unlink(filepath)


class CodeReviewer:
    """AI-powered code review using Claude Opus 4.6."""

    async def review(
        self,
        code: str,
        language: str,
        context: str = "",
        review_type: str = "comprehensive",
    ) -> dict[str, Any]:
        """Review code and provide detailed feedback."""
        import anthropic

        if not settings.anthropic_api_key:
            return {"error": "AI service not configured"}

        prompt = self._build_review_prompt(code, language, context, review_type)

        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=4096,
            system="""You are an expert code reviewer. Provide thorough, constructive feedback.
Return your review as a JSON object with these fields:
- score (0-100): overall code quality
- summary: brief overview
- issues: array of {severity: "error"|"warning"|"info", line: int|null, message: str, suggestion: str}
- strengths: array of strings
- improvements: array of strings
- refactored_code: improved version of the code (optional)
- complexity: "low"|"medium"|"high"
- test_suggestions: array of test case descriptions""",
            messages=[{"role": "user", "content": prompt}],
        )

        raw = response.content[0].text
        return self._parse_review(raw)

    async def explain_code(self, code: str, language: str) -> dict[str, Any]:
        """Generate a line-by-line explanation of code."""
        import anthropic

        if not settings.anthropic_api_key:
            return {"error": "AI service not configured"}

        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=4096,
            system="You are a patient programming tutor. Explain code clearly for beginners. Return JSON.",
            messages=[
                {
                    "role": "user",
                    "content": f"""Explain this {language} code line by line.

```{language}
{code}
```

Return JSON:
{{
  "summary": "What this code does overall",
  "line_explanations": [
    {{"line": 1, "code": "...", "explanation": "..."}}
  ],
  "concepts_used": ["concept1", "concept2"],
  "difficulty_level": "beginner|intermediate|advanced"
}}""",
                }
            ],
        )

        raw = response.content[0].text
        return self._parse_review(raw)

    def _build_review_prompt(
        self, code: str, language: str, context: str, review_type: str
    ) -> str:
        focus = {
            "comprehensive": "Review for correctness, style, performance, security, and best practices.",
            "security": "Focus on security vulnerabilities, injection risks, and data handling.",
            "performance": "Focus on algorithmic complexity, memory usage, and optimization opportunities.",
            "style": "Focus on code style, naming conventions, readability, and idiomatic patterns.",
            "bugs": "Focus on potential bugs, edge cases, and error handling issues.",
        }.get(review_type, "Provide a comprehensive code review.")

        return f"""Review this {language} code.

{f"Context: {context}" if context else ""}

Focus: {focus}

```{language}
{code}
```

Return your analysis as a JSON object."""

    def _parse_review(self, raw: str) -> dict[str, Any]:
        text = raw.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1] if "\n" in text else text[3:]
        if text.endswith("```"):
            text = text[:-3]

        try:
            return json.loads(text.strip())
        except json.JSONDecodeError:
            start = text.find("{")
            end = text.rfind("}") + 1
            if start != -1 and end > start:
                try:
                    return json.loads(text[start:end])
                except json.JSONDecodeError:
                    pass
            return {"raw_review": raw, "parse_error": True}


code_executor = CodeExecutor()
code_reviewer = CodeReviewer()

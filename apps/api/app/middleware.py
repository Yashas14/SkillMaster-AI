"""
Performance middleware for request timing, response compression, and caching headers.
"""

import hashlib
import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class TimingMiddleware(BaseHTTPMiddleware):
    """Adds X-Process-Time header to all responses."""

    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        duration = time.perf_counter() - start
        response.headers["X-Process-Time"] = f"{duration:.4f}"
        return response


class CacheControlMiddleware(BaseHTTPMiddleware):
    """Adds Cache-Control headers based on route patterns."""

    # Paths that can be cached by the client
    CACHEABLE_PREFIXES = [
        "/api/v1/courses",
        "/api/v1/gamification/leaderboard",
    ]
    # Paths that should never be cached
    NO_CACHE_PREFIXES = [
        "/api/v1/ai/",
        "/api/v1/code/execute",
        "/api/v1/notifications",
    ]

    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        path = request.url.path

        if request.method != "GET":
            response.headers["Cache-Control"] = "no-store"
            return response

        for prefix in self.NO_CACHE_PREFIXES:
            if path.startswith(prefix):
                response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
                return response

        for prefix in self.CACHEABLE_PREFIXES:
            if path.startswith(prefix):
                response.headers["Cache-Control"] = "public, max-age=60, stale-while-revalidate=30"
                return response

        # Default: private, short cache
        response.headers["Cache-Control"] = "private, max-age=0, must-revalidate"
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Adds security headers to all responses."""

    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        return response


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Generates a unique request ID for tracing."""

    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID")
        if not request_id:
            raw = f"{time.time()}-{id(request)}"
            request_id = hashlib.md5(raw.encode()).hexdigest()[:16]

        request.state.request_id = request_id
        response: Response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


class TrailingSlashMiddleware(BaseHTTPMiddleware):
    """Strips trailing slashes from request URLs to avoid 307 redirects that drop auth headers."""

    async def dispatch(self, request: Request, call_next):
        path = request.scope["path"]
        if path != "/" and path.endswith("/"):
            request.scope["path"] = path.rstrip("/")
        return await call_next(request)

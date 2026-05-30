# ════════════════════════════════════════════════════════════
# Embedding Service — Vector embeddings for RAG pipeline
# ════════════════════════════════════════════════════════════

from __future__ import annotations

import hashlib
import json
from typing import TYPE_CHECKING

import httpx

from app.config import get_settings

if TYPE_CHECKING:
    pass

settings = get_settings()

EMBEDDING_DIM = 1536  # OpenAI text-embedding-3-small


class EmbeddingService:
    """Generate text embeddings via OpenAI and cache results in Redis."""

    def __init__(self) -> None:
        self.model = "text-embedding-3-small"
        self.api_url = "https://api.openai.com/v1/embeddings"
        self._redis: object | None = None

    async def _get_redis(self):
        if self._redis is None:
            import redis.asyncio as aioredis
            self._redis = aioredis.from_url(settings.redis_url, decode_responses=True)
        return self._redis

    def _cache_key(self, text: str) -> str:
        h = hashlib.sha256(text.encode()).hexdigest()[:16]
        return f"emb:{self.model}:{h}"

    async def embed_text(self, text: str) -> list[float]:
        """Generate embedding for a single text, with Redis cache."""
        r = await self._get_redis()
        key = self._cache_key(text)
        cached = await r.get(key)
        if cached:
            return json.loads(cached)

        embedding = await self._call_api([text])
        vector = embedding[0]

        await r.setex(key, 86400, json.dumps(vector))  # 24h TTL
        return vector

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for a batch of texts."""
        if not texts:
            return []

        r = await self._get_redis()
        results: list[list[float] | None] = [None] * len(texts)
        uncached_indices: list[int] = []
        uncached_texts: list[str] = []

        # Check cache
        for i, text in enumerate(texts):
            key = self._cache_key(text)
            cached = await r.get(key)
            if cached:
                results[i] = json.loads(cached)
            else:
                uncached_indices.append(i)
                uncached_texts.append(text)

        if uncached_texts:
            embeddings = await self._call_api(uncached_texts)
            for idx, emb in zip(uncached_indices, embeddings, strict=False):
                results[idx] = emb
                key = self._cache_key(texts[idx])
                await r.setex(key, 86400, json.dumps(emb))

        return results  # type: ignore[return-value]

    async def _call_api(self, texts: list[str]) -> list[list[float]]:
        """Call OpenAI embeddings API."""
        if not settings.openai_api_key:
            # Fallback: generate deterministic pseudo-embeddings for dev
            return [self._pseudo_embedding(t) for t in texts]

        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                self.api_url,
                headers={
                    "Authorization": f"Bearer {settings.openai_api_key}",
                    "Content-Type": "application/json",
                },
                json={"model": self.model, "input": texts},
            )
            resp.raise_for_status()
            data = resp.json()
            return [item["embedding"] for item in data["data"]]

    @staticmethod
    def _pseudo_embedding(text: str) -> list[float]:
        """Generate a deterministic pseudo-embedding for dev/testing."""
        h = hashlib.sha256(text.encode()).digest()
        vec: list[float] = []
        for i in range(0, EMBEDDING_DIM * 2, 2):
            byte_pair = h[(i % 32)] ^ h[((i + 1) % 32)]
            val = (byte_pair / 255.0) * 2 - 1
            vec.append(round(val, 6))
        # Pad or truncate to EMBEDDING_DIM
        while len(vec) < EMBEDDING_DIM:
            vec.append(0.0)
        return vec[:EMBEDDING_DIM]


embedding_service = EmbeddingService()

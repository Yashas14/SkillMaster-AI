# ════════════════════════════════════════════════════════════
# RAG Pipeline — Retrieval-Augmented Generation
# Elasticsearch-backed semantic search + context injection
# ════════════════════════════════════════════════════════════

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from app.config import get_settings
from app.services import EMBEDDING_DIM, embedding_service

settings = get_settings()

INDEX_NAME = "skillmaster_content"
INDEX_SETTINGS = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0,
        "analysis": {
            "analyzer": {
                "content_analyzer": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": ["lowercase", "stop", "snowball"],
                }
            }
        },
    },
    "mappings": {
        "properties": {
            "id": {"type": "keyword"},
            "content_type": {"type": "keyword"},
            "course_id": {"type": "keyword"},
            "lesson_id": {"type": "keyword"},
            "module_id": {"type": "keyword"},
            "title": {"type": "text", "analyzer": "content_analyzer"},
            "content": {"type": "text", "analyzer": "content_analyzer"},
            "chunk_index": {"type": "integer"},
            "embedding": {
                "type": "dense_vector",
                "dims": EMBEDDING_DIM,
                "index": True,
                "similarity": "cosine",
            },
            "metadata": {"type": "object", "enabled": False},
            "created_at": {"type": "date"},
        }
    },
}


class RAGPipeline:
    """Retrieval-Augmented Generation pipeline using Elasticsearch as the vector store."""

    def __init__(self) -> None:
        self._es = None

    async def _get_es(self):
        if self._es is None:
            from elasticsearch import AsyncElasticsearch
            self._es = AsyncElasticsearch(
                hosts=[settings.elasticsearch_url] if hasattr(settings, "elasticsearch_url")
                else ["http://localhost:9200"],
                request_timeout=30,
            )
            # Ensure index exists
            if not await self._es.indices.exists(index=INDEX_NAME):
                await self._es.indices.create(index=INDEX_NAME, body=INDEX_SETTINGS)
        return self._es

    # ─── Ingestion ─────────────────────────────────────────

    def chunk_text(self, text: str, chunk_size: int = 512, overlap: int = 64) -> list[str]:
        """Split text into overlapping chunks by word count."""
        words = text.split()
        chunks: list[str] = []
        start = 0
        while start < len(words):
            end = min(start + chunk_size, len(words))
            chunk = " ".join(words[start:end])
            if chunk.strip():
                chunks.append(chunk.strip())
            start += chunk_size - overlap
        return chunks or [text]

    async def ingest_lesson(
        self,
        lesson_id: str,
        course_id: str,
        module_id: str,
        title: str,
        content: str,
        content_type: str = "lesson",
        metadata: dict | None = None,
    ) -> int:
        """Ingest lesson content into the vector store."""
        es = await self._get_es()
        chunks = self.chunk_text(content)
        embeddings = await embedding_service.embed_batch(
            [f"{title}\n\n{chunk}" for chunk in chunks]
        )

        actions: list[dict[str, Any]] = []
        for i, (chunk, emb) in enumerate(zip(chunks, embeddings, strict=False)):
            doc_id = f"{lesson_id}_chunk_{i}"
            doc = {
                "id": doc_id,
                "content_type": content_type,
                "course_id": course_id,
                "lesson_id": lesson_id,
                "module_id": module_id,
                "title": title,
                "content": chunk,
                "chunk_index": i,
                "embedding": emb,
                "metadata": metadata or {},
                "created_at": datetime.now(UTC).isoformat(),
            }
            await es.index(index=INDEX_NAME, id=doc_id, document=doc)
            actions.append(doc)

        return len(actions)

    async def ingest_course_metadata(
        self, course_id: str, title: str, description: str, metadata: dict | None = None
    ) -> str:
        """Ingest course-level metadata."""
        es = await self._get_es()
        emb = await embedding_service.embed_text(f"{title}\n\n{description}")
        doc_id = f"course_{course_id}"
        doc = {
            "id": doc_id,
            "content_type": "course_metadata",
            "course_id": course_id,
            "lesson_id": "",
            "module_id": "",
            "title": title,
            "content": description,
            "chunk_index": 0,
            "embedding": emb,
            "metadata": metadata or {},
            "created_at": datetime.now(UTC).isoformat(),
        }
        await es.index(index=INDEX_NAME, id=doc_id, document=doc)
        return doc_id

    # ─── Retrieval ─────────────────────────────────────────

    async def semantic_search(
        self,
        query: str,
        course_id: str | None = None,
        top_k: int = 5,
        min_score: float = 0.7,
    ) -> list[dict[str, Any]]:
        """Search for relevant content using vector similarity + keyword hybrid."""
        es = await self._get_es()
        query_embedding = await embedding_service.embed_text(query)

        # Hybrid: KNN vector + keyword BM25
        knn_query = {
            "field": "embedding",
            "query_vector": query_embedding,
            "k": top_k,
            "num_candidates": top_k * 4,
        }

        body: dict[str, Any] = {
            "size": top_k,
            "knn": knn_query,
            "query": {
                "bool": {
                    "should": [
                        {"match": {"content": {"query": query, "boost": 0.3}}},
                        {"match": {"title": {"query": query, "boost": 0.5}}},
                    ],
                }
            },
        }

        if course_id:
            body["query"]["bool"]["filter"] = [{"term": {"course_id": course_id}}]
            knn_query["filter"] = {"term": {"course_id": course_id}}

        result = await es.search(index=INDEX_NAME, body=body)

        hits: list[dict[str, Any]] = []
        for hit in result["hits"]["hits"]:
            score = hit.get("_score", 0)
            if score >= min_score:
                source = hit["_source"]
                hits.append({
                    "id": source["id"],
                    "title": source["title"],
                    "content": source["content"],
                    "course_id": source["course_id"],
                    "lesson_id": source["lesson_id"],
                    "content_type": source["content_type"],
                    "score": score,
                    "chunk_index": source.get("chunk_index", 0),
                })
        return hits

    async def get_context_for_tutor(
        self,
        query: str,
        course_id: str | None = None,
        top_k: int = 3,
    ) -> str:
        """Get formatted context string for AI tutor injection."""
        results = await self.semantic_search(query, course_id=course_id, top_k=top_k, min_score=0.5)
        if not results:
            return ""

        context_parts = ["--- Relevant Course Material ---"]
        for r in results:
            context_parts.append(
                f"\n[{r['content_type'].upper()}] {r['title']} (relevance: {r['score']:.2f})\n{r['content']}\n"
            )
        context_parts.append("--- End of Course Material ---\n")
        return "\n".join(context_parts)

    # ─── Deletion ──────────────────────────────────────────

    async def delete_lesson_content(self, lesson_id: str) -> int:
        """Remove all chunks for a lesson."""
        es = await self._get_es()
        result = await es.delete_by_query(
            index=INDEX_NAME,
            body={"query": {"term": {"lesson_id": lesson_id}}},
        )
        return result.get("deleted", 0)

    async def delete_course_content(self, course_id: str) -> int:
        """Remove all content for a course."""
        es = await self._get_es()
        result = await es.delete_by_query(
            index=INDEX_NAME,
            body={"query": {"term": {"course_id": course_id}}},
        )
        return result.get("deleted", 0)


rag_pipeline = RAGPipeline()

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import KnowledgeChunk
from app.rag.embeddings import get_embedding
from app.core.config import settings


class RagRetriever:

    async def retrieve(
        self,
        session: AsyncSession,
        query: str,
        top_k: int | None = None,
        category: str | None = None,
    ):
        top_k = top_k or settings.rag_top_k
        query_embedding = get_embedding(query)

        stmt = select(
            KnowledgeChunk,
            KnowledgeChunk.embedding.cosine_distance(query_embedding).label(
                "distance"
            ),
        )

        if category:
            stmt = stmt.where(KnowledgeChunk.category == category)

        stmt = stmt.order_by("distance").limit(top_k)

        result = await session.execute(stmt)
        rows = result.all()

        results = []
        for chunk, distance in rows:
            similarity = 1 - distance
            if similarity >= settings.rag_similarity_threshold:
                results.append({"chunk": chunk, "similarity": similarity})

        return results

    def build_context(self, results: list[dict]) -> str:
        seen_content = set()
        blocks = []

        for r in results:
            chunk = r["chunk"]

            snippet = chunk.content[:100].strip().lower()
            if snippet in seen_content:
                continue
            seen_content.add(snippet)

            blocks.append(f"[Category: {chunk.category}]\n{chunk.content}")

        return "\n\n---\n\n".join(blocks)

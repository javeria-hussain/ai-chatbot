import asyncio
from sqlalchemy import select
from app.db.session import async_session
from app.db.models import KnowledgeChunk, KnowledgeDocument
from app.rag.embeddings import get_embedding


async def test_search(query: str, top_k: int = 3):
    query_embedding = get_embedding(query)

    async with async_session() as session:
        stmt = (
            select(
                KnowledgeChunk.content,
                KnowledgeDocument.title,
                KnowledgeChunk.embedding.cosine_distance(query_embedding).label("distance"),
            )
            .join(KnowledgeDocument, KnowledgeChunk.document_id == KnowledgeDocument.id)
            .order_by("distance")
            .limit(top_k)
        )
        result = await session.execute(stmt)
        rows = result.all()

        print(f"\nQuery: '{query}'\n")
        for i, row in enumerate(rows, 1):
            print(f"{i}. [{row.title}] (distance: {row.distance:.4f})")
            print(f"   {row.content[:150]}...\n")


if __name__ == "__main__":
    asyncio.run(test_search("What services does MoinSystems AI offer?"))
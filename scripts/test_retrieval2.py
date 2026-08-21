import asyncio

from app.db.session import get_db
from app.rag.retriever import RagRetriever


async def main():
    retriever = RagRetriever()
    async for session in get_db():
        results = await retriever.retrieve(
            session, "What services does MoinSystems AI offer?"
        )
        for r in results:
            print(round(r["similarity"], 3), "-", r["chunk"].content[:80])
        print("\n--- Context for LLM ---\n")
        print(retriever.build_context(results))
        break


if __name__ == "__main__":
    asyncio.run(main())




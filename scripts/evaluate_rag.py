import asyncio
import json
from pathlib import Path

from app.db.session import async_session
from app.rag.retriever import RagRetriever

EVAL_PATH = Path("data/eval_set.json")


async def run_evaluation():
    with open(EVAL_PATH, "r", encoding="utf-8") as f:
        eval_set = json.load(f)

    retriever = RagRetriever()
    hits_top3 = 0
    hits_top5 = 0
    failures = []

    async with async_session() as session:
        for case in eval_set:
            results = await retriever.retrieve(session, case["query"], top_k=5)
            retrieved_ids = [r["chunk"].external_id.replace("_chunk_0", "") for r in results]

            top3 = retrieved_ids[:3]
            top5 = retrieved_ids[:5]

            if case["expected_record"] in top3:
                hits_top3 += 1
            if case["expected_record"] in top5:
                hits_top5 += 1
            else:
                failures.append({
                    "id": case["id"],
                    "query": case["query"],
                    "expected": case["expected_record"],
                    "got": retrieved_ids,
                })

    total = len(eval_set)
    print(f"\nTotal queries: {total}")
    print(f"Top-3 Recall: {hits_top3}/{total} ({100*hits_top3/total:.1f}%)")
    print(f"Top-5 Recall: {hits_top5}/{total} ({100*hits_top5/total:.1f}%)")

    if failures:
        print(f"\n--- Failures ({len(failures)}) ---")
        for f in failures:
            print(f"[{f['id']}] Query: {f['query']}")
            print(f"   Expected: {f['expected']} | Got: {f['got']}\n")


if __name__ == "__main__":
    asyncio.run(run_evaluation())
import asyncio
import json
import sys
from pathlib import Path

from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.db.session import async_session
from app.db.models import KnowledgeDocument, KnowledgeChunk
from app.rag.embeddings import get_embedding

DATASET_PATH = Path("data/MoinSystems_AI_Public_Chatbot_RAG_Dataset_v2.jsonl")


def load_jsonl(path: Path) -> list[dict]:
    records = []
    with open(path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as e:
                print(f"Line {line_num} parse nahi hui, skip: {e}")
    return records


def validate_record(rec: dict) -> bool:
    required = ["id", "title", "content", "text"]
    for field in required:
        if not rec.get(field):
            print(f"'{rec.get('id', '???')}' mein '{field}' missing/empty, skip")
            return False
    return True


async def upsert_record(session, rec: dict):
    # 1. Embedding banao (ye 'text' field se banega, ye pura embedding-friendly text hai)
    embedding = get_embedding(rec["text"])
    if len(embedding) != 384:
        raise ValueError(f"Dimension mismatch: mila {len(embedding)}, expected 384")

    # 2. knowledge_document upsert — external_id pe conflict check
    doc_stmt = pg_insert(KnowledgeDocument).values(
        external_id=rec["id"],
        title=rec["title"],
        source=rec.get("metadata", {}).get("source_basis"),
    )
    doc_stmt = doc_stmt.on_conflict_do_update(
        index_elements=["external_id"],
        set_={
            "title": doc_stmt.excluded.title,
            "source": doc_stmt.excluded.source,
        },
    ).returning(KnowledgeDocument.id)

    result = await session.execute(doc_stmt)
    document_id = result.scalar_one()

    # 3. knowledge_chunk upsert — external_id pe conflict check
    chunk_external_id = f"{rec['id']}_chunk_0"
    category = rec.get("category")
    tags = ",".join(rec.get("tags", [])) if rec.get("tags") else None
    intents = ",".join(rec.get("intents", [])) if rec.get("intents") else None

    chunk_stmt = pg_insert(KnowledgeChunk).values(
        external_id=chunk_external_id,
        document_id=document_id,
        content=rec["content"],
        embedding=embedding,
        category=category,
        tags=tags,
        intents=intents,
    )
    chunk_stmt = chunk_stmt.on_conflict_do_update(
        index_elements=["external_id"],
        set_={
            "content": chunk_stmt.excluded.content,
            "embedding": chunk_stmt.excluded.embedding,
            "document_id": chunk_stmt.excluded.document_id,
            "category": chunk_stmt.excluded.category,
            "tags": chunk_stmt.excluded.tags,
            "intents": chunk_stmt.excluded.intents,
        },
    )
    await session.execute(chunk_stmt)


async def run_ingestion():
    print(f"Reading: {DATASET_PATH}")
    records = load_jsonl(DATASET_PATH)
    print(f"Total lines parsed: {len(records)}")

    ids = [r["id"] for r in records if r.get("id")]
    dupes = {i for i in ids if ids.count(i) > 1}
    if dupes:
        print(f"Dataset mein duplicate IDs mile: {dupes}")
        sys.exit(1)

    valid_records = [r for r in records if validate_record(r)]
    print(f"Valid records: {len(valid_records)} / {len(records)}")

    success, failed = 0, 0
    async with async_session() as session:
        for rec in valid_records:
            try:
                await upsert_record(session, rec)
                success += 1
            except Exception as e:
                print(f"Failed for '{rec['id']}': {e}")
                failed += 1
        await session.commit()

    print(f"\nIngestion complete: {success} succeeded, {failed} failed")


if __name__ == "__main__":
    asyncio.run(run_ingestion())
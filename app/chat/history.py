from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from app.db.models import ChatSession, ChatMessage


async def get_or_create_session(db: AsyncSession, session_token: UUID | None) -> ChatSession:
    if session_token:
        result = await db.execute(select(ChatSession).where(ChatSession.session_token == session_token))
        session = result.scalar_one_or_none()
        if session:
            return session
    
    session = ChatSession()
    db.add(session)
    await db.flush()  
    return session


async def save_message(db: AsyncSession, session_id: UUID, role: str, content: str, intent: str | None = None) -> ChatMessage:
    message = ChatMessage(session_id=session_id, role=role, content=content, intent=intent)
    db.add(message)
    await db.flush()
    return message


async def get_recent_history(db: AsyncSession, session_id: UUID, limit: int = 10) -> list[dict]:
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.asc())
        .limit(limit)
    )
    messages = result.scalars().all()
    return [{"role": m.role, "content": m.content} for m in messages]
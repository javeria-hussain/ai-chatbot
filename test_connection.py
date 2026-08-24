import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.core.config import settings


async def test():
    engine = create_async_engine(settings.database_url)
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT version();"))
        print(result.fetchone())
    await engine.dispose()


asyncio.run(test())

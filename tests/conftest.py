import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.core.config import settings
from app.db.session import get_db
from app.main import app


@pytest_asyncio.fixture
async def db_session():
    
    engine = create_async_engine(settings.database_url)
    connection = await engine.connect()
    transaction = await connection.begin()

    
    TestSessionLocal = async_sessionmaker(bind=connection, expire_on_commit=False)
    session = TestSessionLocal()

    yield session

    
    await session.close()
    await transaction.rollback()
    await connection.close()
    await engine.dispose()


@pytest_asyncio.fixture
async def client(db_session):
    
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()

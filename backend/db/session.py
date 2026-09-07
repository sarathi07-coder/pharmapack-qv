"""
Database Session & Connection Management
Supports async SQLite for instant zero-dependency execution and PostgreSQL with pgvector for production.
"""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import create_engine
from backend.core.config import settings
from backend.models.base import Base

# Async Engine for FastAPI async endpoints
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    class_=AsyncSession
)

# Synchronous Engine for offline scripts, seed data, and testing
sync_engine = create_engine(
    settings.SYNC_DATABASE_URL,
    echo=False
)

async def init_db():
    """Create all database tables on startup"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency injection provider for FastAPI endpoints"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

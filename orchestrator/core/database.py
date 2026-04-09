"""
Database setup — SQLite via SQLAlchemy async
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from core.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=False)
SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def init_db() -> None:
    # Panggil model impor agar SQLAlchemy menyadari blueprint sebelum membuat tabel.
    import core.models
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db():
    """Dependency injection untuk FastAPI route."""
    async with SessionLocal() as session:
        yield session

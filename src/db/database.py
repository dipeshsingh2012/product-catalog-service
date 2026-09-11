from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from src.config import settings


class Base(DeclarativeBase):
    pass


_engine = None
_AsyncSessionLocal = None


def get_engine():
    global _engine
    if _engine is None:
        if not settings.DATABASE_URL:
            raise ValueError(
                "Database connection URL is not set! Please provide DATABASE_URL or SQL_DB in your environment/.env pointing to your Neon PostgreSQL instance."
            )
        _engine = create_async_engine(
            settings.DATABASE_URL,
            echo=False,
            future=True,
            pool_pre_ping=True,
            pool_recycle=300,
        )
    return _engine


def get_sessionmaker():
    global _AsyncSessionLocal
    if _AsyncSessionLocal is None:
        _AsyncSessionLocal = async_sessionmaker(
            bind=get_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
    return _AsyncSessionLocal


class _LazyEngineProxy:
    def __getattr__(self, name):
        return getattr(get_engine(), name)


class _LazySessionMakerProxy:
    def __call__(self, *args, **kwargs):
        return get_sessionmaker()(*args, **kwargs)

    def __getattr__(self, name):
        return getattr(get_sessionmaker(), name)


engine = _LazyEngineProxy()
AsyncSessionLocal = _LazySessionMakerProxy()


async def get_db():
    session_factory = get_sessionmaker()
    async with session_factory() as session:
        try:
            yield session
        finally:
            await session.close()

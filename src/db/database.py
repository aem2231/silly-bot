from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from core.config import settings
from typing import AsyncGenerator

db_url = f"sqlite+aiosqlite:///{settings.DB_PATH}"

# Connect args specific to SQLite for async use
connect_args: dict[str, bool] = {
    "check_same_thread": False
}

engine = create_async_engine(db_url, connect_args=connect_args, echo=False)

AsyncSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False
)

Base = declarative_base()

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from core.config import settings
from functools import wraps
from typing import Callable, Any
import inspect

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

def with_db(func: Callable) -> Callable:
    """Decorator to provide an AsyncSession."""
    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        async with AsyncSessionLocal() as session:
            kwargs['db'] = session
            return await func(*args, **kwargs)

    sig = inspect.signature(func)
    if 'db' in sig.parameters:
        new_params = [p for name, p in sig.parameters.items() if name != 'db']
        wrapper.__signature__ = sig.replace(parameters=new_params) # type: ignore

    return wrapper

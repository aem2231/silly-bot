from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from db.models.users import User
from db.models.server import Server
from typing import Optional, List
import datetime

async def register_user(db: AsyncSession, user_id: str, initial_balance: int = 0) -> User:
    db_user = User(user_id=str(user_id), balance=initial_balance)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def get_user_by_id(db: AsyncSession, user_id: str) -> Optional[User]:
    result = await db.execute(select(User).filter(User.user_id == str(user_id)))
    return result.scalars().first()

async def get_user_balance(db: AsyncSession, user_id: str) -> int:
    db_user = await get_user_by_id(db, user_id)
    if not db_user:
        db_user = await register_user(db, user_id)
    return db_user.balance

async def update_user_balance(db: AsyncSession, user_id: str, amount: int) -> User:
    db_user = await get_user_by_id(db, user_id)
    if not db_user:
        db_user = await register_user(db, user_id)

    db_user.balance += amount
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def register_server(db: AsyncSession, guild_id: str) -> Server:
    db_server = Server(guild_id=str(guild_id))
    db.add(db_server)
    await db.commit()
    await db.refresh(db_server)
    return db_server

async def get_server_by_id(db: AsyncSession, guild_id: str) -> Optional[Server]:
    result = await db.execute(select(Server).filter(Server.guild_id == str(guild_id)))
    return result.scalars().first()

async def get_daily_cooldown(db: AsyncSession, user_id: str) -> int:
    db_user = await get_user_by_id(db, user_id)
    if not db_user:
        db_user = await register_user(db, user_id)
    return db_user.last_daily

async def update_daily_cooldown(db: AsyncSession, user_id: str) -> None:
    db_user = await get_user_by_id(db, user_id)
    if not db_user:
        db_user = await register_user(db, user_id)
    db_user.last_daily = int(datetime.datetime.now().timestamp())
    await db.commit()

async def get_work_cooldown(db: AsyncSession, user_id: str) -> int:
    db_user = await get_user_by_id(db, user_id)
    if not db_user:
        db_user = await register_user(db, user_id)
    return db_user.last_work

async def update_work_cooldown(db: AsyncSession, user_id: str) -> None:
    db_user = await get_user_by_id(db, user_id)
    if not db_user:
        db_user = await register_user(db, user_id)
    db_user.last_work = int(datetime.datetime.now().timestamp())
    await db.commit()

async def get_bank_rob_cooldown(db: AsyncSession, guild_id: str) -> int:
    db_server = await get_server_by_id(db, guild_id)
    if not db_server:
        db_server = await register_server(db, guild_id)
    return db_server.last_bank_rob

async def update_bank_rob_cooldown(db: AsyncSession, guild_id: str) -> None:
    db_server = await get_server_by_id(db, guild_id)
    if not db_server:
        db_server = await register_server(db, guild_id)
    db_server.last_bank_rob = int(datetime.datetime.now().timestamp())
    await db.commit()

async def get_user_level(db: AsyncSession, user_id: str) -> int:
    db_user = await get_user_by_id(db, user_id)
    if not db_user:
        db_user = await register_user(db, user_id)
    return db_user.level

async def update_user_level(db: AsyncSession, user_id: str, level: int) -> None:
    db_user = await get_user_by_id(db, user_id)
    if not db_user:
        db_user = await register_user(db, user_id)
    db_user.level = level
    await db.commit()

async def get_user_xp(db: AsyncSession, user_id: str) -> int:
    db_user = await get_user_by_id(db, user_id)
    if not db_user:
        db_user = await register_user(db, user_id)
    return db_user.xp

async def update_user_xp(db: AsyncSession, user_id: str, xp: int) -> None:
    db_user = await get_user_by_id(db, user_id)
    if not db_user:
        db_user = await register_user(db, user_id)
    db_user.xp = xp
    await db.commit()

async def get_user_level_xp(db: AsyncSession, user_id: str) -> int:
    db_user = await get_user_by_id(db, user_id)
    if not db_user:
        db_user = await register_user(db, user_id)
    return db_user.level_xp

async def update_user_level_xp(db: AsyncSession, user_id: str, level_xp: int) -> None:
    db_user = await get_user_by_id(db, user_id)
    if not db_user:
        db_user = await register_user(db, user_id)
    db_user.level_xp = level_xp
    await db.commit()

async def get_user_level_progress(db: AsyncSession, user_id: str) -> float:
    db_user = await get_user_by_id(db, user_id)
    if not db_user:
        db_user = await register_user(db, user_id)
    return db_user.xp / db_user.level_xp

async def get_top_users_global(db: AsyncSession, limit: int = 10) -> List[User]:
    result = await db.execute(select(User).order_by(User.level.desc()).limit(limit))
    return result.scalars().all()

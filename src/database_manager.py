import aiosqlite
from pathlib import Path
import datetime
from functools import wraps
import logging
import asyncio
from typing import Optional, Type, Tuple, Any
import constants as const

logger = logging.getLogger(__name__)

def db_cursor(
  max_retries: int = 3,
  retry_delay: float = 0.1,
  retry_on: Tuple[Type[Exception], ...] = (aiosqlite.OperationalError, aiosqlite.DatabaseError)
):
  def decorator(func):
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
      last_exception = None

      for attempt in range(max_retries + 1):
        try:
          # Check connection health before proceeding
          await self._ensure_connection_alive()

          async with self.conn.cursor() as cursor:
            try:
              result = await func(self, cursor, *args, **kwargs)
              await self.conn.commit()

              if attempt > 0:
                logger.info(f"Database operation {func.__name__} succeeded on attempt {attempt + 1}")

              return result

            except Exception as e:
              # Log detailed error information
              logger.error(
                f"Database error in {func.__name__}: {type(e).__name__}: {e}",
                extra={
                  'function': func.__name__,
                  'attempt': attempt + 1,
                  'args': str(args)[:200],  # Truncate for safety
                  'kwargs': {k: str(v)[:100] for k, v in kwargs.items()}
                }
              )

              await self.conn.rollback()
              raise

        except retry_on as e:
          last_exception = e
          if attempt < max_retries:
            logger.warning(
              f"Retrying database operation {func.__name__} "
              f"(attempt {attempt + 1}/{max_retries + 1}) after error: {e}"
            )
            await asyncio.sleep(retry_delay * (2 ** attempt))  # Exponential backoff
            continue
          else:
            logger.error(f"Database operation {func.__name__} failed after {max_retries + 1} attempts")
            raise

        except Exception as e:
          # Non-retryable exceptions
          self._log_critical_error(func.__name__, e, args, kwargs)
          raise

      # This shouldn't be reached, but just in case
      if last_exception:
        raise last_exception

    return wrapper
  return decorator

class Database():
  def __init__(self):
    self.conn = None

  async def __aenter__(self):
    self.conn = await aiosqlite.connect(const.DB_PATH)
    await self._db_setup()
    return self

  async def __aexit__(self, exec_type, exc_value, exc_traceback):
    if self.conn:
      try:
        await self.conn.close()
      except Exception as e:
        logger.error(f"Error closing database connection: {e}")

  async def _ensure_connection_alive(self):
    """Verify the database connection is still alive"""
    try:
      await self.conn.execute("SELECT 1")
    except Exception as e:
      logger.error(f"Database connection check failed: {e}")
      # Attempt to reconnect
      await self._reconnect()

  async def _reconnect(self):
    """Attempt to reconnect to the database"""
    try:
      if self.conn:
        await self.conn.close()
    except Exception:
      pass  # Connection might already be closed

    try:
      self.conn = await aiosqlite.connect(const.DB_PATH)
      logger.info("Database reconnection successful")
    except Exception as e:
      logger.critical(f"Failed to reconnect to database: {e}")
      raise

  def _log_critical_error(self, func_name: str, error: Exception, args: tuple, kwargs: dict):
    """Log critical database errors with full context"""
    logger.critical(
      f"Critical database error in {func_name}",
      extra={
        'error_type': type(error).__name__,
        'error_message': str(error),
        'function': func_name,
        'args': str(args)[:500],
        'kwargs': {k: str(v)[:200] for k, v in kwargs.items()},
        'connection_state': 'closed' if not self.conn else 'open'
      },
      exc_info=True
    )

  async def _db_setup(self):
    setup_statements = [
      """create table if not exists `users` (
        `user_id` TEXT not null,
        `balance` INT null default 0,
        `last_daily` INT null default 0,
        `last_work` INT null default 0,
        primary key (`user_id`)
      )""",
      """create table if not exists `server` (
        `guild_id` TEXT not null,
        `last_bank_rob` INT null default 0,
        primary key (`guild_id`)
      )""",
      """create table if not exists `levels` (
        `user_id` TEXT not null,
        `level` INT not null default 1,
        `xp` INT not null default 0,
        primary key (`user_id`)
      )"""
    ]

    try:
      async with self.conn.cursor() as cursor:
        for statement in setup_statements:
          await cursor.execute(statement)
      await self.conn.commit()
      logger.info("Database setup completed successfully")
    except Exception as e:
      logger.error(f"Database setup failed: {e}")
      raise

  @db_cursor()
  async def update_cooldown(self, cursor, column, table, id_column, id):
    unix_time = datetime.datetime.now().timestamp()
    statement = f"UPDATE {table} SET {column} = :unix_time WHERE {id_column} = :id"
    await cursor.execute(statement, {f"unix_time": unix_time, "id": id})

  @db_cursor()
  async def get_cooldown_start(self, cursor, cooldown_column, table, id_column, id):
    await self.check_entity_presence(cursor, table, id_column, id)
    statement = f"SELECT {cooldown_column} FROM {table} WHERE {id_column} = :id"
    await cursor.execute(statement, {"id": id})
    row = await cursor.fetchone()
    if row is None:
      logger.warning(f"No cooldown data found for {id} in {table}.{cooldown_column}")
      return 0
    return row[0]

  @db_cursor()
  async def update_balance(self, cursor, id, balance):
    await self.check_entity_presence(cursor, const.USER_TABLE, const.USER_COLUMN, id)
    statement = f"UPDATE {const.USER_TABLE} SET balance = :coins WHERE {const.USER_COLUMN} = :id"
    await cursor.execute(statement, {"coins": balance, "id": id})
    return True

  @db_cursor()
  async def get_balance(self, cursor, id):
    await self.check_entity_presence(cursor, const.USER_TABLE, const.USER_COLUMN, id)
    statement = f"SELECT balance FROM {const.USER_TABLE} WHERE {const.USER_COLUMN} = :id"
    await cursor.execute(statement, {"id": id})
    row = await cursor.fetchone()
    if row is None:
      logger.warning(f"No balance data found for user {id}")
      return 0
    return row[0]

  async def check_entity_presence(self, cursor, table, id_column, id_value):
    statement = f"SELECT 1 FROM {table} WHERE {id_column} = :id_value LIMIT 1"
    await cursor.execute(statement, {"id_value": id_value})
    row = await cursor.fetchone()

    if row is None:
      logger.debug(f"Adding new entity to {table}: {id_column}={id_value}")
      await self.add_entity(cursor, table, id_column, id_value)

  async def add_entity(self, cursor, table, id_column, id_value):
    try:
      statement = f"INSERT INTO {table} ({id_column}) VALUES (:id_value)"
      await cursor.execute(statement, {"id_value": id_value})
      logger.debug(f"Successfully added entity to {table}: {id_column}={id_value}")
    except aiosqlite.IntegrityError as e:
      # Handle race condition where entity was created between check and insert
      logger.debug(f"Entity already exists in {table}: {id_column}={id_value}")
    except Exception as e:
      logger.error(f"Failed to add entity to {table}: {e}")
      raise

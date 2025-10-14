import aiosqlite
from pathlib import Path
import datetime
from functools import wraps
import constants

def db_cursor(func):
  @wraps(func)
  async def wrapper(self, *args, **kwargs):
    async with self.conn.cursor() as cursor:
      try:
        result = await func(self, cursor, *args, **kwargs)
        await self.conn.commit()
        return result
      except Exception as e:
        print(f"Database error: {e}")
        await self.conn.rollback()
        raise
  return wrapper

class Database():
  def __init__(self):
    self.conn = None

  async def __aenter__(self):
    self.conn = await aiosqlite.connect(constants.DB_PATH)
    await self._db_setup()
    return self

  async def __aexit__(self, exec_type, exc_value, exc_traceback):
    if self.conn:
        await self.conn.close()

  async def _db_setup(self):
    setup_statements = [
      """create table if not exists `users` (
        `user_id` TEXT not null,
        `balance` INT null default 0,
        `last_daily` INT null,
        `last_work` INT null,
        primary key (`user_id`)
      )""",
      """create table if not exists `server` (
        `guild_id` TEXT not null,
        `last_bank_rob` INT null,
        primary key (`guild_id`)
      )""",
      """create table if not exists `levels` (
        `user_id` TEXT not null,
        `level` INT not null default 1,
        `xp` INT not null default 0,
        primary key (`user_id`)
      )"""
    ]
    async with self.conn.cursor() as cursor:
        for statement in setup_statements:
            await cursor.execute(statement)

  async def calculate_remaining_cooldown(self, cooldown_length, cooldown_start_unix_timestamp):
    current_time = datetime.datetime.now().timestamp()
    if cooldown_length + cooldown_start_unix_timestamp < current_time:
      return 0
    return (cooldown_start_unix_timestamp + cooldown_length) - current_time

  @db_cursor
  async def update_cooldown(self, cursor, column, table, id_column, id):
    unix_time = datetime.datetime.now().timestamp()
    statement = f"UPDATE {table} SET {column} = :unix_time WHERE {id_column} = :id"
    await cursor.execute(statement, {f"unix_time": unix_time, "id": id})

  @db_cursor
  async def get_cooldown_start(self, cursor, task_cooldown, table, cooldown_length, id_column, id):
    await self.check_entity_presence(cursor, table, id_column, id)
    statement = f"SELECT {task_cooldown} FROM {table} WHERE {id_column} = :id"
    await cursor.execute(statement, {"id": id})
    row = await cursor.fetchone()
    if row is None:
      await self.update_cooldown(task_cooldown, table, id_column, id)
      return 0
    cooldown_start_time = row[0]
    if cooldown_start_time is None:
      await self.update_cooldown(task_cooldown, table, id_column, id)
      return 0
    remaining_cooldown_seconds = await self.calculate_remaining_cooldown(cooldown_length, cooldown_start_time)
    return remaining_cooldown_seconds

  @db_cursor
  async def update_coins(self, cursor, id, coins):
    await self.check_entity_presence(cursor, constants.USER_TABLE, constants.USER_COLUMN, id)
    statement = f"UPDATE {constants.USER_TABLE} SET balance = :coins WHERE {constants.USER_COLUMN} = :id"
    await cursor.execute(statement, {"coins": coins, "id": id})
    return True

  @db_cursor
  async def get_balance(self, cursor, id):
    await self.check_entity_presence(cursor, constants.USER_TABLE, constants.USER_COLUMN, id)
    statement = f"SELECT balance FROM {constants.USER_TABLE} WHERE {constants.USER_COLUMN} = :id"
    await cursor.execute(statement, {"id": id})
    row = await cursor.fetchone()
    return row[0]

  async def check_entity_presence(self, cursor, table, id_column, id_value):
    statement = f"SELECT 1 FROM {table} WHERE {id_column} = :id_value LIMIT 1"
    await cursor.execute(statement, {"id_value": id_value})
    row = await cursor.fetchone()

    if row is None:
      await self.add_entity(cursor, table, id_column, id_value)

  async def add_entity(self, cursor, table, id_column, id_value):
    statement = f"INSERT INTO {table} ({id_column}) VALUES (:id_value)"
    await cursor.execute(statement, {"id_value": id_value})

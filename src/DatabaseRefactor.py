import sqlite3
from pathlib import Path
import datetime
from functools import wraps

def db_cursor(func):
  @wraps(func) # a wrapper function handle error handling for database operation
  def wrapper(self, *args, **kwargs):
    cursor = self.conn.cursor()
    try:
      result = func(self, cursor, *args, **kwargs)
      self.conn.commit()
      print('hi')
      return result
    except sqlite3.OperationalError as e:
      print(f"Database error: {e}")
      self.conn.rollback()
      return None
  return wrapper

class EconomyDatabase():
  def __init__(self):
    self.db_path = Path("db1/database.db")
    self.conn = sqlite3.connect(self.db_path)
    self.db_setup()

  def calculate_remaining_cooldown(self, cooldown_length, cooldown_start_unix_timestamp):
    current_time = datetime.datetime.now().timestamp()
    if cooldown_length + cooldown_start_unix_timestamp < current_time:
      return True
    return False

  @db_cursor
  def db_setup(self, cursor):
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

    for statement in setup_statements:
      print(statement)
      cursor.execute(statement)

  @db_cursor
  def check_cooldown(self, cursor, task, table, cooldown_length, cooldown_start_unix_timestamp, id):
    statement = f"SELECT f{task} FROM {table} WHERE {id} = :id"
    cursor.execute(statement, {"id": id})

  @db_cursor
  def update_coins(self, id, coins):
    pass

  @db_cursor
  def get_balance(self, id):
    pass

  @db_cursor
  def check_entity_presence(self, entity_type, id):
    pass

db1 = EconomyDatabase()

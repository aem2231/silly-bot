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
      return result
    except Exception as e:
      print(f"Database error: {e}")
      self.conn.rollback()
      return None
  return wrapper

class EconomyDatabase():
  def __init__(self):
    self.db_path = Path("db1/database.db")
    self.user_table = "users"
    self.guild_table = "server"
    self.user_column = "user_id"
    self.guild_column = "guild_id"
    self.conn = sqlite3.connect(self.db_path)
    self.db_setup()

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
      cursor.execute(statement)

  def calculate_remaining_cooldown(self, cooldown_length, cooldown_start_unix_timestamp):
    current_time = datetime.datetime.now().timestamp()
    if cooldown_length + cooldown_start_unix_timestamp < current_time:
      return 0
    return (cooldown_start_unix_timestamp + cooldown_length) - current_time

  @db_cursor
  def check_cooldown(self, cursor, task, table, cooldown_length, id_column, id):
    self.check_entity_presence(cursor, table, id_column, id)
    statement = f"SELECT {task} FROM {table} WHERE {id_column} = :id"
    cursor.execute(statement, {"id": id})
    row = cursor.fetchone()
    if row is None:
      return 0
    cooldown_start_time = row[0]
    if cooldown_start_time is None:
      return 0
    remaining_cooldown_seconds = self.calculate_remaining_cooldown(cooldown_length, cooldown_start_time)
    return remaining_cooldown_seconds

  @db_cursor
  def update_coins(self, cursor, id, coins):
    self.check_entity_presence(cursor, self.user_table, self.user_column, id)
    statement = f"UPDATE users SET balance = :coins WHERE user_id = :id"
    cursor.execute(statement, {"coins": coins, "id": id})
    return True

  @db_cursor
  def get_balance(self, cursor, id):
    self.check_entity_presence(cursor, self.user_table, self.user_column, id)
    statement = f"SELECT balance FROM users WHERE user_id = :id"
    cursor.execute(statement, {"id": id})
    row = cursor.fetchone()
    return row[0]

  def check_entity_presence(self, cursor, table, id_column, id_value):
    statement = f"SELECT 1 FROM {table} WHERE {id_column} = :id_value LIMIT 1"
    cursor.execute(statement, {"id_value": id_value})
    row = cursor.fetchone()

    if row is None:
      self.add_entity(cursor, table, id_column, id_value)

  def add_entity(self, cursor, table, id_column, id_value):
    statement = f"INSERT INTO {table} ({id_column}) VALUES (:id_value)"
    cursor.execute(statement, {"id_value": id_value})

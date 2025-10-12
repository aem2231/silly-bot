import sqlite3
from pathlib import Path
from sqlite3.dbapi2 import sqlite_version
import datetime

class Database():
  def __init__(self):
    self.db_path = Path("db1/database.db")
    self.sql_create_statements = [
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
      )"""
    ]
    self.init_db()
    print("import workin")

  def init_db(self):
    self.db_path.parent.mkdir(parents=True, exist_ok=True)

    try:
      with sqlite3.connect(self.db_path) as conn:
        print(f"Opened SQLite database with version {sqlite3.sqlite_version} successfully.")
        cursor = conn.cursor()
        for statement in self.sql_create_statements:
          _ = cursor.execute(statement)

    except sqlite3.OperationalError as e:
      print("Failed to open database:", e)

  def update_coins(self, id, coins):
    try:
      with sqlite3.connect(self.db_path) as conn:
        cursor = conn.cursor()
        select_statement = "SELECT balance FROM users WHERE user_id = :id"
        _ = cursor.execute(select_statement, {"id": id})
        result = cursor.fetchone()

        if self.check_user_presence(id, result) == False:
          self.add_user(id)
          _ = cursor.execute(select_statement, {"id": id})
          result = cursor.fetchone()

        update_statement = "UPDATE users SET balance = :coins WHERE user_id = :id"
        _ = cursor.execute(update_statement, {"coins": coins, "id": id})
        conn.commit()
        return True
    except sqlite3.OperationalError as e:
      print(f'fail: {e}')
      return None

  def get_balance(self, id):
    try:
      with sqlite3.connect(self.db_path) as conn:
        cursor = conn.cursor()
        select_statement = "SELECT balance FROM users WHERE user_id = :id"
        _ = cursor.execute(select_statement, {"id": id})
        result = cursor.fetchone()

        if self.check_user_presence(id, result) == False:
          self.add_user(id)
          _ = cursor.execute(select_statement, {"id": id})
          result = cursor.fetchone()

        balance = result[0]
        return balance

    except sqlite3.OperationalError as e:
      print(e)
      return None

  def check_daily(self, id):
    day_seconds = 86400
    current_time = datetime.datetime.now()
    unix_time = current_time.timestamp()
    select_statement = "SELECT last_daily FROM users WHERE user_id = :id"
    update_statement = "UPDATE users SET last_daily = :unix_time WHERE user_id = :id"

    try:
      with sqlite3.connect(self.db_path) as conn:
        cursor = conn.cursor()
        _ = cursor.execute(select_statement, {"id": id})
        result = cursor.fetchone()

        if self.check_user_presence(id, result) == False:
          # User was just added, set their last_daily to 0 so they can get daily
          _ = cursor.execute(update_statement, {"unix_time": 0, "id": id})
          conn.commit()
          return (True, 0)

        # User exists, check their last daily time
        last_daily = result[0]
        if last_daily is None or last_daily + day_seconds < unix_time:
          # Update their last_daily to current time
          _ = cursor.execute(update_statement, {"unix_time": unix_time, "id": id})
          conn.commit()
          return (True, 0)
        else:
          time_since_last_daily = unix_time - last_daily
          return (False, time_since_last_daily)

    except sqlite3.OperationalError as e:
      print(e)
      return None

  def check_bank(self, guild_id):
    half_hour_seconds = 1800
    current_time = datetime.datetime.now()
    unix_time = current_time.timestamp()
    select_statement = "SELECT last_bank_rob FROM server WHERE guild_id = :id"
    update_statement = "UPDATE server SET last_bank_rob = :unix_time WHERE guild_id = :id"

    try:
      with sqlite3.connect(self.db_path) as conn:
        cursor = conn.cursor()
        _ = cursor.execute(select_statement, {"id": guild_id})
        result = cursor.fetchone()

        if self.check_guild_presence(guild_id, result) == False:
          # Server was just added, set last_bank_rob to 0 so the server can bank_rob
          _ = cursor.execute(update_statement, {"unix_time": 0, "id": guild_id})
          conn.commit()
          print("bank_rob allowed (new server)")
          return (True, 0)

        last_bank_rob = result[0]
        if last_bank_rob is None or last_bank_rob + half_hour_seconds < unix_time:
          # Update last_bank_rob to current time
          _ = cursor.execute(update_statement, {"unix_time": unix_time, "id": guild_id})
          conn.commit()
          return (True, 0)
        else:
          return (False, last_bank_rob)

    except sqlite3.OperationalError as e:
      print(e)
      return None

  def check_work(self, id):
    six_hours_seconds = 21600
    current_time = datetime.datetime.now()
    unix_time = current_time.timestamp()
    select_statement = "SELECT last_work FROM users WHERE user_id = :id"
    update_statement = "UPDATE users SET last_work = :unix_time WHERE user_id = :id"

    try:
      with sqlite3.connect(self.db_path) as conn:
        cursor = conn.cursor()
        _ = cursor.execute(select_statement, {"id": id})
        result = cursor.fetchone()

        if self.check_user_presence(id, result) == False:
          _ = cursor.execute(update_statement, {"unix_time": unix_time, "id": id})
          conn.commit()
          return (True, 0)

        last_work = result[0]
        if last_work is None or last_work + six_hours_seconds < unix_time:
          _ = cursor.execute(update_statement, {"unix_time": unix_time, "id": id})
          conn.commit()
          return (True, 0)
        else:
          time_since_last_work = unix_time - last_work
          return (False, time_since_last_work)

    except sqlite3.OperationalError as e:
      print(e)
      return None

  def add_user(self, id):
    try:
      with sqlite3.connect(self.db_path) as conn:
        cursor = conn.cursor()
        statement = "INSERT OR IGNORE INTO users(user_id) VALUES (:id)"
        _ = cursor.execute(statement, {"id": id})
        conn.commit()
    except sqlite3.OperationalError as e:
      print(e)

  def add_guild(self, id):
    try:
      with sqlite3.connect(self.db_path) as conn:
        cursor = conn.cursor()
        statement = "INSERT OR IGNORE INTO server(guild_id) VALUES (:id)"
        print(id)
        _ = cursor.execute(statement, {"id": id})
        conn.commit()
    except sqlite3.OperationalError as e:
      print(e)

  def check_user_presence(self, id, result):
    if result == None:
      self.add_user(id)
      print("added", id)
      return False
    return True

  def check_guild_presence(self, id, result):
    if result == None:
      print(id)
      self.add_guild(id)
      print("added", id)
      return False
    return True
#db1 = Database()
#db1.update_coins(2, 20)
#db1.get_balance(2)
#db1.check_daily(1)
#db1.check_bank(1)
#db1.check_work(1)

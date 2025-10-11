import sqlite3
from pathlib import Path

class Database():
  def __init__(self):
    self.db_path = Path("db1/database.db")
    self.init_db()

  def init_db(self):
    self.db_path.parent.mkdir(parents=True, exist_ok=True)
    try:
      with sqlite3.connect(self.db_path) as conn:
        print(f"Opened SQLite database with version {sqlite3.sqlite_version} successfully.")

    except sqlite3.OperationalError as e:
      print("Failed to open database:", e)

  def update_coins(self, id):
    pass

  def get_balance(self, id):
    pass

  def check_daily(self, id):
    pass

  def check_bank(self, guild_id):
    pass

  def check_work(self, id):
    pass

db1 = Database()

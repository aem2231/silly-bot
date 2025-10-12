## Code Review: `src/Database.py`

Here are some suggestions to simplify and improve your `Database.py` file.

### 1. Centralize Database Connection Management

**Observation:** A new database connection is established and closed in almost every method using `with sqlite3.connect(self.db_path) as conn:`. While the `with` statement correctly handles closing the connection, creating new connections repeatedly can be inefficient.

**Suggestion:** Create a single, persistent database connection when the `Database` class is instantiated. This connection can be stored in `self.conn` and reused by all methods. You would then be responsible for explicitly committing transactions and closing the connection when the application shuts down.

**Example:**

```python
class Database:
    def __init__(self):
        # ... (other setup)
        self.conn = sqlite3.connect(self.db_path)
        self.init_db()

    def close(self):
        self.conn.close()

    def some_method(self):
        cursor = self.conn.cursor()
        # ... do stuff ...
        self.conn.commit()
```

**Reading:**

*   **sqlite3 Connection Objects:** [https://docs.python.org/3/library/sqlite3.html#connection-objects](https://docs.python.org/3/library/sqlite3.html#connection-objects)

### 2. Reduce Code Duplication with a Decorator for Cursor and Error Handling

**Observation:** The `try...except sqlite3.OperationalError` block is repeated in almost every method that interacts with the database. This is a lot of boilerplate code.

**Suggestion:** Create a Python decorator to handle getting a cursor from the connection and catching exceptions. This will make your database methods much cleaner and easier to read.

**Example:**

```python
from functools import wraps

def db_cursor(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            cursor = self.conn.cursor()
            result = func(self, cursor, *args, **kwargs)
            self.conn.commit()
            return result
        except sqlite3.OperationalError as e:
            print(f'fail: {e}')
            # self.conn.rollback() might be needed here
            return None
    return wrapper

class Database:
    # ...

    @db_cursor
    def get_balance(self, cursor, user_id):
        # ... now you have a cursor and error handling for free
```

**Reading:**

*   **Python Decorators:** [https://realpython.com/primer-on-python-decorators/](https://realpython.com/primer-on-python-decorators/)
*   **`functools.wraps`:** [https://docs.python.org/3/library/functools.html#functools.wraps](https://docs.python.org/3/library/functools.html#functools.wraps)

### 3. Generalize Repetitive Logic

**Observation:**

*   The `check_user_presence` and `check_guild_presence` methods are nearly identical.
*   The logic for checking and adding a user if they don't exist is repeated in `update_coins`, `get_balance`, `check_daily`, and `check_work`.
*   The `check_daily`, `check_bank`, and `check_work` methods all share the same core logic: get a timestamp, compare it to the current time plus a cooldown, and update it if the cooldown has passed.

**Suggestion:**

*   Combine `check_user_presence` and `check_guild_presence` into a single, more generic method like `_ensure_row_exists(self, table_name, id_column, id_value)`.
*   Create a single, generalized method for handling cooldowns, for example: `_check_cooldown(self, table, id_column, time_column, cooldown_seconds, id_value)`. The existing `check_daily`, `check_bank`, and `check_work` methods can then become simple, one-line calls to this new method with the appropriate parameters.

### 4. Improve Readability and Minor Code Cleanup

**Observation:**

*   `_ = cursor.execute(...)`: The underscore `_` is not necessary. You can simply call `cursor.execute(...)`.
*   The `print()` statements used for debugging should ideally be replaced with a proper logging library like Python's built-in `logging` module. This gives you more control over when and where to show debug messages.

**Suggestion:**

*   Remove the `_ =` from `cursor.execute` calls.
*   Consider using the `logging` module for debug output instead of `print()`.

**Reading:**

*   **Logging in Python:** [https://docs.python.org/3/howto/logging.html](https://docs.python.org/3/howto/logging.html)

### Further Reading (Advanced)

For more complex database interactions, you might consider using an Object-Relational Mapper (ORM) like SQLAlchemy. An ORM allows you to work with your database using Python objects instead of writing raw SQL, which can further simplify your code and reduce the chance of errors.

*   **SQLAlchemy:** [https://www.sqlalchemy.org/](https://www.sqlalchemy.org/)

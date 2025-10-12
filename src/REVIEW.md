Code Review and Refactoring Guide: `src/Database.py`

This document provides a detailed code review of `Database.py` and a guide to refactoring it effectively. The goal is to make the code more efficient, readable, and maintainable by applying established software development best practices.

---

## Part 1: Code Review of `Database.py`

The current implementation is functional, but there are several key areas where it can be significantly improved.

### 1.1. Inefficient Connection Management

**Observation:** A new database connection is established and closed in nearly every method.

```python
# From get_balance()
try:
  with sqlite3.connect(self.db_path) as conn:
    # ...
except sqlite3.OperationalError as e:
  # ...
```

While using a `with` statement is good practice for ensuring resources are closed, creating a new connection for every single query is inefficient. Database connections are expensive to create, and doing so repeatedly adds unnecessary latency to your application.

### 1.2. High Code Duplication (Violates DRY Principle)

The "Don't Repeat Yourself" (DRY) principle is a cornerstone of good software design. The current code has three main areas of duplication.

**A. Error Handling:**
The `try...except sqlite3.OperationalError` block is repeated in almost every method. This boilerplate code clutters the logic of each method.

**B. User/Guild Presence Checks:**
The logic to check if a user or guild exists, and to add them if they don't, is duplicated across `update_coins`, `get_balance`, `check_daily`, etc.

```python
# From get_balance()
_ = cursor.execute(select_statement, {"id": id})
result = cursor.fetchone()

if self.check_user_presence(id, result) == False:
  self.add_user(id)
  _ = cursor.execute(select_statement, {"id": id})
  result = cursor.fetchone()
```

This pattern is verbose and inefficient, sometimes requiring multiple database queries for a single operation.

**C. Cooldown Logic:**
The methods `check_daily`, `check_bank`, and `check_work` are nearly identical. They all fetch a timestamp, compare it against a cooldown period, and potentially update the timestamp. The only differences are the table, the column names, and the cooldown duration. This is a classic case for abstraction.

### 1.3. Minor Readability Issues

*   **Unnecessary assignments:** The `_ = cursor.execute(...)` pattern is unnecessary. The return value of `cursor.execute` doesn't need to be assigned.
*   **Debugging with `print()`:** Using `print()` for errors and status messages is fine for small scripts, but a dedicated logging framework provides more control over message levels (e.g., DEBUG, INFO, ERROR) and where messages are sent.

---

## Part 2: Recommended Refactoring Approach

For a file of this size, a full rewrite or a complex pattern like the "Strangler Fig" is unnecessary. The best approach is an **incremental refactoring on a new `git` branch**, using a set of automated tests as a safety net.

Since you don't have a test file yet, the first step would be to create one (`tests/test_database.py`) and write tests that confirm the current behavior. However, you can also proceed carefully without them.

### Recommended Steps:

1.  **Create a New Branch:** Start by creating a new branch in git (e.g., `git checkout -b refactor-database`). This isolates your work and keeps the `main` branch clean.
2.  **Centralize the Connection:** Modify the `__init__` method to create a single, persistent database connection and store it in `self.conn`. Create a `close()` method to close this connection when the application shuts down.
3.  **Introduce a Decorator:** Create the `db_cursor` decorator as discussed. This decorator will be responsible for getting a cursor, managing transactions (commit/rollback), and handling exceptions. This immediately cleans up the duplicated `try...except` blocks.
4.  **Generalize User/Guild Checks:** Create a single helper method, like `_ensure_row_exists(self, cursor, table, id_column, id_value)`, that uses an `INSERT OR IGNORE` command. This is a highly efficient way to ensure a row exists without needing to `SELECT` first.
5.  **Generalize Cooldown Logic:** Create a single helper method, `_check_cooldown(...)`, that contains the shared logic from `check_daily`, `check_bank`, and `check_work`. The original methods will then become simple, one-line calls to this new, powerful helper.
6.  **Refactor Method by Method:** Go through each original method (`get_balance`, `update_coins`, etc.) and apply the new tools:
    *   Add the `@db_cursor` decorator.
    *   Update the method signature to accept the `cursor` argument.
    *   Replace the manual presence-checking logic with a call to `_ensure_row_exists`.
    *   Remove the `with sqlite3.connect(...)` blocks.
7.  **Clean Up:** Remove the now-redundant `check_user_presence` and `check_guild_presence` methods.

---

## Part 3: Detailed Explanations

### The `db_cursor` Decorator

A decorator is a function that wraps another function to add new functionality. Our `db_cursor` decorator automates the repetitive parts of a database operation.

```python
from functools import wraps

def db_cursor(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        # 1. Get cursor (setup)
        cursor = self.conn.cursor()
        try:
            # 2. Run the original function, passing the cursor in
            result = func(self, cursor, *args, **kwargs)
            # 3. Commit the transaction on success (teardown)
            self.conn.commit()
            return result
        except sqlite3.OperationalError as e:
            # 4. Rollback on error (error handling)
            print(f'Database error: {e}')
            self.conn.rollback()
            return None
    return wrapper
```

When you apply this with `@db_cursor` to a method, you are transparently wrapping it in this setup, teardown, and error-handling logic.

---

## Part 4: References and Further Reading

*   **Python `sqlite3` Official Docs:**
    *   [https://docs.python.org/3/library/sqlite3.html](https://docs.python.org/3/library/sqlite3.html)
*   **Python Decorators (Excellent Guide):**
    *   [https://realpython.com/primer-on-python-decorators/](https://realpython.com/primer-on-python-decorators/)
*   **Refactoring Best Practices (by Martin Fowler, a key figure in software engineering):**
    *   [Branch by Abstraction](https://martinfowler.com/bliki/BranchByAbstraction.html)
    *   [Strangler Fig Application](https://martinfowler.com/bliki/StranglerFigApplication.html)
*   **Object-Relational Mappers (ORMs) - For future projects:**
    *   [SQLAlchemy

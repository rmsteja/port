# SQL Injection Fix Explanation

## The Vulnerability

In `app.py`, the `/users` endpoint is vulnerable to SQL Injection:

```python
# VULNERABLE CODE
query = f"SELECT * FROM users WHERE username = '{username}'"
cursor.execute(query)
```

**Problem:** User input is directly concatenated into the SQL query string, allowing attackers to inject malicious SQL code.

**Example Attack:**
```
GET /users?username=admin' OR '1'='1
```

This results in the query:
```sql
SELECT * FROM users WHERE username = 'admin' OR '1'='1'
```

Which returns ALL users instead of just the one matching "admin".

## The Fix

In `app_fixed.py`, the vulnerability is fixed using parameterized queries:

```python
# FIXED CODE
cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
```

**Solution:** 
- Use `?` as a placeholder instead of string interpolation
- Pass user input as a separate parameter tuple `(username,)`
- The database driver automatically escapes and sanitizes the input
- User input is treated as data, not executable SQL code

## Key Differences

| Aspect | Vulnerable (`app.py`) | Fixed (`app_fixed.py`) |
|--------|----------------------|------------------------|
| Query Construction | String concatenation with f-strings | Parameterized query with placeholders |
| Input Handling | Directly inserted into SQL | Passed as parameter |
| Security | Vulnerable to SQL injection | Protected against SQL injection |
| Example | `f"SELECT ... WHERE username = '{username}'"` | `"SELECT ... WHERE username = ?", (username,)` |

## Testing the Fix

1. **Test the vulnerable version:**
   ```bash
   uvicorn app:app --reload
   ```
   Try: `http://localhost:8000/users?username=admin' OR '1'='1`
   - Returns all users (vulnerability exploited)

2. **Test the fixed version:**
   ```bash
   uvicorn app_fixed:app --reload
   ```
   Try: `http://localhost:8000/users?username=admin' OR '1'='1`
   - Returns empty or only exact matches (secure)

## Best Practices

- **Always use parameterized queries** for any user input in database queries
- Never use string concatenation or f-strings for SQL queries with user input
- This applies to all database operations: SELECT, INSERT, UPDATE, DELETE
- Works with all database drivers (sqlite3, psycopg2, mysql-connector, etc.)


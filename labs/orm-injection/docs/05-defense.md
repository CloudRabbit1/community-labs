# Defense

The fix is one line. Replace string interpolation with a parameterized query:

```python
# Vulnerable
query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
row = db.execute(query).fetchone()

# Fixed
row = db.execute(
    "SELECT * FROM users WHERE username = ? AND password = ?",
    (username, password)
).fetchone()
```

With parameterized queries, the database driver handles quoting and escaping. The user input is passed as a value, never interpreted as SQL syntax. A `'--` in the username is stored and compared as a literal string, not parsed as SQL.

Additional controls that reduce blast radius if a parameterized query is missed:

- Run queries as a least-privilege database user with no INSERT, UPDATE, or DROP rights on sensitive tables.
- Hash passwords with bcrypt or argon2 so a successful query bypass does not expose credentials.
- Log and alert on SQL errors from user-supplied input.

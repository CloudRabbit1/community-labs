# Background: SQL Injection via String Interpolation

Most login systems check credentials by running a SQL query against a database. A correct implementation uses parameterized queries, where the user input is treated as a value, never as SQL syntax.

A vulnerable implementation builds the query by pasting the user input directly into the query string:

```python
query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
```

If you supply the username `alice`, the query becomes:

```sql
SELECT * FROM users WHERE username = 'alice' AND password = 'secret'
```

That looks correct. But SQL has comment syntax. The sequence `--` tells the database to ignore everything that follows on the same line. If you supply the username `alice'--`, the query becomes:

```sql
SELECT * FROM users WHERE username = 'alice'--' AND password = 'secret'
```

The `--` comments out `' AND password = 'secret'`. The database sees only the username check. If a user named `alice` exists, the query returns that row regardless of what password you gave.

This technique is called a SQL comment bypass. It is one of the oldest and most reliable SQL injection patterns.

The term "ORM injection" refers to cases where an ORM (Object-Relational Mapper) is configured to pass raw SQL strings rather than using its safe parameterized interface. The underlying vulnerability is the same: untrusted input embedded in a SQL query string.

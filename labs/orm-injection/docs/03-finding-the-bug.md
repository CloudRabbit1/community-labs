# Finding the Bug

Try a login with a known-bad password first to confirm the rejection behavior:

```
curl -X POST http://localhost:8080/login \
  -d "username=admin&password=wrongpassword"
```

```json
{
  "success": false,
  "error": "Invalid credentials"
}
```

Good. The application rejects bad passwords. Now probe whether the username field is treated as SQL or as a plain string.

A single quote in a SQL string literal will break the query syntax if the input is interpolated directly. Send a quote as the username:

```
curl -X POST http://localhost:8080/login \
  -d "username='&password=anything"
```

```json
{
  "success": false,
  "error": "unrecognized token: \"'admin'\" ..."
}
```

The error message leaks the SQL syntax error. The input is going directly into the query. The application is vulnerable.

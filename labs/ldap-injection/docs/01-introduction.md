# Introduction

You are looking at a corporate directory services portal. It authenticates users against an LDAP directory. You do not have valid credentials.

Your goal: bypass the login and retrieve the flag.

The portal runs at `http://localhost:8080`.

```
curl http://localhost:8080/
```

```json
{
  "service": "Directory Services Portal v1.3",
  "endpoints": [
    "POST /login  -- body: username=<u>&password=<p>"
  ],
  "note": "Authentication backed by LDAP directory."
}
```

The application tells you it uses LDAP for authentication. That detail matters. LDAP queries have their own filter syntax, and if the application builds that filter using your input without escaping it, you can change what the query means.

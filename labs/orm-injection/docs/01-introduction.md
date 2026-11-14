# Introduction

You have access to an employee portal. It has a login form. You do not have valid credentials.

Your goal: get in anyway and retrieve the flag.

The portal is running at `http://localhost:8080`. Start by looking at what it exposes.

```
curl http://localhost:8080/
```

```json
{
  "service": "Employee Portal v2.1",
  "endpoints": [
    "POST /login  -- body: username=<u>&password=<p>"
  ],
  "hint": "Login is for authorized employees only."
}
```

There is one endpoint: `/login`. It accepts a POST request with a username and a password. The hint confirms there is a valid admin account. You just do not know the password.

The question is: does the application check that password securely?

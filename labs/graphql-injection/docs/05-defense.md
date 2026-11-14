# Defense

## Fix 1: validate the password in the mutation

The immediate fix is to actually check the password:

```python
def mutate(self, info, username, password):
    user = USERS.get(username)
    if not user or not check_password(password, user["password_hash"]):
        raise GraphQLError("Invalid credentials")
    return Login(token=user["token"], role=user["role"])
```

Never return a flag or sensitive data in a mutation response. If a flag must be accessible, put it behind a separate authenticated query, not embedded in the login payload.

## Fix 2: disable introspection in production

Introspection is a development tool. Disable it in production:

```python
# graphene: pass introspection=False to schema.execute()
result = schema.execute(query, introspection=False, ...)
```

Most GraphQL servers and frameworks have a flag for this. Without introspection, attackers cannot enumerate endpoints, field names, or descriptions.

## Fix 3: do not expose internal field names in the schema

Field descriptions like "Admin-only endpoint" or "internal cost tracking" tell attackers exactly what to target. Keep descriptions generic or omit them entirely in production schemas.

## Fix 4: authorize at the resolver, not at the route

Every resolver that returns sensitive data must check the caller's role:

```python
def resolve_admin_panel(self, info):
    username, role = get_user_from_request()
    if role != "admin":
        raise GraphQLError("Forbidden")
    return {"username": username, "role": role, "flag": FLAG2}
```

Do not rely on the client to avoid calling privileged endpoints.

## Indicators of compromise

Look for introspection queries in your logs:

```
POST /graphql
{"query":"{ __schema { ... } }"}
```

A spike in introspection requests from an unfamiliar IP is a signal that someone is mapping your schema before an attack.

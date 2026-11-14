# Background

## How the update endpoint works

A profile update API typically receives a JSON body and applies it to the user's record in the database. The simple implementation is:

```python
user.update(request.json)
```

This is mass assignment: every field in the request lands in the model. If the model has a `role` field that determines admin access, the caller can set it. The server treats `role` exactly like `name` or `email` -- just another field to update.

## Why this is dangerous

Application code often separates "public fields" from "internal fields" at the display layer, not the write layer. The user profile page might not show `role` in the form, but the underlying API still accepts it. An attacker who reads the API response (which includes `role`) knows the field exists, and can try setting it.

The pattern appears in many forms:
- `role`, `is_admin`, `isAdmin`, `privilege`
- `verified`, `email_verified`, `phone_verified`
- `credit`, `balance`, `subscription_tier`
- `created_at`, `updated_at` (can backdate records)

## The fix

An allowlist specifies exactly which fields the caller is allowed to update. Everything else is ignored:

```python
ALLOWED = {"name", "email", "phone"}
safe = {k: v for k, v in request.json.items() if k in ALLOWED}
user.update(safe)
```

The validation layer should be at the write path, not just at the display layer.

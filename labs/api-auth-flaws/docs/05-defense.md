# Defense

## Fix BOLA: ownership check

The user endpoint must verify that the caller owns the requested record before returning it. Read the caller's identity from the token, not from the URL:

```python
@app.get("/api/users/<int:user_id>")
@token_required
def get_user(user_id):
    if request.caller["user_id"] != user_id:
        return jsonify({"error": "forbidden"}), 403
    con = get_db()
    row = con.execute(
        "SELECT id, username, role, email FROM users WHERE id=?",
        (user_id,),
    ).fetchone()
    if not row:
        return jsonify({"error": "not found"}), 404
    return jsonify(dict(row))
```

The URL parameter is still used as the lookup key, but it is only served when it matches the token's `user_id`. Admins that legitimately need to view other users' profiles need a separate admin-only endpoint with an explicit role check.

## Fix BFLA: role middleware

Add a decorator that checks the caller's role in the database before executing any admin function:

```python
def admin_required(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        con = get_db()
        row = con.execute(
            "SELECT role FROM users WHERE id=?",
            (request.caller["user_id"],),
        ).fetchone()
        if not row or row["role"] != "admin":
            return jsonify({"error": "admin only"}), 403
        return f(*args, **kwargs)
    return wrapper

@app.get("/api/admin/users")
@token_required
@admin_required
def admin_users():
    ...
```

Apply `@admin_required` to every admin endpoint. Do not rely on URL prefixes or client-supplied role claims as a substitute.

## Fix mass assignment: explicit allowlist

The update endpoint must name the fields it permits, and `role` must not be one of them:

```python
@app.patch("/api/users/<int:user_id>")
@token_required
def update_user(user_id):
    if request.caller["user_id"] != user_id:
        return jsonify({"error": "forbidden"}), 403
    data = request.get_json(silent=True) or {}
    con = get_db()
    ALLOWED = {"username", "email"}
    for field in ALLOWED:
        if field in data:
            con.execute(
                f"UPDATE users SET {field}=? WHERE id=?",
                (data[field], user_id),
            )
    con.commit()
    return jsonify({"message": "updated"})
```

Role changes must go through a dedicated admin endpoint that checks the caller is an admin before modifying another user's role.

## Detection

Log every 4xx response from API endpoints. A sequence of incrementing user IDs in 200 responses from a single token is BOLA enumeration. Any successful request to `/api/admin/*` from a non-admin token is a BFLA finding. A `role` field appearing in a PATCH request body is mass assignment attempted; log it and reject the field rather than accepting it silently.

# Defense

## Fix: use an explicit allowlist

Reject any field not in the allowed set for user updates:

```python
ALLOWED_FIELDS = {"name", "email", "phone"}

@app.route("/api/user/profile", methods=["PUT"])
def update_profile():
    username = current_user()
    if not username:
        return jsonify({"error": "not authenticated"}), 401
    data = request.get_json(force=True) or {}
    safe = {k: v for k, v in data.items() if k in ALLOWED_FIELDS}
    USERS[username].update(safe)
    ...
```

`role`, `password`, and any other sensitive fields are silently dropped. The caller never gets an error that reveals the field exists; they just cannot change it.

## Separate write models from read models

Use separate data classes for read and write operations. The read model can include `role` for display. The write model for profile updates does not:

```python
@dataclass
class ProfileUpdate:
    name: str = ""
    email: str = ""
    phone: str = ""

@dataclass
class ProfileView:
    name: str
    email: str
    role: str
```

Deserialization into `ProfileUpdate` ignores `role` by construction.

## Audit fields exposed in GET responses

If a field appears in a GET response, assume an attacker will try to set it in a PUT. Review every field in every read model and confirm it has either an allowlist check or a separate write model that excludes it.

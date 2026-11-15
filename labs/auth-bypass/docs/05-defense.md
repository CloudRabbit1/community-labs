# Defense

## Fix the session cookie: sign it

Flask's built-in session mechanism signs cookies using `itsdangerous` with an HMAC. Use it instead of bare base64:

```python
from flask import Flask, session

app = Flask(__name__)
app.secret_key = os.urandom(32)  # generated once at startup, stored in env

@app.post("/api/login")
def login():
    # ... verify credentials ...
    session["username"] = user["username"]
    session["role"] = user["role"]
    return jsonify({"message": "logged in"})

@app.get("/api/admin")
def admin_panel():
    if session.get("role") != "admin":
        return jsonify({"error": "admin only"}), 403
    ...
```

Flask signs the session cookie with the secret key. The signature is verified on every request. A client that modifies the cookie gets a signature mismatch and Flask rejects it.

The secret key must be generated randomly and kept server-side only. Hardcoding it or using a predictable value defeats the protection.

## Fix the reset token: use cryptographically random bytes

Replace the MD5 derivation with a random token stored in the database:

```python
import secrets

@app.post("/api/reset")
def reset_request():
    username = request.get_json().get("username")
    token = secrets.token_hex(32)
    # Store token alongside an expiry time, single-use flag
    con.execute(
        "INSERT INTO reset_tokens (username, token, expires_at, used) VALUES (?,?,?,0)",
        (username, token, time.time() + 3600),
    )
    con.commit()
    # Send token via email — never return it in the HTTP response
    send_reset_email(username, token)
    return jsonify({"message": "reset email sent"})
```

Key points:
- Generate with `secrets.token_hex()`, not a hash of known inputs
- Store in the database with an expiry time
- Mark as used after first confirmation so the same token cannot be reused
- Never return the token in the HTTP response — send it only via the out-of-band channel (email)

## Fix username enumeration

Return a single generic message regardless of whether the username exists:

```python
if not user or user["password"] != password:
    return jsonify({"error": "Invalid credentials"}), 401
```

Add a constant-time comparison for the password check to prevent timing-based enumeration:

```python
import hmac
if not hmac.compare_digest(user["password"], password):
    return jsonify({"error": "Invalid credentials"}), 401
```

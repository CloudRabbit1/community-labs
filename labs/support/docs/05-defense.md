# Defense

## Fix 1: never unpickle data from clients

The correct fix is not to validate or sanitise the pickle payload. There is no safe way to unpickle untrusted data: any callable in Python's standard library is reachable from a crafted payload. The only safe fix is to not unpickle data you did not create yourself.

Use a safe serialisation format for session data. JSON cannot execute code:

```python
import json, base64, hmac, hashlib

SECRET = os.environ["SESSION_SECRET"]  # random 32-byte hex

def encode_session(data: dict) -> str:
    payload = base64.b64encode(json.dumps(data).encode()).decode()
    sig = hmac.new(SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return f"{payload}.{sig}"

def decode_session(raw: str) -> dict | None:
    try:
        payload, sig = raw.rsplit(".", 1)
    except ValueError:
        return None
    expected = hmac.new(SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(sig, expected):
        return None  # tampered
    return json.loads(base64.b64decode(payload))
```

An attacker who does not know `SECRET` cannot produce a valid signature. Forging a session cookie with `role: admin` is no longer possible.

## Fix 2: use a framework session implementation

Flask's built-in session uses HMAC-SHA1 and is well-audited. Using `flask.session` instead of a custom implementation avoids reinventing security-critical code:

```python
from flask import Flask, session
app = Flask(__name__)
app.secret_key = os.environ["SESSION_SECRET"]  # required

@app.route("/login", methods=["POST"])
def login():
    session["username"] = "alice"
    session["role"] = "user"
    return redirect("/")
```

The session data is stored server-side or signed client-side depending on the backend. Neither case allows client-side tampering without the secret key.

## Fix 3: separate privilege checks from session data

Even with a signed session, it is safer to verify roles against a database rather than trusting the role claim in the session token:

```python
def require_admin(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        username = session.get("username")
        user = db.get_user(username)
        if not user or user["role"] != "admin":
            abort(403)
        return f(*args, **kwargs)
    return wrapper
```

This way, even if an attacker somehow forges a session with `role: admin`, the check fails because the database does not have that user as an admin.

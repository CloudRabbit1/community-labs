# Defense

## Never Deserialize Untrusted Pickle

The simplest and most reliable fix: use a safer format for data that crosses a trust boundary.

Replace pickle with JSON:

```python
import json, base64, secrets, hmac

SECRET = secrets.token_bytes(32)

def save_session(data: dict) -> str:
    blob = json.dumps(data).encode()
    sig = hmac.new(SECRET, blob, 'sha256').hexdigest()
    return base64.b64encode(blob).decode() + '.' + sig

def restore_session(token: str) -> dict:
    try:
        b64, sig = token.rsplit('.', 1)
        blob = base64.b64decode(b64)
        expected = hmac.new(SECRET, blob, 'sha256').hexdigest()
        if not hmac.compare_digest(sig, expected):
            raise ValueError('invalid signature')
        return json.loads(blob)
    except Exception:
        raise ValueError('invalid session token')
```

JSON has no callable-dispatch mechanism. An attacker who forges a JSON blob with `"role": "admin"` still can't execute code, but the HMAC prevents them from forging the payload at all.

## If You Must Use Pickle: Restrict with a Custom Unpickler

Python 3.2+ lets you subclass `pickle.Unpickler` and override `find_class`:

```python
import pickle

ALLOWED = {('builtins', 'dict'), ('builtins', 'str'), ('builtins', 'list')}

class SafeUnpickler(pickle.Unpickler):
    def find_class(self, module, name):
        if (module, name) not in ALLOWED:
            raise pickle.UnpicklingError(f'blocked: {module}.{name}')
        return super().find_class(module, name)

restored = SafeUnpickler(io.BytesIO(raw)).load()
```

This blocks anything not on the allowlist, including `os.system`, `subprocess.Popen`, and gadget chains. It is harder to maintain correctly than switching to JSON.

## Checklist for Developers

- Never call `pickle.loads()`, `yaml.load()`, or similar on data from HTTP requests, cookies, files from untrusted sources, or message queues.
- For session data: use a framework-provided signed cookie mechanism (Flask's default session, Django sessions) or JWT with a strong secret.
- For inter-service communication: use JSON, protobuf, or messagepack with schema validation.
- Treat any deserialized object as untrusted input: validate fields before using them.

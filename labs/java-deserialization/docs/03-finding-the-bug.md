# Finding the Bug

## The Vulnerable Endpoint

The `/api/session/restore` route in `lab/app.py` calls `pickle.loads()` on attacker-supplied bytes:

```python
@app.route('/api/session/restore', methods=['POST'])
def session_restore():
    data = request.get_json(force=True) or {}
    blob = data.get('session_blob', '')
    raw = base64.b64decode(blob)
    # VULNERABLE: untrusted data passed to pickle.loads
    restored = pickle.loads(raw)
    session['user'] = restored.get('user', 'anonymous')
    session['role'] = restored.get('role', 'user')
    return jsonify({'message': 'Session restored', ...})
```

There are two problems here:

1. `pickle.loads(raw)` is called with no type checking. Any Python object can be reconstructed, including one with a malicious `__reduce__` method.
2. The result is immediately trusted: `restored.get('role', 'user')` reads the role directly from the deserialized data with no server-side validation.

## Confirming the Input Reaches pickle.loads

Log in as alice and save a legitimate blob:

```bash
CJAR=$(mktemp)
curl -s -c "$CJAR" -b "$CJAR" -X POST http://127.0.0.1:8091/api/login \
    -H "Content-Type: application/json" \
    -d '{"username":"alice","password":"alice123"}'

curl -s -c "$CJAR" -b "$CJAR" http://127.0.0.1:8091/api/session/save
```

The response includes a `session_blob`. Decode it on the command line to see what it contains:

```bash
echo "eyJ1c2VyIjogImFsaWNlIiwgInJvbGUiOiAidXNlciJ9..." | python3 -c "
import pickle, base64, sys
blob = base64.b64decode(sys.stdin.read().strip())
print(pickle.loads(blob))
"
```

Output: `{'user': 'alice', 'role': 'user'}`

A dict is serialized as a pickle. The restore endpoint deserializes it and trusts its contents. Any blob that deserializes to a dict with `role: admin` will grant admin access, and any blob with a `__reduce__` method will execute code.

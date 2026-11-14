#!/usr/bin/env python3
"""
Host Header Injection -- password reset poisoning

The password reset flow uses request.host to build the reset URL. An attacker
who intercepts the request (or controls a misconfigured proxy) can inject a
Host header pointing to their server. The victim receives an email with a
reset link pointing to the attacker's domain, and the token is captured when
the victim clicks it.

CVE anchor: CVE-2024-28107 (phpMyAdmin host header injection)
"""
import os
import secrets
from flask import Flask, request, jsonify, session

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
FLAG1 = open('/flag1.txt').read().strip()
FLAG2 = open('/flag2.txt').read().strip()

USERS = {
    'admin': {'password': 'SuperSecure!' + secrets.token_hex(4), 'email': 'admin@lab.internal'},
    'alice': {'password': 'alice123', 'email': 'alice@lab.internal'},
}

# In-memory token store and simulated email spool
RESET_TOKENS = {}
EMAIL_SPOOL = []     # simulated sent emails (accessible at /debug/last-email)


@app.route('/')
def index():
    return """<!doctype html><html><head><title>ResetApp</title>
<style>body{font-family:sans-serif;max-width:600px;margin:40px auto;padding:0 20px}
pre{background:#f4f4f4;padding:12px;border-radius:4px;overflow:auto}</style></head>
<body><h2>ResetApp</h2>
<p>Endpoints:</p>
<pre>POST /reset-password  {"email": "user@example.com"}
GET  /reset?token=xxx&password=newpass
POST /login            {"username": "...", "password": "..."}
GET  /profile          (requires login)
GET  /admin-data       (requires admin login)
GET  /debug/last-email (developer debug endpoint)</pre>
</body></html>"""


@app.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json(force=True) or {}
    email = data.get('email', '')
    user = next((u for u, d in USERS.items() if d['email'] == email), None)
    if not user:
        # Return same message to avoid user enumeration
        return jsonify({'message': 'If that email exists, a reset link has been sent.'})

    token = secrets.token_hex(16)
    RESET_TOKENS[token] = user

    # Bug: uses request.host to build the reset URL -- attacker controls this header
    host = request.headers.get('Host', 'localhost:8090')
    reset_url = f"http://{host}/reset?token={token}"

    # Simulate sending email (stores in spool for lab demonstration)
    EMAIL_SPOOL.append({
        'to': email,
        'subject': 'Password Reset',
        'body': f"Click here to reset your password: {reset_url}"
    })

    return jsonify({'message': 'If that email exists, a reset link has been sent.'})


@app.route('/reset')
def reset():
    token = request.args.get('token', '')
    new_password = request.args.get('password', '')
    user = RESET_TOKENS.pop(token, None)
    if not user:
        return jsonify({'error': 'Invalid or expired token'}), 400
    if not new_password:
        return jsonify({'error': 'password parameter required'}), 400
    USERS[user]['password'] = new_password
    return jsonify({'message': f'Password for {user} has been reset.'})


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json(force=True) or {}
    username = data.get('username', '')
    password = data.get('password', '')
    user = USERS.get(username)
    if not user or user['password'] != password:
        return jsonify({'error': 'Invalid credentials'}), 401
    session['user'] = username
    return jsonify({'message': f'Logged in as {username}', 'flag': FLAG1 if username == 'admin' else None})


@app.route('/profile')
def profile():
    if 'user' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    return jsonify({'user': session['user'], 'email': USERS[session['user']]['email']})


@app.route('/admin-data')
def admin_data():
    if session.get('user') != 'admin':
        return jsonify({'error': 'Admin only'}), 403
    return jsonify({'secret': FLAG2})


@app.route('/debug/last-email')
def debug_last_email():
    # Developer debug endpoint: should be removed in production but was left in
    if not EMAIL_SPOOL:
        return jsonify({'message': 'No emails sent yet'})
    return jsonify(EMAIL_SPOOL[-1])


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)

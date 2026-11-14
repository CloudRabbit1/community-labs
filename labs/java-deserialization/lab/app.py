import base64
import os
import pickle
import secrets

from flask import Flask, jsonify, request, session

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

FLAG1 = open('/flag1.txt').read().strip()
FLAG2 = open('/flag2.txt').read().strip()

USERS = {
    'admin': {'role': 'admin', 'email': 'admin@corp.internal'},
    'alice': {'role': 'user',  'email': 'alice@corp.internal'},
}


@app.route('/')
def index():
    return jsonify({
        'app': 'CorpPortal Session API',
        'endpoints': [
            'POST /api/login',
            'GET  /api/profile',
            'POST /api/session/save',
            'POST /api/session/restore',
            'GET  /api/admin/secret',
        ],
    })


@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json(force=True) or {}
    username = data.get('username', '')
    password = data.get('password', '')
    # Simplified: alice's password is "alice123"; admin is not reachable via login
    valid = {'alice': 'alice123'}
    if username not in valid or valid[username] != password:
        return jsonify({'error': 'Invalid credentials'}), 401
    session['user'] = username
    session['role'] = USERS[username]['role']
    return jsonify({'message': f'Logged in as {username}', 'role': USERS[username]['role']})


@app.route('/api/profile')
def profile():
    if 'user' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    return jsonify({
        'username': session['user'],
        'role': session['role'],
        'email': USERS.get(session['user'], {}).get('email', ''),
        'hint': FLAG1 if session['role'] == 'admin' else None,
    })


@app.route('/api/session/save', methods=['GET', 'POST'])
def session_save():
    """Return a serialized (pickled) snapshot of the caller's session."""
    if 'user' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    snapshot = {'user': session['user'], 'role': session['role']}
    blob = base64.b64encode(pickle.dumps(snapshot)).decode()
    return jsonify({'session_blob': blob, 'note': 'Save this and POST to /api/session/restore'})


@app.route('/api/session/restore', methods=['POST'])
def session_restore():
    """Restore a session from a pickled blob.

    Bug: calls pickle.loads() on attacker-supplied bytes without any
    validation. The __reduce__ method on a malicious object runs arbitrary
    code during deserialization.
    """
    data = request.get_json(force=True) or {}
    blob = data.get('session_blob', '')
    if not blob:
        return jsonify({'error': 'session_blob required'}), 400
    try:
        raw = base64.b64decode(blob)
        # VULNERABLE: untrusted data passed to pickle.loads
        restored = pickle.loads(raw)
        session['user'] = restored.get('user', 'anonymous')
        session['role'] = restored.get('role', 'user')
        return jsonify({'message': 'Session restored', 'user': session['user'], 'role': session['role']})
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/admin/secret')
def admin_secret():
    if session.get('role') != 'admin':
        return jsonify({'error': 'Admin only'}), 403
    return jsonify({'secret': FLAG2})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)

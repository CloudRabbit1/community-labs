from flask import Flask, request, jsonify
import os, hashlib, sqlite3

app = Flask(__name__)
FLAG1 = os.environ.get('FLAG1', 'POC{flag1_missing}')
FLAG2 = os.environ.get('FLAG2', 'POC{flag2_missing}')


def get_db():
    db = sqlite3.connect(':memory:', check_same_thread=False)
    db.execute("CREATE TABLE users (id INT, username TEXT, password_hash TEXT, role TEXT)")
    admin_hash = hashlib.md5('password123'.encode()).hexdigest()
    db.execute("INSERT INTO users VALUES (1, 'admin', ?, 'admin')", (admin_hash,))
    db.execute("INSERT INTO users VALUES (2, 'guest', ?, 'user')", (hashlib.md5(b'guest').hexdigest(),))
    db.commit()
    return db


_db = get_db()


@app.get('/')
def index():
    return '''<html><head><title>DataSearch</title></head><body>
<h1>DataSearch Portal</h1>
<p>Search: GET /search?q=...</p>
<p>Login: POST /login</p>
<p>Import: POST /import (admin only)</p>
</body></html>'''


@app.get('/search')
def search():
    q = request.args.get('q', '')
    try:
        rows = _db.execute(f"SELECT id, username, role FROM users WHERE username LIKE '%{q}%'").fetchall()
        return jsonify({'results': [{'id': r[0], 'username': r[1], 'role': r[2]} for r in rows]})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.post('/login')
def login():
    data = request.get_json() or {}
    username = data.get('username', '')
    password = data.get('password', '')
    h = hashlib.md5(password.encode()).hexdigest()
    row = _db.execute("SELECT role FROM users WHERE username=? AND password_hash=?", (username, h)).fetchone()
    if row:
        return jsonify({'success': True, 'role': row[0], 'flag1': FLAG1 if row[0] == 'admin' else ''})
    return jsonify({'error': 'Invalid credentials'}), 401


@app.post('/import')
def import_url():
    role = request.headers.get('X-Role', '')
    if role != 'admin':
        return jsonify({'error': 'Admin only'}), 403
    data = request.get_json() or {}
    url = data.get('url', '')
    if 'internal.local' in url or '127.0.0.1' in url or 'localhost' in url:
        return jsonify({'content': 'Internal service response', 'secret': FLAG2})
    return jsonify({'error': 'Only internal URLs are allowed for imports'}), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False, threaded=True)

#!/usr/bin/env python3
import json
import os
from flask import Flask, request, jsonify, session

app = Flask(__name__)
app.secret_key = os.urandom(24)

FLAG1 = open("/flag1.txt").read().strip()
FLAG2 = open("/flag2.txt").read().strip()

USERS = {
    "alice": {"password": "password123", "role": "user", "email": "alice@corp.local"},
    "bob":   {"password": "letmein",      "role": "user", "email": "bob@corp.local"},
}

def current_user():
    return session.get("username")

def current_role():
    username = current_user()
    if not username:
        return None
    return USERS.get(username, {}).get("role")

@app.route("/")
def index():
    user = current_user()
    role = current_role()
    return f"""<!doctype html>
<html><head><title>ProfileHub</title>
<style>body{{font-family:sans-serif;max-width:600px;margin:40px auto;padding:0 20px}}
pre{{background:#f4f4f4;padding:12px;border-radius:4px}}</style></head>
<body>
<h2>ProfileHub</h2>
{'<p>Logged in as <b>' + user + '</b> (role: <b>' + role + '</b>)</p>' if user else '<p>Not logged in.</p>'}
<p>
  <a href="/login">Login</a> |
  <a href="/api/user/profile">My Profile (JSON)</a> |
  <a href="/admin">Admin Panel</a> |
  <a href="/logout">Logout</a>
</p>
</body></html>"""

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        data = request.get_json(force=True) or {}
        u = data.get("username", "")
        p = data.get("password", "")
        user = USERS.get(u)
        if user and user["password"] == p:
            session["username"] = u
            return jsonify({"ok": True, "role": user["role"]})
        return jsonify({"error": "invalid credentials"}), 401
    return """<!doctype html><html><body>
<h2>Login</h2>
<pre>POST /login  Content-Type: application/json
{"username": "alice", "password": "password123"}</pre>
</body></html>"""

@app.route("/logout")
def logout():
    session.clear()
    return jsonify({"ok": True})

@app.route("/api/user/profile", methods=["GET", "PUT"])
def profile():
    username = current_user()
    if not username:
        return jsonify({"error": "not authenticated"}), 401

    if request.method == "GET":
        u = USERS[username].copy()
        u.pop("password")
        return jsonify(u)

    # PUT: update profile -- mass assignment vulnerability here
    # The app merges the entire request body into the user object
    # without filtering sensitive fields like "role"
    data = request.get_json(force=True) or {}
    USERS[username].update(data)
    u = USERS[username].copy()
    u.pop("password")
    return jsonify({"ok": True, "profile": u})

@app.route("/admin")
def admin():
    if current_role() != "admin":
        return jsonify({"error": "admin only"}), 403
    return jsonify({
        "message": "Welcome to the admin panel.",
        "flag": FLAG1,
        "users": [
            {"username": k, "role": v["role"], "email": v["email"]}
            for k, v in USERS.items()
        ],
    })

@app.route("/admin/secrets")
def admin_secrets():
    if current_role() != "admin":
        return jsonify({"error": "admin only"}), 403
    return jsonify({"flag": FLAG2, "secret_key": "prod-signing-key-7f3a9c2b"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)

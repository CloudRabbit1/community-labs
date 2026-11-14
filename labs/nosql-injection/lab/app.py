#!/usr/bin/env python3
import os
import time
from flask import Flask, request, jsonify, session
from pymongo import MongoClient

app = Flask(__name__)
app.secret_key = os.urandom(24)

FLAG1 = open("/flag1.txt").read().strip()
FLAG2 = open("/flag2.txt").read().strip()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongo:27017/")
client = None
db = None

def get_db():
    global client, db
    if db is None:
        for _ in range(30):
            try:
                client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
                client.server_info()
                db = client["nosql_lab"]
                break
            except Exception:
                time.sleep(1)
        if db is None:
            raise RuntimeError("MongoDB not available")
    return db

def seed():
    database = get_db()
    if database.users.count_documents({}) == 0:
        database.users.insert_many([
            {"username": "alice", "password": "hunter2",   "role": "user"},
            {"username": "bob",   "password": "letmein",   "role": "user"},
            {"username": "admin", "password": os.urandom(16).hex(), "role": "admin"},
        ])

@app.before_request
def init():
    app.before_request_funcs[None].remove(init)
    seed()

@app.route("/")
def index():
    user = session.get("username")
    role = session.get("role")
    return f"""<!doctype html><html><head><title>NosqlHub</title>
<style>body{{font-family:sans-serif;max-width:600px;margin:40px auto;padding:0 20px}}
pre{{background:#f4f4f4;padding:12px;border-radius:4px}}</style></head>
<body><h2>NosqlHub</h2>
{'<p>Logged in as <b>' + user + '</b> (role: <b>' + role + '</b>)</p>' if user else '<p>Not logged in.</p>'}
<p><a href="/login">Login</a> | <a href="/dashboard">Dashboard</a> | <a href="/admin">Admin</a> | <a href="/logout">Logout</a></p>
<pre>POST /login  Content-Type: application/json
{{"username": "alice", "password": "hunter2"}}</pre>
</body></html>"""

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        data = request.get_json(force=True) or {}
        username = data.get("username")
        password = data.get("password")

        # VULNERABLE: user-supplied values passed directly to MongoDB query
        # Allows operator injection: {"$gt": ""} matches any value
        user = get_db().users.find_one(
            {"username": username, "password": password}
        )

        if user:
            session["username"] = user["username"]
            session["role"] = user.get("role", "user")
            return jsonify({"ok": True, "username": user["username"], "role": user.get("role")})
        return jsonify({"error": "invalid credentials"}), 401
    return """<!doctype html><html><body>
<h2>Login</h2>
<pre>POST /login  Content-Type: application/json
{"username": "alice", "password": "hunter2"}</pre>
</body></html>"""

@app.route("/logout")
def logout():
    session.clear()
    return jsonify({"ok": True})

@app.route("/dashboard")
def dashboard():
    if not session.get("username"):
        return jsonify({"error": "not authenticated"}), 401
    return jsonify({
        "message": f"Hello, {session['username']}.",
        "flag": FLAG1,
    })

@app.route("/admin")
def admin():
    if session.get("role") != "admin":
        return jsonify({"error": "admin only"}), 403
    return jsonify({
        "message": "Admin panel.",
        "flag": FLAG2,
        "users": list(get_db().users.find({}, {"_id": 0, "password": 0})),
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)

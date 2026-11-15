import base64
import hashlib
import json
import os
import sqlite3

from flask import Flask, make_response, request, jsonify

app = Flask(__name__)
DB_PATH = "/data/app.db"


def get_db():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con


def decode_session(cookie):
    try:
        padded = cookie + "=" * (-len(cookie) % 4)
        return json.loads(base64.b64decode(padded).decode())
    except Exception:
        return None


def encode_session(username, role):
    return base64.b64encode(
        json.dumps({"username": username, "role": role}).encode()
    ).decode()


@app.post("/api/login")
def login():
    data = request.get_json(silent=True) or {}
    username = data.get("username", "")
    password = data.get("password", "")
    con = get_db()
    # Username enumeration: different error messages for missing vs wrong password
    user = con.execute(
        "SELECT username, role FROM users WHERE username=?", (username,)
    ).fetchone()
    if not user:
        return jsonify({"error": "Username not found"}), 401
    real = con.execute(
        "SELECT password FROM users WHERE username=?", (username,)
    ).fetchone()
    if real["password"] != password:
        return jsonify({"error": "Incorrect password"}), 401
    resp = make_response(jsonify({"message": "logged in", "username": user["username"]}))
    # Unsigned base64 session cookie: trivially forgeable
    resp.set_cookie("session", encode_session(user["username"], user["role"]))
    return resp


@app.get("/api/admin")
def admin_panel():
    cookie = request.cookies.get("session", "")
    sess = decode_session(cookie)
    if not sess or sess.get("role") != "admin":
        return jsonify({"error": "admin only"}), 403
    con = get_db()
    flag1 = con.execute("SELECT value FROM config WHERE key='flag1'").fetchone()
    return jsonify({"message": "admin panel", "flag1": flag1["value"]})


@app.post("/api/reset")
def reset_request():
    data = request.get_json(silent=True) or {}
    username = data.get("username", "")
    con = get_db()
    user = con.execute(
        "SELECT username FROM users WHERE username=?", (username,)
    ).fetchone()
    if not user:
        return jsonify({"error": "Username not found"}), 404
    # Predictable reset token: MD5 of the username
    token = hashlib.md5(username.encode()).hexdigest()
    return jsonify({"message": "reset token issued", "token": token})


@app.post("/api/reset/confirm")
def reset_confirm():
    data = request.get_json(silent=True) or {}
    username = data.get("username", "")
    token = data.get("token", "")
    new_password = data.get("password", "")
    expected = hashlib.md5(username.encode()).hexdigest()
    if token != expected:
        return jsonify({"error": "invalid token"}), 401
    con = get_db()
    con.execute("UPDATE users SET password=? WHERE username=?", (new_password, username))
    con.commit()
    return jsonify({"message": "password updated"})


@app.get("/api/profile")
def profile():
    cookie = request.cookies.get("session", "")
    sess = decode_session(cookie)
    if not sess:
        return jsonify({"error": "not logged in"}), 401
    con = get_db()
    row = con.execute(
        "SELECT username, role, flag2 FROM users WHERE username=?",
        (sess.get("username"),),
    ).fetchone()
    if not row:
        return jsonify({"error": "user not found"}), 404
    return jsonify(dict(row))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)

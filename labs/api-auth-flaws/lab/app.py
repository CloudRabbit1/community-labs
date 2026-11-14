import functools
import os
import sqlite3

import jwt
from flask import Flask, g, jsonify, request

app = Flask(__name__)
DB_PATH = "/data/app.db"
JWT_SECRET = os.environ.get("JWT_SECRET", "dev-secret")


def get_db():
    if "db" not in g:
        con = sqlite3.connect(DB_PATH)
        con.row_factory = sqlite3.Row
        g.db = con
    return g.db


@app.teardown_appcontext
def close_db(exc):
    db = g.pop("db", None)
    if db:
        db.close()


def token_required(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return jsonify({"error": "missing token"}), 401
        try:
            payload = jwt.decode(auth[7:], JWT_SECRET, algorithms=["HS256"])
            request.caller = payload
        except Exception:
            return jsonify({"error": "invalid token"}), 401
        return f(*args, **kwargs)
    return wrapper


@app.post("/api/login")
def login():
    data = request.get_json(silent=True) or {}
    con = get_db()
    row = con.execute(
        "SELECT id, username FROM users WHERE username=? AND password=?",
        (data.get("username"), data.get("password")),
    ).fetchone()
    if not row:
        return jsonify({"error": "invalid credentials"}), 401
    token = jwt.encode(
        {"user_id": row["id"], "username": row["username"]},
        JWT_SECRET,
        algorithm="HS256",
    )
    return jsonify({"token": token})


@app.get("/api/users/<int:user_id>")
@token_required
def get_user(user_id):
    # BOLA: no ownership check — returns any user's profile including flag1
    con = get_db()
    row = con.execute(
        "SELECT id, username, role, email, flag1 FROM users WHERE id=?",
        (user_id,),
    ).fetchone()
    if not row:
        return jsonify({"error": "not found"}), 404
    return jsonify(dict(row))


@app.patch("/api/users/<int:user_id>")
@token_required
def update_user(user_id):
    if request.caller["user_id"] != user_id:
        return jsonify({"error": "forbidden"}), 403
    data = request.get_json(silent=True) or {}
    con = get_db()
    # Mass assignment: 'role' is accepted as an updatable field
    for field in ("username", "email", "role"):
        if field in data:
            con.execute(
                f"UPDATE users SET {field}=? WHERE id=?",
                (data[field], user_id),
            )
    con.commit()
    return jsonify({"message": "updated"})


@app.get("/api/admin/users")
@token_required
def admin_users():
    # BFLA: no role check — any authenticated user can call this admin endpoint
    con = get_db()
    rows = con.execute(
        "SELECT id, username, role, email, flag2 FROM users"
    ).fetchall()
    return jsonify([dict(r) for r in rows])


@app.get("/api/admin/secret")
@token_required
def admin_secret():
    con = get_db()
    row = con.execute(
        "SELECT role FROM users WHERE id=?",
        (request.caller["user_id"],),
    ).fetchone()
    if not row or row["role"] != "admin":
        return jsonify({"error": "admin only"}), 403
    flag3 = con.execute(
        "SELECT value FROM config WHERE key='flag3'"
    ).fetchone()
    return jsonify({"flag3": flag3["value"]})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)

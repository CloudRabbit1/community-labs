#!/bin/sh
set -e

export FLAG1="POC{$(openssl rand -hex 16)}"
export FLAG2="POC{$(openssl rand -hex 16)}"

mkdir -p /data

python3 - << 'PYEOF'
import os, sqlite3

db = sqlite3.connect('/data/app.db')
db.executescript("""
CREATE TABLE IF NOT EXISTS users (
    id       INTEGER PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role     TEXT NOT NULL DEFAULT 'user',
    flag2    TEXT
);
CREATE TABLE IF NOT EXISTS config (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
""")
db.execute("DELETE FROM users")
db.execute("DELETE FROM config")
db.executemany(
    "INSERT INTO users (username,password,role,flag2) VALUES (?,?,?,?)",
    [
        ('alice', 'alice123',           'user',  None),
        ('bob',   'bobs-secret-pass',   'user',  os.environ['FLAG2']),
        ('admin', 'admin-secret-pass',  'admin', None),
    ],
)
db.execute("INSERT INTO config (key,value) VALUES ('flag1', ?)", (os.environ['FLAG1'],))
db.commit()
db.close()
print("Database initialised")
PYEOF

exec python3 /app/app.py

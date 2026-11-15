#!/bin/sh
set -e

export FLAG1="POC{$(openssl rand -hex 16)}"
export FLAG2="POC{$(openssl rand -hex 16)}"
export FLAG3="POC{$(openssl rand -hex 16)}"
export ADMIN_PASS="$(openssl rand -hex 20)"
export JWT_SECRET="$(openssl rand -hex 32)"

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
    email    TEXT,
    flag1    TEXT,
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
    "INSERT INTO users (id,username,password,role,email,flag1,flag2) VALUES (?,?,?,?,?,?,?)",
    [
        (1, 'alice', 'alice123', 'user',  'alice@corp.local', None,                   None),
        (2, 'bob',   'bob123',   'user',  'bob@corp.local',   os.environ['FLAG1'],    None),
        (3, 'admin', os.environ['ADMIN_PASS'], 'admin', 'admin@corp.local', None, os.environ['FLAG2']),
    ],
)
db.execute("INSERT INTO config (key,value) VALUES ('flag3', ?)", (os.environ['FLAG3'],))
db.commit()
db.close()
print("Database initialised")
PYEOF

exec python3 /app/app.py

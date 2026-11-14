# Defense

## Fix SQL injection: use parameterized queries

Replace string interpolation with a parameterized query:

```python
# Vulnerable
rows = db.execute(f"SELECT ... WHERE username LIKE '%{q}%'").fetchall()

# Fixed
rows = db.execute("SELECT ... WHERE username LIKE ?", (f'%{q}%',)).fetchall()
```

Parameterized queries pass the value separately from the SQL structure. The database driver handles escaping. User input can never change the query structure.

## Fix weak password hashing: use bcrypt

MD5 is not a password hashing algorithm. It is fast by design, which makes brute-forcing fast. Use bcrypt, which is intentionally slow and includes a salt:

```python
import bcrypt
hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
# Verify
bcrypt.checkpw(password.encode(), hashed)
```

A unique salt means identical passwords produce different hashes. The work factor makes dictionary attacks take months instead of milliseconds.

## Fix SSRF: use an allowlist of specific URLs

An "internal URLs only" rule is not a defense. It is the attack surface. Instead, define an explicit allowlist of permitted endpoints:

```python
ALLOWED_URLS = {'http://reports.internal/export', 'http://assets.internal/images'}

if url not in ALLOWED_URLS:
    return jsonify({'error': 'URL not permitted'}), 400
```

If a dynamic URL is unavoidable, resolve it and check the resulting IP against a blocklist of RFC 1918 ranges before making the request.

# Defense

## Use Constant-Error Messages

Return the same error regardless of whether the username exists or the password is wrong:

```python
# Vulnerable
if username not in USERS:
    return error("user not found")
if USERS[username] != password:
    return error("incorrect password")

# Safe: same message for both failures
user = USERS.get(username)
if user is None or user != password:
    return error("invalid credentials")
```

Also run the same code path regardless of outcome to prevent timing attacks: hash the supplied password even when the username does not exist.

## Enforce Strong Passwords

Reject passwords that appear in a blocklist of common values. The NIST SP 800-63B guideline recommends checking new passwords against a list of known-compromised values:

```python
COMMON_PASSWORDS = {"password", "123456", "admin", "admin123", "letmein"}

if new_password in COMMON_PASSWORDS:
    return error("that password is too common")
```

Require a minimum length of at least 12 characters.

## Rate Limiting and Lockout

Limit failed login attempts per username and per IP address:

```python
from collections import defaultdict
import time

FAIL_TIMES: dict = defaultdict(list)
MAX_FAILS = 5
WINDOW = 300  # 5 minutes

def check_rate(key: str):
    now = time.time()
    FAIL_TIMES[key] = [t for t in FAIL_TIMES[key] if now - t < WINDOW]
    if len(FAIL_TIMES[key]) >= MAX_FAILS:
        raise ValueError("too many failed attempts")
    FAIL_TIMES[key].append(now)
```

Apply this to both the username and the source IP.

## Multi-Factor Authentication

Requiring a second factor (TOTP, SMS, hardware key) limits the impact of a brute-forced password. Even if the password is guessed, the attacker cannot complete the login without the second factor.

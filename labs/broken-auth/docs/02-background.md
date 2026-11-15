# Background

## Username Enumeration

A login form has two secret values: the username and the password. If the error message reveals which one is wrong, the attacker can discover valid usernames without knowing any passwords.

| Response | What it leaks |
|----------|--------------|
| "user not found" | username does not exist |
| "incorrect password" | username exists |
| "invalid credentials" | reveals nothing (correct) |

A timing difference produces the same leak: if the server hashes the password only when the username is found, login attempts on nonexistent users return faster.

## Brute-Force Attacks

Once a valid username is confirmed, the attacker tries passwords from a wordlist. The wordlist contains common passwords (`password`, `123456`, `admin`), passwords derived from the site name, and patterns from previous data breaches.

OWASP publishes the Top 10 most common passwords. `admin123`, `password`, and `123456` appear on every list. An application where any account uses these passwords is vulnerable to a credential stuffing attack from public breach data.

## Session Cookies

After a successful login, the server issues a session cookie. The cookie is a token that the browser sends with every request. The server maps tokens to user accounts in memory or in a database.

A stolen or guessed token gives the attacker the same access as the account it belongs to. Session tokens must be:
- Cryptographically random (at least 128 bits)
- Sent only over HTTPS (Secure flag)
- Inaccessible to JavaScript (HttpOnly flag)
- Invalidated on logout

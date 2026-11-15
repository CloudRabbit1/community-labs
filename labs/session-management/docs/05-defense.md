# Defense

## Use Cryptographically Random Tokens

Replace the counter with a CSPRNG:

```python
import secrets
token = secrets.token_hex(32)   # 256 bits of entropy, unguessable
```

The token reveals nothing about when it was issued or who else has tokens.

## Invalidate Tokens on Logout

The current app never expires tokens. Add an explicit logout endpoint that removes the token from the server-side store:

```python
del _sessions[token]
```

## Rotate Tokens on Privilege Change

Issue a new token any time the user's role changes (login, sudo, role assignment). This prevents a token captured before a privilege change from still being valid after it.

## Use a Framework Session Middleware

Flask-Login, Django sessions, and Express session all handle token generation, rotation, and expiry correctly by default. Rolling your own session management is the most common path to this class of bug.

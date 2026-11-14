# Background

## Session cookies

A session cookie stores identity information the server uses to recognize a returning user. The simplest approach is to put the data directly in the cookie: `{"username":"alice","role":"user"}`. Encode it in base64 so it survives HTTP transport and you have a readable session mechanism.

The problem is that base64 is reversible by anyone. There is no secret involved. If the server trusts the cookie's contents without verifying them, the client controls its own identity.

The correct approach is to sign the cookie with a server-side secret using an HMAC. Flask's `flask.session` does this by default. A cookie signed with `HS256` and a 32-byte secret cannot be forged without that secret. The server verifies the signature on every request and rejects anything it did not issue.

## Password reset tokens

A secure reset token must be unguessable by anyone who does not receive it out-of-band, usually via email. That means it needs to be:

- Cryptographically random, generated with `os.urandom()` or `secrets.token_hex()`
- Long enough that brute force is infeasible (32+ bytes of entropy)
- Short-lived: tied to a single-use record in the database, deleted on first use

Using a deterministic function of the username, like MD5, fails all three criteria. The token is guessable by anyone who knows the username, it is not random, and there is no expiry or single-use check.

## Username enumeration

The login endpoint in this lab returns different error messages for a valid username with the wrong password ("Incorrect password") versus a username that does not exist ("Username not found"). That difference lets an attacker enumerate valid usernames before attacking them. Secure login endpoints return a single generic message: "Invalid credentials."

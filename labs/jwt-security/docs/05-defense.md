# Defense

## Reject alg:none

Never allow the token header to control which algorithm is used for verification. Hard-code the expected algorithm on the server side:

```python
# Vulnerable: trusts whatever the header says
alg = header.get("alg")
if alg == "none": return payload  # bypass!

# Safe: ignore the header's alg entirely
expected = hmac.new(SECRET.encode(), sig_input, hashlib.sha256).digest()
if not hmac.compare_digest(expected, given):
    raise ValueError("invalid signature")
```

If you use a JWT library, make sure the `algorithms` parameter is an explicit allowlist:

```python
# PyJWT: explicitly name the allowed algorithms
payload = jwt.decode(token, SECRET, algorithms=["HS256"])
# Never: algorithms=["HS256", "none"] or leaving it at the default
```

## Use a Strong Secret

A short dictionary word as the HMAC secret can be cracked offline in seconds. The key should be at least 256 bits of random data:

```python
import secrets
SECRET = secrets.token_hex(32)  # 64 hex chars = 256 bits
```

Store it in an environment variable or secrets manager, never in source code.

## Prefer Asymmetric Algorithms

With RS256 or ES256, the server signs with a private key and verifies with a public key. The signing key is never transmitted or shared with clients, so it cannot be recovered even by someone who intercepts every token.

## Libraries and Standards

Use a well-maintained JWT library rather than implementing JWT manually. Libraries like PyJWT, python-jose, and Auth0's jwt enforce algorithm restrictions by default and receive security patches when new bypass techniques are discovered.

# Background

## JWT Structure

A JWT is three base64url-encoded sections joined by dots:

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InVzZXIifQ.SIG
 ^-- header (JSON)                       ^-- payload (JSON)           ^-- signature
```

The header declares the algorithm. The payload holds your claims. The signature protects both against tampering.

Decode any section with:
```python
import base64, json
def b64d(s):
    pad = 4 - len(s) % 4
    return json.loads(base64.urlsafe_b64decode(s + "=" * (pad % 4)))
```

## The alg Field

The header's `alg` field tells the server which algorithm to use when verifying the signature. Common values:

| alg | Meaning |
|-----|---------|
| `HS256` | HMAC-SHA256 with a shared secret |
| `RS256` | RSA signature with a private key |
| `none` | No signature |

RFC 7518 defines `none` as a valid algorithm for cases where integrity is guaranteed by other means. A server that blindly trusts the header's `alg` field will accept a token claiming `alg: none` with no signature at all.

## HMAC Signing

For `HS256`, the server computes:

```
HMAC-SHA256(key, base64url(header) + "." + base64url(payload))
```

If the key is weak, an offline dictionary attack recovers it quickly. Tools like `hashcat` and `john` have dedicated JWT modes. With the key in hand, an attacker can sign any payload they like.

## Why This Matters

Both attacks let an attacker impersonate any user, including administrators, without knowing a password. The exploit is entirely passive after the initial token is observed.

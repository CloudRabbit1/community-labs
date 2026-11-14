# Background

## How TOTP Works

TOTP (Time-based One-Time Password, RFC 6238) generates codes from two inputs: a shared secret and the current 30-second time window. The secret is seeded during enrollment and never transmitted again. The server and the authenticator app both run the same HMAC-SHA1 computation and arrive at the same six digits.

The key property is the shared secret. Without it, knowing the time is not enough to generate a valid code.

## What This App Does Instead

This app computes the OTP as:

```python
str(int(time.time()) % 1_000_000).zfill(6)
```

That is the current Unix timestamp modulo one million, zero-padded to six digits. There is no secret. Any client that knows this formula and the current time can produce a valid OTP.

## Why This Fails as MFA

A second factor is supposed to be something you have (a physical token or a device running an authenticator app). The formula above depends only on something you know (the algorithm), which is equivalent to a second password. Worse, the algorithm is deterministic and public, so it provides no additional security at all.

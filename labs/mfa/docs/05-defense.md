# Defense

## Use a Standard TOTP Library

Replace the custom formula with a proper TOTP implementation:

```python
import pyotp
secret = pyotp.random_base32()   # generated at enrollment, stored server-side per user
totp = pyotp.TOTP(secret)
totp.verify(otp_from_user)       # returns True only within the current 30-second window
```

The secret is shared with the user's authenticator app during enrollment (usually via QR code) and never transmitted again. Without the secret, an attacker cannot generate valid OTPs.

## Enforce Rate Limiting

A properly seeded TOTP has a one-in-a-million brute force chance per 30-second window. Still, lock the account after 5 failed MFA attempts to prevent automated guessing.

## Do Not Roll Your Own Crypto

The core failure here was implementing a custom OTP derivation. Cryptographic protocols have subtle requirements that are easy to get wrong. Use vetted libraries (pyotp, python-otp, or your framework's MFA module) instead of writing the formula yourself.

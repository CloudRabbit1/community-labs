# Defense

## Do not use ECB mode

ECB is listed as "not recommended" in every modern cryptography reference. Use AES-GCM or AES-CBC with a random IV. Both modes break the block independence that the oracle attack requires.

```python
# Wrong: ECB leaks structure
from Crypto.Cipher import AES
cipher = AES.new(key, AES.MODE_ECB)
ciphertext = cipher.encrypt(padded_plaintext)

# Right: GCM provides authenticated encryption
cipher = AES.new(key, AES.MODE_GCM)
ciphertext, tag = cipher.encrypt_and_digest(plaintext)
# Store nonce + tag + ciphertext
```

## Never append a secret to user-controlled input before encrypting

If the plaintext is `user_input + secret`, any block cipher in any mode leaks the secret to an adaptive chosen-plaintext attacker when output length or value is observable. The safe pattern is to keep user input and secrets separate, and to encrypt them under different keys or at least in separate operations.

## Treat encryption output as opaque

The oracle in this lab returns the raw ciphertext. If the application instead returned only a fixed-length HMAC or token, the block comparison technique would not work: the attacker cannot observe individual cipher blocks. Encrypt internally; return only the minimum information the application requires.

## Why this matters

AES-ECB vulnerabilities have been found in production systems. Payment processing, session tokens, database field encryption. The pattern is always the same: developer picks "AES" without specifying a mode, default or legacy code uses ECB, and an adaptive input vector appears in an API. The fix is a one-line mode change.

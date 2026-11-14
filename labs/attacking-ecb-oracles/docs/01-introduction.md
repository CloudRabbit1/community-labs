# Introduction

AES-ECB is a block cipher mode where each 16-byte block of plaintext is encrypted independently using the same key. That independence is a problem. If an attacker can ask a service to encrypt arbitrary data, and that service appends a secret before encrypting, the attacker can recover the secret one byte at a time without ever knowing the key.

This attack is called the byte-at-a-time ECB decryption oracle attack, or just "ECB oracle." It is not theoretical. Real applications have been broken this way.

## What this lab gives you

A service that encrypts: `AES-ECB( PKCS7( your_input + secret ) )`. The secret is the flag. You cannot ask for the flag directly. You recover it by making many small requests and comparing block outputs.

## What you need

- Docker and Docker Compose
- Python 3 (stdlib only)

Start the lab:

```bash
docker compose up --build -d
```

The oracle listens on `http://localhost:5000`.

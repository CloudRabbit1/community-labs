# Multi-Factor Authentication

A two-step login that generates its OTP from the server clock. Predict the code, skip the second factor.

## Quick Start

```
docker compose up --build
```

Then run the exploit:

```
python3 exploit/exploit.py http://localhost:8080
```

## What You Will Find

The app accepts a username and password at `/login`, then issues a 6-digit one-time password challenge at `/mfa`. The OTP is not random: it is derived from the current Unix timestamp. An attacker who knows the derivation formula can compute the expected value before submitting the form.

## Lab Structure

```
mfa/
  lab/          Dockerfile + app.py (the vulnerable server)
  exploit/      exploit.py (the working attack)
  docs/         background reading
  solutions/    walkthrough with full output
  test.sh       CI harness
```

## Prerequisites

- Docker with Compose
- Python 3.9+

# CVE-2025-25227: Joomla MFA Authentication Bypass

Joomla's post-login state machine is missing a check. After `POST /login`
succeeds, the server sets `state=logged_in` and tells the client to complete
MFA. The bug: admin route handlers check `state == "logged_in"` but never
verify that `mfa_verified == True`. Skipping the MFA step entirely grants
admin access with just the initial login token.

Affected versions: Joomla 4.0.0 through 5.2.5.

## Quick Start

```bash
docker compose up --build
```

The vulnerable app starts on `http://localhost:8080`.

## Run the Exploit

```bash
python3 exploit/exploit.py http://localhost:8080
```

## Get This Lab

**Clone the whole repo:**
```bash
git clone https://github.com/CloudRabbit1/community-labs.git
cd community-labs/joomify
```

**Clone this lab only (sparse checkout):**
```bash
git clone --filter=blob:none --sparse https://github.com/CloudRabbit1/community-labs.git
cd community-labs
git sparse-checkout set labs/joomify
cd joomify
```

**Download a single file:**
```bash
curl -O https://raw.githubusercontent.com/CloudRabbit1/community-labs/master/joomify/exploit/exploit.py
```

## Learn More

Read the docs in order:

1. [Introduction](./docs/01-introduction.md)
2. [Background](./docs/02-background.md)
3. [Finding the Bug](./docs/03-finding-the-bug.md)
4. [Exploitation](./docs/04-exploitation.md)
5. [Defense](./docs/05-defense.md)

The [walkthrough](./solutions/walkthrough.md) has the full solution.

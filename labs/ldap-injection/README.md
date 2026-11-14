# LDAP Injection

| Field | Value |
|-------|-------|
| Technique | LDAP filter injection via unsanitized username input |
| Target | Directory Services Portal login endpoint |
| Difficulty | Easy |

## Quick Start

```bash
docker compose up --build -d
python3 exploit/exploit.py http://localhost:8080
```

## How It Works

The `/login` endpoint builds an LDAP search filter by directly interpolating the username into the filter string. LDAP metacharacters in the username close the uid assertion early and add an OR clause that always matches, bypassing the password check.

See [docs/](docs/) for background and [solutions/walkthrough.md](solutions/walkthrough.md) for the full walkthrough.

## Clone This Lab

```bash
git clone https://github.com/CloudRabbit1/community-labs.git
cd community-labs/ldap-injection
docker compose up --build -d
```

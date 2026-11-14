# Broken Authentication: Username Enumeration and Weak Password Brute-Force

A login portal leaks user existence through different error messages and uses a guessable password for the admin account. By first confirming that `admin` is a valid user, then brute-forcing from a small wordlist, an attacker gains admin access without prior knowledge of the password.

> This container binds to `127.0.0.1` only. Never expose port 8085 beyond localhost.

## Get this lab

**Recommended. Sparse checkout (git only fetches this lab):**
```bash
git clone --filter=blob:none --sparse https://github.com/CloudRabbit1/community-labs
cd community-labs
git sparse-checkout set labs/broken-auth
```

**SVN export (no git required):**
```bash
svn export https://github.com/CloudRabbit1/community-labs/trunk/labs/broken-auth
```

**curl + tar (zero dependencies):**
```bash
curl -sL https://github.com/CloudRabbit1/community-labs/archive/refs/heads/master.tar.gz \
  | tar xz --strip=3 "community-labs-master/labs/broken-auth"
```

Or clone the full repo if you want all labs: `git clone https://github.com/CloudRabbit1/community-labs`

## Quick start

```bash
docker compose up --build -d
```

The lab listens on `127.0.0.1:8085`.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/login` | Accepts `{"username": "...", "password": "..."}`, sets session cookie on success |
| GET | `/dashboard` | Returns flag if the session belongs to `admin` |

## Docs

```
docs/01-introduction.md    what broken authentication means and how these flaws combine
docs/02-background.md      username enumeration, brute-force mechanics, session cookies
docs/03-finding-the-bug.md observing the different error messages
docs/04-exploitation.md    enumerate users then brute-force the password
docs/05-defense.md         constant-time errors, lockouts, rate limiting
```

Stuck? `solutions/walkthrough.md` has the full solution.

## Stop the lab

```bash
docker compose down
```

## Requirements

- Docker with Compose
- Python 3

## Installing Docker

**Kali / Debian / Ubuntu:**

```bash
sudo apt update && sudo apt install -y docker.io docker-compose-plugin
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
```

Log out and back in after the last command.

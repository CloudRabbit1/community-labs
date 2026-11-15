# JWT Security: alg:none Bypass and Weak Secret Forgery

A login service issues JWT tokens, but accepts tokens where the algorithm is set to "none" (no signature required) and uses a guessable secret for HMAC signing. Both weaknesses let an attacker forge an admin token without knowing the admin password.

> This container binds to `127.0.0.1` only. Never expose port 8081 beyond localhost.

## Get this lab

**Recommended. Sparse checkout (git only fetches this lab):**
```bash
git clone --filter=blob:none --sparse https://github.com/CloudRabbit1/community-labs
cd community-labs
git sparse-checkout set labs/jwt-security
```

**SVN export (no git required):**
```bash
svn export https://github.com/CloudRabbit1/community-labs/trunk/labs/jwt-security
```

**curl + tar (zero dependencies):**
```bash
curl -sL https://github.com/CloudRabbit1/community-labs/archive/refs/heads/master.tar.gz \
  | tar xz --strip=3 "community-labs-master/labs/jwt-security"
```

Or clone the full repo if you want all labs: `git clone https://github.com/CloudRabbit1/community-labs`

## Quick start

```bash
docker compose up --build -d
```

The first run builds the container. Expect 1 to 3 minutes. Subsequent starts are instant.

The lab listens on `127.0.0.1:8081`.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/login` | Accepts `{"username": "...", "password": "..."}`, returns a JWT |
| GET | `/admin` | Reads `Authorization: Bearer <token>`, returns flag if username is admin |

## Docs

```
docs/01-introduction.md    what JWT is and why these attacks work
docs/02-background.md      token structure, alg field, HMAC signing
docs/03-finding-the-bug.md decoding tokens and observing the flaw
docs/04-exploitation.md    two attack paths: alg:none and key brute-force
docs/05-defense.md         how to fix both issues
```

Stuck? `solutions/walkthrough.md` has the full solution.

## Stop the lab

```bash
docker compose down
```

## Requirements

- Docker with Compose (see below if not installed)
- Python 3 (stdlib only, no extra packages needed)
- Linux, macOS, or Windows with WSL2

## Installing Docker

**Kali / Debian / Ubuntu:**

```bash
sudo apt update && sudo apt install -y docker.io docker-compose-plugin
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
```

Log out and back in after the last command.

**macOS:** Install [Docker Desktop](https://www.docker.com/products/docker-desktop/).

**Windows:** Install [Docker Desktop](https://www.docker.com/products/docker-desktop/) with WSL2 backend, then run all commands inside a WSL2 terminal.

Verify Docker is working:

```bash
docker run --rm hello-world
```

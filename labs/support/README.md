# support: Python pickle deserialization to RCE and privilege escalation

A support ticketing system that stores session state as an unsigned pickle blob in a cookie. Send a crafted pickle to execute arbitrary Python code on the server (flag1) or simply forge an admin session without any code execution (flag2).

> This container binds to `127.0.0.1` only. Never expose port 8082 beyond localhost.

## Get this lab

**Recommended. Sparse checkout (git only fetches this lab):**
```bash
git clone --filter=blob:none --sparse https://github.com/CloudRabbit1/community-labs
cd community-labs
git sparse-checkout set labs/support
```

**SVN export (no git required):**
```bash
svn export https://github.com/CloudRabbit1/community-labs/trunk/labs/support
```

**curl + tar (zero dependencies):**
```bash
curl -sL https://github.com/CloudRabbit1/community-labs/archive/refs/heads/master.tar.gz \
  | tar xz --strip=3 "community-labs-master/labs/support"
```

Or clone the full repo: `git clone https://github.com/CloudRabbit1/community-labs`

## Quick start

```bash
docker compose up --build -d
```

The first run builds the container. Expect 1 to 2 minutes. TicketDesk listens on `127.0.0.1:8082`.

## Flags

| Flag | Technique | Path |
|------|-----------|------|
| flag1 | pickle RCE | craft a pickle with `subprocess.check_output(['cat', '/flag1.txt'])` as the session cookie |
| flag2 | forged admin session | craft a pickle that returns `{"role": "admin"}` and access `/admin` |

## Accounts

| Username | Password | Role |
|----------|----------|------|
| alice | alice123 | user |

Admin credentials are not provided. The goal is to reach the admin panel without them.

## Docs

```
docs/01-introduction.md    what pickle deserialization is and why it is dangerous
docs/02-background.md      __reduce__ protocol, unsigned cookies, and the attack surface
docs/03-finding-the-bug.md how to identify and confirm the vulnerability
docs/04-exploitation.md    capturing both flags
docs/05-defense.md         safe session handling with HMAC and JSON
```

Stuck? `solutions/walkthrough.md` has the full solution.

## Stop the lab

```bash
docker compose down
```

## Requirements

- Docker with Compose
- Python 3 (for crafting payloads — standard library only, no pip installs needed)
- Linux, macOS, or Windows with WSL2
- x86_64 or AArch64 (Apple Silicon, ARM64)

## Installing Docker

**Kali / Debian / Ubuntu:**

```bash
sudo apt update && sudo apt install -y docker.io docker-compose-plugin
sudo systemctl start docker && sudo systemctl enable docker
sudo usermod -aG docker $USER
```

Log out and back in after the last command.

**macOS / Windows:** Install [Docker Desktop](https://www.docker.com/products/docker-desktop/).

Verify: `docker run --rm hello-world`

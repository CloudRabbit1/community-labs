# silent-monitor: credential exposure and command injection pivot

A network monitoring dashboard with two chained vulnerabilities: default credentials hidden in an HTML comment grant access, and a ping endpoint passes user input unsanitised to bash. The injection lets you read flag1 directly and pivot to an internal service on localhost:9090 for flag2.

> This container binds to `127.0.0.1` only. Never expose port 8081 beyond localhost.

## Get this lab

**Recommended. Sparse checkout (git only fetches this lab):**
```bash
git clone --filter=blob:none --sparse https://github.com/CloudRabbit1/community-labs
cd community-labs
git sparse-checkout set labs/silent-monitor
```

**SVN export (no git required):**
```bash
svn export https://github.com/CloudRabbit1/community-labs/trunk/labs/silent-monitor
```

**curl + tar (zero dependencies):**
```bash
curl -sL https://github.com/CloudRabbit1/community-labs/archive/refs/heads/master.tar.gz \
  | tar xz --strip=3 "community-labs-master/labs/silent-monitor"
```

Or clone the full repo: `git clone https://github.com/CloudRabbit1/community-labs`

## Quick start

```bash
docker compose up --build -d
```

The first run builds the container. Expect 1 to 2 minutes. Apache listens on `127.0.0.1:8081`.

## Flags

| Flag | Technique | Path |
|------|-----------|------|
| flag1 | command injection | inject `;cat /flag1.txt` into the ping host parameter |
| flag2 | internal pivot | inject `;curl http://127.0.0.1:9090/` to reach the internal service |

## Docs

```
docs/01-introduction.md    what the two vulnerabilities are
docs/02-background.md      default credentials, shell injection, and network pivots
docs/03-finding-the-bug.md how to discover and confirm each flaw
docs/04-exploitation.md    capturing both flags
docs/05-defense.md         correct input handling and least-privilege networking
```

Stuck? `solutions/walkthrough.md` has the full solution.

## Stop the lab

```bash
docker compose down
```

## Requirements

- Docker with Compose
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

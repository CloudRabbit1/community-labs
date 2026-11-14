# CORS Origin Reflection: Cross-Origin Credential Leak

Exploit a misconfigured CORS policy that reflects any `Origin` header to read authenticated API data from a cross-origin context.

> This container binds to `127.0.0.1` only. Never expose port 8080 beyond localhost.

## Get this lab

**Recommended. Sparse checkout (git only fetches this lab):**
```bash
git clone --filter=blob:none --sparse https://github.com/CloudRabbit1/community-labs
cd community-labs
git sparse-checkout set labs/cors-sop
```

**SVN export (no git required):**
```bash
svn export https://github.com/CloudRabbit1/community-labs/trunk/labs/cors-sop
```

**curl + tar (zero dependencies):**
```bash
curl -sL https://github.com/CloudRabbit1/community-labs/archive/refs/heads/master.tar.gz \
  | tar xz --strip=3 "community-labs-master/labs/cors-sop"
```

Or clone the full repo if you want all labs: `git clone https://github.com/CloudRabbit1/community-labs`

## Quick start

```bash
docker compose up --build -d
```

The first run builds the container. Expect 30 to 60 seconds. Subsequent starts use the cached image and are instant.

The lab listens on `http://127.0.0.1:8080`.

## Accounts

| Account | Password    | Purpose                        |
|---------|-------------|--------------------------------|
| `alice` | `password123` | Low-privilege user; session cookie holds the flag |
| `bob`   | `hunter2`   | Second account for comparison  |

## Docs

```
docs/01-introduction.md    what this bug is and why it matters
docs/02-background.md      Same-Origin Policy and CORS explained
docs/03-finding-the-bug.md confirming the misconfiguration with curl
docs/04-exploitation.md    scripted cross-origin credential read
docs/05-defense.md         allowlist fix and detection guidance
```

Stuck? `solutions/walkthrough.md` has the full solution.

## Stop the lab

```bash
docker compose down
```

## Requirements

- Docker with Compose installed (see below if not installed)
- Linux, macOS, or Windows with WSL2
- x86_64 or AArch64 (Apple Silicon, ARM64)

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

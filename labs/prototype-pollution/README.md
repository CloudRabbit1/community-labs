# prototype-pollution: Bypass admin authentication via Object.prototype poisoning

A Node.js note-sharing API merges user-supplied JSON without filtering `__proto__`. Sending `{"__proto__": {"isAdmin": true}}` to the merge endpoint poisons `Object.prototype`, causing every subsequent empty-object admin check to pass.

> This container binds to `127.0.0.1` only. Never expose port 8080 beyond localhost.

## Get this lab

**Recommended. Sparse checkout (git only fetches this lab):**
```bash
git clone --filter=blob:none --sparse https://github.com/CloudRabbit1/community-labs
cd community-labs
git sparse-checkout set labs/prototype-pollution
```

**SVN export (no git required):**
```bash
svn export https://github.com/CloudRabbit1/community-labs/trunk/labs/prototype-pollution
```

**curl + tar (zero dependencies):**
```bash
curl -sL https://github.com/CloudRabbit1/community-labs/archive/refs/heads/master.tar.gz \
  | tar xz --strip=3 "community-labs-master/labs/prototype-pollution"
```

Or clone the full repo if you want all labs: `git clone https://github.com/CloudRabbit1/community-labs`

## Quick start

```bash
docker compose up --build -d
```

The first run builds the container. Expect 1 to 2 minutes. Subsequent starts use the cached image and are instant.

The lab listens on `127.0.0.1:8080`.

## Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Service info |
| `/notes` | GET | List notes |
| `/notes` | POST | Create a note |
| `/notes/merge` | POST | Merge options into a note |
| `/admin/flag` | GET | Read the flag (admin only) |

## Docs

```
docs/01-introduction.md    what this bug is and why it matters
docs/02-background.md      concepts you need before starting
docs/03-finding-the-bug.md confirming the vulnerable merge behaviour
docs/04-exploitation.md    building the exploit
docs/05-defense.md         detection and fixes
```

Stuck? `solutions/walkthrough.md` has the full solution.

## Stop the lab

```bash
docker compose down
```

## Requirements

- Docker with Compose (see below if not installed)
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

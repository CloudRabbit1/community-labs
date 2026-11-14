# LAB-NAME: One-line description of what the student does

One sentence explaining what vulnerability this lab covers and what the student learns.

> This container binds to `127.0.0.1` only. Never expose port 2222 beyond localhost.

## Get this lab

**Recommended. Sparse checkout (git only fetches this lab):**
```bash
git clone --filter=blob:none --sparse https://github.com/CloudRabbit1/community-labs
cd community-labs
git sparse-checkout set LAB-NAME
```

**SVN export (no git required):**
```bash
svn export https://github.com/CloudRabbit1/community-labs/trunk/LAB-NAME
```

**curl + tar (zero dependencies):**
```bash
curl -sL https://github.com/CloudRabbit1/community-labs/archive/refs/heads/master.tar.gz \
  | tar xz --strip=2 "community-labs-master/LAB-NAME"
```

Or clone the full repo if you want all labs: `git clone https://github.com/CloudRabbit1/community-labs`

## Quick start

```bash
docker compose up --build -d
```

The first run builds the container. Expect X to Y minutes. Subsequent starts use the cached image and are instant.

The lab listens on `127.0.0.1:2222`.

## Accounts

| Account   | Purpose |
|-----------|---------|
| `user1`   | flag1 is in its home directory |
| `user2`   | flag2 is in its home directory |

## Docs

```
docs/01-introduction.md    what this bug is and why it matters
docs/02-background.md      concepts you need before starting
docs/03-finding-the-bug.md verifying the pieces inside the container
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

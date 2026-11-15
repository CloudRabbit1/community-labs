# Advanced Container Escape via Docker Socket

A containerized web application exposes the Docker socket API. An attacker who reaches the app can use the socket to create a privileged container with the host filesystem mounted, then read host files directly. This lab walks through discovering the exposed socket, crafting the escape container, and capturing both flags.

> This container binds to `127.0.0.1` only. Never expose port 8113 beyond localhost.

## Get this lab

**Recommended. Sparse checkout (git only fetches this lab):**
```bash
git clone --filter=blob:none --sparse https://github.com/CloudRabbit1/community-labs
cd community-labs
git sparse-checkout set labs/advanced-container-escapes
```

**SVN export (no git required):**
```bash
svn export https://github.com/CloudRabbit1/community-labs/trunk/labs/advanced-container-escapes
```

**curl + tar (zero dependencies):**
```bash
curl -sL https://github.com/CloudRabbit1/community-labs/archive/refs/heads/master.tar.gz \
  | tar xz --strip=3 "community-labs-master/labs/advanced-container-escapes"
```

Or clone the full repo if you want all labs: `git clone https://github.com/CloudRabbit1/community-labs`

## Quick start

```bash
docker compose up --build -d
```

The first run builds the container. Expect 1 to 3 minutes. Subsequent starts use the cached image and are instant.

The lab listens on `http://127.0.0.1:8113`.

## Flags

| Flag | Location |
|------|----------|
| Flag 1 | Returned from the Docker info endpoint, confirming socket exposure |
| Flag 2 | Returned after creating a privileged container with host filesystem mounted |

## Docs

```
docs/01-introduction.md    what this bug is and why it matters
docs/02-background.md      concepts you need before starting
docs/03-finding-the-bug.md discovering the exposed Docker socket
docs/04-exploitation.md    creating the escape container
docs/05-defense.md         detection and fixes
```

Stuck? `solutions/walkthrough.md` has the full solution.

## Stop the lab

```bash
docker compose down
```

## Requirements

- Docker with Compose
- Linux, macOS, or Windows with WSL2
- x86_64 or AArch64

## Installing Docker

**Kali / Debian / Ubuntu:**

```bash
sudo apt update && sudo apt install -y docker.io docker-compose-plugin
sudo systemctl start docker && sudo systemctl enable docker
sudo usermod -aG docker $USER
```

Log out and back in after the last command.

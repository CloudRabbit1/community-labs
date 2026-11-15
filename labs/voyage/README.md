# Multi-Stage Web Exploit: LFI to Command Injection

A three-stage exploit chain starting from an unauthenticated position. Local File Inclusion in a file viewer exposes a configuration file containing admin credentials. Those credentials unlock an admin panel. The admin panel's ping utility has unsanitized command injection, giving remote code execution.

> This container binds to `127.0.0.1` only. Never expose port 8115 beyond localhost.

## Get this lab

**Recommended. Sparse checkout (git only fetches this lab):**
```bash
git clone --filter=blob:none --sparse https://github.com/CloudRabbit1/community-labs
cd community-labs
git sparse-checkout set labs/voyage
```

**SVN export (no git required):**
```bash
svn export https://github.com/CloudRabbit1/community-labs/trunk/labs/voyage
```

**curl + tar (zero dependencies):**
```bash
curl -sL https://github.com/CloudRabbit1/community-labs/archive/refs/heads/master.tar.gz \
  | tar xz --strip=3 "community-labs-master/labs/voyage"
```

Or clone the full repo if you want all labs: `git clone https://github.com/CloudRabbit1/community-labs`

## Quick start

```bash
docker compose up --build -d
```

The first run builds the container. Expect 1 to 3 minutes. Subsequent starts use the cached image and are instant.

The lab listens on `http://127.0.0.1:8115`.

## Flags

| Flag | Location |
|------|----------|
| Flag 1 | Returned from admin login after LFI reveals credentials |
| Flag 2 | Returned from command injection in the admin ping utility |

## Docs

```
docs/01-introduction.md    what this challenge is about
docs/02-background.md      concepts you need before starting
docs/03-finding-the-bug.md confirming each vulnerability
docs/04-exploitation.md    chaining all three stages
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

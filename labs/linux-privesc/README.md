# linux-privesc: SUID, sudo, writable scripts, and Linux capabilities

Four privilege escalation paths on a single Linux target. SSH in as a low-privilege user and read four root-owned flags, one per technique: SUID binary, sudo find, world-writable sudo script, and a file capability on Python.

> This container binds to `127.0.0.1` only. Never expose port 2222 beyond localhost.

## Get this lab

**Recommended. Sparse checkout (git only fetches this lab):**
```bash
git clone --filter=blob:none --sparse https://github.com/CloudRabbit1/community-labs
cd community-labs
git sparse-checkout set labs/linux-privesc
```

**SVN export (no git required):**
```bash
svn export https://github.com/CloudRabbit1/community-labs/trunk/labs/linux-privesc
```

**curl + tar (zero dependencies):**
```bash
curl -sL https://github.com/CloudRabbit1/community-labs/archive/refs/heads/master.tar.gz \
  | tar xz --strip=3 "community-labs-master/labs/linux-privesc"
```

Or clone the full repo if you want all labs: `git clone https://github.com/CloudRabbit1/community-labs`

## Quick start

```bash
docker compose up --build -d
```

The first run builds the container. Expect 2 to 4 minutes (installs build tools). Subsequent starts use the cached image and are faster.

SSH in on port 2222.

## Account

| Account | Password |
|---------|----------|
| `lowpriv` | `lowpriv123` |

```bash
ssh -p 2222 lowpriv@127.0.0.1
```

## Flags

Four root-owned flags at `/root/flag{1,2,3,4}.txt`. Each requires a different technique.

| Flag | Technique | Mechanism |
|------|-----------|-----------|
| flag1 | SUID binary | `/usr/local/bin/readfile` runs as root |
| flag2 | sudo find | `sudo find /root/flag2.txt -exec cat {} \;` |
| flag3 | writable sudo script | inject into `/opt/backup.sh`, then `sudo /opt/backup.sh` |
| flag4 | Linux capabilities | `/usr/local/bin/py3` has `cap_dac_read_search` |

## Docs

```
docs/01-introduction.md    what these four techniques are
docs/02-background.md      SUID, sudo, capabilities explained
docs/03-finding-the-bug.md enumeration commands that reveal each path
docs/04-exploitation.md    exploiting each path and reading each flag
docs/05-defense.md         how to audit and fix each misconfiguration
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

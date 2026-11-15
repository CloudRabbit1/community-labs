# webserver-misconfig: Apache directory listing and CGI command injection

Two Apache httpd misconfigurations on a single target: a backup directory with listing enabled exposes a configuration file containing flag1, and a CGI network diagnostic tool passes user input unsanitized to bash, giving you OS command injection for flag2.

> This container binds to `127.0.0.1` only. Never expose port 8080 beyond localhost.

## Get this lab

**Recommended. Sparse checkout (git only fetches this lab):**
```bash
git clone --filter=blob:none --sparse https://github.com/CloudRabbit1/community-labs
cd community-labs
git sparse-checkout set labs/webserver-misconfig
```

**SVN export (no git required):**
```bash
svn export https://github.com/CloudRabbit1/community-labs/trunk/labs/webserver-misconfig
```

**curl + tar (zero dependencies):**
```bash
curl -sL https://github.com/CloudRabbit1/community-labs/archive/refs/heads/master.tar.gz \
  | tar xz --strip=3 "community-labs-master/labs/webserver-misconfig"
```

Or clone the full repo if you want all labs: `git clone https://github.com/CloudRabbit1/community-labs`

## Quick start

```bash
docker compose up --build -d
```

The first run builds the container. Expect 1 to 2 minutes. Subsequent starts use the cached image and are faster.

Apache listens on `127.0.0.1:8080`.

## Flags

| Flag | Technique | Path |
|------|-----------|------|
| flag1 | directory listing | browse `/backup/`, download `config.bak` |
| flag2 | CGI command injection | inject into `host` parameter of `/cgi-bin/status.sh` |

## Docs

```
docs/01-introduction.md    what these misconfigurations are
docs/02-background.md      Apache Options, CGI, and shell injection
docs/03-finding-the-bug.md reconnaissance and finding each flaw
docs/04-exploitation.md    capturing both flags
docs/05-defense.md         correct Apache configuration and input handling
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

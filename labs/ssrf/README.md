# SSRF: Server-Side Request Forgery to Internal Metadata Service

A URL fetcher proxies HTTP requests on behalf of the user. An internal metadata service on port 9000 holds the flag and is only reachable from the server process, not from outside the container. By supplying `http://127.0.0.1:9000/secret` as the URL, the attacker uses the server as a proxy to reach the otherwise-inaccessible internal service.

> This container binds to `127.0.0.1` only. Never expose port 8083 beyond localhost.

## Get this lab

**Recommended. Sparse checkout (git only fetches this lab):**
```bash
git clone --filter=blob:none --sparse https://github.com/CloudRabbit1/community-labs
cd community-labs
git sparse-checkout set labs/ssrf
```

**SVN export (no git required):**
```bash
svn export https://github.com/CloudRabbit1/community-labs/trunk/labs/ssrf
```

**curl + tar (zero dependencies):**
```bash
curl -sL https://github.com/CloudRabbit1/community-labs/archive/refs/heads/master.tar.gz \
  | tar xz --strip=3 "community-labs-master/labs/ssrf"
```

Or clone the full repo if you want all labs: `git clone https://github.com/CloudRabbit1/community-labs`

## Quick start

```bash
docker compose up --build -d
```

The first run builds the container. Expect 1 to 3 minutes. Subsequent starts are instant.

The lab listens on `127.0.0.1:8083`.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Service info |
| GET | `/fetch?url=<url>` | Fetch a URL and return the response body |

## Docs

```
docs/01-introduction.md    what SSRF is and why it matters
docs/02-background.md      internal services and cloud metadata APIs
docs/03-finding-the-bug.md confirming the fetch endpoint is vulnerable
docs/04-exploitation.md    targeting the internal metadata service
docs/05-defense.md         allowlists and network segmentation
```

Stuck? `solutions/walkthrough.md` has the full solution.

## Stop the lab

```bash
docker compose down
```

## Requirements

- Docker with Compose
- curl or Python 3

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

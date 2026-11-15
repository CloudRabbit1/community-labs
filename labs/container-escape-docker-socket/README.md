# Container Escape via Docker Socket SSRF

SSRF in a monitoring service reaches the unauthenticated Docker remote API. Create a privileged container with the host filesystem bind-mounted, exec into it, and read the flag.

**Category:** Container Security  
**Difficulty:** Medium  
**CVE:** N/A (misconfiguration pattern)

## Get this lab

**Recommended. Sparse checkout (git only fetches this lab):**
```bash
git clone --filter=blob:none --sparse https://github.com/CloudRabbit1/community-labs
cd community-labs
git sparse-checkout set labs/container-escape-docker-socket
```

**SVN export (no git required):**
```bash
svn export https://github.com/CloudRabbit1/community-labs/trunk/labs/container-escape-docker-socket
```

**curl + tar (zero dependencies):**
```bash
curl -sL https://github.com/CloudRabbit1/community-labs/archive/refs/heads/master.tar.gz \
  | tar xz --strip=3 "community-labs-master/labs/container-escape-docker-socket"
```

Or clone the full repo if you want all labs: `git clone https://github.com/CloudRabbit1/community-labs`

## Quick start

```bash
docker compose up --build -d

python3 exploit/exploit.py http://localhost:8080
# [*] Flag: POC{...}

docker compose down
```

## Lab contents

| Path | What it is |
|------|-----------|
| `lab/app.py` | Monitoring service (SSRF at /fetch) + simulated Docker daemon on port 2376 |
| `exploit/exploit.py` | Four-step exploit: probe → create container → create exec → start exec |
| `docs/` | Five documents: intro, SSRF and Docker background, finding the bug, exploitation, defense |
| `solutions/walkthrough.md` | Full solution. manual and automated |
| `test.sh` | CI harness |

## Requirements

- Docker and Docker Compose
- Python 3 (stdlib only)

# Multi-Stage Web Exploit Chain: SQLi to SSRF

Three vulnerabilities chain together to compromise this application. First, a SQL injection in the search endpoint leaks the admin password hash. Second, the MD5 hash cracks to a known password. Third, an authenticated import feature is vulnerable to SSRF, giving access to an internal service.

> This container binds to `127.0.0.1` only. Never expose port 8114 beyond localhost.

## Get this lab

**Recommended. Sparse checkout (git only fetches this lab):**
```bash
git clone --filter=blob:none --sparse https://github.com/CloudRabbit1/community-labs
cd community-labs
git sparse-checkout set labs/sequence
```

**SVN export (no git required):**
```bash
svn export https://github.com/CloudRabbit1/community-labs/trunk/labs/sequence
```

**curl + tar (zero dependencies):**
```bash
curl -sL https://github.com/CloudRabbit1/community-labs/archive/refs/heads/master.tar.gz \
  | tar xz --strip=3 "community-labs-master/labs/sequence"
```

Or clone the full repo if you want all labs: `git clone https://github.com/CloudRabbit1/community-labs`

## Quick start

```bash
docker compose up --build -d
```

The first run builds the container. Expect 1 to 3 minutes. Subsequent starts use the cached image and are instant.

The lab listens on `http://127.0.0.1:8114`.

## Flags

| Flag | Location |
|------|----------|
| Flag 1 | Returned on successful admin login after cracking the leaked hash |
| Flag 2 | Returned from the internal service via SSRF on the import endpoint |

## Docs

```
docs/01-introduction.md    what this lab is and why chaining matters
docs/02-background.md      SQLi, MD5 hash cracking, and SSRF concepts
docs/03-finding-the-bug.md confirming each vulnerability
docs/04-exploitation.md    the full three-stage chain
docs/05-defense.md         parameterized queries, bcrypt, URL allowlists
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

# Subdomain Takeover via Dangling CNAME

A company subdomain has a CNAME pointing to a deleted Netlify site. An attacker discovers the dangling record, registers the external service, and serves a malicious XSS payload on the original subdomain to steal an admin session cookie. This lab walks through subdomain enumeration, service registration, and cross-subdomain cookie theft.

> This container binds to `127.0.0.1` only. Never expose port 8112 beyond localhost.

## Get this lab

**Recommended. Sparse checkout (git only fetches this lab):**
```bash
git clone --filter=blob:none --sparse https://github.com/CloudRabbit1/community-labs
cd community-labs
git sparse-checkout set labs/subdomain-takeover
```

**SVN export (no git required):**
```bash
svn export https://github.com/CloudRabbit1/community-labs/trunk/labs/subdomain-takeover
```

**curl + tar (zero dependencies):**
```bash
curl -sL https://github.com/CloudRabbit1/community-labs/archive/refs/heads/master.tar.gz \
  | tar xz --strip=3 "community-labs-master/labs/subdomain-takeover"
```

Or clone the full repo if you want all labs: `git clone https://github.com/CloudRabbit1/community-labs`

## Quick start

```bash
docker compose up --build -d
```

The first run builds the container. Expect 1 to 3 minutes. Subsequent starts use the cached image and are instant.

The lab listens on `http://127.0.0.1:8112`.

## Flags

| Flag | Location |
|------|----------|
| Flag 1 | Returned from the DNS check endpoint when the dangling CNAME is found |
| Flag 2 | Returned when the XSS payload executes on the claimed subdomain |

## Docs

```
docs/01-introduction.md    what subdomain takeover is and why it matters
docs/02-background.md      DNS CNAMEs, dangling records, and XSS scope
docs/03-finding-the-bug.md discovering the dangling CNAME
docs/04-exploitation.md    claiming the subdomain and triggering XSS
docs/05-defense.md         prevention and monitoring
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

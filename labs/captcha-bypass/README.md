# CAPTCHA Bypass Techniques

A login form protected by a CAPTCHA that reveals its own seed in the challenge text, making the answer trivially computable. The tokens are also never invalidated after use, allowing unlimited replay. This lab covers both predictable CAPTCHA answer bypass and token replay attacks.

> This container binds to `127.0.0.1` only. Never expose port 8111 beyond localhost.

## Get this lab

**Recommended. Sparse checkout (git only fetches this lab):**
```bash
git clone --filter=blob:none --sparse https://github.com/CloudRabbit1/community-labs
cd community-labs
git sparse-checkout set labs/captcha-bypass
```

**SVN export (no git required):**
```bash
svn export https://github.com/CloudRabbit1/community-labs/trunk/labs/captcha-bypass
```

**curl + tar (zero dependencies):**
```bash
curl -sL https://github.com/CloudRabbit1/community-labs/archive/refs/heads/master.tar.gz \
  | tar xz --strip=3 "community-labs-master/labs/captcha-bypass"
```

Or clone the full repo if you want all labs: `git clone https://github.com/CloudRabbit1/community-labs`

## Quick start

```bash
docker compose up --build -d
```

The first run builds the container. Expect 1 to 3 minutes. Subsequent starts use the cached image and are instant.

The lab listens on `http://127.0.0.1:8111`.

## Flags

| Flag | Location |
|------|----------|
| Flag 1 | Returned from the `/captcha` endpoint |
| Flag 2 | Returned from `/login` after a successful CAPTCHA bypass |

## Docs

```
docs/01-introduction.md    what CAPTCHA bypass is and why predictable CAPTCHAs fail
docs/02-background.md      how CAPTCHAs work and what makes them weak
docs/03-finding-the-bug.md confirming both vulnerabilities
docs/04-exploitation.md    computing the answer and replaying tokens
docs/05-defense.md         fixing predictable CAPTCHAs and token replay
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

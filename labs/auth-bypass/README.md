# auth-bypass: unsigned session cookies and predictable reset tokens

Exploit two authentication bypass flaws: forge an admin session by decoding and re-encoding an unsigned base64 cookie, then take over another account by computing its predictable password reset token.

> This container binds to `127.0.0.1` only. Never expose port 5000 beyond localhost.

## Get this lab

**Recommended. Sparse checkout (git only fetches this lab):**
```bash
git clone --filter=blob:none --sparse https://github.com/CloudRabbit1/community-labs
cd community-labs
git sparse-checkout set labs/auth-bypass
```

**SVN export (no git required):**
```bash
svn export https://github.com/CloudRabbit1/community-labs/trunk/labs/auth-bypass
```

**curl + tar (zero dependencies):**
```bash
curl -sL https://github.com/CloudRabbit1/community-labs/archive/refs/heads/master.tar.gz \
  | tar xz --strip=3 "community-labs-master/labs/auth-bypass"
```

Or clone the full repo if you want all labs: `git clone https://github.com/CloudRabbit1/community-labs`

## Quick start

```bash
docker compose up --build -d
```

The first run builds the container. Expect 1 to 2 minutes. Subsequent starts use the cached image and are faster.

The API listens on `127.0.0.1:5000`.

## Accounts

| Account | Password | Purpose |
|---------|----------|---------|
| `alice` | `alice123` | starting account |
| `bob` | unknown | holds flag2, password must be reset |
| `admin` | unknown | admin panel holds flag1 |

## Flags

| Flag | Technique | Path |
|------|-----------|------|
| flag1 | unsigned cookie forgery | `GET /api/admin` with forged admin cookie |
| flag2 | predictable reset token | reset bob's password, then `GET /api/profile` |

## Docs

```
docs/01-introduction.md    what these flaws are and why they matter
docs/02-background.md      session cookies, tokens, and what "signed" means
docs/03-finding-the-bug.md decoding the cookie and discovering the token pattern
docs/04-exploitation.md    capturing both flags step by step
docs/05-defense.md         signed cookies and cryptographically random tokens
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

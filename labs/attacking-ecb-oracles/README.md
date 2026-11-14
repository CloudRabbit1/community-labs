# ECB Oracle Attack

Byte-at-a-time secret recovery against an AES-ECB encryption oracle. No key, no brute force. Just chosen-plaintext requests and block comparison.

**Topic:** AES-ECB mode weakness / chosen-plaintext oracle attack  
**Difficulty:** Intermediate  
**Prerequisites:** Basic Python, understanding that AES processes 16-byte blocks

## Get this lab

**Recommended. Sparse checkout (git only fetches this lab):**
```bash
git clone --filter=blob:none --sparse https://github.com/CloudRabbit1/community-labs
cd community-labs
git sparse-checkout set labs/attacking-ecb-oracles
```

**SVN export (no git required):**
```bash
svn export https://github.com/CloudRabbit1/community-labs/trunk/labs/attacking-ecb-oracles
```

**curl + tar (zero dependencies):**
```bash
curl -sL https://github.com/CloudRabbit1/community-labs/archive/refs/heads/master.tar.gz \
  | tar xz --strip=3 "community-labs-master/labs/attacking-ecb-oracles"
```

Or clone the full repo if you want all labs: `git clone https://github.com/CloudRabbit1/community-labs`

## Quick start

```bash
docker compose up --build -d

python3 exploit/exploit.py http://localhost:5000
# [+] Secret: POC{...}

docker compose down
```

## Lab contents

| Path | What it is |
|------|-----------|
| `lab/app.py` | The encryption oracle. encrypts your input + secret flag |
| `exploit/exploit.py` | Byte-at-a-time ECB decryption script |
| `docs/` | Five documents: intro, ECB background, detection, exploitation, defense |
| `solutions/walkthrough.md` | Full solution with every command and expected output |
| `test.sh` | CI harness |

## Requirements

- Docker and Docker Compose
- Python 3 (stdlib only)

## Notes

The oracle uses only the openssl binary for AES-ECB. No Python crypto library dependencies. The flag regenerates on every container start. The exploit makes at most 256 × flag_length oracle calls.

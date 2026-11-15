# AWS IAM PassRole Privilege Escalation

Low-privilege IAM user escalates to administrator via `iam:PassRole` and AWS Lambda. Classic cloud privilege escalation found in real-world AWS environments.

**Category:** Cloud Security / AWS IAM  
**Difficulty:** Medium  
**CVE:** N/A (misconfiguration pattern)

## Get this lab

**Recommended. Sparse checkout (git only fetches this lab):**
```bash
git clone --filter=blob:none --sparse https://github.com/CloudRabbit1/community-labs
cd community-labs
git sparse-checkout set labs/aws-iam-privesc
```

**SVN export (no git required):**
```bash
svn export https://github.com/CloudRabbit1/community-labs/trunk/labs/aws-iam-privesc
```

**curl + tar (zero dependencies):**
```bash
curl -sL https://github.com/CloudRabbit1/community-labs/archive/refs/heads/master.tar.gz \
  | tar xz --strip=3 "community-labs-master/labs/aws-iam-privesc"
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
| `lab/app.py` | Simulated AWS IAM and Lambda API |
| `exploit/exploit.py` | Four-step exploit: enumerate → list roles → create Lambda → invoke |
| `docs/` | Five documents: intro, IAM background, finding the bug, exploitation, defense |
| `solutions/walkthrough.md` | Full solution. manual and automated |
| `test.sh` | CI harness |

## Requirements

- Docker and Docker Compose
- Python 3 (stdlib only)

# Azure Lateral Movement: Managed Identity Hop Chain

Three-hop lateral movement through Azure services using a VM's Managed Identity. IMDS → Key Vault → Blob Storage. No credentials required upfront.

**Topic:** Azure Managed Identity abuse / lateral movement  
**Difficulty:** Intermediate  
**Prerequisites:** Basic HTTP, familiarity with cloud IAM concepts

## Get this lab

**Recommended. Sparse checkout (git only fetches this lab):**
```bash
git clone --filter=blob:none --sparse https://github.com/CloudRabbit1/community-labs
cd community-labs
git sparse-checkout set labs/azure-lateral-movement
```

**SVN export (no git required):**
```bash
svn export https://github.com/CloudRabbit1/community-labs/trunk/labs/azure-lateral-movement
```

**curl + tar (zero dependencies):**
```bash
curl -sL https://github.com/CloudRabbit1/community-labs/archive/refs/heads/master.tar.gz \
  | tar xz --strip=3 "community-labs-master/labs/azure-lateral-movement"
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
| `lab/app.py` | Simulates IMDS, Azure Key Vault, and Azure Blob Storage |
| `exploit/exploit.py` | Three-hop exploit chain |
| `docs/` | Five documents: intro, Azure identity background, detection, exploitation, defense |
| `solutions/walkthrough.md` | Full solution. manual and automated |
| `test.sh` | CI harness |

## Requirements

- Docker and Docker Compose
- Python 3 (stdlib only)

## Notes

The lab simulates the Azure IMDS at `/metadata/identity/oauth2/token`, Key Vault at `/secrets/`, and Blob Storage at `/blob/`. Tokens are signed HS256 JWTs. All secrets regenerate on every container start.

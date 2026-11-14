# Introduction

Azure Managed Identities let a VM authenticate to other Azure services without storing credentials. The VM queries the Azure Instance Metadata Service (IMDS) at a link-local address, gets a JWT, and uses that JWT as a Bearer token against Azure APIs. No password, no service principal secret.

When an attacker gains code execution on that VM, through any means, they inherit the Managed Identity. From there, they can query Azure Key Vault, read secrets, access storage accounts, and pivot to other subscriptions, all without touching a password file.

This lab simulates a two-hop chain:

1. Query IMDS to get a Managed Identity JWT.
2. Use the JWT to read a secret from Key Vault.
3. Use the secret to access Blob Storage and retrieve the flag.

Each hop is a separate Azure service call. No credentials are known upfront.

## Requirements

- Docker and Docker Compose
- Python 3 (stdlib only)

```bash
docker compose up --build -d
```

The lab runs on `http://localhost:8080`.

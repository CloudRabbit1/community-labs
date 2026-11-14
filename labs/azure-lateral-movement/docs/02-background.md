# Background

## Azure Instance Metadata Service

Every Azure VM can reach the IMDS endpoint at `169.254.169.254`. This is a link-local address routable only from the VM itself. An application running on the VM queries it to get metadata, including Managed Identity tokens.

```
GET http://169.254.169.254/metadata/identity/oauth2/token
    ?resource=https://vault.azure.net
    &api-version=2018-02-01
Header: Metadata: true
```

The `Metadata: true` header is required. It prevents web browsers and other clients from making cross-site requests to the endpoint, since browsers do not send custom headers by default.

The response contains an `access_token`. A JWT that tells Azure services "this request comes from VM1's Managed Identity."

## Azure Key Vault

Key Vault stores secrets, certificates, and cryptographic keys. When a request arrives with a valid Bearer token, Key Vault checks whether that identity has the `Key Vault Secrets User` role and returns the secret value.

If the VM's Managed Identity has that role assigned, any process on the VM can read the secret. No additional credentials needed.

## Azure Blob Storage

Blob Storage accepts authentication via storage access keys. These are long random strings that grant full access to a storage account. If a Key Vault stores a storage access key as a secret, compromising Key Vault gives full access to the storage account.

## Why this is a problem

A single compromised VM can pivot:
1. VM code execution → IMDS token (no access control, any process on the VM)
2. IMDS token → Key Vault secret (depends on RBAC)
3. Key Vault secret → storage account (full access with the key)

Each step requires a separate privilege, but organizations frequently grant broad roles to Managed Identities for convenience. The result is a hop chain that leads from a low-value VM to sensitive data.

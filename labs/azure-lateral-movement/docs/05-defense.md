# Defense

## Principle of least privilege for Managed Identities

Assign the narrowest role possible. A VM running a web application does not need to read secrets from every vault in the subscription. Create a dedicated vault for each application, assign only the secrets that application needs, and scope the RBAC role to that vault.

```
Wrong: VM → Key Vault Secrets User on /subscriptions/<id>
Right: VM → Key Vault Secrets Reader on /subscriptions/<id>/resourceGroups/<rg>/providers/Microsoft.KeyVault/vaults/<app-vault>
```

## Do not store storage account keys in Key Vault

Storage account keys grant full access to all blobs, tables, queues, and files in the account. Storing them in Key Vault widens the blast radius: anyone who can read Key Vault secrets gets storage access too.

Use Managed Identity directly against storage. Azure Storage supports role-based access:

```
Wrong: Store storage key in Key Vault, grant VM Key Vault Secrets User
Right: Grant VM Storage Blob Data Reader on the specific container
```

This eliminates the second hop entirely.

## Restrict Managed Identity scope

Managed Identities should only have permissions on the resources the VM actually uses. Run Azure Advisor and Microsoft Defender for Cloud regularly to find over-privileged identities.

## Monitor IMDS queries

Log and alert on IMDS token requests for unusual resources. A VM that handles web traffic should not be requesting tokens for `https://management.azure.com`. Requests for that resource indicate credential theft or lateral movement.

Azure Diagnostic Settings can send IMDS logs to a Log Analytics workspace for query and alerting.

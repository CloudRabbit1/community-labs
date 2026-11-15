# 05: Defense

## Remove debug endpoints before deployment

The `/api/read?path=` endpoint is a debug tool that was left in production. Debug endpoints that read arbitrary files must be gated by an environment variable and disabled in production:

```python
import os

@app.get('/api/read')
def api_read():
    if os.environ.get('DEBUG') != 'true':
        abort(404)
    # ... rest of handler
```

## Avoid hostPath volumes

HostPath volumes are inherently dangerous. Use alternatives:

| Use case | Secure alternative |
|----------|-------------------|
| Shared storage between pods | PersistentVolumeClaim with a network storage backend |
| Node log collection | DaemonSet with specific, read-only hostPath paths scoped to log directories |
| Node-level monitoring | Privileged daemonset with minimal scope, not application pods |

The Kubernetes docs note that hostPath volumes present security risks and should be avoided when possible. When required (log collectors, monitoring agents), limit the mount to the minimum required path and set it read-only:

```yaml
volumes:
  - name: logs
    hostPath:
      path: /var/log/app
      type: DirectoryOrCreate
volumeMounts:
  - name: logs
    mountPath: /mnt/logs
    readOnly: true
```

## Protect environment variables

Do not inject secrets as environment variables if they are sensitive. Use mounted secrets instead, and restrict access to the mount path:

```yaml
# Instead of:
env:
  - name: DB_PASSWORD
    value: supersecret  # visible in /proc/self/environ

# Use:
envFrom:
  - secretRef:
      name: db-secret   # still in environ, but rotatable

# Best: mount as file, read once at startup, then unset from env
```

## Kubernetes Pod Security Standards

Enable Pod Security Standards (PSS) at the namespace level to prevent pods from mounting hostPath volumes:

```yaml
apiVersion: v1
kind: Namespace
metadata:
  labels:
    pod-security.kubernetes.io/enforce: restricted
```

The `restricted` policy denies hostPath volumes, privileged containers, host networking, and other high-risk configurations.

## CVE-2024-21626 mitigation

For the runc CWD escape (CVE-2024-21626), update to runc >= 1.1.12 or containerd >= 1.7.14. These versions close the file descriptor leak that allowed WORKDIR `/proc/self/fd/7` to resolve to a host path.

# Defense

## Never expose the Docker socket over TCP without authentication

The Docker remote API has no authentication by default. Binding it to `0.0.0.0` or even `127.0.0.1:2376` is dangerous when the same host runs any service with SSRF potential.

If you need remote Docker control, use TLS client certificates. Without them, anyone who can reach the port controls the host.

```
# In /etc/docker/daemon.json: TLS required
{
  "hosts": ["tcp://0.0.0.0:2376"],
  "tlsverify": true,
  "tlscacert": "/etc/docker/ca.pem",
  "tlscert": "/etc/docker/server-cert.pem",
  "tlskey": "/etc/docker/server-key.pem"
}
```

The default Unix socket at `/var/run/docker.sock` is safer: only processes that can access the socket file can use the API. Control access to that file with standard Unix permissions.

## Add SSRF protection to URL-fetch endpoints

Validate the target URL before making the request. At minimum, block requests to RFC 1918 addresses (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`) and loopback (`127.0.0.0/8`):

```python
import ipaddress, socket

def is_internal(url):
    host = urllib.parse.urlparse(url).hostname
    try:
        ip = ipaddress.ip_address(socket.gethostbyname(host))
        return ip.is_private or ip.is_loopback
    except Exception:
        return True  # deny on resolution failure

if is_internal(url):
    return 400, {"error": "Internal URLs are not allowed"}
```

A stricter control is an allowlist: only permit fetches to known-safe domains or IP ranges. Deny everything else.

## Use network segmentation

The Docker daemon on this host is reachable from inside the container because they share a network namespace. Isolating the Docker control plane to a separate network, with firewall rules that prevent application containers from reaching it, eliminates this lateral move even if SSRF is present.

## Run containers without Privileged and without broad bind mounts

A `Privileged: true` container with `/:/host-root` mapped is as powerful as root on the host. Neither should be the default. Use `readOnlyRootFilesystem: true` and mount only the specific paths the application needs, as read-only where possible.

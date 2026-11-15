# Defense

## Allowlist Outbound Destinations

The most effective control is to only allow fetches to a fixed set of approved hosts:

```python
from urllib.parse import urlparse

ALLOWED_HOSTS = {"api.example.com", "cdn.example.com"}

def safe_fetch(url):
    parsed = urlparse(url)
    if parsed.hostname not in ALLOWED_HOSTS:
        raise ValueError(f"host {parsed.hostname!r} not allowed")
    # ... proceed with the request
```

An allowlist fails closed: any host not explicitly approved is blocked.

## Blocklist Private Address Ranges

If an allowlist is too restrictive, block requests to RFC 1918 private ranges, loopback, link-local, and cloud metadata addresses:

```python
import ipaddress

BLOCKED = [
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("169.254.0.0/16"),  # link-local / metadata
    ipaddress.ip_network("::1/128"),
]

def is_safe(url):
    host = urlparse(url).hostname
    try:
        addr = ipaddress.ip_address(host)
    except ValueError:
        # It is a hostname: resolve it, then check
        import socket
        addr = ipaddress.ip_address(socket.gethostbyname(host))
    return not any(addr in net for net in BLOCKED)
```

Resolve hostnames before checking. DNS rebinding can bypass a check that only looks at the raw URL string.

## Disable Redirects

An attacker may supply a URL that redirects to an internal address. Disable automatic redirect following, or recheck the final URL after each redirect:

```python
# requests library: disable redirects
response = requests.get(url, allow_redirects=False)

# urllib: custom redirect handler that checks each hop
class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise urllib.error.URLError("redirect to external URL not allowed")
```

## Network Segmentation

Segregate the web application into a network that cannot reach internal infrastructure. The application should only be able to reach the services it needs, not the entire internal network or cloud metadata API.

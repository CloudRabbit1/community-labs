# Defense

## Validate the Destination Before Fetching

Resolve the URL's hostname to an IP address and reject private ranges before making the request:

```python
import ipaddress, socket, urllib.parse

PRIVATE = [
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("169.254.0.0/16"),  # cloud metadata
    ipaddress.ip_network("::1/128"),
]

def is_safe(url: str) -> bool:
    host = urllib.parse.urlparse(url).hostname
    try:
        ip = ipaddress.ip_address(socket.gethostbyname(host))
    except Exception:
        return False
    return not any(ip in net for net in PRIVATE)
```

Reject the request if `is_safe()` returns False. For DNS rebinding protection, resolve the name once, pin the IP, and open the socket to that IP directly rather than re-resolving at connect time.

## Allowlist the Scheme and Port

A URL validator that only checks the hostname is not enough. Attackers can use:

- `file:///etc/passwd` to read local files
- `gopher://` to send raw TCP payloads
- `dict://` to reach Redis

Restrict the scheme to `https` only (or `http` for lab purposes). Block non-standard ports if possible.

## Remove the Feature If Not Needed

The safest URL fetch is one that never happens. If the preview feature can be replaced with server-side rendering at known, trusted URLs, the SSRF surface disappears entirely.

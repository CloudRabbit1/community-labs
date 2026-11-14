# Background

## Why SSRF Is Dangerous

When a server makes an outbound HTTP request, it uses its own network identity, not the attacker's. This matters because:

- Internal services often trust requests from localhost or the local subnet without authentication.
- Cloud metadata services (AWS IMDSv1, GCP metadata server) are accessible only from the instance. They return IAM credentials, SSH keys, and other sensitive data.
- Internal APIs and admin panels are frequently reachable from within the data center but not from the public internet.

A URL fetch feature bridges the gap between the attacker's network and the server's network.

## IP-Based Access Controls

Trusting an IP address as authentication is fragile. An IP check on an HTTP request works only when the network ensures the address cannot be spoofed. For localhost (127.0.0.1), it works against external callers. But when the server itself makes the request, the source IP is 127.0.0.1 by definition. The check cannot distinguish "a request from the server itself" from "a request the server was tricked into making."

## Restricting Outbound Fetches

The correct fix is to validate the destination before fetching:

1. Resolve the hostname to an IP.
2. Reject private ranges: 127.0.0.0/8, 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16, 169.254.0.0/16 (link-local / cloud metadata).
3. Enforce the allowlist after resolution, not on the raw hostname, to defeat DNS rebinding.

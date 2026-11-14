# Background

## Internal Services and Network Position

Cloud VMs, containers, and corporate servers often run services that are intentionally invisible to the internet: admin panels, health-check endpoints, internal APIs, and infrastructure metadata services. These services assume that only trusted code on the same machine or network can reach them.

A web application that fetches URLs on behalf of users changes that assumption. The application process has the same network access as any other process on the machine, so it can reach `127.0.0.1`, the Docker bridge subnet (`172.16.0.0/12`), or any service accessible from the host.

## Cloud Metadata APIs

Cloud providers expose instance metadata on a well-known address:

| Provider | Metadata URL |
|----------|-------------|
| AWS | `http://169.254.169.254/latest/meta-data/` |
| GCP | `http://metadata.google.internal/computeMetadata/v1/` |
| Azure | `http://169.254.169.254/metadata/instance` |
| DigitalOcean | `http://169.254.169.254/metadata/v1/` |

These return instance identity, SSH keys, IAM role credentials, and sometimes user-data scripts that contain secrets. Fetching them through an SSRF-vulnerable server on a cloud VM is one of the most common SSRF impact scenarios.

## Blind vs. Reflected SSRF

In this lab, the response body is returned directly to the attacker (reflected SSRF). In real-world cases, the response may be suppressed. Blind SSRF is detected by observing side effects: DNS lookups, TCP connections to a collaborator server (Burp Collaborator, interactsh), or timing differences that reveal whether a port is open.

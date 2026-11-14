# Background

## SSRF

**Server-Side Request Forgery (SSRF)** is a vulnerability where you cause a server to make an HTTP request to a URL you control. The request comes from the server's network context, not yours. That matters because the server can reach internal services that your machine cannot.

A monitoring service that fetches URLs to check health endpoints is a common source of SSRF. The service needs to reach arbitrary URLs to do its job, so developers often do not restrict the target. The result: any caller can instruct the server to fetch internal resources.

## Docker remote API

Docker exposes a **remote API** that accepts HTTP requests and controls the Docker daemon. By default it listens on a Unix socket at `/var/run/docker.sock`. When configured to listen on a TCP port instead (using `-H tcp://...`), any process that can reach that port can control Docker. No authentication is required unless TLS client certificates are configured.

The remote API supports the full container lifecycle: create, start, exec, stop, remove. If you can reach it, you can run any command on the host.

## The privileged container escape

A container with `Privileged: true` and a host bind mount can read and write the host filesystem. The container runs as root. The bind mount maps the host's `/` to a path inside the container, such as `/host-root`. Commands that run inside the container see the host's files at that path.

You do not need to be on the host to do this. If you can reach the Docker API, you can create the container and exec into it remotely. The Docker daemon does the privileged work for you.

## Why the Docker daemon is on port 2376

The lab runs the Docker API simulator on `127.0.0.1:2376`, which is the conventional plaintext Docker TCP port (2376 for TLS, 2375 for plaintext. This lab uses plaintext). It is bound to localhost, so it is not reachable from outside the container. The SSRF bridges that gap.

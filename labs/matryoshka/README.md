# Matryoshka: Container Escape via cgroup v1 release_agent

A privileged Docker container exposes a command execution endpoint used for
infrastructure diagnostics. By mounting the cgroup v1 memory controller and
configuring a release_agent payload, you cause the host kernel to run your
script as root outside the container. Read the flag the payload writes.

**Difficulty:** Medium
**Category:** Container Escape

## Setup

Requires Docker and Docker Compose.

```
docker compose up --build -d
```

The service listens on `http://localhost:8080`.

## Goal

Escape the container and read `/flag.txt` from the host filesystem.

## Hints

- Check `/info` to confirm the container's privilege level.
- The cgroup v1 memory controller is at `/sys/fs/cgroup/memory`.
- `notify_on_release` fires `release_agent` when a cgroup empties.
- The kernel runs `release_agent` as root in the host namespace.

## Solution

See `solutions/walkthrough.md` or run the automated exploit:

```
python3 exploit/exploit.py http://localhost:8080
```

## Background reading

- `docs/02-background.md`: cgroups, release_agent, and privileged containers
- Felix Wilhelm's original writeup (2019): `cve-2019-5736` context

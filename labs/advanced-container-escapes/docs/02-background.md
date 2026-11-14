# Background

## The Docker socket

The Docker daemon listens on a Unix socket at `/var/run/docker.sock`. Any process with read/write access to this socket can send commands to the daemon using Docker's HTTP-over-Unix-socket API.

When a container mounts this socket with a volume bind like `-v /var/run/docker.sock:/var/run/docker.sock`, the container can communicate with the host Docker daemon as if it were running on the host directly.

## Privileged containers

A container started with `--privileged` has all Linux capabilities enabled and all device access granted. Combined with mounting the host filesystem, it effectively bypasses all container isolation.

The key combination: `Privileged: true` plus `Binds: ["/:/hostfs"]`. This creates a container that runs with full host privileges and can access every file on the host by looking under `/hostfs`.

## Why this is considered a full escape

From inside the privileged container:
- Read `/hostfs/etc/shadow` for password hashes
- Write to `/hostfs/etc/cron.d/` to schedule jobs as root on the host
- Execute commands via `nsenter --target 1 --mount --uts --ipc --net --pid` to enter the host's process namespace

The Docker socket escape is well-known but still found in real environments because convenience often wins over security in developer tooling.

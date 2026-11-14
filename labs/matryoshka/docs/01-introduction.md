# Matryoshka: Container Escape via cgroup v1 release_agent

A privileged Docker container is not a security boundary. This lab demonstrates
one of the most reliable techniques for escaping a privileged container: the
cgroup v1 release_agent attack discovered by Felix Wilhelm in 2019.

The target is a container that runs with the `--privileged` flag. It exposes a
diagnostic command execution endpoint. By mounting the cgroup v1 memory
controller inside the container and setting a release_agent script, you cause
the host kernel to execute an arbitrary command as root outside the container.

The flag is on the host filesystem. The release_agent payload copies it to a
path you can read from inside the container.

## What you will do

Mount a cgroup filesystem, configure a release_agent payload, trigger cgroup
deletion to fire the agent, and read the flag the payload writes.

## Prerequisites

- Docker and Docker Compose
- Python 3.x (stdlib only)
- Familiarity with Linux process management and filesystems

## Setup

```
docker compose up --build -d
```

The service listens on `http://localhost:8080`.

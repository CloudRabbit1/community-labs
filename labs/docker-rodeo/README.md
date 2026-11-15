# Docker Rodeo

A Docker management dashboard that exposes the host Docker socket via HTTP. Use its API proxy to create a privileged container, mount the secret vault volume, and read the flag.

## Quick Start

```bash
docker compose up --build -d
python3 exploit/exploit.py http://localhost:8080
```

## What You Learn

- Why mounting /var/run/docker.sock into a container is a critical misconfiguration
- How to interact with the Docker API over a Unix socket
- How an attacker with socket access can create privileged containers and escape to the host

## Lab Architecture

```
[exploit.py] --HTTP--> [app:8080] --Unix socket--> [/var/run/docker.sock] --> Docker daemon
                                                                                    |
                                                                              [new container]
                                                                              mounts: vault:/vault
                                                                              reads: /vault/flag.txt
```

## Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | Dashboard info |
| `GET /api/docker/containers/json` | List containers |
| `POST /api/docker/containers/create` | Create a container |
| `POST /api/docker/containers/{id}/start` | Start a container |
| `POST /api/docker/containers/{id}/wait` | Wait for a container to exit |
| `GET /api/docker/containers/{id}/logs` | Read container logs |
| `DELETE /api/docker/containers/{id}` | Remove a container |

## Prerequisites

- Docker and Docker Compose
- Python 3.x (for the exploit)

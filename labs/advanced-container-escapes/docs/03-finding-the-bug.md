# Finding the Bug

## Step 1: Confirm the lab is running

```
curl -s http://127.0.0.1:8113/
```

You should see the Container Management Portal home page.

## Step 2: Check the Docker info endpoint

```
curl -s http://127.0.0.1:8113/api/info
```

Expected response:

```json
{
  "DockerRootDir": "/var/lib/docker",
  "OperatingSystem": "Ubuntu 22.04.3 LTS",
  "ServerVersion": "24.0.5",
  "SocketPath": "/var/run/docker.sock",
  "flag1": "POC{...}"
}
```

The `SocketPath` field confirms the Docker socket is accessible from inside the container. This is the misconfiguration that makes the escape possible.

## Step 3: List running containers

```
curl -s http://127.0.0.1:8113/api/containers/json
```

This returns the current container list via the Docker socket API.

## Step 4: Understand the attack surface

The API exposes:
- `POST /api/containers/create` - create a new container with custom HostConfig
- `POST /api/containers/<id>/start` - start a container
- `GET /api/escape` - check if an escape container is ready

The `HostConfig.Privileged` and `HostConfig.Binds` fields in the create request control whether the new container has host access.

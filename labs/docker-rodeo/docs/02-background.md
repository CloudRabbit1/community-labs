# Background

## The Docker Socket

The Docker daemon is a background process that manages containers, images, networks, and volumes. Client tools like `docker run` communicate with it over a Unix domain socket at `/var/run/docker.sock`. The Docker API is plain HTTP over that socket.

A Docker client making a request looks like this:

```
POST /containers/create HTTP/1.1
Host: localhost
Content-Type: application/json

{"Image": "alpine", "Cmd": ["cat", "/etc/passwd"]}
```

You can send this yourself with any HTTP client that supports Unix sockets, including Python's stdlib `socket` module.

## Why Socket Access Equals Root

When you create a container, you control its `HostConfig`. That config accepts:
- `Binds`: mount any path from the host into the container
- `Privileged`: disable all security restrictions
- `CapAdd`: add Linux capabilities

There is no access control inside the Docker socket. If you can send bytes to it, you can create a container that mounts the host filesystem at `/mnt/host` and reads anything, including `/etc/shadow`.

## Named Volumes

A Docker named volume is a directory managed by Docker, stored on the host at `/var/lib/docker/volumes/<name>/_data`. When a container mounts a named volume, it reads and writes the data there.

If a secret is stored in a named volume (instead of the container's filesystem), it persists across container restarts but is still accessible to any container that mounts the same volume name.

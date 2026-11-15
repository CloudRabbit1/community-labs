# Defense

## Never mount the Docker socket in containers

The root fix is to not mount `/var/run/docker.sock` inside containers. If a service needs to manage containers, use the Docker API over TCP with TLS client certificates and restrict access to that endpoint.

If you need container management from inside a container for CI/CD, evaluate Kaniko, Buildah, or Docker-in-Docker with explicit isolation instead of socket pass-through.

## Use rootless Docker

Rootless Docker runs the daemon as a non-root user. Even if an attacker escapes, they land as an unprivileged user on the host rather than root. This significantly limits the blast radius.

## Block privileged container creation

Use an admission controller (Kubernetes OPA/Gatekeeper, or Docker authorization plugins) to reject any container creation request with `Privileged: true` or sensitive `Binds` entries like `/:`.

## AppArmor and seccomp profiles

Apply restrictive AppArmor profiles to containers. The default Docker seccomp profile blocks a subset of dangerous syscalls. Custom profiles can further restrict what a container can do even with the socket mounted.

## Audit existing mounts

Run:

```
docker ps -q | xargs docker inspect --format '{{.Name}}: {{.HostConfig.Binds}}' | grep docker.sock
```

This finds any running container with the Docker socket mounted.

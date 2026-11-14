# Defense

## Never Mount the Docker Socket into a Container

The root cause here is the bind mount `/var/run/docker.sock:/var/run/docker.sock`. Remove it. If a containerized app needs to manage other containers, use a dedicated sidecar with the Docker SDK and limit its capabilities with an authorization plugin.

## Use Docker Authorization Plugins

Docker supports authorization plugins that can restrict which API calls are allowed. OPA (Open Policy Agent) can enforce policies such as "no container creation from inside a container."

## Use a High-Level Abstraction Instead

If the goal is to run jobs, use a task queue or a Kubernetes Job rather than calling the Docker daemon directly. The application never needs raw daemon access.

## Read-Only Mounts and No Privileged Containers

For any container that genuinely needs limited Docker access (a CI agent, for example), enforce:
- `--read-only` on the socket mount (still dangerous but reduces write-based attacks)
- Block `Privileged: true` via policy
- Block host bind mounts via policy

## Principle of Least Privilege

A web application serving HTTP has no legitimate reason to create Docker containers. The access granted to any process should match exactly what it needs to do its job. Overly permissive configurations are the most common source of container escapes in real environments.

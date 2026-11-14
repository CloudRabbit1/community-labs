# 02: Background

## Kubernetes pod security model

A Kubernetes pod runs one or more containers on a node. The container runtime (runc, crun, containerd) isolates each container using Linux namespaces and cgroups. The key namespaces are:

- **mount namespace**: the container sees its own filesystem, not the node's
- **pid namespace**: the container sees only its own processes (or a subset)
- **network namespace**: the container has its own network stack
- **user namespace**: (optional) the container maps uid 0 to a non-root uid on the host

When a pod is configured with a hostPath volume, the container runtime bind-mounts a node directory into the container's mount namespace. This is a deliberate hole in the mount isolation.

## /proc/self

The proc filesystem is a virtual filesystem that exposes kernel and process data. For any running process, `/proc/self` is a symlink to its own `/proc/<pid>` directory. Key files:

| Path | Contents |
|------|----------|
| `/proc/self/environ` | null-separated environment variables |
| `/proc/self/mounts` | current mount table |
| `/proc/self/status` | process status (uid, gid, memory) |
| `/proc/self/cmdline` | command line used to start the process |
| `/proc/self/fd/` | open file descriptors (CVE-2024-21626 vector) |

Kubernetes injects pod metadata, service account tokens, and secrets as environment variables or mounted files. Reading `/proc/self/environ` gives the full environment of the running process.

## hostPath volumes

A hostPath volume mounts a node directory into the pod:

```yaml
volumes:
  - name: node-data
    hostPath:
      path: /var/data
      type: Directory
```

Any process in the pod can read files from `/var/data` on the node. If the pod runs as root (uid 0) and the directory has permissive permissions, the pod can read or write node files that it should not be able to access.

## Service account tokens

Every Kubernetes pod automatically receives a service account token at `/var/run/secrets/kubernetes.io/serviceaccount/token`. This token authenticates the pod to the Kubernetes API server. If an attacker reads this token, they can call the API as that service account, potentially listing or modifying other pods, secrets, or configmaps within the namespace.

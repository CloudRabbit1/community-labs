# Defense

## Remove the Capability

The fix is to not grant `CAP_SYS_PTRACE` unless the container's specific workload
requires it. Performance monitoring that needs process inspection should run as a
privileged sidecar with a tightly scoped security policy, not as a capability
granted to an application container.

In `docker-compose.yml`:

```yaml
services:
  app:
    cap_drop:
      - ALL
    # Do NOT add CAP_SYS_PTRACE unless the application specifically requires it
```

## Do Not Share the Host PID Namespace

`--pid=host` removes PID namespace isolation entirely. Containers that need to
monitor host processes should use the Docker API or a dedicated monitoring agent
instead.

```yaml
services:
  app:
    pid: "host"   # Remove this line
```

## Use seccomp to Block ptrace Syscalls

Docker's default seccomp profile already blocks `ptrace`. Confirm that your
deployment has not disabled it:

```bash
docker inspect <container> | grep -i seccomp
```

If the value is `unconfined`, the seccomp filter is off. Apply the default:

```bash
docker run --security-opt seccomp=default ...
```

## Detection

Alert on any container that has `CAP_SYS_PTRACE` in its effective capability set.
Most application containers have no need for it. Inspect with:

```bash
docker inspect <container> --format '{{.HostConfig.CapAdd}}'
```

Any result containing `SYS_PTRACE` warrants review of that container's workload
and isolation configuration.

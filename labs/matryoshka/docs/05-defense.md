# Defense

## Do not run containers with --privileged

This is the root cause. Remove the flag. If a container needs specific
capabilities, grant only what it needs:

```yaml
# Instead of privileged: true, grant only what is required
cap_add:
  - NET_ADMIN
cap_drop:
  - ALL
```

For most workloads, `cap_drop: ALL` with no additions is sufficient.

## Use cgroup v2

The release_agent technique requires cgroup v1. Cgroup v2 (unified hierarchy)
does not have a `release_agent` file. Modern kernels (5.14+) and distributions
default to cgroup v2. Confirm with:

```
stat -f /sys/fs/cgroup
```

If the filesystem type is `cgroup2`, the technique does not apply.

## Restrict filesystem mounts with seccomp

The escape starts with a `mount` syscall. A seccomp profile that blocks `mount`
prevents the first step. Docker's default seccomp profile blocks it, but
`--privileged` disables the default profile. Apply an explicit seccomp profile
even on privileged containers for sensitive workloads.

## Audit container configurations in CI

Scan `docker-compose.yml` and Kubernetes manifests for `privileged: true`,
`CAP_SYS_ADMIN`, and `securityContext.privileged`. Tools like Trivy, Checkov,
and Falco flag these at build time and runtime.

## Use a container-aware kernel security module

AppArmor and SELinux policies can deny `mount` and `cgroup` operations even
in a privileged container. Docker applies an AppArmor profile by default;
passing `--security-opt apparmor=unconfined` removes that protection.

## Summary

The release_agent technique works because three defaults are overridden at
once: `--privileged` removes capability restrictions, disables seccomp, and
removes the AppArmor profile. Any one of those defaults, left in place,
stops the attack.

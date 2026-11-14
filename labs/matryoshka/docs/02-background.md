# Background: cgroups, release_agent, and Privileged Containers

## What a privileged container is

A Docker container normally runs in a constrained environment: it has a limited
set of Linux capabilities, its processes live in a separate PID namespace, and
the kernel namespace and device access are restricted. A privileged container
removes most of those restrictions. It gets the full set of capabilities the
host kernel allows, it can mount filesystems, and it can access `/dev` devices
directly.

Operators use `--privileged` for containers that need to manage other
containers, run kernel modules, or perform system-level diagnostics. The flag
is a last resort when fine-grained capability tuning is too complex.

## What cgroups are

A **control group** (cgroup) is a kernel mechanism for grouping processes so
the kernel can apply resource limits and accounting to them. Each cgroup
hierarchy has a set of controllers: `memory`, `cpu`, `devices`, and others.
The kernel maintains these hierarchies as a pseudo-filesystem mounted under
`/sys/fs/cgroup`.

## The release_agent hook

Each cgroup hierarchy has a `release_agent` file. When the last process in a
cgroup exits, the kernel runs the program named in that file. The purpose is
cleanup: notify an external daemon that a cgroup was emptied so it can release
accounting resources.

The critical property is **context**: the kernel runs release_agent as root,
in the host's PID namespace and filesystem namespace, not the container's.
Inside a privileged container you can mount a cgroup filesystem and write an
arbitrary path to `release_agent`. When you trigger a cgroup deletion, the
kernel runs your script on the host.

## The notify_on_release flag

By default, the kernel does not fire release_agent when a cgroup empties. You
enable it per-cgroup by writing `1` to `notify_on_release`. Create a child
cgroup, enable the flag, put a process into it, let that process exit, and
the hook fires.

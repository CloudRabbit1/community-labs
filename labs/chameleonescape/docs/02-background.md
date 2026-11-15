# Background: Linux Capabilities and PID Namespaces

## Linux Capabilities

Traditional Unix permissions are binary: a process either runs as root (all
privileges) or not (restricted). Linux capabilities split root's privileges into
about 40 distinct units. `CAP_SYS_PTRACE` is one: it lets a process call
`ptrace()` on other processes, bypassing the normal restriction that only a parent
process can trace its own children.

Performance monitors need this to sample CPU counters, attach to arbitrary
processes, and read their call stacks. Granting just `CAP_SYS_PTRACE` looks
reasonable. It is safer than `--privileged`, which grants every capability
at once.

## PID Namespaces

By default, a Docker container gets its own PID namespace. Processes inside the
container cannot see host processes; `ps` shows only the container's own tree.

When a container is started with `--pid=host`, it shares the host PID namespace.
Processes inside can see and address every process on the host. This is sometimes
used for monitoring tools that need to report on host-level process activity.

## The Combination

`CAP_SYS_PTRACE` + shared PID namespace = the container can call `ptrace()` on
any host process by its host PID. `ptrace(PTRACE_PEEKDATA, pid, addr, ...)` reads
4 or 8 bytes of a target process's memory. The same reads are available via the
`/proc/<pid>/mem` pseudo-file: open it, seek to the address, read.

The container is a chameleon: it presents as a harmless monitoring service but
can read and write host process memory.

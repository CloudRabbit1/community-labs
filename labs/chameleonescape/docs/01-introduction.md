# ChameleonEscape: Container Escape via CAP_SYS_PTRACE

## What This Lab Is About

Linux capabilities let you grant a container a narrow slice of root privileges
without running it fully privileged. `CAP_SYS_PTRACE` is one of them. It is
used by profiling tools like `strace`, `gdb`, and performance monitors to attach
to running processes and inspect their state.

The problem: when a container shares the host PID namespace and has `SYS_PTRACE`,
it can attach to host processes, including PID 1, and read their memory via
`/proc/<pid>/mem`. The container looks contained. It is not.

This lab presents a container running a "process debugger" API. The API exposes
the container's capabilities and lets you read process memory. Your job is to
enumerate those capabilities, identify the host process you can target, and
read the flag out of host PID 1's memory.

## Lab Setup

```bash
docker compose up --build
```

The service starts on `http://localhost:8080`.

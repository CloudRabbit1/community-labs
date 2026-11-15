# Finding the Bug

## Step 1: Read the Capabilities

The service exposes its own capability set:

```bash
curl http://localhost:8080/api/caps
```

Output:
```json
{
  "CapEff": "0000000000400000",
  "decoded": ["CAP_SYS_PTRACE"],
  "note": "Container was launched with SYS_PTRACE; intended for perf monitoring"
}
```

`0x400000` in the effective capability bitmask is bit 19, which is `CAP_SYS_PTRACE`.
The container has exactly one elevated capability. That is enough.

## Step 2: List Visible Processes

```bash
curl http://localhost:8080/api/processes
```

Output:
```json
{
  "processes": [
    {"pid": 1,    "name": "systemd",    "user": "root", "host": true},
    {"pid": 7,    "name": "sshd",       "user": "root", "host": true},
    {"pid": 843,  "name": "dockerd",    "user": "root", "host": true},
    {"pid": 2047, "name": "python3",    "user": "app",  "host": false}
  ]
}
```

The container shares the host PID namespace. Host processes are visible and
addressable. PID 1 is the host init process. The most privileged and most
interesting target.

## Step 3: Read PID 1's Memory Map

```bash
curl http://localhost:8080/api/process/1/maps
```

Output:
```json
{"maps": [
  {"start": "0x55a000000000", "perms": "r-xp", "label": "[systemd .text]"},
  ...
  {"start": "0x7f4000500000", "perms": "r--p", "label": "[mmap anon]"},
  ...
]}
```

The anonymous mmap segment (`[mmap anon]`) is where the flag is stored. Its
starting address is the read target.

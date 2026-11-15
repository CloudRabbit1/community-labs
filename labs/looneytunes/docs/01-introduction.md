# CVE-2023-4911: Looney Tunables

## What This Lab Is About

The name "Looney Tunables" comes from the vulnerable mechanism: `GLIBC_TUNABLES`, an
environment variable that lets users configure glibc's internal allocator behavior at
runtime. In glibc 2.34 through 2.38, the code that parses this variable copies its
value into a fixed-size heap buffer without checking how long the value is. Send a
value that is too long and the copy runs past the end of the buffer, corrupting heap
metadata. With the right payload, that corruption escalates an unprivileged local
process to root.

This was one of the most widely exploited Linux LPEs of 2023. The affected glibc
versions shipped in Fedora 37/38, Ubuntu 22.04, and Debian 12.

## Lab Setup

```bash
docker compose up --build
```

The lab runs on `http://localhost:8080` and simulates the vulnerable GLIBC_TUNABLES
parsing logic as an HTTP service.

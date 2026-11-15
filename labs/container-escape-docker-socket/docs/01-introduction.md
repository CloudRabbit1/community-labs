# Introduction

You have access to a monitoring service that fetches URLs on your behalf. The Docker daemon on the same host is not exposed externally, but it is reachable from inside the container at `127.0.0.1:2376`. Your goal is to read the flag from the host filesystem.

The monitoring service's `/fetch` endpoint makes HTTP requests without filtering the target URL. That is the SSRF. The Docker remote API has no authentication configured. That is the second mistake. Together, they let you create a privileged container, mount the host root filesystem into it, and run a command that reads the flag.

## What you will do

Use `/fetch` to reach the Docker daemon, create a privileged container with `/` bind-mounted to `/host-root`, create an exec that runs `cat /host-root/flag.txt`, start the exec, and collect the output.

## Lab setup

```bash
docker compose up --build -d
python3 exploit/exploit.py http://localhost:8080
docker compose down
```

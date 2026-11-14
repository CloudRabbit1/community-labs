# ChameleonEscape: Container Escape via CAP_SYS_PTRACE

A container running with `CAP_SYS_PTRACE` looks harmless from the outside. The
capability is commonly granted for performance monitoring and debugging tools.
But with `SYS_PTRACE` and access to the host PID namespace, any process inside
the container can attach to any process on the host, including PID 1, and
read or write its memory directly via `/proc/<pid>/mem`.

No kernel exploit required. Just a misconfigured container.

## Quick Start

```bash
docker compose up --build
```

The vulnerable service starts on `http://localhost:8080`.

## Run the Exploit

```bash
python3 exploit/exploit.py http://localhost:8080
```

## Get This Lab

**Clone the whole repo:**
```bash
git clone https://github.com/CloudRabbit1/community-labs.git
cd community-labs/chameleonescape
```

**Clone this lab only (sparse checkout):**
```bash
git clone --filter=blob:none --sparse https://github.com/CloudRabbit1/community-labs.git
cd community-labs
git sparse-checkout set labs/chameleonescape
cd chameleonescape
```

**Download a single file:**
```bash
curl -O https://raw.githubusercontent.com/CloudRabbit1/community-labs/master/chameleonescape/exploit/exploit.py
```

## Learn More

Read the docs in order:

1. [Introduction](./docs/01-introduction.md)
2. [Background](./docs/02-background.md)
3. [Finding the Bug](./docs/03-finding-the-bug.md)
4. [Exploitation](./docs/04-exploitation.md)
5. [Defense](./docs/05-defense.md)

The [walkthrough](./solutions/walkthrough.md) has the full solution.

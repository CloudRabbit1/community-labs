# CVE-2023-4911: Looney Tunables (glibc GLIBC_TUNABLES Heap Overflow)

The glibc dynamic loader parses the `GLIBC_TUNABLES` environment variable at
process startup. In glibc 2.34 through 2.38, the parsing routine copies the
variable's value into a fixed 256-byte heap buffer without bounds checking.
A value starting with `glibc.malloc.mxfast=` and longer than 256 bytes overflows
the buffer, corrupting adjacent heap metadata and enabling privilege escalation
to root on any system running the vulnerable glibc.

Disclosed by Qualys, October 2023. CVSS 7.8. Affects Fedora 37/38, Ubuntu 22.04,
Debian 12, and any distribution shipping glibc 2.34 to 2.38.

## Quick Start

```bash
docker compose up --build
```

The simulation starts on `http://localhost:8080`.

## Run the Exploit

```bash
python3 exploit/exploit.py http://localhost:8080
```

## Get This Lab

**Clone the whole repo:**
```bash
git clone https://github.com/CloudRabbit1/community-labs.git
cd community-labs/looneytunes
```

**Clone this lab only (sparse checkout):**
```bash
git clone --filter=blob:none --sparse https://github.com/CloudRabbit1/community-labs.git
cd community-labs
git sparse-checkout set labs/looneytunes
cd looneytunes
```

**Download a single file:**
```bash
curl -O https://raw.githubusercontent.com/CloudRabbit1/community-labs/master/looneytunes/exploit/exploit.py
```

## Learn More

Read the docs in order:

1. [Introduction](./docs/01-introduction.md)
2. [Background](./docs/02-background.md)
3. [Finding the Bug](./docs/03-finding-the-bug.md)
4. [Exploitation](./docs/04-exploitation.md)
5. [Defense](./docs/05-defense.md)

The [walkthrough](./solutions/walkthrough.md) has the full solution.

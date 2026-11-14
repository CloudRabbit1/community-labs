# Defense

## Never Pass User Input to a Shell

The root fix is to avoid `shell=True` entirely. Use `subprocess.run` with a list of arguments:

```python
# Vulnerable
import subprocess, os
os.system(f"ping -c 3 {host}")                          # shell=True implicit

# Safe
subprocess.run(["ping", "-c", "3", host], check=True)  # no shell, no injection
```

When the command is a list, the OS executes `ping` directly with `host` as a literal argument. The shell never sees the input, so metacharacters have no effect.

## Allowlist Validation

If you must pass input near a shell, validate it against a strict allowlist first:

```python
import re
if not re.fullmatch(r'[a-zA-Z0-9.\-]{1,253}', host):
    return error("Invalid hostname")
```

This rejects any input containing `;`, `|`, `&`, spaces, or other shell metacharacters. Use this as a defense-in-depth layer, not as the primary control.

## Principle of Least Privilege

The web server process should not have permission to read sensitive files or spawn shells. Run the application as a non-root user with minimal filesystem access. If the server cannot read `/etc/passwd` or write to `/tmp`, injection is significantly harder to exploit even when it exists.

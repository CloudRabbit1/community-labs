# Defense

## The Correct Fix

Resolve the full path and check it starts with the expected base directory:

```python
import os

BASE = "/app/pages"

def safe_open(user_input: str):
    full = os.path.realpath(os.path.join(BASE, user_input))
    if not full.startswith(BASE + os.sep):
        raise PermissionError(f"Access denied: {user_input}")
    return open(full)
```

`os.path.realpath` resolves all `..` sequences and symlinks before the check, so there is no bypass path.

## Additional Controls

Use an allowlist. If only `about.txt` and `contact.txt` are valid pages, reject everything else:

```python
ALLOWED = {"about.txt", "contact.txt"}
if page not in ALLOWED:
    raise PermissionError
```

Do not combine both approaches if the allowlist is exhaustive. One check is easier to reason about than two.

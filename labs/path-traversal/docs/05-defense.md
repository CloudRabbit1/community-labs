# Defense

## Canonicalize Before Comparing

Resolve the full canonical path and reject anything that falls outside the document root:

```python
import os

DOC_ROOT = os.path.realpath("/app/docs")

def safe_read(name):
    target = os.path.realpath(os.path.join(DOC_ROOT, name))
    if not target.startswith(DOC_ROOT + os.sep):
        return None, "access denied"
    try:
        return open(target).read(), None
    except FileNotFoundError:
        return None, "not found"
```

`os.path.realpath` resolves every `..`, symlink, and encoded segment before the check. A traversal attempt resolves to a path outside `DOC_ROOT` and is blocked before the file is opened.

## Allowlist the Filename

If you serve a fixed set of files, reject any name that is not in the list:

```python
ALLOWED = {"readme.txt", "policy.txt", "report.txt"}

def safe_read(name):
    if name not in ALLOWED:
        return None, "not allowed"
    return open(os.path.join(DOC_ROOT, name)).read(), None
```

An allowlist eliminates traversal entirely because arbitrary paths are never formed.

## Avoid Serving the Filesystem Directly

The root fix is to avoid mapping user input to filesystem paths at all. Serve files from a database or a fixed URL-to-path table where user input selects a key, not a path:

```python
FILES = {
    "readme":  "/app/docs/readme.txt",
    "policy":  "/app/docs/policy.txt",
    "report":  "/app/docs/report.txt",
}

def safe_read(key):
    path = FILES.get(key)
    if not path:
        return None, "not found"
    return open(path).read(), None
```

User input touches only the dictionary key, never the filesystem path.

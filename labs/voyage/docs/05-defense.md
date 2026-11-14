# Defense

## Fix LFI: use an allowlist for file names

Never pass user input directly to a file read. Use an explicit allowlist:

```python
ALLOWED_FILES = {'about.txt', 'readme.txt', 'help.txt'}

def view_file():
    filename = request.args.get('file', '')
    if filename not in ALLOWED_FILES:
        return 'Not found', 404
    path = os.path.join('/var/www/public', filename)
    return open(path).read()
```

If you must use dynamic paths, resolve the path and verify it stays inside the intended directory:

```python
base = os.path.realpath('/var/www/public')
target = os.path.realpath(os.path.join(base, filename))
if not target.startswith(base + os.sep):
    return 'Forbidden', 403
```

## Fix credential exposure: never store secrets in app-readable files

Move credentials to environment variables. Configuration files should contain only non-secret settings. Use a secrets manager (Vault, AWS Secrets Manager, environment injection) for passwords.

If a configuration file must exist, set filesystem permissions so the web process cannot read it, and use a separate privileged process to supply credentials at startup.

## Fix command injection: avoid shell commands with user input

The safest fix is to not shell out for a ping at all. Use a library that constructs the network packet directly. If you must call a system command:

```python
import subprocess, re

# Validate: only hostname characters allowed
if not re.match(r'^[a-zA-Z0-9.\-]+$', host):
    return 'Invalid host', 400

result = subprocess.run(['ping', '-c', '1', host],
                        capture_output=True, text=True, timeout=5)
```

Passing arguments as a list (not `shell=True`) with no f-string interpolation eliminates injection.

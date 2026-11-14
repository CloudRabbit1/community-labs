# Background

## Local File Inclusion

LFI happens when an application uses user-supplied input to construct a file path and reads that file, without restricting what paths are allowed. An attacker can supply path traversal sequences (`../`) to escape the intended directory and read files anywhere the web process can access.

A typical vulnerable pattern:

```python
filename = request.args.get('file')
return open(filename).read()
```

A safe pattern uses an allowlist:

```python
allowed = {'about.txt', 'readme.txt'}
filename = request.args.get('file')
if filename not in allowed:
    return 'Not found', 404
return open(os.path.join('/safe/dir', filename)).read()
```

## Credentials in configuration files

Applications commonly store database passwords, API keys, and admin credentials in configuration files. When LFI is present, any file the web process can read becomes a target. Configuration files at predictable paths like `../config.ini`, `../../app/settings.py`, or `../../etc/passwd` are common first targets.

## OS command injection

Command injection occurs when user input is embedded in a shell command without sanitization. For a ping utility:

```python
# Vulnerable
os.system(f'ping -c1 {host}')

# Attacker input
host = "localhost; cat /etc/shadow"
# Runs: ping -c1 localhost; cat /etc/shadow
```

The fix is to avoid shell=True and pass arguments as a list, or to validate that input contains only allowed characters (hostname characters: letters, digits, dots, hyphens).

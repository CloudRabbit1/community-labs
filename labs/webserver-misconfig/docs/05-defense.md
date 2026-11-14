# Defense

## Fix 1: disable directory listing globally

Apply `Options -Indexes` at the server level so every directory inherits it by default:

```apache
<Directory "/var/www/html">
    Options -Indexes
</Directory>
```

Do not rely on per-subdirectory directives to disable listing. A new directory added by a deployment script or a developer will inherit whatever the parent allows. Set the secure default at the root and require an explicit opt-in for directories that genuinely need browsing.

## Fix 2: keep backup files outside the web root

The underlying problem is not the directory listing — it is that a configuration backup with credentials exists inside the web root at all. Place backups in a directory the web server cannot serve:

```
/var/backups/app/        OK — not under /var/www/html
/home/deploy/backups/    OK — not under /var/www/html
/var/www/html/backup/    WRONG — directly reachable by HTTP
```

If a backup must be created programmatically from the application, write it to a path that Apache has no `DocumentRoot` or `Alias` mapping to.

## Fix 3: never pass user input to shell commands

The root cause of the CGI injection is constructing a shell command by concatenating user input. The correct approach is to avoid shell invocation entirely. Run the command directly using the language's exec API, which passes arguments as a list rather than a string interpreted by a shell:

```python
import subprocess, shlex

host = params.get('host', ['127.0.0.1'])[0]
result = subprocess.run(
    ['ping', '-c', '1', '-W', '1', host],
    capture_output=True, text=True, timeout=5
)
```

No shell is involved. The argument list is passed directly to `execve`. A semicolon in `host` is passed as a literal argument to ping, which rejects it as an invalid hostname. No second command runs.

If a shell must be used, validate the input strictly before interpolating it. For a hostname or IP address, accept only characters in `[a-zA-Z0-9.\-]`:

```python
import re
if not re.fullmatch(r'[a-zA-Z0-9.\-]{1,253}', host):
    sys.exit(1)
```

Reject anything that does not match. Do not attempt to strip or escape shell metacharacters — the allowlist approach is safer and simpler.

## Fix 4: run CGI with minimal permissions

The CGI process ran as `www-data`, which had read access to `/var/www/secret/flag2.txt`. If the diagnostic script has no need to read files outside `/var/www/html`, restrict what `www-data` can access using filesystem permissions. Place files that only the application backend should read under a separate owner and group, not readable by the web server user.

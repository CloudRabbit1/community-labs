# Defense

## Fix 1: remove default credentials and credential hints

Never ship a default password in production. Never leave credential hints in HTML comments, JavaScript, or any client-visible content. During development, use a `.env` file or environment variables for credentials and ensure those files are not committed to version control or included in Docker images.

For this application, generate a random password at container start:

```bash
ADMIN_PASS="$(openssl rand -hex 16)"
```

And pass it as an environment variable to the application.

## Fix 2: never pass user input to shell commands

The root cause is `shell=True` with string concatenation. Remove both:

```python
# WRONG
result = subprocess.run(f"ping -c 1 -W 1 {host}", shell=True, ...)

# CORRECT
result = subprocess.run(["ping", "-c", "1", "-W", "1", host], ...)
```

Passing a list to `subprocess.run` without `shell=True` bypasses the shell entirely. The host value is passed as a literal argument to ping. A semicolon in host is treated as a literal character ping does not understand, not as a command separator.

## Fix 3: validate the host value before using it

Even without shell injection, accepting arbitrary hosts can allow SSRF to internal services. Validate that the host matches a hostname or IP address pattern before passing it to ping:

```python
import re
if not re.fullmatch(r'[a-zA-Z0-9.\-]{1,253}', host):
    return error("invalid host")
```

This blocks `127.0.0.1;id`, `localhost;cat /flag1.txt`, and similar payloads. It also blocks `http://...` style values that might target an SSRF path.

## Fix 4: restrict what the monitoring service can access

The injected curl command reached `127.0.0.1:9090` because the application process had network access to all localhost ports. Use network namespace isolation or firewall rules to restrict which internal services a web application can reach, following the principle of least privilege.

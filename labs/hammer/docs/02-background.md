# Background

## Rate Limiting and Client-Supplied Headers

A rate limiter counts requests from each caller and rejects callers that exceed the limit. The question is: what identifies a caller?

IP address is the most common answer. But in real deployments, apps sit behind load balancers or proxies that forward requests on behalf of clients. The original IP address is passed in a header like `X-Forwarded-For`. The app reads this header to get the real client IP.

The flaw: `X-Forwarded-For` is set by the client, not by the proxy. Any HTTP client can set it to any value. If the rate limiter trusts this header, an attacker rotates the value and gets unlimited attempts.

## Prefix-Based Command Allowlists

A naive allowlist check:

```python
ALLOWED = ["id", "whoami", "ls"]
if any(cmd.startswith(a) for a in ALLOWED):
    run(cmd)
```

This checks whether the command string starts with an allowed word. It does not check that the command is only that word. Shell metacharacters like `;`, `|`, and `&&` let an attacker append a second command. `id; cat /flag.txt` starts with `id`, passes the check, and then the shell runs both commands.

The correct check is `cmd in ALLOWED` (exact match) or parse and validate the command before passing it to a shell, or avoid the shell entirely.

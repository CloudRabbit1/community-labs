# Defense

## Fix the Rate Limiter: Do Not Trust Client Headers

Never use `X-Forwarded-For` as the rate-limit key unless you control every proxy in the chain and strip the header at the edge. For a direct connection:

```python
ip = self.client_address[0]
```

For apps behind a trusted reverse proxy, extract the real IP from the rightmost entry added by the proxy, not the leftmost entry the client set:

```python
# nginx sets X-Real-IP from the actual socket address
ip = self.headers.get("X-Real-IP") or self.client_address[0]
```

If you must use `X-Forwarded-For`, use the rightmost IP (the last proxy in the chain, which you control) rather than the leftmost (which the client controls).

## Fix the Allowlist: Exact Match or No Shell

Replace prefix matching with exact matching:

```python
if cmd not in ALLOWED_CMDS:
    return 403

# Better: avoid the shell entirely
if cmd == "id":
    output = subprocess.run(["id"], capture_output=True, text=True).stdout
```

Passing a list to `subprocess.run` instead of a string with `shell=True` prevents shell metacharacter interpretation entirely. There is no way to inject a second command when the shell is not involved.

## Longer OTPs

A 4-digit OTP has 10,000 values. Even at one attempt per second, that is under three hours. Use at minimum a 6-digit OTP (1,000,000 values), expire it after 5 minutes, and enforce the rate limit on the server side, not on a client-supplied header.

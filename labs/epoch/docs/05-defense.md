# Defense

## Never use shell=True with user input

The root cause is `shell=True` combined with unsanitized user input. The fix is to pass arguments as a list, which bypasses the shell entirely:

```python
# Vulnerable
subprocess.run(f"date -d @{ts}", shell=True)

# Safe
subprocess.run(["date", "-d", f"@{ts}"])
```

When arguments are passed as a list, the OS invokes the binary directly. There is no shell to interpret metacharacters. The semicolon is passed as a literal argument to `date`, which rejects it as invalid.

## Validate and constrain input

If the input is supposed to be a timestamp, check that it is:

```python
def parse_ts(ts: str) -> int:
    try:
        return int(ts)
    except ValueError:
        raise ValueError("timestamp must be an integer")
```

An integer cannot contain shell metacharacters. Validate first, then use.

## Avoid shell commands for simple operations

For timestamp conversion, there is no reason to call `date` at all. Python's standard library handles it:

```python
import datetime
dt = datetime.datetime.utcfromtimestamp(int(ts))
result = dt.strftime("%a %b %d %H:%M:%S UTC %Y")
```

If the operation can be done in the application language, do it there. External processes introduce attack surface that does not need to exist.

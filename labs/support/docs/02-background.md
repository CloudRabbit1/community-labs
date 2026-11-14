# Background

## Python pickle serialization

Python's `pickle` module converts objects to a stream of bytes and reconstructs them later. It is used to store session data, cache computed results, or pass objects between processes.

The deserialization protocol is powerful by design: when you unpickle an object, Python can call arbitrary functions to reconstruct it. This power is the problem. A crafted pickle payload can instruct Python to call any callable with any arguments, including functions that run shell commands.

## The `__reduce__` protocol

When a class defines `__reduce__`, pickle calls it during pickling and uses its return value as a recipe for reconstruction. The return value is a tuple: `(callable, args)`. When the bytes are unpickled, Python calls `callable(*args)`.

An attacker can define a class whose `__reduce__` returns a dangerous callable:

```python
import pickle, subprocess, base64

class RCE:
    def __reduce__(self):
        return (subprocess.check_output, (['cat', '/etc/passwd'],))

payload = base64.b64encode(pickle.dumps(RCE())).decode()
```

Sending this as a session cookie causes the server to call `subprocess.check_output(['cat', '/etc/passwd'])` during deserialization. The return value is bytes containing the file contents.

## Unsigned session cookies

TicketDesk stores session data in a cookie as `base64(pickle.dumps(data))`. There is no HMAC and no signature. The server cannot tell whether the cookie was issued by itself or crafted by the client.

This means two attacks are possible:

1. **Code execution**: replace the cookie with a malicious pickle that calls a system function.
2. **Privilege escalation**: replace the cookie with a pickle that returns `{"username": "...", "role": "admin"}`. No code execution needed. The server unpickles it and treats it as a legitimate session.

Flask's built-in session mechanism uses HMAC-SHA256 to prevent this. TicketDesk implements its own session handling without that protection.

## Why pickle is not safe for untrusted data

The Python documentation warns explicitly: "The pickle module is not secure. Only unpickle data you trust." Any application that unpickles data from a client, a database that the client wrote to, or any untrusted network source is vulnerable.

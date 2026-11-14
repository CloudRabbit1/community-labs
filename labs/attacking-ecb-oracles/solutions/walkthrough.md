# Walkthrough: ECB Oracle

## Setup

```bash
docker compose up --build -d
```

Confirm the oracle is up:

```bash
curl -s "http://localhost:5000/encrypt?input=AAAA"
```

```json
{"ciphertext":"cNtcVTvZZOHNEEFPsKw7Pw=="}
```

## Step 1: Confirm ECB mode

Send 48 identical bytes. In ECB, three identical 16-byte input blocks produce three identical output blocks.

```bash
python3 -c "
import base64, json, urllib.request
r = urllib.request.urlopen('http://localhost:5000/encrypt?input=' + 'A'*48)
ct = base64.b64decode(json.loads(r.read())['ciphertext'])
blocks = [ct[i:i+16].hex() for i in range(0, len(ct), 16)]
print('First 3 blocks identical:', blocks[0] == blocks[1] == blocks[2])
"
```

```
First 3 blocks identical: True
```

## Step 2: Measure the secret length

```bash
python3 -c "
import base64, json, urllib.request
def enc(s):
    r = urllib.request.urlopen(f'http://localhost:5000/encrypt?input={s}')
    return len(base64.b64decode(json.loads(r.read())['ciphertext']))
base = enc('')
for i in range(1, 17):
    if enc('A'*i) > base:
        print(f'Secret length: {base - i}')
        break
"
```

```
Secret length: 37
```

## Step 3: Run the exploit

```bash
python3 exploit/exploit.py http://localhost:5000
```

```
[*] Target: http://localhost:5000
[*] Secret length: 37 bytes
[*] Recovered 37/37: POC{a3f8c2d19b4e7f60abc123def456789a}
[+] Secret: POC{a3f8c2d19b4e7f60abc123def456789a}
```

The flag value changes on every container start.

## Teardown

```bash
docker compose down
```

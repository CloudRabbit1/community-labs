# Finding the Bug

## Confirm the oracle accepts input

Call the encrypt endpoint with a short test string:

```bash
curl -s "http://localhost:5000/encrypt?input=AAAA"
```

```json
{"ciphertext": "cNtcVTvZZOHNEEFPsKw7Pw=="}
```

The response is 16 bytes (base64-decoded), which is one AES block. The input was 4 bytes; the secret fills the rest of the block plus the padding.

## Confirm ECB mode by detecting duplicate blocks

Send 48 bytes of the same value. In ECB mode, identical plaintext blocks produce identical ciphertext blocks.

```bash
python3 -c "
import base64, json, urllib.request
r = urllib.request.urlopen('http://localhost:5000/encrypt?input=' + 'A'*48)
ct = base64.b64decode(json.loads(r.read())['ciphertext'])
blocks = [ct[i:i+16].hex() for i in range(0, len(ct), 16)]
print('blocks:', blocks)
print('duplicates:', len(blocks) != len(set(blocks)))
"
```

```
blocks: ['d6d6d6...', 'd6d6d6...', 'd6d6d6...', ...]
duplicates: True
```

The first three blocks are identical because you sent three identical 16-byte blocks of `A`. ECB encrypted them identically. CBC mode would have produced three different ciphertext blocks.

## Measure the secret length

Send 1, 2, 3... bytes until the ciphertext grows by 16 bytes. That growth means your filler just pushed the padding across a block boundary.

```bash
python3 -c "
import base64, json, urllib.request
def enc(s): 
    r = urllib.request.urlopen(f'http://localhost:5000/encrypt?input={s}')
    return len(base64.b64decode(json.loads(r.read())['ciphertext']))
base = enc('')
for i in range(1, 17):
    if enc('A'*i) > base:
        print(f'Secret length: {base - i} bytes (ciphertext grew at i={i})')
        break
"
```

```
Secret length: 37 bytes (ciphertext grew at i=11)
```

Your flag is 37 bytes. You will make 37 × 256 = at most 9,472 requests to recover it.

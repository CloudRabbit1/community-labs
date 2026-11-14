# Finding the Bug

## The Vulnerable Code in lab/app.py

The `/sso/acs` route calls two functions:

```python
# Step 1: verify signature (finds the signed assertion by Signature element)
if not verify_assertion(xml_str, IDP_SECRET):
    return jsonify({'error': 'Signature verification failed'}), 403

# Step 2: read attributes (reads the FIRST assertion -- XSW attack here)
attrs = read_attributes(xml_str)
```

## verify_assertion

```python
for m in re.finditer(r'(<saml:Assertion\b[^>]*>.*?</saml:Assertion>)', xml_str, re.DOTALL):
    block = m.group(1)
    if '<ds:SignatureValue>' not in block:
        continue   # skip assertions without a signature
    # ... verify HMAC on this block
```

This function iterates over all assertions and stops at the first one that contains a `<ds:SignatureValue>` element. It verifies the HMAC on that node.

## read_attributes

```python
root = ET.fromstring(xml_str)
# Read the first assertion (vulnerable: should read the verified one)
assertion = root.find('.//saml:Assertion', NS)
```

This function uses ElementTree's `.find()` to get the first assertion in document order. It does not care whether the assertion was signed.

## The Gap

An attacker can put an unsigned admin assertion before the signed user assertion:

- `verify_assertion` skips the unsigned admin assertion (no Signature) and validates the signed user assertion.
- `read_attributes` finds the unsigned admin assertion (first in document order) and returns `role=admin`.

Both functions succeed, but they operated on different nodes.

## Confirming with the Debug Endpoint

```bash
curl -s http://127.0.0.1:8093/debug/idp
```

The response shows the signed XML for alice. Decode and inspect it to understand the structure before constructing the XSW payload.

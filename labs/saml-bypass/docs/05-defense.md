# Defense

## The Root Cause

The application verifies the signature on one node and reads attributes from a different node. The fix is to perform both operations on the same verified node.

## Fix: Use the Verified Node for Attribute Reading

```python
def acs_fixed(xml_str, secret):
    # Step 1: find the signed assertion (the one with a SignatureValue)
    signed_block = None
    for m in re.finditer(r'(<saml:Assertion\b[^>]*>.*?</saml:Assertion>)', xml_str, re.DOTALL):
        block = m.group(1)
        if '<ds:SignatureValue>' in block:
            signed_block = block
            break
    if not signed_block:
        raise ValueError('No signed assertion found')

    # Step 2: verify the signature on that specific block
    if not verify_hmac(signed_block, secret):
        raise ValueError('Signature verification failed')

    # Step 3: read attributes from THE SAME block, not from the document root
    return read_attributes_from_block(signed_block)
```

By reading attributes from `signed_block` (the verified node) rather than from the document root, the unsigned injected assertion is never consulted.

## Fix: Reject Documents with More Than One Assertion

If the application only expects one assertion per response, reject any document that contains multiple:

```python
assertions = re.findall(r'<saml:Assertion\b', xml_str)
if len(assertions) != 1:
    raise ValueError(f'Expected 1 assertion, found {len(assertions)}')
```

This is a simple, cheap defense that eliminates most XSW variants.

## Fix: Use a Battle-Tested SAML Library

Do not implement XML-DSig verification or SAML parsing by hand. Use a library that is specifically designed to resist XSW:

- Python: `python3-saml` (wraps libxml2 with XSW protections enabled by default)
- Java: `OpenSAML` with signature validation properly configured
- .NET: `ITfoxtec.Identity.Saml2`

Libraries that handle XSW correctly reject documents where the signed reference does not cover the assertion the application relies on.

## Checklist for Developers

- After verifying a signature, read attributes from the same node, not from the document.
- Reject SAML Responses that contain more than one assertion if you only expect one.
- Reject assertions with IDs that do not match the signature reference.
- Never implement XML-DSig or SAML parsing from scratch.
- Run `samlsploit` or similar tools against your ACS endpoint in security reviews.

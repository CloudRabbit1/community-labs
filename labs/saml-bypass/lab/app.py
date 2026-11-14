"""
SAML XML Signature Wrapping (XSW) lab.

The /sso/acs endpoint receives a base64-encoded SAML Response, verifies
the XML signature, then reads the NameID and attributes from the
document. The bug: verification is done on a node found by ID, but
attribute reading is done by XPath position -- not by the verified node.

An attacker can:
1. Keep the original signed assertion (with role=user) intact.
2. Add a second, unsigned assertion with role=admin BEFORE the signed one.
3. The verifier finds and validates the signed node (by ID reference).
4. The attribute reader grabs the first assertion in the document
   (the unsigned admin one).
"""
import base64
import hashlib
import hmac
import os
import re
import secrets
import xml.etree.ElementTree as ET
from flask import Flask, jsonify, request, session

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

FLAG1 = open('/flag1.txt').read().strip()
FLAG2 = open('/flag2.txt').read().strip()

# Shared secret used to sign assertions (in a real IdP this would be RSA;
# here we use HMAC-SHA256 keyed on a server secret to keep the lab simple)
IDP_SECRET = secrets.token_hex(32)


# ---------------------------------------------------------------------------
# Minimal SAML helpers
# ---------------------------------------------------------------------------

NS = {
    'saml': 'urn:oasis:names:tc:SAML:2.0:assertion',
    'samlp': 'urn:oasis:names:tc:SAML:2.0:protocol',
    'ds': 'http://www.w3.org/2000/09/xmldsig#',
}


def _canon(xml_str: str) -> bytes:
    """Very simple canonicalization: strip whitespace between tags."""
    return re.sub(rb'\s+', b' ', xml_str.encode()).strip()


def sign_assertion(xml_str: str, secret: str) -> str:
    """Add an HMAC-SHA256 signature element to the assertion."""
    sig = hmac.new(secret.encode(), _canon(xml_str), hashlib.sha256).hexdigest()
    return xml_str.replace(
        '</saml:Assertion>',
        f'<ds:Signature xmlns:ds="http://www.w3.org/2000/09/xmldsig#">'
        f'<ds:SignatureValue>{sig}</ds:SignatureValue>'
        f'</ds:Signature></saml:Assertion>'
    )


def verify_assertion(xml_str: str, secret: str) -> bool:
    """
    Verify the HMAC signature on the assertion that contains a Signature element.
    Uses string-based extraction to avoid namespace mangling by ET.tostring.

    The XSW vulnerability: this function finds the SIGNED assertion (by looking
    for one that contains <ds:SignatureValue>), but read_attributes reads the
    FIRST assertion in document order. An attacker inserts an unsigned admin
    assertion before the signed one, so verification passes on the signed node
    while the attribute reader returns the unsigned admin node.
    """
    # Find the assertion block that contains a signature using string search
    for m in re.finditer(r'(<saml:Assertion\b[^>]*>.*?</saml:Assertion>)', xml_str, re.DOTALL):
        block = m.group(1)
        if '<ds:SignatureValue>' not in block:
            continue
        # Extract the stored signature value
        sig_match = re.search(r'<ds:SignatureValue>([0-9a-f]+)</ds:SignatureValue>', block)
        if not sig_match:
            continue
        stored_sig = sig_match.group(1)
        # Reconstruct the pre-signature XML by removing the signature element
        assertion_no_sig = re.sub(
            r'<ds:Signature[^>]*>.*?</ds:Signature>', '', block, flags=re.DOTALL
        )
        expected = hmac.new(
            secret.encode(), _canon(assertion_no_sig), hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(expected, stored_sig)
    return False


def read_attributes(xml_str: str) -> dict:
    """
    Read NameID and attributes from the assertion.
    Bug: reads from the FIRST assertion in document order, not the signed one.
    An XSW attack puts an unsigned admin assertion first.
    """
    root = ET.fromstring(xml_str)
    # Read the first assertion (vulnerable: should read the verified one)
    assertion = root.find('.//saml:Assertion', NS)
    if assertion is None:
        return {}
    name_id_el = assertion.find('.//saml:NameID', NS)
    name_id = name_id_el.text if name_id_el is not None else 'unknown'
    attrs = {}
    for attr in assertion.findall('.//saml:Attribute', NS):
        name = attr.get('Name', '')
        values = [v.text for v in attr.findall('saml:AttributeValue', NS)]
        attrs[name] = values[0] if len(values) == 1 else values
    return {'name_id': name_id, 'attrs': attrs}


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route('/')
def index():
    return jsonify({
        'app': 'CorpSSO SAML SP',
        'endpoints': [
            'GET  /sso/request  -- get a SAML AuthnRequest to send to the IdP',
            'POST /sso/acs      -- consume a SAML Response from the IdP',
            'GET  /profile      -- view current session',
            'GET  /admin/secret -- admin-only flag',
            'GET  /debug/idp    -- get a signed SAML Response as alice (test IdP)',
        ],
    })


def _make_assertion(name_id: str, role: str, assertion_id: str) -> str:
    return (
        f'<saml:Assertion xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion" '
        f'ID="{assertion_id}">'
        f'<saml:NameID>{name_id}</saml:NameID>'
        f'<saml:AttributeStatement>'
        f'<saml:Attribute Name="role">'
        f'<saml:AttributeValue>{role}</saml:AttributeValue>'
        f'</saml:Attribute>'
        f'</saml:AttributeStatement>'
        f'</saml:Assertion>'
    )


@app.route('/debug/idp')
def debug_idp():
    """Return a valid signed SAML Response for alice (role=user) for testing."""
    assertion_id = 'a' + secrets.token_hex(8)
    assertion_xml = _make_assertion('alice', 'user', assertion_id)
    signed = sign_assertion(assertion_xml, IDP_SECRET)
    response_xml = (
        f'<samlp:Response xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol">'
        f'{signed}'
        f'</samlp:Response>'
    )
    blob = base64.b64encode(response_xml.encode()).decode()
    return jsonify({
        'saml_response': blob,
        'decoded': response_xml,
        'note': 'Valid signed SAML Response for alice. Modify to perform XSW.',
    })


@app.route('/sso/acs', methods=['POST'])
def acs():
    """SAML Assertion Consumer Service -- vulnerable to XSW."""
    data = request.get_json(force=True) or {}
    saml_b64 = data.get('SAMLResponse', '')
    if not saml_b64:
        return jsonify({'error': 'SAMLResponse required'}), 400
    try:
        xml_str = base64.b64decode(saml_b64).decode()
    except Exception:
        return jsonify({'error': 'Invalid base64'}), 400

    # Step 1: verify signature (finds the signed assertion by ID)
    if not verify_assertion(xml_str, IDP_SECRET):
        return jsonify({'error': 'Signature verification failed'}), 403

    # Step 2: read attributes (reads the FIRST assertion -- XSW attack here)
    attrs = read_attributes(xml_str)
    if not attrs:
        return jsonify({'error': 'No assertion found'}), 400

    session['user'] = attrs['name_id']
    session['role'] = attrs['attrs'].get('role', 'user')
    return jsonify({
        'message': f'SSO login as {session["user"]}',
        'role': session['role'],
    })


@app.route('/profile')
def profile():
    if 'user' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    hint = FLAG1 if session.get('role') == 'admin' else None
    return jsonify({'user': session['user'], 'role': session['role'], 'hint': hint})


@app.route('/admin/secret')
def admin_secret():
    if session.get('role') != 'admin':
        return jsonify({'error': 'Admin only'}), 403
    return jsonify({'secret': FLAG2})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)

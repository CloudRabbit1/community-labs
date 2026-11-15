"""
Open Redirect Chain lab.

Attack chain (CVE-2024-21501 class: OAuth redirect_uri prefix validation):

1. The OAuth server at /oauth/authorize validates redirect_uri using a
   prefix check only: the URI must start with 'http://127.0.0.1:8097/client'.
   This is weaker than exact-match validation.

2. The client app exposes an open redirect at /client/go?to=... with no
   sanitization of the destination URL. Because this endpoint lives on
   127.0.0.1:8097/client, it passes the prefix check.

3. An attacker combines these two flaws:
      redirect_uri = http://127.0.0.1:8097/client/go?to=http://ATTACKER
   The OAuth server accepts it (prefix matches).
   After authorization, the code is delivered to /client/go?to=http://ATTACKER
   which immediately redirects to http://ATTACKER with the code in the URL.

4. The attacker page at /attacker/land captures the code from the query
   string and exchanges it for an access token using /oauth/token.

Flags:
  FLAG1: returned from /api/profile when the access token belongs to alice.
  FLAG2: returned from /api/secret when the access token belongs to alice.
         Obtained by exchanging the STOLEN code (not the legitimate callback).
"""
import hashlib
import os
import secrets
import time
from flask import Flask, jsonify, redirect, request, session, url_for

app = Flask(__name__)
app.secret_key = os.urandom(32)

FLAG1 = open('/flag1.txt').read().strip()
FLAG2 = open('/flag2.txt').read().strip()

# Simulated user db
USERS = {'alice': 'hunter2', 'bob': 'password'}

# OAuth client registration (legitimate app)
# In a real deployment, redirect_uri would be exact-matched or use a strict allowlist.
# This server uses prefix matching -- the bug.
CLIENTS = {
    'trusted-app': {
        'secret': 'client-secret-xyz',
        'redirect_prefix': 'http://127.0.0.1:8097/client',
    }
}

# In-memory stores
auth_codes: dict = {}    # code -> {user, client_id, expires}
access_tokens: dict = {} # token -> {user, expires}


def _new_code(user: str, client_id: str) -> str:
    code = secrets.token_hex(16)
    auth_codes[code] = {'user': user, 'client_id': client_id, 'expires': time.time() + 120}
    return code


def _new_token(user: str) -> str:
    token = secrets.token_hex(32)
    access_tokens[token] = {'user': user, 'expires': time.time() + 3600}
    return token


def _token_user(token: str):
    entry = access_tokens.get(token)
    if not entry or entry['expires'] < time.time():
        return None
    return entry['user']


@app.get('/')
def index():
    return jsonify({
        'app': 'BankOAuth',
        'endpoints': [
            'GET /oauth/authorize?client_id=&redirect_uri=&state=&response_type=code',
            'POST /oauth/token  {code, client_id, client_secret}',
            'GET /client/callback?code=&state=  (legitimate callback)',
            'GET /client/go?to=...             (VULNERABLE open redirect)',
            'GET /api/profile                  (requires Bearer token)',
            'GET /api/secret                   (requires Bearer token, alice only)',
            'GET /attacker/land?code=          (simulates attacker capture page)',
        ],
    })


@app.get('/oauth/authorize')
def oauth_authorize():
    client_id = request.args.get('client_id', '')
    redirect_uri = request.args.get('redirect_uri', '')
    state = request.args.get('state', '')
    response_type = request.args.get('response_type', '')

    client = CLIENTS.get(client_id)
    if not client:
        return jsonify({'error': 'unknown_client'}), 400
    if response_type != 'code':
        return jsonify({'error': 'unsupported_response_type'}), 400

    # BUG: prefix check instead of exact match
    if not redirect_uri.startswith(client['redirect_prefix']):
        return jsonify({'error': 'invalid_redirect_uri',
                        'detail': f'must start with {client["redirect_prefix"]}'}), 400

    # Auto-authorize as alice (simulates user clicking "Allow")
    code = _new_code('alice', client_id)

    dest = f'{redirect_uri}?code={code}'
    if state:
        dest += f'&state={state}'
    return redirect(dest)


@app.post('/oauth/token')
def oauth_token():
    data = request.get_json(silent=True) or {}
    code = data.get('code', '')
    client_id = data.get('client_id', '')
    client_secret = data.get('client_secret', '')

    client = CLIENTS.get(client_id)
    if not client or client['secret'] != client_secret:
        return jsonify({'error': 'invalid_client'}), 401

    entry = auth_codes.pop(code, None)
    if not entry or entry['expires'] < time.time():
        return jsonify({'error': 'invalid_code'}), 400
    if entry['client_id'] != client_id:
        return jsonify({'error': 'code_client_mismatch'}), 400

    token = _new_token(entry['user'])
    return jsonify({'access_token': token, 'token_type': 'Bearer', 'user': entry['user']})


@app.get('/client/callback')
def client_callback():
    """Legitimate callback: would exchange code for token and log user in."""
    code = request.args.get('code', '')
    state = request.args.get('state', '')
    return jsonify({'message': 'Legitimate callback reached', 'code': code, 'state': state,
                    'hint': 'Exchange this code at /oauth/token to get an access token'})


@app.get('/client/go')
def client_go():
    """VULNERABLE: open redirect with no destination validation."""
    to = request.args.get('to', '/')
    # BUG: no validation of `to`; any URL is accepted
    return redirect(to)


@app.get('/api/profile')
def api_profile():
    token = request.headers.get('Authorization', '').removeprefix('Bearer ').strip()
    user = _token_user(token)
    if not user:
        return jsonify({'error': 'unauthorized'}), 401
    result = {'user': user}
    if user == 'alice':
        result['flag1'] = FLAG1
    return jsonify(result)


@app.get('/api/secret')
def api_secret():
    token = request.headers.get('Authorization', '').removeprefix('Bearer ').strip()
    user = _token_user(token)
    if not user:
        return jsonify({'error': 'unauthorized'}), 401
    if user != 'alice':
        return jsonify({'error': 'forbidden', 'detail': 'alice only'}), 403
    return jsonify({'secret': FLAG2})


@app.get('/attacker/land')
def attacker_land():
    """Simulates the attacker-controlled page that captures the OAuth code."""
    code = request.args.get('code', '')
    if not code:
        return jsonify({'message': 'No code received yet'}), 200
    return jsonify({
        'message': 'Attacker captured the authorization code!',
        'stolen_code': code,
        'next_step': 'POST /oauth/token with this code to get an access token',
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)

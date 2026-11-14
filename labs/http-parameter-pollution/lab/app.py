"""
HTTP Parameter Pollution lab.

This app simulates two vulnerabilities caused by duplicate HTTP parameters:

1. WAF bypass via parameter splitting.
   The WAF layer reads request.args.get('id') -- the FIRST value.
   The backend reads request.args.getlist('id')[-1] -- the LAST value.
   Send: ?id=1&id=1 OR 1=1--
   WAF sees '1' (safe). Backend sees '1 OR 1=1--' (injection).

2. Access control bypass via duplicate 'role' parameter.
   The middleware checks request.args.get('role') -- the FIRST value.
   The handler reads request.args.getlist('role')[-1] -- the LAST value.
   Send: ?role=user&role=admin
   Middleware sees 'user' (allowed). Handler sees 'admin' (flag2).

Flags:
  FLAG1: /api/search with SQLi-looking payload past the WAF via HPP
  FLAG2: /api/admin with role=admin past the access check via HPP
"""
import os
from flask import Flask, jsonify, request

app = Flask(__name__)

FLAG1 = open('/flag1.txt').read().strip()
FLAG2 = open('/flag2.txt').read().strip()

# Simulated user data (no real DB; flag1 appears when query triggers "admin" row)
USERS = [
    {'id': 1, 'name': 'alice', 'role': 'user'},
    {'id': 2, 'name': 'bob', 'role': 'user'},
    {'id': 999, 'name': 'admin', 'role': 'admin', 'secret': FLAG1},
]

SQLI_PATTERNS = ["'", '"', '--', 'or ', 'union', 'select', 'drop', 'insert']


def waf_check_id(value: str) -> bool:
    """Returns True (block) if any SQLi pattern found."""
    low = value.lower()
    return any(p in low for p in SQLI_PATTERNS)


@app.get('/')
def index():
    return jsonify({
        'app': 'CorpSearch',
        'endpoints': [
            'GET /api/search?id=<number>  -- search users by id (WAF protected)',
            'GET /api/admin?role=<value>  -- admin panel (role check protected)',
            'GET /api/status              -- health check',
        ],
    })


@app.get('/api/status')
def status():
    return jsonify({'status': 'ok'})


@app.get('/api/search')
def api_search():
    all_ids = request.args.getlist('id')
    if not all_ids:
        return jsonify({'error': 'id parameter required'}), 400

    # WAF reads the FIRST value
    waf_value = all_ids[0]
    if waf_check_id(waf_value):
        return jsonify({'error': 'WAF: blocked suspicious input', 'blocked_value': waf_value}), 403

    # Backend reads the LAST value (HPP vulnerability)
    backend_value = all_ids[-1]

    # Simulate query: if value triggers OR injection pattern, return all rows including admin
    is_injection = any(p in backend_value.lower() for p in ["' or", "or 1", "1=1", "' --", "-- "])
    if is_injection:
        # Injection "succeeds" -- returns all rows
        result = USERS
    else:
        try:
            uid = int(backend_value)
        except ValueError:
            return jsonify({'error': 'id must be an integer'}), 400
        result = [u for u in USERS if u['id'] == uid]

    return jsonify({'results': result, 'count': len(result)})


@app.get('/api/admin')
def api_admin():
    all_roles = request.args.getlist('role')
    if not all_roles:
        return jsonify({'error': 'role parameter required'}), 400

    # Access check reads the FIRST role value
    check_role = all_roles[0]
    if check_role != 'admin':
        # Middleware allows user/guest through without escalation check
        pass

    # Handler reads the LAST role value (HPP vulnerability)
    handler_role = all_roles[-1]
    if handler_role == 'admin':
        return jsonify({'flag2': FLAG2, 'panel': 'Admin panel accessed via HPP'})

    return jsonify({'message': f'Welcome {handler_role}. No admin access.'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)

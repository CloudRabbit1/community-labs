from flask import Flask, request, jsonify
import os

app = Flask(__name__)
FLAG1 = os.environ.get('FLAG1', 'POC{flag1_missing}')
FLAG2 = os.environ.get('FLAG2', 'POC{flag2_missing}')

_HOME = '''<!DOCTYPE html>
<html><head><title>DNS Tools</title></head><body>
<h1>DNS Subdomain Scanner</h1>
<p>Check CNAME records for dangling entries.</p>
<p>Endpoints: GET /dns/check?domain=... | POST /claim | GET /xss-test</p>
</body></html>'''


@app.get('/')
def index():
    return _HOME


@app.get('/dns/check')
def dns_check():
    domain = request.args.get('domain', '')
    if 'assets.example.com' in domain:
        return jsonify({
            'domain': 'assets.example.com',
            'cname': 'example-company.netlify.app',
            'status': 'DANGLING',
            'vulnerable': True,
            'flag1': FLAG1
        })
    return jsonify({'domain': domain, 'status': 'OK', 'vulnerable': False})


_claimed = False


@app.post('/claim')
def claim():
    global _claimed
    data = request.get_json() or {}
    site_name = data.get('site_name', '')
    if 'example-company.netlify.app' in site_name or site_name == 'example-company':
        _claimed = True
        return jsonify({'status': 'claimed', 'message': 'Site registered successfully', 'site': site_name})
    return jsonify({'error': 'Wrong site name'}), 400


@app.get('/xss-test')
def xss_test():
    if not _claimed:
        return jsonify({'error': 'Subdomain not yet claimed'}), 403
    victim_cookie = 'admin_session=abc123; admin_flag=' + FLAG2
    return jsonify({
        'executed': True,
        'stolen_cookie': victim_cookie,
        'flag2': FLAG2
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False, threaded=True)

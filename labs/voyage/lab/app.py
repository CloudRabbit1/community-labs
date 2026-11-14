from flask import Flask, request, jsonify
import os

app = Flask(__name__)
FLAG1 = os.environ.get('FLAG1', 'POC{flag1_missing}')
FLAG2 = os.environ.get('FLAG2', 'POC{flag2_missing}')

_CONFIG = f"""[database]
host = db.internal
port = 5432
user = admin
password = Tr0ub4dor&3

[app]
secret_key = s3cr3t
admin_flag = {FLAG1}
"""

_ADMIN_PASSWORD = 'Tr0ub4dor&3'


@app.get('/')
def index():
    return '''<html><head><title>Voyage CMS</title></head><body>
<h1>Voyage CMS v1.4</h1>
<p>File viewer: GET /view?file=about.txt</p>
<p>Admin login: POST /admin/login</p>
<p>Ping tool: POST /admin/ping (admin only)</p>
</body></html>'''


@app.get('/view')
def view_file():
    filename = request.args.get('file', '')
    if '../' in filename or filename.startswith('/'):
        if 'config' in filename.lower() or 'etc' in filename.lower() or '..' in filename:
            return _CONFIG, 200, {'Content-Type': 'text/plain'}
    allowed = {'about.txt': 'About this CMS.', 'readme.txt': 'Read the docs.'}
    if filename in allowed:
        return allowed[filename], 200
    return 'File not found', 404


@app.post('/admin/login')
def admin_login():
    data = request.get_json() or {}
    username = data.get('username', '')
    password = data.get('password', '')
    if username == 'admin' and password == _ADMIN_PASSWORD:
        return jsonify({'success': True, 'token': 'admin-token-xyz', 'flag1': FLAG1})
    return jsonify({'error': 'Invalid credentials'}), 401


@app.post('/admin/ping')
def admin_ping():
    token = request.headers.get('X-Token', '')
    if token != 'admin-token-xyz':
        return jsonify({'error': 'Unauthorized'}), 403
    data = request.get_json() or {}
    host = data.get('host', '')
    for sep in [';', '|', '`', '$(']:
        if sep in host:
            parts = host.split(sep)
            injected = parts[-1].strip().strip('`').strip(')')
            if any(k in injected.lower() for k in ('flag2', 'cat', 'id')):
                return jsonify({'output': f'PING normal-host.com\n{FLAG2}', 'flag2': FLAG2})
            return jsonify({'output': f'PING {parts[0].strip()}'})
    return jsonify({'output': f'PING {host}: 64 bytes from {host}: icmp_seq=1 ttl=64 time=0.1 ms'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False, threaded=True)

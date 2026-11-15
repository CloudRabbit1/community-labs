from flask import Flask, request, jsonify
import os, hashlib, secrets

app = Flask(__name__)
app.secret_key = 'static-secret-key-captcha'

FLAG1 = os.environ.get('FLAG1', 'POC{flag1_missing}')
FLAG2 = os.environ.get('FLAG2', 'POC{flag2_missing}')

CAPTCHA_SEED = 'captcha-seed-2024'
CAPTCHA_ANSWER = hashlib.md5(CAPTCHA_SEED.encode()).hexdigest()[:6]

_valid_tokens = set()


@app.get('/')
def index():
    return '''<html><head><title>Secure Login</title></head><body>
<h1>CaptchaApp v2.1</h1>
<p>Protected by CAPTCHA security.</p>
<p>Get CAPTCHA: <a href="/captcha">GET /captcha</a></p>
<p>Login: POST /login with username, password, captcha_token, captcha_answer</p>
</body></html>'''


@app.get('/captcha')
def get_captcha():
    token = secrets.token_hex(8)
    _valid_tokens.add(token)
    return jsonify({'token': token, 'challenge': 'Solve: MD5(captcha-seed-2024)[:6]', 'flag1': FLAG1})


@app.post('/login')
def login():
    data = request.get_json() or {}
    username = data.get('username', '')
    password = data.get('password', '')
    captcha_token = data.get('captcha_token', '')
    captcha_answer = data.get('captcha_answer', '')

    if captcha_answer != CAPTCHA_ANSWER:
        return jsonify({'error': 'Wrong CAPTCHA'}), 403

    if captcha_token not in _valid_tokens:
        return jsonify({'error': 'Invalid CAPTCHA token'}), 403

    if username == 'admin' and password == 'admin123':
        return jsonify({'success': True, 'message': 'Welcome, admin!', 'flag2': FLAG2})

    return jsonify({'error': 'Wrong credentials'}), 401


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False, threaded=True)

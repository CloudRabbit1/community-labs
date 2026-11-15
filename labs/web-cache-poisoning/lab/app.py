"""
Web Cache Poisoning lab.

The app caches responses by URL path only, ignoring the X-Forwarded-Host
header. That header is reflected into the response body (used to build
absolute URLs for scripts and links). An attacker who sends a request
with X-Forwarded-Host: attacker.com gets the poisoned response cached,
then all subsequent visitors to that URL receive a response pointing to
attacker.com -- classic web cache poisoning leading to XSS.

Flags:
  FLAG1: returned when the attacker successfully poisons the cache
         (the cache serves back the attacker's reflected header)
  FLAG2: returned from the /admin endpoint, only reachable by exploiting
         the cache-poisoned response (simulate script-include XSS)
"""
import secrets
import time
from flask import Flask, jsonify, request, session

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

FLAG1 = open('/flag1.txt').read().strip()
FLAG2 = open('/flag2.txt').read().strip()

# ---------------------------------------------------------------------------
# Toy in-process cache: keyed on (method, path) only -- ignores headers
# ---------------------------------------------------------------------------
_cache: dict[str, dict] = {}
CACHE_TTL = 60  # seconds


def cache_get(key: str):
    entry = _cache.get(key)
    if entry and (time.time() - entry['ts']) < CACHE_TTL:
        return entry['body'], entry['headers']
    return None, None


def cache_set(key: str, body: str, headers: dict):
    _cache[key] = {'body': body, 'headers': dict(headers), 'ts': time.time()}


def cache_clear():
    _cache.clear()


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route('/')
def index():
    return jsonify({
        'app': 'CorpPortal with Caching',
        'endpoints': [
            'GET /home    -- cached homepage (uses X-Forwarded-Host for URLs)',
            'GET /api/data -- cached API response',
            'GET /admin   -- admin endpoint (not cached)',
            'POST /cache/clear -- clear the cache (for testing)',
            'GET /cache/stats  -- see cache keys',
        ],
    })


@app.route('/home')
def home():
    cache_key = 'GET:/home'
    cached_body, cached_headers = cache_get(cache_key)
    if cached_body:
        # Return cached response (the headers are already baked in)
        from flask import Response
        return Response(cached_body, headers={'X-Cache': 'HIT', 'Content-Type': 'application/json'})

    # Build response using X-Forwarded-Host header (vulnerable)
    # In a real app this would be used for asset URLs, Open Graph tags, etc.
    forwarded_host = request.headers.get('X-Forwarded-Host', request.host)
    body = {
        'page': 'home',
        'script_src': f'http://{forwarded_host}/static/app.js',
        'canonical_url': f'http://{forwarded_host}/home',
        'content': 'Welcome to CorpPortal',
        'poisoned': forwarded_host != request.host,
    }
    import json
    body_str = json.dumps(body)

    # Cache the response (keyed on path only, not on X-Forwarded-Host)
    cache_set(cache_key, body_str, {})

    # Reveal flag1 if the response was poisoned
    if body['poisoned']:
        body['flag1'] = FLAG1
        body_str = json.dumps(body)

    from flask import Response
    return Response(body_str, headers={'X-Cache': 'MISS', 'Content-Type': 'application/json'})


@app.route('/api/data')
def api_data():
    cache_key = 'GET:/api/data'
    cached_body, _ = cache_get(cache_key)
    if cached_body:
        from flask import Response
        return Response(cached_body, headers={'X-Cache': 'HIT', 'Content-Type': 'application/json'})

    forwarded_host = request.headers.get('X-Forwarded-Host', request.host)
    import json
    body = {
        'data': [1, 2, 3],
        'source': f'http://{forwarded_host}/api',
        'poisoned': forwarded_host != request.host,
    }
    body_str = json.dumps(body)
    cache_set(cache_key, body_str, {})
    from flask import Response
    return Response(body_str, headers={'X-Cache': 'MISS', 'Content-Type': 'application/json'})


@app.route('/admin')
def admin():
    # Simulate a victim who was affected by the poisoned script include
    # In a real scenario the XSS from the poisoned page would steal a cookie
    # Here we simulate: if the cache for /home is poisoned, return flag2
    cached_body, _ = cache_get('GET:/home')
    if cached_body:
        import json
        try:
            cached = json.loads(cached_body)
            if cached.get('poisoned'):
                return jsonify({'secret': FLAG2, 'note': 'XSS from poisoned cache stole this'})
        except Exception:
            pass
    return jsonify({'error': 'No active cache poisoning detected'}), 403


@app.route('/cache/clear', methods=['POST'])
def clear_cache():
    cache_clear()
    return jsonify({'message': 'Cache cleared'})


@app.route('/cache/stats')
def cache_stats():
    return jsonify({
        'entries': [
            {'key': k, 'age_s': round(time.time() - v['ts'], 1)}
            for k, v in _cache.items()
        ]
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)

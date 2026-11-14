# 05: Defense

## Fix 1: be consistent about which value you read

The simplest fix is to decide once -- first value, last value, or reject if multiple -- and enforce it everywhere:

```python
def get_single_param(name: str) -> str:
    """Return the parameter value, raising 400 if duplicated."""
    values = request.args.getlist(name)
    if len(values) > 1:
        abort(400, description=f'duplicate {name} parameter not allowed')
    return values[0] if values else ''
```

Apply this helper everywhere a security-sensitive parameter is read.

## Fix 2: reject requests with duplicate security-sensitive parameters

A WAF or middleware can explicitly block requests where any critical parameter appears more than once:

```python
GUARDED_PARAMS = {'id', 'role', 'user', 'token'}

@app.before_request
def check_duplicate_params():
    for key in GUARDED_PARAMS:
        if len(request.args.getlist(key)) > 1:
            abort(400, description=f'duplicate {key} not allowed')
```

## Fix 3: normalize at the ingress layer

If your WAF or reverse proxy handles parameter parsing before forwarding to the backend, configure it to strip duplicate parameters or raise an error:

- Nginx `limit_req_zone` does not handle HPP, but custom Lua modules can
- ModSecurity rule `SecRule ARGS_NAMES "@contains id" "count=1"` blocks multiple `id` params
- AWS WAF does not natively block duplicate params; use a custom rule

## Why this matters beyond WAFs

HPP is not just a WAF bypass technique. It affects any two-layer system:

- Load balancer reads `role` to route privileged requests; backend reads `role` for access control
- API gateway reads `token` for rate limiting; microservice reads `token` for authentication
- Logging layer reads `user` for audit; application reads `user` for data access

Each pair is a potential HPP surface if the layers use different indexing conventions.

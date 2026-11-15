# 02: Background

## How query strings work

A URL query string is a sequence of `key=value` pairs separated by `&`. The same key can appear multiple times:

```
GET /search?id=1&id=2&id=3
```

The RFC does not specify which value should be used when a key appears more than once. Each framework implements its own behavior.

## Framework behavior comparison

| Framework | `get('id')` reads | `getlist('id')` reads |
|-----------|------------------|-----------------------|
| Flask (Python) | first value | all values as list |
| Django (Python) | last value | all values as list |
| PHP `$_GET` | last value | n/a |
| Express.js (Node) | last value | array when >1 |
| Java Servlet | first value | array |

This inconsistency is the root of HPP vulnerabilities. A WAF written in one language reading the first value and a backend written in another language reading the last value creates a split-brain situation.

## The WAF bypass model

```
Request: GET /api/search?id=1&id=1 OR 1=1--

WAF layer:
  ids = request.args.getlist('id')  # ['1', '1 OR 1=1--']
  waf_checks(ids[0])                # checks '1' -- clean, allow

Backend:
  ids = request.args.getlist('id')  # ['1', '1 OR 1=1--']
  execute_query(ids[-1])            # executes '1 OR 1=1--' -- injection
```

Both layers read the same Flask `request.args` object, but with different indexing. This models what happens when a shared layer (middleware, proxy, CDN) and application code have different conventions for handling repeated parameters.

## The access control model

```
Request: GET /api/admin?role=user&role=admin

Middleware:
  roles = request.args.getlist('role')  # ['user', 'admin']
  if roles[0] != 'admin': pass_through()  # 'user' != 'admin', allowed

Handler:
  roles = request.args.getlist('role')  # ['user', 'admin']
  if roles[-1] == 'admin': grant_access()  # 'admin' == 'admin', access
```

The middleware and handler are consistent in framework choice but inconsistent in indexing. This is the common case in real applications where security checks were added as middleware after the handler was written, without coordinating on which value to use.

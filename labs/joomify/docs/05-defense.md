# Defense

## The Fix

Upgrade to Joomla 4.4.13 or 5.2.6. The patch adds an explicit `mfa_verified` check to
every admin route handler. The check runs at the point of access, not at the client
routing layer.

## Code-Level Enforcement

The vulnerable pattern:

```python
if session.get("state") != "logged_in":
    return 403
# allow access
```

The fixed pattern:

```python
if session.get("state") != "logged_in":
    return 403
if not session.get("mfa_verified"):
    return 403, redirect_to_mfa_challenge
# allow access
```

## Defense-in-Depth

Do not rely on client routing to enforce security invariants. Any check that depends on
the client following the correct sequence can be bypassed by a client that does not
follow that sequence.

Treat every request as if it arrived out of order. Each protected endpoint must verify
the full set of preconditions independently, regardless of what the client was supposed
to do before making that request.

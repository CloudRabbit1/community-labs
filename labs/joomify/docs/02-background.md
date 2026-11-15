# Background: MFA State Machines

## How MFA Is Supposed to Work

After a successful username and password check, a server issues a partial session. The
session has a state machine: the user starts at `logged_in` but cannot access protected
resources until they complete a second factor, at which point the state advances to
`mfa_verified`. Every protected route checks both states.

The pattern has two parts. First, the authentication handler creates the session:

```
POST /login   →  session{state: logged_in, mfa_verified: false}
```

Second, every downstream check requires both conditions:

```
if session.state == "logged_in" AND session.mfa_verified == True:
    allow access
```

## The Design Assumption That Failed

Joomla's admin route handlers checked only `state == "logged_in"`. The assumption was
that any session with that state had already passed through the MFA challenge page. That
assumption only holds if the client follows the intended flow. An attacker who skips the
MFA route entirely still has a `state == "logged_in"` token and can reach admin routes
directly.

This class of bug is called a broken authentication flow. The fix is to verify the full
state at the point of access, not to rely on clients following the prescribed sequence.

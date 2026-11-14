# Background

## Authorization vs. authentication

Authentication answers "who are you." Authorization answers "what are you allowed to do." An API can get authentication right, issuing valid tokens to the right users, and still be fully compromised if it gets authorization wrong. All three bugs in this lab are authorization failures. The login system works correctly; the problem is what happens after the token is issued.

## Object-level vs. function-level

REST APIs serve two kinds of requests: requests for specific objects (`GET /api/users/2` — give me user 2's record) and requests for functions (`GET /api/admin/users` — run the admin list function). These require different authorization checks.

Object-level authorization asks: does this caller own or have permission to access this specific record? The check must happen on every request, using the caller's identity from the token, not a user ID passed in the URL.

Function-level authorization asks: does this caller have the role or permission required to invoke this function at all? Admin endpoints, billing operations, and anything destructive need this check before the function runs.

BOLA is a failed object-level check. BFLA is a failed function-level check. Both are missing checks, not broken ones.

## Mass assignment

When an API update endpoint deserializes a JSON request body directly into a database row, it may accept fields that the client should never be able to set, like `role`, `is_admin`, or `account_balance`. The fix is an explicit allowlist of fields the endpoint is permitted to update. Without it, any field the ORM recognizes is writable.

## JWTs in this lab

The API issues JSON Web Tokens on login. Each token contains the user's ID and username, signed with a server secret. The API validates the signature on every request and reads the `user_id` from the token payload to identify the caller.

What it does not do is re-verify that the token's `user_id` matches any object being requested or confirm that the token's user has a role that permits the function being called. That is where each bug lives.

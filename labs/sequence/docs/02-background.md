# Background

## SQL injection and UNION attacks

SQL injection occurs when user input is inserted directly into a SQL query without sanitization. A UNION attack extends the original query to also select data from a different table. For it to work, the injected SELECT must return the same number of columns as the original query.

In this lab the search query selects three columns: id, username, and role. The UNION payload must also select three values. By placing the target column (password_hash) in the username position, it appears in the JSON response under the "username" key.

## MD5 and hash cracking

MD5 produces a 32-character hex digest from any input. It is fast to compute, which makes it fast to crack. Tools like hashcat and john can test millions of common passwords per second against an MD5 hash. A password like "password123" appears in every common wordlist and cracks in under a second.

Storing passwords as plain MD5 without a salt is a known-bad practice that has been deprecated for decades. Any hash in a credential dump should be treated as crackable.

## Server-side request forgery

SSRF occurs when a server fetches a URL supplied by the user. An attacker can point this at internal services that are not reachable from the public internet: metadata endpoints, admin panels, internal APIs. In this lab, the import feature is restricted to "internal URLs only," which is itself the attack surface: the server resolves the URL internally, bypassing any firewall that would block the attacker's own machine.

# Defense

## HTML Escape All Output

Any user-supplied content that appears in an HTML page must be escaped before rendering. In Python:

```python
import html
safe = html.escape(user_input)
```

This converts `<script>` to `&lt;script&gt;`, which the browser displays as text rather than executing.

## Content Security Policy

A Content-Security-Policy header restricts what scripts can run on a page:

```
Content-Security-Policy: default-src 'self'; script-src 'nonce-RANDOM'
```

Even if an attacker injects a `<script>` tag, the browser will not execute it without the matching nonce. This is a defense in depth: the primary fix is always escaping output.

## HttpOnly and Secure Cookies

Mark session cookies HttpOnly so they are not accessible via JavaScript:

```python
Set-Cookie: session=abc123; HttpOnly; Secure; SameSite=Strict
```

This would have blocked the specific attack in this lab (cookie theft via `document.cookie`), but it does not prevent other XSS attacks such as DOM manipulation or keylogging.

## Input Validation

Validate that input conforms to expected types and formats at ingestion time. A comment field that only allows printable ASCII is a narrower attack surface than one that accepts arbitrary Unicode.

The correct layered approach: escape output (required), add CSP (defense in depth), use HttpOnly cookies (limits blast radius).

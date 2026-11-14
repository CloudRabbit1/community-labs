# Defense

## Never Call unserialize() on Untrusted Input

The PHP documentation warns:

> Do not pass untrusted user input to unserialize() regardless of the options value of allowed_classes.

The `allowed_classes` option in PHP 7+ lets you restrict which classes can be reconstructed, but it does not protect against data forgery (plain arrays and primitives are always allowed). The only complete fix is to avoid `unserialize()` for data that crosses a trust boundary.

## Use JSON + HMAC for Session Blobs

```php
define('SESSION_SECRET', getenv('SESSION_SECRET') ?: bin2hex(random_bytes(32)));

function save_session(array $data): string {
    $json = json_encode($data);
    $sig  = hash_hmac('sha256', $json, SESSION_SECRET);
    return base64_encode($json) . '.' . $sig;
}

function restore_session(string $token): array {
    [$b64, $sig] = explode('.', $token, 2) + ['', ''];
    $json = base64_decode($b64);
    $expected = hash_hmac('sha256', $json, SESSION_SECRET);
    if (!hash_equals($expected, $sig)) {
        throw new RuntimeException('invalid session token');
    }
    return json_decode($json, true);
}
```

JSON has no magic methods. The HMAC prevents forgery. An attacker who does not know `SESSION_SECRET` cannot produce a valid token, so even changing `role` to `admin` in the JSON will fail signature verification.

## If unserialize() Is Required

Apply the `allowed_classes` option with an explicit allowlist:

```php
$options = ['allowed_classes' => ['SafeClass1', 'SafeClass2']];
$restored = unserialize($raw, $options);
```

This blocks `Logger`, `Template`, and other dangerous classes. It does not block data forgery in arrays.

## Checklist for Developers

- Search the codebase for every call to `unserialize()`. Each one is a risk surface.
- Replace cookie-based serialized sessions with PHP's built-in session handler (server-side).
- For API tokens: use JWTs with a strong secret, or opaque signed tokens.
- Remove or scope gadget classes. A class with a dangerous `__destruct` that never runs in production is still exploitable.
- Run automated scanners (PHPCS, Psalm, Semgrep) with rules that flag `unserialize()` on request input.

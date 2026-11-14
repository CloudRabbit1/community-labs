# Finding the Bug

## The Vulnerable Code

In `lab/index.php`, the `/session/restore` endpoint:

```php
$raw = base64_decode($blob);
// Bug: unserialize() on attacker-supplied data triggers magic methods
$restored = unserialize($raw);
if (!is_array($restored)) {
    json_out(['error' => 'Invalid session data'], 400);
}
$_SESSION['user'] = $restored['user'] ?? 'anonymous';
$_SESSION['role'] = $restored['role'] ?? 'user';
```

There are two bugs:

1. `unserialize($raw)` is called before any validation. If `$raw` contains a serialized `Logger` object, `__destruct` will fire before the `is_array()` check can reject it.
2. The `role` field is read directly from the deserialized data. Even a plain PHP array can be forged to claim admin.

## The Gadget Classes

Also in `lab/index.php`:

```php
class Logger {
    public $logfile;
    public $message;

    public function __destruct() {
        if ($this->logfile && $this->message) {
            file_put_contents($this->logfile, $this->message . "\n", FILE_APPEND);
        }
    }
}
```

This class exists as part of the application. It is never instantiated in the normal code flow. But `unserialize()` will reconstruct any class whose name appears in the payload, using the codebase's class definitions.

## Confirming the Bug

Log in as alice and save a legitimate blob:

```bash
CJAR=$(mktemp)
curl -s -c "$CJAR" -b "$CJAR" -X POST http://127.0.0.1:8092/login \
    -H "Content-Type: application/json" -d '{"username":"alice","password":"alice123"}'

curl -s -c "$CJAR" -b "$CJAR" -X POST http://127.0.0.1:8092/session/save \
    -H "Content-Type: application/json" -d '{}'
```

Decode the blob to see the PHP serialized format:

```bash
echo "YToy..." | python3 -c "import base64,sys; print(base64.b64decode(sys.stdin.read()).decode())"
# Output: a:2:{s:4:"user";s:5:"alice";s:4:"role";s:4:"user";}
```

A plain array. The restore endpoint trusts whatever `role` appears in this string.

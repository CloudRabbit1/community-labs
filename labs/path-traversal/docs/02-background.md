# Background

## How Path Joins Work

`os.path.join(base, name)` builds a path by appending `name` to `base`:

```python
os.path.join("/app/docs", "readme.txt")   # /app/docs/readme.txt
os.path.join("/app/docs", "../../flag.txt")  # /app/docs/../../flag.txt
```

The second result contains `..` sequences. The OS resolves them when the path is opened: `/app/docs/../../flag.txt` becomes `/flag.txt`.

The function does not remove or warn about `..`. It simply concatenates.

## Canonicalization

`os.path.realpath` resolves all `..` and symlinks to produce the absolute canonical path:

```python
os.path.realpath("/app/docs/../../flag.txt")  # /flag.txt
```

Comparing the canonical path to the document root tells you whether the access is legitimate:

```python
doc_root = "/app/docs"
canonical = os.path.realpath(os.path.join(doc_root, name))
if not canonical.startswith(doc_root + "/"):
    return error("access denied")
```

## Encoding Variants

Servers often normalize URLs before routing, but the query string value is typically decoded later. These payloads all resolve to `../../flag.txt` after URL decoding:

| Payload | Decoded |
|---------|---------|
| `../../flag.txt` | `../../flag.txt` |
| `%2e%2e%2f%2e%2e%2fflag.txt` | `../../flag.txt` |
| `..%2f..%2fflag.txt` | `../../flag.txt` |

Some filters block the literal `../` string; URL-encoding bypasses them.

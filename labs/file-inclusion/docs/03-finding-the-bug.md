# Finding the Bug

The vulnerability is in `app.py`:

```python
full_path = os.path.join(PAGES_DIR, page)
with open(full_path) as f:
    content = f.read()
```

`PAGES_DIR` is `/app/pages`. The `page` parameter comes directly from the query string with no stripping or validation. `os.path.join` appends it verbatim, so:

- `page=about.txt` opens `/app/pages/about.txt` (intended)
- `page=../../flag.txt` opens `/app/pages/../../flag.txt`, which resolves to `/flag.txt` (unintended)

The fix is to resolve both paths and reject any result that does not start with the base directory:

```python
real = os.path.realpath(os.path.join(PAGES_DIR, page))
if not real.startswith(PAGES_DIR + "/"):
    raise PermissionError
```

# Background

## Path Traversal Sequences

Every Unix filesystem has two special directory entries: `.` (current directory) and `..` (parent directory). A path like `/app/pages/../../flag.txt` resolves to `/flag.txt` because each `..` moves one level up.

When an application builds a file path like this:

```python
full_path = os.path.join("/app/pages", user_input)
```

the result for `user_input = "../../flag.txt"` is `/app/pages/../../flag.txt`, which the OS resolves to `/flag.txt`. The `join()` call does not block or strip traversal sequences.

## Why os.path.join Is Not Enough

A common misconception is that `os.path.join` is safe. It is not. It concatenates path components and resolves `..` normally. The only safe pattern is to resolve the full path and confirm it starts with the expected base:

```python
full_path = os.path.realpath(os.path.join(BASE_DIR, user_input))
if not full_path.startswith(BASE_DIR + os.sep):
    raise PermissionError
```

## URL Encoding

Servers may decode URL-encoded sequences before the application sees them. `%2e%2e%2f` decodes to `../`, so blocklists that only check for literal `../` can be bypassed.

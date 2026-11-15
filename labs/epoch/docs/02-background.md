# Background

## Shell command construction

When a Python application calls `subprocess.run(cmd, shell=True)` or `os.system(cmd)`, the entire string `cmd` is passed to `/bin/sh -c`. The shell parses the string the same way it would parse something you typed at a terminal. That means metacharacters have special meaning.

A semicolon `;` ends one command and starts another:

```
date -d @0 ; cat /flag.txt
```

The shell runs `date -d @0` first, then `cat /flag.txt`. Both run. Both produce output.

## Why this is dangerous

If the application builds the command string from user input:

```python
cmd = f"date -d @{user_input}"
subprocess.run(cmd, shell=True)
```

And the user supplies `0;cat /flag.txt`, the shell sees:

```
date -d @0;cat /flag.txt
```

The flag is read as part of the same command execution.

## Common metacharacters

| Character | Effect |
|-----------|--------|
| `;` | Run next command unconditionally |
| `\|` | Pipe stdout of first to stdin of second |
| `&&` | Run next command if first succeeds |
| `\|\|` | Run next command if first fails |
| `` ` `` | Run command in subshell, substitute output |
| `$()` | Run command in subshell, substitute output |

Any of these can terminate the intended command and start an attacker-controlled one.

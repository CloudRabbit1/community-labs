# Background

## How Shell Metacharacters Work

A Unix shell treats certain characters as separators between commands. The most common ones:

| Character | Meaning |
|-----------|---------|
| `;` | Run the next command regardless of exit code |
| `\|` | Pipe stdout of left command to stdin of right command |
| `&&` | Run the next command only if the first succeeded |
| `` ` `` | Execute the enclosed command and substitute the output |
| `$()` | Same as backtick, modern syntax |

When the server builds a command string like `"ping -c 3 " + user_input` and passes it to `subprocess.run(..., shell=True)` or `os.system(...)`, the shell processes every metacharacter in `user_input`. The developer intended only a hostname, but the shell has no way to know that.

## Why Sanitization Is Hard

Blocklists fail. If you block `;` and `|`, an attacker uses `%0a` (newline), `${IFS}` (the shell's internal field separator), or `{cat,/flag.txt}` (brace expansion). The correct fix is never to pass user input to a shell at all.

# Defense

[Two parts: how to detect this in the wild, and how to fix it.
Keep it practical. Commands and config changes, not theory.]

## Detection

[What evidence does this attack leave? Log lines, network signatures,
filesystem changes. Show the actual log output an analyst would see.]

```
[example log entry or alert]
```

[One sentence: what field or value to key on.]

## Fix

[What change eliminates the vulnerability? Show the before and after
for any config file, patch, or package update.]

**Upgrade:**

```bash
[package upgrade command]
```

**Or patch the config:**

```
[before]
```

```
[after]
```

## Verify the fix

[Show one command that confirms the fix is in place and what output
to expect.]

```bash
[verification command]
```

```
[expected output after fix]
```

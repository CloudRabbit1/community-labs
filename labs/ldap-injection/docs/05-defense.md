# Defense

Escape LDAP special characters before interpolating user input into a filter. RFC 4515 defines the escape sequence: each special character is replaced with a backslash followed by its two-digit hex code.

Characters to escape: `*` `(` `)` `\` `NUL`.

```python
def ldap_escape(s: str) -> str:
    replacements = {
        "\\": "\\5c",
        "*":  "\\2a",
        "(":  "\\28",
        ")":  "\\29",
        "\0": "\\00",
    }
    for char, escaped in replacements.items():
        s = s.replace(char, escaped)
    return s

# Safe filter construction
safe_username = ldap_escape(username)
safe_password = ldap_escape(password)
ldap_filter = f"(&(uid={safe_username})(userPassword={safe_password}))"
```

With escaping applied, `*)(uid=*))(|(uid=*` becomes `\2a\29\28uid=\2a\29\29\28|\28uid=\2a`, which the LDAP server treats as a literal string, not filter syntax.

Prefer LDAP libraries that accept parameterized queries or handle escaping internally, such as `python-ldap`'s `ldap.filter.escape_filter_chars()`. Do not write escape functions by hand in production code.

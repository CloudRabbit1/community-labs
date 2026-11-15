# Background: LDAP Filter Syntax

LDAP (Lightweight Directory Access Protocol) is a protocol for reading and querying directory services, such as Active Directory or OpenLDAP. Applications use it to look up users, check group memberships, and authenticate.

Authentication works by constructing a search filter and asking the directory whether any entry matches. A typical filter looks like this:

```
(&(uid=alice)(userPassword=secret))
```

This means: find an entry where the uid is `alice` AND the userPassword is `secret`. Both conditions must be true. If a matching entry exists, the user is authenticated.

The characters `(`, `)`, `*`, `\`, and `NUL` are special in LDAP filter syntax. If an application interpolates user input directly into a filter string without escaping those characters, the input can change the structure of the filter.

Consider the injection payload `*)(uid=*))(|(uid=*`:

```
(&(uid=*)(uid=*))(|(uid=*)(userPassword=anything))
```

Breaking it down:
- `(&(uid=*)(uid=*))` matches any entry where uid exists. The `*` wildcard matches everything.
- `(|(uid=*)(userPassword=anything))` is an OR clause, also always true via `uid=*`.

The original password check is now outside the closing `&` scope and is never enforced. Any user with a uid is returned.

This is an LDAP injection, the directory-services analogue of SQL injection.

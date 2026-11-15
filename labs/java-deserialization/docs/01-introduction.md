# Introduction

## What This Lab Is About

This lab shows how an application that deserializes user-supplied bytes without validation gives attackers two distinct powers: privilege escalation (forge any session) and remote code execution (run arbitrary shell commands).

The lab uses Python's `pickle` module. The same attack class applies to Java's `ObjectInputStream`, PHP's `unserialize()`, Ruby's `Marshal.load`, and any other language that deserializes user input without restrictions. The mechanics are different but the outcome is identical: an attacker who controls the bytes being deserialized controls what code runs on the server.

## The Vulnerable Pattern

```python
# Bug: attacker controls `raw`
restored = pickle.loads(raw)
session['user'] = restored.get('user', 'anonymous')
session['role'] = restored.get('role', 'user')
```

## Two Exploits in One Bug

**Exploit 1 (privilege escalation):** A plain dict pickle `{'user': 'admin', 'role': 'admin'}` deserializes to a Python dict. The app reads `role = 'admin'` from it. No `__reduce__`, no shell commands needed. The app trusted the data.

**Exploit 2 (RCE):** A class with a `__reduce__` method can return any callable with any arguments. `pickle.loads` will call it. `(os.system, ('id',))` runs `id` on the server. This works even if the app never uses the return value.

## Why This Matters

Insecure deserialization is OWASP A08:2021. Real-world examples include CVE-2015-4852 (Oracle WebLogic), CVE-2017-7525 (Jackson Java), and many others. The pattern is the same in every case: a framework or application deserializes untrusted bytes and an attacker uses the type system of the language itself as a weapon.

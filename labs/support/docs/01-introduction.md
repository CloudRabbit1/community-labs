# Introduction

This lab contains a support ticket system called TicketDesk. It has a critical vulnerability in how it handles session state.

**Pickle deserialization**: Python's `pickle` module serializes objects to bytes and can reconstruct them later. When an object is unpickled, Python calls its `__reduce__` method to decide how to reconstruct it. This means a crafted pickle payload can call any Python function during deserialization, including `subprocess.check_output`, effectively running arbitrary commands.

TicketDesk stores session data as a base64-encoded pickle blob in a cookie. The server unpickles whatever it receives with no signature and no integrity check. An attacker can replace the cookie with a malicious pickle to execute code on the server.

The two flags require two different techniques:
- flag1: craft a pickle that calls `subprocess.check_output` to read `/flag1.txt`. The return value (bytes) is detected and echoed in the HTTP response.
- flag2: craft a pickle that returns a plain dict with `"role": "admin"`. The server accepts it as a legitimate session, grants access to the admin panel, and the panel displays flag2.

The second technique does not require code execution. It shows that even without RCE, a forged session cookie can be enough to escalate privileges.

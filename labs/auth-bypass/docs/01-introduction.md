# Introduction

This lab contains two authentication bypass bugs. Both are in the session and account management layer, not in the business logic. They are common, easy to miss in code review, and exploitable with nothing more than base64 decoding and an MD5 hash.

**Unsigned session cookie**: the application stores session data as base64-encoded JSON in a cookie. Base64 is encoding, not encryption and not signing. Anyone can decode it, change the `role` field to `admin`, re-encode it, and send it back. The server has no way to tell the difference between a cookie it issued and one the attacker fabricated.

**Predictable password reset token**: the password reset endpoint generates a token from the MD5 hash of the username. MD5 is a public hash function. Given any username, you can compute the expected token without touching the server. This lets you request a password reset for any account and immediately confirm it without ever receiving the reset email.

You will exploit both flaws in this lab. At the end you will have accessed the admin panel using a forged session and taken over bob's account by computing his reset token.

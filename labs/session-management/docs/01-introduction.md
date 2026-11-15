# Introduction

A session token is the credential a server issues after login. Every subsequent request carries the token so the server knows who is asking. The token must be unpredictable: if an attacker can guess another user's token, they can impersonate that user without knowing their password.

This lab shows what happens when tokens are issued sequentially. The app hands out `session_1`, `session_2`, `session_3`, and so on. The admin account was created at startup and received `session_1`. Any user who registers and receives `session_5` can immediately infer that earlier tokens exist and try them, one by one, until they find one that belongs to a privileged account.

This class of bug is called session prediction. It is listed in the OWASP Testing Guide (OTG-SESS-003) and is one of the original session management failures that motivated the creation of cryptographically random session identifiers.

# Introduction

Multi-factor authentication adds a second check after the password. The idea is that even if an attacker steals your password, they cannot log in without the second factor. OTP apps like Google Authenticator generate codes from a shared secret and the current time using a standard algorithm (TOTP, RFC 6238). The secret never leaves the device, so the server and the client stay in sync without sending the code over the wire first.

This lab shows what happens when a developer reimplements OTP generation without following that standard. The server produces a six-digit code from the current Unix timestamp with no shared secret. Any attacker who reads the source code, or who can guess the derivation formula, can compute the same code and bypass MFA entirely.

The lesson is not about brute force. The lesson is that security through obscurity fails: a formula that is not cryptographically tied to a secret is not a second factor.

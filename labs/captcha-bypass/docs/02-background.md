# Background

## How CAPTCHAs work

A CAPTCHA presents a challenge that is easy for humans but hard for automated scripts. The server generates a challenge, the client solves it, and the server verifies the solution before allowing the form submission to proceed.

For a CAPTCHA to be effective, two properties must hold:

1. The challenge must be unpredictable. If the answer can be computed from information available to the attacker, any script can solve it.
2. Each token must be single-use. If a token remains valid after use, an attacker can obtain one token and replay it indefinitely.

## What makes CAPTCHAs weak

**Static or predictable seeds**: if the server derives the answer from a fixed value and that value is exposed, the CAPTCHA is effectively disabled. Any caller who reads the challenge text can compute the answer without rendering or solving anything.

**No token invalidation**: a token that is never removed from the valid set can be reused. The attacker fetches one token at startup and uses it for every subsequent request.

## MD5 as a CAPTCHA answer

MD5 is a hash function, not a secret. If the input (the seed) is known, the output is deterministic and immediately computable with any language's standard library. Using MD5 of a static string as a CAPTCHA answer provides no security at all.

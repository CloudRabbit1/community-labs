# Introduction

Rate limiting is a common defense against brute-force attacks. The idea is to slow an attacker down enough to make guessing impractical. This lab shows two ways that defense breaks when it is not built carefully.

The app uses a password reset flow: request an OTP for an email address, then submit the OTP to get a session token. The OTP is four digits, giving 10,000 possible values. Without any rate limiting, brute-forcing that takes seconds.

The rate limit checks the `X-Forwarded-For` header to identify the caller. That header is set by the client, not the network. An attacker can send any value they want. Rotating the value on each request makes every attempt look like it comes from a different IP address.

After getting a session token, the `/execute` endpoint runs OS commands. It checks that the command starts with one of a small allowlist. Checking a prefix instead of the full string is a common logic error. `id; cat /flag.txt` starts with `id`, so it passes.

This lab chains both flaws: bypass the rate limit to brute-force the OTP, then bypass the allowlist to read the flag.

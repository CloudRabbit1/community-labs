# Introduction

Real attacks rarely rely on a single vulnerability. They chain several smaller issues together, where the output of one step becomes the input for the next. This lab presents exactly that: three distinct vulnerabilities that individually might seem limited, but together give full access to an internal service.

The chain: SQL injection leaks an admin password hash, the hash is weak and cracks in seconds, the cracked password logs you in as admin, and admin access to an import feature enables server-side request forgery to reach an internal endpoint.

## What you will do in this lab

1. Inject a UNION payload into the search endpoint to extract the admin password hash from the database.
2. Identify the hash algorithm and crack the hash to recover the plaintext password.
3. Log in as admin and use the import endpoint to send a request to an internal URL, capturing the second flag.

## Why it matters

Attackers rarely stop at the first vulnerability they find. If SQL injection only returns usernames, they look for password hashes. If the hashes are weak, they crack them. This lab trains the habit of following a chain through to its end.

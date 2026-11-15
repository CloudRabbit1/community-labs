# Introduction

Insecure Direct Object Reference (IDOR) happens when an application uses a user-controlled value to look up a resource without checking whether the requesting user is allowed to access it. The server authenticates the user but does not authorise the access. In this lab the value is a document ID in the URL. Any authenticated user can read any document, including documents that belong to other accounts.

## What you will do

- Confirm that authentication is enforced but ownership is not checked
- Enumerate document IDs to find resources outside your own account
- Read the admin's private document and retrieve the flag

## What you need

- Docker with Compose installed ([instructions in the README](../README.md))
- Basic comfort with curl
- No special tools; sequential integer IDs are enough

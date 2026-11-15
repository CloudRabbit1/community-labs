# Introduction

This lab contains a REST API with three authorization bugs that appear in real applications every year. They are not subtle implementation errors. They are design decisions that look reasonable until you think about them from the outside.

The three flaws are:

**BOLA (Broken Object Level Authorization)**: the API uses a user ID in the URL to decide which record to return, but it does not check whether the caller owns that record. Change the ID in the request and you get someone else's data.

**BFLA (Broken Function Level Authorization)**: the API has a separate set of admin endpoints, but it never checks whether the caller is actually an admin before serving the response. Any authenticated user can call them.

**Mass assignment**: the account update endpoint accepts a JSON object and writes every field it recognizes into the database, including `role`. A regular user can promote themselves to admin with a single request.

OWASP lists BOLA as the top API security risk and BFLA and mass assignment as separate entries in the same top-ten list. That placement reflects their frequency in production systems, not their theoretical severity.

You will exploit all three in this lab against an account called `alice`. When you finish, `alice` will have read another user's private data, accessed an admin endpoint she was never supposed to reach, and given herself admin privileges.

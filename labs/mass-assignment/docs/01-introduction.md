# Introduction

Mass assignment happens when a web API automatically binds the fields in a JSON request body to an internal data model, without checking which fields the caller is allowed to change. If the model contains a `role` or `isAdmin` field, an attacker can include it in a normal profile update request and change their own privilege level.

This lab runs a user profile API where `PUT /api/user/profile` accepts any JSON and merges it into the user's record. Sending `{"role": "admin"}` escalates you to admin. No password required, no special headers, just an extra field in a standard request.

The vulnerability was assigned CVE-2023-35933 in the Payload CMS project. It is a common class of bug in frameworks that auto-deserialize request bodies into model objects.

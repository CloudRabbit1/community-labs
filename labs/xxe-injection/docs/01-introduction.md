# Introduction

XML External Entities (XXE) is a vulnerability that affects applications parsing XML input. XML supports a feature called external entities: a placeholder name that the parser replaces with the contents of a URI before the application sees the data. When the URI is a `file://` path, the parser reads a local file. When the URI is an `http://` URL, the parser makes an outbound request (Server-Side Request Forgery).

This lab runs a document processor that accepts XML and returns the text content of `<item>` elements. The parser expands external entities before extracting items, so injecting a DOCTYPE that maps an entity to `file:///flag.txt` causes the flag to appear in the parsed output.

XXE is part of the OWASP Top 10. Real-world impacts include reading `/etc/passwd`, application configuration files, AWS instance metadata, and reaching internal services that accept HTTP.

## What you will do

- Send well-formed XML to understand the normal response format
- Craft a DOCTYPE that declares an external entity pointing to `/flag.txt`
- Reference the entity inside an `<item>` element and read the flag from the response

## What you need

- Docker with Compose installed ([instructions in the README](../README.md))
- curl or Python 3
- Basic familiarity with XML syntax

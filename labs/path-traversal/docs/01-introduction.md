# Introduction

Path traversal is what happens when a web application builds a file path from user-supplied input without checking that the final path stays within the intended directory. The `..` sequence moves up one directory level in the filesystem. By chaining enough of them, an attacker can step above the document root and read any file the web server process can open.

This lab runs a document server that exposes a `/file?name=` endpoint. The name is passed directly to `os.path.join(doc_root, name)` with no normalization. Supplying `../../flag.txt` as the name causes the join to resolve outside the document root to `/flag.txt`.

Path traversal appears on the OWASP Top 10 as part of Broken Access Control. Real-world impacts include reading source code, configuration files, private keys, and database credentials.

## What you will do

- Browse the document root to understand the normal use case
- Identify the unsanitized parameter
- Craft a traversal payload that reads `/flag.txt`

## What you need

- Docker with Compose installed ([instructions in the README](../README.md))
- curl or Python 3

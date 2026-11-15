# Introduction

JSON Web Tokens (JWTs) are the most common way web applications prove that a user is who they claim to be. The server signs a token when you log in, and you send that token with every request so the server knows it is talking to you.

The design has two common failure modes. First, the server may trust whatever algorithm the token header names, including "none", which means no signature at all. An attacker who knows this can forge a token claiming to be any user. Second, if the signing key is a weak password like "secret123", an attacker can brute-force it offline and mint any token they want.

This lab demonstrates both attacks against a small authentication service. One valid credential is provided. The goal is to reach the `/admin` endpoint, which only accepts tokens where the username is "admin".

## What you will do

- Log in as a normal user and inspect the token the server issues
- Forge an admin token using the alg:none bypass
- Forge an admin token by recovering the signing key

## What you need

- Docker with Compose installed ([instructions in the README](../README.md))
- Python 3 with no extra packages
- Basic comfort with base64 and JSON

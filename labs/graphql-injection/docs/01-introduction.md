# Introduction

GraphQL is a query language for APIs that gives clients control over what data they request. Instead of fixed URL endpoints, a GraphQL server exposes a single endpoint where clients send structured queries. This flexibility is powerful -- and it creates new attack surfaces that do not exist in REST APIs.

This lab demonstrates two of them:

1. Introspection: GraphQL servers expose their full schema by default. An attacker can query `__schema` to discover every type, field, mutation, and argument -- including endpoints that were never meant to be public.

2. Broken mutation logic: A login mutation that accepts a password argument but forgets to check it. Any user authenticates with any password, and the server returns a flag in the mutation response.

## Goal

Flag 1: use introspection to find the broken `login` mutation, then authenticate as alice with the wrong password.

Flag 2: use the same technique to get an admin token, then call the `adminPanel` query that only admin-role tokens can access.

## Setup

```bash
docker compose up --build -d
```

The app starts on `127.0.0.1:8086`. Visit `http://127.0.0.1:8086/` to see the homepage with example queries.

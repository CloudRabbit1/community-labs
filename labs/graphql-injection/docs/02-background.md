# Background

## GraphQL in 60 seconds

A GraphQL server exposes one HTTP endpoint, usually `/graphql`. Clients POST a JSON body containing a `query` or `mutation` string.

A query reads data:

```graphql
{
  products {
    name
    price
  }
}
```

A mutation modifies data (or, in many apps, performs actions like login):

```graphql
mutation {
  login(username: "alice", password: "secret") {
    token
    role
  }
}
```

The server returns JSON shaped exactly like the query.

## Introspection

GraphQL servers answer questions about their own schema. The `__schema` meta-field lists every type and every operation the server supports:

```graphql
{
  __schema {
    queryType { fields { name description } }
    mutationType { fields { name description args { name } } }
  }
}
```

This is not a vulnerability by itself. It is a feature. The vulnerability is what introspection reveals: endpoints, argument names, descriptions, and sometimes notes the developer left in the schema that were never meant to be public.

## Common GraphQL flaws

| Flaw | Description |
|------|-------------|
| Introspection left enabled in production | Exposes full schema to unauthenticated callers |
| Missing input validation in mutations | Arguments accepted but not checked (this lab) |
| Broken object-level authorization | Query resolver returns data for any token without checking ownership |
| Batching attacks | Multiple operations in one request bypass per-request rate limits |

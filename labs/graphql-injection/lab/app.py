#!/usr/bin/env python3
import os
import graphene
from flask import Flask, request, jsonify
from graphql import GraphQLError

app = Flask(__name__)

FLAG1 = open("/flag1.txt").read().strip()
FLAG2 = open("/flag2.txt").read().strip()

USERS = {
    "alice": {"role": "user",  "token": "tok_alice_7f3a"},
    "admin": {"role": "admin", "token": "tok_admin_9b2c"},
}

PRODUCTS = [
    {"id": 1, "name": "Widget",  "price": 9.99,   "internal_sku": "INT-001"},
    {"id": 2, "name": "Gadget",  "price": 19.99,  "internal_sku": "INT-002"},
    {"id": 3, "name": "Thingus", "price": 4.99,   "internal_sku": "INT-003"},
]

def get_user_from_request():
    token = request.headers.get("X-Auth-Token", "")
    for username, data in USERS.items():
        if data["token"] == token:
            return username, data["role"]
    return None, None


class ProductType(graphene.ObjectType):
    id    = graphene.Int()
    name  = graphene.String()
    price = graphene.Float()
    internal_sku = graphene.String()
    secret_field = graphene.String(description="Admin-only: internal cost tracking")


class UserType(graphene.ObjectType):
    username = graphene.String()
    role     = graphene.String()
    flag     = graphene.String(description="Admin-only flag field")


class Query(graphene.ObjectType):
    products = graphene.List(ProductType)
    product  = graphene.Field(ProductType, id=graphene.Int(required=True))
    me       = graphene.Field(UserType)
    admin_panel = graphene.Field(UserType, description="Admin-only endpoint")

    def resolve_products(self, info):
        return [
            {
                "id": p["id"],
                "name": p["name"],
                "price": p["price"],
                "internal_sku": p["internal_sku"],
                "secret_field": None,
            }
            for p in PRODUCTS
        ]

    def resolve_product(self, info, id):
        p = next((p for p in PRODUCTS if p["id"] == id), None)
        if not p:
            raise GraphQLError("Product not found")
        return {
            "id": p["id"],
            "name": p["name"],
            "price": p["price"],
            "internal_sku": p["internal_sku"],
            "secret_field": None,
        }

    def resolve_me(self, info):
        username, role = get_user_from_request()
        if not username:
            raise GraphQLError("Not authenticated")
        return {"username": username, "role": role, "flag": None}

    def resolve_admin_panel(self, info):
        username, role = get_user_from_request()
        if role != "admin":
            raise GraphQLError("Admin only")
        return {"username": username, "role": role, "flag": FLAG2}


class Login(graphene.Mutation):
    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)

    token = graphene.String()
    role  = graphene.String()
    flag  = graphene.String()

    # VULNERABLE: password check is broken -- any password works for alice
    # The flag is exposed in the login mutation response
    def mutate(self, info, username, password):
        user = USERS.get(username)
        if not user:
            raise GraphQLError("User not found")
        # Bug: forgot to check the password
        return Login(token=user["token"], role=user["role"], flag=FLAG1)


class Mutation(graphene.ObjectType):
    login = Login.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)


@app.route("/graphql", methods=["GET", "POST"])
def graphql_view():
    data = request.get_json(force=True) or {}
    query = data.get("query", "")
    variables = data.get("variables")
    result = schema.execute(query, variable_values=variables,
                            context_value=request)
    response = {}
    if result.errors:
        response["errors"] = [str(e) for e in result.errors]
    if result.data is not None:
        response["data"] = result.data
    return jsonify(response), 200 if not result.errors else 400


@app.route("/")
def index():
    return """<!doctype html><html><head><title>GraphHub</title>
<style>body{font-family:sans-serif;max-width:600px;margin:40px auto;padding:0 20px}
pre{background:#f4f4f4;padding:12px;border-radius:4px;overflow:auto}</style></head>
<body><h2>GraphHub API</h2>
<p>GraphQL endpoint: <code>POST /graphql</code></p>
<p>Try introspection to discover the schema:</p>
<pre>curl -s -X POST http://127.0.0.1:8086/graphql \\
  -H 'Content-Type: application/json' \\
  -d '{"query":"{ __schema { queryType { fields { name description } } } }"}'</pre>
</body></html>"""

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)

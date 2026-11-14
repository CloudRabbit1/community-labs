# Defense

## Fix 1: validate that field values are strings

Before passing user input to MongoDB, check that each field is the type you expect:

```python
def login():
    data = request.get_json(force=True) or {}
    username = data.get("username")
    password = data.get("password")

    if not isinstance(username, str) or not isinstance(password, str):
        return jsonify({"error": "invalid input"}), 400

    user = db.users.find_one({"username": username, "password": password})
    ...
```

An object like `{"$gt": ""}` fails the `isinstance(x, str)` check and is rejected before reaching MongoDB.

## Fix 2: use a schema validation library

Libraries like `pydantic`, `marshmallow`, or `cerberus` validate the shape and types of incoming data:

```python
from pydantic import BaseModel

class LoginRequest(BaseModel):
    username: str
    password: str

@app.route("/login", methods=["POST"])
def login():
    try:
        body = LoginRequest.model_validate(request.get_json())
    except Exception:
        return jsonify({"error": "invalid input"}), 400
    user = db.users.find_one({"username": body.username, "password": body.password})
    ...
```

Pydantic rejects any `username` value that is not a string, including objects with MongoDB operators.

## Fix 3: hash passwords

The lab stores passwords in plaintext. Even with parameterized queries, plaintext passwords are exposed if the database is compromised. Hash passwords with bcrypt or argon2 and compare the hash:

```python
import bcrypt

# On registration
hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
db.users.insert_one({"username": username, "password_hash": hashed})

# On login (after type validation)
user = db.users.find_one({"username": username})
if user and bcrypt.checkpw(password.encode(), user["password_hash"]):
    # authenticated
```

This also prevents the `$gt: ""` attack on the password field, since the password comparison becomes a hash check that happens in application code, not in a MongoDB query.

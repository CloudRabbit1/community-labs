# Background

## MongoDB query format

MongoDB queries use JSON objects to describe what to match. A simple equality check looks like:

```javascript
db.users.find_one({"username": "alice", "password": "hunter2"})
```

MongoDB also supports comparison operators: `$gt` (greater than), `$lt` (less than), `$in` (in list), `$regex` (regular expression). These are prefixed with `$` and go inside the value object:

```javascript
// Match any user where age is greater than 18
db.users.find_one({"age": {"$gt": 18}})
```

## Why this is a problem

If the application passes the user-supplied JSON directly to MongoDB, an attacker can inject these operators. Instead of:

```json
{"username": "alice", "password": "hunter2"}
```

they send:

```json
{"username": {"$gt": ""}, "password": {"$gt": ""}}
```

MongoDB interprets this as: find any user where `username > ""` AND `password > ""`. Every non-empty string satisfies `$gt: ""`, so this matches the first user in the collection.

## The difference from SQL injection

SQL injection breaks out of a string context using quotes. NoSQL injection here works within the JSON structure. The attacker does not inject text into a string; they replace the string value with a JSON object containing an operator. The injection succeeds because the application trusts the JSON body completely.

## $regex for targeting

`$regex` lets you specify a regular expression:

```json
{"username": {"$regex": "^admin$"}, "password": {"$gt": ""}}
```

This matches only users whose username matches the pattern `^admin$` (exactly "admin"). You can target specific accounts without knowing the password.

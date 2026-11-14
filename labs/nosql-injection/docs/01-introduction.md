# Introduction

NoSQL databases like MongoDB do not use SQL, but they still support query operators that can be injected if user input reaches the database query without sanitization. MongoDB's query language uses JSON objects, and operators like `$gt` (greater than), `$regex` (regular expression match), and `$where` (JavaScript evaluation) change how the query is evaluated.

This lab runs a login form that passes the entire JSON request body directly to `db.users.find_one()`. Sending `{"$gt": ""}` as the value for `username` turns the equality check into a "greater than empty string" check, which matches any user. Sending `{"$regex": "^admin$"}` matches specifically the user named `admin`.

The technique was used in the wild against HarperDB (CVE-2023-27084) and is common in Node.js applications using Mongoose without input validation.

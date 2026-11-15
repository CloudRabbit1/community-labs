# Finding the Bug

Start the lab and try a username that does not exist:

```bash
docker compose up --build -d

curl -s -X POST http://localhost:8085/login \
  -H "Content-Type: application/json" \
  -d '{"username":"notauser","password":"anything"}'
```

Output:
```json
{"error": "user not found"}
```

Now try a username that might be real, with a wrong password:

```bash
curl -s -X POST http://localhost:8085/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"wrongpassword"}'
```

Output:
```json
{"error": "incorrect password"}
```

The messages are different. `admin` returned "incorrect password" rather than "user not found". The admin account exists, and the attacker now knows to focus their brute-force on that username alone.

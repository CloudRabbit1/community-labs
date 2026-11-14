# Finding the Bug

Start the lab and test the endpoint with clean XML:

```bash
docker compose up --build -d

curl -s -X POST http://localhost:8084/upload \
  -H "Content-Type: application/xml" \
  -d '<data><item>hello world</item></data>'
```

Output:
```json
{
  "parsed": true,
  "items": ["hello world"]
}
```

The service returns whatever text appears in `<item>` elements. Now test whether the parser expands internal entities:

```bash
curl -s -X POST http://localhost:8084/upload \
  -H "Content-Type: application/xml" \
  -d '<?xml version="1.0"?><!DOCTYPE data [<!ENTITY x "EXPANDED">]><data><item>&x;</item></data>'
```

Output:
```json
{
  "parsed": true,
  "items": ["EXPANDED"]
}
```

The entity `&x;` was replaced with `EXPANDED`. The parser processes entity declarations. The next step is to test a SYSTEM entity pointing to a local file.

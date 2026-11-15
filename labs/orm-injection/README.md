# ORM Injection

| Field | Value |
|-------|-------|
| Technique | SQL injection via raw string interpolation in login query |
| Target | Employee Portal login endpoint |
| Difficulty | Medium |

## Quick Start

```bash
docker compose up --build -d
python3 exploit/exploit.py http://localhost:8080
```

## How It Works

The `/login` endpoint builds a SQL query by directly interpolating the username and password into the query string. No parameterized queries are used. Appending `'--` to the username closes the string literal and comments out the rest of the WHERE clause, so the password check never runs.

See [docs/](docs/) for background and [solutions/walkthrough.md](solutions/walkthrough.md) for the full walkthrough.

## Clone This Lab

```bash
git clone https://github.com/CloudRabbit1/community-labs.git
cd community-labs/orm-injection
docker compose up --build -d
```

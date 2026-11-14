# Background

## Default credentials

Many web applications ship with a default administrator account. The credentials are set during installation and are either documented in the product manual, left in comments in the source code, or guessed by trying common combinations like `admin/admin` or `admin/password`.

Developers sometimes leave credential hints in HTML comments during development and forget to remove them before deployment. Browser dev tools show the full HTML source including comments; curl shows it in the response body.

## Shell command injection

When a web application runs a system command and includes user-supplied input in that command, any shell metacharacter in the input becomes part of the command itself.

In bash, a semicolon separates two commands:

```bash
bash -c "ping -c 1 127.0.0.1; id"
```

This runs ping and then runs `id`. The two commands are independent. If the application builds the command by concatenating user input, an attacker who controls that input can inject any command after a semicolon.

The `/api/ping` endpoint in this lab does exactly this:

```python
result = subprocess.run(
    f"ping -c 1 -W 1 {host}",
    shell=True, ...
)
```

The `shell=True` parameter means Python passes the string to bash. A semicolon in `host` creates a second command.

## Internal service pivot

In a real network, internal services often bind to `127.0.0.1` or to a private network segment that is not reachable from the internet. An attacker who gains code execution on one host can then reach those internal services by running commands on that host: `curl http://127.0.0.1:9090/`, `nc 10.0.0.5 3306`, and so on. This is called a pivot: using one compromised system to reach another.

In this lab, the internal service is on `127.0.0.1:9090` inside the container. Port 9090 is not exposed in `docker-compose.yml`, so you cannot connect to it directly from your machine. The only path to it is through the injection.

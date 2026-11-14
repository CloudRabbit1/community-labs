# Introduction

Server-Side Template Injection (SSTI) happens when an application passes user input to a template engine without first sanitizing it. Template engines like Jinja2, Twig, and Freemarker evaluate expressions inside `{{ }}` markers. When input lands inside those markers, an attacker controls what the engine evaluates.

The consequence in Python/Jinja2 is full remote code execution. The Python object hierarchy is reachable from any string object. By walking from `''.__class__` up through `__mro__` and then down through `__subclasses__()`, an attacker reaches `subprocess.Popen` and can run arbitrary shell commands as the web server process.

This lab simulates a Flask blog where the greeting endpoint renders the `name` parameter directly in a Jinja2 `render_string()` call. No authentication is required. Any visitor who discovers the endpoint can execute commands on the server.

# Defense

## Never Render User Input as a Template String

The fix is a one-line change:

```python
# Vulnerable
render_template_string(f"Hello, {user_input}!")

# Safe
render_template_string("Hello, {{ name }}!", name=user_input)
```

In the safe version, `name` is a variable binding. Jinja2 HTML-escapes it and never evaluates it as an expression. The user cannot inject `{{ }}` markers because they are not in the template string.

## Sandbox the Template Engine

Jinja2 has a `SandboxedEnvironment` that restricts attribute access and blocks access to dunder methods:

```python
from jinja2.sandbox import SandboxedEnvironment
env = SandboxedEnvironment()
env.from_string("Hello, {{ name }}!").render(name=user_input)
```

This blocks the `__class__.__mro__.__subclasses__()` chain. It is a defense-in-depth measure, not a substitute for passing user data as variables.

## Treat All Template Input as Untrusted

Code review should flag any call where user-controlled data appears in the first argument of `render_template_string()`, `Environment.from_string()`, or equivalent methods in other template engines (Twig's `createTemplate()`, Freemarker's `new Template()`, etc.).

Static analysis tools like Semgrep have rules for SSTI patterns in Flask and Django applications.

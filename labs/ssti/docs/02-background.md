# Background

## Template Engines

A template engine takes a string with placeholders and fills them in with data. Flask uses Jinja2 by default. The safe way to pass user data into a template is to render a fixed template string and pass user data as a variable:

```python
render_template_string("Hello, {{ name }}!", name=user_input)
```

Here `name` is a variable reference, not an expression. Jinja2 HTML-escapes it and never evaluates it as code.

The unsafe pattern passes user input as part of the template string itself:

```python
render_template_string(f"Hello, {user_input}!")
```

If `user_input` is `{{ 7*7 }}`, Jinja2 evaluates the expression and returns `Hello, 49!`. The user just ran code on the server.

## Python Object Hierarchy

Every Python object carries a chain of references to its class and that class's ancestors. From a string:

- `''.__class__` is `<class 'str'>`
- `''.__class__.__mro__` is the method resolution order: `[str, object]`
- `''.__class__.__mro__[1]` is `object`
- `object.__subclasses__()` returns every class that inherits from `object`, which is effectively every class in the Python runtime

`subprocess.Popen` is always in that list. Once you have the index, you can call it with any shell command.

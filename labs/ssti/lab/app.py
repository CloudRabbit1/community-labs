#!/usr/bin/env python3
"""
Server-Side Template Injection (SSTI) lab.

A Flask-style blog app renders user input directly into a Jinja2 template
string without sandboxing. The name parameter lands inside {{ }} evaluation,
giving an attacker access to Python's object hierarchy and ultimately arbitrary
command execution.

The simulation applies Jinja2 evaluation rules manually so no external
dependencies are needed.
"""
import json
import os
import re
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer

SUBCLASSES = [
    "<class 'type'>",
    "<class 'weakref'>",
    "<class 'weakcallableproxy'>",
    "<class 'weakproxy'>",
    "<class 'int'>",
    "<class 'bytearray'>",
    "<class 'bytes'>",
    "<class 'list'>",
    "<class 'NoneType'>",
    "<class 'NotImplementedType'>",
    "<class 'traceback'>",
    "<class 'super'>",
    "<class 'range'>",
    "<class 'dict'>",
    "<class 'dict_keys'>",
    "<class 'dict_values'>",
    "<class 'dict_items'>",
    "<class 'dict_reversekeyiterator'>",
    "<class 'odict_iterator'>",
    "<class 'set'>",
    "<class 'str'>",
    "<class 'slice'>",
    "<class 'staticmethod'>",
    "<class 'complex'>",
    "<class 'float'>",
    "<class 'frozenset'>",
    "<class 'property'>",
    "<class 'managedbuffer'>",
    "<class 'memoryview'>",
    "<class 'tuple'>",
    "<class 'enumerate'>",
    "<class 'reversed'>",
    "<class 'stderrprinter'>",
    "<class 'code'>",
    "<class 'frame'>",
    "<class 'builtin_function_or_method'>",
    "<class 'method'>",
    "<class 'function'>",
    "<class 'mappingproxy'>",
    "<class 'generator'>",
    "<class 'getset_descriptor'>",
    "<class 'wrapper_descriptor'>",
    "<class 'method-wrapper'>",
    "<class 'ellipsis'>",
    "<class 'member_descriptor'>",
    "<class 'types.SimpleNamespace'>",
    "<class 'PyCapsule'>",
    "<class 'longrange_iterator'>",
    "<class 'cell'>",
    "<class 'instancemethod'>",
    "<class 'classmethod_descriptor'>",
    "<class 'method_descriptor'>",
    "<class 'callable_iterator'>",
    "<class 'iterator'>",
    "<class 'coroutine'>",
    "<class 'coroutine_wrapper'>",
    "<class 'InterpreterID'>",
    "<class 'warnings.WarningMessage'>",
    "<class 'warnings.catch_warnings'>",
    "<class '_weakrefset._IterationGuard'>",
    "<class '_weakrefset.WeakSet'>",
    "<class 'os._Environ'>",
    "<class 'os.stat_result'>",
    "<class 'os.statvfs_result'>",
    "<class 'os.DirEntry'>",
    "<class 'os.terminal_size'>",
    "<class 'posix.SchedParam'>",
    "<class 'os.times_result'>",
    "<class 'os.uname_result'>",
    "<class 'os.uname_result'>",
    "<class 'os.confstr_error'>",
    "<class '_io._IOBase'>",
    "<class '_io._RawIOBase'>",
    "<class '_io.FileIO'>",
    "<class '_io._BufferedIOBase'>",
    "<class '_io.BufferedReader'>",
    "<class '_io.BufferedWriter'>",
    "<class '_io.BufferedRWPair'>",
    "<class '_io.BufferedRandom'>",
    "<class '_io.IncrementalNewlineDecoder'>",
    "<class '_io._TextIOBase'>",
    "<class '_io.TextIOWrapper'>",
    "<class '_io.StringIO'>",
    "<class '_io.BytesIO'>",
    "<class 'subprocess.CompletedProcess'>",
    "<class 'subprocess.Popen'>",
]


def render_template(name: str) -> str:
    """Apply Jinja2-style evaluation to the name parameter."""
    # Arithmetic expressions
    if name == "{{7*7}}":
        return "49"
    if name == "{{7*'7'}}":
        return "7777777"
    if name in ("{{''.class}}", "{{''.__class__}}", "{{''.__class__.__name__}}"):
        return "<class 'str'>"

    low = name.lower()

    # RCE via os/subprocess: check before subclass enumeration so a full
    # exploit payload (which contains both __subclasses__ and communicate)
    # is handled here rather than stopped at the enumeration branch
    if any(k in low for k in ("os.popen", "popen", "subprocess", "communicate", "read()")):
        if any(k in low for k in ("flag", "cat", "flag.txt")):
            return open("/flag.txt").read().strip()
        # Generic command execution probe without flag target
        return "uid=33(www-data) gid=33(www-data) groups=33(www-data)"

    # Class enumeration via __subclasses__
    if "__subclasses__" in name:
        return "[" + ", ".join(SUBCLASSES) + "]"

    # Config disclosure
    if "config" in low:
        return "{'SECRET_KEY': 'dev-secret-do-not-use', 'DEBUG': True, 'DATABASE_URI': 'sqlite:///blog.db'}"

    # Jinja2 expression syntax present but no known payload: reflect as-is to show eval
    if "{{" in name and "}}" in name:
        return name  # unrecognised expression, reflect unevaluated

    return f"Hello, {name}!"


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def send_json(self, code: int, data: dict):
        b = json.dumps(data, indent=2).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def body(self) -> str:
        n = int(self.headers.get("Content-Length", 0))
        return self.rfile.read(n).decode(errors="replace") if n else ""

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        qs = urllib.parse.parse_qs(parsed.query)

        if path == "/":
            self.send_json(200, {
                "app": "Flask Blog v1.0 (dev)",
                "note": "SSTI: user input is rendered directly into template strings",
                "endpoints": [
                    "GET  /render?name=<input>",
                    "POST /render  {\"name\": \"<input>\"}",
                ],
            })
            return

        if path == "/render":
            name = qs.get("name", ["World"])[0]
            result = render_template(name)
            self.send_json(200, {"output": result})
            return

        self.send_json(404, {"error": "Not found"})

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/render":
            try:
                data = json.loads(self.body())
            except Exception:
                self.send_json(400, {"error": "Invalid JSON"})
                return
            name = data.get("name", "World")
            result = render_template(name)
            self.send_json(200, {"output": result})
            return

        self.send_json(404, {"error": "Not found"})


if __name__ == "__main__":
    HTTPServer(("0.0.0.0", 8080), Handler).serve_forever()

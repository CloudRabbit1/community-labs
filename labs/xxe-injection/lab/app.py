#!/usr/bin/env python3
"""
XXE Injection lab: a document upload endpoint parses user-supplied XML with
external entity expansion enabled. Injecting a DOCTYPE that declares a file
entity causes the parser to include the contents of /flag.txt in the response.

POST /upload  Content-Type: application/xml  <data><item>...</item></data>
GET  /        service info
"""
import json
import re
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
from xml.etree import ElementTree as ET

ENTITY_RE = re.compile(
    r'<!ENTITY\s+(\w+)\s+SYSTEM\s+"file://([^"]+)"', re.IGNORECASE
)


def strip_doctype(xml_str: str) -> str:
    """Remove DOCTYPE declaration including optional internal subset."""
    idx = xml_str.find("<!DOCTYPE")
    if idx < 0:
        return xml_str
    depth = 0
    i = idx + 9
    while i < len(xml_str):
        c = xml_str[i]
        if c == "[":
            depth += 1
        elif c == "]":
            depth -= 1
        elif c == ">" and depth <= 0:
            return xml_str[:idx] + xml_str[i + 1:]
        i += 1
    return xml_str


def process_xml(body: str) -> dict:
    entities = {}
    for name, path in ENTITY_RE.findall(body):
        try:
            entities[name] = open(path).read()
        except Exception as e:
            entities[name] = f"[error: {e}]"

    # Substitute entity references before stripping DOCTYPE
    for ename, evalue in entities.items():
        body = body.replace(f"&{ename};", evalue)

    stripped = strip_doctype(body)

    root = ET.fromstring(stripped)
    items = [el.text or "" for el in root.iter("item")]
    return {"parsed": True, "items": items}


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

    def body_bytes(self) -> bytes:
        n = int(self.headers.get("Content-Length", 0))
        return self.rfile.read(n) if n else b""

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/":
            self.send_json(200, {
                "service": "Document Processor v1.0",
                "endpoint": "POST /upload  (application/xml)",
                "example": "<data><item>hello</item></data>",
            })
        else:
            self.send_json(404, {"error": "not found"})

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path != "/upload":
            self.send_json(404, {"error": "not found"})
            return

        body = self.body_bytes()
        if not body:
            self.send_json(400, {"error": "empty body"})
            return

        try:
            result = process_xml(body.decode(errors="replace"))
            self.send_json(200, result)
        except Exception as e:
            self.send_json(400, {"error": f"XML parse error: {e}"})


if __name__ == "__main__":
    HTTPServer(("0.0.0.0", 8080), Handler).serve_forever()

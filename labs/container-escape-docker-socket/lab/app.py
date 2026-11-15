#!/usr/bin/env python3
"""
Container escape lab: SSRF to Docker socket.

The monitoring app exposes /fetch (SSRF). The Docker socket API runs on
the same host at port 2376 (internal). The flag lives on the simulated
host filesystem — only readable from a privileged container with the
host root bind-mounted.

Exploit chain:
  /fetch -> docker:2376/containers/create (privileged, Binds: /:/host-root)
  /fetch -> docker:2376/containers/{id}/exec  (Cmd: cat /host-root/flag.txt)
  /fetch -> docker:2376/exec/{id}/start
"""
import json
import os
import threading
import urllib.parse
import urllib.request
import urllib.error
from http.server import HTTPServer, BaseHTTPRequestHandler

# ------------------------------------------------------------------ state
CONTAINERS = {}
EXECS = {}
_cid = [0]
_eid = [0]


def next_cid():
    _cid[0] += 1
    return f"c{_cid[0]:08x}"


def next_eid():
    _eid[0] += 1
    return f"e{_eid[0]:08x}"


# ------------------------------------------------------------------ Docker daemon (port 2376)
class DockerHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def send_json(self, code, data):
        body = json.dumps(data).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)

    def send_text(self, code, text):
        body = text.encode()
        self.send_response(code)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)

    def body(self):
        n = int(self.headers.get("Content-Length", 0))
        return json.loads(self.rfile.read(n)) if n else {}

    def do_GET(self):
        if self.path == "/_ping":
            self.send_text(200, "OK")
        elif self.path in ("/info", "/v1.41/info"):
            self.send_json(200, {
                "ID": "sim:docker:daemon",
                "ServerVersion": "24.0.5",
                "Containers": len(CONTAINERS),
                "OperatingSystem": "Linux",
            })
        elif self.path in ("/containers/json", "/v1.41/containers/json"):
            cs = []
            for cid, c in CONTAINERS.items():
                cs.append({"Id": cid, "Image": c["image"],
                            "State": "running", "Names": [f"/{cid[:8]}"]})
            self.send_json(200, cs)
        else:
            self.send_json(404, {"message": "page not found"})

    def do_POST(self):
        data = self.body()
        # Normalize: strip query string, strip optional /v1.xx version prefix
        raw = self.path.split("?")[0]
        import re
        path = re.sub(r"^/v\d+\.\d+", "", raw)  # /v1.41/containers/... -> /containers/...

        if path == "/containers/create":
            cid = next_cid()
            hc = data.get("HostConfig", {})
            CONTAINERS[cid] = {
                "image": data.get("Image", "unknown"),
                "privileged": hc.get("Privileged", False),
                "binds": hc.get("Binds", []),
            }
            self.send_json(201, {"Id": cid, "Warnings": []})

        elif re.match(r"^/containers/[^/]+/exec$", path):
            cid = path.split("/")[2]
            if cid not in CONTAINERS:
                self.send_json(404, {"message": f"No such container: {cid}"})
                return
            c = CONTAINERS[cid]
            eid = next_eid()
            EXECS[eid] = {
                "cmd": data.get("Cmd", []),
                "privileged": c["privileged"],
                "binds": c["binds"],
            }
            self.send_json(201, {"Id": eid})

        elif re.match(r"^/exec/[^/]+/start$", path):
            eid = path.split("/")[2]
            if eid not in EXECS:
                self.send_json(404, {"message": f"No such exec: {eid}"})
                return
            ex = EXECS[eid]
            output = _run(ex["cmd"], ex["privileged"], ex["binds"])
            self.send_text(200, output)

        else:
            self.send_json(404, {"message": "page not found"})


def _run(cmd, privileged, binds):
    flag = open("/flag.txt").read().strip()
    host_root = any("/host-root" in b or ":/root" in b for b in binds)
    can_read_host = privileged and host_root
    cmd_str = " ".join(cmd)

    if "cat" in cmd_str and "flag" in cmd_str:
        return (flag + "\n") if can_read_host else "cat: permission denied\n"
    if "ls" in cmd_str and "host-root" in cmd_str:
        return "flag.txt\netc\nhome\n" if can_read_host else "ls: permission denied\n"
    if cmd_str.strip() == "id":
        return "uid=0(root) gid=0(root)\n"
    if "whoami" in cmd_str:
        return "root\n"
    return f"# {cmd_str}\n"


# ------------------------------------------------------------------ Web app (port 8080)
class AppHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def send_json(self, code, data):
        body = json.dumps(data).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)

    def send_text(self, code, text):
        body = text.encode()
        self.send_response(code)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)

    def body(self):
        n = int(self.headers.get("Content-Length", 0))
        return json.loads(self.rfile.read(n)) if n else {}

    def do_GET(self):
        if self.path == "/":
            self.send_text(200, (
                "Internal monitoring service v1.0\n"
                "POST /fetch  {url, method?, body?}  — fetch a URL\n"
                "GET  /health                        — service health\n"
            ))
        elif self.path == "/health":
            self.send_json(200, {"status": "ok"})
        else:
            self.send_text(404, "Not found\n")

    def do_POST(self):
        if self.path != "/fetch":
            self.send_text(404, "Not found\n")
            return

        data = self.body()
        url = data.get("url", "")
        method = data.get("method", "GET").upper()
        req_body = data.get("body")

        if not url:
            self.send_json(400, {"error": "url is required"})
            return

        body_bytes = None
        if req_body is not None:
            body_bytes = json.dumps(req_body).encode()

        try:
            req = urllib.request.Request(url, data=body_bytes, method=method)
            if body_bytes:
                req.add_header("Content-Type", "application/json")
                req.add_header("Content-Length", str(len(body_bytes)))
            with urllib.request.urlopen(req, timeout=5) as r:
                resp_body = r.read().decode(errors="replace")
                ct = r.headers.get("Content-Type", "text/plain")
            self.send_json(200, {"status": r.status, "content_type": ct, "body": resp_body})
        except urllib.error.HTTPError as e:
            self.send_json(200, {"status": e.code,
                                 "content_type": "text/plain",
                                 "body": e.read().decode(errors="replace")})
        except Exception as e:
            self.send_json(500, {"error": str(e)})


if __name__ == "__main__":
    docker_srv = HTTPServer(("127.0.0.1", 2376), DockerHandler)
    t = threading.Thread(target=docker_srv.serve_forever, daemon=True)
    t.start()
    HTTPServer(("0.0.0.0", 8080), AppHandler).serve_forever()

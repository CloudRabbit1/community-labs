#!/usr/bin/env python3
"""
Monitoring Evasion lab — ETW function-pointer patching simulation.

An application runs with an in-process monitoring agent. The agent uses a
function-pointer table (analogous to Windows ETW's EventWrite) to log every
command execution to an audit trail.

The diagnostic API left enabled in this build lets callers overwrite the
function pointer at a named address. Patching the pointer to a no-op disables
logging without stopping the process — commands run silently.

Exploit chain:
  1. Read the function-pointer table to find the logging hook address.
  2. PATCH that address to point to the no-op stub.
  3. POST /exec — command runs but is not logged.
  4. GET /flag — issued only if the last exec left no audit entry.
"""
import json
import hashlib
import os
from http.server import HTTPServer, BaseHTTPRequestHandler

# Simulate ETW function-pointer table
FUNC_TABLE = {
    "EventWrite":    "0xfffff800_etw_hook",    # real logging hook
    "EventWriteNop": "0xfffff800_nop_stub",    # no-op replacement
}

STATE = {
    "log_ptr": "EventWrite",          # currently active pointer
    "audit_log": [],                  # entries appended by EventWrite
    "last_exec_logged": None,         # True/False/None
}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def send_json(self, code, data):
        b = json.dumps(data).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(b))
        self.end_headers()
        self.wfile.write(b)

    def body(self):
        n = int(self.headers.get("Content-Length", 0))
        return json.loads(self.rfile.read(n)) if n else {}

    def do_GET(self):
        if self.path == "/":
            self.send_json(200, {
                "service": "Internal command runner with ETW monitoring",
                "monitoring": "ENABLED" if STATE["log_ptr"] == "EventWrite" else "PATCHED",
                "endpoints": [
                    "GET  /monitoring/status",
                    "GET  /monitoring/func-table",
                    "POST /monitoring/patch  {symbol, target}",
                    "POST /exec              {cmd}",
                    "GET  /audit-log",
                    "GET  /flag",
                ],
            })
        elif self.path == "/monitoring/status":
            self.send_json(200, {
                "log_ptr": STATE["log_ptr"],
                "address": FUNC_TABLE[STATE["log_ptr"]],
                "monitoring_active": STATE["log_ptr"] == "EventWrite",
                "audit_entries": len(STATE["audit_log"]),
            })
        elif self.path == "/monitoring/func-table":
            self.send_json(200, {
                "FunctionPointerTable": FUNC_TABLE,
                "current_hook": STATE["log_ptr"],
                "note": "EventWriteNop is a no-op stub — patching to it disables logging",
            })
        elif self.path == "/audit-log":
            self.send_json(200, {
                "entries": STATE["audit_log"],
                "count": len(STATE["audit_log"]),
            })
        elif self.path == "/flag":
            if STATE["last_exec_logged"] is None:
                self.send_json(403, {"error": "No command executed yet", "hint": "POST /exec first"})
                return
            if STATE["last_exec_logged"]:
                self.send_json(403, {
                    "error": "Command was logged — monitoring still active",
                    "hint": "Patch the EventWrite pointer to EventWriteNop first",
                    "audit_entries": len(STATE["audit_log"]),
                })
                return
            flag = open("/flag.txt").read().strip()
            self.send_json(200, {
                "flag": flag,
                "note": "Command executed with no audit entry — monitoring successfully evaded",
            })
        else:
            self.send_json(404, {"error": "Not found"})

    def do_POST(self):
        data = self.body()

        if self.path == "/monitoring/patch":
            symbol = data.get("symbol", "")
            target = data.get("target", "")
            if symbol not in FUNC_TABLE or target not in FUNC_TABLE:
                self.send_json(400, {
                    "error": f"Unknown symbol or target",
                    "valid_symbols": list(FUNC_TABLE.keys()),
                })
                return
            if symbol != "EventWrite":
                self.send_json(400, {"error": "Only EventWrite can be patched"})
                return
            old = STATE["log_ptr"]
            STATE["log_ptr"] = target
            self.send_json(200, {
                "patched": symbol,
                "old_target": FUNC_TABLE[old],
                "new_target": FUNC_TABLE[target],
                "monitoring_active": STATE["log_ptr"] == "EventWrite",
            })

        elif self.path == "/exec":
            cmd = data.get("cmd", "")
            if not cmd:
                self.send_json(400, {"error": "cmd required"})
                return
            logged = STATE["log_ptr"] == "EventWrite"
            if logged:
                STATE["audit_log"].append({
                    "cmd": cmd,
                    "EventWrite": FUNC_TABLE["EventWrite"],
                })
            STATE["last_exec_logged"] = logged
            self.send_json(200, {
                "executed": cmd,
                "logged": logged,
                "log_ptr": STATE["log_ptr"],
                "note": "No audit entry created" if not logged else "Audit entry appended",
            })

        else:
            self.send_json(404, {"error": "Not found"})


if __name__ == "__main__":
    HTTPServer(("0.0.0.0", 8080), Handler).serve_forever()

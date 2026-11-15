#!/usr/bin/env python3
"""
Race condition on a bank transfer endpoint.

The /transfer endpoint checks the balance, then sleeps 50ms, then deducts.
No locking between the check and the deduct means concurrent requests can
each pass the check before any deduction runs. When the balance drops below
-50 the flag is revealed.
"""
import json
import os
import time
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer, ThreadingHTTPServer

STATE = {"balance": 10}
FLAG_REVEALED = False


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

    def do_GET(self):
        global FLAG_REVEALED
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        params = urllib.parse.parse_qs(parsed.query)

        if path == "/":
            self.send_json(200, {
                "service": "BankSim v1.0",
                "endpoints": [
                    "GET  /balance",
                    "POST /deposit?amount=<n>",
                    "POST /transfer?amount=<n>",
                ],
            })
            return

        if path == "/balance":
            resp = {"balance": STATE["balance"]}
            if FLAG_REVEALED or STATE["balance"] < -50:
                FLAG_REVEALED = True
                resp["flag"] = open("/flag.txt").read().strip()
            self.send_json(200, resp)
            return

        self.send_json(404, {"error": "Not found"})

    def do_POST(self):
        global FLAG_REVEALED
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        params = urllib.parse.parse_qs(parsed.query)

        if path == "/deposit":
            try:
                amount = int(params.get("amount", ["0"])[0])
            except ValueError:
                self.send_json(400, {"error": "invalid amount"})
                return
            if amount <= 0:
                self.send_json(400, {"error": "amount must be positive"})
                return
            STATE["balance"] += amount
            self.send_json(200, {"balance": STATE["balance"]})
            return

        if path == "/transfer":
            try:
                amount = int(params.get("amount", ["0"])[0])
            except ValueError:
                self.send_json(400, {"error": "invalid amount"})
                return
            if amount <= 0:
                self.send_json(400, {"error": "amount must be positive"})
                return

            # VULNERABLE: check then sleep then deduct — no lock
            current = STATE["balance"]
            if current < amount:
                self.send_json(400, {"error": "insufficient funds", "balance": current})
                return

            time.sleep(0.5)  # 500ms window for concurrent requests to race through check

            STATE["balance"] -= amount
            resp = {"transferred": amount, "balance": STATE["balance"]}
            if FLAG_REVEALED or STATE["balance"] < -50:
                FLAG_REVEALED = True
                resp["flag"] = open("/flag.txt").read().strip()
            self.send_json(200, resp)
            return

        self.send_json(404, {"error": "Not found"})


if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", 8080), Handler).serve_forever()

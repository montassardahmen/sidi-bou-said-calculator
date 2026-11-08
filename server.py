"""Tiny dependency-free web server for the Sidi Bou Said calculator.

    python server.py            # http://127.0.0.1:8000
    python server.py 5000       # custom port

Serves the front end from ./static and exposes one JSON endpoint:

    POST /api/calculate   {"expression": "2+3*4"}  ->  {"result": "14"}
"""

from __future__ import annotations

import json
import os
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from calculator import CalculatorError, calculate

STATIC_DIR = Path(__file__).resolve().parent / "static"
MAX_BODY_BYTES = 4096


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(STATIC_DIR), **kwargs)

    def end_headers(self):
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def _send_json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        if self.path != "/api/calculate":
            return self._send_json(404, {"error": "Not found"})

        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            length = -1
        if length <= 0 or length > MAX_BODY_BYTES:
            return self._send_json(400, {"error": "Bad request body"})

        try:
            payload = json.loads(self.rfile.read(length))
            expression = payload["expression"]
        except (ValueError, KeyError, TypeError):
            return self._send_json(
                400, {"error": 'Send JSON like {"expression": "2+2"}'}
            )

        try:
            result = calculate(expression)
        except CalculatorError as exc:
            return self._send_json(422, {"error": str(exc)})
        self._send_json(200, {"result": result})


def main() -> None:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else int(os.environ.get("PORT", 8000))
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"Aslema! The souk is open at http://127.0.0.1:{port}  (Ctrl+C to close)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nSaha! Souk closed.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()

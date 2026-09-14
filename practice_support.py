"""Deterministic, offline HTTP fixtures for the local API lessons."""
from contextlib import contextmanager
from copy import deepcopy
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import threading
from urllib.parse import parse_qs, urlsplit


@contextmanager
def local_api(items):
    """Yield a loopback URL; GET /items and POST /echo use real HTTP sockets."""
    records = deepcopy(items)

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def reply(self, status, value):
            body = json.dumps(value, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            parts = urlsplit(self.path)
            if parts.path != "/items":
                self.reply(404, {"error": "not_found"})
                return
            query = parse_qs(parts.query, keep_blank_values=True)
            term = query.get("q", [""])[0].casefold()
            try:
                limit = int(query.get("limit", ["100"])[0])
                if not 0 <= limit <= 100:
                    raise ValueError()
            except ValueError:
                self.reply(400, {"error": "invalid_limit"})
                return
            selected = [item for item in records if term in item["name"].casefold()]
            self.reply(200, {"items": selected[:limit], "total": len(selected)})

        def do_POST(self):
            if urlsplit(self.path).path != "/echo":
                self.reply(404, {"error": "not_found"})
                return
            if self.headers.get_content_type() != "application/json":
                self.reply(415, {"error": "json_required"})
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if not 0 < length <= 128 * 1024:
                    raise ValueError()
                value = json.loads(self.rfile.read(length).decode("utf-8"))
            except (ValueError, UnicodeError):
                self.reply(400, {"error": "invalid_json"})
                return
            self.reply(200, {"received": value})

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    server.daemon_threads = True
    thread = threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.01}, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

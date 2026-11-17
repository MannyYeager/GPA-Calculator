"""Small loopback-only HTTP shell for this project's browser interface."""
import json
import secrets
import threading
import time
from http.cookies import CookieError, SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit


class LocalServer(ThreadingHTTPServer):
    def __init__(self, address, static_dir, cookie_name, session_factory):
        super().__init__(address, Handler)
        self.static_dir = Path(static_dir)
        self.cookie_name = cookie_name
        self.session_factory = session_factory
        self.sessions = {}
        self.lock = threading.RLock()


class Handler(BaseHTTPRequestHandler):
    def setup(self):
        super().setup()
        self.connection.settimeout(10)

    def reply(self, status, body, mime="application/json; charset=utf-8", cookie=None, download=None):
        if isinstance(body, dict):
            body = json.dumps(body, ensure_ascii=False, allow_nan=False)
        if isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'self'; style-src 'self'; script-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'")
        if cookie:
            self.send_header("Set-Cookie", cookie)
        if download:
            self.send_header("Content-Disposition", f'attachment; filename="{download}"')
        self.end_headers()
        self.wfile.write(body)

    def valid_host(self):
        return self.headers.get("Host") in {
            f"localhost:{self.server.server_port}", f"127.0.0.1:{self.server.server_port}"
        }

    def session(self):
        now = time.time()
        self.server.sessions = {key: value for key, value in self.server.sessions.items() if value[1] > now}
        cookies = SimpleCookie()
        try:
            cookies.load(self.headers.get("Cookie", ""))
        except CookieError:
            pass
        item = cookies.get(self.server.cookie_name)
        token = item.value if item else None
        if token in self.server.sessions:
            return self.server.sessions[token][0], None
        if len(self.server.sessions) >= 256:
            raise ValueError("Too many local demo sessions. Restart the app to reset them.")
        token = secrets.token_urlsafe(32)
        data = self.server.session_factory()
        self.server.sessions[token] = (data, now + 28800)
        return data, f"{self.server.cookie_name}={token}; HttpOnly; SameSite=Strict; Path=/; Max-Age=28800"

    def do_GET(self):
        with self.server.lock:
            if not self.valid_host():
                self.reply(403, {"error": "Use the local app address."})
                return
            path = urlsplit(self.path).path
            try:
                if path in {"/", "/app.js", "/style.css", "/ui.js", "/ui.css", "/theme.css", "/workspace.css", "/vendor/anime.umd.min.js"}:
                    name, mime = {"/": ("index.html", "text/html"), "/app.js": ("app.js", "text/javascript"),
                                  "/style.css": ("style.css", "text/css"), "/ui.js": ("ui.js", "text/javascript"),
                                  "/ui.css": ("ui.css", "text/css"), "/theme.css": ("theme.css", "text/css"), "/workspace.css": ("workspace.css", "text/css"),
                                  "/vendor/anime.umd.min.js": ("vendor/anime.umd.min.js", "text/javascript")}[path]
                    self.reply(200, (self.server.static_dir / name).read_bytes(), mime + "; charset=utf-8")
                elif path in {"/api/state", "/api/export"}:
                    data, cookie = self.session()
                    if path == "/api/export" and hasattr(self.server, "export"):
                        body, name = self.server.export(data)
                        self.reply(200, body, "text/csv; charset=utf-8", cookie, name)
                    elif path == "/api/state":
                        self.reply(200, self.server.snapshot(data), cookie=cookie)
                    else:
                        self.reply(404, {"error": "Page not found."})
                else:
                    self.reply(404, {"error": "Page not found."})
            except ValueError as error:
                self.reply(400, {"error": str(error)})
            except (OSError, RuntimeError):
                self.reply(500, {"error": "The local app could not complete this request. Check its terminal."})

    def do_POST(self):
        with self.server.lock:
            if not self.valid_host() or self.headers.get("Origin") not in {
                f"http://localhost:{self.server.server_port}", f"http://127.0.0.1:{self.server.server_port}"
            }:
                self.reply(403, {"error": "Request origin rejected. Open the app at its local address."})
                return
            try:
                size = int(self.headers.get("Content-Length", "0"))
                if not 0 < size <= 65536 or self.headers.get_content_type() != "application/json":
                    raise ValueError("Send a JSON form under 64 KB.")
                payload = json.loads(self.rfile.read(size))
                if not isinstance(payload, dict):
                    raise ValueError("Send a form object.")
                data, cookie = self.session()
                message = self.server.action(urlsplit(self.path).path, payload, data)
                self.reply(200, {"message": message, "state": self.server.snapshot(data)}, cookie=cookie)
            except (ValueError, UnicodeError) as error:
                self.reply(400, {"error": str(error)})
            except (OSError, RuntimeError):
                self.reply(500, {"error": "The local app could not complete this request. Check its terminal."})

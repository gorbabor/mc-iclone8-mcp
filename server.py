import hmac
import json
import os
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

# Optional shared secret. When MC_ICLONE8_MCP_TOKEN is set in the environment,
# every /mcp POST must present it via "X-MCP-Token: <token>" or
# "Authorization: Bearer <token>". Unset (default) keeps local CLI clients
# working with no configuration.
_TOKEN_ENV = "MC_ICLONE8_MCP_TOKEN"

# Loopback hosts allowed to originate browser requests. Requests with no Origin
# header (native/CLI MCP clients such as Claude Code and curl) are always
# allowed; a cross-site page in the user's browser carries a non-loopback
# Origin and is rejected, closing the DNS-rebind / CSRF hole.
_LOOPBACK_HOSTS = ("localhost", "127.0.0.1", "::1")


def _origin_allowed(origin):
    if not origin:
        return True
    try:
        return urlparse(origin).hostname in _LOOPBACK_HOSTS
    except Exception:
        return False


class _RequestHandler(BaseHTTPRequestHandler):
    server_version = "mc-iclone8-mcp/0.1"

    def log_message(self, *_args):
        return

    def _cors(self, origin=None):
        # Reflect only an allowed loopback origin instead of a wildcard.
        allow = origin if (origin and _origin_allowed(origin)) else "http://127.0.0.1"
        self.send_header("Access-Control-Allow-Origin", allow)
        self.send_header("Vary", "Origin")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Accept, Mcp-Session-Id, X-MCP-Token, Authorization")

    def _authorized(self):
        token = os.environ.get(_TOKEN_ENV)
        if not token:
            return True
        provided = self.headers.get("X-MCP-Token")
        if provided is None:
            auth = self.headers.get("Authorization", "")
            if auth.startswith("Bearer "):
                provided = auth[7:]
        return provided is not None and hmac.compare_digest(provided, token)

    def do_OPTIONS(self):
        self.send_response(200)
        self._cors(self.headers.get("Origin"))
        self.end_headers()

    def do_GET(self):
        if self.path == "/health":
            payload = {"status": "ok", "server": "mc-iclone8-mcp", "api": "iClone 8 RLPy"}
            self.send_response(200)
            self._cors(self.headers.get("Origin"))
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(payload).encode("utf-8"))
            return
        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        if self.path != "/mcp":
            self.send_response(404)
            self.end_headers()
            return
        origin = self.headers.get("Origin")
        if not _origin_allowed(origin):
            self.send_response(403)
            self.end_headers()
            return
        if not self._authorized():
            self.send_response(401)
            self.end_headers()
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            body = self.rfile.read(length).decode("utf-8")
            result = self.server.mcp_handler(body)
            self.send_response(200)
            self._cors(origin)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(result.encode("utf-8"))
        except (ConnectionResetError, BrokenPipeError, OSError):
            return


class MCPServer:
    def __init__(self, handler, host="127.0.0.1", port=8766):
        self.handler = handler
        self.host = host
        self.port = port
        self.httpd = None
        self.thread = None
        self.running = False

    def start(self):
        if self.running and self.httpd:
            return "http://%s:%d/mcp" % (self.host, self.port)
        ThreadingHTTPServer.allow_reuse_address = True
        ThreadingHTTPServer.daemon_threads = True
        if hasattr(ThreadingHTTPServer, "block_on_close"):
            ThreadingHTTPServer.block_on_close = False
        self.httpd = ThreadingHTTPServer((self.host, self.port), _RequestHandler)
        self.httpd.mcp_handler = self.handler
        self.running = True
        self.thread = threading.Thread(target=self.httpd.serve_forever, name="mc-iclone8-mcp", daemon=True)
        self.thread.start()
        return "http://%s:%d/mcp" % (self.host, self.port)

    def stop(self):
        httpd, thread = self.httpd, self.thread
        self.running = False
        self.httpd = None
        self.thread = None
        if httpd:
            try:
                httpd.shutdown()
            finally:
                httpd.server_close()
        if thread and thread is not threading.current_thread():
            thread.join(timeout=2)

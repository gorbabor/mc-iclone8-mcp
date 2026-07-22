import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class _RequestHandler(BaseHTTPRequestHandler):
    server_version = "mc-iclone8-mcp/0.1"

    def log_message(self, *_args):
        return

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Accept, Mcp-Session-Id")

    def do_OPTIONS(self):
        self.send_response(200)
        self._cors()
        self.end_headers()

    def do_GET(self):
        if self.path == "/health":
            payload = {"status": "ok", "server": "mc-iclone8-mcp", "api": "iClone 8 RLPy"}
            self.send_response(200)
            self._cors()
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
        try:
            length = int(self.headers.get("Content-Length", "0"))
            body = self.rfile.read(length).decode("utf-8")
            result = self.server.mcp_handler(body)
            self.send_response(200)
            self._cors()
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

import http.server
import socket
import socketserver
import os
import json
import mimetypes
import hashlib
import urllib.parse
from pathlib import Path

import helpers
import templates


class Handler(http.server.BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        # suppress default logging
        pass

    def _log_access(self, method, path, status=200):
        if path in ("/api/status",):
            return
        ip = self.client_address[0]
        ua = self.headers.get("User-Agent", "")
        device, browser = helpers.parse_user_agent(ua)
        if status >= 500:
            level = "error"
        elif status >= 400:
            level = "warn"
        elif path == "/api/upload" or method == "POST":
            level = "success"
        elif path.startswith("/files/") or path.startswith("/view/"):
            level = "info"
        else:
            level = "muted"
        short_path = path if len(path) <= 40 else path[:38] + "…"
        msg = f"{device}  {browser}  ·  {ip}  ·  {method} {short_path}  [{status}]"
        helpers.log_queue.append((level, msg))

    def do_GET(self):
        path = urllib.parse.unquote(self.path)

        if path not in ("/api/status",):
            helpers.record_peer(self.client_address[0], self.headers.get("User-Agent", ""))

        if path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(templates.render_page().encode())
            self._log_access("GET", path, 200)
            return

        if path == "/simple":
            try:
                files = sorted(f for f in os.listdir(os.getcwd())
                               if os.path.isfile(os.path.join(os.getcwd(), f)))
            except Exception:
                files = []
            html = templates.render_simple_page(files)
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(html.encode())
            self._log_access("GET", path, 200)
            return

        if path == "/api/status":
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            try:
                s.connect(("8.8.8.8", 80))
                ip = s.getsockname()[0]
            except Exception:
                ip = "127.0.0.1"
            finally:
                s.close()
            port = int(self.server.server_address[1])
            payload = json.dumps({"status": "live", "url": f"http://{ip}:{port}"})
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(payload.encode())
            return

        if path == "/api/peers":
            with helpers._lock:
                peers_list = list(helpers.connected_peers.values())
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(peers_list).encode())
            return

        if path.startswith("/api/checksum/"):
            filename = urllib.parse.unquote(path[14:])
            filepath = os.path.join(os.getcwd(), filename)
            if os.path.isfile(filepath):
                try:
                    sha = hashlib.sha256()
                    with open(filepath, "rb") as f:
                        for chunk in iter(lambda: f.read(65536), b""):
                            sha.update(chunk)
                    result = json.dumps({"file": filename, "sha256": sha.hexdigest()})
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(result.encode())
                    self._log_access("GET", path, 200)
                except Exception as e:
                    helpers.log_queue.append(("error", f"Checksum error: {e}"))
                    self.send_response(500)
                    self.end_headers()
            else:
                self.send_response(404)
                self.end_headers()
                self._log_access("GET", path, 404)
            return

        if path.startswith("/files/"):
            filename = urllib.parse.unquote(path[7:])
            filepath = os.path.join(os.getcwd(), filename)
            if os.path.isfile(filepath):
                with open(filepath, "rb") as f:
                    data = f.read()
                mime = mimetypes.guess_type(filename)[0] or "application/octet-stream"
                self.send_response(200)
                self.send_header("Content-Type", mime)
                self.send_header("Content-Disposition", f'attachment; filename="{filename}"')
                self.end_headers()
                self.wfile.write(data)
                self._log_access("GET", path, 200)
            else:
                self.send_response(404)
                self.end_headers()
                self._log_access("GET", path, 404)
            return

        if path.startswith("/view/"):
            filename = urllib.parse.unquote(path[6:])
            filepath = os.path.join(os.getcwd(), filename)
            if os.path.isfile(filepath):
                mime = mimetypes.guess_type(filename)[0] or "application/octet-stream"
                with open(filepath, "rb") as f:
                    data = f.read()
                self.send_response(200)
                self.send_header("Content-Type", mime)
                self.end_headers()
                self.wfile.write(data)
                self._log_access("GET", path, 200)
            else:
                self.send_response(404)
                self.end_headers()
                self._log_access("GET", path, 404)
            return

        if path == "/api/list":
            try:
                files = [f for f in os.listdir(os.getcwd())
                         if os.path.isfile(os.path.join(os.getcwd(), f))]
            except Exception:
                files = []
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(sorted(files)).encode())
            self._log_access("GET", path, 200)
            return

        self.send_response(404)
        self.end_headers()
        self._log_access("GET", path, 404)

    def do_POST(self):
        helpers.record_peer(self.client_address[0], self.headers.get("User-Agent", ""))

        if self.path == "/api/upload":
            try:
                length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(length)
                boundary = self.headers.get("Content-Type", "").split("boundary=")[-1].encode()
                parts = body.split(b"--" + boundary)
                saved = []
                for part in parts:
                    if b'filename="' in part:
                        fname = part.split(b'filename="')[1].split(b'"')[0].decode()
                        fdata = part.split(b"\r\n\r\n", 1)[1].rstrip(b"\r\n--")
                        fpath = os.path.join(os.getcwd(), fname)
                        if os.path.exists(fpath):
                            base, ext = os.path.splitext(fname)
                            fpath = os.path.join(os.getcwd(), f"{base}_copy{ext}")
                        with open(fpath, "wb") as f:
                            f.write(fdata)
                        saved.append(fname)
                if saved:
                    ip = self.client_address[0]
                    ua = self.headers.get("User-Agent", "")
                    device, browser = helpers.parse_user_agent(ua)
                    helpers.log_queue.append(("success",
                        f"{device}  {browser}  ·  {ip}  ·  ⬆ Uploaded: {', '.join(saved)}"))
            except Exception as e:
                helpers.log_queue.append(("error", f"Upload error: {e}"))
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"ok":true}')

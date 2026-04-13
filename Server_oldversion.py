import http.server
import socketserver
import socket
import os
import threading
import tkinter as tk
from tkinter import filedialog, scrolledtext
from pathlib import Path
import urllib.parse
import webbrowser

PORT = 8080
server = None

# -----------------------------
# CLIENT PAGE (NO CHANGE)
# -----------------------------
def render_page():
    files = os.listdir(os.getcwd())

    file_list = ""
    for f in files:
        file_list += f'<li><a href="/files/{f}">{f}</a></li>'

    return f"""
    <html>
    <body>
        <h2>FileWaver Basic</h2>

        <h3>Upload File</h3>
        <form method="POST" enctype="multipart/form-data">
            <input type="file" name="file">
            <button type="submit">Upload</button>
        </form>

        <h3>Files</h3>
        <ul>
            {file_list}
        </ul>
    </body>
    </html>
    """

# -----------------------------
# HANDLER
# -----------------------------
class Handler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):
        path = urllib.parse.unquote(self.path)

        if path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(render_page().encode())
            return

        if path.startswith("/files/"):
            filename = path.replace("/files/", "")
            filepath = os.path.join(os.getcwd(), filename)

            if os.path.exists(filepath):
                with open(filepath, "rb") as f:
                    self.send_response(200)
                    self.send_header("Content-Disposition",
                                     f'attachment; filename="{filename}"')
                    self.end_headers()
                    self.wfile.write(f.read())
            return

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)

        boundary = self.headers['Content-Type'].split("boundary=")[-1]
        parts = body.split(("--" + boundary).encode())

        for part in parts:
            if b"filename=" in part:
                filename = part.split(b'filename="')[1].split(b'"')[0].decode()
                filedata = part.split(b"\r\n\r\n")[1].rstrip(b"\r\n--")

                filepath = os.path.join(os.getcwd(), filename)

                with open(filepath, "wb") as f:
                    f.write(filedata)

                log(f"Uploaded: {filename}")

        self.send_response(200)
        self.end_headers()


# -----------------------------
# NETWORK
# -----------------------------
def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip


# -----------------------------
# SERVER CONTROL
# -----------------------------
def start_server():
    global server

    port = int(port_entry.get())
    folder = folder_var.get()

    if not os.path.isdir(folder):
        log("Invalid folder")
        return

    os.chdir(folder)

    def run():
        global server
        with socketserver.TCPServer(("0.0.0.0", port), Handler) as httpd:
            server = httpd
            ip = get_ip()

            url = f"http://{ip}:{port}"

            status.set("RUNNING")
            local.set(f"http://127.0.0.1:{port}")
            net.set(url)

            log("Server Started")
            log(url)

            httpd.serve_forever()

    threading.Thread(target=run, daemon=True).start()


def stop_server():
    global server
    if server:
        server.shutdown()
        status.set("STOPPED")
        log("Server stopped")


def browse():
    path = filedialog.askdirectory()
    if path:
        folder_var.set(path)


def open_browser():
    if net.get():
        webbrowser.open(net.get())


def copy_ip():
    if net.get():
        root.clipboard_clear()
        root.clipboard_append(net.get())
        log("IP copied")


def log(msg):
    logs.insert(tk.END, msg + "\n")
    logs.see(tk.END)


# -----------------------------
# GUI (WHITE PROFESSIONAL)
# -----------------------------
root = tk.Tk()
root.title("FileWaver Basic Server")
root.geometry("720x520")
root.configure(bg="#f9fafb")  # WHITE BACKGROUND

folder_var = tk.StringVar(value=str(Path.cwd()))
status = tk.StringVar(value="STOPPED")
local = tk.StringVar()
net = tk.StringVar()

# HEADER
tk.Label(root, text="FileWaver Basic Server",
         font=("Segoe UI", 20, "bold"),
         bg="#f9fafb", fg="#111827").pack(pady=15)

# CARD
card = tk.Frame(root, bg="white", bd=1, relief="solid")
card.pack(padx=20, pady=10, fill="x")

tk.Label(card, text="Shared Folder", bg="white", fg="#374151").pack(anchor="w", padx=10, pady=5)
tk.Entry(card, textvariable=folder_var, bg="#f3f4f6", fg="black", width=70).pack(padx=10)

tk.Button(card, text="Browse", bg="#2563eb", fg="white",
          command=browse).pack(pady=8)

tk.Label(card, text="Port", bg="white", fg="#374151").pack(anchor="w", padx=10)
port_entry = tk.Entry(card, bg="#f3f4f6", fg="black")
port_entry.insert(0, "8000")
port_entry.pack(padx=10, pady=5)

# BUTTONS
btn_frame = tk.Frame(root, bg="#f9fafb")
btn_frame.pack(pady=10)

tk.Button(btn_frame, text="Start", bg="#16a34a", fg="white",
          width=10, command=start_server).grid(row=0, column=0, padx=8)

tk.Button(btn_frame, text="Stop", bg="#dc2626", fg="white",
          width=10, command=stop_server).grid(row=0, column=1, padx=8)

tk.Button(btn_frame, text="Open", bg="#2563eb", fg="white",
          width=10, command=open_browser).grid(row=0, column=2, padx=8)

tk.Button(btn_frame, text="Copy IP", bg="#0ea5e9", fg="white",
          width=10, command=copy_ip).grid(row=0, column=3, padx=8)

# STATUS
status_frame = tk.Frame(root, bg="white", bd=1, relief="solid")
status_frame.pack(padx=20, pady=10, fill="x")

tk.Label(status_frame, text="Status:", bg="white").grid(row=0, column=0, padx=5)
tk.Label(status_frame, textvariable=status, bg="white", fg="#16a34a").grid(row=0, column=1)

tk.Label(status_frame, text="Local:", bg="white").grid(row=1, column=0, padx=5)
tk.Label(status_frame, textvariable=local, bg="white", fg="#2563eb").grid(row=1, column=1)

tk.Label(status_frame, text="Network:", bg="white").grid(row=2, column=0, padx=5)
tk.Label(status_frame, textvariable=net, bg="white", fg="#16a34a").grid(row=2, column=1)

# LOGS
tk.Label(root, text="Logs", bg="#f9fafb", fg="#111827").pack(anchor="w", padx=20)

logs = scrolledtext.ScrolledText(root, bg="white", fg="black", height=10)
logs.pack(padx=20, pady=5, fill="both", expand=True)

root.mainloop()
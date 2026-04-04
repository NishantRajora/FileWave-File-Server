import http.server
import socketserver
import socket
import os
import threading
import tkinter as tk
from tkinter import filedialog, scrolledtext
import webbrowser
from pathlib import Path
import urllib.parse
import json

PORT = 8000
server = None

# -----------------------------
# HTML PAGE
# -----------------------------
def render_page():
    return """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>FileWave Pro</title>

<style>
body{font-family:Arial;background:#0f172a;margin:0;color:white;}
.top{background:#020617;padding:15px;text-align:center;font-size:22px;}
.box{max-width:900px;margin:20px auto;background:#1e293b;padding:20px;border-radius:10px;}

.upbox{border:2px dashed #475569;padding:20px;text-align:center;border-radius:10px;}

.file{display:flex;justify-content:space-between;padding:10px;border-bottom:1px solid #334155;}

.file a{margin-left:10px;color:#38bdf8;text-decoration:none;}
.file a:hover{text-decoration:underline;}
</style>

</head>

<body>

<div class="top">🚀 FileWave Pro</div>

<div class="box">

<div class="upbox">
<h3>📤 Upload Files</h3>
<input type="file" multiple onchange="uploadFiles(this.files)">
<progress id="bar" value="0" max="100"></progress>
<div id="pl"></div>
</div>

<h3>📁 Files</h3>
<div id="files"></div>

</div>

<script>

function loadFiles(){
 fetch('/api/list')
 .then(r=>r.json())
 .then(data=>{
    let html="";
    data.forEach(f=>{
        html += `<div class="file">
            <span>${f}</span>
            <div>
                <a href="/view/${f}" target="_blank">👁 View</a>
                <a href="/files/${f}" download>⬇ Download</a>
            </div>
        </div>`;
    });
    document.getElementById("files").innerHTML = html;
 });
}

function uploadFiles(files){
 let total = files.length;
 let done = 0;

 Array.from(files).forEach(file=>{
    let fd = new FormData();
    fd.append("file", file);

    fetch('/api/upload',{method:'POST',body:fd})
    .then(()=>{
        done++;
        document.getElementById("bar").value = (done/total)*100;
        document.getElementById("pl").innerText = done+"/"+total+" uploaded";

        if(done===total) setTimeout(loadFiles,500);
    });
 });
}

loadFiles();
</script>

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
                    data = f.read()

                self.send_response(200)
                self.send_header("Content-Disposition",
                                 f'attachment; filename="{filename}"')
                self.end_headers()
                self.wfile.write(data)
            return

        # FILE PREVIEW
        if path.startswith("/view/"):
            filename = path.replace("/view/", "")
            filepath = os.path.join(os.getcwd(), filename)

            if os.path.exists(filepath):
                self.send_response(200)

                if filename.endswith((".png",".jpg",".jpeg",".gif")):
                    self.send_header("Content-Type","image/jpeg")
                elif filename.endswith(".mp4"):
                    self.send_header("Content-Type","video/mp4")
                elif filename.endswith(".mp3"):
                    self.send_header("Content-Type","audio/mpeg")
                elif filename.endswith(".pdf"):
                    self.send_header("Content-Type","application/pdf")
                elif filename.endswith((".txt",".py",".js",".html",".css")):
                    self.send_header("Content-Type","text/plain")
                else:
                    self.send_header("Content-Type","application/octet-stream")

                self.end_headers()

                with open(filepath, "rb") as f:
                    self.wfile.write(f.read())
            return

        if path == "/api/list":
            files = os.listdir(os.getcwd())
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps(files).encode())
            return

    def do_POST(self):
        if self.path == "/api/upload":
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)

            boundary = self.headers['Content-Type'].split("boundary=")[-1]
            parts = body.split(("--" + boundary).encode())

            for part in parts:
                if b"filename=" in part:
                    filename = part.split(b'filename="')[1].split(b'"')[0].decode()
                    filedata = part.split(b"\r\n\r\n")[1].rstrip(b"\r\n--")

                    filepath = os.path.join(os.getcwd(), filename)

                    if os.path.exists(filepath):
                        filepath += "_new"

                    with open(filepath, "wb") as f:
                        f.write(filedata)

                    log(f"📤 Uploaded: {filename} from {self.client_address[0]}")

            self.send_response(200)
            self.end_headers()

# -----------------------------
# SERVER CONTROL
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


def start_server():
    global server

    port = int(port_entry.get())
    folder = folder_var.get()

    if not os.path.isdir(folder):
        log("❌ Invalid folder")
        return

    os.chdir(folder)

    def run():
        global server
        with socketserver.TCPServer(("0.0.0.0", port), Handler) as httpd:
            server = httpd
            ip = get_ip()

            status.set("🟢 RUNNING")
            local.set(f"http://127.0.0.1:{port}")
            net.set(f"http://{ip}:{port}")

            log("✅ Server Started")
            log(net.get())

            httpd.serve_forever()

    threading.Thread(target=run, daemon=True).start()


def stop_server():
    global server
    if server:
        server.shutdown()
        status.set("🔴 STOPPED")
        log("⛔ Server stopped")


def browse():
    path = filedialog.askdirectory()
    if path:
        folder_var.set(path)


def open_browser():
    webbrowser.open(net.get())


def log(msg):
    logs.insert(tk.END, msg + "\n")
    logs.see(tk.END)


# -----------------------------
# GUI (DASHBOARD)
# -----------------------------
root = tk.Tk()
root.title("FileWave Pro Dashboard")
root.geometry("750x550")
root.configure(bg="#0f172a")

folder_var = tk.StringVar(value=str(Path.cwd()))
status = tk.StringVar(value="🔴 STOPPED")
local = tk.StringVar()
net = tk.StringVar()

tk.Label(root, text="🚀 FileWave Server",
         font=("Segoe UI", 20, "bold"),
         bg="#0f172a", fg="#38bdf8").pack(pady=10)

card = tk.Frame(root, bg="#1e293b")
card.pack(padx=20, pady=10, fill="x")

tk.Label(card, text="📂 Folder", bg="#1e293b", fg="white").pack(anchor="w", padx=10)
tk.Entry(card, textvariable=folder_var, bg="#334155", fg="white", width=70).pack(padx=10)
tk.Button(card, text="Browse", bg="#38bdf8", command=browse).pack(pady=5)

tk.Label(card, text="Port", bg="#1e293b", fg="white").pack(anchor="w", padx=10)
port_entry = tk.Entry(card)
port_entry.insert(0, "8000")
port_entry.pack(padx=10, pady=5)

btn_frame = tk.Frame(root, bg="#0f172a")
btn_frame.pack()

tk.Button(btn_frame, text="▶ Start", bg="green", fg="white", command=start_server).grid(row=0, column=0, padx=10)
tk.Button(btn_frame, text="⛔ Stop", bg="red", fg="white", command=stop_server).grid(row=0, column=1, padx=10)
tk.Button(btn_frame, text="🌐 Open", bg="blue", fg="white", command=open_browser).grid(row=0, column=2, padx=10)

status_frame = tk.Frame(root, bg="#1e293b")
status_frame.pack(padx=20, pady=10, fill="x")

tk.Label(status_frame, text="Status:", bg="#1e293b", fg="white").grid(row=0, column=0)
tk.Label(status_frame, textvariable=status, bg="#1e293b", fg="yellow").grid(row=0, column=1)


tk.Label(status_frame, text="Local:", bg="#1e293b", fg="white").grid(row=1, column=0)
tk.Label(status_frame, textvariable=local, bg="#1e293b", fg="cyan").grid(row=1, column=1)

tk.Label(status_frame, text="Network:", bg="#1e293b", fg="white").grid(row=2, column=0)
tk.Label(status_frame, textvariable=net, bg="#1e293b", fg="lightgreen").grid(row=2, column=1)

tk.Label(root, text="Logs", bg="#0f172a", fg="white").pack(anchor="w", padx=20)

logs = scrolledtext.ScrolledText(root, bg="black", fg="white", height=12)
logs.pack(padx=20, pady=5, fill="both", expand=True)

root.mainloop()
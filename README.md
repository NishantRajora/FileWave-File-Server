# ⚡ FileWave Pro

A lightweight, self-contained local file server with a professional dark UI — built entirely in Python with zero external dependencies.

Run it, point it at a folder, and instantly get a clean web interface to browse, upload, preview, and download files from any device on your network.

---

## Screenshot

> Desktop control panel on the left · Browser file manager on the right

```
┌─────────────────────────────────────────────────────────┐
│ ⚡ FileWave Pro                              ● LIVE      │
├──────────────────────┬──────────────────────────────────┤
│  CONFIGURATION       │  ACTIVITY LOG                    │
│  Folder  [........]  │  [10:42:01] Server started on    │
│  Port    [8000    ]  │             port 8000            │
│                      │  [10:42:01] Local  → http://...  │
│  SERVER CONTROL      │  [10:42:01] Network→ http://...  │
│  ▶ Start  ■ Stop     │                                  │
│  ⬡ Open Browser      │                                  │
│                      │                                  │
│  CONNECTION          │                                  │
│  Local   http://...  │                                  │
│  Network http://...  │                                  │
└──────────────────────┴──────────────────────────────────┘
```

---

## Features

- **Zero dependencies** — pure Python standard library, nothing to `pip install`
- **Desktop GUI** — Tkinter control panel to set folder, port, and manage the server
- **Web UI** — professional dark browser interface served at your local IP
- **File browser** — list and grid views, search/filter, sort by name or type
- **Drag & drop upload** — drop files onto the browser page or use the file picker
- **Inline preview** — images, video, audio, PDF, and code files preview in-place
- **Color-coded file types** — blue for code, red for images, green for docs, yellow for archives
- **Semantic log colors** — green = success, red = error, yellow = warning, blue = info
- **LAN access** — serves on `0.0.0.0` so any device on your network can connect
- **Auto port fallback** — configurable port, defaults to `8000`

---

## Requirements

| Requirement | Version |
|---|---|
| Python | 3.7 or higher |
| Tkinter | Included with most Python installs |

No third-party packages are required.

> **Linux users:** if Tkinter is missing, install it with:
> ```bash
> sudo apt install python3-tk       # Debian / Ubuntu
> sudo dnf install python3-tkinter  # Fedora
> ```

---

## Installation

```bash
# Clone the repository
git clone https://github.com/NishantRajora/FileWave-File-Server

# Run directly — no install step needed
python Server.py
```

---

## Usage

### 1. Launch the app

```bash
python Server.py
```

The desktop control panel opens.

### 2. Configure

- **Folder** — click **Browse** to select the directory you want to serve, or type the path manually.
- **Port** — defaults to `8000`. Change it if the port is already in use.

### 3. Start the server

Click **▶ Start**. The status pill changes from `● OFFLINE` to `● LIVE` and the Connection section shows your URLs.

### 4. Open in browser

Click **⬡ Open Browser**, or navigate manually to one of:

| URL | Access from |
|---|---|
| `http://127.0.0.1:8000` | This machine only |
| `http://192.168.x.x:8000` | Any device on your LAN |

### 5. Stop the server

Click **■ Stop** in the control panel, or close the window.

---

## Web Interface

| Feature | Detail |
|---|---|
| Upload | Drag & drop or click **Choose Files** — multiple files at once |
| Progress bar | Live upload progress with file count |
| File list | List or grid view, searchable, sortable |
| File tags | Color-coded by type (image / video / audio / doc / code / archive / data) |
| Preview | Click any file — images, video, audio, PDF, and plain text render inline |
| Download | Hover a file and click the download icon |

---

## API Endpoints

FileWave  exposes a minimal HTTP API used by the web UI.

| Method | Path | Description |
|---|---|---|
| `GET` | `/` | Serves the web UI |
| `GET` | `/api/list` | Returns a JSON array of filenames in the served folder |
| `GET` | `/files/<name>` | Downloads a file (with `Content-Disposition: attachment`) |
| `GET` | `/view/<name>` | Serves a file inline for preview |
| `POST` | `/api/upload` | Accepts `multipart/form-data` file upload |

---

## Project Structure

```
FileWave-File-Server/
└── Server.py       # Everything — server, GUI, and web UI in one file
```

The entire project is intentionally a single file. The web UI HTML is embedded as a Python string inside `render_page()` and served dynamically.

---

## Color System

Both the desktop GUI and the browser UI share the same semantic color palette:

| Color | Meaning |
|---|---|
| 🔵 Blue `#3b82f6` | Primary actions, buttons, active states, code files |
| 🟢 Green `#22c55e` | Live status, success messages, document files |
| 🔴 Red `#ef4444` | Stop/error, image file tags, error log lines |
| 🟡 Yellow `#eab308` | Warnings, archive and audio file tags |

---

## Troubleshooting

**Port already in use**
Change the port number in the control panel to any unused port (e.g. `8080`, `9000`).

**Tkinter not found (Linux)**
```bash
sudo apt install python3-tk
```

**Can't access from another device**
Make sure your firewall allows inbound connections on the chosen port. On Windows, you may see a firewall prompt the first time you start the server — click **Allow**.

**File not showing in the list**
The file browser only lists files directly inside the chosen folder (not subdirectories). Move the file to the root of the served folder.

---

## License

MIT — do whatever you want with it.

---

*Built with Python · Tkinter · Vanilla JS · No frameworks · No dependencies*

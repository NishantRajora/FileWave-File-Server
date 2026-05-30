import os
import threading
import socketserver
import webbrowser
import time
from pathlib import Path
import tkinter as tk
from tkinter import filedialog

import helpers
from handler import Handler


class App(tk.Tk):

    BG       = "#F7F7FB"
    WHITE    = "#FFFFFF"
    LAVENDER = "#F0EDFF"
    BORDER   = "#E5E7EB"
    BORDER2  = "#D1D5DB"

    PURPLE   = "#7C3AED"
    PURPLE_L = "#9D6FF5"
    PURPLE_T = "#EDE9FE"
    PURPLE_D = "#6D28D9"

    INK      = "#1A1A2E"
    SLATE    = "#6B7280"
    MIST     = "#9CA3AF"

    GREEN    = "#10B981"
    GREEN_T  = "#D1FAE5"
    RED      = "#EF4444"
    RED_T    = "#FEE2E2"
    AMBER    = "#F59E0B"
    AMBER_T  = "#FEF3C7"
    BLUE     = "#3B82F6"
    BLUE_T   = "#EFF6FF"

    def __init__(self):
        super().__init__()
        self.title("FileWave Pro")
        self.geometry("1000x640")
        self.minsize(820, 540)
        self.configure(bg=self.BG)
        self.resizable(True, True)

        self._server_obj = None
        self._running    = False
        self._log_after  = None

        self._build_ui()
        self._poll_logs()
        self._poll_peers()

    def _frame(self, parent, bg=None, **kw):
        return tk.Frame(parent, bg=bg or self.BG, **kw)

    def _label(self, parent, text, font=None, fg=None, bg=None, **kw):
        return tk.Label(parent, text=text,
            font=font or ("Helvetica", 10),
            fg=fg or self.SLATE, bg=bg or self.BG, **kw)

    def _entry(self, parent, textvariable, width=None, **kw):
        e = tk.Entry(parent,
            textvariable=textvariable,
            bg=self.WHITE, fg=self.INK,
            insertbackground=self.PURPLE,
            relief="flat",
            font=("Helvetica", 11),
            highlightthickness=1,
            highlightbackground=self.BORDER,
            highlightcolor=self.PURPLE,
            **({} if width is None else {"width": width}), **kw)
        return e

    def _btn(self, parent, text, cmd, bg=None, fg="#FFFFFF",
             hover=None, padx=16, pady=8):
        bg    = bg    or self.PURPLE
        hover = hover or self.PURPLE_L
        b = tk.Button(parent, text=text, command=cmd,
            bg=bg, fg=fg,
            activebackground=hover, activeforeground=fg,
            relief="flat", bd=0, cursor="hand2",
            font=("Helvetica", 10, "bold"), padx=padx, pady=pady)
        b.bind("<Enter>", lambda e, h=hover: b.config(bg=h))
        b.bind("<Leave>", lambda e, c=bg:    b.config(bg=c))
        return b

    def _ghost_btn(self, parent, text, cmd, fg=None, font_size=10):
        fg = fg or self.PURPLE
        b = tk.Button(parent, text=text, command=cmd,
            bg=self.WHITE, fg=fg,
            activebackground=self.PURPLE_T, activeforeground=fg,
            relief="flat", bd=0, cursor="hand2",
            font=("Helvetica", font_size),
            padx=12, pady=7,
            highlightthickness=1,
            highlightbackground=self.BORDER,
            highlightcolor=self.PURPLE)
        b.bind("<Enter>", lambda e: b.config(bg=self.PURPLE_T))
        b.bind("<Leave>", lambda e: b.config(bg=self.WHITE))
        return b

    def _divider(self, parent, orient="h", color=None, **kw):
        color = color or self.BORDER
        if orient == "h":
            return tk.Frame(parent, bg=color, height=1, **kw)
        return tk.Frame(parent, bg=color, width=1, **kw)

    def _section_lbl(self, parent, text, bg=None):
        bg = bg or self.BG
        f  = self._frame(parent, bg=bg)
        f.pack(fill="x", pady=(0, 6))
        self._label(f, text,
            font=("Helvetica", 9, "bold"),
            fg=self.MIST, bg=bg).pack(side="left")
        return f

    def _build_ui(self):
        self._build_navbar()
        self._build_body()
        self._build_statusbar()

    def _build_navbar(self):
        nav = tk.Frame(self, bg=self.WHITE, height=52)
        nav.pack(fill="x")
        nav.pack_propagate(False)
        self._divider(nav, "h").pack(side="bottom", fill="x")

        left = tk.Frame(nav, bg=self.WHITE)
        left.pack(side="left", padx=20)

        logo = tk.Frame(left, bg=self.PURPLE, width=30, height=30)
        logo.pack(side="left")
        logo.pack_propagate(False)
        tk.Label(logo, text="⚡", font=("Helvetica", 14, "bold"),
                 bg=self.PURPLE, fg=self.WHITE).place(relx=.5, rely=.5, anchor="center")

        tk.Label(left, text="  FileWave Pro",
                 font=("Helvetica", 14, "bold"),
                 bg=self.WHITE, fg=self.INK).pack(side="left")
        tk.Label(left, text="  LOCAL FILE SERVER",
                 font=("Helvetica", 8),
                 bg=self.WHITE, fg=self.MIST).pack(side="left", pady=(4, 0))

        right = tk.Frame(nav, bg=self.WHITE)
        right.pack(side="right", padx=20)

        self._peer_badge = tk.Label(right, text="👥 0 peers",
            font=("Helvetica", 9), bg=self.BLUE_T, fg=self.BLUE,
            padx=8, pady=4)
        self._peer_badge.pack(side="right", padx=(8, 0))

        self._status_frame = tk.Frame(right, bg=self.RED_T, padx=10, pady=4)
        self._status_frame.pack(side="right")

        self._status_dot = tk.Label(self._status_frame, text="●",
            font=("Helvetica", 8), bg=self.RED_T, fg=self.RED)
        self._status_dot.pack(side="left")

        self._status_lbl = tk.Label(self._status_frame, text=" OFFLINE",
            font=("Helvetica", 9, "bold"), bg=self.RED_T, fg=self.RED)
        self._status_lbl.pack(side="left")

    def _build_body(self):
        body = tk.Frame(self, bg=self.BG)
        body.pack(fill="both", expand=True)
        body.columnconfigure(0, weight=0, minsize=370)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

        left  = tk.Frame(body, bg=self.WHITE)
        right = tk.Frame(body, bg=self.BG)
        left.grid(row=0, column=0, sticky="nsew")
        right.grid(row=0, column=1, sticky="nsew")
        self._divider(body, "v").grid(row=0, column=0, sticky="nse")

        self._build_left(left)
        self._build_right(right)

    def _build_left(self, parent):
        canvas = tk.Canvas(parent, bg=self.WHITE, highlightthickness=0)
        canvas.pack(fill="both", expand=True)
        inner = tk.Frame(canvas, bg=self.WHITE)
        canvas.create_window((0, 0), window=inner, anchor="nw")
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        self._build_left_inner(inner)

    def _build_left_inner(self, p):
        pad = dict(padx=20)

        hero = tk.Frame(p, bg=self.LAVENDER)
        hero.pack(fill="x")
        tk.Label(hero, text="Your local file server  📡",
                 font=("Helvetica", 11), bg=self.LAVENDER, fg=self.PURPLE).pack(
                 side="left", padx=20, pady=12)

        tk.Frame(p, bg=self.BG, height=16).pack(fill="x")

        self._section_lbl(p, "  SERVE FOLDER", bg=self.WHITE).pack(**pad, fill="x")
        row1 = tk.Frame(p, bg=self.WHITE)
        row1.pack(fill="x", **pad, pady=(0, 10))
        self.folder_var = tk.StringVar(value=str(Path.cwd()))
        self._entry(row1, self.folder_var).pack(side="left", fill="x", expand=True, padx=(0, 8))
        self._ghost_btn(row1, "Browse", self._browse).pack(side="left")

        self._section_lbl(p, "  PORT", bg=self.WHITE).pack(**pad, fill="x")
        row2 = tk.Frame(p, bg=self.WHITE)
        row2.pack(fill="x", **pad, pady=(0, 4))
        self.port_var = tk.StringVar(value="8000")
        self._entry(row2, self.port_var, width=10).pack(side="left")
        self._label(row2, "   Default: 8000", fg=self.MIST,
                    bg=self.WHITE, font=("Helvetica", 9)).pack(side="left")

        self._divider(p).pack(fill="x", **pad, pady=16)

        self._section_lbl(p, "  SERVER CONTROL", bg=self.WHITE).pack(**pad, fill="x")
        btns = tk.Frame(p, bg=self.WHITE)
        btns.pack(fill="x", **pad, pady=(0, 4))
        self._btn(btns, "▶  Start Server", self._start).pack(side="left", padx=(0, 8))
        self._btn(btns, "■  Stop", self._stop, bg=self.RED, hover="#DC2626").pack(side="left", padx=(0, 8))
        self._ghost_btn(btns, "🌐  Open Browser", self._open_browser).pack(side="left")

        tk.Frame(p, bg=self.WHITE, height=8).pack(fill="x")
        simple_row = tk.Frame(p, bg=self.WHITE)
        simple_row.pack(fill="x", **pad, pady=(0, 4))
        self._ghost_btn(simple_row, "📟  Open Simple Mode",
                        self._open_simple, fg=self.SLATE).pack(side="left")
        self._label(simple_row, "  (no JS — for old devices)",
                    fg=self.MIST, bg=self.WHITE, font=("Helvetica", 9)).pack(side="left")

        self._divider(p).pack(fill="x", **pad, pady=16)

        self._section_lbl(p, "  CONNECTION DETAILS", bg=self.WHITE).pack(**pad, fill="x")
        conn = tk.Frame(p, bg=self.WHITE)
        conn.pack(fill="x", **pad, pady=(0, 4))

        self.local_var = tk.StringVar(value="Not running")
        self.net_var   = tk.StringVar(value="Not running")

        for label, var, ico in [("Local", self.local_var, "🖥"), ("Network", self.net_var, "🌐")]:
            row = tk.Frame(conn, bg=self.WHITE)
            row.pack(fill="x", pady=4)
            badge = tk.Frame(row, bg=self.PURPLE_T, padx=6, pady=4)
            badge.pack(side="left")
            tk.Label(badge, text=ico, bg=self.PURPLE_T, font=("Helvetica", 11)).pack()
            info = tk.Frame(row, bg=self.WHITE)
            info.pack(side="left", padx=10)
            tk.Label(info, text=label, font=("Helvetica", 8, "bold"),
                     bg=self.WHITE, fg=self.MIST).pack(anchor="w")
            url_lbl = tk.Label(info, textvariable=var, font=("Helvetica", 10, "bold"),
                     bg=self.WHITE, fg=self.PURPLE, cursor="hand2")
            url_lbl.pack(anchor="w")
            url_lbl.bind("<Button-1>", lambda e, v=var: self._copy_url(v.get()))

        self._divider(p).pack(fill="x", **pad, pady=16)

        copy_row = tk.Frame(p, bg=self.WHITE)
        copy_row.pack(fill="x", **pad, pady=(0, 10))
        self._ghost_btn(copy_row, "📋 Copy Local",
                        lambda: self._copy_url(self.local_var.get())).pack(side="left", padx=(0, 8))
        self._ghost_btn(copy_row, "📋 Copy Network",
                        lambda: self._copy_url(self.net_var.get())).pack(side="left")

        self._divider(p).pack(fill="x", **pad, pady=10)

        tip = tk.Frame(p, bg=self.AMBER_T, padx=14, pady=12)
        tip.pack(fill="x", **pad, pady=(0, 20))
        tk.Label(tip, text="💡  Tip", font=("Helvetica", 9, "bold"),
                 bg=self.AMBER_T, fg=self.AMBER).pack(anchor="w")
        tk.Label(tip,
                 text="Share your Network URL with devices on the same Wi-Fi.\n"
                      "Use 📟 Simple Mode for old devices or browsers without JS.\n"
                      "Click any URL above to copy it.",
                 font=("Helvetica", 9), bg=self.AMBER_T, fg=self.INK,
                 justify="left").pack(anchor="w", pady=(4, 0))

    def _build_right(self, parent):
        header = tk.Frame(parent, bg=self.WHITE, height=44)
        header.pack(fill="x")
        header.pack_propagate(False)
        self._divider(header).pack(side="bottom", fill="x")
        tk.Label(header, text="  📋  Activity Log",
                 font=("Helvetica", 12, "bold"),
                 bg=self.WHITE, fg=self.INK).pack(side="left", padx=16, pady=10)

        legend = tk.Frame(header, bg=self.WHITE)
        legend.pack(side="left", padx=8)
        for sym, fg, tip in [("🖥", self.SLATE, "Desktop"),
                              ("📱", self.SLATE, "Mobile"),
                              ("📟", self.SLATE, "Tablet")]:
            tk.Label(legend, text=f"{sym} {tip}", font=("Helvetica", 8),
                     bg=self.WHITE, fg=fg).pack(side="left", padx=4)

        self._ghost_btn(header, "Clear", self._clear_log,
                        fg=self.SLATE, font_size=9).pack(side="right", padx=12, pady=8)

        log_bg = tk.Frame(parent, bg=self.BG)
        log_bg.pack(fill="both", expand=True, padx=16, pady=12)

        log_card = tk.Frame(log_bg, bg=self.BORDER, padx=1, pady=1)
        log_card.pack(fill="both", expand=True)

        inner = tk.Frame(log_card, bg=self.WHITE)
        inner.pack(fill="both", expand=True)

        self.log_box = tk.Text(inner,
            bg=self.WHITE, fg=self.INK,
            insertbackground=self.PURPLE,
            font=("Courier", 10),
            relief="flat",
            state="disabled",
            wrap="word",
            padx=14, pady=12,
            selectbackground=self.PURPLE_T,
            selectforeground=self.INK,
            cursor="arrow",
            spacing1=3, spacing3=3)
        self.log_box.pack(side="left", fill="both", expand=True)

        sb = tk.Scrollbar(inner, command=self.log_box.yview,
                          bg=self.BG, troughcolor=self.BG,
                          relief="flat", bd=0, width=8)
        sb.pack(side="right", fill="y")
        self.log_box.configure(yscrollcommand=sb.set)

        self.log_box.tag_config("ts",      foreground=self.MIST)
        self.log_box.tag_config("success", foreground=self.GREEN)
        self.log_box.tag_config("error",   foreground=self.RED)
        self.log_box.tag_config("warn",    foreground=self.AMBER)
        self.log_box.tag_config("info",    foreground=self.BLUE)
        self.log_box.tag_config("muted",   foreground=self.SLATE)

        self._log("FileWave Pro ready.  Choose a folder and start the server.", "muted")
        self._log("Device  ·  Browser  ·  IP  ·  Method  Path  [status]", "muted")

    def _build_statusbar(self):
        bar = tk.Frame(self, bg=self.WHITE, height=28)
        bar.pack(fill="x", side="bottom")
        bar.pack_propagate(False)
        self._divider(bar).pack(side="top", fill="x")
        self._sb_left = tk.Label(bar, text="  No server running",
            font=("Helvetica", 9), bg=self.WHITE, fg=self.MIST, anchor="w")
        self._sb_left.pack(side="left", fill="x", expand=True, padx=4)
        tk.Label(bar, text="FileWave Pro  ",
            font=("Helvetica", 9), bg=self.WHITE, fg=self.MIST).pack(side="right")

    def _browse(self):
        p = filedialog.askdirectory()
        if p:
            self.folder_var.set(p)
            self._log(f"Folder → {p}", "info")

    def _start(self):
        if self._running:
            self._log("Server already running.", "warn"); return
        folder = self.folder_var.get()
        if not os.path.isdir(folder):
            self._log("Invalid folder path.", "error"); return
        try:
            port = int(self.port_var.get())
        except ValueError:
            self._log("Invalid port number.", "error"); return

        os.chdir(folder)
        self._running = True

        def run():
            try:
                with socketserver.TCPServer(("0.0.0.0", port), Handler) as httpd:
                    self._server_obj = httpd
                    ip        = helpers.get_ip()
                    local_url = f"http://127.0.0.1:{port}"
                    net_url   = f"http://{ip}:{port}"
                    self.local_var.set(local_url)
                    self.net_var.set(net_url)
                    self._set_live(True)
                    self._sb_left.config(text=f"  Serving  {folder}  →  {net_url}")
                    helpers.log_queue.append(("success", f"Server started · port {port}"))
                    helpers.log_queue.append(("info",    f"Local   → {local_url}"))
                    helpers.log_queue.append(("info",    f"Network → {net_url}"))
                    helpers.log_queue.append(("muted",   f"Simple Mode → {net_url}/simple"))
                    httpd.serve_forever()
            except Exception as e:
                helpers.log_queue.append(("error", f"Error: {e}"))
                self._running = False
                self._set_live(False)

        threading.Thread(target=run, daemon=True).start()

    def _stop(self):
        if self._server_obj:
            self._server_obj.shutdown()
            self._server_obj = None
            self._running = False
            self.local_var.set("Not running")
            self.net_var.set("Not running")
            self._set_live(False)
            self._sb_left.config(text="  No server running")
            self._log("Server stopped.", "warn")
        else:
            self._log("No server is running.", "warn")

    def _open_browser(self):
        url = self.net_var.get()
        if url and url != "Not running":
            webbrowser.open(url)
            self._log(f"Opened browser → {url}", "info")
        else:
            self._log("Start the server first.", "warn")

    def _open_simple(self):
        url = self.net_var.get()
        if url and url != "Not running":
            webbrowser.open(url + "/simple")
            self._log(f"Opened Simple Mode → {url}/simple", "info")
        else:
            self._log("Start the server first.", "warn")

    def _copy_url(self, url):
        if url and url != "Not running":
            self.clipboard_clear()
            self.clipboard_append(url)
            self._log(f"Copied to clipboard: {url}", "success")
        else:
            self._log("Start the server first.", "warn")

    def _clear_log(self):
        self.log_box.config(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.config(state="disabled")

    def _set_live(self, live):
        if live:
            self._status_frame.config(bg=self.GREEN_T)
            self._status_dot.config(bg=self.GREEN_T, fg=self.GREEN)
            self._status_lbl.config(bg=self.GREEN_T, fg=self.GREEN, text=" LIVE")
            self._animate_dot()
        else:
            self._status_frame.config(bg=self.RED_T)
            self._status_dot.config(bg=self.RED_T, fg=self.RED)
            self._status_lbl.config(bg=self.RED_T, fg=self.RED, text=" OFFLINE")

    def _animate_dot(self, visible=True):
        if not self._running:
            return
        self._status_dot.config(fg=self.GREEN if visible else self.GREEN_T)
        self.after(900, lambda: self._animate_dot(not visible))

    def _log(self, msg, level="muted"):
        ts = time.strftime("%H:%M:%S")
        icons = {"success": "✓", "error": "✗", "warn": "⚠", "info": "→", "muted": "·"}
        prefix = icons.get(level, "·")
        self.log_box.config(state="normal")
        self.log_box.insert("end", f"[{ts}]  ", "ts")
        self.log_box.insert("end", f"{prefix}  {msg}\n", level)
        self.log_box.see("end")
        self.log_box.config(state="disabled")

    def _poll_logs(self):
        while helpers.log_queue:
            entry = helpers.log_queue.pop(0)
            level, msg = entry if isinstance(entry, tuple) else ("muted", entry)
            self._log(msg, level)
        self.after(250, self._poll_logs)

    def _poll_peers(self):
        with helpers._lock:
            count = len(helpers.connected_peers)
        self._peer_badge.config(text=f"👥 {count} peer{'s' if count != 1 else ''}")
        self.after(3000, self._poll_peers)

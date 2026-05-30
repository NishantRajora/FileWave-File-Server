import os
import threading
import time
import socket

# Shared application state
log_queue = []
connected_peers = {}
_lock = threading.Lock()


# SIZE HELPERS
def _fmt_size(sz):
    for unit in ["B", "KB", "MB", "GB"]:
        if sz < 1024:
            return f"{int(sz)} {unit}" if unit == 'B' else f"{sz:.1f} {unit}"
        sz /= 1024
    return f"{sz:.1f} TB"


def _fmt_size_safe(filename):
    try:
        return _fmt_size(os.path.getsize(os.path.join(os.getcwd(), filename)))
    except Exception:
        return ""


# USER-AGENT / DEVICE DETECTION
def parse_user_agent(ua):
    ua = ua or ""
    ul = ua.lower()

    if any(x in ul for x in ["iphone", "android", "mobile", "blackberry", "windows phone"]):
        device = "📱 Mobile"
    elif any(x in ul for x in ["ipad", "tablet", "kindle"]):
        device = "📟 Tablet"
    else:
        device = "🖥  Desktop"

    if "edg/" in ul or "edge/" in ul:
        browser = "Edge"
    elif "chrome/" in ul and "chromium" not in ul:
        browser = "Chrome"
    elif "firefox/" in ul:
        browser = "Firefox"
    elif "safari/" in ul and "chrome" not in ul:
        browser = "Safari"
    elif "curl" in ul:
        browser = "curl"
    elif "python" in ul:
        browser = "Python"
    else:
        browser = "Browser"

    return device, browser


# PEER TRACKER
def record_peer(ip, ua):
    device, browser = parse_user_agent(ua)
    with _lock:
        if ip not in connected_peers:
            connected_peers[ip] = {
                "ip": ip,
                "device": device,
                "browser": browser,
                "first_seen": time.strftime("%H:%M:%S"),
                "requests": 0,
            }
        connected_peers[ip]["last_seen"] = time.strftime("%H:%M:%S")
        connected_peers[ip]["requests"] += 1


# NETWORK HELPERS
def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"
    finally:
        s.close()

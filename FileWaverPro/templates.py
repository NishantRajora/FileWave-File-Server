import urllib.parse


def render_simple_page(files):
    file_rows = "\n".join(
        f'<li><a href="/files/{urllib.parse.quote(f)}" download>{f}</a></li>'
        for f in files
    ) or '<li><em>No files available.</em></li>'

    return f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><title>FileWave Basic</title></head>
<body>
<h2>FileWave Basic</h2>

<h3>Download Files</h3>
<ul>
{file_rows}
</ul>

<h3>Upload a File</h3>
<form method="post" action="/api/upload" enctype="multipart/form-data">
  <input type="file" name="file" multiple><br><br>
  <input type="submit" value="Upload">
</form>

<p><a href="/">Switch to Full UI</a></p>
</body>
</html>"""


# Full page is large; keep as a single function returning the raw HTML/JS/CSS string.
def render_page():
    return r"""<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
<title>FileWave Pro</title>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<script src="https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js"></script>
<style>
/* ── THEME VARIABLES ─────────────────────── */
:root,[data-theme="dark"]{
  --bg:        #111318;
  --surface:   #1a1d24;
  --panel:     #1f2330;
  --border:    #2c3040;
  --border2:   #353a4d;
  --blue:      #3b82f6;
  --blue-dim:  rgba(59,130,246,0.12);
  --blue-mid:  rgba(59,130,246,0.22);
  --green:     #22c55e;
  --green-dim: rgba(34,197,94,0.1);
  --red:       #ef4444;
  --red-dim:   rgba(239,68,68,0.1);
  --yellow:    #eab308;
  --yellow-dim:rgba(234,179,8,0.1);
  --text:      #e2e5ef;
  --text-2:    #9099b5;
  --text-3:    #5c6380;
  --shadow:    rgba(0,0,0,0.4);
  --modal-bg:  rgba(0,0,0,0.7);
}
[data-theme="light"]{
  --bg:        #f0f2f8;
  --surface:   #ffffff;
  --panel:     #f7f8fc;
  --border:    #dde1ef;
  --border2:   #c8cedf;
  --blue:      #2563eb;
  --blue-dim:  rgba(37,99,235,0.08);
  --blue-mid:  rgba(37,99,235,0.16);
  --green:     #16a34a;
  --green-dim: rgba(22,163,74,0.08);
  --red:       #dc2626;
  --red-dim:   rgba(220,38,38,0.08);
  --yellow:    #ca8a04;
  --yellow-dim:rgba(202,138,4,0.08);
  --text:      #1e2235;
  --text-2:    #4a5270;
  --text-3:    #8a91ab;
  --shadow:    rgba(0,0,0,0.12);
  --modal-bg:  rgba(0,0,0,0.45);
}

*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html,body{height:100%;overflow:hidden}
body{font-family:'IBM Plex Sans',sans-serif;background:var(--bg);color:var(--text);font-size:14px;line-height:1.5;transition:background .25s,color .25s}

/* ── APP SHELL ──────────────────────────── */
.app-shell{display:grid;grid-template-rows:48px 1fr;height:100vh;overflow:hidden}

/* ── NAVBAR ─────────────────────────────── */
.navbar{
  background:var(--panel);
  border-bottom:1px solid var(--border);
  display:flex;align-items:center;padding:0 16px;gap:10px;
  flex-shrink:0;position:relative;z-index:100;
}
.nav-brand{display:flex;align-items:center;gap:9px;font-weight:600;font-size:15px;letter-spacing:-.2px;color:var(--text);white-space:nowrap}
.nav-logo{width:26px;height:26px;background:var(--blue);border-radius:4px;display:flex;align-items:center;justify-content:center;font-size:13px;flex-shrink:0}
.nav-sep{width:1px;height:20px;background:var(--border);margin:0 2px;flex-shrink:0}
.nav-spacer{flex:1}

.nav-pill{display:flex;align-items:center;gap:5px;padding:3px 10px;border-radius:20px;font-family:'IBM Plex Mono',monospace;font-size:11px;font-weight:500;letter-spacing:.3px;border:1px solid;transition:all .4s;white-space:nowrap;flex-shrink:0}
.nav-pill.live{color:var(--green);border-color:rgba(34,197,94,.35);background:var(--green-dim)}
.nav-pill.offline{color:var(--red);border-color:rgba(239,68,68,.35);background:var(--red-dim)}
.nav-pill .dot{width:6px;height:6px;border-radius:50%;background:currentColor}
.nav-pill.live .dot{animation:blink 1.8s ease-in-out infinite}
@keyframes blink{0%,100%{opacity:1}50%{opacity:.35}}

.nav-icon-btn{width:32px;height:32px;border-radius:6px;border:1px solid var(--border2);background:transparent;color:var(--text-2);cursor:pointer;font-size:15px;display:flex;align-items:center;justify-content:center;transition:all .15s;flex-shrink:0}
.nav-icon-btn:hover{background:var(--blue-dim);color:var(--blue);border-color:var(--blue)}

.nav-info{font-family:'IBM Plex Mono',monospace;font-size:11px;color:var(--text-3);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:200px}

/* hamburger — mobile only */
.hamburger{display:none;width:32px;height:32px;border-radius:6px;border:1px solid var(--border2);background:transparent;color:var(--text-2);cursor:pointer;font-size:18px;align-items:center;justify-content:center;flex-shrink:0}

/* ── CONTENT ─────────────────────────────── */
.content{display:grid;grid-template-columns:340px 1fr;overflow:hidden;height:100%}

/* ── LEFT / RIGHT PANELS ─────────────────── */
.left-panel{background:var(--surface);border-right:1px solid var(--border);display:flex;flex-direction:column;overflow:hidden;transition:transform .28s cubic-bezier(.4,0,.2,1)}
.right-panel{display:flex;flex-direction:column;overflow:hidden;background:var(--bg)}

.section-head{padding:12px 16px 10px;border-bottom:1px solid var(--border);display:flex;align-items:center;justify-content:space-between;flex-shrink:0}
.section-title{font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.8px;color:var(--text-3);display:flex;align-items:center;gap:7px}

/* ── UPLOAD AREA ─────────────────────────── */
.upload-area{padding:14px;border-bottom:1px solid var(--border);flex-shrink:0}
.drop-zone{border:1.5px dashed var(--border2);border-radius:7px;padding:20px 16px;text-align:center;cursor:pointer;transition:all .18s;background:var(--bg)}
.drop-zone:hover,.drop-zone.drag-over{border-color:var(--blue);background:var(--blue-dim)}
.drop-icon{font-size:26px;margin-bottom:8px;display:block}
.drop-zone h3{font-size:13px;font-weight:600;color:var(--text);margin-bottom:3px}
.drop-zone p{font-size:11px;color:var(--text-3);font-family:'IBM Plex Mono',monospace}
#fileInput{display:none}
.btn{display:inline-flex;align-items:center;gap:6px;padding:7px 14px;border-radius:4px;border:1px solid transparent;font-family:'IBM Plex Sans',sans-serif;font-weight:500;font-size:13px;cursor:pointer;transition:all .15s;line-height:1}
.btn-primary{background:var(--blue);color:#fff;border-color:var(--blue)}
.btn-primary:hover{filter:brightness(1.12)}
.btn-ghost{background:transparent;color:var(--text-2);border-color:var(--border2)}
.btn-ghost:hover{background:var(--panel);color:var(--text);border-color:var(--blue)}
.btn-sm{padding:4px 10px;font-size:12px}
.upload-btn-row{margin-top:10px;display:flex;justify-content:center}
.progress-wrap{margin-top:12px;display:none}
.progress-wrap.active{display:block}
.progress-row{display:flex;justify-content:space-between;font-family:'IBM Plex Mono',monospace;font-size:11px;color:var(--text-3);margin-bottom:6px}
.progress-track{height:4px;background:var(--border);border-radius:99px;overflow:hidden}
.progress-fill{height:100%;background:var(--blue);border-radius:99px;width:0%;transition:width .25s}

/* ── STATS / TOOLBAR ─────────────────────── */
.stats-strip{padding:8px 16px;border-bottom:1px solid var(--border);display:flex;gap:18px;flex-shrink:0;flex-wrap:wrap}
.stat-item{display:flex;align-items:center;gap:5px;font-family:'IBM Plex Mono',monospace;font-size:11px;color:var(--text-3)}
.stat-item strong{color:var(--text);font-weight:500}
.toolbar{padding:10px 14px;border-bottom:1px solid var(--border);display:flex;gap:8px;align-items:center;flex-shrink:0;flex-wrap:wrap}
.search-field{flex:1;min-width:120px;display:flex;align-items:center;gap:7px;background:var(--bg);border:1px solid var(--border2);border-radius:4px;padding:5px 10px;transition:border-color .15s}
.search-field:focus-within{border-color:var(--blue)}
.search-field input{background:none;border:none;outline:none;color:var(--text);font-family:'IBM Plex Mono',monospace;font-size:12px;width:100%}
.search-field .ico{color:var(--text-3);font-size:13px}
.sort-sel{background:var(--bg);border:1px solid var(--border2);border-radius:4px;padding:5px 8px;color:var(--text-2);font-family:'IBM Plex Mono',monospace;font-size:11px;cursor:pointer;outline:none}
.view-grp{display:flex;border:1px solid var(--border2);border-radius:4px;overflow:hidden}
.view-btn{padding:5px 10px;background:none;border:none;border-right:1px solid var(--border2);color:var(--text-3);cursor:pointer;font-size:13px;transition:all .15s}
.view-btn:last-child{border-right:none}
.view-btn.active{background:var(--blue-dim);color:var(--blue)}
.view-btn:hover:not(.active){background:var(--panel);color:var(--text)}

/* ── FILE LIST / GRID ────────────────────── */
.file-scroll{flex:1;overflow-y:auto;padding:8px}
::-webkit-scrollbar{width:5px}
::-webkit-scrollbar-track{background:transparent}
::-webkit-scrollbar-thumb{background:var(--border2);border-radius:99px}
.file-list{display:flex;flex-direction:column;gap:2px}
.file-item{display:flex;align-items:center;gap:10px;padding:9px 10px;border-radius:4px;border:1px solid transparent;transition:all .15s;cursor:pointer;animation:rowIn .2s ease forwards;opacity:0}
@keyframes rowIn{from{opacity:0;transform:translateY(4px)}to{opacity:1;transform:translateY(0)}}
.file-item:hover{background:var(--blue-dim);border-color:var(--border)}
.file-icon{width:34px;height:34px;border-radius:4px;display:flex;align-items:center;justify-content:center;font-size:16px;flex-shrink:0;border:1px solid var(--border)}
.ic-img{background:rgba(239,68,68,.1);border-color:rgba(239,68,68,.2)}
.ic-video{background:rgba(59,130,246,.1);border-color:rgba(59,130,246,.2)}
.ic-audio{background:rgba(234,179,8,.1);border-color:rgba(234,179,8,.2)}
.ic-doc{background:rgba(34,197,94,.1);border-color:rgba(34,197,94,.2)}
.ic-code{background:rgba(59,130,246,.1);border-color:rgba(59,130,246,.2)}
.ic-arch{background:rgba(234,179,8,.1);border-color:rgba(234,179,8,.2)}
.ic-data{background:rgba(34,197,94,.1);border-color:rgba(34,197,94,.2)}
.ic-other{background:var(--surface);border-color:var(--border)}
.file-meta-col{flex:1;min-width:0}
.file-name{font-size:13px;font-weight:500;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;color:var(--text);margin-bottom:2px}
.file-sub{font-size:10px;font-family:'IBM Plex Mono',monospace;color:var(--text-3);display:flex;gap:6px;align-items:center}
.tag{padding:1px 5px;border-radius:2px;font-size:10px;font-family:'IBM Plex Mono',monospace;font-weight:500,letter-spacing:.3px}
.tag-img{background:rgba(239,68,68,.15);color:var(--red)}
.tag-video{background:rgba(59,130,246,.15);color:var(--blue)}
.tag-audio{background:rgba(234,179,8,.15);color:var(--yellow)}
.tag-doc{background:rgba(34,197,94,.15);color:var(--green)}
.tag-code{background:rgba(59,130,246,.15);color:var(--blue)}
.tag-arch{background:rgba(234,179,8,.15);color:var(--yellow)}
.tag-data{background:rgba(34,197,94,.15);color:var(--green)}
.tag-other{background:var(--border);color:var(--text-3)}
.file-actions{display:flex;gap:4px;opacity:0;transition:opacity .15s}
.file-item:hover .file-actions{opacity:1}
.icon-btn{width:28px;height:28px;border-radius:4px;border:1px solid var(--border2);background:var(--panel);color:var(--text-2);font-size:13px;cursor:pointer;display:flex;align-items:center;justify-content:center;text-decoration:none;transition:all .15s}
.icon-btn:hover{background:var(--blue);color:#fff;border-color:var(--blue)}
.icon-btn.dl:hover{background:var(--green);color:#fff;border-color:var(--green)}
.icon-btn.sh:hover{background:var(--yellow);color:#fff;border-color:var(--yellow)}
.icon-btn.chk:hover{background:var(--green);color:#fff;border-color:var(--green)}

.file-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(110px,1fr));gap:8px;padding:8px}
.grid-card{background:var(--surface);border:1px solid var(--border);border-radius:7px;padding:16px 10px 12px;text-align:center;cursor:pointer;transition:all .15s;animation:fadeIn .25s ease forwards;opacity:0}
.grid-card:hover{border-color:var(--blue);background:var(--blue-dim);transform:translateY(-2px);box-shadow:0 4px 16px var(--shadow)}
@keyframes fadeIn{to{opacity:1}}
.grid-icon{font-size:28px;margin-bottom:8px;display:block}
.grid-label{font-size:11px;font-weight:500;overflow:hidden;white-space:nowrap;text-overflow:ellipsis;margin-bottom:8px;color:var(--text)}
.grid-tag{display:inline-block;margin-bottom:8px}
.grid-dl{display:block;opacity:0;transition:opacity .15s}
.grid-card:hover .grid-dl{opacity:1}
.empty-state{text-align:center;padding:50px 20px;color:var(--text-3)}
.empty-state .e-icon{font-size:38px;margin-bottom:10px;opacity:.4;display:block}
.empty-state p{font-size:12px;font-family:'IBM Plex Mono',monospace}

/* ── PREVIEW ─────────────────────────────── */
.preview-placeholder{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;color:var(--text-3);gap:12px}
.preview-placeholder .big-icon{font-size:48px;opacity:.25}
.preview-placeholder p{font-size:12px;font-family:'IBM Plex Mono',monospace}
.preview-pane{flex:1;overflow:auto;display:none;flex-direction:column}
.preview-pane.active{display:flex}
.preview-header{padding:10px 16px;border-bottom:1px solid var(--border);display:flex;align-items:center;gap:10px;background:var(--panel);flex-shrink:0}
.preview-filename{font-family:'IBM Plex Mono',monospace;font-size:12px;font-weight:500;color:var(--text);flex:1;overflow:hidden;white-space:nowrap;text-overflow:ellipsis}
.preview-body{flex:1;overflow:auto;display:flex;align-items:center;justify-content:center;padding:20px;background:var(--bg)}
.preview-body img,.preview-body video{max-width:100%;max-height:calc(100vh - 200px);border-radius:7px;border:1px solid var(--border)}
.preview-body audio{width:100%}
.preview-body pre{text-align:left;font-family:'IBM Plex Mono',monospace;font-size:12px;color:var(--green);white-space:pre-wrap;line-height:1.75;width:100%;background:var(--surface);padding:16px;border-radius:7px;border:1px solid var(--border);overflow:auto}
.preview-body iframe{width:100%;height:calc(100vh - 180px);border:none;border-radius:7px}

/* ── SHARE MODAL ─────────────────────────── */
.modal-backdrop{position:fixed;inset:0;background:var(--modal-bg);z-index:500;display:none;align-items:center;justify-content:center;padding:16px}
.modal-backdrop.open{display:flex}
.modal{background:var(--surface);border:1px solid var(--border);border-radius:12px;width:100%;max-width:420px;overflow:hidden;animation:modalIn .22s ease}
@keyframes modalIn{from{opacity:0;transform:scale(.95)}to{opacity:1;transform:scale(1)}}
.modal-head{padding:16px 20px;border-bottom:1px solid var(--border);display:flex;align-items:center;justify-content:space-between}
.modal-head h2{font-size:15px;font-weight:600;color:var(--text)}
.modal-close{width:28px;height:28px;border:none;background:none;color:var(--text-3);font-size:18px;cursor:pointer;border-radius:4px;display:flex;align-items:center;justify-content:center}
.modal-close:hover{background:var(--red-dim);color:var(--red)}
.modal-body{padding:20px;display:flex;flex-direction:column;gap:16px}
.share-url-row{display:flex;gap:8px}
.share-url-box{flex:1;background:var(--bg);border:1px solid var(--border2);border-radius:6px;padding:8px 12px;font-family:'IBM Plex Mono',monospace;font-size:12px;color:var(--text);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.qr-wrap{display:flex;justify-content:center;padding:8px;background:var(--bg);border:1px solid var(--border);border-radius:8px}
#qrCanvas{border-radius:6px}
.share-actions{display:flex;gap:8px;flex-wrap:wrap}
.share-actions .btn{flex:1;min-width:100px;justify-content:center}
.share-label{font-size:11px;color:var(--text-3);font-family:'IBM Plex Mono',monospace;text-align:center}

/* ── PEERS MODAL ─────────────────────────── */
.peer-card{padding:10px 12px;border:1px solid var(--border);border-radius:6px;background:var(--bg);display:flex;flex-direction:column;gap:3px}
.peer-card .pc-name{font-size:13px;font-weight:500;color:var(--text)}
.peer-card .pc-ip{font-family:'IBM Plex Mono',monospace;font-size:11px;color:var(--text-2)}
.peer-card .pc-time{font-family:'IBM Plex Mono',monospace;font-size:10px;color:var(--text-3)}
.peer-count-badge{background:var(--blue-dim);border:1px solid var(--blue);border-radius:99px;padding:2px 8px;font-family:'IBM Plex Mono',monospace;font-size:10px;color:var(--blue)}

/* ── TOAST ───────────────────────────────── */
#toast-stack{position:fixed;bottom:20px;right:20px;z-index:999;display:flex;flex-direction:column;gap:6px;pointer-events:none}
.toast{padding:9px 16px;border-radius:4px;font-size:12px;font-family:'IBM Plex Mono',monospace;border:1px solid;animation:toastSlide .25s ease forwards;box-shadow:0 4px 16px var(--shadow);max-width:300px}
.toast.success{background:rgba(34,197,94,.12);border-color:rgba(34,197,94,.35);color:var(--green)}
.toast.error{background:rgba(239,68,68,.12);border-color:rgba(239,68,68,.35);color:var(--red)}
.toast.info{background:rgba(59,130,246,.12);border-color:rgba(59,130,246,.35);color:var(--blue)}
.toast.warn{background:rgba(234,179,8,.12);border-color:rgba(234,179,8,.35);color:var(--yellow)}
@keyframes toastSlide{from{opacity:0;transform:translateX(16px)}to{opacity:1;transform:translateX(0)}}

/* ── MOBILE OVERLAY ─────────────────────── */
@media(max-width:720px){
  .hamburger{display:flex}
  .nav-info{display:none}
  .content{grid-template-columns:1fr}
  .left-panel{
    position:fixed;top:48px;left:0;bottom:0;z-index:200;width:min(340px,92vw);
    transform:translateX(-110%);box-shadow:4px 0 24px var(--shadow);
  }
  .left-panel.open{transform:translateX(0)}
  .mobile-overlay{position:fixed;inset:0;top:48px;background:var(--modal-bg);z-index:199;display:none}
  .mobile-overlay.open{display:block}
  .right-panel{grid-column:1}
  .file-actions{opacity:1}
  .grid-dl{opacity:1}
}
@media(min-width:721px){
  .mobile-overlay{display:none!important}
}
</style>
</head>
<body>
<div class="app-shell">

  <nav class="navbar">
    <button class="hamburger" id="hamburger" onclick="toggleSidebar()" aria-label="Menu">☰</button>

    <div class="nav-brand">
      <div class="nav-logo">⚡</div>
      <span>FileWave Pro</span>
    </div>
    <div class="nav-sep"></div>

    <div class="nav-pill offline" id="statusPill">
      <span class="dot"></span>
      <span id="statusText">CHECKING…</span>
    </div>

    <div class="nav-spacer"></div>

    <div class="nav-info" id="urlDisplay">Connecting…</div>

    <button class="nav-icon-btn" onclick="openShareModal()" title="Share Server">📡</button>
    <button class="nav-icon-btn" id="peerBtn" onclick="openPeersModal()" title="Connected Peers">👥</button>
    <a class="nav-icon-btn" href="/simple" title="Simple Mode — no JS required" style="text-decoration:none">📟</a>
    <button class="nav-icon-btn" id="themeBtn" onclick="toggleTheme()" title="Toggle theme">🌙</button>
  </nav>

  <div class="mobile-overlay" id="mobileOverlay" onclick="closeSidebar()"></div>

  <div class="content">

    <div class="left-panel" id="leftPanel">

      <div class="upload-area">
        <div class="section-title" style="margin-bottom:10px"><span>📤</span> Upload Files</div>
        <div class="drop-zone" id="dropZone" onclick="document.getElementById('fileInput').click()">
          <span class="drop-icon">📂</span>
          <h3>Drop files here</h3>
          <p>or tap to browse</p>
          <input type="file" id="fileInput" multiple onchange="uploadFiles(this.files)">
        </div>
        <div class="upload-btn-row">
          <button class="btn btn-primary" onclick="document.getElementById('fileInput').click()">Choose Files</button>
        </div>
        <div class="progress-wrap" id="progressWrap">
          <div class="progress-row">
            <span id="progressLabel">Uploading…</span>
            <span id="progressPct">0%</span>
          </div>
          <div class="progress-track"><div class="progress-fill" id="progressFill"></div></div>
        </div>
      </div>

      <div class="stats-strip">
        <div class="stat-item"><span style="color:var(--blue)">●</span><strong id="statCount">0</strong> files</div>
        <div class="stat-item"><span style="color:var(--green)">●</span><strong id="statTypes">—</strong> types</div>
        <div class="stat-item"><span style="color:var(--yellow)">●</span><strong id="statPeers">0</strong> peers</div>
        <div class="stat-item" id="statFilterWrap" style="display:none">
          <span style="color:var(--yellow)">◆</span><strong id="statFiltered">0</strong> shown
        </div>
      </div>

      <div class="toolbar">
        <div class="search-field">
          <span class="ico">🔍</span>
          <input type="text" id="searchInput" placeholder="Filter files…" oninput="filterFiles()">
        </div>
        <select class="sort-sel" id="sortSelect" onchange="renderFiles()">
          <option value="name">A → Z</option>
          <option value="name-desc">Z → A</option>
          <option value="ext">By Type</option>
        </select>
        <div class="view-grp">
          <button class="view-btn active" id="btnList" onclick="setView('list')" title="List">☰</button>
          <button class="view-btn" id="btnGrid" onclick="setView('grid')" title="Grid">⊞</button>
        </div>
      </div>

      <div class="file-scroll" id="fileContainer"></div>
    </div>

    <div class="right-panel">
      <div class="section-head">
        <div class="section-title"><span>👁</span> Preview</div>
        <button class="btn btn-ghost btn-sm" onclick="closePrev()">Clear</button>
      </div>
      <div class="preview-placeholder" id="previewPlaceholder">
        <span class="big-icon">📄</span>
        <p>Select a file to preview</p>
      </div>
      <div class="preview-pane" id="previewPane">
        <div class="preview-header">
          <span id="prevIcon" style="font-size:16px">📄</span>
          <span class="preview-filename" id="prevName">—</span>
          <a class="btn btn-ghost btn-sm dl" id="prevDownload" href="#" download>⬇ Download</a>
        </div>
        <div class="preview-body" id="previewBody"></div>
      </div>
    </div>
  </div>
</div>

<!-- ── SHARE MODAL ───────────────────────── -->
<div class="modal-backdrop" id="shareModal">
  <div class="modal">
    <div class="modal-head">
      <h2>📡 Share This Server</h2>
      <button class="modal-close" onclick="closeShareModal()">✕</button>
    </div>
    <div class="modal-body">
      <div class="share-label">📶 Network URL (same Wi-Fi)</div>
      <div class="share-url-row">
        <div class="share-url-box" id="shareUrlBox">—</div>
        <button class="btn btn-primary" onclick="copyShareUrl()">Copy</button>
      </div>
      <div class="qr-wrap"><div id="qrCanvas"></div></div>
      <div class="share-actions">
        <button class="btn btn-ghost" onclick="nativeShare()" id="nativeShareBtn" style="display:none">↗ Share…</button>
        <button class="btn btn-ghost" onclick="openShareUrl()">🌐 Open</button>
        <button class="btn btn-primary" onclick="copyShareUrl()">📋 Copy Link</button>
      </div>
    </div>
  </div>
</div>

<!-- ── PEERS MODAL ──────────────────────── -->
<div class="modal-backdrop" id="peersModal">
  <div class="modal">
    <div class="modal-head">
      <h2>👥 Connected Peers</h2>
      <button class="modal-close" onclick="closePeersModal()">✕</button>
    </div>
    <div class="modal-body" id="peersBody" style="max-height:360px;overflow-y:auto">
      <p style="font-family:'IBM Plex Mono',monospace;font-size:12px;color:var(--text-3)">Loading…</p>
    </div>
  </div>
</div>

<div id="toast-stack"></div>

<script>
let allFiles = [], currentView = 'list', activeFile = null;
let currentNetUrl = '';

const TYPES = {
  img:   ['png','jpg','jpeg','gif','webp','svg','bmp','ico'],
  video: ['mp4','mov','avi','mkv','webm'],
  audio: ['mp3','wav','ogg','flac','aac','m4a'],
  doc:   ['pdf','doc','docx','xls','xlsx','ppt','pptx'],
  code:  ['py','js','ts','html','css','json','xml','sh','c','cpp','java','rb','go','rs','md','yaml','yml'],
  arch:  ['zip','rar','gz','tar','7z'],
  data:  ['csv','tsv','sql','db'],
};
const ICONS = {img:'🖼️',video:'🎬',audio:'🎵',doc:'📄',code:'⚡',arch:'📦',data:'📊',other:'📃'};

function getExt(f){return f.split('.').pop().toLowerCase()}
function classify(f){const e=getExt(f);for(const[k,v]of Object.entries(TYPES))if(v.includes(e))return k;return 'other'}
function icon(f){return ICONS[classify(f)]}
function icClass(f){return 'ic-'+classify(f)}
function tagClass(f){return 'tag-'+classify(f)}
function tagLabel(f){return getExt(f).toUpperCase()}

const themeBtn = document.getElementById('themeBtn');
function applyTheme(t){
  document.documentElement.setAttribute('data-theme',t);
  themeBtn.textContent = t==='dark'?'🌙':'☀️';
  localStorage.setItem('fw-theme',t);
}
(function(){applyTheme(localStorage.getItem('fw-theme')||'dark')})();
function toggleTheme(){
  applyTheme(document.documentElement.getAttribute('data-theme')==='dark'?'light':'dark');
}

function toggleSidebar(){
  const lp=document.getElementById('leftPanel'),ov=document.getElementById('mobileOverlay');
  const open=lp.classList.toggle('open');
  ov.classList.toggle('open',open);
}
function closeSidebar(){
  document.getElementById('leftPanel').classList.remove('open');
  document.getElementById('mobileOverlay').classList.remove('open');
}

const pill=document.getElementById('statusPill');
const pillTxt=document.getElementById('statusText');
const urlDisp=document.getElementById('urlDisplay');

async function checkStatus(){
  try{
    const r=await fetch('/api/status',{cache:'no-store'});
    if(r.ok){
      const d=await r.json();
      pill.className='nav-pill live';
      pillTxt.textContent='LIVE';
      const u=d.url||window.location.host;
      urlDisp.textContent=u;
      currentNetUrl=d.url||window.location.href;
    }else throw 0;
  }catch{
    pill.className='nav-pill offline';
    pillTxt.textContent='OFFLINE';
    urlDisp.textContent='Server unreachable';
  }
}
checkStatus();
setInterval(checkStatus,5000);

async function loadFiles(){
  try{
    const r=await fetch('/api/list');
    allFiles=await r.json();
    updateStats(allFiles);
    renderFiles();
  }catch{toast('Failed to load file list','error')}
}

function updateStats(filtered){
  document.getElementById('statCount').textContent=allFiles.length;
  const types=[...new Set(allFiles.map(classify))];
  document.getElementById('statTypes').textContent=types.join(', ')||'—';
  const wrap=document.getElementById('statFilterWrap');
  if(filtered.length!==allFiles.length){
    wrap.style.display='flex';
    document.getElementById('statFiltered').textContent=filtered.length;
  }else wrap.style.display='none';
}

async function refreshPeerCount(){
  try{
    const r=await fetch('/api/peers');
    const peers=await r.json();
    document.getElementById('statPeers').textContent=peers.length;
  }catch{}
}
refreshPeerCount();
setInterval(refreshPeerCount,8000);

function filterFiles(){renderFiles()}

function setView(v){
  currentView=v;
  document.getElementById('btnList').classList.toggle('active',v==='list');
  document.getElementById('btnGrid').classList.toggle('active',v==='grid');
  renderFiles();
}

function renderFiles(){
  const q=document.getElementById('searchInput').value.toLowerCase();
  const sort=document.getElementById('sortSelect').value;
  const box=document.getElementById('fileContainer');
  let files=allFiles.filter(f=>f.toLowerCase().includes(q));
  updateStats(files);
  if(sort==='name')files.sort((a,b)=>a.localeCompare(b));
  else if(sort==='name-desc')files.sort((a,b)=>b.localeCompare(a));
  else if(sort==='ext')files.sort((a,b)=>classify(a).localeCompare(classify(b)));
  if(!files.length){
    box.innerHTML=`<div class="empty-state"><span class="e-icon">📭</span><p>No files found</p></div>`;
    return;
  }
  if(currentView==='list'){
    box.innerHTML=`<div class="file-list">${files.map((f,i)=>`
      <div class="file-item" style="animation-delay:${i*.03}s" onclick="preview('${encodeURIComponent(f)}','${f.replace(/'/g,"\\'")}')">
        <div class="file-icon ${icClass(f)}">${icon(f)}</div>
        <div class="file-meta-col">
          <div class="file-name">${f}</div>
          <div class="file-sub"><span class="tag ${tagClass(f)}">${tagLabel(f)}</span></div>
        </div>
        <div class="file-actions">
          <button class="icon-btn sh" onclick="quickShare(event,'${encodeURIComponent(f)}','${f.replace(/'/g,"\\'")}')">📤</button>
          <button class="icon-btn chk" onclick="showChecksum(event,'${encodeURIComponent(f)}','${f.replace(/'/g,"\\'")}')">🔐</button>
          <a class="icon-btn dl" href="/files/${encodeURIComponent(f)}" download onclick="event.stopPropagation()" title="Download">⬇</a>
        </div>
      </div>`).join('')}</div>`;
  }else{
    box.innerHTML=`<div class="file-grid">${files.map((f,i)=>`
      <div class="grid-card" style="animation-delay:${i*.03}s" onclick="preview('${encodeURIComponent(f)}','${f.replace(/'/g,"\\'")}')">
        <span class="grid-icon">${icon(f)}</span>
        <div class="grid-label">${f}</div>
        <span class="tag ${tagClass(f)} grid-tag">${tagLabel(f)}</span>
        <a class="icon-btn dl grid-dl" href="/files/${encodeURIComponent(f)}" download onclick="event.stopPropagation()">⬇</a>
      </div>`).join('')}</div>`;
  }
}

function uploadFiles(files){
  const wrap=document.getElementById('progressWrap'),
        fill=document.getElementById('progressFill'),
        label=document.getElementById('progressLabel'),
        pct=document.getElementById('progressPct');
  wrap.classList.add('active');
  let total=files.length,done=0;
  Array.from(files).forEach(file=>{
    const fd=new FormData();fd.append('file',file);
    fetch('/api/upload',{method:'POST',body:fd}).then(()=>{
      done++;
      const p=Math.round((done/total)*100);
      fill.style.width=p+'%';pct.textContent=p+'%';
      label.textContent=`Uploading ${done} of ${total}…`;
      if(done===total){
        label.textContent=`✓ ${total} file(s) ready`;
        setTimeout(()=>{wrap.classList.remove('active');fill.style.width='0%'},2000);
        loadFiles();toast(`${total} file(s) uploaded`,'success');
      }
    }).catch(()=>toast('Upload failed','error'));
  });
}

const dz=document.getElementById('dropZone');
['dragover','dragenter'].forEach(e=>dz.addEventListener(e,ev=>{ev.preventDefault();dz.classList.add('drag-over')}));
['dragleave','dragend','drop'].forEach(e=>dz.addEventListener(e,ev=>{ev.preventDefault();dz.classList.remove('drag-over')}));
dz.addEventListener('drop',ev=>{ev.preventDefault();if(ev.dataTransfer.files.length)uploadFiles(ev.dataTransfer.files)});

function preview(enc,fname){
  activeFile=fname;
  const ext=getExt(fname),url=`/view/${enc}`,body=document.getElementById('previewBody');
  document.getElementById('prevName').textContent=fname;
  document.getElementById('prevIcon').textContent=icon(fname);
  document.getElementById('prevDownload').href=`/files/${enc}`;
  document.getElementById('prevDownload').download=fname;
  const type=classify(fname);
  if(type==='img')body.innerHTML=`<img src="${url}" alt="${fname}">`;
  else if(type==='video')body.innerHTML=`<video src="${url}" controls></video>`;
  else if(type==='audio')body.innerHTML=`<div style="text-align:center;width:100%"><div style="font-size:56px;margin-bottom:24px;opacity:.5">${icon(fname)}</div><audio src="${url}" controls style="width:80%"></audio></div>`;
  else if(type==='code'||['txt','md','json','xml','csv','yaml','yml'].some(x=>ext===x))
    fetch(url).then(r=>r.text()).then(t=>{body.innerHTML=`<pre>${t.replace(/</g,'&lt;')}</pre>`});
  else if(ext==='pdf')body.innerHTML=`<iframe src="${url}"></iframe>`;
  else body.innerHTML=`<div style="text-align:center;color:var(--text-3)"><div style="font-size:56px;margin-bottom:16px;opacity:.3">${icon(fname)}</div><p style="font-family:var(--mono);font-size:12px;margin-bottom:16px">No preview for .${ext.toUpperCase()}</p><a class="btn btn-primary" href="/files/${enc}" download>⬇ Download File</a></div>`;
  document.getElementById('previewPlaceholder').style.display='none';
  document.getElementById('previewPane').classList.add('active');
  closeSidebar();
}
function closePrev(){
  document.getElementById('previewPane').classList.remove('active');
  document.getElementById('previewPlaceholder').style.display='';
  document.getElementById('previewBody').innerHTML='';
  activeFile=null;
}
document.addEventListener('keydown',e=>{if(e.key==='Escape'){closePrev();closeShareModal();closePeersModal()}});

let qrGenerated=false;
function openShareModal(){
  const modal=document.getElementById('shareModal');
  const url=currentNetUrl||window.location.href;
  document.getElementById('shareUrlBox').textContent=url;
  modal.classList.add('open');
  if(!qrGenerated){
    const qc=document.getElementById('qrCanvas');
    qc.innerHTML='';
    new QRCode(qc,{text:url,width:180,height:180,colorDark:'#3b82f6',colorLight:'#111318',correctLevel:QRCode.CorrectLevel.H});
    qrGenerated=false;
  }
  if(navigator.share)document.getElementById('nativeShareBtn').style.display='';
}
function closeShareModal(){document.getElementById('shareModal').classList.remove('open')}
document.getElementById('shareModal').addEventListener('click',function(e){if(e.target===this)closeShareModal()});

function copyShareUrl(){
  const url=currentNetUrl||window.location.href;
  navigator.clipboard.writeText(url).then(()=>toast('Link copied!','success')).catch(()=>{
    const ta=document.createElement('textarea');ta.value=url;
    document.body.appendChild(ta);ta.select();document.execCommand('copy');
    document.body.removeChild(ta);toast('Link copied!','success');
  });
}
function openShareUrl(){window.open(currentNetUrl||window.location.href,'_blank')}
function nativeShare(){
  if(navigator.share)navigator.share({title:'FileWave Pro',url:currentNetUrl||window.location.href}).catch(()=>{});
}

function quickShare(evt,enc,fname){
  evt.stopPropagation();
  const base=currentNetUrl||window.location.origin;
  const url=`${base}/files/${enc}`;
  if(navigator.share){
    navigator.share({title:fname,url}).catch(()=>copyToClipboard(url,fname));
  }else{
    copyToClipboard(url,fname);
  }
}
function copyToClipboard(url,fname){
  navigator.clipboard.writeText(url).then(()=>toast(`Link for "${fname}" copied!`,'success')).catch(()=>toast('Copy failed','error'));
}

async function openPeersModal(){
  const modal=document.getElementById('peersModal');
  modal.classList.add('open');
  const body=document.getElementById('peersBody');
  body.innerHTML='<p style="font-family:\'IBM Plex Mono\',monospace;font-size:12px;color:var(--text-3)">Loading peers…</p>';
  try{
    const r=await fetch('/api/peers');
    const peers=await r.json();
    if(!peers.length){
      body.innerHTML='<p style="font-family:\'IBM Plex Mono\',monospace;font-size:12px;color:var(--text-3)">No peers have connected yet.</p>';
      return;
    }
    body.style.display='flex';
    body.style.flexDirection='column';
    body.style.gap='8px';
    body.innerHTML=`
      <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:4px">
        <span style="font-size:11px;color:var(--text-3);font-family:'IBM Plex Mono',monospace">ACTIVE PEERS</span>
        <span class="peer-count-badge">${peers.length} connected</span>
      </div>
      ${peers.map(p=>`
        <div class="peer-card">
          <div class="pc-name">${p.device} &nbsp;·&nbsp; ${p.browser}</div>
          <div class="pc-ip">IP: <strong style="color:var(--text)">${p.ip}</strong> &nbsp;·&nbsp; ${p.requests} request(s)</div>
          <div class="pc-time">First: ${p.first_seen} &nbsp;·&nbsp; Last seen: ${p.last_seen}</div>
        </div>`).join('')}`;
  }catch{
    body.innerHTML='<p style="color:var(--red);font-size:12px;font-family:\'IBM Plex Mono\',monospace">Failed to load peers.</p>';
  }
}
function closePeersModal(){document.getElementById('peersModal').classList.remove('open')}
document.getElementById('peersModal').addEventListener('click',function(e){if(e.target===this)closePeersModal()});

async function showChecksum(evt,enc,fname){
  evt.stopPropagation();
  toast('Computing SHA-256…','info');
  try{
    const r=await fetch('/api/checksum/'+enc);
    if(!r.ok) throw new Error('not found');
    const d=await r.json();
    navigator.clipboard.writeText(d.sha256).catch(()=>{});
    toast('SHA-256: '+d.sha256.slice(0,20)+'… (copied!)','success');
  }catch(e){
    toast('Checksum failed','error');
  }
}

function toast(msg,type='info'){
  const stack=document.getElementById('toast-stack'),el=document.createElement('div');
  el.className=`toast ${type}`;
  const prefix={success:'✓',error:'✗',info:'ℹ',warn:'⚠'}[type]||'•';
  el.textContent=`${prefix}  ${msg}`;
  stack.appendChild(el);
  setTimeout(()=>el.remove(),3200);
}

loadFiles();
</script>
</body>
</html>"""

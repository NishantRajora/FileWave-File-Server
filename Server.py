import http.server
import socketserver
import socket
import os
import threading
import tkinter as tk
from tkinter import filedialog, scrolledtext, ttk
import webbrowser
from pathlib import Path
import urllib.parse
import json
import mimetypes
import time

PORT = 8000
server = None
log_queue = []

# ─────────────────────────────────────────────
# CLIENT-SIDE HTML PAGE
# ─────────────────────────────────────────────
def render_page():
    return r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>FileWave Pro</title>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
  :root {
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

    --radius-sm: 4px;
    --radius:    7px;
    --radius-lg: 10px;

    --font:      'IBM Plex Sans', sans-serif;
    --mono:      'IBM Plex Mono', monospace;
  }

  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    font-family: var(--font);
    background: var(--bg);
    color: var(--text);
    min-height: 100vh;
    font-size: 14px;
    line-height: 1.5;
  }

  /* ── Layout ── */
  .app-shell {
    display: grid;
    grid-template-rows: 48px 1fr;
    height: 100vh;
    overflow: hidden;
  }

  /* ── Top Nav Bar ── */
  .navbar {
    background: var(--panel);
    border-bottom: 1px solid var(--border);
    display: flex;
    align-items: center;
    padding: 0 20px;
    gap: 16px;
    flex-shrink: 0;
  }

  .nav-brand {
    display: flex;
    align-items: center;
    gap: 9px;
    font-weight: 600;
    font-size: 15px;
    letter-spacing: -0.2px;
    color: var(--text);
  }

  .nav-logo {
    width: 26px; height: 26px;
    background: var(--blue);
    border-radius: var(--radius-sm);
    display: flex; align-items: center; justify-content: center;
    font-size: 13px;
  }

  .nav-sep {
    width: 1px;
    height: 20px;
    background: var(--border);
    margin: 0 4px;
  }

  .nav-pill {
    display: flex;
    align-items: center;
    gap: 5px;
    padding: 3px 10px;
    border-radius: 20px;
    font-family: var(--mono);
    font-size: 11px;
    font-weight: 500;
    letter-spacing: 0.3px;
    border: 1px solid;
  }

  .nav-pill.live   { color: var(--green); border-color: rgba(34,197,94,0.35); background: var(--green-dim); }
  .nav-pill.offline { color: var(--red); border-color: rgba(239,68,68,0.35); background: var(--red-dim); }

  .nav-pill .dot {
    width: 6px; height: 6px;
    border-radius: 50%;
    background: currentColor;
  }

  .nav-pill.live .dot { animation: blink 1.8s ease-in-out infinite; }

  @keyframes blink {
    0%,100% { opacity: 1; }
    50%      { opacity: 0.35; }
  }

  .nav-spacer { flex: 1; }

  .nav-info {
    font-family: var(--mono);
    font-size: 11px;
    color: var(--text-3);
  }

  /* ── Main content ── */
  .content {
    display: grid;
    grid-template-columns: 340px 1fr;
    overflow: hidden;
  }

  /* ── Left Panel ── */
  .left-panel {
    background: var(--surface);
    border-right: 1px solid var(--border);
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  /* ── Right Panel ── */
  .right-panel {
    display: flex;
    flex-direction: column;
    overflow: hidden;
    background: var(--bg);
  }

  /* ── Section headers ── */
  .section-head {
    padding: 12px 16px 10px;
    border-bottom: 1px solid var(--border);
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-shrink: 0;
  }

  .section-title {
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    color: var(--text-3);
    display: flex;
    align-items: center;
    gap: 7px;
  }

  .section-title .icon { font-size: 13px; }

  /* ── Upload zone ── */
  .upload-area {
    padding: 14px;
    border-bottom: 1px solid var(--border);
    flex-shrink: 0;
  }

  .drop-zone {
    border: 1.5px dashed var(--border2);
    border-radius: var(--radius);
    padding: 22px 16px;
    text-align: center;
    cursor: pointer;
    transition: all 0.18s ease;
    background: var(--bg);
  }

  .drop-zone:hover, .drop-zone.drag-over {
    border-color: var(--blue);
    background: var(--blue-dim);
  }

  .drop-icon {
    font-size: 26px;
    margin-bottom: 8px;
    display: block;
  }

  .drop-zone h3 {
    font-size: 13px;
    font-weight: 600;
    color: var(--text);
    margin-bottom: 3px;
  }

  .drop-zone p {
    font-size: 11px;
    color: var(--text-3);
    font-family: var(--mono);
  }

  #fileInput { display: none; }

  .btn {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 7px 14px;
    border-radius: var(--radius-sm);
    border: 1px solid transparent;
    font-family: var(--font);
    font-weight: 500;
    font-size: 13px;
    cursor: pointer;
    transition: all 0.15s;
    line-height: 1;
  }

  .btn-primary {
    background: var(--blue);
    color: #fff;
    border-color: var(--blue);
  }
  .btn-primary:hover { background: #2563eb; border-color: #2563eb; }

  .btn-ghost {
    background: transparent;
    color: var(--text-2);
    border-color: var(--border2);
  }
  .btn-ghost:hover { background: var(--panel); color: var(--text); border-color: var(--blue); }

  .btn-danger {
    background: transparent;
    color: var(--red);
    border-color: rgba(239,68,68,0.4);
  }
  .btn-danger:hover { background: var(--red-dim); }

  .btn-sm { padding: 4px 10px; font-size: 12px; }

  .upload-btn-row {
    margin-top: 10px;
    display: flex;
    justify-content: center;
  }

  /* ── Progress ── */
  .progress-wrap {
    margin-top: 12px;
    display: none;
  }
  .progress-wrap.active { display: block; }

  .progress-row {
    display: flex;
    justify-content: space-between;
    font-family: var(--mono);
    font-size: 11px;
    color: var(--text-3);
    margin-bottom: 6px;
  }

  .progress-track {
    height: 4px;
    background: var(--border);
    border-radius: 99px;
    overflow: hidden;
  }

  .progress-fill {
    height: 100%;
    background: var(--blue);
    border-radius: 99px;
    width: 0%;
    transition: width 0.25s ease;
  }

  /* ── Stats strip ── */
  .stats-strip {
    padding: 8px 16px;
    border-bottom: 1px solid var(--border);
    display: flex;
    gap: 18px;
    flex-shrink: 0;
  }

  .stat-item {
    display: flex;
    align-items: center;
    gap: 5px;
    font-family: var(--mono);
    font-size: 11px;
    color: var(--text-3);
  }

  .stat-item strong { color: var(--text); font-weight: 500; }
  .stat-item .dot-blue  { color: var(--blue); }
  .stat-item .dot-green { color: var(--green); }
  .stat-item .dot-yellow{ color: var(--yellow); }

  /* ── Toolbar ── */
  .toolbar {
    padding: 10px 14px;
    border-bottom: 1px solid var(--border);
    display: flex;
    gap: 8px;
    align-items: center;
    flex-shrink: 0;
  }

  .search-field {
    flex: 1;
    display: flex;
    align-items: center;
    gap: 7px;
    background: var(--bg);
    border: 1px solid var(--border2);
    border-radius: var(--radius-sm);
    padding: 5px 10px;
    transition: border-color 0.15s;
  }

  .search-field:focus-within { border-color: var(--blue); }

  .search-field input {
    background: none;
    border: none;
    outline: none;
    color: var(--text);
    font-family: var(--mono);
    font-size: 12px;
    width: 100%;
  }

  .search-field .ico { color: var(--text-3); font-size: 13px; }

  .sort-sel {
    background: var(--bg);
    border: 1px solid var(--border2);
    border-radius: var(--radius-sm);
    padding: 5px 8px;
    color: var(--text-2);
    font-family: var(--mono);
    font-size: 11px;
    cursor: pointer;
    outline: none;
  }

  .view-grp {
    display: flex;
    border: 1px solid var(--border2);
    border-radius: var(--radius-sm);
    overflow: hidden;
  }

  .view-btn {
    padding: 5px 10px;
    background: none;
    border: none;
    border-right: 1px solid var(--border2);
    color: var(--text-3);
    cursor: pointer;
    font-size: 13px;
    transition: all 0.15s;
  }

  .view-btn:last-child { border-right: none; }
  .view-btn.active { background: var(--blue-dim); color: var(--blue); }
  .view-btn:hover:not(.active) { background: var(--panel); color: var(--text); }

  /* ── File list ── */
  .file-scroll {
    flex: 1;
    overflow-y: auto;
    padding: 8px;
  }

  ::-webkit-scrollbar { width: 5px; }
  ::-webkit-scrollbar-track { background: transparent; }
  ::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 99px; }

  .file-list { display: flex; flex-direction: column; gap: 2px; }

  .file-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 9px 10px;
    border-radius: var(--radius-sm);
    border: 1px solid transparent;
    transition: all 0.15s;
    cursor: pointer;
    animation: rowIn 0.2s ease forwards;
    opacity: 0;
  }

  @keyframes rowIn {
    from { opacity: 0; transform: translateY(4px); }
    to   { opacity: 1; transform: translateY(0); }
  }

  .file-item:hover {
    background: var(--blue-dim);
    border-color: var(--border);
  }

  .file-icon {
    width: 34px; height: 34px;
    border-radius: var(--radius-sm);
    display: flex; align-items: center; justify-content: center;
    font-size: 16px;
    flex-shrink: 0;
    border: 1px solid var(--border);
  }

  /* type-color badges */
  .ic-img   { background: rgba(239,68,68,0.1);    border-color: rgba(239,68,68,0.2); }
  .ic-video { background: rgba(59,130,246,0.1);   border-color: rgba(59,130,246,0.2); }
  .ic-audio { background: rgba(234,179,8,0.1);    border-color: rgba(234,179,8,0.2); }
  .ic-doc   { background: rgba(34,197,94,0.1);    border-color: rgba(34,197,94,0.2); }
  .ic-code  { background: rgba(59,130,246,0.1);   border-color: rgba(59,130,246,0.2); }
  .ic-arch  { background: rgba(234,179,8,0.1);    border-color: rgba(234,179,8,0.2); }
  .ic-data  { background: rgba(34,197,94,0.1);    border-color: rgba(34,197,94,0.2); }
  .ic-other { background: var(--surface);          border-color: var(--border); }

  .file-meta-col { flex: 1; min-width: 0; }

  .file-name {
    font-size: 13px;
    font-weight: 500;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    color: var(--text);
    margin-bottom: 2px;
  }

  .file-sub {
    font-size: 10px;
    font-family: var(--mono);
    color: var(--text-3);
    display: flex;
    gap: 6px;
    align-items: center;
  }

  .tag {
    padding: 1px 5px;
    border-radius: 2px;
    font-size: 10px;
    font-family: var(--mono);
    font-weight: 500;
    letter-spacing: 0.3px;
  }

  .tag-img   { background: rgba(239,68,68,0.15);  color: var(--red);    }
  .tag-video { background: rgba(59,130,246,0.15); color: var(--blue);   }
  .tag-audio { background: rgba(234,179,8,0.15);  color: var(--yellow); }
  .tag-doc   { background: rgba(34,197,94,0.15);  color: var(--green);  }
  .tag-code  { background: rgba(59,130,246,0.15); color: var(--blue);   }
  .tag-arch  { background: rgba(234,179,8,0.15);  color: var(--yellow); }
  .tag-data  { background: rgba(34,197,94,0.15);  color: var(--green);  }
  .tag-other { background: var(--border);          color: var(--text-3); }

  .file-actions {
    display: flex;
    gap: 4px;
    opacity: 0;
    transition: opacity 0.15s;
  }

  .file-item:hover .file-actions { opacity: 1; }

  .icon-btn {
    width: 28px; height: 28px;
    border-radius: var(--radius-sm);
    border: 1px solid var(--border2);
    background: var(--panel);
    color: var(--text-2);
    font-size: 13px;
    cursor: pointer;
    display: flex; align-items: center; justify-content: center;
    text-decoration: none;
    transition: all 0.15s;
  }

  .icon-btn:hover         { background: var(--blue);    color: #fff; border-color: var(--blue); }
  .icon-btn.del:hover     { background: var(--red);     color: #fff; border-color: var(--red); }
  .icon-btn.dl:hover      { background: var(--green);   color: #fff; border-color: var(--green); }

  /* ── Grid view ── */
  .file-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
    gap: 8px;
    padding: 8px;
  }

  .grid-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 16px 10px 12px;
    text-align: center;
    cursor: pointer;
    transition: all 0.15s;
    animation: fadeIn 0.25s ease forwards;
    opacity: 0;
    position: relative;
  }

  .grid-card:hover {
    border-color: var(--blue);
    background: var(--blue-dim);
    transform: translateY(-2px);
    box-shadow: 0 4px 16px rgba(0,0,0,0.3);
  }

  @keyframes fadeIn { to { opacity: 1; } }

  .grid-icon  { font-size: 30px; margin-bottom: 8px; display: block; }
  .grid-label {
    font-size: 11px;
    font-weight: 500;
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
    margin-bottom: 8px;
    color: var(--text);
  }

  .grid-tag { display: inline-block; margin-bottom: 8px; }

  .grid-dl {
    display: block;
    opacity: 0;
    transition: opacity 0.15s;
  }
  .grid-card:hover .grid-dl { opacity: 1; }

  /* ── Empty state ── */
  .empty-state {
    text-align: center;
    padding: 50px 20px;
    color: var(--text-3);
  }

  .empty-state .e-icon { font-size: 38px; margin-bottom: 10px; opacity: 0.4; display: block; }
  .empty-state p { font-size: 12px; font-family: var(--mono); }

  /* ── Right panel — preview area ── */
  .preview-placeholder {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: var(--text-3);
    gap: 12px;
  }

  .preview-placeholder .big-icon { font-size: 48px; opacity: 0.25; }
  .preview-placeholder p { font-size: 12px; font-family: var(--mono); }

  .preview-pane {
    flex: 1;
    overflow: auto;
    display: none;
    flex-direction: column;
  }

  .preview-pane.active { display: flex; }

  .preview-header {
    padding: 10px 16px;
    border-bottom: 1px solid var(--border);
    display: flex;
    align-items: center;
    gap: 10px;
    background: var(--panel);
    flex-shrink: 0;
  }

  .preview-filename {
    font-family: var(--mono);
    font-size: 12px;
    font-weight: 500;
    color: var(--text);
    flex: 1;
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
  }

  .preview-body {
    flex: 1;
    overflow: auto;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 20px;
    background: var(--bg);
  }

  .preview-body img, .preview-body video {
    max-width: 100%;
    max-height: calc(100vh - 200px);
    border-radius: var(--radius);
    border: 1px solid var(--border);
  }

  .preview-body audio { width: 100%; }

  .preview-body pre {
    text-align: left;
    font-family: var(--mono);
    font-size: 12px;
    color: var(--green);
    white-space: pre-wrap;
    line-height: 1.75;
    width: 100%;
    background: var(--surface);
    padding: 16px;
    border-radius: var(--radius);
    border: 1px solid var(--border);
    overflow: auto;
  }

  .preview-body iframe {
    width: 100%;
    height: calc(100vh - 180px);
    border: none;
    border-radius: var(--radius);
  }

  /* ── Toast ── */
  #toast-stack {
    position: fixed;
    bottom: 20px;
    right: 20px;
    z-index: 999;
    display: flex;
    flex-direction: column;
    gap: 6px;
    pointer-events: none;
  }

  .toast {
    padding: 9px 16px;
    border-radius: var(--radius-sm);
    font-size: 12px;
    font-family: var(--mono);
    border: 1px solid;
    animation: toastSlide 0.25s ease forwards;
    box-shadow: 0 4px 16px rgba(0,0,0,0.4);
    max-width: 300px;
  }

  .toast.success { background: rgba(34,197,94,0.12);  border-color: rgba(34,197,94,0.35);  color: var(--green); }
  .toast.error   { background: rgba(239,68,68,0.12);  border-color: rgba(239,68,68,0.35);  color: var(--red);   }
  .toast.info    { background: rgba(59,130,246,0.12); border-color: rgba(59,130,246,0.35); color: var(--blue);  }
  .toast.warn    { background: rgba(234,179,8,0.12);  border-color: rgba(234,179,8,0.35);  color: var(--yellow);}

  @keyframes toastSlide {
    from { opacity: 0; transform: translateX(16px); }
    to   { opacity: 1; transform: translateX(0); }
  }
</style>
</head>

<body>
<div class="app-shell">

  <!-- ── Nav Bar ── -->
  <nav class="navbar">
    <div class="nav-brand">
      <div class="nav-logo">⚡</div>
      FileWave Pro
    </div>
    <div class="nav-sep"></div>
    <div class="nav-pill offline" id="statusPill">
      <span class="dot"></span>
      <span id="statusText">OFFLINE</span>
    </div>
    <div class="nav-spacer"></div>
    <div class="nav-info" id="urlDisplay">No server running</div>
  </nav>

  <!-- ── Main content ── -->
  <div class="content">

    <!-- ── Left Panel ── -->
    <div class="left-panel">

      <!-- Upload -->
      <div class="upload-area">
        <div class="section-title" style="margin-bottom:10px">
          <span class="icon">📤</span> Upload Files
        </div>

        <div class="drop-zone" id="dropZone" onclick="document.getElementById('fileInput').click()">
          <span class="drop-icon">📂</span>
          <h3>Drop files here</h3>
          <p>or click to browse your device</p>
          <input type="file" id="fileInput" multiple onchange="uploadFiles(this.files)">
        </div>

        <div class="upload-btn-row">
          <button class="btn btn-primary" onclick="document.getElementById('fileInput').click()">
            Choose Files
          </button>
        </div>

        <div class="progress-wrap" id="progressWrap">
          <div class="progress-row">
            <span id="progressLabel">Uploading…</span>
            <span id="progressPct">0%</span>
          </div>
          <div class="progress-track">
            <div class="progress-fill" id="progressFill"></div>
          </div>
        </div>
      </div>

      <!-- Stats strip -->
      <div class="stats-strip">
        <div class="stat-item">
          <span class="dot-blue">●</span>
          <strong id="statCount">0</strong> files
        </div>
        <div class="stat-item">
          <span class="dot-green">●</span>
          <strong id="statTypes">—</strong> types
        </div>
        <div class="stat-item" id="statFilterWrap" style="display:none">
          <span class="dot-yellow">◆</span>
          <strong id="statFiltered">0</strong> shown
        </div>
      </div>

      <!-- Toolbar -->
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

      <!-- File scroll area -->
      <div class="file-scroll" id="fileContainer"></div>
    </div>

    <!-- ── Right Panel (Preview) ── -->
    <div class="right-panel">

      <div class="section-head">
        <div class="section-title"><span class="icon">👁</span> Preview</div>
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

<!-- Toast stack -->
<div id="toast-stack"></div>

<script>
let allFiles = [];
let currentView = 'list';
let activeFile  = null;

// ── File type classification ──
const TYPES = {
  img:   ['png','jpg','jpeg','gif','webp','svg','bmp','ico'],
  video: ['mp4','mov','avi','mkv','webm'],
  audio: ['mp3','wav','ogg','flac','aac','m4a'],
  doc:   ['pdf','doc','docx','xls','xlsx','ppt','pptx'],
  code:  ['py','js','ts','html','css','json','xml','sh','c','cpp','java','rb','go','rs','md','yaml','yml'],
  arch:  ['zip','rar','gz','tar','7z'],
  data:  ['csv','tsv','sql','db'],
};

const ICONS = {
  img:'🖼️', video:'🎬', audio:'🎵', doc:'📄', code:'⚡', arch:'📦', data:'📊', other:'📃'
};

function getExt(f)  { return f.split('.').pop().toLowerCase(); }

function classify(f) {
  const e = getExt(f);
  for (const [k,v] of Object.entries(TYPES)) if (v.includes(e)) return k;
  return 'other';
}

function icon(f)    { return ICONS[classify(f)]; }
function icClass(f) { return 'ic-' + classify(f); }
function tagClass(f){ return 'tag-' + classify(f); }
function tagLabel(f){ return getExt(f).toUpperCase(); }

function setView(v) {
  currentView = v;
  document.getElementById('btnList').classList.toggle('active', v==='list');
  document.getElementById('btnGrid').classList.toggle('active', v==='grid');
  renderFiles();
}

// ── Data loading ──
async function loadFiles() {
  try {
    const r = await fetch('/api/list');
    allFiles = await r.json();
    updateStats(allFiles);
    renderFiles();
  } catch { toast('Failed to load file list', 'error'); }
}

function updateStats(filtered) {
  document.getElementById('statCount').textContent = allFiles.length;
  const types = [...new Set(allFiles.map(classify))];
  document.getElementById('statTypes').textContent = types.join(', ') || '—';

  const wrap = document.getElementById('statFilterWrap');
  if (filtered.length !== allFiles.length) {
    wrap.style.display = 'flex';
    document.getElementById('statFiltered').textContent = filtered.length;
  } else {
    wrap.style.display = 'none';
  }
}

function filterFiles() { renderFiles(); }

function renderFiles() {
  const q    = document.getElementById('searchInput').value.toLowerCase();
  const sort = document.getElementById('sortSelect').value;
  const box  = document.getElementById('fileContainer');

  let files = allFiles.filter(f => f.toLowerCase().includes(q));
  updateStats(files);

  if (sort === 'name')      files.sort((a,b) => a.localeCompare(b));
  else if (sort==='name-desc') files.sort((a,b) => b.localeCompare(a));
  else if (sort==='ext')    files.sort((a,b) => classify(a).localeCompare(classify(b)));

  if (!files.length) {
    box.innerHTML = `<div class="empty-state">
      <span class="e-icon">📭</span><p>No files found</p>
    </div>`;
    return;
  }

  if (currentView === 'list') {
    box.innerHTML = `<div class="file-list">
      ${files.map((f,i) => `
        <div class="file-item" style="animation-delay:${i*0.03}s" onclick="preview('${encodeURIComponent(f)}','${f}')">
          <div class="file-icon ${icClass(f)}">${icon(f)}</div>
          <div class="file-meta-col">
            <div class="file-name">${f}</div>
            <div class="file-sub">
              <span class="tag ${tagClass(f)}">${tagLabel(f)}</span>
            </div>
          </div>
          <div class="file-actions">
            <a class="icon-btn dl" href="/files/${encodeURIComponent(f)}" download onclick="event.stopPropagation()" title="Download">⬇</a>
          </div>
        </div>`).join('')}
    </div>`;
  } else {
    box.innerHTML = `<div class="file-grid">
      ${files.map((f,i) => `
        <div class="grid-card" style="animation-delay:${i*0.03}s" onclick="preview('${encodeURIComponent(f)}','${f}')">
          <span class="grid-icon">${icon(f)}</span>
          <div class="grid-label">${f}</div>
          <span class="tag ${tagClass(f)} grid-tag">${tagLabel(f)}</span>
          <a class="icon-btn dl grid-dl" href="/files/${encodeURIComponent(f)}" download onclick="event.stopPropagation()" title="Download">⬇</a>
        </div>`).join('')}
    </div>`;
  }
}

// ── Upload ──
function uploadFiles(files) {
  const wrap  = document.getElementById('progressWrap');
  const fill  = document.getElementById('progressFill');
  const label = document.getElementById('progressLabel');
  const pct   = document.getElementById('progressPct');

  wrap.classList.add('active');
  let total = files.length, done = 0;

  Array.from(files).forEach(file => {
    const fd = new FormData();
    fd.append('file', file);
    fetch('/api/upload', { method:'POST', body:fd })
      .then(() => {
        done++;
        const p = Math.round((done/total)*100);
        fill.style.width = p + '%';
        pct.textContent  = p + '%';
        label.textContent = `Uploading ${done} of ${total}…`;
        if (done === total) {
          label.textContent = `✓ ${total} file(s) ready`;
          setTimeout(() => { wrap.classList.remove('active'); fill.style.width='0%'; }, 2000);
          loadFiles();
          toast(`${total} file(s) uploaded`, 'success');
        }
      })
      .catch(() => toast('Upload failed', 'error'));
  });
}

// ── Drag & drop ──
const dz = document.getElementById('dropZone');
['dragover','dragenter'].forEach(e => dz.addEventListener(e, ev => { ev.preventDefault(); dz.classList.add('drag-over'); }));
['dragleave','dragend','drop'].forEach(e => dz.addEventListener(e, ev => { ev.preventDefault(); dz.classList.remove('drag-over'); }));
dz.addEventListener('drop', ev => { ev.preventDefault(); if (ev.dataTransfer.files.length) uploadFiles(ev.dataTransfer.files); });

// ── Preview ──
function preview(enc, fname) {
  activeFile = fname;
  const ext  = getExt(fname);
  const url  = `/view/${enc}`;
  const body = document.getElementById('previewBody');

  document.getElementById('prevName').textContent = fname;
  document.getElementById('prevIcon').textContent = icon(fname);
  document.getElementById('prevDownload').href = `/files/${enc}`;
  document.getElementById('prevDownload').download = fname;

  const type = classify(fname);

  if (type === 'img') {
    body.innerHTML = `<img src="${url}" alt="${fname}">`;
  } else if (type === 'video') {
    body.innerHTML = `<video src="${url}" controls></video>`;
  } else if (type === 'audio') {
    body.innerHTML = `<div style="text-align:center;width:100%">
      <div style="font-size:56px;margin-bottom:24px;opacity:0.5">${icon(fname)}</div>
      <audio src="${url}" controls style="width:80%"></audio>
    </div>`;
  } else if (type === 'code' || ['txt','md','json','xml','csv','yaml','yml'].some(x=>ext===x)) {
    fetch(url).then(r=>r.text()).then(t=>{
      body.innerHTML = `<pre>${t.replace(/</g,'&lt;')}</pre>`;
    });
  } else if (ext === 'pdf') {
    body.innerHTML = `<iframe src="${url}"></iframe>`;
  } else {
    body.innerHTML = `<div style="text-align:center;color:var(--text-3)">
      <div style="font-size:56px;margin-bottom:16px;opacity:0.3">${icon(fname)}</div>
      <p style="font-family:var(--mono);font-size:12px;margin-bottom:16px">No preview available for .${ext.toUpperCase()} files</p>
      <a class="btn btn-primary" href="/files/${enc}" download>⬇ Download File</a>
    </div>`;
  }

  document.getElementById('previewPlaceholder').style.display = 'none';
  document.getElementById('previewPane').classList.add('active');
}

function closePrev() {
  document.getElementById('previewPane').classList.remove('active');
  document.getElementById('previewPlaceholder').style.display = '';
  document.getElementById('previewBody').innerHTML = '';
  activeFile = null;
}

document.addEventListener('keydown', e => { if (e.key==='Escape') closePrev(); });

// ── Toast ──
function toast(msg, type='info') {
  const stack = document.getElementById('toast-stack');
  const el = document.createElement('div');
  el.className = `toast ${type}`;
  const prefix = {success:'✓', error:'✗', info:'ℹ', warn:'⚠'}[type] || '•';
  el.textContent = `${prefix}  ${msg}`;
  stack.appendChild(el);
  setTimeout(() => el.remove(), 3000);
}

loadFiles();
</script>
</body>
</html>"""


# ─────────────────────────────────────────────
# REQUEST HANDLER
# ─────────────────────────────────────────────
class Handler(http.server.BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        pass  # Suppress default logging; we handle it in the GUI

    def do_GET(self):
        path = urllib.parse.unquote(self.path)

        if path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(render_page().encode())
            return

        if path.startswith("/files/"):
            filename = path[7:]
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
            else:
                self.send_response(404)
                self.end_headers()
            return

        if path.startswith("/view/"):
            filename = path[6:]
            filepath = os.path.join(os.getcwd(), filename)
            if os.path.isfile(filepath):
                mime = mimetypes.guess_type(filename)[0] or "application/octet-stream"
                with open(filepath, "rb") as f:
                    data = f.read()
                self.send_response(200)
                self.send_header("Content-Type", mime)
                self.end_headers()
                self.wfile.write(data)
            else:
                self.send_response(404)
                self.end_headers()
            return

        if path == "/api/list":
            try:
                files = [f for f in os.listdir(os.getcwd())
                         if os.path.isfile(os.path.join(os.getcwd(), f))]
            except:
                files = []
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(sorted(files)).encode())
            return

        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        if self.path == "/api/upload":
            try:
                length = int(self.headers["Content-Length"])
                body = self.rfile.read(length)
                boundary = self.headers["Content-Type"].split("boundary=")[-1].encode()
                parts = body.split(b"--" + boundary)

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
                        log_queue.append(f"✅ Uploaded: {fname}")
            except Exception as e:
                log_queue.append(f"❌ Upload error: {e}")

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"ok":true}')


# ─────────────────────────────────────────────
# NETWORK HELPERS
# ─────────────────────────────────────────────
def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except:
        return "127.0.0.1"
    finally:
        s.close()


# ─────────────────────────────────────────────
# TKINTER GUI  — Professional dark theme
# Matches the web UI colour system exactly:
#   Blue   = actions / primary buttons
#   Green  = live / success
#   Red    = stop / error
#   Yellow = warning / info
# ─────────────────────────────────────────────
class App(tk.Tk):

    # ── Colour palette (mirrors CSS variables) ──
    BG      = "#111318"   # --bg
    SURFACE = "#1a1d24"   # --surface
    PANEL   = "#1f2330"   # --panel  (navbar / card headers)
    BORDER  = "#2c3040"   # --border
    BORDER2 = "#353a4d"   # --border2

    BLUE    = "#3b82f6"   # actions, primary buttons, links
    GREEN   = "#22c55e"   # live status, success log lines
    RED     = "#ef4444"   # stop button, error log lines
    YELLOW  = "#eab308"   # warnings

    TEXT    = "#e2e5ef"   # primary text
    TEXT2   = "#9099b5"   # secondary / labels
    TEXT3   = "#5c6380"   # muted / placeholders

    # Derived hover shades
    BLUE_H  = "#2563eb"
    GREEN_H = "#16a34a"
    RED_H   = "#dc2626"

    def __init__(self):
        super().__init__()
        self.title("FileWave Pro")
        self.geometry("860x580")
        self.minsize(760, 500)
        self.configure(bg=self.BG)
        self.resizable(True, True)

        self._server_obj = None
        self._running    = False
        self._log_after  = None

        self._build_ui()
        self._poll_logs()

    # ─── Low-level widget helpers ─────────────

    def _frame(self, parent, bg=None, **kw):
        return tk.Frame(parent, bg=bg or self.BG, **kw)

    def _label(self, parent, text, font=None, fg=None, bg=None, **kw):
        return tk.Label(parent,
            text=text,
            font=font or ("Courier", 10),
            fg=fg or self.TEXT2,
            bg=bg or self.BG,
            **kw)

    def _entry(self, parent, textvariable, width=None, **kw):
        e = tk.Entry(parent,
            textvariable=textvariable,
            bg=self.SURFACE,
            fg=self.TEXT,
            insertbackground=self.TEXT,
            relief="flat",
            font=("Courier", 11),
            highlightthickness=1,
            highlightbackground=self.BORDER2,
            highlightcolor=self.BLUE,
            **({} if width is None else {"width": width}),
            **kw)
        return e

    def _btn(self, parent, text, cmd, bg, fg="#ffffff",
             hover=None, padx=14, pady=6, font_size=10):
        """Flat button with hover colour shift."""
        _hover = hover or self._darken(bg, 20)
        b = tk.Button(parent,
            text=text, command=cmd,
            bg=bg, fg=fg,
            activebackground=_hover, activeforeground=fg,
            relief="flat", bd=0, cursor="hand2",
            font=("Helvetica", font_size, "bold"),
            padx=padx, pady=pady)
        b.bind("<Enter>", lambda e, h=_hover: b.config(bg=h))
        b.bind("<Leave>", lambda e, c=bg:     b.config(bg=c))
        return b

    def _ghost_btn(self, parent, text, cmd, fg=None, font_size=10):
        """Border-style ghost button."""
        fg = fg or self.TEXT2
        b = tk.Button(parent,
            text=text, command=cmd,
            bg=self.SURFACE, fg=fg,
            activebackground=self.PANEL, activeforeground=fg,
            relief="flat", bd=0, cursor="hand2",
            font=("Helvetica", font_size),
            padx=12, pady=6,
            highlightthickness=1,
            highlightbackground=self.BORDER2,
            highlightcolor=self.BLUE)
        b.bind("<Enter>", lambda e: b.config(bg=self.PANEL))
        b.bind("<Leave>", lambda e: b.config(bg=self.SURFACE))
        return b

    @staticmethod
    def _darken(hex_color, amount=20):
        r = max(0, int(hex_color[1:3], 16) - amount)
        g = max(0, int(hex_color[3:5], 16) - amount)
        b = max(0, int(hex_color[5:7], 16) - amount)
        return f"#{r:02x}{g:02x}{b:02x}"

    # ─── Section header ───────────────────────

    def _section_head(self, parent, title, bg=None):
        bg = bg or self.PANEL
        row = self._frame(parent, bg=bg)
        row.pack(fill="x", pady=(0, 0))
        # Accent bar
        tk.Frame(row, bg=self.BLUE, width=3).pack(side="left", fill="y")
        self._label(row, f"  {title}",
            font=("Courier", 9, "bold"),
            fg=self.TEXT3, bg=bg).pack(side="left", pady=8)
        tk.Frame(row, bg=self.BORDER, height=1).pack(
            side="left", fill="x", expand=True, padx=(10, 0))

    # ─── Card wrapper ─────────────────────────

    def _card(self, parent, title, pady_bottom=10):
        outer = self._frame(parent, bg=self.BORDER)   # 1-px border illusion
        outer.pack(fill="x", padx=16, pady=(0, pady_bottom))
        inner = self._frame(outer, bg=self.PANEL)
        inner.pack(fill="both", expand=True, padx=1, pady=1)
        self._section_head(inner, title, bg=self.PANEL)
        body = self._frame(inner, bg=self.PANEL)
        body.pack(fill="both", expand=True, padx=14, pady=(8, 12))
        return body

    # ─── Main UI build ────────────────────────

    def _build_ui(self):
        self._build_navbar()
        self._build_body()
        self._build_statusbar()

    # ── Navbar ──
    def _build_navbar(self):
        nav = tk.Frame(self, bg=self.PANEL, height=46)
        nav.pack(fill="x")
        nav.pack_propagate(False)

        # Logo block
        logo_bg = tk.Frame(nav, bg=self.BLUE, width=46, height=46)
        logo_bg.pack(side="left")
        logo_bg.pack_propagate(False)
        tk.Label(logo_bg, text="⚡", font=("Helvetica", 18, "bold"),
                 bg=self.BLUE, fg="#fff").place(relx=0.5, rely=0.5, anchor="center")

        # Separator
        tk.Frame(nav, bg=self.BORDER, width=1).pack(side="left", fill="y", pady=10)

        # Title
        tk.Label(nav, text="FileWave Pro",
                 font=("Helvetica", 14, "bold"),
                 bg=self.PANEL, fg=self.TEXT).pack(side="left", padx=14)

        tk.Label(nav, text="LOCAL FILE SERVER",
                 font=("Courier", 8),
                 bg=self.PANEL, fg=self.TEXT3).pack(side="left")

        # Status pill (right side)
        pill_frame = tk.Frame(nav, bg=self.PANEL)
        pill_frame.pack(side="right", padx=16)

        self._pill_dot = tk.Label(pill_frame, text="●",
            font=("Courier", 10), bg=self.PANEL, fg=self.RED)
        self._pill_dot.pack(side="left")

        self._pill_txt = tk.Label(pill_frame, text=" OFFLINE",
            font=("Courier", 9, "bold"), bg=self.PANEL, fg=self.RED)
        self._pill_txt.pack(side="left")

    # ── Two-column body ──
    def _build_body(self):
        body = self._frame(self, bg=self.BG)
        body.pack(fill="both", expand=True)
        body.columnconfigure(0, weight=0, minsize=340)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

        left  = self._frame(body, bg=self.BG)
        right = self._frame(body, bg=self.BG)
        left.grid(row=0, column=0, sticky="nsew")
        right.grid(row=0, column=1, sticky="nsew")

        # Vertical divider
        tk.Frame(body, bg=self.BORDER, width=1).grid(
            row=0, column=0, sticky="nse")

        self._build_left(left)
        self._build_right(right)

    # ── Left panel: config + controls ──
    def _build_left(self, parent):
        parent.pack_propagate(True)
        top_pad = self._frame(parent, bg=self.BG)
        top_pad.pack(fill="both", expand=True, pady=(14, 14))

        # ── Configuration card ──
        cf = self._card(top_pad, "CONFIGURATION")

        # Folder row
        r1 = self._frame(cf, bg=self.PANEL)
        r1.pack(fill="x", pady=(0, 8))
        self._label(r1, "Folder", fg=self.TEXT3, bg=self.PANEL,
                    font=("Courier", 9, "bold"), width=7, anchor="w").pack(side="left")
        self.folder_var = tk.StringVar(value=str(Path.cwd()))
        self._entry(r1, self.folder_var).pack(
            side="left", fill="x", expand=True, padx=(6, 6))
        self._ghost_btn(r1, "Browse", self._browse, fg=self.TEXT2).pack(side="left")

        # Port row
        r2 = self._frame(cf, bg=self.PANEL)
        r2.pack(fill="x")
        self._label(r2, "Port", fg=self.TEXT3, bg=self.PANEL,
                    font=("Courier", 9, "bold"), width=7, anchor="w").pack(side="left")
        self.port_var = tk.StringVar(value="8000")
        self._entry(r2, self.port_var, width=10).pack(side="left", padx=(6, 0))

        # ── Server Control card ──
        ctrl = self._card(top_pad, "SERVER CONTROL")

        btn_row = self._frame(ctrl, bg=self.PANEL)
        btn_row.pack(fill="x", pady=(0, 10))

        self._btn(btn_row, "▶  Start", self._start,
                  bg=self.BLUE, hover=self.BLUE_H).pack(side="left", padx=(0, 6))
        self._btn(btn_row, "■  Stop", self._stop,
                  bg=self.RED,  hover=self.RED_H).pack(side="left", padx=(0, 6))
        self._ghost_btn(btn_row, "⬡  Open Browser",
                        self._open_browser, fg=self.BLUE).pack(side="left")

        # ── Connection info ──
        conn = self._card(top_pad, "CONNECTION")

        self.local_var = tk.StringVar(value="—")
        self.net_var   = tk.StringVar(value="—")

        for icon, label, var in [
            ("⬡", "Local   ", self.local_var),
            ("⬡", "Network ", self.net_var),
        ]:
            row = self._frame(conn, bg=self.PANEL)
            row.pack(fill="x", pady=2)
            self._label(row, label, fg=self.TEXT3, bg=self.PANEL,
                        font=("Courier", 9), width=9, anchor="w").pack(side="left")
            tk.Label(row, textvariable=var,
                     font=("Courier", 10, "bold"),
                     bg=self.PANEL, fg=self.GREEN,
                     cursor="hand2").pack(side="left")

    # ── Right panel: activity log ──
    def _build_right(self, parent):
        header = self._frame(parent, bg=self.PANEL)
        header.pack(fill="x")

        # Section header with blue accent
        tk.Frame(header, bg=self.BLUE, width=3).pack(side="left", fill="y")
        self._label(header, "  ACTIVITY LOG",
            font=("Courier", 9, "bold"),
            fg=self.TEXT3, bg=self.PANEL).pack(side="left", pady=10)

        # Clear button
        self._ghost_btn(header, "Clear", self._clear_log,
                        fg=self.TEXT3, font_size=9).pack(side="right", padx=10, pady=6)

        # Log text widget
        log_wrap = self._frame(parent, bg=self.BORDER)
        log_wrap.pack(fill="both", expand=True, padx=1, pady=1)

        self.log_box = tk.Text(log_wrap,
            bg=self.SURFACE,
            fg=self.TEXT2,
            insertbackground=self.TEXT,
            font=("Courier", 10),
            relief="flat",
            state="disabled",
            wrap="word",
            padx=12, pady=10,
            selectbackground=self.BORDER2,
            selectforeground=self.TEXT,
            cursor="arrow",
        )
        self.log_box.pack(side="left", fill="both", expand=True)

        sb = tk.Scrollbar(log_wrap, command=self.log_box.yview,
                          bg=self.SURFACE, troughcolor=self.SURFACE,
                          relief="flat", bd=0, width=8)
        sb.pack(side="right", fill="y")
        self.log_box.configure(yscrollcommand=sb.set)

        # Colour tags for semantic log lines
        self.log_box.tag_config("ts",      foreground=self.TEXT3)
        self.log_box.tag_config("success", foreground=self.GREEN)
        self.log_box.tag_config("error",   foreground=self.RED)
        self.log_box.tag_config("warn",    foreground=self.YELLOW)
        self.log_box.tag_config("info",    foreground=self.BLUE)
        self.log_box.tag_config("muted",   foreground=self.TEXT3)

        self._log("FileWave Pro ready — choose a folder and start the server.", "muted")

    # ── Status bar ──
    def _build_statusbar(self):
        bar = tk.Frame(self, bg=self.PANEL, height=26)
        bar.pack(fill="x", side="bottom")
        bar.pack_propagate(False)

        tk.Frame(bar, bg=self.BORDER, height=1).pack(fill="x", side="top")

        self._sb_left = tk.Label(bar, text="  No server running",
            font=("Courier", 9), bg=self.PANEL, fg=self.TEXT3, anchor="w")
        self._sb_left.pack(side="left", fill="x", expand=True)

        tk.Label(bar, text="FileWave Pro  ",
            font=("Courier", 9), bg=self.PANEL, fg=self.TEXT3).pack(side="right")

    # ─── Actions ──────────────────────────────

    def _browse(self):
        p = filedialog.askdirectory()
        if p:
            self.folder_var.set(p)
            self._log(f"Folder set → {p}", "info")

    def _start(self):
        if self._running:
            self._log("Server is already running.", "warn")
            return
        folder = self.folder_var.get()
        if not os.path.isdir(folder):
            self._log("Invalid folder path.", "error")
            return
        try:
            port = int(self.port_var.get())
        except ValueError:
            self._log("Invalid port number.", "error")
            return

        os.chdir(folder)
        self._running = True

        def run():
            try:
                with socketserver.TCPServer(("0.0.0.0", port), Handler) as httpd:
                    self._server_obj = httpd
                    ip        = get_ip()
                    local_url = f"http://127.0.0.1:{port}"
                    net_url   = f"http://{ip}:{port}"

                    self.local_var.set(local_url)
                    self.net_var.set(net_url)
                    self._pill_dot.config(fg=self.GREEN)
                    self._pill_txt.config(fg=self.GREEN, text=" LIVE")
                    self._sb_left.config(
                        text=f"  Serving  {folder}  →  {net_url}")
                    log_queue.append(("success", f"Server started on port {port}"))
                    log_queue.append(("info",    f"Local   → {local_url}"))
                    log_queue.append(("info",    f"Network → {net_url}"))
                    httpd.serve_forever()
            except Exception as e:
                log_queue.append(("error", f"Error: {e}"))
                self._running = False

        threading.Thread(target=run, daemon=True).start()

    def _stop(self):
        if self._server_obj:
            self._server_obj.shutdown()
            self._server_obj = None
            self._running = False
            self.local_var.set("—")
            self.net_var.set("—")
            self._pill_dot.config(fg=self.RED)
            self._pill_txt.config(fg=self.RED, text=" OFFLINE")
            self._sb_left.config(text="  No server running")
            self._log("Server stopped.", "warn")
        else:
            self._log("No server is running.", "warn")

    def _open_browser(self):
        url = self.net_var.get()
        if url and url != "—":
            webbrowser.open(url)
            self._log(f"Opened browser → {url}", "info")
        else:
            self._log("Start the server first.", "warn")

    def _clear_log(self):
        self.log_box.config(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.config(state="disabled")

    # ─── Logging ──────────────────────────────

    def _log(self, msg, level="muted"):
        """
        level: 'success' (green) | 'error' (red) |
               'warn' (yellow)   | 'info' (blue)  | 'muted' (grey)
        """
        ts = time.strftime("%H:%M:%S")
        self.log_box.config(state="normal")

        # Timestamp
        self.log_box.insert("end", f"[{ts}]  ", "ts")
        # Message
        self.log_box.insert("end", f"{msg}\n", level)

        self.log_box.see("end")
        self.log_box.config(state="disabled")

    def _poll_logs(self):
        while log_queue:
            entry = log_queue.pop(0)
            if isinstance(entry, tuple):
                level, msg = entry
            else:
                level, msg = "muted", entry
            self._log(msg, level)
        self._log_after = self.after(300, self._poll_logs)


# ─────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────
if __name__ == "__main__":
    app = App()
    app.mainloop()
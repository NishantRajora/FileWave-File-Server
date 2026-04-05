import http.server
import socketserver
import socket
import os
import threading
import tkinter as tk
from tkinter import filedialog, font as tkfont
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

  .app-shell {
    display: grid;
    grid-template-rows: 48px 1fr;
    height: 100vh;
    overflow: hidden;
  }

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

  .nav-sep { width: 1px; height: 20px; background: var(--border); margin: 0 4px; }

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
    transition: all 0.4s ease;
  }

  .nav-pill.live    { color: var(--green); border-color: rgba(34,197,94,0.35); background: var(--green-dim); }
  .nav-pill.offline { color: var(--red);   border-color: rgba(239,68,68,0.35); background: var(--red-dim);   }

  .nav-pill .dot { width: 6px; height: 6px; border-radius: 50%; background: currentColor; }
  .nav-pill.live .dot { animation: blink 1.8s ease-in-out infinite; }

  @keyframes blink { 0%,100%{opacity:1} 50%{opacity:.35} }

  .nav-spacer { flex: 1; }

  .nav-info { font-family: var(--mono); font-size: 11px; color: var(--text-3); }

  .content {
    display: grid;
    grid-template-columns: 340px 1fr;
    overflow: hidden;
  }

  .left-panel {
    background: var(--surface);
    border-right: 1px solid var(--border);
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  .right-panel {
    display: flex;
    flex-direction: column;
    overflow: hidden;
    background: var(--bg);
  }

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

  .upload-area { padding: 14px; border-bottom: 1px solid var(--border); flex-shrink: 0; }

  .drop-zone {
    border: 1.5px dashed var(--border2);
    border-radius: var(--radius);
    padding: 22px 16px;
    text-align: center;
    cursor: pointer;
    transition: all 0.18s ease;
    background: var(--bg);
  }

  .drop-zone:hover, .drop-zone.drag-over { border-color: var(--blue); background: var(--blue-dim); }

  .drop-icon { font-size: 26px; margin-bottom: 8px; display: block; }
  .drop-zone h3 { font-size: 13px; font-weight: 600; color: var(--text); margin-bottom: 3px; }
  .drop-zone p  { font-size: 11px; color: var(--text-3); font-family: var(--mono); }

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

  .btn-primary { background: var(--blue); color: #fff; border-color: var(--blue); }
  .btn-primary:hover { background: #2563eb; border-color: #2563eb; }

  .btn-ghost { background: transparent; color: var(--text-2); border-color: var(--border2); }
  .btn-ghost:hover { background: var(--panel); color: var(--text); border-color: var(--blue); }

  .btn-sm { padding: 4px 10px; font-size: 12px; }

  .upload-btn-row { margin-top: 10px; display: flex; justify-content: center; }

  .progress-wrap { margin-top: 12px; display: none; }
  .progress-wrap.active { display: block; }

  .progress-row {
    display: flex;
    justify-content: space-between;
    font-family: var(--mono);
    font-size: 11px;
    color: var(--text-3);
    margin-bottom: 6px;
  }

  .progress-track { height: 4px; background: var(--border); border-radius: 99px; overflow: hidden; }
  .progress-fill  { height: 100%; background: var(--blue); border-radius: 99px; width: 0%; transition: width 0.25s ease; }

  .stats-strip {
    padding: 8px 16px;
    border-bottom: 1px solid var(--border);
    display: flex;
    gap: 18px;
    flex-shrink: 0;
  }

  .stat-item { display: flex; align-items: center; gap: 5px; font-family: var(--mono); font-size: 11px; color: var(--text-3); }
  .stat-item strong { color: var(--text); font-weight: 500; }
  .stat-item .dot-blue  { color: var(--blue); }
  .stat-item .dot-green { color: var(--green); }
  .stat-item .dot-yellow{ color: var(--yellow); }

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

  .view-grp { display: flex; border: 1px solid var(--border2); border-radius: var(--radius-sm); overflow: hidden; }

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

  .file-scroll { flex: 1; overflow-y: auto; padding: 8px; }

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

  @keyframes rowIn { from{opacity:0;transform:translateY(4px)} to{opacity:1;transform:translateY(0)} }

  .file-item:hover { background: var(--blue-dim); border-color: var(--border); }

  .file-icon {
    width: 34px; height: 34px;
    border-radius: var(--radius-sm);
    display: flex; align-items: center; justify-content: center;
    font-size: 16px;
    flex-shrink: 0;
    border: 1px solid var(--border);
  }

  .ic-img   { background: rgba(239,68,68,0.1);  border-color: rgba(239,68,68,0.2); }
  .ic-video { background: rgba(59,130,246,0.1); border-color: rgba(59,130,246,0.2); }
  .ic-audio { background: rgba(234,179,8,0.1);  border-color: rgba(234,179,8,0.2); }
  .ic-doc   { background: rgba(34,197,94,0.1);  border-color: rgba(34,197,94,0.2); }
  .ic-code  { background: rgba(59,130,246,0.1); border-color: rgba(59,130,246,0.2); }
  .ic-arch  { background: rgba(234,179,8,0.1);  border-color: rgba(234,179,8,0.2); }
  .ic-data  { background: rgba(34,197,94,0.1);  border-color: rgba(34,197,94,0.2); }
  .ic-other { background: var(--surface);        border-color: var(--border); }

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

  .file-sub { font-size: 10px; font-family: var(--mono); color: var(--text-3); display: flex; gap: 6px; align-items: center; }

  .tag { padding: 1px 5px; border-radius: 2px; font-size: 10px; font-family: var(--mono); font-weight: 500; letter-spacing: 0.3px; }
  .tag-img   { background: rgba(239,68,68,0.15);  color: var(--red);    }
  .tag-video { background: rgba(59,130,246,0.15); color: var(--blue);   }
  .tag-audio { background: rgba(234,179,8,0.15);  color: var(--yellow); }
  .tag-doc   { background: rgba(34,197,94,0.15);  color: var(--green);  }
  .tag-code  { background: rgba(59,130,246,0.15); color: var(--blue);   }
  .tag-arch  { background: rgba(234,179,8,0.15);  color: var(--yellow); }
  .tag-data  { background: rgba(34,197,94,0.15);  color: var(--green);  }
  .tag-other { background: var(--border);          color: var(--text-3); }

  .file-actions { display: flex; gap: 4px; opacity: 0; transition: opacity 0.15s; }
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

  .icon-btn:hover     { background: var(--blue);  color: #fff; border-color: var(--blue); }
  .icon-btn.dl:hover  { background: var(--green); color: #fff; border-color: var(--green); }

  .file-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(120px,1fr)); gap: 8px; padding: 8px; }

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
  }

  .grid-card:hover {
    border-color: var(--blue);
    background: var(--blue-dim);
    transform: translateY(-2px);
    box-shadow: 0 4px 16px rgba(0,0,0,0.3);
  }

  @keyframes fadeIn { to { opacity: 1; } }

  .grid-icon  { font-size: 30px; margin-bottom: 8px; display: block; }
  .grid-label { font-size: 11px; font-weight: 500; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; margin-bottom: 8px; color: var(--text); }
  .grid-tag   { display: inline-block; margin-bottom: 8px; }
  .grid-dl    { display: block; opacity: 0; transition: opacity 0.15s; }
  .grid-card:hover .grid-dl { opacity: 1; }

  .empty-state { text-align: center; padding: 50px 20px; color: var(--text-3); }
  .empty-state .e-icon { font-size: 38px; margin-bottom: 10px; opacity: 0.4; display: block; }
  .empty-state p { font-size: 12px; font-family: var(--mono); }

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

  .preview-pane { flex: 1; overflow: auto; display: none; flex-direction: column; }
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

  .preview-body img, .preview-body video { max-width: 100%; max-height: calc(100vh - 200px); border-radius: var(--radius); border: 1px solid var(--border); }
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

  .preview-body iframe { width: 100%; height: calc(100vh - 180px); border: none; border-radius: var(--radius); }

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

  @keyframes toastSlide { from{opacity:0;transform:translateX(16px)} to{opacity:1;transform:translateX(0)} }
</style>
</head>
<body>
<div class="app-shell">

  <nav class="navbar">
    <div class="nav-brand">
      <div class="nav-logo">⚡</div>
      FileWave Pro
    </div>
    <div class="nav-sep"></div>
    <!-- STATUS PILL — updated by JS polling /api/status -->
    <div class="nav-pill offline" id="statusPill">
      <span class="dot"></span>
      <span id="statusText">CHECKING…</span>
    </div>
    <div class="nav-spacer"></div>
    <div class="nav-info" id="urlDisplay">Connecting…</div>
  </nav>

  <div class="content">

    <div class="left-panel">

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
          <button class="btn btn-primary" onclick="document.getElementById('fileInput').click()">Choose Files</button>
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

      <div class="stats-strip">
        <div class="stat-item"><span class="dot-blue">●</span><strong id="statCount">0</strong> files</div>
        <div class="stat-item"><span class="dot-green">●</span><strong id="statTypes">—</strong> types</div>
        <div class="stat-item" id="statFilterWrap" style="display:none">
          <span class="dot-yellow">◆</span><strong id="statFiltered">0</strong> shown
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

<div id="toast-stack"></div>

<script>
let allFiles = [];
let currentView = 'list';
let activeFile  = null;

const TYPES = {
  img:   ['png','jpg','jpeg','gif','webp','svg','bmp','ico'],
  video: ['mp4','mov','avi','mkv','webm'],
  audio: ['mp3','wav','ogg','flac','aac','m4a'],
  doc:   ['pdf','doc','docx','xls','xlsx','ppt','pptx'],
  code:  ['py','js','ts','html','css','json','xml','sh','c','cpp','java','rb','go','rs','md','yaml','yml'],
  arch:  ['zip','rar','gz','tar','7z'],
  data:  ['csv','tsv','sql','db'],
};

const ICONS = { img:'🖼️', video:'🎬', audio:'🎵', doc:'📄', code:'⚡', arch:'📦', data:'📊', other:'📃' };

function getExt(f)   { return f.split('.').pop().toLowerCase(); }
function classify(f) { const e=getExt(f); for(const [k,v] of Object.entries(TYPES)) if(v.includes(e)) return k; return 'other'; }
function icon(f)     { return ICONS[classify(f)]; }
function icClass(f)  { return 'ic-'  + classify(f); }
function tagClass(f) { return 'tag-' + classify(f); }
function tagLabel(f) { return getExt(f).toUpperCase(); }

function setView(v) {
  currentView = v;
  document.getElementById('btnList').classList.toggle('active', v==='list');
  document.getElementById('btnGrid').classList.toggle('active', v==='grid');
  renderFiles();
}

// ── SERVER STATUS POLLING  (fixes "offline" bug) ──────────────────────────
const pill    = document.getElementById('statusPill');
const pillTxt = document.getElementById('statusText');
const urlDisp = document.getElementById('urlDisplay');

async function checkStatus() {
  try {
    const r = await fetch('/api/status', { cache: 'no-store' });
    if (r.ok) {
      const d = await r.json();
      pill.className = 'nav-pill live';
      pillTxt.textContent = 'LIVE';
      urlDisp.textContent = d.url || window.location.host;
    } else {
      throw new Error('non-ok');
    }
  } catch {
    pill.className = 'nav-pill offline';
    pillTxt.textContent = 'OFFLINE';
    urlDisp.textContent = 'Server unreachable';
  }
}

checkStatus();
setInterval(checkStatus, 5000);  // poll every 5 s
// ─────────────────────────────────────────────────────────────────────────

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
    box.innerHTML = `<div class="empty-state"><span class="e-icon">📭</span><p>No files found</p></div>`;
    return;
  }

  if (currentView === 'list') {
    box.innerHTML = `<div class="file-list">${files.map((f,i) => `
      <div class="file-item" style="animation-delay:${i*0.03}s" onclick="preview('${encodeURIComponent(f)}','${f}')">
        <div class="file-icon ${icClass(f)}">${icon(f)}</div>
        <div class="file-meta-col">
          <div class="file-name">${f}</div>
          <div class="file-sub"><span class="tag ${tagClass(f)}">${tagLabel(f)}</span></div>
        </div>
        <div class="file-actions">
          <a class="icon-btn dl" href="/files/${encodeURIComponent(f)}" download onclick="event.stopPropagation()" title="Download">⬇</a>
        </div>
      </div>`).join('')}</div>`;
  } else {
    box.innerHTML = `<div class="file-grid">${files.map((f,i) => `
      <div class="grid-card" style="animation-delay:${i*0.03}s" onclick="preview('${encodeURIComponent(f)}','${f}')">
        <span class="grid-icon">${icon(f)}</span>
        <div class="grid-label">${f}</div>
        <span class="tag ${tagClass(f)} grid-tag">${tagLabel(f)}</span>
        <a class="icon-btn dl grid-dl" href="/files/${encodeURIComponent(f)}" download onclick="event.stopPropagation()" title="Download">⬇</a>
      </div>`).join('')}</div>`;
  }
}

function uploadFiles(files) {
  const wrap=document.getElementById('progressWrap'), fill=document.getElementById('progressFill'),
        label=document.getElementById('progressLabel'), pct=document.getElementById('progressPct');
  wrap.classList.add('active');
  let total=files.length, done=0;
  Array.from(files).forEach(file => {
    const fd=new FormData(); fd.append('file',file);
    fetch('/api/upload',{method:'POST',body:fd}).then(()=>{
      done++;
      const p=Math.round((done/total)*100);
      fill.style.width=p+'%'; pct.textContent=p+'%';
      label.textContent=`Uploading ${done} of ${total}…`;
      if (done===total) {
        label.textContent=`✓ ${total} file(s) ready`;
        setTimeout(()=>{ wrap.classList.remove('active'); fill.style.width='0%'; },2000);
        loadFiles(); toast(`${total} file(s) uploaded`,'success');
      }
    }).catch(()=>toast('Upload failed','error'));
  });
}

const dz=document.getElementById('dropZone');
['dragover','dragenter'].forEach(e=>dz.addEventListener(e,ev=>{ev.preventDefault();dz.classList.add('drag-over');}));
['dragleave','dragend','drop'].forEach(e=>dz.addEventListener(e,ev=>{ev.preventDefault();dz.classList.remove('drag-over');}));
dz.addEventListener('drop',ev=>{ev.preventDefault();if(ev.dataTransfer.files.length)uploadFiles(ev.dataTransfer.files);});

function preview(enc, fname) {
  activeFile=fname;
  const ext=getExt(fname), url=`/view/${enc}`, body=document.getElementById('previewBody');
  document.getElementById('prevName').textContent=fname;
  document.getElementById('prevIcon').textContent=icon(fname);
  document.getElementById('prevDownload').href=`/files/${enc}`;
  document.getElementById('prevDownload').download=fname;
  const type=classify(fname);
  if (type==='img') body.innerHTML=`<img src="${url}" alt="${fname}">`;
  else if (type==='video') body.innerHTML=`<video src="${url}" controls></video>`;
  else if (type==='audio') body.innerHTML=`<div style="text-align:center;width:100%">
    <div style="font-size:56px;margin-bottom:24px;opacity:0.5">${icon(fname)}</div>
    <audio src="${url}" controls style="width:80%"></audio></div>`;
  else if (type==='code'||['txt','md','json','xml','csv','yaml','yml'].some(x=>ext===x))
    fetch(url).then(r=>r.text()).then(t=>{ body.innerHTML=`<pre>${t.replace(/</g,'&lt;')}</pre>`; });
  else if (ext==='pdf') body.innerHTML=`<iframe src="${url}"></iframe>`;
  else body.innerHTML=`<div style="text-align:center;color:var(--text-3)">
    <div style="font-size:56px;margin-bottom:16px;opacity:0.3">${icon(fname)}</div>
    <p style="font-family:var(--mono);font-size:12px;margin-bottom:16px">No preview for .${ext.toUpperCase()}</p>
    <a class="btn btn-primary" href="/files/${enc}" download>⬇ Download File</a></div>`;
  document.getElementById('previewPlaceholder').style.display='none';
  document.getElementById('previewPane').classList.add('active');
}

function closePrev() {
  document.getElementById('previewPane').classList.remove('active');
  document.getElementById('previewPlaceholder').style.display='';
  document.getElementById('previewBody').innerHTML='';
  activeFile=null;
}

document.addEventListener('keydown',e=>{if(e.key==='Escape')closePrev();});

function toast(msg,type='info') {
  const stack=document.getElementById('toast-stack'),el=document.createElement('div');
  el.className=`toast ${type}`;
  const prefix={success:'✓',error:'✗',info:'ℹ',warn:'⚠'}[type]||'•';
  el.textContent=`${prefix}  ${msg}`;
  stack.appendChild(el);
  setTimeout(()=>el.remove(),3000);
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
        pass

    def do_GET(self):
        path = urllib.parse.unquote(self.path)

        if path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(render_page().encode())
            return

        # ── NEW: /api/status endpoint — fixes the "offline" bug ──
        if path == "/api/status":
            import socket as _s
            s = _s.socket(_s.AF_INET, _s.SOCK_DGRAM)
            try:
                s.connect(("8.8.8.8", 80))
                ip = s.getsockname()[0]
            except:
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
                self.send_response(404); self.end_headers()
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
                self.send_response(404); self.end_headers()
            return

        if path == "/api/list":
            try:
                files = [f for f in os.listdir(os.getcwd()) if os.path.isfile(os.path.join(os.getcwd(), f))]
            except:
                files = []
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(sorted(files)).encode())
            return

        self.send_response(404); self.end_headers()

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
                        log_queue.append(("success", f"Uploaded: {fname}"))
            except Exception as e:
                log_queue.append(("error", f"Upload error: {e}"))
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
# CANVA-STYLE TKINTER GUI
# Clean · Light · Professional
#
# Palette:
#   White     #FFFFFF  — canvas / card background
#   Snow      #F5F5F5  — app background
#   Lavender  #F0EDFF  — subtle accent tints
#   Purple    #7C3AED  — primary action (Canva brand-adjacent)
#   Purple-L  #9D6FF5  — hover / lighter shade
#   Purple-XL #EDE9FE  — ghost tints
#   Ink       #1A1A2E  — primary text
#   Slate     #6B7280  — secondary text
#   Cloud     #E5E7EB  — borders
#   Red       #EF4444  — stop / danger
#   Green     #10B981  — success / live
#   Amber     #F59E0B  — warning
# ─────────────────────────────────────────────
class App(tk.Tk):

    # ── Palette ──────────────────────────────
    BG       = "#F7F7FB"   # app background (off-white)
    WHITE    = "#FFFFFF"   # card / panel background
    LAVENDER = "#F0EDFF"   # tinted accent bg
    BORDER   = "#E5E7EB"   # subtle border
    BORDER2  = "#D1D5DB"   # slightly stronger border

    PURPLE   = "#7C3AED"   # primary / Canva-purple
    PURPLE_L = "#9D6FF5"   # hover
    PURPLE_T = "#EDE9FE"   # tinted ghost bg
    PURPLE_D = "#6D28D9"   # active / pressed

    INK      = "#1A1A2E"   # primary text
    SLATE    = "#6B7280"   # secondary text
    MIST     = "#9CA3AF"   # placeholder / muted

    GREEN    = "#10B981"   # live / success
    GREEN_T  = "#D1FAE5"   # green tint
    RED      = "#EF4444"   # stop / danger
    RED_T    = "#FEE2E2"   # red tint
    AMBER    = "#F59E0B"   # warning
    AMBER_T  = "#FEF3C7"   # amber tint

    def __init__(self):
        super().__init__()
        self.title("FileWave Pro")
        self.geometry("900x600")
        self.minsize(800, 520)
        self.configure(bg=self.BG)
        self.resizable(True, True)

        self._server_obj = None
        self._running    = False
        self._log_after  = None
        self._dot_anim   = False

        self._build_ui()
        self._poll_logs()

    # ── Widget helpers ────────────────────────

    def _frame(self, parent, bg=None, **kw):
        return tk.Frame(parent, bg=bg or self.BG, **kw)

    def _label(self, parent, text, font=None, fg=None, bg=None, **kw):
        return tk.Label(parent,
            text=text,
            font=font or ("Helvetica", 10),
            fg=fg or self.SLATE,
            bg=bg or self.BG,
            **kw)

    def _entry(self, parent, textvariable, width=None, **kw):
        e = tk.Entry(parent,
            textvariable=textvariable,
            bg=self.WHITE,
            fg=self.INK,
            insertbackground=self.PURPLE,
            relief="flat",
            font=("Helvetica", 11),
            highlightthickness=1,
            highlightbackground=self.BORDER,
            highlightcolor=self.PURPLE,
            **({} if width is None else {"width": width}),
            **kw)
        return e

    def _btn(self, parent, text, cmd, bg=None, fg="#FFFFFF",
             hover=None, padx=16, pady=8):
        bg    = bg    or self.PURPLE
        hover = hover or self.PURPLE_L
        b = tk.Button(parent,
            text=text, command=cmd,
            bg=bg, fg=fg,
            activebackground=hover, activeforeground=fg,
            relief="flat", bd=0, cursor="hand2",
            font=("Helvetica", 10, "bold"),
            padx=padx, pady=pady)
        b.bind("<Enter>", lambda e, h=hover: b.config(bg=h))
        b.bind("<Leave>", lambda e, c=bg:    b.config(bg=c))
        return b

    def _ghost_btn(self, parent, text, cmd, fg=None, font_size=10):
        fg = fg or self.PURPLE
        b = tk.Button(parent,
            text=text, command=cmd,
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

    # ── Pill / badge ──────────────────────────

    def _pill(self, parent, text, bg, fg, font_size=9):
        f = tk.Frame(parent, bg=bg, padx=8, pady=3)
        tk.Label(f, text=text, font=("Helvetica", font_size, "bold"),
                 bg=bg, fg=fg).pack()
        return f

    # ── Card container ────────────────────────

    def _card(self, parent, padx=0, pady=0):
        """White rounded-feel card with a subtle border."""
        outer = tk.Frame(parent, bg=self.BORDER, padx=1, pady=1)
        outer.pack(fill="x", padx=padx, pady=pady)
        inner = tk.Frame(outer, bg=self.WHITE)
        inner.pack(fill="both", expand=True)
        return inner

    # ── Section label ─────────────────────────

    def _section_lbl(self, parent, text, bg=None):
        bg = bg or self.BG
        f  = self._frame(parent, bg=bg)
        f.pack(fill="x", pady=(0, 6))
        self._label(f, text,
            font=("Helvetica", 9, "bold"),
            fg=self.MIST, bg=bg).pack(side="left")
        return f

    # ─────────────────────────────────────────
    # BUILD UI
    # ─────────────────────────────────────────

    def _build_ui(self):
        self._build_navbar()
        self._build_body()
        self._build_statusbar()

    # ── Navbar ────────────────────────────────

    def _build_navbar(self):
        nav = tk.Frame(self, bg=self.WHITE, height=52)
        nav.pack(fill="x")
        nav.pack_propagate(False)

        self._divider(nav, "h", color=self.BORDER).pack(side="bottom", fill="x")

        # Left: logo + name
        left = tk.Frame(nav, bg=self.WHITE)
        left.pack(side="left", padx=20, pady=0)

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

        # Right: status pill
        right = tk.Frame(nav, bg=self.WHITE)
        right.pack(side="right", padx=20)

        self._status_frame = tk.Frame(right, bg=self.RED_T,
                                      padx=10, pady=4)
        self._status_frame.pack(side="right")

        self._status_dot = tk.Label(self._status_frame, text="●",
            font=("Helvetica", 8), bg=self.RED_T, fg=self.RED)
        self._status_dot.pack(side="left")

        self._status_lbl = tk.Label(self._status_frame, text=" OFFLINE",
            font=("Helvetica", 9, "bold"), bg=self.RED_T, fg=self.RED)
        self._status_lbl.pack(side="left")

    # ── Two-column body ───────────────────────

    def _build_body(self):
        body = tk.Frame(self, bg=self.BG)
        body.pack(fill="both", expand=True)
        body.columnconfigure(0, weight=0, minsize=360)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

        left  = tk.Frame(body, bg=self.WHITE)
        right = tk.Frame(body, bg=self.BG)
        left.grid(row=0, column=0, sticky="nsew")
        right.grid(row=0, column=1, sticky="nsew")
        self._divider(body, "v").grid(row=0, column=0, sticky="nse")

        self._build_left(left)
        self._build_right(right)

    # ── LEFT PANEL ────────────────────────────

    def _build_left(self, parent):
        # Scrollable area via inner frame
        canvas = tk.Canvas(parent, bg=self.WHITE, highlightthickness=0)
        canvas.pack(fill="both", expand=True)

        inner = tk.Frame(canvas, bg=self.WHITE)
        canvas.create_window((0, 0), window=inner, anchor="nw")
        inner.bind("<Configure>", lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")))

        self._build_left_inner(inner)

    def _build_left_inner(self, p):
        pad = dict(padx=20)

        # ── App hero strip ──
        hero = tk.Frame(p, bg=self.LAVENDER)
        hero.pack(fill="x")
        tk.Label(hero, text="Your local file server",
                 font=("Helvetica", 11), bg=self.LAVENDER,
                 fg=self.PURPLE).pack(side="left", padx=20, pady=12)

        # ── SECTION: Folder ──
        tk.Frame(p, bg=self.BG, height=16).pack(fill="x")
        self._section_lbl(p, "  SERVE FOLDER", bg=self.WHITE).pack(
            **pad, fill="x")

        row1 = tk.Frame(p, bg=self.WHITE)
        row1.pack(fill="x", **pad, pady=(0, 10))

        self.folder_var = tk.StringVar(value=str(Path.cwd()))
        entry = self._entry(row1, self.folder_var)
        entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self._ghost_btn(row1, "Browse", self._browse).pack(side="left")

        # ── SECTION: Port ──
        self._section_lbl(p, "  PORT", bg=self.WHITE).pack(**pad, fill="x")

        row2 = tk.Frame(p, bg=self.WHITE)
        row2.pack(fill="x", **pad, pady=(0, 4))
        self.port_var = tk.StringVar(value="8000")
        self._entry(row2, self.port_var, width=10).pack(side="left")
        self._label(row2, "   Default: 8000", fg=self.MIST,
                    bg=self.WHITE, font=("Helvetica", 9)).pack(side="left")

        self._divider(p).pack(fill="x", **pad, pady=16)

        # ── SECTION: Controls ──
        self._section_lbl(p, "  SERVER CONTROL", bg=self.WHITE).pack(
            **pad, fill="x")

        btns = tk.Frame(p, bg=self.WHITE)
        btns.pack(fill="x", **pad, pady=(0, 4))

        self._btn(btns, "▶  Start Server", self._start,
                  bg=self.PURPLE, hover=self.PURPLE_L).pack(
                  side="left", padx=(0, 8))

        self._btn(btns, "■  Stop", self._stop,
                  bg=self.RED, fg=self.WHITE, hover="#DC2626").pack(
                  side="left", padx=(0, 8))

        self._ghost_btn(btns, "🌐  Open Browser",
                        self._open_browser).pack(side="left")

        self._divider(p).pack(fill="x", **pad, pady=16)

        # ── SECTION: Connection URLs ──
        self._section_lbl(p, "  CONNECTION DETAILS", bg=self.WHITE).pack(
            **pad, fill="x")

        conn = tk.Frame(p, bg=self.WHITE)
        conn.pack(fill="x", **pad, pady=(0, 4))

        self.local_var = tk.StringVar(value="Not running")
        self.net_var   = tk.StringVar(value="Not running")

        for label, var, icon in [
            ("Local", self.local_var, "🖥"),
            ("Network", self.net_var, "🌐"),
        ]:
            row = tk.Frame(conn, bg=self.WHITE)
            row.pack(fill="x", pady=4)

            # Icon badge
            badge = tk.Frame(row, bg=self.PURPLE_T, padx=6, pady=4)
            badge.pack(side="left")
            tk.Label(badge, text=icon, bg=self.PURPLE_T,
                     font=("Helvetica", 11)).pack()

            info = tk.Frame(row, bg=self.WHITE)
            info.pack(side="left", padx=10)

            tk.Label(info, text=label,
                     font=("Helvetica", 8, "bold"),
                     bg=self.WHITE, fg=self.MIST).pack(anchor="w")

            tk.Label(info, textvariable=var,
                     font=("Helvetica", 10, "bold"),
                     bg=self.WHITE, fg=self.PURPLE,
                     cursor="hand2").pack(anchor="w")

        self._divider(p).pack(fill="x", **pad, pady=16)

        # ── SECTION: Quick tip ──
        tip = tk.Frame(p, bg=self.AMBER_T, padx=14, pady=12)
        tip.pack(fill="x", **pad, pady=(0, 20))
        tk.Label(tip, text="💡  Tip",
                 font=("Helvetica", 9, "bold"),
                 bg=self.AMBER_T, fg=self.AMBER).pack(anchor="w")
        tk.Label(tip,
                 text="Share your Network URL with\ndevices on the same Wi-Fi.",
                 font=("Helvetica", 9),
                 bg=self.AMBER_T, fg=self.INK,
                 justify="left").pack(anchor="w", pady=(4, 0))

    # ── RIGHT PANEL: Activity log ─────────────

    def _build_right(self, parent):

        # Header bar
        header = tk.Frame(parent, bg=self.WHITE, height=44)
        header.pack(fill="x")
        header.pack_propagate(False)
        self._divider(header).pack(side="bottom", fill="x")

        tk.Label(header, text="  Activity Log",
                 font=("Helvetica", 12, "bold"),
                 bg=self.WHITE, fg=self.INK).pack(side="left", padx=16, pady=10)

        self._ghost_btn(header, "Clear", self._clear_log,
                        fg=self.SLATE, font_size=9).pack(
                        side="right", padx=12, pady=8)

        # Log area
        log_bg = tk.Frame(parent, bg=self.BG)
        log_bg.pack(fill="both", expand=True, padx=16, pady=12)

        log_card = tk.Frame(log_bg, bg=self.BORDER, padx=1, pady=1)
        log_card.pack(fill="both", expand=True)

        inner = tk.Frame(log_card, bg=self.WHITE)
        inner.pack(fill="both", expand=True)

        self.log_box = tk.Text(inner,
            bg=self.WHITE,
            fg=self.INK,
            insertbackground=self.PURPLE,
            font=("Courier", 10),
            relief="flat",
            state="disabled",
            wrap="word",
            padx=14, pady=12,
            selectbackground=self.PURPLE_T,
            selectforeground=self.INK,
            cursor="arrow",
            spacing1=2, spacing3=2,
        )
        self.log_box.pack(side="left", fill="both", expand=True)

        sb = tk.Scrollbar(inner, command=self.log_box.yview,
                          bg=self.BG, troughcolor=self.BG,
                          relief="flat", bd=0, width=8)
        sb.pack(side="right", fill="y")
        self.log_box.configure(yscrollcommand=sb.set)

        # Semantic colour tags
        self.log_box.tag_config("ts",      foreground=self.MIST)
        self.log_box.tag_config("success", foreground=self.GREEN)
        self.log_box.tag_config("error",   foreground=self.RED)
        self.log_box.tag_config("warn",    foreground=self.AMBER)
        self.log_box.tag_config("info",    foreground=self.PURPLE)
        self.log_box.tag_config("muted",   foreground=self.SLATE)

        self._log("FileWave Pro ready — choose a folder and start the server.", "muted")

    # ── Status bar ────────────────────────────

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

    # ─── Actions ──────────────────────────────

    def _browse(self):
        p = filedialog.askdirectory()
        if p:
            self.folder_var.set(p)
            self._log(f"Folder → {p}", "info")

    def _start(self):
        if self._running:
            self._log("Server is already running.", "warn"); return
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
                    ip        = get_ip()
                    local_url = f"http://127.0.0.1:{port}"
                    net_url   = f"http://{ip}:{port}"
                    self.local_var.set(local_url)
                    self.net_var.set(net_url)
                    self._set_live(True)
                    self._sb_left.config(text=f"  Serving  {folder}  →  {net_url}")
                    log_queue.append(("success", f"Server started on port {port}"))
                    log_queue.append(("info",    f"Local   → {local_url}"))
                    log_queue.append(("info",    f"Network → {net_url}"))
                    httpd.serve_forever()
            except Exception as e:
                log_queue.append(("error", f"Error: {e}"))
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

    def _clear_log(self):
        self.log_box.config(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.config(state="disabled")

    # ── Live / offline pill ───────────────────

    def _set_live(self, live):
        if live:
            self._status_frame.config(bg=self.GREEN_T)
            self._status_dot.config(bg=self.GREEN_T, fg=self.GREEN)
            self._status_lbl.config(bg=self.GREEN_T, fg=self.GREEN, text=" LIVE")
            self._animate_dot()
        else:
            self._dot_anim = False
            self._status_frame.config(bg=self.RED_T)
            self._status_dot.config(bg=self.RED_T, fg=self.RED)
            self._status_lbl.config(bg=self.RED_T, fg=self.RED, text=" OFFLINE")

    def _animate_dot(self, visible=True):
        if not self._running:
            return
        self._dot_anim = True
        self._status_dot.config(fg=self.GREEN if visible else self.GREEN_T)
        self.after(900, lambda: self._animate_dot(not visible))

    # ─── Logging ──────────────────────────────

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
        while log_queue:
            entry = log_queue.pop(0)
            level, msg = entry if isinstance(entry, tuple) else ("muted", entry)
            self._log(msg, level)
        self.after(300, self._poll_logs)


# ─────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────
if __name__ == "__main__":
    app = App()
    app.mainloop()
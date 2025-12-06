#!/usr/bin/env python3
"""
EhkoForge Control Panel v3.0
Aligned with terminal aesthetic (blue palette, violet tint for differentiation).
"""

import os
import signal
import subprocess
import sys
import threading
import webbrowser
import urllib.request
import urllib.error
import json
from datetime import datetime
from pathlib import Path
from tkinter import *
from tkinter import ttk, messagebox, scrolledtext

# =============================================================================
# CONFIGURATION
# =============================================================================

EHKOFORGE_ROOT = Path("G:/Other computers/Ehko/Obsidian/EhkoForge")
MIRRORWELL_ROOT = Path("G:/Other computers/Ehko/Obsidian/Mirrorwell")
SCRIPTS_PATH = EHKOFORGE_ROOT / "5.0 Scripts"
SERVER_SCRIPT = SCRIPTS_PATH / "forge_server.py"
SERVER_URL = "http://localhost:5000"
REFRESH_SCRIPT = SCRIPTS_PATH / "ehko_refresh.py"

# Colours (terminal-aligned, violet tint)
C = {
    "bg": "#080a0e",
    "bg2": "#0c1018",
    "bg3": "#111620",
    "accent": "#8b7cce",
    "accent_dim": "#5a4a85",
    "text": "#e8eef8",
    "text2": "#8aa4d6",
    "dim": "#4a6fa5",
    "success": "#5fb3a1",
    "warning": "#c9a962",
    "error": "#d97373",
    "recog": "#c94a4a",
}

server_process = None

# =============================================================================
# HELPERS
# =============================================================================

def log(w, msg, tag=None):
    ts = datetime.now().strftime("%H:%M:%S")
    w.config(state=NORMAL)
    w.insert(END, f"[{ts}] {msg}\n", tag or ())
    w.see(END)
    w.config(state=DISABLED)

def api(endpoint, method="GET", data=None):
    try:
        url = f"{SERVER_URL}{endpoint}"
        if method == "POST":
            req = urllib.request.Request(url, json.dumps(data or {}).encode(), 
                                         {'Content-Type': 'application/json'}, method='POST')
        else:
            req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())
    except Exception as e:
        return {"error": str(e)}

def run_async(w, cmd, cwd=None, shell=False):
    def _run():
        try:
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                 cwd=cwd, shell=shell, text=True, bufsize=1)
            for line in iter(p.stdout.readline, ''):
                if line: log(w, line.strip())
            p.wait()
            log(w, "✓ Done" if p.returncode == 0 else f"✗ Exit {p.returncode}", 
                "success" if p.returncode == 0 else "error")
        except Exception as e:
            log(w, f"✗ {e}", "error")
    threading.Thread(target=_run, daemon=True).start()

# =============================================================================
# COMMANDS
# =============================================================================

def start_server(w, status):
    global server_process
    if server_process and server_process.poll() is None:
        log(w, "Already running", "warning"); return
    try:
        server_process = subprocess.Popen(
            [sys.executable, str(SERVER_SCRIPT)], stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, cwd=str(SCRIPTS_PATH), text=True, bufsize=1,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0)
        status.config(text="● ONLINE", fg=C["success"])
        log(w, f"✓ Started (PID {server_process.pid})", "success")
        def stream():
            for line in iter(server_process.stdout.readline, ''):
                if line and server_process.poll() is None: log(w, f"[srv] {line.strip()}")
            status.config(text="○ OFFLINE", fg=C["error"])
        threading.Thread(target=stream, daemon=True).start()
    except Exception as e:
        log(w, f"✗ {e}", "error")

def start_terminal(w, status):
    global server_process
    if server_process and server_process.poll() is None:
        log(w, "Already running", "warning"); return
    try:
        cmd = f'cd "{SCRIPTS_PATH}" ; py forge_server.py'
        server_process = subprocess.Popen(['powershell', '-NoExit', '-Command', cmd],
                                          creationflags=subprocess.CREATE_NEW_CONSOLE)
        status.config(text="● ONLINE", fg=C["success"])
        log(w, "✓ Started in terminal", "success")
    except Exception as e:
        log(w, f"✗ {e}", "error")

def stop_server(w, status):
    global server_process
    if not server_process or server_process.poll() is not None:
        status.config(text="○ OFFLINE", fg=C["error"]); return
    try:
        if os.name == 'nt': server_process.send_signal(signal.CTRL_BREAK_EVENT)
        else: server_process.terminate()
        server_process.wait(timeout=5)
        log(w, "✓ Stopped", "success")
    except: server_process.kill(); log(w, "✓ Killed", "warning")
    finally: server_process = None; status.config(text="○ OFFLINE", fg=C["error"])

def open_ui(w): webbrowser.open(SERVER_URL); log(w, "Opened browser", "info")

def recog_check(w):
    log(w, "ReCog check...", "recog")
    r = api("/api/recog/check", "POST")
    if "error" in r: log(w, f"✗ {r['error']}", "error")
    else:
        q = r.get("queued", [])
        if q:
            for op in q: log(w, f"  → {op.get('description', op.get('type'))}", "recog")
            log(w, f"✓ {len(q)} queued", "success")
        else: log(w, "Nothing to queue", "info")

def recog_process(w):
    log(w, "Processing...", "recog")
    r = api("/api/recog/process", "POST")
    if "error" in r: log(w, f"✗ {r['error']}", "error")
    elif r.get("processed", 0) > 0:
        log(w, f"✓ {r['processed']} processed", "success")
        if r.get("report_id"): log(w, f"  Report #{r['report_id']}", "info")
    else: log(w, "Nothing confirmed to process", "warning")

def system_status(w):
    log(w, "─" * 35, "info")
    a = api("/api/authority")
    if "error" not in a: log(w, f"Authority: {a.get('percentage',0)}% ({a.get('stage','?')})", "info")
    m = api("/api/mana/balance")
    if "error" not in m: log(w, f"Mana: {m.get('current',0):,} / {m.get('max',0):,}", "info")
    r = api("/api/recog/status")
    if "error" not in r:
        log(w, f"Sessions: {r.get('hot_sessions',0)} hot", "info")
        log(w, f"Insights: {r.get('pending_insights',0)} | Patterns: {r.get('pattern_count',0)}", "info")
    p = api("/api/recog/progression")
    if "error" not in p: log(w, f"Stage: {p.get('stage','?').upper()} | Core: {p.get('core_memories',0)}", "info")
    log(w, "─" * 35, "info")

def refresh_index(w):
    if REFRESH_SCRIPT.exists(): run_async(w, [sys.executable, str(REFRESH_SCRIPT)], str(SCRIPTS_PATH))
    else: log(w, "Script not found", "error")

def refresh_full(w):
    if REFRESH_SCRIPT.exists(): run_async(w, [sys.executable, str(REFRESH_SCRIPT), "--full"], str(SCRIPTS_PATH))
    else: log(w, "Script not found", "error")

def git_push(w):
    p = EHKOFORGE_ROOT / "git_push.bat"
    if p.exists(): subprocess.Popen(['cmd', '/c', 'start', 'cmd', '/k', str(p)], cwd=str(EHKOFORGE_ROOT))
    else: log(w, "git_push.bat not found", "error")

def open_folder(path, w):
    if path.exists(): os.startfile(str(path)) if os.name == 'nt' else subprocess.run(['xdg-open', str(path)])
    else: log(w, f"Not found: {path}", "error")

def clear_log(w): w.config(state=NORMAL); w.delete(1.0, END); w.config(state=DISABLED)

def run_cmd(w, e):
    cmd = e.get().strip()
    if cmd: log(w, f"> {cmd}", "info"); e.delete(0, END); run_async(w, cmd, str(SCRIPTS_PATH), True)

# =============================================================================
# GUI
# =============================================================================

def main():
    root = Tk()
    root.title("◈ EHKOFORGE CONTROL")
    root.geometry("680x480")
    root.configure(bg=C["bg"])
    
    # Styles
    style = ttk.Style()
    style.theme_use('clam')
    style.configure("TFrame", background=C["bg"])
    style.configure("TLabel", background=C["bg"], foreground=C["text"], font=("Consolas", 10))
    style.configure("H.TLabel", font=("Consolas", 13, "bold"), foreground=C["accent"])
    style.configure("TLabelframe", background=C["bg"])
    style.configure("TLabelframe.Label", background=C["bg"], foreground=C["accent_dim"], font=("Consolas", 9, "bold"))
    style.configure("TButton", background=C["bg3"], foreground=C["text"], font=("Consolas", 9), padding=(8, 6))
    style.map("TButton", background=[("active", C["accent_dim"])])
    style.configure("G.TButton", background="#1a3a2a")
    style.map("G.TButton", background=[("active", "#2a5a4a")])
    style.configure("R.TButton", background="#3a1a1a")
    style.map("R.TButton", background=[("active", "#5a2a2a")])
    style.configure("B.TButton", background="#1a2a3a")
    style.map("B.TButton", background=[("active", "#2a4a5a")])
    
    f = ttk.Frame(root, padding=10)
    f.pack(fill=BOTH, expand=True)
    
    # Header
    hdr = ttk.Frame(f)
    hdr.pack(fill=X, pady=(0, 10))
    ttk.Label(hdr, text="◈ EHKOFORGE CONTROL v3.0", style="H.TLabel").pack(side=LEFT)
    status = Label(hdr, text="○ OFFLINE", bg=C["bg"], fg=C["error"], font=("Consolas", 11, "bold"))
    status.pack(side=RIGHT)
    
    # Buttons
    bf = ttk.Frame(f)
    bf.pack(fill=X, pady=(0, 10))
    
    # Server
    sf = ttk.LabelFrame(bf, text="SERVER", padding=5)
    sf.grid(row=0, column=0, padx=(0,3), sticky="nsew")
    ttk.Button(sf, text="▶ Start", command=lambda: start_server(log_w, status), style="G.TButton", width=11).pack(fill=X, pady=2)
    ttk.Button(sf, text="▶ Terminal", command=lambda: start_terminal(log_w, status), style="G.TButton", width=11).pack(fill=X, pady=2)
    ttk.Button(sf, text="■ Stop", command=lambda: stop_server(log_w, status), style="R.TButton", width=11).pack(fill=X, pady=2)
    ttk.Button(sf, text="🌐 Open UI", command=lambda: open_ui(log_w), width=11).pack(fill=X, pady=2)
    
    # ReCog
    rf = ttk.LabelFrame(bf, text="RECOG", padding=5)
    rf.grid(row=0, column=1, padx=3, sticky="nsew")
    ttk.Button(rf, text="⚙ Check", command=lambda: recog_check(log_w), style="R.TButton", width=11).pack(fill=X, pady=2)
    ttk.Button(rf, text="▶ Process", command=lambda: recog_process(log_w), style="R.TButton", width=11).pack(fill=X, pady=2)
    ttk.Button(rf, text="📊 Status", command=lambda: system_status(log_w), width=11).pack(fill=X, pady=2)
    
    # Index
    xf = ttk.LabelFrame(bf, text="INDEX", padding=5)
    xf.grid(row=0, column=2, padx=3, sticky="nsew")
    ttk.Button(xf, text="🔄 Refresh", command=lambda: refresh_index(log_w), style="B.TButton", width=11).pack(fill=X, pady=2)
    ttk.Button(xf, text="🔄 Full", command=lambda: refresh_full(log_w), style="B.TButton", width=11).pack(fill=X, pady=2)
    ttk.Button(xf, text="🚀 Git Push", command=lambda: git_push(log_w), width=11).pack(fill=X, pady=2)
    
    # Folders
    ff = ttk.LabelFrame(bf, text="FOLDERS", padding=5)
    ff.grid(row=0, column=3, padx=(3,0), sticky="nsew")
    ttk.Button(ff, text="📁 EhkoForge", command=lambda: open_folder(EHKOFORGE_ROOT, log_w), width=11).pack(fill=X, pady=2)
    ttk.Button(ff, text="📁 Mirrorwell", command=lambda: open_folder(MIRRORWELL_ROOT, log_w), width=11).pack(fill=X, pady=2)
    ttk.Button(ff, text="📁 Scripts", command=lambda: open_folder(SCRIPTS_PATH, log_w), width=11).pack(fill=X, pady=2)
    
    for i in range(4): bf.columnconfigure(i, weight=1)
    
    # Log
    lf = ttk.LabelFrame(f, text="OUTPUT", padding=5)
    lf.pack(fill=BOTH, expand=True, pady=(0, 8))
    log_w = scrolledtext.ScrolledText(lf, height=8, bg=C["bg2"], fg=C["text"], font=("Consolas", 9),
                                      state=DISABLED, wrap=WORD, relief=FLAT, insertbackground=C["text"])
    log_w.pack(fill=BOTH, expand=True)
    log_w.tag_config("info", foreground=C["text2"])
    log_w.tag_config("success", foreground=C["success"])
    log_w.tag_config("warning", foreground=C["warning"])
    log_w.tag_config("error", foreground=C["error"])
    log_w.tag_config("recog", foreground=C["recog"])
    
    # Command
    cf = ttk.Frame(f)
    cf.pack(fill=X)
    Label(cf, text=">", bg=C["bg"], fg=C["accent"], font=("Consolas", 11, "bold")).pack(side=LEFT)
    cmd = Entry(cf, bg=C["bg3"], fg=C["text"], font=("Consolas", 10), relief=FLAT, insertbackground=C["accent"])
    cmd.pack(side=LEFT, fill=X, expand=True, padx=5, ipady=5)
    cmd.bind("<Return>", lambda e: run_cmd(log_w, cmd))
    ttk.Button(cf, text="Run", width=5, command=lambda: run_cmd(log_w, cmd)).pack(side=RIGHT)
    ttk.Button(cf, text="Clear", width=5, command=lambda: clear_log(log_w)).pack(side=RIGHT, padx=(0,5))
    
    log(log_w, "EhkoForge Control v3.0 ready", "success")
    
    def on_close():
        global server_process
        if server_process and server_process.poll() is None:
            if messagebox.askyesno("Server Running", "Stop server?"): stop_server(log_w, status)
        root.destroy()
    root.protocol("WM_DELETE_WINDOW", on_close)
    
    root.mainloop()

if __name__ == "__main__":
    main()

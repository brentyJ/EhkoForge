#!/usr/bin/env python3
"""
EhkoForge Control Panel v4.3
Consolidated interface with dedicated server log panel.

Features:
- Server control with restart
- ReCog pipeline management  
- Git workflows (Quick + Session)
- Factory Reset for testing
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
import shutil
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
QUICK_COMMIT_SCRIPT = EHKOFORGE_ROOT / "quick_commit.bat"
GIT_PUSH_SCRIPT = EHKOFORGE_ROOT / "git_push.bat"
DATABASE_PATH = EHKOFORGE_ROOT / "_data" / "ehko_index.db"

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
    "server": "#6ecf6e",
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

def api(endpoint, method="GET", data=None, timeout=60):
    try:
        url = f"{SERVER_URL}{endpoint}"
        if method == "POST":
            req = urllib.request.Request(url, json.dumps(data or {}).encode(), 
                                         {'Content-Type': 'application/json'}, method='POST')
        else:
            req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=timeout) as r:
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
            log(w, "Done" if p.returncode == 0 else f"Exit {p.returncode}", 
                "success" if p.returncode == 0 else "error")
        except Exception as e:
            log(w, f"Error: {e}", "error")
    threading.Thread(target=_run, daemon=True).start()

# =============================================================================
# SERVER COMMANDS
# =============================================================================

def start_server(srv_log, status_lbl, start_btn, stop_btn, restart_btn):
    global server_process
    if server_process and server_process.poll() is None:
        log(srv_log, "Server already running", "warning")
        return
    try:
        server_process = subprocess.Popen(
            [sys.executable, str(SERVER_SCRIPT)], 
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, 
            cwd=str(SCRIPTS_PATH), 
            text=True, 
            bufsize=1,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
        )
        status_lbl.config(text="● SERVER ONLINE", fg=C["success"])
        start_btn.config(state=DISABLED)
        stop_btn.config(state=NORMAL)
        restart_btn.config(state=NORMAL)
        log(srv_log, f"Server started (PID {server_process.pid})", "success")
        
        def stream():
            for line in iter(server_process.stdout.readline, ''):
                if line and server_process.poll() is None:
                    line = line.strip()
                    if "ERROR" in line or "error" in line.lower():
                        log(srv_log, line, "error")
                    elif "WARNING" in line or "warn" in line.lower():
                        log(srv_log, line, "warning")
                    elif "[OK]" in line:
                        log(srv_log, line, "success")
                    elif "RECOG" in line or "recog" in line.lower():
                        log(srv_log, line, "recog")
                    else:
                        log(srv_log, line, "server")
            status_lbl.config(text="○ SERVER OFFLINE", fg=C["error"])
            start_btn.config(state=NORMAL)
            stop_btn.config(state=DISABLED)
            restart_btn.config(state=DISABLED)
            log(srv_log, "Server stopped", "warning")
        
        threading.Thread(target=stream, daemon=True).start()
    except Exception as e:
        log(srv_log, f"Failed to start: {e}", "error")

def stop_server(srv_log, status_lbl, start_btn, stop_btn, restart_btn):
    global server_process
    if not server_process or server_process.poll() is not None:
        status_lbl.config(text="○ SERVER OFFLINE", fg=C["error"])
        start_btn.config(state=NORMAL)
        stop_btn.config(state=DISABLED)
        restart_btn.config(state=DISABLED)
        return
    try:
        log(srv_log, "Stopping server...", "warning")
        if os.name == 'nt':
            server_process.send_signal(signal.CTRL_BREAK_EVENT)
        else:
            server_process.terminate()
        server_process.wait(timeout=5)
        log(srv_log, "Server stopped gracefully", "success")
    except:
        server_process.kill()
        log(srv_log, "Server killed", "warning")
    finally:
        server_process = None
        status_lbl.config(text="○ SERVER OFFLINE", fg=C["error"])
        start_btn.config(state=NORMAL)
        stop_btn.config(state=DISABLED)
        restart_btn.config(state=DISABLED)

def restart_server(srv_log, status_lbl, start_btn, stop_btn, restart_btn):
    """Stop and start server."""
    log(srv_log, "Restarting server...", "warning")
    stop_server(srv_log, status_lbl, start_btn, stop_btn, restart_btn)
    # Small delay to ensure port is freed
    import time
    time.sleep(1)
    start_server(srv_log, status_lbl, start_btn, stop_btn, restart_btn)

def open_ui(out_log):
    webbrowser.open(SERVER_URL)
    log(out_log, "Opened browser", "info")

def open_studio(out_log):
    webbrowser.open(f"{SERVER_URL}/studio")
    log(out_log, "Opened Evolution Studio", "info")

# =============================================================================
# FACTORY RESET
# =============================================================================

def factory_reset(out_log, srv_log, status_lbl, start_btn, stop_btn, restart_btn):
    """Reset database to fresh state for testing."""
    global server_process
    
    # Confirm with user
    if not messagebox.askyesno("Factory Reset", 
        "This will:\n"
        "• Stop the server\n"
        "• Delete the database (ehko_index.db)\n"
        "• Re-run all migrations\n"
        "• Clear all ReCog data, sessions, ingots\n\n"
        "Mirrorwell vault files will NOT be deleted.\n\n"
        "Are you sure?"):
        log(out_log, "Factory reset cancelled", "warning")
        return
    
    # Double confirm
    if not messagebox.askyesno("Confirm Reset", 
        "LAST CHANCE!\n\n"
        "All database content will be permanently deleted.\n\n"
        "Continue?"):
        log(out_log, "Factory reset cancelled", "warning")
        return
    
    log(out_log, "=" * 40, "warning")
    log(out_log, "FACTORY RESET INITIATED", "error")
    log(out_log, "=" * 40, "warning")
    
    # Stop server if running
    if server_process and server_process.poll() is None:
        log(out_log, "Stopping server...", "warning")
        stop_server(srv_log, status_lbl, start_btn, stop_btn, restart_btn)
        import time
        time.sleep(1)
    
    # Backup database (just in case)
    if DATABASE_PATH.exists():
        backup_path = DATABASE_PATH.with_suffix('.db.backup')
        try:
            shutil.copy2(DATABASE_PATH, backup_path)
            log(out_log, f"Backup created: {backup_path.name}", "info")
        except Exception as e:
            log(out_log, f"Backup failed: {e}", "warning")
        
        # Delete database
        try:
            DATABASE_PATH.unlink()
            log(out_log, "Database deleted", "success")
        except Exception as e:
            log(out_log, f"Failed to delete database: {e}", "error")
            return
    else:
        log(out_log, "No database found (already clean)", "info")
    
    # Run migrations
    migrations = [
        ("Ingot Migration", SCRIPTS_PATH / "run_ingot_migration.py"),
        ("Reorientation Migration", SCRIPTS_PATH / "run_reorientation_migration.py"),
        ("Mana Migration", SCRIPTS_PATH / "run_mana_migration.py"),
        ("Memory Migration", SCRIPTS_PATH / "run_memory_migration.py"),
        ("Tethers Migration", SCRIPTS_PATH / "run_tethers_migration.py"),
        ("Document Ingestion Migration", SCRIPTS_PATH / "run_ingestion_migration.py"),
        ("Entity Registry Migration", SCRIPTS_PATH / "run_entity_migration.py"),
    ]
    
    def run_migrations():
        for name, script in migrations:
            if script.exists():
                log(out_log, f"Running {name}...", "info")
                try:
                    result = subprocess.run(
                        [sys.executable, str(script)],
                        cwd=str(SCRIPTS_PATH),
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    if result.returncode == 0:
                        log(out_log, f"  {name}: OK", "success")
                    else:
                        log(out_log, f"  {name}: Failed", "error")
                        if result.stderr:
                            log(out_log, f"  {result.stderr[:100]}", "error")
                except Exception as e:
                    log(out_log, f"  {name}: Error - {e}", "error")
            else:
                log(out_log, f"  {name}: Script not found, skipping", "warning")
        
        log(out_log, "=" * 40, "success")
        log(out_log, "FACTORY RESET COMPLETE", "success")
        log(out_log, "Database is now empty. Start server to begin fresh.", "info")
        log(out_log, "=" * 40, "success")
    
    threading.Thread(target=run_migrations, daemon=True).start()

# =============================================================================
# RECOG COMMANDS
# =============================================================================

def recog_check(out_log):
    log(out_log, "ReCog: Checking for work...", "recog")
    r = api("/api/recog/check", "POST")
    if "error" in r:
        log(out_log, f"Error: {r['error']}", "error")
    else:
        q = r.get("queued", [])
        if q:
            for op in q:
                log(out_log, f"  -> {op.get('description', op.get('type'))}", "recog")
            log(out_log, f"Queued {len(q)} operation(s)", "success")
        else:
            log(out_log, "Nothing to queue", "info")

def recog_pending(out_log):
    log(out_log, "ReCog: Fetching pending...", "recog")
    r = api("/api/recog/pending", "GET")
    if "error" in r:
        log(out_log, f"Error: {r['error']}", "error")
    else:
        pending = r.get("pending", [])
        if pending:
            for op in pending:
                status = op.get('status', '?')
                desc = op.get('description', op.get('operation_type', '?'))
                mana = op.get('estimated_mana', 0)
                log(out_log, f"  [{status}] {desc} (~{mana} mana)", "recog")
            log(out_log, f"Total: {len(pending)} pending", "info")
        else:
            log(out_log, "No pending operations", "info")

def recog_confirm_all(out_log):
    log(out_log, "ReCog: Confirming all pending...", "recog")
    r = api("/api/recog/pending", "GET")
    if "error" in r:
        log(out_log, f"Error: {r['error']}", "error")
        return
    
    pending = [op for op in r.get("pending", []) if op.get("status") == "pending"]
    if not pending:
        log(out_log, "No pending operations to confirm", "info")
        return
    
    confirmed = 0
    for op in pending:
        op_id = op.get("id")
        result = api(f"/api/recog/confirm/{op_id}", "POST")
        if "error" not in result and result.get("success"):
            confirmed += 1
            log(out_log, f"  Confirmed #{op_id}", "success")
        else:
            log(out_log, f"  Failed #{op_id}", "error")
    
    log(out_log, f"Confirmed {confirmed}/{len(pending)} operations", "success" if confirmed else "warning")

def recog_process(out_log):
    log(out_log, "ReCog: Processing confirmed operations...", "recog")
    log(out_log, "(This may take 1-2 minutes for LLM calls)", "info")
    
    def _process():
        r = api("/api/recog/process", "POST", timeout=180)
        if "error" in r:
            log(out_log, f"Error: {r['error']}", "error")
        elif r.get("processed", 0) > 0:
            results = r.get("results", [])
            for res in results:
                insights = res.get("insights_created", 0)
                patterns = res.get("patterns_found", 0)
                synths = res.get("syntheses_generated", 0)
                log(out_log, f"  -> {res.get('operation_type')}: {insights}i / {patterns}p / {synths}s", "recog")
            log(out_log, f"Processed {r['processed']} operation(s)", "success")
        else:
            log(out_log, "No confirmed operations to process", "warning")
    
    threading.Thread(target=_process, daemon=True).start()

# =============================================================================
# SYSTEM COMMANDS
# =============================================================================

def system_status(out_log):
    log(out_log, "-" * 40, "info")
    
    a = api("/api/authority")
    if "error" not in a:
        log(out_log, f"Authority: {a.get('percentage',0):.0f}% ({a.get('stage','?')})", "info")
    
    m = api("/api/mana/balance")
    if "error" not in m:
        regen = m.get('regenerating', {})
        purch = m.get('purchased', {})
        log(out_log, f"Mana: {regen.get('current',0):,} regen + {purch.get('current',0):,} purchased", "info")
    
    r = api("/api/recog/status")
    if "error" not in r:
        log(out_log, f"Hot Sessions: {r.get('hot_sessions',0)}", "info")
        log(out_log, f"Pending Insights: {r.get('pending_insights',0)} | Patterns: {r.get('patterns',0)}", "info")
        q = r.get('queue', {})
        if q:
            log(out_log, f"Queue: {q.get('pending',0)} pending, {q.get('ready',0)} ready", "recog")
    
    p = api("/api/recog/progression")
    if "error" not in p:
        log(out_log, f"Ehko Stage: {p.get('stage','?').upper()}", "info")
        log(out_log, f"Core Memories: {p.get('core_memory_count',0)}", "info")
    
    log(out_log, "-" * 40, "info")

def refresh_index(out_log):
    if REFRESH_SCRIPT.exists():
        run_async(out_log, [sys.executable, str(REFRESH_SCRIPT)], str(SCRIPTS_PATH))
    else:
        log(out_log, "ehko_refresh.py not found", "error")

def refresh_full(out_log):
    if REFRESH_SCRIPT.exists():
        run_async(out_log, [sys.executable, str(REFRESH_SCRIPT), "--full"], str(SCRIPTS_PATH))
    else:
        log(out_log, "ehko_refresh.py not found", "error")

def vault_health(out_log):
    if REFRESH_SCRIPT.exists():
        run_async(out_log, [sys.executable, str(REFRESH_SCRIPT), "--health"], str(SCRIPTS_PATH))
    else:
        log(out_log, "ehko_refresh.py not found", "error")

# =============================================================================
# GIT COMMANDS
# =============================================================================

def git_push(out_log):
    """Open git_push.bat for full session commit."""
    if GIT_PUSH_SCRIPT.exists():
        subprocess.Popen(['cmd', '/c', 'start', 'cmd', '/k', str(GIT_PUSH_SCRIPT)], cwd=str(EHKOFORGE_ROOT))
        log(out_log, "Opened git_push.bat", "info")
    else:
        log(out_log, "git_push.bat not found", "error")

def quick_commit(out_log):
    """Interactive git quick commit."""
    if not QUICK_COMMIT_SCRIPT.exists():
        log(out_log, "quick_commit.bat not found", "error")
        return
    
    from tkinter import simpledialog
    msg = simpledialog.askstring("Quick Commit", "Commit message (for small changes):", parent=None)
    
    if msg:
        subprocess.Popen(['cmd', '/c', 'start', 'cmd', '/k', str(QUICK_COMMIT_SCRIPT), msg], 
                        cwd=str(EHKOFORGE_ROOT))
        log(out_log, f"Quick commit: {msg}", "success")
    else:
        log(out_log, "Quick commit cancelled", "warning")

# =============================================================================
# UTILITY COMMANDS
# =============================================================================

def open_folder(path, out_log):
    if path.exists():
        if os.name == 'nt':
            os.startfile(str(path))
        else:
            subprocess.run(['xdg-open', str(path)])
    else:
        log(out_log, f"Not found: {path}", "error")

def clear_log(w):
    w.config(state=NORMAL)
    w.delete(1.0, END)
    w.config(state=DISABLED)

def copy_log(root, w):
    w.config(state=NORMAL)
    content = w.get(1.0, END).strip()
    w.config(state=DISABLED)
    root.clipboard_clear()
    root.clipboard_append(content)
    root.update()

def run_cmd(out_log, entry):
    cmd = entry.get().strip()
    if cmd:
        log(out_log, f"> {cmd}", "info")
        entry.delete(0, END)
        run_async(out_log, cmd, str(SCRIPTS_PATH), True)

# =============================================================================
# GUI
# =============================================================================

def create_log_widget(parent, height=10):
    log_w = scrolledtext.ScrolledText(
        parent, 
        height=height, 
        bg=C["bg2"], 
        fg=C["text"], 
        font=("Consolas", 9),
        state=DISABLED, 
        wrap=WORD, 
        relief=FLAT, 
        insertbackground=C["text"]
    )
    log_w.tag_config("info", foreground=C["text2"])
    log_w.tag_config("success", foreground=C["success"])
    log_w.tag_config("warning", foreground=C["warning"])
    log_w.tag_config("error", foreground=C["error"])
    log_w.tag_config("recog", foreground=C["recog"])
    log_w.tag_config("server", foreground=C["server"])
    return log_w

def main():
    root = Tk()
    root.title("EHKOFORGE CONTROL")
    root.geometry("850x750")
    root.minsize(750, 550)
    root.configure(bg=C["bg"])
    
    # Styles
    style = ttk.Style()
    style.theme_use('clam')
    style.configure("TFrame", background=C["bg"])
    style.configure("TLabel", background=C["bg"], foreground=C["text"], font=("Consolas", 10))
    style.configure("H.TLabel", font=("Consolas", 14, "bold"), foreground=C["accent"])
    style.configure("TLabelframe", background=C["bg"])
    style.configure("TLabelframe.Label", background=C["bg"], foreground=C["accent_dim"], font=("Consolas", 9, "bold"))
    style.configure("TButton", background=C["bg3"], foreground=C["text"], font=("Consolas", 9), padding=(8, 5))
    style.map("TButton", background=[("active", C["accent_dim"]), ("disabled", C["bg2"])])
    style.configure("G.TButton", background="#1a3a2a")
    style.map("G.TButton", background=[("active", "#2a5a4a"), ("disabled", "#0a1a0a")])
    style.configure("R.TButton", background="#3a1a1a")
    style.map("R.TButton", background=[("active", "#5a2a2a"), ("disabled", "#1a0a0a")])
    style.configure("B.TButton", background="#1a2a3a")
    style.map("B.TButton", background=[("active", "#2a4a5a")])
    style.configure("Y.TButton", background="#3a3a1a")
    style.map("Y.TButton", background=[("active", "#5a5a2a")])
    
    main_frame = ttk.Frame(root, padding=10)
    main_frame.pack(fill=BOTH, expand=True)
    
    # === HEADER ===
    header = ttk.Frame(main_frame)
    header.pack(fill=X, pady=(0, 10))
    ttk.Label(header, text="EHKOFORGE CONTROL v4.3", style="H.TLabel").pack(side=LEFT)
    status_lbl = Label(header, text="○ SERVER OFFLINE", bg=C["bg"], fg=C["error"], font=("Consolas", 11, "bold"))
    status_lbl.pack(side=RIGHT)
    
    # === SERVER SECTION ===
    srv_frame = ttk.LabelFrame(main_frame, text="SERVER", padding=5)
    srv_frame.pack(fill=BOTH, expand=True, pady=(0, 10))
    
    srv_btn_frame = ttk.Frame(srv_frame)
    srv_btn_frame.pack(fill=X, pady=(0, 5))
    
    start_btn = ttk.Button(srv_btn_frame, text="Start", style="G.TButton", width=10)
    start_btn.pack(side=LEFT, padx=(0, 5))
    
    stop_btn = ttk.Button(srv_btn_frame, text="Stop", style="R.TButton", width=8, state=DISABLED)
    stop_btn.pack(side=LEFT, padx=(0, 5))
    
    restart_btn = ttk.Button(srv_btn_frame, text="Restart", style="Y.TButton", width=8, state=DISABLED)
    restart_btn.pack(side=LEFT, padx=(0, 5))
    
    ttk.Button(srv_btn_frame, text="Open UI", width=8, 
               command=lambda: open_ui(out_log)).pack(side=LEFT, padx=(0, 5))
    
    ttk.Button(srv_btn_frame, text="Studio", width=8,
               command=lambda: open_studio(out_log)).pack(side=LEFT, padx=(0, 5))
    
    ttk.Button(srv_btn_frame, text="Copy", width=6,
               command=lambda: copy_log(root, srv_log)).pack(side=RIGHT, padx=(0, 5))
    
    ttk.Button(srv_btn_frame, text="Clear", width=6,
               command=lambda: clear_log(srv_log)).pack(side=RIGHT)
    
    srv_log = create_log_widget(srv_frame, height=12)
    srv_log.pack(fill=BOTH, expand=True)
    
    # Wire up server buttons
    start_btn.config(command=lambda: start_server(srv_log, status_lbl, start_btn, stop_btn, restart_btn))
    stop_btn.config(command=lambda: stop_server(srv_log, status_lbl, start_btn, stop_btn, restart_btn))
    restart_btn.config(command=lambda: threading.Thread(target=lambda: restart_server(srv_log, status_lbl, start_btn, stop_btn, restart_btn), daemon=True).start())
    
    # === TOOLS SECTION ===
    tools_frame = ttk.Frame(main_frame)
    tools_frame.pack(fill=X, pady=(0, 10))
    
    # ReCog
    recog_frame = ttk.LabelFrame(tools_frame, text="RECOG", padding=5)
    recog_frame.grid(row=0, column=0, padx=(0, 5), sticky="nsew")
    
    ttk.Button(recog_frame, text="Check", style="R.TButton", width=10,
               command=lambda: recog_check(out_log)).pack(side=LEFT, padx=2)
    ttk.Button(recog_frame, text="Confirm All", width=10,
               command=lambda: recog_confirm_all(out_log)).pack(side=LEFT, padx=2)
    ttk.Button(recog_frame, text="Process", style="R.TButton", width=10,
               command=lambda: recog_process(out_log)).pack(side=LEFT, padx=2)
    ttk.Button(recog_frame, text="Pending", width=8,
               command=lambda: recog_pending(out_log)).pack(side=LEFT, padx=2)
    
    # Git
    git_frame = ttk.LabelFrame(tools_frame, text="GIT", padding=5)
    git_frame.grid(row=0, column=1, padx=(5, 0), sticky="nsew")
    
    ttk.Button(git_frame, text="Quick", style="G.TButton", width=8,
               command=lambda: quick_commit(out_log)).pack(side=LEFT, padx=2)
    ttk.Button(git_frame, text="Git Push", style="B.TButton", width=10,
               command=lambda: git_push(out_log)).pack(side=LEFT, padx=2)
    
    tools_frame.columnconfigure(0, weight=2)
    tools_frame.columnconfigure(1, weight=1)
    
    # === SYSTEM SECTION ===
    sys_frame = ttk.Frame(main_frame)
    sys_frame.pack(fill=X, pady=(0, 10))
    
    sys_left = ttk.LabelFrame(sys_frame, text="SYSTEM", padding=5)
    sys_left.grid(row=0, column=0, padx=(0, 5), sticky="nsew")
    
    ttk.Button(sys_left, text="Status", width=8,
               command=lambda: system_status(out_log)).pack(side=LEFT, padx=2)
    ttk.Button(sys_left, text="Index", style="B.TButton", width=8,
               command=lambda: refresh_index(out_log)).pack(side=LEFT, padx=2)
    ttk.Button(sys_left, text="Health", width=8,
               command=lambda: vault_health(out_log)).pack(side=LEFT, padx=2)
    
    # Danger zone
    danger_frame = ttk.LabelFrame(sys_frame, text="DANGER ZONE", padding=5)
    danger_frame.grid(row=0, column=1, padx=(5, 0), sticky="nsew")
    
    ttk.Button(danger_frame, text="Factory Reset", style="R.TButton", width=14,
               command=lambda: factory_reset(out_log, srv_log, status_lbl, start_btn, stop_btn, restart_btn)).pack(side=LEFT, padx=2)
    
    sys_frame.columnconfigure(0, weight=2)
    sys_frame.columnconfigure(1, weight=1)
    
    # === OUTPUT SECTION ===
    out_frame = ttk.LabelFrame(main_frame, text="OUTPUT", padding=5)
    out_frame.pack(fill=BOTH, expand=True, pady=(0, 8))
    
    out_log = create_log_widget(out_frame, height=8)
    out_log.pack(fill=BOTH, expand=True)
    
    # === COMMAND LINE ===
    cmd_frame = ttk.Frame(main_frame)
    cmd_frame.pack(fill=X)
    
    Label(cmd_frame, text=">", bg=C["bg"], fg=C["accent"], font=("Consolas", 11, "bold")).pack(side=LEFT)
    
    cmd_entry = Entry(cmd_frame, bg=C["bg3"], fg=C["text"], font=("Consolas", 10), 
                      relief=FLAT, insertbackground=C["accent"])
    cmd_entry.pack(side=LEFT, fill=X, expand=True, padx=5, ipady=5)
    cmd_entry.bind("<Return>", lambda e: run_cmd(out_log, cmd_entry))
    
    ttk.Button(cmd_frame, text="Run", width=6, 
               command=lambda: run_cmd(out_log, cmd_entry)).pack(side=RIGHT)
    ttk.Button(cmd_frame, text="Copy", width=6,
               command=lambda: copy_log(root, out_log)).pack(side=RIGHT, padx=(0, 5))
    ttk.Button(cmd_frame, text="Clear", width=6,
               command=lambda: clear_log(out_log)).pack(side=RIGHT, padx=(0, 5))
    
    # Quick folder buttons
    folder_frame = ttk.Frame(main_frame)
    folder_frame.pack(fill=X, pady=(8, 0))
    
    ttk.Button(folder_frame, text="EhkoForge", width=10,
               command=lambda: open_folder(EHKOFORGE_ROOT, out_log)).pack(side=LEFT, padx=(0, 5))
    ttk.Button(folder_frame, text="Mirrorwell", width=10,
               command=lambda: open_folder(MIRRORWELL_ROOT, out_log)).pack(side=LEFT, padx=(0, 5))
    ttk.Button(folder_frame, text="Scripts", width=10,
               command=lambda: open_folder(SCRIPTS_PATH, out_log)).pack(side=LEFT)
    
    # Initial log
    log(out_log, "EhkoForge Control v4.3 ready", "success")
    log(out_log, "Start server to begin", "info")
    
    # Close handler
    def on_close():
        global server_process
        if server_process and server_process.poll() is None:
            if messagebox.askyesno("Server Running", "Stop server before closing?"):
                stop_server(srv_log, status_lbl, start_btn, stop_btn, restart_btn)
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()

if __name__ == "__main__":
    main()

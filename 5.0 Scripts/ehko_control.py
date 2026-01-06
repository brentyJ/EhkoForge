#!/usr/bin/env python3
"""
Ehko Control Panel v5.2
Unified interface with tabbed navigation for EhkoForge, ReCog, Website, and GlyphWorks.

Optimised for Surface Pro touch screen (2196 x 1464).
Terminal aesthetic matching EhkoLabs website.

Tabs:
- EhkoForge: Server control, integrated ReCog, Git, System tools
- ReCog: Standalone ReCog server \+ React UI dev server
- Website: Astro dev server for local testing
- GlyphWorks: Advanced SVG art creation and rendering
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
import re
import math
from datetime import datetime
from pathlib import Path
from tkinter import *
from tkinter import ttk, messagebox, scrolledtext, colorchooser, filedialog

# =============================================================================
# CONFIGURATION
# =============================================================================

EHKOFORGE_ROOT = Path("C:/EhkoVaults/EhkoForge")
MIRRORWELL_ROOT = Path("C:/EhkoVaults/Mirrorwell")
SCRIPTS_PATH = EHKOFORGE_ROOT / "5.0 Scripts"
SERVER_SCRIPT = SCRIPTS_PATH / "forge_server.py"
SERVER_URL = "http://localhost:5000"

# ReCog Configuration
RECOG_ROOT = Path("C:/EhkoVaults/ReCog")
RECOG_SCRIPTS = RECOG_ROOT / "_scripts"
RECOG_SERVER_SCRIPT = RECOG_SCRIPTS / "server.py"
RECOG_URL = "http://localhost:5100"
RECOG_UI_PATH = RECOG_ROOT / "_ui"
RECOG_UI_URL = "http://localhost:3100"

# Website Configuration
WEBSITE_PATH = Path("C:/EhkoDev/ehkolabs-website")
WEBSITE_URL = "http://localhost:4321"

# Automation scripts
AUTOMATION_PATH = Path("C:/EhkoVaults/.automation/scripts")
GITHUB_PROJECT_SYNC = AUTOMATION_PATH / "github_project_sync.py"

REFRESH_SCRIPT = SCRIPTS_PATH / "ehko_refresh.py"
QUICK_COMMIT_SCRIPT = EHKOFORGE_ROOT / "quick_commit.bat"
GIT_PUSH_SCRIPT = EHKOFORGE_ROOT / "git_push.bat"
DATABASE_PATH = EHKOFORGE_ROOT / "_data" / "ehko_index.db"
GLYPHWORKS_OUTPUT = EHKOFORGE_ROOT / "_data" / "glyphworks"

# Terminal Blue Palette (matching website)
C = {
    # Backgrounds
    "bg_primary": "#080a0e",
    "bg_secondary": "#0c1018",
    "bg_tertiary": "#111620",
    "bg_elevated": "#161c28",
    
    # Text
    "text_primary": "#e8eef8",
    "text_secondary": "#8aa4d6",
    "text_muted": "#4a6fa5",
    "text_dim": "#3d5a80",
    
    # Accents
    "accent": "#6b8cce",
    "accent_dim": "#4a6fa5",
    "accent_glow": "#3d5a80",
    
    # Status
    "success": "#5fb3a1",
    "warning": "#d9c67e",
    "error": "#d97373",
    "recog": "#c94a4a",
    
    # Semantic
    "server": "#5fb3a1",
    "website": "#6eb3cf",
    "glyph": "#9b7ed9",
    
    # Borders
    "border": "rgba(107, 140, 206, 0.3)",
    "border_subtle": "#1c2a3a",
}

# Process handles
server_process = None
recog_process = None
recog_ui_process = None
website_process = None

# =============================================================================
# HELPERS
# =============================================================================

def log(widget, msg, tag=None):
    """Append timestamped message to log widget."""
    ts = datetime.now().strftime("%H:%M:%S")
    widget.config(state=NORMAL)
    widget.insert(END, f"[{ts}] {msg}\n", tag or ())
    widget.see(END)
    widget.config(state=DISABLED)

def api(endpoint, method="GET", data=None, timeout=60, base_url=SERVER_URL):
    """Make API request to server."""
    try:
        url = f"{base_url}{endpoint}"
        if method == "POST":
            req = urllib.request.Request(
                url, 
                json.dumps(data or {}).encode(),
                {'Content-Type': 'application/json'}, 
                method='POST'
            )
        else:
            req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read())
    except Exception as e:
        return {"error": str(e)}

def run_async(log_widget, cmd, cwd=None, shell=False):
    """Run command asynchronously, streaming output to log."""
    def _run():
        try:
            p = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT,
                cwd=cwd, 
                shell=shell, 
                text=True, 
                bufsize=1
            )
            for line in iter(p.stdout.readline, ''):
                if line:
                    log(log_widget, line.strip())
            p.wait()
            log(log_widget, "Done" if p.returncode == 0 else f"Exit {p.returncode}",
                "success" if p.returncode == 0 else "error")
        except Exception as e:
            log(log_widget, f"Error: {e}", "error")
    threading.Thread(target=_run, daemon=True).start()

# =============================================================================
# CUSTOM WIDGETS
# =============================================================================

class TerminalLog(scrolledtext.ScrolledText):
    """Styled log widget matching terminal aesthetic."""
    
    def __init__(self, parent, height=12, **kwargs):
        super().__init__(
            parent,
            height=height,
            bg=C["bg_secondary"],
            fg=C["text_primary"],
            font=("Consolas", 10),
            state=DISABLED,
            wrap=WORD,
            relief=FLAT,
            insertbackground=C["text_primary"],
            selectbackground=C["accent_dim"],
            selectforeground=C["text_primary"],
            padx=8,
            pady=8,
            **kwargs
        )
        self._setup_tags()
    
    def _setup_tags(self):
        self.tag_config("info", foreground=C["text_secondary"])
        self.tag_config("success", foreground=C["success"])
        self.tag_config("warning", foreground=C["warning"])
        self.tag_config("error", foreground=C["error"])
        self.tag_config("recog", foreground=C["recog"])
        self.tag_config("server", foreground=C["server"])
        self.tag_config("website", foreground=C["website"])
        self.tag_config("glyph", foreground=C["glyph"])
        self.tag_config("dim", foreground=C["text_dim"])
    
    def clear(self):
        self.config(state=NORMAL)
        self.delete(1.0, END)
        self.config(state=DISABLED)
    
    def copy_contents(self, root):
        self.config(state=NORMAL)
        content = self.get(1.0, END).strip()
        self.config(state=DISABLED)
        root.clipboard_clear()
        root.clipboard_append(content)
        root.update()


class TerminalButton(ttk.Button):
    """Touch-friendly button with terminal styling."""
    pass


class StatusIndicator(Label):
    """Status indicator with dot and label."""
    
    def __init__(self, parent, text="OFFLINE", **kwargs):
        super().__init__(
            parent,
            bg=C["bg_primary"],
            fg=C["error"],
            font=("Consolas", 11, "bold"),
            **kwargs
        )
        self.set_offline(text)
    
    def set_online(self, text="ONLINE"):
        self.config(text=f"● {text}", fg=C["success"])
    
    def set_offline(self, text="OFFLINE"):
        self.config(text=f"○ {text}", fg=C["error"])
    
    def set_warning(self, text="WARNING"):
        self.config(text=f"◐ {text}", fg=C["warning"])


# =============================================================================
# EHKOFORGE TAB - Server, ReCog, Git, System
# =============================================================================

class EhkoForgeTab(ttk.Frame):
    """Main EhkoForge control tab."""
    
    def __init__(self, parent, root):
        super().__init__(parent)
        self.root = root
        self.configure(style="TFrame")
        self._build_ui()
    
    def _build_ui(self):
        # Main container with padding
        container = ttk.Frame(self, padding=10)
        container.pack(fill=BOTH, expand=True)
        
        # === TOP ROW: Server + Status ===
        top_row = ttk.Frame(container)
        top_row.pack(fill=X, pady=(0, 10))
        
        # Server controls
        srv_frame = ttk.LabelFrame(top_row, text="SERVER (Port 5000)", padding=8)
        srv_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 5))
        
        btn_row = ttk.Frame(srv_frame)
        btn_row.pack(fill=X, pady=(0, 8))
        
        self.start_btn = ttk.Button(btn_row, text="▶ Start", style="G.TButton", width=12,
                                     command=self._start_server)
        self.start_btn.pack(side=LEFT, padx=2)
        
        self.stop_btn = ttk.Button(btn_row, text="■ Stop", style="R.TButton", width=10,
                                    state=DISABLED, command=self._stop_server)
        self.stop_btn.pack(side=LEFT, padx=2)
        
        self.restart_btn = ttk.Button(btn_row, text="↻ Restart", style="Y.TButton", width=10,
                                       state=DISABLED, command=self._restart_server)
        self.restart_btn.pack(side=LEFT, padx=2)
        
        ttk.Separator(btn_row, orient=VERTICAL).pack(side=LEFT, fill=Y, padx=8)
        
        ttk.Button(btn_row, text="Open UI", width=10,
                   command=self._open_ui).pack(side=LEFT, padx=2)
        ttk.Button(btn_row, text="Studio", width=10,
                   command=self._open_studio).pack(side=LEFT, padx=2)
        
        # Status indicator
        self.status = StatusIndicator(btn_row, "SERVER OFFLINE")
        self.status.pack(side=RIGHT, padx=10)
        
        # Server log
        self.srv_log = TerminalLog(srv_frame, height=10)
        self.srv_log.pack(fill=BOTH, expand=True)
        
        log_btns = ttk.Frame(srv_frame)
        log_btns.pack(fill=X, pady=(5, 0))
        ttk.Button(log_btns, text="Clear", width=8,
                   command=self.srv_log.clear).pack(side=RIGHT, padx=2)
        ttk.Button(log_btns, text="Copy", width=8,
                   command=lambda: self.srv_log.copy_contents(self.root)).pack(side=RIGHT, padx=2)
        
        # === MIDDLE ROW: ReCog + Git ===
        mid_row = ttk.Frame(container)
        mid_row.pack(fill=X, pady=(0, 10))
        
        # ReCog controls (for EhkoForge integrated ReCog)
        recog_frame = ttk.LabelFrame(mid_row, text="RECOG ENGINE (Integrated)", padding=8)
        recog_frame.pack(side=LEFT, fill=X, expand=True, padx=(0, 5))
        
        ttk.Button(recog_frame, text="Check", style="Accent.TButton", width=10,
                   command=self._recog_check).pack(side=LEFT, padx=2)
        ttk.Button(recog_frame, text="Pending", width=10,
                   command=self._recog_pending).pack(side=LEFT, padx=2)
        ttk.Button(recog_frame, text="Confirm All", width=12,
                   command=self._recog_confirm).pack(side=LEFT, padx=2)
        ttk.Button(recog_frame, text="Process", style="Accent.TButton", width=10,
                   command=self._recog_process).pack(side=LEFT, padx=2)
        
        # Git controls
        git_frame = ttk.LabelFrame(mid_row, text="GIT", padding=8)
        git_frame.pack(side=LEFT, fill=X, padx=(5, 0))
        
        ttk.Button(git_frame, text="Quick Commit", style="G.TButton", width=14,
                   command=self._quick_commit).pack(side=LEFT, padx=2)
        ttk.Button(git_frame, text="Git Push", style="B.TButton", width=12,
                   command=self._git_push).pack(side=LEFT, padx=2)
        
        # === GITHUB PROJECT ROW ===
        github_row = ttk.Frame(container)
        github_row.pack(fill=X, pady=(0, 10))
        
        github_frame = ttk.LabelFrame(github_row, text="GITHUB PROJECT AUTOMATION", padding=8)
        github_frame.pack(side=LEFT, fill=X, expand=True)
        
        ttk.Button(github_frame, text="⚡ Sync Project", style="Accent.TButton", width=14,
                   command=self._github_sync).pack(side=LEFT, padx=2)
        ttk.Button(github_frame, text="Dry Run", width=10,
                   command=self._github_sync_dry).pack(side=LEFT, padx=2)
        ttk.Button(github_frame, text="Archive Done", width=12,
                   command=self._github_archive).pack(side=LEFT, padx=2)
        ttk.Button(github_frame, text="📊 Open Project", style="B.TButton", width=14,
                   command=self._github_open).pack(side=LEFT, padx=2)
        
        # === SYSTEM ROW ===
        sys_row = ttk.Frame(container)
        sys_row.pack(fill=X, pady=(0, 10))
        
        sys_frame = ttk.LabelFrame(sys_row, text="SYSTEM", padding=8)
        sys_frame.pack(side=LEFT, fill=X, expand=True, padx=(0, 5))
        
        ttk.Button(sys_frame, text="Status", width=10,
                   command=self._system_status).pack(side=LEFT, padx=2)
        ttk.Button(sys_frame, text="Refresh Index", width=14,
                   command=self._refresh_index).pack(side=LEFT, padx=2)
        ttk.Button(sys_frame, text="Full Reindex", width=12,
                   command=self._refresh_full).pack(side=LEFT, padx=2)
        ttk.Button(sys_frame, text="Health Check", width=12,
                   command=self._health_check).pack(side=LEFT, padx=2)
        
        # Danger zone
        danger_frame = ttk.LabelFrame(sys_row, text="⚠ DANGER", padding=8)
        danger_frame.pack(side=LEFT, padx=(5, 0))
        
        ttk.Button(danger_frame, text="Factory Reset", style="R.TButton", width=14,
                   command=self._factory_reset).pack(side=LEFT, padx=2)
        
        # === OUTPUT LOG ===
        out_frame = ttk.LabelFrame(container, text="OUTPUT", padding=8)
        out_frame.pack(fill=BOTH, expand=True)
        
        self.out_log = TerminalLog(out_frame, height=12)
        self.out_log.pack(fill=BOTH, expand=True)
        
        out_btns = ttk.Frame(out_frame)
        out_btns.pack(fill=X, pady=(5, 0))
        
        # Folder shortcuts
        ttk.Button(out_btns, text="📁 EhkoForge", width=12,
                   command=lambda: self._open_folder(EHKOFORGE_ROOT)).pack(side=LEFT, padx=2)
        ttk.Button(out_btns, text="📁 Mirrorwell", width=12,
                   command=lambda: self._open_folder(MIRRORWELL_ROOT)).pack(side=LEFT, padx=2)
        ttk.Button(out_btns, text="📁 Scripts", width=10,
                   command=lambda: self._open_folder(SCRIPTS_PATH)).pack(side=LEFT, padx=2)
        
        ttk.Button(out_btns, text="Clear", width=8,
                   command=self.out_log.clear).pack(side=RIGHT, padx=2)
        ttk.Button(out_btns, text="Copy", width=8,
                   command=lambda: self.out_log.copy_contents(self.root)).pack(side=RIGHT, padx=2)
        
        # Initial message
        log(self.out_log, "EhkoForge ready. Start server to begin.", "info")
    
    # === SERVER METHODS ===
    def _start_server(self):
        global server_process
        if server_process and server_process.poll() is None:
            log(self.srv_log, "Server already running", "warning")
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
            self.status.set_online("SERVER ONLINE")
            self.start_btn.config(state=DISABLED)
            self.stop_btn.config(state=NORMAL)
            self.restart_btn.config(state=NORMAL)
            log(self.srv_log, f"Server started (PID {server_process.pid})", "success")
            
            def stream():
                for line in iter(server_process.stdout.readline, ''):
                    if line and server_process.poll() is None:
                        line = line.strip()
                        if "ERROR" in line or "error" in line.lower():
                            log(self.srv_log, line, "error")
                        elif "WARNING" in line or "warn" in line.lower():
                            log(self.srv_log, line, "warning")
                        elif "[OK]" in line:
                            log(self.srv_log, line, "success")
                        elif "RECOG" in line or "recog" in line.lower():
                            log(self.srv_log, line, "recog")
                        else:
                            log(self.srv_log, line, "server")
                self.status.set_offline("SERVER OFFLINE")
                self.start_btn.config(state=NORMAL)
                self.stop_btn.config(state=DISABLED)
                self.restart_btn.config(state=DISABLED)
                log(self.srv_log, "Server stopped", "warning")
            
            threading.Thread(target=stream, daemon=True).start()
        except Exception as e:
            log(self.srv_log, f"Failed to start: {e}", "error")
    
    def _stop_server(self):
        global server_process
        if not server_process or server_process.poll() is not None:
            self.status.set_offline("SERVER OFFLINE")
            self.start_btn.config(state=NORMAL)
            self.stop_btn.config(state=DISABLED)
            self.restart_btn.config(state=DISABLED)
            return
        
        try:
            log(self.srv_log, "Stopping server...", "warning")
            if os.name == 'nt':
                server_process.send_signal(signal.CTRL_BREAK_EVENT)
            else:
                server_process.terminate()
            server_process.wait(timeout=5)
            log(self.srv_log, "Server stopped gracefully", "success")
        except:
            server_process.kill()
            log(self.srv_log, "Server killed", "warning")
        finally:
            server_process = None
            self.status.set_offline("SERVER OFFLINE")
            self.start_btn.config(state=NORMAL)
            self.stop_btn.config(state=DISABLED)
            self.restart_btn.config(state=DISABLED)
    
    def _restart_server(self):
        def restart():
            log(self.srv_log, "Restarting server...", "warning")
            self._stop_server()
            import time
            time.sleep(1)
            self._start_server()
        threading.Thread(target=restart, daemon=True).start()
    
    def _open_ui(self):
        webbrowser.open(SERVER_URL)
        log(self.out_log, "Opened Forge UI", "info")
    
    def _open_studio(self):
        webbrowser.open(f"{SERVER_URL}/studio")
        log(self.out_log, "Opened Evolution Studio", "info")
    
    # === RECOG METHODS ===
    def _recog_check(self):
        log(self.out_log, "ReCog: Checking for work...", "recog")
        r = api("/api/recog/check", "POST")
        if "error" in r:
            log(self.out_log, f"Error: {r['error']}", "error")
        else:
            q = r.get("queued", [])
            if q:
                for op in q:
                    log(self.out_log, f"  → {op.get('description', op.get('type'))}", "recog")
                log(self.out_log, f"Queued {len(q)} operation(s)", "success")
            else:
                log(self.out_log, "Nothing to queue", "info")
    
    def _recog_pending(self):
        log(self.out_log, "ReCog: Fetching pending...", "recog")
        r = api("/api/recog/pending")
        if "error" in r:
            log(self.out_log, f"Error: {r['error']}", "error")
        else:
            pending = r.get("pending", [])
            if pending:
                for op in pending:
                    status = op.get('status', '?')
                    desc = op.get('description', op.get('operation_type', '?'))
                    mana = op.get('estimated_mana', 0)
                    log(self.out_log, f"  [{status}] {desc} (~{mana} mana)", "recog")
                log(self.out_log, f"Total: {len(pending)} pending", "info")
            else:
                log(self.out_log, "No pending operations", "info")
    
    def _recog_confirm(self):
        log(self.out_log, "ReCog: Confirming all pending...", "recog")
        r = api("/api/recog/pending")
        if "error" in r:
            log(self.out_log, f"Error: {r['error']}", "error")
            return
        
        pending = [op for op in r.get("pending", []) if op.get("status") == "pending"]
        if not pending:
            log(self.out_log, "No pending operations to confirm", "info")
            return
        
        confirmed = 0
        for op in pending:
            op_id = op.get("id")
            result = api(f"/api/recog/confirm/{op_id}", "POST")
            if "error" not in result and result.get("success"):
                confirmed += 1
                log(self.out_log, f"  Confirmed #{op_id}", "success")
            else:
                log(self.out_log, f"  Failed #{op_id}", "error")
        
        log(self.out_log, f"Confirmed {confirmed}/{len(pending)}", "success" if confirmed else "warning")
    
    def _recog_process(self):
        log(self.out_log, "ReCog: Processing... (may take 1-2 min)", "recog")
        
        def _process():
            r = api("/api/recog/process", "POST", timeout=180)
            if "error" in r:
                log(self.out_log, f"Error: {r['error']}", "error")
            elif r.get("processed", 0) > 0:
                results = r.get("results", [])
                for res in results:
                    insights = res.get("insights_created", 0)
                    patterns = res.get("patterns_found", 0)
                    synths = res.get("syntheses_generated", 0)
                    log(self.out_log, f"  → {res.get('operation_type')}: {insights}i / {patterns}p / {synths}s", "recog")
                log(self.out_log, f"Processed {r['processed']} operation(s)", "success")
            else:
                log(self.out_log, "No confirmed operations to process", "warning")
        
        threading.Thread(target=_process, daemon=True).start()
    
    # === GIT METHODS ===
    def _quick_commit(self):
        if not QUICK_COMMIT_SCRIPT.exists():
            log(self.out_log, "quick_commit.bat not found", "error")
            return
        
        from tkinter import simpledialog
        msg = simpledialog.askstring("Quick Commit", "Commit message:", parent=self.root)
        if msg:
            subprocess.Popen(['cmd', '/c', 'start', 'cmd', '/k', str(QUICK_COMMIT_SCRIPT), msg],
                           cwd=str(EHKOFORGE_ROOT))
            log(self.out_log, f"Quick commit: {msg}", "success")
        else:
            log(self.out_log, "Cancelled", "warning")
    
    def _git_push(self):
        if GIT_PUSH_SCRIPT.exists():
            subprocess.Popen(['cmd', '/c', 'start', 'cmd', '/k', str(GIT_PUSH_SCRIPT)],
                           cwd=str(EHKOFORGE_ROOT))
            log(self.out_log, "Opened git_push.bat", "info")
        else:
            log(self.out_log, "git_push.bat not found", "error")
    
    # === SYSTEM METHODS ===
    def _system_status(self):
        log(self.out_log, "─" * 40, "dim")
        
        a = api("/api/authority")
        if "error" not in a:
            log(self.out_log, f"Authority: {a.get('percentage', 0):.0f}% ({a.get('stage', '?')})", "info")
        
        m = api("/api/mana/balance")
        if "error" not in m:
            regen = m.get('regenerating', {})
            purch = m.get('purchased', {})
            log(self.out_log, f"Mana: {regen.get('current', 0):,} regen + {purch.get('current', 0):,} purchased", "info")
        
        r = api("/api/recog/status")
        if "error" not in r:
            log(self.out_log, f"Hot Sessions: {r.get('hot_sessions', 0)}", "info")
            log(self.out_log, f"Pending Insights: {r.get('pending_insights', 0)} | Patterns: {r.get('patterns', 0)}", "info")
            q = r.get('queue', {})
            if q:
                log(self.out_log, f"Queue: {q.get('pending', 0)} pending, {q.get('ready', 0)} ready", "recog")
        
        p = api("/api/recog/progression")
        if "error" not in p:
            log(self.out_log, f"Ehko Stage: {p.get('stage', '?').upper()}", "info")
            log(self.out_log, f"Core Memories: {p.get('core_memory_count', 0)}", "info")
        
        log(self.out_log, "─" * 40, "dim")
    
    def _refresh_index(self):
        if REFRESH_SCRIPT.exists():
            run_async(self.out_log, [sys.executable, str(REFRESH_SCRIPT)], str(SCRIPTS_PATH))
        else:
            log(self.out_log, "ehko_refresh.py not found", "error")
    
    def _refresh_full(self):
        if REFRESH_SCRIPT.exists():
            run_async(self.out_log, [sys.executable, str(REFRESH_SCRIPT), "--full"], str(SCRIPTS_PATH))
        else:
            log(self.out_log, "ehko_refresh.py not found", "error")
    
    def _health_check(self):
        if REFRESH_SCRIPT.exists():
            run_async(self.out_log, [sys.executable, str(REFRESH_SCRIPT), "--health"], str(SCRIPTS_PATH))
        else:
            log(self.out_log, "ehko_refresh.py not found", "error")
    
    def _factory_reset(self):
        global server_process
        
        if not messagebox.askyesno("Factory Reset",
            "This will:\n"
            "• Stop the server\n"
            "• Delete the database\n"
            "• Re-run all migrations\n\n"
            "Vault files will NOT be deleted.\n\n"
            "Continue?"):
            return
        
        if not messagebox.askyesno("Confirm", "LAST CHANCE!\n\nAll database content will be deleted.\n\nContinue?"):
            return
        
        log(self.out_log, "=" * 40, "error")
        log(self.out_log, "FACTORY RESET INITIATED", "error")
        log(self.out_log, "=" * 40, "error")
        
        if server_process and server_process.poll() is None:
            log(self.out_log, "Stopping server...", "warning")
            self._stop_server()
            import time
            time.sleep(1)
        
        if DATABASE_PATH.exists():
            backup_path = DATABASE_PATH.with_suffix('.db.backup')
            try:
                shutil.copy2(DATABASE_PATH, backup_path)
                log(self.out_log, f"Backup: {backup_path.name}", "info")
            except Exception as e:
                log(self.out_log, f"Backup failed: {e}", "warning")
            
            try:
                DATABASE_PATH.unlink()
                log(self.out_log, "Database deleted", "success")
            except Exception as e:
                log(self.out_log, f"Delete failed: {e}", "error")
                return
        else:
            log(self.out_log, "No database (already clean)", "info")
        
        migrations = [
            ("Ingot Migration", SCRIPTS_PATH / "run_ingot_migration.py"),
            ("Reorientation", SCRIPTS_PATH / "run_reorientation_migration.py"),
            ("Mana", SCRIPTS_PATH / "run_mana_migration.py"),
            ("Memory", SCRIPTS_PATH / "run_memory_migration.py"),
            ("Tethers", SCRIPTS_PATH / "run_tethers_migration.py"),
            ("Ingestion", SCRIPTS_PATH / "run_ingestion_migration.py"),
            ("Entity Registry", SCRIPTS_PATH / "run_entity_migration.py"),
        ]
        
        def run_migrations():
            for name, script in migrations:
                if script.exists():
                    log(self.out_log, f"Running {name}...", "info")
                    try:
                        result = subprocess.run(
                            [sys.executable, str(script)],
                            cwd=str(SCRIPTS_PATH),
                            capture_output=True,
                            text=True,
                            timeout=30
                        )
                        if result.returncode == 0:
                            log(self.out_log, f"  ✓ {name}", "success")
                        else:
                            log(self.out_log, f"  ✗ {name}", "error")
                    except Exception as e:
                        log(self.out_log, f"  ✗ {name}: {e}", "error")
                else:
                    log(self.out_log, f"  ⊘ {name}: not found", "warning")
            
            log(self.out_log, "=" * 40, "success")
            log(self.out_log, "FACTORY RESET COMPLETE", "success")
            log(self.out_log, "=" * 40, "success")
        
        threading.Thread(target=run_migrations, daemon=True).start()
    
    def _open_folder(self, path):
        if path.exists():
            if os.name == 'nt':
                os.startfile(str(path))
            else:
                subprocess.run(['xdg-open', str(path)])
        else:
            log(self.out_log, f"Not found: {path}", "error")
    
    # === GITHUB PROJECT METHODS ===
    def _github_sync(self):
        """Run full GitHub Project sync."""
        if not GITHUB_PROJECT_SYNC.exists():
            log(self.out_log, "GitHub sync script not found", "error")
            log(self.out_log, f"Expected: {GITHUB_PROJECT_SYNC}", "dim")
            return
        
        if not os.environ.get("GITHUB_TOKEN"):
            log(self.out_log, "⚠️  GITHUB_TOKEN not set", "warning")
            log(self.out_log, "Set it in System Environment Variables", "info")
            return
        
        log(self.out_log, "Starting GitHub Project sync...", "info")
        run_async(self.out_log, [sys.executable, str(GITHUB_PROJECT_SYNC), "sync"], str(AUTOMATION_PATH))
    
    def _github_sync_dry(self):
        """Run GitHub Project sync in dry-run mode."""
        if not GITHUB_PROJECT_SYNC.exists():
            log(self.out_log, "GitHub sync script not found", "error")
            return
        
        if not os.environ.get("GITHUB_TOKEN"):
            log(self.out_log, "⚠️  GITHUB_TOKEN not set", "warning")
            log(self.out_log, "Set it in System Environment Variables", "info")
            return
        
        log(self.out_log, "Starting dry run...", "info")
        run_async(self.out_log, [sys.executable, str(GITHUB_PROJECT_SYNC), "sync", "--dry-run"], str(AUTOMATION_PATH))
    
    def _github_archive(self):
        """Archive completed items."""
        if not GITHUB_PROJECT_SYNC.exists():
            log(self.out_log, "GitHub sync script not found", "error")
            return
        
        if not os.environ.get("GITHUB_TOKEN"):
            log(self.out_log, "⚠️  GITHUB_TOKEN not set", "warning")
            return
        
        log(self.out_log, "Archiving completed items...", "info")
        run_async(self.out_log, [sys.executable, str(GITHUB_PROJECT_SYNC), "archive"], str(AUTOMATION_PATH))
    
    def _github_open(self):
        """Open The Ehko Project in browser."""
        webbrowser.open("https://github.com/users/brentyJ/projects/2")
        log(self.out_log, "Opened GitHub Project", "info")


# =============================================================================
# RECOG TAB - Standalone ReCog Server
# =============================================================================

class ReCogTab(ttk.Frame):
    """Standalone ReCog server control tab."""
    
    def __init__(self, parent, root):
        super().__init__(parent)
        self.root = root
        self.configure(style="TFrame")
        self._build_ui()
    
    def _build_ui(self):
        container = ttk.Frame(self, padding=10)
        container.pack(fill=BOTH, expand=True)
        
        # === HEADER ===
        header = ttk.Frame(container)
        header.pack(fill=X, pady=(0, 10))
        
        ttk.Label(header, text="RECOG ENGINE", style="H.TLabel").pack(side=LEFT)
        ttk.Label(header, text="v0.6.0 MVP • Standalone Document Intelligence", style="Sub.TLabel").pack(side=LEFT, padx=10)

        # === SERVER CONTROLS ===
        srv_frame = ttk.LabelFrame(container, text="BACKEND (Port 5100)", padding=10)
        srv_frame.pack(fill=X, pady=(0, 10))
        
        btn_row = ttk.Frame(srv_frame)
        btn_row.pack(fill=X)
        
        self.start_btn = ttk.Button(btn_row, text="▶ Start", style="G.TButton", width=12,
                                     command=self._start_recog)
        self.start_btn.pack(side=LEFT, padx=2)
        
        self.stop_btn = ttk.Button(btn_row, text="■ Stop", style="R.TButton", width=10,
                                    state=DISABLED, command=self._stop_recog)
        self.stop_btn.pack(side=LEFT, padx=2)
        
        self.restart_btn = ttk.Button(btn_row, text="↻ Restart", style="Y.TButton", width=10,
                                       state=DISABLED, command=self._restart_recog)
        self.restart_btn.pack(side=LEFT, padx=2)
        
        ttk.Separator(btn_row, orient=VERTICAL).pack(side=LEFT, fill=Y, padx=10)
        
        ttk.Button(btn_row, text="🌐 Open UI", width=10,
                   command=self._open_recog_ui).pack(side=LEFT, padx=2)
        ttk.Button(btn_row, text="Health", width=8,
                   command=self._health_check).pack(side=LEFT, padx=2)
        ttk.Button(btn_row, text="Stats", width=8,
                   command=self._show_stats).pack(side=LEFT, padx=2)
        
        self.status = StatusIndicator(btn_row, "BACKEND OFFLINE")
        self.status.pack(side=RIGHT, padx=10)
        
        # === UI DEV SERVER ===
        ui_frame = ttk.LabelFrame(container, text="UI DEV SERVER (Port 3100)", padding=10)
        ui_frame.pack(fill=X, pady=(0, 10))
        
        ui_btn_row = ttk.Frame(ui_frame)
        ui_btn_row.pack(fill=X)
        
        self.ui_start_btn = ttk.Button(ui_btn_row, text="▶ Start UI", style="G.TButton", width=12,
                                        command=self._start_ui)
        self.ui_start_btn.pack(side=LEFT, padx=2)
        
        self.ui_stop_btn = ttk.Button(ui_btn_row, text="■ Stop", style="R.TButton", width=10,
                                       state=DISABLED, command=self._stop_ui)
        self.ui_stop_btn.pack(side=LEFT, padx=2)
        
        ttk.Separator(ui_btn_row, orient=VERTICAL).pack(side=LEFT, fill=Y, padx=10)
        
        ttk.Button(ui_btn_row, text="🌐 Open UI", style="B.TButton", width=10,
                   command=self._open_recog_ui).pack(side=LEFT, padx=2)
        
        self.ui_status = StatusIndicator(ui_btn_row, "UI OFFLINE")
        self.ui_status.pack(side=RIGHT, padx=10)
        
        # Path info
        path_frame = ttk.Frame(ui_frame)
        path_frame.pack(fill=X, pady=(8, 0))
        ttk.Label(path_frame, text="Backend:", style="Dim.TLabel").pack(side=LEFT)
        ttk.Label(path_frame, text=RECOG_URL, style="Path.TLabel").pack(side=LEFT, padx=5)
        ttk.Label(path_frame, text="UI:", style="Dim.TLabel").pack(side=LEFT, padx=(15, 0))
        ttk.Label(path_frame, text=RECOG_UI_URL, style="Path.TLabel").pack(side=LEFT, padx=5)
        
        # === API ACTIONS ===
        api_frame = ttk.LabelFrame(container, text="API ACTIONS", padding=10)
        api_frame.pack(fill=X, pady=(0, 10))
        
        api_row1 = ttk.Frame(api_frame)
        api_row1.pack(fill=X, pady=(0, 5))
        
        ttk.Button(api_row1, text="Tier 0 Test", width=12,
                   command=self._tier0_test).pack(side=LEFT, padx=2)
        ttk.Button(api_row1, text="List Entities", width=12,
                   command=self._list_entities).pack(side=LEFT, padx=2)
        ttk.Button(api_row1, text="Unknown Entities", width=14,
                   command=self._unknown_entities).pack(side=LEFT, padx=2)
        ttk.Button(api_row1, text="List Insights", width=12,
                   command=self._list_insights).pack(side=LEFT, padx=2)
        
        api_row2 = ttk.Frame(api_frame)
        api_row2.pack(fill=X)
        
        ttk.Button(api_row2, text="Preflight Sessions", width=16,
                   command=self._list_preflights).pack(side=LEFT, padx=2)
        ttk.Button(api_row2, text="Synth Stats", width=12,
                   command=self._synth_stats).pack(side=LEFT, padx=2)
        ttk.Button(api_row2, text="Critique Stats", width=12,
                   command=self._critique_stats).pack(side=LEFT, padx=2)
        ttk.Button(api_row2, text="Queue Status", width=12,
                   command=self._queue_status).pack(side=LEFT, padx=2)
        
        # === GIT CONTROLS ===
        git_frame = ttk.LabelFrame(container, text="GIT", padding=10)
        git_frame.pack(fill=X, pady=(0, 10))
        
        git_row = ttk.Frame(git_frame)
        git_row.pack(fill=X)
        
        ttk.Button(git_row, text="Git Status", width=12,
                   command=self._git_status).pack(side=LEFT, padx=2)
        ttk.Button(git_row, text="Git Push", style="G.TButton", width=12,
                   command=self._git_push).pack(side=LEFT, padx=2)
        ttk.Button(git_row, text="Git Pull", style="B.TButton", width=12,
                   command=self._git_pull).pack(side=LEFT, padx=2)
        
        ttk.Separator(git_row, orient=VERTICAL).pack(side=LEFT, fill=Y, padx=10)
        
        ttk.Button(git_row, text="📁 Open Folder", width=14,
                   command=self._open_folder).pack(side=LEFT, padx=2)
        ttk.Button(git_row, text="📁 Test Corpus", width=14,
                   command=self._open_test_corpus).pack(side=LEFT, padx=2)
        
        # === SERVER LOG ===
        log_frame = ttk.LabelFrame(container, text="SERVER LOG", padding=10)
        log_frame.pack(fill=BOTH, expand=True)
        
        self.recog_log = TerminalLog(log_frame, height=18)
        self.recog_log.pack(fill=BOTH, expand=True)
        
        log_btns = ttk.Frame(log_frame)
        log_btns.pack(fill=X, pady=(8, 0))
        
        ttk.Button(log_btns, text="Clear", width=8,
                   command=self.recog_log.clear).pack(side=RIGHT, padx=2)
        ttk.Button(log_btns, text="Copy", width=8,
                   command=lambda: self.recog_log.copy_contents(self.root)).pack(side=RIGHT, padx=2)
        
        # Initial message
        log(self.recog_log, "ReCog v0.6.0 • Standalone Mode", "recog")
        log(self.recog_log, "1. Start Backend (Flask API on 5100)", "dim")
        log(self.recog_log, "2. Start UI (Vite dev server on 3100)", "dim")
        log(self.recog_log, "3. Click 'Open UI' to access the React interface", "dim")
    
    # === SERVER METHODS ===
    def _start_recog(self):
        global recog_process
        if recog_process and recog_process.poll() is None:
            log(self.recog_log, "Backend already running", "warning")
            return
        
        if not RECOG_SERVER_SCRIPT.exists():
            log(self.recog_log, f"Server script not found: {RECOG_SERVER_SCRIPT}", "error")
            return
        
        try:
            recog_process = subprocess.Popen(
                [sys.executable, str(RECOG_SERVER_SCRIPT)],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                cwd=str(RECOG_SCRIPTS),
                text=True,
                bufsize=1,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
            )
            self.status.set_online("BACKEND ONLINE")
            self.start_btn.config(state=DISABLED)
            self.stop_btn.config(state=NORMAL)
            self.restart_btn.config(state=NORMAL)
            log(self.recog_log, f"Backend started (PID {recog_process.pid})", "success")
            
            def stream():
                for line in iter(recog_process.stdout.readline, ''):
                    if line and recog_process.poll() is None:
                        line = line.strip()
                        if "ERROR" in line or "error" in line.lower():
                            log(self.recog_log, line, "error")
                        elif "WARNING" in line or "warn" in line.lower():
                            log(self.recog_log, line, "warning")
                        elif "Running on" in line or "started" in line.lower():
                            log(self.recog_log, line, "success")
                        else:
                            log(self.recog_log, line, "recog")
                self.status.set_offline("BACKEND OFFLINE")
                self.start_btn.config(state=NORMAL)
                self.stop_btn.config(state=DISABLED)
                self.restart_btn.config(state=DISABLED)
                log(self.recog_log, "Backend stopped", "warning")
            
            threading.Thread(target=stream, daemon=True).start()
        except Exception as e:
            log(self.recog_log, f"Failed to start: {e}", "error")
    
    def _stop_recog(self):
        global recog_process
        if not recog_process or recog_process.poll() is not None:
            self.status.set_offline("BACKEND OFFLINE")
            self.start_btn.config(state=NORMAL)
            self.stop_btn.config(state=DISABLED)
            self.restart_btn.config(state=DISABLED)
            return
        
        try:
            log(self.recog_log, "Stopping backend...", "warning")
            if os.name == 'nt':
                recog_process.send_signal(signal.CTRL_BREAK_EVENT)
            else:
                recog_process.terminate()
            recog_process.wait(timeout=5)
            log(self.recog_log, "Backend stopped gracefully", "success")
        except:
            recog_process.kill()
            log(self.recog_log, "Backend killed", "warning")
        finally:
            recog_process = None
            self.status.set_offline("BACKEND OFFLINE")
            self.start_btn.config(state=NORMAL)
            self.stop_btn.config(state=DISABLED)
            self.restart_btn.config(state=DISABLED)
    
    def _restart_recog(self):
        def restart():
            log(self.recog_log, "Restarting backend...", "warning")
            self._stop_recog()
            import time
            time.sleep(1)
            self._start_recog()
        threading.Thread(target=restart, daemon=True).start()
    
    # === UI DEV SERVER ===
    def _kill_port_3100(self):
        """Kill any process using port 3100 (orphaned node processes)."""
        if os.name != 'nt':
            return
        try:
            # Find PID using port 3100
            result = subprocess.run(
                ['powershell', '-Command',
                 'Get-NetTCPConnection -LocalPort 3100 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess'],
                capture_output=True, text=True, timeout=5
            )
            pids = set(result.stdout.strip().split('\n'))
            pids.discard('')
            pids.discard('0')  # Filter out invalid PIDs
            for pid in pids:
                if pid.isdigit() and int(pid) > 0:
                    try:
                        subprocess.run(['taskkill', '/F', '/PID', pid], capture_output=True, timeout=5)
                        log(self.recog_log, f"Killed orphaned process on port 3100 (PID {pid})", "warning")
                    except:
                        pass
        except:
            pass  # Silently ignore errors - port might just be free

    def _start_ui(self):
        global recog_ui_process
        if recog_ui_process and recog_ui_process.poll() is None:
            log(self.recog_log, "UI already running", "warning")
            return

        if not RECOG_UI_PATH.exists():
            log(self.recog_log, f"UI path not found: {RECOG_UI_PATH}", "error")
            return

        # Clean up any orphaned processes on port 3100
        self._kill_port_3100()

        try:
            cmd = ['cmd', '/c', 'npm', 'run', 'dev'] if os.name == 'nt' else ['npm', 'run', 'dev']
            recog_ui_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                cwd=str(RECOG_UI_PATH),
                text=True,
                bufsize=1,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
            )
            self.ui_status.set_online("UI ONLINE")
            self.ui_start_btn.config(state=DISABLED)
            self.ui_stop_btn.config(state=NORMAL)
            log(self.recog_log, f"UI dev server started (PID {recog_ui_process.pid})", "success")
            
            def stream():
                for line in iter(recog_ui_process.stdout.readline, ''):
                    if line and recog_ui_process.poll() is None:
                        line = line.strip()
                        if "error" in line.lower():
                            log(self.recog_log, line, "error")
                        elif "Local:" in line or "ready" in line.lower():
                            log(self.recog_log, line, "success")
                        elif "warn" in line.lower():
                            log(self.recog_log, line, "warning")
                        else:
                            log(self.recog_log, line, "info")
                self.ui_status.set_offline("UI OFFLINE")
                self.ui_start_btn.config(state=NORMAL)
                self.ui_stop_btn.config(state=DISABLED)
                log(self.recog_log, "UI dev server stopped", "warning")
            
            threading.Thread(target=stream, daemon=True).start()
        except FileNotFoundError:
            log(self.recog_log, "npm not found - install Node.js", "error")
        except Exception as e:
            log(self.recog_log, f"UI start failed: {e}", "error")
    
    def _stop_ui(self):
        global recog_ui_process
        if not recog_ui_process or recog_ui_process.poll() is not None:
            # Even if our tracked process is gone, clean up any orphaned processes
            self._kill_port_3100()
            self.ui_status.set_offline("UI OFFLINE")
            self.ui_start_btn.config(state=NORMAL)
            self.ui_stop_btn.config(state=DISABLED)
            return

        try:
            log(self.recog_log, "Stopping UI...", "warning")
            if os.name == 'nt':
                # Kill the process tree (cmd -> npm -> node)
                subprocess.run(
                    ['taskkill', '/F', '/T', '/PID', str(recog_ui_process.pid)],
                    capture_output=True, timeout=5
                )
            else:
                recog_ui_process.terminate()
            recog_ui_process.wait(timeout=5)
            log(self.recog_log, "UI stopped", "success")
        except:
            try:
                recog_ui_process.kill()
            except:
                pass
            log(self.recog_log, "UI killed", "warning")
        finally:
            # Clean up any remaining processes on port 3100
            self._kill_port_3100()
            recog_ui_process = None
            self.ui_status.set_offline("UI OFFLINE")
            self.ui_start_btn.config(state=NORMAL)
            self.ui_stop_btn.config(state=DISABLED)
    
    def _open_recog_ui(self):
        global recog_ui_process
        if recog_ui_process and recog_ui_process.poll() is None:
            webbrowser.open(RECOG_UI_URL)
            log(self.recog_log, f"Opened {RECOG_UI_URL}", "info")
        else:
            webbrowser.open(RECOG_URL)
            log(self.recog_log, f"UI not running - opened {RECOG_URL} (start UI for full features)", "warning")
    
    def _health_check(self):
        log(self.recog_log, "Checking health...", "info")
        r = api("/api/health", base_url=RECOG_URL)
        if "error" in r:
            log(self.recog_log, f"Error: {r['error']}", "error")
        else:
            data = r.get("data", r)
            log(self.recog_log, f"Status: {data.get('status', 'unknown')}", "success")
            db = data.get('database', {})
            log(self.recog_log, f"Database: {db.get('tables', 0)} tables, {db.get('rows', 0)} rows", "info")
            log(self.recog_log, f"LLM Configured: {data.get('llm_configured', False)}", "info")
            providers = data.get('available_providers', [])
            if providers:
                log(self.recog_log, f"Providers: {', '.join(providers)}", "info")
    
    def _show_stats(self):
        log(self.recog_log, "─" * 40, "dim")
        
        # Entity stats
        r = api("/api/entities/stats", base_url=RECOG_URL)
        if "error" not in r:
            data = r.get("data", r)
            log(self.recog_log, f"Entities: {data.get('total', 0)} total, {data.get('confirmed', 0)} confirmed", "info")
        
        # Insight stats
        r = api("/api/insights/stats", base_url=RECOG_URL)
        if "error" not in r:
            data = r.get("data", r)
            log(self.recog_log, f"Insights: {data.get('total', 0)} total", "info")
        
        # Synth stats
        r = api("/api/synth/stats", base_url=RECOG_URL)
        if "error" not in r:
            data = r.get("data", r)
            log(self.recog_log, f"Patterns: {data.get('total_patterns', 0)}", "info")
            log(self.recog_log, f"Clusters: {data.get('total_clusters', 0)}", "info")
        
        log(self.recog_log, "─" * 40, "dim")
    
    # === API ACTIONS ===
    def _tier0_test(self):
        log(self.recog_log, "Running Tier 0 test...", "recog")
        test_text = "Had a great meeting with Sarah on Monday. She mentioned the Q3 budget is around $50,000. Contact her at sarah@example.com or 0412-555-789."
        r = api("/api/tier0", "POST", {"text": test_text}, base_url=RECOG_URL)
        if "error" in r:
            log(self.recog_log, f"Error: {r['error']}", "error")
        else:
            data = r.get("data", r)
            log(self.recog_log, f"Emotions: {data.get('emotions', {})}", "info")
            log(self.recog_log, f"Entities: {len(data.get('entities', []))} found", "info")
            for ent in data.get('entities', [])[:5]:
                log(self.recog_log, f"  • {ent.get('type')}: {ent.get('value')}", "recog")
    
    def _list_entities(self):
        log(self.recog_log, "Fetching entities...", "info")
        r = api("/api/entities?limit=10", base_url=RECOG_URL)
        if "error" in r:
            log(self.recog_log, f"Error: {r['error']}", "error")
        else:
            entities = r.get("data", {}).get("entities", r.get("entities", []))
            log(self.recog_log, f"Found {len(entities)} entities:", "success")
            for ent in entities[:10]:
                name = ent.get('display_name') or ent.get('normalised_value', '?')
                etype = ent.get('entity_type', '?')
                log(self.recog_log, f"  [{etype}] {name}", "info")
    
    def _unknown_entities(self):
        log(self.recog_log, "Fetching unknown entities...", "info")
        r = api("/api/entities/unknown", base_url=RECOG_URL)
        if "error" in r:
            log(self.recog_log, f"Error: {r['error']}", "error")
        else:
            entities = r.get("data", {}).get("entities", r.get("entities", []))
            if entities:
                log(self.recog_log, f"Found {len(entities)} unknown entities:", "warning")
                for ent in entities[:10]:
                    val = ent.get('normalised_value', '?')
                    etype = ent.get('entity_type', '?')
                    log(self.recog_log, f"  [{etype}] {val}", "warning")
            else:
                log(self.recog_log, "No unknown entities", "success")
    
    def _list_insights(self):
        log(self.recog_log, "Fetching insights...", "info")
        r = api("/api/insights?limit=10", base_url=RECOG_URL)
        if "error" in r:
            log(self.recog_log, f"Error: {r['error']}", "error")
        else:
            insights = r.get("data", {}).get("insights", r.get("insights", []))
            log(self.recog_log, f"Found {len(insights)} insights:", "success")
            for ins in insights[:10]:
                content = ins.get('content', '?')[:60]
                sig = ins.get('significance', 0)
                log(self.recog_log, f"  [{sig}★] {content}...", "info")
    
    def _list_preflights(self):
        log(self.recog_log, "Fetching preflight sessions...", "info")
        r = api("/api/preflight", base_url=RECOG_URL)
        if "error" in r:
            log(self.recog_log, f"Error: {r['error']}", "error")
        else:
            sessions = r.get("data", {}).get("sessions", r.get("sessions", []))
            if sessions:
                log(self.recog_log, f"Found {len(sessions)} sessions:", "success")
                for sess in sessions[:10]:
                    sid = sess.get('id', '?')
                    status = sess.get('status', '?')
                    items = sess.get('item_count', 0)
                    log(self.recog_log, f"  [{status}] Session {sid}: {items} items", "info")
            else:
                log(self.recog_log, "No preflight sessions", "info")
    
    def _synth_stats(self):
        log(self.recog_log, "Fetching synth stats...", "info")
        r = api("/api/synth/stats", base_url=RECOG_URL)
        if "error" in r:
            log(self.recog_log, f"Error: {r['error']}", "error")
        else:
            data = r.get("data", r)
            log(self.recog_log, f"Total Patterns: {data.get('total_patterns', 0)}", "info")
            log(self.recog_log, f"Active Patterns: {data.get('active_patterns', 0)}", "info")
            log(self.recog_log, f"Total Clusters: {data.get('total_clusters', 0)}", "info")
            log(self.recog_log, f"Pending Clusters: {data.get('pending_clusters', 0)}", "info")
    
    def _critique_stats(self):
        log(self.recog_log, "Fetching critique stats...", "info")
        r = api("/api/critique/stats", base_url=RECOG_URL)
        if "error" in r:
            log(self.recog_log, f"Error: {r['error']}", "error")
        else:
            data = r.get("data", r)
            log(self.recog_log, f"Total Critiques: {data.get('total', 0)}", "info")
            log(self.recog_log, f"Passed: {data.get('passed', 0)}", "success")
            log(self.recog_log, f"Failed: {data.get('failed', 0)}", "error")
            log(self.recog_log, f"Strictness: {data.get('strictness', 'unknown')}", "info")
    
    def _queue_status(self):
        log(self.recog_log, "Fetching queue status...", "info")
        r = api("/api/queue/stats", base_url=RECOG_URL)
        if "error" in r:
            log(self.recog_log, f"Error: {r['error']}", "error")
        else:
            data = r.get("data", r)
            log(self.recog_log, f"Pending: {data.get('pending', 0)}", "info")
            log(self.recog_log, f"Processing: {data.get('processing', 0)}", "warning")
            log(self.recog_log, f"Complete: {data.get('complete', 0)}", "success")
            log(self.recog_log, f"Failed: {data.get('failed', 0)}", "error")
    
    # === GIT METHODS ===
    def _git_status(self):
        log(self.recog_log, "Checking git status...", "info")
        run_async(self.recog_log, ["git", "status", "--short"], str(RECOG_ROOT))
    
    def _git_push(self):
        log(self.recog_log, "Running git push...", "info")
        # Use automation script if available
        git_script = AUTOMATION_PATH / "git_recog.py"
        if git_script.exists():
            run_async(self.recog_log, [sys.executable, str(git_script)], str(AUTOMATION_PATH))
        else:
            # Fallback to direct git commands
            def git_push():
                try:
                    # Add all
                    result = subprocess.run(["git", "add", "-A"], cwd=str(RECOG_ROOT), capture_output=True, text=True)
                    log(self.recog_log, "Staged changes", "info")
                    
                    # Commit
                    msg = f"Update: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                    result = subprocess.run(["git", "commit", "-m", msg], cwd=str(RECOG_ROOT), capture_output=True, text=True)
                    if "nothing to commit" in result.stdout or "nothing to commit" in result.stderr:
                        log(self.recog_log, "Nothing to commit", "info")
                        return
                    log(self.recog_log, f"Committed: {msg}", "success")
                    
                    # Push
                    result = subprocess.run(["git", "push", "origin", "main"], cwd=str(RECOG_ROOT), capture_output=True, text=True)
                    if result.returncode == 0:
                        log(self.recog_log, "Pushed to origin/main", "success")
                    else:
                        log(self.recog_log, f"Push failed: {result.stderr}", "error")
                except Exception as e:
                    log(self.recog_log, f"Error: {e}", "error")
            
            threading.Thread(target=git_push, daemon=True).start()
    
    def _git_pull(self):
        log(self.recog_log, "Running git pull...", "info")
        run_async(self.recog_log, ["git", "pull", "origin", "main"], str(RECOG_ROOT))
    
    def _open_folder(self):
        if RECOG_ROOT.exists():
            if os.name == 'nt':
                os.startfile(str(RECOG_ROOT))
            else:
                subprocess.run(['xdg-open', str(RECOG_ROOT)])
        else:
            log(self.recog_log, f"Not found: {RECOG_ROOT}", "error")
    
    def _open_test_corpus(self):
        test_path = RECOG_SCRIPTS / "_data" / "test_corpus"
        if test_path.exists():
            if os.name == 'nt':
                os.startfile(str(test_path))
            else:
                subprocess.run(['xdg-open', str(test_path)])
            log(self.recog_log, "Opened test corpus folder", "info")
        else:
            log(self.recog_log, f"Test corpus not found: {test_path}", "error")


# =============================================================================
# WEBSITE TAB - Astro Dev Server
# =============================================================================

class WebsiteTab(ttk.Frame):
    """Website development server control tab."""
    
    def __init__(self, parent, root):
        super().__init__(parent)
        self.root = root
        self.configure(style="TFrame")
        self._build_ui()
    
    def _build_ui(self):
        container = ttk.Frame(self, padding=10)
        container.pack(fill=BOTH, expand=True)
        
        # === HEADER ===
        header = ttk.Frame(container)
        header.pack(fill=X, pady=(0, 10))
        
        ttk.Label(header, text="EHKOLABS WEBSITE", style="H.TLabel").pack(side=LEFT)
        
        self.status = StatusIndicator(header, "WEBSITE OFFLINE")
        self.status.pack(side=RIGHT)
        
        # === CONTROLS ===
        ctrl_frame = ttk.LabelFrame(container, text="DEV SERVER (Astro)", padding=10)
        ctrl_frame.pack(fill=X, pady=(0, 10))
        
        btn_row = ttk.Frame(ctrl_frame)
        btn_row.pack(fill=X)
        
        self.start_btn = ttk.Button(btn_row, text="▶ Start Dev Server", style="G.TButton", width=18,
                                     command=self._start_website)
        self.start_btn.pack(side=LEFT, padx=2)
        
        self.stop_btn = ttk.Button(btn_row, text="■ Stop", style="R.TButton", width=10,
                                    state=DISABLED, command=self._stop_website)
        self.stop_btn.pack(side=LEFT, padx=2)
        
        ttk.Separator(btn_row, orient=VERTICAL).pack(side=LEFT, fill=Y, padx=10)
        
        ttk.Button(btn_row, text="🌐 Open Site", width=12,
                   command=self._open_website).pack(side=LEFT, padx=2)
        ttk.Button(btn_row, text="📁 Open Folder", width=14,
                   command=self._open_folder).pack(side=LEFT, padx=2)
        
        # Path display
        path_frame = ttk.Frame(ctrl_frame)
        path_frame.pack(fill=X, pady=(10, 0))
        ttk.Label(path_frame, text="Path:", style="Dim.TLabel").pack(side=LEFT)
        ttk.Label(path_frame, text=str(WEBSITE_PATH), style="Path.TLabel").pack(side=LEFT, padx=5)
        
        # === GIT CONTROLS ===
        git_frame = ttk.LabelFrame(container, text="GIT", padding=10)
        git_frame.pack(fill=X, pady=(0, 10))
        
        git_row = ttk.Frame(git_frame)
        git_row.pack(fill=X)
        
        ttk.Button(git_row, text="Git Status", width=12,
                   command=self._git_status).pack(side=LEFT, padx=2)
        ttk.Button(git_row, text="Git Push", style="G.TButton", width=12,
                   command=self._git_push).pack(side=LEFT, padx=2)
        ttk.Button(git_row, text="Git Pull", style="B.TButton", width=12,
                   command=self._git_pull).pack(side=LEFT, padx=2)
        ttk.Button(git_row, text="Build", style="Y.TButton", width=10,
                   command=self._build_website).pack(side=LEFT, padx=2)
        
        # === LOG ===
        log_frame = ttk.LabelFrame(container, text="DEV SERVER LOG", padding=10)
        log_frame.pack(fill=BOTH, expand=True)
        
        self.web_log = TerminalLog(log_frame, height=20)
        self.web_log.pack(fill=BOTH, expand=True)
        
        log_btns = ttk.Frame(log_frame)
        log_btns.pack(fill=X, pady=(8, 0))
        
        ttk.Button(log_btns, text="Clear", width=8,
                   command=self.web_log.clear).pack(side=RIGHT, padx=2)
        ttk.Button(log_btns, text="Copy", width=8,
                   command=lambda: self.web_log.copy_contents(self.root)).pack(side=RIGHT, padx=2)
        
        # Initial message
        log(self.web_log, f"Website path: {WEBSITE_PATH}", "info")
        log(self.web_log, f"Dev URL: {WEBSITE_URL}", "info")
        log(self.web_log, "Start dev server to test locally.", "dim")
    
    def _start_website(self):
        global website_process
        if website_process and website_process.poll() is None:
            log(self.web_log, "Already running", "warning")
            return
        
        if not WEBSITE_PATH.exists():
            log(self.web_log, f"Path not found: {WEBSITE_PATH}", "error")
            return
        
        try:
            cmd = ['cmd', '/c', 'npm', 'run', 'dev'] if os.name == 'nt' else ['npm', 'run', 'dev']
            website_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                cwd=str(WEBSITE_PATH),
                text=True,
                bufsize=1,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
            )
            self.status.set_online("WEBSITE ONLINE")
            self.start_btn.config(state=DISABLED)
            self.stop_btn.config(state=NORMAL)
            log(self.web_log, f"Started (PID {website_process.pid})", "success")
            
            def stream():
                for line in iter(website_process.stdout.readline, ''):
                    if line and website_process.poll() is None:
                        line = line.strip()
                        if "error" in line.lower():
                            log(self.web_log, line, "error")
                        elif "ready" in line or "Local" in line or "started" in line:
                            log(self.web_log, line, "success")
                        elif "warn" in line.lower():
                            log(self.web_log, line, "warning")
                        else:
                            log(self.web_log, line, "website")
                self.status.set_offline("WEBSITE OFFLINE")
                self.start_btn.config(state=NORMAL)
                self.stop_btn.config(state=DISABLED)
                log(self.web_log, "Stopped", "warning")
            
            threading.Thread(target=stream, daemon=True).start()
        except FileNotFoundError:
            log(self.web_log, "npm not found. Install Node.js.", "error")
        except Exception as e:
            log(self.web_log, f"Failed: {e}", "error")
    
    def _stop_website(self):
        global website_process
        if not website_process or website_process.poll() is not None:
            self.status.set_offline("WEBSITE OFFLINE")
            self.start_btn.config(state=NORMAL)
            self.stop_btn.config(state=DISABLED)
            return
        
        try:
            log(self.web_log, "Stopping...", "warning")
            if os.name == 'nt':
                website_process.send_signal(signal.CTRL_BREAK_EVENT)
            else:
                website_process.terminate()
            website_process.wait(timeout=5)
            log(self.web_log, "Stopped gracefully", "success")
        except:
            website_process.kill()
            log(self.web_log, "Killed", "warning")
        finally:
            website_process = None
            self.status.set_offline("WEBSITE OFFLINE")
            self.start_btn.config(state=NORMAL)
            self.stop_btn.config(state=DISABLED)
    
    def _open_website(self):
        webbrowser.open(WEBSITE_URL)
        log(self.web_log, "Opened in browser", "info")
    
    def _open_folder(self):
        if WEBSITE_PATH.exists():
            if os.name == 'nt':
                os.startfile(str(WEBSITE_PATH))
            else:
                subprocess.run(['xdg-open', str(WEBSITE_PATH)])
        else:
            log(self.web_log, f"Not found: {WEBSITE_PATH}", "error")
    
    # === GIT METHODS ===
    def _git_status(self):
        log(self.web_log, "Checking git status...", "info")
        run_async(self.web_log, ["git", "status", "--short"], str(WEBSITE_PATH))
    
    def _git_push(self):
        log(self.web_log, "Running git push...", "info")
        # Use automation script if available
        git_script = AUTOMATION_PATH / "git_website.py"
        if git_script.exists():
            run_async(self.web_log, [sys.executable, str(git_script)], str(AUTOMATION_PATH))
        else:
            def git_push():
                try:
                    subprocess.run(["git", "add", "-A"], cwd=str(WEBSITE_PATH), capture_output=True)
                    log(self.web_log, "Staged changes", "info")
                    
                    msg = f"Website update: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                    result = subprocess.run(["git", "commit", "-m", msg], cwd=str(WEBSITE_PATH), capture_output=True, text=True)
                    if "nothing to commit" in result.stdout + result.stderr:
                        log(self.web_log, "Nothing to commit", "info")
                        return
                    log(self.web_log, f"Committed: {msg}", "success")
                    
                    result = subprocess.run(["git", "push", "origin", "main"], cwd=str(WEBSITE_PATH), capture_output=True, text=True)
                    if result.returncode == 0:
                        log(self.web_log, "Pushed to origin/main", "success")
                    else:
                        # Try master
                        result = subprocess.run(["git", "push", "origin", "master"], cwd=str(WEBSITE_PATH), capture_output=True, text=True)
                        if result.returncode == 0:
                            log(self.web_log, "Pushed to origin/master", "success")
                        else:
                            log(self.web_log, f"Push failed: {result.stderr}", "error")
                except Exception as e:
                    log(self.web_log, f"Error: {e}", "error")
            
            threading.Thread(target=git_push, daemon=True).start()
    
    def _git_pull(self):
        log(self.web_log, "Running git pull...", "info")
        run_async(self.web_log, ["git", "pull"], str(WEBSITE_PATH))
    
    def _build_website(self):
        log(self.web_log, "Building website...", "info")
        cmd = ['cmd', '/c', 'npm', 'run', 'build'] if os.name == 'nt' else ['npm', 'run', 'build']
        run_async(self.web_log, cmd, str(WEBSITE_PATH))


# =============================================================================
# WEB PANEL TAB - Browser-based Control Panel
# =============================================================================

class WebPanelTab(ttk.Frame):
    """Web-based Control Panel launcher and manager."""
    
    def __init__(self, parent, root):
        super().__init__(parent)
        self.root = root
        self.configure(style="TFrame")
        self.backend_process = None
        self.frontend_process = None
        self._build_ui()
    
    def _build_ui(self):
        container = ttk.Frame(self, padding=10)
        container.pack(fill=BOTH, expand=True)
        
        # === HEADER ===
        header = ttk.Frame(container)
        header.pack(fill=X, pady=(0, 10))
        
        ttk.Label(header, text="WEB CONTROL PANEL", style="H.TLabel").pack(side=LEFT)
        ttk.Label(header, text="Browser-based interface with shadcn/ui", style="Sub.TLabel").pack(side=LEFT, padx=10)
        
        # === BACKEND SERVER ===
        backend_frame = ttk.LabelFrame(container, text="BACKEND SERVER (Port 5001)", padding=10)
        backend_frame.pack(fill=X, pady=(0, 10))
        
        btn_row1 = ttk.Frame(backend_frame)
        btn_row1.pack(fill=X)
        
        self.backend_start = ttk.Button(btn_row1, text="▶ Start Backend", style="G.TButton", width=14,
                                        command=self._start_backend)
        self.backend_start.pack(side=LEFT, padx=2)
        
        self.backend_stop = ttk.Button(btn_row1, text="■ Stop", style="R.TButton", width=10,
                                       state=DISABLED, command=self._stop_backend)
        self.backend_stop.pack(side=LEFT, padx=2)
        
        self.backend_status = StatusIndicator(btn_row1, "BACKEND OFFLINE")
        self.backend_status.pack(side=RIGHT, padx=10)
        
        path_row1 = ttk.Frame(backend_frame)
        path_row1.pack(fill=X, pady=(8, 0))
        ttk.Label(path_row1, text="Path:", style="Dim.TLabel").pack(side=LEFT)
        ttk.Label(path_row1, text="C:\\EhkoDev\\ehko-control\\server.py", style="Path.TLabel").pack(side=LEFT, padx=5)
        
        # === FRONTEND DEV SERVER ===
        frontend_frame = ttk.LabelFrame(container, text="FRONTEND DEV SERVER (Port 3000)", padding=10)
        frontend_frame.pack(fill=X, pady=(0, 10))
        
        btn_row2 = ttk.Frame(frontend_frame)
        btn_row2.pack(fill=X)
        
        self.frontend_start = ttk.Button(btn_row2, text="▶ Start Frontend", style="G.TButton", width=14,
                                         command=self._start_frontend)
        self.frontend_start.pack(side=LEFT, padx=2)
        
        self.frontend_stop = ttk.Button(btn_row2, text="■ Stop", style="R.TButton", width=10,
                                        state=DISABLED, command=self._stop_frontend)
        self.frontend_stop.pack(side=LEFT, padx=2)
        
        ttk.Separator(btn_row2, orient=VERTICAL).pack(side=LEFT, fill=Y, padx=10)
        
        ttk.Button(btn_row2, text="🌐 Open Browser", style="B.TButton", width=14,
                   command=self._open_browser).pack(side=LEFT, padx=2)
        
        self.frontend_status = StatusIndicator(btn_row2, "FRONTEND OFFLINE")
        self.frontend_status.pack(side=RIGHT, padx=10)
        
        path_row2 = ttk.Frame(frontend_frame)
        path_row2.pack(fill=X, pady=(8, 0))
        ttk.Label(path_row2, text="Path:", style="Dim.TLabel").pack(side=LEFT)
        ttk.Label(path_row2, text="C:\\EhkoDev\\ehko-control", style="Path.TLabel").pack(side=LEFT, padx=5)
        ttk.Label(path_row2, text="URL:", style="Dim.TLabel").pack(side=LEFT, padx=(15, 0))
        ttk.Label(path_row2, text="http://localhost:3000", style="Path.TLabel").pack(side=LEFT, padx=5)
        
        # === QUICK ACTIONS ===
        action_frame = ttk.LabelFrame(container, text="QUICK ACTIONS", padding=10)
        action_frame.pack(fill=X, pady=(0, 10))
        
        action_row = ttk.Frame(action_frame)
        action_row.pack(fill=X)
        
        ttk.Button(action_row, text="⚡ Start Both", style="Accent.TButton", width=12,
                   command=self._start_both).pack(side=LEFT, padx=2)
        ttk.Button(action_row, text="□ Stop Both", style="R.TButton", width=12,
                   command=self._stop_both).pack(side=LEFT, padx=2)
        ttk.Button(action_row, text="📁 Open Folder", width=12,
                   command=self._open_folder).pack(side=LEFT, padx=2)
        
        # === INFO ===
        info_frame = ttk.LabelFrame(container, text="ABOUT", padding=10)
        info_frame.pack(fill=X, pady=(0, 10))
        
        info_text = """This web-based control panel demonstrates the shadcn/ui design system with the EhkoForge terminal theme.

Features:
• Server management (start/stop EhkoForge, ReCog, Website)
• Real-time status monitoring
• Quick actions (vault refresh, git operations)
• Responsive web interface
• Accessible from any device on your network

The backend (Flask) manages server processes. The frontend (React + Vite) provides the UI.
Both must be running to access the web panel."""
        
        info_label = ttk.Label(info_frame, text=info_text, style="Dim.TLabel", justify=LEFT)
        info_label.pack(fill=X)
        
        # === LOG ===
        log_frame = ttk.LabelFrame(container, text="LOG", padding=10)
        log_frame.pack(fill=BOTH, expand=True)
        
        self.web_panel_log = TerminalLog(log_frame, height=12)
        self.web_panel_log.pack(fill=BOTH, expand=True)
        
        log_btns = ttk.Frame(log_frame)
        log_btns.pack(fill=X, pady=(8, 0))
        
        ttk.Button(log_btns, text="Clear", width=8,
                   command=self.web_panel_log.clear).pack(side=RIGHT, padx=2)
        ttk.Button(log_btns, text="Copy", width=8,
                   command=lambda: self.web_panel_log.copy_contents(self.root)).pack(side=RIGHT, padx=2)
        
        # Initial message
        log(self.web_panel_log, "Web Control Panel launcher ready.", "info")
        log(self.web_panel_log, "Start backend first, then frontend.", "dim")
    
    # === BACKEND METHODS ===
    def _start_backend(self):
        if self.backend_process and self.backend_process.poll() is None:
            log(self.web_panel_log, "Backend already running", "warning")
            return
        
        backend_path = Path("C:/EhkoDev/ehko-control/server.py")
        if not backend_path.exists():
            log(self.web_panel_log, f"Backend not found: {backend_path}", "error")
            return
        
        try:
            self.backend_process = subprocess.Popen(
                [sys.executable, str(backend_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                cwd="C:/EhkoDev/ehko-control",
                text=True,
                bufsize=1,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
            )
            self.backend_status.set_online("BACKEND ONLINE")
            self.backend_start.config(state=DISABLED)
            self.backend_stop.config(state=NORMAL)
            log(self.web_panel_log, f"Backend started (PID {self.backend_process.pid})", "success")
            
            def stream():
                for line in iter(self.backend_process.stdout.readline, ''):
                    if line and self.backend_process.poll() is None:
                        line = line.strip()
                        if "error" in line.lower():
                            log(self.web_panel_log, line, "error")
                        elif "Running on" in line or "started" in line.lower():
                            log(self.web_panel_log, line, "success")
                        else:
                            log(self.web_panel_log, line, "info")
                self.backend_status.set_offline("BACKEND OFFLINE")
                self.backend_start.config(state=NORMAL)
                self.backend_stop.config(state=DISABLED)
                log(self.web_panel_log, "Backend stopped", "warning")
            
            threading.Thread(target=stream, daemon=True).start()
        except Exception as e:
            log(self.web_panel_log, f"Backend failed: {e}", "error")
    
    def _stop_backend(self):
        if not self.backend_process or self.backend_process.poll() is not None:
            self.backend_status.set_offline("BACKEND OFFLINE")
            self.backend_start.config(state=NORMAL)
            self.backend_stop.config(state=DISABLED)
            return
        
        try:
            log(self.web_panel_log, "Stopping backend...", "warning")
            if os.name == 'nt':
                self.backend_process.send_signal(signal.CTRL_BREAK_EVENT)
            else:
                self.backend_process.terminate()
            self.backend_process.wait(timeout=5)
            log(self.web_panel_log, "Backend stopped", "success")
        except:
            self.backend_process.kill()
            log(self.web_panel_log, "Backend killed", "warning")
        finally:
            self.backend_process = None
            self.backend_status.set_offline("BACKEND OFFLINE")
            self.backend_start.config(state=NORMAL)
            self.backend_stop.config(state=DISABLED)
    
    # === FRONTEND METHODS ===
    def _start_frontend(self):
        if self.frontend_process and self.frontend_process.poll() is None:
            log(self.web_panel_log, "Frontend already running", "warning")
            return
        
        frontend_path = Path("C:/EhkoDev/ehko-control")
        if not frontend_path.exists():
            log(self.web_panel_log, f"Frontend path not found: {frontend_path}", "error")
            return
        
        try:
            cmd = ['cmd', '/c', 'npm', 'run', 'dev'] if os.name == 'nt' else ['npm', 'run', 'dev']
            self.frontend_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                cwd=str(frontend_path),
                text=True,
                bufsize=1,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
            )
            self.frontend_status.set_online("FRONTEND ONLINE")
            self.frontend_start.config(state=DISABLED)
            self.frontend_stop.config(state=NORMAL)
            log(self.web_panel_log, f"Frontend started (PID {self.frontend_process.pid})", "success")
            
            def stream():
                for line in iter(self.frontend_process.stdout.readline, ''):
                    if line and self.frontend_process.poll() is None:
                        line = line.strip()
                        if "error" in line.lower():
                            log(self.web_panel_log, line, "error")
                        elif "Local:" in line or "ready" in line.lower():
                            log(self.web_panel_log, line, "success")
                        else:
                            log(self.web_panel_log, line, "info")
                self.frontend_status.set_offline("FRONTEND OFFLINE")
                self.frontend_start.config(state=NORMAL)
                self.frontend_stop.config(state=DISABLED)
                log(self.web_panel_log, "Frontend stopped", "warning")
            
            threading.Thread(target=stream, daemon=True).start()
        except FileNotFoundError:
            log(self.web_panel_log, "npm not found - install Node.js", "error")
        except Exception as e:
            log(self.web_panel_log, f"Frontend failed: {e}", "error")
    
    def _stop_frontend(self):
        if not self.frontend_process or self.frontend_process.poll() is not None:
            self.frontend_status.set_offline("FRONTEND OFFLINE")
            self.frontend_start.config(state=NORMAL)
            self.frontend_stop.config(state=DISABLED)
            return
        
        try:
            log(self.web_panel_log, "Stopping frontend...", "warning")
            if os.name == 'nt':
                self.frontend_process.send_signal(signal.CTRL_BREAK_EVENT)
            else:
                self.frontend_process.terminate()
            self.frontend_process.wait(timeout=5)
            log(self.web_panel_log, "Frontend stopped", "success")
        except:
            self.frontend_process.kill()
            log(self.web_panel_log, "Frontend killed", "warning")
        finally:
            self.frontend_process = None
            self.frontend_status.set_offline("FRONTEND OFFLINE")
            self.frontend_start.config(state=NORMAL)
            self.frontend_stop.config(state=DISABLED)
    
    # === ACTIONS ===
    def _start_both(self):
        log(self.web_panel_log, "Starting both servers...", "info")
        self._start_backend()
        import time
        time.sleep(2)
        self._start_frontend()
    
    def _stop_both(self):
        log(self.web_panel_log, "Stopping both servers...", "warning")
        self._stop_frontend()
        import time
        time.sleep(1)
        self._stop_backend()
    
    def _open_browser(self):
        webbrowser.open("http://localhost:3000")
        log(self.web_panel_log, "Opened http://localhost:3000", "info")
    
    def _open_folder(self):
        folder = Path("C:/EhkoDev/ehko-control")
        if folder.exists():
            if os.name == 'nt':
                os.startfile(str(folder))
            else:
                subprocess.run(['xdg-open', str(folder)])
        else:
            log(self.web_panel_log, "Folder not found", "error")


# =============================================================================
# GLYPHWORKS TAB - Advanced SVG Rendering
# =============================================================================

class GlyphWorksTab(ttk.Frame):
    """Advanced SVG art creation using programmatic rendering techniques."""
    
    # Material presets based on Advanced SVG Rendering Guide
    MATERIAL_PRESETS = {
        "Brushed Aluminum": {
            "description": "Anisotropic metallic surface with directional noise",
            "noise": {"baseFrequencyX": 0.005, "baseFrequencyY": 0.2, "numOctaves": 2, "type": "turbulence"},
            "lighting": {"surfaceScale": 3, "specularConstant": 1.5, "specularExponent": 25},
            "light": {"type": "distant", "azimuth": 225, "elevation": 45},
            "base_color": "#a8b0c0"
        },
        "Forged Carbon": {
            "description": "Chaotic carbon fiber flakes with multi-angle reflections",
            "noise": {"baseFrequencyX": 0.03, "baseFrequencyY": 0.03, "numOctaves": 4, "type": "turbulence"},
            "lighting": {"surfaceScale": 2, "specularConstant": 2, "specularExponent": 15},
            "light": {"type": "point", "x": 150, "y": 100, "z": 200},
            "base_color": "#1a1a1a"
        },
        "Weathered Stone": {
            "description": "Granite texture with cracks and ambient occlusion",
            "noise": {"baseFrequencyX": 0.04, "baseFrequencyY": 0.04, "numOctaves": 5, "type": "turbulence"},
            "lighting": {"surfaceScale": 4, "specularConstant": 0.5, "specularExponent": 8},
            "light": {"type": "distant", "azimuth": 315, "elevation": 30},
            "base_color": "#6a6a6a"
        },
        "Neon Glow": {
            "description": "Emissive neon with layered bloom effect",
            "noise": None,
            "lighting": None,
            "glow": {"inner_color": "#ffffff", "outer_color": "#ff3366", "layers": 4, "max_blur": 15},
            "base_color": "#ff3366"
        },
        "Holographic": {
            "description": "Rainbow chromatic shift with iridescence",
            "noise": {"baseFrequencyX": 0.02, "baseFrequencyY": 0.02, "numOctaves": 3, "type": "fractalNoise"},
            "lighting": {"surfaceScale": 1, "specularConstant": 2, "specularExponent": 40},
            "light": {"type": "distant", "azimuth": 0, "elevation": 60},
            "chromatic": True,
            "base_color": "#88ccff"
        },
        "Glass": {
            "description": "Transparent refractive surface with caustics",
            "noise": None,
            "lighting": {"surfaceScale": 0.5, "specularConstant": 3, "specularExponent": 80},
            "light": {"type": "point", "x": 100, "y": 50, "z": 300},
            "base_color": "#aaddff",
            "opacity": 0.3
        },
        "Gold Foil": {
            "description": "Reflective hammered gold texture",
            "noise": {"baseFrequencyX": 0.08, "baseFrequencyY": 0.08, "numOctaves": 3, "type": "turbulence"},
            "lighting": {"surfaceScale": 1.5, "specularConstant": 2.5, "specularExponent": 35},
            "light": {"type": "distant", "azimuth": 135, "elevation": 50},
            "base_color": "#d4af37"
        },
        "Cyberpunk Chrome": {
            "description": "High-contrast chrome with glitch effects",
            "noise": {"baseFrequencyX": 0.01, "baseFrequencyY": 0.15, "numOctaves": 2, "type": "turbulence"},
            "lighting": {"surfaceScale": 5, "specularConstant": 3, "specularExponent": 50},
            "light": {"type": "spot", "x": 200, "y": 100, "z": 300, "pointsAtX": 150, "pointsAtY": 150, "pointsAtZ": 0, "limitingConeAngle": 30},
            "chromatic": True,
            "base_color": "#88aacc"
        }
    }
    
    def __init__(self, parent, root):
        super().__init__(parent)
        self.root = root
        self.configure(style="TFrame")
        self.current_preset = None
        self.custom_params = {}
        self._build_ui()
    
    def _build_ui(self):
        container = ttk.Frame(self, padding=10)
        container.pack(fill=BOTH, expand=True)
        
        # === HEADER ===
        header = ttk.Frame(container)
        header.pack(fill=X, pady=(0, 10))
        
        ttk.Label(header, text="GLYPHWORKS", style="H.TLabel").pack(side=LEFT)
        ttk.Label(header, text="Advanced SVG Rendering Engine", style="Sub.TLabel").pack(side=LEFT, padx=10)
        
        # === MAIN LAYOUT: Left (Controls) | Right (Preview) ===
        main_paned = ttk.PanedWindow(container, orient=HORIZONTAL)
        main_paned.pack(fill=BOTH, expand=True)
        
        # --- LEFT PANEL: Controls ---
        left_frame = ttk.Frame(main_paned, width=500)
        main_paned.add(left_frame, weight=1)
        
        # Material Presets
        preset_frame = ttk.LabelFrame(left_frame, text="MATERIAL PRESETS", padding=10)
        preset_frame.pack(fill=X, pady=(0, 10))
        
        preset_grid = ttk.Frame(preset_frame)
        preset_grid.pack(fill=X)
        
        row, col = 0, 0
        for name in self.MATERIAL_PRESETS:
            btn = ttk.Button(preset_grid, text=name, width=16,
                            command=lambda n=name: self._select_preset(n))
            btn.grid(row=row, column=col, padx=2, pady=2, sticky="ew")
            col += 1
            if col >= 4:
                col = 0
                row += 1
        
        for i in range(4):
            preset_grid.columnconfigure(i, weight=1)
        
        self.preset_desc = ttk.Label(preset_frame, text="Select a material preset", style="Dim.TLabel")
        self.preset_desc.pack(fill=X, pady=(8, 0))
        
        # Parameter Controls (scrollable)
        param_outer = ttk.LabelFrame(left_frame, text="PARAMETERS", padding=10)
        param_outer.pack(fill=BOTH, expand=True, pady=(0, 10))
        
        # Canvas with scrollbar for parameters
        param_canvas = Canvas(param_outer, bg=C["bg_secondary"], highlightthickness=0)
        param_scrollbar = ttk.Scrollbar(param_outer, orient=VERTICAL, command=param_canvas.yview)
        self.param_frame = ttk.Frame(param_canvas)
        
        param_canvas.configure(yscrollcommand=param_scrollbar.set)
        param_scrollbar.pack(side=RIGHT, fill=Y)
        param_canvas.pack(side=LEFT, fill=BOTH, expand=True)
        
        param_canvas.create_window((0, 0), window=self.param_frame, anchor=NW)
        self.param_frame.bind("<Configure>", lambda e: param_canvas.configure(scrollregion=param_canvas.bbox("all")))
        
        self._build_param_controls()
        
        # Shape Controls
        shape_frame = ttk.LabelFrame(left_frame, text="SHAPE", padding=10)
        shape_frame.pack(fill=X, pady=(0, 10))
        
        shape_row = ttk.Frame(shape_frame)
        shape_row.pack(fill=X)
        
        ttk.Label(shape_row, text="Type:").pack(side=LEFT)
        self.shape_var = StringVar(value="rectangle")
        shape_menu = ttk.Combobox(shape_row, textvariable=self.shape_var, width=15,
                                   values=["rectangle", "circle", "text", "path", "polygon"])
        shape_menu.pack(side=LEFT, padx=5)
        
        ttk.Label(shape_row, text="Size:").pack(side=LEFT, padx=(10, 0))
        self.size_var = StringVar(value="300x200")
        ttk.Entry(shape_row, textvariable=self.size_var, width=12).pack(side=LEFT, padx=5)
        
        text_row = ttk.Frame(shape_frame)
        text_row.pack(fill=X, pady=(5, 0))
        ttk.Label(text_row, text="Text:").pack(side=LEFT)
        self.text_var = StringVar(value="EHKO")
        ttk.Entry(text_row, textvariable=self.text_var, width=30).pack(side=LEFT, padx=5, fill=X, expand=True)
        
        # Actions
        action_frame = ttk.Frame(left_frame)
        action_frame.pack(fill=X)
        
        ttk.Button(action_frame, text="⚡ Generate Preview", style="G.TButton", width=18,
                   command=self._generate_preview).pack(side=LEFT, padx=2)
        ttk.Button(action_frame, text="💾 Export SVG", width=12,
                   command=self._export_svg).pack(side=LEFT, padx=2)
        ttk.Button(action_frame, text="📋 Copy Code", width=12,
                   command=self._copy_code).pack(side=LEFT, padx=2)
        
        # --- RIGHT PANEL: Preview + Log ---
        right_frame = ttk.Frame(main_paned, width=600)
        main_paned.add(right_frame, weight=2)
        
        # Preview area
        preview_frame = ttk.LabelFrame(right_frame, text="PREVIEW", padding=10)
        preview_frame.pack(fill=BOTH, expand=True, pady=(0, 10))
        
        self.preview_canvas = Canvas(preview_frame, bg=C["bg_primary"], 
                                      highlightthickness=1, highlightbackground=C["accent_dim"])
        self.preview_canvas.pack(fill=BOTH, expand=True)
        
        # Draw placeholder
        self.preview_canvas.create_text(300, 200, text="Preview will appear here",
                                         fill=C["text_dim"], font=("Consolas", 12))
        
        # Log
        log_frame = ttk.LabelFrame(right_frame, text="OUTPUT", padding=10)
        log_frame.pack(fill=X)
        
        self.glyph_log = TerminalLog(log_frame, height=8)
        self.glyph_log.pack(fill=BOTH, expand=True)
        
        log(self.glyph_log, "GlyphWorks ready.", "glyph")
        log(self.glyph_log, "Select a material preset to begin.", "info")
    
    def _build_param_controls(self):
        """Build parameter sliders and inputs."""
        # Clear existing
        for widget in self.param_frame.winfo_children():
            widget.destroy()
        
        # Noise parameters
        noise_lbl = ttk.Label(self.param_frame, text="// NOISE (feTurbulence)", style="Section.TLabel")
        noise_lbl.pack(fill=X, pady=(0, 5))
        
        self.noise_freq_x = self._add_slider("Base Frequency X", 0.001, 0.2, 0.02)
        self.noise_freq_y = self._add_slider("Base Frequency Y", 0.001, 0.2, 0.02)
        self.noise_octaves = self._add_slider("Octaves", 1, 8, 3, integer=True)
        
        noise_type_row = ttk.Frame(self.param_frame)
        noise_type_row.pack(fill=X, pady=2)
        ttk.Label(noise_type_row, text="Type:", width=20).pack(side=LEFT)
        self.noise_type = StringVar(value="turbulence")
        ttk.Radiobutton(noise_type_row, text="Turbulence", variable=self.noise_type, value="turbulence").pack(side=LEFT)
        ttk.Radiobutton(noise_type_row, text="Fractal", variable=self.noise_type, value="fractalNoise").pack(side=LEFT)
        
        self.noise_seed = self._add_slider("Seed", 0, 1000, 42, integer=True)
        
        # Lighting parameters
        ttk.Separator(self.param_frame, orient=HORIZONTAL).pack(fill=X, pady=10)
        light_lbl = ttk.Label(self.param_frame, text="// LIGHTING (Phong Model)", style="Section.TLabel")
        light_lbl.pack(fill=X, pady=(0, 5))
        
        self.surface_scale = self._add_slider("Surface Scale", 0.1, 10, 2)
        self.spec_constant = self._add_slider("Specular Constant", 0.1, 5, 1.5)
        self.spec_exponent = self._add_slider("Specular Exponent", 1, 100, 20)
        self.diff_constant = self._add_slider("Diffuse Constant", 0.1, 3, 1)
        
        # Light source
        ttk.Separator(self.param_frame, orient=HORIZONTAL).pack(fill=X, pady=10)
        source_lbl = ttk.Label(self.param_frame, text="// LIGHT SOURCE", style="Section.TLabel")
        source_lbl.pack(fill=X, pady=(0, 5))
        
        source_row = ttk.Frame(self.param_frame)
        source_row.pack(fill=X, pady=2)
        ttk.Label(source_row, text="Source Type:", width=20).pack(side=LEFT)
        self.light_type = StringVar(value="distant")
        ttk.Radiobutton(source_row, text="Distant", variable=self.light_type, value="distant").pack(side=LEFT)
        ttk.Radiobutton(source_row, text="Point", variable=self.light_type, value="point").pack(side=LEFT)
        ttk.Radiobutton(source_row, text="Spot", variable=self.light_type, value="spot").pack(side=LEFT)
        
        self.light_azimuth = self._add_slider("Azimuth", 0, 360, 225)
        self.light_elevation = self._add_slider("Elevation", 0, 90, 45)
        self.light_x = self._add_slider("Light X", 0, 400, 150)
        self.light_y = self._add_slider("Light Y", 0, 400, 100)
        self.light_z = self._add_slider("Light Z", 10, 500, 200)
        
        # Glow parameters
        ttk.Separator(self.param_frame, orient=HORIZONTAL).pack(fill=X, pady=10)
        glow_lbl = ttk.Label(self.param_frame, text="// GLOW / BLOOM", style="Section.TLabel")
        glow_lbl.pack(fill=X, pady=(0, 5))
        
        self.glow_layers = self._add_slider("Glow Layers", 1, 8, 4, integer=True)
        self.glow_max_blur = self._add_slider("Max Blur", 2, 50, 15)
        
        # Color
        color_row = ttk.Frame(self.param_frame)
        color_row.pack(fill=X, pady=5)
        ttk.Label(color_row, text="Base Color:", width=20).pack(side=LEFT)
        self.base_color = StringVar(value="#6b8cce")
        self.color_entry = ttk.Entry(color_row, textvariable=self.base_color, width=10)
        self.color_entry.pack(side=LEFT, padx=5)
        ttk.Button(color_row, text="Pick", width=6, command=self._pick_color).pack(side=LEFT)
        
        self.color_preview = Label(color_row, bg="#6b8cce", width=4, height=1)
        self.color_preview.pack(side=LEFT, padx=5)
    
    def _add_slider(self, label, min_val, max_val, default, integer=False):
        """Add a labeled slider control."""
        row = ttk.Frame(self.param_frame)
        row.pack(fill=X, pady=2)
        
        ttk.Label(row, text=f"{label}:", width=20).pack(side=LEFT)
        
        var = DoubleVar(value=default) if not integer else IntVar(value=int(default))
        
        slider = ttk.Scale(row, from_=min_val, to=max_val, variable=var, orient=HORIZONTAL, length=150)
        slider.pack(side=LEFT, padx=5)
        
        value_lbl = ttk.Label(row, text=f"{default:.3f}" if not integer else str(default), width=8)
        value_lbl.pack(side=LEFT)
        
        def update_label(*args):
            val = var.get()
            value_lbl.config(text=f"{val:.3f}" if not integer else str(int(val)))
        
        var.trace_add("write", update_label)
        
        return var
    
    def _select_preset(self, name):
        """Load a material preset."""
        preset = self.MATERIAL_PRESETS.get(name)
        if not preset:
            return
        
        self.current_preset = name
        self.preset_desc.config(text=preset["description"])
        
        # Apply noise params
        if preset.get("noise"):
            n = preset["noise"]
            self.noise_freq_x.set(n.get("baseFrequencyX", 0.02))
            self.noise_freq_y.set(n.get("baseFrequencyY", 0.02))
            self.noise_octaves.set(n.get("numOctaves", 3))
            self.noise_type.set(n.get("type", "turbulence"))
        
        # Apply lighting params
        if preset.get("lighting"):
            l = preset["lighting"]
            self.surface_scale.set(l.get("surfaceScale", 2))
            self.spec_constant.set(l.get("specularConstant", 1.5))
            self.spec_exponent.set(l.get("specularExponent", 20))
        
        # Apply light source params
        if preset.get("light"):
            lt = preset["light"]
            self.light_type.set(lt.get("type", "distant"))
            if lt.get("type") == "distant":
                self.light_azimuth.set(lt.get("azimuth", 225))
                self.light_elevation.set(lt.get("elevation", 45))
            else:
                self.light_x.set(lt.get("x", 150))
                self.light_y.set(lt.get("y", 100))
                self.light_z.set(lt.get("z", 200))
        
        # Apply glow params
        if preset.get("glow"):
            g = preset["glow"]
            self.glow_layers.set(g.get("layers", 4))
            self.glow_max_blur.set(g.get("max_blur", 15))
        
        # Apply color
        self.base_color.set(preset.get("base_color", "#6b8cce"))
        self.color_preview.config(bg=preset.get("base_color", "#6b8cce"))
        
        log(self.glyph_log, f"Loaded preset: {name}", "glyph")
    
    def _pick_color(self):
        """Open color picker."""
        color = colorchooser.askcolor(initialcolor=self.base_color.get())
        if color[1]:
            self.base_color.set(color[1])
            self.color_preview.config(bg=color[1])
    
    def _generate_svg_code(self):
        """Generate SVG code based on current parameters."""
        size = self.size_var.get().split("x")
        width = int(size[0]) if len(size) > 0 else 300
        height = int(size[1]) if len(size) > 1 else 200
        
        # Build filter
        filter_id = "glyphworks_filter"
        noise_type = self.noise_type.get()
        freq_x = self.noise_freq_x.get()
        freq_y = self.noise_freq_y.get()
        octaves = int(self.noise_octaves.get())
        seed = int(self.noise_seed.get())
        
        surface_scale = self.surface_scale.get()
        spec_const = self.spec_constant.get()
        spec_exp = int(self.spec_exponent.get())
        
        light_type = self.light_type.get()
        base_color = self.base_color.get()
        
        # Build light source element
        if light_type == "distant":
            azimuth = self.light_azimuth.get()
            elevation = self.light_elevation.get()
            light_source = f'<feDistantLight azimuth="{azimuth}" elevation="{elevation}"/>'
        elif light_type == "point":
            x = self.light_x.get()
            y = self.light_y.get()
            z = self.light_z.get()
            light_source = f'<fePointLight x="{x}" y="{y}" z="{z}"/>'
        else:
            x = self.light_x.get()
            y = self.light_y.get()
            z = self.light_z.get()
            light_source = f'<feSpotLight x="{x}" y="{y}" z="{z}" pointsAtX="{width/2}" pointsAtY="{height/2}" pointsAtZ="0" limitingConeAngle="30"/>'
        
        # Build shape
        shape_type = self.shape_var.get()
        if shape_type == "rectangle":
            shape = f'<rect x="20" y="20" width="{width-40}" height="{height-40}" rx="8" fill="{base_color}" filter="url(#{filter_id})"/>'
        elif shape_type == "circle":
            r = min(width, height) / 2 - 20
            shape = f'<circle cx="{width/2}" cy="{height/2}" r="{r}" fill="{base_color}" filter="url(#{filter_id})"/>'
        elif shape_type == "text":
            text = self.text_var.get()
            shape = f'<text x="{width/2}" y="{height/2}" text-anchor="middle" dominant-baseline="middle" font-family="Arial Black" font-size="72" font-weight="bold" fill="{base_color}" filter="url(#{filter_id})">{text}</text>'
        else:
            shape = f'<rect x="20" y="20" width="{width-40}" height="{height-40}" fill="{base_color}" filter="url(#{filter_id})"/>'
        
        # Check if this is a glow preset
        is_glow = self.current_preset == "Neon Glow"
        
        if is_glow:
            glow_layers = int(self.glow_layers.get())
            max_blur = self.glow_max_blur.get()
            
            # Build glow filter
            glow_primitives = []
            for i in range(glow_layers):
                blur = max_blur * (i + 1) / glow_layers
                opacity = 1 - (i / glow_layers) * 0.7
                glow_primitives.append(f'''
        <feGaussianBlur in="SourceGraphic" stdDeviation="{blur}" result="blur{i}"/>
        <feColorMatrix in="blur{i}" type="matrix" values="1 0 0 0 0 0 1 0 0 0 0 0 1 0 0 0 0 0 {opacity} 0" result="glow{i}"/>''')
            
            merge_nodes = "\n".join([f'      <feMergeNode in="glow{i}"/>' for i in range(glow_layers-1, -1, -1)])
            merge_nodes += '\n      <feMergeNode in="SourceGraphic"/>'
            
            filter_def = f'''  <filter id="{filter_id}" x="-50%" y="-50%" width="200%" height="200%">
        {"".join(glow_primitives)}
    <feMerge>
{merge_nodes}
    </feMerge>
  </filter>'''
        else:
            # Standard material filter
            filter_def = f'''  <filter id="{filter_id}" x="-10%" y="-10%" width="120%" height="120%">
    <!-- Noise Generation -->
    <feTurbulence type="{noise_type}" baseFrequency="{freq_x} {freq_y}" 
                  numOctaves="{octaves}" seed="{seed}" result="noise"/>
    
    <!-- Diffuse Lighting -->
    <feDiffuseLighting in="noise" surfaceScale="{surface_scale}" 
                       diffuseConstant="{self.diff_constant.get()}" 
                       lighting-color="{base_color}" result="diffuse">
      {light_source}
    </feDiffuseLighting>
    
    <!-- Specular Lighting -->
    <feSpecularLighting in="noise" surfaceScale="{surface_scale}" 
                        specularConstant="{spec_const}" 
                        specularExponent="{spec_exp}" 
                        lighting-color="#ffffff" result="specular">
      {light_source}
    </feSpecularLighting>
    
    <!-- Composite -->
    <feComposite in="diffuse" in2="SourceGraphic" operator="in" result="diffuse_masked"/>
    <feComposite in="specular" in2="SourceGraphic" operator="in" result="specular_masked"/>
    <feBlend in="diffuse_masked" in2="specular_masked" mode="screen"/>
  </filter>'''
        
        svg_code = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
  <defs>
{filter_def}
  </defs>
  
  <!-- Background -->
  <rect width="100%" height="100%" fill="#080a0e"/>
  
  <!-- Shape with Material -->
  {shape}
</svg>'''
        
        return svg_code
    
    def _generate_preview(self):
        """Generate and display preview."""
        log(self.glyph_log, "Generating preview...", "glyph")
        
        svg_code = self._generate_svg_code()
        
        # Save temp file
        GLYPHWORKS_OUTPUT.mkdir(parents=True, exist_ok=True)
        temp_file = GLYPHWORKS_OUTPUT / "preview.svg"
        temp_file.write_text(svg_code, encoding="utf-8")
        
        # Open in browser for preview (SVG rendering is complex in Tkinter)
        webbrowser.open(str(temp_file))
        
        log(self.glyph_log, f"Preview saved: {temp_file}", "success")
        log(self.glyph_log, "Opened in browser for accurate rendering.", "info")
    
    def _export_svg(self):
        """Export SVG to file."""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".svg",
            filetypes=[("SVG files", "*.svg"), ("All files", "*.*")],
            initialdir=str(GLYPHWORKS_OUTPUT),
            initialfile=f"glyph_{datetime.now().strftime('%Y%m%d_%H%M%S')}.svg"
        )
        
        if file_path:
            svg_code = self._generate_svg_code()
            Path(file_path).write_text(svg_code, encoding="utf-8")
            log(self.glyph_log, f"Exported: {file_path}", "success")
    
    def _copy_code(self):
        """Copy SVG code to clipboard."""
        svg_code = self._generate_svg_code()
        self.root.clipboard_clear()
        self.root.clipboard_append(svg_code)
        self.root.update()
        log(self.glyph_log, "SVG code copied to clipboard", "success")


# =============================================================================
# MAIN APPLICATION
# =============================================================================

class EhkoControlPanel:
    """Main application window."""
    
    def __init__(self):
        self.root = Tk()
        self.root.title("Ehko Control Panel v5.2")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 700)
        self.root.configure(bg=C["bg_primary"])
        
        self._setup_styles()
        self._build_ui()
        self._setup_bindings()
    
    def _setup_styles(self):
        """Configure ttk styles for terminal aesthetic."""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Frame styles
        style.configure("TFrame", background=C["bg_primary"])
        style.configure("TLabelframe", background=C["bg_primary"])
        style.configure("TLabelframe.Label", 
                       background=C["bg_primary"], 
                       foreground=C["accent_dim"],
                       font=("Consolas", 10, "bold"))
        
        # Label styles
        style.configure("TLabel", 
                       background=C["bg_primary"], 
                       foreground=C["text_primary"],
                       font=("Consolas", 10))
        style.configure("H.TLabel", 
                       font=("Consolas", 16, "bold"), 
                       foreground=C["accent"])
        style.configure("Sub.TLabel",
                       foreground=C["text_dim"],
                       font=("Consolas", 10))
        style.configure("Dim.TLabel",
                       foreground=C["text_dim"],
                       font=("Consolas", 9))
        style.configure("Path.TLabel",
                       foreground=C["text_muted"],
                       font=("Consolas", 9))
        style.configure("Section.TLabel",
                       foreground=C["accent_dim"],
                       font=("Consolas", 9, "bold"))
        
        # Button styles
        style.configure("TButton",
                       background=C["bg_tertiary"],
                       foreground=C["text_primary"],
                       font=("Consolas", 10),
                       padding=(12, 8))
        style.map("TButton",
                 background=[("active", C["accent_dim"]), ("disabled", C["bg_secondary"])],
                 foreground=[("disabled", C["text_dim"])])
        
        # Colored button variants
        style.configure("G.TButton", background="#1a3a2a")
        style.map("G.TButton", background=[("active", "#2a5a4a"), ("disabled", "#0a1a0a")])
        
        style.configure("R.TButton", background="#3a1a1a")
        style.map("R.TButton", background=[("active", "#5a2a2a"), ("disabled", "#1a0a0a")])
        
        style.configure("B.TButton", background="#1a2a3a")
        style.map("B.TButton", background=[("active", "#2a4a5a")])
        
        style.configure("Y.TButton", background="#3a3a1a")
        style.map("Y.TButton", background=[("active", "#5a5a2a")])
        
        style.configure("Accent.TButton", background="#2a3a5a")
        style.map("Accent.TButton", background=[("active", "#3a4a6a")])
        
        # Notebook (tabs)
        style.configure("TNotebook", background=C["bg_primary"], borderwidth=0)
        style.configure("TNotebook.Tab",
                       background=C["bg_secondary"],
                       foreground=C["text_secondary"],
                       font=("Consolas", 11, "bold"),
                       padding=(20, 10))
        style.map("TNotebook.Tab",
                 background=[("selected", C["bg_tertiary"])],
                 foreground=[("selected", C["accent"])])
        
        # Separator
        style.configure("TSeparator", background=C["border_subtle"])
        
        # Scale (slider)
        style.configure("TScale", background=C["bg_primary"])
        
        # Combobox
        style.configure("TCombobox",
                       fieldbackground=C["bg_secondary"],
                       background=C["bg_tertiary"],
                       foreground=C["text_primary"])
        
        # Entry
        style.configure("TEntry",
                       fieldbackground=C["bg_secondary"],
                       foreground=C["text_primary"])
    
    def _build_ui(self):
        """Build main UI with tabbed interface."""
        # Header
        header = ttk.Frame(self.root, padding=(15, 10))
        header.pack(fill=X)
        
        ttk.Label(header, text="EHKO CONTROL PANEL", style="H.TLabel").pack(side=LEFT)
        ttk.Label(header, text="v5.1", style="Dim.TLabel").pack(side=LEFT, padx=10)
        
        # Separator
        ttk.Separator(self.root, orient=HORIZONTAL).pack(fill=X)
        
        # Notebook (tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        self.ehkoforge_tab = EhkoForgeTab(self.notebook, self.root)
        self.recog_tab = ReCogTab(self.notebook, self.root)
        self.website_tab = WebsiteTab(self.notebook, self.root)
        self.webpanel_tab = WebPanelTab(self.notebook, self.root)
        self.glyphworks_tab = GlyphWorksTab(self.notebook, self.root)
        
        self.notebook.add(self.ehkoforge_tab, text="  EHKOFORGE  ")
        self.notebook.add(self.recog_tab, text="  RECOG  ")
        self.notebook.add(self.website_tab, text="  WEBSITE  ")
        self.notebook.add(self.webpanel_tab, text="  WEB PANEL  ")
        self.notebook.add(self.glyphworks_tab, text="  GLYPHWORKS  ")
    
    def _setup_bindings(self):
        """Setup keyboard shortcuts and close handler."""
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        
        # Keyboard shortcuts
        self.root.bind("<Control-1>", lambda e: self.notebook.select(0))
        self.root.bind("<Control-2>", lambda e: self.notebook.select(1))
        self.root.bind("<Control-3>", lambda e: self.notebook.select(2))
        self.root.bind("<Control-4>", lambda e: self.notebook.select(3))
        self.root.bind("<Control-5>", lambda e: self.notebook.select(4))
    
    def _on_close(self):
        """Handle window close - stop running services."""
        global server_process, recog_process, website_process
        
        stop_needed = []
        if server_process and server_process.poll() is None:
            stop_needed.append("EhkoForge Server")
        if recog_process and recog_process.poll() is None:
            stop_needed.append("ReCog Server")
        if website_process and website_process.poll() is None:
            stop_needed.append("Website Dev Server")
        
        if stop_needed:
            services = ", ".join(stop_needed)
            if messagebox.askyesno("Services Running", f"Stop {services} before closing?"):
                if server_process and server_process.poll() is None:
                    try:
                        if os.name == 'nt':
                            server_process.send_signal(signal.CTRL_BREAK_EVENT)
                        else:
                            server_process.terminate()
                        server_process.wait(timeout=3)
                    except:
                        server_process.kill()
                
                if recog_process and recog_process.poll() is None:
                    try:
                        if os.name == 'nt':
                            recog_process.send_signal(signal.CTRL_BREAK_EVENT)
                        else:
                            recog_process.terminate()
                        recog_process.wait(timeout=3)
                    except:
                        recog_process.kill()
                
                if website_process and website_process.poll() is None:
                    try:
                        if os.name == 'nt':
                            website_process.send_signal(signal.CTRL_BREAK_EVENT)
                        else:
                            website_process.terminate()
                        website_process.wait(timeout=3)
                    except:
                        website_process.kill()
        
        self.root.destroy()
    
    def run(self):
        """Start the application."""
        self.root.mainloop()


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    app = EhkoControlPanel()
    app.run()

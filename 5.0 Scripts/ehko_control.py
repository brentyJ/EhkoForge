#!/usr/bin/env python3
"""
EhkoForge Control Panel v2.0
Touch-optimized GUI for managing EhkoForge operations.
Designed for Surface Pro / tablet use.

Run: py ehko_control.py
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

# Paths - adjust if your vault location differs
EHKOFORGE_ROOT = Path("G:/Other computers/Ehko/Obsidian/EhkoForge")
MIRRORWELL_ROOT = Path("G:/Other computers/Ehko/Obsidian/Mirrorwell")
SCRIPTS_PATH = EHKOFORGE_ROOT / "5.0 Scripts"
BACKUPS_PATH = Path("G:/Other computers/Ehko/Obsidian/backups")

# Server settings
SERVER_SCRIPT = SCRIPTS_PATH / "forge_server.py"
SERVER_URL = "http://localhost:5000"

# Scripts
REFRESH_SCRIPT = SCRIPTS_PATH / "ehko_refresh.py"
BATCH_SCRIPT = Path("G:/Other computers/Ehko/Obsidian/run_process_transcriptions.bat")

# =============================================================================
# GLOBAL STATE
# =============================================================================

server_process = None

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def log(text_widget, message, tag=None):
    """Add timestamped message to log widget."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    text_widget.config(state=NORMAL)
    if tag:
        text_widget.insert(END, f"[{timestamp}] {message}\n", tag)
    else:
        text_widget.insert(END, f"[{timestamp}] {message}\n")
    text_widget.see(END)
    text_widget.config(state=DISABLED)


def run_command_async(text_widget, command, cwd=None, shell=False):
    """Run a command asynchronously and stream output to log."""
    def _run():
        try:
            log(text_widget, f"Running: {command}", "info")
            
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                cwd=cwd,
                shell=shell,
                text=True,
                bufsize=1
            )
            
            for line in iter(process.stdout.readline, ''):
                if line:
                    log(text_widget, line.strip())
            
            process.wait()
            
            if process.returncode == 0:
                log(text_widget, "✓ Command completed successfully", "success")
            else:
                log(text_widget, f"✗ Command exited with code {process.returncode}", "error")
                
        except Exception as e:
            log(text_widget, f"✗ Error: {str(e)}", "error")
    
    thread = threading.Thread(target=_run, daemon=True)
    thread.start()


def api_call(endpoint, method="GET", data=None):
    """Make an API call to the local server."""
    url = f"{SERVER_URL}{endpoint}"
    
    try:
        if method == "POST":
            req = urllib.request.Request(
                url,
                data=json.dumps(data or {}).encode('utf-8') if data else b'{}',
                headers={'Content-Type': 'application/json'},
                method='POST'
            )
        else:
            req = urllib.request.Request(url)
        
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.URLError as e:
        return {"error": f"Connection failed: {e.reason}"}
    except Exception as e:
        return {"error": str(e)}


# =============================================================================
# SERVER CONTROLS
# =============================================================================

def start_server_terminal(text_widget, status_label):
    """Start the Forge server in a new terminal window."""
    global server_process
    
    if server_process and server_process.poll() is None:
        log(text_widget, "Server is already running", "warning")
        return
    
    try:
        log(text_widget, "Starting Forge server in terminal...", "info")
        
        if os.name == 'nt':
            cmd = f'cd "{SCRIPTS_PATH}" ; py forge_server.py'
            server_process = subprocess.Popen(
                ['powershell', '-NoExit', '-Command', cmd],
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
        else:
            server_process = subprocess.Popen(
                ['x-terminal-emulator', '-e', f'cd "{SCRIPTS_PATH}" && python3 forge_server.py'],
            )
        
        status_label.config(text="● Server Running", foreground="#5fb3a1")
        log(text_widget, f"Server started in separate terminal window", "success")
        log(text_widget, f"  Access at: {SERVER_URL}", "info")
        
    except Exception as e:
        log(text_widget, f"Failed to start server: {str(e)}", "error")
        status_label.config(text="○ Server Stopped", foreground="#d97373")


def start_server(text_widget, status_label):
    """Start the Forge server with output in control panel."""
    global server_process
    
    if server_process and server_process.poll() is None:
        log(text_widget, "Server is already running", "warning")
        return
    
    try:
        log(text_widget, "Starting Forge server...", "info")
        
        server_process = subprocess.Popen(
            [sys.executable, str(SERVER_SCRIPT)],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            cwd=str(SCRIPTS_PATH),
            text=True,
            bufsize=1,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
        )
        
        status_label.config(text="● Server Running", foreground="#5fb3a1")
        log(text_widget, f"✓ Server started (PID: {server_process.pid})", "success")
        log(text_widget, f"  Access at: {SERVER_URL}", "info")
        
        def stream_output():
            for line in iter(server_process.stdout.readline, ''):
                if line and server_process.poll() is None:
                    log(text_widget, f"[server] {line.strip()}")
            status_label.config(text="○ Server Stopped", foreground="#d97373")
            log(text_widget, "Server process ended", "warning")
        
        thread = threading.Thread(target=stream_output, daemon=True)
        thread.start()
        
    except Exception as e:
        log(text_widget, f"✗ Failed to start server: {str(e)}", "error")
        status_label.config(text="○ Server Stopped", foreground="#d97373")


def stop_server(text_widget, status_label):
    """Stop the Forge server."""
    global server_process
    
    if not server_process or server_process.poll() is not None:
        log(text_widget, "Server is not running", "warning")
        status_label.config(text="○ Server Stopped", foreground="#d97373")
        return
    
    try:
        log(text_widget, "Stopping server...", "info")
        
        if os.name == 'nt':
            server_process.send_signal(signal.CTRL_BREAK_EVENT)
        else:
            server_process.terminate()
        
        server_process.wait(timeout=5)
        log(text_widget, "✓ Server stopped", "success")
        
    except subprocess.TimeoutExpired:
        log(text_widget, "Server didn't stop gracefully, forcing...", "warning")
        server_process.kill()
        log(text_widget, "✓ Server killed", "success")
        
    except Exception as e:
        log(text_widget, f"✗ Error stopping server: {str(e)}", "error")
    
    finally:
        server_process = None
        status_label.config(text="○ Server Stopped", foreground="#d97373")


def open_forge_ui(text_widget):
    """Open Forge UI in default browser."""
    log(text_widget, f"Opening {SERVER_URL} in browser...", "info")
    webbrowser.open(SERVER_URL)


# =============================================================================
# FORGE/SMELT CONTROLS (API-based)
# =============================================================================

def queue_all_sessions(text_widget):
    """Queue all forged sessions for smelting via API."""
    log(text_widget, "Queuing all sessions for smelting...", "info")
    
    result = api_call("/api/smelt/queue-all", method="POST")
    
    if "error" in result:
        log(text_widget, f"✗ {result['error']}", "error")
    else:
        count = result.get("count", 0)
        log(text_widget, f"✓ Queued {count} session(s) for smelting", "success")


def run_smelt(text_widget):
    """Run smelt processor via API."""
    log(text_widget, "Running smelt processor...", "info")
    
    result = api_call("/api/smelt/run", method="POST", data={"limit": 10})
    
    if "error" in result:
        log(text_widget, f"✗ {result['error']}", "error")
    else:
        created = result.get("ingots_created", 0)
        surfaced = result.get("surfaced", 0)
        log(text_widget, f"✓ Smelt complete: {created} ingots created, {surfaced} surfaced", "success")


def resurface_ingots(text_widget):
    """Re-check surfacing criteria for existing ingots."""
    log(text_widget, "Resurfacing ingots...", "info")
    
    result = api_call("/api/smelt/resurface", method="POST")
    
    if "error" in result:
        log(text_widget, f"✗ {result['error']}", "error")
    else:
        surfaced = result.get("surfaced", 0)
        log(text_widget, f"✓ Surfaced {surfaced} ingot(s)", "success")


def get_smelt_status(text_widget):
    """Get smelt queue and ingot status."""
    log(text_widget, "Fetching status...", "info")
    
    # Queue status
    queue_result = api_call("/api/smelt/status")
    if "error" not in queue_result:
        pending = queue_result.get("queue", {}).get("pending", {}).get("count", 0)
        log(text_widget, f"  Smelt queue: {pending} pending", "info")
    
    # Ingot counts
    debug_result = api_call("/api/ingots/debug")
    if "error" not in debug_result:
        ingots = debug_result.get("ingots", [])
        by_status = {}
        for ing in ingots:
            status = ing.get("status", "unknown")
            by_status[status] = by_status.get(status, 0) + 1
        
        log(text_widget, f"  Ingots: {debug_result.get('total', 0)} total", "info")
        for status, count in by_status.items():
            log(text_widget, f"    - {status}: {count}", "info")


# =============================================================================
# SCRIPT RUNNERS
# =============================================================================

def run_refresh(text_widget):
    """Run ehko_refresh.py to reindex vaults."""
    if not REFRESH_SCRIPT.exists():
        log(text_widget, f"✗ Script not found: {REFRESH_SCRIPT}", "error")
        return
    
    run_command_async(
        text_widget,
        [sys.executable, str(REFRESH_SCRIPT)],
        cwd=str(SCRIPTS_PATH)
    )


def run_refresh_full(text_widget):
    """Run ehko_refresh.py with --full flag."""
    if not REFRESH_SCRIPT.exists():
        log(text_widget, f"✗ Script not found: {REFRESH_SCRIPT}", "error")
        return
    
    run_command_async(
        text_widget,
        [sys.executable, str(REFRESH_SCRIPT), "--full"],
        cwd=str(SCRIPTS_PATH)
    )


def run_transcription_batch(text_widget):
    """Run the transcription processing batch file."""
    if not BATCH_SCRIPT.exists():
        log(text_widget, f"✗ Batch file not found: {BATCH_SCRIPT}", "error")
        return
    
    run_command_async(
        text_widget,
        str(BATCH_SCRIPT),
        cwd=str(BATCH_SCRIPT.parent),
        shell=True
    )


def run_git_push(text_widget):
    """Run git_push.bat to commit and push to GitHub."""
    git_script = EHKOFORGE_ROOT / "git_push.bat"
    
    if not git_script.exists():
        log(text_widget, f"✗ Script not found: {git_script}", "error")
        return
    
    log(text_widget, "Opening git push script...", "info")
    
    # Run in new terminal so user can enter commit message
    if os.name == 'nt':
        subprocess.Popen(
            ['cmd', '/c', 'start', 'cmd', '/k', str(git_script)],
            cwd=str(EHKOFORGE_ROOT)
        )
    else:
        subprocess.Popen(
            ['x-terminal-emulator', '-e', str(git_script)],
            cwd=str(EHKOFORGE_ROOT)
        )


# =============================================================================
# FILE OPERATIONS
# =============================================================================

def open_folder(path, text_widget):
    """Open folder in file explorer."""
    if not path.exists():
        log(text_widget, f"✗ Path not found: {path}", "error")
        return
    
    log(text_widget, f"Opening: {path}", "info")
    
    if os.name == 'nt':
        os.startfile(str(path))
    elif sys.platform == 'darwin':
        subprocess.run(['open', str(path)])
    else:
        subprocess.run(['xdg-open', str(path)])


def clear_backups(text_widget):
    """Delete all files in backups folder."""
    if not BACKUPS_PATH.exists():
        log(text_widget, f"Backups folder doesn't exist: {BACKUPS_PATH}", "warning")
        return
    
    files = list(BACKUPS_PATH.glob("*"))
    
    if not files:
        log(text_widget, "No backup files to delete", "info")
        return
    
    result = messagebox.askyesno(
        "Clear Backups",
        f"Delete {len(files)} file(s) from backups folder?\n\nThis cannot be undone."
    )
    
    if result:
        deleted = 0
        for f in files:
            try:
                if f.is_file():
                    f.unlink()
                    deleted += 1
            except Exception as e:
                log(text_widget, f"✗ Failed to delete {f.name}: {e}", "error")
        
        log(text_widget, f"✓ Deleted {deleted} backup file(s)", "success")


def clear_log(text_widget):
    """Clear the log output."""
    text_widget.config(state=NORMAL)
    text_widget.delete(1.0, END)
    text_widget.config(state=DISABLED)
    log(text_widget, "Log cleared", "info")


# =============================================================================
# COMMAND LINE RUNNER
# =============================================================================

def run_custom_command(text_widget, entry_widget):
    """Run a custom command from the entry field."""
    command = entry_widget.get().strip()
    
    if not command:
        log(text_widget, "No command entered", "warning")
        return
    
    log(text_widget, f"> {command}", "info")
    entry_widget.delete(0, END)
    
    run_command_async(
        text_widget,
        command,
        cwd=str(SCRIPTS_PATH),
        shell=True
    )


# =============================================================================
# GUI - TOUCH OPTIMIZED
# =============================================================================

def create_touch_button(parent, text, command, style="TButton", width=14):
    """Create a large touch-friendly button."""
    btn = ttk.Button(
        parent, 
        text=text, 
        command=command, 
        style=style,
        width=width
    )
    return btn


def create_gui():
    """Create the touch-optimized control panel GUI."""
    
    # Main window
    root = Tk()
    root.title("◈ EhkoForge Control Panel")
    root.geometry("800x600")
    root.configure(bg="#0d0f13")
    root.resizable(True, True)
    
    # Style
    style = ttk.Style()
    style.theme_use('clam')
    
    # Base styles
    style.configure("TFrame", background="#0d0f13")
    style.configure("TLabel", background="#0d0f13", foreground="#e8e6e3", font=("Segoe UI", 11))
    style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"), foreground="#9b7ed9")
    style.configure("Status.TLabel", font=("Segoe UI", 12))
    
    style.configure("TLabelframe", background="#0d0f13", foreground="#e8e6e3")
    style.configure("TLabelframe.Label", background="#0d0f13", foreground="#6b8cce", 
                    font=("Segoe UI", 10, "bold"))
    
    # Touch-friendly button style (larger padding)
    style.configure("TButton", 
                    background="#1a1e26", 
                    foreground="#e8e6e3",
                    borderwidth=1,
                    focuscolor="none",
                    font=("Segoe UI", 10),
                    padding=(12, 10))
    style.map("TButton",
              background=[("active", "#2a2e36"), ("pressed", "#0d0f13")],
              foreground=[("active", "#ffffff")])
    
    # Colored button styles
    style.configure("Server.TButton", background="#1a4a3a", font=("Segoe UI", 10, "bold"))
    style.map("Server.TButton", background=[("active", "#2a6a5a")])
    
    style.configure("Stop.TButton", background="#4a1a1a", font=("Segoe UI", 10, "bold"))
    style.map("Stop.TButton", background=[("active", "#6a2a2a")])
    
    style.configure("Forge.TButton", background="#3a2a1a", font=("Segoe UI", 10, "bold"))
    style.map("Forge.TButton", background=[("active", "#5a4a2a")])
    
    style.configure("Action.TButton", background="#1a2a4a")
    style.map("Action.TButton", background=[("active", "#2a4a6a")])
    
    # Entry style
    style.configure("TEntry", fieldbackground="#14171d", foreground="#e8e6e3")
    
    # Main container
    main_frame = ttk.Frame(root, padding="10")
    main_frame.pack(fill=BOTH, expand=True)
    
    # Header row
    header_frame = ttk.Frame(main_frame)
    header_frame.pack(fill=X, pady=(0, 10))
    
    title_label = ttk.Label(header_frame, text="◈ EhkoForge Control Panel", style="Header.TLabel")
    title_label.pack(side=LEFT)
    
    status_label = ttk.Label(header_frame, text="○ Server Stopped", 
                            style="Status.TLabel", foreground="#d97373")
    status_label.pack(side=RIGHT)
    
    # Button grid - using grid for better touch layout
    buttons_frame = ttk.Frame(main_frame)
    buttons_frame.pack(fill=X, pady=(0, 10))
    
    # Row 0: Server controls
    server_frame = ttk.LabelFrame(buttons_frame, text="Server", padding="8")
    server_frame.grid(row=0, column=0, padx=(0, 5), pady=2, sticky="nsew")
    
    create_touch_button(server_frame, "▶ Start Server", 
                       lambda: start_server(log_text, status_label), "Server.TButton").pack(fill=X, pady=3)
    create_touch_button(server_frame, "▶ In Terminal",
                       lambda: start_server_terminal(log_text, status_label), "Server.TButton").pack(fill=X, pady=3)
    create_touch_button(server_frame, "■ Stop Server",
                       lambda: stop_server(log_text, status_label), "Stop.TButton").pack(fill=X, pady=3)
    create_touch_button(server_frame, "🌐 Open UI",
                       lambda: open_forge_ui(log_text)).pack(fill=X, pady=3)
    
    # Row 0: Forge controls (NEW)
    forge_frame = ttk.LabelFrame(buttons_frame, text="Forge / Smelt", padding="8")
    forge_frame.grid(row=0, column=1, padx=5, pady=2, sticky="nsew")
    
    create_touch_button(forge_frame, "📥 Queue All",
                       lambda: queue_all_sessions(log_text), "Forge.TButton").pack(fill=X, pady=3)
    create_touch_button(forge_frame, "⚒️ Run Smelt",
                       lambda: run_smelt(log_text), "Forge.TButton").pack(fill=X, pady=3)
    create_touch_button(forge_frame, "🔼 Resurface",
                       lambda: resurface_ingots(log_text), "Forge.TButton").pack(fill=X, pady=3)
    create_touch_button(forge_frame, "📊 Status",
                       lambda: get_smelt_status(log_text)).pack(fill=X, pady=3)
    
    # Row 0: Scripts
    scripts_frame = ttk.LabelFrame(buttons_frame, text="Scripts", padding="8")
    scripts_frame.grid(row=0, column=2, padx=5, pady=2, sticky="nsew")
    
    create_touch_button(scripts_frame, "🔄 Refresh Index",
                       lambda: run_refresh(log_text), "Action.TButton").pack(fill=X, pady=3)
    create_touch_button(scripts_frame, "🔄 Full Rebuild",
                       lambda: run_refresh_full(log_text), "Action.TButton").pack(fill=X, pady=3)
    create_touch_button(scripts_frame, "📝 Transcripts",
                       lambda: run_transcription_batch(log_text), "Action.TButton").pack(fill=X, pady=3)
    create_touch_button(scripts_frame, "🚀 Git Push",
                       lambda: run_git_push(log_text), "Action.TButton").pack(fill=X, pady=3)
    
    # Row 0: Folders & Maintenance
    misc_frame = ttk.LabelFrame(buttons_frame, text="Folders / Maint.", padding="8")
    misc_frame.grid(row=0, column=3, padx=(5, 0), pady=2, sticky="nsew")
    
    create_touch_button(misc_frame, "📁 EhkoForge",
                       lambda: open_folder(EHKOFORGE_ROOT, log_text)).pack(fill=X, pady=3)
    create_touch_button(misc_frame, "📁 Mirrorwell",
                       lambda: open_folder(MIRRORWELL_ROOT, log_text)).pack(fill=X, pady=3)
    create_touch_button(misc_frame, "🗑 Clear Backups",
                       lambda: clear_backups(log_text)).pack(fill=X, pady=3)
    create_touch_button(misc_frame, "📋 Clear Log",
                       lambda: clear_log(log_text)).pack(fill=X, pady=3)
    
    # Make columns expand evenly
    buttons_frame.columnconfigure(0, weight=1)
    buttons_frame.columnconfigure(1, weight=1)
    buttons_frame.columnconfigure(2, weight=1)
    buttons_frame.columnconfigure(3, weight=1)
    
    # Log output
    log_frame = ttk.LabelFrame(main_frame, text="Output Log", padding="8")
    log_frame.pack(fill=BOTH, expand=True, pady=(5, 0))
    
    log_text = scrolledtext.ScrolledText(
        log_frame, 
        height=12,
        bg="#0a0c10",
        fg="#e8e6e3",
        insertbackground="#e8e6e3",
        font=("Consolas", 10),
        state=DISABLED,
        wrap=WORD,
        relief=FLAT,
        borderwidth=0
    )
    log_text.pack(fill=BOTH, expand=True)
    
    # Configure log tags
    log_text.tag_config("info", foreground="#6b8cce")
    log_text.tag_config("success", foreground="#5fb3a1")
    log_text.tag_config("warning", foreground="#c9a962")
    log_text.tag_config("error", foreground="#d97373")
    
    # Command line input (optional)
    cmd_frame = ttk.Frame(main_frame)
    cmd_frame.pack(fill=X, pady=(8, 0))
    
    cmd_label = ttk.Label(cmd_frame, text=">", font=("Consolas", 12, "bold"), foreground="#5fb3a1")
    cmd_label.pack(side=LEFT, padx=(0, 5))
    
    cmd_entry = Entry(
        cmd_frame,
        bg="#14171d",
        fg="#e8e6e3",
        insertbackground="#e8e6e3",
        font=("Consolas", 11),
        relief=FLAT,
        borderwidth=0
    )
    cmd_entry.pack(side=LEFT, fill=X, expand=True, ipady=8)
    
    # Bind Enter key to run command
    cmd_entry.bind("<Return>", lambda e: run_custom_command(log_text, cmd_entry))
    
    run_btn = ttk.Button(cmd_frame, text="Run", width=6,
                        command=lambda: run_custom_command(log_text, cmd_entry))
    run_btn.pack(side=RIGHT, padx=(5, 0))
    
    # Initial log
    log(log_text, "EhkoForge Control Panel v2.0 ready", "info")
    log(log_text, f"Scripts: {SCRIPTS_PATH}", "info")
    log(log_text, "Tip: Type commands in the input field below", "info")
    
    # Handle window close
    def on_closing():
        global server_process
        if server_process and server_process.poll() is None:
            result = messagebox.askyesno(
                "Server Running",
                "The Forge server is still running.\n\nStop it before closing?"
            )
            if result:
                stop_server(log_text, status_label)
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    return root


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    app = create_gui()
    app.mainloop()

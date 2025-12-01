#!/usr/bin/env python3
"""
EhkoForge Control Panel v1.0
A simple GUI for managing EhkoForge operations.

Run: py ehko_control.py
"""

import os
import signal
import subprocess
import sys
import threading
import webbrowser
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
            # Windows: open in new PowerShell window
            cmd = f'cd "{SCRIPTS_PATH}" ; py forge_server.py'
            server_process = subprocess.Popen(
                ['powershell', '-NoExit', '-Command', cmd],
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
        else:
            # Unix: open in new terminal
            server_process = subprocess.Popen(
                ['x-terminal-emulator', '-e', f'cd "{SCRIPTS_PATH}" && python3 forge_server.py'],
            )
        
        status_label.config(text="● Server Running (Terminal)", foreground="#5fb3a1")
        log(text_widget, f"Server started in separate terminal window", "success")
        log(text_widget, f"  Access at: {SERVER_URL}", "info")
        log(text_widget, f"  Close the terminal window to stop the server", "info")
        
    except Exception as e:
        log(text_widget, f"Failed to start server: {str(e)}", "error")
        status_label.config(text="○ Server Stopped", foreground="#d97373")


def start_server(text_widget, status_label):
    """Start the Forge server."""
    global server_process
    
    if server_process and server_process.poll() is None:
        log(text_widget, "Server is already running", "warning")
        return
    
    try:
        log(text_widget, "Starting Forge server...", "info")
        
        # Start server process
        server_process = subprocess.Popen(
            [sys.executable, str(SERVER_SCRIPT)],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            cwd=str(SCRIPTS_PATH),
            text=True,
            bufsize=1,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
        )
        
        # Update status
        status_label.config(text="● Server Running", foreground="#5fb3a1")
        log(text_widget, f"✓ Server started (PID: {server_process.pid})", "success")
        log(text_widget, f"  Access at: {SERVER_URL}", "info")
        
        # Stream output in background
        def stream_output():
            for line in iter(server_process.stdout.readline, ''):
                if line and server_process.poll() is None:
                    log(text_widget, f"[server] {line.strip()}")
            
            # Server stopped
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
            # Windows: send CTRL_BREAK_EVENT
            server_process.send_signal(signal.CTRL_BREAK_EVENT)
        else:
            # Unix: send SIGTERM
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
# GUI
# =============================================================================

def create_gui():
    """Create the control panel GUI."""
    
    # Main window
    root = Tk()
    root.title("EhkoForge Control Panel")
    root.geometry("700x550")
    root.configure(bg="#14171d")
    root.resizable(True, True)
    
    # Style
    style = ttk.Style()
    style.theme_use('clam')
    
    # Configure colors
    style.configure("TFrame", background="#14171d")
    style.configure("TLabel", background="#14171d", foreground="#e8e6e3")
    style.configure("TLabelframe", background="#14171d", foreground="#e8e6e3")
    style.configure("TLabelframe.Label", background="#14171d", foreground="#9b7ed9")
    style.configure("TButton", 
                    background="#1a1e26", 
                    foreground="#e8e6e3",
                    borderwidth=1,
                    focuscolor="none",
                    padding=(10, 5))
    style.map("TButton",
              background=[("active", "#2a2e36"), ("pressed", "#0d0f13")],
              foreground=[("active", "#ffffff")])
    
    # Custom button styles
    style.configure("Server.TButton", background="#1a4a3a")
    style.map("Server.TButton", background=[("active", "#2a5a4a")])
    
    style.configure("Stop.TButton", background="#4a1a1a")
    style.map("Stop.TButton", background=[("active", "#5a2a2a")])
    
    style.configure("Action.TButton", background="#1a2a4a")
    style.map("Action.TButton", background=[("active", "#2a3a5a")])
    
    # Main container
    main_frame = ttk.Frame(root, padding="10")
    main_frame.pack(fill=BOTH, expand=True)
    
    # Header
    header_frame = ttk.Frame(main_frame)
    header_frame.pack(fill=X, pady=(0, 10))
    
    title_label = ttk.Label(header_frame, text="◈ EhkoForge Control Panel", 
                           font=("Segoe UI", 14, "bold"), foreground="#9b7ed9")
    title_label.pack(side=LEFT)
    
    status_label = ttk.Label(header_frame, text="○ Server Stopped", 
                            font=("Segoe UI", 10), foreground="#d97373")
    status_label.pack(side=RIGHT)
    
    # Button panels
    buttons_frame = ttk.Frame(main_frame)
    buttons_frame.pack(fill=X, pady=(0, 10))
    
    # Server controls
    server_frame = ttk.LabelFrame(buttons_frame, text="Server", padding="5")
    server_frame.pack(side=LEFT, fill=Y, padx=(0, 5))
    
    # Scripts
    scripts_frame = ttk.LabelFrame(buttons_frame, text="Scripts", padding="5")
    scripts_frame.pack(side=LEFT, fill=Y, padx=5)
    
    # Folders
    folders_frame = ttk.LabelFrame(buttons_frame, text="Folders", padding="5")
    folders_frame.pack(side=LEFT, fill=Y, padx=5)
    
    # Maintenance
    maint_frame = ttk.LabelFrame(buttons_frame, text="Maintenance", padding="5")
    maint_frame.pack(side=LEFT, fill=Y, padx=(5, 0))
    
    # Log output
    log_frame = ttk.LabelFrame(main_frame, text="Output Log", padding="5")
    log_frame.pack(fill=BOTH, expand=True)
    
    log_text = scrolledtext.ScrolledText(
        log_frame, 
        height=15,
        bg="#0d0f13",
        fg="#e8e6e3",
        insertbackground="#e8e6e3",
        font=("Consolas", 9),
        state=DISABLED,
        wrap=WORD
    )
    log_text.pack(fill=BOTH, expand=True)
    
    # Configure log tags
    log_text.tag_config("info", foreground="#6b8cce")
    log_text.tag_config("success", foreground="#5fb3a1")
    log_text.tag_config("warning", foreground="#c9a962")
    log_text.tag_config("error", foreground="#d97373")
    
    # Server buttons
    ttk.Button(server_frame, text="▶ Start Server", style="Server.TButton",
               command=lambda: start_server(log_text, status_label)).pack(fill=X, pady=2)
    
    ttk.Button(server_frame, text="▶ Start in Terminal", style="Server.TButton",
               command=lambda: start_server_terminal(log_text, status_label)).pack(fill=X, pady=2)
    
    ttk.Button(server_frame, text="■ Stop Server", style="Stop.TButton",
               command=lambda: stop_server(log_text, status_label)).pack(fill=X, pady=2)
    
    ttk.Button(server_frame, text="🌐 Open UI",
               command=lambda: open_forge_ui(log_text)).pack(fill=X, pady=2)
    
    # Script buttons
    ttk.Button(scripts_frame, text="🔄 Refresh Index", style="Action.TButton",
               command=lambda: run_refresh(log_text)).pack(fill=X, pady=2)
    
    ttk.Button(scripts_frame, text="🔄 Full Rebuild", style="Action.TButton",
               command=lambda: run_refresh_full(log_text)).pack(fill=X, pady=2)
    
    ttk.Button(scripts_frame, text="📝 Process Transcripts", style="Action.TButton",
               command=lambda: run_transcription_batch(log_text)).pack(fill=X, pady=2)
    
    # Folder buttons
    ttk.Button(folders_frame, text="📁 EhkoForge",
               command=lambda: open_folder(EHKOFORGE_ROOT, log_text)).pack(fill=X, pady=2)
    
    ttk.Button(folders_frame, text="📁 Mirrorwell",
               command=lambda: open_folder(MIRRORWELL_ROOT, log_text)).pack(fill=X, pady=2)
    
    ttk.Button(folders_frame, text="📁 Scripts",
               command=lambda: open_folder(SCRIPTS_PATH, log_text)).pack(fill=X, pady=2)
    
    # Maintenance buttons
    ttk.Button(maint_frame, text="🗑 Clear Backups",
               command=lambda: clear_backups(log_text)).pack(fill=X, pady=2)
    
    ttk.Button(maint_frame, text="📋 Clear Log",
               command=lambda: clear_log(log_text)).pack(fill=X, pady=2)
    
    # Initial log message
    log(log_text, "EhkoForge Control Panel ready", "info")
    log(log_text, f"EhkoForge: {EHKOFORGE_ROOT}", "info")
    log(log_text, f"Mirrorwell: {MIRRORWELL_ROOT}", "info")
    
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

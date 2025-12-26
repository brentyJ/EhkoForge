#!/usr/bin/env python3
"""
EhkoForge Control Panel Server v1.0
Lightweight Flask server for web-based control panel.
Port: 5001

Manages:
- EhkoForge server (port 5000)
- ReCog server (port 5100)
- Website dev server (port 4321)
- Vault operations (refresh, git)
- GlyphWorks operations
"""

import os
import sys
import json
import signal
import subprocess
import threading
import time
from pathlib import Path
from datetime import datetime
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

# =============================================================================
# CONFIGURATION
# =============================================================================

EHKOFORGE_ROOT = Path("G:/Other computers/Ehko/Obsidian/EhkoForge")
MIRRORWELL_ROOT = Path("G:/Other computers/Ehko/Obsidian/Mirrorwell")
RECOG_ROOT = Path("G:/Other computers/Ehko/Obsidian/ReCog")
WEBSITE_PATH = Path("C:/ehkolabs-website")

SCRIPTS_PATH = EHKOFORGE_ROOT / "5.0 Scripts"
RECOG_SCRIPTS = RECOG_ROOT / "_scripts"

# Server scripts
FORGE_SERVER = SCRIPTS_PATH / "forge_server.py"
RECOG_SERVER = RECOG_SCRIPTS / "server.py"

# Automation scripts
REFRESH_SCRIPT = SCRIPTS_PATH / "ehko_refresh.py"

# Process management
processes = {
    'forge': None,
    'recog': None,
    'website': None
}

# Logs storage (last 100 lines per process)
logs = {
    'forge': [],
    'recog': [],
    'website': [],
    'system': []
}

MAX_LOG_LINES = 100

# =============================================================================
# FLASK APP
# =============================================================================

app = Flask(__name__, static_folder='control_panel/dist', static_url_path='')
CORS(app)

def log_message(category, message):
    """Add timestamped message to logs."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    entry = f"[{timestamp}] {message}"
    
    if category not in logs:
        logs[category] = []
    
    logs[category].append(entry)
    
    # Keep only last MAX_LOG_LINES
    if len(logs[category]) > MAX_LOG_LINES:
        logs[category] = logs[category][-MAX_LOG_LINES:]
    
    print(entry)  # Also print to console

# =============================================================================
# PROCESS MANAGEMENT
# =============================================================================

def is_port_in_use(port):
    """Check if a port is in use."""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def start_server(name, script, port, cwd=None):
    """Start a server process."""
    if processes[name] and processes[name].poll() is None:
        log_message(name, f"{name.title()} already running")
        return False
    
    try:
        log_message(name, f"Starting {name.title()} server on port {port}...")
        
        process = subprocess.Popen(
            [sys.executable, str(script)],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            cwd=cwd,
            text=True,
            bufsize=1
        )
        
        processes[name] = process
        
        # Start log streaming thread
        threading.Thread(target=stream_logs, args=(name, process), daemon=True).start()
        
        # Wait a moment to check if it started
        time.sleep(2)
        
        if process.poll() is None:
            log_message(name, f"{name.title()} server started successfully")
            return True
        else:
            log_message(name, f"{name.title()} server failed to start")
            return False
            
    except Exception as e:
        log_message(name, f"Error starting {name}: {str(e)}")
        return False

def stop_server(name):
    """Stop a server process."""
    if not processes[name] or processes[name].poll() is not None:
        log_message(name, f"{name.title()} not running")
        return False
    
    try:
        log_message(name, f"Stopping {name.title()} server...")
        
        if sys.platform == 'win32':
            processes[name].send_signal(signal.CTRL_C_EVENT)
        else:
            processes[name].terminate()
        
        processes[name].wait(timeout=5)
        processes[name] = None
        
        log_message(name, f"{name.title()} server stopped")
        return True
        
    except subprocess.TimeoutExpired:
        log_message(name, f"Force killing {name}...")
        processes[name].kill()
        processes[name] = None
        return True
    except Exception as e:
        log_message(name, f"Error stopping {name}: {str(e)}")
        return False

def stream_logs(name, process):
    """Stream process output to logs."""
    try:
        for line in iter(process.stdout.readline, ''):
            if line:
                log_message(name, line.strip())
    except Exception as e:
        log_message(name, f"Log streaming error: {str(e)}")

def get_server_status(name, port):
    """Get server status."""
    process = processes.get(name)
    
    if process and process.poll() is None:
        return {
            'running': True,
            'port': port,
            'pid': process.pid,
            'status': 'active'
        }
    else:
        # Check if port is in use (might be external process)
        if is_port_in_use(port):
            return {
                'running': True,
                'port': port,
                'pid': None,
                'status': 'external'
            }
        else:
            return {
                'running': False,
                'port': port,
                'pid': None,
                'status': 'stopped'
            }

# =============================================================================
# API ROUTES
# =============================================================================

@app.route('/')
def index():
    """Serve React app."""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/status')
def api_status():
    """Get status of all servers."""
    return jsonify({
        'forge': get_server_status('forge', 5000),
        'recog': get_server_status('recog', 5100),
        'website': get_server_status('website', 4321),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/logs/<category>')
def api_logs(category):
    """Get logs for a category."""
    if category not in logs:
        return jsonify({'error': 'Invalid category'}), 400
    
    return jsonify({
        'category': category,
        'logs': logs[category],
        'count': len(logs[category])
    })

@app.route('/api/server/<name>/start', methods=['POST'])
def api_server_start(name):
    """Start a server."""
    servers = {
        'forge': (FORGE_SERVER, 5000, SCRIPTS_PATH),
        'recog': (RECOG_SERVER, 5100, RECOG_SCRIPTS),
        'website': (WEBSITE_PATH / 'package.json', 4321, WEBSITE_PATH)
    }
    
    if name not in servers:
        return jsonify({'error': 'Invalid server name'}), 400
    
    script, port, cwd = servers[name]
    
    # Special handling for website (npm command)
    if name == 'website':
        try:
            log_message('website', "Starting Astro dev server...")
            process = subprocess.Popen(
                ['npm', 'run', 'dev'],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                cwd=cwd,
                text=True,
                bufsize=1
            )
            processes['website'] = process
            threading.Thread(target=stream_logs, args=('website', process), daemon=True).start()
            success = True
        except Exception as e:
            log_message('website', f"Error: {str(e)}")
            success = False
    else:
        success = start_server(name, script, port, cwd)
    
    return jsonify({
        'success': success,
        'server': name,
        'status': get_server_status(name, port)
    })

@app.route('/api/server/<name>/stop', methods=['POST'])
def api_server_stop(name):
    """Stop a server."""
    if name not in ['forge', 'recog', 'website']:
        return jsonify({'error': 'Invalid server name'}), 400
    
    success = stop_server(name)
    
    port = {'forge': 5000, 'recog': 5100, 'website': 4321}[name]
    
    return jsonify({
        'success': success,
        'server': name,
        'status': get_server_status(name, port)
    })

@app.route('/api/refresh', methods=['POST'])
def api_refresh():
    """Run vault refresh."""
    data = request.json or {}
    vault = data.get('vault', 'all')
    
    log_message('system', f"Running vault refresh ({vault})...")
    
    try:
        cmd = [sys.executable, str(REFRESH_SCRIPT)]
        if vault != 'all':
            cmd.extend(['--vault', vault])
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300
        )
        
        # Log output
        for line in result.stdout.split('\n'):
            if line.strip():
                log_message('system', line.strip())
        
        success = result.returncode == 0
        
        if success:
            log_message('system', "Vault refresh completed")
        else:
            log_message('system', f"Vault refresh failed: {result.stderr}")
        
        return jsonify({
            'success': success,
            'returncode': result.returncode,
            'output': result.stdout
        })
        
    except Exception as e:
        log_message('system', f"Refresh error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/git/<operation>', methods=['POST'])
def api_git(operation):
    """Run git operations."""
    data = request.json or {}
    project = data.get('project', 'ehkoforge')
    
    if operation not in ['commit', 'push', 'pull', 'status']:
        return jsonify({'error': 'Invalid operation'}), 400
    
    log_message('system', f"Git {operation} ({project})...")
    
    # Map projects to paths
    paths = {
        'ehkoforge': EHKOFORGE_ROOT,
        'recog': RECOG_ROOT,
        'website': WEBSITE_PATH
    }
    
    if project not in paths:
        return jsonify({'error': 'Invalid project'}), 400
    
    cwd = paths[project]
    
    try:
        if operation == 'commit':
            message = data.get('message', f'Update from control panel - {datetime.now().strftime("%Y-%m-%d %H:%M")}')
            cmd = ['git', 'add', '.']
            subprocess.run(cmd, cwd=cwd, check=True)
            cmd = ['git', 'commit', '-m', message]
        elif operation == 'push':
            cmd = ['git', 'push']
        elif operation == 'pull':
            cmd = ['git', 'pull']
        elif operation == 'status':
            cmd = ['git', 'status', '--short']
        
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        # Log output
        for line in result.stdout.split('\n'):
            if line.strip():
                log_message('system', line.strip())
        
        return jsonify({
            'success': result.returncode == 0,
            'output': result.stdout,
            'error': result.stderr
        })
        
    except Exception as e:
        log_message('system', f"Git error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# =============================================================================
# MAIN
# =============================================================================

if __name__ == '__main__':
    log_message('system', "=" * 60)
    log_message('system', "EhkoForge Control Panel Server v1.0")
    log_message('system', "=" * 60)
    log_message('system', "Starting on http://localhost:5001")
    log_message('system', "")
    
    try:
        app.run(host='0.0.0.0', port=5001, debug=True, use_reloader=False)
    except KeyboardInterrupt:
        log_message('system', "\nShutting down...")
        # Stop all managed processes
        for name in ['forge', 'recog', 'website']:
            if processes[name]:
                stop_server(name)
        log_message('system', "Control panel stopped")

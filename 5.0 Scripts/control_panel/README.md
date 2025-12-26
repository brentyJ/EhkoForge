# EhkoForge Web Control Panel

Web-based control panel for managing EhkoForge servers and operations.

## Setup (First Time Only)

1. **Install dependencies:**
   ```bash
   cd "G:\Other computers\Ehko\Obsidian\EhkoForge\5.0 Scripts\control_panel"
   npm install
   ```

2. **Install flask-cors for the server:**
   ```bash
   pip install flask-cors
   ```

## Running the Control Panel

### Option 1: Development Mode (Recommended for testing)

**Terminal 1 - Backend Server:**
```bash
cd "G:\Other computers\Ehko\Obsidian\EhkoForge\5.0 Scripts"
python control_server.py
```

**Terminal 2 - Frontend Dev Server:**
```bash
cd "G:\Other computers\Ehko\Obsidian\EhkoForge\5.0 Scripts\control_panel"
npm run dev
```

Then open: **http://localhost:3000**

### Option 2: Production Mode

1. **Build the frontend:**
   ```bash
   cd "G:\Other computers\Ehko\Obsidian\EhkoForge\5.0 Scripts\control_panel"
   npm run build
   ```

2. **Run the backend (serves built frontend):**
   ```bash
   cd "G:\Other computers\Ehko\Obsidian\EhkoForge\5.0 Scripts"
   python control_server.py
   ```

Then open: **http://localhost:5001**

## What It Does

- **Server Management:** Start/stop EhkoForge, ReCog, and Website servers
- **Status Monitoring:** Real-time server status with auto-refresh
- **Quick Actions:** Vault refresh, git operations
- **shadcn/ui Demo:** Shows professional UI components with EhkoForge terminal theme

## Features

✅ Real-time server status (3-second polling)
✅ Start/stop servers with one click
✅ Open server URLs in browser
✅ Terminal blue theme matching EhkoForge aesthetic
✅ Responsive design
✅ shadcn/ui components (currently using base Tailwind, will add shadcn/ui components next)

## Next Steps

1. Test the basic functionality
2. Add shadcn/ui components (Button, Card, Badge, etc.)
3. Add live log viewer
4. Add git operations UI
5. Add GlyphWorks integration

## File Structure

```
control_panel/
├── src/
│   ├── App.jsx           - Main application
│   ├── main.jsx          - React entry point
│   └── index.css         - Tailwind + EhkoForge theme
├── index.html            - HTML template
├── package.json          - Dependencies
├── tailwind.config.js    - Theme configuration
└── vite.config.js        - Build configuration

../control_server.py      - Flask backend (port 5001)
```

## API Endpoints

- `GET /api/status` - Get all server statuses
- `GET /api/logs/<category>` - Get logs for a server
- `POST /api/server/<n>/start` - Start a server (forge/recog/website)
- `POST /api/server/<n>/stop` - Stop a server
- `POST /api/refresh` - Run vault refresh
- `POST /api/git/<operation>` - Git operations (commit/push/pull/status)

## Troubleshooting

**"Module not found" errors:**
- Run `npm install` in the control_panel directory

**Backend errors:**
- Make sure flask-cors is installed: `pip install flask-cors`
- Check that ports 5001 and 3000 are available

**Servers won't start:**
- Check if they're already running on those ports
- Check the logs in the control panel

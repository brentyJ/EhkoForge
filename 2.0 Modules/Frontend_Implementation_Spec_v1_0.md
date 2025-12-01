---
title: "EhkoForge Frontend Implementation Specification"
vault: "EhkoForge"
type: "module"
category: "Interface Design"
status: active
version: "1.0"
created: 2025-11-28
updated: 2025-11-28
tags: [ehkoforge, frontend, flask, implementation, api]
related: ["UI-MDV-Specification", "Data Model", "ehko_refresh.py"]
source: "Claude Stackwright"
confidence: 0.95
revealed: true
---

# EHKOFORGE FRONTEND IMPLEMENTATION SPECIFICATION v1.0

## 1. Overview

This document specifies the technical implementation of the EhkoForge MDV (Minimum Delightful Version) frontend using **Flask + Vanilla HTML/CSS/JS**.

**Stack:**
- Backend: Python 3.10+, Flask 3.x
- Database: SQLite (existing `ehko_index.db` + new session tables)
- Frontend: Vanilla HTML5, CSS3, JavaScript (ES6+)
- No build tools, no npm, no frameworks

**File Structure:**
```
EhkoForge/
├── 5.0 Scripts/
│   └── forge_server.py          # Flask application
├── 6.0 Frontend/
│   ├── static/
│   │   ├── index.html           # Main UI
│   │   ├── styles.css           # MDV styling
│   │   └── app.js               # Frontend logic
│   └── assets/
│       └── avatar-placeholder.svg
├── _data/
│   └── ehko_index.db            # Extended with session tables
└── Config/
    └── ui-preferences.json      # User settings
```

---

## 2. Database Schema Extensions

Add to existing `ehko_index.db`:

```sql
-- Forge UI Sessions
CREATE TABLE IF NOT EXISTS forge_sessions (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    session_tags TEXT,              -- JSON array: ["identity", "memory"]
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    message_count INTEGER DEFAULT 0,
    is_archived INTEGER DEFAULT 0
);

-- Session Messages
CREATE TABLE IF NOT EXISTS forge_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    role TEXT NOT NULL,             -- 'user' or 'ehko'
    content TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    forged INTEGER DEFAULT 0,       -- 1 if saved to vault
    forged_path TEXT,               -- Path to reflection if forged
    FOREIGN KEY (session_id) REFERENCES forge_sessions(id)
);

-- Index for fast session message retrieval
CREATE INDEX IF NOT EXISTS idx_messages_session 
ON forge_messages(session_id, timestamp);
```

---

## 3. API Endpoints

Base URL: `http://localhost:5000`

### Sessions

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/sessions` | List all sessions (newest first) |
| POST | `/api/sessions` | Create new session |
| GET | `/api/sessions/<id>` | Get session details |
| DELETE | `/api/sessions/<id>` | Archive session |

**GET /api/sessions Response:**
```json
{
  "sessions": [
    {
      "id": "session-2025-11-28-001",
      "title": "Evening Reflection",
      "session_tags": ["identity", "memory"],
      "created_at": "2025-11-28T19:30:00",
      "updated_at": "2025-11-28T20:15:00",
      "message_count": 12
    }
  ]
}
```

**POST /api/sessions Request:**
```json
{
  "title": "New Session"
}
```

### Messages

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/sessions/<id>/messages` | Get all messages in session |
| POST | `/api/sessions/<id>/messages` | Add message to session |

**GET /api/sessions/<id>/messages Response:**
```json
{
  "session_id": "session-2025-11-28-001",
  "messages": [
    {
      "id": 1,
      "role": "user",
      "content": "I've been thinking about...",
      "timestamp": "2025-11-28T19:30:15",
      "forged": false
    },
    {
      "id": 2,
      "role": "ehko",
      "content": "That connects to what you shared about...",
      "timestamp": "2025-11-28T19:30:45",
      "forged": false
    }
  ]
}
```

**POST /api/sessions/<id>/messages Request:**
```json
{
  "role": "user",
  "content": "Message content here"
}
```

### Forge (Save to Vault)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/forge` | Save message(s) as Mirrorwell reflection |

**POST /api/forge Request:**
```json
{
  "session_id": "session-2025-11-28-001",
  "message_ids": [1, 2, 3],
  "title": "Evening Thoughts on Identity",
  "tags": ["identity", "reflection"],
  "emotional_tags": ["contemplative", "hopeful"]
}
```

**POST /api/forge Response:**
```json
{
  "success": true,
  "reflection_path": "Mirrorwell/2_Reflection Library/2.1 Journals/2025-11-28_evening-thoughts-identity.md",
  "forged_count": 3
}
```

### Stats

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/stats` | Get symbolic stats for ribbon |

**GET /api/stats Response:**
```json
{
  "identity_depth": 0.45,
  "clarity": 0.62,
  "resonance": 0.38,
  "anchors": 0.71
}
```

Stats are derived from:
- `identity_depth`: Count of identity-tagged reflections / total reflections
- `clarity`: Percentage of reflections with all required fields populated
- `resonance`: Average confidence score across reflections
- `anchors`: Count of core_memory=true / total reflections

### Config

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/config` | Get UI preferences |
| POST | `/api/config` | Update UI preferences |

**GET /api/config Response:**
```json
{
  "theme": "forge-dark",
  "avatar_visible": true,
  "low_motion_mode": false,
  "high_contrast_mode": false
}
```

### Reflections (Read-Only Query)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/reflections` | Query indexed reflections |
| GET | `/api/reflections/<id>` | Get single reflection |

**GET /api/reflections Query Params:**
- `?tag=identity` — Filter by tag
- `?core_memory=true` — Only core memories
- `?limit=10` — Limit results
- `?search=family` — Full-text search (title + tags)

---

## 4. Frontend Components

### Layout Structure (index.html)

```
┌─────────────────────────────────────────────────────────┐
│ ┌─────────────┐ ┌─────────────────────────────────────┐ │
│ │             │ │           STATS RIBBON              │ │
│ │   SIDEBAR   │ ├─────────────────────────────────────┤ │
│ │             │ │                                     │ │
│ │  Sessions   │ │           AVATAR ZONE               │ │
│ │    List     │ │                                     │ │
│ │             │ ├─────────────────────────────────────┤ │
│ │             │ │                                     │ │
│ │             │ │           CHAT AREA                 │ │
│ │             │ │                                     │ │
│ │             │ │                                     │ │
│ │             │ ├─────────────────────────────────────┤ │
│ │ [+] New     │ │           INPUT BAR                 │ │
│ └─────────────┘ └─────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### CSS Classes (styles.css)

**Layout:**
- `.app-container` — Flexbox root
- `.sidebar` — Left panel, fixed width 280px
- `.main-panel` — Flex-grow right panel
- `.stats-ribbon` — Horizontal stat icons
- `.avatar-zone` — Centered avatar container
- `.chat-area` — Scrollable message list
- `.input-bar` — Fixed bottom input

**Components:**
- `.session-item` — Sidebar session entry
- `.session-tag` — Glowing tag pill
- `.message` — Chat message container
- `.message--user` — User message variant
- `.message--ehko` — Ehko message variant (glow)
- `.stat-icon` — Individual stat in ribbon
- `.avatar` — Ehko avatar element
- `.forge-btn` — Forge-to-vault button

**States:**
- `.is-active` — Selected session
- `.is-forged` — Message saved to vault
- `.is-thinking` — Ehko processing state
- `.is-pulsing` — Stat update animation

### JavaScript Modules (app.js)

```javascript
// State
const state = {
  currentSessionId: null,
  sessions: [],
  messages: [],
  stats: {},
  config: {}
};

// API Functions
async function fetchSessions() { ... }
async function createSession(title) { ... }
async function fetchMessages(sessionId) { ... }
async function sendMessage(sessionId, content) { ... }
async function forgeMessages(sessionId, messageIds, metadata) { ... }
async function fetchStats() { ... }
async function fetchConfig() { ... }
async function updateConfig(settings) { ... }

// UI Functions
function renderSidebar() { ... }
function renderMessages() { ... }
function renderStats() { ... }
function scrollToBottom() { ... }
function showThinkingIndicator() { ... }
function hideThinkingIndicator() { ... }
function animateForge(messageId) { ... }

// Event Handlers
function handleSessionClick(sessionId) { ... }
function handleNewSession() { ... }
function handleSendMessage() { ... }
function handleForgeClick(messageId) { ... }

// Initialisation
async function init() {
  await fetchConfig();
  await fetchSessions();
  await fetchStats();
  if (state.sessions.length > 0) {
    await handleSessionClick(state.sessions[0].id);
  }
  setupEventListeners();
}

document.addEventListener('DOMContentLoaded', init);
```

---

## 5. Ehko Response Generation (MVP)

For MDV, Ehko responses are **templated placeholders**, not AI-generated.

**Response Types:**
1. **Acknowledgement:** "I've noted that reflection."
2. **Prompt:** "Would you like to explore that further?"
3. **Connection:** "This seems to connect with themes of [tag]."
4. **Encouragement:** "Thank you for sharing. Take your time."

**Future Integration Point:**
Replace `generate_ehko_response()` in `forge_server.py` with actual LLM API call (Claude, GPT, local model).

```python
def generate_ehko_response(user_message: str, session_context: list) -> str:
    """
    MVP: Return templated response
    Future: Call LLM API with context
    """
    # MVP implementation
    prompts = [
        "I've noted that. What else is on your mind?",
        "That's worth sitting with. Would you like to explore it further?",
        "Thank you for sharing. I'm here when you're ready to continue.",
    ]
    return random.choice(prompts)
```

---

## 6. File Paths & Configuration

**Vault Paths (Windows):**
```python
EHKOFORGE_ROOT = Path("G:/Other computers/Ehko/Obsidian/EhkoForge")
MIRRORWELL_ROOT = Path("G:/Other computers/Ehko/Obsidian/Mirrorwell")
DATABASE_PATH = EHKOFORGE_ROOT / "_data" / "ehko_index.db"
CONFIG_PATH = EHKOFORGE_ROOT / "Config" / "ui-preferences.json"
STATIC_PATH = EHKOFORGE_ROOT / "6.0 Frontend" / "static"
```

**Default Config (ui-preferences.json):**
```json
{
  "theme": "forge-dark",
  "avatar_visible": true,
  "low_motion_mode": false,
  "high_contrast_mode": false,
  "reduced_chroma_mode": false,
  "dyslexic_font": false,
  "last_session_id": null
}
```

---

## 7. Colour Palette (CSS Variables)

```css
:root {
  /* Base */
  --bg-primary: #0d0f13;
  --bg-secondary: #14171d;
  --bg-tertiary: #1a1e26;
  
  /* Text */
  --text-primary: #e8e6e3;
  --text-secondary: #9ca3af;
  --text-muted: #6b7280;
  
  /* Accents */
  --accent-blue: #6b8cce;
  --accent-violet: #9b7ed9;
  --accent-gold: #c9a962;
  --accent-teal: #5fb3a1;
  
  /* Glows */
  --glow-blue: rgba(107, 140, 206, 0.3);
  --glow-violet: rgba(155, 126, 217, 0.3);
  --glow-gold: rgba(201, 169, 98, 0.2);
  
  /* UI Elements */
  --border-subtle: rgba(255, 255, 255, 0.08);
  --shadow-soft: 0 4px 20px rgba(0, 0, 0, 0.4);
  
  /* Semantic */
  --success: #5fb3a1;
  --warning: #c9a962;
  --error: #d97373;
}
```

---

## 8. Running the Server

**Install Dependencies:**
```bash
pip install flask --break-system-packages
```

**Start Server:**
```bash
cd "G:\Other computers\Ehko\Obsidian\EhkoForge\5.0 Scripts"
python forge_server.py
```

**Access UI:**
```
http://localhost:5000
```

---

## 9. Security Notes (Local Use)

- Server binds to `127.0.0.1` only (not exposed to network)
- No authentication for MDV (single-user local app)
- CORS disabled (same-origin only)
- File writes restricted to Mirrorwell vault path

**Future consideration:** Add API key or session token if deploying to network.

---

## 10. Testing Checklist

- [ ] Server starts without errors
- [ ] `/api/sessions` returns empty list initially
- [ ] Creating session via POST works
- [ ] Session appears in sidebar
- [ ] Sending message adds to chat
- [ ] Ehko response appears after user message
- [ ] Forge button saves to Mirrorwell vault
- [ ] Stats ribbon displays (placeholder values OK)
- [ ] Theme toggle works
- [ ] Low motion mode disables animations

---

**Changelog**
- v1.0 — 2025-11-28 — Initial implementation specification

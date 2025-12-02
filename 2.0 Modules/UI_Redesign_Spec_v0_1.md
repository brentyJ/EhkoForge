---
title: "UI Redesign Specification v0.1"
vault: EhkoForge
type: specification
category: Frontend
status: draft
version: "0.1"
created: 2025-12-02
updated: 2025-12-02
tags: [ehkoforge, frontend, ui, specification]
related:
  - "[[Forge_UI_Update_Spec_v0_1]]"
  - "[[UI-MDV-Specification]]"
  - "[[Frontend_Implementation_Spec_v1_0]]"
---

# UI REDESIGN SPECIFICATION v0.1

## 1. Overview

### 1.1 Purpose

This specification defines a restructured UI that separates the EhkoForge interface into three distinct areas with independent aesthetics and purposes:

| Area | Route | Purpose | Aesthetic |
|------|-------|---------|-----------|
| **Reflections** | `/reflect` | Personal insight capture | Serene, aqua/teal tones |
| **Forge** | `/forge` | Ingot review, smelting | Current MDV (gold/violet) |
| **Terminal** | `/terminal` | General AI assistant | Retro PC, dark blue/grey |

### 1.2 Motivation

The current proof-of-concept UI blends all functionality into a single interface. This redesign:

1. **Separates concerns** — Reflection work should feel contemplative; AI chat should feel utilitarian
2. **Reduces cognitive load** — Each area has a clear purpose
3. **Enables distinct moods** — Aesthetic changes reinforce functional context
4. **Supports future expansion** — Each area can evolve independently

### 1.3 Navigation Architecture

**Route-Based Navigation** with distinct pages:

```
/                 → Redirect to /reflect
/reflect          → Reflections area (default: Chat sub-mode)
/reflect/chat     → Reflection Chat
/reflect/journal  → Journal Mode
/reflect/upload   → Upload Ore
/forge            → Forge area (Ingot queue + review)
/terminal         → Terminal area (General AI chat)
```

Each area has **distinct chrome** (sidebar style, header, accents) but shares a common navigation bar for area switching.

---

## 2. Global Architecture

### 2.1 Shared Navigation Bar

A persistent top bar across all areas:

```
┌──────────────────────────────────────────────────────────────────┐
│ ◈ EhkoForge    [Reflect ▼] [Forge] [Terminal]    ◇ Forming  ⚙   │
└──────────────────────────────────────────────────────────────────┘
```

**Components:**
- **Logo** — Always visible, links to `/reflect`
- **Area Tabs** — Reflect (with sub-dropdown), Forge, Terminal
- **Ehko State** — Current state indicator (nascent/forming/emerging/present)
- **Settings** — Global settings cog

**Behaviour:**
- Current area tab is highlighted with area-specific accent colour
- Reflect tab shows dropdown on hover: Chat, Journal, Upload
- Forge tab shows badge with pending ingot count
- Terminal tab shows current model indicator

### 2.2 Page Layout Template

Each area follows this structure:

```
┌─────────────────────────────────────────────────────────────────┐
│                        NAVIGATION BAR                           │
├─────────────────┬───────────────────────────────────────────────┤
│                 │                                               │
│    SIDEBAR      │              MAIN CONTENT                     │
│  (area-specific)│           (area-specific)                     │
│                 │                                               │
│                 │                                               │
│                 │                                               │
│                 │                                               │
│                 │                                               │
│                 ├───────────────────────────────────────────────┤
│                 │              INPUT BAR                        │
│                 │           (if applicable)                     │
└─────────────────┴───────────────────────────────────────────────┘
```

**Sidebar Width:** 280px (consistent across areas)
**Main Content:** Flexible, fills remaining space
**Input Bar:** Present in Chat/Terminal, absent in Journal/Upload/Forge

### 2.3 Colour Palettes

#### 2.3.1 Reflections Palette (Serene/Aqua)

```css
:root[data-area="reflect"] {
    --accent-primary: #5fb3a1;    /* Teal */
    --accent-secondary: #7bc4b5;  /* Light teal */
    --accent-glow: rgba(95, 179, 161, 0.4);
    --bg-primary: #0a1214;        /* Deep blue-grey */
    --bg-secondary: #0f1a1d;
    --bg-tertiary: #152226;
    --bg-elevated: #1a2a2f;
    --border-focus: rgba(95, 179, 161, 0.5);
}
```

#### 2.3.2 Forge Palette (Current MDV)

```css
:root[data-area="forge"] {
    --accent-primary: #c9a962;    /* Gold */
    --accent-secondary: #9b7ed9;  /* Violet */
    --accent-glow: rgba(201, 169, 98, 0.4);
    --bg-primary: #0d0f13;
    --bg-secondary: #14171d;
    --bg-tertiary: #1a1e26;
    --bg-elevated: #1f242d;
    --border-focus: rgba(201, 169, 98, 0.5);
}
```

#### 2.3.3 Terminal Palette (Retro PC)

```css
:root[data-area="terminal"] {
    --accent-primary: #6b8cce;    /* Blue */
    --accent-secondary: #4a6fa5;  /* Darker blue */
    --accent-glow: rgba(107, 140, 206, 0.3);
    --bg-primary: #0a0c10;        /* Near black */
    --bg-secondary: #10131a;
    --bg-tertiary: #161a24;
    --bg-elevated: #1c2230;
    --border-focus: rgba(107, 140, 206, 0.5);
    
    /* Terminal-specific */
    --terminal-scanline: rgba(107, 140, 206, 0.03);
    --terminal-glow: 0 0 10px rgba(107, 140, 206, 0.2);
}
```

---

## 3. Reflections Area (`/reflect`)

### 3.1 Purpose

The Reflections area is where the forger captures insights through conversational exploration, traditional journalling, or bulk upload. The Ehko assists in reflection mode, prompting and mirroring to surface patterns.

**Aesthetic Goal:** Calm, contemplative, non-intrusive. The interface should feel like a quiet space for thought.

### 3.2 Sub-Modes

| Sub-Mode | Route | Purpose |
|----------|-------|---------|
| Chat | `/reflect/chat` | Conversational insight capture with Ehko |
| Journal | `/reflect/journal` | Traditional dated entries with calendar |
| Upload | `/reflect/upload` | Bulk upload of ore for smelting |

### 3.3 Reflections Sidebar

```
┌─────────────────────┐
│ ◎ Reflection Chat   │  ← Sub-mode tabs (vertical)
│ ☰ Journal           │
│ ↑ Upload            │
├─────────────────────┤
│ SESSIONS            │  ← Context-dependent
│ ┌─────────────────┐ │
│ │ Recent chat...  │ │
│ │ Yesterday...    │ │
│ └─────────────────┘ │
│                     │
│ [+ New Session]     │
├─────────────────────┤
│ ─────────────────── │
│ Ehko: Forming ◇     │
└─────────────────────┘
```

**Sub-Mode Tabs:**
- Vertical tab group at top of sidebar
- Active tab highlighted with teal accent
- Icons: ◎ (Chat), ☰ (Journal), ↑ (Upload)

**Context Panel:**
- **Chat mode:** Session list (same as current)
- **Journal mode:** Calendar navigator + recent entries
- **Upload mode:** Queue status + recent uploads

### 3.4 Reflection Chat (`/reflect/chat`)

Functionally equivalent to current Chat mode, but with serene aesthetic.

**Main Content:**
```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│     ◎                                                          │
│    ╭─╮     Ready                                               │
│    ╰─╯                                                          │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│                    [Message bubbles]                            │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ You: I've been thinking about how I handle conflict...   │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Ehko: That's an interesting pattern. You mentioned       │  │
│  │ something similar last month when discussing...          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│ │ Share your thoughts...                              [Send] │  │
│ └────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

**Changes from current:**
- Avatar present but simplified (smaller, no rotating rings, just core glow)
- Stats ribbon compact, positioned below avatar
- Message bubbles softer, less "tech" styling
- Input bar glow uses teal instead of blue

**Ehko Presence:**
The Ehko is present in all modes — it's who you're talking to, even in Terminal ("tech geek mode"). The avatar adapts its styling to match each area's palette but remains consistent in form.

**Forge-to-Vault:** Same as current, but uses teal accent for selection.

### 3.5 Journal Mode (`/reflect/journal`)

Traditional journalling with calendar navigation.

**Sidebar (Journal Context):**
```
┌─────────────────────┐
│      ◀ Dec 2025 ▶   │
├──┬──┬──┬──┬──┬──┬──┤
│Mo│Tu│We│Th│Fr│Sa│Su│
├──┼──┼──┼──┼──┼──┼──┤
│  │  │  │  │  │  │ 1│
│ 2│ 3│ 4│ 5│ 6│ 7│ 8│
│[9]│10│11│12│13│14│15│  ← [9] = selected/today
│16│17│18│19│20│21│22│
│23│24│25│26│27│28│29│
│30│31│  │  │  │  │  │
└──┴──┴──┴──┴──┴──┴──┘
│                     │
│ ENTRIES THIS MONTH  │
│ ┌─────────────────┐ │
│ │ Dec 2 - Session │ │
│ │ Dec 1 - Morning │ │
│ └─────────────────┘ │
└─────────────────────┘
```

**Calendar Features:**
- Dots on dates with entries
- Click date to view/create entry
- Month navigation arrows
- Current date highlighted

**Main Content (Viewing Entry):**
```
┌─────────────────────────────────────────────────────────────────┐
│  ◀ Monday, December 2, 2025                               [Edit]│
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ## Morning Reflection                                          │
│                                                                 │
│  Woke up thinking about the conversation with Dad yesterday.    │
│  There's something in the way he talked about his childhood     │
│  that I want to capture before I forget the details...          │
│                                                                 │
│  ---                                                            │
│                                                                 │
│  ### Tags                                                       │
│  family, memory, dad, childhood                                 │
│                                                                 │
│  ### Emotional State                                            │
│  contemplative, nostalgic                                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Main Content (Creating Entry):**
```
┌─────────────────────────────────────────────────────────────────┐
│  New Entry for Monday, December 2, 2025                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Title: [                                                    ]  │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                                                           │  │
│  │  [Markdown editor area]                                   │  │
│  │                                                           │  │
│  │                                                           │  │
│  │                                                           │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  Tags: [                                                     ]  │
│  Emotional: [                                                ]  │
│                                                                 │
│  ☐ Original date differs (for backdated entries)               │
│     Original Date: [          ]                                 │
│                                                                 │
│                                         [Cancel] [Save Entry]   │
└─────────────────────────────────────────────────────────────────┘
```

**Backdating:**
- Checkbox reveals "Original Date" field
- Original date stored in YAML frontmatter as `original_date`
- Display date = original_date if set, otherwise created date
- AI extraction of dates from content is a ReCog Engine sweep task, not real-time

**Voice Input (Future):**
- 🎤 button in editor area
- Transcribes to text in place
- Mobile-first feature, later priority

### 3.6 Upload Mode (`/reflect/upload`)

Bulk upload interface for ore (raw material to be smelted).

**Main Content:**
```
┌─────────────────────────────────────────────────────────────────┐
│  UPLOAD ORE FOR PROCESSING                                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                                                           │  │
│  │              Drag files here or click to browse           │  │
│  │                                                           │  │
│  │     Supported: .txt, .md, .json, .csv, images, audio      │  │
│  │                                                           │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  QUEUED FOR PROCESSING                                          │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ ✓ phone_backup_2024.json          12.4 MB      Queued     │  │
│  │ ✓ old_diary_scan.txt              48 KB        Queued     │  │
│  │ ◌ voice_memo_dec1.m4a             2.1 MB       Processing │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  RECENTLY PROCESSED                                             │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ ✓ therapy_notes_nov.md            → 14 segments extracted │  │
│  │ ✓ chat_export.json                → 47 segments extracted │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Upload Types:**
| Type | Processing |
|------|------------|
| Text files (.txt, .md) | Direct to smelt queue |
| JSON (chat exports) | Parse messages → segments |
| CSV | Row-per-segment extraction |
| Images | Store for future OCR/analysis |
| Audio | Transcription → segments |

**Queue Integration:**
- Uploads go directly to `smelt_queue` table
- Priority: lower than Reflection Chat sessions
- Processing status visible in sidebar

---

## 4. Forge Area (`/forge`)

### 4.1 Purpose

The Forge is where extracted ingots are reviewed, accepted, or rejected. This is the quality control gate before insights become part of the Ehko's permanent memory.

**Aesthetic:** Current MDV (gold/violet, arcane-tech warmth). No changes needed.

### 4.2 Layout

Identical to current Forge Mode, now as standalone page:

```
┌─────────────────────────────────────────────────────────────────┐
│                        NAVIGATION BAR                           │
├─────────────┬───────────────────────────────────────────────────┤
│ INGOT QUEUE │                                                   │
│ ───────────-│              INGOT DETAIL                         │
│ Filter: [▼] │                                                   │
│ ┌─────────┐ │  💎 MYTHIC                         92% significance│
│ │ 💎 ...  │ │                                                   │
│ │ 🥇 ...  │ │  Summary                                          │
│ │ 🥈 ...  │ │  [Full ingot summary text...]                     │
│ └─────────┘ │                                                   │
│             │  Themes: [tag] [tag]                              │
│ SMELT QUEUE │  Emotions: [tag] [tag]                            │
│ ─────────── │  Patterns: [tag] [tag]                            │
│ 12 pending  │                                                   │
│ [⚒️ Smelt]  │  Sources (3)                                      │
│             │  └─ [source list]                                 │
│             │                                                   │
│             │  [✗ Reject]              [◈ Forge into Ehko]      │
└─────────────┴───────────────────────────────────────────────────┘
```

**No input bar** — Forge is review-only, no chat.

### 4.3 Smelt Controls

Smelt section in sidebar:
- Pending count from all queues (reflection chat + upload)
- Manual smelt trigger
- Future: scheduling configuration

---

## 5. Terminal Area (`/terminal`)

### 5.1 Purpose

The Terminal is a general-purpose AI assistant interface. The forger can use any LLM model for tasks unrelated to personal reflection. The aesthetic signals "utility tool" rather than "contemplative space."

**Key difference from Reflections:** Terminal chats are processed with lower priority and a separate queue. Users should feel the "pressure is off" — they can brainstorm, ask questions, get help without every word being scrutinised for identity insights.

### 5.2 Aesthetic

**Retro PC / Line-Based Terminal:**
- Monospace or semi-mono font for messages
- Subtle scanline effect (optional, toggle-able)
- Blue glow instead of purple
- Sharp corners instead of rounded
- Grid/line decorations

**Inspiration:** Classic terminal emulators, BBS systems, early hacker aesthetic — but tasteful and modern.

### 5.3 Layout

```
┌─────────────────────────────────────────────────────────────────┐
│                        NAVIGATION BAR                           │
├─────────────┬───────────────────────────────────────────────────┤
│ MODEL       │     ◇ Ehko                                        │
│ ┌─────────┐ │   [stats]      Ready                              │
│ │◉ Sonnet │ │ ════════════════════════════════════════════════ │
│ │○ Haiku  │ │                                                   │
│ │○ GPT-4o │ │  > You: Can you help me debug this Python error?  │
│ │○ GPT-4m │ │                                                   │
│ └─────────┘ │  < Ehko: Sure, paste the traceback and I'll       │
│             │    take a look...                                 │
│ HISTORY     │                                                   │
│ ─────────── │  > You: [code block]                              │
│ [Recent 1]  │                                                   │
│ [Recent 2]  │  < Ehko: The issue is on line 42...               │
│ [Recent 3]  │                                                   │
│  ...        │ ════════════════════════════════════════════════ │
│ [+ New]     │                                                   │
├─────────────┼───────────────────────────────────────────────────┤
│             │ ┌───────────────────────────────────────────────┐ │
│             │ │ > _                                           │ │
│             │ └───────────────────────────────────────────────┘ │
└─────────────┴───────────────────────────────────────────────────┘
```

**Note:** Ehko avatar appears at top of main content area with compact stats bar beneath. Messages labelled "Ehko" not "Terminal" — it's still the Ehko responding, just with a different tool at hand.

### 5.4 Model Selector

**Sidebar Component:**
```
MODEL
┌─────────────────────┐
│ ◉ Claude Sonnet 4   │  ← Current selection
│ ○ Claude Haiku 4    │
│ ○ GPT-4o            │
│ ○ GPT-4o-mini       │
│ ○ Gemini Pro        │  (future)
└─────────────────────┘
```

**Behaviour:**
- Selecting a different model shows warning: "Switching models will start a new chat. Your Ehko remembers everything, so no context is truly lost. Continue?"
- On confirm: Create new session with selected model
- Current model stored in session metadata

### 5.5 Message Styling

**Terminal-style messages:**
```css
.terminal-message {
    font-family: 'JetBrains Mono', 'Consolas', monospace;
    font-size: 14px;
    line-height: 1.6;
    padding: 12px 16px;
    border-left: 2px solid var(--accent-primary);
    background: var(--bg-tertiary);
    margin: 8px 0;
}

.terminal-message.user::before {
    content: '> ';
    color: var(--accent-primary);
}

.terminal-message.assistant::before {
    content: '< ';
    color: var(--accent-secondary);
}
```

### 5.6 Processing Queue

Terminal sessions feed into a **separate smelt queue**:
- `queue_source: 'terminal'` (vs `'reflection'` or `'upload'`)
- Lower priority in processing order
- Same ingot extraction pipeline, just deferred
- Ingots surface in Forge like any other

---

## 6. Backend Changes

### 6.1 Route Registration

**Flask Routes:**
```python
# Page routes
@app.route('/')
def index():
    return redirect('/reflect')

@app.route('/reflect')
@app.route('/reflect/<submode>')
def reflect(submode='chat'):
    return render_template('reflect.html', submode=submode)

@app.route('/forge')
def forge():
    return render_template('forge.html')

@app.route('/terminal')
def terminal():
    return render_template('terminal.html')
```

### 6.2 API Extensions

**New Endpoints:**

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/journal/entries` | GET | List journal entries with date filters |
| `/api/journal/entries` | POST | Create new journal entry |
| `/api/journal/entries/<id>` | GET/PUT | Retrieve/update specific entry |
| `/api/upload/queue` | POST | Add file to upload queue |
| `/api/upload/status` | GET | Get upload processing status |
| `/api/terminal/sessions` | GET/POST | Terminal session management |
| `/api/terminal/sessions/<id>/messages` | GET/POST | Terminal message handling |

**Modified Endpoints:**

| Endpoint | Change |
|----------|--------|
| `/api/sessions` | Add `source` filter (reflection/terminal) |
| `/api/smelt/status` | Add queue breakdown by source |

### 6.3 Database Extensions

**New Columns:**

`forge_sessions` table:
```sql
ALTER TABLE forge_sessions ADD COLUMN source TEXT DEFAULT 'reflection';
-- Values: 'reflection', 'terminal'

ALTER TABLE forge_sessions ADD COLUMN model_used TEXT;
-- e.g., 'claude-sonnet-4', 'gpt-4o'
```

`smelt_queue` table:
```sql
ALTER TABLE smelt_queue ADD COLUMN queue_source TEXT DEFAULT 'reflection';
-- Values: 'reflection', 'terminal', 'upload'

ALTER TABLE smelt_queue ADD COLUMN priority INTEGER DEFAULT 5;
-- 1 = highest, 10 = lowest
-- reflection = 3, upload = 5, terminal = 7
```

**New Table: `journal_entries`**
```sql
CREATE TABLE journal_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    content TEXT NOT NULL,
    entry_date DATE NOT NULL,           -- Display date
    original_date DATE,                  -- Backdated date if different
    tags TEXT,                           -- JSON array
    emotional_tags TEXT,                 -- JSON array
    reflection_object_id TEXT,           -- Link to reflection_objects if synced
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_journal_entry_date ON journal_entries(entry_date);
CREATE INDEX idx_journal_original_date ON journal_entries(original_date);
```

### 6.4 Model Routing for Terminal

**Update `config.py`:**
```python
# Add terminal role with user-selectable models
ROLE_MODELS = {
    'processing': {...},
    'conversation': {...},  # Reflection Chat uses this
    'ehko': {...},
    'terminal': {
        'provider': 'user_selected',  # Dynamic
        'model': 'user_selected',
        'fallback': ('anthropic', 'claude-sonnet-4')
    }
}
```

**Terminal model selection:**
- User picks model in UI
- Selection passed to API with each request
- Factory instantiates appropriate provider

---

## 7. File Structure

### 7.1 Template Files

```
6.0 Frontend/
├── templates/
│   ├── base.html           # Shared layout + nav bar
│   ├── reflect.html        # Reflections area
│   ├── forge.html          # Forge area  
│   └── terminal.html       # Terminal area
├── static/
│   ├── css/
│   │   ├── base.css        # Shared styles
│   │   ├── reflect.css     # Reflection-specific
│   │   ├── forge.css       # Forge-specific (current styles)
│   │   └── terminal.css    # Terminal-specific
│   ├── js/
│   │   ├── common.js       # Shared utilities
│   │   ├── reflect.js      # Reflection logic
│   │   ├── forge.js        # Forge logic (current app.js, renamed)
│   │   ├── terminal.js     # Terminal logic
│   │   └── journal.js      # Journal-specific (calendar, etc.)
│   └── fonts/
│       └── JetBrainsMono/  # Terminal font
```

### 7.2 Migration Path

1. Rename current files:
   - `index.html` → `forge.html` (content extracted)
   - `styles.css` → split into `base.css` + `forge.css`
   - `app.js` → split into `common.js` + `forge.js`

2. Create new files:
   - `base.html` (nav bar, common layout)
   - `reflect.html`, `reflect.css`, `reflect.js`
   - `terminal.html`, `terminal.css`, `terminal.js`
   - `journal.js` (calendar component)

---

## 8. Implementation Phases

### Phase 1: Route Infrastructure (Foundation)
1. Create `base.html` with navigation bar
2. Set up Flask routes for all pages
3. Split existing CSS into base + forge
4. Verify current functionality still works at `/forge`

### Phase 2: Reflections Area
1. Create `reflect.html` with sub-mode tabs
2. Port Chat mode to `/reflect/chat`
3. Apply serene colour palette
4. Verify forge-to-vault works

### Phase 3: Journal Mode
1. Implement calendar component
2. Create journal entry CRUD API
3. Build entry editor with backdating
4. Integrate with indexing

### Phase 4: Terminal Area
1. Create `terminal.html` with retro aesthetic
2. Implement model selector
3. Add model-switch warning flow
4. Set up separate queue routing

### Phase 5: Upload System
1. Create upload dropzone UI
2. Implement upload queue API
3. Connect to smelt pipeline
4. Add progress indicators

### Phase 6: Polish
1. Responsive design pass
2. Keyboard shortcuts per area
3. Settings persistence
4. Animation/transition refinement

---

## 9. Resolved Design Decisions

1. **Ehko Avatar** — Present in ALL modes (Reflect, Forge, Terminal). The Ehko is who you're talking to everywhere. Simplified styling (no rotating rings), adapts colour to area palette.

2. **Stats Ribbon** — Compact bar positioned below the Ehko avatar. Shows key metrics without dominating the interface.

3. **Terminal History Limit** — 20 sessions in sidebar. Older sessions accessible via search/pagination. Sessions backed up to Mirrorwell for ReCog processing.

4. **Upload File Size Limit** — 50MB per file. Sufficient for large chat exports (20K messages ≈ 5-10MB JSON). Larger archives should be split.

5. **Journal Entry Length** — No hard limit. Trust users. Very long entries may be chunked for smelt processing.

## 10. Future Considerations

1. **Permanent Memory Architecture** — Terminal and Reflection chat sessions need backup to Mirrorwell for ReCog Engine processing. Spec needed for:
   - Session → Reflection Object conversion
   - Storage location in Mirrorwell vault
   - Incremental vs batch backup triggers
   - Memory retrieval for context injection

---

## Changelog

- v0.1.1 — 2025-12-02 — Resolved open questions: Ehko present in all modes, stats below avatar, 20 session limit, 50MB upload limit. Added future considerations for permanent memory architecture.
- v0.1 — 2025-12-02 — Initial specification


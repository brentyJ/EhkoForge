---
title: "Forge UI Update Specification"
vault: "EhkoForge"
type: "module"
category: "Frontend"
status: draft
version: "0.1"
created: 2025-12-01
updated: 2025-12-01
tags: [ehkoforge, frontend, ui, ingots, forge]
related:
  - "Ingot_System_Schema_v0_1.md"
  - "Smelt_Processor_Spec_v0_1.md"
  - "Frontend_Implementation_Spec_v1_0.md"
  - "UI-MDV-Specification.md"
---

# FORGE UI UPDATE SPECIFICATION v0.1

## 1. Overview

This specification defines how the frontend evolves from "select messages → forge" to "review ingots → accept/reject/defer" with the new smelt pipeline.

### 1.1 Design Goals

1. **Two distinct modes** — Chat (input capture) and Forge (ingot review)
2. **Ingots as primary unit** — Users interact with distilled insights, not raw messages
3. **Visual significance** — Ingot colour/glow reflects significance tier
4. **Ehko evolution visibility** — Changes to Ehko are surfaced, not hidden
5. **ADHD-aware** — Minimal clickable distractions during reflection, clear focus states

---

## 2. Screen Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         THE FORGE UI                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────┐  ┌─────────────────────────────────────────────┐  │
│  │             │  │                                             │  │
│  │   SIDEBAR   │  │              MAIN PANEL                     │  │
│  │             │  │                                             │  │
│  │  - Mode     │  │   [Changes based on mode]                   │  │
│  │    Toggle   │  │                                             │  │
│  │             │  │   CHAT MODE:                                │  │
│  │  - Sessions │  │     - Ehko avatar (nascent/forming)         │  │
│  │    (Chat)   │  │     - Message thread                        │  │
│  │             │  │     - Input area                            │  │
│  │  - Ingots   │  │     - "Send to Smelt" button                │  │
│  │    (Forge)  │  │                                             │  │
│  │             │  │   FORGE MODE:                               │  │
│  │  - Stats    │  │     - Ingot queue (surfaced)                │  │
│  │             │  │     - Selected ingot detail                 │  │
│  │  - Settings │  │     - Accept/Reject/Defer controls          │  │
│  │             │  │     - Source preview                        │  │
│  │             │  │                                             │  │
│  └─────────────┘  └─────────────────────────────────────────────┘  │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                      STATS RIBBON                           │   │
│  │   Identity: ████░░  Clarity: ███░░░  Resonance: █████░      │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 3. Mode Toggle

**Location:** Top of sidebar, prominent

**States:**
- **CHAT** — Input capture mode (talk to Ehko/Proko)
- **FORGE** — Ingot review mode (accept/reject insights)

**Visual:**
```
┌─────────────────────┐
│  ◉ CHAT    ○ FORGE  │
└─────────────────────┘
```

**Behaviour:**
- Clicking toggles between modes
- Badge on FORGE shows count of surfaced ingots awaiting review
- Subtle pulse animation if ingots are waiting

---

## 4. Chat Mode (Revised)

### 4.1 Layout

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│            ┌───────────────────────┐                    │
│            │                       │                    │
│            │    EHKO AVATAR        │                    │
│            │    (nascent state)    │                    │
│            │                       │                    │
│            └───────────────────────┘                    │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │ Message history                                  │   │
│  │                                                  │   │
│  │ You: I've been thinking about my relationship   │   │
│  │      with control lately...                     │   │
│  │                                                  │   │
│  │ Ehko: That's worth exploring. What triggered    │   │
│  │       this reflection?                          │   │
│  │                                                  │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │ Type your reflection...                     [↵] │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ┌──────────────┐  ┌──────────────┐                    │
│  │ 🔥 Send to   │  │ ✓ End        │                    │
│  │    Smelt     │  │   Session    │                    │
│  └──────────────┘  └──────────────┘                    │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 4.2 New Elements

**"Send to Smelt" Button:**
- Manually queues current session for immediate smelting
- Sets priority = 10 (high)
- Visual feedback: button glows briefly, tooltip "Queued for smelting"
- Does NOT close session — user can continue chatting

**"End Session" Button:**
- Closes current session
- Auto-queues for smelt if not already queued
- Returns to session list

**Annotation Controls (Future — v0.2):**
- Highlight text in messages
- Add inline comments
- Tag passages
- Deferred to keep v0.1 simple

### 4.3 Ehko Avatar States

| State | Visual | Condition |
|-------|--------|-----------|
| **Nascent** | Faint electron/particle cloud, barely visible | < 5 forged ingots |
| **Forming** | Translucent humanoid silhouette, flickering | 5-20 forged ingots |
| **Emerging** | Semi-solid form, features visible | 20-50 forged ingots |
| **Present** | Solid avatar, responsive animations | 50+ forged ingots |

Avatar state derived from `COUNT(*) FROM ingots WHERE status = 'forged'`.

---

## 5. Forge Mode (New)

### 5.1 Layout

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  INGOT QUEUE                              [3 awaiting]  │
│  ┌─────────────────────────────────────────────────┐   │
│  │ ● Control patterns in relationships      [gold] │   │
│  │ ○ Childhood isolation from sister       [silver]│   │
│  │ ○ Validation-seeking behaviour          [silver]│   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ─────────────────────────────────────────────────────  │
│                                                         │
│  SELECTED INGOT                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │                                                  │   │
│  │  ◆ Control patterns in relationships            │   │
│  │                                                  │   │
│  │  "A recurring pattern of needing to control     │   │
│  │   outcomes in relationships, stemming from      │   │
│  │   early experiences of unpredictability and     │   │
│  │   emotional unavailability."                    │   │
│  │                                                  │   │
│  │  Themes: control, relationships, anxiety        │   │
│  │  Emotions: fear, loneliness                     │   │
│  │  Patterns: avoidance, hypervigilance            │   │
│  │  Significance: 0.78 (gold)                      │   │
│  │  Sources: 3 reflections                         │   │
│  │                                                  │   │
│  │  ┌─────────────────────────────────────────┐   │   │
│  │  │ SOURCE EXCERPTS                         │   │   │
│  │  │                                         │   │   │
│  │  │ "I realise I've always tried to        │   │   │
│  │  │  control situations because..."        │   │   │
│  │  │  — 2025-09-08 Control & Anxiety        │   │   │
│  │  │                                         │   │   │
│  │  │ "The need to know what's coming next   │   │   │
│  │  │  feels almost compulsive..."           │   │   │
│  │  │  — 2025-11-26 Therapy Session          │   │   │
│  │  │                                         │   │   │
│  │  └─────────────────────────────────────────┘   │   │
│  │                                                  │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │ ✓ ACCEPT │  │ ✗ REJECT │  │ ◷ DEFER  │             │
│  │   FORGE  │  │          │  │          │             │
│  └──────────┘  └──────────┘  └──────────┘             │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 5.2 Ingot Queue

**Display:** Surfaced ingots (`status = 'surfaced'`) ordered by significance DESC

**Visual indicators:**
- Filled circle (●) = selected
- Empty circle (○) = unselected
- Colour badge reflects significance tier

### 5.3 Significance Colours

| Tier | Significance | Colour | CSS Variable |
|------|--------------|--------|--------------|
| Copper | 0.00 - 0.24 | `#b87333` | `--ingot-copper` |
| Iron | 0.25 - 0.49 | `#5a5a5a` | `--ingot-iron` |
| Silver | 0.50 - 0.74 | `#c0c0c0` | `--ingot-silver` |
| Gold | 0.75 - 0.89 | `#ffd700` | `--ingot-gold` |
| Mythic | 0.90 - 1.00 | `#ff6ec7` | `--ingot-mythic` |

### 5.4 Selected Ingot Detail

**Sections:**
1. **Summary** — The distilled insight (1-3 sentences)
2. **Metadata** — Themes, emotions, patterns, significance
3. **Source excerpts** — Relevant quotes from contributing reflections
4. **Action buttons** — Accept/Reject/Defer

### 5.5 Action Buttons

**ACCEPT (Forge):**
- Sets `ingots.status = 'forged'`
- Sets `ingots.forged_at = NOW()`
- Creates entry in `ehko_personality_layers`
- Optionally creates reflection file in Mirrorwell
- Shows confirmation animation (ingot glows, avatar pulses)
- Advances to next ingot in queue

**REJECT:**
- Sets `ingots.status = 'rejected'`
- Logs rejection in `ingot_history`
- Shows brief fade-out animation
- Advances to next ingot in queue

**DEFER:**
- Leaves ingot in queue (`status = 'surfaced'`)
- Moves it to end of queue visually
- User can return to it later

---

## 6. Sidebar Updates

### 6.1 Chat Mode Sidebar

```
┌─────────────────────┐
│  ◉ CHAT    ○ FORGE  │
├─────────────────────┤
│                     │
│  SESSIONS           │
│  ┌─────────────────┐│
│  │ + New Session   ││
│  ├─────────────────┤│
│  │ Today           ││
│  │  ▸ Morning...   ││
│  │  ▸ Therapy...   ││
│  │ Yesterday       ││
│  │  ▸ Control...   ││
│  └─────────────────┘│
│                     │
│  ─────────────────  │
│                     │
│  SMELT STATUS       │
│  ┌─────────────────┐│
│  │ Queue: 3        ││
│  │ Processing: 0   ││
│  │ [Run Smelt]     ││
│  └─────────────────┘│
│                     │
│  ─────────────────  │
│                     │
│  ⚙ Settings        │
│                     │
└─────────────────────┘
```

**Smelt Status Panel:**
- Shows queue counts
- "Run Smelt" button triggers manual smelt
- Updates after each smelt run

### 6.2 Forge Mode Sidebar

```
┌─────────────────────┐
│  ○ CHAT    ◉ FORGE  │
├─────────────────────┤
│                     │
│  INGOT FILTERS      │
│  ┌─────────────────┐│
│  │ ○ All Surfaced  ││
│  │ ○ Gold+         ││
│  │ ○ By Theme...   ││
│  └─────────────────┘│
│                     │
│  ─────────────────  │
│                     │
│  FORGED TODAY       │
│  ┌─────────────────┐│
│  │ 2 ingots        ││
│  │ +0.03 identity  ││
│  └─────────────────┘│
│                     │
│  ─────────────────  │
│                     │
│  EHKO STATUS        │
│  ┌─────────────────┐│
│  │ State: Forming  ││
│  │ Layers: 12      ││
│  │ [View Layers]   ││
│  └─────────────────┘│
│                     │
│  ─────────────────  │
│                     │
│  ⚙ Settings        │
│                     │
└─────────────────────┘
```

**New panels:**
- **Ingot Filters** — Filter queue by tier or theme
- **Forged Today** — Session progress summary
- **Ehko Status** — Current avatar state, layer count, link to view layers

---

## 7. Stats Ribbon Updates

Current stats (identity_depth, clarity, resonance, anchors) remain.

**New stat: Ehko Solidity**

```python
def calculate_ehko_solidity() -> float:
    """Calculate how 'solid' the Ehko is based on forged ingots."""
    conn = get_db()
    cursor = conn.cursor()
    
    # Count forged ingots
    cursor.execute("SELECT COUNT(*) FROM ingots WHERE status = 'forged'")
    forged_count = cursor.fetchone()[0]
    
    # Target: 50 ingots = 1.0 solidity
    solidity = min(1.0, forged_count / 50.0)
    
    conn.close()
    return solidity
```

**Display:**
```
Solidity: ██░░░░ (24%)  — "Forming"
```

---

## 8. API Endpoints (New/Updated)

### 8.1 Ingot Endpoints

```python
@app.route("/api/ingots", methods=["GET"])
def get_ingots():
    """
    Get ingots for Forge UI.
    
    Query params:
    - status: filter by status (default: 'surfaced')
    - min_significance: minimum significance threshold
    - theme: filter by theme tag
    - limit: max results (default: 20)
    """
    status = request.args.get("status", "surfaced")
    min_sig = request.args.get("min_significance", 0.0, type=float)
    theme = request.args.get("theme")
    limit = request.args.get("limit", 20, type=int)
    
    conn = get_db()
    cursor = conn.cursor()
    
    query = """
        SELECT id, summary, themes_json, emotional_tags_json, patterns_json,
               significance, confidence, source_count, created_at, updated_at
        FROM ingots
        WHERE status = ?
        AND significance >= ?
    """
    params = [status, min_sig]
    
    if theme:
        query += " AND themes_json LIKE ?"
        params.append(f'%"{theme}"%')
    
    query += " ORDER BY significance DESC LIMIT ?"
    params.append(limit)
    
    cursor.execute(query, params)
    
    ingots = []
    for row in cursor.fetchall():
        ingots.append({
            "id": row["id"],
            "summary": row["summary"],
            "themes": json.loads(row["themes_json"]) if row["themes_json"] else [],
            "emotional_tags": json.loads(row["emotional_tags_json"]) if row["emotional_tags_json"] else [],
            "patterns": json.loads(row["patterns_json"]) if row["patterns_json"] else [],
            "significance": row["significance"],
            "significance_tier": get_significance_tier(row["significance"]),
            "confidence": row["confidence"],
            "source_count": row["source_count"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        })
    
    conn.close()
    return jsonify({"ingots": ingots})


@app.route("/api/ingots/<ingot_id>", methods=["GET"])
def get_ingot_detail(ingot_id):
    """Get full ingot details including sources."""
    conn = get_db()
    cursor = conn.cursor()
    
    # Get ingot
    cursor.execute("SELECT * FROM ingots WHERE id = ?", (ingot_id,))
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        return jsonify({"error": "Ingot not found"}), 404
    
    ingot = {
        "id": row["id"],
        "summary": row["summary"],
        "themes": json.loads(row["themes_json"]) if row["themes_json"] else [],
        "emotional_tags": json.loads(row["emotional_tags_json"]) if row["emotional_tags_json"] else [],
        "patterns": json.loads(row["patterns_json"]) if row["patterns_json"] else [],
        "significance": row["significance"],
        "significance_tier": get_significance_tier(row["significance"]),
        "confidence": row["confidence"],
        "source_count": row["source_count"],
        "status": row["status"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }
    
    # Get sources
    cursor.execute("""
        SELECT source_type, source_id, excerpt, added_at
        FROM ingot_sources
        WHERE ingot_id = ?
        ORDER BY added_at ASC
    """, (ingot_id,))
    
    sources = []
    for src in cursor.fetchall():
        source_title = get_source_title(cursor, src["source_type"], src["source_id"])
        sources.append({
            "type": src["source_type"],
            "id": src["source_id"],
            "title": source_title,
            "excerpt": src["excerpt"],
            "added_at": src["added_at"],
        })
    
    ingot["sources"] = sources
    
    conn.close()
    return jsonify(ingot)


@app.route("/api/ingots/<ingot_id>/forge", methods=["POST"])
def forge_ingot(ingot_id):
    """Accept and forge an ingot into the Ehko."""
    conn = get_db()
    cursor = conn.cursor()
    
    now = datetime.utcnow().isoformat() + "Z"
    
    # Get ingot data
    cursor.execute("SELECT * FROM ingots WHERE id = ?", (ingot_id,))
    ingot = cursor.fetchone()
    
    if not ingot:
        conn.close()
        return jsonify({"error": "Ingot not found"}), 404
    
    if ingot["status"] == "forged":
        conn.close()
        return jsonify({"error": "Ingot already forged"}), 400
    
    # Update ingot status
    cursor.execute("""
        UPDATE ingots SET status = 'forged', forged_at = ?, updated_at = ?
        WHERE id = ?
    """, (now, now, ingot_id))
    
    # Create personality layer
    # Determine layer type from ingot patterns/themes
    layer_type = determine_layer_type(ingot)
    layer_content = build_layer_content(ingot)
    
    cursor.execute("""
        INSERT INTO ehko_personality_layers (ingot_id, layer_type, content, weight, integrated_at)
        VALUES (?, ?, ?, ?, ?)
    """, (ingot_id, layer_type, layer_content, ingot["significance"], now))
    
    # Log history
    cursor.execute("""
        INSERT INTO ingot_history (ingot_id, event_type, event_at, trigger)
        VALUES (?, 'forged', ?, 'user_action')
    """, (ingot_id, now))
    
    conn.commit()
    conn.close()
    
    return jsonify({
        "success": True,
        "ingot_id": ingot_id,
        "layer_type": layer_type,
        "message": "Ingot forged into Ehko"
    })


@app.route("/api/ingots/<ingot_id>/reject", methods=["POST"])
def reject_ingot(ingot_id):
    """Reject an ingot."""
    conn = get_db()
    cursor = conn.cursor()
    
    now = datetime.utcnow().isoformat() + "Z"
    
    cursor.execute("""
        UPDATE ingots SET status = 'rejected', updated_at = ?
        WHERE id = ?
    """, (now, ingot_id))
    
    cursor.execute("""
        INSERT INTO ingot_history (ingot_id, event_type, event_at, trigger)
        VALUES (?, 'rejected', ?, 'user_action')
    """, (ingot_id, now))
    
    conn.commit()
    conn.close()
    
    return jsonify({"success": True, "ingot_id": ingot_id})


@app.route("/api/ehko/status", methods=["GET"])
def get_ehko_status():
    """Get Ehko's current status."""
    conn = get_db()
    cursor = conn.cursor()
    
    # Forged ingot count
    cursor.execute("SELECT COUNT(*) FROM ingots WHERE status = 'forged'")
    forged_count = cursor.fetchone()[0]
    
    # Layer count
    cursor.execute("SELECT COUNT(*) FROM ehko_personality_layers WHERE active = 1")
    layer_count = cursor.fetchone()[0]
    
    # Solidity
    solidity = min(1.0, forged_count / 50.0)
    
    # State
    if forged_count < 5:
        state = "nascent"
    elif forged_count < 20:
        state = "forming"
    elif forged_count < 50:
        state = "emerging"
    else:
        state = "present"
    
    conn.close()
    
    return jsonify({
        "forged_count": forged_count,
        "layer_count": layer_count,
        "solidity": solidity,
        "state": state,
    })


@app.route("/api/ehko/layers", methods=["GET"])
def get_ehko_layers():
    """Get all active personality layers."""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT epl.id, epl.ingot_id, epl.layer_type, epl.content, epl.weight, epl.integrated_at,
               i.summary as ingot_summary
        FROM ehko_personality_layers epl
        JOIN ingots i ON epl.ingot_id = i.id
        WHERE epl.active = 1
        ORDER BY epl.weight DESC, epl.integrated_at DESC
    """)
    
    layers = []
    for row in cursor.fetchall():
        layers.append({
            "id": row["id"],
            "ingot_id": row["ingot_id"],
            "ingot_summary": row["ingot_summary"],
            "layer_type": row["layer_type"],
            "content": row["content"],
            "weight": row["weight"],
            "integrated_at": row["integrated_at"],
        })
    
    conn.close()
    return jsonify({"layers": layers})
```

### 8.2 Helper Functions

```python
def get_significance_tier(significance: float) -> str:
    """Map significance score to tier name."""
    if significance >= 0.9:
        return "mythic"
    elif significance >= 0.75:
        return "gold"
    elif significance >= 0.5:
        return "silver"
    elif significance >= 0.25:
        return "iron"
    else:
        return "copper"


def get_source_title(cursor, source_type: str, source_id: str) -> str:
    """Get human-readable title for a source."""
    if source_type == "chat_session":
        cursor.execute("SELECT title FROM forge_sessions WHERE id = ?", (source_id,))
        row = cursor.fetchone()
        return row["title"] if row else source_id
    elif source_type == "transcript_segment":
        cursor.execute("SELECT transcript_path FROM transcript_segments WHERE id = ?", (source_id,))
        row = cursor.fetchone()
        return Path(row["transcript_path"]).stem if row else source_id
    elif source_type == "reflection":
        cursor.execute("SELECT title FROM reflection_objects WHERE file_path = ?", (source_id,))
        row = cursor.fetchone()
        return row["title"] if row else source_id
    return source_id


def determine_layer_type(ingot: dict) -> str:
    """Determine personality layer type from ingot content."""
    patterns = json.loads(ingot["patterns_json"]) if ingot["patterns_json"] else []
    themes = json.loads(ingot["themes_json"]) if ingot["themes_json"] else []
    
    # Heuristics
    if any(p in ["behaviour", "tendency", "habit", "reaction"] for p in patterns):
        return "pattern"
    if any(t in ["values", "beliefs", "principles"] for t in themes):
        return "value"
    if any(t in ["memory", "childhood", "event", "experience"] for t in themes):
        return "memory"
    if any(t in ["voice", "speech", "communication", "tone"] for t in themes):
        return "voice"
    
    return "trait"  # default


def build_layer_content(ingot: dict) -> str:
    """Build personality layer content from ingot."""
    summary = ingot["summary"]
    patterns = json.loads(ingot["patterns_json"]) if ingot["patterns_json"] else []
    
    content = summary
    if patterns:
        content += f" (Patterns: {', '.join(patterns)})"
    
    return content
```

---

## 9. CSS Additions

```css
/* Ingot tier colours */
:root {
    --ingot-copper: #b87333;
    --ingot-iron: #5a5a5a;
    --ingot-silver: #c0c0c0;
    --ingot-gold: #ffd700;
    --ingot-mythic: #ff6ec7;
    
    --ingot-copper-glow: rgba(184, 115, 51, 0.3);
    --ingot-iron-glow: rgba(90, 90, 90, 0.3);
    --ingot-silver-glow: rgba(192, 192, 192, 0.3);
    --ingot-gold-glow: rgba(255, 215, 0, 0.4);
    --ingot-mythic-glow: rgba(255, 110, 199, 0.5);
}

/* Mode toggle */
.mode-toggle {
    display: flex;
    gap: 1rem;
    padding: 0.75rem;
    background: var(--panel-bg);
    border-radius: 8px;
    margin-bottom: 1rem;
}

.mode-toggle label {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    cursor: pointer;
    padding: 0.5rem 1rem;
    border-radius: 6px;
    transition: background 0.2s;
}

.mode-toggle label:hover {
    background: var(--hover-bg);
}

.mode-toggle input:checked + span {
    color: var(--accent-primary);
    font-weight: 600;
}

.mode-badge {
    background: var(--accent-primary);
    color: var(--bg-primary);
    font-size: 0.75rem;
    padding: 0.125rem 0.5rem;
    border-radius: 10px;
    margin-left: 0.5rem;
}

/* Ingot queue */
.ingot-queue {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    max-height: 200px;
    overflow-y: auto;
}

.ingot-queue-item {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.75rem;
    background: var(--panel-bg);
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.2s;
}

.ingot-queue-item:hover {
    background: var(--hover-bg);
}

.ingot-queue-item.selected {
    background: var(--hover-bg);
    border-left: 3px solid var(--accent-primary);
}

.ingot-tier-badge {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    flex-shrink: 0;
}

.ingot-tier-badge.copper { background: var(--ingot-copper); }
.ingot-tier-badge.iron { background: var(--ingot-iron); }
.ingot-tier-badge.silver { background: var(--ingot-silver); }
.ingot-tier-badge.gold { background: var(--ingot-gold); box-shadow: 0 0 8px var(--ingot-gold-glow); }
.ingot-tier-badge.mythic { background: var(--ingot-mythic); box-shadow: 0 0 12px var(--ingot-mythic-glow); }

/* Ingot detail */
.ingot-detail {
    background: var(--panel-bg);
    border-radius: 8px;
    padding: 1.5rem;
}

.ingot-detail-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 1rem;
}

.ingot-detail-header .tier-icon {
    font-size: 1.5rem;
}

.ingot-summary {
    font-size: 1.1rem;
    line-height: 1.6;
    margin-bottom: 1.5rem;
    color: var(--text-primary);
}

.ingot-metadata {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 1rem;
    margin-bottom: 1.5rem;
}

.ingot-meta-item {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
}

.ingot-meta-label {
    font-size: 0.8rem;
    color: var(--text-muted);
    text-transform: uppercase;
}

.ingot-meta-value {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
}

.ingot-tag {
    background: var(--tag-bg);
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-size: 0.85rem;
}

/* Source excerpts */
.ingot-sources {
    background: var(--bg-secondary);
    border-radius: 6px;
    padding: 1rem;
    margin-bottom: 1.5rem;
}

.ingot-sources-header {
    font-size: 0.9rem;
    color: var(--text-muted);
    margin-bottom: 0.75rem;
}

.ingot-source-item {
    padding: 0.75rem 0;
    border-bottom: 1px solid var(--border-color);
}

.ingot-source-item:last-child {
    border-bottom: none;
}

.ingot-source-excerpt {
    font-style: italic;
    color: var(--text-secondary);
    margin-bottom: 0.25rem;
}

.ingot-source-ref {
    font-size: 0.8rem;
    color: var(--text-muted);
}

/* Action buttons */
.ingot-actions {
    display: flex;
    gap: 1rem;
    justify-content: center;
}

.ingot-action-btn {
    padding: 0.75rem 1.5rem;
    border-radius: 6px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
    border: none;
}

.ingot-action-btn.accept {
    background: var(--success-color);
    color: white;
}

.ingot-action-btn.accept:hover {
    background: var(--success-hover);
    box-shadow: 0 0 12px var(--success-glow);
}

.ingot-action-btn.reject {
    background: var(--error-color);
    color: white;
}

.ingot-action-btn.reject:hover {
    background: var(--error-hover);
}

.ingot-action-btn.defer {
    background: var(--panel-bg);
    color: var(--text-secondary);
    border: 1px solid var(--border-color);
}

.ingot-action-btn.defer:hover {
    background: var(--hover-bg);
}

/* Forge animation */
@keyframes forge-glow {
    0% { box-shadow: 0 0 0 0 var(--ingot-gold-glow); }
    50% { box-shadow: 0 0 30px 10px var(--ingot-gold-glow); }
    100% { box-shadow: 0 0 0 0 var(--ingot-gold-glow); }
}

.ingot-forging {
    animation: forge-glow 1s ease-out;
}

/* Ehko avatar states */
.ehko-avatar.ehko-nascent {
    opacity: 0.2;
    filter: blur(2px);
}

.ehko-avatar.ehko-forming {
    opacity: 0.5;
    filter: blur(1px);
    animation: flicker 2s infinite;
}

.ehko-avatar.ehko-emerging {
    opacity: 0.8;
}

.ehko-avatar.ehko-present {
    opacity: 1.0;
}

@keyframes flicker {
    0%, 100% { opacity: 0.5; }
    50% { opacity: 0.7; }
    75% { opacity: 0.4; }
}
```

---

## 10. JavaScript Structure (app.js updates)

```javascript
// =============================================================================
// STATE
// =============================================================================

const state = {
    mode: 'chat',  // 'chat' or 'forge'
    // ... existing state ...
    
    // Forge mode state
    ingots: [],
    selectedIngotId: null,
    ehkoStatus: {
        forged_count: 0,
        layer_count: 0,
        solidity: 0,
        state: 'nascent'
    }
};


// =============================================================================
// MODE SWITCHING
// =============================================================================

function setMode(mode) {
    state.mode = mode;
    
    document.getElementById('chat-mode-content').style.display = mode === 'chat' ? 'block' : 'none';
    document.getElementById('forge-mode-content').style.display = mode === 'forge' ? 'block' : 'none';
    
    // Update sidebar
    updateSidebarForMode(mode);
    
    if (mode === 'forge') {
        loadIngots();
        loadEhkoStatus();
    }
}


// =============================================================================
// INGOT FUNCTIONS
// =============================================================================

async function loadIngots() {
    try {
        const response = await fetch('/api/ingots?status=surfaced');
        const data = await response.json();
        state.ingots = data.ingots;
        renderIngotQueue();
        
        // Select first ingot if any
        if (state.ingots.length > 0 && !state.selectedIngotId) {
            selectIngot(state.ingots[0].id);
        }
    } catch (error) {
        console.error('Failed to load ingots:', error);
    }
}

function renderIngotQueue() {
    const queue = document.getElementById('ingot-queue');
    
    if (state.ingots.length === 0) {
        queue.innerHTML = '<div class="empty-state">No ingots awaiting review</div>';
        return;
    }
    
    queue.innerHTML = state.ingots.map(ingot => `
        <div class="ingot-queue-item ${ingot.id === state.selectedIngotId ? 'selected' : ''}"
             onclick="selectIngot('${ingot.id}')">
            <div class="ingot-tier-badge ${ingot.significance_tier}"></div>
            <div class="ingot-queue-summary">${truncate(ingot.summary, 50)}</div>
        </div>
    `).join('');
}

async function selectIngot(ingotId) {
    state.selectedIngotId = ingotId;
    renderIngotQueue();
    
    try {
        const response = await fetch(`/api/ingots/${ingotId}`);
        const ingot = await response.json();
        renderIngotDetail(ingot);
    } catch (error) {
        console.error('Failed to load ingot detail:', error);
    }
}

function renderIngotDetail(ingot) {
    const detail = document.getElementById('ingot-detail');
    
    const tierIcon = {
        copper: '◇',
        iron: '◆',
        silver: '◈',
        gold: '❖',
        mythic: '✦'
    }[ingot.significance_tier] || '◆';
    
    detail.innerHTML = `
        <div class="ingot-detail-header">
            <span class="tier-icon" style="color: var(--ingot-${ingot.significance_tier})">${tierIcon}</span>
            <span class="ingot-tier-label">${ingot.significance_tier.toUpperCase()}</span>
        </div>
        
        <div class="ingot-summary">${ingot.summary}</div>
        
        <div class="ingot-metadata">
            <div class="ingot-meta-item">
                <span class="ingot-meta-label">Themes</span>
                <div class="ingot-meta-value">
                    ${ingot.themes.map(t => `<span class="ingot-tag">${t}</span>`).join('')}
                </div>
            </div>
            <div class="ingot-meta-item">
                <span class="ingot-meta-label">Emotions</span>
                <div class="ingot-meta-value">
                    ${ingot.emotional_tags.map(e => `<span class="ingot-tag">${e}</span>`).join('')}
                </div>
            </div>
            <div class="ingot-meta-item">
                <span class="ingot-meta-label">Patterns</span>
                <div class="ingot-meta-value">
                    ${ingot.patterns.map(p => `<span class="ingot-tag">${p}</span>`).join('')}
                </div>
            </div>
            <div class="ingot-meta-item">
                <span class="ingot-meta-label">Significance</span>
                <div class="ingot-meta-value">${(ingot.significance * 100).toFixed(0)}%</div>
            </div>
        </div>
        
        <div class="ingot-sources">
            <div class="ingot-sources-header">SOURCE EXCERPTS (${ingot.sources.length})</div>
            ${ingot.sources.map(src => `
                <div class="ingot-source-item">
                    <div class="ingot-source-excerpt">"${src.excerpt}"</div>
                    <div class="ingot-source-ref">— ${src.title}</div>
                </div>
            `).join('')}
        </div>
        
        <div class="ingot-actions">
            <button class="ingot-action-btn accept" onclick="forgeIngot('${ingot.id}')">✓ ACCEPT</button>
            <button class="ingot-action-btn reject" onclick="rejectIngot('${ingot.id}')">✗ REJECT</button>
            <button class="ingot-action-btn defer" onclick="deferIngot('${ingot.id}')">◷ DEFER</button>
        </div>
    `;
}

async function forgeIngot(ingotId) {
    try {
        const response = await fetch(`/api/ingots/${ingotId}/forge`, { method: 'POST' });
        const result = await response.json();
        
        if (result.success) {
            // Visual feedback
            const detail = document.getElementById('ingot-detail');
            detail.classList.add('ingot-forging');
            setTimeout(() => detail.classList.remove('ingot-forging'), 1000);
            
            // Reload
            await loadIngots();
            await loadEhkoStatus();
            
            // Select next ingot
            if (state.ingots.length > 0) {
                selectIngot(state.ingots[0].id);
            } else {
                document.getElementById('ingot-detail').innerHTML = '<div class="empty-state">All ingots reviewed!</div>';
            }
        }
    } catch (error) {
        console.error('Failed to forge ingot:', error);
    }
}

async function rejectIngot(ingotId) {
    try {
        await fetch(`/api/ingots/${ingotId}/reject`, { method: 'POST' });
        await loadIngots();
        
        if (state.ingots.length > 0) {
            selectIngot(state.ingots[0].id);
        } else {
            document.getElementById('ingot-detail').innerHTML = '<div class="empty-state">All ingots reviewed!</div>';
        }
    } catch (error) {
        console.error('Failed to reject ingot:', error);
    }
}

function deferIngot(ingotId) {
    // Move to end of local array (no server change needed)
    const idx = state.ingots.findIndex(i => i.id === ingotId);
    if (idx > -1) {
        const ingot = state.ingots.splice(idx, 1)[0];
        state.ingots.push(ingot);
        renderIngotQueue();
        
        if (state.ingots.length > 0) {
            selectIngot(state.ingots[0].id);
        }
    }
}


// =============================================================================
// EHKO STATUS
// =============================================================================

async function loadEhkoStatus() {
    try {
        const response = await fetch('/api/ehko/status');
        state.ehkoStatus = await response.json();
        updateEhkoDisplay();
    } catch (error) {
        console.error('Failed to load Ehko status:', error);
    }
}

function updateEhkoDisplay() {
    // Update avatar appearance based on state
    const avatar = document.getElementById('ehko-avatar');
    avatar.className = `ehko-avatar ehko-${state.ehkoStatus.state}`;
    
    // Update stats ribbon
    const solidityBar = document.getElementById('solidity-bar');
    if (solidityBar) {
        solidityBar.style.width = `${state.ehkoStatus.solidity * 100}%`;
    }
    
    // Update sidebar status
    const statusPanel = document.getElementById('ehko-status-panel');
    if (statusPanel) {
        statusPanel.innerHTML = `
            <div>State: ${state.ehkoStatus.state}</div>
            <div>Layers: ${state.ehkoStatus.layer_count}</div>
            <div>Forged: ${state.ehkoStatus.forged_count}</div>
        `;
    }
}


// =============================================================================
// UTILITY
// =============================================================================

function truncate(str, len) {
    return str.length > len ? str.substring(0, len) + '...' : str;
}
```

---

## 11. Files to Update

| File | Changes |
|------|---------|
| `EhkoForge/6.0 Frontend/static/index.html` | Add forge mode HTML, mode toggle |
| `EhkoForge/6.0 Frontend/static/styles.css` | Add ingot styles, tier colours |
| `EhkoForge/6.0 Frontend/static/app.js` | Add forge mode logic, ingot functions |
| `EhkoForge/5.0 Scripts/forge_server.py` | Add ingot API endpoints |

---

## 12. Open Items

- [ ] Annotation controls for Chat mode (highlight, comment, tag)
- [ ] Ingot editing before forge (adjust themes/emotions)
- [ ] Ehko layer viewer modal
- [ ] Notification system for new surfaced ingots
- [ ] Proko personality injection (pre-Ehko threshold)

---

**Changelog**
- v0.1 — 2025-12-01 — Initial specification

---
title: "EhkoForge UI — Minimum Delightful Version (MDV) Specification"
vault: "EhkoForge"
type: "module"
category: "Interface Design"
status: active
version: "1.0"
created: 2025-11-27
updated: 2025-11-27
tags: [ehkoforge, ui, frontend, mdv, interface, design]
related: ["Universal Template Framework", "System Architecture", "Behaviour Engine"]
source: "Brent Lefebure design spec"
confidence: 0.95
revealed: true
---

# EHKOFORGE UI — MINIMUM DELIGHTFUL VERSION (MDV) SPECIFICATION

## 0. Raw Input (Preserved)

EHKOFORGE v1.0 — MINIMUM DELIGHTFUL VERSION (MDV) UI SPEC

PURPOSE:
Define the minimal set of UI elements required to make EhkoForge 1.0 feel charming,
cohesive, and "alive" without entering into full gamification or advanced animations.
The aesthetic target is "Stardew Valley simplicity + arcane-tech warmth."

1. CORE LAYOUT
----------------
- Left sidebar: "Forging Sessions"
    - List of sessions with small glowing tags (identity, memory, reflection, lore, garden)
    - Soft translucent background
    - + New Session button at the bottom
- Main panel:
    - Top: Ehko Avatar Window
    - Middle: Chat area (Ehko <-> User)
    - Bottom: Input bar
- Stats ribbon (minimal)
    - Four or five symbolic stats (identity depth, clarity, resonance, anchors)
    - Simple iconography, no numbers, no bars

2. COLOUR PALETTE
--------------------
- Dark neutral background (#0d0f13 range)
- Accent blues, violets, muted gold
- Soft gradients, gentle glows
- No harsh neon, no flat white backgrounds

3. TYPOGRAPHY
--------------------
- Clean, modern sans-serif for all text
- Slightly rounded font pairs well (Inter, Satoshi, Noto)
- Text should breathe: generous spacing

4. EHKO AVATAR (v1)
-----------------------
- Small, floating, animated presence (GIF or CSS animation)
- Choose ONE archetype:
    - Mana Sprite (orb + drifting particles)
    - Geometric Wisp (central orb + orbiting shapes)
- Subtle looping animation (6–12 frames or CSS breathing effect)
- Faint glow behind avatar (low opacity)
- Toggle to disable avatar and show "minimal mode" icon

5. CHAT WINDOW
---------------------
- Clean message bubbles
- Slight glow on Ehko messages (subtle arcane aura)
- Animate message appearance with a soft slide-in or fade-in
- Vertical scrolling, no clutter

6. INPUT BAR
-------------------
- Simple text field with subtle forge-glow on the left edge
- Send button minimalistic (e.g., arrow rune, small flame icon)
- Auto-expand textbox for long entries

7. MICRO-DELIGHT ELEMENTS
----------------------------
- Hover glow on buttons
- Soft shimmer when a message is "forged into the vault"
- Tiny particle flicker when Ehko is thinking (not loading spinner)
- Light pulse in the stats ribbon when an insight is strong

8. SETTINGS PANEL (MINIMAL)
-------------------------------
- Toggle: "Minimal Mode (hide visual Ehko)"
- Toggle: "Low motion mode"
- Theme presets: "Forge Dark" (default), "Arcane Blue", "Ember Gold"

9. ACCESSIBILITY
--------------------
- High contrast mode
- Reduced chroma mode
- Dyslexic-friendly font option (optional for v1)

10. AESTHETIC GUARDRAILS
-----------------------------
- Everything must feel intentional, hand-crafted, warm.
- Nothing should look corporate, sterile, or clinical.
- Avoid over-sharp lines: round edges, soft corners.
- Keep charm > complexity.
- Keep simplicity > slickness.
- Keep soul > polish.

This MDV represents the minimum UI needed for EhkoForge v1.0 to feel alive, elegant, and emotionally resonant while remaining simple to implement.

---

## 1. Context

This specification defines the **Minimum Delightful Version (MDV)** of the EhkoForge user interface — the smallest feature set required to make the system feel emotionally resonant, visually cohesive, and functionally usable.

The design philosophy prioritises **charm over complexity**, **soul over polish**, and **intentionality over feature bloat**. The aesthetic target is "Stardew Valley simplicity meets arcane-tech warmth" — hand-crafted, warm, and alive without being corporate or sterile.

This is **not** the full gamified experience (stats progression, achievement trees, visual forge mechanics). This is the foundation: clean, accessible, emotionally grounded interface design that can scale into deeper gamification layers later.

**Target audience:**
- Brent (primary user, ADHD-aware design needs)
- Future users of the EhkoForge framework
- Developers implementing the first working prototype

---

## 2. Observations

### Core Layout Elements

**Left Sidebar ("Forging Sessions")**
- Persistent list of conversation sessions
- Each session tagged with small glowing labels: `identity`, `memory`, `reflection`, `lore`, `garden`
- Soft translucent background (#0d0f13 with ~15% opacity)
- "+ New Session" button at bottom of sidebar

**Main Panel (Three-Zone Structure)**
- **Top Zone:** Ehko Avatar Window (floating, animated presence)
- **Middle Zone:** Chat area (user ↔ Ehko conversational flow)
- **Bottom Zone:** Input bar with subtle forge-glow accent

**Stats Ribbon (Minimal Symbolic Display)**
- Four to five symbolic stats: `identity depth`, `clarity`, `resonance`, `anchors`
- Icon-based, no numeric readouts, no progress bars
- Subtle glow/pulse when stats shift during conversation

### Visual Design Language

**Colour Palette:**
- Base: Dark neutral (#0d0f13 range)
- Accents: Blues, violets, muted gold
- Gradients and glows should be soft, never harsh
- No neon, no flat white backgrounds

**Typography:**
- Modern sans-serif with slight rounding (Inter, Satoshi, Noto Sans)
- Generous spacing, text should "breathe"
- High readability over stylistic extremes

**Animation Principles:**
- Subtle, looping, hand-crafted feel
- Micro-delights: hover glows, particle flickers, soft slide-ins
- No loading spinners; use thematic "thinking" animations (particle shimmer)

### Ehko Avatar (v1 Archetypes)

Two possible implementations for MDV:

1. **Mana Sprite:** Central orb with drifting particles
2. **Geometric Wisp:** Central orb with orbiting shapes

**Technical specs:**
- GIF (6–12 frames) or CSS-based breathing animation
- Faint glow behind avatar (low opacity halo)
- Toggle for "minimal mode" (collapses to small icon)

### Accessibility Considerations

- High contrast mode
- Reduced chroma mode (for photosensitivity)
- Dyslexic-friendly font option (optional for v1)
- Low motion toggle (disables animations, keeps static UI)

---

## 3. Reflection / Interpretation

This UI spec reflects a deeper architectural principle in EhkoForge: **interfaces should feel like instruments, not tools**.

The distinction matters:
- **Tools** are functional, transactional, disposable.
- **Instruments** are expressive, resonant, worth caring for.

The Ehko avatar, the glowing message bubbles, the stats ribbon — these aren't just "nice to have" decorations. They're **emotional scaffolding** that transform a chatbot into a companion, a reflection engine into a forge, a journaling app into an identity practice.

### Why This Matters for ADHD Users

The spec explicitly includes:
- **Visual continuity** (sessions persist in sidebar, never lost)
- **Low-friction entry** (input bar always visible, auto-expands)
- **Micro-rewards** (shimmer on vault-save, stat pulses on insight)
- **Toggles for overwhelm** (minimal mode, low motion mode)

These aren't accommodations; they're **design choices that make the system better for everyone** while being essential for neurodivergent users.

### Aesthetic Guardrails as Design Philosophy

The final section ("Aesthetic Guardrails") functions as a **values statement**:

- "Intentional, hand-crafted, warm" → rejects auto-generated slickness
- "Nothing corporate, sterile, or clinical" → centres human connection over productivity-tech aesthetics
- "Charm > complexity, simplicity > slickness, soul > polish" → explicit prioritisation when trade-offs arise

This isn't just stylistic preference. It's **architectural guidance** for every future UI decision.

---

## 4. Actions / Updates

### Immediate Integration Points

**1. ehko_refresh.py (Indexing Script)**

The indexing script must recognise and tag UI-relevant metadata:

```python
# New tags for UI-linked reflections
UI_TAGS = [
    'ui_feedback',           # User feedback on interface experience
    'interface_preference',  # Stated UI preferences (animations, themes, etc.)
    'session_context',       # Reflection tied to specific UI session
    'stat_trigger'           # Reflection that might update symbolic stats
]

# Session metadata extraction
def extract_session_context(reflection_obj):
    """
    Parse YAML frontmatter for 'session_id', 'session_tags'
    Link reflections to UI sessions for display in sidebar
    """
    pass

# Stat calculation hooks
def calculate_symbolic_stats(vault_path):
    """
    Derive 'identity depth', 'clarity', 'resonance', 'anchors'
    from reflection corpus metadata (tags, core_memory flags, etc.)
    
    Returns dict of symbolic stat levels (0.0–1.0 scale)
    """
    pass
```

**Integration rule:**  
When `ehko_refresh.py` indexes a new reflection, it should update a **session manifest** (JSON or SQLite) that the UI reads to populate the sidebar.

---

**2. Frontend Tech Stack (To Be Decided)**

The spec is **stack-agnostic**, but implementation requires choosing:

**Option A: Electron App**
- Pro: Offline-first, native feel, easy file access
- Con: Heavier bundle, more complex distribution

**Option B: Local Web Server (Flask/FastAPI + Static HTML/CSS/JS)**
- Pro: Lightweight, easier to develop, portable
- Con: Requires running Python server in background

**Option C: Obsidian Plugin**
- Pro: Lives inside existing vault infrastructure
- Con: Limited UI customisation, plugin API constraints

**Recommendation:**  
Start with **Option B** (local web server + static frontend). Allows rapid prototyping, easy iteration, and future deployment flexibility (could become Electron app or hosted service later).

---

**3. Asset Pipeline**

The Ehko avatar requires visual assets:

**For GIF-based avatar:**
- 6–12 frame looping animation
- Transparent background
- 256x256px or 512x512px (scales down well)

**For CSS-based avatar:**
- SVG base shape (orb, geometric form)
- CSS keyframe animations for breathing/orbiting effects
- Particle effects using `<canvas>` or pure CSS

**Action:** Choose ONE archetype (Mana Sprite vs Geometric Wisp) and create initial asset. Gemini can generate concept art; Brent or a designer refines into final animated asset.

**Storage location:**  
`EhkoForge/Assets/UI/avatar-v1.gif` or `.svg`

---

**4. Settings & User Preferences**

The Settings Panel must write to a **config file** that persists across sessions:

**File:** `EhkoForge/Config/ui-preferences.json`

```json
{
  "theme": "forge-dark",
  "avatar_visible": true,
  "low_motion_mode": false,
  "high_contrast_mode": false,
  "reduced_chroma_mode": false,
  "dyslexic_font": false,
  "last_session_id": "session-2025-11-27-003"
}
```

This config is read on app launch and updated whenever user toggles a setting.

---

**5. Chat-to-Vault Flow (Message Forging)**

When a user message is "forged into the vault" (i.e., saved as a Mirrorwell reflection):

1. UI triggers "shimmer" animation on the message bubble
2. Backend writes reflection object to vault (using Mirrorwell Reflection Template v1.2)
3. `ehko_refresh.py` runs indexing pass (or queues for batch indexing)
4. Stats ribbon pulses if the reflection triggered a stat update
5. Sidebar updates with new session tag or count

**Technical requirement:**  
The UI must call a **"forge message"** endpoint that handles Markdown generation, file write, and index update.

---

### Next Steps (Ordered by Dependency)

1. **Choose frontend tech stack** (web server + static files recommended)
2. **Extend `ehko_refresh.py`** with session tracking and symbolic stat calculation
3. **Design & implement Ehko avatar** (choose archetype, create initial asset)
4. **Build core layout** (HTML/CSS structure for sidebar, main panel, stats ribbon)
5. **Implement chat window** (message bubbles, animations, scroll behaviour)
6. **Connect input bar to backend** (message send → reflection write → index update)
7. **Add settings panel** (toggles, theme switching, config persistence)
8. **Test accessibility features** (high contrast, low motion, dyslexic font)

---

## 5. Cross-References

**Related EhkoForge Modules:**
- [[Universal Template Framework v1.2]] — Defines structure for all reflection objects
- [[System Architecture]] — High-level overview of EhkoForge components
- [[Behaviour Engine]] (planned) — Will govern stat calculations and gamification logic
- [[ehko_refresh.py Specification]] — Indexing script that feeds UI data

**Related Mirrorwell Content:**
- User feedback on UI prototypes (tagged `ui_feedback`)
- Interface preferences stated in reflections (tagged `interface_preference`)

**External Design Inspirations:**
- Stardew Valley (charm, hand-crafted warmth)
- Arcane/mystical tech aesthetics (Transistor, Hades UI design)
- Obsidian's minimal, text-focused interface philosophy

---

**Changelog**
- v1.0 — 2025-11-27 — Initial MDV specification created from design notes; integration points with ehko_refresh.py defined; frontend tech stack options outlined; asset pipeline and config persistence specified

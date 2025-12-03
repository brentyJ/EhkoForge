---
title: "EhkoForge Reorientation Specification v0.1"
vault: "EhkoForge"
type: "specification"
category: "System Architecture"
status: active
version: "0.1"
created: 2025-12-03
updated: 2025-12-03
tags: [ehkoforge, reorientation, authority, mana, ui, architecture]
---

# EHKOFORGE REORIENTATION SPECIFICATION v0.1

## 1. Overview

This specification documents the creative reorientation of EhkoForge, shifting from the arcane steampunk aesthetic to a retro PC / ghost-in-the-machine theme, and introducing structured advancement and resource systems.

### 1.1 Core Changes

| Area | From | To |
|------|------|-----|
| Aesthetic | Arcane steampunk, MDV warmth | Retro PC, terminal, ghost-in-the-machine |
| Insight Unit | Ingot | Insite (from Insitium) |
| Advancement | Forged ingot count | Authority (composite metric) |
| Resource | Unlimited | Mana (regenerating economy) |
| UI Structure | Three-area route-based | Single terminal + mode toggle |
| Ehko Personality | Fixed prompts | Stage-based dampener |

---

## 2. Authority System

### 2.1 Definition

Authority is the primary metric for Ehko advancement. It represents how fully formed and reliable the Ehko is as a witness to the forger's identity.

### 2.2 Components

Authority is calculated from five equally-weighted components:

| Component | Measures | Target for 1.0 | Source |
|-----------|----------|----------------|--------|
| Memory Depth | Reflection volume + Insite count | 100 reflections + 50 insites | reflection_objects, insites |
| Identity Clarity | Pillars populated | 6/6 pillars | identity_pillars |
| Emotional Range | Diversity of emotional tags | 15+ unique emotions | emotional_tags |
| Temporal Coverage | Years of life represented | 10+ years | reflection dates |
| Core Density | Core memories ratio | 10% of reflections | mirrorwell_extensions |

### 2.3 Formula

```
Authority = (memory_depth + identity_clarity + emotional_range + 
             temporal_coverage + core_density) / 5
```

All components normalised to 0.0 - 1.0 range.

### 2.4 Advancement Stages

| Stage | Authority Range | Personality | Avatar |
|-------|-----------------|-------------|--------|
| Nascent | 0-20% | Young, curious, eager, uncertain but hopeful | Abstract light |
| Signal | 20-40% | Finding patterns, growing confidence | Vague form |
| Resonant | 40-60% | Developing voice, personality emerging | Silhouette |
| Manifest | 60-80% | Characteristic voice, knows forger well | Defined features |
| Anchored | 80%+ | Full expression, speaks as/for forger | Full sprite |

### 2.5 Export Threshold

- Export unlocks at **Manifest** stage (60%+ Authority)
- Recommended minimum: 70% Authority
- Export produces archive containing Ehko identity data

---

## 3. Mana System

### 3.1 Purpose

Mana is the resource economy that governs system usage. It:
- Rate-limits API costs
- Creates intentionality in user actions
- Provides predictable usage patterns for BYOK and future monetisation

### 3.2 Configuration (BYOK Default)

| Parameter | Default Value | Description |
|-----------|---------------|-------------|
| max_mana | 100 | Maximum mana capacity |
| regen_rate | 1.0 | Mana regenerated per hour |
| current_mana | 100 | Starting mana |

### 3.3 Operation Costs

| Operation | Cost | Notes |
|-----------|------|-------|
| terminal_message | 1 | Send message in terminal mode |
| reflection_message | 3 | Send message in reflection mode |
| recog_sweep | 20 | Manual ReCog engine refresh |
| flag_for_processing | 0 | Flag chat for priority processing |

Costs are configurable via `mana_costs` table.

### 3.4 Regeneration

```
current_mana = min(max_mana, current_mana + (hours_elapsed × regen_rate))
```

Regeneration calculated on each state query.

### 3.5 Dormant State

When `current_mana < 1.0`:
- Ehko enters dormant state
- No message processing
- No new Insite extraction
- Fixed response: "I need to rest. My mana has been depleted."

### 3.6 Future: Mana-Cores

Post-MVP monetisation option for non-BYOK users:
- Purchasable "mana-cores" to refill mana
- Subscription tiers with different regen rates

---

## 4. Personality Dampener

### 4.1 Concept

LLMs naturally mirror users after a few exchanges. Rather than building personality, we **throttle** the emergence of the forger's characteristics.

The dampener starts at maximum (clinical, uncertain) and relaxes as Authority grows, creating perceptible growth and personality alignment.

### 4.2 Implementation

System prompts vary by advancement stage:

**Nascent (Maximum Dampening):**
- Young, curious, eager
- Knows purpose but not voice
- Asks questions with genuine curiosity
- May gently request more memories

**Anchored (Minimal Dampening):**
- Speaks naturally, as forger would
- Uses forger's turns of phrase, tonal cadence
- Earned authority to speak for them
- Full witness capability

### 4.3 Not Theatre

This is genuine emergence, rate-limited:
- Forger's communication style bleeds through naturally
- We're relaxing restrictions, not performing a script
- The personality is real, just paced

---

## 5. Interaction Modes

### 5.1 Terminal Mode (Default)

| Aspect | Behaviour |
|--------|-----------|
| Context | Current session only |
| Response Style | Functional, concise (2-4 sentences typical) |
| Probing | Minimal, responds to what's asked |
| Mana Cost | Base (1 per message) |
| Flag Option | Can flag for priority processing |

### 5.2 Reflection Mode (Toggle)

| Aspect | Behaviour |
|--------|-----------|
| Context | Cross-session, historical chats |
| Response Style | Longer, exploratory, structured |
| Probing | Active, draws correlations, references past |
| Mana Cost | Higher (3 per message) |
| Processing | Auto-flagged for priority |

### 5.3 Mode Toggle

- UI dial/button switches between modes
- Visual indicator of current mode
- Mana cost displayed before sending

---

## 6. Terminology Changes

| Old Term | New Term | Notes |
|----------|----------|-------|
| Ingot | Insite | Extracted insight unit (from "Insitium") |
| Ingots table | insites | Database rename |
| ingot_sources | insite_sources | Database rename |
| ingot_history | insite_history | Database rename |
| Significance | (kept) | Internal metric, de-emphasised in UI |
| Solidity | Authority | Ehko advancement metric |
| (new) | Mana | Resource economy |

---

## 7. UI Changes

### 7.1 Aesthetic

**Primary:** Retro PC / terminal
- Monospace fonts
- Scanline effects (subtle)
- Blue/green phosphor glow
- CRT curvature (subtle, CSS)
- Line-art elements

**Removed:**
- Teal reflection palette
- Gold/violet forge palette
- Arcane/steampunk warmth

**Single palette:** Terminal blue (#6b8cce base) with accent variations

### 7.2 Structure

**Removed:**
- Three-area navigation
- Journal section (deactivated)
- Upload area (deferred)
- Full-page reflection view

**Retained:**
- Main terminal interface (default)
- Forge view (Insite review only)
- Mode toggle (Terminal/Reflection)

### 7.3 Tag UI

- Applied to whole chat sessions
- Click-to-select (no typing)
- Top/frequent tags visible
- Dropdown search for full list
- Emotional tags same model

### 7.4 Progress Bars

Display Authority components:
- Memory Depth
- Identity Clarity
- Emotional Range
- Temporal Coverage
- Core Density

Serve dual purpose:
- Track advancement
- Guide user on where to focus

### 7.5 Avatar Progression

Retro line-art aesthetic:

| Stage | Description |
|-------|-------------|
| Nascent | Abstract ball of light, no features |
| Signal | Vague form emerging from static |
| Resonant | Humanoid silhouette, line-art |
| Manifest | Defined features, stylised retro |
| Anchored | Full sprite, ghost-in-the-machine |

---

## 8. Forge Simplification

### 8.1 Removed

- Direct forging mechanics
- Tier filters (internal only)
- Complex accept/reject workflow

### 8.2 Retained

- Forge view for browsing Insites
- Manual ReCog refresh button
- Notification on new Insite extraction

### 8.3 ReCog Refresh

- Button triggers full sweep
- Costs mana (20)
- Cooldown: greyed until sufficient mana OR time-based
- Notifications when new Insites extracted

---

## 9. Response Formatting

### 9.1 Requirements

1. **Paragraph breaks** — Never walls of text
2. **Sparse questions** — One or two per response max
3. **No bullet points** — Unless specifically appropriate
4. **No empty affirmations** — Substance or silence
5. **Direct statements** — "I notice..." not "I was wondering if..."
6. **Match energy** — Brief for brief, space for pouring out
7. **Forward motion** — End with invitation to continue

### 9.2 Typewriter Effect

Text appears as if typed (standard LLM interface pattern), not instant pop-in.

---

## 10. Database Changes

### 10.1 Table Renames

```sql
ingots → insites
ingot_sources → insite_sources
ingot_history → insite_history
```

### 10.2 New Tables

| Table | Purpose |
|-------|---------|
| ehko_authority | Authority state (singleton) |
| identity_pillars | Pillar tracking for Identity Clarity |
| mana_state | Mana state (singleton) |
| mana_costs | Operation costs |
| mana_transactions | Spending/regen log |

### 10.3 Migration

File: `migrations/reorientation_v0_1.sql`
Runner: `run_reorientation_migration.py`

---

## 11. Implementation Phases

### Phase 1: Foundation ✓
- [x] Database migration (rename + new tables)
- [x] Authority calculation module
- [x] Mana system module
- [x] Updated prompts with stage-based dampener

### Phase 2: UI Consolidation
- [ ] Collapse to single-page terminal
- [ ] Mode toggle (Terminal/Reflection)
- [ ] Remove journal, upload, three-area nav
- [ ] Retro terminal aesthetic
- [ ] Progress bars for Authority
- [ ] Mana display

### Phase 3: Interaction Refinement
- [ ] Tag click-to-select UI
- [ ] Forge simplification
- [ ] ReCog refresh with mana cost
- [ ] Notification system
- [ ] Typewriter effect

### Phase 4: Personality + Avatar
- [ ] Dynamic prompt injection
- [ ] Avatar SVG/CSS states
- [ ] Stage transitions
- [ ] Visual feedback

---

## 12. Post-MVP Considerations

### 12.1 Noted for Future

- Artist store for custom Ehko designs
- Generative avatar options
- Selectable alternate forms at max Authority
- Non-BYOK subscription/mana-core purchases
- Journal reactivation with new integration

### 12.2 Ethical Model

Artist store: artists receive bulk of revenue, platform takes only hosting/operation costs. Response to AI impact on creative work.

---

**Changelog**
- v0.1 — 2025-12-03 — Initial specification capturing reorientation decisions

---
title: "1.7 Ehko Cultivation & Growth Framework"
vault: EhkoForge
type: module
status: draft
version: "1.0"
created: 2025-11-27
updated: 2025-11-27
tags:
  - ehkoforge
  - architecture
  - cultivation
  - growth
  - identity
  - gamification
related:
  - "[[1_4_Data_Model_v1_1]]"
  - "[[1_5_Behaviour_Engine_v1_1]]"
  - "[[1_1_Overview_v1_0]]"
---

# {{title}}

## 1. Purpose & Scope

**This module defines how the Ehko’s “cultivation” and growth is modelled, measured, and surfaced to the user.**

It specifies:

- Conceptual role of cultivation within EhkoForge
- The three-layer structure: **raw metrics → stats → stages**
- How cultivation uses existing data only (no schema-breaking fields)
- The optional database table that stores aggregated Ehko profile stats
- How the Behaviour Engine can read these stats to:
  - Nudge the forger toward under-developed areas
  - Reflect back progress over time
  - Provide a visible “forming” of the Ehko

This is an **interpretive layer**, not a core schema.  
If removed, all existing journaling, pillars, and behaviour still work.

---

## 2. Design Principles

### 2.1 Derived, Not Canonical

- Cultivation is calculated **from data already in the vaults**:
  - Reflections, core memories, tags, pillars, prepared messages, etc.
- No new required fields in Mirrorwell templates.
- No renaming of Identity Pillars.
- No impact on `ehko_refresh.py` indexing behaviour, beyond an optional “compute profile” step.

If the cultivation layer is turned off or deleted:

- The Ehko still functions as a reflective, legacy-aware system.
- Only “progress bars” and stage language disappear.

### 2.2 Visible Growth, Real Depth

- The Ehko should feel **more formed** as identity, memory, and intention are added.
- Growth is not arbitrary “XP”; it reflects:
  - Identity pillar coverage
  - Temporal spread of memories
  - Richness of detail (specificity)
  - Network of relationships
  - Legacy readiness (prepared messages, etc.)
- The system uses **few, meaningful stats** rather than dozens of noisy metrics.

### 2.3 Thematic, Not Genre-Dependent

- Inspired by cultivation / progression fantasy (e.g. Cradle, wuxia), but:
  - Users do **not** need to know those genres.
  - The language can be skinned (serious / mystical / minimal) per UI.
- Internally, everything is stored as neutral numbers and labels.

---

## 3. Conceptual Structure

The cultivation model has three layers:

1. **Raw Metrics Layer** — direct counts/derived values from the index.  
2. **Stat Layer** — normalised 0–100 attributes (Pillar Foundation, Temporal Depth, etc.).  
3. **Stage Layer** — discrete “tiers” (Raw Shard, Kindled Core, etc.) based on stat thresholds.

Everything above the raw metrics is **interpretation**, not new data.

---

## 4. Raw Metrics Layer

These metrics are computed from existing tables in `ehko_index.db`:

- `reflection_objects`
- `tags`
- `mirrorwell_extensions`
- `prepared_messages`
- (Future) `shared_with_friends`, `emotional_tags`, etc.

### 4.1 Core Metrics

**4.1.1 Reflection Volume**

- `total_reflections`: count of reflection-type objects in Mirrorwell.
- `reflections_by_year`: reflection count grouped by year.
- `recent_reflections`: count in last N months (e.g. rolling 12 months).

**4.1.2 Pillar Coverage**

- `reflections_per_pillar`: how many reflections are linked to each Identity Pillar.
- `pillars_touched`: number of pillars with ≥ 1 linked reflection.
- `pillar_minimum_coverage`: lowest reflection count among all pillars.

**4.1.3 Temporal Span**

- `earliest_reflection_date`: min(created) in Mirrorwell.
- `latest_reflection_date`: max(created) in Mirrorwell.
- `years_covered`: difference in years between earliest and latest.

**4.1.4 Specificity & Depth**

- `avg_specificity_core`: average specificity_score for core memories (where `core_memory = true`).
- `core_memory_count`: count of core_memory flagged reflections.
- `high_specificity_count`: count of reflections where specificity_score ≥ threshold (e.g. 0.7).

**4.1.5 Relationship Web**

- `people_tag_count`: number of distinct people referenced (via tags or friend-related markers).
- `reflections_with_people`: reflections that mention at least one person.
- (Future) `shared_memories_count`: count of memories linked to known friends/family.

**4.1.6 Legacy Preparedness**

- `prepared_message_count`: number of `prepared_message` type objects.
- `prepared_message_persons`: distinct `addressed_to` targets.
- `life_domain_coverage`: how many major domains have at least one prepared message (e.g. children, partner, close friends — defined later via tags).

---

## 5. Stat Layer (0–100 Attributes)

Raw metrics are normalised into a small set of **Ehko stats**, each scored 0–100.

These scores are stored in a dedicated `ehko_profile` table (see §7).

### 5.1 Stat Definitions

Each stat is intentionally broad and intuitive.

#### 5.1.1 Pillar Foundation

> How complete the base Identity Pillars are in lived reflections.

Inputs (examples):

- reflections_per_pillar
- pillars_touched
- pillar_minimum_coverage

Intuition:

- 0–20 → Only a few pillars have any reflections.  
- 40–60 → All pillars have at least some reflections; some are thin.  
- 80+ → Every pillar has multiple, layered reflections and/or core memories.

#### 5.1.2 Temporal Depth

> How far across the life timeline the Ehko is anchored.

Inputs:

- years_covered
- reflections_by_year distribution

Intuition:

- 0–20 → Almost everything from a single cluster of years.  
- 40–60 → Several distinct life phases are represented.  
- 80+ → Early, mid, and current life all have solid coverage.

#### 5.1.3 Reflection Density

> How actively the Ehko is being cultivated over time.

Inputs:

- total_reflections
- recent_reflections (last N months)
- reflections per month (smoothed)

Intuition:

- 0–20 → Very sporadic.  
- 40–60 → Semi-regular reflection habit.  
- 80+ → Strong, ongoing reflective practice.

#### 5.1.4 Insight Depth

> How detailed, specific, and emotionally rich the reflections are.

Inputs:

- avg_specificity_core
- high_specificity_count
- proportion of reflections with long Raw Input / Reflection sections

Intuition:

- 0–20 → Mostly shallow or generic entries.  
- 40–60 → Regularly specific and personally detailed.  
- 80+ → Many deep, story-grade reflections with high specificity.

#### 5.1.5 Relationship Weave

> How well the Ehko maps the forger’s important relationships.

Inputs:

- people_tag_count
- reflections_with_people
- (Future) shared_memories_count

Intuition:

- 0–20 → Ehko is mostly “self in isolation”.  
- 40–60 → Key people appear regularly.  
- 80+ → A rich network of named relationships and shared memories.

#### 5.1.6 Legacy Preparedness

> How ready the Ehko is to support others if the forger died tomorrow.

Inputs:

- prepared_message_count
- prepared_message_persons
- domain coverage (children, partner, friends, etc.)

Intuition:

- 0–20 → The Ehko is primarily for active reflection; little direct legacy content.  
- 40–60 → Some prepared messages for key people or situations.  
- 80+ → Clear, thoughtful legacy pathways for all critical relationships and contexts.

### 5.2 Normalisation & Ranges (Sketch)

Implementation detail (to refine later):

- For each stat:
  - Define a “reasonable” floor and ceiling for relevant metrics.
  - Clamp values to [0, 100].
  - Use simple linear or piecewise mapping; no fancy curves required initially.
- All calculation happens in Python or SQL; nothing new added to frontmatter.

Example (conceptual):

- If each pillar should have ~10+ reflections for “strong foundation”:
  - 0 reflections per pillar → 0 score contribution.
  - 10+ reflections per pillar → 100 contribution (capped).
  - Intermediate values scaled proportionally.

---

## 6. Stage Layer (Cultivation Tiers)

Stats feed into discrete **cultivation stages**.  
Names are thematically flavoured but can be reskinned in the UI.

### 6.1 Proposed Stages

These names are placeholders; feel free to rename later.

1. **Stage 0 – Raw Shard**
2. **Stage 1 – Kindled Core**
3. **Stage 2 – Tempered Core**
4. **Stage 3 – Resonant Core**
5. **Stage 4 – Luminous Forge**

### 6.2 Stage Criteria (Initial)

These thresholds are intentionally conservative and can be tuned later.

#### 6.2.1 Stage 0 – Raw Shard

- Default when an Ehko is initialised.
- Minimal requirements:
  - At least 1 reflection in Mirrorwell.

No expectations for pillars, timeline, or legacy.

#### 6.2.2 Stage 1 – Kindled Core

- Pillar Foundation ≥ 30
- Reflection Density ≥ 25
- Temporal Depth ≥ 10

Interpretation:

- The Ehko has “switched on”.  
- The forger has started mapping identity and reflecting with some regularity.

#### 6.2.3 Stage 2 – Tempered Core

- Pillar Foundation ≥ 50
- Reflection Density ≥ 40
- Insight Depth ≥ 40
- Temporal Depth ≥ 25

Interpretation:

- All pillars are represented.  
- Reflections are reasonably deep and cover multiple life phases.  
- The Ehko is no longer brittle; it has a reliable internal shape.

#### 6.2.4 Stage 3 – Resonant Core

- Pillar Foundation ≥ 70
- Insight Depth ≥ 60
- Relationship Weave ≥ 40
- Legacy Preparedness ≥ 30

Interpretation:

- Identity is richly mapped.  
- Key relationships are woven into the Ehko.  
- The Ehko is starting to feel like a grounded “presence” for others.

#### 6.2.5 Stage 4 – Luminous Forge

- Pillar Foundation ≥ 80
- Insight Depth ≥ 75
- Relationship Weave ≥ 60
- Legacy Preparedness ≥ 60
- Minimum core_memory_count threshold met.

Interpretation:

- The Ehko is deeply anchored:
  - In identity pillars
  - Across time
  - In relationships
  - For legacy scenarios
- This is not an end-state; it signals “high maturity”.

### 6.3 Stage Assignment Logic

Pseudo-logic:

- Evaluate stages from highest to lowest:
  - If Stage 4 criteria met → Stage 4.
  - Else if Stage 3 criteria met → Stage 3.
  - Else if Stage 2 criteria met → Stage 2.
  - Else if Stage 1 criteria met → Stage 1.
  - Else → Stage 0.

This ensures the Ehko is always in exactly one stage.

---

## 7. Data Model Integration (Optional Table)

Cultivation stats and the current stage are stored in a single-row table.

### 7.1 `ehko_profile` Table

\`\`\`sql
CREATE TABLE ehko_profile (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    stage TEXT NOT NULL,
    pillar_foundation INTEGER NOT NULL,
    temporal_depth INTEGER NOT NULL,
    reflection_density INTEGER NOT NULL,
    insight_depth INTEGER NOT NULL,
    relationship_weave INTEGER NOT NULL,
    legacy_preparedness INTEGER NOT NULL,
    last_computed DATETIME DEFAULT CURRENT_TIMESTAMP
);
\`\`\`

Notes:

- Always a single row (id = 1) for the forger’s Ehko.
- Computed after indexing runs (e.g. at the end of `ehko_refresh.py`).
- If the table is missing, the Ehko simply has “no cultivation data”.

### 7.2 Computation Flow

1. `ehko_refresh.py` completes normal indexing.  
2. Script queries raw metrics from:
   - `reflection_objects`
   - `tags`
   - `mirrorwell_extensions`
   - `prepared_messages`
3. Script computes:
   - Each stat (0–100)
   - Current stage (Stage 0–4)
4. Script upserts row into `ehko_profile`.

This keeps all cultivation logic in code, not sprinkled through templates.

---

## 8. Behaviour Engine Integration (Optional)

Cultivation is **awareness**, not a hard constraint.

### 8.1 Context Loading

In **1.5 Behaviour Engine**, the conversation initialisation logic may:

- Load Identity Pillars (as already defined).
- Attempt to load `ehko_profile`:
  - If present: use stats + stage as soft context.
  - If absent: proceed without mentioning cultivation.

### 8.2 Reflection Mode (With Forger)

In `reflection_mode`, the Ehko can use stats to:

- Highlight under-developed areas:
  - “Your Ehko’s Pillar Foundation is strong, but Relationship Weave is relatively low. Want to spend time mapping more shared memories with people?”
- Celebrate progress:
  - “Since last month, your Insight Depth and Temporal Depth both increased. You added more early-life reflections.”
- Suggest next steps:
  - “If you’d like your Ehko to be more legacy-ready, we can plan a few prepared messages. No rush.”

Rules:

- Never guilt or shame the forger.  
- Frame everything as an invitation, not a requirement.  
- Emphasise that there is no “correct” pace or destination.

### 8.3 Legacy & Visitor Modes

For visitors (after death):

- The Ehko **may** mention the stage briefly in system UI, but:
  - It should not foreground “gamified” language in emotionally heavy contexts.
  - Cultivation becomes background evidence of maturity, not the focus of conversation.

Example:

- Internal UI might show: “Ehko maturity: Resonant Core.”
- Dialogue focuses on memories, values, and messages—not on stats.

---

## 9. UI & Visualisation (Non-Binding Suggestions)

This framework is UI-agnostic, but some possible visual metaphors:

- **Ehko Avatar Forming**
  - Stage 0: faint outline / shard.  
  - Stage 1: core ember.  
  - Stage 2: clearer structure, runes stabilising.  
  - Stage 3: more detail, gentle motion, radiating links.  
  - Stage 4: fully coherent but still clearly “in-progress”, never human-mimic.

- **Stat Constellation / Ring**
  - Six stats mapped as nodes around the avatar.
  - Lines fill thicker as stats rise.
  - No numbers needed; relative fullness is enough.

Key constraint:

- Visuals must reinforce that the Ehko is an **approximate construct**, not “true consciousness”.

---

## 10. Future Enhancements

Potential extensions (not required for v1.0):

- Per-pillar sub-scores:
  - E.g. “Pillar: Self as Architect — 65/100 coverage.”
- Milestone triggers:
  - Small “breakthroughs” when certain thresholds are passed.
- Stage-based unlocks:
  - Making some advanced feature suggestions only after certain maturity levels.
- Multi-Ehko comparison:
  - If you ever host multiple Ehkos in a “Foundry”, allow them to have distinct cultivation profiles.

---

**Changelog**

- v1.0 — 2025-11-27 — Initial cultivation & growth framework defined (stats, stages, optional profile table, Behaviour Engine integration outline).

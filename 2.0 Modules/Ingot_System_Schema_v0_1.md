---
title: "Ingot System Schema Specification"
vault: "EhkoForge"
type: "module"
category: "Data Architecture"
status: draft
version: "0.1"
created: 2025-12-01
updated: 2025-12-01
tags: [ehkoforge, schema, ingots, smelt, database]
related:
  - "1_4_Data_Model_v1_3.md"
  - "Frontend_Implementation_Spec_v1_0.md"
---

# INGOT SYSTEM SCHEMA SPECIFICATION v0.1

## 1. Overview

This specification defines the SQLite schema for the smelt/ingot system — the metabolic layer that transforms raw reflections into distilled insights (ingots) ready for integration into an Ehko's personality.

### 1.1 Design Principles

- **Ingots are mutable, living objects** — they evolve through multiple analysis passes
- **Raw input is sacred** — never modified, only annotated and referenced
- **User annotations are hints, not dictates** — influence significance, don't control it
- **Full lineage tracking** — every ingot traces back to source material
- **Layered personality integration** — forged ingots become discrete personality components

### 1.2 Core Flow

```
Raw Input (chat, transcript, upload)
    ↓
[Tier 0: Code pre-annotation]
    ↓
[User annotations - optional]
    ↓
Smelt Queue (accumulated, timestamped)
    ↓
[Tier 2: Batch smelt - extract ingots]
    ↓
Ingot Pool (status: raw → refined)
    ↓
[Periodic Tier 2/3: Cross-correlation passes]
    ↓
Surfaced Insights (status: surfaced)
    ↓
User Review (accept / reject / defer)
    ↓
[On Accept: Integration into Ehko personality layer]
    ↓
Forged (status: forged)
```

---

## 2. LLM Cost Tiers

| Tier | Model Class | Purpose | Frequency |
|------|-------------|---------|-----------|
| **Tier 0** | Code/regex | Pre-annotation (keywords, intensity markers, entities) | Every message |
| **Tier 1** | Cheap (Haiku/Flash) | Chat companion, basic reflection prompts | Per message |
| **Tier 2** | Mid (Sonnet) | Smelt processing, ingot extraction, pattern tagging | Batch (daily/on-demand) |
| **Tier 3** | Expensive (Opus) | Cross-correlation, personality integration, deep analysis | Rare (weekly/milestone) |

---

## 3. New Tables

### 3.1 `smelt_queue`

Tracks raw input pending analysis.

```sql
CREATE TABLE smelt_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_type TEXT NOT NULL,          -- 'chat_session', 'transcript', 'upload'
    source_id TEXT NOT NULL,            -- session_id, file_path, segment_id
    queued_at TEXT NOT NULL,            -- ISO timestamp
    status TEXT DEFAULT 'pending',      -- 'pending', 'processing', 'complete', 'failed'
    priority INTEGER DEFAULT 0,         -- higher = process sooner
    word_count INTEGER,                 -- for threshold checks
    pre_annotation_json TEXT,           -- Tier 0 output (JSON blob)
    last_processed_at TEXT,             -- last smelt pass timestamp
    pass_count INTEGER DEFAULT 0,       -- how many times smelted
    notes TEXT                          -- error messages, processing notes
);

CREATE INDEX idx_smelt_queue_status ON smelt_queue(status, priority DESC);
CREATE INDEX idx_smelt_queue_source ON smelt_queue(source_type, source_id);
```

**Field notes:**
- `pass_count` enables multi-pass refinement
- `pre_annotation_json` caches Tier 0 output to avoid re-processing
- `priority` allows user-triggered immediate smelting to jump the queue

**Status values:**
- `pending` — awaiting first smelt pass
- `processing` — currently being analysed
- `complete` — all passes done, ingots extracted
- `failed` — error during processing (check `notes`)

---

### 3.2 `transcript_segments`

Breaks large uploads into manageable chunks for analysis.

```sql
CREATE TABLE transcript_segments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transcript_path TEXT NOT NULL,      -- original file path
    segment_index INTEGER NOT NULL,     -- order within transcript
    content TEXT NOT NULL,              -- segment text
    word_count INTEGER,
    start_timestamp TEXT,               -- if available from source
    end_timestamp TEXT,                 -- if available from source
    speaker TEXT,                       -- if identified
    pre_annotation_json TEXT,           -- Tier 0 output for this segment
    created_at TEXT NOT NULL,
    
    UNIQUE(transcript_path, segment_index)
);

CREATE INDEX idx_transcript_segments_path ON transcript_segments(transcript_path);
```

**Segmentation triggers:**
- Files over configurable threshold (default: 2000 words)
- Natural breaks (speaker changes, timestamps, paragraph gaps)
- Semantic boundaries (topic shifts detected by Tier 0)

**Notes:**
- Small files don't need segmentation — process as single unit
- Segments are referenced by `smelt_queue.source_type='transcript_segment'`

---

### 3.3 `annotations`

User-added hints on raw content.

```sql
CREATE TABLE annotations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_type TEXT NOT NULL,          -- 'chat_message', 'transcript_segment'
    source_id INTEGER NOT NULL,         -- message_id or segment_id
    annotation_type TEXT NOT NULL,      -- 'highlight', 'comment', 'tag', 'intensity'
    content TEXT,                       -- comment text, tag value, intensity level
    char_start INTEGER,                 -- for partial highlights (nullable)
    char_end INTEGER,                   -- for partial highlights (nullable)
    created_at TEXT NOT NULL,
    
    UNIQUE(source_type, source_id, annotation_type, char_start)
);

CREATE INDEX idx_annotations_source ON annotations(source_type, source_id);
```

**Annotation types:**

| Type | Purpose | `content` value |
|------|---------|-----------------|
| `highlight` | User marked passage as significant | NULL (uses char_start/end) |
| `comment` | User added clarification | Comment text |
| `tag` | User-assigned theme | Tag value |
| `intensity` | User-marked emotional weight | 'low' / 'medium' / 'high' |

**Design notes:**
- User cannot edit raw text — only annotate
- Annotations influence smelt model but don't dictate outcomes
- `char_start`/`char_end` allow highlighting specific phrases within a message

---

### 3.4 `ingots`

The core insight objects.

```sql
CREATE TABLE ingots (
    id TEXT PRIMARY KEY,                -- UUID
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    status TEXT DEFAULT 'raw',          -- 'raw', 'refined', 'surfaced', 'forged', 'rejected', 'merged'
    
    -- Significance
    significance REAL DEFAULT 0.5,      -- 0.0-1.0
    significance_tier TEXT,             -- derived: 'copper', 'iron', 'silver', 'gold', 'mythic'
    confidence REAL DEFAULT 0.5,        -- how certain is this insight
    
    -- Content
    summary TEXT NOT NULL,              -- 1-3 sentence distillation
    themes_json TEXT,                   -- JSON array of theme tags
    emotional_tags_json TEXT,           -- JSON array of emotional tags
    patterns_json TEXT,                 -- JSON array of identified patterns
    
    -- Lineage
    source_count INTEGER DEFAULT 1,     -- how many sources contributed
    earliest_source_date TEXT,          -- oldest contributing source
    latest_source_date TEXT,            -- newest contributing source
    
    -- Integration
    forged_at TEXT,                     -- when accepted into Ehko
    forged_reflection_id INTEGER,       -- link to reflection_objects if file created
    merged_into_id TEXT,                -- if merged, points to surviving ingot
    
    -- Processing metadata
    last_analysis_at TEXT,
    analysis_model TEXT,                -- which LLM tier processed this
    analysis_pass INTEGER DEFAULT 1     -- which pass generated/updated this
);

CREATE INDEX idx_ingots_status ON ingots(status);
CREATE INDEX idx_ingots_significance ON ingots(significance DESC);
CREATE INDEX idx_ingots_forged ON ingots(forged_at) WHERE forged_at IS NOT NULL;
```

**Status lifecycle:**

| Status | Meaning |
|--------|---------|
| `raw` | Just extracted, single source, minimal processing |
| `refined` | Multiple passes or sources have contributed |
| `surfaced` | Ready for user review (meets surfacing threshold) |
| `forged` | User accepted, integrated into Ehko |
| `rejected` | User declined (kept for history, excluded from Ehko) |
| `merged` | Absorbed into another ingot (see `merged_into_id`) |

**Surfacing threshold (configurable):**

Default: An ingot surfaces when ANY of:
- `significance >= 0.5` AND `pass_count >= 2`
- `source_count >= 3` (cross-correlation insight)
- User manually requests review
- Age > 7 days in pool (prevents stagnation)

---

### 3.5 `ingot_sources`

Links ingots to their source material.

```sql
CREATE TABLE ingot_sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ingot_id TEXT NOT NULL,
    source_type TEXT NOT NULL,          -- 'chat_message', 'transcript_segment', 'reflection'
    source_id TEXT NOT NULL,            -- message_id, segment_id, reflection file_path
    contribution_weight REAL DEFAULT 1.0, -- how much this source contributed
    excerpt TEXT,                       -- relevant snippet (for UI display)
    added_at TEXT NOT NULL,
    
    FOREIGN KEY (ingot_id) REFERENCES ingots(id),
    UNIQUE(ingot_id, source_type, source_id)
);

CREATE INDEX idx_ingot_sources_ingot ON ingot_sources(ingot_id);
CREATE INDEX idx_ingot_sources_source ON ingot_sources(source_type, source_id);
```

**Design notes:**
- An ingot can have many sources (cross-correlation)
- A source can contribute to many ingots (rich content yields multiple insights)
- `contribution_weight` allows partial attribution
- `excerpt` provides context in Forge UI without loading full source

---

### 3.6 `ingot_history`

Tracks ingot evolution over time.

```sql
CREATE TABLE ingot_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ingot_id TEXT NOT NULL,
    event_type TEXT NOT NULL,           -- see event types below
    event_at TEXT NOT NULL,
    old_value TEXT,                     -- JSON of previous state
    new_value TEXT,                     -- JSON of new state
    trigger TEXT,                       -- 'smelt_pass', 'user_action', 'correlation'
    
    FOREIGN KEY (ingot_id) REFERENCES ingots(id)
);

CREATE INDEX idx_ingot_history_ingot ON ingot_history(ingot_id, event_at);
```

**Event types:**
- `created` — ingot first extracted
- `significance_change` — significance value updated
- `source_added` — new source linked
- `refined` — status changed to refined
- `surfaced` — status changed to surfaced
- `forged` — user accepted
- `rejected` — user declined
- `merged` — absorbed into another ingot

---

### 3.7 `ehko_personality_layers`

Forged ingots become personality layers.

```sql
CREATE TABLE ehko_personality_layers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ingot_id TEXT NOT NULL,
    layer_type TEXT NOT NULL,           -- 'trait', 'memory', 'pattern', 'value', 'voice'
    content TEXT NOT NULL,              -- the actual personality instruction/context
    weight REAL DEFAULT 1.0,            -- influence strength
    active INTEGER DEFAULT 1,           -- can be toggled off without deleting
    integrated_at TEXT NOT NULL,
    
    FOREIGN KEY (ingot_id) REFERENCES ingots(id)
);

CREATE INDEX idx_personality_layers_active ON ehko_personality_layers(active, layer_type);
```

**Layer types:**

| Type | Purpose | Example |
|------|---------|---------|
| `trait` | Personality characteristic | "tends toward dry humour" |
| `memory` | Specific experience to reference | "remembers the 2019 camping trip" |
| `pattern` | Behavioural tendency | "retreats when feeling judged" |
| `value` | Core belief | "prioritises authenticity over harmony" |
| `voice` | Speech pattern | "uses Australian spelling, avoids corporate jargon" |

**Usage:**
When building the Ehko's system prompt, active layers are assembled by type and weight. Higher weight = more prominent in prompt. Inactive layers are preserved but excluded from prompt assembly.

---

## 4. Significance Tier Mapping

Derived field, calculated on read. Not stored separately.

```python
def get_significance_tier(significance: float) -> str:
    """Map significance score to named tier."""
    if significance >= 0.9:
        return 'mythic'
    elif significance >= 0.75:
        return 'gold'
    elif significance >= 0.5:
        return 'silver'
    elif significance >= 0.25:
        return 'iron'
    else:
        return 'copper'
```

**Note:** For v0.1, all ingots are treated with equal weight during forging. Tier display is cosmetic. Weighted forging deferred to v0.2+.

---

## 5. Integration with Existing Tables

### 5.1 No Changes Required

| Table | Notes |
|-------|-------|
| `forge_sessions` | Chat sessions remain as-is. Referenced by `smelt_queue.source_id` |
| `forge_messages` | Individual messages remain as-is. Referenced by `ingot_sources.source_id` |
| `reflection_objects` | Forged ingots can create reflection files. Linked via `ingots.forged_reflection_id` |

### 5.2 Optional Future Enhancement

`mirrorwell_extensions` could add `source_ingot_id` column to track which ingot spawned a reflection. Deferred — not blocking.

---

## 6. Migration Script

Run against existing `ehko_index.db` after current tables are in place.

```sql
-- =============================================================================
-- INGOT SYSTEM MIGRATION v0.1
-- =============================================================================
-- Run: sqlite3 ehko_index.db < this_file.sql
-- =============================================================================

-- Smelt queue
CREATE TABLE IF NOT EXISTS smelt_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_type TEXT NOT NULL,
    source_id TEXT NOT NULL,
    queued_at TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    priority INTEGER DEFAULT 0,
    word_count INTEGER,
    pre_annotation_json TEXT,
    last_processed_at TEXT,
    pass_count INTEGER DEFAULT 0,
    notes TEXT
);

CREATE INDEX IF NOT EXISTS idx_smelt_queue_status ON smelt_queue(status, priority DESC);
CREATE INDEX IF NOT EXISTS idx_smelt_queue_source ON smelt_queue(source_type, source_id);

-- Transcript segments
CREATE TABLE IF NOT EXISTS transcript_segments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transcript_path TEXT NOT NULL,
    segment_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    word_count INTEGER,
    start_timestamp TEXT,
    end_timestamp TEXT,
    speaker TEXT,
    pre_annotation_json TEXT,
    created_at TEXT NOT NULL,
    UNIQUE(transcript_path, segment_index)
);

CREATE INDEX IF NOT EXISTS idx_transcript_segments_path ON transcript_segments(transcript_path);

-- Annotations
CREATE TABLE IF NOT EXISTS annotations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_type TEXT NOT NULL,
    source_id INTEGER NOT NULL,
    annotation_type TEXT NOT NULL,
    content TEXT,
    char_start INTEGER,
    char_end INTEGER,
    created_at TEXT NOT NULL,
    UNIQUE(source_type, source_id, annotation_type, char_start)
);

CREATE INDEX IF NOT EXISTS idx_annotations_source ON annotations(source_type, source_id);

-- Ingots
CREATE TABLE IF NOT EXISTS ingots (
    id TEXT PRIMARY KEY,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    status TEXT DEFAULT 'raw',
    significance REAL DEFAULT 0.5,
    significance_tier TEXT,
    confidence REAL DEFAULT 0.5,
    summary TEXT NOT NULL,
    themes_json TEXT,
    emotional_tags_json TEXT,
    patterns_json TEXT,
    source_count INTEGER DEFAULT 1,
    earliest_source_date TEXT,
    latest_source_date TEXT,
    forged_at TEXT,
    forged_reflection_id INTEGER,
    merged_into_id TEXT,
    last_analysis_at TEXT,
    analysis_model TEXT,
    analysis_pass INTEGER DEFAULT 1
);

CREATE INDEX IF NOT EXISTS idx_ingots_status ON ingots(status);
CREATE INDEX IF NOT EXISTS idx_ingots_significance ON ingots(significance DESC);

-- Ingot sources
CREATE TABLE IF NOT EXISTS ingot_sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ingot_id TEXT NOT NULL,
    source_type TEXT NOT NULL,
    source_id TEXT NOT NULL,
    contribution_weight REAL DEFAULT 1.0,
    excerpt TEXT,
    added_at TEXT NOT NULL,
    FOREIGN KEY (ingot_id) REFERENCES ingots(id),
    UNIQUE(ingot_id, source_type, source_id)
);

CREATE INDEX IF NOT EXISTS idx_ingot_sources_ingot ON ingot_sources(ingot_id);
CREATE INDEX IF NOT EXISTS idx_ingot_sources_source ON ingot_sources(source_type, source_id);

-- Ingot history
CREATE TABLE IF NOT EXISTS ingot_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ingot_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    event_at TEXT NOT NULL,
    old_value TEXT,
    new_value TEXT,
    trigger TEXT,
    FOREIGN KEY (ingot_id) REFERENCES ingots(id)
);

CREATE INDEX IF NOT EXISTS idx_ingot_history_ingot ON ingot_history(ingot_id, event_at);

-- Ehko personality layers
CREATE TABLE IF NOT EXISTS ehko_personality_layers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ingot_id TEXT NOT NULL,
    layer_type TEXT NOT NULL,
    content TEXT NOT NULL,
    weight REAL DEFAULT 1.0,
    active INTEGER DEFAULT 1,
    integrated_at TEXT NOT NULL,
    FOREIGN KEY (ingot_id) REFERENCES ingots(id)
);

CREATE INDEX IF NOT EXISTS idx_personality_layers_active ON ehko_personality_layers(active, layer_type);

-- =============================================================================
-- END MIGRATION
-- =============================================================================
```

---

## 7. Table Summary

| Table | Purpose |
|-------|---------|
| `smelt_queue` | Tracks pending raw input for analysis |
| `transcript_segments` | Breaks large uploads into chunks |
| `annotations` | User hints on raw content |
| `ingots` | Core insight objects |
| `ingot_sources` | Links ingots to source material |
| `ingot_history` | Audit trail of ingot evolution |
| `ehko_personality_layers` | Forged insights as personality components |

---

## 8. Open Items (Deferred)

- [ ] Ingot merging algorithm
- [ ] Significance calculation weights
- [ ] Proko-to-Ehko handoff threshold
- [ ] Staged personality integration rules
- [ ] Reversal/unforge mechanics

---

**Changelog**
- v0.1 — 2025-12-01 — Initial schema specification

---
title: 1.4 Data Model
vault: EhkoForge
type: module
status: active
version: "1.4"
created: 2025-11-22
updated: 2025-12-03
tags:
  - ehkoforge
  - pinned
---
# {{title}}

## 1a. License Split

**Important:** The EhkoForge data model is split across two licenses:

| License | Scope | Document |
|---------|-------|----------|
| **MIT** | Core tables (reflection_objects, tags, sessions, authentication) | [[Data_Model_Core_Tables_v1_0]] |
| **AGPLv3** | ReCog Engine tables (ingots, smelt_queue, personality_layers) | [[2.0 Modules/ReCog/Ingot_System_Schema_v0_1]] |

**Core tables (MIT)** are free to use, modify, and distribute. Any identity preservation system can adopt this schema.

**ReCog tables (AGPLv3)** implement the cognitive processing pipeline. Commercial use requires either open-sourcing your implementation or obtaining a commercial license from brent@ehkolabs.io.

This document provides the overview. For implementation details, see the linked schema specifications.

---

## 1. Purpose & Scope

**This module defines the canonical data model for all EhkoForge reflection objects.**

It specifies:
- YAML frontmatter schema (required/optional fields, types, constraints)
- Markdown body structure (section naming, ordering, preservation rules)
- JSON packet schema for `_inbox` batch operations
- SQLite index schema for querying
- Version/changelog mechanics
- Cross-reference linking conventions
- **Authentication and friend registry schemas (integrated from 1.3 Security & Ownership)**

This is the implementation spec. A Python developer should be able to:
1. Build `ehko_refresh.py` to scan Mirrorwell and populate SQLite
2. Implement `_inbox` packet processing
3. Generate valid reflection objects programmatically
4. Implement authentication system with friend registry

---

## 2. Core Principles

### 2.1 Files Are Truth
- Markdown files in Obsidian vaults are the **source of truth**.
- SQLite is a **derived index** for querying; it is always rebuildable from files.
- No silent updates. Version bumps + changelog entries are mandatory for all modifications.

### 2.2 Raw Input is Sacred
- Section `## 0. Raw Input (Preserved)` must **never be modified** after creation.
- All edits happen in interpretation/reflection sections or via append-only changelog.

### 2.3 Template Inheritance
- **Universal Template Framework v1.1** is the abstract base.
- **Mirrorwell Reflection Template v1.2** is the primary specialisation.
- Specialisations may add fields or sections but must not remove base requirements.

### 2.4 Versioning is Explicit
- Every object has `version: "X.Y"` in frontmatter.
- Major version bump (X) = structural change (new required field, section reordering).
- Minor version bump (Y) = content update, new cross-references, tag additions.
- `updated: YYYY-MM-DD` timestamp changes on every edit.

### 2.5 Cross-References Are Typed
- `related: []` contains wiki-links to other reflection objects.
- Links may optionally include type hints: `[[1.2 Core Memory Index|memory]]`.
- Tags follow taxonomies (see Section 5.3).

---

## 3. Structures & Components

### 3.1 Universal Reflection Object Schema

#### 3.1.1 Required Frontmatter Fields
```yaml
title: string                    # Human-readable title
vault: string                    # Mirrorwell or EhkoForge
type: string                     # Object type (reflection, prepared_message, module, etc.)
status: string                   # One of: active, archived, deprecated, draft
version: string                  # Semantic version "X.Y"
created: date (YYYY-MM-DD)       # Creation date (never changes)
updated: date (YYYY-MM-DD)       # Last modification date
tags: array[string]              # Folksonomy tags
```

#### 3.1.2 Optional Frontmatter Fields
```yaml
category: string                 # Hierarchical category (e.g., "journaling")
related: array[string]           # Wiki-links to related objects
source: string                   # Origin context (internal, transcript, therapy, conversation)
confidence: float (0.0-1.0)      # Certainty level for derived insights (default: 0.95)
revealed: boolean                # Visibility flag (default: true; false = veiled content)
reveal_conditions: object        # Conditional revelation rules (see 1.3 Security & Ownership)
```

#### 3.1.3 Mirrorwell Extension Fields

Additional **optional** fields for Mirrorwell content:

```yaml
emotional_tags: array[string]    # Emotion markers (anger, grief, joy, clarity, etc.)
core_memory: boolean             # Flag for Core Memory Index inclusion
identity_pillar: string          # Link to identity framework (if applicable)
shared_with: array[string]       # Names of friends mentioned/involved in this memory

# Core Memory Index fields (see 1_7_Core_Memory_Index_Framework)
core_memory_status: string       # One of: nominated, curated, archived
core_memory_themes: array[string]  # Thematic tags for index grouping
pillar_links: array[string]      # Identity Pillars this memory informs
index_priority: integer          # 1=highest, 5=lowest (default: 3)
last_reviewed: date              # Last curation review date
```

#### 3.1.4 Prepared Message Extension Fields

```yaml
# Required for type: prepared_message
addressed_to: array[string]          # Names from friend_registry, or ["*"] for anyone
trigger_type: string                 # One of: first_contact, topic, milestone, distress, manual
trigger_conditions: object           # Type-specific trigger configuration
  topics: array[string]              # Keywords/phrases that activate (for topic type)
  milestones: array[string]          # Life events (for milestone type)
  distress_keywords: array[string]   # Emotional signals (for distress type)
  manual_phrase: string              # Exact phrase required (for manual type)
delivery_priority: integer           # Lower = higher priority (default: 5)
one_time_delivery: boolean           # If true, only delivered once per person (default: true)
```

### 3.2 Universal Body Structure

All reflection objects use this section order (from Universal Template Framework v1.1):
```markdown
## 0. Raw Input (Preserved)
[Original unedited text captured exactly as written/dictated]

---

## 1. Context
[Situational background, triggers, people involved, purpose]

---

## 2. Observations
[Factual, sensory, situational details without interpretation]

---

## 3. Reflection / Interpretation
[Meaning, emotional resonance, patterns, thematic connections]

---

## 4. Actions / Updates
[Follow-up tasks, next steps, maintenance, future revisit points]

---

## 5. Cross-References
[Links to related entries]

---

**Changelog**
- vX.Y — YYYY-MM-DD — [Description of change]
```

**Rules:**
- Sections may be empty but headers must exist.
- Raw Input is **append-only after creation**; use Actions/Updates or changelog for corrections.

### 3.3 Specialisation: Mirrorwell Reflection Template v1.2

**File naming:** `YYYY-MM-DD_reflection-slug.md` or `YYYY-MM-DD-HHMM_reflection-slug.md` for multiple same-day entries.

**Frontmatter example:**
```yaml
---
title: Reflections on Jessie's Last Day
vault: Mirrorwell
type: reflection
category: journaling
status: active
version: "1.2"
created: 2024-08-15
updated: 2024-08-15
tags: [grief, dogs, jessie, core-memory]
emotional_tags: [grief, love, acceptance]
shared_with: [theo, jono, wife]
related: ["[[Jessie - Core Memory]]", "[[Dogs as Emotional Anchors]]"]
source: internal
confidence: 1.0
revealed: true
core_memory: true
---
```

**Body:** Uses universal 0-5 structure exactly as specified.

---

## 4. Flows & Workflows

### 4.1 Reflection Object Lifecycle
```
1. Creation
   → User writes raw text (dictation, typing, transcript)
   → System wraps in template (or user uses template manually)
   → Frontmatter populated with required fields
   → Raw Input section = exact user text
   → File saved to Mirrorwell folder

2. Interpretation
   → Context/Observations/Reflection sections filled
   → Tags/cross-references added
   → Version remains X.0

3. Updates
   → Content added to Actions/Updates or new sections
   → Frontmatter `updated` timestamp changes
   → Minor version bump (X.Y → X.Y+1)
   → Changelog entry appended

4. Structural Change
   → Major refactor (new required field, section reorder)
   → Major version bump (X.Y → X+1.0)
   → Changelog documents breaking change
```

### 4.2 _inbox Packet Processing

**Purpose:** Mobile dictation or batch imports drop JSON packets into `_inbox/*.json`. Scripts process them into full reflection objects.

**Packet schema:**
```json
{
  "packet_id": "uuid-v4",
  "timestamp": "YYYY-MM-DDTHH:MM:SSZ",
  "type": "reflection",
  "payload": {
    "raw_input": "Exact transcription of user speech or text",
    "suggested_title": "Optional title hint",
    "tags": ["optional", "user-provided", "tags"],
    "metadata": {
      "source": "mobile_dictation",
      "location": "optional GPS or context",
      "emotional_state": "optional mood hint"
    }
  }
}
```

**Processing rules:**
1. Generate filename: `YYYY-MM-DD-HHMM_auto-slug.md`
2. Create frontmatter:
   - `vault` = `Mirrorwell`
   - `type` from packet
   - `title` = `payload.suggested_title` or auto-generated from first sentence
   - `created` = `timestamp` date
   - `updated` = `timestamp` date
   - `version` = `"1.0"`
   - `tags` = merge packet tags with auto-detected tags
   - `source` = `payload.metadata.source`
3. Body:
   - `## 0. Raw Input (Preserved)` = `payload.raw_input` (verbatim)
   - Sections 1-5 = empty or AI-generated initial pass
4. Save to `Mirrorwell/2_Reflection Library/YYYY/MM/` (or appropriate folder)
5. Append changelog: `v1.0 — YYYY-MM-DD — Created from _inbox packet [packet_id]`
6. Archive packet to `_inbox/processed/`

### 4.3 SQLite Index Generation

**Purpose:** `ehko_refresh.py` scans Mirrorwell, parses YAML + Markdown, populates SQLite for querying.

**Core tables:**
```sql
CREATE TABLE reflection_objects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT UNIQUE NOT NULL,
    vault TEXT NOT NULL,
    type TEXT NOT NULL,
    title TEXT NOT NULL,
    category TEXT,
    status TEXT NOT NULL,
    version TEXT NOT NULL,
    created DATE NOT NULL,
    updated DATE NOT NULL,
    source TEXT,
    confidence REAL,
    revealed BOOLEAN DEFAULT 1,
    raw_input_hash TEXT,  -- SHA256 of Raw Input section for change detection
    content_hash TEXT,    -- SHA256 of full file for change detection
    indexed_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    object_id INTEGER NOT NULL,
    tag TEXT NOT NULL,
    FOREIGN KEY (object_id) REFERENCES reflection_objects(id) ON DELETE CASCADE
);

CREATE TABLE cross_references (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id INTEGER NOT NULL,
    target_path TEXT NOT NULL,  -- Wiki-link target (may not exist yet)
    FOREIGN KEY (source_id) REFERENCES reflection_objects(id) ON DELETE CASCADE
);

CREATE TABLE changelog_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    object_id INTEGER NOT NULL,
    version TEXT NOT NULL,
    change_date DATE NOT NULL,
    description TEXT,
    FOREIGN KEY (object_id) REFERENCES reflection_objects(id) ON DELETE CASCADE
);

-- Mirrorwell extension table

CREATE TABLE mirrorwell_extensions (
    object_id INTEGER PRIMARY KEY,
    core_memory BOOLEAN DEFAULT 0,
    identity_pillar TEXT,
    core_memory_status TEXT,           -- nominated, curated, archived
    core_memory_themes TEXT,           -- JSON array of theme strings
    pillar_links TEXT,                 -- JSON array of pillar names
    index_priority INTEGER DEFAULT 3,  -- 1=highest, 5=lowest
    last_reviewed DATE,
    FOREIGN KEY (object_id) REFERENCES reflection_objects(id) ON DELETE CASCADE
);

CREATE TABLE emotional_tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    object_id INTEGER NOT NULL,
    emotion TEXT NOT NULL,
    FOREIGN KEY (object_id) REFERENCES reflection_objects(id) ON DELETE CASCADE
);

CREATE TABLE shared_with_friends (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    object_id INTEGER NOT NULL,
    friend_name TEXT NOT NULL,
    FOREIGN KEY (object_id) REFERENCES reflection_objects(id) ON DELETE CASCADE
);

-- Security & Authentication tables (see 1.3 Security & Ownership for full specification)

CREATE TABLE friend_registry (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    relationship_type TEXT,
    email TEXT UNIQUE NOT NULL,
    phone TEXT,
    access_level TEXT DEFAULT 'standard',
    blacklisted BOOLEAN DEFAULT 0,
    blacklist_reason TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_authenticated DATETIME,
    authentication_count INTEGER DEFAULT 0
);

CREATE TABLE shared_memories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    friend_id INTEGER NOT NULL,
    memory_file_path TEXT NOT NULL,
    specificity_score REAL,
    challenge_eligible BOOLEAN DEFAULT 1,
    times_used INTEGER DEFAULT 0,
    last_used DATETIME,
    FOREIGN KEY (friend_id) REFERENCES friend_registry(id) ON DELETE CASCADE
);

CREATE TABLE authentication_tokens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    token TEXT UNIQUE NOT NULL,
    friend_id INTEGER NOT NULL,
    claimed_identity TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME NOT NULL,
    used BOOLEAN DEFAULT 0,
    used_at DATETIME,
    ip_address TEXT,
    user_agent TEXT,
    FOREIGN KEY (friend_id) REFERENCES friend_registry(id) ON DELETE CASCADE
);

CREATE TABLE authentication_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    claimed_identity TEXT NOT NULL,
    friend_id INTEGER,
    authentication_method TEXT,
    success BOOLEAN NOT NULL,
    confidence_score REAL,
    challenge_memory_path TEXT,
    user_response TEXT,
    suspicious BOOLEAN DEFAULT 0,
    custodian_notified BOOLEAN DEFAULT 0,
    ip_address TEXT,
    user_agent TEXT,
    FOREIGN KEY (friend_id) REFERENCES friend_registry(id) ON DELETE SET NULL
);

CREATE TABLE custodians (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    relationship TEXT,
    email TEXT UNIQUE NOT NULL,
    phone TEXT,
    priority INTEGER,
    active BOOLEAN DEFAULT 1,
    handoff_date DATE,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Prepared Messages tables (see 1.5 Behaviour Engine Section 3.6)

CREATE TABLE prepared_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    addressed_to TEXT NOT NULL,           -- JSON array of names or ["*"]
    trigger_type TEXT NOT NULL,           -- first_contact, topic, milestone, distress, manual
    trigger_conditions TEXT,              -- JSON object with topics, milestones, etc.
    delivery_priority INTEGER DEFAULT 5,
    one_time_delivery BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE message_deliveries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message_id INTEGER NOT NULL,
    friend_id INTEGER NOT NULL,
    delivered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    trigger_context TEXT,                 -- What triggered delivery
    session_id TEXT,                      -- Link to conversation session
    FOREIGN KEY (message_id) REFERENCES prepared_messages(id) ON DELETE CASCADE,
    FOREIGN KEY (friend_id) REFERENCES friend_registry(id) ON DELETE CASCADE
);

-- Indexes for performance

CREATE INDEX idx_reflection_vault_type ON reflection_objects(vault, type, status);
CREATE INDEX idx_reflection_created ON reflection_objects(created);
CREATE INDEX idx_reflection_updated ON reflection_objects(updated);
CREATE INDEX idx_tags_lookup ON tags(tag);
CREATE INDEX idx_friend_email ON friend_registry(email);
CREATE INDEX idx_friend_name ON friend_registry(name);
CREATE INDEX idx_shared_memory_friend ON shared_memories(friend_id);
CREATE INDEX idx_shared_memory_eligible ON shared_memories(challenge_eligible);
CREATE INDEX idx_token ON authentication_tokens(token);
CREATE INDEX idx_token_expiry ON authentication_tokens(expires_at);
CREATE INDEX idx_auth_log_timestamp ON authentication_logs(timestamp);
CREATE INDEX idx_auth_log_suspicious ON authentication_logs(suspicious);
CREATE INDEX idx_prepared_addressed ON prepared_messages(addressed_to);
CREATE INDEX idx_prepared_trigger ON prepared_messages(trigger_type);
CREATE INDEX idx_prepared_priority ON prepared_messages(delivery_priority);
CREATE INDEX idx_delivery_message ON message_deliveries(message_id);
CREATE INDEX idx_delivery_friend ON message_deliveries(friend_id);
CREATE INDEX idx_delivery_timestamp ON message_deliveries(delivered_at);
```

**Indexing strategy:**
- Primary index on `(vault, type, status)`
- Full-text search on `title` + extracted section text (future: FTS5 virtual table)
- Tag lookup via `tags` join table
- Change detection via `raw_input_hash` and `content_hash`
- Friend authentication via `friend_registry` and `shared_memories`
- Security monitoring via `authentication_logs`

### 4.4 Query Examples

**Find all core memories:**
```sql
SELECT ro.title, ro.file_path 
FROM reflection_objects ro
JOIN mirrorwell_extensions me ON ro.id = me.object_id
WHERE me.core_memory = 1;
```

**Find all reflections tagged with grief:**
```sql
SELECT DISTINCT ro.title, ro.created
FROM reflection_objects ro
JOIN tags t ON ro.id = t.object_id
WHERE t.tag = 'grief'
ORDER BY ro.created DESC;
```

**Find all memories shared with a specific friend:**
```sql
SELECT ro.title, ro.created, ro.file_path
FROM reflection_objects ro
JOIN shared_with_friends swf ON ro.id = swf.object_id
WHERE swf.friend_name = 'theo'
ORDER BY ro.created DESC;
```

**Find high-specificity memories for authentication challenges:**
```sql
SELECT sm.memory_file_path, sm.specificity_score, fr.name
FROM shared_memories sm
JOIN friend_registry fr ON sm.friend_id = fr.id
WHERE sm.challenge_eligible = 1
  AND sm.specificity_score >= 0.70
  AND fr.name = 'theo'
ORDER BY sm.specificity_score DESC, sm.times_used ASC
LIMIT 5;
```

**Find all prepared messages for a specific friend:**
```sql
SELECT pm.title, pm.trigger_type, pm.file_path
FROM prepared_messages pm
WHERE pm.addressed_to LIKE '%"theo"%'
   OR pm.addressed_to = '["*"]'
ORDER BY pm.delivery_priority ASC;
```

**Find undelivered first-contact messages for a friend:**
```sql
SELECT pm.title, pm.file_path
FROM prepared_messages pm
WHERE pm.trigger_type = 'first_contact'
  AND (pm.addressed_to LIKE '%"theo"%' OR pm.addressed_to = '["*"]')
  AND pm.id NOT IN (
    SELECT message_id FROM message_deliveries md
    JOIN friend_registry fr ON md.friend_id = fr.id
    WHERE fr.name = 'theo'
  );
```

---

## 5. Data & Metadata

### 5.1 Metadata Hierarchy

**Truth source:**
- Markdown file YAML frontmatter

**Derived/Indexed:**
- SQLite database (rebuildable)
- Auto-generated tag clouds, link graphs, timelines

**Hidden/Veiled:**
- `revealed: false` objects excluded from public exports
- May have additional access control metadata (future: `access_level`, `reveal_conditions`)

### 5.2 Timestamp Rules

- `created`: Set once at object creation. **Never changes.**
- `updated`: Changes every time file is modified (content or frontmatter).
- Changelog entries include explicit dates for version bumps.

**Timezone handling:**
- All dates in YAML are `YYYY-MM-DD` (date only, no timezone).
- `_inbox` packet timestamps use ISO 8601 with timezone (`YYYY-MM-DDTHH:MM:SSZ`).
- Scripts convert to local date for `created`/`updated` fields.

### 5.3 Tag Taxonomies

**General tags:** Free-form folksonomy (lowercase, hyphenated).

**Mirrorwell recommended tags:**
- `core-memory`, `identity`, `trauma`, `growth`, `relationships`
- Emotional tags: `grief`, `anger`, `joy`, `clarity`, `confusion`, `shame`, `pride`

**EhkoForge recommended tags:**
- `architecture`, `template`, `framework`, `pinned`, `specification`

### 5.4 Confidence Scoring

**Default: 0.95** (high confidence in human-authored content)

**Lower confidence scenarios:**
- AI-generated initial interpretations: `0.70-0.80`
- Reconstructed memories from fragmentary notes: `0.60-0.70`
- Speculative or unverified family stories: `0.50-0.60`

**Usage:**
- Filters for "high confidence only" queries
- Visual indicators in UI (future: greyed-out low-confidence entries)
- Prompts for human review when confidence < 0.70

### 5.5 Friend Tagging & Shared Memories

**Purpose:** Enable contextual authentication (see 1.3 Security & Ownership)

**Frontmatter field:**
```yaml
shared_with: [theo, jono, wife, daughter]
```

**Processing:**
- `ehko_refresh.py` populates `shared_with_friends` table
- Links reflection objects to `friend_registry` entries
- Auto-populates `shared_memories` for authentication system

**Specificity scoring:**
Automatic algorithm assigns 0.0-1.0 score based on:
- Detail density (more sensory/factual details = higher score)
- Uniqueness (generic events like "went to pub" = lower score)
- Emotional specificity (vague "it was nice" vs detailed emotional arc)
- Proper nouns (specific locations, inside jokes, nicknames)

High-specificity memories (0.70+) are flagged as `challenge_eligible` for authentication.

---

## 6. Rules for Change

### 6.1 When to Bump Version

**Minor version (X.Y → X.Y+1):**
- Content added to any section except Raw Input
- New tags, cross-references, or metadata fields
- Changelog entry appended
- `updated` timestamp changes

**Major version (X.Y → X+1.0):**
- New required frontmatter field added
- Section structure changed (reordered, renamed, removed)
- Template schema breaking change
- All objects of this type must migrate or be marked deprecated

### 6.2 What Must Stay Stable

**Never change:**
- `created` timestamp
- `## 0. Raw Input (Preserved)` section content
- `file_path` (renaming = new object + archive old)

**Change with care:**
- `vault` (objects belong to their origin vault)
- `type` (changing type = potential schema mismatch)

### 6.3 Deprecation Process

1. Set `status: deprecated` in frontmatter
2. Add `deprecated_reason: "Explanation"` field
3. Link to replacement object in `related: []`
4. Append changelog entry documenting deprecation
5. Exclude from active queries (SQLite: `WHERE status = 'active'`)

### 6.4 Template Evolution

When Universal Template Framework or specialisation templates change:

1. Increment template version (e.g., v1.1 → v1.2)
2. Document changes in template's own changelog
3. Existing objects **do not auto-migrate**
4. New objects use new template version
5. Migration scripts (if needed) must be explicit, logged, reversible

### 6.5 Authentication Schema Changes

When friend registry or authentication tables change:

1. Major version bump for breaking changes (e.g., new required field)
2. Migration script must handle existing data
3. Backwards compatibility maintained where possible
4. Authentication logs preserved for audit trail

---

## 7. Open Questions / TODOs

### 7.1 Schema Gaps

- [ ] **Attachments/Media:** How to reference images, audio, PDFs? Inline base64? External file links?
- [ ] **Veiled content access control:** Define `reveal_conditions` schema (date-based, person-based, prompt-based?)
- [ ] **Multi-author objects:** Future scenario where Ehko writes back into vault. How to distinguish human vs AI authorship?

### 7.2 Performance Considerations

- [ ] **Large vaults:** What happens when Mirrorwell has 10,000+ reflections? SQLite sufficient or need vector DB?
- [ ] **Full-text search:** Implement FTS5 virtual table or use external search (Typesense, MeiliSearch)?
- [ ] **Incremental indexing:** `ehko_refresh.py` should only re-index changed files (hash comparison). Spec this out.

### 7.3 API Design

- [ ] **Read API:** RESTful endpoints for querying SQLite index?
- [ ] **Write API:** POST to `_inbox` vs direct file manipulation?
- [ ] **Conflict resolution:** What if mobile app and desktop Obsidian both edit same file?

### 7.4 Export Formats

- [ ] **Public Ehko export:** Generate static site from `revealed: true` objects only?
- [ ] **Archive format:** Zip bundle of markdown + SQLite + media?
- [ ] **JSON export:** For LLM fine-tuning or external systems?

### 7.5 Authentication & Prepared Messages Processing

- [ ] **Automatic friend detection:** Should `ehko_refresh.py` auto-populate `friend_registry` from `shared_with` fields?
- [ ] **Specificity scoring algorithm:** Define exact NLP/heuristic approach
- [ ] **Memory challenge selection:** Prioritise rarely-used memories to prevent predictability?
- [ ] **prepared_message indexing:** ehko_refresh.py must parse prepared_message type files and populate prepared_messages table
- [ ] **JSON field handling:** trigger_conditions and addressed_to stored as JSON strings for SQLite querying
- [ ] **Delivery sync:** message_deliveries table updated by Behaviour Engine, not ehko_refresh.py
- [ ] **Validation:** Verify addressed_to names exist in friend_registry (warn if not)

---

## 8. Cross-References

**Depends on:**
- [[1_0_Ehko_Manifest|Manifest]] — Durability principles (§4.5, §8)
- [[universal_template|Universal Template]] — Base schema this extends

**Schema consumers:**
- [[1_3_Security_Ownership|Security & Ownership]] — Uses friend_registry, authentication tables
- [[1_5_Behaviour_Engine_v1_1|Behaviour Engine]] — Uses prepared_messages, conversation state
- [[ehko_refresh.py|ehko_refresh.py]] — Implements indexing from this schema

**Vocabulary:**
- [[4_0_Lexicon_v1_0#5.1 Object Types|Object Types]] — Valid `type` values
- [[4_0_Lexicon_v1_0#5.2 Object Status|Object Status]] — Valid `status` values
- [[4_0_Lexicon_v1_0#4.2 Emotional Tags|Emotional Tags]] — `emotional_tags` vocabulary

**Navigation:**
- [[_Index|← Back to Index]]
- [[1_3_Security_Ownership|← Previous: Security]]
- [[1_5_Behaviour_Engine_v1_1|Next: Behaviour Engine →]]

---

**Changelog**
- v1.4 — 2025-12-03 — Added license split documentation (Section 1a); referenced Data_Model_Core_Tables_v1_0.md (MIT) and 2.0 Modules/ReCog/Ingot_System_Schema_v0_1.md (AGPL)
- v1.3 — 2025-11-29 — Integrated Core Memory Index framework: added core_memory_status, core_memory_themes, pillar_links, index_priority, last_reviewed fields to mirrorwell_extensions; see [[1_7_Core_Memory_Index_Framework_v1_0]]
- v1.2 — 2025-11-26 — Scope reduction: removed MonsterGarden and ManaCore vault references, plant_extensions and lore_extensions tables; simplified to Mirrorwell-only model; integrated prepared_messages tables from v1.2 patch; merged all query examples; cleaned up tag taxonomies
- v1.1 — 2025-11-25 — Integrated authentication schema from 1.3 Security & Ownership: added friend_registry, shared_memories, authentication_tokens, authentication_logs, custodians tables; added shared_with frontmatter field; added shared_with_friends table; updated cross-vault query examples
- v1.0 — 2025-11-23 — Initial data model specification

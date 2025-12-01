---
title: "1.7 Core Memory Index Framework"
vault: EhkoForge
type: module
category: System Architecture
status: active
version: "1.0"
created: 2025-11-29
updated: 2025-11-29
tags: [ehkoforge, core-memory, framework, architecture, pinned]
related: ["[[1_4_Data_Model_v1_1|Data Model]]", "[[1_6_Identity_Pillars_Scientific_Basis_v1_0|Identity Pillars]]"]
---

# 1.7 Core Memory Index Framework

## 1. Purpose

The Core Memory Index is the curated heart of Mirrorwell — a selective collection of memories that define who Brent is across time. Not every reflection is a core memory. Core memories are the formative moments, recurring patterns, and defining experiences that future visitors (or Brent himself) would need to understand to know him.

**The Core Memory Index sits between:**
- Raw reflections (Mirrorwell journal entries)
- Identity Pillars (abstracted patterns and values)

It answers: "Which specific memories matter most, and why?"

---

## 2. What Makes a Memory "Core"

### 2.1 Selection Criteria

A memory qualifies as **core** when it meets **two or more** of these criteria:

| Criterion | Description | Example |
|-----------|-------------|---------|
| **Formative** | Shaped identity, beliefs, or patterns | First major loss, career-defining moment |
| **Recurring** | Theme appears across multiple reflections | Pattern of boundary violations in relationships |
| **Emotionally Dense** | High emotional charge, even years later | Jessie's last day, father's funeral |
| **Relationship-Defining** | Shaped how Brent relates to others | Conflict with mother, friendship formation |
| **Self-Insight** | Moment of clarity about self | Realising ADHD patterns, recognising avoidance |
| **Values-Revealing** | Demonstrates core values in action | Standing up for someone, difficult ethical choice |

### 2.2 What Core Memory Is NOT

- **Not comprehensive:** A curated selection, not a complete history
- **Not static:** New core memories can be added; old ones can be archived
- **Not external validation:** Significant to Brent, not necessarily to outsiders
- **Not trauma-only:** Joyful, mundane, and transformative moments all qualify

---

## 3. Core Memory Lifecycle

```
1. NOMINATION
   Source: New reflection flagged with core_memory: true
   Or: Existing reflection promoted via manual review
   Status: core_memory_status: nominated

2. CURATION
   Action: Review against selection criteria
   Decision: Curate (→ curated) or Decline (→ remove flag)
   Requires: Assign themes, pillar links, priority
   Status: core_memory_status: curated

3. INTEGRATION
   Action: Add to Core Memory Index
   Action: Link to relevant Identity Pillars
   Action: Update cross-references

4. REVIEW
   Trigger: Periodic review (quarterly) or major life change
   Action: Re-evaluate priority, themes, pillar links
   Status: May be archived if superseded
```

---

## 4. Schema Extensions

### 4.1 Frontmatter Fields (Mirrorwell Reflections)

Add to existing `reflection_template.md`:

```yaml
# Core Memory curation (optional)
core_memory_status: nominated           # One of: nominated, curated, archived
core_memory_themes: []                  # Thematic tags for index grouping
pillar_links: []                        # Identity Pillars this memory informs
index_priority: 3                       # 1=highest, 5=lowest
last_reviewed: YYYY-MM-DD              # Last curation review date
```

### 4.2 Core Memory Index Structure

**Location:** `Mirrorwell/1_Core Identity/1.4 Core Memory Index/core_memory_index.md`

```markdown
---
title: Core Memory Index
vault: Mirrorwell
type: index
status: active
version: "1.0"
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [core-memory, index, identity]
---

# Core Memory Index

## Overview
Curated collection of formative memories that define identity across time.

**Total curated:** X memories
**Last review:** YYYY-MM-DD

---

## By Identity Pillar

### Web (Relationships)
- [[Memory Title]] — Brief context (Priority: X)
- [[Memory Title]] — Brief context (Priority: X)

### Thread (Continuity)
- [[Memory Title]] — Brief context (Priority: X)

### Mirror (Self-Perception)
- [[Memory Title]] — Brief context (Priority: X)

### Compass (Values)
- [[Memory Title]] — Brief context (Priority: X)

### Anchor (Stability)
- [[Memory Title]] — Brief context (Priority: X)

### Flame (Drive)
- [[Memory Title]] — Brief context (Priority: X)

---

## By Theme

### Family Dynamics
- [[Memory Title]] — Pillar: X

### Childhood & Formation
- [[Memory Title]] — Pillar: X

### Relationships & Belonging
- [[Memory Title]] — Pillar: X

### Career & Purpose
- [[Memory Title]] — Pillar: X

### Loss & Grief
- [[Memory Title]] — Pillar: X

### Growth & Insight
- [[Memory Title]] — Pillar: X

---

## Nominated (Pending Curation)
- [[Memory Title]] — Nominated YYYY-MM-DD

---

## Archived
- [[Memory Title]] — Archived YYYY-MM-DD, Reason: X

---

**Changelog**
- vX.Y — YYYY-MM-DD — Description
```

### 4.3 SQLite Schema Changes

Add to `mirrorwell_extensions` table:

```sql
ALTER TABLE mirrorwell_extensions ADD COLUMN core_memory_status TEXT;
ALTER TABLE mirrorwell_extensions ADD COLUMN core_memory_themes TEXT;   -- JSON array
ALTER TABLE mirrorwell_extensions ADD COLUMN pillar_links TEXT;         -- JSON array
ALTER TABLE mirrorwell_extensions ADD COLUMN index_priority INTEGER;
ALTER TABLE mirrorwell_extensions ADD COLUMN last_reviewed DATE;

-- Index for curation queries
CREATE INDEX idx_core_memory_status ON mirrorwell_extensions(core_memory_status);
CREATE INDEX idx_core_memory_priority ON mirrorwell_extensions(index_priority);
```

---

## 5. Curation Workflow

### 5.1 Nomination

When creating a new reflection, set:
```yaml
core_memory: true
core_memory_status: nominated
```

Or flag existing reflection manually.

### 5.2 Curation Review

Review nominated memories against Section 2.1 criteria.

**For each nominated memory:**
1. Does it meet ≥2 selection criteria?
2. Which Identity Pillars does it inform?
3. What themes does it belong to?
4. What priority (1-5)?

**If curating:**
```yaml
core_memory_status: curated
core_memory_themes: [family-dynamics, self-insight]
pillar_links: [mirror, web]
index_priority: 2
last_reviewed: 2025-11-29
```

**If declining:**
Remove `core_memory: true` flag or set:
```yaml
core_memory_status: archived
```

### 5.3 Index Update

After curating memories:
1. Add entry to `core_memory_index.md` under appropriate Pillar and Theme sections
2. Include brief context and priority
3. Update "Total curated" count
4. Update "Last review" date

---

## 6. Relationship to Identity Pillars

The six Identity Pillars (from 1.6 Identity Pillars Scientific Basis):

| Pillar | Domain | Core Memory Connection |
|--------|--------|------------------------|
| **Web** | Relationships | Memories about connections, belonging, social bonds |
| **Thread** | Continuity | Memories linking past-present-future self |
| **Mirror** | Self-Perception | Moments of self-insight, identity recognition |
| **Compass** | Values | Experiences that revealed or tested core values |
| **Anchor** | Stability | Memories providing grounding, security, resilience |
| **Flame** | Drive | Moments of motivation, purpose, passion |

A single core memory may link to multiple pillars.

---

## 7. Query Examples

**Find all curated core memories:**
```sql
SELECT ro.title, ro.file_path, me.pillar_links, me.index_priority
FROM reflection_objects ro
JOIN mirrorwell_extensions me ON ro.id = me.object_id
WHERE me.core_memory_status = 'curated'
ORDER BY me.index_priority ASC, ro.created DESC;
```

**Find core memories for a specific pillar:**
```sql
SELECT ro.title, ro.file_path
FROM reflection_objects ro
JOIN mirrorwell_extensions me ON ro.id = me.object_id
WHERE me.core_memory_status = 'curated'
  AND me.pillar_links LIKE '%"web"%'
ORDER BY me.index_priority ASC;
```

**Find nominated memories pending curation:**
```sql
SELECT ro.title, ro.created, ro.file_path
FROM reflection_objects ro
JOIN mirrorwell_extensions me ON ro.id = me.object_id
WHERE me.core_memory_status = 'nominated'
ORDER BY ro.created DESC;
```

---

## 8. Open Questions

- [ ] **Curation assistance:** Should `ehko_refresh.py` suggest core memory candidates based on emotional_tags density?
- [ ] **Auto-theming:** Can themes be auto-suggested from existing tags?
- [ ] **Pillar linking:** Should Ehko (AI) suggest pillar connections during curation?
- [ ] **Review cadence:** Quarterly? Triggered by major life events?

---

## 9. Cross-References

**Depends on:**
- [[1_4_Data_Model_v1_1|Data Model]] — Schema definitions
- [[1_6_Identity_Pillars_Scientific_Basis_v1_0|Identity Pillars]] — Six-pillar framework

**Consumers:**
- [[reflection_template|Reflection Template]] — Adds optional frontmatter fields
- [[ehko_refresh.py|ehko_refresh.py]] — Indexes core memory fields

**Navigation:**
- [[_Index|← Back to Index]]
- [[1_6_Identity_Pillars_Scientific_Basis_v1_0|← Previous: Identity Pillars]]

---

**Changelog**
- v1.0 — 2025-11-29 — Initial framework specification: selection criteria, lifecycle, schema extensions, curation workflow, pillar relationships

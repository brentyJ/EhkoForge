---
title: "Core Data Model Tables"
vault: "EhkoForge"
type: "module"
category: "System Architecture"
status: active
version: "1.0"
created: 2025-12-03
updated: 2025-12-03
tags: [ehkoforge, schema, database, core]
related:
  - "1_4_Data_Model_v1_3.md"
  - "2.0 Modules/ReCog/Ingot_System_Schema_v0_1.md"
license: "MIT"
---

# CORE DATA MODEL TABLES v1.0

## 1. Overview

This document defines the MIT-licensed core database schema for EhkoForge. These tables provide the foundational data structures for identity preservation and reflection storage.

**License:** MIT — Free to use, modify, and distribute.

For ReCog Engine tables (ingot processing, smelt queue, personality layers), see:
`2.0 Modules/ReCog/Ingot_System_Schema_v0_1.md` (AGPLv3 licensed)

---

## 2. Core Tables

### 2.1 `reflection_objects`

The primary index of all vault content.

```sql
CREATE TABLE reflection_objects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT UNIQUE NOT NULL,
    title TEXT,
    vault TEXT NOT NULL,
    type TEXT,
    category TEXT,
    status TEXT DEFAULT 'active',
    version TEXT,
    created_date TEXT,
    updated_date TEXT,
    source TEXT,
    confidence REAL,
    revealed INTEGER DEFAULT 1,
    content_hash TEXT,
    indexed_at TEXT NOT NULL,
    word_count INTEGER
);

CREATE INDEX idx_reflection_objects_vault ON reflection_objects(vault);
CREATE INDEX idx_reflection_objects_type ON reflection_objects(type);
CREATE INDEX idx_reflection_objects_status ON reflection_objects(status);
```

**Field notes:**
- `file_path` is the canonical identifier (relative to vault root)
- `content_hash` enables efficient change detection
- `revealed` controls visibility (0 = veiled/private)

---

### 2.2 `tags`

General-purpose tagging for reflection objects.

```sql
CREATE TABLE tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    object_id INTEGER NOT NULL,
    tag TEXT NOT NULL,
    FOREIGN KEY (object_id) REFERENCES reflection_objects(id) ON DELETE CASCADE,
    UNIQUE(object_id, tag)
);

CREATE INDEX idx_tags_object ON tags(object_id);
CREATE INDEX idx_tags_tag ON tags(tag);
```

---

### 2.3 `emotional_tags`

Emotional markers for reflections.

```sql
CREATE TABLE emotional_tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    object_id INTEGER NOT NULL,
    emotion TEXT NOT NULL,
    FOREIGN KEY (object_id) REFERENCES reflection_objects(id) ON DELETE CASCADE,
    UNIQUE(object_id, emotion)
);

CREATE INDEX idx_emotional_tags_object ON emotional_tags(object_id);
CREATE INDEX idx_emotional_tags_emotion ON emotional_tags(emotion);
```

---

### 2.4 `cross_references`

Links between reflection objects.

```sql
CREATE TABLE cross_references (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id INTEGER NOT NULL,
    target_path TEXT NOT NULL,
    link_type TEXT DEFAULT 'related',
    FOREIGN KEY (source_id) REFERENCES reflection_objects(id) ON DELETE CASCADE
);

CREATE INDEX idx_cross_references_source ON cross_references(source_id);
CREATE INDEX idx_cross_references_target ON cross_references(target_path);
```

**Link types:**
- `related` — general relationship
- `extends` — builds upon target
- `contradicts` — conflicts with target
- `responds_to` — direct reply/continuation

---

### 2.5 `changelog_entries`

Version history for reflection objects.

```sql
CREATE TABLE changelog_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    object_id INTEGER NOT NULL,
    version TEXT NOT NULL,
    date TEXT NOT NULL,
    description TEXT,
    FOREIGN KEY (object_id) REFERENCES reflection_objects(id) ON DELETE CASCADE
);

CREATE INDEX idx_changelog_object ON changelog_entries(object_id);
```

---

### 2.6 `mirrorwell_extensions`

Additional metadata for personal reflections (Mirrorwell vault).

```sql
CREATE TABLE mirrorwell_extensions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    object_id INTEGER UNIQUE NOT NULL,
    core_memory INTEGER DEFAULT 0,
    identity_pillar TEXT,
    shared_with_json TEXT,
    FOREIGN KEY (object_id) REFERENCES reflection_objects(id) ON DELETE CASCADE
);

CREATE INDEX idx_mirrorwell_core_memory ON mirrorwell_extensions(core_memory);
CREATE INDEX idx_mirrorwell_pillar ON mirrorwell_extensions(identity_pillar);
```

**Field notes:**
- `core_memory` flags entries for the Core Memory Index
- `identity_pillar` links to Identity Pillar categories
- `shared_with_json` stores access control list

---

## 3. Session Tables

### 3.1 `forge_sessions`

Chat session tracking.

```sql
CREATE TABLE forge_sessions (
    id TEXT PRIMARY KEY,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    title TEXT,
    message_count INTEGER DEFAULT 0,
    word_count INTEGER DEFAULT 0,
    status TEXT DEFAULT 'active'
);

CREATE INDEX idx_forge_sessions_updated ON forge_sessions(updated_at DESC);
CREATE INDEX idx_forge_sessions_status ON forge_sessions(status);
```

---

### 3.2 `forge_messages`

Individual messages within sessions.

```sql
CREATE TABLE forge_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    word_count INTEGER,
    FOREIGN KEY (session_id) REFERENCES forge_sessions(id) ON DELETE CASCADE
);

CREATE INDEX idx_forge_messages_session ON forge_messages(session_id, timestamp);
```

---

## 4. Authentication Tables

### 4.1 `friend_registry`

Known people for sharing.

```sql
CREATE TABLE friend_registry (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE,
    relationship TEXT,
    access_level TEXT DEFAULT 'visitor',
    created_at TEXT NOT NULL,
    last_access_at TEXT
);
```

---

### 4.2 `authentication_tokens`

Active session tokens.

```sql
CREATE TABLE authentication_tokens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    friend_id INTEGER,
    token_hash TEXT UNIQUE NOT NULL,
    created_at TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    last_used_at TEXT,
    FOREIGN KEY (friend_id) REFERENCES friend_registry(id) ON DELETE CASCADE
);
```

---

### 4.3 `custodians`

Posthumous access control.

```sql
CREATE TABLE custodians (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    friend_id INTEGER NOT NULL,
    role TEXT NOT NULL,
    permissions_json TEXT,
    activated INTEGER DEFAULT 0,
    activated_at TEXT,
    FOREIGN KEY (friend_id) REFERENCES friend_registry(id) ON DELETE CASCADE
);
```

---

### 4.4 `prepared_messages`

Time-capsule messages for future delivery.

```sql
CREATE TABLE prepared_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recipient_id INTEGER NOT NULL,
    subject TEXT,
    content TEXT NOT NULL,
    trigger_type TEXT NOT NULL,
    trigger_date TEXT,
    trigger_event TEXT,
    created_at TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    FOREIGN KEY (recipient_id) REFERENCES friend_registry(id) ON DELETE CASCADE
);
```

---

## 5. Schema Split Reference

| License | Tables | Location |
|---------|--------|----------|
| **MIT** | reflection_objects, tags, emotional_tags, cross_references, changelog_entries, mirrorwell_extensions, forge_sessions, forge_messages, friend_registry, authentication_tokens, custodians, prepared_messages | This document |
| **AGPLv3** | smelt_queue, transcript_segments, annotations, ingots, ingot_sources, ingot_history, ehko_personality_layers | `2.0 Modules/ReCog/Ingot_System_Schema_v0_1.md` |

---

## 6. Migration

These tables are created by `ehko_refresh.py` on first run. No separate migration required for core tables.

For ReCog tables, run:
```bash
python run_ingot_migration.py
```

---

**Changelog**
- v1.0 — 2025-12-03 — Extracted from Data Model v1.3 as MIT-licensed core schema

---
title: "ehko_refresh.py Specification"
vault: EhkoForge
type: module
category: scripts
status: active
version: "1.0"
created: 2025-11-26
updated: 2025-11-26
tags: [ehkoforge, scripts, indexing, sqlite, automation]
related: ["[[1_4_Data_Model_v1_1]]", "[[1_3_Security_Ownership]]"]
---

# {{title}}

## 1. Purpose & Scope

**This module documents the `ehko_refresh.py` indexing script — the keystone automation for EhkoForge.**

It specifies:
- What the script does
- How to run it
- Dependencies and installation
- Configuration options
- Database schema implementation
- Error handling behaviour

---

## 2. Core Principles

### 2.1 Files Are Truth
SQLite is derived from markdown files. The index can always be rebuilt from vault contents.

### 2.2 Incremental by Default
Only re-index files whose content hash has changed. Full rebuild available via `--full` flag.

### 2.3 Non-Destructive
Script never modifies source markdown files. Only reads and populates the index.

### 2.4 Fail-Safe
Individual file errors don't halt the entire process. Errors are logged and skipped.

---

## 3. Installation

### 3.1 Dependencies

```bash
pip install pyyaml
```

### 3.2 Location

```
EhkoForge/
└── 5.0 Scripts/
    └── ehko_refresh.py
```

### 3.3 Database Location

```
EhkoForge/
└── _data/
    └── ehko_index.db
```

---

## 4. Usage

### 4.1 Basic Commands

```bash
# Incremental update (default)
python ehko_refresh.py

# Full rebuild (ignore cached hashes)
python ehko_refresh.py --full

# Show statistics only (no indexing)
python ehko_refresh.py --report
```

### 4.2 Running from Any Directory

The script auto-detects vault locations relative to its own path. Run from anywhere:

```bash
cd "G:\Other computers\Ehko\Obsidian\EhkoForge\5.0 Scripts"
python ehko_refresh.py
```

---

## 5. What It Indexes

### 5.1 Vaults Scanned

| Vault | Path |
|-------|------|
| EhkoForge | `../EhkoForge/` |
| Mirrorwell | `../Mirrorwell/` |

### 5.2 Files Processed

- All `.md` files with valid YAML frontmatter
- Required frontmatter fields: `title`, `vault`, `type`, `status`, `version`, `created`, `updated`

### 5.3 Files Skipped

- Directories: `.obsidian`, `_inbox`, `attachments`, `archive`, `_data`, `_ledger`
- Files: `index.md`, `README.md`, `Start Here.md`
- Files without frontmatter
- Files missing required fields

---

## 6. Database Schema

Implements the full schema from **1.4 Data Model v1.1**:

### 6.1 Core Tables

| Table | Purpose |
|-------|---------|
| `reflection_objects` | All indexed markdown files |
| `tags` | Folksonomy tags per object |
| `cross_references` | Wiki-link relationships |
| `changelog_entries` | Version history per object |

### 6.2 Mirrorwell Extensions

| Table | Purpose |
|-------|---------|
| `mirrorwell_extensions` | Core memory flags, identity pillar links |
| `emotional_tags` | Emotion markers per object |
| `shared_with_friends` | Friend mentions for authentication |

### 6.3 Authentication Tables

| Table | Purpose |
|-------|---------|
| `friend_registry` | Known friends/family |
| `shared_memories` | Memory-to-friend links for challenges |
| `authentication_tokens` | Email verification tokens |
| `authentication_logs` | Security audit trail |
| `custodians` | Handoff management |

### 6.4 Prepared Messages

| Table | Purpose |
|-------|---------|
| `prepared_messages` | Messages left for specific people/triggers |
| `message_deliveries` | Delivery tracking |

---

## 7. Extracted Data

### 7.1 From Frontmatter

All standard and vault-specific fields defined in 1.4 Data Model.

### 7.2 From Body

| Data | Extraction Method |
|------|-------------------|
| Raw Input | Section `## 0. Raw Input` parsed |
| Wiki-links | `[[target]]` pattern matching |
| Changelog | `**Changelog**` section parsing |

### 7.3 Calculated Fields

| Field | Calculation |
|-------|-------------|
| `content_hash` | SHA256 of full file |
| `raw_input_hash` | SHA256 of Raw Input section |
| `specificity_score` | Heuristic based on detail density (for authentication) |

---

## 8. Specificity Scoring

Used to determine which memories are suitable for authentication challenges.

### 8.1 Algorithm

```
Base score: 0.5

Positive modifiers:
  +0.15  3+ proper nouns detected
  +0.10  Specific dates/times mentioned
  +0.10  Dialogue or quotes present
  +0.10  Sensory details (saw, heard, felt, etc.)
  +0.05  Deep emotional vocabulary

Negative modifiers:
  -0.15  Generic events (birthday, christmas, dinner)
  -0.15  Raw input < 100 characters
  -0.10  No people mentioned

Range: 0.0 to 1.0
Challenge eligible threshold: 0.70
```

---

## 9. Error Handling

| Scenario | Behaviour |
|----------|-----------|
| Missing frontmatter | Skip file, log warning |
| Missing required field | Skip file, log which fields missing |
| YAML parse error | Skip file, log error |
| File read error | Skip file, log error, continue |
| Database error | Log error, may halt depending on severity |

---

## 10. Output

### 10.1 Console Output

```
============================================================
EHKO REFRESH — Indexing Started
============================================================
Mode: Incremental
Database: G:\...\EhkoForge\_data\ehko_index.db

Scanning EhkoForge...
  Found 8 files
  INDEXED: 1_0_Ehko_Manifest.md
  INDEXED: 1_1_Overview_v1_0.md
  ...

Scanning Mirrorwell...
  Found 3 files
  INDEXED: 2025-11-22 – Growing Up in the 90s.md
  ...

Updating shared memories linkage...

============================================================
EHKO INDEX REPORT
============================================================

Indexing Results:
  Scanned:  11
  Indexed:  9
  Skipped:  2
  Deleted:  0
  Errors:   0

Index Contents:
  Total Objects:    9
  Unique Tags:      24
  Cross-References: 12
  Friends:          0
  Prepared Msgs:    0

By Vault:
  EhkoForge: 7
  Mirrorwell: 2

By Type:
  module: 7
  reflection: 2

============================================================
Done.
```

---

## 11. Future Enhancements

- [ ] Full-text search index (FTS5 virtual table)
- [ ] Vector embeddings for semantic search
- [ ] Watch mode (file system monitoring)
- [ ] Export to JSON for external tools
- [ ] Specificity score stored during indexing (currently calculated but not persisted)

---

**Changelog**
- v1.0 — 2025-11-26 — Initial implementation: full schema, incremental indexing, specificity scoring, report generation

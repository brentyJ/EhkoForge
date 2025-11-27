---
title: "Indexing Scripts Overview"
vault: EhkoForge
type: module
category: scripts
status: active
version: "1.0"
created: 2025-11-26
updated: 2025-11-26
tags: [ehkoforge, scripts, indexing, overview]
related: ["[[ehko_refresh.py]]"]
---

# {{title}}

## 1. Purpose & Scope

**Index of all indexing and automation scripts for EhkoForge.**

---

## 2. Script Registry

| Script | Status | Purpose |
|--------|--------|---------|
| `ehko_refresh.py` | ✅ Active | Core indexing — scans vaults, populates SQLite |
| `inbox_processor.py` | 🔜 Planned | Process `_inbox/` JSON packets into reflections |
| `export_archive.py` | 🔜 Planned | Generate portable archive bundles |

---

## 3. Running Scripts

All scripts are Python 3.x and should be run from this directory:

```bash
cd "G:\Other computers\Ehko\Obsidian\EhkoForge\5.0 Scripts"
py <script_name>.py
```

### Dependencies

```bash
py -m pip install pyyaml
```

---

## 4. Database Location

```
EhkoForge/_data/ehko_index.db
```

SQLite database. Can be browsed with DB Browser for SQLite or queried via Python.

---

**Changelog**
- v1.0 — 2025-11-26 — Initial index created

---
title: EhkoForge Index
vault: EhkoForge
type: index
status: active
version: "1.2"
created: 2025-11-28
updated: 2025-11-29
tags:
  - ehkoforge
  - pinned
  - navigation
  - index
---
# EhkoForge Index

> Central navigation hub for all EhkoForge system documentation.

---

## Core Architecture (1.x)

| Module | Purpose |
|--------|---------|
| [[1_0_Ehko_Manifest\|Manifest]] | Philosophy, ethics, design principles |
| [[1_0a_Ehko_Manifesto_Personal\|Personal Manifesto]] | Brent's personal origin story |
| [[1_1_Overview_v1_0\|Overview]] | Architecture overview, module index |
| [[1_2_Components_v1_0\|Components]] | System parts and relationships |
| [[1_3_Security_Ownership\|Security & Ownership]] | Authentication, access control, custodians |
| [[1_4_Data_Model_v1_3\|Data Model]] | Schemas, SQLite, packet processing |
| [[1_5_Behaviour_Engine_v1_1\|Behaviour Engine]] | AI interaction rules, voice, personality |
| [[1_6_Identity_Pillars_Scientific_Basis_v1_0\|Identity Pillars]] | Scientific basis for identity framework |
| [[1_7_Core_Memory_Index_Framework_v1_0\|Core Memory Index]] | Framework for curating formative memories |

---

## Feature Specifications (2.x)

| Module | Purpose |
|--------|---------|
| [[UI-MDV-Specification\|UI-MDV Spec]] | Minimum Durable Version interface design |
| [[Frontend_Implementation_Spec_v1_0\|Frontend Implementation]] | Technical frontend specification |
| [[SPINOFF_IDEAS\|Spinoff Ideas]] | Future feature concepts |

---

## Templates (3.x)

| Template | Purpose |
|----------|---------|
| [[universal_template\|Universal Template]] | Base template for all reflection objects |

**Mirrorwell Templates** (in Mirrorwell vault):
- `reflection_template.md` — Standard reflection entry

---

## Reference (4.x)

| Module | Purpose |
|--------|---------|
| [[4_0_Lexicon_v1_0\|Lexicon]] | Terminology, tag taxonomies, controlled vocabularies |

---

## Scripts & Automation (5.x)

| Script | Purpose |
|--------|---------|
| [[ehko_refresh.py\|ehko_refresh.py]] | Main indexer — scans vaults, populates SQLite |
| [[ehko_refresh.py.md\|ehko_refresh.py docs]] | Documentation for the indexer |
| [[indexing scripts\|Indexing Scripts]] | Supporting index utilities |
| [[misc utilities\|Misc Utilities]] | Helper scripts |

---

## Frontend (6.x)

Located in `6.0 Frontend/static/`:
- `index.html` — Entry point
- `styles.css` — Styling
- `app.js` — Application logic

---

## Key Concepts (Quick Links)

**Identity & Content:**
- [[1_5_Behaviour_Engine_v1_1#3.6 Prepared Messages System|Prepared Messages]] — Direct messages for future delivery
- [[1_3_Security_Ownership|Veiled Content]] — Hidden content with conditional reveal
- [[1_4_Data_Model_v1_3#3.1 Universal Reflection Object Schema|Reflection Object Schema]] — Canonical data structure

**Authentication:**
- [[1_3_Security_Ownership|Contextual Authentication]] — Memory-based identity verification
- [[1_4_Data_Model_v1_3#friend_registry|Friend Registry]] — Known people database

**Voice & Behaviour:**
- [[1_5_Behaviour_Engine_v1_1#2.6 Speaking For, Not Speaking As|Voice Distinction]] — Third-person rule
- [[1_5_Behaviour_Engine_v1_1#3.2 Conversation Modes|Conversation Modes]] — Reflection, Legacy, Support

---

## Status Overview

| Area | Status |
|------|--------|
| Core Architecture | ✅ Complete |
| Data Model | ✅ Complete |
| Behaviour Engine | ✅ Complete |
| Security Spec | ✅ Complete |
| Lexicon | ✅ Complete |
| Templates | ✅ Complete |
| Indexing Scripts | ✅ Working |
| Frontend | 🔄 In Progress |
| Recovery/Export | 📋 Planned |

---

## See Also

- [[PROJECT_STATUS|Project Status]] — Current implementation state
- [[README|README]] — Repository overview

---

**Changelog**
- v1.2 — 2025-11-29 — Updated Data Model links (v1_1→v1_3)
- v1.1 — 2025-11-29 — Added 1_7 Core Memory Index Framework
- v1.0 — 2025-11-28 — Initial index created

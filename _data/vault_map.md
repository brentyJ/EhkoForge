---
title: "EhkoForge Vault Map"
vault: "EhkoForge"
type: "system"
category: "_data"
status: "active"
version: "2.5"
created: 2025-11-29
updated: 2025-12-03
tags: [system, reference, navigation]
---

# EHKOFORGE VAULT MAP

**Purpose:** Lightweight reference for vault structure. Loaded at session start instead of filesystem scanning.
**Update frequency:** After major structural changes or weekly.
**Generated:** 2025-12-03 (Session 17 - Reorientation Phase 1)

---

## ROOT STRUCTURE

```
G:\Other computers\Ehko\Obsidian\
├── EhkoForge/          [System framework vault]
├── Mirrorwell/         [Personal content vault]
├── MonsterGarden/      [DORMANT - Future plant tracking]
└── ManaCore/           [DORMANT - Fiction worldbuilding]
```

---

## LICENSE STRUCTURE

EhkoForge uses split licensing:

| Component | License | Location |
|-----------|---------|----------|
| Framework (core) | MIT | `EhkoForge/LICENSE` |
| ReCog Engine (code) | AGPLv3 | `5.0 Scripts/recog_engine/LICENSE` |
| ReCog Engine (specs) | AGPLv3 | `2.0 Modules/ReCog/LICENSE` |

---

## EHKOFORGE VAULT

### 1.0 System Architecture/
**Purpose:** Core specifications and canonical modules

```
1_0_Ehko_Manifest.md                              [canonical, v2.1]
1_0a_Ehko_Manifesto_Personal.md                   [essay, v1.0]
1_1_Overview_v1_0.md                              [module, v1.1]
1_2_Components_v1_0.md                            [module, v1.1]
1_3_Security_Ownership.md                         [module, v1.0]
1_4_Data_Model_v1_4.md                            [module, v1.4]
1_5_Behaviour_Engine_v1_1.md                      [module, v1.1]
1_6_Identity_Pillars_Scientific_Basis_v1_0.md     [module, v1.0]
1_7_Core_Memory_Index_Framework_v1_0.md           [module, v1.0]
Data_Model_Core_Tables_v1_0.md                    [module, v1.0] — MIT schema
_Index.md                                         [navigation, v1.0]
```

### 2.0 Modules/
**Purpose:** Feature specifications and extensions

```
Frontend_Implementation_Spec_v1_0.md              [module, v1.0]
UI-MDV-Specification.md                           [module, v1.0]
SPINOFF_IDEAS.md                                  [planning, v1.0]
Ideas for road mapping - Proko & Evolution Concept Scaffold.md  [concept, draft]
Forge_UI_Update_Spec_v0_1.md                      [module, v0.1] — UI design

# ReCog Engine (AGPL-licensed)
ReCog/
├── LICENSE                                       [AGPLv3]
├── ReCog_Engine_Spec_v0_2.md                     [module, v0.2] — Recursive cognition
├── Ingot_System_Schema_v0_1.md                   [module, v0.1] — DB tables
├── Tier0_PreAnnotation_Spec_v0_1.md              [module, v0.1] — Signal extraction
└── Smelt_Processor_Spec_v0_1.md                  [module, v0.1] — Batch processing
```

### 3.0 Templates/
**Purpose:** Universal templates and frameworks

```
Universal/
  └── universal_template.md                       [framework, v1.2]
```

### 4.0 Lexicon/
**Purpose:** Controlled vocabularies and taxonomies

```
4_0_Lexicon_v1_0.md                               [reference, v1.0]
```

### 5.0 Scripts/
**Purpose:** Automation, server, and utilities

#### Root Scripts
```
ehko_refresh.py                   [v2.0, working] — Vault indexing + transcription processing
forge_server.py                   [v2.1, working] — Flask server + Authority/Mana + Insite endpoints
ehko_control.py                   [v2.0, working] — GUI control panel (tkinter, touch-optimized)
EhkoForge Control Panel.vbs       [v1.0, working] — Silent launcher (no console window)
run_ingot_migration.py            [v1.0, working] — DB migration runner
run_reorientation_migration.py    [v1.0, working] — Reorientation migration runner
seed_test_ingots.py               [v1.0, utility]  — Test data generator
.env                              [config]        — API keys (not in git)

# Utility scripts
fix_regex.py                      [applied] — Patch theme extraction
fix_theme_headers.py              [applied] — Header level fix
fix_transcription_extraction.py   [applied] — Section boundary fix
run_process_transcriptions.bat    [working] — Batch runner
```

#### recog_engine/ Module (AGPL-licensed)
```
recog_engine/
├── LICENSE                       [AGPLv3]
├── __init__.py
├── tier0.py                      [v0.1, working] — Signal extraction (no LLM)
├── smelt.py                      [v0.1, working] — Batch ingot extraction
├── prompts.py                    [v0.2, working] — Stage-based personality dampener
├── authority_mana.py             [v0.1, working] — Authority & Mana systems
└── forge_integration.py          [v0.1, guide]   — Server integration helpers
```

#### ehkoforge/ Module (MIT-licensed)
```
ehkoforge/
├── __init__.py
├── llm/                          [v1.1, working] — Multi-provider LLM integration
│   ├── __init__.py
│   ├── base.py                   — Abstract provider interface
│   ├── claude_provider.py        — Anthropic API wrapper
│   ├── openai_provider.py        — OpenAI API wrapper
│   ├── provider_factory.py       — Role-based provider instantiation
│   ├── context_builder.py        — Reflection corpus search
│   └── config.py                 — API key + role routing
├── preprocessing/                [redirects to recog_engine]
│   └── __init__.py               — Import redirect notice
└── processing/                   [redirects to recog_engine]
    └── __init__.py               — Import redirect notice
```

#### migrations/
```
migrations/
├── ingot_migration_v0_1.sql      [applied] — Ingot system tables
└── reorientation_v0_1.sql        [applied] — Authority/Mana/Insite tables
```

#### Documentation (in 5.0 Scripts/)
```
ehko_refresh.py.md                [specification, v1.0]
indexing scripts.md               [overview, v1.0]
misc utilities.md                 [utilities, draft]

System Logs/
  └── vault_actions.md            [log, v1.0]
```

### 6.0 Frontend/
**Purpose:** Three-area Web UI (Reflect, Forge, Terminal)

```
templates/                        [v2.0]
├── base.html                     — Shared layout + nav bar
├── reflect.html                  — Reflect area (chat, journal, upload)
├── forge.html                    — Forge area (ingot review)
└── terminal.html                 — Terminal area (general AI chat)

static/
├── css/                          [v2.0]
│   ├── base.css                  — Shared styles (nav, layout, modals)
│   ├── reflect.css               — Reflect area (teal palette)
│   ├── forge.css                 — Forge area (gold/violet palette)
│   └── terminal.css              — Terminal area (blue retro palette)
├── js/                           [v2.0]
│   ├── common.js                 — Shared utilities (config, stats, API)
│   ├── reflect.js                — Reflect chat logic
│   ├── forge.js                  — Ingot review logic
│   ├── terminal.js               — Terminal chat logic
│   └── journal.js                — Journal calendar + CRUD
├── index.html                    [v1.2, legacy] — Old single-page UI
├── styles.css                    [v1.2, legacy] — Old combined styles
└── app.js                        [v1.2, legacy] — Old combined logic
```

**Architecture (v2.0):**
- Route-based navigation: `/reflect`, `/forge`, `/terminal`
- Jinja2 templates with base inheritance
- Area-specific palettes:
  - Reflect: Teal (#5fb3a1)
  - Forge: Gold/Violet (#c9a962, #9b7ed9)
  - Terminal: Blue retro (#6b8cce)

**Features:**
- **Reflect:** Chat, Journal (calendar), Upload (drag-drop)
- **Forge:** Ingot queue, detail panel, accept/reject, smelt status
- **Terminal:** Model selector, retro aesthetic, model-switch modal
- **Common:** Nav bar, Ehko avatar, stats bar, settings modal

### Config/
**Purpose:** Configuration files

```
ui-preferences.json               [user settings]
```

### _data/
**Purpose:** Database and system files

```
ehko_index.db                     [SQLite, ~200KB]
vault_map.md                      [this file]
script_registry.md                [v1.0] — Compressed script reference
db_schema_summary.md              [v1.0] — Compressed DB schema reference
```

### PROJECT_STATUS.md
**Purpose:** Current implementation state and priorities
**Location:** `EhkoForge/PROJECT_STATUS.md`
**Version:** 1.13

---

## DATABASE SCHEMA

### License Split

| License | Tables |
|---------|--------|
| **MIT** | reflection_objects, tags, emotional_tags, cross_references, changelog_entries, mirrorwell_extensions, forge_sessions, forge_messages, friend_registry, shared_with_friends, shared_memories, authentication_tokens, authentication_logs, custodians, prepared_messages, message_deliveries |
| **AGPLv3** | smelt_queue, transcript_segments, annotations, ingots, ingot_sources, ingot_history, ehko_personality_layers |

### Core Tables (MIT)
- `reflection_objects` — Indexed vault entries
- `tags` — General tags (object_id, tag)
- `emotional_tags` — Emotional tags (object_id, emotion)
- `cross_references` — Links between entries
- `changelog_entries` — Version history
- `mirrorwell_extensions` — Personal metadata (core_memory, pillar, shared_with)

### Friend/Auth Tables (MIT)
- `friend_registry` — Known people
- `shared_with_friends` — Sharing permissions
- `shared_memories` — Shared content
- `authentication_tokens` — Active sessions
- `authentication_logs` — Auth history
- `custodians` — Posthumous access
- `prepared_messages` — Time-capsule messages
- `message_deliveries` — Delivery tracking

### Forge Session Tables (MIT)
- `forge_sessions` — Chat sessions
- `forge_messages` — Session messages

### Ingot/Insite System Tables (AGPLv3)
- `smelt_queue` — Pending content for analysis
- `transcript_segments` — Chunked transcripts
- `annotations` — User hints on content
- `ingots` — Core insight objects (legacy)
- `insites` — Core insight objects (new name)
- `ingot_sources` / `insite_sources` — Links to sources
- `ingot_history` / `insite_history` — Audit trail
- `ehko_personality_layers` — Forged personality components

### Authority & Mana Tables (AGPLv3)
- `ehko_authority` — Ehko advancement state (singleton)
- `identity_pillars` — Pillar tracking for Identity Clarity
- `mana_state` — Resource economy state (singleton)
- `mana_costs` — Operation costs
- `mana_transactions` — Spending/regen log

---

## MIRRORWELL VAULT

### Templates/
```
reflection_template.md            [v1.2]
```

### 1_Core Identity/
**Status:** First curation pass complete (2025-11-29)

```
1.1 Pillars/                      [populated - 6 documents]
    ├── web_relationships.md
    ├── thread_continuity.md
    ├── mirror_self_perception.md
    ├── compass_values.md
    ├── anchor_grounding.md
    └── flame_drive.md
1.2 Values & Beliefs/             [empty]
1.3 Narrative Arcs/               [empty]
1.4 Core Memory Index/
    └── core_memory_index.md      [v1.1 - 10 memories indexed]
```

### 2_Reflection Library/

#### 2.1 Journals/
**Total:** 15 entries

```
2025-11-28_structuring_manacore_as_an_ai_text_adventure.md
2025-11-28_first-ui-forge.md
2025-11-27_building_the_echo_forge_framework.md
2025-11-26_isolation-family-dynamics-seeking-validation.md
2025-11-22 — Growing Up in the 90s.md
2025-11-16_navigating-family-conflict-sister.md
2025-11-14_family-trauma-sisterly-silence.md
2025-09-09_unjust_police_resignation_after_drug_test.md
2025-09-08_unpacking_control_and_self_perception.md
2025-09-08_control_anxiety_relationships.md
2025-08-02_evolving-beliefs-societal-views.md
2025-08-01_ai-childhood-trauma-reflection.md
2025-08-01_lasting-bonds-childhood-friendships.md
2025-08-01_toxic-mother-son-dynamics.md
2025-07-31_childhood-trauma-family-reflection.md
```

#### 2.2 Transcripts/
```
_processed/                       [archived originals]
```

---

## DORMANT VAULTS

### MonsterGarden/
**Status:** Dormant (VAULT_STATUS.md created 2025-11-29)
**Purpose:** Future plant tracking project

### ManaCore/
**Status:** Dormant (VAULT_STATUS.md created 2025-11-29)
**Purpose:** Fiction worldbuilding

---

## QUICK REFERENCE

### Key Files
| File | Purpose | Location |
|------|---------|----------|
| PROJECT_STATUS.md | Implementation state | EhkoForge/ |
| vault_map.md | This file | EhkoForge/_data/ |
| ehko_index.db | SQLite database | EhkoForge/_data/ |
| forge_server.py | Flask server | EhkoForge/5.0 Scripts/ |
| reflection_template.md | Personal template | Mirrorwell/Templates/ |

### Run Commands
```bash
# Start server
cd "G:\Other computers\Ehko\Obsidian\EhkoForge\5.0 Scripts"
python forge_server.py

# Refresh index
python ehko_refresh.py

# Run ingot migration (one-time)
python run_ingot_migration.py

# Seed test ingots
python seed_test_ingots.py

# GUI control panel
python ehko_control.py
```

### Access Points
- **Forge UI:** http://localhost:5000
- **API Base:** http://localhost:5000/api/

---

## UPDATE PROTOCOL

**When to update this map:**
1. After adding/removing top-level folders
2. After creating new modules or scripts
3. After major version bumps
4. At end of significant work sessions

**How to update:**
- Manual: Edit this file directly
- Session end: Ask Claude to regenerate

---

**Changelog:**
- v2.5 — 2025-12-03 Session 17 — Reorientation Phase 1: Added authority_mana.py, prompts.py v0.2, reorientation migration. Added Authority/Mana table section. Updated recog_engine module listing.
- v2.4 — 2025-12-03 Session 16 — License split reorganisation: Added recog_engine/ module (AGPL). Moved ReCog specs to 2.0 Modules/ReCog/. Added Data_Model_Core_Tables_v1_0.md. Updated ehkoforge/ to redirect preprocessing/processing to recog_engine. Updated Data Model to v1.4. Added license structure section.
- v2.3 — 2025-12-02 Session 15 — Updated ehko_control.py to v2.0. Added EhkoForge Control Panel.vbs launcher. Added .env to scripts listing.
- v2.2 — 2025-12-02 Session 14 — UI Redesign Phase 1: Added templates/, css/, js/ directories. Updated forge_server.py to v2.0 with route-based navigation.
- v2.1 — 2025-12-02 Session 13 — Updated ReCog_Engine_Spec to v0.2 (framing clarifications).
- v2.1 — 2025-12-02 Session 13 — Added script_registry.md and db_schema_summary.md to _data.
- v2.0 — 2025-12-02 Session 12 — Added ReCog_Engine_Spec_v0_1.md to 2.0 Modules.
- v1.9 — 2025-12-02 Session 11 — Added openai_provider.py, provider_factory.py to LLM module. Updated llm/ to v1.1.
- v1.8 — 2025-12-01 Session 10 — Ingot system complete: Added tier0.py, smelt.py to ehkoforge module. Added migrations/ folder. Added run_ingot_migration.py, seed_test_ingots.py. Updated frontend to v1.2. Moved ingot tables from "specified" to "created". Added quick reference section.
- v1.7 — 2025-12-01 — Added Forge_UI_Update_Spec_v0_1.md to 2.0 Modules.
- v1.6 — 2025-12-01 — Added Ingot System specs to 2.0 Modules (Schema, Tier0, Smelt Processor). Added future DB tables list.
- v1.5 — 2025-11-30 — Added 6.0 Frontend section, LLM module details, updated forge_server.py to v1.1
- v1.4 — 2025-11-29 — Identity Pillars folder populated (6 documents)
- v1.3 — 2025-11-29 — Data Model filename corrected; dormant vaults marked
- v1.2 — 2025-11-29 — Core Memory Index first curation pass complete
- v1.1 — 2025-11-29 — Added Core Memory Index Framework
- v1.0 — 2025-11-29 — Initial vault map created

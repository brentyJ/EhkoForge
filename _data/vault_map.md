---
title: "EhkoForge Vault Map"
vault: "EhkoForge"
type: "system"
category: "_data"
status: "active"
version: "4.5"
created: 2025-11-29
updated: 2025-12-17
tags: [system, reference, navigation]
---

# EHKOFORGE VAULT MAP

**Purpose:** Lightweight reference for vault structure. Loaded at session start instead of filesystem scanning.
**Update frequency:** After major structural changes or weekly.
**Generated:** 2025-12-16 (Session 31 - Web Components Complete)

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

## LICENSE

EhkoForge is licensed under **AGPLv3**.

Single LICENSE file at repository root.

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
1_8_Ehko_Visual_Identity_Spec_v1_0.md             [spec, v1.1] — Generative avatar system
Data_Model_Core_Tables_v1_0.md                    [module, v1.0] — MIT schema
_Index.md                                         [navigation, v1.0]
```

### 2.0 Modules/
**Purpose:** Feature specifications and extensions

```
Frontend_Implementation_Spec_v1_0.md              [module, v1.0]
UI-MDV-Specification.md                           [module, v1.0]
Reorientation_Spec_v0_1.md                        [module, v0.1] — Creative direction
# Note: SPINOFF_IDEAS.md moved to documents/ folder
Ideas for road mapping - Proko & Evolution Concept Scaffold.md  [concept, draft]
Forge_UI_Update_Spec_v0_1.md                      [module, v0.1] — UI design

# ReCog Engine
ReCog/
├── ReCog_Core_Spec_v1_0.md                       [spec, v1.0] — Standalone engine architecture
├── ReCog_Engine_Spec_v0_2.md                     [superseded] — Old EhkoForge-coupled design
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
forge_server.py                   [v2.9, working] — Flask server + Mana + LLM + ReCog + Tethers + Evolution Studio
ehko_control.py                   [v2.0, working] — GUI control panel (tkinter, touch-optimized)
EhkoForge Control Panel.vbs       [v1.0, working] — Silent launcher (no console window)
run_ingot_migration.py            [v1.0, applied]  — Ingot tables migration
run_reorientation_migration.py    [v1.0, applied]  — Authority/Mana migration
run_mana_migration.py             [v1.0, applied]  — Mana purchase migration
run_memory_migration.py           [v1.0, applied]  — Memory tiers + progression migration
seed_test_ingots.py               [v1.0, utility]  — Test data generator
test_recog_core.py                [v1.0, utility]  — ReCog Core Phase 1 tests
test_recog_extractor.py           [v1.0, utility]  — ReCog Extractor Phase 2 tests
test_recog_correlator.py          [v1.0, utility]  — ReCog Correlator Phase 3 tests
test_recog_synthesizer.py         [v1.0, utility]  — ReCog Synthesizer Phase 4 tests
test_recog_ehkoforge.py           [v1.0, utility]  — ReCog EhkoForge adapter tests
test_recog_scheduler.py           [v1.0, utility]  — ReCog Scheduler confirmation flow
test_recog_integration.py         [v1.0, utility]  — Full ReCog pipeline integration test
test_openai_integration.py        [v1.0, utility]  — Provider verification
test_mana_system.py               [v1.0, utility]  — Mana API testing
test_mana_simple.py               [v1.0, utility]  — Mana API testing (non-interactive)
run_process_transcriptions.bat    [working] — Batch runner
.env                              [config]        — API keys (not in git)

# Archived (applied patches, no longer needed)
_archive/
├── fix_regex.py
├── fix_theme_headers.py
├── fix_transcription_extraction.py
└── cleanup_unused_ui.py
```

#### recog_engine/ Module
```
recog_engine/
├── __init__.py                   [v1.0] — Main package with v1.0 + legacy API
├── core/                         [NEW - v1.0 Core]
│   ├── __init__.py
│   ├── types.py                  [v1.0] — Document, Insight, Pattern, Synthesis
│   ├── config.py                 [v1.0] — RecogConfig engine configuration
│   ├── llm.py                    [v1.0] — LLMProvider interface, MockLLMProvider
│   ├── signal.py                 [v1.0] — Tier 0 signal processor
│   ├── extractor.py              [v1.0] — Tier 1 insight extraction
│   ├── correlator.py             [v1.0] — Tier 2 pattern correlation
│   ├── synthesizer.py            [v1.0] — Tier 3 deep synthesis
│   └── ehko_llm.py               [v1.0] — Wrapper bridging ehkoforge LLM to ReCog
├── adapters/                     [NEW - v1.0 Adapters]
│   ├── __init__.py
│   ├── base.py                   [v1.0] — RecogAdapter interface
│   ├── memory.py                 [v1.0] — In-memory adapter for testing
│   └── ehkoforge.py              [v1.0] — EhkoForge database adapter
├── tier0.py                      [v0.1, legacy] — Original signal extraction
├── smelt.py                      [v0.1, legacy] — Batch ingot extraction
├── prompts.py                    [v0.2] — Stage-based personality dampener
├── authority_mana.py             [v0.1] — Authority & Mana systems
├── mana_manager.py               [v0.1] — Purchase system, BYOK/Mana/Hybrid
├── scheduler.py                  [v1.0] — ReCog queue management + confirmation flow
├── tether_manager.py             [v0.1] — Direct BYOK conduits (never deplete)
└── forge_integration.py          [v0.1, guide] — Server integration helpers
```

#### ehkoforge/ Module
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
├── reorientation_v0_1.sql        [applied] — Authority/Mana/Insite tables
├── mana_purchase_v0_1.sql        [applied] — Mana purchase tables (7 tables)
├── memory_progression_v0_1.sql   [applied] — Memory tiers + progression tables (5 tables)
└── tethers_v0_1.sql              [pending] — Tether tables (3 tables, 2 views)
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
**Purpose:** Consolidated Terminal UI with Forge review

```
templates/
├── index.html                    [v2.1] — Main terminal UI (Phase 2 consolidated)
└── evolution_studio.html         [v1.0] — Interactive Ehko stage explorer

static/
├── css/
│   ├── main.css                  [v2.1] — Main terminal styles (retro aesthetic)
│   ├── forge.css                 — Forge area (gold/violet palette)
│   └── recog.css                 [v1.0] — ReCog UI (red palette, processing animation)
├── js/
│   ├── main.js                   [v2.6] — Main terminal logic (full Web Components integration)
│   ├── forge.js                  — Insite review logic
│   └── recog.js                  [v1.0] — ReCog scheduler UI (queue/reports/progression)
├── reference_nascent.svg         [v1.0] — Stage 1 Ehko reference
├── reference_signal.svg          [v1.0] — Stage 2 Ehko reference
├── reference_resonant.svg        [v1.0] — Stage 3 Ehko reference
├── reference_manifest.svg        [v1.0] — Stage 4 Ehko reference
├── reference_anchored.svg        [v1.0] — Stage 5 Ehko reference
└── ehko_reference_gallery.html   [v1.0] — All-stage visual gallery

components/
├── ehko-avatar.js                [v1.1] — Avatar Web Component (5 Authority stages, 3 moods)
├── ehko-toast.js                 [v1.0] — Toast notification Web Component
├── ehko-mana-bar.js              [v1.1] — Mana bar Web Component
├── ehko-tether-bar.js            [v1.0] — Tether bar Web Component (never depletes)
└── ehko-tether-panel.js          [v1.0] — Tether management panel Web Component
```

**Architecture (v2.1 - Phase 2 Reorientation):**
- Single terminal interface at `/`
- Mode toggle: Terminal (1 mana) / Reflection (3 mana)
- Forge view at `/forge` for Insite review
- Legacy routes `/reflect` and `/terminal` redirect to `/`

**Features:**
- **Main Terminal:** Mode toggle, Authority bars (5 components), Mana display (regen + purchased), session management
- **Forge:** Insite queue, detail panel, accept/reject
- **Retro Aesthetic:** CRT scanlines, blue terminal palette (#6b8cce), JetBrains Mono font

### 7.0 Website/
**Purpose:** Website documentation and deployment guides

```
EhkoLabs-Website-Plan.md                      [planning, v1.0] — Professional site (PRIORITY)
EhkoForge-Website-Development.md              [reference, v1.0] — Product site build docs
EhkoForge-Website-QuickRef.md                 [guide, v1.0] — Deployment steps
Philosophy-WhyThisExists-Section.md           [content, v1.0] — Philosophy page content
```

**Priority Order:**
1. EhkoLabs.io - Professional presence (build first)
2. EhkoForge.ai - Product site (ready when EhkoLabs done)

### Config/
**Purpose:** Configuration files

```
ui-preferences.json               [user settings]
```

### documents/
**Purpose:** Working documents, research PDFs, images, planning docs

```
SPINOFF_IDEAS.md                          [planning, v1.0]
First Deep Recursive Insight Attempt OPUS4.5.md  [reference]
Defining Ehko's Identity Pillars...pdf    [research]
iconArcane.png, iconArcane.ico            [assets]
TechnoForge.png, technoForge_noText.png   [assets]
```

### _data/
**Purpose:** Database and system files

```
ehko_index.db                     [SQLite, ~200KB]
vault_map.md                      [this file]
script_registry.md                [v1.2] — Compressed script reference
db_schema_summary.md              [v1.6] — Compressed DB schema reference
STACKWRIGHT_INSTRUCTIONS.md       [v2.5] — Claude project instructions (UPDATED)
```

### _private/
**Purpose:** Strategic planning (gitignored)

```
README.md                         — Directory purpose
TWO_LAYER_ARCHITECTURE.md         — Open-core business model (Layer 1 AGPL / Layer 2 Commercial)
FORM_EVOLUTION_VISION.md          — Authority-driven visual progression
MANA_ECONOMICS.md                 — Pricing psychology, monetization
STRATEGIC_NOTES.md                — Future features, marketplace concepts
MEMORY_CORES_TERMINOLOGY.md       — Key terminology decisions
CREATIVE_STUDIO_VISION.md         — Character design platform
ROADMAP.md                        — Expansion phases (Ehko Bridge, Mana Core)
```

### PROJECT_STATUS.md
**Purpose:** Current implementation state and priorities
**Location:** `EhkoForge/PROJECT_STATUS.md`
**Version:** 1.28

---

## DATABASE SCHEMA

### Table Count
**Total:** 43 tables (after tethers migration)

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
**Purpose:** Fiction worldbuilding — potential Expansion 1 (text adventure)

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
- v4.6 — 2025-12-18 Session 40 — Added TWO_LAYER_ARCHITECTURE.md to _private/ section.
- v4.5 — 2025-12-17 Session 39 — Added 7.0 Website/ section with EhkoForge website docs (moved from CareerForge vault).
- v4.4 — 2025-12-17 Session 38 — Added STACKWRIGHT_INSTRUCTIONS.md v2.3 to _data/. Added insights_columns migration. Updated db_schema_summary.md v1.6.
- v4.2 — 2025-12-16 Session 31 — Web Components Migration complete: main.js v2.6, main.css v2.1, all UI elements using components.
- v4.1 — 2025-12-16 Session 31 — Web Components Migration: ehko-avatar.js v1.1 with 5 Authority stages, main.js v2.5.
- v4.0 — 2025-12-14 Session 29 — Tether System Phases 1-5: tether_manager.py, tethers_v0_1.sql migration, forge_server.py v2.9 with 8 tether endpoints + routing, Web Components (ehko-tether-bar, ehko-tether-panel), main.js v2.3.
- v3.9 — 2025-12-08 Session 28 — Ehko Visual Identity System: Added 1_8 spec, 5 reference SVGs, gallery, evolution studio.
- v3.8 — 2025-12-06 Session 26 — ReCog Forge UI Phase 5: recog.css, recog.js. Updated frontend section.
- v3.7 — 2025-12-06 Session 26 — ReCog Scheduler v1.0: scheduler.py, test_recog_scheduler.py, forge_server.py v2.4, 8 API endpoints.
- v3.6 — 2025-12-06 Session 26 — Memory & Progression migration: memory_progression_v0_1.sql, run_memory_migration.py. 5 new tables.
- v3.5 — 2025-12-05 Session 25 — EhkoForge adapter: ehkoforge.py bridges ReCog to database.
- v3.4 — 2025-12-05 Session 25 — ReCog Core Phase 3-4: correlator.py, synthesizer.py, test scripts.
- v3.3 — 2025-12-05 Session 25 — ReCog Core Phase 2: config.py, llm.py, extractor.py, test script.
- v3.2 — 2025-12-05 Session 25 — ReCog Core Phase 1 implementation: core/types.py, core/signal.py, adapters/base.py, adapters/memory.py, test script.
- v3.1 — 2025-12-05 Session 25 — Added ReCog_Core_Spec_v1_0.md (standalone engine architecture).
- v3.0 — 2025-12-05 Session 25 — Consolidated to single AGPLv3 license at root. Removed split licensing references.
- v2.9 — 2025-12-05 Session 24 — Actually removed stale recog/ folder (Session 23 crashed). Corrected changelogs.
- v2.8 — 2025-12-05 Session 23 — [INCOMPLETE - chat crashed] Work started but not completed.
- v2.7 — 2025-12-05 Session 22 — Diagnostic sweep: Added _private/ folder listing, _archive/ folder, mana_manager.py, all migration scripts. Removed legacy template references (cleanup complete). Updated database table counts (35 total).
- v2.6 — 2025-12-03 Session 18 — Reorientation Phase 2: Updated 6.0 Frontend section for consolidated terminal UI.
- v2.5 — 2025-12-03 Session 17 — Reorientation Phase 1: Added authority_mana.py, prompts.py v0.2, reorientation migration.
- v2.4 — 2025-12-03 Session 16 — License split reorganisation: Added recog_engine/ module (AGPL).
- v2.3 — 2025-12-02 Session 15 — Updated ehko_control.py to v2.0. Added VBS launcher.
- v2.2 — 2025-12-02 Session 14 — UI Redesign Phase 1.
- v2.1 — 2025-12-02 Session 13 — Added script_registry.md and db_schema_summary.md.
- v2.0 — 2025-12-02 Session 12 — Added ReCog_Engine_Spec_v0_1.md.
- v1.9 — 2025-12-02 Session 11 — Added openai_provider.py, provider_factory.py.
- v1.8 — 2025-12-01 Session 10 — Ingot system complete.
- v1.0 — 2025-11-29 — Initial vault map created

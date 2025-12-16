# EhkoForge Project Status

**Last Updated:** 2025-12-16  
**Version:** 1.51  
**Repository:** https://github.com/brentyJ/EhkoForge

---

## IN PROGRESS

### Web Components Migration (NEW)
- [x] **Phase 1: Foundation** — Core component library
  - Components: `ehko-avatar.js`, `ehko-toast.js`, `ehko-mana-bar.js`, `ehko-message.js`
  - Location: `6.0 Frontend/components/`
  - Test page: `/component-test.html`
  - Server route: `/components/<filename>`
- [x] **Phase 2: Integration** — Replace current UI elements with components
  - [x] Replace toast system in main.js with `<ehko-toast>`
  - [x] Replace avatar display with `<ehko-avatar>` — Session 31
  - [x] Replace mana display with `<ehko-mana-bar>` — Session 31 (verified)
  - [x] Replace chat messages with `<ehko-message>` — Session 31
- [ ] **Phase 3: HTMX Integration** — Server-driven updates
  - [ ] Add HTMX library
  - [ ] Convert fetch() calls to hx-* attributes
  - [ ] Return HTML fragments from server
- [x] **Phase 4: Cleanup** — Remove obsolete CSS/JS
  - [x] Delete message CSS from main.css (~75 lines)
  - [x] Delete avatar CSS from main.css (~195 lines)
  - [x] Update main.css v2.0 → v2.1 with cleanup notes

**Benefits:**
- Shadow DOM = no CSS conflicts or caching issues
- Portable Ehkos = Web Component .js files
- Code-generated visuals = SVG/Canvas inside components
- Durable = W3C standard, no framework dependency

### Document Ingestion System (NEW)
- [x] **Phase 1: Core Pipeline** — Folder watch, parsers, chunking, database
  - Migration: `document_ingestion_v0_1.sql` (6 tables)
  - Module: `ingestion/` with service, chunker, parsers
  - Parsers: PDF, Markdown, Plaintext, Messages (WhatsApp/SMS/iMessage)
  - CLI: `ingest.py` for manual processing
  - Inbox: `_inbox/` folder for drop zone
- [x] **Phase 2: ReCog Bridge** — Connect ingestion to ReCog processing
  - Scheduler: `extract_docs` operation type for document chunks
  - Adapter: `load_unprocessed_chunks()`, `save_chunk_insight()`, `mark_chunk_processed()`
  - Batch processing: 20 chunks per run, linked to ingots
- [ ] **Phase 3: Entity Extraction** — People, dates, places, events
- [ ] **Phase 4: Cross-Document Correlation** — Thread detection, chain reconstruction
- [ ] **Phase 5: UI Integration** — Drag-drop, progress, history

### Memory Tiers & Progression System
- [x] **Phase 1: Schema** — Memory tier tables, progression tracking, ReCog queue
  - Tables: `session_summaries`, `ehko_progression`, `recog_processing_log`, `recog_reports`, `recog_queue`
  - Extended: `forge_sessions` with memory_tier (hot/warm/cold)
  - Migration: `memory_progression_v0_1.sql` applied
- [ ] **Phase 2: Session Distillation** — Auto-summarise sessions as they age
- [x] **Phase 3: ReCog Scheduler** — Automatic processing with mana confirmation
  - scheduler.py: Queue management, confirmation flow, processing pipeline
  - API endpoints: /api/recog/* (status, check, pending, confirm, cancel, process, reports, progression)
  - forge_server.py v2.4 with scheduler integration
- [ ] **Phase 4: Progression Tracking** — Stage advancement (nascent→sovereign)
- [x] **Phase 5: ReCog Forge UI** — Red palette, animated processing visualisation
  - recog.css: Red palette (#c94a4a), operation cards, processing animation
  - recog.js: API interactions, queue/reports/progression tabs
  - Updated index.html with ReCog drawer, overlays, toast notifications
  - ehko_control.py v3.0: Aligned theme, Server/ReCog/Index/Folders panels
- [ ] **Phase 6: Report System** — ReCog → Ehko snapshots

### Tether System (NEW - Session 29)
- [x] **Phase 1: Schema** — Database tables for direct BYOK conduits
  - Migration: `tethers_v0_1.sql` (3 tables, 2 views)
  - Tables: `tethers`, `tether_usage_log`, `tether_providers`
  - Views: `v_active_tethers`, `v_tether_usage_stats`
- [x] **Phase 2: Manager Module** — Business logic
  - Module: `recog_engine/tether_manager.py`
  - CRUD: create/get/delete/toggle tethers
  - Verification: API key validation per provider
  - Routing: `get_active_tether_for_operation()`
  - Usage logging (analytics only, no billing)
- [x] **Phase 3: API Endpoints** — Server integration
  - `/api/tethers` GET (list) / POST (create)
  - `/api/tethers/<provider>` DELETE
  - `/api/tethers/<provider>/verify` POST
  - `/api/tethers/<provider>/toggle` POST
  - `/api/tethers/providers` GET
  - `/api/tethers/stats` GET
  - `/api/tethers/active` GET
  - forge_server.py v2.8
- [x] **Phase 4: Frontend** — Tether UI
  - `<ehko-tether-bar>` Web Component (mana bar style, never depletes)
  - `<ehko-tether-panel>` Web Component (management modal)
  - Tethers section in status bar with manage button
  - main.js v2.3 with tether loading/rendering
  - Visual: glowing/pulsing when connected, dim when disconnected
- [x] **Phase 5: Routing Integration** — Use tethers instead of mana
  - Chat endpoint checks tethers first, falls back to mana
  - Tether usage logged for analytics (no billing)
  - forge_server.py v2.9
  - ReCog tether integration: *deferred* (uses separate processing path)

**Concept:** Tethers are direct conduits to Sources. Unlike mana, they never deplete — always full while connected.

### Ehko Visual Identity System
- [x] **Phase 1: Specification** — Complete design language documentation
  - Spec: `1.0 System Architecture/1_8_Ehko_Visual_Identity_Spec_v1_0.md`
  - 5 Authority stages with generative parameter bounds
  - Universal canvas (80×80 SVG), colour system, animation states
  - Export formats (SVG with metadata, PNG, CSS-only)
- [x] **Phase 2: Reference Implementations** — SVG examples for all stages
  - Files: `reference_nascent.svg`, `reference_signal.svg`, `reference_resonant.svg`, `reference_manifest.svg`, `reference_anchored.svg`
  - Gallery: `ehko_reference_gallery.html`
  - Studio: `evolution_studio.html` (interactive stage explorer)
- [ ] **Phase 3: Generative Engine** — JavaScript EhkoGenerator class
- [ ] **Phase 4: Export System** — SVG/PNG/CSS download interface
- [ ] **Phase 5: Evolution Engine** — Stage transition animations

### Reorientation (Creative Direction Shift)
- [x] **Phase 1: Foundation** — Database migration, Authority/Mana systems, stage-based prompts
- [x] **Phase 2: UI Consolidation** — Single terminal, mode toggle, retro aesthetic, Authority bars, Mana display
- [x] **Phase 3: Cleanup** — Removed unused route-based UI files
- [x] **Phase 4A: Mana Infrastructure (Backend)** — Database tables, mana_manager.py, API endpoints
- [x] **Phase 4B: Mana Infrastructure (Frontend)** — Purchase modal, config panel, balance display, usage history
- [ ] **Phase 5: ReCog Engine** — Prototype, validate, integrate
- [ ] **Phase 6: Identity Pillars + Core Memories** — Auto-population + suggestion system
- [x] **Phase 7: Ehko Evolution System** — Authority-driven visual progression (see Ehko Visual Identity System)

See: `2.0 Modules/Reorientation_Spec_v0_1.md`  
**Note:** Phase 7+ strategic planning in `_private/` docs

---

## NEEDS TESTING

- [ ] **End-to-End Ingot Flow** — Real conversation → smelt → review → forge
  - Have substantive chat conversation
  - Queue session for smelting
  - Run smelt (Tier 0 + Tier 2)
  - Review surfaced ingots
  - Accept valuable insights into Ehko
  - Verify Ehko state progression

- [ ] **ehko_refresh.py with Full Vault Content**
  - Need to verify: Tag extraction, emotional tag parsing, shared_with friend linking
  - Test with: Multiple reflection types, edge cases, malformed YAML

---

## SPECIFIED (Design Complete, No Implementation)

### ReCog Engine (Core Priority)
- [x] **ReCog Core v1.0** — Standalone recursive insight engine
  - Spec: `EhkoForge/2.0 Modules/ReCog/ReCog_Core_Spec_v1_0.md`
  - Status: **COMPLETE** - All tiers + EhkoForge adapter
  - Architecture: Domain-agnostic engine with adapter pattern
  - EhkoForge becomes a client adapter, not the core
  - [x] **Phase 1:** Core types, signal processor, memory adapter
  - [x] **Phase 2:** Extractor (Tier 1) - config, LLM interface, extraction
  - [x] **Phase 3:** Correlator (Tier 2) - theme clustering, pattern detection
  - [x] **Phase 4:** Synthesizer (Tier 3) - trait/belief/tendency/theme synthesis
  - [x] **EhkoForge Adapter:** Database integration, ingots/personality layers mapping

### Processing & Automation

- [ ] **Mobile Input Processor** — Convert _inbox JSON packets to structured reflections
  - Spec: Defined in `1_4_Data_Model_v1_4.md` Section 4.2
  - Status: Architecture designed, no code written
  - Blocker: None

- [ ] **Authentication Engine API** — Runtime authentication system
  - Spec: Defined in `1_3_Security_Ownership.md`
  - Database tables: Exist and ready
  - Status: Logic specified, no implementation
  - Blocker: None

### User Interface
- [ ] **Export System** — Generate portable archives
  - Spec: Mentioned in `1_1_Overview_v1_0.md` Section 5.0
  - Status: Concept exists, no implementation
  - Formats needed: Text-only, JSON, static site

---

## GAPS & MISSING PIECES

### Medium Priority
1. ~~**Permanent Memory Architecture**~~ → **IN PROGRESS** (Memory Tiers & Progression System)
   - [x] Schema: hot/warm/cold session tiers, progression tracking
   - [ ] Session distillation (raw → summary)
   - [ ] Archive management
   - [ ] Context injection for Ehko

2. **Friend Registry Population** — No data entry method
   - Tables exist but empty
   - Need: Manual entry script or UI
   - Need: Auto-detection from `shared_with` fields

3. **Recovery & Export Protocols** — Not specified
   - Need: Export format specification
   - Need: Degradation level definitions (archival, interactive, full)
   - Need: Handoff instructions for custodians

### Lower Priority
4. **Smelt Scheduling** — Currently manual only
   - APScheduler integration specified but not implemented
   - Consider: Auto-smelt after N messages or daily batch

5. **Visitor Mode** — System prompt defined, not exposed
   - Behaviour Engine has visitor mode logic
   - Needs: Mode selection in UI
   - Needs: Authentication gate

---

## NEXT PRIORITIES (Recommended Order)

### Immediate (Testing)
1. **End-to-End Test with Real Content** — Substantive chat → smelt → review → forge
2. **Bug Fixes** — Address any issues discovered

### Short Term (Polish)
3. **Smelt Scheduling** — Add APScheduler for automatic processing
4. **Export System** — Portable archive generation

### Medium Term
5. **ReCog Engine Implementation** — After real data validates the need
6. **Friend Registry Population** — Entry mechanism
7. **Visitor Mode** — UI exposure + authentication gate

---

## BLOCKERS

**None. All major decisions resolved.**

---

## IMPLEMENTED (Working Code Exists)

### Core Infrastructure
- [x] **ehko_refresh.py v2.0** — Full indexing + transcription processing system
  - Location: `EhkoForge/5.0 Scripts/ehko_refresh.py`
  - Features: Incremental indexing with hash-based change detection, transcription processing pipeline

- [x] **SQLite Database Schema** — 35 tables deployed
  - Location: `EhkoForge/_data/ehko_index.db`
  - Core Tables: reflection_objects, tags, cross_references, mirrorwell_extensions
  - Auth Tables: friend_registry, authentication_tokens, custodians
  - Forge Tables: forge_sessions, forge_messages
  - Ingot Tables: smelt_queue, ingots, ingot_sources, ehko_personality_layers
  - Authority Tables: ehko_authority, identity_pillars, mana_state, mana_transactions
  - Mana Purchase Tables: users, user_mana_balance, mana_purchases, user_config, mana_usage_log

- [x] **LLM Integration Module v1.1** — Multi-provider with role-based routing
  - Location: `EhkoForge/5.0 Scripts/ehkoforge/llm/`
  - Role-Based Routing: processing (OpenAI gpt-4o-mini), conversation (Claude Sonnet), ehko (Claude Sonnet)

- [x] **Ingot System v0.1** — Complete ingot extraction and forging pipeline
  - Components: tier0.py, smelt.py, forge_server.py endpoints
  - Pipeline: Chat → Queue → Tier 0 → Tier 2 → Surface → Review → Forge/Reject

- [x] **Authority & Mana Systems v0.1** — Progression and resource economy
  - Authority: 5 components (Memory Depth, Pattern Recognition, Emotional Resonance, Identity Clarity, Generative Coherence)
  - Mana: Regenerating resource + purchased mana, mode switching (BYOK/Mana/Hybrid)

- [x] **Mana Purchase System v0.1** — Complete purchase infrastructure
  - Backend: mana_manager.py with 6 API endpoints
  - Frontend: Purchase modal, config panel, split balance display, usage history
  - Status: Stripe placeholder (simulated purchases working)

### Documentation & Architecture

- [x] **System Architecture Modules** — 9 specification documents in `1.0 System Architecture/`
- [x] **Ingot System Specifications** — 4 design docs in `2.0 Modules/ReCog/`
- [x] **ReCog Core Specification v1.0** — Standalone engine architecture (supersedes v0.2)
- [x] **Universal Template Framework v1.2** — Base structure for all entries
- [x] **Mirrorwell Reflection Template v1.2** — Personal reflection structure

### Repository & Distribution

- [x] **GitHub Repository** — Public at https://github.com/brentyJ/EhkoForge
- [x] **License** — AGPLv3 (single LICENSE at repository root)
- [x] **Control Panel v2.0** — Touch-optimized tkinter GUI with VBS launcher

### Frontend

- [x] **Frontend Implementation v2.1** — Single terminal interface with mode toggle
  - Main terminal at `/`, Forge view at `/forge`
  - Authority bars (5 components), Mana display (regen + purchased)
  - Retro terminal aesthetic with CRT scanlines

---

## RECENTLY COMPLETED

- **2025-12-16 Session 33:** ReCog Full Pipeline Complete — Fixed cursor reuse bug in `get_patterns()` that was only returning 1 pattern instead of all 13. Updated progression endpoint to query actual `ehko_personality_layers` table instead of empty static data. Enhanced progression UI with content previews, colored pillar borders, and expand-on-click. Full ReCog pipeline now operational: Extract (77 insights) → Correlate (12 patterns) → Synthesise (3 personality components) → Display in pillars (Mirror: 2 items, Compass: 1 item).

- **2025-12-16 Session 32:** ReCog Synthesis Fix — Added emerging themes fallback when patterns are limited. synthesis_min_patterns lowered from 2 to 1. Synthesiser now generates "emerging observations" instead of returning nothing. Report summaries distinguish between full syntheses and emerging themes. Added comprehensive logging to correlator and scheduler.

- **2025-12-16 Session 31:** Web Components Migration Phases 2+4 COMPLETE — All UI elements now use Web Components. Avatar (`<ehko-avatar>` v1.1), mana bar (`<ehko-mana-bar>`), chat messages (`<ehko-message>`), toast notifications (`<ehko-toast>`), tethers (`<ehko-tether-bar>`, `<ehko-tether-panel>`). main.js v2.6 with full component integration. main.css v2.1 with ~270 lines obsolete CSS removed. Mana bar integration verified (removed duplicate updateManaDisplay, fixed state.mana sync, connected mana-topup event).

- **2025-12-15 Session 30:** UI Layout Refinements — ASCII EHKO logo moved to status bar (3-column layout: Authority | ASCII Logo | Mana+Tethers), avatar zone reverted to original design with matrix background and corner brackets, settings drawer streamlined (removed redundant API key inputs, added "Manage Tethers" button, Display toggles including ASCII logo visibility, Data & Privacy section, About section with links and license). Updated main.css, index.html, main.js v2.4.

- **2025-12-14 Session 29:** Tether System Phases 1-5 complete — Schema (`tethers_v0_1.sql` with 3 tables, 2 views), tether_manager.py (CRUD, verification, routing, usage logging), 8 API endpoints in forge_server.py v2.9, Web Components (`<ehko-tether-bar>`, `<ehko-tether-panel>`), UI integration in main.js v2.3, chat routing integration (tethers bypass mana). Tethers are direct BYOK conduits that never deplete, styled like mana bars but always full when connected.
- **2025-12-08 Session 28:** Ehko Visual Identity System Phases 1-2 complete — Full specification v1.1 (500+ lines), 5 reference SVGs (one per Authority stage), gallery viewer, evolution studio. Stage-based generative constraints, export formats, animation states defined.
- **2025-12-07 Session 27:** LLM Tether UI, API key management with hot-reload, SQLite threading fixes.
- **2025-12-06 Session 26:** Memory Tiers & Progression System Phases 1+3+5 complete — Schema migration (5 tables), ReCog Scheduler v1.0 with confirmation flow, 8 new API endpoints (/api/recog/*), ReCog UI (red palette, queue/reports/progression tabs, processing animation), forge_server.py v2.4.
- **2025-12-05 Session 25:** ReCog Core v1.0 complete — All 4 tiers + EhkoForge adapter. Integration test passed (9 insights, 1 pattern, 2 syntheses from real content).

- **2025-12-05 Session 24:** Actually removed stale `recog/` folder (Session 23 crashed mid-operation). Fixed README repository structure (frontend templates/, split css/js, migration files). Corrected changelogs.
- **2025-12-05 Session 23:** [INCOMPLETE - chat crashed] Diagnostic work started but not completed.
- **2025-12-05 Session 22:** Full diagnostic sweep. Archived deprecated scripts (fix_*.py, cleanup_unused_ui.py). Created _private/ROADMAP.md with Mana Core expansion and Ehko Bridge post-MVP phases. Updated vault_map, script_registry, db_schema_summary. Reorganised PROJECT_STATUS.md structure.
- **2025-12-04 Session 19:** Phase 4B complete — Mana purchase modal with tier selection, config panel with BYOK/Mana/Hybrid mode switching, split mana display (regen + purchased bars), usage history modal.
- **2025-12-04 Session 19:** Phase 4A complete — 7 mana purchase database tables, mana_manager.py module, 6 mana API endpoints.
- **2025-12-03 Session 18:** Phase 2 UI Consolidation complete — Single terminal interface with mode toggle, Authority bars, Mana display, retro aesthetic.
- **2025-12-03 Session 17:** Phase 1 Foundation complete — Authority system, Mana system, stage-based prompts, reorientation migration.
- **2025-12-02 Session 15:** Control Panel v2.0, OpenAI .env loading verified, speaker attribution fix.
- **2025-12-02 Session 12:** ReCog Engine Specification v0.2 created.
- **2025-12-02 Session 11:** OpenAI integration complete, multi-provider LLM module.
- **2025-12-01 Session 10:** Ingot System complete — Full pipeline operational.

---

## SCRIPT INVENTORY

| Script | Version | Status |
|--------|---------|--------|
| ehko_refresh.py | v2.0 | ✅ Working |
| forge_server.py | v2.9 | ✅ Working |
| ehko_control.py | v2.0 | ✅ Working |
| run_ingot_migration.py | v1.0 | ✅ Applied |
| run_reorientation_migration.py | v1.0 | ✅ Applied |
| run_mana_migration.py | v1.0 | ✅ Applied |
| run_memory_migration.py | v1.0 | ✅ Applied |
| run_tethers_migration.py | v1.0 | ⏳ Pending |
| ehkoforge/llm/ | v1.1 | ✅ Working |
| recog_engine (core) | v1.0 | ✅ Working |
| recog_engine (legacy) | v0.1 | ✅ Working |
| recog_engine/prompts.py | v0.2 | ✅ Working |
| recog_engine/authority_mana.py | v0.1 | ✅ Working |
| recog_engine/mana_manager.py | v0.1 | ✅ Working |
| recog_engine/scheduler.py | v1.0 | ✅ Working |
| recog_engine/tether_manager.py | v0.1 | ✅ Working |

---

## SPECIFICATION INVENTORY

| Spec | Version | Status |
|------|---------|--------|
| 1_8_Ehko_Visual_Identity_Spec_v1_0.md | v1.1 | 📋 Specified |
| ReCog_Engine_Spec_v0_2.md | v0.2 | 📋 Specified |
| Ingot_System_Schema_v0_1.md | v0.1 | ✅ Implemented |
| Tier0_PreAnnotation_Spec_v0_1.md | v0.1 | ✅ Implemented |
| Smelt_Processor_Spec_v0_1.md | v0.1 | ✅ Implemented |
| Forge_UI_Update_Spec_v0_1.md | v0.1 | ✅ Implemented |
| Reorientation_Spec_v0_1.md | v0.1 | 🔄 In Progress |

---

## MIRRORWELL CONTENT STATUS

**Journals:** 15 entries
**Processed Transcripts:** 4 files (archived)
**Core Memories Flagged:** 10 (first curation pass complete)
**Identity Pillars Populated:** 6 (Web, Thread, Mirror, Compass, Anchor, Flame)

---

## NOTES

- This file should be updated whenever implementation status changes
- Check this file at the start of each session to maintain alignment
- "Implemented" means working code exists; "Specified" means design complete but no code
- Append completed items to "Recently Completed" section with dates

---

**Changelog:**
- v1.51 — 2025-12-16 Session 33 — ReCog Full Pipeline Complete: Fixed cursor reuse bug in get_patterns(), progression endpoint queries actual ehko_personality_layers, enhanced progression UI with content previews and expand-on-click. Full pipeline tested successfully.
- v1.50 — 2025-12-16 Session 32 — ReCog Synthesis Fix: Lowered synthesis_min_patterns to 1, added emerging themes fallback, improved logging.
- v1.49 — 2025-12-16 Session 31 — Web Components Migration Phases 2+4 complete. main.js v2.6 (full component integration), main.css v2.1 (~270 lines obsolete CSS removed). Mana bar integration verified.
- v1.47 — 2025-12-16 Session 31 — Web Components Migration Phase 2: Avatar replaced with <ehko-avatar> component v1.1 (5 Authority stages). main.js v2.5 with component integration.
- v1.46 — 2025-12-15 Session 30 — UI Layout Refinements: ASCII logo in status bar (3-column layout), avatar zone restored to original, settings drawer streamlined (tether panel integration, About section, removed redundant inputs), main.js v2.4.
- v1.45 — 2025-12-14 Session 29 — Tether System Phases 1-5: Schema (3 tables, 2 views), tether_manager.py, 8 API endpoints (forge_server.py v2.9), Web Components (ehko-tether-bar, ehko-tether-panel), UI integration (main.js v2.3), chat routing (tethers bypass mana).
- v1.42 — 2025-12-08 Session 28 — Ehko Visual Identity System: Spec v1.1, 5 reference SVGs, gallery, evolution studio. Marked Reorientation Phase 7 complete.
- v1.41 — 2025-12-06 Session 26 — Document Ingestion Phase 2: ReCog Bridge. Scheduler extract_docs operation, adapter chunk methods, batch processing pipeline.
- v1.40 — 2025-12-06 Session 26 — Document Ingestion System Phase 1: migration (6 tables), ingestion module (parsers for PDF/MD/TXT/Messages), chunker, CLI, _inbox folder.
- v1.39 — 2025-12-06 Session 26 — ReCog Forge UI Phase 5: recog.css (red palette), recog.js (API interactions), index.html updates (drawer, overlays, toast), scheduler.py cooldown fix, ehko_control.py v3.0 (theme alignment, streamlined panels).
- v1.38 — 2025-12-06 Session 26 — ReCog Scheduler v1.0: Confirmation flow, queue management, 8 API endpoints, forge_server.py v2.4.
- v1.37 — 2025-12-06 Session 26 — Memory Tiers & Progression System Phase 1: Schema migration with 5 new tables, 173 sessions marked 'hot'.
- v1.36 — 2025-12-05 Session 25 — EhkoForge adapter complete: ehkoforge.py bridges ReCog to database (ingots, patterns, personality_layers).
- v1.35 — 2025-12-05 Session 25 — ReCog Core Phases 3-4 complete: correlator.py (Tier 2), synthesizer.py (Tier 3). Full pipeline done.
- v1.34 — 2025-12-05 Session 25 — ReCog Core Phase 2 complete: config.py, llm.py (LLMProvider interface), extractor.py (Tier 1).
- v1.33 — 2025-12-05 Session 25 — ReCog Core Phase 1 complete: types.py, signal.py, adapters (base, memory), test script.
- v1.32 — 2025-12-05 Session 25 — ReCog Core v1.0 spec: Standalone engine architecture with adapter pattern. EhkoForge becomes client adapter.
- v1.31 — 2025-12-05 Session 25 — Consolidated to AGPLv3 (removed split licensing).
- v1.30 — 2025-12-05 Session 24 — Actually removed stale recog/ folder (Session 23 crashed before completing). Fixed README repository structure.
- v1.29 — 2025-12-05 Session 23 — [INCOMPLETE - chat crashed] Diagnostic work started.
- v1.28 — 2025-12-05 Session 22 — Diagnostic sweep: Reorganised structure (incomplete items at top). Archived deprecated scripts. Added private roadmap. Updated all reference docs.
- v1.27 — 2025-12-04 Session 19 — Phase 4B complete: Mana purchase system frontend.
- v1.26 — 2025-12-04 Session 19 — Phase 4A complete: Mana purchase system backend.
- v1.25 — 2025-12-04 Session 19 — Phase 3 cleanup: Removed unused route-based UI.
- v1.24 — 2025-12-03 Session 18 — Phase 2 UI Consolidation complete.
- v1.23 — 2025-12-03 Session 17 — Reorientation Phase 1 complete.
- v1.22 — 2025-12-03 Session 16 — License split (MIT/AGPL).
- v1.21 — 2025-12-02 Session 15 — Control Panel v2.0.

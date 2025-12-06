# SCRIPT REGISTRY

**Purpose:** Quick reference for script capabilities. Read this instead of full source files.
**Updated:** 2025-12-06 (Session 26 - Control Panel v3.0)

### recog_engine.adapters.ehkoforge (NEW)
- `EhkoForgeAdapter(db_path)` — Connect to EhkoForge database
- `adapter.load_documents(source_type, limit)` — Load from reflection_objects, sessions
- `adapter.save_insight(insight)` — Save to ingots table
- `adapter.save_pattern(pattern)` — Save to ingot_patterns table
- `adapter.save_synthesis(synthesis)` — Save to ehko_personality_layers table

---

## Core Scripts

| Script | Version | Purpose |
|--------|---------|---------|
| `ehko_refresh.py` | 2.0 | Vault indexing, transcription processing, DB sync |
| `forge_server.py` | 2.4 | Flask API, LLM routing, mana system, chat sessions, ReCog scheduler |
| `ehko_control.py` | 3.0 | Tkinter GUI — Server, ReCog, Index, Folders |

## Migration Scripts

| Script | Purpose | Status |
|--------|---------|--------|
| `run_ingot_migration.py` | Ingot system tables | Applied |
| `run_reorientation_migration.py` | Authority/Mana tables | Applied |
| `run_mana_migration.py` | Mana purchase tables | Applied |
| `run_memory_migration.py` | Memory tiers + progression | Applied |

## Test Scripts

| Script | Purpose |
|--------|---------|
| `test_recog_core.py` | ReCog Core Phase 1 verification |
| `test_recog_extractor.py` | ReCog Extractor Phase 2 verification |
| `test_recog_correlator.py` | ReCog Correlator Phase 3 verification |
| `test_recog_synthesizer.py` | ReCog Synthesizer Phase 4 verification |
| `test_recog_ehkoforge.py` | ReCog EhkoForge adapter verification |
| `test_recog_scheduler.py` | ReCog Scheduler confirmation flow |
| `test_recog_integration.py` | Full ReCog pipeline with real LLM |
| `test_openai_integration.py` | Provider setup verification |
| `test_mana_system.py` | Mana API endpoint testing (interactive) |
| `test_mana_simple.py` | Mana API testing (non-interactive) |
| `seed_test_ingots.py` | Generate test data for ingot system |

## Utility Scripts

| Script | Purpose |
|--------|---------|
| `run_process_transcriptions.bat` | Batch runner for refresh + transcription processing |
| `EhkoForge Control Panel.vbs` | Silent launcher for ehko_control.py |

## Archived Scripts (5.0 Scripts/_archive/)

| Script | Reason |
|--------|--------|
| `fix_regex.py` | One-time patch, applied |
| `fix_theme_headers.py` | One-time patch, applied |
| `fix_transcription_extraction.py` | One-time patch, applied |
| `cleanup_unused_ui.py` | One-time cleanup, executed |

---

## Module: ehkoforge/llm/ (MIT)

| File | Purpose |
|------|---------|
| `base.py` | Abstract LLMProvider interface |
| `claude_provider.py` | Anthropic API wrapper |
| `openai_provider.py` | OpenAI API wrapper |
| `provider_factory.py` | Role-based instantiation (processing/conversation/ehko) |
| `config.py` | API keys, model names, role routing |
| `context_builder.py` | Searches reflections for relevant context |

## Module: recog_engine/ (AGPL)

### v1.0 Core (New)

| File | Version | Purpose |
|------|---------|---------|
| `core/types.py` | 1.0 | Document, Insight, Pattern, Synthesis, ProcessingState, Corpus |
| `core/config.py` | 1.0 | RecogConfig engine configuration |
| `core/llm.py` | 1.0 | LLMProvider interface, LLMResponse, MockLLMProvider |
| `core/signal.py` | 1.0 | Tier 0 signal extraction (refactored, uses new types) |
| `core/extractor.py` | 1.0 | Tier 1 insight extraction from documents |
| `core/correlator.py` | 1.0 | Tier 2 pattern correlation across insights |
| `core/synthesizer.py` | 1.0 | Tier 3 deep synthesis (traits, beliefs, tendencies) |
| `adapters/base.py` | 1.0 | RecogAdapter abstract interface |
| `adapters/memory.py` | 1.0 | In-memory adapter for testing/standalone use |
| `adapters/ehkoforge.py` | 1.0 | EhkoForge database adapter (ingots, personality_layers) |

### Legacy (EhkoForge-specific)

| File | Version | Purpose |
|------|---------|---------|
| `tier0.py` | 0.1 | Original signal extraction (backwards compat) |
| `smelt.py` | 0.1 | Batch ingot extraction from queue |
| `prompts.py` | 0.2 | System prompts with stage-based personality dampener |
| `authority_mana.py` | 0.1 | Authority progression + Mana regeneration systems |
| `mana_manager.py` | 0.1 | Mana purchase, BYOK/Mana/Hybrid modes, spending limits |
| `scheduler.py` | 1.0 | ReCog queue management, confirmation flow, processing pipeline |
| `forge_integration.py` | 0.1 | Server integration guide (sample code) |

---

## Key Functions Quick Reference

### ehko_refresh.py
- `refresh_vault(vault_path)` — Main entry, indexes all .md files
- `process_transcriptions()` — Extracts themes from transcripts
- `compute_hash(content)` — Content hashing for change detection

### forge_server.py v2.4
- `/api/chat` — LLM chat endpoint
- `/api/sessions` — Session CRUD
- `/api/ingots` — Ingot queue management
- `/api/smelt/status` — Processing status
- `/api/smelt/trigger` — Manual smelt run
- `/api/mana/balance` — Current mana state
- `/api/mana/config` — User mode configuration
- `/api/mana/purchase` — Purchase mana (Stripe placeholder)
- `/api/mana/pricing` — Available tiers
- `/api/mana/history` — Purchase and usage history
- `/api/mana/api-keys` — BYOK key management
- `/api/recog/status` — ReCog scheduler status
- `/api/recog/pending` — Operations awaiting confirmation
- `/api/recog/confirm/<id>` — Confirm operation
- `/api/recog/cancel/<id>` — Cancel operation
- `/api/recog/process` — Process confirmed operations
- `/api/recog/reports` — ReCog report snapshots
- `/api/recog/progression` — Ehko progression status

### provider_factory.py
- `get_provider(role)` — Returns appropriate LLM for role
- Roles: `processing`, `conversation`, `ehko`

### mana_manager.py
- `get_user_config(user_id)` — Retrieve mode and limits
- `spend_mana_smart(user_id, amount)` — Mode-aware spending
- `record_purchase(user_id, tier_id)` — Log mana purchase
- `get_usage_stats(user_id, days)` — Usage analytics

### recog_engine.core (NEW)
- `Document.create(content, source_type, source_ref)` — Create document
- `SignalProcessor().process(document)` — Tier 0 signal extraction
- `process_text(text)` — Convenience function for signals
- `Insight.create(summary, themes, significance, ...)` — Create insight
- `Pattern.create(summary, pattern_type, insight_ids, strength)` — Create pattern

### recog_engine.adapters (NEW)
- `MemoryAdapter()` — In-memory storage for testing
- `adapter.add_document(doc)` — Add document to store
- `adapter.save_insight(insight)` — Save extracted insight
- `adapter.get_insights(**filters)` — Retrieve insights

### recog_engine.core.extractor (NEW)
- `Extractor(llm, config)` — Create extractor with LLM provider
- `extractor.extract(document)` — Extract insights from single document
- `extractor.extract_batch(documents, adapter)` — Batch extraction with persistence
- `extract_from_text(text, llm)` — Convenience function for raw text

### recog_engine.core.correlator (NEW)
- `Correlator(llm, config)` — Create correlator with LLM provider
- `correlator.correlate(insights, adapter)` — Find patterns across insights
- `find_patterns(insights, llm)` — Convenience function

### recog_engine.core.synthesizer (NEW)
- `Synthesizer(llm, config)` — Create synthesizer with LLM provider
- `synthesizer.synthesise(patterns, insights)` — Generate high-level syntheses
- `synthesise_patterns(patterns, llm)` — Convenience function

---

**Changelog:**
- v1.8 — 2025-12-06 — ehko_control.py v3.0: Aligned theme, streamlined panels (Server/ReCog/Index/Folders).
- v1.7 — 2025-12-06 — Added scheduler.py, ReCog API endpoints, updated forge_server to v2.4.
- v1.6 — 2025-12-05 — Added EhkoForge adapter: ehkoforge.py, test script.
- v1.5 — 2025-12-05 — Added Phase 3-4: correlator.py, synthesizer.py. Added test scripts.
- v1.4 — 2025-12-05 — Added Phase 2: config.py, llm.py, extractor.py. Added test_recog_extractor.py.
- v1.3 — 2025-12-05 — Added ReCog Core v1.0 structure (core/, adapters/). Added test_recog_core.py.
- v1.2 — 2025-12-05 — Added mana_manager.py, authority_mana.py. Moved deprecated scripts to _archive. Added test scripts section.
- v1.1 — 2025-12-03 — License split: moved tier0, smelt, prompts to recog_engine/ (AGPL). Updated ehko_control to v2.0.
- v1.0 — 2025-12-02 — Initial registry created

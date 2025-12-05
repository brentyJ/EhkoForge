# SCRIPT REGISTRY

**Purpose:** Quick reference for script capabilities. Read this instead of full source files.
**Updated:** 2025-12-05 (Session 22)

---

## Core Scripts

| Script | Version | Purpose |
|--------|---------|---------|
| `ehko_refresh.py` | 2.0 | Vault indexing, transcription processing, DB sync |
| `forge_server.py` | 2.3 | Flask API, LLM routing, mana system, chat sessions |
| `ehko_control.py` | 2.0 | Tkinter GUI, touch-optimized, Forge/Smelt controls |

## Migration Scripts

| Script | Purpose | Status |
|--------|---------|--------|
| `run_ingot_migration.py` | Ingot system tables | Applied |
| `run_reorientation_migration.py` | Authority/Mana tables | Applied |
| `run_mana_migration.py` | Mana purchase tables | Applied |

## Test Scripts

| Script | Purpose |
|--------|---------|
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

| File | Version | Purpose |
|------|---------|---------|
| `tier0.py` | 0.1 | Signal extraction without LLM (timestamps, speakers, questions) |
| `smelt.py` | 0.1 | Batch ingot extraction from queue |
| `prompts.py` | 0.2 | System prompts with stage-based personality dampener |
| `authority_mana.py` | 0.1 | Authority progression + Mana regeneration systems |
| `mana_manager.py` | 0.1 | Mana purchase, BYOK/Mana/Hybrid modes, spending limits |
| `forge_integration.py` | 0.1 | Server integration guide (sample code) |

---

## Key Functions Quick Reference

### ehko_refresh.py
- `refresh_vault(vault_path)` — Main entry, indexes all .md files
- `process_transcriptions()` — Extracts themes from transcripts
- `compute_hash(content)` — Content hashing for change detection

### forge_server.py v2.3
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

### provider_factory.py
- `get_provider(role)` — Returns appropriate LLM for role
- Roles: `processing`, `conversation`, `ehko`

### mana_manager.py
- `get_user_config(user_id)` — Retrieve mode and limits
- `spend_mana_smart(user_id, amount)` — Mode-aware spending
- `record_purchase(user_id, tier_id)` — Log mana purchase
- `get_usage_stats(user_id, days)` — Usage analytics

---

**Changelog:**
- v1.2 — 2025-12-05 — Added mana_manager.py, authority_mana.py. Moved deprecated scripts to _archive. Added test scripts section.
- v1.1 — 2025-12-03 — License split: moved tier0, smelt, prompts to recog_engine/ (AGPL). Updated ehko_control to v2.0.
- v1.0 — 2025-12-02 — Initial registry created

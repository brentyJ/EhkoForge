# SCRIPT REGISTRY

**Purpose:** Quick reference for script capabilities. Read this instead of full source files.
**Updated:** 2025-12-02

---

## Core Scripts

| Script | Version | Purpose |
|--------|---------|---------|
| `ehko_refresh.py` | 2.0 | Vault indexing, transcription processing, DB sync |
| `forge_server.py` | 1.2 | Flask API, LLM routing, ingot endpoints, chat sessions |
| `ehko_control.py` | 1.0 | Tkinter GUI for server/refresh control |

## Utilities

| Script | Purpose |
|--------|---------|
| `run_ingot_migration.py` | One-time DB migration for ingot tables |
| `seed_test_ingots.py` | Generate test data for ingot system |
| `fix_regex.py` | Applied patch for theme extraction |
| `fix_theme_headers.py` | Applied patch for header levels |
| `fix_transcription_extraction.py` | Applied patch for section boundaries |

---

## Module: ehkoforge/llm/

| File | Purpose |
|------|---------|
| `base.py` | Abstract LLMProvider interface |
| `claude_provider.py` | Anthropic API wrapper |
| `openai_provider.py` | OpenAI API wrapper |
| `provider_factory.py` | Role-based instantiation (quality→Claude, cost→GPT) |
| `config.py` | API keys, model names, role routing |
| `context_builder.py` | Searches reflections for relevant context |
| `system_prompt.py` | Prompts for forging/visitor/archived modes |
| `forge_integration.py` | Server integration helpers |

## Module: ehkoforge/preprocessing/

| File | Purpose |
|------|---------|
| `tier0.py` | Signal extraction without LLM (timestamps, speakers, questions) |

## Module: ehkoforge/processing/

| File | Purpose |
|------|---------|
| `smelt.py` | Batch ingot extraction from queue |

---

## Key Functions Quick Reference

### ehko_refresh.py
- `refresh_vault(vault_path)` — Main entry, indexes all .md files
- `process_transcriptions()` — Extracts themes from transcripts
- `compute_hash(content)` — Content hashing for change detection

### forge_server.py
- `/api/chat` — LLM chat endpoint
- `/api/sessions` — Session CRUD
- `/api/ingots` — Ingot queue management
- `/api/smelt/status` — Processing status
- `/api/smelt/trigger` — Manual smelt run

### provider_factory.py
- `get_provider(role)` — Returns appropriate LLM for role
- Roles: `quality`, `cost`, `default`

---

**Changelog:**
- v1.0 — 2025-12-02 — Initial registry created

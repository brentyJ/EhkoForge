# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

EhkoForge is a personal memory and identity preservation framework that creates AI-powered digital representations called "Ehkos". The system uses a metallurgy metaphor: raw content is "smelted" into atomic identity insights called "ingots", which users "forge" into their Ehko's personality.

**Key Principle:** 200-year durability over convenience. Markdown files are canonical storage; SQLite indexes are derived, not source of truth.

## Development Commands

```bash
# Start the Flask server (main entry point)
cd "5.0 Scripts"
python forge_server.py

# Refresh vault index (re-index markdown files)
python ehko_refresh.py

# Run the GUI control panel
python ehko_control.py

# Run database migrations (in order if fresh install)
python run_ingot_migration.py
python run_reorientation_migration.py
python run_mana_migration.py
python run_memory_migration.py
python run_insights_migration.py
python run_tethers_migration.py
python run_entity_migration.py
```

**Web UI:** http://localhost:5000 (after starting forge_server.py)

## Architecture

### Core Components

1. **Flask Server** (`forge_server.py`) - REST API with LLM integration, mana system, chat sessions, ReCog scheduler
2. **Vault Indexer** (`ehko_refresh.py`) - Scans markdown files, extracts YAML frontmatter, populates SQLite
3. **ReCog Engine** (`recog_engine/`) - Recursive cognition system with 4 tiers:
   - **Tier 0** (signal.py): Code-based signal extraction (free, no LLM)
   - **Tier 1** (extractor.py): LLM insight extraction from documents
   - **Tier 2** (correlator.py): Pattern detection across insights
   - **Tier 3** (synthesizer.py): Deep synthesis into personality traits
4. **LLM Integration** (`ehkoforge/llm/`) - Multi-provider with role-based routing:
   - `processing` role → OpenAI gpt-4o-mini (cheaper batch ops)
   - `conversation` role → Claude Sonnet (chat)
   - `ehko` role → Claude Sonnet (Ehko personality)

### Key Directories

- `1.0 System Architecture/` - Core specifications and design documents
- `2.0 Modules/ReCog/` - ReCog engine specifications
- `5.0 Scripts/` - All Python code, migrations, and modules
- `6.0 Frontend/` - Web UI (templates, CSS, JS, Web Components)
- `_data/` - SQLite database, reference docs (vault_map.md, script_registry.md, db_schema_summary.md)

### Database

SQLite at `_data/ehko_index.db` with 43+ tables. Key table groups:
- Core: `reflection_objects`, `tags`, `cross_references`
- Forge: `forge_sessions`, `forge_messages`
- Ingots: `ingots`, `ingot_sources`, `ehko_personality_layers`
- ReCog: `recog_queue`, `recog_reports`, `ingot_patterns`
- Mana: `mana_state`, `mana_transactions`, `user_mana_balance`

See `_data/db_schema_summary.md` for complete schema reference.

### Module Structure

```
5.0 Scripts/
├── recog_engine/
│   ├── core/           # v1.0 standalone engine (types, signal, extractor, correlator, synthesizer)
│   ├── adapters/       # Database adapters (memory.py for testing, ehkoforge.py for production)
│   ├── scheduler.py    # ReCog queue management
│   ├── mana_manager.py # Mana economy system
│   └── tether_manager.py # BYOK API key management
└── ehkoforge/
    └── llm/            # Multi-provider LLM integration
```

## API Endpoints

Key endpoints in `forge_server.py`:
- `/api/chat` - LLM chat with Ehko
- `/api/sessions` - Session CRUD
- `/api/ingots` - Ingot management
- `/api/smelt/trigger` - Trigger ingot extraction
- `/api/recog/*` - ReCog scheduler (status, confirm, process, reports)
- `/api/mana/*` - Mana system (balance, purchase, history)
- `/api/tethers/*` - BYOK tether management

## Code Conventions

- **Australian spelling**: organisation, behaviour, colour, realise
- **YAML frontmatter** in all markdown files for metadata
- **Never modify raw input** - user content preserved exactly
- **Semantic versioning** in frontmatter and filenames
- API keys via environment variables or `.env` file in `5.0 Scripts/`

## Reference Documents

Before diving into code, check these compressed references in `_data/`:
- `script_registry.md` - Quick reference for all scripts and their functions
- `db_schema_summary.md` - Database table overview with common queries
- `vault_map.md` - Full directory structure and file purposes
- `PROJECT_STATUS.md` (root) - Current implementation status and priorities

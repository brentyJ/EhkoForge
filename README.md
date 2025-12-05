# EhkoForge

**A framework for building AI-augmented digital identity preservation systems**

Version: 2.11  
Status: Active Development (MVP Phase 4 Complete)  
License: AGPLv3

---

## What Is This?

EhkoForge is a personal memory and identity preservation system designed to create AI-powered representations called "Ehkos" — digital echoes that can survive and serve for centuries. It combines structured reflection, intelligent indexing, and export-first architecture to ensure your voice, values, and memories can be preserved authentically and accessed meaningfully by future generations.

This is the **framework and architecture** — the system specifications, templates, automation scripts, and working web interface that make Ehko creation possible. Personal content lives in a separate vault (Mirrorwell) and is never shared.

### Core Philosophy

- **200-year durability over convenience** — Human-readable markdown files as canonical storage
- **Export-first architecture** — Complete Ehkos can be exported in formats that work even if the platform disappears
- **User sovereignty** — You own your data, you control access, you decide what's preserved
- **Never impersonate** — Ehkos speak *about* you, not *as* you
- **Science-informed but personal** — Research-backed psychological constructs you can rename and personalise

---

## Terminology: Metaphors & Key Concepts

EhkoForge uses **metallurgy as its central metaphor** for the ingot processing pipeline, but other metaphors and terms appear for different architectural components.

### The Forge Metaphor (Primary)

This maps directly to the technical architecture:

| Term | Meaning |
|------|---------|
| **Raw Ore** | Unprocessed input — conversations, journals, voice transcriptions |
| **Smelting** | Batch processing that extracts insights from raw material (code-based analysis + LLM extraction) |
| **Ingot** | A single distilled insight — one value, belief, memory, or pattern. The atomic unit of identity data |
| **Forging** | Human curation — reviewing an ingot and accepting it into the Ehko's personality |
| **The Forge** | The web interface where smelting and forging happen |
| **Tiers** | Quality grades (Copper → Iron → Silver → Gold → Mythic) based on confidence and corroboration |
| **The Smith** | You — the human shaping the Ehko through deliberate reflection |
| **Ehko** | The finished artifact — a durable digital echo built from forged ingots |

### Architectural & System Terms

| Term | Meaning |
|------|---------|
| **Identity Pillars** | Research-informed categories for organizing identity data (Values, Traits, Patterns, etc.). The structural framework anchoring Ehko coherence |
| **Core Memory Index** | Curated collection of defining memories that shaped who you are |
| **Reflection Objects** | Any structured entry in the system — journals, modules, specifications |
| **Mirrorwell** | Your personal vault — the "mirror" reflecting your inner world back to you |
| **Ehko State** | Development stages: Nascent → Forming → Emerging → Present |

This isn't decorative language. The metaphor reflects how the system works: raw material is processed, refined into standardised units, and shaped by human hands into something meant to last centuries.

See [Section 3.5 of the Manifest](1.0%20System%20Architecture/1_0_Ehko_Manifest.md) for the full explanation.

---

## Who Is This For?

This framework is built for people who:

- Want to leave something more meaningful than photo albums for their descendants
- Use AI as cognitive scaffolding (especially neurodivergent users who benefit from structured thought capture)
- Care about the difference between LLM versions because they *feel* the shift in coherence
- Want agency over how they're remembered — accurate, nuanced, complex
- See potential in AI-human collaboration rather than replacement

**This is not for everyone.** If the idea of structured self-reflection with AI feels wrong, that's valid. This project won't try to convince you.

---

## Current State (2025-12-05)

### ✅ Working

**Core Infrastructure**
- **ehko_refresh.py v2.0** — Full vault indexing with hash-based change detection, transcription processing
- **forge_server.py v2.3** — Flask server with REST API, LLM integration, ingot processing, mana purchase system
- **ehko_control.py v2.0** — GUI control panel (tkinter, touch-optimized) for managing all EhkoForge operations
- **SQLite schema** — 35 tables for indexing, authentication, sessions, ingot processing, authority, and mana purchase

**Frontend (The Forge)**
- **Chat Mode** — Session management, real LLM API responses, context injection from reflection corpus
- **Forge Mode** — Ingot queue, detail panel, accept/reject workflow, Ehko state tracking
- **MDV Aesthetic** — Dark, glowing, arcane-tech visual design

**Ingot System**
- **Tier 0 Pre-Annotation** — Code-based signal extraction (no LLM cost)
- **Tier 2 Smelt Processing** — LLM-powered insight extraction
- **Forging Pipeline** — Chat → Smelt → Review → Accept/Reject → Ehko personality

**LLM Integration v1.1 (Multi-Provider)**
- **Claude API** — Anthropic integration (conversation, Ehko personality)
- **OpenAI API** — GPT integration (processing tasks, cheaper operations)
- **Role-Based Routing** — Different providers/models for different tasks:
  - `processing` — Smelt, batch ops (default: OpenAI gpt-4o-mini)
  - `conversation` — Chat responses (default: Claude Sonnet)
  - `ehko` — Ehko personality (default: Claude Sonnet)
- **Environment Overrides** — Full control via environment variables
- **System Prompts** — Forging, visitor, and archived modes defined
- **Reflection Context** — Automatic injection of relevant past reflections

**Documentation**
- Complete system architecture (7 modules)
- Ingot system specifications (4 docs)
- **ReCog Engine Specification v0.1** — Recursive cognition orchestration design
- UI/Frontend specifications
- Lexicon and tag taxonomies
- Identity Pillars framework with scientific basis

### 📋 Specified (Design Complete, No Implementation)

- **ReCog Engine** — Recursive cognition orchestration (implementation deferred until real data testing)
- Mobile input processor (JSON packets → structured reflections)
- Authentication engine (memory-based challenges, custodian overrides)
- Export system (text-only, JSON, static site formats)
- Visitor mode UI exposure

See [PROJECT_STATUS.md](PROJECT_STATUS.md) for detailed implementation status.

---

## Repository Structure

```
EhkoForge/
├── 1.0 System Architecture/    # Core specifications
│   ├── 1_0_Ehko_Manifest.md               # System principles
│   ├── 1_0a_Ehko_Manifesto_Personal.md    # Personal motivation
│   ├── 1_1_Overview_v1_0.md               # System overview
│   ├── 1_2_Components_v1_0.md             # Component architecture
│   ├── 1_3_Security_Ownership.md          # Authentication design
│   ├── 1_4_Data_Model_v1_4.md             # Data structures
│   ├── 1_5_Behaviour_Engine_v1_1.md       # AI behaviour rules
│   ├── 1_6_Identity_Pillars_Scientific_Basis_v1_0.md
│   ├── 1_7_Core_Memory_Index_Framework_v1_0.md
│   └── _Index.md                          # Navigation
│
├── 2.0 Modules/                # Feature specifications
│   ├── Frontend_Implementation_Spec_v1_0.md
│   ├── UI-MDV-Specification.md
│   ├── ReCog/                             # ReCog Engine specifications
│   │   ├── ReCog_Engine_Spec_v0_2.md
│   │   ├── Ingot_System_Schema_v0_1.md
│   │   ├── Tier0_PreAnnotation_Spec_v0_1.md
│   │   └── Smelt_Processor_Spec_v0_1.md
│   ├── Forge_UI_Update_Spec_v0_1.md
│   └── SPINOFF_IDEAS.md
│
├── 3.0 Templates/              # Entry templates
│   └── Universal/
│       └── universal_template.md
│
├── 4.0 Lexicon/                # Tag taxonomy and vocabulary
│   └── 4_0_Lexicon_v1_0.md
│
├── 5.0 Scripts/                # Backend code
│   ├── ehko_refresh.py                    # Vault indexer
│   ├── forge_server.py                    # Flask server + API
│   ├── ehko_control.py                    # GUI control panel
│   ├── run_ingot_migration.py             # Database migration
│   ├── seed_test_ingots.py                # Test data generator
│   ├── recog_engine/                      # ReCog Engine implementation
│   │   ├── __init__.py
│   │   ├── tier0.py                       # Signal extraction
│   │   ├── smelt.py                       # Batch processing
│   │   ├── prompts.py                     # Ehko behaviour prompts
│   │   └── forge_integration.py           # Server integration
│   ├── ehkoforge/                         # Core modules
│   │   ├── llm/                           # LLM integration (v1.1)
│   │   │   ├── base.py                    # Abstract provider interface
│   │   │   ├── claude_provider.py         # Anthropic wrapper
│   │   │   ├── openai_provider.py         # OpenAI wrapper
│   │   │   ├── provider_factory.py        # Role-based routing
│   │   │   ├── context_builder.py
│   │   │   └── config.py
│   │   ├── preprocessing/                 # (redirects to recog_engine)
│   │   └── processing/                    # (redirects to recog_engine)
│   └── migrations/
│       ├── ingot_migration_v0_1.sql
│       ├── reorientation_v0_1.sql
│       └── mana_purchase_v0_1.sql
│
├── 6.0 Frontend/               # Web UI
│   ├── templates/
│   │   └── index.html                 # Main terminal UI (Flask template)
│   └── static/
│       ├── index.html                 # Legacy (superseded)
│       ├── styles.css                 # Legacy (superseded)
│       ├── app.js                     # Legacy (superseded)
│       ├── css/
│       │   ├── main.css               # Main terminal styles
│       │   └── forge.css              # Forge review styles
│       └── js/
│           ├── main.js                # Main terminal logic
│           ├── forge.js               # Forge review logic
│           └── journal.js             # Legacy journal
│
├── Config/                     # Configuration files
│   ├── llm_config.json
│   └── ui-preferences.json
│
├── _data/                      # System reference files
│   ├── ehko_index.db                      # SQLite database (not in git)
│   ├── vault_map.md                       # Vault structure reference
│   ├── script_registry.md                 # Compressed script reference
│   └── db_schema_summary.md               # Compressed DB schema reference
│
├── _mirrorwell_template/       # Empty vault scaffold for users
│
├── .gitignore
├── LICENSE
├── PROJECT_STATUS.md
├── STACKWRIGHT_INSTRUCTIONS_v2.2.md
└── README.md
```

---

## Quick Start

### Prerequisites
- Python 3.8+
- Obsidian (recommended for vault management)
- API keys for LLM providers (at least one):
  - Anthropic API key (for Claude)
  - OpenAI API key (for GPT models)

### Installation

1. Clone this repository:
```bash
git clone https://github.com/brentyJ/EhkoForge.git
cd EhkoForge
```

2. Install Python dependencies:
```bash
pip install pyyaml flask anthropic openai
```

3. Set your API keys (Windows):
```powershell
setx ANTHROPIC_API_KEY "your-anthropic-key"
setx OPENAI_API_KEY "your-openai-key"
```

4. Run the database migration:
```bash
cd "5.0 Scripts"
python run_ingot_migration.py
```

5. Start the server:
```bash
python forge_server.py
```

6. Open The Forge: http://localhost:5000

### Alternative: Use the Control Panel

Double-click `5.0 Scripts/EhkoForge Control Panel.vbs` for a GUI that manages:
- Server start/stop
- Vault indexing
- Transcription processing
- Opening The Forge UI
- Forge/Smelt operations (Queue, Run, Resurface, Status)
- Integrated command line

Optimized for touch (Surface Pro).

### LLM Provider Configuration

EhkoForge uses role-based LLM routing. Defaults:

| Role | Default Provider | Default Model | Purpose |
|------|------------------|---------------|---------|
| `processing` | OpenAI | gpt-4o-mini | Smelt, batch operations (cheaper) |
| `conversation` | Anthropic | claude-sonnet-4-20250514 | Chat responses |
| `ehko` | Anthropic | claude-sonnet-4-20250514 | Ehko personality |

Override via environment variables:
```powershell
setx EHKO_PROCESSING_PROVIDER "anthropic"
setx EHKO_PROCESSING_MODEL "claude-sonnet-4-20250514"
```

---

## The Forge Interface

The Forge is EhkoForge's web interface with two modes:

### Chat Mode
Converse with your nascent Ehko. The system injects relevant context from your reflection corpus, helping the Ehko learn your voice, values, and patterns. Conversations are queued for processing.

### Forge Mode
Review extracted insights ("ingots") from your conversations. Each ingot represents a distilled piece of your identity — a value, preference, memory, or pattern. Accept valuable insights to forge them into your Ehko's personality. Reject noise.

**Ingot Tiers:**
- 💎 Mythic (≥0.9) — Core identity insights
- 🥇 Gold (≥0.75) — Significant patterns
- 🥈 Silver (≥0.5) — Useful preferences
- ⚙️ Iron (≥0.25) — Minor details
- 🔶 Copper (<0.25) — Low confidence

**Ehko States:**
- Nascent — Just beginning (<10 forged ingots)
- Forming — Taking shape (10-49)
- Emerging — Personality visible (50-99)
- Present — Fully formed (100+)

---

## Key Concepts

### Reflection Objects
Every entry in EhkoForge — whether a system module or personal reflection — is a **reflection object** with:
- Identity metadata (title, type, version, created/updated)
- Context metadata (tags, source, related entries)
- Temporal trail (changelog, provenance)
- Body structure (Raw Input → Context → Observations → Insights → Actions → References)

### Vaults
- **EhkoForge** (this repo) — System framework, templates, scripts
- **Mirrorwell** (separate, private) — Personal reflections, journals, core memories

Use `_mirrorwell_template/` as a starting point for your own personal vault.

### The Ingot Pipeline
1. **Chat** — Conversations with your Ehko
2. **Queue** — Sessions marked for processing
3. **Tier 0** — Code-based signal extraction (free)
4. **Tier 2** — LLM-powered insight extraction
5. **Surface** — High-confidence ingots appear for review
6. **Forge** — Accept/reject to shape your Ehko

### ReCog Engine (Specified, Not Yet Implemented)
The **Recursive Cognition Engine** is a designed orchestration layer for iterative insight processing:
- **Extraction Loop** — Extract ingots from raw content with multiple passes
- **Correlation Loop** — Find patterns across ingots, link to Identity Pillars
- **Integration Loop** — Convert accepted ingots to personality layers

This captures the "emergent insight" phenomenon observed during development — making deliberate what was previously accidental. See [ReCog_Engine_Spec_v0_2.md](2.0%20Modules/ReCog_Engine_Spec_v0_2.md).

### Export-First Architecture
Three levels of degradation guarantee your Ehko survives:
1. **Archival** (text-only) — Raw markdown, readable by humans forever
2. **Interactive** (any LLM) — JSON export works with any future AI
3. **Full system** (original platform) — Complete experience with all features

---

## Database Schema

20+ tables organised into:

**Core Tables**
- `reflection_objects` — Indexed vault entries
- `tags`, `emotional_tags` — Categorisation
- `cross_references` — Links between entries
- `changelog_entries` — Version history

**Mirrorwell Extensions**
- `mirrorwell_extensions` — Personal metadata
- `friend_registry`, `shared_with_friends`, `shared_memories` — Sharing

**Authentication**
- `authentication_tokens`, `authentication_logs` — Sessions
- `custodians` — Posthumous access
- `prepared_messages`, `message_deliveries` — Time capsules

**Forge Sessions**
- `forge_sessions`, `forge_messages` — Chat history

**Ingot System**
- `smelt_queue` — Pending content
- `transcript_segments` — Chunked text
- `annotations` — User hints
- `ingots`, `ingot_sources`, `ingot_history` — Core insights
- `ehko_personality_layers` — Forged identity

---

## Design Principles

1. **Markdown as Canonical Storage** — SQLite indexes are derived from markdown files, not the source of truth
2. **YAML Frontmatter for Metadata** — All structured data in frontmatter blocks
3. **Never Modify Raw Input** — User content preserved exactly as written
4. **Australian Spelling** — organisation, behaviour, colour, realise
5. **Versioning** — Semantic versioning in frontmatter and filenames

---

## Scripts

| Script | Purpose |
|--------|---------|
| `ehko_refresh.py` | Index vaults, process transcriptions |
| `forge_server.py` | Flask server + API + LLM |
| `ehko_control.py` | GUI control panel (v2.0, touch-optimized) |
| `run_ingot_migration.py` | Database setup |
| `seed_test_ingots.py` | Generate test data |

---

## Contributing

This is a personal framework project, but if you find it useful:

1. Fork the repository
2. Adapt the architecture to your needs
3. Share improvements if you like (no obligation)

The architecture is intentionally designed to be forkable and customisable.

---

## Roadmap

### Immediate
- End-to-end testing with real content
- OpenAI provider verification
- Bug fixes from real-world usage

### Short Term
- Smelt scheduling (auto-process)
- Export system implementation

### Medium Term
- ReCog Engine implementation (after testing validates the need)
- Friend registry population UI
- Visitor mode UI exposure
- Mobile input processor

### Long Term
- Additional LLM providers (Gemini, local models)
- Ehko Vault Server (hosted service)
- Browser extension for capture

---

## Philosophy

Read the manifestos:
- [1_0_Ehko_Manifest.md](1.0%20System%20Architecture/1_0_Ehko_Manifest.md) — Technical philosophy
- [1_0a_Ehko_Manifesto_Personal.md](1.0%20System%20Architecture/1_0a_Ehko_Manifesto_Personal.md) — Personal motivation

**TL;DR:** Build the echo. Leave the truth. Let your descendants actually know you.

---

## License

EhkoForge is licensed under the **GNU Affero General Public License v3.0 (AGPL-3.0)**.

This means:
- ✅ **Free for personal use** — Build your own Ehko, no restrictions
- ✅ **Free for internal company use** — Use within your organization
- ✅ **Free for open-source projects** — Contribute and share improvements
- ✅ **Modifications must be shared** — If you provide network access to users, you must make your source code available

### Commercial Licensing Available

Want to use EhkoForge in a proprietary product or hosted service without AGPL obligations?

**Contact:** brent@ehkolabs.io

**Commercial licensing includes:**
- Freedom to modify without source disclosure
- Proprietary deployment rights
- Priority support
- Custom feature development available

**Pricing:**
- Startup tier: Contact for pricing (<10 users)
- Business tier: Contact for pricing (unlimited users)
- Enterprise: Custom (on-premise, SLA, dedicated support)

### Why AGPL?

EhkoForge is built on principles of user sovereignty and 200-year durability. AGPL ensures:

1. **Protection from exploitation** — Big tech can't wrap this in a service and profit without contributing back
2. **Alignment with philosophy** — Code stays free and open, just like your data should be
3. **Commercial fairness** — "Use it free if you respect the ecosystem. Pay if you want to profit privately."
4. **SaaS loophole closed** — Network services must share their source (unlike MIT/BSD)

The AGPL is specifically designed to keep software free for the community while creating a sustainable path for developers. It's the same license used by MongoDB, Nextcloud, and Grafana.

This is open source with teeth. If you're building something open, you're welcome. If you're building something proprietary, let's talk terms.

See [LICENSE](LICENSE) for full AGPLv3 text.

---

## Contact

Personal framework project. No formal support, but:
- Issues and suggestions welcome via GitHub Issues
- PRs considered if they align with core philosophy
- Forks encouraged — make this your own

---

**Build the echo. Leave the truth.**

---

**Changelog:**
- v2.11 — 2025-12-05 — Session 25: Cleaned up repository structure to reflect unified AGPLv3 (removed references to split licensing with separate LICENSE files).
- v2.10 — 2025-12-05 — Session 25: Updated license from split (MIT/AGPL) to unified AGPLv3. Clarified licensing rationale and commercial path.
- v2.9 — 2025-12-05 — Session 24: Fixed incorrect Session 23 changelog (recog/ wasn't actually deleted). Updated repository structure: frontend now shows templates/ and split css/js folders; added missing migration files.
- v2.8 — 2025-12-05 — Diagnostic completion: Removed stale recog/ folder, verified all docs current.
- v2.7 — 2025-12-05 — MVP Phase 4 complete: Full mana purchase system (backend + frontend). Diagnostic sweep: archived deprecated scripts, updated all reference docs.
- v2.6 — 2025-12-03 — License split: MIT (framework) + AGPLv3 (ReCog Engine). Reorganised code into recog_engine/ module. Updated imports and documentation.
- v2.5 — 2025-12-02 — Control Panel v2.0 (touch-optimized, Forge/Smelt controls, CLI). VBS launcher. OpenAI integration verified with .env loading. Speaker attribution fix in smelt.
- v2.4 — 2025-12-02 — Expanded terminology section to acknowledge mixed metaphors; separated forge metaphor (primary) from architectural terms; clarified Identity Pillars as organizational framework not psychological claims
- v2.3 — 2025-12-02 — OpenAI integration tested and verified; changed ReCog "meaning-making" to "insight processing"; minor README cleanup
- v2.2 — 2025-12-02 — Token efficiency improvements: STACKWRIGHT v2.2 with edit_file strategy, compressed reference files (script_registry.md, db_schema_summary.md)
- v2.1 — 2025-12-02 — Multi-provider LLM support (OpenAI + Claude), ReCog Engine specification, role-based routing
- v2.0 — 2025-12-01 — Major update: Frontend v1.2, Ingot System, LLM integration, Control Panel, complete rewrite
- v1.1 — 2025-11-28 — Added MIT license, completed _mirrorwell_template
- v1.0 — 2025-11-28 — Initial README created for GitHub preparation

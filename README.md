# EhkoForge

**A framework for building AI-augmented digital identity preservation systems**

Version: 1.2  
Status: Active Development  
License: MIT

---

## What Is This?

EhkoForge is a personal memory and identity preservation system designed to create AI-powered representations called "Ehkos" - digital echoes that can survive and serve for centuries. It combines structured reflection, intelligent indexing, and export-first architecture to ensure your voice, values, and memories can be preserved authentically and accessed meaningfully by future generations.

This is the **framework and architecture** - the system specifications, templates, and automation scripts that make Ehko creation possible. Personal content lives in a separate vault (Mirrorwell) and is never shared.

### Core Philosophy

- **200-year durability over convenience** - Human-readable markdown files as canonical storage
- **Export-first architecture** - Complete Ehkos can be exported in formats that work even if the platform disappears
- **User sovereignty** - You own your data, you control access, you decide what's preserved
- **Never impersonate** - Ehkos speak *about* you, not *as* you
- **Science-informed but personal** - Research-backed psychological constructs you can rename and personalize

---

## Who Is This For?

This framework is built for people who:

- Want to leave something more meaningful than photo albums for their descendants
- Use AI as cognitive scaffolding (especially neurodivergent users who benefit from structured thought capture)
- Care about the difference between LLM versions because they *feel* the shift in coherence
- Want agency over how they're remembered - accurate, nuanced, complex
- See potential in AI-human collaboration rather than replacement

**This is not for everyone.** If the idea of structured self-reflection with AI feels wrong, that's valid. This project won't try to convince you.

---

## Current State (2025-11-28)

### ✅ Working
- **ehko_refresh.py v2.0** - Full vault indexing with hash-based change detection
- **Transcription processing** - Auto-converts voice dictations to structured reflections
- **SQLite schema** - Complete database structure (13 tables) for indexing and metadata
- **Documentation** - System architecture, data model, authentication design, UI specification
- **Universal Template Framework** - Consistent structure across all entries
- **Mirrorwell Reflection Template** - Structure for personal reflections and journals

### 📋 Specified (Design Complete, No Implementation)
- Mobile input processor (JSON packets → structured reflections)
- Authentication engine (memory-based challenges, custodian overrides)
- Frontend UI (immersive 3-screen interface - The Forge)
- Export system (text-only, JSON, static site formats)

### 🔨 In Progress
- Frontend tech stack decision (Flask vs React vs Obsidian plugin)
- Core Memory Index Framework definition
- Lexicon and tag taxonomy population

See [PROJECT_STATUS.md](PROJECT_STATUS.md) for detailed implementation status.

---

## Repository Structure

```
EhkoForge/
├── 1.0 System Architecture/    # Core specifications and philosophy
│   ├── 1_0_Ehko_Manifest.md               # System principles
│   ├── 1_0a_Ehko_Manifesto_Personal.md    # Personal motivation essay
│   ├── 1_1_Overview_v1_0.md               # System overview
│   ├── 1_2_Components_v1_0.md             # Component architecture
│   ├── 1_3_Security_Ownership.md          # Authentication design
│   ├── 1_4_Data_Model_v1_1.md             # Data structures
│   └── 1_6_Identity_Pillars_Scientific_Basis_v1_0.md
│
├── 2.0 Modules/                # Feature specifications
│   ├── UI-MDV-Specification.md            # Frontend design (MDV)
│   └── SPINOFF_IDEAS.md                   # Future extensions
│
├── 3.0 Templates/              # Entry templates
│   └── Universal/
│       └── universal_template.md          # Base structure for all entries
│
├── 4.0 Lexicon/                # Tag taxonomy and vocabulary (planned)
│
├── 5.0 Scripts/                # Automation and utilities
│   ├── ehko_refresh.py                    # Main indexing script
│   ├── ehko_refresh.py.md                 # Script documentation
│   ├── indexing_scripts.md                # Script specifications
│   ├── misc_utilities.md                  # Utility docs
│   ├── fix_*.py                           # Bugfix utilities
│   ├── run_process_transcriptions.bat     # Batch runner
│   └── System Logs/
│
├── archive/                    # Deprecated or superseded modules
├── attachments/                # Media files
├── documents/                  # Reference PDFs
├── _data/                      # Generated database (not in git)
├── _inbox/                     # Mobile input staging area
├── _ledger/                    # System action logs
│
├── .gitignore
├── PROJECT_STATUS.md           # Current implementation status
└── README.md                   # This file
```

---

## Quick Start

### Prerequisites
- Python 3.8+ (for indexing scripts)
- Obsidian (recommended for vault management)
- `pyyaml` Python library

### Installation

1. Clone this repository:
```bash
git clone https://github.com/[username]/ehkoforge.git
cd ehkoforge
```

2. Install Python dependencies:
```bash
pip install pyyaml
```

3. (Optional) Open in Obsidian:
   - Open Obsidian
   - Open folder as vault → select `EhkoForge/` directory

### Running the Indexer

Index all markdown files and populate the database:
```bash
python "5.0 Scripts/ehko_refresh.py"
```

Force full rebuild (ignores hashes, reprocesses everything):
```bash
python "5.0 Scripts/ehko_refresh.py" --rebuild
```

The script creates/updates `_data/ehko_index.db` with:
- All reflection objects (entries with YAML frontmatter)
- Tags and cross-references
- Changelog entries
- Emotional tags and friend sharing metadata

---

## Documentation Files vs Python Scripts

You'll notice some scripts have both `.md` and `.py` versions:
- **`.md` files** - Human-readable documentation and specifications
- **`.py` files** - Actual executable scripts

Example:
- `ehko_refresh.py.md` → What the script does, how it works
- `ehko_refresh.py` → The actual Python code

This pattern keeps technical specs accessible to non-developers while maintaining working code.

---

## Key Concepts

### Reflection Objects
Every entry in EhkoForge - whether a system module or personal reflection - is a **reflection object** with:
- Identity metadata (title, type, version, created/updated)
- Context metadata (tags, source, related entries)
- Temporal trail (changelog, provenance)
- Body structure (Raw Input → Context → Observations → Insights → Actions → References)

### Vaults
- **EhkoForge** (this repo) - System framework, templates, scripts
- **Mirrorwell** (separate, private) - Personal reflections, journals, core memories

### Export-First Architecture
Three levels of degradation guarantee your Ehko survives:
1. **Archival** (text-only) - Raw markdown, readable by humans forever
2. **Interactive** (any LLM) - JSON export works with any future AI
3. **Full system** (original platform) - Complete experience with all features

---

## Design Principles

### 1. Markdown as Canonical Storage
SQLite indexes are *derived* from markdown files, not the other way around. The database can be regenerated at any time by running `ehko_refresh.py`.

### 2. YAML Frontmatter for Metadata
All structured data lives in YAML frontmatter blocks at the top of each file.

### 3. Never Modify Raw Input
User-generated content is preserved exactly as written. Structure is added around it, never through it.

### 4. Australian Spelling
Consistently use: organisation, behaviour, colour, realise, etc.

### 5. Versioning
All modules use semantic versioning (x.y) in frontmatter and filenames. Changelogs track all modifications.

---

## Contributing

This is a personal project framework, but if you find it useful and want to adapt it:

1. Fork the repository
2. Adapt the architecture to your needs
3. Share your improvements (optional - no obligation)

The architecture is intentionally designed to be forkable and customizable.

---

## Roadmap

### Immediate Priorities
1. Frontend tech stack decision
2. Core Memory Index Framework specification
3. MVP chat interface implementation

### Medium Term
4. Mobile input processor implementation
5. Authentication engine implementation
6. Friend registry population
7. Lexicon and tag taxonomy completion

### Long Term
8. Export system (multiple format support)
9. Multi-API integration (ChatGPT, Gemini, Claude variants)
10. Ehko Vault Server (hosted digital personas - paid tier)

See [PROJECT_STATUS.md](PROJECT_STATUS.md) for detailed status.

---

## Philosophy

Read the manifestos for the full picture:
- [1_0_Ehko_Manifest.md](1.0%20System%20Architecture/1_0_Ehko_Manifest.md) - Technical philosophy and principles
- [1_0a_Ehko_Manifesto_Personal.md](1.0%20System%20Architecture/1_0a_Ehko_Manifesto_Personal.md) - Personal motivation and emotional case

**TL;DR:** Build the echo. Leave the truth. Let your descendants actually know you.

---

## Technical Notes

### Database Schema
13 tables:
- Core: `reflection_objects`, `tags`, `cross_references`, `changelog_entries`
- Mirrorwell extensions: `mirrorwell_extensions`, `emotional_tags`, `shared_with_friends`
- Authentication: `friend_registry`, `shared_memories`, `authentication_tokens`, `authentication_logs`, `custodians`
- Messaging: `prepared_messages`, `message_deliveries`

### File Naming Conventions
- Underscores for multi-word filenames (not hyphens)
- Dates: `YYYY-MM-DD` format
- Versions in filenames: `module_name_vX_Y.md`

### Script Documentation Pattern
Each `.py` script has:
- Corresponding `.md` file with full specification
- Inline comments for implementation details
- Version number in both files
- Changelog in both files

---

## License

MIT License — see [LICENSE](LICENSE) for full text.

TL;DR: Do whatever you want with this. Fork it, adapt it, sell it, whatever. Just include the copyright notice.

---

## Contact & Support

This is a personal framework project. No formal support, but:
- Issues and suggestions welcome via GitHub Issues
- PRs considered if they align with core philosophy
- Forks encouraged - make this your own

---

**Build the echo. Leave the truth.**

---

**Changelog:**
- v1.1 — 2025-11-28 — Added MIT license, completed _mirrorwell_template
- v1.0 — 2025-11-28 — Initial README created for GitHub preparation

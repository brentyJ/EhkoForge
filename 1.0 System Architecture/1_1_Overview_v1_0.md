---
title: 1.1 Overview
vault: EhkoForge
type: module
status: active
version: "1.1"
created: 2025-11-25
updated: 2025-11-26
tags:
  - ehkoforge
  - pinned
  - architecture
  - index
---
# {{title}}

## 1. Purpose & Scope

**This module provides the architectural overview and navigation index for the entire EhkoForge system.**

It specifies:
- What EhkoForge is and what it produces
- The relationship between EhkoForge (system) and Mirrorwell (content)
- The module hierarchy and dependencies
- The technology stack and durability layer
- How the system degrades gracefully across time

This is the entry point. A new reader should be able to:
1. Understand what EhkoForge does in under 2 minutes
2. Know which module to read for any given concern
3. Grasp the philosophical and technical foundations
4. Navigate confidently to deeper specifications

---

## 2. Core Principles

### 2.1 The Ehko Is the Output
EhkoForge is not the product. The **Ehko** is the product—a structured, durable, AI-readable archive of identity, memory, and meaning that survives its creator.

### 2.2 Two Vaults, Two Purposes
- **EhkoForge** = system framework, specifications, architecture
- **Mirrorwell** = personal content, reflections, identity material

They are interdependent but structurally separate. EhkoForge defines how; Mirrorwell contains what.

### 2.3 Modules Are Specifications, Not Code
EhkoForge modules are implementation specs. A developer should be able to build working software from these documents without additional explanation.

### 2.4 Durability Over Convenience
Every architectural decision prioritises 200-year survival over 2-year convenience. Human-readable formats, no proprietary dependencies, multiple storage redundancy.

### 2.5 Separation of Truth and Index
Markdown files are truth. SQLite is derived. The index can always be rebuilt from the files.

---

## 3. Structures & Components

### 3.1 System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         EHKOFORGE                               │
│                    (Framework & Specs)                          │
├─────────────────────────────────────────────────────────────────┤
│  1.0 Manifest          │ Philosophy, ethics, design principles  │
│  1.1 Overview          │ This file - architecture index         │
│  1.2 Components        │ System parts and relationships         │
│  1.3 Security          │ Auth, access control, veiled content   │
│  1.4 Data Model        │ Schemas, SQLite, packet processing     │
│  1.5 Behaviour Engine  │ AI interaction rules, reflection logic │
│  2.0 Templates         │ Universal + specialised templates      │
│  3.0 Lexicon           │ Terminology, tag taxonomies            │
│  4.0 Scripts           │ ehko_refresh.py, inbox processing      │
│  5.0 Recovery          │ Handoff protocols, export formats      │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
                    ┌─────────────────────┐
                    │     MIRRORWELL      │
                    │     (Identity)      │
                    ├─────────────────────┤
                    │ Reflections         │
                    │ Core memories       │
                    │ Identity pillars    │
                    │ Emotional work      │
                    │ Transcripts         │
                    │ Prepared messages   │
                    └─────────────────────┘
                                │
                                ▼
                    ┌─────────────────────┐
                    │     SQLite Index    │
                    │  (Derived, Query)   │
                    └─────────────────────┘
                                │
                                ▼
                    ┌─────────────────────┐
                    │    EHKO (Output)    │
                    │  Interactive Echo   │
                    │  of the Creator     │
                    └─────────────────────┘
```

### 3.2 Module Index

| Module | Purpose | Status |
|--------|---------|--------|
| **1.0 Ehko Manifest** | Philosophy, ethics, design principles, origin story | Canonical v2.1 |
| **1.1 Overview** | Architecture overview, module index, technology stack | Active v1.1 |
| **1.2 Components** | System components, relationships, integration points | Active v1.1 |
| **1.3 Security & Ownership** | Authentication, access control, veiled content, custodians | Active v1.0 |
| **1.4 Data Model** | YAML schemas, SQLite tables, packet processing, versioning | Active v1.2 |
| **1.5 Behaviour Engine** | AI interaction rules, reflection prompts, tone calibration | Active v1.1 |
| **2.0 Templates** | Universal Template Framework, Mirrorwell specialisation | Active v1.1 |
| **3.0 Lexicon** | Terminology definitions, tag taxonomies | Planned |
| **4.0 Scripts** | Python tooling (ehko_refresh.py, inbox processor) | Planned |
| **5.0 Recovery** | Export formats, handoff protocols, durability strategies | Planned |

### 3.3 Vault Definitions

**EhkoForge**
- **Purpose:** Meta-vault containing system architecture and specifications
- **Content types:** Modules, templates, scripts, recovery documentation
- **Template:** Universal Template Framework v1.1
- **Primary output:** The blueprint that defines how Ehkos are built

**Mirrorwell**
- **Purpose:** Personal reflection, identity work, emotional processing
- **Content types:** Reflections, core memories, identity pillars, therapy notes, transcripts, prepared messages
- **Template:** Mirrorwell Reflection Template v1.2
- **Primary output:** The personal Ehko—who Brent is, was, and became

### 3.4 Technology Stack

| Layer | Technology | Purpose | Durability Rating |
|-------|------------|---------|-------------------|
| **Storage** | Markdown + YAML | Human-readable reflection objects | ★★★★★ (200+ years) |
| **Index** | SQLite | Querying, fast lookups | ★★★★☆ (50+ years) |
| **Editing** | Obsidian | User interface for vault management | ★★☆☆☆ (10 years) |
| **Processing** | Python | Indexing, inbox processing, exports | ★★★☆☆ (20+ years) |
| **AI Layer** | API-agnostic | LLM interaction for Ehko behaviour | ★★☆☆☆ (swappable) |
| **Backup** | Git + Cloud + Physical | Multi-location redundancy | ★★★★★ (indefinite) |

---

## 4. Flows & Workflows

### 4.1 Content Creation Flow

```
User Input (voice, text, transcript)
         │
         ▼
┌─────────────────────────┐
│  _inbox JSON Packet     │  ← Mobile dictation, batch imports
│  OR Direct Obsidian     │  ← Manual template usage
└─────────────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Template Application   │  ← Raw Input preserved verbatim
│  Frontmatter populated  │  ← Required fields enforced
└─────────────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Interpretation Pass    │  ← Context, Observations, Reflection
│  (Human or AI-assisted) │  ← Tags, cross-references added
└─────────────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Mirrorwell Storage     │  ← File = Source of Truth
└─────────────────────────┘
         │
         ▼
┌─────────────────────────┐
│  ehko_refresh.py        │  ← Scans vault, populates SQLite
│  Index Updated          │
└─────────────────────────┘
```

### 4.2 Ehko Interaction Flow

```
Friend/Descendant Arrives
         │
         ▼
┌─────────────────────────┐
│  Authentication         │  ← 1.3 Security & Ownership
│  (Contextual → Email)   │
└─────────────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Behaviour Engine       │  ← 1.5 Behaviour Engine
│  Loads identity context │
└─────────────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Query Processing       │  ← SQLite index + full-text search
│  Relevant memories      │
└─────────────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Response Generation    │  ← Ehko voice, tone, boundaries
│  Veiled content check   │
└─────────────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Conversation           │  ← Iterative, memory-aware
│  Logging (optional)     │
└─────────────────────────┘
```

### 4.3 Export and Handoff Flow

```
Export Request
         │
         ├─────────────────────────────┐
         ▼                             ▼
┌─────────────────────┐    ┌─────────────────────┐
│  Full Archive       │    │  Public Archive     │
│  (All content)      │    │  (revealed: true)   │
└─────────────────────┘    └─────────────────────┘
         │                             │
         ▼                             ▼
┌─────────────────────────────────────────────────┐
│  Export Package Contains:                       │
│  - All markdown files (organised)               │
│  - SQLite database (rebuildable)                │
│  - RECOVERY.md (rebuild instructions)           │
│  - DESCENDANT_ACCESS.md (welcome + auth info)   │
│  - VEILED_PROTOCOLS.md (conditional content)    │
└─────────────────────────────────────────────────┘
```

---

## 5. Data & Metadata

### 5.1 Cross-Module Dependencies

```yaml
dependencies:
  "1.0 Manifest":
    depends_on: []
    provides: [philosophy, design_principles, ethical_framework]
    
  "1.1 Overview":
    depends_on: ["1.0 Manifest"]
    provides: [architecture_map, module_index, technology_stack]
    
  "1.2 Components":
    depends_on: ["1.0 Manifest", "1.1 Overview"]
    provides: [component_definitions, integration_specs]
    
  "1.3 Security":
    depends_on: ["1.0 Manifest", "1.4 Data Model"]
    provides: [auth_protocols, access_control, veiled_content]
    
  "1.4 Data Model":
    depends_on: ["1.0 Manifest", "2.0 Templates"]
    provides: [schemas, sqlite_tables, packet_specs, versioning_rules]
    
  "1.5 Behaviour Engine":
    depends_on: ["1.0 Manifest", "1.3 Security", "1.4 Data Model"]
    provides: [ai_rules, tone_calibration, reflection_prompts]
    
  "2.0 Templates":
    depends_on: ["1.0 Manifest"]
    provides: [universal_template, mirrorwell_specialisation]
```

### 5.2 Versioning Strategy

**Module versions:** Semantic X.Y format
- X = Major (breaking changes, structural refactors)
- Y = Minor (additions, clarifications, new sections)

**Cross-module compatibility:**
- When 1.4 Data Model changes schema, dependent modules (1.3, 1.5) must be reviewed
- Breaking changes require migration documentation in changelog

### 5.3 File Organisation

```
EhkoForge/
├── 1.0 System Architecture/
│   ├── 1_0_Ehko_Manifest.md
│   ├── 1_0a_Ehko_Manifesto_Personal.md
│   ├── 1_1_Overview_v1_0.md
│   ├── 1_2_Components_v1_0.md
│   ├── 1_3_Security_Ownership.md
│   ├── 1_4_Data_Model_v1_1.md
│   └── 1_5_Behaviour_Engine_v1_1.md
├── 2.0 Modules/
├── 3.0 Templates/
│   └── Universal/
│       └── universal_template.md
├── 4.0 Lexicon/
├── 5.0 Scripts/
│   ├── ehko_refresh.py.md
│   ├── indexing scripts.md
│   └── misc utilities.md
├── _inbox/
└── _ledger/

Mirrorwell/
├── 1_Core Identity/
│   ├── 1.1 Pillars/
│   ├── 1.2 Values & Beliefs/
│   ├── 1.3 Narrative Arcs/
│   └── 1.4 Core Memory Index/
├── 2_Reflection Library/
│   ├── 2.1 Journals/
│   ├── 2.2 Transcripts/
│   ├── 2.3 Messages/
│   └── 2.4 Prompts & Responses/
├── 3_Interpretation Layer/
│   ├── 3.1 Analyses/
│   ├── 3.2 Themes/
│   ├── 3.3 Continuities/
│   └── 3.4 Veiled Content/
├── 4_Archive Corpus/
└── 5_System Indexes/
```

---

## 6. Rules for Change

### 6.1 Module Hierarchy

Changes cascade downward:
1. **1.0 Manifest** changes may affect all modules
2. **1.4 Data Model** changes affect 1.3, 1.5
3. **2.0 Templates** changes affect Mirrorwell content

### 6.2 Backwards Compatibility

- Existing reflection objects must remain valid when modules update
- Migration scripts required for breaking schema changes
- Deprecated fields retained for minimum 2 major versions

### 6.3 Documentation Standards

Every module must include:
- Purpose & Scope (what it does)
- Core Principles (non-negotiable rules)
- Structures & Components (technical definitions)
- Flows & Workflows (how things move)
- Data & Metadata (what's stored where)
- Rules for Change (versioning, deprecation)
- Open Questions / TODOs (acknowledged gaps)
- Changelog (version history)

---

## 7. Open Questions / TODOs

### 7.1 Planned Modules

- [ ] **3.0 Lexicon:** Define official terminology, tag taxonomies, emotional vocabulary
- [ ] **4.0 Scripts:** Specify ehko_refresh.py, inbox processor, export tools
- [ ] **5.0 Recovery:** Define export formats, handoff protocols, multi-generational transfer

### 7.2 Architecture Decisions Pending

- [ ] **Vector database:** Is SQLite sufficient for 10,000+ reflections or need vector search?
- [ ] **Hosted Ehko:** Define "Ehko vault" server architecture for persistent AI hosting
- [ ] **Multi-user:** Can EhkoForge support multiple Ehkos (family members) in shared infrastructure?

### 7.3 Integration Questions

- [ ] **Obsidian sync:** How to handle sync conflicts between mobile/desktop?
- [ ] **AI provider switching:** Define handoff protocol when switching Claude → GPT → local

---

**Changelog**
- v1.1 — 2025-11-26 — Scope reduction: removed MonsterGarden and ManaCore from active scope; simplified to two-vault model (EhkoForge + Mirrorwell); updated architecture diagram, vault definitions, file organisation; removed multi-vault references throughout
- v1.0 — 2025-11-25 — Initial specification: architecture overview, module index, technology stack, flow diagrams, dependency mapping

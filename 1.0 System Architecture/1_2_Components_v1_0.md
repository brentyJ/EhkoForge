---
title: 1.2 Components
vault: EhkoForge
type: module
status: active
version: "1.1"
created: 2025-11-25
updated: 2025-11-26
tags:
  - ehkoforge
  - pinned
  - components
  - architecture
---
# {{title}}

## 1. Purpose & Scope

**This module defines all system components, their responsibilities, interfaces, and relationships.**

It specifies:
- What each component does (single responsibility)
- How components communicate (interfaces, data contracts)
- Dependencies between components (what needs what)
- State management (where state lives, how it flows)
- Failure modes (what happens when components fail)

This is the component map. A developer should be able to:
1. Identify which component handles any given function
2. Understand the data contract between components
3. Build or replace any component in isolation
4. Debug failures by tracing component interactions

---

## 2. Core Principles

### 2.1 Single Responsibility
Each component does one thing well. If a component has multiple responsibilities, it should be split.

### 2.2 Explicit Interfaces
Components communicate through defined contracts. No hidden state, no implicit assumptions.

### 2.3 Replaceable by Design
Every component can be swapped without breaking others. The AI layer, storage backend, and UI are all replaceable.

### 2.4 Fail-Safe Defaults
When a component fails, the system degrades gracefully rather than catastrophically. The archive remains readable even if the AI dies.

### 2.5 Stateless Where Possible
Components should be stateless where feasible. State belongs in files (truth) or SQLite (derived).

---

## 3. Structures & Components

### 3.1 Component Overview

```
┌────────────────────────────────────────────────────────────────────────┐
│                          EHKOFORGE SYSTEM                              │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                 │
│  │   CAPTURE    │  │  PROCESSING  │  │   STORAGE    │                 │
│  │  LAYER       │  │   LAYER      │  │   LAYER      │                 │
│  ├──────────────┤  ├──────────────┤  ├──────────────┤                 │
│  │ Voice Input  │  │ Template     │  │ Vault Files  │                 │
│  │ Text Input   │──▶ Wrapper     │──▶ (Markdown)   │                 │
│  │ Transcript   │  │              │  │              │                 │
│  │ _inbox       │  │ Inbox        │  │ SQLite Index │                 │
│  │              │  │ Processor    │  │              │                 │
│  └──────────────┘  └──────────────┘  └──────────────┘                 │
│         │                │                   │                         │
│         │                │                   │                         │
│         ▼                ▼                   ▼                         │
│  ┌──────────────────────────────────────────────────────────────┐     │
│  │                      INDEX LAYER                              │     │
│  │                   (ehko_refresh.py)                           │     │
│  │  - Scans vault files                                          │     │
│  │  - Parses YAML frontmatter                                    │     │
│  │  - Populates SQLite tables                                    │     │
│  │  - Builds cross-references                                    │     │
│  │  - Calculates specificity scores                              │     │
│  └──────────────────────────────────────────────────────────────┘     │
│                                │                                       │
│                                ▼                                       │
│  ┌──────────────────────────────────────────────────────────────┐     │
│  │                    INTERACTION LAYER                          │     │
│  │                                                                │     │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐              │     │
│  │  │   AUTH     │  │ BEHAVIOUR  │  │  RESPONSE  │              │     │
│  │  │  ENGINE    │  │  ENGINE    │  │ GENERATOR  │              │     │
│  │  ├────────────┤  ├────────────┤  ├────────────┤              │     │
│  │  │ Friend     │  │ Context    │  │ Query      │              │     │
│  │  │ Registry   │  │ Loader     │  │ Processor  │              │     │
│  │  │            │  │            │  │            │              │     │
│  │  │ Challenge  │  │ Tone       │  │ Memory     │              │     │
│  │  │ Generator  │  │ Calibrator │  │ Retrieval  │              │     │
│  │  │            │  │            │  │            │              │     │
│  │  │ Token      │  │ Boundary   │  │ Veiled     │              │     │
│  │  │ Manager    │  │ Enforcer   │  │ Content    │              │     │
│  │  │            │  │            │  │ Filter     │              │     │
│  │  └────────────┘  └────────────┘  └────────────┘              │     │
│  └──────────────────────────────────────────────────────────────┘     │
│                                │                                       │
│                                ▼                                       │
│  ┌──────────────────────────────────────────────────────────────┐     │
│  │                       AI LAYER                                │     │
│  │                   (API-Agnostic)                              │     │
│  │  - Claude API (primary)                                       │     │
│  │  - OpenAI API (fallback)                                      │     │
│  │  - Local LLM (offline fallback)                               │     │
│  └──────────────────────────────────────────────────────────────┘     │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Capture Layer Components

#### 3.2.1 Voice Input Handler

**Responsibility:** Convert voice recordings to text and package for processing.

**Interface:**
```yaml
input:
  - audio_file: binary (wav, m4a, mp3)
  - metadata:
      timestamp: ISO8601
      device: string
      location: string (optional)

output:
  - _inbox packet (JSON)

dependencies:
  - Transcription service (Whisper, cloud API, or manual)
  - _inbox directory write access

failure_mode:
  - If transcription fails: Store audio in _inbox/failed/ for manual processing
  - If write fails: Log error, retry with backoff
```

#### 3.2.2 Text Input Handler

**Responsibility:** Accept raw text and package for processing.

**Interface:**
```yaml
input:
  - raw_text: string
  - source: enum (manual, paste, import)
  - metadata:
      timestamp: ISO8601
      suggested_title: string (optional)
      tags: array[string] (optional)

output:
  - _inbox packet (JSON)
  - OR direct template application (if immediate mode)

dependencies:
  - Template library
  - Vault write access

failure_mode:
  - If validation fails: Return error with specific field issues
  - If write fails: Hold in memory, prompt retry
```

#### 3.2.3 Transcript Importer

**Responsibility:** Parse conversation transcripts (therapy, AI chats, interviews) into reflection objects.

**Interface:**
```yaml
input:
  - transcript_file: text (markdown, txt, json)
  - transcript_type: enum (therapy, ai_chat, interview, other)
  - participant_map: object (optional, maps speakers to names)

output:
  - One or more reflection objects
  - OR _inbox packets for batch processing

processing_rules:
  - Preserve speaker attribution
  - Detect emotional markers (if therapy)
  - Chunk by topic or time if long
  - Tag with source: transcript

dependencies:
  - Template library
  - NLP parsing (optional, for chunking)

failure_mode:
  - If format unrecognised: Treat as raw text, wrap in single reflection
  - If too long: Split at natural breaks, link with related: []
```

#### 3.2.4 _inbox Directory

**Responsibility:** Staging area for asynchronous content capture.

**Structure:**
```
_inbox/
├── pending/           # Awaiting processing
│   ├── 2025-11-25T10-30-00_voice.json
│   └── 2025-11-25T11-45-22_paste.json
├── processed/         # Successfully converted to reflections
│   └── 2025-11-24T09-00-00_voice.json
└── failed/            # Processing errors
    └── 2025-11-23T14-22-00_corrupt.json
```

**Packet Schema:** See 1.4 Data Model Section 4.2 for full specification.

### 3.3 Processing Layer Components

#### 3.3.1 Template Wrapper

**Responsibility:** Apply appropriate template to raw content, populate frontmatter, preserve raw input.

**Interface:**
```yaml
input:
  - raw_content: string
  - content_type: enum (reflection, prepared_message, module)
  - metadata: object (optional overrides)

output:
  - Complete markdown file with:
      - Valid YAML frontmatter
      - Raw Input section (preserved verbatim)
      - Empty sections for interpretation
      - Changelog entry

processing_rules:
  - Determine template from content_type
  - Generate filename: YYYY-MM-DD[-HHMM]_slug.md
  - Populate required frontmatter fields
  - Set version: "1.0"
  - Append changelog: "v1.0 — {date} — Entry created"

dependencies:
  - Template library (2.0 Templates)
  - Slug generator
  - Date formatter

failure_mode:
  - If template missing: Use Universal Template as fallback
  - If required field missing: Prompt for value or use default
```

#### 3.3.2 Inbox Processor

**Responsibility:** Batch process _inbox packets into vault entries.

**Interface:**
```yaml
input:
  - _inbox/pending/*.json

output:
  - Reflection objects in Mirrorwell folders
  - Processed packets moved to _inbox/processed/
  - Failed packets moved to _inbox/failed/ with error log

processing_flow:
  1. Scan _inbox/pending/ for JSON files
  2. For each packet:
     a. Validate packet schema
     b. Call Template Wrapper with packet.payload
     c. Save to Mirrorwell/{year}/{month}/
     d. Move packet to processed/ or failed/
  3. Trigger ehko_refresh.py for index update

scheduling:
  - On-demand (manual trigger)
  - Scheduled (cron, 4x daily)
  - On file system watch (optional)

dependencies:
  - Template Wrapper
  - Vault write access
  - ehko_refresh.py trigger

failure_mode:
  - If packet invalid: Move to failed/ with validation errors
  - If vault write fails: Retry 3x, then move to failed/
  - If all packets fail: Alert via log, continue with next run
```

#### 3.3.3 AI Interpretation Assistant

**Responsibility:** Assist with filling Context, Observations, and Reflection sections (optional, human-in-loop).

**Interface:**
```yaml
input:
  - reflection_object: markdown file
  - sections_to_fill: array[enum] (context, observations, reflection)
  - author_guidance: string (optional)

output:
  - Suggested content for each section
  - Confidence score for each suggestion
  - Human approval required before commit

processing_rules:
  - NEVER modify Raw Input
  - Suggestions are proposals, not final
  - Must be explicitly approved before writing
  - Track AI contributions in changelog

tone_calibration:
  - Match author's writing style (from existing reflections)
  - Preserve voice, not sanitise
  - Flag uncertain interpretations

dependencies:
  - AI Layer (Claude/GPT/local)
  - Style profile (derived from corpus)

failure_mode:
  - If AI unavailable: Skip, leave sections empty
  - If suggestions rejected: Log for style improvement
```

### 3.4 Storage Layer Components

#### 3.4.1 Vault Files (Markdown)

**Responsibility:** Source of truth for all reflection objects.

**Properties:**
```yaml
format: Markdown with YAML frontmatter
encoding: UTF-8
line_endings: LF (Unix)
max_file_size: 1MB (recommended)

directory_structure:
  Mirrorwell/
  ├── 1_Core_Identity/
  │   ├── 1.1 Pillars/
  │   ├── 1.2 Values & Beliefs/
  │   ├── 1.3 Narrative Arcs/
  │   └── 1.4 Core Memory Index/
  ├── 2_Reflection_Library/
  │   ├── 2.1 Journals/
  │   ├── 2.2 Transcripts/
  │   ├── 2.3 Messages/
  │   └── 2.4 Prompts & Responses/
  ├── 3_Interpretation_Layer/
  ├── 4_Archive_Corpus/
  └── 5_System_Indexes/

file_naming:
  reflection: YYYY-MM-DD_slug.md
  with_time: YYYY-MM-DD-HHMM_slug.md
  module: X_Y_Module_Name.md
```

**Durability:**
- Human-readable without software
- Survives platform changes
- Version-controllable (Git)
- Multi-location backup compatible

#### 3.4.2 SQLite Index

**Responsibility:** Derived index for fast querying.

**Properties:**
```yaml
database_file: ehko_index.db
location: EhkoForge/_data/

tables:
  - reflection_objects (core metadata)
  - tags (folksonomy)
  - cross_references (wiki-links)
  - changelog_entries (version history)
  - mirrorwell_extensions (identity-specific fields)
  - emotional_tags (emotion markers)
  - shared_with_friends (authentication support)
  - friend_registry (authentication)
  - shared_memories (contextual auth)
  - authentication_tokens (email verification)
  - authentication_logs (security audit)
  - custodians (handoff management)
  - prepared_messages (direct messages from forger)
  - message_deliveries (delivery tracking)

rebuild_policy:
  - Can be deleted and rebuilt from vault files
  - ehko_refresh.py is authoritative rebuild script
  - Never edit SQLite directly—always through scripts
```

**See 1.4 Data Model Section 4.3 for full schema.**

### 3.5 Index Layer Components

#### 3.5.1 ehko_refresh.py

**Responsibility:** Scan Mirrorwell, parse files, populate SQLite index.

**Interface:**
```yaml
input:
  - vault_path: string (path to Mirrorwell)
  - incremental: boolean (default true—only changed files)
  - force_rebuild: boolean (default false—full rebuild)

output:
  - Updated SQLite database
  - Index report (files processed, errors, stats)

processing_flow:
  1. Load existing index (if incremental)
  2. Scan vault directories recursively
  3. For each .md file:
     a. Calculate content_hash
     b. If hash unchanged and incremental: skip
     c. Parse YAML frontmatter
     d. Extract body sections
     e. Calculate raw_input_hash
     f. Extract tags, cross-references
     g. Calculate specificity_score (for shared_memories)
     h. Upsert into SQLite
  4. Clean orphaned records (files deleted)
  5. Output report

dependencies:
  - YAML parser (PyYAML)
  - Markdown parser (for section extraction)
  - SQLite3
  - hashlib (SHA256)

failure_mode:
  - If file parse fails: Log error, continue with next
  - If database locked: Retry with backoff
  - If catastrophic: Exit with error code, preserve existing index
```

#### 3.5.2 Specificity Scorer

**Responsibility:** Calculate how unique/detailed a memory is for authentication purposes.

**Interface:**
```yaml
input:
  - reflection_object: parsed markdown

output:
  - specificity_score: float (0.0-1.0)
  - challenge_eligible: boolean

scoring_algorithm:
  base_score: 0.5
  
  modifiers:
    +0.15: Contains 3+ proper nouns (people, places, specific things)
    +0.10: Contains specific date/time references
    +0.10: Contains dialogue or quotes
    +0.10: Contains sensory details (sights, sounds, smells)
    +0.05: Contains emotional descriptors beyond basic
    -0.20: Generic event (birthday, christmas, generic dinner)
    -0.15: Single-sentence raw input
    -0.10: No people mentioned
  
  max_score: 1.0
  min_score: 0.0
  
  challenge_eligible_threshold: 0.70

dependencies:
  - NLP tokeniser (basic)
  - Named entity recognition (optional)

failure_mode:
  - If scoring fails: Default to 0.5, challenge_eligible: false
```

### 3.6 Interaction Layer Components

#### 3.6.1 Authentication Engine

**Responsibility:** Verify visitor identity through contextual challenges and fallbacks.

**Sub-components:**

**Friend Registry Manager**
```yaml
responsibility: CRUD operations on friend_registry table
operations:
  - add_friend(name, email, relationship_type, access_level)
  - remove_friend(friend_id)
  - update_friend(friend_id, updates)
  - find_by_name(name) → friend_record
  - find_by_email(email) → friend_record
  - set_blacklist(friend_id, reason)
```

**Challenge Generator**
```yaml
responsibility: Select and pose authentication challenges

interface:
  input:
    - friend_id: integer
  output:
    - challenge_question: string
    - expected_memory_path: string

selection_criteria:
  - specificity_score >= 0.70
  - challenge_eligible = true
  - Prioritise rarely-used memories (times_used ASC)
  - Avoid recently used (last_used > 30 days preferred)
```

**Response Validator**
```yaml
responsibility: Fuzzy match user response against stored memory

interface:
  input:
    - user_response: string
    - expected_memory_path: string
  output:
    - confidence_score: float (0.0-1.0)
    - matched_details: array[string]
    - contradictions: array[string]

matching_algorithm:
  - Extract key entities from both texts
  - Compare: people, locations, actions, emotions, objects
  - Penalise contradictions heavily
  - Allow for paraphrasing and memory variation
```

**Token Manager**
```yaml
responsibility: Generate, validate, and expire email tokens

operations:
  - generate_token(friend_id, claimed_identity) → token_string
  - validate_token(token_string) → {valid, friend_id, expired, used}
  - mark_used(token_string)
  - cleanup_expired()
```

**See 1.3 Security & Ownership for full authentication flow.**

#### 3.6.2 Behaviour Engine

**Responsibility:** Configure Ehko's personality, tone, and interaction boundaries.

**Sub-components:**

**Context Loader**
```yaml
responsibility: Load relevant identity context for conversation

interface:
  input:
    - authenticated_friend: friend_record (optional)
    - conversation_topic: string (optional)
  output:
    - identity_pillars: array[summary]
    - relevant_memories: array[reflection_summary]
    - relationship_context: object (if friend known)
    - conversation_history: array (if exists)

loading_strategy:
  - Always load: Core identity pillars, fundamental values
  - Conditional: Memories tagged with friend name
  - Topic-based: Semantic search on conversation topic
```

**Tone Calibrator**
```yaml
responsibility: Adjust Ehko's response style based on context

parameters:
  warmth: float (0.0-1.0)
  formality: float (0.0-1.0)
  verbosity: float (0.0-1.0)
  humour: float (0.0-1.0)
  directness: float (0.0-1.0)

calibration_rules:
  - Close friends: warmth↑, formality↓, humour↑
  - Descendants: warmth↑, verbosity↑, directness↓
  - Unknown visitors: formality↑, warmth↓, humour↓
  - Sensitive topics: verbosity↓, directness↓
```

**Boundary Enforcer**
```yaml
responsibility: Ensure Ehko stays within defined boundaries

hard_limits:
  - Never reveal veiled content without proper authentication
  - Never fabricate memories not in the archive
  - Never claim certainty about things not recorded
  - Never speak for living people without clear attribution

soft_limits:
  - Redirect harmful questions
  - Acknowledge uncertainty
  - Offer to discuss topics differently
```

**See 1.5 Behaviour Engine for full specification.**

#### 3.6.3 Response Generator

**Responsibility:** Construct Ehko's responses using retrieved context.

**Sub-components:**

**Query Processor**
```yaml
responsibility: Parse user input and determine information needs

interface:
  input:
    - user_message: string
    - conversation_history: array
  output:
    - query_type: enum (factual, emotional, exploratory, challenge)
    - search_terms: array[string]
    - temporal_filter: object (optional)
    - topic_filter: array[string]
```

**Memory Retrieval**
```yaml
responsibility: Fetch relevant memories for response generation

interface:
  input:
    - search_terms: array[string]
    - filters: object
    - max_results: integer (default 10)
  output:
    - relevant_memories: array[reflection_object]
    - confidence_scores: array[float]

retrieval_strategy:
  - Full-text search on title + raw_input
  - Tag matching
  - Temporal proximity
  - Cross-reference graph traversal
```

**Veiled Content Filter**
```yaml
responsibility: Check and enforce content visibility rules

interface:
  input:
    - memory: reflection_object
    - authenticated_identity: friend_record
    - current_date: date
  output:
    - visible: boolean
    - redacted_version: reflection_object (if partially visible)
    - reveal_reason: string (if revealed)

filter_rules:
  - Check revealed: boolean
  - Check reveal_conditions against:
      - Current date (time_locked)
      - Authenticated identity (person_locked)
      - Conversation context (prompt_locked)
```

### 3.7 AI Layer Components

#### 3.7.1 API Wrapper

**Responsibility:** Abstract AI provider specifics behind common interface.

**Interface:**
```yaml
methods:
  - generate_response(prompt, context, parameters) → response
  - generate_embedding(text) → vector
  - validate_connection() → boolean

providers:
  - anthropic: Claude API (claude-sonnet-4-20250514 default)
  - openai: GPT-4 API
  - local: Ollama or similar

configuration:
  primary_provider: anthropic
  fallback_chain: [openai, local]
  timeout_seconds: 30
  max_retries: 3
  
failure_mode:
  - If primary fails: Try next in fallback_chain
  - If all fail: Return graceful error message
  - Log all failures for monitoring
```

#### 3.7.2 Prompt Constructor

**Responsibility:** Build effective prompts from context and user input.

**Interface:**
```yaml
input:
  - user_message: string
  - identity_context: object
  - relevant_memories: array
  - tone_parameters: object
  - conversation_history: array

output:
  - system_prompt: string
  - user_prompt: string
  - context_window_usage: integer (tokens)

construction_rules:
  - System prompt establishes Ehko identity and boundaries
  - Include identity pillars summary
  - Include relevant memories (summarised if needed)
  - Include relationship context (if friend known)
  - Respect context window limits (truncate oldest first)
```

---

## 4. Flows & Workflows

### 4.1 Component Interaction: Reflection Creation

```
[User speaks into phone]
         │
         ▼
┌─────────────────────┐
│  Voice Input        │
│  Handler            │
└─────────────────────┘
         │ (audio file + metadata)
         ▼
┌─────────────────────┐
│  Transcription      │
│  Service (external) │
└─────────────────────┘
         │ (text + metadata)
         ▼
┌─────────────────────┐
│  _inbox/pending/    │
│  [JSON packet]      │
└─────────────────────┘
         │ (trigger)
         ▼
┌─────────────────────┐
│  Inbox Processor    │
│                     │
│  - Validates packet │
│  - Calls Template   │
│    Wrapper          │
└─────────────────────┘
         │
         ▼
┌─────────────────────┐
│  Template Wrapper   │
│                     │
│  - Applies template │
│  - Populates meta   │
│  - Preserves raw    │
└─────────────────────┘
         │ (complete .md file)
         ▼
┌─────────────────────┐
│  Vault Files        │
│  (Mirrorwell/)      │
└─────────────────────┘
         │ (trigger)
         ▼
┌─────────────────────┐
│  ehko_refresh.py    │
│                     │
│  - Parses file      │
│  - Updates index    │
│  - Scores memory    │
└─────────────────────┘
         │
         ▼
┌─────────────────────┐
│  SQLite Index       │
│  (updated)          │
└─────────────────────┘
```

### 4.2 Component Interaction: Ehko Conversation

```
[Friend visits Ehko]
         │
         ▼
┌─────────────────────┐
│  Authentication     │
│  Engine             │
│  - Challenge        │
│  - Validate         │
│  - Grant access     │
└─────────────────────┘
         │ (authenticated_friend)
         ▼
┌─────────────────────┐
│  Context Loader     │
│  - Identity pillars │
│  - Friend memories  │
│  - Relationship     │
└─────────────────────┘
         │ (context_bundle)
         ▼
┌─────────────────────┐
│  Tone Calibrator    │
│  - Set warmth       │
│  - Set formality    │
└─────────────────────┘
         │ (tone_parameters)
         │
         │  [Friend asks question]
         ▼
┌─────────────────────┐
│  Query Processor    │
│  - Parse intent     │
│  - Extract terms    │
└─────────────────────┘
         │ (search_query)
         ▼
┌─────────────────────┐
│  Memory Retrieval   │
│  - SQLite search    │
│  - Rank results     │
└─────────────────────┘
         │ (relevant_memories)
         ▼
┌─────────────────────┐
│  Veiled Content     │
│  Filter             │
│  - Check visibility │
│  - Redact if needed │
└─────────────────────┘
         │ (filtered_memories)
         ▼
┌─────────────────────┐
│  Prompt Constructor │
│  - Build system     │
│  - Build user       │
│  - Manage tokens    │
└─────────────────────┘
         │ (prompts)
         ▼
┌─────────────────────┐
│  API Wrapper        │
│  - Send to Claude   │
│  - Handle fallback  │
└─────────────────────┘
         │ (raw_response)
         ▼
┌─────────────────────┐
│  Boundary Enforcer  │
│  - Check limits     │
│  - Validate claims  │
└─────────────────────┘
         │ (validated_response)
         ▼
[Friend receives Ehko's response]
```

---

## 5. Data & Metadata

### 5.1 Inter-Component Data Contracts

**_inbox Packet → Inbox Processor**
```json
{
  "packet_id": "uuid-v4",
  "timestamp": "ISO8601",
  "type": "reflection",
  "payload": {
    "raw_input": "string (required)",
    "suggested_title": "string (optional)",
    "tags": ["array", "optional"],
    "metadata": {}
  }
}
```

**Template Wrapper → Vault File**
```yaml
# YAML frontmatter (required fields)
title: string
vault: Mirrorwell
type: string
status: active
version: "1.0"
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: []

# Markdown body
## 0. Raw Input (Preserved)
[verbatim payload.raw_input]

## 1. Context
[empty or AI-suggested]

# ... remaining sections
```

**ehko_refresh.py → SQLite**
See 1.4 Data Model Section 4.3 for full table schemas.

### 5.2 State Management

| Component | State Location | Persistence |
|-----------|----------------|-------------|
| Voice Input | _inbox/pending/ | Until processed |
| Template Wrapper | None (stateless) | N/A |
| Inbox Processor | None (stateless) | N/A |
| Vault Files | Filesystem | Permanent |
| SQLite Index | Database file | Rebuildable |
| Auth Engine | SQLite (friend_registry, tokens) | Persistent |
| Behaviour Engine | None (loads from files) | N/A |
| AI Layer | None (stateless) | N/A |

### 5.3 Component Dependencies

```yaml
dependencies:
  voice_input_handler:
    - external: transcription_service
    - internal: _inbox_directory
    
  text_input_handler:
    - internal: template_wrapper
    - internal: vault_files
    
  inbox_processor:
    - internal: template_wrapper
    - internal: vault_files
    - internal: ehko_refresh
    
  template_wrapper:
    - internal: template_library
    
  ehko_refresh:
    - internal: vault_files
    - internal: sqlite_index
    - internal: specificity_scorer
    
  auth_engine:
    - internal: sqlite_index (friend_registry, shared_memories)
    - external: email_service
    
  behaviour_engine:
    - internal: sqlite_index
    - internal: vault_files (identity pillars)
    
  response_generator:
    - internal: sqlite_index
    - internal: vault_files
    - internal: ai_layer
    
  ai_layer:
    - external: anthropic_api
    - external: openai_api (fallback)
    - external: local_llm (fallback)
```

---

## 6. Rules for Change

### 6.1 Adding New Components

1. Define single responsibility
2. Specify interfaces (input/output)
3. Document dependencies
4. Define failure modes
5. Add to component diagram
6. Update dependency graph

### 6.2 Modifying Existing Components

1. Check downstream dependencies
2. Maintain backwards compatibility where possible
3. Version data contracts if breaking
4. Update all affected documentation

### 6.3 Removing Components

1. Ensure no active dependencies
2. Deprecate before removal (min 1 major version)
3. Document removal in changelog
4. Archive component spec

---

## 7. Open Questions / TODOs

### 7.1 Implementation Gaps

- [ ] **Transcription service:** Which service? Whisper API? Local Whisper? Manual fallback?
- [ ] **Email service:** Self-hosted SMTP? SendGrid? Postmark? Authentication token delivery.
- [ ] **File system watcher:** Real-time _inbox processing or scheduled?

### 7.2 Scaling Concerns

- [ ] **Large corpus:** At 10,000+ reflections, does SQLite FTS5 suffice or need vector DB?
- [ ] **Concurrent access:** Multiple devices editing same vault—conflict resolution?
- [ ] **AI context limits:** How to summarise identity when corpus exceeds context window?

### 7.3 Future Components

- [ ] **Ehko Form Renderer:** Generate visual representation from reflection data
- [ ] **Export Engine:** Generate archive bundles in multiple formats
- [ ] **Migration Tool:** Import from other journaling apps (Day One, Notion, etc.)

---

**Changelog**
- v1.1 — 2025-11-26 — Scope reduction: removed MonsterGarden and ManaCore references; simplified to single-vault model (Mirrorwell only); updated component interfaces, data contracts, and directory structures; removed multi-vault enum values
- v1.0 — 2025-11-25 — Initial specification: component definitions, interfaces, data contracts, interaction flows, dependency mapping

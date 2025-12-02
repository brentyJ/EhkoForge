---
title: "ReCog Engine Specification"
vault: "EhkoForge"
type: "module"
category: "Core Architecture"
status: draft
version: "0.2"
created: 2025-12-02
updated: 2025-12-02
tags: [ehkoforge, recog, recursion, cognition, architecture]
related:
  - "1_5_Behaviour_Engine_v1_1.md"
  - "1_4_Data_Model_v1_3.md"
  - "Ingot_System_Schema_v0_1.md"
  - "1_7_Core_Memory_Index_Framework_v1_0.md"
---

# RECOG ENGINE SPECIFICATION v0.2

## 1. Purpose & Scope

### 1.0 Technical Framing Note

**ReCog is a data processing pipeline, not a cognitive model.** Any functional parallels to human cognition emerge from the recursive structure, not from explicit neurological simulation. The term "cognition" in the name is metaphorical, referring to iterative refinement processes, not brain modelling.

This is software engineering, not neuroscience.

### 1.1 What ReCog Is

**ReCog Engine** (Recursive Cognition Engine) is the processing orchestration layer that drives iterative content refinement within EhkoForge.

It transforms:
- **Raw input** (chats, transcripts, reflections) → **Distilled insights** (ingots)
- **Isolated insights** → **Cross-correlated patterns**
- **Patterns** → **Integrated personality components**

ReCog is the answer to: *"How do we make the insight refinement process reliable and controllable instead of emergent and accidental?"*

### 1.2 What ReCog Is Not

- **Not a separate AI model.** ReCog orchestrates existing LLM calls, it doesn't replace them.
- **Not a cognitive science framework.** It borrows useful metaphors but doesn't claim to model human cognition.
- **Not a replacement for the Ingot System.** ReCog *uses* the Ingot System as its data layer.
- **Not magic.** It's a processing pipeline with defined stages, triggers, and termination conditions.

### 1.3 Position in Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        EHKOFORGE                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────┐  │
│  │ Raw Input   │───▶│ ReCog Engine│───▶│ Ehko Personality    │  │
│  │ (Mirrorwell)│    │             │    │ (Behaviour Engine)  │  │
│  └─────────────┘    │ ┌─────────┐ │    └─────────────────────┘  │
│                     │ │ Ingot   │ │                             │
│                     │ │ System  │ │                             │
│                     │ └─────────┘ │                             │
│                     └─────────────┘                             │
│                            │                                    │
│                     ┌──────┴──────┐                             │
│                     │ Identity    │                             │
│                     │ Anchors     │                             │
│                     │ (Pillars,   │                             │
│                     │ Core Memory)│                             │
│                     └─────────────┘                             │
└─────────────────────────────────────────────────────────────────┘
```

**Dependencies:**
- Uses `Ingot System` tables for data storage
- Reads `Core Memory Index` and `Identity Pillars` for coherence anchoring
- Outputs to `ehko_personality_layers` for Behaviour Engine consumption

---

## 2. Core Concepts

### 2.1 How Recursion Is Implemented

In ReCog, recursion means: **iterative passes over accumulated content, where each pass refines and correlates insights from previous passes**.

It is NOT:
- A function calling itself
- Infinite regress
- General-purpose metacognition

It IS:
- Pass N reads output from Pass N-1
- Each pass may: refine existing ingots, extract new ingots, merge related ingots, update significance scores
- Passes continue until termination conditions are met

### 2.2 The Three Loops

ReCog operates three distinct processing loops:

| Loop | Frequency | Scope | Purpose |
|------|-----------|-------|---------|
| **Extraction Loop** | Per smelt batch | Single source | Extract ingots from raw content |
| **Correlation Loop** | Daily/on-demand | Ingot pool | Find patterns across ingots |
| **Integration Loop** | On user accept | Single ingot | Convert ingot to personality layer |

### 2.3 Termination Conditions

Every loop must have explicit termination:

**Extraction Loop terminates when:**
- All content in smelt_queue batch is processed
- Max passes reached (configurable, default: 3)
- No new ingots extracted for 2 consecutive passes

**Correlation Loop terminates when:**
- All ingot pairs checked once
- Max correlation passes reached (default: 2)
- Correlation yield drops below threshold (< 5% new connections)

**Integration Loop terminates when:**
- Single ingot successfully converted to personality layer
- (This loop is not recursive — it's a single transformation)

---

## 3. Processing Stages

### 3.1 Stage 0: Pre-Annotation (Tier 0 — Code)

**Trigger:** New content enters system (chat message, transcript upload, reflection file)

**Process:**
1. Extract keywords and entities
2. Detect intensity markers (exclamation, emphasis, repetition)
3. Identify emotional signals (lexicon matching)
4. Flag potential themes
5. Calculate word count for batching decisions

**Output:** `pre_annotation_json` stored in `smelt_queue` or `transcript_segments`

**No LLM cost.** Pure code processing.

### 3.2 Stage 1: Extraction (Tier 2 — Smelt)

**Trigger:** Smelt batch initiated (manual or scheduled)

**Process:**
```
FOR each item in smelt_queue WHERE status = 'pending':
    
    1. Load content + pre_annotation_json
    2. Load user annotations (if any)
    3. Load relevant Identity Pillars (context)
    4. Load recent ingots (avoid duplication)
    
    5. LLM CALL (Tier 2):
       - Prompt: "Extract insights from this content"
       - Include: pre-annotations as hints
       - Include: user annotations as priority signals
       - Include: identity context for coherence
       - Include: existing ingot summaries to prevent duplicates
    
    6. Parse LLM response into ingot candidates
    
    7. FOR each candidate:
       - Check similarity against existing ingots
       - If similar (>0.8 cosine): flag for merge review
       - If novel: create new ingot
       - Link to source via ingot_sources
       - Log to ingot_history
    
    8. Update smelt_queue: status = 'complete', pass_count++

LOOP TERMINATION:
    - Queue empty, OR
    - Max passes reached
```

**Output:** New or updated ingots in `ingots` table

### 3.3 Stage 2: Correlation (Tier 2/3)

**Trigger:** Correlation scheduled (daily cron or manual)

**Process:**
```
1. Load all ingots WHERE status IN ('raw', 'refined')

2. Group by theme (themes_json overlap)

3. FOR each theme group:
    - If group size >= 3:
        
        LLM CALL (Tier 2):
        - Prompt: "What pattern connects these insights?"
        - Include: ingot summaries + sources
        - Ask: "Is this a recurring theme, a contradiction, or unrelated?"
        
        IF pattern found:
            - Create new 'pattern' ingot
            - Link original ingots as sources
            - OR merge into existing pattern ingot
            - Update significance of source ingots

4. FOR ingots with no theme matches:
    - LLM CALL (Tier 2):
        - Prompt: "Does this connect to any Identity Pillar?"
        - Include: pillar summaries
        
    IF pillar link found:
        - Update ingot.patterns_json
        - Update significance (pillar-linked = +0.15)

LOOP TERMINATION:
    - All groups processed, OR
    - Max passes reached, OR
    - Yield below threshold
```

**Output:** Pattern ingots, updated significance scores, pillar links

### 3.4 Stage 3: Surfacing

**Trigger:** After each Extraction or Correlation pass

**Process:**
```
FOR each ingot WHERE status IN ('raw', 'refined'):
    
    SURFACE_IF any of:
        - significance >= SURFACING_THRESHOLD (default: 0.5) AND pass_count >= 2
        - source_count >= 3 (cross-correlation insight)
        - age > 7 days AND status = 'raw' (anti-stagnation)
        - User manually queued for review
    
    IF SURFACE_IF:
        - Update status = 'surfaced'
        - Log to ingot_history
```

**Output:** Ingots moved to `surfaced` status, visible in Forge UI queue

### 3.5 Stage 4: User Review

**Trigger:** User opens Forge mode, views surfaced ingots

**User Actions:**
- **Accept** → Proceed to Integration
- **Reject** → status = 'rejected', excluded from Ehko
- **Defer** → remains in queue, significance decays slightly over time
- **Edit** → User can adjust summary before accepting

**No automated processing.** Human in the loop.

### 3.6 Stage 5: Integration (On Accept)

**Trigger:** User clicks "Accept" on surfaced ingot

**Process:**
```
1. Determine layer_type:
    - If themes contain 'trait', 'personality' → layer_type = 'trait'
    - If themes contain 'memory', 'experience' → layer_type = 'memory'
    - If themes contain 'pattern', 'tendency' → layer_type = 'pattern'
    - If themes contain 'value', 'belief' → layer_type = 'value'
    - If themes contain 'voice', 'speech' → layer_type = 'voice'
    - Default: 'trait'

2. Generate personality instruction:
    
    LLM CALL (Tier 2):
    - Prompt: "Convert this insight into a concise personality instruction"
    - Input: ingot summary + themes + sources
    - Output format: Single sentence, imperative or descriptive
    - Example: "Tends to use humour as deflection when discussing family conflict"

3. Create ehko_personality_layers record:
    - ingot_id = accepted ingot
    - layer_type = determined above
    - content = generated instruction
    - weight = significance (0.0-1.0)
    - active = 1
    - integrated_at = NOW()

4. Update ingot:
    - status = 'forged'
    - forged_at = NOW()

5. Log to ingot_history

6. OPTIONAL: Create Mirrorwell reflection file
    - If forged ingot represents significant insight
    - User can toggle this behaviour
```

**Output:** New personality layer, forged ingot, optional reflection file

---

## 4. Coherence Anchoring

### 4.1 Purpose

Prevent semantic drift. Ensure insights align with authentic identity rather than drifting toward generic LLM outputs.

### 4.2 Anchor Sources

| Source | How Used |
|--------|----------|
| **Identity Pillars** | Loaded as context during extraction; pillar links boost significance |
| **Core Memory Index** | Cross-referenced during correlation; core memories anchor patterns |
| **Voice Profile** (Behaviour Engine) | Guides personality instruction generation |
| **Forged Layers** | Previous layers provide consistency baseline |

### 4.3 Drift Detection

**Not implemented in v0.1.** Future consideration.

Concept: Compare new ingot summaries against existing personality layers. Flag if:
- Contradicts existing layer without acknowledging evolution
- Uses language inconsistent with voice profile
- Makes claims not grounded in source material

---

## 5. Data Structures

### 5.1 New Fields (Extensions)

No new tables required. ReCog uses existing Ingot System tables.

**Suggested additions to `ingots` table (future migration):**

```sql
-- v0.2 additions
pillar_links_json TEXT,           -- JSON array of linked Identity Pillars
coherence_score REAL,             -- 0.0-1.0 alignment with identity
drift_flags_json TEXT,            -- JSON array of drift warnings
correlation_pass INTEGER DEFAULT 0 -- how many correlation passes
```

### 5.2 Processing State

ReCog maintains processing state in existing tables:

| State | Stored In |
|-------|-----------|
| Extraction progress | `smelt_queue.status`, `smelt_queue.pass_count` |
| Ingot lifecycle | `ingots.status`, `ingots.analysis_pass` |
| Audit trail | `ingot_history` |
| User decisions | `ingots.status` (forged/rejected) |
| Personality output | `ehko_personality_layers` |

---

## 6. Configuration

### 6.1 Tuneable Parameters

```yaml
# recog_config.yaml

extraction:
  max_passes: 3                    # Per-item extraction passes
  batch_size: 10                   # Items per smelt batch
  similarity_threshold: 0.8        # Cosine threshold for merge detection

correlation:
  max_passes: 2                    # Correlation loop iterations
  min_group_size: 3                # Minimum ingots for theme group
  yield_threshold: 0.05            # Stop if < 5% new connections
  pillar_boost: 0.15               # Significance boost for pillar link

surfacing:
  significance_threshold: 0.5      # Minimum significance to surface
  min_passes: 2                    # Minimum passes before surfacing
  cross_correlation_threshold: 3   # Source count for auto-surface
  stagnation_days: 7               # Days before anti-stagnation surfaces

integration:
  create_reflection_file: false    # Toggle reflection file creation
  default_weight: 1.0              # Default layer weight
```

### 6.2 LLM Model Routing

ReCog uses existing `provider_factory.py` for model selection:

| Stage | Role | Default Model |
|-------|------|---------------|
| Pre-Annotation | N/A (code) | N/A |
| Extraction | `smelt` | Sonnet (Tier 2) |
| Correlation | `correlation` | Sonnet (Tier 2) |
| Integration | `integration` | Sonnet (Tier 2) |
| Deep Analysis | `deep_analysis` | Opus (Tier 3) — future |

---

## 7. API Endpoints

### 7.1 Planned Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/recog/status` | GET | Current processing state |
| `/api/recog/trigger/extraction` | POST | Manually trigger extraction loop |
| `/api/recog/trigger/correlation` | POST | Manually trigger correlation loop |
| `/api/recog/config` | GET/PUT | View/update configuration |

### 7.2 Integration with Existing Endpoints

ReCog extends existing Forge server endpoints:

- `/api/smelt/trigger` → Invokes ReCog Extraction Loop
- `/api/ingots/accept` → Invokes ReCog Integration Loop
- `/api/ingots/queue` → Returns surfaced ingots (ReCog Stage 3 output)

---

## 8. Implementation Order

### Phase 1: Foundation (Current)
- [x] Ingot System schema
- [x] Basic smelt processing
- [x] Forge UI with ingot queue

### Phase 2: ReCog Core
- [ ] Extraction Loop with pass tracking
- [ ] Coherence context loading (pillars, core memory)
- [ ] Surfacing logic with configurable thresholds
- [ ] Integration Loop with personality layer generation

### Phase 3: Correlation
- [ ] Theme-based grouping
- [ ] Correlation Loop with pattern detection
- [ ] Pillar linking
- [ ] Cross-correlation ingots

### Phase 4: Refinement
- [ ] Drift detection
- [ ] Significance decay (anti-stagnation)
- [ ] Merge UI and logic
- [ ] Configuration UI

---

## 9. What This Does NOT Include

Explicitly out of scope for v0.1:

- **Automatic personality layer weighting** — All layers weight 1.0
- **Drift detection and correction** — Deferred
- **Contradiction resolution** — Flag only, no auto-resolve
- **Multi-user/multi-Ehko** — Single forger assumed
- **Real-time processing** — Batch only
- **Voice analysis** — Text only, no audio processing

---

## 10. Open Questions

### 10.1 Architectural

- [ ] Should correlation run automatically or only on-demand?
- [ ] What triggers deep analysis (Tier 3)?
- [ ] How to handle contradictory ingots (belief evolution vs error)?

### 10.2 UX

- [ ] How to visualise ingot lineage in UI?
- [ ] Should users see correlation groups before surfacing?
- [ ] Notification when new insights surface?

### 10.3 Performance

- [ ] At what ingot count does correlation become expensive?
- [ ] Caching strategy for pillar/core memory context?
- [ ] Incremental vs full re-correlation?

---

## 11. Cross-References

**Depends on:**
- [[Ingot_System_Schema_v0_1|Ingot System Schema]] — Data layer
- [[1_4_Data_Model_v1_3|Data Model]] — Base schema
- [[1_5_Behaviour_Engine_v1_1|Behaviour Engine]] — Voice profile, personality layers
- [[1_7_Core_Memory_Index_Framework_v1_0|Core Memory Index]] — Coherence anchoring

**Consumed by:**
- [[forge_server.py]] — API implementation
- [[6.0 Frontend]] — Forge UI

**Vocabulary:**
- [[4_0_Lexicon_v1_0]] — Term definitions

---

**Changelog**
- v0.2 — 2025-12-02 — Framing clarification: Added technical disclaimer (Section 1.0), replaced "meaning-making" with "refinement", renamed Section 2.1 to emphasize implementation over metaphor. No functional changes.
- v0.1 — 2025-12-02 — Initial specification. Defines purpose, processing stages, loops, termination conditions, coherence anchoring, configuration. Scoped for batch processing only.

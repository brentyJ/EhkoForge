---
title: 4.0 Lexicon
vault: EhkoForge
type: module
category: Reference
status: active
version: "1.0"
created: 2025-11-28
updated: 2025-11-28
tags:
  - ehkoforge
  - pinned
  - lexicon
  - taxonomy
  - vocabulary
---
# {{title}}

## 1. Purpose & Scope

**This module defines the canonical vocabulary for the EhkoForge system.**

It specifies:
- Core terminology and definitions
- Tag taxonomies (general, emotional, system)
- Controlled vocabularies for frontmatter fields
- Relationship type definitions
- Access level hierarchy
- Status and type enumerations

This is the reference spec. Any developer, AI agent, or future maintainer should be able to:
1. Understand what any EhkoForge term means
2. Select appropriate tags from defined taxonomies
3. Use correct values for controlled vocabulary fields
4. Maintain consistency across vaults and modules

---

## 2. Core Principles

### 2.1 Controlled Where It Matters
Some fields use **controlled vocabularies** (fixed allowed values). Others use **folksonomies** (free-form, user-defined). This module distinguishes between them.

### 2.2 Australian English
All terminology uses Australian spelling: behaviour, organisation, colour, analyse, etc.

### 2.3 Lowercase and Hyphenated
Tags are lowercase, hyphenated for multi-word terms: `core-memory`, `first-contact`, `identity-pillar`.

### 2.4 Extensible With Care
New terms can be added but existing terms should not be redefined. Deprecate rather than delete.

---

## 3. Core Terminology

### 3.1 System Terms

| Term | Definition |
|------|------------|
| **Ehko** | The output of the EhkoForge system—a structured, durable, AI-readable archive of identity, memory, and meaning that can interact with visitors after the creator's death. Pronounced "echo". |
| **Forger** | The human creator of an Ehko. The person whose identity, memories, and values are preserved. |
| **Visitor** | Any person interacting with an Ehko after the forger's death (or during legacy mode testing). |
| **Custodian** | A trusted person with administrative authority over an Ehko after the forger's death. Can override access, authenticate edge cases, and make structural decisions. |
| **EhkoForge** | The framework/system that builds Ehkos. Contains specifications, templates, and architecture. The "forge" where Ehkos are created. |
| **Mirrorwell** | The personal vault containing the forger's reflections, memories, and identity material. The source content that feeds the Ehko. Named for its function as a reflective surface into the self. |
| **Reflection Object** | Any structured markdown file conforming to the Universal Template Framework. The atomic unit of content in both vaults. |
| **Raw Input** | The original, unedited text captured exactly as written or dictated. Sacred—never modified after creation. |
| **Identity Pillar** | A fundamental aspect of the forger's identity (values, traits, beliefs) derived from patterns across reflections. |
| **Core Memory** | A reflection flagged as particularly significant to the forger's identity or life narrative. |
| **Prepared Message** | A direct communication left by the forger for specific people or conditions, delivered by the Ehko as a messenger. |
| **Veiled Content** | Content marked `revealed: false` that is hidden by default and only accessible under specific conditions. |

### 3.2 Mode Terms

| Term | Definition |
|------|------------|
| **Reflection Mode** | Ehko behaviour when interacting with the living forger. Focuses on facilitation, mirroring, and pattern surfacing. |
| **Legacy Mode** | Ehko behaviour when interacting with visitors after the forger's death. Focuses on sharing memories and perspectives in third person. |
| **Support Mode** | Ehko behaviour activated when emotional distress is detected. Focuses on presence, validation, and appropriate boundaries. |

### 3.3 Authentication Terms

| Term | Definition |
|------|------------|
| **Contextual Authentication** | Primary authentication method using shared memory challenges—questions only a genuine friend would know. |
| **Specificity Score** | A 0.0-1.0 rating of how unique/detailed a shared memory is. Higher scores = better authentication challenges. |
| **Friend Registry** | Database of known people in the forger's life with relationship metadata and authentication history. |
| **Blacklist** | Friends marked as denied access, with optional reason. Ehko will not authenticate or engage with blacklisted individuals. |

---

## 4. Tag Taxonomies

### 4.1 General Tags (Folksonomy)

Free-form tags for content categorisation. These are recommendations, not restrictions.

**Life Domains:**
- `family`, `friends`, `work`, `health`, `creativity`, `spirituality`, `politics`, `technology`

**Life Events:**
- `milestone`, `transition`, `loss`, `celebration`, `conflict`, `resolution`

**Content Types:**
- `story`, `opinion`, `question`, `realisation`, `memory`, `plan`, `dream`

**Time Markers:**
- `childhood`, `adolescence`, `early-adulthood`, `adulthood`, `recent`

**People (as tags):**
- Use lowercase first names: `theo`, `jono`, `dad`, `mum`
- For privacy, use relationship terms for sensitive content: `ex-partner`, `therapist`

### 4.2 Emotional Tags (Controlled Vocabulary)

Used in the `emotional_tags` frontmatter field. These map to the Behaviour Engine's emotion detection.

**Primary Emotions:**
| Tag | Description |
|-----|-------------|
| `joy` | Happiness, delight, contentment, elation |
| `sadness` | Sorrow, melancholy, disappointment, loss |
| `anger` | Frustration, irritation, rage, indignation |
| `fear` | Anxiety, worry, dread, terror |
| `surprise` | Shock, astonishment, unexpectedness |
| `disgust` | Revulsion, contempt, moral outrage |

**Complex Emotions:**
| Tag | Description |
|-----|-------------|
| `grief` | Deep sorrow from loss, mourning |
| `shame` | Self-directed negative judgment, embarrassment |
| `guilt` | Regret over actions, responsibility for harm |
| `pride` | Satisfaction in achievement, self-worth |
| `love` | Deep affection, attachment, care |
| `gratitude` | Thankfulness, appreciation |
| `hope` | Optimism, positive expectation |
| `nostalgia` | Bittersweet longing for the past |
| `clarity` | Insight, understanding, breakthrough |
| `confusion` | Uncertainty, disorientation, ambiguity |
| `relief` | Release of tension, burden lifted |
| `loneliness` | Isolation, disconnection, longing for connection |
| `contentment` | Peaceful satisfaction, acceptance |
| `anxiety` | Persistent worry, unease, apprehension |
| `overwhelm` | Feeling flooded, too much to process |
| `vulnerability` | Exposure, openness, emotional risk |
| `acceptance` | Coming to terms, letting go of resistance |
| `resentment` | Lingering bitterness, unresolved anger |
| `compassion` | Care for others' suffering, empathy |
| `self-compassion` | Care for one's own suffering, self-kindness |

### 4.3 System Tags (Controlled Vocabulary)

Used in EhkoForge modules and system content.

| Tag | Usage |
|-----|-------|
| `ehkoforge` | All EhkoForge vault content |
| `mirrorwell` | Cross-references to Mirrorwell content |
| `pinned` | High-priority, frequently-referenced content |
| `architecture` | System design and structure |
| `specification` | Implementation-ready specs |
| `template` | Template definitions |
| `framework` | Conceptual frameworks |
| `script` | Code and automation |
| `deprecated` | Superseded content (keep for history) |

### 4.4 Prepared Message Tags

| Tag | Usage |
|-----|-------|
| `prepared-message` | All prepared messages (required) |
| `first-contact` | Delivered on first visit |
| `milestone` | Triggered by life events |
| `comfort` | Triggered by distress detection |
| `topic-triggered` | Activated by conversation topic |

---

## 5. Controlled Vocabularies

### 5.1 Object Types (`type` field)

| Value | Vault | Description |
|-------|-------|-------------|
| `reflection` | Mirrorwell | Personal journal entry, memory, or thought |
| `prepared_message` | Mirrorwell | Direct message for future delivery |
| `module` | EhkoForge | System specification document |
| `framework` | EhkoForge | Conceptual or architectural framework |
| `specification` | EhkoForge | Implementation-ready technical spec |
| `template` | Both | Reusable document structure |
| `index` | Both | Navigation or reference document |

### 5.2 Object Status (`status` field)

| Value | Description |
|-------|-------------|
| `active` | Current, valid, in use |
| `draft` | Work in progress, not yet canonical |
| `archived` | No longer current but preserved for history |
| `deprecated` | Superseded by newer version, scheduled for removal |

### 5.3 Relationship Types (`relationship_type` field)

Used in friend_registry and relationship modifiers.

| Value | Description | Default Access |
|-------|-------------|----------------|
| `spouse` | Life partner, married or equivalent | elevated |
| `partner` | Romantic partner, not spouse | elevated |
| `child` | Son or daughter (any age) | elevated |
| `parent` | Mother or father | standard |
| `sibling` | Brother or sister | standard |
| `close_friend` | Inner circle, deep trust | standard |
| `friend` | General friendship | standard |
| `extended_family` | Aunts, uncles, cousins, etc. | standard |
| `colleague` | Work relationship | restricted |
| `acquaintance` | Known but not close | restricted |
| `unknown` | Identity not established | restricted |

### 5.4 Access Levels (`access_level` field)

| Value | Description | Capabilities |
|-------|-------------|--------------|
| `elevated` | Closest relationships | All content including most veiled; can trigger comfort messages; receives relationship-specific forger references ("your dad") |
| `standard` | Known friends and family | General content; some veiled content by condition; standard authentication |
| `restricted` | Acquaintances or unknown | Public content only; no veiled access; full authentication required |
| `blacklisted` | Denied access | No interaction permitted |

### 5.5 Trigger Types (`trigger_type` field)

For prepared messages.

| Value | Description | Activation |
|-------|-------------|------------|
| `first_contact` | Delivered on first authenticated visit | Automatic after authentication |
| `topic` | Activated when specific topic arises | Keyword/phrase detection in conversation |
| `milestone` | Triggered by life events | Visitor mentions wedding, birth, graduation, etc. |
| `distress` | Triggered by emotional distress | Grief/crisis language detection |
| `manual` | Requires specific phrase | Visitor says exact trigger phrase |

### 5.6 Source Types (`source` field)

| Value | Description |
|-------|-------------|
| `internal` | Written directly by forger in Obsidian |
| `dictation` | Voice recording transcribed |
| `transcript` | Conversation or interview transcript |
| `therapy` | Notes from therapy sessions |
| `conversation` | Extracted from chat/messaging |
| `import` | Migrated from external system |
| `ai_generated` | Created or drafted by AI (lower confidence) |

### 5.7 Confidence Levels

Numeric scale with semantic meaning.

| Range | Label | Evidence Level | Ehko Language |
|-------|-------|----------------|---------------|
| 0.85-1.0 | High | Direct quote, repeated theme | "Brent was clear about this..." |
| 0.60-0.84 | Medium | Indirect reference, inferred | "Based on what Brent wrote, it seems..." |
| 0.30-0.59 | Low | Thin documentation, old | "I'm not certain what Brent thought..." |
| 0.0-0.29 | None | No evidence in archive | "I don't have any record..." |

---

## 6. Naming Conventions

### 6.1 File Names

**Mirrorwell reflections:**
```
YYYY-MM-DD_descriptive-slug.md
YYYY-MM-DD-HHMM_descriptive-slug.md  (for multiple same-day entries)
```

**EhkoForge modules:**
```
X_Y_Module_Name_vZ_W.md
```
Where X.Y = module number, Z.W = version.

**Examples:**
- `2024-08-15_jessies-last-day.md`
- `2024-08-15-1430_afternoon-walk-reflection.md`
- `1_5_Behaviour_Engine_v1_1.md`

### 6.2 Frontmatter Conventions

- Field names: `snake_case`
- String values: quoted if containing special characters
- Arrays: YAML list format `[item1, item2]` or multi-line
- Dates: `YYYY-MM-DD` (no time, no timezone)
- Versions: quoted strings `"1.0"` to prevent YAML float interpretation

### 6.3 Cross-Reference Format

Wiki-link style with optional type hint:
```markdown
[[File Name]]
[[File Name|display text]]
[[1.2 Core Memory Index|memory]]
```

---

## 7. Extensibility

### 7.1 Adding New Tags

**General tags:** Add freely. No approval needed.

**Emotional tags:** 
1. Check if existing tag covers the concept
2. If genuinely new, add to Section 4.2 with description
3. Update Behaviour Engine emotion detection if needed
4. Bump Lexicon version

**System tags:**
1. Document use case
2. Add to Section 4.3
3. Bump Lexicon version

### 7.2 Adding New Controlled Vocabulary Values

1. Document the new value with description
2. Add to appropriate section (5.x)
3. Check for conflicts with existing values
4. Update dependent modules (Data Model, Behaviour Engine)
5. Bump Lexicon version

### 7.3 Deprecating Terms

1. Do NOT remove from this document
2. Mark with `(deprecated)` suffix
3. Add deprecation note with date and replacement term
4. Retain for minimum 2 major versions

---

## 8. Quick Reference Card

### Most Common Tags
```yaml
# Mirrorwell reflections
tags: [family, memory, core-memory]
emotional_tags: [grief, love, clarity]

# EhkoForge modules  
tags: [ehkoforge, pinned, architecture]
```

### Required Frontmatter
```yaml
title: string
vault: Mirrorwell | EhkoForge
type: reflection | module | prepared_message | ...
status: active | draft | archived | deprecated
version: "X.Y"
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: []
```

### Mirrorwell Extensions
```yaml
emotional_tags: []
core_memory: true | false
identity_pillar: string | null
shared_with: [names]
source: internal | dictation | transcript | ...
confidence: 0.0-1.0
revealed: true | false
```

---

## 9. Open Questions / TODOs

- [ ] **Emotion taxonomy validation:** Review against psychological literature for completeness
- [ ] **Localisation:** Should non-English Ehkos have translated emotion terms?
- [ ] **Tag synonyms:** Should `grief` and `mourning` be treated as equivalent?
- [ ] **Auto-tagging:** Can ehko_refresh.py suggest tags from content analysis?
- [ ] **Tag frequency tracking:** Monitor which tags are actually used to prune unused ones

---

**Changelog**
- v1.0 — 2025-11-28 — Initial lexicon: core terminology, tag taxonomies (general, emotional, system, prepared message), controlled vocabularies (type, status, relationship, access level, trigger type, source, confidence), naming conventions, extensibility rules, quick reference

---

## 10. Cross-References

**Used by:**
- [[1_4_Data_Model_v1_3|Data Model]] — Frontmatter field values
- [[1_5_Behaviour_Engine_v1_1|Behaviour Engine]] — Emotion detection, relationship modifiers
- [[1_3_Security_Ownership|Security & Ownership]] — Access levels, relationship types

**Defines vocabulary for:**
- [[universal_template|Universal Template]] — Base frontmatter fields
- Mirrorwell reflection_template — Emotional tags, source types

**Related:**
- [[1_0_Ehko_Manifest|Manifest]] — Core terminology origins

**Navigation:**
- [[_Index|← Back to Index]]
- [[1_6_Identity_Pillars_Scientific_Basis_v1_0|← Previous: Identity Pillars]]

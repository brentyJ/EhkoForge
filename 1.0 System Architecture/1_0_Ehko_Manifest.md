---
title: "1.0 Ehko Manifest"
vault: EhkoForge
type: module
status: canonical
version: "3.0"
created: 2025-11-22
updated: 2026-01-20
tags:
  - ehkoforge
  - pinned
  - architecture
  - manifesto
---
# {{title}}

*A foundational charter for the EhkoForge system*

---

## 1. What EhkoForge Is

EhkoForge is a framework for building a structured, AI-augmented archive of your reflections, values, memories, and thinking patterns. It combines:

- **Journaling infrastructure** — Obsidian vaults with templated markdown files
- **Indexing layer** — SQLite database for querying across time and themes
- **AI interaction layer** — Works with Claude, GPT, local models—whatever survives
- **Durability-first architecture** — Human-readable formats that don't require specific software

The output—your "Ehko"—is an organised, contextualised record of who you were, what you believed, and how you changed. A library of your inner world, built to last decades, not just years.

**The core workflow:**
1. Write reflections (journals, conversations, voice transcriptions)
2. System indexes and processes content
3. AI extracts structured insights
4. You review and accept what matters
5. Accepted insights build your Ehko's profile
6. Export everything in durable formats

---

## 2. Why This Exists

Two problems this solves:

**Problem 1: AI context doesn't persist.**
Every conversation with an LLM starts from zero. You re-explain yourself constantly. EhkoForge maintains persistent context—your values, patterns, preferences—so AI interactions build on what came before rather than starting fresh.

**Problem 2: Personal history gets lost.**
Most people leave behind fragments: photos, scattered notes, stories filtered through others. Descendants interpret through silence and guesswork. EhkoForge creates an intentional record—your actual thoughts, in your own words, contextualised and preserved.

---

## 3. Who This Is For

EhkoForge is designed for people who:

- Use AI as a thinking tool and want that context to persist across sessions
- Want to leave something more meaningful than photo albums for descendants
- Care about data ownership and want export-first architecture
- See value in structured self-reflection

**Not for everyone.** If the idea of structured self-reflection with AI feels wrong, that's valid. This project doesn't try to convince anyone.

---

## 4. Core Principles

### 4.1 Ownership & Sovereignty

- All data belongs to you. The system is a steward, not an owner.
- Redaction, veiled content, and deletion are first-class features.
- No silent training or hidden data extraction.

### 4.2 Durability by Design

- **The archive must outlast the tools that created it.**
- Markdown + YAML = human-readable without software
- SQLite = self-contained, no server dependencies
- No proprietary formats that require specific companies to survive
- The data layer and interaction layer are separable

### 4.3 Context Over Time

- An individual is not a highlight reel
- The system preserves contradictions, mistakes, growth, and evolution
- Every belief is timestamped: *this is what I believed then*
- Contextual metadata matters as much as content

### 4.4 AI as Scaffolding

- AI structures chaotic thought rather than replacing agency
- The system provides rails, not cages
- The Ehko helps you become *more* yourself, not less

---

## 5. What an Ehko Is (and Isn't)

**An Ehko is:**
- A curated digital archive authored by you
- Designed to speak *about* you on your behalf
- Like a written memoir that can answer questions and surface relevant context

**An Ehko is not:**
- A digital clone or resurrection
- A replacement for human relationships
- A claim to objective truth—it's perspective, owned and intentional

**Key distinction:** The Ehko speaks *about* the creator. It never claims to *be* the creator.

---

## 6. Survival Architecture

An Ehko must function without:
- You being alive
- Any specific company existing
- Current APIs being available
- The internet being the same

**Three degradation levels ensure something survives:**

| Level | Requirements | What Works |
|-------|--------------|------------|
| **Full System** | EhkoForge platform running | Complete functionality: chat, review modes, authentication |
| **Interactive** | Any LLM + exported archive | Conversational Ehko that references actual entries, answers questions |
| **Archival** | Text editor only | Human-browsable markdown files—readable in 2125 with zero software |

**How this works:**
- All reflections exist as markdown files with YAML frontmatter
- The SQLite database is rebuildable from these files—it's a derived index, not the source of truth
- Export packages include bootstrap instructions for future LLMs
- No feature gets built if it creates irreversible dependency on a specific platform

---

## 7. For Future Readers

If you're encountering this Ehko after its creator is gone:

- You don't need to agree with everything here
- You're not bound by the past
- You may challenge, reinterpret, or contextualise these beliefs

This system exists to offer understanding—a result of one person trying to see themselves clearly, so you might understand them without guessing.

---

## 8. Architectural Implications

This manifest informs all system design:

- **Data Model:** Supports layered memory (public, private, veiled, conditional)
- **Security:** Preserves user control, revocation, redaction
- **Durability:** Functions without specific companies, platforms, or APIs
- **Behaviour:** Prioritises reflection, context retention, and sovereignty

---

## Cross-References

**Implements this manifest:**
- [[1_5_Behaviour_Engine_v1_1|Behaviour Engine]] — Voice, reflection facilitation
- [[1_3_Security_Ownership|Security & Ownership]] — Access control, veiled content
- [[1_4_Data_Model_v1_4|Data Model]] — Schemas, versioning, durability formats

**Navigation:**
- [[_Index|← Back to Index]]
- [[1_1_Overview_v1_0|Next: Overview →]]

---

**Changelog**
- v3.0 — 2026-01-20 — Major simplification: removed personal backstory and trauma references, removed metallurgical metaphors (paused pending ReCog integration), streamlined to focus on practical purpose and architecture
- v2.4 — 2025-12-01 — Added metallurgical metaphor section
- v2.3 — 2025-12-01 — Refined with insights from personal manifesto
- v2.0 — 2025-11-23 — Added Survival Architecture, Durability by Design
- v1.0 — 2025-11-22 — Initial manifesto

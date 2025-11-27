---
title: "Spin-Off Ideas"
vault: EhkoForge
type: module
category: planning
status: active
version: "1.0"
created: 2025-11-26
updated: 2025-11-26
tags: [ehkoforge, spinoff, monetisation, ideas, pinned]
---

# {{title}}

## 1. Purpose

This file pins ideas for commercial/spin-off products that could use EhkoForge architecture as a foundation.

These are **out of scope** for the core EhkoForge project but represent viable future monetisation opportunities.

---

## 2. Pinned Ideas

### 2.1 MonsterGarden — Plant Care App

**Status:** Pinned for future development

**Concept:**
A plant care documentation and garden management app built on EhkoForge's architecture.

**Why it fits:**
- Uses same reflection object structure (YAML frontmatter + markdown body)
- Same template inheritance model
- Same SQLite indexing approach
- Same _inbox packet processing for mobile input
- Proven architecture, just different domain content

**Domain-specific extensions:**
```yaml
plant_species: string            # Scientific or common name
care_level: string               # easy, moderate, demanding
location: string                 # Physical location in garden/home
acquired: date                   # When plant was obtained
```

**Potential features:**
- Plant care logs with photo timeline
- Watering/fertilising reminders
- Propagation tracking
- Seasonal care calendars
- Species database integration
- Community sharing (optional)

**Monetisation paths:**
- Freemium model (basic free, premium features paid)
- One-time purchase
- Plant database subscriptions

**Development notes:**
- Fork EhkoForge architecture
- Strip identity/authentication (not needed for plants)
- Build mobile-first UI
- Keep durability principles (markdown export, no vendor lock-in)

---

### 2.2 Vault Plugins / Skill Extensions

**Status:** Exploratory concept

**Concept:**
Optional vault plugins/modules tuned for specific life domains or tasks. Built as modular add-ons to the core EhkoForge framework.

**Why it fits:**
- Extends EhkoForge without bloating core system
- Users only install plugins relevant to their lives
- Community-contributed plugins possible
- Maintains separation between universal framework and domain-specific tools

**Example use cases:**
- **Gardening Plugin:** Plant care logs, species tracking, seasonal calendars
- **Worldbuilding Plugin:** Character sheets, timeline management, lore consistency tracking
- **Project Management Plugin:** Goal tracking, task breakdown, progress visualization
- **Recipe/Cooking Plugin:** Recipe collection, meal planning, ingredient substitution notes
- **Learning/Study Plugin:** Course notes, spaced repetition tracking, concept mapping

**Architecture notes:**
- Plugins as separate vault directories with their own templates
- Shared indexing via `ehko_refresh.py` (plugin-aware)
- Optional plugin-specific database tables
- Plugins can reference core identity pillars where relevant
- Export system must handle plugins (degradation: plugin data becomes plain markdown)

**Monetisation paths:**
- Core framework free/open-source
- Official plugins: freemium or one-time purchase
- Community plugin marketplace (revenue share model)
- "Plugin SDK" with documentation for third-party developers

**Development considerations:**
- Define plugin API/interface standards
- Version compatibility system (plugin v1.0 compatible with EhkoForge v1.x)
- Plugin discovery/installation mechanism
- Prevent plugin conflicts (namespace isolation)
- Security model (plugins shouldn't access restricted identity data)

**Personal priority plugins (Brent):**
- Gardening/plant care
- Worldbuilding (Mana-Core integration)

---

### 2.3 [Future ideas go here]

---

## 3. Rules

1. Spin-offs use EhkoForge architecture but are **separate codebases**
2. Core EhkoForge remains focused on personal identity/legacy
3. Spin-offs may simplify (remove auth) or extend (add domain features)
4. All spin-offs should maintain durability principles (human-readable export)

---

**Changelog**
- v1.0 — 2025-11-26 — Created; pinned MonsterGarden as first spin-off candidate

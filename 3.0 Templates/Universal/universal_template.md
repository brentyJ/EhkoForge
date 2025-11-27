---
title: "Ehko Universal Template Framework v1.2"
vault: "EhkoForge"
category: "System Templates"
type: "framework"
status: active
version: "1.2"
created: 2025-11-11
updated: 2025-11-26
tags: [ehkoforge, templates, framework, architecture]
---

# EHKO UNIVERSAL TEMPLATE FRAMEWORK v1.2

## 1. Core Philosophy
Every entry — memory, reflection, or system module — is a **reflection object**.

All reflection objects share:

- Identity metadata (title, type, version, created/updated)  
- Context metadata (tags, source, related)  
- Temporal trail (changelog, provenance)  
- Body structure (Raw Input → Context → Observations → Insights → Actions → References)

This guarantees interoperability between Mirrorwell (content) and EhkoForge (system).

---

## 2. Universal Template Skeleton

```markdown
---
title: 
vault: 
type: 
category: 
status: active
version: 1.0
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: []
related: []
source: 
confidence: 0.95
revealed: true
---

# {{title}}

## 0. Raw Input (Preserved)
Original unedited text captured exactly as written or dictated.

---

## 1. Context
Situational background, triggers, people involved, purpose.

---

## 2. Observations
Factual, sensory, or situational details without interpretation.

---

## 3. Reflection / Interpretation
Meaning, emotional resonance, patterns, thematic connections.

---

## 4. Actions / Updates
Follow-up tasks, next steps, maintenance, future revisit points.

---

## 5. Cross-References
Links to related entries across Mirrorwell or EhkoForge modules.

---

**Changelog**
- v1.0 — YYYY-MM-DD — Entry created
```

---

## 3. Vault Contexts

**Mirrorwell** — Personal reflections, identity work, emotional processing
- Primary type: `reflection`
- Extension fields: `emotional_tags`, `core_memory`, `identity_pillar`, `shared_with`

**EhkoForge** — System architecture, specifications, templates
- Primary type: `module`
- Extension fields: none (uses base schema)

---

**Changelog**
- v1.2 — 2025-11-26 — Scope reduction: removed MonsterGarden and ManaCore from interoperability claims; simplified to two-vault model (Mirrorwell + EhkoForge); added Section 3 vault contexts
- v1.1 — 2025-11-11 — Initial framework specification

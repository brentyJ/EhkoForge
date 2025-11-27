# Welcome to Your Mirrorwell

**Mirrorwell** is your personal content vault for the EhkoForge system. This is where your reflections, memories, and identity work live.

---

## What This Vault Is For

- **Personal reflections** - Journal entries, therapy notes, voice transcriptions
- **Core memories** - Significant life experiences that define you
- **Identity pillars** - The frameworks that describe who you are
- **Interpretation layers** - Analysis, themes, and patterns across your life
- **Archive corpus** - Documents, media, and external materials
- **System indexes** - Tags, people, temporal organization

---

## Quick Start

### 1. Use the Reflection Template

Your main tool is the reflection template at:
```
Templates/reflection_template.md
```

Copy this template each time you want to create a new reflection.

### 2. Save Reflections in the Right Place

- **Daily journals, therapy notes:** `2_Reflection Library/2.1 Journals/`
- **Voice transcriptions:** `2_Reflection Library/2.2 Transcripts/`
- **Future messages:** `2_Reflection Library/2.3 Messages/`

### 3. Let the System Process

After creating reflections:
1. Open EhkoForge vault
2. Run `5.0 Scripts/ehko_refresh.py`
3. Your reflections will be indexed into the SQLite database

---

## Folder Structure Explained

### 1. Core Identity
**Where you define yourself**

- **1.1 Pillars** - The fundamental aspects of your identity (values, traits, worldview)
- **1.2 Values & Beliefs** - What you stand for, what you believe
- **1.3 Narrative Arcs** - The big stories that define your life trajectory
- **1.4 Core Memory Index** - Your most significant memories, flagged for importance

### 2. Reflection Library
**Your raw input and processing**

- **2.1 Journals** - Structured reflections using the template
- **2.2 Transcripts** - Voice notes converted to text (auto-processed by ehko_refresh.py)
- **2.3 Messages** - Prepared communications for specific people/situations
- **2.4 Prompts & Responses** - AI conversation logs worth preserving

### 3. Interpretation Layer
**Making sense of your reflections**

- **3.1 Analyses** - Deep dives into specific topics or patterns
- **3.2 Themes** - Recurring patterns across your life
- **3.3 Continuities** - How things connect and evolve over time
- **3.4 Veiled Content** - Reflections that reveal under specific conditions

### 4. Archive Corpus
**External materials and backups**

- **4.1 Imported Media** - Photos, videos, audio files
- **4.2 Documents** - PDFs, text files, important papers
- **4.3 External Links** - Web resources, articles, references
- **4.4 Version History** - Snapshots of your vault over time

### 5. System Indexes
**Organization and cross-referencing**

- **5.1 Tag Lexicon** - Definitions of your tags
- **5.2 People & Entities** - Index of people mentioned across reflections
- **5.3 Temporal Index** - Time-based organization and anniversaries
- **5.4 Cross-World Links** - Connections to fiction vaults (if using)

---

## Important Principles

### 1. Never Edit Raw Input
When you create a reflection, the **Section 0: Raw Input** must never be modified. This is your authentic, unedited thought. All processing happens in later sections.

### 2. Use YAML Frontmatter
Every reflection needs structured metadata at the top. The template handles this - just fill in the values.

### 3. Revelation Control
The `revealed` field controls whether content shows immediately or waits for specific conditions. Use `revealed: false` for veiled content.

### 4. Cross-Reference Everything
Use `[[wiki-style links]]` to connect reflections, people, themes, and memories. This builds the web of your identity.

---

## File Naming Conventions

Use this pattern for journal entries:
```
YYYY-MM-DD_slug-description.md
```

Examples:
- `2025-11-27_father-childhood-memories.md`
- `2025-11-28_therapy-session-boundaries.md`
- `2025-12-01_career-transition-anxiety.md`

---

## Privacy & Security

**This vault is private.** It should never be uploaded to GitHub or shared publicly. The EhkoForge system vault (the framework) is public, but Mirrorwell is yours alone.

When you run `ehko_refresh.py`, data is indexed into a local SQLite database, but the original markdown files remain your canonical source of truth.

---

## Getting Help

1. **EhkoForge documentation:** See the main vault's `1.0 System Architecture/` folder
2. **Template guidance:** Read `Templates/reflection_template.md` comments
3. **PROJECT_STATUS.md:** Check current features and roadmap in EhkoForge vault

---

## Your First Reflection

Ready to start? Here's what to do:

1. Copy `Templates/reflection_template.md`
2. Save it as `2_Reflection Library/2.1 Journals/2025-MM-DD_my-first-reflection.md`
3. Fill in Section 0 (Raw Input) with whatever's on your mind
4. Work through the other sections (Context, Observations, Reflection, Actions)
5. Save the file
6. Run `ehko_refresh.py` from the EhkoForge vault

That's it. You've started building your Ehko.

---

**Build the echo. Leave the truth.**

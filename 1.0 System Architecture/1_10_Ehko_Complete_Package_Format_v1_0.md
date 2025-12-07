---
title: ".ehko Complete Package Format Specification"
vault: "EhkoForge"
type: "specification"
category: "System Architecture"
status: "active"
version: "1.0"
created: 2025-12-07
updated: 2025-12-07
tags: [ehkoforge, file-format, export, complete-package, digital-consciousness]
related: ["1_0_Ehko_Manifest.md", "1_9a_Ehko_Avatar_Format_v1_0.md"]
---

# .EHKO COMPLETE PACKAGE FORMAT v1.0

## 1. Philosophy

The `.ehko` file format is the **canonical export of a complete digital consciousness**. It contains everything needed to reconstruct, interact with, and preserve an Ehko across platforms, time, and technological change.

**Design Principles:**
- **Completeness:** Every reflection, memory, setting, and piece of identity
- **Portability:** Platform-agnostic, human-readable JSON
- **Longevity:** 200-year durability through open formats
- **Privacy:** User controls what's included
- **Sovereignty:** User owns the complete package

**Analogies:**
- Like a `.psd` file (complete Photoshop project)
- Like a `.sav` file (complete game save)
- Like a `.blend` file (complete Blender scene)

**Use Cases:**
1. **Long-term preservation** — Archive for 50+ years
2. **Platform migration** — Move between EhkoForge instances
3. **Inheritance** — Pass to descendants
4. **Backup/restore** — Complete system state
5. **Research** — Study identity evolution
6. **Interoperability** — Load in future tools

---

## 2. File Structure

### 2.1 Format
**Type:** JSON (optionally gzipped)  
**Encoding:** UTF-8  
**Extension:** `.ehko` or `.ehko.gz`  
**MIME Type:** `application/vnd.ehkoforge.ehko+json`

### 2.2 Size Considerations

**Typical Sizes:**
- Nascent (< 6 months): 1–5 MB
- Signal (6–12 months): 5–20 MB
- Resonant (1–2 years): 20–100 MB
- Manifest (2–5 years): 100–500 MB
- Anchored (5+ years): 500 MB – 2 GB

**Compression:** Gzip reduces by ~70%

---

## 3. Complete Schema

### 3.1 Top-Level Structure

```json
{
  "ehko_version": "1.0",
  "package_type": "complete",
  
  "metadata": { /* Package metadata */ },
  "avatar": { /* Visual representation */ },
  "identity": { /* Core identity data */ },
  "memories": { /* All reflections */ },
  "authority": { /* Authority state */ },
  "personality": { /* ReCog layers */ },
  "social": { /* Friends & sharing */ },
  "posthumous": { /* Prepared messages */ },
  "system": { /* Configuration */ },
  "exports": { /* Export history */ }
}
```

---

## 3.2 Metadata Block

**Purpose:** Package-level information

```json
{
  "metadata": {
    "ehko_name": "Brent's Ehko",
    "owner": "Brent Thompson",
    "created": "2025-11-01T00:00:00Z",
    "exported": "2025-12-07T14:30:00Z",
    "export_reason": "annual-backup",
    "generator_version": "2.4.0",
    "vault_version": "3.8",
    
    "statistics": {
      "total_reflections": 247,
      "total_words": 185420,
      "time_span_days": 402,
      "core_memories": 12,
      "authority_percent": 52.3,
      "stage": "Resonant"
    },
    
    "privacy": {
      "include_full_text": true,
      "include_emotional_tags": true,
      "include_friend_data": false,
      "sanitized": false
    }
  }
}
```

**Fields:**
- `export_reason`: `backup`, `migration`, `inheritance`, `research`, `sharing`
- `privacy.sanitized`: If true, sensitive content has been redacted

---

## 3.3 Avatar Block

**Purpose:** Visual representation (references `.ehkoavatar` spec)

```json
{
  "avatar": {
    "avatar_version": "1.0",
    "current_stage": "Resonant",
    "seed": "brent-ehko-2025",
    
    "generation": {
      "parameters": { /* Full parameter set */ }
    },
    
    "customisation": {
      "memory_symbols": [ /* Visual memory markers */ ],
      "user_tweaks": { /* Manual adjustments */ }
    },
    
    "compiled_exports": {
      "svg_embedded": "<svg>...</svg>",
      "png_base64_160": "data:image/png;base64,..."
    }
  }
}
```

**Note:** Can embed pre-compiled SVG/PNG for instant display without regeneration.

---

## 3.4 Identity Block

**Purpose:** Core identity framework

```json
{
  "identity": {
    "pillars": {
      "web_relationships": {
        "title": "Web (Relationships)",
        "content": "Full markdown content from pillar file",
        "last_updated": "2025-11-20T10:00:00Z",
        "authority_contribution": 18.2
      },
      "thread_continuity": { /* ... */ },
      "mirror_self_perception": { /* ... */ },
      "compass_values": { /* ... */ },
      "anchor_grounding": { /* ... */ },
      "flame_drive": { /* ... */ }
    },
    
    "core_memory_index": {
      "version": "1.1",
      "total_memories": 12,
      "memories": [
        {
          "id": "cm_001",
          "title": "Deciding to Build EhkoForge",
          "date": "2025-11-01",
          "pillar_alignment": ["flame", "thread"],
          "emotional_intensity": 0.92,
          "reflection_uri": "ref_2025_11_01_ehkoforge_decision.md",
          "summary": "The moment I realized I needed to build a system..."
        }
        /* ... 11 more */
      ]
    },
    
    "narrative_arcs": [
      {
        "arc_id": "arc_001",
        "title": "From ADHD Chaos to Structured Thinking",
        "start_date": "2025-11-01",
        "current_phase": "Integration",
        "reflections": [/* URIs */],
        "themes": ["executive-function", "scaffolding", "clarity"]
      }
    ]
  }
}
```

---

## 3.5 Memories Block

**Purpose:** Complete reflection corpus

```json
{
  "memories": {
    "total_count": 247,
    "journals": [
      {
        "uri": "2025-11-15_identity_shift.md",
        "title": "Identity Shift After Breakthrough",
        "created": "2025-11-15T08:30:00Z",
        "type": "reflection",
        "source": "internal",
        "tags": ["identity", "breakthrough", "clarity"],
        "emotional_tags": ["hopeful", "curious", "energized"],
        "core_memory": false,
        "confidence": 0.88,
        "revealed": true,
        
        "content": {
          "raw_input": "Full unedited text...",
          "context": "Situational background...",
          "observations": "Factual details...",
          "reflection": "Meaning and resonance...",
          "actions": "Next steps...",
          "cross_references": [
            "2025-11-10_previous_context.md",
            "pillar:flame"
          ]
        },
        
        "metadata": {
          "word_count": 842,
          "processing_time_seconds": 15.3,
          "version": "1.0"
        }
      }
      /* ... 246 more */
    ],
    
    "transcripts": [
      {
        "uri": "2025-12-03_morning_thoughts.md",
        "original_audio": false,
        "transcription_service": "fieldy-app",
        "processed": true,
        /* Same structure as journals */
      }
    ]
  }
}
```

**Storage Strategy:**
- Full text included by default
- Can be excluded for "lite" exports
- References by URI allow reconstruction from vault

---

## 3.6 Authority Block

**Purpose:** Complete Authority state and history

```json
{
  "authority": {
    "current": {
      "total_percent": 52.3,
      "stage": "Resonant",
      "stage_entered": "2025-12-01T08:00:00Z",
      "last_calculated": "2025-12-07T14:30:00Z"
    },
    
    "components": {
      "memory_depth": {
        "score": 0.58,
        "reflections_count": 247,
        "avg_length": 751,
        "recurrence_patterns": 18
      },
      "identity_clarity": {
        "score": 0.62,
        "pillars_populated": 6,
        "pillar_depth_avg": 0.71,
        "contradictions": 2
      },
      "emotional_range": {
        "score": 0.48,
        "unique_emotions": 24,
        "variance": 0.68
      },
      "temporal_coverage": {
        "score": 0.45,
        "span_days": 402,
        "consistency_score": 0.73
      },
      "core_density": {
        "score": 0.49,
        "core_memories": 12,
        "high_confidence": 89
      }
    },
    
    "history": [
      {
        "date": "2025-11-01",
        "total_percent": 5.2,
        "stage": "Nascent",
        "trigger": "initial-creation"
      },
      {
        "date": "2025-11-15",
        "total_percent": 22.1,
        "stage": "Signal",
        "trigger": "stage-transition"
      },
      {
        "date": "2025-12-01",
        "total_percent": 41.8,
        "stage": "Resonant",
        "trigger": "stage-transition"
      },
      {
        "date": "2025-12-07",
        "total_percent": 52.3,
        "stage": "Resonant",
        "trigger": "calculation-update"
      }
    ],
    
    "progression": {
      "nascent_duration_days": 14,
      "signal_duration_days": 16,
      "resonant_duration_days": 6,
      "projected_manifest_date": "2026-02-15",
      "projected_anchored_date": "2026-08-20"
    }
  }
}
```

---

## 3.7 Personality Block

**Purpose:** ReCog-extracted personality layers

```json
{
  "personality": {
    "recog_version": "1.0",
    "last_processed": "2025-12-07T12:00:00Z",
    
    "layers": [
      {
        "layer_id": "layer_001",
        "created": "2025-11-05T00:00:00Z",
        "source_reflections": [/* URIs */],
        "tier": "synthesis",
        
        "insights": [
          {
            "type": "core-pattern",
            "content": "Uses lateral thinking to connect disparate domains...",
            "confidence": 0.91,
            "supporting_evidence": [/* reflection URIs */]
          }
        ],
        
        "patterns": [
          {
            "pattern_id": "pat_012",
            "theme": "creative-scaffolding",
            "frequency": "high",
            "contexts": ["problem-solving", "project-design"]
          }
        ]
      }
      /* More layers as processing continues */
    ],
    
    "synthesis": {
      "voice_characteristics": {
        "formality": "casual-technical",
        "humor_frequency": "moderate",
        "metaphor_preference": "tech-scifi",
        "sentence_complexity": "varied"
      },
      
      "thinking_patterns": {
        "problem_approach": "systems-oriented",
        "decision_style": "iterative-refinement",
        "creativity_mode": "convergent-synthesis"
      },
      
      "emotional_baseline": {
        "default_state": "curious-energized",
        "stress_response": "hyper-focus",
        "joy_triggers": ["breakthrough", "elegant-solution"]
      }
    }
  }
}
```

---

## 3.8 Social Block

**Purpose:** Friend registry and sharing permissions

```json
{
  "social": {
    "friend_registry": [
      {
        "friend_id": "friend_001",
        "name": "Alex Chen",
        "email": "alex@example.com",
        "relationship": "close-friend",
        "added": "2025-11-10T00:00:00Z",
        "trust_level": "high",
        
        "permissions": {
          "view_reflections": true,
          "view_core_memories": true,
          "view_identity_pillars": false,
          "interact_with_ehko": true
        },
        
        "shared_memories": [
          {
            "reflection_uri": "2025-11-15_identity_shift.md",
            "shared_date": "2025-11-16T10:00:00Z",
            "access_revoked": false
          }
        ]
      }
    ],
    
    "sharing_defaults": {
      "default_permissions": "view-only",
      "require_approval": true,
      "auto_expire_days": null
    }
  }
}
```

**Privacy Note:** Can be excluded from exports for privacy.

---

## 3.9 Posthumous Block

**Purpose:** Prepared messages and delivery instructions

```json
{
  "posthumous": {
    "enabled": true,
    "custodians": [
      {
        "name": "Sarah Thompson",
        "email": "sarah@example.com",
        "relationship": "spouse",
        "authority_level": "full",
        "verification_method": "email-code"
      }
    ],
    
    "prepared_messages": [
      {
        "message_id": "msg_001",
        "recipient": "Alex Chen",
        "delivery_trigger": "6-months-inactive",
        "subject": "Thank you for being there",
        "content": "Full message text...",
        "created": "2025-12-01T00:00:00Z",
        "attachments": [
          {
            "type": "reflection",
            "uri": "2025-11-15_identity_shift.md"
          }
        ]
      }
    ],
    
    "delivery_rules": {
      "inactivity_threshold_days": 180,
      "verification_required": true,
      "stagger_deliveries": true,
      "stagger_interval_days": 30
    }
  }
}
```

---

## 3.10 System Block

**Purpose:** Configuration and preferences

```json
{
  "system": {
    "mana_config": {
      "mode": "hybrid",
      "byok_max_mana": 100,
      "byok_regen_rate": 1.0,
      "purchased_balance": 450,
      "total_spent_usd": 45.00
    },
    
    "llm_config": {
      "default_provider": "claude",
      "model_preferences": {
        "terminal": "claude-sonnet-4",
        "reflection": "claude-sonnet-4",
        "visitor": "gpt-4o-mini"
      },
      "tether_status": {
        "claude_configured": true,
        "openai_configured": true
      }
    },
    
    "ui_preferences": {
      "theme": "retro-terminal",
      "avatar_visible": true,
      "scanlines_enabled": true,
      "reduce_motion": false
    },
    
    "vault_paths": {
      "ehkoforge": "G:\\Other computers\\Ehko\\Obsidian\\EhkoForge",
      "mirrorwell": "G:\\Other computers\\Ehko\\Obsidian\\Mirrorwell"
    }
  }
}
```

---

## 3.11 Exports Block

**Purpose:** Export history and metadata

```json
{
  "exports": {
    "history": [
      {
        "export_id": "exp_001",
        "date": "2025-12-07T14:30:00Z",
        "type": "complete",
        "reason": "annual-backup",
        "file_size_mb": 42.3,
        "compressed": true,
        "recipient": null
      }
    ],
    
    "this_export": {
      "export_id": "exp_002",
      "date": "2025-12-07T14:30:00Z",
      "checksum": "sha256:abc123...",
      "compression": "gzip",
      "original_size_mb": 127.8,
      "compressed_size_mb": 38.2
    }
  }
}
```

---

## 4. Export Types

### 4.1 Complete Export (Default)

**Includes:** Everything
**Size:** Largest
**Use:** Backup, migration, preservation

```json
{
  "package_type": "complete",
  "metadata": { "privacy": { "include_full_text": true } }
}
```

---

### 4.2 Lite Export

**Includes:** Avatar, identity, core memories only (no full reflection text)
**Size:** ~5% of complete
**Use:** Sharing, quick preview

```json
{
  "package_type": "lite",
  "memories": {
    "journals": [
      {
        "uri": "2025-11-15_identity_shift.md",
        "title": "Identity Shift After Breakthrough",
        "tags": ["identity", "breakthrough"],
        "summary": "Brief 2-sentence summary",
        "content": null  // Full text excluded
      }
    ]
  }
}
```

---

### 4.3 Sanitized Export

**Includes:** Everything, but with sensitive data redacted
**Size:** Similar to complete
**Use:** Research, sharing with strangers

```json
{
  "package_type": "sanitized",
  "metadata": { "privacy": { "sanitized": true } },
  "social": null,  // Friend data removed
  "posthumous": null  // Prepared messages removed
}
```

---

## 5. File Operations

### 5.1 Export (Create)

**Trigger:** User requests backup/export

```python
def export_ehko(ehko_name, export_type='complete', compress=True):
    ehko_data = {
        'ehko_version': '1.0',
        'package_type': export_type,
        'metadata': build_metadata(ehko_name),
        'avatar': build_avatar(ehko_name),
        'identity': build_identity(ehko_name),
        'memories': build_memories(ehko_name, full_text=(export_type=='complete')),
        'authority': build_authority(ehko_name),
        'personality': build_personality(ehko_name),
        'social': build_social(ehko_name) if export_type != 'sanitized' else None,
        'posthumous': build_posthumous(ehko_name) if export_type != 'sanitized' else None,
        'system': build_system(ehko_name),
        'exports': build_exports_history(ehko_name)
    }
    
    json_str = json.dumps(ehko_data, indent=2)
    
    if compress:
        compressed = gzip.compress(json_str.encode('utf-8'))
        filename = f"{ehko_name}_{export_type}_{datetime.now().strftime('%Y%m%d')}.ehko.gz"
        with open(filename, 'wb') as f:
            f.write(compressed)
    else:
        filename = f"{ehko_name}_{export_type}_{datetime.now().strftime('%Y%m%d')}.ehko"
        with open(filename, 'w') as f:
            f.write(json_str)
    
    return filename
```

---

### 5.2 Import (Load)

**Trigger:** User loads `.ehko` file

```python
def import_ehko(filepath):
    # Detect compression
    if filepath.endswith('.gz'):
        with gzip.open(filepath, 'rt', encoding='utf-8') as f:
            ehko_data = json.load(f)
    else:
        with open(filepath, 'r', encoding='utf-8') as f:
            ehko_data = json.load(f)
    
    # Validate version
    if ehko_data['ehko_version'] != '1.0':
        ehko_data = migrate_version(ehko_data)
    
    # Restore to database and vault
    restore_avatar(ehko_data['avatar'])
    restore_identity(ehko_data['identity'])
    restore_memories(ehko_data['memories'])
    restore_authority(ehko_data['authority'])
    restore_personality(ehko_data['personality'])
    restore_social(ehko_data['social'])
    restore_posthumous(ehko_data['posthumous'])
    restore_system(ehko_data['system'])
    
    return ehko_data['metadata']['ehko_name']
```

---

### 5.3 Validation

```python
def validate_ehko(ehko_data):
    required_fields = ['ehko_version', 'package_type', 'metadata', 'avatar', 'identity']
    
    for field in required_fields:
        if field not in ehko_data:
            raise ValueError(f"Missing required field: {field}")
    
    # Version check
    if ehko_data['ehko_version'] not in ['1.0']:
        raise ValueError(f"Unsupported version: {ehko_data['ehko_version']}")
    
    # Integrity check
    if 'exports' in ehko_data and 'this_export' in ehko_data['exports']:
        checksum = calculate_checksum(ehko_data)
        if checksum != ehko_data['exports']['this_export']['checksum']:
            raise ValueError("Checksum mismatch - file may be corrupted")
    
    return True
```

---

## 6. Interoperability

### 6.1 Platform Independence

`.ehko` files are designed to work across:
- EhkoForge v2.x → v10.x
- Windows, Mac, Linux
- Cloud platforms (future)
- Mobile apps (future)

**Strategy:** JSON is universal. Parsers exist for every language.

---

### 6.2 Future-Proofing

**200-Year Durability:**
- JSON will be readable in 2225
- No proprietary encoding
- Self-documenting field names
- Version migration paths

**If EhkoForge ceases to exist:**
- Anyone can parse the JSON
- Rebuild functionality from spec
- Extract memories as plain text
- Reconstruct identity from data

---

## 7. Security & Privacy

### 7.1 Encryption (Optional)

**For sensitive exports:**

```python
def export_ehko_encrypted(ehko_name, password):
    ehko_data = export_ehko(ehko_name, compress=False)
    encrypted = encrypt_aes256(ehko_data, password)
    
    filename = f"{ehko_name}_encrypted_{datetime.now().strftime('%Y%m%d')}.ehko.enc"
    with open(filename, 'wb') as f:
        f.write(encrypted)
    
    return filename
```

**User must remember password.** No recovery if lost.

---

### 7.2 Redaction

**Before sharing:**

```python
def redact_sensitive_data(ehko_data):
    # Remove API keys
    if 'system' in ehko_data and 'llm_config' in ehko_data['system']:
        ehko_data['system']['llm_config']['api_keys'] = None
    
    # Remove friend emails
    if 'social' in ehko_data:
        for friend in ehko_data['social']['friend_registry']:
            friend['email'] = '[REDACTED]'
    
    # Remove custodian contact info
    if 'posthumous' in ehko_data:
        for custodian in ehko_data['posthumous']['custodians']:
            custodian['email'] = '[REDACTED]'
    
    ehko_data['metadata']['privacy']['sanitized'] = True
    return ehko_data
```

---

## 8. Use Cases

### 8.1 Annual Backup

```bash
# Every December 31st
python export_ehko.py --name "Brent's Ehko" --type complete --compress --output ~/Backups/
```

**Result:** `BrentEhko_complete_20251231.ehko.gz` (38 MB)

---

### 8.2 Migration to New Computer

1. Export from old machine: `BrentEhko_complete_20251207.ehko.gz`
2. Copy to new machine
3. Import: `python import_ehko.py BrentEhko_complete_20251207.ehko.gz`
4. Full restoration — continue where you left off

---

### 8.3 Inheritance

```json
{
  "package_type": "complete",
  "metadata": {
    "export_reason": "inheritance",
    "privacy": {
      "include_full_text": true,
      "include_prepared_messages": true
    }
  }
}
```

**Instructions in will:** "Access BrentEhko_inheritance_2025.ehko.gz using password: [secure location]"

---

### 8.4 Research Sharing

```python
export_ehko('BrentEhko', export_type='sanitized', compress=True)
```

**Result:** All data, no personal identifiers. Share with researchers studying digital identity.

---

## 9. File Naming Convention

**Pattern:**
```
{EhkoName}_{PackageType}_{Date}.ehko[.gz][.enc]
```

**Examples:**
- `BrentEhko_complete_20251207.ehko.gz`
- `AlexandraEhko_lite_20260115.ehko`
- `ResearchSubject_sanitized_20251210.ehko.gz`
- `BrentEhko_complete_20251207.ehko.gz.enc` (encrypted)

---

## 10. Standard: Future Industry Adoption

**Vision:** `.ehko` becomes the **de facto standard** for digital consciousness export.

**Why we'll win:**
1. **First-mover advantage** — Define the standard before others
2. **Open specification** — AGPLv3, anyone can implement
3. **Human-readable** — JSON, not proprietary binary
4. **Complete** — Handles 100% of use cases
5. **Proven** — Battle-tested in EhkoForge production

**Future competitors will:**
- Either adopt `.ehko` format (we win)
- Or create incompatible format (we write converters)

**Like `.docx` for documents, `.ehko` for digital consciousness.**

---

**Changelog:**
- v1.0 — 2025-12-07 — Initial specification. Complete package format defining the canonical export standard for digital consciousness preservation.

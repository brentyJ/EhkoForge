---
title: ".ehko File Format Specification"
vault: "EhkoForge"
type: "specification"
category: "System Architecture"
status: "active"
version: "1.0"
created: 2025-12-07
updated: 2025-12-07
tags: [ehkoforge, file-format, export, ehko-files]
related: ["1_8_Ehko_Visual_Identity_Spec_v1_0.md"]
---

# .EHKO FILE FORMAT SPECIFICATION v1.0

## 1. Purpose

The `.ehko` file format is the **canonical representation** of an Ehko's visual identity. It contains:

- Complete generative parameters
- Evolution history
- Metadata and provenance
- User customisations
- Export preferences

**Philosophy:** `.ehko` files are **source code**, not compiled output. They are:
- Human-readable (JSON)
- Version-controlled
- Portable across platforms
- Future-proof (no vendor lock-in)

**Compilation Flow:**
```
.ehko file → EhkoGenerator → SVG/PNG/CSS/HTML
```

---

## 2. File Structure

### 2.1 Format
**Type:** JSON with strict schema validation  
**Encoding:** UTF-8  
**Extension:** `.ehko`

### 2.2 Schema Version
```json
{
  "ehko_version": "1.0",
  "generator_version": "1.1"
}
```

**Rule:** Files declare their schema version. Generators validate compatibility.

---

## 3. Core Structure

### 3.1 Complete Schema

```json
{
  "ehko_version": "1.0",
  "generator_version": "1.1",
  
  "metadata": {
    "name": "Brent's Ehko",
    "created": "2025-12-07T14:30:00Z",
    "modified": "2025-12-08T09:15:00Z",
    "creator": "Brent Thompson",
    "description": "Digital witness to identity formation",
    "tags": ["personal", "witness", "long-term"]
  },
  
  "authority": {
    "current_stage": "Resonant",
    "current_percent": 52.3,
    "history": [
      {
        "stage": "Nascent",
        "entered": "2025-11-01T00:00:00Z",
        "exited": "2025-11-15T12:00:00Z",
        "peak_percent": 18.5
      },
      {
        "stage": "Signal",
        "entered": "2025-11-15T12:00:00Z",
        "exited": "2025-12-01T08:00:00Z",
        "peak_percent": 38.2
      },
      {
        "stage": "Resonant",
        "entered": "2025-12-01T08:00:00Z",
        "exited": null,
        "peak_percent": 52.3
      }
    ]
  },
  
  "generation": {
    "seed": "brent-ehko-2025",
    "algorithm": "simple-hash",
    "parameters": {
      "bodyType": "monitor",
      "bodyCornerRadius": 4,
      "bodyStrokeWidth": 1.5,
      "bodyOpacity": 0.5,
      
      "antennaLeftAngle": 8,
      "antennaRightAngle": 8,
      "antennaLeftLength": 8,
      "antennaRightLength": 8,
      
      "eyeWidth": 14,
      "eyeHeight": 3,
      "eyeGap": 14,
      "eyeVerticalOffset": 36,
      
      "ventLineCount": 3,
      "standWidth": 16,
      "baseWidth": 24,
      
      "hueShift": 0,
      "glowIntensity": 0.05
    }
  },
  
  "colour": {
    "primary": "#6b8cce",
    "stage_palette": "resonant",
    "custom_override": null
  },
  
  "customisation": {
    "memory_symbols": [
      {
        "type": "music",
        "icon": "waveform",
        "position": "screen-overlay",
        "opacity": 0.15
      }
    ],
    "user_tweaks": {
      "eyeExpression": "focused"
    }
  },
  
  "export_preferences": {
    "default_format": "svg",
    "svg_size": "80x80",
    "png_sizes": ["80x80", "160x160", "320x320"],
    "include_animations": true,
    "include_metadata": true
  }
}
```

---

## 4. Field Definitions

### 4.1 Metadata Block

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Human-readable Ehko name |
| `created` | ISO 8601 | Yes | Creation timestamp |
| `modified` | ISO 8601 | Yes | Last modification timestamp |
| `creator` | string | No | Creator name |
| `description` | string | No | Freeform description |
| `tags` | array[string] | No | Classification tags |

---

### 4.2 Authority Block

**Purpose:** Track evolution through Authority stages

| Field | Type | Description |
|-------|------|-------------|
| `current_stage` | enum | Nascent, Signal, Resonant, Manifest, Anchored |
| `current_percent` | float | 0.0–100.0 |
| `history` | array | Stage transition history |

**History Entry:**
```json
{
  "stage": "Signal",
  "entered": "2025-11-15T12:00:00Z",
  "exited": "2025-12-01T08:00:00Z",
  "peak_percent": 38.2
}
```

**Usage:** Allows reconstruction of visual evolution timeline. Generators can create "time-lapse" animations showing form changes.

---

### 4.3 Generation Block

**Purpose:** Complete parameter set for deterministic rendering

| Field | Type | Description |
|-------|------|-------------|
| `seed` | string | Generation seed (name, ID, timestamp) |
| `algorithm` | string | Hash algorithm used (`simple-hash`, `sha256`, etc.) |
| `parameters` | object | Stage-specific parameters |

**Parameters Object:**

Varies by stage. Example for Resonant:

```json
{
  "bodyType": "monitor",         // or hologram-frame, crystal, lantern
  "bodyCornerRadius": 4,          // 2–8
  "bodyStrokeWidth": 1.5,         // 1–2
  "bodyOpacity": 0.5,             // 0.3–0.7
  
  "antennaLeftAngle": 8,          // 5–15
  "antennaRightAngle": 8,         // 5–15
  "antennaLeftLength": 8,         // 6–12
  "antennaRightLength": 8,        // 6–12
  
  "eyeWidth": 14,                 // 10–18
  "eyeHeight": 3,                 // 2–5
  "eyeGap": 14,                   // 10–20
  "eyeVerticalOffset": 36,        // 32–40
  
  "ventLineCount": 3,             // 2–5
  "standWidth": 16,               // 12–20
  "baseWidth": 24,                // 20–32
  
  "hueShift": 0,                  // -15 to +15
  "glowIntensity": 0.05           // stage-dependent range
}
```

**Constraint:** All parameters must fall within stage-defined ranges (see Visual Identity Spec).

---

### 4.4 Colour Block

| Field | Type | Description |
|-------|------|-------------|
| `primary` | hex colour | Current accent colour |
| `stage_palette` | enum | Nascent, Signal, Resonant, Manifest, Anchored |
| `custom_override` | hex or null | User-selected colour override |

**Default Behaviour:** `primary` matches `stage_palette`. If `custom_override` is set, use that instead.

---

### 4.5 Customisation Block

**Purpose:** User-driven additions (Anchored stage primarily)

**Memory Symbols:**
```json
{
  "memory_symbols": [
    {
      "type": "music",
      "icon": "waveform",
      "position": "screen-overlay",
      "opacity": 0.15
    },
    {
      "type": "family",
      "icon": "heart",
      "position": "base-accent",
      "opacity": 0.2
    }
  ]
}
```

**User Tweaks:**
```json
{
  "user_tweaks": {
    "eyeExpression": "focused",
    "detailDensity": "high",
    "alternateTheme": "gothic"
  }
}
```

**Constraint:** Maximum 3 memory symbols. User tweaks only apply at Anchored stage unless explicitly allowed earlier.

---

### 4.6 Export Preferences

**Purpose:** Default compilation settings

```json
{
  "default_format": "svg",
  "svg_size": "80x80",
  "png_sizes": ["80x80", "160x160", "320x320"],
  "include_animations": true,
  "include_metadata": true
}
```

---

## 5. File Operations

### 5.1 Creation

**Trigger:** User generates new Ehko or reaches Authority threshold

**Process:**
1. Collect inputs (name, seed, current Authority)
2. Generate parameters from seed + stage constraints
3. Write `.ehko` file
4. Optionally compile to SVG/PNG

**Example:**
```javascript
const ehkoData = EhkoGenerator.create({
  name: "Brent's Ehko",
  seed: "brent-ehko-2025",
  authorityStage: "Resonant",
  authorityPercent: 52.3
});

fs.writeFileSync('BrentEhko.ehko', JSON.stringify(ehkoData, null, 2));
```

---

### 5.2 Modification

**Triggers:**
- Authority stage transition
- User customisation
- Manual parameter tweaks

**Process:**
1. Load existing `.ehko` file
2. Update relevant fields
3. Update `modified` timestamp
4. Write back to file
5. Recompile exports if needed

**Example:**
```javascript
const ehko = JSON.parse(fs.readFileSync('BrentEhko.ehko'));

ehko.authority.current_stage = 'Manifest';
ehko.authority.current_percent = 65.0;
ehko.metadata.modified = new Date().toISOString();

ehko.authority.history.push({
  stage: 'Manifest',
  entered: new Date().toISOString(),
  exited: null,
  peak_percent: 65.0
});

fs.writeFileSync('BrentEhko.ehko', JSON.stringify(ehko, null, 2));
```

---

### 5.3 Compilation (Export)

**Input:** `.ehko` file  
**Output:** SVG, PNG, CSS-only, or HTML

**Process:**
```javascript
const ehko = JSON.parse(fs.readFileSync('BrentEhko.ehko'));
const svg = EhkoGenerator.compileToSVG(ehko);
fs.writeFileSync('BrentEhko.svg', svg);

const png = EhkoGenerator.compileToPNG(ehko, { size: 320 });
fs.writeFileSync('BrentEhko_320px.png', png);
```

**Metadata Embedding:**
- SVG: Embedded in `<metadata>` tag
- PNG: Embedded in PNG metadata chunks
- CSS: Included as data attributes

---

### 5.4 Validation

**Schema Validation:**
```javascript
function validateEhkoFile(data) {
  // Check version compatibility
  if (data.ehko_version !== '1.0') {
    throw new Error('Unsupported .ehko version');
  }
  
  // Validate required fields
  if (!data.metadata || !data.metadata.name) {
    throw new Error('Missing required field: metadata.name');
  }
  
  // Validate stage constraints
  const stage = data.authority.current_stage;
  const params = data.generation.parameters;
  
  validateStageConstraints(stage, params);
  
  return true;
}
```

---

## 6. Portability & Future-Proofing

### 6.1 Version Migration

**Scenario:** `.ehko` v1.0 file opened by generator expecting v2.0

**Strategy:**
```javascript
function migrate(ehkoData) {
  const currentVersion = ehkoData.ehko_version;
  
  if (currentVersion === '1.0' && GENERATOR_VERSION === '2.0') {
    // Apply migration transforms
    ehkoData = migrateV1ToV2(ehkoData);
  }
  
  return ehkoData;
}
```

**Philosophy:** Generators should gracefully handle older formats via migration pipelines.

---

### 6.2 Cross-Platform

`.ehko` files are:
- **Platform-agnostic:** JSON works everywhere
- **Human-readable:** Can be edited manually if needed
- **Git-friendly:** Text format, diffs well
- **Self-documenting:** Field names are descriptive

**Use Cases:**
- Version control (track Ehko evolution in git)
- Backup and restore
- Sharing between users
- Importing to other tools/platforms

---

## 7. Example Files

### 7.1 Minimal Nascent

```json
{
  "ehko_version": "1.0",
  "generator_version": "1.1",
  "metadata": {
    "name": "New Ehko",
    "created": "2025-12-07T10:00:00Z",
    "modified": "2025-12-07T10:00:00Z"
  },
  "authority": {
    "current_stage": "Nascent",
    "current_percent": 5.0,
    "history": []
  },
  "generation": {
    "seed": "user-12345-2025",
    "algorithm": "simple-hash",
    "parameters": {
      "coreShape": "circle",
      "coreSize": 30,
      "coreOpacity": 0.2,
      "coreBlur": 10,
      "particleCount": 4,
      "particleSize": 1.5,
      "particleOrbit": 20
    }
  },
  "colour": {
    "primary": "#6b8cce",
    "stage_palette": "nascent",
    "custom_override": null
  },
  "customisation": {
    "memory_symbols": [],
    "user_tweaks": {}
  },
  "export_preferences": {
    "default_format": "svg",
    "include_animations": true,
    "include_metadata": true
  }
}
```

---

### 7.2 Advanced Anchored

```json
{
  "ehko_version": "1.0",
  "generator_version": "1.1",
  "metadata": {
    "name": "Alexandra's Legacy Ehko",
    "created": "2024-03-15T08:00:00Z",
    "modified": "2025-12-07T14:30:00Z",
    "creator": "Alexandra Chen",
    "description": "Digital witness spanning 2+ years of reflection",
    "tags": ["legacy", "anchored", "multi-year"]
  },
  "authority": {
    "current_stage": "Anchored",
    "current_percent": 94.5,
    "history": [
      {"stage": "Nascent", "entered": "2024-03-15T08:00:00Z", "exited": "2024-06-01T00:00:00Z", "peak_percent": 18.0},
      {"stage": "Signal", "entered": "2024-06-01T00:00:00Z", "exited": "2024-09-20T00:00:00Z", "peak_percent": 38.5},
      {"stage": "Resonant", "entered": "2024-09-20T00:00:00Z", "exited": "2025-03-10T00:00:00Z", "peak_percent": 59.2},
      {"stage": "Manifest", "entered": "2025-03-10T00:00:00Z", "exited": "2025-10-05T00:00:00Z", "peak_percent": 78.8},
      {"stage": "Anchored", "entered": "2025-10-05T00:00:00Z", "exited": null, "peak_percent": 94.5}
    ]
  },
  "generation": {
    "seed": "alexandra-chen-legacy-2024",
    "algorithm": "simple-hash",
    "parameters": {
      "formType": "shrine",
      "formComplexity": "maximum",
      "layerCount": 5,
      "detailCount": 28,
      "groundingElement": true,
      "personalisation": {
        "memorySymbols": 3,
        "coreMemoryIntegration": true
      }
    }
  },
  "colour": {
    "primary": "#c9a962",
    "stage_palette": "anchored",
    "custom_override": null
  },
  "customisation": {
    "memory_symbols": [
      {"type": "music", "icon": "waveform", "position": "left-panel", "opacity": 0.6},
      {"type": "travel", "icon": "globe", "position": "right-panel", "opacity": 0.6},
      {"type": "family", "icon": "constellation", "position": "crown", "opacity": 0.5}
    ],
    "user_tweaks": {
      "architecturalStyle": "gothic",
      "detailDensity": "ornate"
    }
  },
  "export_preferences": {
    "default_format": "svg",
    "svg_size": "80x80",
    "png_sizes": ["160x160", "320x320", "640x640"],
    "include_animations": true,
    "include_metadata": true
  }
}
```

---

## 8. File Naming Convention

**Pattern:** `{name}_{stage}_v{iteration}.ehko`

**Examples:**
- `BrentEhko_Nascent_v1.0.ehko`
- `BrentEhko_Resonant_v2.3.ehko`
- `AlexandraLegacy_Anchored_v5.8.ehko`

**Version Numbering:**
- Major version: Stage transitions (1.0 → 2.0 when Nascent → Signal)
- Minor version: Parameter tweaks, customisations within same stage

---

## 9. Integration Points

### 9.1 EhkoForge Vault

**Storage Location:** `Mirrorwell/Ehkos/`

**Workflow:**
1. User reaches Authority milestone
2. System generates `.ehko` file
3. File saved to vault
4. SVG compiled and displayed in UI
5. PNG exported for sharing

---

### 9.2 Git Repository

**Tracking Evolution:**
```bash
git add BrentEhko_Resonant_v2.3.ehko
git commit -m "Authority 52.3% - Resonant stage refinement"
git push
```

**Benefits:**
- Complete evolution history in git log
- Revert to previous stages if needed
- Diff shows exact parameter changes

---

### 9.3 Export API

**Endpoint:** `POST /api/ehko/compile`

**Request:**
```json
{
  "ehko_file": "BrentEhko_Resonant_v2.3.ehko",
  "output_format": "svg",
  "include_metadata": true
}
```

**Response:**
```json
{
  "success": true,
  "output": "<svg>...</svg>",
  "filename": "BrentEhko_Resonant_v2.3.svg"
}
```

---

## 10. Security & Privacy

### 10.1 Sensitive Data

**Do NOT include in `.ehko` files:**
- API keys
- Personal identifiable information beyond name
- Private reflection content
- Authentication tokens

**Safe to include:**
- Visual parameters
- Evolution history (timestamps, stages)
- Memory symbol types (but not actual memory content)

---

### 10.2 Sharing

When sharing `.ehko` files:
- Review `metadata` block for sensitive info
- Consider removing `customisation.memory_symbols` if private
- Export to SVG/PNG strips most metadata (privacy layer)

---

## 11. Future Extensions

### 11.1 Planned Features

**v1.1:**
- `animation_preferences` block (frame rate, loop settings)
- `accessibility` block (high contrast mode, screen reader labels)

**v2.0:**
- 3D rendering parameters
- Voice-reactive animation settings
- Multi-Ehko interaction rules (for shared spaces)

---

**Changelog:**
- v1.0 — 2025-12-07 — Initial specification. Defined JSON schema, file operations, validation, and integration points.

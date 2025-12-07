---
title: ".ehkoavatar File Format Specification"
vault: "EhkoForge"
type: "specification"
category: "System Architecture"
status: "active"
version: "1.0"
created: 2025-12-07
updated: 2025-12-07
tags: [ehkoforge, file-format, avatar, visual-identity]
related: ["1_8_Ehko_Visual_Identity_Spec_v1_0.md", "1_10_Ehko_Complete_Package_Format_v1_0.md"]
---

# .EHKOAVATAR FILE FORMAT SPECIFICATION v1.0

## 1. Purpose

The `.ehkoavatar` file format contains **only visual representation parameters** for an Ehko's avatar. This is a **component format**, not a complete Ehko export.

**Use Cases:**
- Sharing just the visual design (avatar skin)
- Visual-only customisation and theming
- Avatar gallery/marketplace
- Quick visual iterations without full Ehko data

**NOT included:**
- Memories or reflections
- Identity data
- Personality layers
- Interaction history

**For complete Ehko export:** See `.ehko` Complete Package Format specification.

---

## 2. File Structure

### 2.1 Format
**Type:** JSON with strict schema validation  
**Encoding:** UTF-8  
**Extension:** `.ehkoavatar`

### 2.2 Complete Schema

```json
{
  "avatar_version": "1.0",
  "generator_version": "1.1",
  
  "metadata": {
    "name": "Brent's Ehko",
    "created": "2025-12-07T14:30:00Z",
    "modified": "2025-12-08T09:15:00Z",
    "creator": "Brent Thompson",
    "description": "Digital witness avatar",
    "tags": ["personal", "monitor-theme"]
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

## 3. Compilation

**Input:** `.ehkoavatar` file  
**Output:** SVG, PNG, CSS-only, or HTML

```javascript
const avatar = JSON.parse(fs.readFileSync('BrentAvatar.ehkoavatar'));
const svg = AvatarGenerator.compileToSVG(avatar);
const png = AvatarGenerator.compileToPNG(avatar, { size: 320 });
```

---

## 4. Integration

### 4.1 Part of Complete Ehko

When exporting a full `.ehko` package, the avatar data is embedded as a subsection:

```json
{
  "ehko_version": "1.0",
  "avatar": {
    /* .ehkoavatar contents here */
  },
  "memories": { /* ... */ },
  "identity": { /* ... */ }
}
```

### 4.2 Standalone Distribution

`.ehkoavatar` files can be shared independently for:
- Avatar marketplaces
- Visual theming
- Design portfolios

---

**Changelog:**
- v1.0 — 2025-12-07 — Split from complete .ehko format. Visual-only component specification.

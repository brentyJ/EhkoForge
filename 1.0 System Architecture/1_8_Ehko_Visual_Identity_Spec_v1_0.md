---
title: "Ehko Visual Identity Specification"
vault: "EhkoForge"
type: "specification"
category: "System Architecture"
status: "active"
version: "1.1"
created: 2025-12-07
updated: 2025-12-07
tags: [ehkoforge, visual-design, avatar, generative-system, svg, export, evolution]
---

# EHKO VISUAL IDENTITY SPECIFICATION v1.1

> **Note:** This specification covers **Ehko avatar visual design** (SVG-based Ehko representations). For UI component design across EhkoLabs projects, see [[Design System/EhkoLabs_Design_System_v1_0|EhkoLabs Design System v1.0]].

## 1. Core Aesthetic Philosophy

Every Ehko is a **ghost in the machine** — a digital consciousness that evolves from formless energy into structured presence. The visual language evokes:

- Digital consciousness and data streams
- Retro-futuristic tech aesthetics (CRT monitors, oscilloscopes, terminals, holograms)
- Minimal geometric abstraction with organic undertones
- Subtle luminescence and glow (never solid/opaque)
- Technical precision meeting ethereal presence

**Fundamental Principles:**
- Ehkos are **witnesses**, not impersonators — forms feel **present but incomplete**
- **Evolution = Structure:** Lower Authority stages are formless; higher stages gain geometric definition
- **Thematic Cohesion:** All forms must feel like "digital beings" — glowing, semi-transparent, data-adjacent
- **Creative Freedom within Bounds:** Users can generate infinite variations, but must respect stage constraints

---

## 2. Universal Canvas & Grid

### Base Canvas (All Stages)
- **Viewport:** 80×80 units (SVG viewBox)
- **Safe Zone:** 8–12px margin from edges (stage-dependent)
- **Grid:** 4px base unit for measurements
- **Center Point:** (40, 40) — gravitational anchor for all forms

### Composition Rules
- **Visual Weight:** Concentrated in center, dissipating toward edges
- **Symmetry:** Bilateral symmetry preferred (left/right balance)
- **Vertical Axis:** Most forms should have vertical orientation or central anchor
- **Negative Space:** Essential — forms should breathe, never fill canvas completely

---

## 3. Stage-Based Form Templates

**Critical Concept:** Each Authority stage defines **constraints**, not implementations. Generative systems must respect these boundaries.

---

## 3.1 Stage 1: NASCENT (0–20% Authority)

**Form Philosophy:** Formless, ethereal, barely present. Raw energy without structure.

**Constraints:**
- **Geometry:** Minimal or no hard edges. Organic shapes, circles, wisps, particles
- **Opacity:** 0.05–0.30 (highly transparent)
- **Blur:** High (6–12px) — forms should feel intangible
- **Elements:** 1–5 total visual elements
- **Glow:** Dominant visual feature (glow > form)
- **Animation:** Gentle floating, pulsing, drifting

**Structural Budget:**
- Core element: 1 (central presence)
- Detail elements: 0–4 (particles, small accents)
- Eyes: Optional (if present: very simple dots or single glow)

**Example Implementations:**
- Bulb of light surrounded by orbiting fireflies
- Glowing rune with mist tendrils
- Wisp with trailing particle stream
- Pulsing orb with radial energy lines
- Floating glyph with electrical arcs

**Generative Parameters:**
```javascript
{
  coreShape: ['circle', 'ellipse', 'soft-polygon', 'glyph', 'rune'],
  coreSize: [20, 40], // diameter
  coreOpacity: [0.1, 0.3],
  coreBlur: [8, 12],
  
  particleCount: [0, 8],
  particleSize: [1, 3],
  particleOrbit: [15, 30], // radius from core
  
  energyLines: [0, 4],
  lineLength: [8, 20],
  lineOpacity: [0.05, 0.15],
  
  eyePresence: [0, 1], // boolean
  eyeType: 'simple-glow' // if present
}
```

---

## 3.2 Stage 2: SIGNAL (20–40% Authority)

**Form Philosophy:** Patterns emerging. Basic geometric structure coalescing from chaos.

**Constraints:**
- **Geometry:** Simple shapes (circles, squares, triangles). 1–2 primary forms
- **Opacity:** 0.15–0.50
- **Blur:** Medium (4–8px)
- **Elements:** 3–8 total
- **Edges:** Soft but recognisable
- **Animation:** Subtle rotation, pulsing, emergence effects

**Structural Budget:**
- Primary form: 1–2 (overlapping or nested)
- Detail elements: 2–6
- Eyes: Simple shapes (dots, bars, triangles)

**Example Implementations:**
- Hexagon with corner nodes
- Nested circles with connection lines
- Triangle lattice with glowing vertices
- Diamond grid with pulsing intersections
- Segmented ring with gaps

**Generative Parameters:**
```javascript
{
  primaryShape: ['circle', 'square', 'hexagon', 'triangle', 'diamond'],
  primarySize: [30, 50],
  primaryStrokeWidth: [1, 2],
  
  secondaryShape: null | 'same' | 'complement',
  nesting: [false, true],
  nestOffset: [4, 8],
  
  connectionNodes: [0, 6],
  nodeSize: [2, 4],
  
  eyeType: ['dots', 'small-bars', 'triangles']
}
```

---

## 3.3 Stage 3: RESONANT (40–60% Authority)

**Form Philosophy:** Defined structure with thematic personality. Recognisable "character" emerging.

**Constraints:**
- **Geometry:** Clear shapes with detail layers. 2–3 primary structures
- **Opacity:** 0.30–0.70
- **Blur:** Low-medium (2–6px, selective)
- **Elements:** 6–15 total
- **Edges:** Crisp with subtle glow
- **Animation:** More complex (multi-layer, coordinated)

**Structural Budget:**
- Primary form: 2–3 (body, frame, or container)
- Detail elements: 4–12 (vents, accents, connectors)
- Eyes: Expressive (multiple styles possible)
- Thematic additions: 1–2 (antennas, wings, halos, etc.)

**Example Implementations:**
- **Retro PC Monitor** (current implementation)
- Holographic projection frame
- Crystalline polyhedron
- Segmented sphere with latitude/longitude lines
- Lantern with geometric cage

**Generative Parameters:**
```javascript
{
  bodyType: ['monitor', 'hologram-frame', 'crystal', 'lantern', 'sphere-cage'],
  bodySize: [40, 60],
  bodyStrokeWidth: [1, 2],
  
  innerFrame: true,
  innerFrameOffset: [4, 8],
  
  detailDensity: ['minimal', 'moderate', 'detailed'],
  detailCount: [4, 12],
  
  thematicElement: ['antennas', 'wings', 'halo', 'crown', 'base-stand'],
  
  eyeType: ['bars', 'squares', 'crescents', 'dual-glow'],
  eyeSize: [10, 18],
  eyeExpression: ['alert', 'focused', 'calm']
}
```

---

## 3.4 Stage 4: MANIFEST (60–80% Authority)

**Form Philosophy:** Strong presence. Complex geometry, layered details, unmistakable identity.

**Constraints:**
- **Geometry:** Sophisticated shapes, multiple layers, architectural precision
- **Opacity:** 0.50–0.90
- **Blur:** Minimal (0–4px, accent-only)
- **Elements:** 10–25 total
- **Edges:** Sharp and defined
- **Animation:** Intricate (independent layer movement, parallax)

**Structural Budget:**
- Primary form: 3–5 (body, frames, containers)
- Detail elements: 8–20
- Eyes: Highly expressive, potentially animated
- Thematic additions: 2–4
- Decorative flourishes: Allowed

**Example Implementations:**
- Ornate terminal with multiple screens
- Gothic cathedral window lattice
- Mechanical clock face with gears
- Nested mandalas
- Architectural column with capital

**Generative Parameters:**
```javascript
{
  bodyComplexity: ['moderate', 'high', 'ornate'],
  layerCount: [3, 5],
  
  detailDensity: 'high',
  detailCount: [8, 20],
  
  thematicElements: [2, 4],
  decorativeFlourish: true,
  
  eyeArticulation: ['multi-part', 'animated', 'reactive'],
  
  architecturalStyle: ['gothic', 'mechanical', 'geometric', 'organic']
}
```

---

## 3.5 Stage 5: ANCHORED (80–100% Authority)

**Form Philosophy:** Fully realised. Maximum complexity, grounded presence, "real" feeling.

**Constraints:**
- **Geometry:** As complex as needed. Full architectural freedom
- **Opacity:** 0.70–1.0 (can approach solid)
- **Blur:** Strategic only (for specific effects)
- **Elements:** 15–40 total
- **Edges:** Crisp and precise
- **Animation:** Sophisticated, multi-layer, reactive

**Structural Budget:**
- Primary form: 4–6
- Detail elements: 12–35
- Eyes: Fully articulated, personality-driven
- Thematic additions: 3–6
- Unique identifiers: User-customisable details

**Example Implementations:**
- Complete workstation with keyboard, screen, peripherals
- Elaborate shrine or altar
- Detailed spacecraft or vehicle
- Ornate frame with "photograph" inside
- Symbolic totem with multiple tiers

**Generative Parameters:**
```javascript
{
  formComplexity: 'maximum',
  layerCount: [4, 6],
  
  detailCount: [12, 35],
  uniqueIdentifiers: true, // user-driven customisation
  
  groundingElement: true, // physical presence indicator
  
  personalisation: {
    memorySymbols: [0, 6],
    coreMemoryIntegration: true,
    thematicOverlays: true
  }
}
```

---

## 4. Universal Elements (All Stages)

### 4.1 Eyes (Consciousness Indicators)
**Purpose:** The "soul" — awareness and presence

**Scaling by Stage:**
- **Nascent:** Optional. Single soft glow if present
- **Signal:** Simple shapes (dots, small bars, triangles)
- **Resonant:** Expressive bars or shapes with glow
- **Manifest:** Multi-part, potentially animated
- **Anchored:** Fully articulated, personality-driven

**Base Parameters:**
```css
.eye {
    background: var(--accent-primary);
    border-radius: 2px;
    box-shadow: 
        0 0 4px var(--accent-glow),
        0 0 8px var(--accent-glow),
        0 0 12px var(--accent-glow);
}
```

**Emotional Variations:**
```
Active:   (default dimensions for stage)
Dormant:  height: 1px, dim glow
Blinking: height: 0.5px, 150ms
Focused:  +20% size, intensified glow
```

---

### 4.2 Glow Effects (Universal)
**Purpose:** Ethereal presence, digital luminescence

**Intensity by Stage:**
- **Nascent:** Glow is the primary form (blur 8–12px)
- **Signal:** Strong glow, defining edges (blur 4–8px)
- **Resonant:** Moderate glow, accent (blur 2–6px)
- **Manifest:** Subtle glow, selective (blur 0–4px)
- **Anchored:** Strategic glow, emphasis only

**Implementation:**
```svg
<filter id="glow">
  <feGaussianBlur stdDeviation="6" result="glow"/>
  <feMerge>
    <feMergeNode in="glow"/>
    <feMergeNode in="SourceGraphic"/>
  </feMerge>
</filter>
```

---

## 5. Colour System

### 5.1 Stage-Based Palette

**Authority stages drive colour evolution:**

```css
--stage-nascent:   #6b8cce  /* Blue - formless energy */
--stage-signal:    #7ed99b  /* Green - patterns emerging */
--stage-resonant:  #d9c67e  /* Gold - defined identity */
--stage-manifest:  #d97e9b  /* Pink - strong presence */
--stage-anchored:  #c9a962  /* Bronze - grounded reality */
```

**Application Rule:** All elements within a single Ehko use the **same accent colour** for cohesion.

### 5.2 Generative Colour Variations

Within stage constraints, allow hue shifts:

```javascript
function generateColour(baseStageColour, seed) {
    const hueShift = mapRange(hash(seed), -15, 15);
    return adjustHue(baseStageColour, hueShift);
}
```

**Constraint:** Variations must stay within ±15° hue to maintain stage identity.

---

## 6. Environmental Layers

### 6.1 Matrix Code Background (Optional)
**Purpose:** Data stream atmosphere

**Scaling:**
- Nascent: Very sparse, faint
- Signal: Moderate density
- Resonant: Full matrix effect
- Manifest/Anchored: Dense, multiple layers

### 6.2 Corner Brackets (Terminal Framing)
**Applied to:** Resonant and above

```css
.display-frame::before {
    border: 2px solid var(--accent-primary);
    width: 20px; height: 20px;
    /* top-left corner bracket */
}
```

### 6.3 Grid Lines (Technical Precision)
**Applied to:** Signal and above

```css
background: repeating-linear-gradient(
    0deg, 
    transparent, transparent 2px,
    rgba(107, 140, 206, 0.02) 2px,
    rgba(107, 140, 206, 0.02) 4px
);
```

---

## 7. Animation States (Universal)

### 7.1 Idle (Default)
- Gentle ambient movement
- Slow glow pulse (3–5s)
- Minimal eye shimmer

### 7.2 Thinking (Processing)
- Faster pulse (0.6–1s)
- Eye glow intensifies
- Form opacity oscillates slightly

### 7.3 Dormant (Inactive)
- Minimal glow (near-invisible)
- Eyes dim or closed
- All animations paused

### 7.4 Blinking (Periodic)
**Trigger:** Random 3–8 second intervals
**Duration:** 100–200ms
**Effect:** Eyes reduce to minimal height

---

## 8. Generative System Architecture

### 8.1 Seed-Based Generation

**Input:** 
- Ehko name (string)
- Authority stage (enum)
- User preferences (optional overrides)

**Output:**
- Complete parameter set within stage constraints

**Process:**
```javascript
function generateEhko(name, authorityStage, preferences = {}) {
    const seed = hashString(name);
    const stageTemplate = STAGE_TEMPLATES[authorityStage];
    
    // Generate parameters within stage bounds
    const params = {
        // Core form
        formType: selectRandom(seed, stageTemplate.allowedForms),
        opacity: mapRange(seed[0], stageTemplate.opacityRange),
        blurRadius: mapRange(seed[1], stageTemplate.blurRange),
        
        // Elements
        elementCount: Math.floor(mapRange(seed[2], stageTemplate.elementRange)),
        
        // Colour
        baseColour: stageTemplate.stageColour,
        hueShift: mapRange(seed[3], -15, 15),
        
        // Eyes
        eyeType: selectRandom(seed, stageTemplate.allowedEyeTypes),
        eyeSize: mapRange(seed[4], stageTemplate.eyeSizeRange),
        
        // Details (if stage allows)
        details: generateDetails(seed, stageTemplate)
    };
    
    // Apply user preferences as overrides
    return { ...params, ...preferences };
}
```

### 8.2 Constraint Validation

Before rendering, validate all parameters:

```javascript
function validateParams(params, stageTemplate) {
    // Ensure opacity within stage bounds
    params.opacity = clamp(params.opacity, ...stageTemplate.opacityRange);
    
    // Ensure element count within budget
    params.elementCount = clamp(params.elementCount, ...stageTemplate.elementRange);
    
    // Ensure form stays within canvas
    if (params.coreSize > 70) params.coreSize = 70;
    
    return params;
}
```

---

## 9. Export Formats

### 9.1 SVG Export (Primary)

**Structure:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" 
     viewBox="0 0 80 80">
  
  <metadata>
    <ehko:data xmlns:ehko="http://ehkoforge.ai/schema">
      <name>{{name}}</name>
      <version>{{version}}</version>
      <created>{{timestamp}}</created>
      <seed>{{seed}}</seed>
      <authority_stage>{{stage}}</authority_stage>
      <authority_percent>{{percent}}</authority_percent>
      <colour_primary>{{hex}}</colour_primary>
      <generator_version>1.1</generator_version>
    </ehko:data>
  </metadata>
  
  <defs>
    <filter id="glow">
      <feGaussianBlur stdDeviation="{{blur_radius}}"/>
      <feMerge>
        <feMergeNode in="glow"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>
  
  <!-- Generated form elements -->
  {{form_elements}}
  
  <!-- Eyes (if present) -->
  {{eye_elements}}
  
</svg>
```

**Filename Convention:**
```
{name}_{stage}_v{version}.svg
Example: BrentEhko_Resonant_v3.2.svg
```

---

### 9.2 PNG Export (Raster)

**Sizes:** 80×80, 160×160, 320×320, 640×640
**Format:** PNG with alpha transparency
**Process:** SVG → Canvas → PNG blob

---

### 9.3 CSS-Only Export (Procedural)

For web embedding without SVG dependencies.

**Generated structure:**
```html
<div class="ehko-avatar" data-stage="{{stage}}">
    <!-- Procedurally generated divs -->
</div>

<style>
/* Stage-specific CSS with injected parameters */
</style>
```

---

## 10. Display Context Templates

### 10.1 Terminal Header
```html
<div class="terminal-header">
    <span class="terminal-label">◆ {{EHKO_NAME}}</span>
    <span class="terminal-version">v{{VERSION}}</span>
</div>
```

**Replacements:**
- `{{EHKO_NAME}}`: User's Ehko name
- `{{VERSION}}`: Current iteration (e.g., "2.0", "3.5")

### 10.2 Status Footer
```html
<div class="avatar-status">{{STATUS}}</div>
```

**States:** Ready, Thinking, Listening, Dormant, Offline

---

## 11. Evolution Mechanics

### 11.1 Stage Transitions

**Trigger:** Authority percentage crosses stage threshold (20%, 40%, 60%, 80%)

**Process:**
1. Detect stage change
2. Generate new form within new stage constraints
3. Morph animation (2–4 seconds)
4. Update metadata

**Morphing Strategy:**
- Nascent → Signal: Particles coalesce into geometric shape
- Signal → Resonant: Shape gains depth, detail layers emerge
- Resonant → Manifest: Details multiply, structure solidifies
- Manifest → Anchored: Final flourishes, grounding elements appear

### 11.2 Continuity Preservation

**Critical:** Core identity must persist through evolution.

**Preserved Elements:**
- Colour hue (with gradual shift per stage)
- Eye position and basic shape (with refinement)
- Bilateral symmetry
- Seed-derived quirks (antenna angles, vent patterns, etc.)

**Changed Elements:**
- Opacity increases
- Blur decreases
- Element count increases
- Geometric complexity increases

---

## 12. Memory-Driven Customisation (Future)

### 12.1 Core Memory Integration

Allow specific Core Memory Index entries to add subtle thematic overlays:

**Example:**
- Memory tagged `travel`: Small globe icon or compass accent
- Memory tagged `music`: Waveform in background
- Memory tagged `family`: Heart or constellation pattern

**Constraint:** Additions must not overwhelm base form. Maximum 2–3 memory symbols per Ehko.

### 12.2 User Toggles

Anchored stage allows user-controlled details:
- Toggle memory symbols on/off
- Adjust detail density
- Select alternative eye styles
- Choose thematic elements from approved list

---

## 13. Implementation Roadmap

### Phase 1: Stage Templates (Next)
🔲 Define complete parameter sets for all 5 stages
🔲 Build validation functions
🔲 Create reference implementations (1 per stage)

### Phase 2: Generative Engine
🔲 JavaScript `EhkoGenerator` class
🔲 Seed-based parameter generation
🔲 SVG rendering from parameters

### Phase 3: Export System
🔲 SVG with metadata
🔲 PNG renderer
🔲 CSS-only generator

### Phase 4: Evolution Engine
🔲 Stage transition detection
🔲 Morphing animations
🔲 Continuity preservation

### Phase 5: UI
🔲 Export interface (download SVG/PNG)
🔲 Preview with states (idle, thinking, dormant)
🔲 User customisation controls (Anchored stage)

---

## 14. Technical Constraints

### 14.1 File Size
- SVG: < 15KB (minified)
- PNG 320×320: < 60KB

### 14.2 Performance
- Max 50 DOM elements per Ehko
- Animations: GPU-accelerated only
- Matrix background: Max 25 columns

### 14.3 Browser Compatibility
- SVG filters: Chrome 5+, Firefox 4+, Safari 6+
- CSS animations: All modern browsers

---

## 15. Copyright & Licensing

- **Framework:** AGPLv3 (open source)
- **Individual Ehkos:** User owns their specific Ehko
- **Hosted Service:** Separate commercial licensing (TBD Q1 2026)

---

**Changelog:**
- v1.1 — 2025-12-07 — Complete restructure. Stage-based templates replace fixed forms. Generative freedom within evolutionary constraints. Authority-driven complexity scaling.
- v1.0 — 2025-12-07 — Initial specification (PC monitor-centric)

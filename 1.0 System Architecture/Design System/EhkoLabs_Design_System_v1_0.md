---
title: "EhkoLabs Design System"
vault: "EhkoForge"
type: "specification"
category: "Design System"
status: "active"
version: "1.0"
created: 2025-12-26
updated: 2025-12-26
tags: [design-system, ui, component-library, shadcn, cross-project, consistency]
---

# EHKOLABS DESIGN SYSTEM v1.0

## 1. Purpose & Scope

This document defines the unified design system for all EhkoLabs projects, ensuring visual and technical consistency across:

- **EhkoForge** — AI identity preservation framework
- **ReCog** — Recursive cognition engine web interface  
- **GlyphWorks** — SVG generation control panel
- **ehkolabs.io** — Public-facing website

### Core Philosophy

**"Consistent structure, unified aesthetic, shared components"**

All EhkoLabs interfaces should feel like they belong to the same family while allowing each project to express its unique purpose through thematic variations.

---

## 2. Component Foundation: shadcn/ui

### 2.1 Why shadcn/ui?

shadcn/ui was chosen as the component foundation because:

✅ **Already integrated** — We use Tailwind CSS and lucide-react across all projects  
✅ **Code ownership** — Components are copied into projects, not imported from npm  
✅ **Full customization** — Every component can be themed and modified  
✅ **AI-friendly** — Claude can generate and modify shadcn/ui components natively  
✅ **Professional polish** — Accessibility, keyboard navigation, ARIA labels built-in  
✅ **No vendor lock-in** — No black-box dependencies or proprietary systems  

### 2.2 What shadcn/ui Provides

shadcn/ui is a **component distribution system**, not a traditional library. It provides:

- **Base components** — Button, Card, Dialog, Table, Form, Input, Select, etc.
- **Radix UI primitives** — Unstyled, accessible component foundations
- **Tailwind styling** — All components styled with utility classes
- **TypeScript** — Full type safety and autocomplete
- **CLI installation** — `npx shadcn@latest add button` copies component code into project

**Key insight:** We don't install `@shadcn/ui` as a package. We install individual components that become **our code** to modify.

### 2.3 Current Stack Alignment

```
EhkoLabs Stack:
├── Backend: Flask (Python) ✓ Keep
├── Frontend: React ✓ Keep  
├── Styling: Tailwind CSS ✓ Keep
├── Icons: lucide-react ✓ Keep
└── Components: shadcn/ui ← Add this layer
```

---

## 3. Cross-Project Structure

### 3.1 Shared Foundation

**All projects use:**

- **Tailwind CSS** — Utility-first styling  
- **lucide-react** — Icon library (4000+ icons)
- **shadcn/ui components** — Base component library
- **React** — Frontend framework (for web interfaces)
- **TypeScript** — Type safety

### 3.2 Project-Specific Theming

Each project applies a **theme overlay** to the shared foundation:

| Project | Theme | Accent Colors | Visual Style |
|---------|-------|--------------|--------------|
| **EhkoForge** | Terminal/Arcane | Blue/Cyan (#6b8cce) | Dark, glowing, retro-futuristic |
| **ReCog** | Processing/Clinical | Green/Teal (#7ed99b) | Clean, analytical, data-focused |
| **GlyphWorks** | Creative/Generative | Purple/Magenta (#9b7ed9) | Artistic, vibrant, tool-focused |
| **Website** | Professional/Modern | Gold/Bronze (#c9a962) | Polished, approachable, trustworthy |

### 3.3 Component Consistency

**Same components, different themes:**

```typescript
// All projects have the same Button component
import { Button } from "@/components/ui/button"

// But themed differently via CSS variables
<Button>Submit</Button>
```

**EhkoForge theme:**
```css
--primary: 214 70% 60%;      /* Blue */
--background: 222 47% 11%;   /* Dark navy */
```

**ReCog theme:**
```css  
--primary: 142 71% 69%;      /* Green */
--background: 222 47% 11%;   /* Dark navy */
```

---

## 4. Implementation Strategy

### 4.1 Phase 1: EhkoForge Control Panel (Current)

**Goal:** Establish shadcn/ui as base component library for EhkoForge interfaces

**Actions:**
1. ✅ Install shadcn/ui CLI  
2. ✅ Add core components (Button, Card, Dialog, Table)
3. ✅ Apply EhkoForge terminal theme to components
4. ✅ Build Control Panel using themed shadcn/ui components

**Status:** In progress (Session 26)

### 4.2 Phase 2: ehkolabs.io Website

**Goal:** Rebuild website with shadcn/ui components

**Actions:**
1. Install shadcn/ui in website project
2. Add marketing components (Hero, Features, Pricing, Testimonials)
3. Apply professional theme (gold/bronze accents)
4. Rebuild landing page, product pages, documentation

**Timeline:** Q1 2026 (pre-launch)

### 4.3 Phase 3: ReCog Web Interface

**Goal:** Build ReCog processing dashboard with shadcn/ui

**Actions:**
1. Install shadcn/ui in ReCog project
2. Add data visualization components (Charts, Tables, Stats)
3. Apply clinical/analytical theme (green/teal)
4. Build analysis dashboard, batch processing UI

**Timeline:** Q1 2026 (alongside website)

### 4.4 Phase 4: GlyphWorks Control Panel

**Goal:** Create SVG generation interface with shadcn/ui

**Actions:**
1. Install shadcn/ui in GlyphWorks project
2. Add creative components (Color Picker, Slider, Toggle)
3. Apply creative/generative theme (purple/magenta)
4. Build glyph editor, parameter controls, preview system

**Timeline:** Q2 2026 (post-launch)

---

## 5. Component Library Structure

### 5.1 Core Components (All Projects)

**Layout:**
- `Card` — Content containers
- `Separator` — Section dividers
- `Tabs` — Multi-view interfaces

**Forms:**
- `Button` — Actions and triggers
- `Input` — Text fields
- `Select` — Dropdown menus
- `Checkbox` — Binary options
- `RadioGroup` — Mutually exclusive choices
- `Slider` — Numeric ranges
- `Switch` — Toggle states
- `Textarea` — Multi-line text

**Feedback:**
- `Alert` — Status messages
- `Badge` — Labels and tags
- `Progress` — Loading states
- `Skeleton` — Content placeholders
- `Toast` — Notifications

**Overlays:**
- `Dialog` — Modal windows
- `Sheet` — Slide-out panels
- `Popover` — Contextual pointers
- `DropdownMenu` — Action menus
- `ContextMenu` — Right-click menus

**Data Display:**
- `Table` — Structured data
- `Avatar` — User/Ehko representations
- `Accordion` — Collapsible content

### 5.2 Project-Specific Components

**EhkoForge:**
- `IngotCard` — Forge review interface
- `EhkoAvatar` — SVG-based Ehko display (custom)
- `TerminalPrompt` — Command-line aesthetic input
- `MatrixBackground` — Data stream effect (custom)

**ReCog:**
- `AnalysisChart` — Tier 0 signal visualization
- `BatchProgress` — Multi-file processing status
- `EntityCard` — Extracted entity display
- `CorrelationGraph` — Pattern connections (custom)

**GlyphWorks:**
- `GlyphPreview` — Live SVG rendering (custom)
- `ParameterPanel` — Code-based controls
- `ColorPalette` — Hue/saturation/lightness pickers
- `ExportDialog` — Multi-format export options

**Website:**
- `Hero` — Landing section
- `FeatureGrid` — Product highlights
- `PricingCard` — Subscription tiers
- `Testimonial` — User quotes
- `CTABanner` — Call-to-action sections

---

## 6. Typography System

### 6.1 Font Stack

**Primary:** Inter (variable font)
- Clean, modern, highly readable
- Used for UI elements, body text, headings

**Monospace:** JetBrains Mono
- Used for code, terminal output, technical data
- EhkoForge terminal aesthetic

**Implementation:**
```css
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {
  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  --font-mono: 'JetBrains Mono', 'Courier New', monospace;
}
```

### 6.2 Type Scale (Tailwind)

```
text-xs    — 0.75rem  (12px) — Labels, captions
text-sm    — 0.875rem (14px) — Body small, metadata
text-base  — 1rem     (16px) — Body text
text-lg    — 1.125rem (18px) — Emphasized text
text-xl    — 1.25rem  (20px) — Subheadings
text-2xl   — 1.5rem   (24px) — Headings
text-3xl   — 1.875rem (30px) — Page titles
text-4xl   — 2.25rem  (36px) — Hero headings
```

---

## 7. Color System

### 7.1 Base Palette (Tailwind Variables)

All projects use the same CSS variable structure:

```css
:root {
  --background: 222 47% 11%;        /* Dark navy base */
  --foreground: 210 40% 98%;        /* Off-white text */
  
  --card: 222 47% 11%;              /* Same as background */
  --card-foreground: 210 40% 98%;
  
  --popover: 222 84% 4.9%;          /* Darker overlay */
  --popover-foreground: 210 40% 98%;
  
  --primary: XXX XX% XX%;           /* PROJECT-SPECIFIC */
  --primary-foreground: 222 47% 11%;
  
  --secondary: 217 32% 17%;         /* Muted variant */
  --secondary-foreground: 210 40% 98%;
  
  --muted: 217 32% 17%;
  --muted-foreground: 215 20% 65%;
  
  --accent: 217 32% 17%;
  --accent-foreground: 210 40% 98%;
  
  --destructive: 0 62% 30%;         /* Red for errors/delete */
  --destructive-foreground: 210 40% 98%;
  
  --border: 217 32% 17%;
  --input: 217 32% 17%;
  --ring: XXX XX% XX%;              /* PROJECT-SPECIFIC */
}
```

### 7.2 Project-Specific Primary Colors

**EhkoForge (Blue):**
```css
--primary: 214 70% 60%;      /* #6b8cce */
--ring: 214 70% 60%;
```

**ReCog (Green):**
```css
--primary: 142 71% 69%;      /* #7ed99b */
--ring: 142 71% 69%;
```

**GlyphWorks (Purple):**
```css
--primary: 262 54% 67%;      /* #9b7ed9 */
--ring: 262 54% 67%;
```

**Website (Gold):**
```css
--primary: 42 46% 58%;       /* #c9a962 */
--ring: 42 46% 58%;
```

### 7.3 Semantic Colors (Shared)

```css
--success: 142 71% 45%;      /* Green */
--warning: 38 92% 50%;       /* Orange */
--error: 0 84% 60%;          /* Red */
--info: 217 91% 60%;         /* Blue */
```

---

## 8. Spacing & Layout

### 8.1 Spacing Scale (Tailwind)

```
0   — 0px
1   — 0.25rem  (4px)
2   — 0.5rem   (8px)
3   — 0.75rem  (12px)
4   — 1rem     (16px)
6   — 1.5rem   (24px)
8   — 2rem     (32px)
12  — 3rem     (48px)
16  — 4rem     (64px)
```

### 8.2 Layout Grid

**Consistent padding/margins:**
- **Mobile:** `px-4` (16px)
- **Tablet:** `px-6` (24px)
- **Desktop:** `px-8` (32px)
- **Wide:** `px-12` (48px)

**Container max-widths:**
- **sm:** 640px
- **md:** 768px
- **lg:** 1024px
- **xl:** 1280px
- **2xl:** 1536px

---

## 9. Animation & Motion

### 9.1 Transitions (Tailwind)

```css
transition-none     — No transition
transition-all      — All properties (150ms)
transition          — Default (150ms cubic-bezier)
transition-colors   — Color changes only
transition-opacity  — Fade effects
transition-transform — Movement/scaling
```

**Duration scale:**
```
duration-75   — 75ms
duration-100  — 100ms
duration-150  — 150ms (default)
duration-200  — 200ms
duration-300  — 300ms
duration-500  — 500ms
duration-700  — 700ms
```

### 9.2 Easing Curves

```css
ease-linear    — Linear
ease-in        — Start slow
ease-out       — End slow (default for most UI)
ease-in-out    — Slow both ends
```

### 9.3 Project-Specific Animations

**EhkoForge:**
- Matrix code rain (custom)
- Glow pulse (2-4s)
- Terminal blink (500ms on/off)

**ReCog:**
- Progress bars (linear)
- Data fade-in (300ms)
- Chart transitions (500ms ease-out)

**GlyphWorks:**
- SVG path drawing (stroke-dashoffset)
- Color transitions (300ms)
- Parameter sliders (100ms)

---

## 10. Accessibility Standards

### 10.1 WCAG 2.1 Level AA Compliance

**Color Contrast:**
- **Text:** Minimum 4.5:1 ratio
- **Large text (18px+):** Minimum 3:1 ratio
- **UI components:** Minimum 3:1 ratio

**Keyboard Navigation:**
- All interactive elements tabbable
- Focus states clearly visible
- Skip navigation links
- No keyboard traps

**Screen Reader Support:**
- Semantic HTML (header, nav, main, footer)
- ARIA labels on icon buttons
- Alt text on images
- Form labels and error messages

### 10.2 Focus Styles

```css
:focus-visible {
  outline: 2px solid var(--ring);
  outline-offset: 2px;
  border-radius: 0.25rem;
}
```

shadcn/ui components include this by default.

---

## 11. Responsive Design

### 11.1 Breakpoints (Tailwind)

```
sm:  640px  — Mobile landscape / Small tablet
md:  768px  — Tablet portrait
lg:  1024px — Tablet landscape / Small desktop
xl:  1280px — Desktop
2xl: 1536px — Large desktop
```

### 11.2 Mobile-First Approach

All styling starts mobile and scales up:

```tsx
<div className="px-4 md:px-8 lg:px-12">
  {/* 16px mobile, 32px tablet, 48px desktop */}
</div>
```

### 11.3 Project Priorities

**EhkoForge:** Desktop-first (Control Panel is touch-optimized but primarily desktop)
**ReCog:** Desktop-first (Data analysis requires screen space)
**GlyphWorks:** Desktop-only (SVG editing needs precision)
**Website:** Mobile-first (Public audience, SEO)

---

## 12. Icon System

### 12.1 lucide-react Library

**Why lucide-react:**
- 4000+ icons (comprehensive coverage)
- Consistent design language
- Tree-shakeable (only import used icons)
- TypeScript support
- React component API
- Open source (MIT license)

**Usage:**
```tsx
import { Download, Settings, AlertCircle } from 'lucide-react'

<Button>
  <Download className="mr-2 h-4 w-4" />
  Export
</Button>
```

### 12.2 Icon Sizing

```
h-3 w-3   — 12px  — Inline with small text
h-4 w-4   — 16px  — Default (buttons, labels)
h-5 w-5   — 20px  — Emphasized actions
h-6 w-6   — 24px  — Section headings
h-8 w-8   — 32px  — Feature icons
h-12 w-12 — 48px  — Hero icons
```

### 12.3 Custom Icons (GlyphWorks)

GlyphWorks generates custom SVG glyphs programmatically. These supplement lucide-react but follow the same sizing conventions.

---

## 13. Code Style & Conventions

### 13.1 File Naming

**Components:**
```
PascalCase.tsx  — React components
camelCase.ts    — Utilities, helpers
kebab-case.css  — Stylesheets
UPPERCASE.md    — Documentation
```

**Example:**
```
components/
├── ui/
│   ├── Button.tsx
│   ├── Card.tsx
│   └── Dialog.tsx
├── IngotCard.tsx
└── MatrixBackground.tsx
```

### 13.2 Component Structure

```tsx
// Standard shadcn/ui component pattern
import * as React from "react"
import { cn } from "@/lib/utils"

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "default" | "destructive" | "outline" | "ghost"
  size?: "default" | "sm" | "lg" | "icon"
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "default", size = "default", ...props }, ref) => {
    return (
      <button
        className={cn(
          "inline-flex items-center justify-center rounded-md",
          variants[variant],
          sizes[size],
          className
        )}
        ref={ref}
        {...props}
      />
    )
  }
)
Button.displayName = "Button"

export { Button }
```

### 13.3 Tailwind Class Ordering

Use Prettier plugin `prettier-plugin-tailwindcss` for automatic class sorting:

```tsx
// Layout → Sizing → Spacing → Typography → Visual → Interactive
<div className="flex items-center gap-4 px-4 py-2 text-sm font-medium bg-primary text-primary-foreground hover:bg-primary/90 transition-colors">
```

---

## 14. Documentation Standards

### 14.1 Component Documentation

Every custom component includes:

```tsx
/**
 * IngotCard - Displays a single ingot for forge review
 * 
 * @param ingot - Ingot data object from API
 * @param onAccept - Callback when user accepts ingot
 * @param onReject - Callback when user rejects ingot
 * 
 * @example
 * <IngotCard 
 *   ingot={ingotData}
 *   onAccept={handleAccept}
 *   onReject={handleReject}
 * />
 */
export function IngotCard({ ingot, onAccept, onReject }: IngotCardProps) {
  // ...
}
```

### 14.2 Style Guide Documentation

Each project maintains:
- `DESIGN_GUIDE.md` — Project-specific theme documentation
- `COMPONENT_LIBRARY.md` — Available components list
- `EXAMPLES.md` — Real-world usage examples

---

## 15. Future Considerations

### 15.1 Mobile Apps (Tamagui)

**Logged for future:** When building native mobile apps (iOS/Android), consider **Tamagui** as a React Native + Web unified framework.

**Why Tamagui:**
- Unified codebase for mobile + web
- 100% style parity across platforms
- Performance-optimized compiler
- Similar philosophy to shadcn/ui (own the code)

**Use cases:**
- EhkoForge mobile companion app
- ReCog mobile dashboard
- Field data collection

**Timeline:** Post-launch (Q2-Q3 2026)

**Decision:** Log now, evaluate when mobile becomes priority

### 15.2 Design Tokens

Consider extracting shared values into design token system:

```json
{
  "color": {
    "brand": {
      "ehkoforge": "#6b8cce",
      "recog": "#7ed99b",
      "glyphworks": "#9b7ed9",
      "website": "#c9a962"
    }
  },
  "spacing": {
    "base": "4px",
    "scale": [0, 4, 8, 12, 16, 24, 32, 48, 64]
  }
}
```

**Timeline:** Phase 2 (when managing 4+ projects)

---

## 16. Version History

- **v1.0** — 2025-12-26 — Initial design system specification. Established shadcn/ui as foundation, defined cross-project structure, logged Tamagui for future mobile.

---

**Status:** Active  
**Next Review:** Q1 2026 (post-website launch)

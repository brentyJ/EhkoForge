---
title: "Design System Quick Reference"
vault: "EhkoForge"
type: "reference"
category: "Design System"
status: "active"
version: "1.0"
created: 2025-12-26
updated: 2025-12-26
tags: [design-system, quick-reference, shadcn, component-library]
---

# DESIGN SYSTEM QUICK REFERENCE

> One-page summary of EhkoLabs unified design system

---

## Foundation

**Component Library:** shadcn/ui (React + Radix UI + Tailwind CSS)  
**Icons:** lucide-react (4000+ icons)  
**Styling:** Tailwind CSS utility-first  
**Frontend:** React + TypeScript  

**Philosophy:** "Consistent structure, unified aesthetic, shared components"

---

## Project Themes

| Project | Accent Color | Visual Style |
|---------|-------------|--------------|
| **EhkoForge** | Blue (#6b8cce) | Terminal/Arcane |
| **ReCog** | Green (#7ed99b) | Clinical/Data |
| **GlyphWorks** | Purple (#9b7ed9) | Creative/Generative |
| **Website** | Gold (#c9a962) | Professional/Modern |

---

## Core Components (All Projects)

**Layout:** Card, Separator, Tabs  
**Forms:** Button, Input, Select, Checkbox, RadioGroup, Slider, Switch, Textarea  
**Feedback:** Alert, Badge, Progress, Skeleton, Toast  
**Overlays:** Dialog, Sheet, Popover, DropdownMenu, ContextMenu  
**Data:** Table, Avatar, Accordion  

---

## Typography

**Primary:** Inter (variable font) — UI, body text, headings  
**Monospace:** JetBrains Mono — Code, terminal, technical data  

**Scale:** xs(12px) → sm(14px) → base(16px) → lg(18px) → xl(20px) → 2xl(24px) → 3xl(30px) → 4xl(36px)

---

## Colors (CSS Variables)

```css
--background: 222 47% 11%;        /* Dark navy */
--foreground: 210 40% 98%;        /* Off-white */
--primary: XXX XX% XX%;           /* Project-specific */
--destructive: 0 62% 30%;         /* Red */
```

**Project Primary Colors:**
- EhkoForge: `214 70% 60%`
- ReCog: `142 71% 69%`
- GlyphWorks: `262 54% 67%`
- Website: `42 46% 58%`

---

## Spacing Scale

```
0(0px) 1(4px) 2(8px) 3(12px) 4(16px) 6(24px) 8(32px) 12(48px) 16(64px)
```

---

## Responsive Breakpoints

```
sm: 640px   md: 768px   lg: 1024px   xl: 1280px   2xl: 1536px
```

---

## Installation

**1. Install shadcn/ui CLI:**
```bash
npx shadcn@latest init
```

**2. Add components:**
```bash
npx shadcn@latest add button card dialog table
```

**3. Apply project theme:**
Update CSS variables in `globals.css` or `tailwind.config.js`

---

## Usage Example

```tsx
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Download } from "lucide-react"

<Card className="p-6">
  <h2 className="text-2xl font-semibold mb-4">Export Data</h2>
  <Button>
    <Download className="mr-2 h-4 w-4" />
    Download
  </Button>
</Card>
```

---

## Future: Mobile Apps (Tamagui)

**Logged for Q2-Q3 2026:** When building native mobile apps, evaluate **Tamagui** for unified React Native + Web development.

**Use cases:** EhkoForge companion app, ReCog mobile dashboard

---

**Full documentation:** [[Design System/EhkoLabs_Design_System_v1_0|EhkoLabs Design System v1.0]]

# EhkoForge Pre-Continuation Updates

**Target:** Modernize EhkoForge frontend to match ReCog quality standards  
**Date Created:** 2026-01-10  
**For:** Claude Code CLI execution  
**Context:** EhkoForge development has been paused for ReCog work. Now bringing EhkoForge up to speed with modern patterns established in ReCog.

---

## Overview

EhkoForge needs a major frontend upgrade to incorporate:
- shadcn/ui component library (as used in ReCog)
- Organized component structure
- Radix UI primitives
- Modern React patterns
- Consistent terminal theme
- Proper utility functions
- Component documentation

**Reference Implementation:** `C:\EhkoVaults\ReCog\_ui\` (this is the gold standard)

---

## Current State Assessment

### What EhkoForge Has
- ✅ Vite + React setup
- ✅ Tailwind CSS configured
- ✅ lucide-react icons
- ✅ Basic terminal theme CSS variables
- ✅ class-variance-authority
- ✅ Flask backend (forge_server.py)

### What EhkoForge Needs
- ❌ shadcn/ui component library
- ❌ Radix UI primitives
- ❌ Organized src/ structure (components/ui/, contexts/, hooks/)
- ❌ Utility functions (cn, etc.)
- ❌ UI components (Button, Card, Dialog, etc.)
- ❌ components.json configuration
- ❌ Consistent import paths (@/ alias)
- ❌ Modern component patterns

---

## Phase 1: Dependencies & Configuration

### 1.1 Install Missing Dependencies

**Working Directory:** `C:\EhkoVaults\EhkoForge\5.0 Scripts\control_panel\`

```bash
# Radix UI primitives (foundation for shadcn/ui)
npm install @radix-ui/react-dialog
npm install @radix-ui/react-label
npm install @radix-ui/react-select
npm install @radix-ui/react-slot
npm install @radix-ui/react-tabs
npm install @radix-ui/react-checkbox
npm install @radix-ui/react-switch
npm install @radix-ui/react-tooltip
npm install @radix-ui/react-dropdown-menu
npm install @radix-ui/react-popover

# Animation
npm install tailwindcss-animate

# Already installed (verify versions match ReCog):
# - lucide-react ^0.454.0 ✓
# - class-variance-authority ^0.7.0 ✓
# - clsx ^2.1.1 ✓
# - tailwind-merge ^2.5.4 ✓
```

### 1.2 Create components.json

**File:** `C:\EhkoVaults\EhkoForge\5.0 Scripts\control_panel\components.json`

```json
{
  "$schema": "https://ui.shadcn.com/schema.json",
  "style": "default",
  "rsc": false,
  "tsx": false,
  "tailwind": {
    "config": "tailwind.config.js",
    "css": "src/index.css",
    "baseColor": "slate",
    "cssVariables": true,
    "prefix": ""
  },
  "aliases": {
    "components": "@/components",
    "utils": "@/lib",
    "ui": "@/components/ui",
    "lib": "@/lib",
    "hooks": "@/hooks"
  }
}
```

### 1.3 Update vite.config.js

**File:** `C:\EhkoVaults\EhkoForge\5.0 Scripts\control_panel\vite.config.js`

Add path aliases:

```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
})
```

### 1.4 Update Tailwind Config

**File:** `C:\EhkoVaults\EhkoForge\5.0 Scripts\control_panel\tailwind.config.js`

Ensure it has animation support:

```javascript
/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ["class"],
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      keyframes: {
        "accordion-down": {
          from: { height: "0" },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: "0" },
        },
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
}
```

---

## Phase 2: Directory Structure

### 2.1 Create New Directories

**Working Directory:** `C:\EhkoVaults\EhkoForge\5.0 Scripts\control_panel\src\`

```bash
# Create new structure
mkdir components
mkdir components\ui
mkdir lib
mkdir hooks
mkdir contexts
```

### 2.2 Directory Purpose

```
src/
├── components/
│   ├── ui/              # shadcn/ui components (Button, Card, Dialog, etc.)
│   ├── forge/           # EhkoForge-specific components (ForgePanel, ManaBar, etc.)
│   └── pages/           # Page-level components (Dashboard, Settings, etc.)
├── lib/
│   └── utils.js         # Utility functions (cn, etc.)
├── hooks/               # Custom React hooks
├── contexts/            # React contexts (Theme, Auth, etc.)
├── App.jsx              # Main app component
├── main.jsx             # Entry point
└── index.css            # Global styles + Tailwind
```

---

## Phase 3: Core Utilities

### 3.1 Create utils.js

**File:** `C:\EhkoVaults\EhkoForge\5.0 Scripts\control_panel\src\lib\utils.js`

```javascript
import { clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs) {
  return twMerge(clsx(inputs))
}
```

---

## Phase 4: UI Components (Priority Order)

Create these components based on ReCog implementations. Each should follow the same pattern:
- Use Radix UI primitives
- Use class-variance-authority for variants
- Export component + variants
- Include JSDoc comments

### 4.1 Button Component (HIGHEST PRIORITY)

**File:** `C:\EhkoVaults\EhkoForge\5.0 Scripts\control_panel\src\components\ui\button.jsx`

**Source Reference:** `C:\EhkoVaults\ReCog\_ui\src\components\ui\button.jsx`

**Implementation Notes:**
- Copy from ReCog but adjust color scheme for EhkoForge theme
- EhkoForge uses blue primary, ReCog uses orange
- Variants: default, destructive, outline, secondary, ghost, link
- Sizes: default, sm, lg, icon

```javascript
import * as React from "react"
import { Slot } from "@radix-ui/react-slot"
import { cva } from "class-variance-authority"
import { cn } from "@/lib/utils"

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground hover:bg-primary/90",
        destructive: "bg-destructive text-destructive-foreground hover:bg-destructive/90",
        outline: "border border-input bg-transparent hover:bg-accent hover:text-accent-foreground",
        secondary: "bg-secondary text-secondary-foreground hover:bg-secondary/80",
        ghost: "hover:bg-accent hover:text-accent-foreground",
        link: "text-primary underline-offset-4 hover:underline",
      },
      size: {
        default: "h-9 px-4 py-2",
        sm: "h-8 rounded-md px-3 text-xs",
        lg: "h-10 rounded-md px-6",
        icon: "h-9 w-9",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

const Button = React.forwardRef(({ className, variant, size, asChild = false, ...props }, ref) => {
  const Comp = asChild ? Slot : "button"
  return (
    <Comp
      className={cn(buttonVariants({ variant, size, className }))}
      ref={ref}
      {...props}
    />
  )
})
Button.displayName = "Button"

export { Button, buttonVariants }
```

### 4.2 Card Component

**File:** `C:\EhkoVaults\EhkoForge\5.0 Scripts\control_panel\src\components\ui\card.jsx`

**Source Reference:** `C:\EhkoVaults\ReCog\_ui\src\components\ui\card.jsx`

```javascript
import * as React from "react"
import { cn } from "@/lib/utils"

const Card = React.forwardRef(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn(
      "rounded-lg border bg-card text-card-foreground shadow",
      className
    )}
    {...props}
  />
))
Card.displayName = "Card"

const CardHeader = React.forwardRef(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("flex flex-col space-y-1.5 p-6", className)}
    {...props}
  />
))
CardHeader.displayName = "CardHeader"

const CardTitle = React.forwardRef(({ className, ...props }, ref) => (
  <h3
    ref={ref}
    className={cn("font-semibold leading-none tracking-tight", className)}
    {...props}
  />
))
CardTitle.displayName = "CardTitle"

const CardDescription = React.forwardRef(({ className, ...props }, ref) => (
  <p
    ref={ref}
    className={cn("text-sm text-muted-foreground", className)}
    {...props}
  />
))
CardDescription.displayName = "CardDescription"

const CardContent = React.forwardRef(({ className, ...props }, ref) => (
  <div ref={ref} className={cn("p-6 pt-0", className)} {...props} />
))
CardContent.displayName = "CardContent"

const CardFooter = React.forwardRef(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("flex items-center p-6 pt-0", className)}
    {...props}
  />
))
CardFooter.displayName = "CardFooter"

export { Card, CardHeader, CardFooter, CardTitle, CardDescription, CardContent }
```

### 4.3 Input Component

**File:** `C:\EhkoVaults\EhkoForge\5.0 Scripts\control_panel\src\components\ui\input.jsx`

```javascript
import * as React from "react"
import { cn } from "@/lib/utils"

const Input = React.forwardRef(({ className, type, ...props }, ref) => {
  return (
    <input
      type={type}
      className={cn(
        "flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50",
        className
      )}
      ref={ref}
      {...props}
    />
  )
})
Input.displayName = "Input"

export { Input }
```

### 4.4 Label Component

**File:** `C:\EhkoVaults\EhkoForge\5.0 Scripts\control_panel\src\components\ui\label.jsx`

```javascript
import * as React from "react"
import * as LabelPrimitive from "@radix-ui/react-label"
import { cva } from "class-variance-authority"
import { cn } from "@/lib/utils"

const labelVariants = cva(
  "text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
)

const Label = React.forwardRef(({ className, ...props }, ref) => (
  <LabelPrimitive.Root
    ref={ref}
    className={cn(labelVariants(), className)}
    {...props}
  />
))
Label.displayName = LabelPrimitive.Root.displayName

export { Label }
```

### 4.5 Dialog Component

**File:** `C:\EhkoVaults\EhkoForge\5.0 Scripts\control_panel\src\components\ui\dialog.jsx`

**Source Reference:** `C:\EhkoVaults\ReCog\_ui\src\components\ui\dialog.jsx`

This is a complex component. Copy implementation from ReCog and adjust styling as needed.

### 4.6 Tabs Component

**File:** `C:\EhkoVaults\EhkoForge\5.0 Scripts\control_panel\src\components\ui\tabs.jsx`

**Source Reference:** `C:\EhkoVaults\ReCog\_ui\src\components\ui\tabs.jsx`

### 4.7 Select Component

**File:** `C:\EhkoVaults\EhkoForge\5.0 Scripts\control_panel\src\components\ui\select.jsx`

**Source Reference:** `C:\EhkoVaults\ReCog\_ui\src\components\ui\select.jsx`

### 4.8 Textarea Component

**File:** `C:\EhkoVaults\EhkoForge\5.0 Scripts\control_panel\src\components\ui\textarea.jsx`

```javascript
import * as React from "react"
import { cn } from "@/lib/utils"

const Textarea = React.forwardRef(({ className, ...props }, ref) => {
  return (
    <textarea
      className={cn(
        "flex min-h-[60px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50",
        className
      )}
      ref={ref}
      {...props}
    />
  )
})
Textarea.displayName = "Textarea"

export { Textarea }
```

### 4.9 Badge Component

**File:** `C:\EhkoVaults\EhkoForge\5.0 Scripts\control_panel\src\components\ui\badge.jsx`

**Source Reference:** `C:\EhkoVaults\ReCog\_ui\src\components\ui\badge.jsx`

### 4.10 Additional Components (Lower Priority)

Copy these from ReCog as needed:
- Checkbox
- Switch
- Tooltip
- Dropdown Menu
- Popover
- Toast/Sonner (if notifications needed)

---

## Phase 5: Theme Enhancement

### 5.1 Update index.css

**File:** `C:\EhkoVaults\EhkoForge\5.0 Scripts\control_panel\src\index.css`

Keep existing EhkoForge terminal theme but enhance with additional utilities:

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    /* EhkoForge Terminal Theme - Blue */
    --background: 222 47% 11%;        /* #0f1419 - Dark navy */
    --foreground: 210 40% 98%;        /* #fafafa - Off-white */
    
    --card: 222 40% 13%;              /* Slightly lighter than background */
    --card-foreground: 210 40% 98%;
    
    --popover: 222 47% 11%;
    --popover-foreground: 210 40% 98%;
    
    --primary: 214 70% 60%;           /* #6b8cce - Terminal blue */
    --primary-foreground: 222 47% 11%;
    
    --secondary: 217 32% 17%;
    --secondary-foreground: 210 40% 98%;
    
    --muted: 217 32% 17%;
    --muted-foreground: 215 20% 65%;
    
    --accent: 217 32% 17%;
    --accent-foreground: 210 40% 98%;
    
    --destructive: 0 62% 30%;
    --destructive-foreground: 210 40% 98%;
    
    --border: 217 32% 17%;
    --input: 217 32% 17%;
    --ring: 214 70% 60%;
    
    --radius: 0.5rem;
    
    /* Status colors (EhkoForge specific) */
    --success: 142 71% 45%;
    --warning: 38 92% 50%;
    --error: 0 84% 60%;
    
    /* Mana colors (EhkoForge specific) */
    --mana-full: 214 70% 60%;         /* Terminal blue */
    --mana-low: 38 92% 50%;           /* Warning orange */
    --mana-empty: 0 62% 30%;          /* Destructive red */
  }
}

@layer base {
  * {
    @apply border-border;
  }
  body {
    @apply bg-background text-foreground font-sans;
    font-feature-settings: "rlig" 1, "calt" 1;
  }
}

@layer utilities {
  /* Terminal glow effects */
  .terminal-glow {
    box-shadow: 0 0 10px rgba(107, 140, 206, 0.3),
                0 0 20px rgba(107, 140, 206, 0.1);
  }
  
  .glow-blue {
    box-shadow: 0 0 8px rgba(107, 140, 206, 0.3);
  }
  
  .glow-cyan {
    box-shadow: 0 0 12px rgba(0, 255, 255, 0.4);
  }
  
  /* Status classes */
  .status-active {
    @apply text-[hsl(var(--success))];
  }
  
  .status-stopped {
    @apply text-muted-foreground;
  }
  
  .status-error {
    @apply text-[hsl(var(--error))];
  }
  
  /* Scrollbar styling */
  .scrollbar-thin::-webkit-scrollbar {
    width: 8px;
    height: 8px;
  }
  
  .scrollbar-thin::-webkit-scrollbar-track {
    background: hsl(var(--background));
  }
  
  .scrollbar-thin::-webkit-scrollbar-thumb {
    background: hsl(var(--muted));
    border-radius: 4px;
  }
  
  .scrollbar-thin::-webkit-scrollbar-thumb:hover {
    background: hsl(var(--muted-foreground));
  }
}

/* Legacy support - can be removed after migration */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  @apply bg-background;
}

::-webkit-scrollbar-thumb {
  @apply bg-muted rounded;
}

::-webkit-scrollbar-thumb:hover {
  @apply bg-muted-foreground;
}
```

---

## Phase 6: Component Migration Strategy

### 6.1 Audit Existing Components

**Directory:** `C:\EhkoVaults\EhkoForge\5.0 Scripts\control_panel\src\`

Current App.jsx likely has inline components. These need to be:
1. Identified
2. Refactored into separate files
3. Moved to appropriate directories

### 6.2 Migration Pattern

For each existing feature in App.jsx:

```
Old: All in App.jsx
New: 
  - UI primitives → components/ui/
  - Feature components → components/forge/
  - Page layouts → components/pages/
  - Utility functions → lib/
  - Custom hooks → hooks/
  - State management → contexts/
```

---

## Phase 7: Testing & Validation

### 7.1 Create Test Page

**File:** `C:\EhkoVaults\EhkoForge\5.0 Scripts\control_panel\src\components\pages\ComponentTest.jsx`

```javascript
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"

export function ComponentTest() {
  return (
    <div className="container mx-auto p-8 space-y-8">
      <h1 className="text-3xl font-bold">EhkoForge Component Test</h1>
      
      {/* Button variants */}
      <Card>
        <CardHeader>
          <CardTitle>Buttons</CardTitle>
          <CardDescription>All button variants and sizes</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-2 flex-wrap">
            <Button>Default</Button>
            <Button variant="destructive">Destructive</Button>
            <Button variant="outline">Outline</Button>
            <Button variant="secondary">Secondary</Button>
            <Button variant="ghost">Ghost</Button>
            <Button variant="link">Link</Button>
          </div>
          <div className="flex gap-2 flex-wrap">
            <Button size="sm">Small</Button>
            <Button size="default">Default</Button>
            <Button size="lg">Large</Button>
            <Button size="icon">I</Button>
          </div>
        </CardContent>
      </Card>
      
      {/* Form inputs */}
      <Card>
        <CardHeader>
          <CardTitle>Form Elements</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="email">Email</Label>
            <Input id="email" type="email" placeholder="ehko@ehkolabs.io" />
          </div>
        </CardContent>
      </Card>
      
      {/* Badges */}
      <Card>
        <CardHeader>
          <CardTitle>Badges</CardTitle>
        </CardHeader>
        <CardContent className="flex gap-2">
          <Badge>Default</Badge>
          <Badge variant="secondary">Secondary</Badge>
          <Badge variant="destructive">Destructive</Badge>
          <Badge variant="outline">Outline</Badge>
        </CardContent>
      </Card>
    </div>
  )
}
```

### 7.2 Add Test Route

Update App.jsx to include a test route/mode for viewing all components in isolation.

---

## Phase 8: Documentation

### 8.1 Create Component Documentation

**File:** `C:\EhkoVaults\EhkoForge\5.0 Scripts\control_panel\COMPONENTS.md`

```markdown
# EhkoForge Component Library

This document catalogs all UI components available in the EhkoForge control panel.

## Base Components (shadcn/ui)

Located in `src/components/ui/`

### Button
- **Variants:** default, destructive, outline, secondary, ghost, link
- **Sizes:** default, sm, lg, icon
- **Usage:** `<Button variant="default" size="lg">Click me</Button>`

### Card
- **Sub-components:** Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter
- **Usage:** Wrap content in semantic card layout

[... continue for each component ...]

## Feature Components

Located in `src/components/forge/`

[Document EhkoForge-specific components as they're created]

## Styling Guidelines

- Use terminal-themed colors (blue primary, dark backgrounds)
- Apply `.terminal-glow` for emphasis effects
- Use `.status-*` classes for state indication
- Prefer composition over prop-drilling
```

### 8.2 Update README

**File:** `C:\EhkoVaults\EhkoForge\5.0 Scripts\control_panel\README.md`

Add sections for:
- Component library overview
- Directory structure explanation
- Development workflow
- Testing components
- Adding new components

---

## Phase 9: Backend Integration Points

### 9.1 API Integration Pattern

Create a standardized API client:

**File:** `C:\EhkoVaults\EhkoForge\5.0 Scripts\control_panel\src\lib\api.js`

```javascript
const API_BASE = 'http://localhost:5000'

export class ForgeAPI {
  static async fetch(endpoint, options = {}) {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    })
    
    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`)
    }
    
    return response.json()
  }
  
  // Mana endpoints
  static async getManaStatus() {
    return this.fetch('/api/mana/status')
  }
  
  static async purchaseMana(amount) {
    return this.fetch('/api/mana/purchase', {
      method: 'POST',
      body: JSON.stringify({ amount }),
    })
  }
  
  // Tether endpoints
  static async getTethers() {
    return this.fetch('/api/tethers')
  }
  
  static async createTether(data) {
    return this.fetch('/api/tethers', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }
  
  // Add more as needed...
}
```

### 9.2 React Query Setup (Optional but Recommended)

If data fetching becomes complex, consider adding React Query:

```bash
npm install @tanstack/react-query
```

---

## Phase 10: Gradual Migration

### 10.1 Migration Checklist

Don't rewrite everything at once. Migrate incrementally:

- [ ] Set up infrastructure (deps, config, structure)
- [ ] Create core UI components
- [ ] Create test page to validate components
- [ ] Identify one feature to migrate first (e.g., Mana Bar)
- [ ] Refactor that feature using new components
- [ ] Test thoroughly
- [ ] Repeat for next feature

### 10.2 Preserve Existing Functionality

**CRITICAL:** Don't break working features during migration.

- Keep old components until new ones are verified
- Use feature flags if needed
- Test each migration thoroughly
- Git commit after each successful migration

---

## Execution Order

**For Claude Code to execute:**

```bash
# 1. Navigate to control panel
cd "C:\EhkoVaults\EhkoForge\5.0 Scripts\control_panel"

# 2. Install all dependencies (Phase 1.1)
npm install @radix-ui/react-dialog @radix-ui/react-label @radix-ui/react-select @radix-ui/react-slot @radix-ui/react-tabs @radix-ui/react-checkbox @radix-ui/react-switch @radix-ui/react-tooltip @radix-ui/react-dropdown-menu @radix-ui/react-popover tailwindcss-animate

# 3. Create directory structure (Phase 2.1)
mkdir src\components\ui
mkdir src\components\forge
mkdir src\components\pages
mkdir src\lib
mkdir src\hooks
mkdir src\contexts

# 4. Create configuration files (Phase 1.2-1.4)
# - components.json
# - Update vite.config.js
# - Update tailwind.config.js

# 5. Create utils (Phase 3.1)
# - src/lib/utils.js

# 6. Create UI components in priority order (Phase 4)
# - Start with Button, Card, Input, Label
# - Then Dialog, Tabs, Select
# - Then Badge, Textarea
# - Then remaining components as needed

# 7. Update theme (Phase 5.1)
# - Enhance index.css

# 8. Create test page (Phase 7.1)
# - src/components/pages/ComponentTest.jsx

# 9. Create documentation (Phase 8)
# - COMPONENTS.md
# - Update README.md

# 10. Create API client (Phase 9.1)
# - src/lib/api.js

# 11. Test everything
npm run dev
# Navigate to test page and verify all components work

# 12. Git commit
git add .
git commit -m "Frontend modernization: shadcn/ui integration and component library"
```

---

## Success Criteria

✅ All dependencies installed  
✅ Directory structure organized  
✅ components.json created  
✅ Path aliases working (@/ imports)  
✅ Core UI components created (Button, Card, Input, Label, Dialog, Tabs, Select, Badge, Textarea)  
✅ Utility functions in place (cn)  
✅ Theme enhanced with proper CSS variables  
✅ Test page showing all components  
✅ Documentation created  
✅ API client pattern established  
✅ Dev server runs without errors  
✅ Components match terminal aesthetic  
✅ No TypeScript errors (if using TS)  
✅ Git commit made  

---

## Reference Files

**ReCog Implementation (Gold Standard):**
- `C:\EhkoVaults\ReCog\_ui\package.json` - Dependencies reference
- `C:\EhkoVaults\ReCog\_ui\components.json` - Config reference
- `C:\EhkoVaults\ReCog\_ui\tailwind.config.js` - Tailwind setup
- `C:\EhkoVaults\ReCog\_ui\src\index.css` - Theme reference
- `C:\EhkoVaults\ReCog\_ui\src\components\ui\*` - Component implementations

**EhkoForge Current State:**
- `C:\EhkoVaults\EhkoForge\5.0 Scripts\control_panel\package.json`
- `C:\EhkoVaults\EhkoForge\5.0 Scripts\control_panel\src\index.css`
- `C:\EhkoVaults\EhkoForge\PROJECT_STATUS.md`

---

## Notes for Claude Code

1. **Respect existing theme:** EhkoForge uses blue as primary (not orange like ReCog)
2. **Don't break existing features:** Migrate incrementally
3. **Test each component:** Create test page first, validate each component works
4. **Follow ReCog patterns:** But adapt for EhkoForge context
5. **Git commit frequently:** After each successful phase
6. **Update PROJECT_STATUS.md:** When complete, document the upgrade

---

## Post-Upgrade Tasks

After this upgrade is complete, Brent will:
- Review component library
- Test integration with existing features
- Plan next development phase
- Potentially create EhkoForge-specific components (ManaBar, TetherPanel, etc.)
- Continue development with modern component patterns

---

**Created:** 2026-01-10  
**For:** Claude Code CLI  
**Context:** Pre-continuation modernization bringing EhkoForge up to ReCog standards  
**Estimated Time:** 2-4 hours for complete execution

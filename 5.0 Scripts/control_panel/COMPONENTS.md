# EhkoForge Component Library

This document catalogs all UI components available in the EhkoForge control panel.

## Overview

EhkoForge uses [shadcn/ui](https://ui.shadcn.com/) components built on [Radix UI](https://www.radix-ui.com/) primitives, styled with the EhkoForge terminal theme (blue primary).

## Directory Structure

```
src/
├── components/
│   ├── ui/              # shadcn/ui components (Button, Card, Dialog, etc.)
│   ├── forge/           # EhkoForge-specific components
│   └── pages/           # Page-level components
├── lib/
│   ├── utils.js         # Utility functions (cn)
│   └── api.js           # API client
├── hooks/               # Custom React hooks
└── contexts/            # React contexts
```

## Base Components (shadcn/ui)

Located in `src/components/ui/`

### Button

Clickable button with multiple variants and sizes.

**Variants:** `default`, `destructive`, `outline`, `secondary`, `ghost`, `link`
**Sizes:** `default`, `sm`, `lg`, `icon`

```jsx
import { Button } from "@/components/ui/button"

<Button variant="default" size="lg">Click me</Button>
<Button variant="destructive">Delete</Button>
<Button variant="outline">Cancel</Button>
```

### Card

Container component for grouping related content.

**Sub-components:** `Card`, `CardHeader`, `CardTitle`, `CardDescription`, `CardContent`, `CardFooter`

```jsx
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

<Card className="terminal-glow">
  <CardHeader>
    <CardTitle>Server Status</CardTitle>
  </CardHeader>
  <CardContent>
    <p>Content here</p>
  </CardContent>
</Card>
```

### Input

Text input field.

```jsx
import { Input } from "@/components/ui/input"

<Input type="email" placeholder="Enter email" />
```

### Label

Form label with proper accessibility.

```jsx
import { Label } from "@/components/ui/label"

<Label htmlFor="email">Email</Label>
```

### Textarea

Multi-line text input.

```jsx
import { Textarea } from "@/components/ui/textarea"

<Textarea placeholder="Enter message..." />
```

### Select

Dropdown select component.

```jsx
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

<Select>
  <SelectTrigger>
    <SelectValue placeholder="Select..." />
  </SelectTrigger>
  <SelectContent>
    <SelectItem value="option1">Option 1</SelectItem>
    <SelectItem value="option2">Option 2</SelectItem>
  </SelectContent>
</Select>
```

### Dialog

Modal dialog for confirmations and forms.

```jsx
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"

<Dialog>
  <DialogTrigger asChild>
    <Button>Open Dialog</Button>
  </DialogTrigger>
  <DialogContent>
    <DialogHeader>
      <DialogTitle>Dialog Title</DialogTitle>
    </DialogHeader>
    <p>Dialog content</p>
  </DialogContent>
</Dialog>
```

### Tabs

Tabbed interface for switching between views.

```jsx
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

<Tabs defaultValue="tab1">
  <TabsList>
    <TabsTrigger value="tab1">Tab 1</TabsTrigger>
    <TabsTrigger value="tab2">Tab 2</TabsTrigger>
  </TabsList>
  <TabsContent value="tab1">Content 1</TabsContent>
  <TabsContent value="tab2">Content 2</TabsContent>
</Tabs>
```

### Badge

Small status or label indicators.

**Variants:** `default`, `secondary`, `destructive`, `outline`

```jsx
import { Badge } from "@/components/ui/badge"

<Badge>Active</Badge>
<Badge variant="destructive">Error</Badge>
```

## Styling Guidelines

### Theme Colors

EhkoForge uses a dark terminal theme with blue as the primary color:

- **Primary:** `hsl(214 70% 60%)` - Terminal blue (#6b8cce)
- **Background:** `hsl(222 47% 11%)` - Dark navy
- **Destructive:** `hsl(0 62% 30%)` - Red

### Status Classes

Use these classes for status indicators:

```jsx
<span className="status-active">● Active</span>    // Green
<span className="status-stopped">○ Stopped</span>  // Muted
<span className="status-error">● Error</span>      // Red
```

### Terminal Glow

Apply the terminal glow effect to important cards:

```jsx
<Card className="terminal-glow">
  {/* Card glows with blue aura */}
</Card>
```

## API Client

Located in `src/lib/api.js`

```jsx
import { ForgeAPI } from "@/lib/api"

// Get server status
const status = await ForgeAPI.getStatus()

// Start/stop servers
await ForgeAPI.startServer('forge')
await ForgeAPI.stopServer('recog')

// Git operations
await ForgeAPI.gitCommit('commit message')
await ForgeAPI.gitPush()
```

## Test Page

View all components at `/test` by importing `ComponentTest`:

```jsx
import ComponentTest from "@/components/pages/ComponentTest"
```

## Adding New Components

1. Create component in `src/components/ui/` (for base UI)
2. Use `cn()` utility for className merging
3. Follow Radix UI patterns for primitives
4. Match existing styling conventions
5. Update this documentation

## Dependencies

- `@radix-ui/*` - UI primitives
- `class-variance-authority` - Variant management
- `clsx` + `tailwind-merge` - ClassName utilities
- `lucide-react` - Icons
- `tailwindcss-animate` - Animations

---

**Version:** 1.0.0
**Last Updated:** 2026-01-10

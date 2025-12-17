# EhkoForge.ai Website Development
*Complete documentation of website build - December 17, 2025*
*Moved from CareerForge vault - December 17, 2025*

## Project Overview

Complete static website for EhkoForge built with Astro, deployed to Cloudflare Pages. Full MDV (Monochrome Display Vibes) aesthetic with comprehensive content across landing, features, philosophy, download, blog, community, and documentation pages.

**Status:** Ready for deployment
**Timeline:** Completed in one session (Dec 17, 2025)
**Priority:** After EhkoLabs site (professional presence first)

---

## Architecture

### Tech Stack

- **Framework:** Astro 4.x (static site generation)
- **Styling:** Custom CSS (MDV Design System)
- **Hosting:** Cloudflare Pages
- **Deployment:** GitHub Actions (automated)
- **Version Control:** Git + GitHub

### Domain Strategy

**Primary:** ehkoforge.ai
- Main product website
- All features, docs, downloads, blog

**Redirect:** ehkoforge.com → ehkoforge.ai
- Defensive registration
- 301 permanent redirect
- Prevents domain squatting

**Rationale:** .ai extension signals AI-augmented nature honestly. Single product domain prevents SEO split and user confusion.

---

## Design System

### MDV Aesthetic

**Philosophy:** Retro CRT monitor interface = durability metaphor
- Software built to last 200 years
- Timeless design that doesn't chase trends
- Readable, accessible, distinctive

**Color Palette:**
```css
--phosphor-green: #33ff33    /* Primary text, accents */
--phosphor-amber: #ffb000    /* Highlights, CTAs */
--phosphor-dim: #1a4d1a      /* Borders, inactive */
--screen-black: #0a0a0a      /* Background */
--terminal-gray: #0f0f0f     /* Cards, elevated surfaces */
--glow-green: rgba(51, 255, 51, 0.3)
--glow-amber: rgba(255, 176, 0, 0.3)
```

**Typography:**
- **Display:** Space Mono (monospace, retro)
- **Body:** IBM Plex Mono (readable monospace)
- **Code:** IBM Plex Mono

**Visual Effects:**
- Scanlines overlay (CRT aesthetic)
- Phosphor glow on text
- Screen curvature (border-radius)
- Subtle flicker animation
- Terminal-style components

---

## Site Structure

### Pages Built

1. **Landing Page** - Hero, value props, features, CTAs
2. **Features Page** - Mirrorwell, ReCog, export-first, witness architecture, ADHD support
3. **Philosophy Page** - Witness, AGPLv3, data sovereignty, honest AI, 200-year thinking
4. **Download Page** - Installation for Windows/macOS/Linux, quick start, troubleshooting
5. **Blog System** - 2 complete articles, index page, layout system
6. **Community Page** - Contribution paths, code of conduct, recognition, resources
7. **Docs Framework** - Framework + Installation + Quick Start (others TBD)

### Component Library (13 Components)

**Layout:** Header.astro, Footer.astro, BaseLayout, BlogLayout, DocsLayout
**MDV:** CRTScreen, TerminalButton, TerminalCard, CodeBlock
**UI:** Logo, ScanlineOverlay, Hero, Features, Philosophy, CTA

---

## Blog Content (Production-Ready)

1. **"Why I'm Building EhkoForge"** (8-10 min)
2. **"The Witness Architecture"** (8-10 min)

---

## Deployment

See `EhkoForge-Website-QuickRef.md` for deployment steps.

**Total deployment time:** ~1 hour
**Ongoing maintenance:** ~2 hours/month

---

## Full Documentation

The original comprehensive documentation (35+ files, complete implementation details) is preserved in the CareerForge session transcript and can be regenerated on demand.

Key specifications:
- All component code ready
- All page content written
- Deployment configs created
- Blog posts production-ready

---

*This is a condensed reference. Full implementation details available on request.*

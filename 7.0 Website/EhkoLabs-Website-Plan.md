# EhkoLabs.io Website Plan
*Professional presence site - December 17, 2025*

---

## Purpose

EhkoLabs is the main brand for Brent's professional work. It serves as:
- **Professional legitimacy** - A credible presence for consulting work
- **Portfolio showcase** - Demonstrating capabilities and projects
- **Central hub** - Linking to EhkoForge and other projects

**Priority:** Build this BEFORE EhkoForge.ai

---

## Domain Strategy

**Primary:** ehkolabs.io (or ehkolabs.ai?)
- .io signals tech/developer focus
- .ai signals AI expertise

**Decision needed:** Which TLD?
- ehkolabs.io - More traditional tech portfolio vibe
- ehkolabs.ai - Emphasises AI specialisation

**Redirect (if both registered):** .io ↔ .ai (either direction based on choice)

---

## Site Structure

### Pages (4-5 pages, lean)

#### 1. Home (index)
**Purpose:** First impression, establish credibility

**Content:**
- Hero with professional positioning
- Brief intro: "AI systems architect and developer"
- Key projects (cards linking to Portfolio)
- CTA to Contact

**Tone:** Professional but human, not corporate

#### 2. About
**Purpose:** Who is Brent, what does he do

**Content:**
- Background (keep brief, not a biography)
- Technical focus areas
- Philosophy on building software
- Link to EhkoForge (personal project showcase)

**Avoid:** Over-sharing, imposter syndrome hedging

#### 3. Portfolio / Projects
**Purpose:** Demonstrate capability

**Content:**
- **EhkoForge** - Flagship personal project, link to ehkoforge.ai
- **ReCog** - Recognition engine, potential enterprise offering
- **Other projects** - As relevant
- Each with: Brief description, tech stack, outcomes

**Format:** Cards with images, expandable details

#### 4. Services (optional - maybe combine with About)
**Purpose:** What can clients engage for

**Content:**
- AI systems architecture
- LLM integration consulting
- Technical prototyping
- Training/workshops (if offering)

**Keep vague until specific offerings are clear**

#### 5. Contact
**Purpose:** Enable enquiries

**Content:**
- Contact form (or mailto link)
- LinkedIn
- GitHub
- Location (Melbourne, AU) - for local work signals

**No:** Public calendar booking (too presumptuous at start)

---

## Design System

### MDV Variant

**Same family, different tone:**
- EhkoForge = phosphor green (product)
- EhkoLabs = phosphor amber/bronze (professional)

**Color Palette:**
```css
--phosphor-amber: #ffb000     /* Primary text, accents */
--phosphor-bronze: #cd7f32    /* Secondary, CTAs */
--phosphor-dim: #4d3800       /* Borders, inactive */
--screen-black: #0a0a0a       /* Background */
--terminal-gray: #0f0f0f      /* Cards, elevated surfaces */
```

**Typography:** Same as EhkoForge (Space Mono, IBM Plex Mono)

**Visual Effects:** Same (scanlines, glow, CRT borders) but amber instead of green

**Result:** Clearly related to EhkoForge but distinct, more "professional warmth"

---

## Technical Stack

**Same as EhkoForge site:**
- Framework: Astro 4.x
- Hosting: Cloudflare Pages (free tier)
- Deployment: GitHub Actions
- SSL: Cloudflare (automatic)

**Cost:** $0/month (domain only ~$10-15/year)

---

## Content Requirements

### Needed from Brent:

1. **Headshot** - Professional photo (optional but helpful)
2. **Bio copy** - 2-3 paragraph professional summary
3. **Project descriptions** - Brief writeups for portfolio items
4. **Service offerings** - What consulting work is available
5. **Contact preferences** - Email, form, or both

### Can be generated/adapted:
- Page layouts (from MDV components)
- Design implementation
- Deployment config
- Copy refinement

---

## Timeline Estimate

**If content ready:**
- Day 1: Set up repo, implement pages, deploy
- Day 2: Content refinement, testing
- Day 3: Launch

**Total:** 2-3 days focused work (or 1 session if pre-compacted)

---

## Relation to EhkoForge Site

| Aspect | EhkoLabs | EhkoForge |
|--------|----------|-----------|
| Purpose | Professional portfolio | Product site |
| Tone | Consulting/services | Open source project |
| Primary color | Amber/bronze | Green |
| Content | About me, portfolio | Features, docs, downloads |
| Priority | **First** | Second |

**Cross-linking:**
- EhkoLabs → EhkoForge (project showcase)
- EhkoForge → EhkoLabs (creator credit)

---

## Open Questions

1. **Domain:** ehkolabs.io or ehkolabs.ai?
2. **Services page:** Include now or add later?
3. **Blog:** On EhkoLabs, EhkoForge, or both?
4. **Analytics:** Cloudflare Web Analytics (same as EhkoForge)?

---

## Next Steps

1. [ ] Decide domain TLD
2. [ ] Register domain
3. [ ] Provide bio/content
4. [ ] Build site (1 session)
5. [ ] Deploy
6. [ ] Then proceed to EhkoForge.ai

---

*Ready to build when you are.*

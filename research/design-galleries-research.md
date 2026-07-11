# Design Galleries Research — Premium Dark-Themed Patterns for Business Directory Detail Page

**Purpose:** Actionable design inspiration for revamping the business directory detail page on The Videshi News (Indian diaspora news site, dark theme) to feel "modern and posh" — genuinely premium, not generic dark mode.

**Research sources:** Godly/Recent.design, SiteInspire, Land-book.com
**Sites studied:** 7 premium dark-themed and luxury sites

---

## Table of Contents

1. [Site-by-Site Analysis](#site-by-site-analysis)
2. [Cross-Cutting Design Patterns](#cross-cutting-design-patterns)
3. [Actionable Recommendations for Business Directory Detail Page](#actionable-recommendations)
4. [CSS Snippets & Token Reference](#css-snippets--token-reference)

---

## Site-by-Site Analysis

### 1. Aave (aave.com) — via Recent.design

**Category:** DeFi / Finance dark-themed product site
**Why it's relevant:** Shows how to present structured product/service info with cards, stats, and FAQ on a dark background.

**Color Palette:**
- Background: `#0f0f10`, `#111113` (near-black with cool undertone)
- Accent: Purple/violet spectrum — `#8579FD`, `#8075FF`, `#6446A8`, `#B3B0FD`, `#9C93FC`
- Text primary: `#fff`, `#f6f7f4`
- Text secondary: muted grays

**Typography:**
- Font stack: Inter Variable (body), Aave Repro (brand), FT Regola Neue (display)
- Mix of geometric sans-serif for headings + neutral sans for body

**Surface Treatment:**
- Cards: `border: 1px solid var(--border-p-2)` — very subtle purple-tinted borders
- `border-radius: 24px, 32px` for cards; `50%` for avatars
- Modern squircle corners: `corner-shape: superellipse(1.25)` — cutting-edge CSS
- Gradient overlays mixing purple tones on dark backgrounds
- No harsh shadows — separation by subtle border + slight background shifts

**Key Patterns:**
- Partner/integration logos displayed in a horizontal strip
- Statistics section with large animated counters
- FAQ accordion with clean expand/collapse
- Product feature cards in grid layout
- Generous padding: `80px 0` on section level

**What makes it premium:** The purple accent on near-black creates a moody, sophisticated depth. Squircle borders feel refined. Zero visual clutter — every element breathes.

---

### 2. Topology (topology.vc) — via Recent.design

**Category:** VC / Investment firm dark-themed portfolio
**Why it's relevant:** Ultra-minimal dark approach to presenting people/entity profiles — directly applicable to business directory.

**Color Palette:**
- Background: `#020202` (true near-black)
- Primary text: `#E4E2D8` (warm cream — NOT pure white)
- Accent: pure white for emphasis
- Overlays: `rgba(0,0,0,0.85)`, `rgba(0,0,0,0.7)`

**Typography:**
- All-caps navigation/labels (ABOUT, PRINCIPLES, TEAM)
- Clean sans-serif throughout
- Strong hierarchy through weight and size, not color

**Surface Treatment:**
- Near-zero visible UI chrome — no borders, no cards, no boxes
- Separation achieved purely through whitespace and typography
- Team profiles: photo + name + social links, minimal grid

**Key Patterns:**
- Single-page layout with anchor navigation
- Team profiles with circular photos and social icons
- Principles/values displayed as numbered list items
- Animated logo element as hero

**What makes it premium:** Radical restraint. The warm cream (#E4E2D8) on near-black avoids the stark/cold feel of white-on-black. Whitespace IS the design.

---

### 3. The OWO (theowo.london) — via SiteInspire (Luxury filter)

**Category:** Luxury London property/hotel
**Why it's relevant:** Shows how high-end real estate/hospitality presents detail pages — tone directly transferable to premium business listings.

**Color Palette:**
- Background: `#ddd9d3` (warm stone gray) — note: light-on-dark sections alternate
- Near-black: `#141414`
- Accent: `#A2A19C` (muted sage)
- Warm neutrals throughout

**Typography:**
- Serif headings ("AN ICON REBORN") paired with sans-serif body
- `letter-spacing: 0.06em` used extensively — **this is the single most impactful luxury signal**
- All-caps navigation and labels
- Restrained font sizes — elegance, not shouting

**Surface Treatment:**
- Full-bleed hero imagery
- No visible card borders — content floats on clean backgrounds
- Generous vertical padding between sections

**Key Patterns:**
- Full-width hero image → serif headline → body copy flow
- High-end imagery does the heavy lifting
- Muted, desaturated color palette signals sophistication

**What makes it premium:** Letter-spacing + serif + warm neutrals = instant luxury. The `0.06em` tracking on labels and nav items is the easiest single CSS change that elevates any dark theme.

---

### 4. Portman Properties (portmanproperties.com) — via SiteInspire (Luxury filter)

**Category:** Luxury real estate agency
**Why it's relevant:** **Most directly applicable** — shows exactly how a property/business detail page should be laid out for a premium directory.

**Color Palette:**
- Background: `#F8F5F1` (warm cream)
- Accent: `#4fc8d1` (teal)
- Text: near-black

**Typography:**
- All-caps labels and navigation
- Serif + sans-serif mixing
- Letter-spacing on labels

**Detail Page Layout (the blueprint):**
1. **Hero:** Full-width image gallery (carousel with thumbnails)
2. **Title bar:** Property name + key details (price, location, size)
3. **Contact sidebar:** Phone number, email, WhatsApp — prominent CTA "ENQUIRE"
4. **Quick actions:** MAP / READ MORE / SHARE links
5. **Description:** Body text with expandable sections
6. **Related listings:** Horizontal carousel of similar properties below
7. **Agent card:** Small profile card with agent photo + contact

**Key Patterns:**
- Detail page uses two-column layout: main content left + contact sidebar right
- Contact info always visible/sticky
- Featured sales carousel below the detail section
- Breadcrumb navigation at top

**What makes it premium:** The structured hierarchy of information — image first, then identity, then action (contact), then detail, then related — is a proven luxury pattern.

---

### 5. 1inch (1inch.com) — via Land-book

**Category:** Crypto/DeFi dark-themed product landing
**Why it's relevant:** Comprehensive dark design system with extensive CSS custom properties — a complete reference for building a design token system.

**Color Palette (dark theme tokens):**
- Page background: `--greyGrey890: #0F0F12`
- Surface subtle: `--greyGrey880: #141417`
- Card background: `--greyGrey870: #19191C`
- Elevated surface: `--greyGrey865: #212124`
- Border/divider: `--greyGrey860: #27272B`, `--greyGrey850: #2E2E30`
- Text primary: `--whiteWhiteA1: #FFFFFF`
- Text secondary: various white alpha values (`#FFFFFFC2`, `#FFFFFF99`, `#FFFFFF66`)
- Brand blue: `--coloredBlueBrand: #0000FE`
- Brand accent green: `--coloredGreenBrand: #4FF01F`
- Brand cyan: `--coloredMintBrand: #09F9F9`
- Status green: `#25AF3B`
- Status red: `#FF2929`
- Warning orange: `#F97000`

**Typography:**
- Font sizes: Display L `72px` → Display M `60px` → Headline L `32px` → Headline M `24px` → Headline S `20px` → Body L `18px` → Body M `16px` → Body S `14px` → Caption L `12px`
- System sans-serif stack
- Separate font-family tokens: `--fontFamilyTitle`, `--fontFamilyText`, `--fontFamilyButton`, `--fontFamilySpecial`

**Surface Treatment:**
- Cards: `border-radius: 28px, 24px`
- Circular elements: `border-radius: 50%`
- Pill buttons: `border-radius: 100px`
- Backdrop blur: `backdrop-filter: blur(25px)` for floating nav
- System overlay: `var(--systemOverlay)` for modals/dropdowns
- Subtle white alpha borders: `--whiteWhiteA012: #FFFFFF1F` (barely visible)

**Key Patterns:**
- Token swap cards as interactive widgets
- Network chain badges in a horizontal scrollable strip
- Statistics section with large numbers
- Ecosystem product cards (Wallet, Portfolio, Card, Business) in a grid
- FAQ accordion with "Show more" button
- CTA banner at bottom with strong call to action
- Footer organized in collapsible sections

**Spacing System:**
- Section padding: `80px 0`
- Card padding: `32px`, `24px`
- Component gap: `40px`, `20px`, `16px`, `8px`, `4px`
- Button padding: `12px 24px` (primary), `8px 16px` (secondary)

**What makes it premium:** The layered gray system (5+ distinct dark grays from `#0F0F12` to `#2E2E30`) creates subtle depth without borders or shadows. Each surface level is just one notch lighter than its parent.

---

### 6. Linear (linear.app) — via Land-book (bonus benchmark)

**Category:** Product development tool — the gold standard of dark UI
**Why it's relevant:** Linear is widely considered THE benchmark for premium dark-themed product design. Its homepage demonstrates how to present a professional tool with sophistication.

**Color Palette:**
- Background: `#000` (pure black — unusual, most sites avoid this)
- Normal surface (light mode): `#fff`
- Shine/highlight: `#383b3f`
- Text secondary: `#9c9da1`
- Text tertiary: `#585a5c`
- Accent purple: `#6366F1`, `#8B5CF6`
- Accent cyan: `#02B8CC`
- Status colors: red `#EB5757`, green `#27A644`, `#10B981`, cyan `#06B6D4`
- Yellow highlight: `#e4f222`

**Typography:**
- System font stack: `ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica Neue, Arial`
- No custom fonts — relies on system fonts for performance and clean rendering
- Monospace for code: code blocks with syntax highlighting tokens

**Surface Treatment:**
- Very small border-radius: `4px`, `6px`, `8px` — tighter, more utilitarian
- `border-radius: 50%` for avatars only
- Subtle box shadows: `box-shadow: 0 4px 12px rgba(0,0,0,.1), 0 0 0 2px rgba(0,0,0,.2)` — double shadow (spread + blur) for depth
- Gradient accents: `linear-gradient(180deg, #b2d5ff 0%, #dfd1ff 100%)` — blue-to-purple wash

**Key Patterns:**
- Interactive product demo as hero (not just a screenshot — the actual UI)
- Company logos in a horizontal strip (Vercel, Cursor, OpenAI, Coinbase, etc.)
- Feature sections with embedded product UI screenshots
- Numbered section labels ("1.0 Intake", "2.0 Plan", "3.0 Build")
- Clean, functional navigation with Product/Resources dropdowns

**What makes it premium:** Functional elegance. No decoration for decoration's sake. The hero IS the product. Small border-radius (4-8px) communicates "tool" vs the rounded 24-32px that communicates "friendly." The pure black background is bold but works because they earn it with exceptional whitespace management.

---

### 7. Topology — Additional Profile Pattern Detail

The team profile section is the closest pattern to a business directory listing:
- Circular photo (200px+)
- Name in medium weight
- Role/description in lighter weight
- Social links as small icons below
- Grid layout: 3-4 profiles per row with generous gaps
- Hover: no dramatic effect, just subtle opacity or underline on links

---

## Cross-Cutting Design Patterns

### Color: The Dark Hierarchy

The most successful dark themes use a **layered gray system**, not just "black background + white text":

| Layer | Purpose | Hex Range | Example |
|-------|---------|-----------|---------|
| Base | Page background | `#000000` – `#0F0F12` | Linear uses `#000`, most others `#0f0f10` to `#0F0F12` |
| Surface 1 | Card/section bg | `#111113` – `#141417` | One step up from base |
| Surface 2 | Elevated cards | `#19191C` – `#212124` | Modals, dropdowns, hover states |
| Surface 3 | Interactive elements | `#27272B` – `#2E2E30` | Buttons, inputs, active states |
| Border | Dividers/outlines | `#2E2E30` – `#353538` | Barely visible, used sparingly |
| Text secondary | Labels, captions | `#9c9da1` – `#FFFFFF99` | NOT gray — use white with alpha |
| Text primary | Headlines, body | `#E4E2D8` – `#FFFFFF` | Warm cream OR pure white |
| Accent | Brand color | Site-specific | Purple, teal, gold, blue |

**Critical insight:** The best dark themes use **5-6 shades of near-black** to create depth, NOT borders or shadows. Each nested container is one shade lighter than its parent.

### Text: Warm Cream vs Pure White

- **Warm cream** (`#E4E2D8`, `#F6F7F4`, `#F8F5F1`): Used by luxury and editorial sites. Feels softer, more sophisticated, less "screen-y." **Recommended for The Videshi News.**
- **Pure white** (`#FFFFFF`): Used by tech/product sites (Linear, 1inch). Feels sharper, more utilitarian.
- **White with alpha** (`#FFFFFFC2`, `#FFFFFF99`): Better than gray for secondary text on dark backgrounds — maintains the warmth.

### Typography: The Luxury Toolkit

1. **Letter-spacing `0.06em`** on labels, nav items, category tags, all-caps text — the #1 most impactful change
2. **Serif for headings** + sans-serif for body — instant editorial/luxury feel
3. **All-caps for labels** (CATEGORY, STATUS, TYPE) with extra tracking
4. **System sans-serif** for body is fine — don't over-custom-font
5. **Font size hierarchy:** Display 40-72px → Heading 20-32px → Body 14-18px → Caption 10-12px

### Cards & Surfaces

| Pattern | CSS | Used By | Feel |
|---------|-----|---------|------|
| Rounded cards | `border-radius: 24-32px` | Aave, 1inch | Friendly, modern |
| Tight cards | `border-radius: 4-8px` | Linear | Utilitarian, professional |
| Squircle | `corner-shape: superellipse(1.25)` | Aave | Cutting-edge, Apple-like |
| Ghost border | `border: 1px solid rgba(255,255,255,0.08)` | Most sites | Minimal separation |
| Elevation by shade | Background one notch lighter | 1inch, Linear | No-border depth |
| Blur overlay | `backdrop-filter: blur(25px)` | 1inch nav | Glassmorphism |

### Spacing & Whitespace

Premium sites use dramatically more whitespace than typical sites:
- **Section padding:** `80px 0` minimum, often `112px` or more
- **Card padding:** `24px` to `40px` internal
- **Grid gap:** `20px` to `40px` between cards
- **Button padding:** `12px 24px` for primary CTAs
- **Between text blocks:** `20px` to `40px`

### Hover Effects & Micro-interactions

- **Subtle opacity shifts:** `opacity: 0.8` → `1.0` on hover (Topology)
- **Border glow:** `border-color` transitions from transparent to accent on hover (Aave)
- **Background shift:** card background one shade lighter on hover
- **Scale:** `transform: scale(1.02)` with `transition: 0.3s ease` (card hover)
- **Link underlines:** appear on hover, never static
- **Accordion:** smooth height transition with `transition: max-height 0.3s ease`

---

## Actionable Recommendations for Business Directory Detail Page

### Recommended Layout (Based on Portman Properties + Topology patterns)

```
┌──────────────────────────────────────────────────────────────────┐
│  Breadcrumb: Home > Directory > Category > Business Name         │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                   HERO IMAGE / GALLERY                       │ │
│  │              (full-width, 16:9 or 3:2 ratio)                │ │
│  │         carousel dots at bottom, rounded corners 16px       │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌───────────────────────────────┐  ┌─────────────────────────┐ │
│  │                               │  │   CONTACT CARD          │ │
│  │  BUSINESS NAME (serif, 32px)  │  │   (sticky sidebar)      │ │
│  │  CATEGORY (all-caps, 0.06em) │  │                         │ │
│  │  ★★★★☆  4.8 (123 reviews)    │  │   📞 Phone              │ │
│  │  📍 Location                  │  │   📧 Email              │ │
│  │                               │  │   🌐 Website            │ │
│  │  ─────────────────────────    │  │   📱 WhatsApp           │ │
│  │                               │  │                         │ │
│  │  ABOUT (serif heading)        │  │   [ ENQUIRE NOW ]       │ │
│  │  Description body text...     │  │   (primary CTA, accent) │ │
│  │                               │  │                         │ │
│  │  SERVICES                     │  │   HOURS                 │ │
│  │  • Service tags in pills      │  │   Mon-Fri: 9am-6pm     │ │
│  │                               │  │   Sat: 10am-4pm        │ │
│  │  DETAILS                      │  │                         │ │
│  │  Key-value pairs              │  │   📍 MAP                │ │
│  │                               │  │   (embedded mini-map)   │ │
│  └───────────────────────────────┘  └─────────────────────────┘ │
│                                                                  │
│  ─────────────────────────────────────────────────────────────── │
│                                                                  │
│  REVIEWS (section heading, serif)                                │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐                        │
│  │ Review 1 │ │ Review 2 │ │ Review 3 │  ← horizontal scroll   │
│  └──────────┘ └──────────┘ └──────────┘                        │
│                                                                  │
│  ─────────────────────────────────────────────────────────────── │
│                                                                  │
│  SIMILAR BUSINESSES (carousel)                                   │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│  │ Listing  │ │ Listing  │ │ Listing  │ │ Listing  │  →       │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘          │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### Specific CSS Recommendations

#### 1. Background & Surface System
```css
:root {
  /* Base layers — use these instead of flat #000 */
  --bg-base: #0c0c0f;          /* deepest background */
  --bg-surface-1: #111114;      /* card/section background */
  --bg-surface-2: #18181c;      /* elevated cards, hover */
  --bg-surface-3: #222228;      /* interactive elements */
  --bg-surface-4: #2c2c34;      /* active states */

  /* Borders — barely visible, never heavy */
  --border-subtle: rgba(255, 255, 255, 0.06);
  --border-default: rgba(255, 255, 255, 0.10);
  --border-hover: rgba(255, 255, 255, 0.16);

  /* Text — use warm cream, not pure white */
  --text-primary: #E8E5DF;       /* warm cream for body */
  --text-heading: #F4F2EE;       /* slightly brighter for headings */
  --text-secondary: rgba(255, 255, 255, 0.60);
  --text-tertiary: rgba(255, 255, 255, 0.40);

  /* Accent — choose ONE. Gold/amber fits Indian diaspora well */
  --accent-primary: #D4A853;      /* warm gold */
  --accent-primary-hover: #E0BA6A;
  --accent-secondary: #8B7355;    /* muted bronze */

  /* Status */
  --status-success: #27A644;
  --status-warning: #F97000;
  --status-error: #FF4444;
}
```

#### 2. Typography
```css
:root {
  /* Serif for headings — pick ONE */
  --font-heading: 'Playfair Display', 'Georgia', serif;
  /* Or more modern: */
  /* --font-heading: 'DM Serif Display', 'Georgia', serif; */

  /* Sans for body — system stack is fine */
  --font-body: 'Inter', ui-sans-serif, system-ui, sans-serif;

  /* Size scale */
  --text-display: 2.5rem;     /* 40px — business name */
  --text-h2: 1.5rem;          /* 24px — section headings */
  --text-h3: 1.25rem;         /* 20px — sub-headings */
  --text-body: 1rem;          /* 16px — description */
  --text-small: 0.875rem;     /* 14px — metadata */
  --text-caption: 0.75rem;    /* 12px — labels */
}

/* THE luxury letter-spacing trick */
.label, .category-tag, .nav-item, .section-label {
  text-transform: uppercase;
  letter-spacing: 0.06em;
  font-size: var(--text-caption);
  color: var(--text-secondary);
  font-family: var(--font-body);
}

/* Headings: serif + warm cream */
h1, h2, h3 {
  font-family: var(--font-heading);
  color: var(--text-heading);
  font-weight: 400; /* light weight serif = luxury */
}
```

#### 3. Card & Surface Components
```css
/* Business listing card */
.business-card {
  background: var(--bg-surface-1);
  border: 1px solid var(--border-subtle);
  border-radius: 16px;
  padding: 24px;
  transition: background 0.3s ease, border-color 0.3s ease;
}

.business-card:hover {
  background: var(--bg-surface-2);
  border-color: var(--border-hover);
}

/* Contact sidebar card */
.contact-card {
  background: var(--bg-surface-1);
  border: 1px solid var(--border-default);
  border-radius: 16px;
  padding: 32px;
  position: sticky;
  top: 100px;
}

/* Service tag pills */
.service-tag {
  background: var(--bg-surface-2);
  border: 1px solid var(--border-subtle);
  border-radius: 100px;  /* full pill */
  padding: 6px 16px;
  font-size: var(--text-small);
  color: var(--text-secondary);
  letter-spacing: 0.02em;
}

/* Primary CTA button */
.cta-primary {
  background: var(--accent-primary);
  color: var(--bg-base);
  border: none;
  border-radius: 8px;
  padding: 14px 28px;
  font-size: var(--text-body);
  letter-spacing: 0.04em;
  text-transform: uppercase;
  font-weight: 500;
  transition: background 0.2s ease;
  width: 100%;
}

.cta-primary:hover {
  background: var(--accent-primary-hover);
}
```

#### 4. Spacing System
```css
:root {
  --space-xs: 4px;
  --space-sm: 8px;
  --space-md: 16px;
  --space-lg: 24px;
  --space-xl: 40px;
  --space-2xl: 64px;
  --space-3xl: 80px;    /* section padding */
  --space-4xl: 112px;   /* hero section */
}

/* Section spacing */
.section {
  padding: var(--space-3xl) 0;
}

/* Content max-width */
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 var(--space-lg);
}

/* Two-column detail layout */
.detail-layout {
  display: grid;
  grid-template-columns: 1fr 380px;
  gap: var(--space-xl);
  align-items: start;
}

@media (max-width: 1024px) {
  .detail-layout {
    grid-template-columns: 1fr;
  }
}
```

#### 5. Dividers & Separation
```css
/* Use faint horizontal rules instead of card borders */
.section-divider {
  border: none;
  border-top: 1px solid var(--border-subtle);
  margin: var(--space-xl) 0;
}

/* OR use spacing only (the luxury way) */
/* No borders at all — just 64-80px between sections */
```

#### 6. Image Gallery Hero
```css
.hero-gallery {
  border-radius: 16px;
  overflow: hidden;
  aspect-ratio: 16 / 9;
  background: var(--bg-surface-1);
}

.hero-gallery img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* Gallery dots */
.gallery-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.3);
  transition: background 0.2s;
}

.gallery-dot.active {
  background: var(--accent-primary);
  width: 24px;
  border-radius: 4px;
}
```

#### 7. Reviews Carousel
```css
.reviews-track {
  display: flex;
  gap: var(--space-md);
  overflow-x: auto;
  scroll-snap-type: x mandatory;
  scrollbar-width: none;
  padding: var(--space-sm) 0;
}

.review-card {
  flex: 0 0 340px;
  scroll-snap-align: start;
  background: var(--bg-surface-1);
  border: 1px solid var(--border-subtle);
  border-radius: 16px;
  padding: var(--space-lg);
}

/* Star rating in gold */
.star-rating {
  color: var(--accent-primary);
}
```

---

## CSS Snippets & Token Reference

### Glassmorphism Navigation (from 1inch)
```css
.sticky-nav {
  position: sticky;
  top: 0;
  background: rgba(12, 12, 15, 0.80);
  backdrop-filter: blur(25px);
  -webkit-backdrop-filter: blur(25px);
  border-bottom: 1px solid var(--border-subtle);
  z-index: 100;
}
```

### Subtle Card Glow on Hover (from Aave)
```css
.card:hover {
  box-shadow: 0 0 0 1px var(--accent-primary),
              0 4px 24px rgba(212, 168, 83, 0.08);
}
```

### Map Embed Styling
```css
.map-container {
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid var(--border-subtle);
  filter: grayscale(1) invert(1) brightness(0.6) contrast(1.2);
  /* Makes standard Google Maps look dark-themed */
}
```

### Breadcrumb (from The OWO)
```css
.breadcrumb {
  font-size: var(--text-caption);
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--text-tertiary);
}

.breadcrumb a {
  color: var(--text-tertiary);
  text-decoration: none;
  transition: color 0.2s;
}

.breadcrumb a:hover {
  color: var(--text-primary);
}

.breadcrumb .separator {
  margin: 0 8px;
  opacity: 0.4;
}
```

### Business Hours Component
```css
.hours-list {
  display: grid;
  grid-template-columns: 80px 1fr;
  gap: 8px 16px;
  font-size: var(--text-small);
}

.hours-day {
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  font-size: var(--text-caption);
}

.hours-time {
  color: var(--text-primary);
}

.hours-open-now {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: var(--status-success);
  font-size: var(--text-caption);
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.hours-open-now::before {
  content: '';
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--status-success);
}
```

---

## Summary: The 5 Highest-Impact Changes

If implementing everything above is too much, these five changes alone will transform the page from "generic dark" to "premium":

1. **Letter-spacing `0.06em`** on all labels, categories, nav items, and all-caps text
2. **Warm cream text** (`#E8E5DF`) instead of pure white (`#FFFFFF`)
3. **Layered grays** (5 shades from `#0c0c0f` to `#2c2c34`) instead of flat black + border
4. **Serif heading font** (Playfair Display or DM Serif Display) for the business name and section headings
5. **Generous whitespace** — double the current padding/margins; use `80px` section padding, `24-32px` card padding

### Accent Color Recommendation for The Videshi News

For an Indian diaspora news site, consider:
- **Warm gold** `#D4A853` — conveys prestige, connects to South Asian design traditions
- **Saffron amber** `#E09130` — culturally resonant, warm on dark backgrounds
- **Deep teal** `#2A9D8F` — modern, fresh, pairs beautifully with gold accents

Avoid: pure blue (too corporate), bright green (too fintech), neon colors (too crypto/gaming).

---

*Research conducted July 2026 across Recent.design, SiteInspire, and Land-book.com*

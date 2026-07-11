# Directory Detail Page — Design Inspiration & Implementation Guide

> Research from Awwwards, Godly.website, luxury hospitality sites, and premium design patterns.
> Goal: Transform DirectoryDetailPage into a **modern, posh** experience on a dark theme (`#0a0a0a`).

---

## 1. Design Philosophy: "Quiet Luxury"

The strongest pattern across award-winning sites is **restraint**. Premium doesn't mean more — it means less, done better. The sites that win Awwwards and dominate design showcases share these traits:

- **Aman Resorts**: "Minimalism as a language of peace." Soft tones, generous space, imagery does the talking.
- **Aesop**: Editorial-style layouts. Calm typography, neutral tones, tactile visual language. Content structure that feels *paced*, not repetitive.
- **Apple (Liquid Glass, WWDC 2025)**: Translucent, layered depth. Glass surfaces that feel alive. Hierarchy through material, not decoration.

**Key takeaway for The Videshi Directory**: Don't try to show everything at once. Let the page breathe. Use space as a design element. The directory currently packs info tight — the revamp should space it out and let each piece of information land.

---

## 2. Color System for Dark Premium

### Background Layers (Avoid Pure Black)
Pure `#000000` creates harsh contrast and eye strain. Use layered dark grays:

```css
/* Background hierarchy — darkest to lightest */
--bg-base:       #0a0a0a;   /* Page background (current — good) */
--bg-elevated:   #111111;   /* Raised sections, hero overlaps */
--bg-card:       #141414;   /* Cards, info panels */
--bg-surface:    #1a1a1a;   /* Interactive elements, hover states */
--bg-subtle:     #222222;   /* Borders that need visibility */
```

### Text Opacity Scale (Not Gray Hex Values)
Use `rgba(255,255,255, opacity)` rather than static grays — adapts better to background changes:

```css
--text-primary:    rgba(255, 255, 255, 0.92);  /* Headings, critical info */
--text-secondary:  rgba(255, 255, 255, 0.64);  /* Body text, descriptions */
--text-tertiary:   rgba(255, 255, 255, 0.38);  /* Labels, metadata, captions */
--text-ghost:      rgba(255, 255, 255, 0.18);  /* Dividers, decorative text */
```

### Accent Colors — Warm Gold + Category Tints
Luxury sites avoid cold blues. The Videshi brand gold (`#D4A843`) is perfect as the primary accent. Use it sparingly for maximum impact:

```css
/* Primary accent — warm gold (brand) */
--accent-gold:        #D4A843;
--accent-gold-muted:  rgba(212, 168, 67, 0.15);  /* Background tints */
--accent-gold-glow:   rgba(212, 168, 67, 0.08);  /* Subtle glows */

/* Supporting accents — for category differentiation */
--accent-emerald:     #34D399;  /* Verified badges */
--accent-amber:       #F59E0B;  /* Ratings */
--accent-purple:      #A78BFA;  /* Community tags */
```

### Gradient Treatments
Award-winning dark sites use gradients for depth, not decoration:

```css
/* Hero fade-out */
background: linear-gradient(to top, #0a0a0a 0%, transparent 100%);

/* Section dividers — invisible but felt */
background: linear-gradient(to right, transparent, rgba(255,255,255,0.06), transparent);

/* Card top-edge highlight (simulates overhead light) */
background: linear-gradient(to bottom, rgba(255,255,255,0.04), transparent 60%);

/* Gold accent gradient for premium CTAs */
background: linear-gradient(135deg, #D4A843 0%, #B8942F 100%);
```

---

## 3. Typography System

### Font Pairing
The current site uses a serif (`font-serif`) for headings. For a premium feel, the pairing should be:

- **Headings**: Serif (Playfair Display or current font-serif) — conveys elegance, editorial quality
- **Body/UI**: Sans-serif (Inter or system) — clean, highly readable
- **Labels/Meta**: Sans-serif, UPPERCASE with wide tracking — signals premium categories

### Type Scale (Major Third — 1.25 ratio)

```css
/* Fluid type scale using clamp() */
--text-xs:    clamp(0.6875rem, 0.6rem + 0.2vw, 0.75rem);     /* 11-12px — captions */
--text-sm:    clamp(0.8125rem, 0.75rem + 0.15vw, 0.875rem);   /* 13-14px — metadata */
--text-base:  clamp(0.9375rem, 0.875rem + 0.15vw, 1rem);      /* 15-16px — body */
--text-lg:    clamp(1.125rem, 1rem + 0.3vw, 1.25rem);         /* 18-20px — lead text */
--text-xl:    clamp(1.5rem, 1.25rem + 0.6vw, 1.75rem);        /* 24-28px — section heads */
--text-2xl:   clamp(1.875rem, 1.5rem + 1vw, 2.5rem);          /* 30-40px — page title */
--text-3xl:   clamp(2.25rem, 1.75rem + 1.5vw, 3.25rem);       /* 36-52px — hero title */
```

### Letter-Spacing Rules
Premium sites use letter-spacing deliberately:

```css
/* Section labels — ALL CAPS with generous tracking */
.section-label {
  font-size: var(--text-xs);
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.2em;        /* Wide tracking for labels */
  color: var(--text-tertiary);
}

/* Headings — tight tracking for large text */
.heading-large {
  font-family: var(--font-serif);
  font-size: var(--text-3xl);
  font-weight: 700;
  letter-spacing: -0.02em;      /* Tighten at large sizes */
  line-height: 1.1;
}

/* Body text — slightly relaxed for readability on dark */
.body-text {
  font-size: var(--text-base);
  line-height: 1.85;            /* More generous on dark backgrounds */
  letter-spacing: 0.01em;       /* Slightly open for legibility */
}
```

---

## 4. Spacing System

### Base Unit: 8px
Use an 8px grid. Premium sites use *more* space than feels necessary — that's what creates the "posh" feel:

| Token   | Value   | Tailwind  | Usage |
|---------|---------|-----------|-------|
| `xs`    | 4px     | `p-1`    | Icon gaps, tight internal spacing |
| `sm`    | 8px     | `p-2`    | Between inline elements |
| `md`    | 16px    | `p-4`    | Standard element padding |
| `lg`    | 24px    | `p-6`    | Card internal padding |
| `xl`    | 32px    | `p-8`    | Between major sections |
| `2xl`   | 48px    | `p-12`   | Section breathing room |
| `3xl`   | 64px    | `p-16`   | Hero-to-content gap |
| `4xl`   | 96px    | `p-24`   | Page-level vertical rhythm |

### Key Spacing Decisions
- **Section gaps**: `48-64px` minimum between major content blocks (About, Hours, Photos)
- **Card padding**: `24-32px` internal padding (current `p-5` = 20px is too tight)
- **Title to first info**: `32-48px` after the hero title before any content
- **Line-height for body**: `1.85` on dark backgrounds (dark needs more vertical space)

---

## 5. Card & Surface Design

### The Glass Card (Inspired by Apple Liquid Glass + Awwwards winners)
The most impactful visual upgrade. Replace flat `bg-white/[0.03] border border-white/[0.06]` cards with layered glass:

```css
/* Premium glass card */
.glass-card {
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(12px) saturate(120%);
  -webkit-backdrop-filter: blur(12px) saturate(120%);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 16px;
  box-shadow:
    0 0 0 0.5px rgba(255, 255, 255, 0.04),           /* Hairline outer ring */
    0 2px 8px rgba(0, 0, 0, 0.3),                     /* Soft drop shadow */
    inset 0 1px 0 rgba(255, 255, 255, 0.05);          /* Top-edge highlight */
  overflow: hidden;
}

/* Top-edge light effect (simulates light source from above) */
.glass-card::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  background: linear-gradient(
    to bottom,
    rgba(255, 255, 255, 0.04) 0%,
    transparent 40%
  );
  pointer-events: none;
}
```

### Tailwind Implementation
```html
<!-- Glass card in Tailwind -->
<div class="relative bg-white/[0.03] backdrop-blur-sm border border-white/[0.06]
            rounded-2xl shadow-[0_2px_8px_rgba(0,0,0,0.3),inset_0_1px_0_rgba(255,255,255,0.05)]
            overflow-hidden">
  <!-- Top light gradient -->
  <div class="absolute inset-0 bg-gradient-to-b from-white/[0.04] to-transparent pointer-events-none rounded-2xl" />
  <!-- Content -->
  <div class="relative p-6 lg:p-8">
    ...
  </div>
</div>
```

### Interactive Card (Hover State)
Premium sites use *subtle* hover transitions — never jarring:

```css
.glass-card {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.glass-card:hover {
  border-color: rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.05);
  box-shadow:
    0 0 0 0.5px rgba(255, 255, 255, 0.06),
    0 4px 16px rgba(0, 0, 0, 0.4),
    inset 0 1px 0 rgba(255, 255, 255, 0.08);
  transform: translateY(-1px);  /* Barely perceptible lift */
}
```

### Border Radius Scale
Award-winning sites use consistent, generous radii:

```css
--radius-sm:  8px;    /* Small elements: tags, badges */
--radius-md:  12px;   /* Buttons, inputs */
--radius-lg:  16px;   /* Cards, panels */
--radius-xl:  24px;   /* Hero images, major containers */
--radius-full: 9999px; /* Pills, circular elements */
```

---

## 6. Page Layout — Two-Column with Hero

### Reference: Event Detail Page + Aman/Aesop Patterns

```
┌─────────────────────────────────────────────────┐
│              FULL-WIDTH HERO IMAGE              │
│          (max-height: 60vh, object-contain)      │
│        ┌───────── gradient fade ─────────┐      │
└────────┴─────────────────────────────────┴──────┘
│  breadcrumb (tiny, muted)                        │
│                                                  │
│  CATEGORY · SUBCATEGORY · COMMUNITY              │ ← uppercase, tracked
│                                                  │
│  Business Name                                   │ ← serif, 36-52px
│  City, State · Affiliation                       │ ← muted, 16px
│  ★★★★☆ 4.2 (89 reviews)                        │
│  🗣 Hindi, Gujarati                              │
│                                                  │
│  [📞 Call Now]  [🌐 Visit Website]               │ ← prominent CTAs
│  Share: WhatsApp · Copy Link                     │
│                                                  │
├──────────────────────── gradient divider ─────────┤
│                                                  │
│  ┌── MAIN COLUMN (60%) ──┐  ┌── SIDEBAR (320px)─┐│
│  │                        │  │                    ││
│  │  ABOUT (section label) │  │  CONTACT INFO card ││
│  │  AI description text   │  │  📍 Address        ││
│  │                        │  │  📞 Phone          ││
│  │  SERVICES              │  │  ✉️ Email          ││
│  │  [tag] [tag] [tag]     │  │  🌐 Website        ││
│  │                        │  │  [Call Now] CTA    ││
│  │  HOURS                 │  │                    ││
│  │  Mon-Sun schedule      │  │  More {Category} → ││
│  │                        │  │  More in {City} →  ││
│  │  PHOTOS                │  │                    ││
│  │  Horizontal scroll     │  │                    ││
│  │                        │  └────────────────────┘│
│  └────────────────────────┘                       │
│                                                  │
├──────────────────────── gradient divider ─────────┤
│  Source disclaimer  ·  ← Back to Directory       │
└──────────────────────────────────────────────────┘
```

### Key Layout Decisions
1. **Hero image**: Full-width, max 60vh, with bottom gradient fade into `#0a0a0a`
2. **Title overlaps hero**: `-mt-6` to create visual connection (like event page)
3. **Two-column on desktop**: `grid-cols-[1fr_320px]` with 40px gap
4. **Single column on mobile**: Sidebar stacks below main content
5. **Section headers**: Uppercase, tracked, tiny, ghost-colored — like Aman's navigation
6. **Generous vertical space**: 48-64px between sections

---

## 7. Micro-Interactions & Transitions

### Global Transition Curve
Use a custom easing for all transitions — feels more natural than linear:

```css
/* The "premium" easing curve — slight overshoot on entry */
--ease-premium: cubic-bezier(0.16, 1, 0.3, 1);

/* Standard transition for interactive elements */
transition: all 0.3s var(--ease-premium);
```

### Specific Interactions

**Hover on category/city links:**
```css
/* Subtle scale + border brightening */
.nav-link:hover {
  border-color: rgba(255, 255, 255, 0.12);
  transform: translateY(-1px);
  transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}
```

**CTA Button — Primary (Call Now):**
```css
/* Gold gradient with subtle glow on hover */
.cta-primary {
  background: linear-gradient(135deg, #D4A843 0%, #B8942F 100%);
  color: #0a0a0a;
  box-shadow: 0 0 0 0 rgba(212, 168, 67, 0);
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}
.cta-primary:hover {
  box-shadow: 0 0 24px rgba(212, 168, 67, 0.2);
  transform: scale(1.02);
}
.cta-primary:active {
  transform: scale(0.98);
}
```

**CTA Button — Secondary (Visit Website):**
```css
.cta-secondary {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.12);
  color: rgba(255, 255, 255, 0.8);
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}
.cta-secondary:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.2);
}
```

**Photo gallery image hover:**
```css
.gallery-img {
  transition: transform 0.5s cubic-bezier(0.16, 1, 0.3, 1);
}
.gallery-img:hover {
  transform: scale(1.03);
}
```

**Star rating — subtle pulse on the rating number:**
```css
.rating-value {
  color: #F59E0B;
  font-variant-numeric: tabular-nums;
  /* No animation by default — let the number speak */
}
```

---

## 8. Specific Component Patterns

### Contact Info Card (Sidebar)
Inspired by Google Maps info panel + Aman's restrained design:

```html
<div class="glass-card p-6 lg:p-8 space-y-5">
  <h3 class="section-label">Contact</h3>

  <div class="space-y-4">
    <!-- Each contact row: icon + info -->
    <div class="flex items-start gap-4">
      <span class="text-lg mt-0.5 opacity-60">📍</span>
      <div>
        <p class="text-white/80 text-sm font-medium leading-relaxed">
          123 Main Street, Suite 200
        </p>
        <a class="inline-flex items-center gap-1.5 text-xs text-white/30
                   hover:text-white/60 transition-colors mt-1.5 group">
          <svg><!-- pin icon --></svg>
          <span class="group-hover:underline">Get Directions</span>
        </a>
      </div>
    </div>
  </div>

  <!-- Full-width CTA at bottom of card -->
  <a class="flex items-center justify-center gap-2 w-full px-6 py-3.5
            rounded-full bg-gradient-to-r from-[#D4A843] to-[#B8942F]
            text-[#0a0a0a] font-bold text-sm
            hover:shadow-[0_0_24px_rgba(212,168,67,0.2)]
            transition-all">
    📞 Call Now
  </a>
</div>
```

### Hours Display
Inspired by Google Maps — current day highlighted, clean grid:

```html
<section class="space-y-5">
  <h2 class="section-label">Hours</h2>
  <div class="glass-card p-5 divide-y divide-white/[0.04]">
    <!-- Today's row gets highlight -->
    <div class="flex justify-between py-2.5 px-3 -mx-1
                bg-[#D4A843]/[0.06] rounded-lg text-sm">
      <span class="text-white/90 font-medium">Friday</span>
      <span class="text-[#D4A843] font-medium">9:00 AM – 6:00 PM</span>
    </div>
    <!-- Other days -->
    <div class="flex justify-between py-2.5 px-3 text-sm text-white/40">
      <span>Saturday</span>
      <span>10:00 AM – 2:00 PM</span>
    </div>
  </div>
</section>
```

### Service Tags
Pill-shaped, ghost-style, with subtle hover:

```html
<div class="flex flex-wrap gap-2">
  <span class="px-3.5 py-1.5 rounded-full
               bg-white/[0.04] border border-white/[0.08]
               text-white/50 text-sm
               hover:bg-white/[0.08] hover:text-white/70
               transition-all cursor-default">
    Family Medicine
  </span>
</div>
```

### Rating Display
Premium sites keep ratings understated:

```html
<div class="flex items-center gap-3">
  <div class="flex items-center gap-0.5">
    <!-- Filled stars: text-amber-400; Empty: text-white/15 -->
    <span class="text-amber-400 text-lg">★</span>
    <span class="text-amber-400 text-lg">★</span>
    <span class="text-amber-400 text-lg">★</span>
    <span class="text-amber-400 text-lg">★</span>
    <span class="text-white/15 text-lg">★</span>
  </div>
  <span class="text-amber-400 font-semibold text-lg tabular-nums">4.2</span>
  <span class="text-white/30 text-sm">(89 reviews)</span>
</div>
```

### Photo Gallery
Horizontal scroll with snap, generous sizing:

```html
<div class="flex gap-3 overflow-x-auto pb-4
            scrollbar-none snap-x snap-mandatory -mx-4 px-4">
  <div class="flex-shrink-0 snap-start
              w-[80%] sm:w-[45%] lg:w-[32%]
              rounded-xl overflow-hidden group">
    <img class="w-full h-48 sm:h-56 object-cover bg-white/5
                transition-transform duration-500
                group-hover:scale-[1.03]" />
  </div>
</div>
```

---

## 9. Responsive Behavior

### Breakpoints
```css
/* Mobile first */
@media (min-width: 640px)  { /* sm: tablets */ }
@media (min-width: 1024px) { /* lg: desktop — two-column kicks in */ }
@media (min-width: 1280px) { /* xl: wide desktop — more breathing room */ }
```

### Mobile Adaptations
- Hero image: `max-h-[45vh]` on mobile (vs `60vh` desktop)
- Title: `text-3xl` on mobile (vs `text-5xl` desktop)
- Sidebar: Stacks below main content
- CTA buttons: Full width on mobile
- Photo gallery: Single card width `w-[85%]`
- Card padding: `p-5` on mobile, `p-8` on desktop

---

## 10. What NOT to Do (Anti-Patterns from Research)

1. **Don't use pure black `#000000`** — `#0a0a0a` is correct, stay with it
2. **Don't add too many accent colors** — Gold + Amber (ratings) + Emerald (verified) is the max
3. **Don't use heavy box-shadows** — On dark themes, inner glows and subtle top-edge highlights work better than drop shadows
4. **Don't animate everything** — Only interactive elements should transition. Static content stays still
5. **Don't use colored backgrounds for tags/badges** — Ghost-style (transparent bg + subtle border) reads more premium
6. **Don't crowd the sidebar** — One contact card + 1-2 navigation links, that's it
7. **Don't use emoji as primary icons** — For a "posh" feel, consider transitioning to Lucide icons or thin SVGs. Emoji reads casual. (Exception: category icons that are part of the directory's identity can stay)
8. **Don't sacrifice readability for aesthetics** — WCAG contrast ratio of 4.5:1 minimum. `rgba(255,255,255,0.64)` on `#0a0a0a` passes; `rgba(255,255,255,0.38)` does not for body text (fine for labels)

---

## 11. Implementation Priority

### Phase 1 — Layout & Typography (Highest Impact)
1. Switch to two-column layout with hero overlap
2. Apply type scale and section labels
3. Add generous spacing between sections (48-64px)
4. Gold CTA buttons instead of plain white

### Phase 2 — Surface Treatment
5. Glass card styling (backdrop-blur, inset shadows, gradient overlays)
6. Hours display with today-highlight in gold
7. Service tags as ghost pills
8. Gradient dividers between sections

### Phase 3 — Polish
9. Hover transitions with premium easing
10. Photo gallery with scale-on-hover
11. Breadcrumb and back-link styling
12. Source disclaimer in ghost text

---

## 12. Reference Sites (Verified & Researched)

| Site | What to Study | Key Lesson |
|------|--------------|------------|
| [aman.com](https://www.aman.com) | Detail pages, spacing, typography | "Luxury through simplicity" |
| [aesop.com](https://www.aesop.com) | Product pages, editorial pacing | Calm typography, neutral tones |
| [godly.website](https://godly.website) | Dark theme showcase gallery | Curated inspiration feed |
| [awwwards.com](https://www.awwwards.com) | Award winners, design trends | Annual best practices |
| Apple Liquid Glass (WWDC 2025) | Translucent glass UI, depth layers | `backdrop-filter: blur() saturate()` |
| [Fluid Glass (Awwwards winner 2026)](https://thesource.com) | Gaussian Blur effects, depth | Sophisticated glass depth |
| [Active Theory (Awwwards winner)](https://thesource.com) | Cinematic dark aesthetics | Dark = premium when done right |

---

## 13. Quick-Reference Tailwind Cheat Sheet

```jsx
// Section label
<h2 className="text-[11px] font-bold uppercase tracking-[0.2em] text-white/30 mb-6">

// Glass card
<div className="relative bg-white/[0.03] backdrop-blur-sm border border-white/[0.06]
  rounded-2xl overflow-hidden
  shadow-[0_2px_8px_rgba(0,0,0,0.3),inset_0_1px_0_rgba(255,255,255,0.05)]">

// Gold CTA
<a className="inline-flex items-center gap-2 px-8 py-4 rounded-full
  bg-gradient-to-r from-[#D4A843] to-[#B8942F] text-[#0a0a0a]
  font-bold text-sm
  hover:shadow-[0_0_24px_rgba(212,168,67,0.2)]
  hover:scale-[1.02] active:scale-[0.98]
  transition-all duration-300">

// Ghost tag
<span className="px-3.5 py-1.5 rounded-full bg-white/[0.04] border border-white/[0.08]
  text-white/50 text-sm">

// Gradient divider
<div className="h-px bg-gradient-to-r from-transparent via-white/[0.08] to-transparent" />

// Today's hours highlight
<div className="bg-[#D4A843]/[0.06] rounded-lg">
  <span className="text-[#D4A843]">9:00 AM – 6:00 PM</span>
</div>

// Section spacing
<div className="space-y-12 lg:space-y-16">  {/* 48-64px between sections */}

// Hero serif title
<h1 className="font-serif text-3xl sm:text-4xl md:text-5xl text-white font-bold
  leading-[1.1] tracking-tight">
```

---

*Last updated: 2026-07-10. Research compiled from Awwwards, Godly.website, Aman Resorts, Aesop, Apple Liquid Glass (WWDC 2025), DesignRush, Mediaboom luxury hotel analysis, and CSS-Tricks glassmorphism guides.*

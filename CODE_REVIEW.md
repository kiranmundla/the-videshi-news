# The Videshi — Comprehensive Code Review

*Generated: June 2025*

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Data Flow: RSS → Signals → Topics → Articles → Frontend](#2-data-flow)
3. [Pipeline v2 (P2) — Stage by Stage](#3-pipeline-v2-stages)
4. [Image Sourcing Strategy](#4-image-sourcing-strategy)
5. [Frontend Architecture](#5-frontend-architecture)
6. [Admin & Pipeline Dashboard](#6-admin-pipeline-dashboard)
7. [Legacy v1 Pipeline](#7-legacy-v1-pipeline)
8. [Resilience & Error Handling](#8-resilience-error-handling)
9. [Entity System](#9-entity-system)
10. [Supporting Edge Functions](#10-supporting-edge-functions)
11. [Configuration & Deployment](#11-configuration-deployment)
12. [Notable Patterns](#12-notable-patterns)
13. [Issues & Improvement Areas](#13-issues-improvements)

---

## 1. Architecture Overview

The Videshi is a fully automated Indian diaspora news platform with two main layers:

### Frontend (React + Vite + TypeScript)
- **Framework**: React 18 with Vite, deployed on **Vercel**
- **Styling**: Tailwind CSS + shadcn/ui (Radix primitives)
- **Data fetching**: TanStack React Query + direct Supabase client
- **Routing**: React Router with `react-helmet-async` for SEO
- **Key pattern**: SSR-like OG tag injection via Vercel Edge Middleware (`middleware.ts`)

### Backend (Supabase)
- **Database**: PostgreSQL via Supabase (27 tables, 4 RPC functions)
- **Edge Functions**: ~20 Deno functions handling ingestion, AI processing, image sourcing, admin operations
- **AI Models**: Gemini 2.5 Flash (ranking/clustering), Claude Sonnet 4 (article synthesis), Claude Haiku 4.5 (entity extraction, vision scoring)
- **Storage**: Supabase Storage bucket `article-images` for rehosted images
- **Email**: Resend API for contact form and pipeline alert emails

### External Services
| Service | Purpose |
|---------|---------|
| Gemini 2.5 Flash | Signal clustering, topic ranking, carousel photo suggestions |
| Claude Sonnet 4.6 | Article synthesis with web search |
| Claude Haiku 4.5 | Entity extraction, image relevance scoring (Vision) |
| Unsplash API | Stock photo candidates |
| Pexels API | Stock photo candidates |
| Pixabay API | Stock photo candidates |
| Wikipedia / Wikimedia | Free entity images |
| The News API | Homepage carousel news images |
| Resend | Transactional email |
| rss2json | RSS proxy for blocked feeds |

---

## 2. Data Flow

```
RSS Feeds (Indian news sites, govt sources, Google News)
    │
    ▼
┌──────────┐
│ p2-ingest │  Fetches RSS, dedupes by url_hash → p2_signals
└────┬─────┘  Primary feeds also seed p2_source_hunts (full content)
     │
     ▼  (45s delay)
┌─────────┐
│ p2-rank  │  Three parallel Gemini calls:
└────┬────┘   1. Re-rank existing published articles (score decay)
     │        2. Cluster new signals into topics → p2_topics
     │        3. Generate carousel photo suggestions
     │
     ▼  (90s delay)
┌──────────────┐
│ p2-synthesize │  Claude Sonnet writes articles for top-scored topics
└────┬─────────┘  Auto-publish if confidence ≥ 65 AND diaspora score ≥ 60
     │            Otherwise → "review" status for human approval
     │
     ▼  (120s delay)
┌───────────┐
│ p2-images  │  Multi-tier image sourcing + Claude Vision scoring
└────┬──────┘  Stores winners in Supabase Storage
     │
     ▼
┌──────────────┐
│ Frontend SPA  │  React app queries p2_articles via Supabase client
└──────────────┘  Categories, featured hero, event clusters, carousels
```

### Orchestration
`p2-orchestrate` runs the full pipeline sequentially with sleep delays between stages:
- Ingest → 45s → Rank → 90s → Synthesize → 120s → Images
- Total pipeline run: ~5-6 minutes minimum
- Calls each function via HTTP POST to the Supabase functions endpoint

---

## 3. Pipeline v2 (P2) — Stage by Stage

### 3.1 p2-ingest

**Purpose**: Fetch RSS feeds, deduplicate, store raw signals.

**Input**: `videshi_sources` table (active sources with `pipeline_stage` = discovery or primary)

**Process**:
1. Loads all active sources from `videshi_sources` (not `p2_feed_sources` — normalized to common interface)
2. Fetches feeds in batches of 5 with 500ms delays between batches
3. Unwraps rss2json proxy URLs to fetch underlying RSS directly (rss2json returns HTTP 422 for some Indian publishers)
4. Parses RSS/XML with regex-based parser (supports `<item>` and `<entry>` formats, CDATA blocks)
5. Falls back to rss2json JSON format if response starts with `{`
6. Filters items older than 48 hours
7. Generates SHA-256 URL hash (first 32 hex chars) for deduplication
8. Upserts into `p2_signals` with `onConflict: "url_hash"`
9. Primary-layer feeds also write to `p2_source_hunts` (up to 30 items with content > 100 chars) for later synthesis
10. Updates source metadata: `last_fetched_at`, rolling average items/day, error counters, total stats
11. Logs per-source results to `videshi_source_logs`

**Error handling**: 
- Fetch failures logged to `pipeline_alerts` + `videshi_source_logs`
- `consecutive_errors` counter incremented on source (no auto-disable threshold)
- 20s timeout per feed fetch

**Output**: `p2_signals` rows, `p2_source_hunts` rows, `videshi_source_logs` entries

### 3.2 p2-rank

**Purpose**: Cluster signals into topics, re-rank existing articles, generate carousel photos.

**AI Model**: Gemini 2.5 Flash (with fallback to 2.0 Flash on 503)

**Process**: Three independent Gemini calls run in parallel via `Promise.allSettled`:

#### Call A — Re-rank existing articles
- Fetches published articles from last 96 hours
- Gemini scores each 0-100 based on diaspora relevance, significance, age, developing/resolved status
- Decay guidance: breaking (<6h) = full value, fresh (6-24h) = slight decay, yesterday = significant decay, old (48-72h) = heavy decay
- Articles not returned by Gemini get a fallback mathematical decay

#### Call B — Cluster new signals into topics
- Provides Gemini with headline list annotated with source name, tier (TOP-STORY/SECTION/SPECIALIST), and hours ago
- Also provides already-published headlines to avoid recreating covered events
- Gemini returns ranked topics with: canonical_title, vertical, category, event_type, event_date, scores, urgency, keywords, key_entities, free_sources, synthesis_angle, image metadata
- Category rules: "news" for India-domestic, "nri-world" for Indian-origin people outside India
- Detailed diaspora scoring rubric (H-1B/visa = 90-100, national elections = 75-89, state politics = 65-74, etc.)

#### Call C — Carousel photos
- Gemini suggests 5 copyright-free images for the homepage carousel from recent events

**Deduplication**: Entity-aware comparison against recent topics (48h window):
- Extracts proper-noun entities from titles via regex
- Politics/news verticals require 3 shared entities to be considered duplicate (higher threshold due to name collisions like "Vijay")
- Other verticals require 2 shared entities
- Also checks against published article headlines
- Breaking urgency topics bypass dedup

**Scoring formula**: `score_total = diaspora * 0.60 + significance * 0.30` (capped at 100)

**Filtering**: Topics with `score_diaspora < 45` are dropped. Maximum 12 topics per run.

**Output**: `p2_topics` rows, updated `p2_articles.score_total` (re-ranked), `videshi_carousel_photos` rows

**Retry logic**: Up to 3 attempts per Gemini call (gemini-2.5-flash × 2, then gemini-2.0-flash), with 2s incremental delay. JSON repair attempts on parse failure (5 attempts, alternating `]` and `}` suffixes).

### 3.3 p2-synthesize

**Purpose**: Write original news articles for top-ranked topics.

**AI Model**: Claude Sonnet 4.6 (via Anthropic SDK)

**Process**:
1. Fetches top 5 pending topics with `score_total ≥ 60`
2. Skips topics that already have articles
3. Duplicate check: compares topic title words against recently published headlines (3+ shared words of length > 4 = duplicate → rejected)
4. Searches `p2_source_hunts` for keyword-matched content (up to 3 matches, keyword in title)
5. If pre-loaded sources exist: feeds them as context to Claude
6. If no pre-loaded sources: enables Claude's `web_search_20250305` tool for real-time web research
7. Claude writes article with: headline, subheadline, body (250-320 words), diaspora_angle, tags, sources, image search hints
8. Citations stripped from output (removes `<cite>` tags, `[N]` markers)
9. Auto-publish if: `confidence ≥ 65` AND `score_diaspora ≥ 60`; otherwise → "review" status
10. Slug generated: lowercase headline (first 80 chars) + timestamp in base-36

**Writing style directives**:
- 250-320 words, strong lede, 2-3 bold-header sections, closing "what to watch" line
- Economist-style: precise, authoritative, one idea per sentence
- Diaspora angle mandatory (exactly 1 sentence)
- Single quotes only in JSON body values (to avoid JSON parse issues)

**Error handling**: On failure, topic status reverts to "pending"; alert logged to `pipeline_alerts`

**Output**: `p2_articles` rows (status: published or review), updated `p2_topics.status`

### 3.4 p2-images

**Purpose**: Source, evaluate, and store hero images for published articles.

**AI Models**: Claude Haiku 4.5 (entity extraction + vision scoring)

**Process** (per article):

1. **Text-first filter**: Articles about military/conflict/terrorism skip image sourcing entirely
2. **Gemini fast path**: If `p2-rank` provided an `image_url`, try downloading it directly
3. **Gemini wiki fast path**: If Gemini provided a search query, try first Wikimedia/Wikipedia candidate without Vision scoring
4. **Full pipeline** (if above paths fail):
   a. Claude Haiku extracts primary entity + search query from headline
   b. **Tier 1**: Wikipedia entity image + Wikimedia Commons search (6 results)
   c. **Tier 2**: Scrape source article pages for images (og:image, article body imgs, srcset)
   d. **Tier 3**: Unsplash + Pexels + Pixabay (only if < 6 candidates)
   e. Candidates reordered: government/press sources first, stock photos last
   f. **Claude Vision scores each candidate** individually (up to 12, fetched as base64 thumbnails ≤ 500KB):
      - Government/press photos get +3 bonus
      - Entity match required; generic imagery capped at score 4
      - Stock clichés (handshakes, lightbulbs) capped at 3
      - Accept threshold: score ≥ 6 (previously 8, lowered in scoring prompt but code checks `< 6`)
   g. Duplicate check: skip URLs already used by other articles
   h. Winner downloaded to Supabase Storage
5. **Carousel processing**: Downloads/stores images from `videshi_carousel_photos`

**Logging**: All decisions logged to `videshi_image_log` (article_id, source used, candidates count, vision score)

**Output**: Updated `p2_articles.image_url` and `p2_articles.image_attribution`

---

## 4. Image Sourcing Strategy

The image pipeline is remarkably sophisticated, with 6 source tiers and AI-powered quality control:

### Source Priority (descending)
1. **Gemini-suggested URL** (from p2-rank) — downloaded directly if valid image
2. **Wikipedia entity image** — REST API page summary thumbnail
3. **Wikimedia Commons** — search API, converted to Special:FilePath URLs
4. **Source article scraping** — og:image, article body images, srcset high-res
5. **Unsplash** — landscape, high content filter, up to 15 results
6. **Pexels** — landscape orientation, up to 15 results
7. **Pixabay** — horizontal, popular order, safe search, up to 10 results

### Quality Gates
- **Claude Haiku Vision** scores each candidate 0-10 on relevance, entity match, and photo quality
- Government/press source photos receive +3 score bonus
- Score ≥ 6 required to accept (previously 8, lowered)
- Per-image scoring (not batch) provides granular control
- Dedup against all previously used image URLs
- 500ms delay between articles to respect rate limits

### Copyright Strategy
- Rankings prompt instructs: "NEVER Getty/AP/Reuters/news site images"
- Prefers Wikimedia Commons (CC-BY-SA), PIB (public domain), Unsplash/Pexels (free to use)
- Source scraping targets government domains (`.gov.in`, `pib.gov`, `uscis.gov`) for attribution

---

## 5. Frontend Architecture

### Pages

| Route | Component | Description |
|-------|-----------|-------------|
| `/` | `Index.tsx` | Homepage with featured hero, category sections, event clusters, article carousel |
| `/articles/:slug` | `ArticlePage.tsx` | Full article with markdown rendering, related articles, sources |
| `/:category` | `CategoryPage.tsx` | Paginated article grid (12 per page) for any category |
| `/admin` | `Admin.tsx` | Featured article admin (pin/unpin with admin key) |
| `/about` | `About.tsx` | Static about page |
| `/contact` | `Contact.tsx` | Contact form (sends via Resend) |
| `/admin/p2/*` | `PipelineLayout` + child pages | Full pipeline dashboard |

### Homepage Layout (Index.tsx)

The homepage is editorial-style, resembling a newspaper front page:

1. **Featured Hero** — Highest-scored or pinned article with full-width image + overlay text
2. **India News** — Tag-based event clustering (hardcoded clusters like "Tamil Nadu: Vijay's Government", "IPL 2026 Playoff Race", "H-1B & Visas")
3. **World News** — Same clustering for NRI-world category
4. **Category Sections** — Markets & Finance, Sports, Technology, Entertainment, Lifestyle & Health, Travel, Food
5. **Article Carousel** — Auto-playing image carousel of top 3 published articles with images

**Event Clustering**: `buildClusters()` matches articles by tag intersection against hardcoded cluster definitions. Each cluster requires matching `require` tags AND `also` tags. Articles used in clusters are excluded from the ungrouped grid. Clusters need ≥ 2 articles to display.

**Scroll Position**: Saves/restores scroll position to `sessionStorage` when navigating away/back.

**Data Loading**: `Promise.all` fetches featured article + all category pools simultaneously.

### Key Components

**FeaturedHero**: Full-width hero with gradient overlay. Falls back to dark solid background if image is a flag or invalid. Uses `object-position: center 25%` for better face framing.

**ArticleCard**: Multi-variant card component (`hero`, `featured`, `card`, `long`, `compact`). Text-first cards (no image) get a red top accent bar and ~20% larger headlines. Per-category accent colors. Saves scroll position on click.

**EventCluster**: Left-bordered card with primary-colored accent. Lead article with image + 2 secondary headline links.

**ArticleCarousel**: Auto-advancing (5s) image carousel querying `p2_articles` for top 3 published articles with images. Touch swipe support. Filters out SVGs, flag images, and Hindustan Times domain images.

**HeroCarousel**: Pulls from `carousel_images` table (today's date). Similar auto-advance (6s) with touch support. Caption overlay with credit attribution.

**Masthead**: Clean newspaper-style header with serif title, date display, hairline rule.

**CategoryPills**: Mobile-only horizontal scrolling category pills. On homepage, acts as scroll-spy navigation (scrolls to section). On category pages, shows breadcrumb.

### Article Rendering (ArticlePage.tsx)

- Uses `ReactMarkdown` with custom renderers:
  - Strips `<h1>` tags (headline already shown above)
  - Unwraps image-only links (removes wrapping `<a>`)
  - Filters tracking pixels (`counter.theconversation.com`, `count.gif`, etc.)
  - Deduplicates hero image if it appears in body
- Supports `ArticleBlocks` format (structured JSON blocks) via `tryParseBlocks()`
- Displays source attribution with clickable links
- Related articles: 3 articles from same category

### SEO

- **React Helmet**: Each page sets `<title>`, `<meta description>`, Open Graph, and Twitter Card tags
- **Vercel Middleware** (`middleware.ts`): Edge middleware intercepts `/articles/:slug` requests, fetches article from Supabase, injects OG meta tags into the static `index.html` shell before serving. Enables proper social media previews for the SPA.
- **Canonical URLs** set on all pages
- SPA fallback via `vercel.json`: `/(.*) → /index.html`

---

## 6. Admin & Pipeline Dashboard

### Featured Admin (`/admin`)
Simple admin interface:
- Lists all published articles sorted by pinned status → featured score
- Admin key stored in `localStorage` (`videshi-admin-key`)
- Pin/unpin articles as featured for 24 hours via `admin-pin-article` edge function
- Shows featured score, publication date, and pin status

### Pipeline Dashboard (`/admin/p2/*`)

Full-featured editorial pipeline management with sidebar navigation:

#### Feed Sources (`/admin/p2/feeds`)
- CRUD for `p2_feed_sources` table
- Filters: layer (discovery/primary), vertical, tier (A/B/C), active status
- Toggle active/inactive per feed
- Add/edit dialog with: name, URL, type (RSS/scrape/API), layer, tier, fetch interval, verticals
- Pagination (20 per page)

#### Topic Radar (`/admin/p2/topics`)
- Dashboard with summary cards: today's topics, pending, in review, published, rejected
- Filters: vertical, urgency (breaking/daily/evergreen), status
- Sort by: score, date, signals
- Expandable rows showing:
  - Score breakdown (diaspora, significance, recency, source availability)
  - Keywords
  - Contributing signals with source names
  - Source hunts with relevance scores and content previews
  - Generated article (if exists)
- Actions: mark rejected

#### Review Queue (`/admin/p2/review`)
- Two-panel layout: article list (left) + full editor (right)
- Urgency-colored left borders on article cards
- Full article editor with: headline, subheadline, body (with word count), diaspora angle, tags, sources
- Actions: Approve & Publish, Save Edits, Reject
- Optional Beehiiv integration toggle (UI only, not wired)
- Badge count in sidebar (auto-refreshes every 30s)

#### Run Log (`/admin/p2/run`)
- Today's stats: signals ingested, topics ranked, articles synthesized, published
- Alert history from `pipeline_alerts` table (last 20)
- Severity-colored badges (error/warning/info)
- "Run Pipeline Now" button (currently just shows a toast, not wired to `p2-orchestrate`)

### Source Registry (`/admin/sources`)
- More comprehensive source management for `videshi_sources` table
- Registry tab: CRUD with filters for pipeline stage, type, vertical, status, search
- Performance tab: Bar chart of items fetched per source (last 7 days) using Recharts, plus detailed stats table (runs, fetched, accepted, accept %, error %, avg duration)
- Form sheet with sections: Identity, Type, Targeting (verticals, skip verticals, categories), Access (endpoint URL, API key secret, proxy settings), Operations (priority, interval, max items), Legal (license type, attribution requirements), Notes

---

## 7. Legacy v1 Pipeline

The codebase contains a complete legacy pipeline that operated through a `story_queue` claim/lock pattern:

### Legacy Functions
| Function | Role | Model |
|----------|------|-------|
| `ingest-rss` | RSS fetching with hardcoded source list | N/A |
| `agent-scout` | Groups raw articles, writes story briefs → `story_queue` | Claude Haiku 4.5 |
| `agent-writer` | Claims pending jobs, writes articles with web search | Claude Sonnet |
| `agent-enricher` | Claims writing jobs, produces rich diaspora-focused articles | Claude Haiku 4.5 |
| `agent-editor` | Final edit pass | Claude Haiku |
| `agent-cleanup` | Resets stuck jobs (writing/enriching/editing > 15 min) | N/A |
| `agent-images` | Vision-verified image sourcing (Wikipedia, Wikimedia, Unsplash, Pexels) | Claude Haiku 4.5 (Vision) |
| `process-stories` | End-to-end: pull raw articles → Claude groups → Claude writes → store | Claude Sonnet |

### Legacy Tables
- `raw_articles` — ingested RSS items
- `story_groups` / `story_clusters` — grouped stories
- `story_queue` — job queue with status/lock/claim pattern
- `articles` — final articles (different schema from `p2_articles`)
- `dead_letter_queue` — failed jobs

### Key Differences from v2
1. **RSS sources hardcoded** in `ingest-rss/index.ts` (30+ sources) vs v2's database-driven `videshi_sources`
2. **Job queue pattern** with claim/lock/timeout vs v2's simpler sequential orchestration
3. **Multi-agent pipeline** (scout → writer → enricher → editor → images) vs v2's simpler 4-stage pipeline
4. **No Gemini** — v1 was all Claude-based
5. **Different article table** — `articles` (v1) vs `p2_articles` (v2)

### Notable Legacy Patterns
- `ingest-rss` handles PIB, MEA (HTML scraping), USCIS, RBI, Google News, and 20+ Indian news publishers
- `agent-enricher` includes Google News URL unwrapping (follows redirects to real publisher URLs)
- `process-stories` is a monolithic alternative that does everything in one function
- `ingest-conversation-india` ingests from The Conversation India's Atom feed (CC BY-ND 4.0 licensed), with full Atom/XML parsing and HTML→Markdown conversion

---

## 8. Resilience & Error Handling

### Shared Resilience Module (`_shared/resilience.ts`)

A sophisticated error handling framework used by legacy agents:

**Error Classification**:
- **Fatal** (401, 403, auth errors): No retry, immediate alert + email
- **Transient** (408, 502, 503, 504, 529, overloaded): Up to 4 retries with backoff [2s, 5s, 15s, 30s]
- **Recoverable** (429 rate limit, JSON parse): Up to 2 retries with 10s delay
- **Unknown**: Single retry at 2s then fail

**Circuit Breaker**: 5+ overloaded errors per agent within 10 minutes trips the circuit. Once tripped:
- All subsequent calls immediately fail
- Critical alert logged + email sent via Resend
- No automatic recovery (requires timeout expiry)

**Alert Email**: Sends critical/fatal alerts to `editor@thevideshi.com` via Resend API. HTML-formatted with agent, error type, job ID, timestamp, and message.

**Dead Letter Queue**: `moveToDLQ()` records failed jobs with full error history for manual investigation.

**50s Hard Timeout**: `AbortSignal.timeout(50000)` on Claude API calls to stay under Supabase's 60s function timeout.

### P2 Pipeline Error Handling

The v2 pipeline takes a simpler approach:

- **p2-ingest**: Per-feed error tracking with `consecutive_errors` counter, alerts to `pipeline_alerts`, per-source logs to `videshi_source_logs`
- **p2-rank**: `Promise.allSettled` allows independent failure of re-rank/cluster/carousel calls. JSON repair on truncated output.
- **p2-synthesize**: Per-topic try/catch with status rollback to "pending" on failure. Alert logging.
- **p2-images**: Per-article try/catch. 8s timeout on image downloads. 500ms delays between articles.
- **p2-orchestrate**: No error handling for individual stage failures — continues to next stage regardless.

### Pipeline Health Endpoint

`pipeline-health` provides a real-time health snapshot:
- Per-agent status (healthy/warning/degraded)
- Queue depth by status
- Stuck jobs (locked or stalled > 30 min)
- DLQ depth (total + last 24h)
- Recent alerts (last hour)
- Recent pipeline runs

---

## 9. Entity System

The entity system exists primarily for deduplication in `p2-rank`:

### Extraction
- **Gemini-provided**: `key_entities` array in topic clustering response, with disambiguated entity IDs (e.g., `vijay-politician-tamil-nadu` vs `vijay-deverakonda-actor-telugu`)
- **Regex-based**: `PROPER_NOUN_RE` extracts 1-3 word capitalized phrases, filtered against stopwords

### Deduplication Logic
- Combines Gemini entities + regex entities, lowercased
- Compares against recent topics (48h) and published articles
- Politics/news: 3+ shared entities = duplicate
- Other verticals: 2+ shared entities = duplicate
- Breaking urgency bypasses dedup entirely

### Database Tables
- `videshi_entities` — Entity definitions (appears unused in current code)
- `videshi_topic_entities` — Entity-to-topic mapping (appears unused)
- `videshi_event_fingerprints` — Event dedup hashes (appears unused)

**Note**: The `videshi_entities` tables appear to be schema-only — the actual dedup logic operates inline in `p2-rank` without reading from or writing to these entity tables.

---

## 10. Supporting Edge Functions

### admin-pipeline-write
Secure write proxy for admin UI. Authenticates via `x-admin-key` header against `VIDESHI_API_KEY` env var. Allows insert/update/delete on: `p2_feed_sources`, `p2_topics`, `p2_articles`, `videshi_sources`. All pipeline admin writes flow through this function to keep table writes restricted to the service role.

### admin-pin-article
Pin/unpin featured articles for N hours (default 24). Uses `x-admin-key` auth. Updates `is_pinned_featured` and `pinned_until` on the legacy `articles` table. **Bug**: Targets `articles` table, not `p2_articles` — may not work with v2 pipeline data.

### get-article
Public API endpoint for fetching a single article by slug. Authenticated via `x-videshi-key` header or `?key=` query param. In-memory rate limiter (60 req/min per IP). Maps `p2_articles` fields to legacy field names for API consumers.

### send-contact-email
Contact form handler. Validates inputs, sends email via Resend API to `editor@thevideshi.com`. No CAPTCHA or rate limiting beyond basic validation.

### unsplash-hero
Homepage carousel image refresh. Primary source: The News API (top world headlines with images). Fallback: Unsplash if < 5 usable images. Each image scored by Claude Haiku Vision (reject < 7). Stores daily set in `carousel_images` table, replaces entirely on each run.

### recaption-images
One-time batch operation: regenerates `image_caption` for all published articles via Claude Haiku Vision. Targets legacy `articles` table.

### rehost-images
One-time batch: downloads all external article images to Supabase Storage. Targets legacy `articles` table.

### reverify-images
One-time batch: re-evaluates and potentially replaces images using Claude Haiku for query generation + Unsplash + Claude Vision scoring. Targets legacy `articles` table. Records pipeline run.

### compare-models
Development tool: runs the same synthesis prompt through Claude Sonnet 4.6, Gemini 2.5 Pro, and GPT-5 (via Lovable gateway) in parallel. Returns raw outputs + timings for comparison.

### gemini-test
Test function for Gemini API. **Bug**: Has a duplicate `const data = await response.json()` line that would cause a runtime error.

---

## 11. Configuration & Deployment

### Vercel (`vercel.json`)
```json
{ "rewrites": [{ "source": "/(.*)", "destination": "/index.html" }] }
```
SPA fallback — all routes serve index.html, client-side routing handles the rest.

### Vercel Edge Middleware (`middleware.ts`)
- Matches `/articles/:slug*` routes
- Fetches article from Supabase REST API using anon key
- Injects OG/Twitter meta tags into the HTML shell
- 300s CDN cache with stale-while-revalidate
- **Note**: Queries legacy `articles` table (not `p2_articles`), so OG tags may not work for v2 articles

### Vite (`vite.config.ts`)
- Uses `@vitejs/plugin-react-swc` (SWC compiler for faster builds)
- `lovable-tagger` plugin in development mode
- Path alias: `@` → `./src`
- Dedupe array for React, React DOM, and TanStack Query (prevents multiple instances)

### Supabase (`config.toml`)
- All edge functions set `verify_jwt = false` (public endpoints)
- Missing from config: `p2-ingest`, `p2-rank`, `p2-synthesize`, `p2-images`, `admin-pipeline-write`, `get-article`, `compare-models`, `ingest-conversation-india`

### Environment Variables (Required)
| Variable | Used By |
|----------|---------|
| `SUPABASE_URL` / `VITE_SUPABASE_URL` | Frontend client, edge functions |
| `SUPABASE_SERVICE_ROLE_KEY` | All edge functions |
| `ANTHROPIC_API_KEY` | p2-synthesize, p2-images, all agent-* functions |
| `GEMINI_API_KEY` | p2-rank |
| `UNSPLASH_ACCESS_KEY` | p2-images, agent-images, reverify-images |
| `PEXELS_API_KEY` | p2-images, agent-images |
| `PIXABAY_API_KEY` | p2-images (optional) |
| `VIDESHI_API_KEY` | admin-pipeline-write, admin-pin-article, get-article |
| `RESEND_API_KEY` | send-contact-email, resilience alerts |
| `NEWS_API_KEY` | unsplash-hero |
| `RSS2JSON_KEY` | p2-ingest (declared but unused) |

---

## 12. Notable Patterns

### Smart Defaults
- Articles auto-publish when both confidence and diaspora scores are high enough, reducing editorial bottleneck
- Topic dedup uses entity-aware comparison with vertical-specific thresholds
- Image sourcing prioritizes free/open-source images with government source bonuses

### Category Mapping
Two separate mapping systems:
- `VERTICAL_TO_CATEGORY` in edge functions maps internal verticals (politics, economy, etc.) to frontend categories (news, markets-finance, etc.)
- `categories.ts` in frontend defines the full category taxonomy including `hasPipeline` flag for categories that have automated content

### Hardcoded Event Clusters
The homepage event clustering (`Index.tsx`) uses hardcoded cluster definitions for major ongoing stories (Tamil Nadu politics, Bengal BJP, Kerala CM, Gulf Crisis, IPL, H-1B). These need manual updates as events evolve.

### Dual Source Tables
- `videshi_sources` — Comprehensive source registry with pipeline stages, legal metadata, proxy settings
- `p2_feed_sources` — Simpler feed-only table
- `p2-ingest` reads from `videshi_sources` but normalizes to the `p2_feed_sources` field names. The admin dashboard manages both tables independently.

### Admin Auth
Admin authentication is a simple shared secret (`VIDESHI_API_KEY`), stored in localStorage on the client. No user accounts, sessions, or RBAC.

---

## 13. Issues & Improvement Areas

### Critical Bugs

1. **`gemini-test` has duplicate variable declaration**: `const data = await response.json()` appears twice, causing a runtime error.

2. **`admin-pin-article` targets wrong table**: Updates `articles` (v1) instead of `p2_articles` (v2). Pinning won't affect current pipeline articles.

3. **Middleware OG tags target wrong table**: `middleware.ts` queries the legacy `articles` table for OG tag injection. V2 articles in `p2_articles` won't get proper social media previews.

4. **`p2-orchestrate` exposes anon key in source code**: The Supabase anon key is hardcoded in the function. While anon keys are designed to be public, the function also hardcodes the full base URL making it easy to enumerate all function endpoints.

5. **ArticleCarousel links use wrong path**: Links to `/article/${slug}` (singular) but the router expects `/articles/${slug}` (plural). Carousel links would 404.

### Security Concerns

6. **All edge functions have `verify_jwt = false`**: Every function is publicly accessible. While admin functions check `x-admin-key`, the pipeline functions (p2-ingest, p2-rank, p2-synthesize, p2-images) can be invoked by anyone.

7. **No CSRF/rate limiting on contact form**: `send-contact-email` has no CAPTCHA, rate limiting, or bot protection. Susceptible to spam.

8. **Admin key in localStorage**: `videshi-admin-key` stored unencrypted in browser localStorage. XSS vulnerability could expose it.

### Architecture Issues

9. **Legacy vs v2 data split**: The codebase has two complete parallel systems. Frontend `articles.ts` reads from `p2_articles`, but several edge functions and middleware still reference the legacy `articles` table. This creates confusion and potential data inconsistencies.

10. **No scheduled execution**: `p2-orchestrate` isn't listed in any cron/scheduler configuration. The pipeline requires manual triggering or external scheduling.

11. **Hardcoded event clusters**: Homepage clusters are manually coded for specific current events (Tamil Nadu politics, IPL 2026). These will become stale and need regular updates.

12. **RSS parser is regex-based**: The XML parser in `p2-ingest` uses regex patterns which can break on malformed feeds, nested CDATA, or unusual XML structures. A proper XML parser (like `fast-xml-parser` used in `ingest-conversation-india`) would be more robust.

13. **Single-point-of-failure orchestration**: `p2-orchestrate` runs stages sequentially with fixed delays. If `p2-rank` takes longer than expected, `p2-synthesize` runs before ranking is complete. No event-driven triggering.

### Performance

14. **N+1 queries in p2-rank**: Each topic insert is a separate database call, followed by a separate `p2_topic_signals` upsert. Could batch these.

15. **No pagination on homepage data**: Fetches up to 18 India News + 12 World News + 12 × 7 category articles = 114 articles on initial page load.

16. **Image vision scoring is sequential per candidate**: `p2-images` scores each image candidate individually with a separate Claude API call. Could batch or use concurrent scoring.

### Data Quality

17. **No content validation on synthesis**: Articles are auto-published based solely on confidence + diaspora score thresholds. No fact-checking, plagiarism detection, or content policy screening.

18. **Carousel photo suggestions are generic**: Gemini generates carousel photos without access to actual article images. The suggestion quality depends on Gemini's training data knowledge of recent events.

19. **Source hunt matching is basic**: `findSourceHunts()` matches by checking if any keyword appears in the hunt title. No semantic similarity or relevance scoring.

### Cleanup Needed

20. **Dead code**: Multiple legacy edge functions (`agent-writer`, `agent-editor`, `agent-enricher`, `agent-scout`, `agent-cleanup`, `process-stories`, `ingest-rss`) are still deployed but presumably unused since v2 took over. These consume resources and increase the attack surface.

21. **Inconsistent model references**: Code references `claude-sonnet-4-6`, `claude-haiku-4-5-20251001`, `claude-haiku-4-5`, and `claude-3-5-haiku-20241022` across different functions. Should standardize.

22. **Unused database tables**: `videshi_entities`, `videshi_topic_entities`, `videshi_event_fingerprints` exist in the schema but aren't read or written by any current code.

23. **`recaption-images`, `rehost-images`, `reverify-images`** are one-time migration scripts that should be removed after use.

### Recommended Priority Fixes

1. Fix ArticleCarousel link path (`/article/` → `/articles/`)
2. Update `middleware.ts` to query `p2_articles` for OG tags
3. Update `admin-pin-article` to target `p2_articles`
4. Set up scheduled execution for `p2-orchestrate` (Supabase cron or external)
5. Add JWT verification or IP allowlisting to pipeline functions
6. Remove or archive legacy v1 edge functions
7. Fix `gemini-test` duplicate variable declaration

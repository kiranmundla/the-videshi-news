# Media Library — backup pool for The Videshi

A deliberate, growing, **quality-gated, attribution-clean** pool of **high-quality
images AND videos** that articles and reels fall back to when X / Threads /
Instagram or dynamic search yields nothing better. Auto-kept-fresh from the
entities/keywords in newly published articles.

## Why
Real, credited imagery over generic stock — with a graceful fallback so a reel
or article is never stuck without a usable, on-brand, copyright-clean asset.

## Components

| File | Role |
|------|------|
| `migration-media-library.sql` | One-time `media_library` table DDL (run in Supabase SQL editor). |
| `media_library_store.py` | Shared module: env, JSON-mirror I/O, Supabase upsert/upload, **quality gates + scoring**, download/probe helpers. |
| `media-library-enqueue.py` | **Freshness loop.** Scans recent articles, extracts subjects, enqueues uncovered ones to `media-library-queue.json`. |
| `media-library-source.py` | **Sourcing.** Works the queue: Wikimedia Commons → PIB → (opt-in) Pexels concept tier; gates, uploads, captions, scores, persists. |
| `media_library_lookup.py` | **Fallback hook** for article writers + reel pipeline: `find_media(...)`. |
| `media-library.json` | JSON mirror of the library (durable; pipeline reads this without a DB round-trip). |
| `media-library-queue.json` | Article-driven subject queue. |

## Data model (`media_library` table + JSON mirror)
`id, media_type('image'|'video'), url (Supabase-hosted), thumb_url, subject,
subject_type('person'|'place'|'thing'|'event'|'concept'), caption, attribution,
license, source_url, tags[], width, height, duration(sec; null for images),
quality_score, added_date, last_used, times_used`

- **Storage bucket:** existing public `article-images` bucket, under the
  `media-library/<subject_type>/` prefix. URLs are Supabase-hosted so they never
  rot. (Storage uploads send BOTH `apikey` and `Authorization: Bearer` headers —
  required by the new `sb_secret_` key, per AGENTS.md.)
- **Table is optional at runtime:** if `media_library` doesn't exist yet, the
  scripts run fully on the JSON mirror and `upsert_table()` is a no-op. Run the
  SQL to enable DB-side querying. (No `exec_sql` RPC exists on this project, so
  the table must be created manually.)

## Quality gates (HARD — Kiran's top requirement)
Enforced in `media_library_store.py` and re-verified from the downloaded file
(not just API metadata):
- **Images:** longest side **≥ 1600px** (rejects small/upscaled).
- **Videos:** short side **≥ 720px** (prefer 1080p) AND **4s ≤ duration ≤ 90s**.
- Anything failing the gate is rejected — *better to store nothing than store
  low-res.*
- `quality_score` (0–100) = resolution component × source-trust weight
  (Wikimedia/PIB > Openverse > Pexels).

## Attribution (every asset)
- **Wikimedia Commons:** caption from the Commons description; attribution
  `"Wikimedia Commons / <Artist>, <License>"`; non-free/fair-use licenses are
  rejected (CC / public-domain / GODL only).
- **PIB:** ready-made caption; `"Press Information Bureau (PIB), Government of
  India / GODL-India"`.
- **Pexels (concept tier only):** `"Pexels / <photographer>"`, `Pexels License`.

## Fallback-priority contract (the CALLER enforces ordering)
```
1. X / Threads / Instagram social card  OR  dynamic search   → FIRST
2. media_library  (find_media)                               → SECOND
3. existing chain (Pexels generic, etc.)                     → LAST
```
**Article photos** must call `find_media(..., exclude_concept=True)` (the
default) so generic `concept` stock is never used as an article image. Reel
b-roll scenes that explicitly want abstract footage pass
`exclude_concept=False`.

### `find_media(...)` signature
```python
from media_library_lookup import find_media
asset = find_media(subject=None, tags=None, subject_type=None,
                   media_type=None, min_quality=0,
                   exclude_concept=True, bump_usage=True)
# → best match (highest quality_score, then least-recently-used) or None.
# Bumps last_used/times_used in mirror + table unless bump_usage=False.
```

## The freshness loop (Kiran's directive)
New articles publish → `media-library-enqueue.py` extracts subjects
(registry persons/orgs, a places gazetteer, the article `tags`/`image_entities`/
`image_search_query` columns) → enqueues any not already covered →
`media-library-source.py` fills them. The list of things we source media for
keeps growing automatically as articles are written. No manual curation.

> Note: the capitalized-noun-phrase headline heuristic is intentionally
> **disabled** — Videshi headlines are title-cased, so it produced sentence-
> fragment noise. Reliable signals only (registry names, places, tags, entity
> columns).

## Proposed cron (REVIEW BEFORE SCHEDULING — not auto-registered)
Daily, low-volume. Enqueue runs after the article writers; sourcing follows.

**Job 1 — enqueue (daily 09:10 UTC):**
```
cron add
  id: media-library-enqueue
  mode: task
  schedule: { kind: daily, time: "09:10", timezone: "UTC" }
  body: |
    cd ~/workspace/the-videshi-news/pipeline && python3 media-library-enqueue.py --hours 26 --limit 40
```

**Job 2 — source images (daily 09:25 UTC), capped:**
```
cron add
  id: media-library-source-images
  mode: task
  timeout_secs: 1800
  schedule: { kind: daily, time: "09:25", timezone: "UTC" }
  body: |
    cd ~/workspace/the-videshi-news/pipeline && python3 media-library-source.py --max 25 --per-subject 2
```

**Job 3 — source videos (weekly Sun 09:45 UTC), small cap (heavier downloads):**
```
cron add
  id: media-library-source-videos
  mode: task
  timeout_secs: 2400
  schedule: { kind: weekly, time: "09:45", dow: ["Sun"], timezone: "UTC" }
  body: |
    cd ~/workspace/the-videshi-news/pipeline && python3 media-library-source.py --max 10 --per-subject 0 --videos
```

(Add `--allow-pexels` to a job only if you want the generic concept tier topped
up; it's off by default so the library stays Wikimedia/PIB-first.)

## Manual ops
```bash
# Seed/source specific subjects on demand:
python3 media-library-source.py --subjects "Narendra Modi:person,Mumbai:place,Indian rupee:concept" --per-subject 2
python3 media-library-source.py --subjects "Mumbai:place" --videos --per-subject 0   # video only

# Inspect a lookup:
python3 media_library_lookup.py "Mumbai"

# Refresh the queue from the last 3 days:
python3 media-library-enqueue.py --hours 72 --limit 40
```

## Known risks / follow-ups
- **Keyword-relevance for persons:** Commons search is keyword-based, so a query
  like "Narendra Modi" can surface "Narendra Modi Stadium." Captions are honest
  about what the asset is, but a future improvement is to prefer Commons
  *category* pages or Wikipedia lead images for `subject_type=person`.
- **PIB direct images:** the PIB index stores gallery pages, not direct CDN image
  URLs, so PIB currently yields assets only when a direct `image_url` is present.
  Commons is the primary high-res path; extending PIB to resolve gallery → image
  is a possible follow-up.
- **Wikimedia rate limits:** the upload host intermittently 429s; downloads now
  retry (3×) with backoff. Keep run caps low.
- **Wiring not done here:** `find_media` is the clean hook, but wiring it into the
  article writers and the reel pipeline (`shotstack-reel.py`) is a *separate*
  task, deliberately deferred so two builds don't edit the same production files
  at once.

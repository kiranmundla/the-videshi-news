#!/usr/bin/env python3
"""
Pre-build static JSON feeds for The Videshi homepage and article pages.

Fetches published articles from Supabase, transforms them to match the
front-end Article type (same shape as mapRow in src/lib/articles.ts),
and writes:
  - public/data/homepage-feed.json  (all homepage sections in one file)
  - public/data/articles/{slug}.json  (individual article detail pages)

This eliminates 14+ Supabase API round-trips on homepage load and 1 per
article page, letting Vercel serve everything from its CDN.
"""

import json
import os
import sys
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path

import time
import requests

# ── Resilient HTTP ────────────────────────────────────────────────────
# The large Supabase fetches occasionally die mid-stream on transient proxy
# drops (ChunkedEncodingError / ConnectionError) or brief 5xx. A single
# hiccup must NOT silently fail the whole feed rebuild, so retry with backoff.
def _get_with_retry(get_url: str, *, headers: dict, params: dict | None = None,
                    attempts: int = 5, base_delay: float = 1.5) -> requests.Response:
    last_exc = None
    for attempt in range(1, attempts + 1):
        try:
            resp = requests.get(get_url, headers=headers, params=params, timeout=60)
            # Retry on transient server-side errors; return everything else
            # (including 4xx) to the caller to handle as before.
            if resp.status_code >= 500 or resp.status_code == 429:
                last_exc = RuntimeError(f"HTTP {resp.status_code}")
                if attempt < attempts:
                    time.sleep(base_delay * attempt)
                    continue
            return resp
        except (requests.exceptions.ChunkedEncodingError,
                requests.exceptions.ConnectionError,
                requests.exceptions.Timeout) as e:
            last_exc = e
            if attempt < attempts:
                time.sleep(base_delay * attempt)
                continue
            raise
    if last_exc:
        raise last_exc
    raise RuntimeError("unreachable retry state")

# ── Config ────────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "public" / "data"
ARTICLES_DIR = DATA_DIR / "articles"
CATEGORY_DIR = DATA_DIR / "category"
PAGE_SIZE_CAT = 18  # fallback to wider window if fewer than this in 72h
HOMEPAGE_FEED = DATA_DIR / "homepage-feed.json"

# Supabase columns to fetch (mirrors P2_COLS in articles.ts)
P2_COLS = (
    "id,slug,headline,subheadline,body,vertical,category,status,"
    "is_featured,published_at,event_at,created_at,sources,diaspora_angle,tags,"
    "image_url,image_attribution,image_caption,gallery_images,social_embeds,score_total,"
    "newsworthiness,diaspora_impact,prominence,article_type,"
    "google_cluster_size,signal_count,focal_x,focal_y,llm_score"
)
# Lightweight version without body (for homepage/category feeds where body is stripped anyway)
P2_COLS_NO_BODY = (
    "id,slug,headline,subheadline,vertical,category,status,"
    "is_featured,published_at,event_at,created_at,sources,diaspora_angle,tags,"
    "image_url,image_attribution,image_caption,gallery_images,social_embeds,score_total,"
    "newsworthiness,diaspora_impact,prominence,article_type,"
    "google_cluster_size,signal_count,focal_x,focal_y,llm_score"
)

# Homepage section config (mirrors Index.tsx constants)
INDIA_NEWS = {"slug": "news", "limit": 18}
WORLD_NEWS = {"slug": "nri-world", "limit": 12}
CATEGORY_SECTIONS = [
    {"slug": "immigration", "limit": 12},
    {"slug": "markets-finance", "limit": 12},
    {"slug": "sports", "limit": 12},
    {"slug": "technology", "limit": 12},
    {"slug": "entertainment", "limit": 12},
    {"slug": "lifestyle-health", "limit": 12},
    {"slug": "food", "limit": 12},
    {"slug": "travel", "limit": 12},
]
CAROUSEL_CATEGORIES = ["immigration", "news", "entertainment", "sports", "technology", "markets-finance"]

MAX_ARTICLE_PAGES = 5000  # Pre-build individual article JSONs for all published articles


# ── Supabase helpers ──────────────────────────────────────────────────

def load_env():
    """Load Supabase creds from env file."""
    env_path = Path.home() / "workspace" / ".env.supabase"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_ANON_KEY")
    if not url or not key:
        print("ERROR: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY required", file=sys.stderr)
        sys.exit(1)
    return url, key


def fetch_all_published(url: str, key: str, include_body: bool = True,
                        since: str | None = None) -> list[dict]:
    """Fetch published articles from Supabase, newest first.
    
    If include_body=False, fetches without body text (much faster for listings).
    If since is set (ISO timestamp), only fetches articles published after that date.
    """
    headers = {"apikey": key, "Authorization": f"Bearer {key}"}
    all_rows = []
    offset = 0
    batch = 500
    cols = P2_COLS if include_body else P2_COLS_NO_BODY

    while True:
        params = {
            "select": cols,
            "status": "eq.published",
            "order": "published_at.desc,id.asc",
            "offset": str(offset),
            "limit": str(batch),
        }
        if since:
            params["published_at"] = f"gte.{since}"
        resp = _get_with_retry(f"{url}/rest/v1/p2_articles", headers=headers, params=params)
        resp.raise_for_status()
        rows = resp.json()
        if not rows:
            break
        all_rows.extend(rows)
        if len(rows) < batch:
            break
        offset += batch

    print(f"  Fetched {len(all_rows)} published articles from Supabase"
          f" ({'with' if include_body else 'without'} body"
          f"{f', since {since[:10]}' if since else ''})")
    return all_rows


def fetch_table(url: str, key: str, table: str, order: str = "id.asc",
                filters: dict | None = None, select: str = "*") -> list[dict]:
    """Generic paginated fetch from any Supabase table."""
    headers = {"apikey": key, "Authorization": f"Bearer {key}"}
    all_rows = []
    offset = 0
    batch = 500

    while True:
        params: dict = {
            "select": select,
            "order": order,
            "offset": str(offset),
            "limit": str(batch),
        }
        if filters:
            params.update(filters)
        resp = _get_with_retry(f"{url}/rest/v1/{table}", headers=headers, params=params)
        resp.raise_for_status()
        rows = resp.json()
        if not rows:
            break
        all_rows.extend(rows)
        if len(rows) < batch:
            break
        offset += batch

    return all_rows


# ── Transform (mirrors mapRow in articles.ts) ────────────────────────

def parse_sources(raw) -> list | None:
    """Parse sources array, matching parseSources() in articles.ts."""
    if not raw or not isinstance(raw, list):
        return None
    result = []
    for s in raw:
        if isinstance(s, str):
            result.append({"label": s})
        elif isinstance(s, dict):
            url_val = str(s["url"]) if s.get("url") else None
            label = s.get("name") or s.get("label") or s.get("title") or url_val or "Source"
            entry = {"label": label}
            if url_val:
                entry["url"] = url_val
            result.append(entry)
    return result if result else None


def parse_gallery_images(raw) -> list | None:
    """Parse gallery_images array, matching parseGalleryImages() in articles.ts."""
    if not raw or not isinstance(raw, list) or len(raw) == 0:
        return None
    return [
        {"url": item["url"], "caption": item.get("caption", "")}
        for item in raw
        if isinstance(item, dict) and isinstance(item.get("url"), str)
    ]


def derive_excerpt(subheadline: str | None, body: str) -> str:
    """Derive excerpt, matching deriveExcerpt() in articles.ts."""
    if subheadline and subheadline.strip():
        return subheadline.strip()
    plain = re.sub(r"[#*_>`~\-]+", "", (body or "")).strip()
    if not plain:
        return ""
    return plain[:217].rstrip() + "…" if len(plain) > 220 else plain


def _compute_display_score(row: dict) -> float:
    """Compute display score from newsworthiness + prominence + diaspora + freshness.
    Falls back to legacy score_total when new columns are NULL.
    """
    nw = row.get("newsworthiness")
    di = row.get("diaspora_impact")
    prom = row.get("prominence")

    # If new scores aren't populated yet, fall back to legacy score_total + freshness
    # so unscored recent articles still outrank scored stale ones
    if nw is None and di is None:
        base = float(row.get("score_total") or 0)
        # Add freshness for unscored articles so today's content isn't buried
        pub = row.get("published_at") or row.get("created_at", "")
        age_freshness = 0.0
        if pub:
            try:
                pub_dt = datetime.fromisoformat(pub.replace("Z", "+00:00"))
                hours_old = (datetime.now(timezone.utc) - pub_dt).total_seconds() / 3600
                # 40 points decaying over 24 hours — ensures a fresh unscored article
                # (40pts) outranks a day-old scored one (score_total typically 30-50)
                age_freshness = 40.0 * max(0.0, 1.0 - hours_old / 24.0)
            except (ValueError, TypeError):
                pass
        llm = row.get("llm_score") or 0
        return base + age_freshness + llm * 5.0

    nw = nw or 15  # default mid-range
    di = di or 10
    prom = prom or 8

    # Freshness decay: 30 points, decays to 0 over 16 hours
    # Steeper curve so newer articles overtake older high-scored ones within hours
    pub = row.get("published_at") or row.get("created_at", "")
    freshness = 0.0
    if pub:
        try:
            pub_dt = datetime.fromisoformat(pub.replace("Z", "+00:00"))
            hours_old = (datetime.now(timezone.utc) - pub_dt).total_seconds() / 3600
            freshness = 30.0 * max(0.0, 1.0 - hours_old / 16.0)
        except (ValueError, TypeError):
            freshness = 0.0

    # Breaking news bonus: high newsworthiness + fresh = extra boost
    breaking_bonus = 0.0
    if nw >= 24 and freshness >= 18:  # newsworthiness 24+ and < ~3h old
        breaking_bonus = 15.0

    # Follow-up penalty: deprioritize articles covering already-reported topics
    followup_penalty = 0.0
    article_type = row.get("article_type") or "breaking"
    if article_type in ("follow-up", "analysis"):
        followup_penalty = -15.0

    # LLM importance boost: 0-25 points based on llm_score (0-5)
    llm = row.get("llm_score") or 0
    llm_boost = llm * 5.0  # score 5 = 25pts, score 3 = 15pts

    return nw + prom + di + freshness + breaking_bonus + followup_penalty + llm_boost


def map_row(row: dict) -> dict:
    """Transform a Supabase p2_articles row to the front-end Article shape."""
    return {
        "id": row["id"],
        "slug": row.get("slug") or row["id"],
        "title": row.get("headline", ""),
        "excerpt": derive_excerpt(row.get("subheadline"), row.get("body", "")),
        "body": row.get("body") or "",
        "category": row.get("category") or row.get("vertical") or "",
        "hero_image_url": row.get("image_url") or "",
        "image_caption": row.get("image_caption"),
        "image_credit": row.get("image_attribution"),
        "gallery_images": parse_gallery_images(row.get("gallery_images")),
        "published_at": row.get("published_at") or row.get("created_at", ""),
        "created_at": row.get("created_at", ""),
        "status": "published" if row.get("status") == "published" else "draft",
        "sources": parse_sources(row.get("sources")),
        "nri_angle": row.get("diaspora_angle"),
        "article_type": row.get("article_type") or "breaking",
        "tags": row.get("tags") if isinstance(row.get("tags"), list) else None,
        "author": "Diaspora Desk",
        "featured_score": _compute_display_score(row),
        "is_pinned_featured": bool(row.get("is_featured")),
        "pinned_until": None,
        "event_at": row.get("event_at"),
        "focal_x": row.get("focal_x", 0.5),
        "focal_y": row.get("focal_y", 0.5),
        "social_embeds": row.get("social_embeds") or [],
    }


def article_without_body(a: dict) -> dict:
    """Return article dict without body (for homepage feed, saves size)."""
    import re, math
    body = a.get("body", "")
    text = re.sub(r'[#*_>`~\-\[\]{}]+', '', body).strip()
    words = len([w for w in text.split() if w])
    reading_time = max(1, round(words / 225))
    out = {k: v for k, v in a.items() if k != "body"}
    out["reading_time"] = reading_time
    return out


def fetch_editorial(url: str, key: str) -> dict | None:
    """Fetch the latest is_editorial=true article from Supabase."""
    headers = {"apikey": key, "Authorization": f"Bearer {key}"}
    resp = _get_with_retry(
        f"{url}/rest/v1/p2_articles",
        headers=headers,
        params={
            "select": P2_COLS_NO_BODY,
            "status": "eq.published",
            "is_editorial": "eq.true",
            "order": "published_at.desc",
            "limit": "1",
        },
    )
    if resp.status_code != 200:
        return None
    rows = resp.json()
    if not rows:
        return None
    return map_row(rows[0])


# ── Homepage feed builder ─────────────────────────────────────────────

def build_homepage_feed(articles: list[dict], url: str = "", key: str = "") -> dict:
    """Build the homepage-feed.json structure."""
    now = datetime.now(timezone.utc)
    since_72h = (now - timedelta(hours=72)).isoformat()
    since_7d = (now - timedelta(days=7)).isoformat()

    # Fetch article IDs already in active developing stories — exclude from featured/hero
    storyline_article_ids: set[str] = set()
    if url and key:
        try:
            active_storylines = fetch_table(url, key, "storylines",
                                            select="id",
                                            filters={"status": "in.(emerging,active,cooling)"})
            if active_storylines:
                # Batch fetch: get ALL storyline_articles in one query instead of N+1
                sl_ids = [s["id"] for s in active_storylines]
                # PostgREST in() filter accepts comma-separated values in parens
                id_list = ",".join(sl_ids)
                all_links = fetch_table(url, key, "storyline_articles",
                                        select="article_id",
                                        filters={"storyline_id": f"in.({id_list})"})
                for link in all_links:
                    storyline_article_ids.add(link["article_id"])
            if storyline_article_ids:
                print(f"  📰 Excluding {len(storyline_article_ids)} developing-story articles from featured/hero")
        except Exception as e:
            print(f"  ⚠️  Could not fetch storyline articles: {e}")

    # Group articles by category
    by_cat: dict[str, list[dict]] = {}
    for a in articles:
        cat = a["category"]
        by_cat.setdefault(cat, []).append(a)

    def get_category_articles(slug: str, limit: int) -> list[dict]:
        """Get articles for a category, sorted by freshness (newest first), preferring recent (72h), fallback to 7d."""
        pool = [a for a in by_cat.get(slug, []) if a["id"] not in storyline_article_ids]
        recent = [a for a in pool if a["published_at"] >= since_72h]
        recent.sort(key=lambda a: a["published_at"], reverse=True)
        if len(recent) >= 3:
            return [article_without_body(a) for a in recent[:limit]]
        wider = [a for a in pool if a["published_at"] >= since_7d]
        wider.sort(key=lambda a: a["published_at"], reverse=True)
        if len(wider) > len(recent):
            return [article_without_body(a) for a in wider[:limit]]
        return [article_without_body(a) for a in recent[:limit]]

    # Featured article: most recent 24h with image and highest LLM importance score
    since_24h = (now - timedelta(hours=24)).isoformat()
    recent_24h = [a for a in articles if a["published_at"] >= since_24h]
    # Sort by LLM score first, then Google cluster size, freshness as tiebreaker
    recent_24h.sort(key=lambda a: (
        a.get("llm_score") or 0,
        a.get("google_cluster_size") or 0,
        a.get("event_at") or a["published_at"],
    ), reverse=True)
    # Categories that should never be the homepage hero
    _NO_FEATURED_CATS = {"food", "travel", "lifestyle-health"}
    featured = None
    for a in recent_24h:
        if a["hero_image_url"] and a.get("category") not in _NO_FEATURED_CATS and a["id"] not in storyline_article_ids:
            featured = article_without_body(a)
            break
    if not featured and recent_24h:
        featured = article_without_body(recent_24h[0])

    # Sections
    sections = {}
    sections["news"] = get_category_articles(INDIA_NEWS["slug"], INDIA_NEWS["limit"])
    sections["nri-world"] = get_category_articles(WORLD_NEWS["slug"], WORLD_NEWS["limit"])
    for sec in CATEGORY_SECTIONS:
        sections[sec["slug"]] = get_category_articles(sec["slug"], sec["limit"])

    # Interviews: ensure interview articles from the last 30 days always
    # appear in their category section so InterviewSpotlight picks them up.
    since_30d = (now - timedelta(days=30)).isoformat()
    interview_articles = [
        a for a in articles
        if a.get("article_type") == "interview"
        and a["published_at"] >= since_30d
        and a.get("hero_image_url")
    ]
    interview_articles.sort(key=lambda a: a["published_at"], reverse=True)
    for ia in interview_articles:
        cat = ia["category"]
        sec_list = sections.get(cat, [])
        existing_ids = {a["id"] for a in sec_list}
        if ia["id"] not in existing_ids:
            sec_list.append(article_without_body(ia))
            sections[cat] = sec_list

    # Carousel: top 1 article with image from each carousel category
    seen_ids = set()
    carousel = []
    for cat in CAROUSEL_CATEGORIES:
        cat_articles = get_category_articles(cat, 10)  # get more to find one with image
        for a in cat_articles:
            if a["hero_image_url"] and a["id"] not in seen_ids:
                carousel.append(a)
                seen_ids.add(a["id"])
                break

    # Editorial pick: article with is_editorial=true (manually curated)
    editorial_article = fetch_editorial(url, key)
    editorial = article_without_body(editorial_article) if editorial_article else None

    return {
        "generated_at": now.isoformat(),
        "featured": featured,
        "editorial": editorial,
        "just_in": _build_just_in(articles, now),
        "sections": sections,
        "carousel": carousel,
    }


def _build_just_in(articles: list[dict], now: datetime) -> list[dict]:
    """Build the 'Just In' strip: 8 most recent articles, purely chronological,
    across all categories. No scoring — just freshness. Dedupes against featured.
    Uses event_at (when the event happened) instead of published_at (when we wrote it)."""
    since_48h = (now - timedelta(hours=48)).isoformat()
    recent = [a for a in articles
              if (a.get("event_at") or a["published_at"]) >= since_48h
              and a.get("hero_image_url")]
    recent.sort(key=lambda a: a.get("event_at") or a["published_at"], reverse=True)

    # Deduplicate headlines: skip articles whose first 6 headline words match an earlier one
    seen_prefixes: set[str] = set()
    deduped: list[dict] = []
    for a in recent:
        prefix = " ".join(a.get("title", "").split()[:6]).lower()
        if prefix in seen_prefixes:
            continue
        seen_prefixes.add(prefix)
        deduped.append(a)
        # Return 15 so the frontend filter (removes hero+sidebar overlap) still leaves 8+
        if len(deduped) >= 15:
            break

    return [article_without_body(a) for a in deduped]


# ── Hero image preload injection ──────────────────────────────────────

INDEX_HTML = REPO_ROOT / "index.html"


def optimize_image_url(url: str, width: int = 1200) -> str:
    """Return a bandwidth-optimized variant of the image URL."""
    if not url:
        return ""
    if "images.pexels.com" in url:
        base = url.split("?")[0]
        return f"{base}?auto=compress&cs=tinysrgb&w={width}&fit=crop"
    return url


def inject_hero_preload(hero_url: str) -> None:
    """Inject a <link rel="preload"> for the hero image into index.html.

    Idempotent: removes any previous hero-preload tag first.
    """
    if not hero_url or not INDEX_HTML.exists():
        return

    html = INDEX_HTML.read_text()
    # Remove any existing hero preload
    html = re.sub(r'<link rel="preload"[^>]*data-hero-preload[^>]*/>\n?', "", html)
    # Build the preload tag
    optimized = optimize_image_url(hero_url)
    preload_tag = f'<link rel="preload" as="image" fetchpriority="high" href="{optimized}" data-hero-preload />\n'
    # Replace comment marker or fall back to inserting before </head>
    if "<!-- HERO_PRELOAD -->" in html:
        html = html.replace("<!-- HERO_PRELOAD -->", preload_tag.strip())
    else:
        html = html.replace("</head>", f"    {preload_tag}  </head>")

    INDEX_HTML.write_text(html)
    print(f"  ✓ Hero preload injected: {optimized[:80]}...")


# ── Main ──────────────────────────────────────────────────────────────

def main():
    print("=== Videshi Feed Pre-builder ===")
    load_env()
    url = os.environ["SUPABASE_URL"]
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ["SUPABASE_ANON_KEY"]

    # Fetch all published articles WITHOUT body (fast — for homepage/category feeds)
    raw_rows = fetch_all_published(url, key, include_body=False)
    if not raw_rows:
        print("  WARNING: No published articles found, skipping prebuild")
        return

    articles = [map_row(r) for r in raw_rows]

    # 1. Build homepage feed
    print("  Building homepage-feed.json...")
    feed = build_homepage_feed(articles, url, key)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    HOMEPAGE_FEED.write_text(json.dumps(feed, ensure_ascii=False, separators=(",", ":")))
    feed_size = HOMEPAGE_FEED.stat().st_size
    print(f"  ✓ homepage-feed.json ({feed_size:,} bytes, {len(feed['sections'])} sections, carousel: {len(feed['carousel'])})")

    # 1b. Hero image preload injection — disabled (was causing PageSpeed variance
    # because the preload URL could mismatch what React renders, and the preload
    # itself didn't help since LCP element is the headline text, not the image)
    # hero_url = (feed.get("featured") or {}).get("hero_image_url", "")
    # if not hero_url and feed.get("carousel"):
    #     hero_url = feed["carousel"][0].get("hero_image_url", "")
    # inject_hero_preload(hero_url)

    # 2. Build per-category feeds
    print("  Building category feeds...")
    CATEGORY_DIR.mkdir(parents=True, exist_ok=True)
    all_category_slugs = [
        "news", "nri-world", "sports", "entertainment", "technology",
        "markets-finance", "lifestyle-health", "food",
    ]
    now = datetime.now(timezone.utc)
    since_7d = (now - timedelta(days=7)).isoformat()
    since_14d = (now - timedelta(days=14)).isoformat()

    by_cat: dict[str, list[dict]] = {}
    for a in articles:
        by_cat.setdefault(a["category"], []).append(a)

    cat_count = 0
    for slug in all_category_slugs:
        pool = by_cat.get(slug, [])
        # Same logic: 7d first, fallback to 14d
        recent = [a for a in pool if a["published_at"] >= since_7d]
        if len(recent) < PAGE_SIZE_CAT:
            wider = [a for a in pool if a["published_at"] >= since_14d]
            if len(wider) > len(recent):
                recent = wider
        # Include body=false for listing, keep up to 200 articles per category
        cat_feed = {
            "generated_at": now.isoformat(),
            "category": slug,
            "articles": [article_without_body(a) for a in recent[:200]],
        }
        path = CATEGORY_DIR / f"{slug}.json"
        path.write_text(json.dumps(cat_feed, ensure_ascii=False, separators=(",", ":")))
        cat_count += 1
        print(f"    {slug}: {len(cat_feed['articles'])} articles")

    print(f"  ✓ {cat_count} category feeds written")

    # 3. Build individual article pages (only recent articles — older ones keep existing JSONs)
    recent_cutoff = (now - timedelta(days=7)).isoformat()
    print(f"  Fetching recent articles with body (last 7 days)...")
    recent_raw = fetch_all_published(url, key, include_body=True, since=recent_cutoff)
    recent_articles = [map_row(r) for r in recent_raw]

    print(f"  Building article JSONs ({len(recent_articles)} recent)...")
    ARTICLES_DIR.mkdir(parents=True, exist_ok=True)

    # Track all known slugs (from the full lightweight fetch) for stale cleanup
    all_slugs = set()
    for a in articles:
        slug = a["slug"]
        if slug and slug != a["id"]:
            all_slugs.add(slug)

    # Only write JSONs for recent articles (they have body text)
    written = 0
    skipped = 0
    for a in recent_articles:
        slug = a["slug"]
        if not slug or slug == a["id"]:
            continue
        path = ARTICLES_DIR / f"{slug}.json"
        content = json.dumps(a, ensure_ascii=False, separators=(",", ":"))
        # Skip write if file already exists with identical content
        if path.exists():
            try:
                if path.read_text() == content:
                    skipped += 1
                    continue
            except Exception:
                pass
        path.write_text(content)
        written += 1

    # Remove article JSONs for articles that are no longer published at all
    removed = 0
    for existing in ARTICLES_DIR.glob("*.json"):
        if existing.stem not in all_slugs:
            existing.unlink()
            removed += 1

    print(f"  ✓ {written} article JSONs written, {skipped} unchanged, {removed} stale removed")

    # 4. Build cars.json
    print("  Building cars.json...")
    cars = fetch_table(url, key, "cars", order="sort_order.asc,name.asc")
    cars_path = DATA_DIR / "cars.json"
    cars_path.write_text(json.dumps(cars, ensure_ascii=False, separators=(",", ":")))
    print(f"  ✓ cars.json ({len(cars)} vehicles)")

    # 5. Build events.json (upcoming + recently past)
    print("  Building events.json...")
    cutoff = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%d")
    events = fetch_table(url, key, "events", order="date.asc",
                         filters={"date": f"gte.{cutoff}"})
    events_path = DATA_DIR / "events.json"
    events_path.write_text(json.dumps(events, ensure_ascii=False, separators=(",", ":")))
    print(f"  ✓ events.json ({len(events)} events)")

    # 5b. Build slim events-homepage.json (only fields the homepage strip needs, all upcoming)
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    upcoming = [e for e in events if e.get("date", "") >= today_str]
    slim_fields = ("id", "title", "date", "time", "venue_name", "city", "state", "category", "latitude", "longitude", "slug")
    slim_events = [{k: e.get(k) for k in slim_fields if e.get(k) is not None} for e in upcoming]
    slim_path = DATA_DIR / "events-homepage.json"
    slim_path.write_text(json.dumps(slim_events, ensure_ascii=False, separators=(",", ":")))
    print(f"  ✓ events-homepage.json ({len(slim_events)} events, {len(slim_path.read_bytes())} bytes)")

    # 6. Build directory.json
    print("  Building directory.json...")
    directory = fetch_table(url, key, "directory_listings",
                            order="featured.desc,rating.desc.nullslast")
    # Dedup by slug (safety net — DB should be clean but cache had 405 dupes)
    seen_slugs = set()
    deduped_dir = []
    for d in directory:
        s = d.get("slug", "")
        if s and s in seen_slugs:
            continue
        seen_slugs.add(s)
        deduped_dir.append(d)
    if len(deduped_dir) < len(directory):
        print(f"    ⚠ Removed {len(directory) - len(deduped_dir)} duplicate slugs")
    directory = deduped_dir
    directory_path = DATA_DIR / "directory.json"
    directory_path.write_text(json.dumps(directory, ensure_ascii=False, separators=(",", ":")))
    print(f"  ✓ directory.json ({len(directory)} listings)")

    # 7. Build classifieds.json
    print("  Building classifieds.json...")
    classifieds = fetch_table(url, key, "classifieds", order="created_at.desc",
                              filters={"status": "eq.active"})
    classifieds_path = DATA_DIR / "classifieds.json"
    classifieds_path.write_text(json.dumps(classifieds, ensure_ascii=False, separators=(",", ":")))
    print(f"  ✓ classifieds.json ({len(classifieds)} classifieds)")

    # 8. Build visa-sightings.json (community-reported appointment sightings)
    print("  Building visa-sightings.json...")
    sightings = fetch_table(url, key, "visa_sightings",
                            order="created_at.desc",
                            filters={"status": "eq.published"})
    sightings = sightings[:100]  # cap at most recent 100
    sightings_path = DATA_DIR / "visa-sightings.json"
    sightings_path.write_text(json.dumps(sightings, ensure_ascii=False, separators=(",", ":")))
    print(f"  ✓ visa-sightings.json ({len(sightings)} sightings)")

    # 9. Build visa-wait-times.json (official consulate wait times)
    print("  Building visa-wait-times.json...")
    wait_times = fetch_table(url, key, "consulate_wait_times",
                             order="scraped_at.desc")
    wait_times_path = DATA_DIR / "visa-wait-times.json"
    wait_times_path.write_text(json.dumps(wait_times, ensure_ascii=False, separators=(",", ":")))
    print(f"  ✓ visa-wait-times.json ({len(wait_times)} rows)")

    # 10. Build instagram-embeds.json (portrait photo embeds for homepage)
    print("  Building instagram-embeds.json...")
    ig_embeds = fetch_table(url, key, "instagram_embeds",
                            order="likes.desc",
                            filters={"active": "eq.true"},
                            select="shortcode,account,category,likes,caption_preview")
    ig_path = DATA_DIR / "instagram-embeds.json"
    ig_path.write_text(json.dumps(ig_embeds, ensure_ascii=False, separators=(",", ":")))
    print(f"  ✓ instagram-embeds.json ({len(ig_embeds)} embeds)")

    print("=== Done ===")


if __name__ == "__main__":
    main()

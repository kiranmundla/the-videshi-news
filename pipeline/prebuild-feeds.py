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

import requests

# ── Config ────────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "public" / "data"
ARTICLES_DIR = DATA_DIR / "articles"
CATEGORY_DIR = DATA_DIR / "category"
HOMEPAGE_FEED = DATA_DIR / "homepage-feed.json"

# Supabase columns to fetch (mirrors P2_COLS in articles.ts)
P2_COLS = (
    "id,slug,headline,subheadline,body,vertical,category,status,"
    "is_featured,published_at,created_at,sources,diaspora_angle,tags,"
    "image_url,image_attribution,image_caption,gallery_images,score_total"
)

# Homepage section config (mirrors Index.tsx constants)
INDIA_NEWS = {"slug": "news", "limit": 18}
WORLD_NEWS = {"slug": "nri-world", "limit": 12}
CATEGORY_SECTIONS = [
    {"slug": "markets-finance", "limit": 12},
    {"slug": "sports", "limit": 12},
    {"slug": "technology", "limit": 12},
    {"slug": "entertainment", "limit": 12},
    {"slug": "lifestyle-health", "limit": 12},
    {"slug": "food", "limit": 12},
]
CAROUSEL_CATEGORIES = ["news", "entertainment", "sports", "technology", "markets-finance"]

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


def fetch_all_published(url: str, key: str) -> list[dict]:
    """Fetch all published articles from Supabase, newest first."""
    headers = {"apikey": key, "Authorization": f"Bearer {key}"}
    all_rows = []
    offset = 0
    batch = 500

    while True:
        params = {
            "select": P2_COLS,
            "status": "eq.published",
            "order": "published_at.desc,id.asc",
            "offset": str(offset),
            "limit": str(batch),
        }
        resp = requests.get(f"{url}/rest/v1/p2_articles", headers=headers, params=params)
        resp.raise_for_status()
        rows = resp.json()
        if not rows:
            break
        all_rows.extend(rows)
        if len(rows) < batch:
            break
        offset += batch

    print(f"  Fetched {len(all_rows)} published articles from Supabase")
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
        resp = requests.get(f"{url}/rest/v1/{table}", headers=headers, params=params)
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
        "article_type": "news",
        "tags": row.get("tags") if isinstance(row.get("tags"), list) else None,
        "author": "Diaspora Desk",
        "featured_score": row.get("score_total") or 0,
        "is_pinned_featured": bool(row.get("is_featured")),
        "pinned_until": None,
    }


def article_without_body(a: dict) -> dict:
    """Return article dict without body (for homepage feed, saves size)."""
    return {k: v for k, v in a.items() if k != "body"}


# ── Homepage feed builder ─────────────────────────────────────────────

def build_homepage_feed(articles: list[dict]) -> dict:
    """Build the homepage-feed.json structure."""
    now = datetime.now(timezone.utc)
    since_72h = (now - timedelta(hours=72)).isoformat()
    since_7d = (now - timedelta(days=7)).isoformat()

    # Group articles by category
    by_cat: dict[str, list[dict]] = {}
    for a in articles:
        cat = a["category"]
        by_cat.setdefault(cat, []).append(a)

    def get_category_articles(slug: str, limit: int) -> list[dict]:
        """Get articles for a category, preferring recent (72h), fallback to 7d."""
        pool = by_cat.get(slug, [])
        recent = [a for a in pool if a["published_at"] >= since_72h]
        if len(recent) >= 3:
            return [article_without_body(a) for a in recent[:limit]]
        wider = [a for a in pool if a["published_at"] >= since_7d]
        if len(wider) > len(recent):
            return [article_without_body(a) for a in wider[:limit]]
        return [article_without_body(a) for a in recent[:limit]]

    # Featured article: most recent 24h with image and highest score
    since_24h = (now - timedelta(hours=24)).isoformat()
    recent_24h = [a for a in articles if a["published_at"] >= since_24h]
    # Sort by score descending, then published_at descending
    recent_24h.sort(key=lambda a: (a.get("featured_score") or 0, a["published_at"]), reverse=True)
    featured = None
    for a in recent_24h:
        if a["hero_image_url"]:
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

    return {
        "generated_at": now.isoformat(),
        "featured": featured,
        "sections": sections,
        "carousel": carousel,
    }


# ── Main ──────────────────────────────────────────────────────────────

def main():
    print("=== Videshi Feed Pre-builder ===")
    load_env()
    url = os.environ["SUPABASE_URL"]
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ["SUPABASE_ANON_KEY"]

    # Fetch all published articles
    raw_rows = fetch_all_published(url, key)
    if not raw_rows:
        print("  WARNING: No published articles found, skipping prebuild")
        return

    articles = [map_row(r) for r in raw_rows]

    # 1. Build homepage feed
    print("  Building homepage-feed.json...")
    feed = build_homepage_feed(articles)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    HOMEPAGE_FEED.write_text(json.dumps(feed, ensure_ascii=False, separators=(",", ":")))
    feed_size = HOMEPAGE_FEED.stat().st_size
    print(f"  ✓ homepage-feed.json ({feed_size:,} bytes, {len(feed['sections'])} sections, carousel: {len(feed['carousel'])})")

    # 2. Build per-category feeds
    print("  Building category feeds...")
    CATEGORY_DIR.mkdir(parents=True, exist_ok=True)
    all_category_slugs = [
        "news", "nri-world", "sports", "entertainment", "technology",
        "markets-finance", "lifestyle-health", "food",
    ]
    now = datetime.now(timezone.utc)
    since_72h = (now - timedelta(hours=72)).isoformat()
    since_7d = (now - timedelta(days=7)).isoformat()

    by_cat: dict[str, list[dict]] = {}
    for a in articles:
        by_cat.setdefault(a["category"], []).append(a)

    cat_count = 0
    for slug in all_category_slugs:
        pool = by_cat.get(slug, [])
        # Same logic as getArticlesByCategory: 72h first, fallback to 7d
        recent = [a for a in pool if a["published_at"] >= since_72h]
        if len(recent) < 3:
            wider = [a for a in pool if a["published_at"] >= since_7d]
            if len(wider) > len(recent):
                recent = wider
        # Include body=false for listing, keep up to 50 articles per category
        cat_feed = {
            "generated_at": now.isoformat(),
            "category": slug,
            "articles": [article_without_body(a) for a in recent[:50]],
        }
        path = CATEGORY_DIR / f"{slug}.json"
        path.write_text(json.dumps(cat_feed, ensure_ascii=False, separators=(",", ":")))
        cat_count += 1
        print(f"    {slug}: {len(cat_feed['articles'])} articles")

    print(f"  ✓ {cat_count} category feeds written")

    # 3. Build individual article pages
    print(f"  Building article JSONs (up to {MAX_ARTICLE_PAGES})...")
    ARTICLES_DIR.mkdir(parents=True, exist_ok=True)

    # Clean out old article JSONs that are no longer in the recent set
    recent_slugs = set()
    written = 0
    for a in articles[:MAX_ARTICLE_PAGES]:
        slug = a["slug"]
        if not slug or slug == a["id"]:
            continue  # Skip articles without proper slugs
        recent_slugs.add(slug)
        path = ARTICLES_DIR / f"{slug}.json"
        path.write_text(json.dumps(a, ensure_ascii=False, separators=(",", ":")))
        written += 1

    # Remove stale article JSONs
    removed = 0
    for existing in ARTICLES_DIR.glob("*.json"):
        if existing.stem not in recent_slugs:
            existing.unlink()
            removed += 1

    print(f"  ✓ {written} article JSONs written, {removed} stale removed")

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

    # 6. Build directory.json
    print("  Building directory.json...")
    directory = fetch_table(url, key, "directory_listings",
                            order="featured.desc,rating.desc.nullslast")
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

    print("=== Done ===")


if __name__ == "__main__":
    main()

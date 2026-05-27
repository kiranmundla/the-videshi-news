#!/usr/bin/env python3
"""
videshi-health.py — Comprehensive pipeline health monitor for The Videshi.
Run by Hatch cron every 6 hours. Detects AND auto-fixes issues.

Checks:
  1. Category staleness — per-category freshness (carousel goes stale if any category dies)
  2. Stale publishing — global publishing gap while unprocessed signals wait
  3. Stuck in review — articles stuck in 'review' status → auto-publish
  4. Null published_at — published articles missing timestamp → fix
  5. Aged articles — >7 day old articles → archive (keeps site fresh)
  6. Duplicate articles — same headline published twice → flag newest dupe
  7. Missing images — recently published articles with no image_url → flag
  8. Broken slugs — published articles with null/empty slug → flag
  9. Cron output gaps — detect if key writer crons haven't produced articles recently
  10. Ingest health — check if RSS ingest is feeding signals

Usage:
  python3 videshi-health.py check     — Run all checks, print JSON report
  python3 videshi-health.py fix       — Run checks AND auto-fix fixable issues
"""

import json
import sys
import os
import requests
from datetime import datetime, timezone, timedelta
from collections import Counter

SB_URL = os.environ.get("SUPABASE_URL", "https://lboecaekpynbpyijrbfz.supabase.co")
SB_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
if not SB_KEY:
    env_path = os.path.expanduser("~/workspace/.env.supabase")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                if line.startswith("SUPABASE_SERVICE_ROLE_KEY="):
                    SB_KEY = line.split("=", 1)[1].strip()

REST = f"{SB_URL}/rest/v1"
HEADERS = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
}


def utc_iso(dt=None):
    """Return ISO timestamp with Z suffix (Supabase-safe, no + encoding issues)."""
    if dt is None:
        dt = datetime.now(timezone.utc)
    return dt.strftime("%Y-%m-%dT%H:%M:%S") + "Z"

# All content categories and their expected max age (hours)
CATEGORY_FRESHNESS = {
    "news":              24,   # writer runs every 2h
    "entertainment":     36,   # writer runs every 2h
    "sports":            48,   # writer runs every 3h
    "technology":        48,   # grouped with entertainment writer
    "markets-finance":   48,   # grouped with lifestyle writer
    "nri-world":         48,   # grouped with news writer
    "lifestyle-health":  72,   # writer runs every 4h
    "immigration":       72,   # writer runs every 4h
    "travel":           168,   # writer runs every 4h, evergreen
    "food":             168,   # less frequent
}

# Categories shown in the homepage featured carousel — highest priority
CAROUSEL_CATEGORIES = ["news", "entertainment", "sports", "technology", "markets-finance"]


def sb_get(table, params):
    r = requests.get(f"{REST}/{table}?{params}", headers=HEADERS)
    return r.json() if r.ok else []


def sb_get_count(table, params):
    h = {**HEADERS, "Prefer": "count=exact"}
    r = requests.get(f"{REST}/{table}?{params}&select=id&limit=1", headers=h)
    cr = r.headers.get("content-range", "")
    try:
        return int(cr.split("/")[1])
    except Exception:
        return 0


def sb_patch(table, filters, data):
    h = {**HEADERS, "Prefer": "return=representation"}
    r = requests.patch(f"{REST}/{table}?{filters}", headers=h, json=data)
    return r.json() if r.ok and r.text else []


# ─── Check 1: Per-category freshness ──────────────────────────────────────────

def check_category_staleness():
    """Check each category against its expected freshness window.
    Flags carousel categories as 'critical', others as 'warning'."""
    now = datetime.now(timezone.utc)
    stale = []
    category_status = {}

    for cat, max_hours in CATEGORY_FRESHNESS.items():
        cutoff = utc_iso(now - timedelta(hours=max_hours))
        recent = sb_get("p2_articles",
            f"status=eq.published&category=eq.{cat}&published_at=gte.{cutoff}"
            f"&select=id&limit=1")

        if recent:
            category_status[cat] = "fresh"
        else:
            # Find how old the latest actually is
            latest = sb_get("p2_articles",
                f"status=eq.published&category=eq.{cat}&published_at=not.is.null"
                f"&select=published_at&order=published_at.desc&limit=1")
            if latest:
                last_dt = datetime.fromisoformat(latest[0]["published_at"].replace("Z", "+00:00"))
                hours_ago = (now - last_dt).total_seconds() / 3600
                severity = "critical" if cat in CAROUSEL_CATEGORIES else "warning"
                category_status[cat] = f"stale ({hours_ago:.0f}h ago)"
                stale.append({
                    "category": cat,
                    "hours_since_last": round(hours_ago, 1),
                    "expected_max_hours": max_hours,
                    "severity": severity,
                })
            else:
                category_status[cat] = "never published"
                stale.append({
                    "category": cat,
                    "hours_since_last": None,
                    "expected_max_hours": max_hours,
                    "severity": "critical" if cat in CAROUSEL_CATEGORIES else "warning",
                })

    # Also detect and report wrong-case categories
    VALID_CATEGORIES = set(CATEGORY_FRESHNESS.keys())
    wrong_case = sb_get("p2_articles",
        "status=eq.published&select=category&limit=500")
    case_counts = Counter(a["category"] for a in wrong_case if a["category"] not in VALID_CATEGORIES)

    critical = [s for s in stale if s["severity"] == "critical"]

    return {
        "check": "category_staleness",
        "stale_count": len(stale),
        "critical_count": len(critical),
        "stale_categories": stale,
        "category_status": category_status,
        "wrong_case_categories": dict(case_counts) if case_counts else {},
        "alert": len(critical) > 0,
        "action_needed": (
            f"trigger writers for: {', '.join(s['category'] for s in critical)}"
            if critical else None
        ),
    }


# ─── Check 2: Global stale publishing ─────────────────────────────────────────

def check_stale_publishing():
    """Check if no articles at all were published in the last 6 hours
    while unprocessed signals exist."""
    cutoff_6h = utc_iso(datetime.now(timezone.utc) - timedelta(hours=6))
    recent = sb_get("p2_articles",
        f"status=eq.published&published_at=gte.{cutoff_6h}&select=id&limit=1")
    has_recent = len(recent) > 0

    cutoff_48h = utc_iso(datetime.now(timezone.utc) - timedelta(hours=48))
    unprocessed = sb_get_count("p2_signals",
        f"is_processed=eq.false&published_at=gte.{cutoff_48h}")

    stale = not has_recent and unprocessed > 0
    return {
        "check": "stale_publishing",
        "stale": stale,
        "has_recent_articles": has_recent,
        "unprocessed_signals": unprocessed,
        "action_needed": "trigger_writer — pipeline stalled" if stale else None,
    }


# ─── Check 3: Stuck in review ─────────────────────────────────────────────────

def check_stuck_review(fix=False):
    """Articles in 'review' status for >1h — auto-publish on fix."""
    stuck = sb_get("p2_articles",
        "status=eq.review&select=id,headline,created_at&limit=50")
    fixed = 0
    if fix and stuck:
        now = utc_iso()
        result = sb_patch("p2_articles", "status=eq.review",
            {"status": "published", "published_at": now})
        fixed = len(result) if isinstance(result, list) else 0
    return {
        "check": "stuck_review",
        "count": len(stuck),
        "fixed": fixed,
        "headlines": [a["headline"][:80] for a in stuck[:5]],
    }


# ─── Check 4: Null published_at ───────────────────────────────────────────────

def check_null_published_at(fix=False):
    """Published articles missing published_at — invisible to the site."""
    broken = sb_get("p2_articles",
        "status=eq.published&published_at=is.null&select=id,headline&limit=50")
    fixed = 0
    if fix and broken:
        now = utc_iso()
        result = sb_patch("p2_articles", "status=eq.published&published_at=is.null",
            {"published_at": now})
        fixed = len(result) if isinstance(result, list) else 0
    return {
        "check": "null_published_at",
        "count": len(broken),
        "fixed": fixed,
        "sample_headlines": [a["headline"][:80] for a in broken[:3]],
    }


# ─── Check 5: Aged articles ───────────────────────────────────────────────────

def check_aged_articles(fix=False):
    """Archive non-evergreen articles older than 7 days."""
    cutoff_7d = utc_iso(datetime.now(timezone.utc) - timedelta(days=7))
    EVERGREEN = ("travel", "food")
    filters = (
        f"status=eq.published&published_at=lt.{cutoff_7d}"
        f"&category=not.in.({','.join(EVERGREEN)})"
    )
    old = sb_get("p2_articles", f"{filters}&select=id&limit=200")
    archived = 0
    if fix and old:
        result = sb_patch("p2_articles", filters, {"status": "archived"})
        archived = len(result) if isinstance(result, list) else 0
    return {
        "check": "aged_articles",
        "older_than_7d": len(old),
        "archived": archived,
    }


# ─── Check 6: Duplicate articles ──────────────────────────────────────────────

def check_duplicates():
    """Detect duplicate headlines published in the last 7 days."""
    cutoff_7d = utc_iso(datetime.now(timezone.utc) - timedelta(days=7))
    articles = sb_get("p2_articles",
        f"status=eq.published&published_at=gte.{cutoff_7d}"
        f"&select=id,headline,published_at&order=published_at.desc&limit=500")

    headline_counts = Counter(a["headline"] for a in articles)
    dupes = []
    for headline, count in headline_counts.items():
        if count > 1:
            matching = [a for a in articles if a["headline"] == headline]
            dupes.append({
                "headline": headline[:80],
                "count": count,
                "ids": [a["id"] for a in matching],
                "newest_id": matching[0]["id"],  # sorted desc, so first is newest
            })

    return {
        "check": "duplicate_articles",
        "count": len(dupes),
        "duplicates": dupes[:5],
        "action_needed": (
            f"delete newest dupes: {', '.join(d['newest_id'][:8] for d in dupes)}"
            if dupes else None
        ),
    }


# ─── Check 7: Missing images ──────────────────────────────────────────────────

def check_missing_images():
    """Recently published articles with no image — reels and social posts will fail."""
    cutoff_48h = utc_iso(datetime.now(timezone.utc) - timedelta(hours=48))
    no_img = sb_get("p2_articles",
        f"status=eq.published&published_at=gte.{cutoff_48h}"
        f"&image_url=is.null&select=id,headline,category&limit=20")
    return {
        "check": "missing_images",
        "count": len(no_img),
        "articles": [{"id": a["id"], "headline": a["headline"][:60], "category": a.get("category")}
                     for a in no_img[:5]],
    }


# ─── Check 8: Broken slugs ────────────────────────────────────────────────────

def check_broken_slugs(fix=False):
    """Published articles with null or empty slug — causes 404s on the site."""
    broken = sb_get("p2_articles",
        "status=eq.published&slug=is.null&select=id,headline&limit=50")
    # Also check for empty string slugs
    empty = sb_get("p2_articles",
        "status=eq.published&slug=eq.&select=id,headline&limit=50")
    all_broken = broken + empty
    return {
        "check": "broken_slugs",
        "count": len(all_broken),
        "articles": [{"id": a["id"], "headline": a["headline"][:60]} for a in all_broken[:5]],
        "action_needed": f"fix {len(all_broken)} broken slugs" if all_broken else None,
    }


# ─── Check 9: Ingest health ───────────────────────────────────────────────────

def check_ingest_health():
    """Check if RSS ingest is feeding fresh topics. If topics dried up,
    writers have nothing to work with.
    Note: pipeline was refactored from p2_signals to p2_topics; check both."""
    cutoff_6h = utc_iso(datetime.now(timezone.utc) - timedelta(hours=6))
    cutoff_24h = utc_iso(datetime.now(timezone.utc) - timedelta(hours=24))

    # Primary: check p2_topics (current ingest target)
    recent_6h = sb_get_count("p2_topics", f"created_at=gte.{cutoff_6h}")
    recent_24h = sb_get_count("p2_topics", f"created_at=gte.{cutoff_24h}")

    # Fallback: also check p2_signals (legacy, uses fetched_at column)
    if recent_24h == 0:
        legacy_6h = sb_get_count("p2_signals", f"fetched_at=gte.{cutoff_6h}")
        legacy_24h = sb_get_count("p2_signals", f"fetched_at=gte.{cutoff_24h}")
        recent_6h = max(recent_6h, legacy_6h)
        recent_24h = max(recent_24h, legacy_24h)

    dry = recent_24h == 0
    low = recent_24h < 10 and not dry
    return {
        "check": "ingest_health",
        "signals_last_6h": recent_6h,
        "signals_last_24h": recent_24h,
        "status": "dry" if dry else ("low" if low else "healthy"),
        "alert": dry,
        "action_needed": "ingest pipeline may be broken — 0 signals in 24h" if dry else None,
    }


# ─── Check 10: Article volume ─────────────────────────────────────────────────

def check_article_volume():
    """Track publishing velocity — how many articles per 24h and per category."""
    cutoff_24h = utc_iso(datetime.now(timezone.utc) - timedelta(hours=24))
    recent = sb_get("p2_articles",
        f"status=eq.published&published_at=gte.{cutoff_24h}"
        f"&select=category&limit=500")

    by_cat = Counter(a.get("category", "unknown") for a in recent)
    total = len(recent)
    return {
        "check": "article_volume_24h",
        "total": total,
        "by_category": dict(by_cat),
        "alert": total < 5,
        "action_needed": f"only {total} articles in 24h — below minimum 5" if total < 5 else None,
    }


# ─── Check 11: Image validation ───────────────────────────────────────────────

def check_image_health():
    """Validate that article images actually load, are real images, and are
    reasonably sized. Broken images = blank cards on the homepage."""
    cutoff_48h = utc_iso(datetime.now(timezone.utc) - timedelta(hours=48))
    articles = sb_get("p2_articles",
        f"status=eq.published&published_at=gte.{cutoff_48h}"
        f"&image_url=not.is.null&select=id,headline,image_url,category"
        f"&order=published_at.desc&limit=50")

    broken = []      # 404, 403, timeout
    tiny = []        # < 5KB (likely placeholder/icon)
    not_image = []   # content-type isn't image/*
    flag_imgs = []   # generic flag images
    expired_cdn = [] # ephemeral CDN URLs (fbcdn, cdninstagram) that will/have expired

    # Ephemeral CDN domains whose URLs expire after ~24-48h
    EPHEMERAL_DOMAINS = ("fbcdn.net", "cdninstagram.com", "scontent-", "lookaside.fbsbx.com")

    for a in articles:
        url = a.get("image_url", "")
        if not url or len(url) < 10:
            broken.append({"id": a["id"], "headline": a["headline"][:60], "reason": "empty URL"})
            continue

        # Detect ephemeral CDN URLs — these WILL break within days
        if any(domain in url for domain in EPHEMERAL_DOMAINS):
            expired_cdn.append({
                "id": a["id"], "headline": a["headline"][:60],
                "domain": next(d for d in EPHEMERAL_DOMAINS if d in url),
            })
            continue  # skip HTTP check, we know these expire

        # Detect generic flag images
        if "flag" in url.lower() and ("wikipedia" in url.lower() or "wikimedia" in url.lower()):
            flag_imgs.append({"id": a["id"], "headline": a["headline"][:60], "url": url[:80]})
            continue

        try:
            r = requests.head(url, timeout=8, allow_redirects=True,
                              headers={"User-Agent": "TheVideshi/1.0"})
            if r.status_code >= 400:
                broken.append({
                    "id": a["id"], "headline": a["headline"][:60],
                    "reason": f"HTTP {r.status_code}", "url": url[:80],
                })
            else:
                ct = r.headers.get("content-type", "")
                cl = int(r.headers.get("content-length", 0) or 0)
                if "image" not in ct:
                    not_image.append({
                        "id": a["id"], "headline": a["headline"][:60],
                        "content_type": ct[:40], "url": url[:80],
                    })
                elif cl > 0 and cl < 5000:
                    tiny.append({
                        "id": a["id"], "headline": a["headline"][:60],
                        "bytes": cl, "url": url[:80],
                    })
        except Exception as e:
            broken.append({
                "id": a["id"], "headline": a["headline"][:60],
                "reason": f"timeout/error: {str(e)[:40]}", "url": url[:80],
            })

    total_issues = len(broken) + len(tiny) + len(not_image) + len(flag_imgs) + len(expired_cdn)
    return {
        "check": "image_health",
        "articles_checked": len(articles),
        "broken_images": broken[:5],
        "tiny_images": tiny[:5],
        "not_image_content": not_image[:5],
        "flag_images": flag_imgs[:5],
        "expired_cdn_urls": expired_cdn[:10],
        "total_issues": total_issues,
        "alert": total_issues > 0,
        "action_needed": (
            f"{total_issues} image issues: {len(broken)} broken, {len(expired_cdn)} expired CDN, "
            f"{len(tiny)} tiny, {len(not_image)} wrong type, {len(flag_imgs)} generic flags"
            if total_issues > 0 else None
        ),
    }


# ─── Check 12: Article quality ────────────────────────────────────────────────

VALID_CATEGORIES = {
    "news", "entertainment", "sports", "technology", "markets-finance",
    "nri-world", "lifestyle-health", "immigration", "travel", "food",
}

def check_article_quality():
    """Strict quality checks on recently published articles:
    - Body must be 400+ words (target 600-800)
    - Subheadline must exist
    - Slug must be lowercase, no spaces, no UUIDs
    - Category must be valid lowercase
    - Sources should exist
    - Headline should be 20-200 chars
    """
    cutoff_48h = utc_iso(datetime.now(timezone.utc) - timedelta(hours=48))
    articles = sb_get("p2_articles",
        f"status=eq.published&published_at=gte.{cutoff_48h}"
        f"&select=id,headline,subheadline,slug,category,body,sources,image_url"
        f"&order=published_at.desc&limit=100")

    issues = []
    for a in articles:
        art_issues = []
        hl = a.get("headline") or ""
        body = a.get("body") or ""
        sub = a.get("subheadline") or ""
        slug = a.get("slug") or ""
        cat = a.get("category") or ""
        sources = a.get("sources") or ""
        img = a.get("image_url") or ""

        # Body length
        word_count = len(body.split())
        if word_count < 100:
            art_issues.append(f"body dangerously short ({word_count}w)")
        elif word_count < 400:
            art_issues.append(f"body below minimum ({word_count}w, want 600+)")

        # Subheadline
        if len(sub.strip()) < 10:
            art_issues.append("missing or trivial subheadline")

        # Headline
        if len(hl) < 20:
            art_issues.append(f"headline too short ({len(hl)} chars)")
        elif len(hl) > 250:
            art_issues.append(f"headline too long ({len(hl)} chars)")

        # Slug
        if not slug:
            art_issues.append("no slug")
        elif slug != slug.lower():
            art_issues.append("slug not lowercase")
        elif " " in slug:
            art_issues.append("slug has spaces")
        # UUID-only slugs (no human-readable content)
        elif len(slug) == 36 and slug.count("-") == 4:
            art_issues.append("slug is a UUID, not human-readable")

        # Category
        if cat not in VALID_CATEGORIES:
            art_issues.append(f"invalid category: '{cat}'")

        # Sources
        if not sources or sources in ("[]", "null", "None"):
            art_issues.append("no sources")

        # No image
        if not img:
            art_issues.append("no image")

        if art_issues:
            issues.append({
                "id": a["id"],
                "headline": hl[:70],
                "category": cat,
                "issues": art_issues,
            })

    return {
        "check": "article_quality",
        "articles_checked": len(articles),
        "articles_with_issues": len(issues),
        "issues": issues[:10],  # top 10
        "alert": len(issues) > 5,
        "action_needed": (
            f"{len(issues)}/{len(articles)} recent articles have quality issues"
            if len(issues) > 5 else None
        ),
    }


# ─── Run all ───────────────────────────────────────────────────────────────────

def run_all(fix=False):
    checks = [
        check_category_staleness(),
        check_stale_publishing(),
        check_article_volume(),
        check_ingest_health(),
        check_article_quality(),
        check_image_health(),
        check_duplicates(),
        check_missing_images(),
        check_broken_slugs(fix=fix),
        check_stuck_review(fix=fix),
        check_null_published_at(fix=fix),
        check_aged_articles(fix=fix),
    ]

    report = {
        "timestamp": utc_iso(),
        "mode": "fix" if fix else "check",
        "checks": checks,
    }

    # Count issues: anything with stale=True, alert=True, count>0, or older_than_7d>0
    issues = 0
    actions = []
    for c in checks:
        is_issue = (
            c.get("stale")
            or c.get("alert")
            or c.get("count", 0) > 0
            or c.get("older_than_7d", 0) > 0
        )
        if is_issue:
            issues += 1
        if c.get("action_needed"):
            actions.append(c["action_needed"])

    report["health"] = "healthy" if issues == 0 else f"{issues} issue(s)"
    report["actions_needed"] = actions
    return report


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    fix = mode == "fix"
    report = run_all(fix=fix)
    print(json.dumps(report, indent=2))

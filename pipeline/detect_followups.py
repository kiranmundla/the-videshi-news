#!/usr/bin/env python3
"""
detect_followups.py — Detect follow-up articles and set article_type.

Scans recent articles and checks if they cover a topic that has already been
written about in p2_articles within the last 30 days. If so, sets article_type
to 'follow-up' instead of the default 'breaking'.

Called by article_ranker.py during scoring, or standalone:
  python3 detect_followups.py [--days 3] [--dry-run]

article_type values:
  - breaking: New topic, first coverage (default)
  - follow-up: Topic already covered in last 30 days
  - analysis: Deep dive on a known topic (set manually or by writer)
  - explainer: Educational/explainer piece (set manually or by writer)
"""

import json, os, re, subprocess, sys, time
from datetime import datetime, timezone, timedelta
from pathlib import Path

# ─── Env ──────────────────────────────────────────────────────────────────
env_file = Path.home() / ".env.supabase"
if env_file.exists():
    for line in env_file.read_text().strip().splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

SUPABASE_ACCESS_TOKEN = os.environ.get("SUPABASE_ACCESS_TOKEN", "")

# ─── Stopwords for keyword extraction ─────────────────────────────────────
STOPWORDS = {
    "the", "and", "for", "are", "but", "not", "you", "all", "can", "had",
    "her", "was", "one", "our", "out", "has", "his", "how", "its", "may",
    "new", "now", "old", "see", "way", "who", "did", "get", "got", "let",
    "say", "she", "too", "use", "with", "will", "from", "that", "this",
    "what", "when", "where", "which", "while", "about", "after", "could",
    "their", "there", "these", "those", "would", "should", "being",
    "over", "into", "also", "been", "have", "more", "than", "very",
    "just", "some", "them", "then", "were", "here", "much", "many",
    "most", "must", "even", "such", "each", "make", "like", "long",
    "look", "only", "come", "back", "year", "last", "first", "made",
    "said", "says", "amid", "among", "india", "indian", "need",
    "know", "every", "best", "kept", "secret", "gets", "plan",
    "plans", "could", "here", "what", "your", "most", "says",
    "want", "wants", "called", "calls", "still", "time", "take",
    "took", "does", "done", "going", "gone", "good", "well",
    "right", "left", "before", "between", "under", "other",
}


def _curl_json(method, url, headers=None, data=None):
    """Make HTTP request via curl (proxy-safe)."""
    cmd = ["curl", "-s", "-X", method, url]
    for k, v in (headers or {}).items():
        cmd += ["-H", f"{k}: {v}"]
    if data:
        cmd += ["-H", "Content-Type: application/json", "-d", json.dumps(data)]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if result.returncode != 0:
        raise RuntimeError(f"curl failed: {result.stderr}")
    return json.loads(result.stdout) if result.stdout.strip() else {}


def supabase_query(sql):
    """Run SQL via Supabase Management API."""
    url = "https://api.supabase.com/v1/projects/lboecaekpynbpyijrbfz/database/query"
    return _curl_json("POST", url,
                      headers={"Authorization": f"Bearer {SUPABASE_ACCESS_TOKEN}"},
                      data={"query": sql})


def extract_keywords(headline: str, min_len=4) -> list[str]:
    """Extract distinctive keywords from a headline."""
    words = re.findall(r"[a-zA-Z]+", headline.lower())
    keywords = [w for w in words if len(w) >= min_len and w not in STOPWORDS]
    # Sort by length desc (longer = more distinctive)
    keywords.sort(key=len, reverse=True)
    return keywords[:8]


def find_prior_coverage(article_id: str, headline: str, category: str,
                        published_at: str, lookback_days: int = 30) -> dict:
    """
    Check if this article covers a topic already written about.
    Returns {"is_followup": bool, "prior_count": int, "prior_slugs": [...]}
    """
    keywords = extract_keywords(headline)
    if len(keywords) < 2:
        return {"is_followup": False, "prior_count": 0, "prior_slugs": []}

    # Build keyword match scoring — require at least 3 keyword hits
    # (or 2 if there are only 2-3 keywords)
    min_hits = 3 if len(keywords) >= 4 else 2

    case_parts = " + ".join(
        f"CASE WHEN headline ILIKE '%{kw}%' THEN 1 ELSE 0 END"
        for kw in keywords
    )

    # Escape single quotes in article_id
    safe_id = article_id.replace("'", "''")

    # First pass: same category
    sql = f"""
    SELECT id, slug, headline, published_at, kw_hits FROM (
        SELECT id, slug, headline, published_at,
               ({case_parts}) as kw_hits
        FROM p2_articles
        WHERE status = 'published'
          AND id != '{safe_id}'
          AND category = '{category}'
          AND published_at > '{published_at}'::timestamptz - INTERVAL '{lookback_days} days'
          AND published_at < '{published_at}'::timestamptz
    ) sub
    WHERE kw_hits >= {min_hits}
    ORDER BY kw_hits DESC, published_at DESC
    LIMIT 5
    """

    try:
        rows = supabase_query(sql)

        # Second pass: cross-category with stricter threshold (4+ keyword hits)
        # Catches cases where same story is filed under different categories
        # (e.g., immigration story filed under "news")
        if (not rows or not isinstance(rows, list) or len(rows) == 0) and len(keywords) >= 4:
            cross_min = max(min_hits + 1, 4)  # require 4+ keywords for cross-category
            sql_cross = f"""
            SELECT id, slug, headline, published_at, kw_hits FROM (
                SELECT id, slug, headline, published_at,
                       ({case_parts}) as kw_hits
                FROM p2_articles
                WHERE status = 'published'
                  AND id != '{safe_id}'
                  AND published_at > '{published_at}'::timestamptz - INTERVAL '{lookback_days} days'
                  AND published_at < '{published_at}'::timestamptz
            ) sub
            WHERE kw_hits >= {cross_min}
            ORDER BY kw_hits DESC, published_at DESC
            LIMIT 5
            """
            rows = supabase_query(sql_cross)

        if not rows or not isinstance(rows, list):
            return {"is_followup": False, "prior_count": 0, "prior_slugs": []}

        prior_slugs = [r.get("slug", "") for r in rows if r.get("slug")]
        return {
            "is_followup": len(rows) > 0,
            "prior_count": len(rows),
            "prior_slugs": prior_slugs[:3],
        }
    except Exception as e:
        print(f"  ⚠ Prior coverage check failed: {e}", file=sys.stderr)
        return {"is_followup": False, "prior_count": 0, "prior_slugs": []}


def update_article_type(article_id: str, article_type: str):
    """Set article_type in the DB."""
    safe_id = article_id.replace("'", "''")
    sql = f"UPDATE p2_articles SET article_type = '{article_type}' WHERE id = '{safe_id}'"
    supabase_query(sql)


def detect_and_tag(days: int = 3, dry_run: bool = False):
    """Scan recent articles and tag follow-ups."""
    sql = f"""
    SELECT id, slug, headline, category, published_at
    FROM p2_articles
    WHERE status = 'published'
      AND (article_type IS NULL OR article_type = 'breaking')
      AND published_at > NOW() - INTERVAL '{days} days'
    ORDER BY published_at DESC
    LIMIT 200
    """
    articles = supabase_query(sql)
    if not articles or not isinstance(articles, list):
        print("No articles to check.")
        return

    print(f"Checking {len(articles)} articles for follow-up detection...\n")

    tagged = 0
    for art in articles:
        aid = art["id"]
        headline = art.get("headline", "")
        category = art.get("category", "")
        published_at = art.get("published_at", "")
        slug = art.get("slug", "")

        result = find_prior_coverage(aid, headline, category, published_at)

        if result["is_followup"]:
            print(f"  📎 FOLLOW-UP: {headline[:70]}...")
            print(f"     Prior coverage ({result['prior_count']}): {', '.join(result['prior_slugs'][:2])}")

            if not dry_run:
                update_article_type(aid, "follow-up")
                print(f"     ✅ Tagged as follow-up")
            else:
                print(f"     (dry run — would tag as follow-up)")
            tagged += 1
        else:
            print(f"  ✓ NEW: {headline[:70]}...")

        time.sleep(0.2)  # light rate limiting

    print(f"\n{'='*60}")
    print(f"Done. Tagged {tagged} follow-ups out of {len(articles)} articles.")


# ─── CLI ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Detect follow-up articles")
    parser.add_argument("--days", type=int, default=3, help="Lookback window for new articles")
    parser.add_argument("--dry-run", action="store_true", help="Print results without saving")
    args = parser.parse_args()

    detect_and_tag(days=args.days, dry_run=args.dry_run)

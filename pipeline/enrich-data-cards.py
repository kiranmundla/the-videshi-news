#!/usr/bin/env python3
"""
Data Card Enrichment Pipeline
Adds structured data cards and key takeaways to published articles.
GPT-4o-mini reads each article and returns structured card data for
the frontend to render as rich HTML infographic cards.

Usage:
  python3 pipeline/enrich-data-cards.py              # Enrich last 24h
  python3 pipeline/enrich-data-cards.py --limit 5    # Max 5 articles
  python3 pipeline/enrich-data-cards.py --since-hours 48
  python3 pipeline/enrich-data-cards.py --force-id <uuid>
  python3 pipeline/enrich-data-cards.py --dry-run     # Preview only
"""
import os, sys, json, time, argparse, requests
from datetime import datetime, timedelta, timezone

# ── Config ──────────────────────────────────────────────────────────────
SUPABASE_URL  = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY  = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
OPENAI_KEY    = os.environ.get("OPENAI_API_KEY", "")

HEADERS_SB = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal"
}

ENRICHMENT_PROMPT = """You are a data journalist extracting structured visual card data from a news article.

Given the article below, produce:

1. **key_takeaways**: 3-5 bullet points that summarize the article in 10 seconds. Each should be a complete, standalone insight. Under 20 words each.

2. **data_cards**: 1-3 data cards. Each card is a rich visual summary of a section — NOT a single stat. Each card must contain multiple data points that together tell the story of that section. A reader should be able to skip the text and understand the key facts from the card alone.

Each card has:
- **card_title**: Punchy editorial title (NOT the article headline repeated)
- **card_type**: One of:
  - "stat_grid": Hero stat + 2-4 supporting stats in a 2×2 grid. Best for data-heavy articles.
  - "comparison": Horizontal bar chart comparing items. Best for rankings, vs scenarios.
  - "timeline": Chronological sequence of events. Best for evolving stories.
  - "highlights": Key bullet points with optional stats. Best for qualitative stories.
- **hero_stat** (optional, for stat_grid): object with "value", "label", and optional "trend" (e.g. "↑ 317%")
- **items**: Array of data points:
  - stat_grid: objects with "value" and "label" — 2-4 items
  - comparison: objects with "name", "value", "numeric_value" — 3-6 items, MUST be sorted by numeric_value descending
  - timeline: objects with "date" and "event" — 3-6 items chronological
  - highlights: objects with "text" and optional "stat" — 3-5 items
- **placement_hint**: "after_lead", "mid_article", or "before_conclusion"
- **source_note** (optional): Brief source attribution

RULES:
- Every stat/number MUST come from the article. Never fabricate.
- If no meaningful stats/data exist, return 0 data_cards — only key_takeaways.
- Each card should pack 4-6 distinct data points, not just one number.
- For comparison, always provide numeric_value as a plain number for bar scaling.
- Card titles should be punchy — "India's Semiconductor Moment", not "About Semiconductors".

Return ONLY valid JSON. No markdown wrapping, no commentary.

ARTICLE:
Headline: {headline}
Subheadline: {subheadline}
Category: {category}

{body}"""


def fetch_articles(since_hours=24, limit=20, force_id=None):
    """Fetch published articles needing enrichment."""
    if force_id:
        r = requests.get(
            f"{SUPABASE_URL}/rest/v1/p2_articles",
            headers={**HEADERS_SB, "Prefer": ""},
            params={
                "select": "id,headline,subheadline,category,body,slug",
                "id": f"eq.{force_id}"
            }
        )
    else:
        since = (datetime.now(timezone.utc) - timedelta(hours=since_hours)).isoformat()
        r = requests.get(
            f"{SUPABASE_URL}/rest/v1/p2_articles",
            headers={**HEADERS_SB, "Prefer": ""},
            params={
                "select": "id,headline,subheadline,category,body,slug",
                "status": "eq.published",
                "enriched_at": "is.null",
                "published_at": f"gte.{since}",
                "order": "published_at.desc",
                "limit": str(limit)
            }
        )
    if r.status_code != 200:
        print(f"ERROR fetching: {r.status_code} {r.text[:200]}")
        return []
    return r.json()


def extract_cards(article):
    """Call GPT-4o-mini to extract card data."""
    body = article.get("body", "") or ""
    if len(body) > 8000:
        body = body[:8000] + "\n...[truncated]"

    prompt = ENRICHMENT_PROMPT.replace("{headline}", article.get("headline", "")) \
        .replace("{subheadline}", article.get("subheadline", "") or "") \
        .replace("{category}", article.get("category", "") or "") \
        .replace("{body}", body)

    resp = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {OPENAI_KEY}", "Content-Type": "application/json"},
        json={
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
            "response_format": {"type": "json_object"},
            "max_tokens": 1500
        }
    )

    if resp.status_code != 200:
        print(f"  OpenAI error: {resp.status_code} {resp.text[:200]}")
        return None

    try:
        content = resp.json()["choices"][0]["message"]["content"]
        return json.loads(content)
    except (KeyError, json.JSONDecodeError) as e:
        print(f"  Parse error: {e}")
        return None


def validate(data):
    """Validate extracted card data."""
    if not isinstance(data, dict):
        return False
    kt = data.get("key_takeaways")
    if not kt or not isinstance(kt, list) or len(kt) < 1:
        return False
    cards = data.get("data_cards", [])
    if not isinstance(cards, list):
        return False
    for card in cards:
        if not card.get("card_title") or not card.get("card_type"):
            return False
        if card["card_type"] not in ("stat_grid", "comparison", "timeline", "highlights"):
            return False
        if not card.get("items") or not isinstance(card["items"], list):
            return False
    return True


def save(article_id, data):
    """Save enrichment to Supabase."""
    now = datetime.now(timezone.utc).isoformat()
    r = requests.patch(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS_SB,
        params={"id": f"eq.{article_id}"},
        json={
            "data_cards": data.get("data_cards", []),
            "key_takeaways": data.get("key_takeaways", []),
            "enriched_at": now
        }
    )
    if r.status_code not in (200, 204):
        print(f"  Save error: {r.status_code} {r.text[:200]}")
        return False
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=30)
    parser.add_argument("--since-hours", type=int, default=24)
    parser.add_argument("--force-id", type=str)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not all([SUPABASE_URL, SUPABASE_KEY, OPENAI_KEY]):
        print("ERROR: Missing env vars")
        sys.exit(1)

    print(f"📊 Data Card Enrichment")
    print(f"   Window: {args.since_hours}h | Limit: {args.limit}")

    articles = fetch_articles(args.since_hours, args.limit, args.force_id)
    print(f"   Found {len(articles)} articles\n")

    if not articles:
        print("Nothing to enrich.")
        return

    enriched = errors = skipped = 0

    for i, art in enumerate(articles):
        hl = art.get("headline", "???")[:80]
        print(f"[{i+1}/{len(articles)}] {hl}")

        data = extract_cards(art)
        if not data:
            errors += 1
            continue

        if not validate(data):
            print(f"  ⚠️  Validation failed")
            skipped += 1
            continue

        n_cards = len(data.get("data_cards", []))
        n_kt = len(data.get("key_takeaways", []))
        types = [c["card_type"] for c in data.get("data_cards", [])]
        print(f"  ✅ {n_kt} takeaways, {n_cards} cards ({', '.join(types) or 'none'})")

        if args.dry_run:
            for c in data.get("data_cards", []):
                print(f"    → {c['card_title']} ({c['card_type']}, {len(c['items'])} items @ {c.get('placement_hint','?')})")
        else:
            if save(art["id"], data):
                enriched += 1
            else:
                errors += 1

        time.sleep(0.3)

    print(f"\n{'='*50}")
    print(f"✅ {enriched} enriched | ⚠️  {skipped} skipped | ❌ {errors} errors")


if __name__ == "__main__":
    main()

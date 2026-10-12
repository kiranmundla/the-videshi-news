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
- TIMELINE DATES (CRITICAL): The article was published on {published_date}. Every timeline
  date MUST use the correct year — events described in the article happened in the same
  year as publication unless the article explicitly states otherwise. NEVER default to a
  past year (e.g. 2023) for current events. If the article says "October 9" and was
  published October 2026, the timeline date is "October 9, 2026".
- STAT VALUES: Never use bare integers 1-5 as stat values without a unit or context
  (e.g. "1" or "2" alone is meaningless). Every stat needs a label that makes it
  self-explanatory.
- COMPARISON CARDS: Only use comparison type when there are 2+ genuinely comparable
  items. Never use comparison for lists, biographies, or single entities.
- SINGLE-ITEM CARDS: Never create a card with only one data point — merge that fact
  into the article body instead.

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
                "select": "id,headline,subheadline,category,body,slug,published_at",
                "id": f"eq.{force_id}"
            }
        )
    else:
        since = (datetime.now(timezone.utc) - timedelta(hours=since_hours)).isoformat()
        r = requests.get(
            f"{SUPABASE_URL}/rest/v1/p2_articles",
            headers={**HEADERS_SB, "Prefer": ""},
            params={
                "select": "id,headline,subheadline,category,body,slug,published_at",
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

    # Published date for timeline year anchoring (Fix 1: prevent year hallucination)
    pub = article.get("published_at", "") or ""
    pub_date = pub[:10] if len(pub) >= 10 else "unknown"

    prompt = ENRICHMENT_PROMPT.replace("{headline}", article.get("headline", "")) \
        .replace("{subheadline}", article.get("subheadline", "") or "") \
        .replace("{category}", article.get("category", "") or "") \
        .replace("{published_date}", pub_date) \
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


def validate(data, article=None):
    """Validate extracted card data.

    Guardrails (2026-10-11):
    - Fix 1: Timeline dates must be within ±18 months of article's published_at.
      Prevents year hallucination (e.g. 2023 dates on 2026 articles).
    - Fix 3: Reject junk cards — bare integers 1-5 as stats, comparison cards
      with <2 rows, single-item cards.
    """
    import re
    if not isinstance(data, dict):
        return False
    kt = data.get("key_takeaways")
    if not kt or not isinstance(kt, list) or len(kt) < 1:
        return False
    cards = data.get("data_cards", [])
    if not isinstance(cards, list):
        return False

    # Parse article published date for timeline anchoring
    pub_date = None
    if article:
        pub_str = article.get("published_at", "") or ""
        try:
            pub_date = datetime.fromisoformat(pub_str.replace("Z", "+00:00"))
            if pub_date.tzinfo is None:
                pub_date = pub_date.replace(tzinfo=timezone.utc)
        except (ValueError, TypeError):
            pub_date = None

    for card in cards:
        # Writer-produced component cards (how_to, key_dates, checklist, price_compare)
        # use 'type'/'title' schema — accept them via their own validation
        card_type = card.get("card_type") or card.get("type")
        if card_type in ("how_to", "key_dates", "checklist", "price_compare"):
            if not card.get("title"):
                return False
            # how_to needs steps, key_dates needs dates, checklist needs items, price_compare needs rows
            content_key = {"how_to": "steps", "key_dates": "dates", "checklist": "items", "price_compare": "rows"}[card_type]
            content = card.get(content_key)
            if not content or not isinstance(content, list) or len(content) < 1:
                print(f"  ⚠️  Rejecting {card_type} card '{card.get('title')}': missing/empty {content_key}")
                return False
            continue
        if not card.get("card_title") or not card.get("card_type"):
            return False
        if card["card_type"] not in ("stat_grid", "comparison", "timeline", "highlights"):
            return False
        items = card.get("items")
        if not items or not isinstance(items, list):
            return False

        # Fix 3: Reject single-item cards
        if len(items) < 2:
            print(f"  ⚠️  Rejecting card '{card.get('card_title')}': only {len(items)} item(s)")
            return False

        # Fix 3: Reject comparison cards with fewer than 2 comparable rows
        if card["card_type"] == "comparison" and len(items) < 2:
            print(f"  ⚠️  Rejecting comparison card '{card.get('card_title')}': <2 rows")
            return False

        # Fix 3: Reject bare integers 1-5 as stat values (no unit/context)
        if card["card_type"] == "stat_grid":
            for item in items:
                val = str(item.get("value", "")).strip()
                if re.fullmatch(r"[1-5]", val):
                    print(f"  ⚠️  Rejecting card '{card.get('card_title')}': bare integer stat '{val}'")
                    return False
            hero = card.get("hero_stat") or {}
            hval = str(hero.get("value", "")).strip()
            if re.fullmatch(r"[1-5]", hval):
                print(f"  ⚠️  Rejecting card '{card.get('card_title')}': bare integer hero stat '{hval}'")
                return False

        # Fix 1: Timeline date guardrail — must be within ±18 months of published_at
        if card["card_type"] == "timeline" and pub_date:
            for item in items:
                date_str = str(item.get("date", "")).strip()
                parsed = _parse_timeline_date(date_str, pub_date)
                if parsed is None:
                    # Could not parse — let it through (don't block on unparseable dates)
                    continue
                delta = abs((parsed - pub_date).days)
                if delta > 548:  # ~18 months
                    print(f"  ⚠️  Rejecting timeline card '{card.get('card_title')}': "
                          f"date '{date_str}' is {delta} days from published_at")
                    return False
    return True


def _parse_timeline_date(date_str, pub_date):
    """Parse a timeline date string, defaulting missing year to published year.
    Returns a timezone-aware datetime or None if unparseable."""
    import re
    s = date_str.strip()
    # Try common formats
    fmts = [
        "%B %d, %Y", "%b %d, %Y",           # October 9, 2026 / Oct 9, 2026
        "%Y-%m-%d",                          # 2026-10-09
        "%d %B %Y", "%d %b %Y",              # 9 October 2026
        "%B %Y", "%b %Y",                    # October 2026
        "%Y",                                # 2026
    ]
    for fmt in fmts:
        try:
            dt = datetime.strptime(s, fmt)
            return dt.replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    # Handle "Month D" without year — assume published year
    m = re.fullmatch(r"(January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{1,2})", s, re.I)
    if m:
        try:
            dt = datetime.strptime(f"{m.group(1)} {m.group(2)} {pub_date.year}", "%B %d %Y")
            return dt.replace(tzinfo=timezone.utc)
        except ValueError:
            pass
    # Handle bare year references like "2023 ODI World Cup" — extract year
    m = re.search(r"\b(19|20)\d{2}\b", s)
    if m:
        try:
            return datetime(int(m.group(0)), 6, 15, tzinfo=timezone.utc)
        except ValueError:
            pass
    return None


def save(article_id, data):
    """Save enrichment to Supabase. Also strips writer's key-takeaways div
    from body to prevent duplicate rendering (frontend renders from the
    key_takeaways jsonb column as vdc-takeaways).

    MERGE (not overwrite) data_cards: preserves writer-produced component
    cards (how_to, key_dates, checklist, price_compare) that enrich doesn't
    generate. Without this, the writer's cards are silently dropped.
    """
    now = datetime.now(timezone.utc).isoformat()
    enrich_cards = data.get("data_cards", [])
    # Fetch existing cards so we can merge, not overwrite
    existing_cards = []
    try:
        gr = requests.get(
            f"{SUPABASE_URL}/rest/v1/p2_articles",
            headers=HEADERS_SB,
            params={"id": f"eq.{article_id}", "select": "data_cards"}
        )
        if gr.status_code == 200 and gr.json():
            existing_cards = gr.json()[0].get("data_cards") or []
    except Exception as e:
        print(f"  ⚠ Could not fetch existing data_cards for merge: {e}")
    # Keep writer's component cards (new types enrich doesn't produce)
    WRITER_TYPES = ("how_to", "key_dates", "checklist", "price_compare")
    kept = [c for c in existing_cards
            if isinstance(c, dict) and (c.get("type") in WRITER_TYPES)]
    # Avoid duplicating if enrich somehow produced the same type
    enrich_types = {(c.get("card_type") or c.get("type")) for c in enrich_cards if isinstance(c, dict)}
    kept = [c for c in kept if c.get("type") not in enrich_types]
    merged_cards = kept + enrich_cards
    if kept:
        print(f"  🔀 Merged {len(kept)} writer card(s) with {len(enrich_cards)} enrich card(s)")
    patch_data = {
        "data_cards": merged_cards,
        "key_takeaways": data.get("key_takeaways", []),
        "enriched_at": now
    }
    # Strip writer's key-takeaways from body to avoid duplication
    if data.get("key_takeaways"):
        try:
            import re
            br = requests.get(
                f"{SUPABASE_URL}/rest/v1/p2_articles",
                headers=HEADERS_SB,
                params={"id": f"eq.{article_id}", "select": "body"}
            )
            if br.status_code == 200:
                body = br.json()[0].get("body", "")
                if '<div class="key-takeaways">' in body:
                    new_body = re.sub(
                        r'<div class="key-takeaways"><ul>.*?</ul></div>',
                        '', body, flags=re.DOTALL)
                    new_body = re.sub(r'\n{3,}', '\n\n', new_body)
                    if new_body != body:
                        patch_data["body"] = new_body
                        print(f"  ✂ Stripped duplicate key-takeaways from body")
        except Exception as e:
            print(f"  ⚠ Could not strip writer key-takeaways: {e}")
    r = requests.patch(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS_SB,
        params={"id": f"eq.{article_id}"},
        json=patch_data
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

        if not validate(data, art):
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

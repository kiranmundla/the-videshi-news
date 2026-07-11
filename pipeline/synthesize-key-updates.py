#!/usr/bin/env python3
"""
Synthesize key updates from recent articles across all categories.
Scans published articles, uses GPT to extract the most impactful developments,
and stores them in the key_updates table.

Usage:
  python3 synthesize-key-updates.py [--days 7] [--category immigration] [--dry-run]
"""

import os, sys, json, argparse, hashlib, re
from datetime import datetime, timedelta, timezone

# ── env ──────────────────────────────────────────────────────────────
ENV_SUPA = os.path.expanduser("~/workspace/.env.supabase")
ENV_OAI  = os.path.expanduser("~/workspace/.env.openai")

def load_env(path):
    if not os.path.exists(path):
        return
    for line in open(path):
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

load_env(ENV_SUPA)
load_env(ENV_OAI)

SUPA_URL = os.environ["SUPABASE_URL"]
SUPA_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
OAI_KEY  = os.environ["OPENAI_API_KEY"]

import subprocess, urllib.request, urllib.parse

# ── Category configs ─────────────────────────────────────────────────
CATEGORY_PROMPTS = {
    "immigration": {
        "slug": "immigration",
        "focus": "immigration policy changes, visa bulletin movements, USCIS processing time changes, court rulings on immigration, H-1B/H-4/L-1/EB/OPT rule changes, executive orders, green card backlogs, consulate appointment changes, deportation policies, travel ban updates",
        "examples": "EB-2 India retrogressed to Jan 2012, H-4 EAD rule rescinded, USCIS fee increase finalized, New H-1B registration system proposed, India consulate wait times drop to 30 days"
    },
    "technology": {
        "slug": "technology",
        "focus": "major tech product launches, significant funding rounds by Indian-origin founders, big tech layoffs affecting Indian workers, AI/semiconductor policy, Indian tech company expansions, startup acquisitions, tech policy changes",
        "examples": "Infosys announces 10,000 US hires, TCS wins $2B deal, Indian-origin CEO appointed at major tech firm, New AI regulation proposed, India's semiconductor fab breaks ground"
    },
    "news": {
        "slug": "news",
        "focus": "major India-US diplomatic developments, significant political changes affecting diaspora, trade agreements, defense deals, major incidents involving Indian nationals abroad, bilateral relations shifts",
        "examples": "India-US trade deal signed, PM Modi visits Washington, Major hate crime against Indian student, India joins new international alliance"
    },
    "markets-finance": {
        "slug": "markets-finance",
        "focus": "major market movements affecting NRI investments, RBI policy changes, India GDP milestones, rupee movements, NRI taxation changes, FEMA/LRS updates, mutual fund regulation changes",
        "examples": "Sensex crosses 80,000, Rupee hits record low against dollar, RBI cuts repo rate, New NRI tax rules for property, LRS limit increased"
    },
    "entertainment": {
        "slug": "entertainment",
        "focus": "major Bollywood/Indian film releases and box office, award wins, Indian artists at global events, streaming platform deals, cultural milestones",
        "examples": "Indian film wins at Cannes, Major Bollywood release crosses $100M, Indian artist headlines Coachella, New streaming deal for Indian content"
    },
    "sports": {
        "slug": "sports",
        "focus": "major cricket results and milestones, Indian athletes at global events, IPL developments, World Cup moments, Olympic qualifications, Indian sports personalities achievements",
        "examples": "India wins T20 World Cup, Kohli breaks batting record, Indian wrestler wins Olympic gold, IPL franchise sold for record price"
    },
    "nri-world": {
        "slug": "nri-world",
        "focus": "notable NRI achievements, diaspora community milestones, Indian-origin political appointments, cultural events, community incidents, diaspora organization developments",
        "examples": "Indian-American appointed federal judge, Desi community raises $10M for charity, Indian-origin student wins national science fair"
    },
}

# ── Supabase helpers ─────────────────────────────────────────────────
def supa_get(path, params=None):
    url = f"{SUPA_URL}/rest/v1/{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params, safe="*,.:!()=")
    result = subprocess.run(
        ["curl", "-s", url,
         "-H", f"apikey: {SUPA_KEY}",
         "-H", f"Authorization: Bearer {SUPA_KEY}"],
        capture_output=True, text=True, timeout=30
    )
    return json.loads(result.stdout)

def supa_post(path, data, headers_extra=None):
    url = f"{SUPA_URL}/rest/v1/{path}"
    body = json.dumps(data)
    cmd = ["curl", "-s", "-X", "POST", url,
         "-H", f"apikey: {SUPA_KEY}",
         "-H", f"Authorization: Bearer {SUPA_KEY}",
         "-H", "Content-Type: application/json",
         "-H", "Prefer: return=representation",
         "-d", body]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    return json.loads(result.stdout)

def fetch_articles(category_slug, days):
    """Fetch recent published articles for a category."""
    since = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    params = {
        "select": "id,headline,slug,published_at,subheadline,tags,body",
        "category": f"eq.{category_slug}",
        "status": "eq.published",
        "published_at": f"gte.{since}",
        "order": "published_at.desc",
        "limit": "100",
    }
    return supa_get("p2_articles", params)

def fetch_existing_updates(category, days):
    """Fetch existing key updates to avoid duplicates."""
    since = (datetime.now(timezone.utc) - timedelta(days=days + 7)).strftime("%Y-%m-%d")
    params = {
        "select": "headline,article_slug",
        "category": f"eq.{category}",
        "event_date": f"gte.{since}",
    }
    try:
        return supa_get("key_updates", params)
    except:
        return []

# ── GPT synthesis ────────────────────────────────────────────────────
def call_gpt(messages, temperature=0.2):
    """Call GPT-4o-mini for synthesis."""
    body = json.dumps({
        "model": "gpt-4o-mini",
        "messages": messages,
        "temperature": temperature,
        "response_format": {"type": "json_object"},
        "max_tokens": 2000,
    }).encode()

    result = subprocess.run(
        ["curl", "-s", "-X", "POST", "https://api.openai.com/v1/chat/completions",
         "-H", f"Authorization: Bearer {OAI_KEY}",
         "-H", "Content-Type: application/json",
         "-d", body.decode()],
        capture_output=True, text=True, timeout=60
    )
    resp = json.loads(result.stdout)
    content = resp["choices"][0]["message"]["content"]
    return json.loads(content)

def synthesize_category(category_key, articles, existing_headlines):
    """Use GPT to extract key updates from articles."""
    config = CATEGORY_PROMPTS[category_key]

    # Build article summaries for GPT
    article_summaries = []
    for a in articles[:60]:  # cap at 60 to fit context
        body_preview = (a.get("body") or "")[:500]
        article_summaries.append({
            "id": a["id"],
            "slug": a["slug"],
            "headline": a["headline"],
            "subheadline": a.get("subheadline", ""),
            "date": a.get("published_at", "")[:10],
            "body_preview": body_preview,
        })

    existing_list = [h["headline"] for h in existing_headlines]

    prompt = f"""You are an editorial analyst for The Videshi, an Indian diaspora news site.

Analyze these recent {config['slug']} articles and extract the KEY DEVELOPMENTS — the most impactful events, policy changes, or milestones that a reader should know about.

Focus on: {config['focus']}

Examples of good key updates: {config['examples']}

RULES:
1. Extract only SIGNIFICANT developments — not every article is a key update. Aim for 3-8 updates from this batch.
2. Each update should be a concise, factual statement (not a headline — a statement of what happened).
3. Assign impact: "high" = directly affects many NRIs or is a major policy change, "medium" = noteworthy development, "low" = interesting but minor.
4. Link each update to the most relevant article.
5. Set event_date to when the event HAPPENED (from the article content), not when the article was published.
6. DO NOT duplicate these existing updates: {json.dumps(existing_list[:30])}

Articles to analyze:
{json.dumps(article_summaries, indent=2)}

Return JSON:
{{
  "updates": [
    {{
      "headline": "short factual statement of what happened (max 100 chars)",
      "detail": "one sentence of additional context (max 200 chars)",
      "impact": "high|medium|low",
      "article_id": "uuid of the most relevant article",
      "article_slug": "slug of that article",
      "article_headline": "headline of that article",
      "event_date": "YYYY-MM-DD"
    }}
  ]
}}"""

    messages = [{"role": "user", "content": prompt}]
    return call_gpt(messages)

# ── Main ─────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=7, help="Look back N days")
    parser.add_argument("--category", default=None, help="Single category key (e.g. immigration)")
    parser.add_argument("--dry-run", action="store_true", help="Print but don't insert")
    parser.add_argument("--backfill", type=int, default=0, help="Backfill N days (runs in weekly chunks)")
    args = parser.parse_args()

    categories = [args.category] if args.category else list(CATEGORY_PROMPTS.keys())

    total_inserted = 0

    for cat_key in categories:
        config = CATEGORY_PROMPTS[cat_key]
        cat_slug = config["slug"]

        if args.backfill > 0:
            # Run in weekly chunks for backfill
            for start_offset in range(0, args.backfill, 7):
                end_offset = start_offset
                chunk_days = min(7, args.backfill - start_offset)
                since = datetime.now(timezone.utc) - timedelta(days=start_offset + chunk_days)
                until = datetime.now(timezone.utc) - timedelta(days=start_offset)
                print(f"\n[{cat_key}] Backfill chunk: {since.strftime('%Y-%m-%d')} to {until.strftime('%Y-%m-%d')}")

                articles = fetch_articles(cat_slug, start_offset + chunk_days)
                # Filter to just this chunk
                articles = [a for a in articles
                           if a.get("published_at") and
                           since.isoformat() <= a["published_at"] <= until.isoformat()]

                if not articles:
                    print(f"  No articles in this chunk")
                    continue

                existing = fetch_existing_updates(cat_key, start_offset + chunk_days)
                print(f"  {len(articles)} articles, {len(existing)} existing updates")

                result = synthesize_category(cat_key, articles, existing)
                updates = result.get("updates", [])
                print(f"  GPT extracted {len(updates)} updates")

                for u in updates:
                    u["category"] = cat_key
                    print(f"  {'🔴' if u['impact']=='high' else '🟡' if u['impact']=='medium' else '⚪'} {u['headline']}")
                    print(f"    → {u.get('detail', '')}")
                    print(f"    📰 {u.get('article_headline', '')[:60]}")

                if not args.dry_run and updates:
                    # Clean up for insert
                    for u in updates:
                        u.pop("article_headline_display", None)
                    inserted = supa_post("key_updates", updates)
                    total_inserted += len(inserted)
                    print(f"  ✅ Inserted {len(inserted)} updates")
        else:
            print(f"\n{'='*60}")
            print(f"[{cat_key}] Scanning last {args.days} days of {cat_slug} articles...")

            articles = fetch_articles(cat_slug, args.days)
            if not articles:
                print(f"  No articles found")
                continue

            existing = fetch_existing_updates(cat_key, args.days)
            print(f"  {len(articles)} articles, {len(existing)} existing updates")

            result = synthesize_category(cat_key, articles, existing)
            updates = result.get("updates", [])
            print(f"  GPT extracted {len(updates)} updates")

            for u in updates:
                u["category"] = cat_key
                print(f"  {'🔴' if u['impact']=='high' else '🟡' if u['impact']=='medium' else '⚪'} {u['headline']}")
                print(f"    → {u.get('detail', '')}")
                print(f"    📰 {u.get('article_headline', '')[:60]}")

            if not args.dry_run and updates:
                inserted = supa_post("key_updates", updates)
                total_inserted += len(inserted)
                print(f"  ✅ Inserted {len(inserted)} updates")

    print(f"\n{'='*60}")
    print(f"Done. Total inserted: {total_inserted}")

if __name__ == "__main__":
    main()

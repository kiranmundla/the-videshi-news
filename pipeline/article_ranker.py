#!/usr/bin/env python3
"""
article_ranker.py — Automatic article ranking for The Videshi homepage.

Scores each article on three dimensions via GPT-4o-mini:
  - newsworthiness (1-35): How major is this story?
  - diaspora_impact (1-20): How directly does it affect NRIs?

Plus a computed signal:
  - prominence (1-25): How many RSS feed sources covered this topic?

Display score (computed at read time):
  display_score = newsworthiness + prominence + diaspora_impact + freshness_bonus
  where freshness_bonus = 20 * max(0, 1 - hours_since_publish / 36)

Usage:
  # Score a single article by slug
  python3 article_ranker.py --slug india-h1b-visa-fee-hike

  # Score all unscored articles from last N days
  python3 article_ranker.py --backfill --days 7

  # Score a single article by providing headline + category + body directly
  python3 article_ranker.py --headline "..." --category "immigration" --body "..."

  # Dry run (print scores, don't write to DB)
  python3 article_ranker.py --backfill --days 3 --dry-run
"""

import argparse
import json
import os
import subprocess
import sys
import time
import re
from datetime import datetime, timezone, timedelta

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

SCORE_MODEL = "gpt-4o-mini"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

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
    access_token = os.environ.get("SUPABASE_ACCESS_TOKEN", "")
    url = "https://api.supabase.com/v1/projects/lboecaekpynbpyijrbfz/database/query"
    return _curl_json("POST", url,
                      headers={"Authorization": f"Bearer {access_token}"},
                      data={"query": sql})


def supabase_rest(method, path, data=None, params=None):
    """Call Supabase REST API."""
    base = SUPABASE_URL.rstrip("/")
    url = f"{base}/rest/v1/{path}"
    if params:
        url += "?" + "&".join(f"{k}={v}" for k, v in params.items())
    headers = {
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "apikey": SUPABASE_KEY,
        "Prefer": "return=minimal",
    }
    return _curl_json(method, url, headers=headers, data=data)


def call_openai(messages, temperature=0.1, max_tokens=300):
    """Call OpenAI chat completions via curl."""
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
    }
    payload = {
        "model": SCORE_MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "response_format": {"type": "json_object"},
    }
    resp = _curl_json("POST", url, headers=headers, data=payload)
    content = resp.get("choices", [{}])[0].get("message", {}).get("content", "")
    return json.loads(content) if content else {}

# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

SCORING_PROMPT = """You are a news editor for an Indian diaspora news site targeting NRIs (Non-Resident Indians) in the US, UK, and Canada.

Score this article on two dimensions. Be calibrated — most routine articles should score in the middle ranges. Reserve high scores for genuinely major stories.

## Dimension 1: Newsworthiness (1-35)
How significant is this story on a global/national news scale?

30-35: Historic/breaking — head of state death, major terror attack, war begins/ends, World Cup final result, assassination
25-29: Major — prominent politician death, World Cup semifinal, major policy reversal, market crash (>5%), landmark court ruling
18-24: Significant — cabinet reshuffle, major company earnings/layoffs, tournament quarterfinal, bilateral summit, significant election result
10-17: Standard — policy update, routine earnings, diplomatic meeting, trade statistics, minor election
1-9: Feature/soft — lifestyle piece, food article, travel guide, opinion column, entertainment gossip, routine sports coverage

## Dimension 2: Diaspora Impact (1-20)
How directly does this affect NRIs in US/UK/Canada?

18-20: Direct personal impact — visa/immigration rule change, NRI tax law change, consular service change, direct bilateral agreement affecting diaspora
13-17: Strong diaspora angle — Indian-origin person in major role/achievement abroad, bilateral trade deal affecting NRI industries, major Indian company US/UK expansion
8-12: Moderate connection — India economy (affects investments), major Bollywood release, cricket international, India foreign policy
3-7: Tangential — domestic Indian politics, world news with no direct NRI angle, general entertainment

Article:
Headline: {headline}
Category: {category}
First 600 words: {body}

Respond with JSON only:
{{"newsworthiness": <int 1-35>, "diaspora_impact": <int 1-20>, "reasoning": "<one sentence>"}}"""


def score_article(headline, category, body):
    """Score an article's newsworthiness and diaspora impact via LLM."""
    body_truncated = (body or "")[:2000]  # ~600 words
    prompt = SCORING_PROMPT.format(
        headline=headline,
        category=category,
        body=body_truncated,
    )
    try:
        result = call_openai([
            {"role": "system", "content": "You are a precise news ranking assistant. Return only valid JSON."},
            {"role": "user", "content": prompt},
        ])
        nw = max(1, min(35, int(result.get("newsworthiness", 15))))
        di = max(1, min(20, int(result.get("diaspora_impact", 10))))
        reasoning = result.get("reasoning", "")
        return nw, di, reasoning
    except Exception as e:
        print(f"  ⚠ LLM scoring failed: {e}", file=sys.stderr)
        return None, None, str(e)


def compute_prominence(article_id, headline, category, published_at):
    """
    Compute prominence by finding matching p2_topics and using their
    signal_count (how many RSS feeds covered that topic).
    """
    # Extract key terms from headline (4+ char words, skip stopwords)
    stopwords = {
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
        "plans", "could", "here", "what", "your", "most",
    }
    words = re.findall(r"[a-zA-Z]{4,}", headline.lower())
    keywords = [w for w in words if w not in stopwords]

    if not keywords or not published_at:
        return 8  # default mid-range

    # Take top 5 most distinctive keywords (longer words first = more distinctive)
    keywords.sort(key=len, reverse=True)
    keywords = keywords[:5]

    # Search p2_topics for matching titles within 48h window
    # Require topics to match at least 2 keywords (tight match = same story cluster)
    try:
        # Build a score per topic: count how many keywords appear in its title
        case_parts = " + ".join(
            f"CASE WHEN canonical_title ILIKE '%{kw}%' THEN 1 ELSE 0 END"
            for kw in keywords
        )
        sql = f"""
        SELECT signal_count, kw_hits FROM (
            SELECT signal_count,
                   ({case_parts}) as kw_hits
            FROM p2_topics
            WHERE created_at > '{published_at}'::timestamptz - INTERVAL '48 hours'
              AND created_at < '{published_at}'::timestamptz + INTERVAL '12 hours'
        ) sub
        WHERE kw_hits >= 2
        ORDER BY kw_hits DESC, signal_count DESC
        LIMIT 20
        """
        rows = supabase_query(sql)
        if rows and len(rows) > 0:
            # Count tight-match topics and their max signal_count
            tight_matches = len(rows)
            max_signals = max(int(r.get("signal_count", 1)) for r in rows)
            total_signals = sum(int(r.get("signal_count", 1)) for r in rows)

            # Combine: tight_matches = how many distinct topics cover this story
            # max_signals = the most-cited single topic
            combined = tight_matches + max_signals

            if combined >= 12:
                return 25
            elif combined >= 8:
                return 20
            elif combined >= 5:
                return 16
            elif combined >= 3:
                return 13
            elif combined >= 2:
                return 10
            else:
                return 7

        # Fallback: try single-keyword matches but with a lower ceiling
        any_match = " OR ".join(
            f"canonical_title ILIKE '%{kw}%'" for kw in keywords[:3]
        )
        sql2 = f"""
        SELECT COUNT(*) as cnt, COALESCE(MAX(signal_count), 0) as max_sig
        FROM p2_topics
        WHERE ({any_match})
          AND created_at > '{published_at}'::timestamptz - INTERVAL '48 hours'
          AND created_at < '{published_at}'::timestamptz + INTERVAL '12 hours'
        """
        rows2 = supabase_query(sql2)
        if rows2 and int(rows2[0].get("cnt", 0)) > 0:
            cnt = int(rows2[0]["cnt"])
            max_sig = int(rows2[0]["max_sig"])
            # Single-keyword match caps at 13 (moderate prominence)
            if cnt >= 10 or max_sig >= 3:
                return 13
            elif cnt >= 3:
                return 10
            else:
                return 7
        return 5
    except Exception as e:
        print(f"  ⚠ Prominence computation failed: {e}", file=sys.stderr)
        return 8  # default


def update_article_scores(article_id, newsworthiness, diaspora_impact, prominence):
    """Write scores back to p2_articles."""
    sql = f"""
    UPDATE p2_articles
    SET newsworthiness = {newsworthiness},
        diaspora_impact = {diaspora_impact},
        prominence = {prominence}
    WHERE id = '{article_id}'
    """
    supabase_query(sql)


# ---------------------------------------------------------------------------
# Batch / Backfill
# ---------------------------------------------------------------------------

def fetch_unscored_articles(days=7, limit=200):
    """Fetch published articles missing ranking scores."""
    sql = f"""
    SELECT id, headline, category, body, published_at, slug
    FROM p2_articles
    WHERE status = 'published'
      AND newsworthiness IS NULL
      AND published_at > NOW() - INTERVAL '{days} days'
    ORDER BY published_at DESC
    LIMIT {limit}
    """
    return supabase_query(sql)


def fetch_article_by_slug(slug):
    """Fetch a single article by slug."""
    sql = f"""
    SELECT id, headline, category, body, published_at, slug
    FROM p2_articles
    WHERE slug = '{slug}'
    LIMIT 1
    """
    rows = supabase_query(sql)
    return rows[0] if rows else None


def score_and_update(article, dry_run=False):
    """Score one article and optionally update DB."""
    aid = article["id"]
    headline = article.get("headline", "")
    category = article.get("category", "")
    body = article.get("body", "")
    published_at = article.get("published_at", "")
    slug = article.get("slug", "")

    print(f"\n📰 {headline[:80]}")
    print(f"   Category: {category} | Published: {published_at[:19] if published_at else 'N/A'}")

    # Score via LLM
    nw, di, reasoning = score_article(headline, category, body)
    if nw is None:
        print(f"   ❌ Skipping (LLM error)")
        return None

    # Compute prominence
    prom = compute_prominence(aid, headline, category, published_at)

    # Compute display score (with current freshness)
    if published_at:
        try:
            pub_dt = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
            hours_old = (datetime.now(timezone.utc) - pub_dt).total_seconds() / 3600
            freshness = 20 * max(0, 1 - hours_old / 36)
        except:
            freshness = 0
    else:
        freshness = 0

    display_score = nw + prom + di + freshness

    print(f"   Newsworthiness: {nw}/35 | Diaspora: {di}/20 | Prominence: {prom}/25 | Freshness: {freshness:.1f}/20")
    print(f"   📊 Display Score: {display_score:.1f}/100")
    print(f"   💡 {reasoning}")

    if not dry_run:
        update_article_scores(aid, nw, di, prom)
        print(f"   ✅ Saved to DB")

    return {"slug": slug, "newsworthiness": nw, "diaspora_impact": di,
            "prominence": prom, "freshness": round(freshness, 1),
            "display_score": round(display_score, 1)}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Score articles for homepage ranking")
    parser.add_argument("--slug", help="Score a single article by slug")
    parser.add_argument("--backfill", action="store_true", help="Score all unscored articles")
    parser.add_argument("--days", type=int, default=7, help="Backfill window in days")
    parser.add_argument("--limit", type=int, default=200, help="Max articles to score")
    parser.add_argument("--dry-run", action="store_true", help="Print scores without saving")
    parser.add_argument("--headline", help="Score a headline directly (with --category, --body)")
    parser.add_argument("--category", help="Category for direct scoring")
    parser.add_argument("--body", help="Body text for direct scoring")
    args = parser.parse_args()

    if args.slug:
        article = fetch_article_by_slug(args.slug)
        if not article:
            print(f"❌ Article not found: {args.slug}")
            sys.exit(1)
        score_and_update(article, dry_run=args.dry_run)

    elif args.headline:
        nw, di, reasoning = score_article(
            args.headline,
            args.category or "news",
            args.body or "",
        )
        print(f"\n📰 {args.headline}")
        print(f"   Newsworthiness: {nw}/35 | Diaspora: {di}/20")
        print(f"   💡 {reasoning}")

    elif args.backfill:
        articles = fetch_unscored_articles(days=args.days, limit=args.limit)
        print(f"Found {len(articles)} unscored articles from last {args.days} days\n")

        scored = 0
        errors = 0
        for i, article in enumerate(articles):
            result = score_and_update(article, dry_run=args.dry_run)
            if result:
                scored += 1
            else:
                errors += 1

            # Rate limit: ~3 per second for gpt-4o-mini
            if i < len(articles) - 1:
                time.sleep(0.4)

        print(f"\n{'='*60}")
        print(f"Done. Scored: {scored} | Errors: {errors} | Total: {len(articles)}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()

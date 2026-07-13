#!/usr/bin/env python3
"""
Content Gap Audit — detects major stories The Videshi may have missed.

Fetches trending headlines from Google News across all beats,
compares against recently published articles, and flags gaps.
Uses GPT-4o-mini to judge whether a gap is genuinely major and
relevant to the Indian diaspora audience.

Usage:
  python3 content-gap-audit.py [--hours 24] [--json out.json] [--quiet]
"""

import argparse, json, os, re, subprocess, sys, urllib.parse
from datetime import datetime, timedelta, timezone
from xml.etree import ElementTree as ET

# ── CONFIG ──────────────────────────────────────────────────────────

# Google News search queries per beat — tuned for diaspora relevance
BEATS = {
    "immigration": [
        "india immigration visa H-1B",
        "green card india EB backlog",
        "USCIS immigration policy india",
        "canada india immigration",
        "UK india visa immigration",
    ],
    "technology": [
        "india technology AI startup",
        "indian CEO tech silicon valley",
        "FAANG india engineer",
        "india semiconductor chips",
        "india IT services TCS Infosys",
    ],
    "news": [
        "india US news",
        "india politics economy",
        "india geopolitics diplomacy",
        "india trade tariff",
    ],
    "entertainment": [
        "bollywood movie",
        "indian entertainment celebrity",
        "indian OTT streaming",
    ],
    "markets-finance": [
        "india stock market sensex nifty",
        "india economy RBI",
        "NRI investment india",
    ],
    "sports": [
        "india cricket",
        "indian athletes olympics",
        "IPL cricket",
    ],
    "nri-world": [
        "indian diaspora NRI",
        "indian american achievement",
        "indian community abroad",
    ],
}

GNEWS_RSS = "https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
MAX_ITEMS_PER_QUERY = 15


# ── HELPERS ─────────────────────────────────────────────────────────

def load_env(path):
    """Source a .env file into os.environ."""
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            v = v.strip().strip("'").strip('"')
            os.environ.setdefault(k, v)


def fetch_gnews(query, max_items=MAX_ITEMS_PER_QUERY):
    """Fetch Google News RSS for a search query, return list of {title, source, pubDate}."""
    url = GNEWS_RSS.format(query=urllib.parse.quote_plus(query))
    try:
        result = subprocess.run(
            ["curl", "-s", "-A", "Mozilla/5.0", "--max-time", "10", url],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode != 0:
            return []
    except Exception:
        return []

    items = []
    try:
        root = ET.fromstring(result.stdout)
        for item in root.iter("item"):
            title_el = item.find("title")
            source_el = item.find("source")
            pub_el = item.find("pubDate")
            if title_el is None:
                continue
            items.append({
                "title": title_el.text or "",
                "source": source_el.text if source_el is not None else "",
                "pubDate": pub_el.text if pub_el is not None else "",
            })
            if len(items) >= max_items:
                break
    except ET.ParseError:
        pass
    return items


def parse_rfc2822(datestr):
    """Parse RFC 2822 date to datetime (UTC)."""
    from email.utils import parsedate_to_datetime
    try:
        return parsedate_to_datetime(datestr).astimezone(timezone.utc)
    except Exception:
        return None


def fetch_our_articles(hours=24):
    """Fetch our published articles from the last N hours via Supabase REST."""
    anon_key = os.environ.get("SUPABASE_ANON_KEY", "")
    supabase_url = os.environ.get("SUPABASE_URL", "")
    if not anon_key or not supabase_url:
        print("⚠️  Missing SUPABASE_URL or SUPABASE_ANON_KEY", file=sys.stderr)
        return []

    cutoff = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
    rest_url = (
        f"{supabase_url}/rest/v1/p2_articles"
        f"?select=headline,category,slug"
        f"&status=eq.published"
        f"&published_at=gte.{urllib.parse.quote(cutoff, safe='')}"
        f"&order=published_at.desc"
        f"&limit=200"
    )
    try:
        result = subprocess.run(
            ["curl", "-s", rest_url,
             "-H", f"apikey: {anon_key}",
             "-H", f"Authorization: Bearer {anon_key}"],
            capture_output=True, text=True, timeout=15
        )
        return json.loads(result.stdout) if result.returncode == 0 else []
    except Exception:
        return []


def call_gpt(system_prompt, user_prompt, max_tokens=2000):
    """Call GPT-4o-mini via curl (proxy-safe)."""
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        print("⚠️  Missing OPENAI_API_KEY", file=sys.stderr)
        return None

    payload = json.dumps({
        "model": "gpt-4o-mini",
        "temperature": 0.2,
        "max_tokens": max_tokens,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    })
    try:
        result = subprocess.run(
            ["curl", "-s", "-X", "POST", "https://api.openai.com/v1/chat/completions",
             "-H", f"Authorization: Bearer {api_key}",
             "-H", "Content-Type: application/json",
             "-d", payload],
            capture_output=True, text=True, timeout=60
        )
        resp = json.loads(result.stdout)
        content = resp["choices"][0]["message"]["content"]
        return json.loads(content)
    except Exception as e:
        print(f"⚠️  GPT call failed: {e}", file=sys.stderr)
        return None


# ── MAIN ────────────────────────────────────────────────────────────

def run_audit(hours=24, output_json=None, quiet=False):
    # Load env
    load_env(os.path.expanduser("~/workspace/.env.supabase"))
    load_env(os.path.expanduser("~/workspace/.env.openai"))

    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)

    # 1. Fetch Google News headlines per beat
    if not quiet:
        print(f"📡 Fetching Google News across {len(BEATS)} beats...")
    gnews_by_beat = {}
    all_gnews = []
    for beat, queries in BEATS.items():
        beat_items = []
        for q in queries:
            items = fetch_gnews(q)
            for item in items:
                pub = parse_rfc2822(item.get("pubDate", ""))
                if pub and pub >= cutoff:
                    item["beat"] = beat
                    item["_pub"] = pub
                    beat_items.append(item)
        # Dedupe by title similarity within beat
        seen_titles = set()
        deduped = []
        for item in beat_items:
            # Simple dedup: lowercase first 60 chars
            key = item["title"].lower()[:60]
            if key not in seen_titles:
                seen_titles.add(key)
                deduped.append(item)
        gnews_by_beat[beat] = deduped
        all_gnews.extend(deduped)

    total_gnews = len(all_gnews)
    if not quiet:
        for beat, items in gnews_by_beat.items():
            print(f"  {beat}: {len(items)} headlines")
        print(f"  Total: {total_gnews}")

    if total_gnews == 0:
        if not quiet:
            print("No recent Google News items found. Exiting.")
        return {"gaps": [], "summary": "No external headlines to compare."}

    # 2. Fetch our articles
    if not quiet:
        print(f"\n📰 Fetching our published articles (last {hours}h)...")
    our_articles = fetch_our_articles(hours=hours)
    if not quiet:
        print(f"  Found {len(our_articles)} published articles")

    our_headlines = [a["headline"] for a in our_articles if a.get("headline")]
    our_headlines_lower = [h.lower().strip() for h in our_headlines]
    our_categories = {}
    for a in our_articles:
        cat = a.get("category", "other")
        our_categories.setdefault(cat, []).append(a["headline"])

    # Pre-filter: remove Google News items that match our own published headlines
    def headline_matches_ours(gnews_title):
        """Check if a Google News headline is essentially one we already published."""
        gt = gnews_title.lower().strip()
        for oh in our_headlines_lower:
            # Exact or near-exact match
            if gt == oh or gt.rstrip('.') == oh.rstrip('.'):
                return True
            # Check significant word overlap (handles minor wording differences)
            g_words = set(re.sub(r'[^\w\s]', '', gt).split())
            o_words = set(re.sub(r'[^\w\s]', '', oh).split())
            sig_g = {w for w in g_words if len(w) > 3}
            sig_o = {w for w in o_words if len(w) > 3}
            if sig_g and sig_o:
                overlap = len(sig_g & sig_o)
                # If 60%+ of the shorter headline's significant words match, it's covered
                min_len = min(len(sig_g), len(sig_o))
                if min_len > 0 and overlap / min_len >= 0.6:
                    return True
        return False

    # Filter each beat's items
    filtered_count = 0
    for beat in gnews_by_beat:
        before = len(gnews_by_beat[beat])
        gnews_by_beat[beat] = [item for item in gnews_by_beat[beat]
                                if not headline_matches_ours(item["title"])]
        filtered_count += before - len(gnews_by_beat[beat])

    if filtered_count > 0 and not quiet:
        print(f"  (pre-filtered {filtered_count} headlines we already cover)")

    # 3. Single GPT call with all remaining headlines vs all our articles
    if not quiet:
        print("\n🔍 Analyzing for must-cover gaps...")

    # Combine all remaining Google News headlines, deduped
    remaining_gnews = []
    seen_titles = set()
    for beat, items in gnews_by_beat.items():
        for item in items:
            key = item["title"].lower()[:60]
            if key not in seen_titles:
                seen_titles.add(key)
                remaining_gnews.append(item)

    if not remaining_gnews:
        if not quiet:
            print("  ✅ All external headlines already covered!")
        return {"timestamp": datetime.now(timezone.utc).isoformat(), "must_cover_gaps": 0, "gaps": []}

    gnews_str = "\n".join(
        f"- {item['title']} ({item.get('source', '?')})"
        for item in remaining_gnews[:60]
    )
    our_all_str = "\n".join(f"- {h}" for h in our_headlines[:150])

    system = (
        "You are a ruthlessly selective news coverage auditor for The Videshi, an Indian diaspora news site. "
        "Your ONLY job: find stories so major that if a reader saw them on CNN/BBC/TOI and NOT on The Videshi, "
        "they'd think we're asleep.\n\n"
        "THE BAR IS EXTREMELY HIGH. Flag ONLY:\n"
        "- New LAW, executive order, or court ruling directly changing immigration/visa rules for Indians\n"
        "- Market crash/correction of 3%+ on Sensex/Nifty, or major rupee move\n"
        "- Billion-dollar+ deals involving India or Indian-origin leaders\n"
        "- Death, arrest, or major appointment of a globally prominent Indian-origin figure\n"
        "- Terrorist attack, natural disaster, or military action directly involving India or large diaspora populations\n"
        "- Major bilateral event (PM/President level summit, trade deal signed, sanctions)\n\n"
        "DO NOT FLAG:\n"
        "- Government spending announcements (₹1000 crore for X, new scheme launched)\n"
        "- Routine policy discussions, negotiations, or talks in progress\n"
        "- Analysis, opinion, or commentary pieces\n"
        "- Celebrity/entertainment news of any kind\n"
        "- Routine corporate news, earnings, partnerships under $1B\n"
        "- Sports results unless truly historic (World Cup final, Olympic gold)\n"
        "- Financial scheme updates (RBI programs, banking initiatives)\n\n"
        "CRITICAL — CHECK BEFORE FLAGGING:\n"
        "A story is COVERED if our published list has ANY article about the same underlying event, "
        "even with completely different wording. 'Sensex drops 600 points' and 'Markets tumble on Iran tensions' "
        "= SAME EVENT = COVERED. You MUST check every candidate against the full list of our articles below. "
        "If in doubt, it's covered.\n\n"
        "Multiple external headlines about the same event = ONE story. Deduplicate.\n\n"
        "Most days should have 0-1 gaps. Return empty gaps array when coverage is solid.\n\n"
        "Return JSON: {\"gaps\": [{\"headline\": str, \"source\": str, \"why_must_cover\": str}], \"verdict\": str}"
    )

    user = (
        f"GOOGLE NEWS HEADLINES (last {hours}h, all beats):\n{gnews_str}\n\n"
        f"OUR PUBLISHED ARTICLES (last {hours}h):\n{our_all_str}\n\n"
        "Find MUST-COVER gaps only. Check each candidate against our full list. "
        "Most days should have 0. Be ruthless."
    )

    all_gaps = []
    result = call_gpt(system, user, max_tokens=1500)
    if result and result.get("gaps"):
        all_gaps = result["gaps"]
        if not quiet:
            for g in all_gaps:
                print(f"  🔴 {g['headline']}")
                print(f"     → {g.get('why_must_cover', '')}")
    if not all_gaps and not quiet:
        verdict = result.get("verdict", "Coverage is solid") if result else "?"
        print(f"  ✅ {verdict}")

    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "hours_checked": hours,
        "external_headlines_checked": total_gnews,
        "our_articles_checked": len(our_articles),
        "must_cover_gaps": len(all_gaps),
        "gaps": all_gaps,
    }

    if output_json:
        with open(output_json, "w") as f:
            json.dump(report, f, indent=2)
        if not quiet:
            print(f"\n📄 Report saved to {output_json}")

    if not quiet:
        print(f"\n{'='*60}")
        print(f"CONTENT GAP AUDIT — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
        print(f"Checked {total_gnews} external headlines vs {len(our_articles)} of our articles")
        print(f"Must-cover gaps: {len(all_gaps)}")
        if not all_gaps:
            print("✅ No must-cover stories missed — coverage is solid.")
        print(f"{'='*60}")

    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Content Gap Audit")
    parser.add_argument("--hours", type=int, default=24, help="Lookback window (default 24)")
    parser.add_argument("--json", type=str, help="Save JSON report to this path")
    parser.add_argument("--quiet", action="store_true", help="Minimal output")
    args = parser.parse_args()

    report = run_audit(hours=args.hours, output_json=args.json, quiet=args.quiet)

    # Exit code: 0 = no gaps, 1 = must-cover gaps found
    sys.exit(1 if report.get("must_cover_gaps", 0) > 0 else 0)

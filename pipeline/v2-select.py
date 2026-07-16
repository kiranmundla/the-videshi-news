#!/usr/bin/env python3
"""
Pipeline V2 Selector — Reads recent signals, clusters them, picks the best
stories for Hatch to write. Outputs a JSON file with candidates + source URLs.

Usage:
  python3 v2-select.py [--hours 4] [--max 10] [--out /tmp/v2-candidates.json]

Hatch reads the output and writes articles from actual source content.
"""

import os, sys, json, re, hashlib, time
from datetime import datetime, timezone, timedelta
from urllib.parse import quote as urlquote, urlparse
import subprocess

# ── Options ───────────────────────────────────────────────────────────────────

HOURS = 4
MAX_CANDIDATES = 10
OUT_PATH = "/tmp/v2-candidates.json"

for i, arg in enumerate(sys.argv[1:], 1):
    if arg == "--hours" and i < len(sys.argv) - 1:
        HOURS = int(sys.argv[i + 1])
    elif arg == "--max" and i < len(sys.argv) - 1:
        MAX_CANDIDATES = int(sys.argv[i + 1])
    elif arg == "--out" and i < len(sys.argv) - 1:
        OUT_PATH = sys.argv[i + 1]

NOW          = datetime.now(timezone.utc)
NOW_ISO      = NOW.isoformat()

# ── Supabase ──────────────────────────────────────────────────────────────────

def load_env(*paths):
    env = {}
    for p in paths:
        p = os.path.expanduser(p)
        if not os.path.exists(p):
            continue
        with open(p) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    env[k.strip()] = v.strip().strip('"').strip("'")
    return env

ENV = load_env("~/workspace/.env.supabase")
SB_URL = ENV.get("SUPABASE_URL", "")
SB_KEY = ENV.get("SUPABASE_SERVICE_ROLE_KEY", "")

def sb_get(endpoint, params=None, range_header=None):
    url = f"{SB_URL}/rest/v1/{endpoint}"
    if params:
        qs = "&".join(f"{k}={urlquote(str(v), safe='.,()_')}" for k, v in params.items())
        url = f"{url}?{qs}"
    cmd = ["curl", "-sS", "--max-time", "20", url,
           "-H", f"apikey: {SB_KEY}",
           "-H", f"Authorization: Bearer {SB_KEY}"]
    if range_header:
        cmd += ["-H", f"Range: {range_header}"]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=25)
    try:
        return json.loads(r.stdout)
    except:
        return []

# ── Text analysis ─────────────────────────────────────────────────────────────

STOP_WORDS = {
    'the','and','for','are','was','were','has','have','had','with','from',
    'that','this','will','been','being','after','before','about','into',
    'over','amid','says','said','more','than','also','just','first','last',
    'next','here','what','when','where','which','while','under','could',
    'would','should','their','there','other','some','most','like','make',
    'only','very','well','still','does','look','need','come','news',
    'people','world','year','years','time','back','take','gets',
    'report','reports','new','many','much','even','every','each',
}

def title_keywords(title):
    words = re.findall(r'[a-z]+', title.lower())
    return set(w for w in words if len(w) >= 4 and w not in STOP_WORDS)

# ── Category detection ────────────────────────────────────────────────────────

CATEGORY_KEYWORDS = {
    "immigration": [
        "visa","immigration","green card","h1b","h-1b","uscis","deportation",
        "asylum","work permit","eb-2","eb-3","opt ","ice ","dhs","cbp",
        "naturalization","citizenship","undocumented","dreamer","daca",
    ],
    "technology": [
        "tech","ai ","artificial intelligence","startup","software","google",
        "apple","meta ","chip","nvidia","openai","microsoft","quantum",
        "cybersecurity","semiconductor","data breach","cloud computing",
    ],
    "entertainment": [
        "bollywood","film","movie","actor","actress","box office","ott",
        "netflix","music","album","celebrity","grammy","oscar","emmy",
        "disney","streaming","concert","award show",
    ],
    "markets-finance": [
        "market","sensex","nifty","stock","gdp","rupee","rbi","nasdaq",
        "dow jones","s&p 500","earnings","fed ","inflation","ipo ",
        "cryptocurrency","bitcoin","wall street","banking","recession",
    ],
    "sports": [
        "cricket","ipl","sports","tennis","match","wicket","goal ",
        "football","soccer","fifa","world cup","athlete","olympic",
        "nba","nfl","premier league","champions league",
    ],
    "nri-world": [
        "nri","diaspora","indian-american","indian american","indian origin",
        "overseas indian","oci ","pio ","expat",
    ],
    "lifestyle": [
        "health","food","yoga","wellness","recipe","travel","fashion",
        "beauty","meditation","ayurveda",
    ],
}

def detect_category(title):
    t = title.lower()
    for cat, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in t for kw in keywords):
            return cat
    return "news"

# ── Diaspora relevance keywords (fast pre-filter) ────────────────────────────

DIASPORA_STRONG = {
    # Auto-pass: clearly diaspora-relevant
    "h-1b","h1b","green card","visa","immigration","uscis","nri","diaspora",
    "indian-american","indian american","indian origin","oci","pio",
    "desi","diwali","navratri","holi","bollywood","ipl","cricket",
    "modi","india","bjp","congress","rupee","sensex","nifty",
    "infosys","tcs","wipro","hcl tech","reliance","tata","adani",
    "sundar pichai","satya nadella","indra nooyi","sanjay mehrotra",
    "india us","india uk","india canada","indian student",
}

DIASPORA_REJECT = {
    # Auto-reject: clearly not relevant or bureaucratic noise
    "county fair","local school board","high school football",
    "little league","yard sale","garage sale","traffic accident",
    "weather forecast","road closure","parking meter",
    "settlement order","listing obligations","disclosure requirements",
    "circular no.","notification no.","gazette notification",
}

def quick_diaspora_check(title):
    """Quick keyword check: 'yes', 'no', or 'maybe' (needs LLM)."""
    t = title.lower()
    for kw in DIASPORA_REJECT:
        if kw in t:
            return "no"
    for kw in DIASPORA_STRONG:
        if kw in t:
            return "yes"
    return "maybe"

# ── Recent article dedup ─────────────────────────────────────────────────────

def load_recent_headlines(days=3):
    """Load recent published article headlines for dedup."""
    cutoff = (NOW - timedelta(days=days)).isoformat()
    rows = sb_get("p2_articles", {
        "select": "headline,slug",
        "status": "eq.published",
        "published_at": f"gte.{cutoff}",
        "order": "published_at.desc",
    }, range_header="0-499")
    if not rows or isinstance(rows, dict):
        return []
    return rows

def is_already_covered(title, recent_articles):
    """Check if a story is already covered (>60% keyword overlap with existing)."""
    title_kw = title_keywords(title)
    if len(title_kw) < 2:
        return False
    for art in recent_articles:
        art_kw = title_keywords(art.get("headline", ""))
        if not art_kw:
            continue
        overlap = len(title_kw & art_kw)
        min_len = min(len(title_kw), len(art_kw))
        if min_len >= 2 and overlap / min_len >= 0.6:
            return True
    return False

# ── Google News URL resolution ────────────────────────────────────────────────

def resolve_google_news_url(url):
    """Resolve Google News redirect URL to actual article URL."""
    if "news.google.com" not in url:
        return url
    # Google News URLs redirect to the actual article
    cmd = ["curl", "-sS", "--max-time", "5", "-o", "/dev/null", "-w", "%{redirect_url}", "-L", "--max-redirs", "1", url]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=8)
        if r.stdout and r.stdout.startswith("http"):
            return r.stdout.strip()
    except:
        pass
    return url

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    t0 = time.time()
    print(f"\n{'='*60}")
    print(f"Pipeline V2 Selector — {NOW.strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"  Window: {HOURS}h, Max candidates: {MAX_CANDIDATES}")
    print(f"{'='*60}")

    # ── Load recent signals ───────────────────────────────────────────────────
    print(f"\n── Loading signals from last {HOURS}h ──")
    cutoff = (NOW - timedelta(hours=HOURS)).isoformat()
    signals = []
    offset = 0
    while True:
        page = sb_get("p2_signals", {
            "select": "id,title,original_url,published_at,fetched_at,source_type,source_name,google_cluster_size",
            "fetched_at": f"gte.{cutoff}",
            "order": "fetched_at.desc",
        }, range_header=f"{offset}-{offset+999}")
        if not page or isinstance(page, dict):
            break
        signals.extend(page)
        if len(page) < 1000:
            break
        offset += 1000

    print(f"  Found {len(signals)} signals")
    if not signals:
        print("  Nothing to do.")
        json.dump({"candidates": [], "timestamp": NOW_ISO}, open(OUT_PATH, "w"))
        return

    # ── Cluster signals by story ──────────────────────────────────────────────
    print(f"\n── Clustering signals ──")
    clusters = {}
    for sig in signals:
        title = sig.get("title", "")
        if not title:
            continue
        # Find matching cluster
        match_key = None
        sig_kw = title_keywords(title)
        if sig_kw and len(sig_kw) >= 2:
            best_overlap = 0
            for key, cluster_sigs in clusters.items():
                cluster_kw = title_keywords(cluster_sigs[0]["title"])
                if not cluster_kw:
                    continue
                overlap = len(sig_kw & cluster_kw)
                min_len = min(len(sig_kw), len(cluster_kw))
                if min_len >= 2 and overlap / min_len >= 0.5 and overlap > best_overlap:
                    best_overlap = overlap
                    match_key = key

        if match_key:
            clusters[match_key].append(sig)
        else:
            key = re.sub(r'[^a-z0-9\s]', '', title.lower().strip())[:60]
            clusters.setdefault(key, []).append(sig)

    print(f"  {len(clusters)} clusters from {len(signals)} signals")

    # ── Score and rank clusters ───────────────────────────────────────────────
    print(f"\n── Scoring clusters ──")
    recent_articles = load_recent_headlines()
    print(f"  Recent articles loaded: {len(recent_articles)}")

    scored = []
    for key, sigs in clusters.items():
        best = max(sigs, key=lambda s: len(s.get("title", "")))
        title = best["title"]
        n = len(sigs)

        # Google News cluster boost
        google_boost = sum(s.get("google_cluster_size", 1) for s in sigs if s.get("source_type") == "google_news")
        effective_size = n + max(0, google_boost - len([s for s in sigs if s.get("source_type") == "google_news"]))

        # Source diversity
        sources = set()
        for s in sigs:
            sources.add(s.get("source_name") or s.get("source_type", "rss"))
        source_diversity = len(sources)

        # Category
        cat = detect_category(title)

        # Diaspora check
        diaspora = quick_diaspora_check(title)
        if diaspora == "no":
            continue

        # Already covered?
        if is_already_covered(title, recent_articles):
            continue

        # Score: cluster_size (40%) + source_diversity (30%) + recency (20%) + diaspora_boost (10%)
        score_cluster = min(effective_size * 15, 60)
        score_sources = min(source_diversity * 12, 40)

        # Recency: hours since first signal
        try:
            oldest = min(s.get("published_at") or s.get("fetched_at", "") for s in sigs)
            if oldest:
                from email.utils import parsedate_to_datetime
                try:
                    age_hours = (NOW - datetime.fromisoformat(oldest.replace("Z", "+00:00"))).total_seconds() / 3600
                except:
                    age_hours = 2
            else:
                age_hours = 2
        except:
            age_hours = 2
        score_recency = max(0, 30 - age_hours * 3)  # Newer = higher

        diaspora_boost = 20 if diaspora == "yes" else 0

        total_score = score_cluster + score_sources + score_recency + diaspora_boost

        # Collect source URLs
        source_urls = []
        seen_urls = set()
        for s in sigs:
            u = s.get("original_url", "")
            if u and u not in seen_urls:
                seen_urls.add(u)
                source_urls.append(u)

        scored.append({
            "title": title,
            "category": cat,
            "score": round(total_score, 1),
            "signal_count": n,
            "effective_size": effective_size,
            "source_diversity": source_diversity,
            "diaspora_relevance": diaspora,
            "source_urls": source_urls[:8],  # Top 8 source URLs
            "all_signals": [{"title": s["title"], "url": s["original_url"], "source": s.get("source_name", "")} for s in sigs[:10]],
        })

    # Sort by score
    scored.sort(key=lambda x: x["score"], reverse=True)

    # Category balance: max 3 per category to ensure diversity
    balanced = []
    cat_counts = {}
    for c in scored:
        cat = c["category"]
        cat_counts.setdefault(cat, 0)
        if cat_counts[cat] < 3:
            balanced.append(c)
            cat_counts[cat] += 1
        if len(balanced) >= MAX_CANDIDATES:
            break

    # ── Output ────────────────────────────────────────────────────────────────
    output = {
        "timestamp": NOW_ISO,
        "window_hours": HOURS,
        "total_signals": len(signals),
        "total_clusters": len(clusters),
        "candidates": balanced,
    }
    with open(OUT_PATH, "w") as f:
        json.dump(output, f, indent=2)

    elapsed = time.time() - t0
    print(f"\n{'='*60}")
    print(f"CANDIDATES: {len(balanced)} stories selected")
    for i, c in enumerate(balanced, 1):
        d = "✅" if c["diaspora_relevance"] == "yes" else "❓"
        print(f"  {i}. [{c['category']}] {c['title'][:70]}")
        print(f"     Score: {c['score']} | Signals: {c['effective_size']} | Sources: {c['source_diversity']} | Diaspora: {d}")
    print(f"\n  Output: {OUT_PATH}")
    print(f"  Time: {elapsed:.1f}s")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()

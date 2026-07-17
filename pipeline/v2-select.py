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
PER_CAT_MAX = 3  # max candidates per category
OUT_PATH = "/tmp/v2-candidates.json"

for i, arg in enumerate(sys.argv[1:], 1):
    if arg == "--hours" and i < len(sys.argv) - 1:
        HOURS = int(sys.argv[i + 1])
    elif arg == "--per-cat" and i < len(sys.argv) - 1:
        PER_CAT_MAX = int(sys.argv[i + 1])
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

ENV = load_env("~/workspace/.env.supabase", "~/workspace/.env.openai")
SB_URL = ENV.get("SUPABASE_URL", "")
SB_KEY = ENV.get("SUPABASE_SERVICE_ROLE_KEY", "")
OPENAI_KEY = ENV.get("OPENAI_API_KEY", "")

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
        "market","sensex","nifty","stock","futures","gdp","rupee","rbi","nasdaq",
        "dow jones","s&p 500","earnings","fed ","inflation","ipo ",
        "cryptocurrency","bitcoin","wall street","banking","recession",
        "shares","rally","slips","plunges","tumbles",
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
    "food": [
        "food","recipe","restaurant","chef","cuisine","cooking","dish",
        "foodie","kitchen","meal","snack","curry","biryani","samosa",
        "dosa","masala","spice","vegan","vegetarian",
    ],
    "travel": [
        "travel","tourism","airline","flight","airport","hotel","destination",
        "vacation","trip","booking","passenger","cruise",
    ],
    "lifestyle": [
        "health","yoga","wellness","fashion",
        "beauty","meditation","ayurveda","fitness","skincare","mental health",
    ],
}

def detect_category(title):
    t = " " + title.lower() + " "
    scores = {}
    for cat, keywords in CATEGORY_KEYWORDS.items():
        hits = 0
        for kw in keywords:
            if kw.endswith(" "):
                if kw in t:
                    hits += 1
            else:
                pattern = r'\b' + re.escape(kw.strip()) + r'\b'
                if re.search(pattern, t):
                    hits += 1
        if hits > 0:
            scores[cat] = hits
    if not scores:
        return "news"
    return max(scores, key=scores.get)

# ── Diaspora relevance keywords (fast pre-filter) ────────────────────────────

DIASPORA_STRONG = {
    "h-1b","h1b","green card","visa","immigration","uscis","nri","diaspora",
    "indian-american","indian american","indian origin","oci","pio",
    "desi","diwali","navratri","holi","bollywood","ipl","cricket",
    "modi","india","bjp","congress","rupee","sensex","nifty",
    "infosys","tcs","wipro","hcl tech","reliance","tata","adani",
    "sundar pichai","satya nadella","indra nooyi","sanjay mehrotra",
    "india us","india uk","india canada","indian student",
}

DIASPORA_REJECT = {
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
    cmd = ["curl", "-sS", "--max-time", "5", "-o", "/dev/null", "-w", "%{redirect_url}", "-L", "--max-redirs", "1", url]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=8)
        if r.stdout and r.stdout.startswith("http"):
            return r.stdout.strip()
    except:
        pass
    return url

# ── LLM helpers ───────────────────────────────────────────────────────────────

def llm_call(payload_dict, label="LLM call", timeout=50):
    """Single OpenAI API call. Returns (parsed_content, usage_dict, error_str)."""
    payload_file = f"/tmp/llm_{label.replace(' ','_')}_{int(time.time())}.json"
    with open(payload_file, "w") as f:
        json.dump(payload_dict, f)
    try:
        r = subprocess.run([
            "curl", "-s", "--max-time", str(timeout),
            "https://api.openai.com/v1/chat/completions",
            "-H", f"Authorization: Bearer {OPENAI_KEY}",
            "-H", "Content-Type: application/json",
            "-d", f"@{payload_file}"
        ], capture_output=True, text=True, timeout=timeout+5)
        os.remove(payload_file)
        resp = json.loads(r.stdout)
        if "error" in resp:
            return None, {}, f"API error: {resp['error'].get('message', '')[:120]}"
        content = json.loads(resp["choices"][0]["message"]["content"])
        usage = resp.get("usage", {})
        return content, usage, None
    except Exception as e:
        try: os.remove(payload_file)
        except: pass
        return None, {}, str(e)


# ── Pass 2: LLM semantic merge ───────────────────────────────────────────────

MERGE_PROMPT = """You are grouping news headlines that cover the SAME underlying story or event.

Two headlines cover the same story if they report on the same event, announcement, ruling, development, 
or situation — even if worded completely differently.

Examples of SAME story:
- "USCIS Confirms No Second H-1B Lottery for FY 2027" ↔ "H-1B Visa Cap Reached: Implications for Indian Professionals"
- "Cricket World Mourns the Passing of Sir Garfield Sobers" ↔ "West Indies Legend Sobers Dies at 89"
- "Nasdaq Falls 1.6% Amid Chip Rout" ↔ "Global Stocks Plummet Amid Semiconductor Turmoil"

Examples of DIFFERENT stories (do NOT merge):
- "Trump Proposes Immigration Reform" ↔ "Trump Signs Trade Deal with India" (different topics)
- "Netflix Q3 Earnings Miss" ↔ "Netflix Launches New Gaming Feature" (different events)
- "India vs Pakistan Cricket Highlights" ↔ "Cricket World Cup Format Changes" (different events)

Given the numbered headlines below, return groups of IDs that cover the SAME story.
Only group headlines you are CONFIDENT cover the same event. When in doubt, keep separate.

Return JSON: {"groups": [[1, 5], [3, 8, 12], ...]}
Headlines not in any group are unique stories. Empty groups array if no merges found.
"""

def llm_semantic_merge(cluster_titles):
    """Send cluster titles to LLM to find same-story clusters that keywords missed.
    Returns list of sets: each set contains indices that should be merged."""
    if not cluster_titles or not OPENAI_KEY or len(cluster_titles) < 2:
        return []

    # Build numbered list — send in chunks if >120 titles to keep prompt manageable
    CHUNK = 120
    all_groups = []

    for chunk_start in range(0, len(cluster_titles), CHUNK):
        chunk = cluster_titles[chunk_start:chunk_start + CHUNK]
        lines = [f"{chunk_start + i + 1}. {t[:140]}" for i, t in enumerate(chunk)]

        content, usage, error = llm_call({
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": MERGE_PROMPT + "\n\nHeadlines:\n" + "\n".join(lines)}],
            "response_format": {"type": "json_object"},
            "max_tokens": 2000,
            "temperature": 0,
        }, label=f"merge_{chunk_start}")

        cost = 0
        if usage:
            cost = usage.get("prompt_tokens", 0) * 0.15 / 1_000_000 + usage.get("completion_tokens", 0) * 0.6 / 1_000_000

        if error:
            print(f"  ⚠ Merge LLM error (chunk {chunk_start}): {error}")
            continue

        groups = content.get("groups", [])
        for g in groups:
            if isinstance(g, list) and len(g) >= 2:
                # Convert to 0-indexed
                all_groups.append(set(idx - 1 for idx in g if isinstance(idx, int)))

        print(f"  Merge chunk {chunk_start}-{chunk_start+len(chunk)}: {len(groups)} groups found (${cost:.4f})")

    return all_groups


# ── Pass 3: LLM scoring with 3-way classification ────────────────────────────

LLM_PROMPT = """You are the editorial filter for The Videshi, a news site for the Indian diaspora — Indians living in the US, UK, Canada, and Australia.

Your readers are educated professionals who LIVE in these countries. They care about:
- India news, Indian culture, Bollywood, cricket, Indian politics & economy
- Immigration policy (H-1B, green cards, visa rules, deportation)
- Indian-origin people in tech, business, politics, sports, entertainment
- BUT ALSO: Major US/UK/global news that affects their daily lives — economy, wars, natural disasters, public health, major policy changes, elections, weather emergencies, food safety recalls
- Big global events everyone should know about
- Indian food, recipes, restaurants, chefs (Sanjeev Kapoor, Ranveer Brar, Vikas Khanna, etc.)
- Travel relevant to diaspora (Air India, Indian destinations, visa-free countries for Indians)
- Bollywood AND Hollywood entertainment, streaming (Netflix, Disney+, OTT), celebrity news
- Health, wellness, yoga, Ayurveda, lifestyle with any Indian connection

They are NOT interested in:
- Hyper-local US news (local school board, yard sale, parking meters, small-town crime)
- Minor celebrity gossip with no Indian connection
- Niche bureaucratic/regulatory noise

IMPORTANT: Be generous with food, entertainment, travel, and lifestyle stories — if a story has ANY Indian connection (Indian chef, Indian restaurant, Bollywood, Indian airline, Indian ingredient, Indian wellness practice), score it at least 3. These categories are essential for a well-rounded diaspora publication.

COVERAGE CLASSIFICATION:
You will receive ALREADY PUBLISHED headlines. For each new story, classify its coverage status:
- "new" — We have NOT covered this topic/event yet. No published headline addresses this event or subject. Write it.
- "update" — We published an article on this topic, BUT this signal contains a MAJOR new development that our readers NEED to know and that our existing article does NOT cover. Examples: a court reversal of a ruling we reported, casualty count doubling, a second earthquake hitting the same region, a CEO resignation following an earnings report we covered. The bar is HIGH — a slightly different angle, additional commentary, or minor new details do NOT qualify as an update. When in doubt, mark as duplicate.
- "duplicate" — We already have an article covering this event/topic. Even if the wording is different or the angle is slightly different, if a reader who read our published article would NOT learn anything major from this new signal, it is a duplicate. This is the DEFAULT when a published headline covers the same underlying event.

WITHIN-BATCH duplicates: if two stories in this batch cover the same event, mark all but the highest-importance one as "duplicate".

Be STRICT about duplicates. Publishing the same story twice with different headlines looks bad to readers and hurts SEO. When in doubt between "update" and "duplicate", choose "duplicate".

For each story below, provide:
1. "relevant": true/false — is this relevant to our audience?
2. "score": 1-5 importance:
   - 5 = Everyone-must-know breaking news (war, major immigration overhaul, catastrophic disaster)
   - 4 = Very important (major economic policy, significant bilateral news, big tech layoffs, immigration ruling)
   - 3 = Important (notable achievement, diplomatic moves, significant cultural story, major sports)
   - 2 = Moderately relevant (interesting cultural piece, community story, mid-tier entertainment/sports)
   - 1 = Mildly relevant (light feature, tangential connection)
3. "coverage": "new" | "update" | "duplicate"
4. "reason": 1-sentence explanation (if duplicate, mention which published headline it duplicates)

Respond as JSON: {"results": [{"id": 1, "relevant": true, "coverage": "new", "score": 4, "reason": "..."},...]}\n"""


def llm_score_stories(stories, recent_articles=None):
    """Batch-score stories via GPT-4o-mini with parallel batches."""
    if not stories or not OPENAI_KEY:
        return {}

    from concurrent.futures import ThreadPoolExecutor, as_completed

    # Build the "already published" context for dedup
    published_block = ""
    if recent_articles:
        pub_lines = [f"- {a.get('headline', '')}" for a in recent_articles[:150]]
        published_block = "\n\nALREADY PUBLISHED HEADLINES (check coverage status against these):\n" + "\n".join(pub_lines)

    BATCH_SIZE = 40
    all_results = {}
    total_cost = 0.0

    def score_batch(batch_start, batch):
        lines = []
        for i, s in enumerate(batch):
            src_info = f" [signals: {s.get('signal_count', 1)}, sources: {s.get('source_diversity', 1)}]"
            desc_part = f" | {s.get('description', '')[:150]}" if s.get('description') else ""
            lines.append(f"{i+1}. {s['title'][:120]}{desc_part}{src_info}")

        payload = {
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": LLM_PROMPT + published_block + "\n\nNEW STORIES TO EVALUATE:\n" + "\n".join(lines)}],
            "response_format": {"type": "json_object"},
            "max_tokens": max(len(batch) * 80, 1200),
            "temperature": 0
        }

        content, usage, error = llm_call(payload, label=f"score_{batch_start}", timeout=50)
        cost = 0
        if usage:
            cost = usage.get("prompt_tokens", 0) * 0.15 / 1_000_000 + usage.get("completion_tokens", 0) * 0.6 / 1_000_000

        # Retry once on failure
        if error:
            time.sleep(2)
            content, usage2, error = llm_call(payload, label=f"score_{batch_start}_retry", timeout=60)
            if usage2:
                cost += usage2.get("prompt_tokens", 0) * 0.15 / 1_000_000 + usage2.get("completion_tokens", 0) * 0.6 / 1_000_000

        if error:
            return batch_start, {}, cost, error

        results = {}
        for item in content.get("results", []):
            idx = item.get("id", 0) - 1
            if 0 <= idx < len(batch):
                global_idx = batch_start + idx
                coverage = item.get("coverage", "new")
                # Backward compat: also check old "duplicate" field
                if item.get("duplicate", False) and coverage == "new":
                    coverage = "duplicate"
                results[global_idx] = {
                    "relevant": item.get("relevant", True),
                    "coverage": coverage,
                    "score": item.get("score", 1) if item.get("relevant", True) else 0,
                    "reason": item.get("reason", ""),
                }
        return batch_start, results, cost, None

    # Build batches
    batches = [(i, stories[i:i+BATCH_SIZE]) for i in range(0, len(stories), BATCH_SIZE)]

    # Run in parallel (10 concurrent)
    with ThreadPoolExecutor(max_workers=5) as pool:
        futures = [pool.submit(score_batch, start, batch) for start, batch in batches]
        done = 0
        for f in as_completed(futures):
            batch_start, results, cost, error = f.result()
            done += 1
            total_cost += cost
            if error:
                print(f"  ⚠ Batch {batch_start//BATCH_SIZE + 1}: {error}")
            else:
                all_results.update(results)
            if done % 10 == 0 or done == len(batches):
                print(f"  Progress: {done}/{len(batches)} batches (${total_cost:.4f})")

    print(f"  Total LLM scored: {len(all_results)}/{len(stories)} (${total_cost:.4f})")
    return all_results


def main():
    t0 = time.time()
    print(f"\n{'='*60}")
    print(f"Pipeline V2 Selector — {NOW.strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"  Window: {HOURS}h, Per-category max: {PER_CAT_MAX}")
    print(f"{'='*60}")

    # ── Load recent signals ───────────────────────────────────────────────────
    print(f"\n── Loading signals from last {HOURS}h ──")
    cutoff = (NOW - timedelta(hours=HOURS)).isoformat()
    signals = []
    offset = 0
    while True:
        page = sb_get("p2_signals", {
            "select": "id,title,original_url,published_at,fetched_at,source_type,source_name,google_cluster_size,description",
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

    # ══════════════════════════════════════════════════════════════════════════
    # PASS 1: Keyword clustering (fast, free)
    # ══════════════════════════════════════════════════════════════════════════
    print(f"\n── Pass 1: Keyword clustering ──")
    clusters = {}
    cluster_keywords = {}  # key -> union of all signal keywords in cluster

    for sig in signals:
        title = sig.get("title", "")
        if not title:
            continue
        match_key = None
        sig_kw = title_keywords(title)
        if sig_kw and len(sig_kw) >= 2:
            best_overlap = 0
            for key, ckw in cluster_keywords.items():
                if not ckw:
                    continue
                overlap = len(sig_kw & ckw)
                rep_kw = title_keywords(clusters[key][0]["title"])
                min_len = min(len(sig_kw), len(rep_kw)) if rep_kw else len(sig_kw)
                if min_len >= 2 and overlap / min_len >= 0.4 and overlap > best_overlap:
                    best_overlap = overlap
                    match_key = key

        if match_key:
            clusters[match_key].append(sig)
            cluster_keywords[match_key] |= sig_kw
        else:
            key = re.sub(r'[^a-z0-9\s]', '', title.lower().strip())[:60]
            clusters.setdefault(key, []).append(sig)
            cluster_keywords[key] = set(sig_kw)

    print(f"  {len(clusters)} clusters from {len(signals)} signals")

    # ══════════════════════════════════════════════════════════════════════════
    # PASS 2: LLM semantic merge (catch same-story clusters keywords missed)
    # ══════════════════════════════════════════════════════════════════════════
    print(f"\n── Pass 2: LLM semantic merge ──")
    cluster_keys = list(clusters.keys())
    cluster_titles = []
    for k in cluster_keys:
        best = max(clusters[k], key=lambda s: len(s.get("title", "")))
        cluster_titles.append(best["title"])

    merge_groups = llm_semantic_merge(cluster_titles)

    # Apply merges: combine signals from grouped clusters
    merged_count = 0
    merged_away = set()  # indices of clusters absorbed into another
    for group in merge_groups:
        group_list = sorted(group)  # deterministic order
        if len(group_list) < 2:
            continue
        # Keep the cluster with the most signals as primary
        primary_idx = max(group_list, key=lambda i: len(clusters[cluster_keys[i]]))
        primary_key = cluster_keys[primary_idx]
        for idx in group_list:
            if idx == primary_idx:
                continue
            merge_key = cluster_keys[idx]
            if merge_key in clusters and merge_key != primary_key:
                clusters[primary_key].extend(clusters[merge_key])
                cluster_keywords[primary_key] |= cluster_keywords.get(merge_key, set())
                del clusters[merge_key]
                merged_away.add(idx)
                merged_count += 1

    if merged_count:
        print(f"  Merged {merged_count} clusters → {len(clusters)} clusters remaining")
    else:
        print(f"  No additional merges found")

    # ══════════════════════════════════════════════════════════════════════════
    # Build candidate list from clusters
    # ══════════════════════════════════════════════════════════════════════════
    print(f"\n── Building candidates ──")
    recent_articles = load_recent_headlines()
    print(f"  Recent articles loaded: {len(recent_articles)}")

    pre_scored = []
    kw_dedup_skips = 0
    for key, sigs in clusters.items():
        best = max(sigs, key=lambda s: len(s.get("title", "")))
        title = best["title"]
        n = len(sigs)

        # Google News cluster boost
        google_boost = sum(s.get("google_cluster_size", 1) for s in sigs if s.get("source_type") == "google_news")
        effective_size = n + max(0, google_boost - len([s for s in sigs if s.get("source_type") == "google_news"]))

        # Source diversity
        sources = set()
        source_types = set()
        for s in sigs:
            sources.add(s.get("source_name") or s.get("source_type", "rss"))
            source_types.add(s.get("source_type", "rss"))
        source_diversity = len(sources)

        # Category
        cat = detect_category(title)

        # Diaspora check (fast keyword pre-filter)
        diaspora = quick_diaspora_check(title)
        if diaspora == "no":
            continue

        # Keyword-level dedup against published (fast pre-filter — LLM does semantic dedup later)
        if is_already_covered(title, recent_articles):
            kw_dedup_skips += 1
            continue

        # Freshness: newest signal timestamp
        try:
            newest = max(s.get("published_at") or s.get("fetched_at", "") for s in sigs)
            if newest:
                try:
                    newest_dt = datetime.fromisoformat(newest.replace("Z", "+00:00"))
                except:
                    newest_dt = NOW
            else:
                newest_dt = NOW
        except:
            newest_dt = NOW

        # Collect source URLs
        source_urls = []
        seen_urls = set()
        for s in sigs:
            u = s.get("original_url", "")
            if u and u not in seen_urls:
                seen_urls.add(u)
                source_urls.append(u)

        # Collect best description from signals
        best_desc = ""
        for s in sigs:
            d = s.get("description", "")
            if d and len(d) > len(best_desc):
                best_desc = d

        pre_scored.append({
            "title": title,
            "description": best_desc,
            "category": cat,
            "signal_count": effective_size,
            "source_diversity": source_diversity,
            "source_types": list(source_types),
            "diaspora_keyword": diaspora,
            "newest_signal": newest_dt.isoformat(),
            "source_urls": source_urls[:8],
            "all_signals": [{"title": s["title"], "url": s["original_url"], "source": s.get("source_name", "")} for s in sigs[:10]],
        })

    if kw_dedup_skips:
        print(f"  Keyword dedup: {kw_dedup_skips} clusters skipped (already covered)")
    print(f"  {len(pre_scored)} candidates to score")

    # ══════════════════════════════════════════════════════════════════════════
    # PASS 3: LLM scoring with 3-way classification (new / update / duplicate)
    # ══════════════════════════════════════════════════════════════════════════
    print(f"\n── Pass 3: LLM scoring + coverage classification ──")

    llm_results = llm_score_stories(pre_scored, recent_articles)

    scored = []
    stats = {"new": 0, "update": 0, "duplicate": 0, "irrelevant": 0, "no_result": 0}
    for i, c in enumerate(pre_scored):
        llm = llm_results.get(i)
        if llm:
            if not llm["relevant"]:
                stats["irrelevant"] += 1
                continue
            coverage = llm.get("coverage", "new")
            if coverage == "duplicate":
                stats["duplicate"] += 1
                continue
            stats[coverage] = stats.get(coverage, 0) + 1
            c["llm_score"] = llm["score"]
            c["llm_reason"] = llm["reason"]
            c["coverage"] = coverage  # "new" or "update"
        else:
            stats["no_result"] += 1
            # LLM didn't return a result — use keyword fallback
            if c["diaspora_keyword"] == "yes":
                c["llm_score"] = 3
            else:
                c["llm_score"] = 1
            c["coverage"] = "new"
        scored.append(c)

    print(f"  Classification: {stats['new']} new, {stats['update']} updates, {stats['duplicate']} duplicates, {stats['irrelevant']} irrelevant, {stats['no_result']} unscored")

    # Sort by LLM score (highest first), then freshness, then signal count
    scored.sort(key=lambda x: (x.get("llm_score", 1), x["newest_signal"], x["signal_count"]), reverse=True)

    # Final keyword dedup within candidates (safety net)
    deduped = []
    for c in scored:
        c_kw = title_keywords(c["title"])
        is_dup = False
        for existing in deduped:
            e_kw = title_keywords(existing["title"])
            if c_kw and e_kw:
                overlap = len(c_kw & e_kw)
                min_len = min(len(c_kw), len(e_kw))
                if min_len >= 2 and overlap / min_len >= 0.5:
                    is_dup = True
                    break
        if not is_dup:
            deduped.append(c)
    if len(scored) != len(deduped):
        print(f"  Final keyword dedup: {len(scored)} → {len(deduped)} (removed {len(scored) - len(deduped)})")
    scored = deduped

    # ── Final LLM dedup on survivors (cross-batch, cheap — only ~30 titles) ──
    if len(scored) > 1 and OPENAI_KEY:
        survivor_titles = [c["title"][:120] for c in scored]
        lines = [f"{i+1}. {t}" for i, t in enumerate(survivor_titles)]
        content_resp, usage, error = llm_call({
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": MERGE_PROMPT + "\n\nHeadlines:\n" + "\n".join(lines)}],
            "response_format": {"type": "json_object"},
            "max_tokens": 1000,
            "temperature": 0,
        }, label="final_dedup")
        if not error and content_resp:
            groups = content_resp.get("groups", [])
            drop_indices = set()
            for g in groups:
                if isinstance(g, list) and len(g) >= 2:
                    sorted_g = sorted(g)  # 1-indexed from LLM
                    # Keep highest-scored, drop the rest
                    best_in_group = max((idx-1 for idx in sorted_g if 0 <= idx-1 < len(scored)),
                                       key=lambda i: scored[i].get("llm_score", 0), default=None)
                    for idx in sorted_g:
                        idx0 = idx - 1
                        if 0 <= idx0 < len(scored) and idx0 != best_in_group:
                            drop_indices.add(idx0)
            if drop_indices:
                print(f"  Final LLM dedup: dropping {len(drop_indices)} cross-batch duplicates")
                for di in sorted(drop_indices):
                    print(f"    ✗ {scored[di]['title'][:80]}")
                scored = [c for i, c in enumerate(scored) if i not in drop_indices]
            else:
                print(f"  Final LLM dedup: no cross-batch duplicates found")
        elif error:
            print(f"  ⚠ Final LLM dedup failed: {error}")

    # Per-category selection: top N per category (no global cap)
    CAT_LIMITS = {"news": 5, "immigration": 5}  # high-volume categories get more
    balanced = []
    cat_counts = {}
    for c in scored:
        cat = c["category"]
        cat_max = CAT_LIMITS.get(cat, PER_CAT_MAX)
        cat_counts.setdefault(cat, 0)
        if cat_counts[cat] < cat_max:
            balanced.append(c)
            cat_counts[cat] += 1

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
        score = c.get("llm_score", "?")
        stars = "⭐" * score if isinstance(score, int) else "?"
        coverage_tag = f" [UPDATE]" if c.get("coverage") == "update" else ""
        print(f"  {i}. [{c['category']}]{coverage_tag} {c['title'][:70]}")
        print(f"     Score: {stars} ({score}) | Signals: {c['signal_count']} | Sources: {c['source_diversity']}")
        if c.get("llm_reason"):
            print(f"     Reason: {c['llm_reason'][:80]}")
    print(f"\n  Output: {OUT_PATH}")
    print(f"  Time: {elapsed:.1f}s")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()

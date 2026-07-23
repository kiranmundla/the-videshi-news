#!/usr/bin/env python3
"""V3 Selector — Topic-centric article candidate selection.

Topics are already clustered by v3-ingest.py. This selector:
  1. Loads pending V3 topics + their linked signals
  2. LLM scores: relevance, newsworthiness, coverage classification (new/update/duplicate)
  3. Per-category caps
  4. Outputs candidates JSON for the writer cron

Usage:
  python3 v3-select.py [--per-cat 3] [--out /tmp/v3-candidates.json] [--dry-run]
"""

import json, os, re, sys, time, subprocess, hashlib
from datetime import datetime, timedelta, timezone
from urllib.parse import quote as urlquote
from concurrent.futures import ThreadPoolExecutor, as_completed

# ── Options ───────────────────────────────────────────────────────────────────
PER_CAT_MAX = 3
OUT_PATH = "/tmp/v3-candidates.json"
DRY_RUN = False

for i, arg in enumerate(sys.argv[1:], 1):
    if arg == "--per-cat" and i < len(sys.argv) - 1:
        PER_CAT_MAX = int(sys.argv[i + 1])
    elif arg == "--out" and i < len(sys.argv) - 1:
        OUT_PATH = sys.argv[i + 1]
    elif arg == "--dry-run":
        DRY_RUN = True

NOW = datetime.now(timezone.utc)
NOW_ISO = NOW.isoformat()

# ── Supabase ──────────────────────────────────────────────────────────────────
def load_env(*paths):
    for p in paths:
        p = os.path.expanduser(p)
        if os.path.exists(p):
            with open(p) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

load_env("~/workspace/.env.supabase", "~/workspace/.env.openai")

SB_URL = os.environ.get("SUPABASE_URL", "")
SB_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
OPENAI_KEY = os.environ.get("OPENAI_API_KEY", "")

if not SB_URL or not SB_KEY:
    print("ERROR: Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY")
    sys.exit(1)


def sb_get(endpoint, params=None, range_header=None):
    """GET from Supabase REST API."""
    url = f"{SB_URL}/rest/v1/{endpoint}"
    if params:
        qs = "&".join(f"{k}={urlquote(str(v), safe='.,()')}" for k, v in params.items())
        url = f"{url}?{qs}"
    headers = [
        "-H", f"apikey: {SB_KEY}",
        "-H", f"Authorization: Bearer {SB_KEY}",
    ]
    if range_header:
        headers += ["-H", f"Range: {range_header}"]
    cmd = ["curl", "-sS", "--max-time", "30", url] + headers
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=35)
    if r.returncode != 0:
        return None
    try:
        return json.loads(r.stdout)
    except:
        return None


def sb_patch(endpoint, data, match_params):
    """PATCH rows in Supabase."""
    url = f"{SB_URL}/rest/v1/{endpoint}"
    qs = "&".join(f"{k}={urlquote(str(v), safe='.,()')}" for k, v in match_params.items())
    url = f"{url}?{qs}"
    payload = json.dumps(data)
    cmd = ["curl", "-sS", "--max-time", "20", "-X", "PATCH", url,
           "-H", f"apikey: {SB_KEY}",
           "-H", f"Authorization: Bearer {SB_KEY}",
           "-H", "Content-Type: application/json",
           "-H", "Prefer: return=minimal",
           "-d", payload]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=25)
    return r.returncode == 0


# ── LLM helpers ───────────────────────────────────────────────────────────────
def llm_call(payload_dict, label="LLM call", timeout=50):
    """Call OpenAI API via curl. Returns (parsed_content, usage_dict, error_string)."""
    if not OPENAI_KEY:
        return None, None, "No API key"

    import tempfile
    payload = json.dumps(payload_dict)
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
        tmp.write(payload)
        tmp_path = tmp.name

    try:
        cmd = [
            "curl", "-sS", "--max-time", str(timeout),
            "-X", "POST", "https://api.openai.com/v1/chat/completions",
            "-H", f"Authorization: Bearer {OPENAI_KEY}",
            "-H", "Content-Type: application/json",
            "-d", f"@{tmp_path}",
        ]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 10)
        if r.returncode != 0:
            return None, None, f"curl error (rc={r.returncode})"

        data = json.loads(r.stdout)
        if "error" in data:
            return None, None, data["error"].get("message", str(data["error"]))

        usage = data.get("usage", {})
        content_str = data["choices"][0]["message"]["content"]
        content = json.loads(content_str)
        return content, usage, None
    except json.JSONDecodeError as e:
        return None, None, f"JSON parse error: {e}"
    except Exception as e:
        return None, None, str(e)
    finally:
        os.unlink(tmp_path)


# ── Category detection ────────────────────────────────────────────────────────
# Keyword-based fast pre-filter; LLM refines in scoring step
CATEGORY_PATTERNS = {
    "immigration": [
        r'\bh-?1b\b', r'\bgreen\s*card\b', r'\bvisa\b', r'\buscis\b', r'\bimmigration\b',
        r'\bdeport\b', r'\basylum\b', r'\beb-?\d\b', r'\bopt[\s,.\-;:)]', r'\bi-?\d{3}\b',
        r'\bcitizenship\b', r'\bnaturaliz', r'\bwork\s*permit\b', r'\bdaca\b',
    ],
    "technology": [
        r'\b(?:ai|artificial intelligence)\b', r'\btech\b', r'\bstartup\b', r'\bsoftware\b',
        r'\bgoogle\b', r'\bmicrosoft\b', r'\bapple\b(?!\s*(?:pie|sauce|cider|juice))',
        r'\bmeta\b(?!\s*(?:analysis|study))', r'\bnvidia\b', r'\bchip\b', r'\bsemiconductor\b',
        r'\bcyber\b', r'\brobot\b', r'\bcloud\b', r'\bdata\b', r'\bblockchain\b',
    ],
    "entertainment": [
        r'\bbollywood\b', r'\bhollywood\b', r'\bmovie\b', r'\bfilm\b', r'\bnetflix\b',
        r'\bdisney\b', r'\bstreaming\b', r'\bactor\b', r'\bactress\b', r'\bcelebrit',
        r'\bmusic\b', r'\balbum\b', r'\bconcert\b', r'\baward\b', r'\boscar\b',
        r'\bbox\s*office\b', r'\bott\b', r'\btrailer\b',
    ],
    "sports": [
        r'\bcricket\b', r'\bipl\b', r'\bworld\s*cup\b', r'\bfifa\b', r'\btennis\b',
        r'\bolympic\b', r'\bsoccer\b', r'\bfootball\b', r'\bnba\b', r'\bmlb\b',
        r'\bformula\s*1\b', r'\bf1\b', r'\bathlet\b', r'\btournament\b',
    ],
    "markets-finance": [
        r'\bstock\b', r'\bmarket\b', r'\bnasdaq\b', r'\bs&p\b', r'\bsensex\b',
        r'\bnifty\b', r'\bearning\b', r'\bipo\b', r'\bfed\b(?!\s*(?:up|ex))',
        r'\binflation\b', r'\binterest\s*rate\b', r'\brupee\b', r'\bdollar\b',
        r'\binvestor\b', r'\bwall\s*street\b', r'\bgdp\b',
    ],
    "food": [
        r'\bindian\s*(?:food|cuisine|recipe|restaurant|chef|dish|spice)\b',
        r'\bcurry\b', r'\bbiryani\b', r'\bmasala\b', r'\bdosa\b', r'\bsamosa\b',
        r'\bnaan\b', r'\btandoori\b', r'\bchutney\b', r'\bpaneer\b',
    ],
    "nri-world": [
        r'\bnri\b', r'\bdiaspora\b', r'\bindian.?american\b', r'\bindian.?origin\b',
        r'\bpio\b', r'\boci\b(?!\s*card)', r'\bexpat\b',
    ],
}

def detect_category(title, description=""):
    """Fast keyword category detection. Returns best category or 'news'."""
    text = (title + " " + description).lower()
    scores = {}
    for cat, patterns in CATEGORY_PATTERNS.items():
        hits = sum(1 for p in patterns if re.search(p, text, re.IGNORECASE))
        if hits:
            scores[cat] = hits
    if scores:
        return max(scores, key=scores.get)
    return "news"


# ── Category normalization (module-level so both LLM scorer and main can use) ──
_CAT_NORMALIZE = {
    "lifestyle": "lifestyle-health", "health": "lifestyle-health",
    "finance": "markets-finance", "markets": "markets-finance",
    "market": "markets-finance", "business": "markets-finance",
    "nri": "nri-world", "world": "nri-world",
    "tech": "technology", "cricket": "sports",
    "bollywood": "entertainment", "movies": "entertainment",
    "visa": "immigration", "h1b": "immigration",
}
_VALID_CATS = {"immigration","technology","news","entertainment","sports",
               "markets-finance","nri-world","food","travel","lifestyle-health"}

# ── Instagram handle reference for LLM ────────────────────────────────────────
def _build_ig_handle_block():
    """Load IG handles + metadata from registry for injection into LLM prompt."""
    reg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "social-embed-registry.json")
    if not os.path.exists(reg_path):
        return ""
    with open(reg_path) as f:
        registry = json.load(f)
    lines = []
    seen = set()
    for cat, data in registry.items():
        if cat.startswith("_") or not isinstance(data, dict):
            continue
        for group in ("persons", "organizations"):
            kind = "person" if group == "persons" else "org"
            for entry in data.get(group, []):
                ig = entry.get("instagram", "")
                name = entry.get("name", "")
                if not ig or ig in seen:
                    continue
                seen.add(ig)
                covers = entry.get("covers", "")
                meta = f"{name} ({kind}, {cat})"
                if covers:
                    meta += f" — {covers}"
                lines.append(f"@{ig}: {meta}")
    if not lines:
        return ""
    return "\n\nKNOWN INSTAGRAM HANDLES:\n" + "\n".join(lines) + "\n"

_IG_HANDLE_BLOCK = _build_ig_handle_block()

def _build_ig_name_lookup():
    """Build handle→full_name dict from registry for post-GPT name verification."""
    reg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "social-embed-registry.json")
    if not os.path.exists(reg_path):
        return {}
    with open(reg_path) as f:
        registry = json.load(f)
    lookup = {}
    for cat, data in registry.items():
        if cat.startswith("_") or not isinstance(data, dict):
            continue
        for group in ("persons", "organizations"):
            for entry in data.get(group, []):
                ig = (entry.get("instagram") or "").lower()
                name = entry.get("name") or ""
                if ig and name:
                    lookup[ig] = name
    return lookup

_IG_NAME_LOOKUP = _build_ig_name_lookup()

def _verify_handle_name(handle, headline, handle_type="person"):
    """Reject person handles where the registry name doesn't match the headline.
    Returns True if the handle should be kept, False if rejected."""
    handle_clean = handle.lstrip("@").lower()
    if handle_clean not in _IG_NAME_LOOKUP:
        return True  # unknown handle, can't verify — keep it
    if handle_type != "person":
        return True  # only verify person handles (orgs are matched by topic)
    full_name = _IG_NAME_LOOKUP[handle_clean]
    name_parts = full_name.split()
    if len(name_parts) < 2:
        return True  # single-name person, can't do last-name check
    last_name = name_parts[-1].lower()
    headline_lower = headline.lower()
    # Check if last name appears in headline
    if last_name in headline_lower:
        return True
    # Also check full name
    if full_name.lower() in headline_lower:
        return True
    return False

# ── LLM scoring prompt ───────────────────────────────────────────────────────
LLM_PROMPT = """You are the editorial filter for The Videshi, a news site for the Indian diaspora — Indians living in the US, UK, Canada, and Australia.

Your readers are educated professionals who LIVE in these countries. They care about:
- India news, Indian culture, Bollywood, cricket, Indian politics & economy
- Immigration policy (H-1B, green cards, visa rules, deportation)
- Indian-origin people in tech, business, politics, sports, entertainment
- Major US/UK/global news that affects their daily lives — economy, wars, natural disasters, public health, major policy changes, elections
- Indian food, recipes, restaurants, chefs
- Travel relevant to diaspora (Air India, Indian destinations, visa-free countries for Indians)
- Bollywood AND Hollywood entertainment, streaming, celebrity news
- Health, wellness, yoga, Ayurveda, lifestyle with any Indian connection

They are NOT interested in:
- Hyper-local US news (local school board, yard sale, parking meters, small-town crime)
- Minor celebrity gossip with no Indian connection
- Niche bureaucratic/regulatory noise
- Promo codes, coupon roundups, deal listicles, affiliate marketing content

IMPORTANT: Be generous with food, entertainment, travel, and lifestyle stories — if a story has ANY Indian connection, score it at least 3.

SCORING GUIDE (be strict — 5 is rare):
- 5: Breaking must-know news — major immigration policy change, Indian-origin person in global headlines, major India event affecting diaspora, critical public health/safety for US/UK
- 4: Very important — significant industry news with Indian angle, important cultural moment, notable NRI achievement, major market move
- 3: Important — interesting story with clear Indian/diaspora connection
- 2: Moderate — tangential Indian connection or minor story
- 1: Mild — barely relevant
A story about India's domestic car market, Indian college football recruits with no Indian heritage, or US-only local sports with no Indian connection should score 1-2, not 4-5. "Indiana" the US state is NOT the same as "India" the country.

CATEGORY RULES:
- technology = tech industry, startups, AI, cybersecurity, semiconductors, software, hardware. NOT consumer product comparisons, car reviews, or appliance roundups
- sports = stories with genuine Indian/cricket/diaspora connection. US college football, MLB, or NFL stories need a real Indian link (Indian-origin player, team with Indian sponsor) — don't score high just because a school has "Indian" in the name
- markets-finance = US/global markets first (FAANG, banks, Fed, macro). India markets (RBI, Sensex, IPOs) with diaspora investment angle

COVERAGE CLASSIFICATION:
You will receive ALREADY PUBLISHED headlines. For each new topic, classify:
- "new" — Not yet covered. Write it.
- "update" — We published on this, BUT this has a MAJOR new development. Classify as "update" in these cases:
  * The OUTCOME of an anticipated event (e.g. we covered "set to launch" and now the launch SUCCEEDED or FAILED — that's an update, not a duplicate)
  * A major escalation, reversal, or result (court ruling after charges filed, death toll doubling, CEO resigning after investigation, election results after campaign coverage)
  * Any story where the published article was forward-looking/anticipatory and the new topic reports what actually happened
  The bar is HIGH for routine incremental updates, but OUTCOMES of anticipated events are always "update".
- "duplicate" — Already covered with no major new info. Even different wording/angle = duplicate if the SUBSTANCE is the same. DEFAULT when a published headline covers the same event AND neither is anticipatory vs outcome.

WITHIN-BATCH duplicates: if two topics in this batch cover the same event, mark all but the most important as "duplicate".

CATEGORY ASSIGNMENT:
Also assign the best category for each topic:
immigration, technology, entertainment, sports, markets-finance, food, travel, lifestyle-health, nri-world, news

CATEGORY RULES — prevent common misclassification:
- "box office" = entertainment (NOT immigration, even though it contains "office")
- "ICE" = immigration ONLY when referring to Immigration and Customs Enforcement. "ice cream", "icy conditions" = NOT immigration
- "OPT" = immigration ONLY when referring to Optional Practical Training. "opt out", "opted", "option" = NOT immigration
- "apple" = technology ONLY when referring to Apple Inc. "apple pie", "apple cider" = food
- "streaming" = entertainment for Netflix/Disney+/etc. "streaming data" = technology
- Do NOT classify by substring matches. Read the full headline meaning.

For each topic, provide:
1. "relevant": true/false
2. "score": 1-5 importance (5=breaking everyone-must-know, 4=very important, 3=important, 2=moderate, 1=mild)
3. "coverage": "new" | "update" | "duplicate"
4. "category": one of the categories above
5. "reason": 1-sentence explanation
6. "ig_handles": array of objects for ALL Instagram handles directly connected to this story.
Each object: {"handle": "@x", "type": "person" or "org", "keywords": ["word1", "word2", "word3"]}
- type: "person" for individuals, "org" for everything else (companies, teams, leagues, govt bodies)
- keywords: 3-5 words likely to appear in that handle's IG caption about this topic (not news headline words)

WHO TO INCLUDE:
- People directly mentioned in or central to the story
- Organizations, teams, leagues, or brands directly involved
- Entities that would likely POST ABOUT this specific event (e.g. @premierleague for a football legend's death, @nasa for a space launch)

WHO TO EXCLUDE:
- Handles only thematically related ("article about CEOs" does NOT mean suggest random CEO handles)
- Handles with no direct connection to the specific story
- Do NOT match on partial name similarity — the person/org must be the SAME entity in the article (e.g. do NOT suggest @arvindkejriwal for an article about "Arvind Ramanathan")

Pick from KNOWN HANDLES when possible. The list is NOT exhaustive — suggest new handles if you are CERTAIN the person/org has an active IG and you know the exact handle. When in doubt, leave it out. Return up to 5, most relevant first. Return [] if none.

Respond as JSON: {"results": [{"id": 1, "relevant": true, "coverage": "new", "score": 4, "category": "technology", "reason": "...", "ig_handles": [{"handle": "@sundarpichai", "type": "person", "keywords": ["google", "ceo", "ai"]}, {"handle": "@google", "type": "org", "keywords": ["google", "ai", "search"]}]},...]}\n"""

MERGE_PROMPT = """You are grouping news headlines that cover the SAME underlying story or event.

Two headlines cover the same story if they report on the same event, announcement, ruling, development,
or situation — even if worded completely differently.

Given the numbered headlines below, return groups of IDs that cover the SAME story.
Only group headlines you are CONFIDENT cover the same event. When in doubt, keep separate.

Return JSON: {"groups": [[1, 5], [3, 8, 12], ...]}
Headlines not in any group are unique stories. Empty groups array if no merges found.
"""


def llm_score_topics(topics_with_signals, recent_articles):
    """Batch-score topics via GPT-4o-mini. Returns dict of topic_index -> result."""
    if not topics_with_signals or not OPENAI_KEY:
        return {}

    # Build published context
    published_block = ""
    if recent_articles:
        pub_lines = [f"- {a.get('headline', '')}" for a in recent_articles[:150]]
        published_block = "\n\nALREADY PUBLISHED HEADLINES:\n" + "\n".join(pub_lines)

    BATCH_SIZE = 40
    all_results = {}
    total_cost = 0.0

    def score_batch(batch_start, batch):
        lines = []
        for i, t in enumerate(batch):
            title = t["canonical_title"]
            sig_count = t.get("signal_count", 1)
            source_count = len(set(s.get("source_name", "") for s in t.get("signals", [])))
            desc = ""
            for s in t.get("signals", []):
                if s.get("description") and len(s["description"]) > len(desc):
                    desc = s["description"]
            desc_part = f" | {desc[:150]}" if desc else ""
            lines.append(f"{i+1}. {title[:120]}{desc_part} [signals: {sig_count}, sources: {source_count}]")

        payload = {
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": LLM_PROMPT + _IG_HANDLE_BLOCK + published_block + "\n\nTOPICS TO EVALUATE:\n" + "\n".join(lines)}],
            "response_format": {"type": "json_object"},
            "max_tokens": max(len(batch) * 130, 2000),
            "temperature": 0,
        }

        content, usage, error = llm_call(payload, label=f"score_{batch_start}", timeout=50)
        cost = 0
        if usage:
            cost = usage.get("prompt_tokens", 0) * 0.15 / 1_000_000 + usage.get("completion_tokens", 0) * 0.6 / 1_000_000

        if error:
            # Retry once
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
                if item.get("duplicate", False) and coverage == "new":
                    coverage = "duplicate"
                # Normalize common LLM category mistakes
                raw_cat = item.get("category", "news")
                _CAT_NORMALIZE = {
                    "lifestyle": "lifestyle-health", "health": "lifestyle-health",
                    "finance": "markets-finance", "markets": "markets-finance",
                    "market": "markets-finance", "business": "markets-finance",
                    "nri": "nri-world", "world": "nri-world",
                    "tech": "technology", "cricket": "sports",
                    "bollywood": "entertainment", "movies": "entertainment",
                    "visa": "immigration", "h1b": "immigration",
                }
                _VALID_CATS = {"immigration","technology","news","entertainment","sports",
                               "markets-finance","nri-world","food","travel","lifestyle-health"}
                norm_cat = _CAT_NORMALIZE.get(raw_cat, raw_cat)
                if norm_cat not in _VALID_CATS:
                    norm_cat = "news"
                results[global_idx] = {
                    "relevant": item.get("relevant", True),
                    "coverage": coverage,
                    "score": item.get("score", 1) if item.get("relevant", True) else 0,
                    "category": norm_cat,
                    "reason": item.get("reason", ""),
                    "ig_handles": item.get("ig_handles", []),
                }
        return batch_start, results, cost, None

    batches = [(i, topics_with_signals[i:i+BATCH_SIZE]) for i in range(0, len(topics_with_signals), BATCH_SIZE)]

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
            if done % 5 == 0 or done == len(batches):
                print(f"  Progress: {done}/{len(batches)} batches (${total_cost:.4f})")

    print(f"  Total LLM scored: {len(all_results)}/{len(topics_with_signals)} (${total_cost:.4f})")
    return all_results


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    t0 = time.time()

    print(f"\n{'='*60}")
    print(f"Pipeline V3 Selector — {NOW.strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"  Per-category max: {PER_CAT_MAX}")
    print(f"  Dry run: {DRY_RUN}")
    print(f"{'='*60}")

    # ── Step 1: Load pending V3 topics ────────────────────────────────────────
    print(f"\n── Step 1: Loading pending V3 topics ──")
    topics = []
    offset = 0
    while True:
        page = sb_get("p2_topics", {
            "select": "id,canonical_title,signal_count,status,created_at,last_signal_at",
            "last_signal_at": "not.is.null",
            "status": "eq.pending",
            "evaluated_at": "is.null",  # only topics not yet evaluated
            "order": "last_signal_at.desc",
        }, range_header=f"{offset}-{offset+999}")
        if not page or isinstance(page, dict):
            break
        topics.extend(page)
        if len(page) < 1000:
            break
        offset += 1000

    print(f"  Found {len(topics)} pending topics")
    if not topics:
        print("  Nothing to do.")
        json.dump({"candidates": [], "timestamp": NOW_ISO}, open(OUT_PATH, "w"))
        return

    # ── Step 2: Load signals for each topic ───────────────────────────────────
    print(f"\n── Step 2: Loading signals for topics ──")
    topic_ids = [t["id"] for t in topics]

    # Batch-load signals for all topics at once
    all_signals = []
    # PostgREST in filter: topic_id=in.(id1,id2,...)
    # Chunk topic IDs to avoid URL length limits
    CHUNK = 50
    for i in range(0, len(topic_ids), CHUNK):
        chunk_ids = topic_ids[i:i+CHUNK]
        id_list = ",".join(chunk_ids)
        page = sb_get("p2_signals", {
            "select": "id,title,original_url,topic_id,source_type,source_name,published_at,description",
            "topic_id": f"in.({id_list})",
            "order": "published_at.desc",
        }, range_header="0-4999")
        if page and isinstance(page, list):
            all_signals.extend(page)

    # Group signals by topic_id
    signals_by_topic = {}
    for sig in all_signals:
        tid = sig.get("topic_id")
        if tid:
            signals_by_topic.setdefault(tid, []).append(sig)

    # Attach signals to topics
    for t in topics:
        t["signals"] = signals_by_topic.get(t["id"], [])

    sig_counts = [len(t["signals"]) for t in topics]
    print(f"  Total signals loaded: {len(all_signals)}")
    print(f"  Topics with signals: {sum(1 for c in sig_counts if c > 0)}/{len(topics)}")
    print(f"  Signal distribution: min={min(sig_counts)}, max={max(sig_counts)}, avg={sum(sig_counts)/len(sig_counts):.1f}")

    # ── Step 3: Load recent published articles for dedup ──────────────────────
    # Three layers:
    #  a) 14-day window sent to LLM for detailed new/update/duplicate classification
    #  b) 30-day headline keyword check to catch stories that resurface after weeks
    #  c) Published topic titles — catches same canonical story resurfacing across runs
    print(f"\n── Step 3: Loading recent articles for dedup ──")
    cutoff_14d = (NOW - timedelta(days=14)).isoformat()
    recent_articles = sb_get("p2_articles", {
        "select": "headline,category,published_at",
        "created_at": f"gte.{cutoff_14d}",
        "status": "eq.published",
        "order": "created_at.desc",
    }, range_header="0-1199")
    if not recent_articles or isinstance(recent_articles, dict):
        recent_articles = []
    print(f"  Recent articles (14d): {len(recent_articles)}")

    # Layer b: fast headline keyword check against 60-day window (extended from 30d)
    # Only loads the EXTRA articles beyond 14d, and only adds those matching a topic
    cutoff_60d = (NOW - timedelta(days=60)).isoformat()
    older_articles = sb_get("p2_articles", {
        "select": "headline,category,published_at",
        "created_at": f"gte.{cutoff_60d}",
        "status": "eq.published",
        "order": "created_at.desc",
    }, range_header="1200-3999")
    if not older_articles or isinstance(older_articles, dict):
        older_articles = []

    if older_articles and topics:
        # Find older headlines that share distinctive keywords with incoming topics
        _dedup_stop = {"the","and","for","with","from","that","this","will","has","have",
                       "been","after","about","over","says","said","more","than","also",
                       "new","india","indian","how","why","what","when","where","who",
                       "could","would","first","last","may","get","set","into","most"}
        added = 0
        for t in topics:
            t_title = (t.get("canonical_title") or "").lower()
            t_words = {w for w in re.findall(r'[a-z]{3,}', t_title)} - _dedup_stop
            if len(t_words) < 2:
                continue
            # Distinctive words = 6+ chars (proper nouns, specific terms)
            t_distinctive = {w for w in t_words if len(w) >= 6}
            for oa in older_articles:
                h_lower = (oa.get("headline") or "").lower()
                h_words = {w for w in re.findall(r'[a-z]{3,}', h_lower)} - _dedup_stop
                overlap = t_words & h_words
                h_distinctive = {w for w in h_words if len(w) >= 6}
                distinctive_overlap = t_distinctive & h_distinctive
                # Match if 3+ total keyword overlap OR 2+ distinctive (6+ char) overlap
                if (len(overlap) >= 3 or len(distinctive_overlap) >= 2) and oa not in recent_articles:
                    recent_articles.append(oa)
                    added += 1
        if added:
            print(f"  + {added} older headline(s) matched by keyword (60d)")

    # Layer c: Published topic titles from p2_topics (catches same canonical story)
    cutoff_30d = (NOW - timedelta(days=30)).isoformat()
    published_topics = sb_get("p2_topics", {
        "select": "canonical_title",
        "status": "eq.published",
        "updated_at": f"gte.{cutoff_30d}",
    }, range_header="0-499")
    if published_topics and not isinstance(published_topics, dict):
        topic_headlines = [{"headline": t.get("canonical_title", ""), "category": "unknown", "published_at": ""}
                          for t in published_topics if t.get("canonical_title")]
        # Add to dedup context (LLM will see these as already-published)
        existing_headlines = {a.get("headline", "").lower() for a in recent_articles}
        added_topics = 0
        for th in topic_headlines:
            if th["headline"].lower() not in existing_headlines:
                recent_articles.append(th)
                existing_headlines.add(th["headline"].lower())
                added_topics += 1
        if added_topics:
            print(f"  + {added_topics} published topic title(s) added to dedup context")

    print(f"  Total dedup context: {len(recent_articles)} headlines")

    # ── Step 3b: Hard dedup — reject topics whose title closely matches an already-published headline ──
    # This catches cases the LLM misses (same story resurfacing with near-identical wording)
    _pub_titles_lower = {(a.get("headline") or "").lower().strip() for a in recent_articles}
    _hard_dedup_count = 0
    for t in topics:
        t_title = (t.get("canonical_title") or "").lower().strip()
        # Strip trailing " - SOURCE" (e.g. " - NDTV") for matching
        t_base = re.sub(r'\s*[-–—]\s*[a-z0-9 ]{2,30}$', '', t_title).strip()
        for pub in _pub_titles_lower:
            pub_base = re.sub(r'\s*[-–—]\s*[a-z0-9 ]{2,30}$', '', pub).strip()
            if not t_base or not pub_base:
                continue
            # Exact match after stripping source
            if t_base == pub_base:
                topic_statuses[t["id"]] = "rejected"
                _hard_dedup_count += 1
                break
            # High word overlap (>=80% of words match)
            t_words = set(re.findall(r'[a-z]{3,}', t_base)) - _dedup_stop
            p_words = set(re.findall(r'[a-z]{3,}', pub_base)) - _dedup_stop
            if t_words and p_words:
                overlap = len(t_words & p_words) / min(len(t_words), len(p_words))
                if overlap >= 0.8:
                    topic_statuses[t["id"]] = "rejected"
                    _hard_dedup_count += 1
                    break
    if _hard_dedup_count:
        print(f"  Hard dedup rejected: {_hard_dedup_count} topics (title match with published)")

    # ── Step 4: LLM scoring + classification ──────────────────────────────────
    # Only LLM-score topics that have loaded signals AND weren't hard-deduped
    topics_with_loaded_signals = [t for t in topics if t.get("signals") and topic_statuses.get(t["id"]) != "rejected"]
    topics_without_signals = [t for t in topics if not t.get("signals") and topic_statuses.get(t["id"]) != "rejected"]
    print(f"\n── Step 4: LLM scoring + coverage classification ──")
    print(f"  Topics with loaded signals: {len(topics_with_loaded_signals)} (scoring)")
    print(f"  Topics without signals: {len(topics_without_signals)} (auto-rejecting)")
    llm_results = llm_score_topics(topics_with_loaded_signals, recent_articles)

    scored = []
    stats = {"new": 0, "update": 0, "duplicate": 0, "irrelevant": 0, "no_result": 0}
    topic_statuses = {}  # topic_id -> status to write back

    # Auto-reject topics without signals
    for t in topics_without_signals:
        topic_statuses[t["id"]] = "rejected"

    for i, t in enumerate(topics_with_loaded_signals):
        llm = llm_results.get(i)
        if llm:
            if not llm["relevant"]:
                stats["irrelevant"] += 1
                topic_statuses[t["id"]] = "rejected"
                continue
            coverage = llm.get("coverage", "new")
            if coverage == "duplicate":
                stats["duplicate"] += 1
                topic_statuses[t["id"]] = "rejected"
                continue
            # Minimum score floor — reject score 1-2 (weak/no diaspora connection)
            if llm.get("score", 1) < 3:
                stats["low_score"] = stats.get("low_score", 0) + 1
                topic_statuses[t["id"]] = "rejected"
                continue
            stats[coverage] = stats.get(coverage, 0) + 1

            # Build candidate
            signals = t.get("signals", [])
            source_urls = []
            seen_urls = set()
            for s in signals:
                u = s.get("original_url", "")
                if u and u not in seen_urls:
                    seen_urls.add(u)
                    source_urls.append(u)

            best_desc = ""
            for s in signals:
                d = s.get("description", "")
                if d and len(d) > len(best_desc):
                    best_desc = d

            sources = set()
            source_types = set()
            for s in signals:
                sources.add(s.get("source_name") or s.get("source_type", "rss"))
                source_types.add(s.get("source_type", "rss"))

            # Freshness
            try:
                newest = max(s.get("published_at") or s.get("fetched_at", "") for s in signals) if signals else NOW_ISO
            except:
                newest = NOW_ISO

            _raw_cat2 = llm.get("category", detect_category(t["canonical_title"]))
            _norm_cat2 = _CAT_NORMALIZE.get(_raw_cat2, _raw_cat2)
            if _norm_cat2 not in _VALID_CATS:
                _norm_cat2 = "news"

            scored.append({
                "topic_id": t["id"],
                "title": t["canonical_title"],
                "description": best_desc,
                "category": _norm_cat2,
                "signal_count": t.get("signal_count", 1),
                "source_diversity": len(sources),
                "source_types": list(source_types),
                "newest_signal": newest,
                "source_urls": source_urls[:8],
                "all_signals": [{"title": s["title"], "url": s["original_url"], "source": s.get("source_name", "")} for s in signals[:10]],
                "llm_score": llm["score"],
                "llm_reason": llm["reason"],
                "coverage": coverage,
                "ig_handles": [h for h in llm.get("ig_handles", []) if _verify_handle_name(h.get("handle", ""), t["canonical_title"], h.get("type", "person"))],
            })
            topic_statuses[t["id"]] = "selected"
        else:
            stats["no_result"] += 1
            topic_statuses[t["id"]] = "pending"  # leave for next run

    print(f"  Classification: {stats['new']} new, {stats['update']} updates, {stats['duplicate']} duplicates, {stats['irrelevant']} irrelevant, {stats.get('low_score', 0)} low-score rejected, {stats['no_result']} unscored")

    # Sort by score desc, then freshness, then signal count
    scored.sort(key=lambda x: (x.get("llm_score", 1), x["newest_signal"], x["signal_count"]), reverse=True)

    # ── Step 5: Per-category caps ─────────────────────────────────────────────
    print(f"\n── Step 5: Per-category caps ──")
    CAT_LIMITS = {"news": 5, "immigration": 5}
    balanced = []
    cat_counts = {}
    capped_ids = []
    for c in scored:
        cat = c["category"]
        cat_max = CAT_LIMITS.get(cat, PER_CAT_MAX)
        cat_counts.setdefault(cat, 0)
        if cat_counts[cat] < cat_max:
            balanced.append(c)
            cat_counts[cat] += 1
        else:
            capped_ids.append(c["topic_id"])
            topic_statuses[c["topic_id"]] = "rejected"

    # ── Step 6: Final LLM dedup on capped candidates ─────────────────────────
    if len(balanced) > 1 and OPENAI_KEY:
        print(f"\n── Step 6: Final LLM dedup ({len(balanced)} candidates) ──")
        survivor_titles = [c["title"][:120] for c in balanced]
        lines = [f"{i+1}. {t}" for i, t in enumerate(survivor_titles)]
        content, usage, error = llm_call({
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": MERGE_PROMPT + "\n\nHeadlines:\n" + "\n".join(lines)}],
            "response_format": {"type": "json_object"},
            "max_tokens": 1000,
            "temperature": 0,
        }, label="final_dedup")
        if not error and content:
            groups = content.get("groups", [])
            drop_indices = set()
            for g in groups:
                if isinstance(g, list) and len(g) >= 2:
                    sorted_g = sorted(g)
                    best_in_group = max((idx-1 for idx in sorted_g if 0 <= idx-1 < len(balanced)),
                                       key=lambda i: balanced[i].get("llm_score", 0), default=None)
                    for idx in sorted_g:
                        idx0 = idx - 1
                        if 0 <= idx0 < len(balanced) and idx0 != best_in_group:
                            drop_indices.add(idx0)
                            topic_statuses[balanced[idx0]["topic_id"]] = "rejected"
            if drop_indices:
                print(f"  Dropping {len(drop_indices)} cross-candidate duplicates")
                for di in sorted(drop_indices):
                    print(f"    ✗ {balanced[di]['title'][:80]}")
                balanced = [c for i, c in enumerate(balanced) if i not in drop_indices]
            else:
                print(f"  No cross-candidate duplicates found")
        elif error:
            print(f"  ⚠ Final dedup failed: {error}")
    else:
        print(f"\n── Step 6: Final LLM dedup — skipped (≤1 candidate) ──")

    # ── Step 7: Batch-update topic statuses ───────────────────────────────────
    print(f"\n── Step 7: Updating topic statuses ──")
    if not DRY_RUN:
        # Group topic IDs by target status
        selected_ids = [tid for tid, st in topic_statuses.items() if st == "selected"]
        rejected_ids = [tid for tid, st in topic_statuses.items() if st == "rejected"]

        updated = 0
        # Batch PATCH rejected topics (chunks of 50 IDs to avoid URL length limits)
        PATCH_CHUNK = 50
        for i in range(0, len(rejected_ids), PATCH_CHUNK):
            chunk = rejected_ids[i:i+PATCH_CHUNK]
            id_list = ",".join(chunk)
            sb_patch("p2_topics", {"status": "rejected", "evaluated_at": NOW_ISO},
                     {"id": f"in.({id_list})"})
            updated += len(chunk)

        # Batch PATCH selected topics (just set evaluated_at, keep status pending for writer)
        for i in range(0, len(selected_ids), PATCH_CHUNK):
            chunk = selected_ids[i:i+PATCH_CHUNK]
            id_list = ",".join(chunk)
            sb_patch("p2_topics", {"evaluated_at": NOW_ISO},
                     {"id": f"in.({id_list})"})
            updated += len(chunk)

        # Save ig_handles per selected topic (each topic has different handles)
        ig_saved = 0
        for c in balanced:
            handles = c.get("ig_handles", [])
            if handles:
                sb_patch("p2_topics", {"ig_handles": json.dumps(handles)},
                         {"id": f"eq.{c['topic_id']}"})
                ig_saved += 1

        print(f"  Updated {updated} topics (selected: {len(selected_ids)}, rejected: {len(rejected_ids)}, ig_handles: {ig_saved})")
    else:
        print(f"  [DRY RUN] Would update {len(topic_statuses)} topics")

    # ── Output ────────────────────────────────────────────────────────────────
    output = {
        "timestamp": NOW_ISO,
        "total_topics_evaluated": len(topics),
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
        if c.get("ig_handles"):
            handles_str = ", ".join(
                h["handle"] + f" ({h['type']})" if isinstance(h, dict) else h
                for h in c["ig_handles"]
            )
            print(f"     IG: {handles_str}")
    print(f"\n  Output: {OUT_PATH}")
    print(f"  Time: {elapsed:.1f}s")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()

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

load_env("~/workspace/.env.supabase", "~/workspace/.env.openai", "~/workspace/.env.google-ai")

SB_URL = os.environ.get("SUPABASE_URL", "")
SB_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
OPENAI_KEY = os.environ.get("OPENAI_API_KEY", "")
GOOGLE_AI_KEY = os.environ.get("GOOGLE_AI_API_KEY", "")

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


def gemini_llm_call(messages_content, max_tokens=2000, label="Gemini call", timeout=60):
    """Fallback: Call Gemini 2.5 Flash via Google AI API. Returns (parsed_content, usage_dict, error_string)."""
    if not GOOGLE_AI_KEY:
        return None, None, "No Google AI API key"

    import tempfile
    payload = json.dumps({
        "contents": [{"parts": [{"text": messages_content}]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "maxOutputTokens": max_tokens,
            "temperature": 0,
            "thinkingConfig": {"thinkingBudget": 0},
        },
    })
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
        tmp.write(payload)
        tmp_path = tmp.name

    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GOOGLE_AI_KEY}"
        cmd = [
            "curl", "-sS", "--max-time", str(timeout),
            "-X", "POST", url,
            "-H", "Content-Type: application/json",
            "-d", f"@{tmp_path}",
        ]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 10)
        if r.returncode != 0:
            return None, None, f"curl error (rc={r.returncode})"

        data = json.loads(r.stdout)
        if "error" in data:
            return None, None, data["error"].get("message", str(data["error"]))

        usage = data.get("usageMetadata", {})
        text = data["candidates"][0]["content"]["parts"][0]["text"]
        content = json.loads(text)
        return content, usage, None
    except json.JSONDecodeError as e:
        return None, None, f"Gemini JSON parse error: {e}"
    except Exception as e:
        return None, None, f"Gemini error: {e}"
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


# ── Diaspora connection gate for entertainment/sports ─────────────────────────
# The LLM frequently ignores prompt instructions and gives score=5 to articles
# in entertainment/sports with zero Indian/diaspora connection. This post-LLM
# keyword gate enforces the editorial policy mechanically: if the headline +
# description lack any Indian/diaspora markers, the score is capped at 2
# (auto-rejected by the existing score < 3 floor).
#
# Cricket is treated as inherently diaspora-relevant per editorial policy.
# Articles with cricket-specific terms pass without needing "India" explicitly.

_DIASPORA_PATTERNS = [re.compile(p, re.IGNORECASE) for p in [
    # Countries & nationalities (word boundary avoids "Indiana")
    r'\bindia\b', r'\bindian\b', r'\bindians\b',
    r'\bpakistan', r'\bbangladesh', r'\bsri\s*lank', r'\bnepal',
    r'\bafghan',
    # Diaspora terms
    r'\bdiaspora\b', r'\bnri\b', r'\bdesi\b', r'\bsouth\s*asian',
    r'\bindo[- ]',
    # Currency / Indian amounts
    r'₹', r'\bcrore', r'\blakh', r'\brupee',
    # Film industries
    r'\bbollywood', r'\btollywood', r'\bkollywood', r'\bmollywood',
    # Indian languages (strong signal for entertainment)
    r'\bhindi\b', r'\btelugu\b', r'\btamil\b', r'\bmalayalam\b',
    r'\bkannada\b', r'\bmarathi\b', r'\bbhojpuri\b', r'\bpunjabi\b',
    # Major Indian cities
    r'\bmumbai\b', r'\bdelhi\b', r'\bkolkata\b', r'\bchennai\b',
    r'\bhyderabad\b', r'\bbengaluru\b', r'\bbangalore\b',
    r'\bpune\b', r'\bjaipur\b', r'\blucknow\b', r'\bahmedabad\b',
    r'\bkochi\b', r'\bgoa\b', r'\bsrinagar\b', r'\bchandigarh\b',
    # Indian sports bodies / leagues
    r'\bbcci\b', r'\bipl\b', r'\bisl\b', r'\bpkl\b',
    r'\bpro\s*kabaddi', r'\bdurand\s*cup', r'\branji\b',
    # Indian regulatory / cultural
    r'\bcbfc\b', r'\bdiwali\b', r'\bholi\b',
    # Multi-sport events where India competes
    r'\bcommonwealth\s*games\b', r'\bcwg\b', r'\basian\s*games\b',
]]

# Cricket is inherently relevant to Indian diaspora per editorial policy.
# These terms bypass the diaspora keyword check for sports articles.
_CRICKET_PATTERNS = [re.compile(p, re.IGNORECASE) for p in [
    r'\bcricket\b', r'\bicc\b', r'\bt20\b', r'\bodi\b',
    r'\bwicket', r'\bbowler', r'\bbatsman', r'\bbattes?man',
    r'\binnings\b', r'\blbw\b', r'\bstumps?\b',
    r'\btest\s*match', r'\btest\s*series',
    r'\brun\s*chase', r'\brun[- ]?rate',
    # Cricket leagues worldwide (Indian diaspora follows cricket globally)
    r'\bcpl\b', r'\bsa20\b', r'\bpsl\b', r'\bbbl\b', r'\blpl\b',
    r'\bthe\s*hundred\b', r'\bbig\s*bash\b',
    # Cricket-specific sources (if source name appears in title/text)
    r'\bcricinfo\b', r'\bcricbuzz\b', r'\bespncric',
]]


def _has_diaspora_connection(title, signals, category):
    """Check if an entertainment/sports topic has Indian/diaspora connection.

    For sports: also accepts cricket-specific terms (cricket is inherently
    relevant to Indian diaspora per editorial policy).

    Checks headline + all signal titles + longest signal description.
    Returns True if connection found, False if not.
    """
    # Build text to scan: headline + best description + all signal titles
    best_desc = ""
    signal_titles = []
    for s in signals:
        d = s.get("description", "")
        if d and len(d) > len(best_desc):
            best_desc = d
        st = s.get("title", "")
        if st:
            signal_titles.append(st)
    text = title + " " + best_desc + " " + " ".join(signal_titles)

    # Check diaspora patterns (applies to both entertainment and sports)
    for pat in _DIASPORA_PATTERNS:
        if pat.search(text):
            return True

    # For sports: also check cricket-specific terms
    if category == "sports":
        for pat in _CRICKET_PATTERNS:
            if pat.search(text):
                return True

    return False

# ── Instagram handle reference for LLM ────────────────────────────────────────
def _build_ig_handle_block():
    """Load IG handles + metadata from DB registry for injection into LLM prompt."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from social_registry import load_registry
    registry = load_registry()
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
    """Build handle→full_name dict from DB registry for post-GPT name verification."""
    from social_registry import get_handle_name_map
    return get_handle_name_map("instagram")

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

IMPORTANT: Be generous with food, travel, and lifestyle stories — if a story has ANY Indian connection, score it at least 3. For entertainment, require a clear Indian/diaspora connection (Bollywood, Indian-origin talent, India box office) — generic Western entertainment with no Indian link scores 1-2.

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
- entertainment = Bollywood, South Indian cinema, Indian-origin actors/directors/musicians, OTT content with Indian cast or themes, and major Hollywood ONLY when there is a genuine Indian/diaspora connection (Indian-origin star, India box office, Indian remake). Generic Hollywood, Western music acts, WWE/AEW wrestling, Western reality TV, and non-Indian celebrity gossip with zero Indian connection should score 1-2

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
- "news" = India domestic politics & government, major geopolitics (wars, diplomacy, summits, UN), India-US/UK bilateral relations, major crime/justice, national security, disasters, elections, major policy changes that don't fit a specific category. Use "news" for big-picture stories — if it would be on the front page of a newspaper, it's probably "news."
- "nri-world" = stories specifically about diaspora life, NRI achievements, community events, cultural identity abroad, Indian-origin people in foreign countries, diaspora organizations. NOT a catch-all for India stories.
- When in doubt between "news" and "nri-world": if the story is about India or geopolitics, use "news". If it's about Indians living abroad or diaspora-specific issues, use "nri-world".
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
6. "kids_relevant": true ONLY if the story is specifically about K-12 education, youth competitions (spelling bee, science olympiad, math competitions, robotics), Indian-American kids' achievements, or education policy directly affecting school-age children. NOT for: student visa/immigration news, college admissions, crime involving minors, or generic "student" mentions.
7. "ig_handles": array of objects for ALL Instagram handles directly connected to this story.
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

Respond as JSON: {"results": [{"id": 1, "relevant": true, "coverage": "new", "score": 4, "category": "technology", "kids_relevant": false, "reason": "...", "ig_handles": [{"handle": "@sundarpichai", "type": "person", "keywords": ["google", "ceo", "ai"]}, {"handle": "@google", "type": "org", "keywords": ["google", "ai", "search"]}]},...]}\n"""

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
    if not topics_with_signals or (not OPENAI_KEY and not GOOGLE_AI_KEY):
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

        if error and GOOGLE_AI_KEY:
            # Fallback to Gemini 2.5 Flash
            gemini_prompt = payload["messages"][0]["content"]
            content, usage_g, error = gemini_llm_call(gemini_prompt, max_tokens=max(len(batch) * 130, 2000), label=f"gemini_score_{batch_start}", timeout=60)

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
                    "kids_relevant": item.get("kids_relevant", False),
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
    TOPIC_WINDOW_DAYS = 3
    topic_cutoff = (datetime.now(timezone.utc) - timedelta(days=TOPIC_WINDOW_DAYS)).strftime("%Y-%m-%dT%H:%M:%SZ")
    # Cooldown: skip topics evaluated in the last 6 hours to avoid re-scoring too soon,
    # but re-evaluate older pending topics that were selected but never written.
    eval_cooldown = (datetime.now(timezone.utc) - timedelta(hours=6)).strftime("%Y-%m-%dT%H:%M:%SZ")
    print(f"\n── Step 1: Loading pending V3 topics (last {TOPIC_WINDOW_DAYS}d) ──")
    topics = []
    offset = 0
    while True:
        page = sb_get("p2_topics", {
            "select": "id,canonical_title,signal_count,status,created_at,last_signal_at",
            "last_signal_at": f"gte.{topic_cutoff}",
            "status": "eq.pending",
            "or": f"(evaluated_at.is.null,evaluated_at.lt.{eval_cooldown})",
            "order": "last_signal_at.desc",
        }, range_header=f"{offset}-{offset+999}")
        if not page or isinstance(page, dict):
            break
        topics.extend(page)
        if len(page) < 1000:
            break
        offset += 1000

    print(f"  Found {len(topics)} pending topics (window: {topic_cutoff})")
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
    CHUNK = 300
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

    _dedup_stop = {"the","and","for","with","from","that","this","will","has","have",
                   "been","after","about","over","says","said","more","than","also",
                   "new","india","indian","how","why","what","when","where","who",
                   "could","would","first","last","may","get","set","into","most"}

    if older_articles and topics:
        # Find older headlines that share distinctive keywords with incoming topics
        # Only check topics WITH signals (others are auto-rejected in Step 4)
        added = 0
        _recent_headline_set = {(a.get("headline") or "").lower() for a in recent_articles}
        # Pre-compute older article word sets once
        _older_parsed = []
        for oa in older_articles:
            h_lower = (oa.get("headline") or "").lower()
            if h_lower in _recent_headline_set:
                continue  # already in dedup context
            h_words = frozenset(re.findall(r'[a-z]{3,}', h_lower)) - _dedup_stop
            h_distinctive = frozenset(w for w in h_words if len(w) >= 6)
            _older_parsed.append((oa, h_words, h_distinctive, h_lower))
        topics_with_sigs = [t for t in topics if t.get("signals")]
        for t in topics_with_sigs:
            t_title = (t.get("canonical_title") or "").lower()
            t_words = frozenset(re.findall(r'[a-z]{3,}', t_title)) - _dedup_stop
            if len(t_words) < 2:
                continue
            # Distinctive words = 6+ chars (proper nouns, specific terms)
            t_distinctive = frozenset(w for w in t_words if len(w) >= 6)
            for oa, h_words, h_distinctive, h_lower in _older_parsed:
                overlap = t_words & h_words
                distinctive_overlap = t_distinctive & h_distinctive
                # Match if 3+ total keyword overlap OR 2+ distinctive (6+ char) overlap
                if (len(overlap) >= 3 or len(distinctive_overlap) >= 2) and h_lower not in _recent_headline_set:
                    recent_articles.append(oa)
                    _recent_headline_set.add(h_lower)
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
    # Pre-compute published headline bases and word sets ONCE for O(n+m) instead of O(n*m) regex calls
    topic_statuses = {}  # topic_id -> status to write back
    _pub_titles_lower = {(a.get("headline") or "").lower().strip() for a in recent_articles}
    _strip_src_re = re.compile(r'\s*[-–—]\s*[a-z0-9 ]{2,30}$')
    _pub_bases = set()  # stripped base strings for exact match
    _pub_word_sets = []  # list of (pub_base, frozenset_of_words) for overlap check
    for pub in _pub_titles_lower:
        pub_base = _strip_src_re.sub('', pub).strip()
        if pub_base:
            _pub_bases.add(pub_base)
            p_words = frozenset(re.findall(r'[a-z]{3,}', pub_base)) - _dedup_stop
            if p_words:
                _pub_word_sets.append(p_words)

    # ── Step 3b-ii: Entity-aware dedup ──
    # Extract 2-word NAME pairs from headlines. Headlines are title-cased, so every word
    # is capitalized — we can't use capitalization to find entities. Instead, we require
    # BOTH words to NOT be common English words (dictionary + suffix check). Only genuinely
    # distinctive name-like pairs survive: "Anil Menon", "Lamine Yamal", "Virat Kohli".
    # Common word pairs like "Profit Surges", "Weather Forecasts" are filtered.
    # Recall losses (e.g. "Taylor Swift" where "swift" is common) are acceptable —
    # the LLM dedup in Step 4 catches those.
    _source_suffix_re2 = re.compile(r'\s*[-–—|]\s*[A-Z][\w\s.&\'-]{2,40}$')
    _cap_word_re = re.compile(r'\b[A-Z][a-z]+\b')

    # Common English words — if EITHER word in a pair is here, the pair is not a name.
    _COMMON_ENGLISH = frozenset("""
        a about above across act add after again against age ago ahead aid aim air
        all allow along also always among amount an and another answer any appear
        apply area arm around arrive art as ask at away back bad bag bank bar base
        be bear beat become bed been before begin behind believe below best better
        between beyond big bill bit black block blow blue board body bomb bond book
        boom boost born both bottom box boy brain brand break bring broad brought
        brown budget build burn bus business busy but buy by call came camp can cap
        car care carry case cash cast catch cause cell center central chain chair
        chance change charge check chief child choice choose church city civil claim
        class clean clear climb close club coach coal cold collect color come common
        company compare complete concern condition consider contain control cool
        copy core cost could count country couple course court cover crash create
        crew crime cross crowd cry cup current cut daily damage dance danger dark
        data date daughter day dead deal dear death debate decide decline deep
        defend degree demand deny design despite detail develop die difficult
        dinner direction discover discuss disease doctor does dog dollar done door
        double doubt down draw dream drink drive drop drug dry during duty each
        early earn earth ease east easy eat edge effect effort eight either elect
        else emerge end enemy energy enjoy enough enter entire error especially
        even evening event ever every evidence evil exactly example except
        executive exist expect experience expert explain eye face fact fail fair
        fall family far fast father fear federal feed feel few field fight figure
        fill final finally financial find fine finger finish fire firm first fish
        fit five fix flat floor fly follow food foot for force foreign forget form
        former forward found four free fresh friend from front full fund future gain
        game garden gas gate gather gave general get girl give glad glass go goal
        goes gold golden gone good got govern grace grand green grew ground group
        grow growth guard guess guide gun guy had hair half hall hand hang happen
        happy hard has hat have he head health hear heart heat heavy help her here
        high hill him his hit hold hole home hope hot hotel hour house how huge
        human hundred hung hunt hurt husband idea if image impact important in
        include increase indeed industry information inside instead interest into
        invest iron island issue it its job join joint judge jump just keen keep key
        kick kid kill kind king kitchen knew knock know labor lack lady laid land
        language large last late later laugh launch law lay lead leader learn least
        leave left legal less let letter level lie life lift light like likely limit
        line link list listen little live local long look lord lose loss lost lot
        loud love low lower luck lunch machine made main major make male man manage
        many march mark market mass master match matter may maybe me meal mean
        measure media medical meet member memory men mention middle might military
        million mind minister minor minute miss model modern moment money month
        more morning most mother mount mouth move much murder music must my name
        nation national natural near nearly necessary need network never new news
        next nice night nine no none nor normal north not note nothing notice now
        number occur of off offer office officer official often oh oil old on once
        one only onto open operation opportunity option or order other our out
        outside over own pace page paid pain pair paper park part particular
        partner party pass past path patient pattern pay peace people per percent
        perform perhaps period person phase phone pick piece place plan plant play
        player please plus point police policy political poor popular position
        possible post pound power practice prepare present president pressure
        pretty prevent price prime private probably problem produce product
        program project promise protect prove provide public pull purpose push
        put quality quarter question quick quickly quiet quite race raise range
        rate rather reach read ready real reality reason receive record red reduce
        region relate release remain remember remove report represent require
        research resource respond rest result return reveal right ring rise risk
        road rock role roll room round route row rule run rush safe said sale same
        save saw say scene school science score season seat second section security
        see seek seem sell send senior sense series serious serve service set
        settle seven several shake shall shape share she ship shock shoot short
        shot should shoulder shout show shut side sign significant similar simple
        since sing single sir sister sit site situation six size skill skin small
        smile so social society soldier some son song soon sort sound source south
        southern space speak special specific speech spend sport spot spread
        spring square staff stage stand standard star start state station stay
        step stick still stock stop store story straight strategy street strike
        strong structure student study stuff style subject success such suddenly
        suffer suggest summer sun support sure surface surprise sweet system table
        take talk target task tax teach team technology tell ten tend term test than
        thank that the their them then there these they thing think third this
        those though thought three through throw thus tie till time tiny to today
        together told tomorrow tonight too tool top total touch tough toward town
        track trade traditional train travel treat tree trial trip trouble true
        trust truth try turn tv two type under understand union unit united until
        up upon urban us use used usual valley value various very victim view
        village violence visit voice vote wait walk wall want war watch water way
        we weapon wear weather week weight well went were west western what whatever
        when where whether which while white who whole whom whose why wide wife
        wild will win wind window wish with within without woman wonder wood word
        work worker world worry worst worth would write wrong yard yeah year yes
        yet you young your youth zero
        alert allege amid american announce annual arab are award bail beef billion
        boot brew brief broker byte cabinet cafe canal cargo cent cheap chicken chinese
        coal coffee column confirm crew crude cyber defeat deliver deploy
        diesel dispute draft drone eager earlier elect elite emerge enact exert
        export extend extract fake fare ferry fiber fleet flour forge former
        fossil forecast fraud grill halt harvest herb hover immune import inquiry
        intact intern invest juice kerosene kidney laser lease lever lodge
        luxury maple margin merge metro mill mortar niche offset olive
        orchid onset orbit otter outlook oxide panel pasta patent pepper
        petrol pier plunge portray portrait portfolio pose potential probe profit
        protein pulse quota radar rally reactor refine reform regime relay revenue
        relief render renew rescue resort retire resume reveal ribbon rival roster
        rubber runway salon salute san sanction savor scandal sea secular seize
        saudi sensor sheriff shrimp siege silk silver sketch solar solemn sonar
        spectrum spice spiral stagger static statue steer strand summit surge
        super surplus suspend symptom tariff tender terrain textile tobacco
        token torture transit trauma treaty troop trophy tunnel turmoil
        tutor ultimate umbrella undergo unrest unveil upgrade uphold upset
        vaccine venture verdict veteran video vigor vintage viral wafer wheat widow
        yield
    """.split())

    # Suffixes that mark common English words (verb forms, abstract nouns, adjectives).
    # Any word ≥5 chars ending in these is treated as common, catching words the
    # dictionary misses. Names almost never have these endings.
    _COMMON_SUFFIXES = ('ing', 'tion', 'sion', 'ment', 'ness', 'ence', 'ance',
                        'ity', 'ous', 'ious', 'ive', 'ful', 'less', 'ally',
                        'ble', 'ical', 'ular', 'ated', 'ized', 'ling', 'ship')

    def _is_common_word(w: str) -> bool:
        """Check if lowercased word is common English (not a name)."""
        if w in _COMMON_ENGLISH:
            return True
        if len(w) >= 5 and w.endswith(_COMMON_SUFFIXES):
            return True
        # Inflection stemming: strip 1-3 trailing chars and check if stem is common.
        # Handles plurals (scores→score), past tense (crashed→crash, named→name),
        # comparatives (louder→loud), 3rd person (grows→grow), double-consonant
        # forms (spotted→spot via strip-3). Minimum stem length 4 to avoid
        # false matches on short roots (menon→men, sonam→son, sundar→sun).
        if len(w) >= 4 and w[:-1] in _COMMON_ENGLISH:
            return True
        if len(w) >= 6 and w[:-2] in _COMMON_ENGLISH:
            return True
        if len(w) >= 7 and w[:-3] in _COMMON_ENGLISH:
            return True
        return False

    def _extract_named_entities(headline_original: str) -> frozenset:
        """Extract 2-word name pairs: adjacent capitalized words where BOTH are uncommon."""
        h = _source_suffix_re2.sub('', headline_original).strip()
        words = _cap_word_re.findall(h)
        pairs = set()
        for i in range(len(words) - 1):
            a_low, b_low = words[i].lower(), words[i + 1].lower()
            # Skip if either word is a common English word
            if _is_common_word(a_low) or _is_common_word(b_low):
                continue
            # Check adjacency in original text
            a_end = h.find(words[i]) + len(words[i])
            b_start = h.find(words[i + 1], a_end)
            between = h[a_end:b_start]
            if between.strip() == "" and len(between) <= 2:
                pair = f"{a_low} {b_low}"
                if len(pair) >= 7:  # at least 3+3+space
                    pairs.add(pair)
        return frozenset(pairs)

    # We need the original-case headlines for entity extraction
    _pub_headlines_original = [(a.get("headline") or "") for a in recent_articles]
    _pub_entity_sets = [_extract_named_entities(h) for h in _pub_headlines_original]



    _hard_dedup_count = 0
    _entity_dedup_count = 0
    _skipped_no_signals = 0
    for t in topics:
        # Skip topics without signals — they'll be auto-rejected in Step 4 anyway.
        # This avoids the expensive O(n×m) word-overlap loop on 12K+ dead topics.
        if not t.get("signals"):
            _skipped_no_signals += 1
            continue
        t_title = (t.get("canonical_title") or "").lower().strip()
        t_base = _strip_src_re.sub('', t_title).strip()
        if not t_base:
            continue
        # Exact match after stripping source
        if t_base in _pub_bases:
            topic_statuses[t["id"]] = "rejected"
            _hard_dedup_count += 1
            continue
        # High word overlap (>=80% of words match)
        t_words = frozenset(re.findall(r'[a-z]{3,}', t_base)) - _dedup_stop
        if not t_words:
            continue
        _matched = False
        for p_words in _pub_word_sets:
            overlap = len(t_words & p_words) / min(len(t_words), len(p_words))
            if overlap >= 0.8:
                topic_statuses[t["id"]] = "rejected"
                _hard_dedup_count += 1
                _matched = True
                break
        if _matched:
            continue

        # Entity-aware dedup: extract multi-word named entities from the ORIGINAL-case topic title
        # Since we only extract multi-word entities now, any shared entity IS a person/org name match
        t_title_orig = t.get("canonical_title") or ""
        t_ents = _extract_named_entities(t_title_orig)
        if t_ents:
            for i, p_ents in enumerate(_pub_entity_sets):
                if not p_ents:
                    continue
                shared_ents = t_ents & p_ents
                # A shared multi-word entity (person/org name) = same story
                # e.g. "Anil Menon", "Uday Ruddarraju", "Galaxy Watch", "Avengers Doomsday"
                if shared_ents:
                    topic_statuses[t["id"]] = "rejected"
                    _entity_dedup_count += 1
                    print(f"    Entity dedup: '{t_title_orig[:80]}' ↔ '{_pub_headlines_original[i][:80]}' (shared: {shared_ents})")
                    break
    if _skipped_no_signals:
        print(f"  Skipped dedup: {_skipped_no_signals} topics (no signals, will be auto-rejected)")
    if _hard_dedup_count:
        print(f"  Hard dedup rejected: {_hard_dedup_count} topics (title match with published)")
    if _entity_dedup_count:
        print(f"  Entity dedup rejected: {_entity_dedup_count} topics (named entity overlap with published)")

    # ── Step 4: LLM scoring + classification ──────────────────────────────────
    # Only LLM-score topics that have loaded signals AND weren't hard-deduped
    topics_with_loaded_signals = [t for t in topics if t.get("signals") and topic_statuses.get(t["id"]) != "rejected"]
    topics_without_signals = [t for t in topics if not t.get("signals") and topic_statuses.get(t["id"]) != "rejected"]

    # ── Backlog cap: limit topics scored per run to stay within timeout ──
    # After an ingest gap, thousands of topics can queue up. Scoring all of them
    # via LLM would exceed the writer cron's timeout window. Cap at 500 topics,
    # prioritized by signal count (more corroboration = more newsworthy) then
    # recency. Unscored topics stay pending and get picked up in the next run.
    MAX_TOPICS_TO_SCORE = 500
    if len(topics_with_loaded_signals) > MAX_TOPICS_TO_SCORE:
        topics_with_loaded_signals.sort(
            key=lambda t: (t.get("signal_count", 1), t.get("last_signal_at", "")),
            reverse=True
        )
        deferred_topics = topics_with_loaded_signals[MAX_TOPICS_TO_SCORE:]
        topics_with_loaded_signals = topics_with_loaded_signals[:MAX_TOPICS_TO_SCORE]
        print(f"\n  ⚠ Backlog cap: scoring top {MAX_TOPICS_TO_SCORE} of {MAX_TOPICS_TO_SCORE + len(deferred_topics)} topics (by signal count + recency)")
        print(f"    Deferred {len(deferred_topics)} lower-priority topics to next run")

    print(f"\n── Step 4: LLM scoring + coverage classification ──")
    print(f"  Topics with loaded signals: {len(topics_with_loaded_signals)} (scoring)")
    print(f"  Topics without signals: {len(topics_without_signals)} (auto-rejecting)")
    llm_results = llm_score_topics(topics_with_loaded_signals, recent_articles)

    scored = []
    stats = {"new": 0, "update": 0, "duplicate": 0, "irrelevant": 0, "no_result": 0}

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
            # ── Diaspora gate for entertainment/sports ──
            # LLM scoring ignores prompt instructions and gives high scores to
            # entertainment/sports with zero Indian connection. Enforce mechanically.
            _gate_cat = _CAT_NORMALIZE.get(llm.get("category", "news"), llm.get("category", "news"))
            if _gate_cat in ("entertainment", "sports") and llm.get("score", 1) >= 3:
                if not _has_diaspora_connection(t["canonical_title"], t.get("signals", []), _gate_cat):
                    _old_score = llm["score"]
                    llm["score"] = 2  # cap at 2 → caught by score floor below
                    stats["diaspora_filtered"] = stats.get("diaspora_filtered", 0) + 1
                    print(f"    ⚠ Diaspora gate [{_gate_cat}]: '{t['canonical_title'][:80]}' score {_old_score}→2 (no Indian/diaspora keywords)")

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
                "kids_relevant": llm.get("kids_relevant", False),
            })
            topic_statuses[t["id"]] = "selected"
        else:
            stats["no_result"] += 1
            topic_statuses[t["id"]] = "pending"  # leave for next run

    print(f"  Classification: {stats['new']} new, {stats['update']} updates, {stats['duplicate']} duplicates, {stats['irrelevant']} irrelevant, {stats.get('low_score', 0)} low-score rejected, {stats.get('diaspora_filtered', 0)} diaspora-filtered, {stats['no_result']} unscored")

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

    # ── Step 5b: News starvation guard ────────────────────────────────────────
    # If no "news" candidates were selected, promote the highest-scoring
    # nri-world candidate to "news" so the homepage carousel stays fresh.
    if cat_counts.get("news", 0) == 0:
        nri_in_balanced = [c for c in balanced if c["category"] == "nri-world"]
        if nri_in_balanced:
            best_nri = max(nri_in_balanced, key=lambda c: c.get("llm_score", 0))
            best_nri["category"] = "news"
            cat_counts["news"] = 1
            cat_counts["nri-world"] = cat_counts.get("nri-world", 1) - 1
            print(f"  ⚠ No news candidates — promoted nri-world → news: {best_nri['title'][:70]}")

    # ── Step 6: Final LLM dedup on capped candidates ─────────────────────────
    if len(balanced) > 1 and (OPENAI_KEY or GOOGLE_AI_KEY):
        print(f"\n── Step 6: Final LLM dedup ({len(balanced)} candidates) ──")
        survivor_titles = [c["title"][:120] for c in balanced]
        lines = [f"{i+1}. {t}" for i, t in enumerate(survivor_titles)]
        dedup_payload = {
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": MERGE_PROMPT + "\n\nHeadlines:\n" + "\n".join(lines)}],
            "response_format": {"type": "json_object"},
            "max_tokens": 1000,
            "temperature": 0,
        }
        content, usage, error = llm_call(dedup_payload, label="final_dedup")
        if error and GOOGLE_AI_KEY:
            dedup_prompt = dedup_payload["messages"][0]["content"]
            content, usage, error = gemini_llm_call(dedup_prompt, max_tokens=1000, label="gemini_final_dedup")
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

    # ── Write candidates JSON FIRST (before DB updates, so timeout doesn't lose them) ──
    output = {
        "timestamp": NOW_ISO,
        "total_topics_evaluated": len(topics),
        "candidates": balanced,
    }
    with open(OUT_PATH, "w") as f:
        json.dump(output, f, indent=2)

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

    # (candidates JSON already written before Step 7)

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

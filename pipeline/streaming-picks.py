#!/usr/bin/env python3
"""
Generate streaming-picks.json for the What to Watch This Week section.

Automatically discovers this week's new Indian/diaspora-relevant streaming
releases via web search + GPT-4o-mini curation. Enriches with Wikipedia
poster images (CC-licensed) and YouTube trailer URLs.

CORROBORATION (added 2026-10-31, after a hallucinated entry shipped):
GPT curation is a PROPOSAL step only. Every pick then passes through
corroborate_picks(), which fetches independent evidence (Wikipedia page +
infobox, platform-neutral press search) and verifies platform, cast,
director and synopsis against it. Picks that cannot be corroborated are
DROPPED, never published on model knowledge alone (fail-closed).

Run: python3 -u pipeline/streaming-picks.py
Output: public/data/streaming-picks.json

Uses curl for all HTTP calls (no requests/urllib for external APIs).
"""
import json, os, sys, re, time, subprocess, tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import quote

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "public" / "data" / "streaming-picks.json"

# ── Env loading ───────────────────────────────────────────────────────────────
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

OPENAI_KEY = os.environ.get("OPENAI_API_KEY", "")

UA = "TheVideshi/1.0 (https://thevideshi.com; editorial)"
WIKI_API = "https://en.wikipedia.org/api/rest_v1/page/summary"


def now_utc():
    return datetime.now(timezone.utc)


def today_str():
    return now_utc().strftime("%Y-%m-%dT%H:%M:%SZ")


def week_range():
    now = now_utc()
    monday = now - timedelta(days=now.weekday())
    sunday = monday + timedelta(days=6)
    return f"{monday.strftime('%b %d')} – {sunday.strftime('%b %d, %Y')}"


# ── curl helpers ──────────────────────────────────────────────────────────────

def curl_get(url, headers=None, timeout=15):
    """GET request via curl. Returns (status_code, body_text)."""
    cmd = ["curl", "-sS", "-w", "\n%{http_code}", "--max-time", str(timeout), url]
    if headers:
        for k, v in headers.items():
            cmd += ["-H", f"{k}: {v}"]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 5)
        if r.returncode != 0:
            return 0, ""
        lines = r.stdout.rsplit("\n", 1)
        if len(lines) == 2:
            body, code = lines
            return int(code), body
        return 0, r.stdout
    except Exception as e:
        print(f"  ⚠ curl_get error: {e}")
        return 0, ""


def curl_post_json(url, data, headers=None, timeout=60):
    """POST JSON via curl. Returns parsed JSON or None."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
        json.dump(data, tmp)
        tmp_path = tmp.name

    cmd = [
        "curl", "-sS", "--max-time", str(timeout),
        "-X", "POST", url,
        "-H", "Content-Type: application/json",
        "-d", f"@{tmp_path}",
    ]
    if headers:
        for k, v in headers.items():
            cmd += ["-H", f"{k}: {v}"]

    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 10)
        os.unlink(tmp_path)
        if r.returncode != 0:
            return None
        return json.loads(r.stdout)
    except Exception as e:
        print(f"  ⚠ curl_post error: {e}")
        try:
            os.unlink(tmp_path)
        except:
            pass
        return None


# ── Web search for streaming releases ─────────────────────────────────────────

def web_search(query, timeout=15):
    """Search via DuckDuckGo HTML and extract result snippets."""
    encoded_q = quote(query)
    url = f"https://html.duckduckgo.com/html/?q={encoded_q}"
    code, body = curl_get(url, headers={"User-Agent": UA}, timeout=timeout)
    if code != 200 or not body:
        return ""
    # Extract text content, strip HTML
    text = re.sub(r'<script[^>]*>.*?</script>', '', body, flags=re.DOTALL)
    text = re.sub(r'<style[^>]*>.*?</style>', '', body, flags=re.DOTALL)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text[:8000]  # Cap to avoid huge prompts


def discover_streaming_releases():
    """Search the web for this week's streaming releases. Returns combined text."""
    now = now_utc()
    month_year = now.strftime("%B %Y")
    week_str = now.strftime("%B %d")

    queries = [
        f"new Indian movies OTT release this week {month_year}",
        f"new Hindi movies streaming this week {month_year}",
        f"new Tamil Telugu movies OTT release {month_year}",
        f"Netflix new releases India {month_year}",
        f"JioHotstar new releases this week {month_year}",
        f"new movies streaming this week {month_year}",
        f"Amazon Prime Video new releases {month_year}",
        f"new OTT releases this week India {week_str}",
    ]

    all_text = []
    for q in queries:
        print(f"  🔍 Searching: {q}")
        result = web_search(q)
        if result:
            all_text.append(f"[Search: {q}]\n{result}")
        time.sleep(0.5)  # Be polite

    return "\n\n".join(all_text)


# ── GPT-4o-mini curation ──────────────────────────────────────────────────────

def curate_picks(search_results):
    """Use GPT-4o-mini to extract and curate streaming picks from search results."""
    if not OPENAI_KEY:
        print("ERROR: No OPENAI_API_KEY")
        return [], ""

    now = now_utc()
    week_of = week_range()

    prompt = f"""You are the entertainment editor for The Videshi, a news site for the Indian diaspora in the US, UK, Canada, and Australia.

Today is {now.strftime('%B %d, %Y')}. The week is {week_of}.

From the search results below, identify movies and shows that are NEW on streaming platforms THIS WEEK (or in the last 7-10 days). Do NOT include titles from more than 2 weeks ago.

PRIORITIES:
1. New Indian language content (Hindi, Tamil, Telugu, Malayalam, Kannada, Bengali, Marathi, Punjabi) — these are MOST important
2. Indian-origin cast/crew in international productions
3. Major global releases the diaspora would care about (big blockbusters, acclaimed shows)
4. South Asian stories or themes in any language

PLATFORMS to look for: Netflix, Prime Video, JioHotstar (formerly Disney+ Hotstar), Disney+, SonyLiv, Zee5, Paramount+, Apple TV+, SunNxt, JioCinema, Lionsgate Play, Mubi

For each pick, provide:
- title: exact title
- slug: URL-safe lowercase slug (e.g., "musafir-cafe")
- platform: streaming platform name (use "JioHotstar" not "Hotstar" or "Disney+ Hotstar")
- platform_icon: lowercase key (netflix, prime, hotstar, apple tv+, disney+, zee5, sonyliv, jiocinema, paramount+, sunnxt, mubi, lionsgate)
- genre: short genre label (e.g., "Romantic Drama", "Action Thriller", "Comedy Crime")
- year: release year (integer)
- media_type: "film" or "series"
- synopsis: 2-3 sentence synopsis. Be specific about plot — no vague "journey of self-discovery" filler. Mention specific characters, settings, conflicts.
- cast: array of main cast names (3-5 names). Use REAL names only — do NOT invent cast members.
- director: director name (empty string if unknown)
- why_watch: 1-2 sentences on why this is worth watching. Be opinionated and specific, like a friend recommending.
- is_indian: true if Indian language or Indian-origin talent is central
- watch_url: platform search URL for this title (e.g., "https://www.netflix.com/search?q=title+here")
- language: primary language (e.g., "Hindi", "Tamil", "English", "Telugu")
- trending: true for up to 3 titles getting the most buzz right now

Return 8-12 picks. At least 5 should be Indian content if available.

CRITICAL:
- Only include titles you are CONFIDENT are actually streaming NOW or this week. If you're unsure about availability, skip it.
- Do NOT make up cast, directors, or plot details. If you don't know, use empty arrays/strings.
- Do NOT include titles that have been streaming for months — only recent additions.
- Every pick is INDEPENDENTLY VERIFIED after this step against Wikipedia and press sources. Any pick whose platform, cast or synopsis cannot be corroborated from a fetched source is dropped automatically — an unverifiable pick is worse than one fewer pick.

SEARCH RESULTS:
{search_results[:12000]}

Respond as JSON: {{"picks": [...], "editorial_intro": "2-3 sentence summary of this week's highlights"}}"""

    payload = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}],
        "response_format": {"type": "json_object"},
        "max_tokens": 4000,
        "temperature": 0.3,
    }

    print("  🤖 Calling GPT-4o-mini for curation...")
    result = curl_post_json(
        "https://api.openai.com/v1/chat/completions",
        payload,
        headers={"Authorization": f"Bearer {OPENAI_KEY}"},
        timeout=60,
    )

    if not result:
        print("  ❌ GPT-4o-mini call failed")
        return [], ""

    if "error" in result:
        print(f"  ❌ GPT error: {result['error'].get('message', str(result['error']))}")
        return [], ""

    usage = result.get("usage", {})
    cost = usage.get("prompt_tokens", 0) * 0.15 / 1_000_000 + usage.get("completion_tokens", 0) * 0.6 / 1_000_000
    print(f"  💰 GPT cost: ${cost:.4f} ({usage.get('prompt_tokens', 0)} in, {usage.get('completion_tokens', 0)} out)")

    try:
        content = json.loads(result["choices"][0]["message"]["content"])
        picks = content.get("picks", [])
        editorial = content.get("editorial_intro", "")
        print(f"  ✅ Got {len(picks)} picks from GPT")
        return picks, editorial
    except (json.JSONDecodeError, KeyError, IndexError) as e:
        print(f"  ❌ Failed to parse GPT response: {e}")
        return [], ""


# ── Corroboration: fail-closed verification of every pick ────────────────────
#
# Why this exists (2026-10-31): the previous pipeline published whatever
# GPT-4o-mini proposed. The model had paired REAL titles found in search
# snippets with cast/synopsis/platform details from its own imagination —
# e.g. "Gajab Raat" shipped with an invented cast (Rajkummar Rao, Bhumi
# Pednekar, Vikrant Massey), a fabricated heist-comedy synopsis and the
# wrong platform; 5 of the other 6 picks that week had fully invented
# casts too, and one title presented as a Zee5 streaming pick was a film
# still playing in cinemas. Nothing downstream checked any field.
#
# The rule now: a pick is emitted ONLY with platform, cast and synopsis
# corroborated by a fetched source (Wikipedia page/infobox and/or press
# coverage). Unverifiable titles are dropped, never filled in.

WIKI_API_ACTION = "https://en.wikipedia.org/w/api.php"

PLATFORM_ALIASES = {
    "netflix": ("netflix",),
    "prime video": ("prime video", "amazon prime"),
    "jiohotstar": ("jiohotstar", "hotstar"),
    "zee5": ("zee5",),
    "sonyliv": ("sonyliv", "sony liv"),
    "disney+": ("disney+", "disney plus"),
    "apple tv+": ("apple tv+",),
    "paramount+": ("paramount+",),
    "sunnxt": ("sunnxt", "sun nxt"),
    "jiocinema": ("jiocinema", "jio cinema"),
    "mubi": ("mubi",),
    "lionsgate play": ("lionsgate",),
}

_SYNOPSIS_STOPWORDS = set(
    "the a an and or of to in on for with as at by from is are was were be been "
    "it its this that their they them he she his her who when while into over "
    "after before between must can will would story film series movie show "
    "one two new life love world journey".split()
)


def _norm(s):
    """Lowercase, punctuation-stripped, whitespace-collapsed text."""
    s = re.sub(r"[^a-z0-9 ]", " ", (s or "").lower())
    return re.sub(r"\s+", " ", s).strip()


def _lev_le1(a, b):
    """True if a and b are within edit distance 1 (and lengths differ by <=1)."""
    if abs(len(a) - len(b)) > 1:
        return False
    if len(a) > len(b):
        a, b = b, a
    diffs = 0
    i = j = 0
    while i < len(a) and j < len(b):
        if a[i] == b[j]:
            i += 1
            j += 1
        else:
            diffs += 1
            if diffs > 1:
                return False
            if len(a) == len(b):
                i += 1
            j += 1
    return diffs + (len(b) - j) <= 1


def _token_in(token, words):
    if token in words:
        return True
    # Surname carried inside a longer evidence word ("krishnan" in
    # "sundarakrishnan") still corroborates.
    if len(token) >= 5 and any(token in w for w in words):
        return True
    # One-letter transliteration variants ("Madhumitha" vs "Madhumita").
    if len(token) >= 6 and any(_lev_le1(token, w) for w in words if abs(len(w) - len(token)) <= 1):
        return True
    return False


def _name_in(name, text_norm):
    """True if a person's name is corroborated by evidence text.

    Every significant token of the name must be evidenced (handles
    'Gouri G. Kishan' vs 'Gouri Kishan'). Invented names still fail:
    none of their tokens appear in the evidence in any of these forms."""
    tokens = [t for t in _norm(name).split() if len(t) > 1]
    if not tokens:
        return False
    words = set(text_norm.split())
    return all(_token_in(t, words) for t in tokens)


def _content_words(text):
    return {t for t in _norm(text).split() if len(t) > 3 and t not in _SYNOPSIS_STOPWORDS}


def _clean_wiki_markup(s):
    s = re.sub(r"<ref[^>]*>.*?</ref>", " ", s or "", flags=re.DOTALL)
    s = re.sub(r"<ref[^>]*/>", " ", s)
    s = re.sub(r"\[\[(?:[^\]|]*\|)?([^\]]*)\]\]", r"\1", s)
    # Templates can nest (e.g. {{Plainlist| ... {{ubl|...}} }}): peel the
    # innermost layer repeatedly until none remain.
    for _ in range(6):
        stripped = re.sub(r"\{\{[^{}]*\}\}", " ", s)
        if stripped == s:
            break
        s = stripped
    s = re.sub(r"\{\{[^|]*\|", " ", s)  # any unclosed template opener left over
    s = re.sub(r"<br\s*/?>", ", ", s)
    s = re.sub(r"<[^>]+>", " ", s)
    s = s.replace("'''", "").replace("''", "")
    return re.sub(r"\s+", " ", s).strip(" ,;")


def _infobox_field(block, *names):
    """Extract an infobox field, whose value may span several lines
    (e.g. a {{Plainlist}} cast list) up to the next field or the box end."""
    for name in names:
        m = re.search(rf"^\|\s*{name}\s*=\s*(.*?)(?=^\||^\}}\}})",
                      block, flags=re.MULTILINE | re.DOTALL)
        if m:
            return _clean_wiki_markup(m.group(1))
    return ""


def _split_people(field):
    if not field:
        return []
    parts = re.split(r",|\n|\*", field)
    return [p.strip() for p in parts if 2 < len(p.strip()) < 60][:6]


def fetch_wikipedia_page(page_title):
    """Fetch a Wikipedia page summary via REST. Returns dict or None."""
    encoded = quote(page_title.replace(" ", "_"), safe="/_:()%")
    code, body = curl_get(f"{WIKI_API}/{encoded}", headers={"User-Agent": UA}, timeout=8)
    if code != 200 or not body:
        return None
    try:
        return json.loads(body)
    except json.JSONDecodeError:
        return None


def _title_bases(title):
    """Acceptable Wikipedia page names for a pick title: the title itself,
    the part before a colon, and the title minus a trailing Season/Part N
    (series pages are named for the show, not the season)."""
    bases = {title.strip()}
    if ":" in title:
        bases.add(title.split(":")[0].strip())
    stripped = re.sub(r"\s*[:\-]?\s*(season|part|chapter)\s+\d+\s*$", "", title, flags=re.I).strip()
    if stripped:
        bases.add(stripped)
        if ":" in stripped:
            bases.add(stripped.split(":")[0].strip())
    return {_norm(b) for b in bases if b}


def search_wikipedia_titles(title, year=0):
    """Wikipedia full-text search → candidate page titles for a work."""
    bases = _title_bases(title)
    queries = []
    for b in sorted(bases, key=len, reverse=True):
        queries += [f"{b} film", f"{b} series", b]
    found = []
    for q in queries:
        url = (f"{WIKI_API_ACTION}?action=query&list=search&format=json"
               f"&srlimit=5&srsearch={quote(q)}")
        code, body = curl_get(url, headers={"User-Agent": UA}, timeout=8)
        if code == 200 and body:
            try:
                for hit in json.loads(body).get("query", {}).get("search", []):
                    t = hit.get("title", "")
                    if t and t not in found:
                        found.append(t)
            except json.JSONDecodeError:
                pass
        # Only pages actually about this title (allowing "(2026 film)" suffixes)
        matches = [t for t in found
                   if _norm(re.sub(r"\(.*?\)", "", t)).strip() in bases]
        if matches:
            return matches
        time.sleep(0.3)
    return []


def fetch_wikipedia_infobox(page_title):
    """Parse director/starring/language/release-year from a page's infobox."""
    url = (f"{WIKI_API_ACTION}?action=query&prop=revisions&rvprop=content"
           f"&rvsection=0&format=json&titles={quote(page_title)}")
    code, body = curl_get(url, headers={"User-Agent": UA}, timeout=8)
    if code != 200 or not body:
        return {}
    try:
        pages = json.loads(body).get("query", {}).get("pages", {})
        wikitext = ""
        for page in pages.values():
            revs = page.get("revisions", [])
            if revs:
                wikitext = revs[0].get("*", "") or revs[0].get("content", "")
    except (json.JSONDecodeError, AttributeError):
        return {}
    if "nfobox" not in wikitext:
        return {}
    block = wikitext[:8000]
    director = _infobox_field(block, "director", "directors", "directed by")
    starring = _infobox_field(block, "starring", "cast", "stars")
    language = _infobox_field(block, "language", "languages")
    dates = _infobox_field(block, "released", "release date", "release_date",
                           "first_aired", "first aired")
    year = 0
    m = re.search(r"\b(19|20)\d{2}\b", dates) or re.search(r"\b(19|20)\d{2}\b", block[:2000])
    if m:
        year = int(m.group(0))
    return {
        "director": director,
        "starring": _split_people(starring),
        "language": language.split(",")[0].strip() if language else "",
        "year": year,
    }


def fetch_title_evidence(pick):
    """Fetch independent evidence for a proposed pick.

    Sources: the work's Wikipedia page (summary + infobox) and a
    platform-neutral press search (the claimed platform is deliberately
    NOT in the query, so coverage cannot be steered into confirming it).
    Returns an evidence dict; evidence['found'] is the existence gate."""
    title = pick.get("title", "").strip()
    year = pick.get("year", 0) or 0
    evidence = {
        "found": False,
        "wiki_title": "",
        "wiki_extract": "",
        "wiki_thumb": "",
        "infobox": {},
        "press_text": "",
        "text": "",
    }
    if not title:
        return evidence

    # Wikipedia: pick the candidate page that is actually about a film/series
    for page_title in search_wikipedia_titles(title, year):
        summary = fetch_wikipedia_page(page_title)
        if not summary:
            continue
        desc = (summary.get("description") or "").lower()
        extract = summary.get("extract") or ""
        looks_like_work = any(k in desc for k in ("film", "series", "television", "programme", "program")) \
            or any(k in extract[:300].lower() for k in ("film", "series", "television"))
        if not looks_like_work:
            continue
        evidence["wiki_title"] = page_title
        evidence["wiki_extract"] = extract
        evidence["wiki_thumb"] = (summary.get("thumbnail") or {}).get("source", "")
        evidence["infobox"] = fetch_wikipedia_infobox(page_title)
        break

    # Press coverage (platform-neutral queries; also try the colon-base
    # title, since series coverage often omits the ": Season N" suffix)
    press_bits = []
    press_titles = {title, title.split(":")[0].strip()}
    for pt in press_titles:
        for q in (f'"{pt}" OTT release cast', f'"{pt}" where to watch streaming',
                  f'"{pt}" review cast director'):
            txt = web_search(q)
            if txt:
                press_bits.append(txt)
            time.sleep(0.3)
    evidence["press_text"] = "\n".join(press_bits)

    # A Wikipedia infobox/summary for a DIFFERENT work with the same title
    # (e.g. the 1990 film vs a 2026 namesake) must not corroborate this pick.
    wiki_year = evidence["infobox"].get("year", 0)
    if evidence["wiki_title"] and wiki_year and year and abs(wiki_year - year) > 1:
        print(f"    ⚠ Wikipedia page '{evidence['wiki_title']}' is a {wiki_year} work, "
              f"not the {year} pick — ignoring it")
        evidence["wiki_title"] = ""
        evidence["wiki_extract"] = ""
        evidence["wiki_thumb"] = ""
        evidence["infobox"] = {}

    text_parts = [evidence["wiki_extract"], evidence["press_text"]]
    ib = evidence["infobox"]
    if ib:
        text_parts.append(ib.get("director", ""))
        text_parts.append(" ".join(ib.get("starring", [])))
        text_parts.append(ib.get("language", ""))
    evidence["text"] = "\n".join(p for p in text_parts if p)

    title_norm = _norm(title)
    evidence["found"] = bool(evidence["wiki_title"]) or title_norm in _norm(evidence["press_text"])
    return evidence


def verify_pick(pick, evidence):
    """Verify one proposed pick against fetched evidence.

    Returns (cleaned_pick, "") on success or (None, reason) when the pick
    must be dropped. Pure function of (pick, evidence) — unit-testable
    without network. Fail-closed on every leg."""
    title = pick.get("title", "").strip()
    if not evidence or not evidence.get("found"):
        return None, "no corroborating source found for the title"

    text_norm = _norm(evidence.get("text", ""))
    ib = evidence.get("infobox") or {}

    # ── Platform must be corroborated by the evidence ──
    platform = (pick.get("platform") or "").strip()
    aliases = PLATFORM_ALIASES.get(platform.lower(), (_norm(platform),))
    if not any(_norm(a) in text_norm for a in aliases if a):
        return None, f"platform '{platform}' not corroborated by any source"

    # ── Cast: keep only names the evidence names; require >= 2 ──
    proposed = [c for c in (pick.get("cast") or []) if c and c.strip()]
    cast = [c for c in proposed if _name_in(c, text_norm)]
    dropped_names = [c for c in proposed if c not in cast]
    if dropped_names:
        print(f"    ⚠ {title}: uncorroborated cast removed: {dropped_names}")
    # Infobox starring is a RESCUE source only (when the proposal named
    # almost nobody real) — never an enrichment source: a series page's
    # infobox lists every season's cast, so supplementing freely would
    # re-add past-season names to a new season's pick.
    if len(cast) < 2:
        for name in ib.get("starring", []):
            if len(cast) >= 5:
                break
            if name not in cast and _name_in(name, text_norm):
                cast.append(name)
    if len(cast) < 2:
        return None, f"fewer than 2 corroborated cast members ({len(cast)} found)"
    pick["cast"] = cast[:5]

    # ── Director: keep only if corroborated, else infobox, else blank ──
    director = (pick.get("director") or "").strip()
    if director and not _name_in(director, text_norm):
        print(f"    ⚠ {title}: uncorroborated director '{director}' cleared")
        director = ""
    if not director and ib.get("director"):
        director = ib["director"].split(",")[0].strip()
    pick["director"] = director

    # ── Synopsis must be grounded in the evidence ──
    # The hard gates above (existence, platform, >=2 evidence-named cast)
    # carry the safety; this overlap is a grounding tripwire. 0.20 because
    # press-snippet evidence is thin — measured 2026-10-31: the CORRECTED
    # Gajab Raat synopsis scores 0.24 against fetched coverage, while the
    # fabricated heist-comedy original scores ~0. A fabricated plot shares
    # almost no content words with real coverage.
    synopsis = (pick.get("synopsis") or "").strip()
    words = _content_words(synopsis)
    overlap = (len(words & _content_words(evidence.get("text", ""))) / len(words)) if words else 0.0
    if overlap < 0.20:
        extract = (evidence.get("wiki_extract") or "").strip()
        if extract:
            sentences = re.split(r"(?<=[.!?])\s+", extract)
            grounded = " ".join(sentences[:2]).strip()
            if len(grounded) > 340:
                grounded = grounded[:337].rsplit(" ", 1)[0] + "..."
            print(f"    ⚠ {title}: synopsis overlap {overlap:.2f} — replaced with Wikipedia extract")
            pick["synopsis"] = grounded
        else:
            return None, f"synopsis not grounded in any source (overlap {overlap:.2f})"

    # ── Language from the infobox when available (it is sourced) ──
    if ib.get("language"):
        pick["language"] = ib["language"]

    # Carry the verified page's poster forward for the enrichment step
    if evidence.get("wiki_thumb"):
        pick["_wiki_thumb"] = evidence["wiki_thumb"]
    return pick, ""


def corroborate_picks(picks, evidence_fetcher=fetch_title_evidence):
    """Verify every proposed pick; drop the ones that fail. Fail-closed."""
    verified = []
    for pick in picks:
        title = pick.get("title", "?")
        print(f"  🔎 Corroborating: {title}")
        try:
            evidence = evidence_fetcher(pick)
        except Exception as e:
            print(f"    ❌ Dropped '{title}': evidence fetch failed ({e})")
            continue
        cleaned, reason = verify_pick(pick, evidence)
        if cleaned is None:
            print(f"    ❌ Dropped '{title}': {reason}")
        else:
            print(f"    ✅ Corroborated '{title}'")
            verified.append(cleaned)
    print(f"  Corroboration: {len(verified)}/{len(picks)} picks survived")
    return verified


# ── Wikipedia poster fetching (via curl) ──────────────────────────────────────

def fetch_wikipedia_image(title, year=0, media_type="auto"):
    """Get poster/thumbnail from Wikipedia via curl. Returns URL or empty string."""
    candidates = [title]
    base_title = title.split(":")[0].strip() if ":" in title else title
    if base_title != title:
        candidates.append(base_title)

    type_suffixes = []
    if media_type in ("film", "auto"):
        type_suffixes.append("film")
        if year:
            type_suffixes.append(f"{year} film")
    if media_type in ("series", "auto"):
        type_suffixes.append("TV series")
        if year:
            type_suffixes.append(f"{year} TV series")
        type_suffixes.append("web series")

    for base in [title, base_title]:
        for suffix in type_suffixes:
            candidates.append(f"{base} ({suffix})")

    # Deduplicate
    seen = set()
    unique = []
    for c in candidates:
        if c not in seen:
            seen.add(c)
            unique.append(c)

    for candidate in unique:
        encoded = quote(candidate.replace(" ", "_"), safe="/_:()%")
        url = f"{WIKI_API}/{encoded}"
        code, body = curl_get(url, headers={"User-Agent": UA}, timeout=8)
        if code == 200 and body:
            try:
                data = json.loads(body)
                thumb = data.get("thumbnail", {}).get("source", "")
                if thumb:
                    # Guard against same-title wrong-work pages: a bare title
                    # like "Love Always" once resolved to a music single's
                    # cover art. Only accept pages that are about a film/series
                    # (per their Wikidata description) or were reached via an
                    # explicit film/series candidate name.
                    desc = (data.get("description") or "").lower()
                    is_work_page = any(k in desc for k in
                                       ("film", "series", "television", "programme", "program"))
                    explicit = any(k in candidate for k in ("film)", "TV series", "web series"))
                    if is_work_page or explicit:
                        print(f"  ✅ Wikipedia image: {candidate}")
                        return thumb
                    print(f"  ⚠ Wikipedia page '{candidate}' is not a film/series page "
                          f"(description: {desc[:60]}) — skipping its image")
            except json.JSONDecodeError:
                pass
        time.sleep(0.3)

    print(f"  ❌ No Wikipedia image: {title}")
    return ""


# ── YouTube trailer search (via curl) ─────────────────────────────────────────

def youtube_search_url(title, suffix="official trailer"):
    query = f"{title} {suffix}".strip()
    return f"https://www.youtube.com/results?search_query={quote(query)}"


def try_find_youtube_trailer(title, year=0, language=""):
    """Try to find a YouTube trailer. Falls back to search URL."""
    lang_tag = f" {language}" if language and language != "English" else ""
    queries = [
        f"{title}{lang_tag} official trailer {year}" if year else f"{title}{lang_tag} official trailer",
        f"{title}{lang_tag} trailer",
    ]

    yt_headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }

    for query in queries:
        search_url = f"https://www.youtube.com/results?search_query={quote(query)}"
        code, body = curl_get(search_url, headers=yt_headers, timeout=10)
        if code == 200 and body:
            video_ids = re.findall(r'"videoId":"([A-Za-z0-9_-]{11})"', body)
            if video_ids:
                vid = video_ids[0]
                print(f"  🎬 YouTube trailer: {vid} for '{title}'")
                return f"https://www.youtube.com/watch?v={vid}"
        time.sleep(0.5)

    print(f"  📎 Using YouTube search URL: {title}")
    return youtube_search_url(title)


def verify_youtube_trailer(url, title):
    """Confirm a scraped watch URL is really this title's trailer, via oEmbed.

    The results-page scrape can misalign video IDs with titles, so an
    unverified first-hit once attached wrong videos. If oEmbed resolves
    the video and its title does not name this work, downgrade to a
    (non-embeddable) search URL rather than embedding a wrong video."""
    m = re.search(r"watch\?v=([A-Za-z0-9_-]{11})", url or "")
    if not m:
        return url
    code, body = curl_get(
        f"https://www.youtube.com/oembed?url={quote(url, safe='')}&format=json",
        headers={"User-Agent": UA}, timeout=8)
    if code != 200 or not body:
        return url  # cannot verify either way; keep, log nothing
    try:
        video_title = json.loads(body).get("title", "")
    except json.JSONDecodeError:
        return url
    base = _norm(title.split(":")[0])
    if base and base in _norm(video_title):
        return url
    tokens = [t for t in _norm(title).split() if len(t) > 3 and t not in ("season", "part")]
    vt = _norm(video_title)
    if tokens and sum(1 for t in tokens if t in vt) >= max(1, len(tokens) // 2):
        return url
    print(f"  ⚠ Trailer mismatch for '{title}': video is '{video_title}' — using search URL")
    return youtube_search_url(title)


# ── Slug generation ───────────────────────────────────────────────────────────

def make_slug(title):
    """Generate a URL-safe slug from a title."""
    slug = title.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    slug = re.sub(r'-+', '-', slug)
    return slug[:60]


# ── Main build ────────────────────────────────────────────────────────────────

def build():
    t0 = time.time()
    print(f"\n{'='*60}")
    print(f"Streaming Picks — {week_range()}")
    print(f"{'='*60}")

    # Step 1: Discover releases via web search
    print(f"\n── Step 1: Discovering streaming releases ──")
    search_results = discover_streaming_releases()
    if not search_results:
        print("  ❌ No search results found. Skipping update.")
        return False

    print(f"  Total search text: {len(search_results)} chars")

    # Step 2: Curate with GPT-4o-mini
    print(f"\n── Step 2: GPT-4o-mini curation ──")
    picks, editorial_intro = curate_picks(search_results)
    if not picks:
        print("  ❌ No picks returned. Keeping existing data.")
        return False

    # Step 3: Validate and clean picks
    print(f"\n── Step 3: Validating picks ──")
    valid_picks = []
    for pick in picks:
        title = pick.get("title", "").strip()
        if not title:
            continue

        # Ensure required fields
        pick.setdefault("slug", make_slug(title))
        pick.setdefault("platform", "Unknown")
        pick.setdefault("platform_icon", pick.get("platform", "").lower().replace(" ", ""))
        pick.setdefault("genre", "")
        pick.setdefault("year", now_utc().year)
        pick.setdefault("synopsis", "")
        pick.setdefault("cast", [])
        pick.setdefault("director", "")
        pick.setdefault("why_watch", "")
        pick.setdefault("is_indian", False)
        pick.setdefault("watch_url", "")
        pick.setdefault("language", "English")
        pick.setdefault("trending", False)

        # Normalize platform_icon
        icon_map = {
            "jiohotstar": "hotstar",
            "disney+ hotstar": "hotstar",
            "hotstar": "hotstar",
            "prime video": "prime",
            "amazon prime video": "prime",
            "amazon prime": "prime",
            "apple tv+": "apple tv+",
            "paramount+": "paramount+",
            "sony liv": "sonyliv",
            "lionsgate play": "lionsgate",
        }
        raw_icon = pick["platform_icon"].lower().strip()
        pick["platform_icon"] = icon_map.get(raw_icon, raw_icon)

        valid_picks.append(pick)

    print(f"  Valid picks: {len(valid_picks)}")

    if not valid_picks:
        print("  ❌ No valid picks after validation. Keeping existing data.")
        return False

    # Step 3.5: Corroborate every field against fetched sources (fail-closed).
    # GPT proposals are NOT publishable on their own — see corroborate_picks().
    print(f"\n── Step 3.5: Corroborating picks against sources ──")
    valid_picks = corroborate_picks(valid_picks)
    if not valid_picks:
        print("  ❌ No picks survived corroboration. Keeping existing data.")
        return False

    # Step 4: Enrich with Wikipedia posters and YouTube trailers
    print(f"\n── Step 4: Enriching with posters and trailers ──")
    for pick in valid_picks:
        title = pick["title"]
        year = pick.get("year", 0)
        media_type = pick.pop("media_type", "auto")
        language = pick.get("language", "")

        print(f"\n  Processing: {title}")

        # Wikipedia poster — prefer the poster of the page that corroborated
        # this pick (guaranteed same work); fall back to the guarded search.
        poster = pick.pop("_wiki_thumb", "") or fetch_wikipedia_image(title, year, media_type)
        pick["poster_url"] = poster
        pick["backdrop_url"] = poster  # Same image for backdrop

        # YouTube trailer (oEmbed-verified; wrong videos downgrade to search)
        trailer = try_find_youtube_trailer(title, year, language)
        pick["trailer_url"] = verify_youtube_trailer(trailer, title)

        time.sleep(0.3)

    # Step 5: Sort — trending Indian first, then Indian, then global
    print(f"\n── Step 5: Sorting and ranking ──")
    indian = [p for p in valid_picks if p.get("is_indian")]
    global_picks = [p for p in valid_picks if not p.get("is_indian")]

    indian.sort(key=lambda p: (0 if p.get("trending") else 1))
    global_picks.sort(key=lambda p: (0 if p.get("trending") else 1))

    all_sorted = indian + global_picks

    # Ensure max 3 trending
    trending_count = 0
    for pick in all_sorted:
        if pick.get("trending"):
            trending_count += 1
            if trending_count > 3:
                pick["trending"] = False

    for i, pick in enumerate(all_sorted):
        pick["rank"] = i + 1

    # Step 6: Write output
    print(f"\n── Step 6: Writing output ──")
    data = {
        "generated_at": today_str(),
        "week_of": week_range(),
        "editorial_intro": editorial_intro or "This week's streaming highlights from across platforms.",
        "picks": all_sorted,
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    # Summary
    with_images = sum(1 for p in all_sorted if p.get("poster_url"))
    with_embeds = sum(1 for p in all_sorted if "watch?v=" in p.get("trailer_url", ""))
    elapsed = time.time() - t0

    print(f"\n{'='*60}")
    print(f"✅ Wrote {len(all_sorted)} streaming picks to {OUT}")
    print(f"   Indian: {len(indian)}, Global: {len(global_picks)}")
    print(f"   Trending: {sum(1 for p in all_sorted if p.get('trending'))}")
    print(f"   With poster images: {with_images}/{len(all_sorted)}")
    print(f"   With embeddable trailers: {with_embeds}/{len(all_sorted)}")
    print(f"   Week: {data['week_of']}")
    print(f"   Elapsed: {elapsed:.1f}s")
    print(f"{'='*60}")

    return True


if __name__ == "__main__":
    success = build()
    sys.exit(0 if success else 1)

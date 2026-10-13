#!/usr/bin/env python3 -u
"""Build per-metro local news index for Your Hub.

V1: scans published article JSONs for US metro mentions (city name in
title/excerpt/body) — our own voice, precise, thin volume.
V2: Google News RSS per metro with a desi query + relevance filter —
external breadth. Merged: our articles first, RSS fills up to PER_METRO.

Writes public/data/local-news.json:
  { "metros": { "San Jose, CA": [{kind,slug|url,title,...}, ...] } }

Top PER_METRO most recent per metro. Ambiguous city names (Washington,
Portland) require state context to avoid false positives; San Jose is
guarded against San José, Costa Rica (metro_blocked). Both layers must
match the metro name in the TITLE — a Google query hit alone is not
proof a story is about the metro — and near-identical headlines across
outlets are deduped to one slot.

Run: python3 -u pipeline/build-local-news.py [--no-rss]
"""
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARTICLES_DIR = os.path.join(REPO, "public", "data", "articles")
OUT_PATH = os.path.join(REPO, "public", "data", "local-news.json")

# (city, state, [extra aliases]) — mirrors the frontend METRO_PICKER
METROS = [
    ("New York", "NY", ["NYC", "New York City"]),
    ("San Jose", "CA", []),
    ("San Francisco", "CA", ["SF", "Bay Area"]),
    ("Fremont", "CA", []),
    # Tri-Valley pooled under Dublin: Dublin CA alone returns zero desi
    # headline news from Google (Ireland swamps it) — its community news
    # lives in San Ramon / Pleasanton / Livermore headlines.
    ("Dublin", "CA", ["San Ramon", "Pleasanton", "Livermore", "Tri-Valley"]),
    ("Los Angeles", "CA", ["LA"]),
    ("Chicago", "IL", []),
    ("Houston", "TX", []),
    ("Dallas", "TX", ["DFW"]),
    ("Austin", "TX", []),
    ("Seattle", "WA", []),
    ("Boston", "MA", []),
    ("Atlanta", "GA", []),
    ("Washington", "DC", []),   # requires DC context (see below)
    ("Edison", "NJ", []),
    ("Philadelphia", "PA", ["Philly"]),
    ("Miami", "FL", []),
    ("Denver", "CO", []),
    ("Phoenix", "AZ", []),
    ("San Diego", "CA", []),
    ("Minneapolis", "MN", ["Twin Cities"]),
    ("Detroit", "MI", []),
    ("Portland", "OR", []),     # requires Oregon context (see below)
    ("Columbus", "OH", []),
    ("Raleigh", "NC", ["Research Triangle"]),
    ("Tampa", "FL", []),
    ("Las Vegas", "NV", ["Vegas"]),
]

# Institutional uses of city names that are NOT local news
# ("New York Fed" is a bank, not the city)
EXCLUDE_RX = re.compile(
    r"\b(new york fed|federal reserve bank of new york|new york times\b|"
    r"\bnyt\b|new york stock exchange\b|\bnyse\b|wall street journal\b)",
    re.IGNORECASE,
)

PER_METRO = 8


def metro_blocked(label: str, title: str) -> bool:
    """Per-metro false-positive guard: the title names a DIFFERENT place
    that shares the metro's name. San Jose, CA vs San José, Costa Rica —
    on 2026-10-13 five Costa Rica embassy stories flooded the San Jose
    bucket because "San Jose" matched with no disambiguation (Washington
    and Portland already had context guards; San Jose was missed)."""
    if label == "San Jose, CA":
        t = title.lower()
        if "costa rica" in t:
            return True
        # Costa Rica's capital is spelled "San José" (accented); the
        # California city is written unaccented in US outlets. Allow the
        # accented form only with explicit California context.
        if "san josé" in t and not any(
            k in t for k in ("california", "silicon valley", "bay area")
        ):
            return True
    if label == "Edison, NJ":
        # "Thomas Edison" is the inventor, not the township — Musk
        # headlines ("the Thomas Edison of our time") match \bEdison\b.
        if "thomas edison" in title.lower():
            return True
    if label == "Dublin, CA":
        # Dublin, Ireland is the far bigger "Dublin" in news. Hard
        # Ireland markers block it; bare "Irish" is allowed (Dublin CA
        # trades on Irish heritage). RSS queries use "Dublin California"
        # to bias Google the same way.
        t = title.lower()
        if any(k in t for k in ("ireland", "dáil", "tánaiste", "garda")):
            return True
    return False


# Metros whose RSS coverage needs more than one query city. Dublin pools
# the whole Tri-Valley; each returned item must still name one of the
# pooled cities in its title (the label's pattern includes the aliases).
METRO_QUERY_CITIES = {
    "Dublin, CA": ["Dublin California", "San Ramon", "Pleasanton", "Livermore"],
}


_TITLE_STOPWORDS = {
    "the", "a", "an", "of", "in", "on", "to", "for", "and", "or", "as",
    "at", "by", "with", "from", "is", "are", "was", "were", "it", "its",
}


def _title_tokens(t: str) -> set:
    return set(re.findall(r"[a-z0-9]+", (t or "").lower())) - _TITLE_STOPWORDS


def titles_too_similar(a: str, b: str) -> bool:
    """Near-duplicate headline check (same wire story, different outlets).
    Jaccard on significant tokens; 0.55 catches reworded variants like
    '...strengthen bilateral ties' vs '...strengthen Central American ties'
    while leaving distinct stories alone."""
    ta, tb = _title_tokens(a), _title_tokens(b)
    if len(ta) < 4 or len(tb) < 4:
        return False
    return len(ta & tb) / len(ta | tb) >= 0.55

# --- V2: Google News RSS ---
# Google offers no official local-news API; the RSS search endpoint is free,
# keyless, and stable. Query biases toward desi topics; the drop-filter below
# removes Native American "Indian" noise (tribal, powwow, casinos...).
GNEWS_RSS = "https://news.google.com/rss/search"
GNEWS_QUERY_TMPL = (
    '{city} (desi OR "Indian-American" OR "Indian American" OR Diwali '
    'OR Holi OR Navratri OR "H-1B" OR "Indian diaspora" OR '
    '"Indian community") when:{days}d'
)
RSS_DROP_RX = re.compile(
    r"\b(tribal|powwow|casino|reservation|tribe\b|native american|"
    r"indian health|chief\b|wampanoag|cherokee|navajo|sioux)\b",
    re.IGNORECASE,
)
RSS_KEEP_RX = re.compile(
    r"\b(desi|india|indian-american|indian american|diwali|holi|navratri|"
    r"dussehra|h-1b|h1b|bollywood|cricket|dandiya|garba|bhangra|"
    r"punjabi|gujarati|telugu|tamil|malayalam|kannada|bengali|marathi|"
    r"rupee|rs\.?\s|nri|oci|samosa|biryani|"
    # Core diaspora vocabulary the original list missed — "green card"
    # stories are local-news staples (e.g. Patch's Edison IT-firms story
    # was dropped for having no keep keyword, 2026-10-13). Safe to widen
    # because every item must ALSO name the metro in its title.
    r"green card|perm\b|visa|immigration|temple|mandir|gurdwara)\b",
    re.IGNORECASE,
)
RSS_DELAY_S = 2

STATE_NAMES = {
    "NY": "New York", "CA": "California", "IL": "Illinois", "TX": "Texas",
    "WA": "Washington", "MA": "Massachusetts", "GA": "Georgia", "DC": "Washington DC",
    "NJ": "New Jersey", "PA": "Pennsylvania", "FL": "Florida", "CO": "Colorado",
    "AZ": "Arizona", "MN": "Minnesota", "MI": "Michigan", "OR": "Oregon",
    "OH": "Ohio", "NC": "North Carolina", "NV": "Nevada",
}


def compile_patterns():
    compiled = []
    for city, state, aliases in METROS:
        pats = [city] + aliases
        if city == "Washington":
            # "Washington" alone is ambiguous (DC vs state) — require DC context
            rx = re.compile(
                r"\bWashington(?:,?\s+D\.?C\.?|\s+DC\b)|\bD\.?C\.?\b.*\bWashington\b",
                re.IGNORECASE,
            )
        elif city == "Portland":
            # Portland OR vs ME — require Oregon context
            rx = re.compile(
                r"\bPortland\b(?=.{0,60}\b(?:Oregon|\bOR\b))|(?:Oregon|\bOR\b).{0,60}\bPortland\b",
                re.IGNORECASE,
            )
        elif city == "Dublin":
            # Dublin CA vs Dublin, Ireland: the pooled Tri-Valley city
            # names are unambiguous and match freely; bare "Dublin"
            # requires California context nearby (2026-10-13: a United
            # Europe-routes article, a Trinity College Dublin study, and
            # a "London, Dublin" protest line all matched Ireland's).
            rx = re.compile(
                r"\b(?:San Ramon|Pleasanton|Livermore|Tri-Valley)\b"
                r"|\bDublin,\s*CA\b"
                r"|\bDublin\b(?=.{0,80}\b(?:California|Bay Area|East Bay|Tri-Valley|Alameda|Contra Costa)\b)"
                r"|\b(?:California|Bay Area|East Bay|Tri-Valley|Alameda|Contra Costa)\b.{0,80}\bDublin\b",
                re.IGNORECASE,
            )
        else:
            alt = "|".join(re.escape(p) for p in pats)
            rx = re.compile(r"\b(?:" + alt + r")\b", re.IGNORECASE)
        compiled.append((f"{city}, {state}", rx))
    return compiled


def fetch_gnews_rss(
    city: str,
    days: int = 14,
    state: str | None = None,
    label: str | None = None,
    rx: re.Pattern | None = None,
) -> list[dict]:
    """Fetch Google News RSS for a metro, filtered for desi relevance."""
    place = f"{city} {state}" if state else city
    q = GNEWS_QUERY_TMPL.format(city=city, days=days)
    if state:
        # state-level fallback: e.g. "Oregon (desi OR ...) when:30d"
        q = GNEWS_QUERY_TMPL.format(city=state, days=days)
    params = urllib.parse.urlencode(
        {"q": q, "hl": "en-US", "gl": "US", "ceid": "US:en"}
    )
    url = f"{GNEWS_RSS}?{params}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            raw = resp.read()
    except Exception as e:
        print(f"  [rss] {city}: fetch failed ({e})", flush=True)
        return []
    try:
        root = ET.fromstring(raw)
    except Exception:
        print(f"  [rss] {city}: parse failed", flush=True)
        return []
    items = []
    seen = set()
    for it in root.find("channel").findall("item"):
        title_el = it.find("title")
        link_el = it.find("link")
        if title_el is None or link_el is None:
            continue
        # Google News titles look like "Headline - SourceName"
        full = (title_el.text or "").strip()
        title = re.sub(r"\s+-\s+[^-]+$", "", full).strip() or full
        link = (link_el.text or "").strip()
        if not title or not link or link in seen:
            continue
        seen.add(link)
        # relevance filter: drop Native-American noise, keep desi topics
        if RSS_DROP_RX.search(title):
            continue
        if not RSS_KEEP_RX.search(title):
            continue
        # The query alone is NOT proof the story is about this metro —
        # Google matched Costa Rica's San José to San Jose, CA. Require
        # the same title match (+ same-name-place guard) as own articles:
        # if a story is really about the metro, the metro is in the title.
        if rx is not None and not rx.search(title):
            continue
        if label and metro_blocked(label, title):
            continue
        src_el = it.find("source")
        src_name = (src_el.text or "").strip() if src_el is not None else ""
        src_url = (src_el.get("url") or "").strip() if src_el is not None else ""
        pub_el = it.find("pubDate")
        pub = ""
        if pub_el is not None and pub_el.text:
            try:
                pub = parsedate_to_datetime(pub_el.text).astimezone(timezone.utc).isoformat()
            except Exception:
                pub = ""
        items.append(
            {
                "kind": "rss",
                "title": title,
                "url": link,
                "domain": urllib.parse.urlparse(src_url).netloc.lower() or None,
                "source": src_name,
                "published_at": pub,
            }
        )
    return items


def main():
    no_rss = "--no-rss" in sys.argv
    patterns = compile_patterns()
    matches: dict[str, list[dict]] = {label: [] for label, _ in patterns}

    files = [f for f in os.listdir(ARTICLES_DIR) if f.endswith(".json")]
    scanned = 0
    for fn in files:
        try:
            with open(os.path.join(ARTICLES_DIR, fn), encoding="utf-8") as fh:
                a = json.load(fh)
        except Exception:
            continue
        if a.get("status") != "published":
            continue
        scanned += 1
        hay_headline = f"{a.get('title') or ''} {a.get('excerpt') or ''}"
        if len(hay_headline) < 20:
            continue
        # skip institutional false positives ("New York Fed" != New York the place)
        if EXCLUDE_RX.search(hay_headline):
            continue
        for label, rx in patterns:
            # Only title/excerpt matches: if a story is really about the metro,
            # the metro is in the headline or dek. Body-only mentions are
            # overwhelmingly passing references ("NY Fed", "NYSE").
            if rx.search(hay_headline) and not metro_blocked(label, hay_headline):
                matches[label].append(
                    {
                        "kind": "article",
                        "slug": a.get("slug"),
                        "title": a.get("title"),
                        "excerpt": a.get("excerpt") or "",
                        "published_at": a.get("published_at") or "",
                        "hero_image_url": a.get("hero_image_url") or "",
                        "category": a.get("category") or "",
                    }
                )

    # V2: Google News RSS per metro (external breadth)
    rss_counts: dict[str, int] = {}
    rx_by_label = dict(patterns)
    if not no_rss:
        for city, state, _aliases in METROS:
            label = f"{city}, {state}"
            query_cities = METRO_QUERY_CITIES.get(label, [city])
            rss_items: list[dict] = []
            seen_links: set = set()
            for qi, qcity in enumerate(query_cities):
                if qi:
                    time.sleep(RSS_DELAY_S)
                for r in fetch_gnews_rss(qcity, label=label, rx=rx_by_label[label]):
                    if r["url"] not in seen_links:
                        seen_links.add(r["url"])
                        rss_items.append(r)
            # dedup against our own titles (case-insensitive containment)
            own_titles = {i["title"].lower() for i in matches[label]}
            fresh = [
                r
                for r in rss_items
                if r["title"].lower() not in own_titles
                and not any(
                    r["title"].lower() in t or t in r["title"].lower()
                    for t in own_titles
                )
            ]
            # Fallback for thin metros: wider window + state-level query.
            # "Right and complete" means no metro left empty or single-item.
            if len(matches[label]) + len(fresh) < 3 and state in STATE_NAMES:
                time.sleep(RSS_DELAY_S)
                wide = fetch_gnews_rss(
                    city, days=30, state=STATE_NAMES[state],
                    label=label, rx=rx_by_label[label],
                )
                have_titles = own_titles | {r["title"].lower() for r in fresh}
                for r in wide:
                    tl = r["title"].lower()
                    if tl not in have_titles and not any(
                        tl in t or t in tl for t in have_titles
                    ):
                        fresh.append(r)
                        have_titles.add(tl)
                print(f"  [rss] {label}: fallback wide+state added", flush=True)
            matches[label].extend(fresh)
            rss_counts[label] = len(fresh)
            print(f"  [rss] {label}: {len(fresh)} kept", flush=True)
            time.sleep(RSS_DELAY_S)

    # keep PER_METRO most recent per metro (our articles first on ties)
    out = {}
    total = 0
    for label, items in matches.items():
        items = [i for i in items if i.get("slug") or i.get("url")]
        items.sort(
            key=lambda x: (
                x["published_at"],
                0 if x.get("kind") == "article" else 1,
            ),
            reverse=True,
        )
        # Cross-source near-dedup: the same wire story from 4 outlets is
        # ONE local story, not 4 slots (2026-10-13 Costa Rica flood).
        deduped: list[dict] = []
        for it in items:
            if any(
                titles_too_similar(it.get("title") or "", k.get("title") or "")
                for k in deduped
            ):
                continue
            deduped.append(it)
        out[label] = deduped[:PER_METRO]
        total += len(out[label])

    payload = {
        "built_at": datetime.now(timezone.utc).isoformat(),
        "metros": out,
    }
    with open(OUT_PATH, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False)
    print(f"scanned={scanned} metros={len(out)} total_matches={total} -> {OUT_PATH}")

    # coverage summary
    empty = [label for label, items in out.items() if not items]
    print(f"metros_with_news={len(out) - len(empty)}/{len(out)}")
    if empty:
        print("empty: " + ", ".join(empty))


if __name__ == "__main__":
    sys.exit(main())

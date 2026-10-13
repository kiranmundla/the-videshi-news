#!/usr/bin/env python3 -u
"""Build per-cluster local news index for Your Hub.

V1: scans published article JSONs for cluster mentions (city name in
title/excerpt) — our own voice, precise, thin volume.
V2: Google News RSS per cluster with a desi query + relevance filter —
external breadth. Merged: our articles first, RSS fills up to PER_METRO.

Clusters come from public/data/clusters.json — the ONE canonical table
(ACS 2024 diaspora clusters; see research/diaspora-suburb-clusters-plan-
2026-10-13.md). The frontend fetches the same file for its picker; there
is no second hand list to drift. Each cluster declares its query cities,
title-match aliases, blocklist regexes, and an optional context-guard
profile for same-name places (San Jose vs Costa Rica, Dublin CA vs
Ireland vs Dublin OH, Portland OR vs ME, Washington DC, Fishers IN).

Writes public/data/local-news.json:
  { "metros": { "San Jose, CA": [{kind,slug|url,title,...}, ...] } }
(key stays "metros" — the frontend's LocalNewsItem contract.)

Top PER_METRO most recent per cluster. Both layers must match a cluster
name in the TITLE — a Google query hit alone is not proof a story is
about the place — and near-identical headlines across outlets are
deduped to one slot.

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
CLUSTERS_PATH = os.path.join(REPO, "public", "data", "clusters.json")

# Institutional uses of city names that are NOT local news
# ("New York Fed" is a bank, not the city)
EXCLUDE_RX = re.compile(
    r"\b(new york fed|federal reserve bank of new york|new york times\b|"
    r"\bnyt\b|new york stock exchange\b|\bnyse\b|wall street journal\b)",
    re.IGNORECASE,
)

PER_METRO = 8

# ---------------------------------------------------------------------------
# Context-guard profiles: title patterns for names that are ambiguous on
# their own. The cluster's plain aliases always match freely; the profile
# adds the guarded name with its required context.
# ---------------------------------------------------------------------------

# "Washington" alone is ambiguous (DC vs state) — require DC context
_WASHINGTON_RX = (
    r"\bWashington(?:,?\s+D\.?C\.?|\s+DC\b)|\bD\.?C\.?\b.*\bWashington\b"
)
# Portland OR vs ME — require Oregon context
_PORTLAND_RX = (
    r"\bPortland\b(?=.{0,60}\b(?:Oregon|\bOR\b))|(?:Oregon|\bOR\b).{0,60}\bPortland\b"
)
_CA_CONTEXT = r"(?:California|Bay Area|East Bay|Tri-Valley|Alameda|Contra Costa)"
# Dublin CA vs Dublin, Ireland (and Dublin, OH): bare "Dublin" requires
# California context nearby (2026-10-13: a United Europe-routes article,
# a Trinity College Dublin study, and a "London, Dublin" protest line all
# matched Ireland's capital).
_DUBLIN_CA_RX = (
    r"\bDublin,\s*CA\b"
    r"|\bDublin\b(?=.{0,80}\b" + _CA_CONTEXT + r"\b)"
    r"|\b" + _CA_CONTEXT + r"\b.{0,80}\bDublin\b"
)
# Dublin OH (Columbus bucket): mirror image — bare "Dublin" requires Ohio
# context. The two Dublins can therefore never cross-match: each demands
# its own state's context, and cluster_blocked() rejects the other's.
_DUBLIN_OH_RX = (
    r"\bDublin,\s*OH\b"
    r"|\bDublin\b(?=.{0,80}\b(?:Ohio|Columbus|\bOH\b))"
    r"|\b(?:Ohio|Columbus)\b.{0,80}\bDublin\b"
)
# Fishers, IN vs "fishers" the occupation: the town matches at title
# start, after in/at/near, or with Indiana context nearby. The occupation
# ("What Changes for Fishers") is blocked in cluster_blocked().
_FISHERS_RX = (
    r"^\s*Fishers\b"
    r"|\b(?:in|at|near)\s+Fishers\b"
    r"|\bFishers\b(?=.{0,60}\b(?:Indiana|Indianapolis|Carmel|Hamilton County|\bIN\b))"
    r"|\b(?:Indiana|Indianapolis|Carmel|Hamilton County)\b.{0,60}\bFishers\b"
)

_PROFILE_RX = {
    "washington_dc": _WASHINGTON_RX,
    "portland_or": _PORTLAND_RX,
    "dublin_ca": _DUBLIN_CA_RX,
    "dublin_oh": _DUBLIN_OH_RX,
    "fishers_in": _FISHERS_RX,
    # san_jose / orange_county profiles affect blocking only (below);
    # their names match plainly.
}


def load_clusters() -> list[dict]:
    with open(CLUSTERS_PATH, encoding="utf-8") as fh:
        return json.load(fh)["clusters"]


def compile_cluster_pattern(cluster: dict) -> re.Pattern:
    """Title-match pattern: plain aliases + the guard profile's pattern."""
    parts = []
    aliases = cluster.get("aliases") or []
    if aliases:
        alt = "|".join(re.escape(a) for a in aliases)
        parts.append(r"\b(?:" + alt + r")\b")
    profile = cluster.get("context_guard")
    if profile in _PROFILE_RX:
        parts.append(_PROFILE_RX[profile])
    return re.compile("|".join(parts), re.IGNORECASE)


def cluster_blocked(cluster: dict, text: str) -> bool:
    """False-positive guard: the text names a DIFFERENT place that shares
    the cluster's name, or a namesake trap declared in the table."""
    t = text.lower()
    for pat in cluster.get("block") or []:
        if re.search(pat, text, re.IGNORECASE):
            return True
    profile = cluster.get("context_guard")
    if profile == "san_jose":
        # Costa Rica's capital is spelled "San José" (accented); the
        # California city is written unaccented in US outlets. Allow the
        # accented form only with explicit California context.
        if "san josé" in t and not any(
            k in t for k in ("california", "silicon valley", "bay area")
        ):
            return True
    elif profile == "dublin_ca":
        # A "Dublin" story with Ohio context belongs to Columbus's Dublin.
        if re.search(r"\bdublin\b", t) and ("ohio" in t or "columbus" in t):
            return True
    elif profile == "dublin_oh":
        # Mirror: a "Dublin" story with California context is Dublin, CA.
        if re.search(r"\bdublin\b", t) and any(
            k in t
            for k in ("california", "bay area", "tri-valley", "san ramon",
                      "pleasanton", "livermore", "silicon valley")
        ):
            return True
    elif profile == "orange_county":
        # "Orange County" also names counties in FL (Orlando) and NC
        # (Chapel Hill). Only blocks when the match is the county name
        # itself — an Irvine story mentioning Florida is unaffected
        # unless it also says "Orange County".
        if "orange county" in t and any(
            k in t for k in ("florida", "orlando", "chapel hill",
                              "north carolina")
        ):
            return True
    elif profile == "fishers_in":
        # "fishers" the occupation: preceded by "for", or in a
        # fishing-industry context. Scoped to titles naming Fishers.
        if "fishers" in t and (
            re.search(r"\bfor fishers\b", t)
            or any(k in t for k in ("fishing", "fishermen", "fisheries",
                                    "deep-sea", "deep sea"))
        ):
            return True
    return False


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
    # because every item must ALSO name the cluster in its title.
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
    "VA": "Virginia", "MD": "Maryland", "IN": "Indiana",
    "WI": "Wisconsin", "MO": "Missouri",
}


def fetch_gnews_rss(
    city: str,
    days: int = 14,
    state: str | None = None,
    cluster: dict | None = None,
    rx: re.Pattern | None = None,
) -> list[dict]:
    """Fetch Google News RSS for one query city, filtered for desi
    relevance and gated on the cluster's title pattern + blocklist."""
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
        # The query alone is NOT proof the story is about this cluster —
        # Google matched Costa Rica's San José to San Jose, CA. Require
        # the same title match (+ same-name-place guard) as own articles:
        # if a story is really about the place, the place is in the title.
        if rx is not None and not rx.search(title):
            continue
        if cluster is not None and cluster_blocked(cluster, title):
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
    clusters = load_clusters()
    compiled = [(c, compile_cluster_pattern(c)) for c in clusters]
    matches: dict[str, list[dict]] = {c["label"]: [] for c in clusters}

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
        for cluster, rx in compiled:
            # Only title/excerpt matches: if a story is really about the
            # place, the place is in the headline or dek. Body-only
            # mentions are overwhelmingly passing references ("NY Fed").
            if rx.search(hay_headline) and not cluster_blocked(cluster, hay_headline):
                matches[cluster["label"]].append(
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

    # V2: Google News RSS per cluster (external breadth), pooling the
    # cluster's query cities. Each item must still name the cluster in
    # its title (the pattern includes every pooled city + aliases).
    rss_counts: dict[str, int] = {}
    if not no_rss:
        for cluster, rx in compiled:
            label = cluster["label"]
            rss_items: list[dict] = []
            seen_links: set = set()
            for qi, qcity in enumerate(cluster["query_cities"]):
                if qi:
                    time.sleep(RSS_DELAY_S)
                for r in fetch_gnews_rss(qcity, cluster=cluster, rx=rx):
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
            # Fallback for thin clusters: wider window + state-level query.
            # "Right and complete" means no cluster left empty or single-item.
            state = cluster["state"]
            if len(matches[label]) + len(fresh) < 3 and state in STATE_NAMES:
                time.sleep(RSS_DELAY_S)
                wide = fetch_gnews_rss(
                    cluster["anchor"], days=30, state=STATE_NAMES[state],
                    cluster=cluster, rx=rx,
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

    # keep PER_METRO most recent per cluster (our articles first on ties)
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
    print(f"scanned={scanned} clusters={len(out)} total_matches={total} -> {OUT_PATH}")

    # coverage summary
    empty = [label for label, items in out.items() if not items]
    print(f"clusters_with_news={len(out) - len(empty)}/{len(out)}")
    if empty:
        print("empty: " + ", ".join(empty))


if __name__ == "__main__":
    sys.exit(main())

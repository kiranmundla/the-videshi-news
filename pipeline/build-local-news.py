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

Fetches run as curl subprocesses with hard whole-transfer timeouts,
under a per-cluster and a global RSS budget; a cluster whose fetch
phase doesn't complete keeps its RSS items from the previous output
(carry-over), and an early own-articles write lands before the RSS
phase — a slow or killed run degrades, it never vanishes (2026-10-15).

Run: python3 -u pipeline/build-local-news.py [--no-rss]
"""
import json
import os
import re
import subprocess
import sys
import time
import urllib.parse
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
# Raleigh, NC: two of its pooled names are traps on their own. "Durham"
# is also the English county-cricket side (Ben Stokes' Durham matched
# Raleigh in the 2026-10-14 audit), and "Apex" is a common English word
# ("the apex court" — a Kerala Waqf story matched via its excerpt).
# Neither stays a plain alias in clusters.json; both match only with
# North Carolina context nearby (or as the Durham Bulls, the NC team).
_NC_CONTEXT = r"(?:North Carolina|Raleigh|Cary|Morrisville|Research Triangle|\bNC\b)"
_RALEIGH_NC_RX = (
    r"\bDurham,?\s+(?:NC|N\.C\.)\b"
    r"|\bDurham Bulls\b"
    r"|\bDurham\b(?=.{0,60}\b" + _NC_CONTEXT + r"\b)"
    r"|\b" + _NC_CONTEXT + r"\b.{0,60}\bDurham\b"
    r"|\bApex,?\s+(?:NC|N\.C\.)\b"
    r"|\bApex\b(?=.{0,60}\b" + _NC_CONTEXT + r"\b)"
    r"|\b" + _NC_CONTEXT + r"\b.{0,60}\bApex\b"
)

# Corona, CA (Orange County cluster member, actually Riverside County):
# bare "Corona" is a trap — Corona Park in Queens, NY (Flushing Meadows)
# filed a Queens Diwali festival as Orange County news in the 2026-10-28
# audit, and the word also appears for the beer and the virus. Like
# Durham/Apex for Raleigh, it leaves the plain aliases in clusters.json
# and matches only with California / Orange County context nearby.
_CORONA_CA_RX = (
    r"\bCorona,?\s+(?:CA|Calif\.)\b"
    r"|\bCorona\b(?=.{0,60}\b(?:California|Orange County|Riverside|Anaheim|Yorba Linda)\b)"
    r"|\b(?:California|Orange County|Riverside)\b.{0,60}\bCorona\b"
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
    "raleigh_nc": _RALEIGH_NC_RX,
    "fishers_in": _FISHERS_RX,
    # orange_county: the profile pattern adds guarded "Corona" (above);
    # the cluster's other names match plainly, and cluster_blocked()
    # still rejects FL/NC "Orange County" namesakes.
    "orange_county": _CORONA_CA_RX,
    # san_jose profile affects blocking only (below); its names match
    # plainly.
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

# --- Fetch hardening (2026-10-15) -------------------------------------
# The 2026-10-15 06:15 enricher run lost its local-news refresh: 196+
# sequential RSS fetches, each bounded only by urllib's 20s
# per-socket-op timeout, no per-cluster or global budget, and output
# written only at the very end. Even healthy, the RSS phase takes
# ~12 min (measured); under proxy/Google latency it crawls past the
# caller's patience (~20 of 47 clusters), gets killed, and — writing
# nothing until the end — leaves the previous file untouched.
# Budgets below bound the worst case: RSS phase <= GLOBAL_RSS_BUDGET_S,
# any one cluster <= CLUSTER_RSS_BUDGET_S, any one fetch <=
# FETCH_MAX_TIME_S end to end (curl --max-time, not per-op).
FETCH_CONNECT_TIMEOUT_S = 10
FETCH_MAX_TIME_S = 15
CLUSTER_RSS_BUDGET_S = 90
GLOBAL_RSS_BUDGET_S = 900

STATE_NAMES = {
    "NY": "New York", "CA": "California", "IL": "Illinois", "TX": "Texas",
    "WA": "Washington", "MA": "Massachusetts", "GA": "Georgia", "DC": "Washington DC",
    "NJ": "New Jersey", "PA": "Pennsylvania", "FL": "Florida", "CO": "Colorado",
    "AZ": "Arizona", "MN": "Minnesota", "MI": "Michigan", "OR": "Oregon",
    "OH": "Ohio", "NC": "North Carolina", "NV": "Nevada",
    "VA": "Virginia", "MD": "Maryland", "IN": "Indiana",
    "WI": "Wisconsin", "MO": "Missouri",
}


def _fetch_bytes(url: str, max_time: int) -> bytes:
    """GET via curl subprocess with a hard whole-transfer deadline.

    Pipeline convention is curl for external fetches: urllib/requests
    are unreliable through this proxy, and urllib's timeout bounds each
    socket operation — not the whole transfer — so a slow response can
    hold the run hostage far past the nominal timeout. curl's
    --max-time bounds connect + transfer end to end. Raises on failure.
    """
    proc = subprocess.run(
        [
            "curl", "-sS", "--fail",
            "--connect-timeout", str(FETCH_CONNECT_TIMEOUT_S),
            "--max-time", str(max_time),
            "-A", "Mozilla/5.0",
            url,
        ],
        capture_output=True,
        timeout=max_time + 15,
    )
    if proc.returncode != 0:
        err = (proc.stderr or b"").decode("utf-8", "replace").strip().splitlines()
        raise RuntimeError(err[0] if err else f"curl exit {proc.returncode}")
    return proc.stdout


def fetch_gnews_rss(
    city: str,
    days: int = 14,
    state: str | None = None,
    cluster: dict | None = None,
    rx: re.Pattern | None = None,
    max_time: int = FETCH_MAX_TIME_S,
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
    try:
        raw = _fetch_bytes(url, max_time)
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


def load_previous_rss() -> dict[str, list[dict]]:
    """The previous output's RSS items per cluster label — the
    carry-over source for clusters whose fetch phase doesn't complete
    this run. Own articles are NOT carried: the article scan is
    authoritative and re-derived every run."""
    try:
        with open(OUT_PATH, encoding="utf-8") as fh:
            metros = json.load(fh).get("metros") or {}
    except Exception:
        return {}
    return {
        label: [i for i in items if i.get("kind") == "rss"]
        for label, items in metros.items()
    }


def shape_output(
    matches: dict[str, list[dict]],
    rss_fresh: dict[str, list[dict]],
    rss_done: set,
    carried_rss: dict[str, list[dict]],
) -> tuple[dict, int]:
    """Merge own articles with RSS per cluster — fresh RSS where the
    cluster's fetch phase completed, carried-over RSS where it didn't —
    and shape to the PER_METRO most recent. Returns (out, total)."""
    merged = {}
    for label, own_items in matches.items():
        rss_items = (
            rss_fresh.get(label, [])
            if label in rss_done
            else carried_rss.get(label, [])
        )
        merged[label] = list(own_items) + list(rss_items)

    # keep PER_METRO most recent per cluster (our articles first on ties)
    out = {}
    total = 0
    # Recency caps (2026-10-14 audit): the article scan had NO age window,
    # so any old article naming a place stayed in its bucket forever —
    # median bucket age was 26.5 days and a 93-day-old story was still
    # being presented as Fremont local news. RSS is windowed at fetch
    # (14d; 30d fallback), so cap rss at 30d and our articles at 45d here,
    # at the single choke point. Undated items are kept (can't prove stale).
    _now = datetime.now(timezone.utc)
    _CAPS = {"rss": 30, "article": 45}
    def _too_old(i: dict) -> bool:
        raw = i.get("published_at") or ""
        try:
            dt = datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
        except Exception:
            return False
        return (_now - dt).days > _CAPS.get(i.get("kind") or "", 45)
    for label, items in merged.items():
        items = [i for i in items
                 if (i.get("slug") or i.get("url")) and not _too_old(i)]
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
    return out, total


def write_output(out: dict) -> None:
    """Atomic write: a kill mid-write must never leave a truncated
    local-news.json behind."""
    payload = {
        "built_at": datetime.now(timezone.utc).isoformat(),
        "metros": out,
    }
    tmp_path = OUT_PATH + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False)
    os.replace(tmp_path, OUT_PATH)


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
    # A cluster's RSS counts as refreshed only if its whole fetch phase
    # completes inside the budgets; otherwise its previous RSS items
    # carry over (see shape_output) instead of the cluster going stale
    # or the run stalling.
    carried_rss: dict[str, list[dict]] = {} if no_rss else load_previous_rss()
    rss_fresh: dict[str, list[dict]] = {}
    rss_done: set = set()
    rss_counts: dict[str, int] = {}
    if not no_rss:
        # Early write (own articles + carried-over RSS): if this
        # process is killed during the slow RSS phase, the file on disk
        # is still a valid refresh, not last run's stale copy.
        _early_out, _ = shape_output(matches, rss_fresh, rss_done, carried_rss)
        write_output(_early_out)
        print(
            "[local-news] early write done (own articles + carried-over "
            "RSS); fetching fresh RSS…",
            flush=True,
        )

        rss_started = time.monotonic()
        for cluster, rx in compiled:
            label = cluster["label"]
            if time.monotonic() - rss_started > GLOBAL_RSS_BUDGET_S:
                print(
                    f"  [rss] {label}: skipped — global RSS budget "
                    f"({GLOBAL_RSS_BUDGET_S}s) exhausted; previous RSS "
                    "carried over",
                    flush=True,
                )
                continue
            cluster_started = time.monotonic()
            try:
                rss_items: list[dict] = []
                seen_links: set = set()
                budget_hit = False
                for qi, qcity in enumerate(cluster["query_cities"]):
                    if qi:
                        time.sleep(RSS_DELAY_S)
                    left = CLUSTER_RSS_BUDGET_S - (
                        time.monotonic() - cluster_started
                    )
                    if left <= 2:
                        budget_hit = True
                        break
                    mt = max(3, min(FETCH_MAX_TIME_S, int(left)))
                    for r in fetch_gnews_rss(
                        qcity, cluster=cluster, rx=rx, max_time=mt
                    ):
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
                # Fallback for thin clusters: wider window + state-level
                # query. "Right and complete" means no cluster left empty
                # or single-item — but only while budget remains.
                state = cluster["state"]
                left = CLUSTER_RSS_BUDGET_S - (
                    time.monotonic() - cluster_started
                )
                if (
                    not budget_hit
                    and len(matches[label]) + len(fresh) < 3
                    and state in STATE_NAMES
                    and left > 2
                    and time.monotonic() - rss_started <= GLOBAL_RSS_BUDGET_S
                ):
                    time.sleep(RSS_DELAY_S)
                    wide = fetch_gnews_rss(
                        cluster["anchor"], days=30, state=STATE_NAMES[state],
                        cluster=cluster, rx=rx,
                        max_time=max(3, min(FETCH_MAX_TIME_S, int(left))),
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
                if budget_hit:
                    print(
                        f"  [rss] {label}: cluster RSS budget "
                        f"({CLUSTER_RSS_BUDGET_S}s) exhausted — previous "
                        "RSS carried over",
                        flush=True,
                    )
                else:
                    rss_fresh[label] = fresh
                    rss_done.add(label)
                    rss_counts[label] = len(fresh)
                    print(f"  [rss] {label}: {len(fresh)} kept", flush=True)
            except Exception as e:
                print(
                    f"  [rss] {label}: cluster failed ({e}) — previous "
                    "RSS carried over",
                    flush=True,
                )
            time.sleep(RSS_DELAY_S)

    out, total = shape_output(matches, rss_fresh, rss_done, carried_rss)
    write_output(out)
    print(f"scanned={scanned} clusters={len(out)} total_matches={total} -> {OUT_PATH}")

    # coverage summary
    empty = [label for label, items in out.items() if not items]
    print(f"clusters_with_news={len(out) - len(empty)}/{len(out)}")
    if empty:
        print("empty: " + ", ".join(empty))
    if not no_rss:
        carried = [c["label"] for c in clusters if c["label"] not in rss_done]
        if carried:
            print(
                f"rss_carried_over={len(carried)}: " + ", ".join(carried))


if __name__ == "__main__":
    sys.exit(main())

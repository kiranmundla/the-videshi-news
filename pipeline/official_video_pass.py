#!/usr/bin/env python3
"""Official-video embed pass — channel-scoped, gate-first YouTube enrichment.

Built 2026-10-22 (Kiran's embeds-and-actual-pictures push, the night the
SQUASHTV highlight was embedded by hand into the Anahat Singh article).

WHY THIS EXISTS
    enrich_youtube() in enrich-on-publish.py searches YouTube globally and
    gates the results. That works for trailers and big entities, but it
    cannot reliably attribute *event highlights* to the rights holder:
    a global search for a squash match returns fan uploads, betting clips
    and re-uploads alongside the official one, and channel authority in
    the shared scorer is a signal, not proof. This pass inverts the flow:

      1. Map the article to a rights holder on the OFFICIAL-CHANNEL
         ALLOWLIST (official-video-channels.json + trailer-channels.json).
      2. Search ONLY inside that channel (YouTube API channelId scope).
      3. Gate every candidate: verified channel identity, the shared
         embed_placement.youtube_embed_accept gate, a strong title match
         (a named person from the headline AND a non-person event word
         must appear in the video title), and a recency window around
         the article date.
      4. Insert <youtube>VIDEO_ID</youtube> after the first body
         paragraph (the placement used for the manual Anahat embed).

    A wrong embed is worse than none: every rejection is logged with a
    reason, and any doubt means no embed.

SAFETY / DEPLOY STATE (2026-10-22)
    - Default mode is DRY-RUN: no Supabase writes, ever, unless BOTH
      --apply is passed AND env VIDESHI_OFFICIAL_VIDEO_PASS_APPLY=1.
    - enrich-on-publish.py calls official_video_for_article() only when
      env VIDESHI_OFFICIAL_VIDEO_PASS=1 (default OFF) — the live cron
      is unchanged until Kiran approves enabling it.
    - YouTube access reuses the existing OAuth credentials in
      ~/workspace/.env.youtube (same refresh-token flow as
      enrich-on-publish.py's _get_youtube_access_token).

X-EMBED WIDENING (official_x_candidates)
    X discovery in the enricher is registry-only (match_handles against
    the social registry). Allowlist entries may carry the rights holder's
    official X handle; when an article maps to that rights holder, the
    handle becomes an additional candidate for the EXISTING machinery
    (_fetch_handle_tweets_live + find_best_tweet + verify_tweet in
    enrich-on-publish.py, inserted as a bare URL line that the frontend
    renders via react-tweet). No frontend work is needed — the
    SocialEmbeds contract already renders bare x.com status URLs and
    structured social_embeds entries.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from embed_placement import _content_words, youtube_embed_accept  # noqa: E402

ALLOWLIST_PATH = os.path.join(HERE, "official-video-channels.json")
TRAILER_CHANNELS_PATH = os.path.join(HERE, "trailer-channels.json")
STATE_DIR = os.path.join(HERE, ".state")

ELIGIBLE_CATEGORIES = {"sports", "entertainment"}
SEARCH_UNITS_PER_CALL = 100  # YouTube Data API search.list cost
MAX_SEARCHES_PER_RUN = 20
MAX_CHANNELS_PER_ARTICLE = 4   # cap on channels actually searched per article
MAX_QUERIES_PER_ARTICLE = 5    # cap on search queries built per article
RECENCY_BEFORE_DAYS = 14   # highlights may precede the write-up slightly
RECENCY_AFTER_DAYS = 2     # ...or land just after publication


# ─── Env / credentials ───────────────────────────────────────────────────────

def _load_env_file(path):
    env = {}
    try:
        with open(os.path.expanduser(path)) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    env[k.strip()] = v.strip()
    except FileNotFoundError:
        pass
    return env


_YT_TOKEN_CACHE = {"token": None}


def get_youtube_token():
    """OAuth access token via the .env.youtube refresh-token flow.

    Mirrors enrich-on-publish.py::_get_youtube_access_token. Returns None
    when credentials are missing or the exchange fails.
    """
    if _YT_TOKEN_CACHE["token"]:
        return _YT_TOKEN_CACHE["token"]
    env = _load_env_file("~/workspace/.env.youtube")
    cid, csec, rtok = (env.get("YOUTUBE_CLIENT_ID", ""),
                       env.get("YOUTUBE_CLIENT_SECRET", ""),
                       env.get("YOUTUBE_REFRESH_TOKEN", ""))
    if not (cid and csec and rtok):
        return None
    payload = json.dumps({"client_id": cid, "client_secret": csec,
                          "refresh_token": rtok, "grant_type": "refresh_token"})
    try:
        r = subprocess.run(
            ["curl", "-sS", "-X", "POST", "https://oauth2.googleapis.com/token",
             "-H", "Content-Type: application/json", "-d", payload],
            capture_output=True, text=True, timeout=15)
        token = json.loads(r.stdout).get("access_token")
    except Exception:
        return None
    _YT_TOKEN_CACHE["token"] = token
    return token


# ─── Allowlist ───────────────────────────────────────────────────────────────

def load_official_channels():
    """Allowlist entries: rights-holder JSON + trailer-channels.json merge.

    Every entry: {name, channel_id, domain, categories, match_terms,
    x_handle (optional), source}. Trailer channels keep their verified
    in-repo channel IDs and match on the studio name appearing in the
    article (their match_terms = the full channel name).
    """
    entries = []
    try:
        with open(ALLOWLIST_PATH) as f:
            for c in json.load(f).get("channels", []):
                entries.append({**c, "source": "official-video-channels.json"})
    except FileNotFoundError:
        pass
    try:
        with open(TRAILER_CHANNELS_PATH) as f:
            for c in json.load(f).get("channels", []):
                name = (c.get("name") or "").strip()
                if not name:
                    continue
                entries.append({
                    "name": name,
                    "channel_id": c.get("channel_id", ""),
                    "domain": "film",
                    "categories": ["entertainment"],
                    "match_terms": [name.lower()],
                    "x_handle": None,
                    "source": "trailer-channels.json",
                })
    except FileNotFoundError:
        pass
    return entries


def _name_fragments(name):
    """Multi-word fragments of a channel name ('New Zealand Cricket' ->
    {'new zealand', 'zealand cricket', 'new zealand cricket'}). A single
    generic word ('cricket') is never a fragment — it proves nothing."""
    words = (name or "").lower().split()
    frags = set()
    for i in range(len(words)):
        for j in range(i + 2, len(words) + 1):
            frags.add(" ".join(words[i:j]))
    return frags


def _channel_specificity(entry, matched_terms, headline_l, haystack):
    """Rank key for a mapped channel — more specific mappings first.

    A generic term like 'cricket' matches ~11 channels; without ranking
    the per-run search budget dies in file order before the article's
    actual rights holder is reached. Signals, strongest first:
      1. the channel itself is named in the headline
      2. a matched term is multi-word ('rugby league', 'world cup')
      3. a multi-word fragment of the channel name ('new zealand' from
         'New Zealand Cricket') appears in the headline
      4. ... or anywhere in the headline+body haystack
      5. the channel's domain word ('rugby league', 'kabaddi') is in
         the headline
      6. a matched term appears in the headline (not only the body)
      7. longest matched term, as a final tiebreak
    Ties keep allowlist file order (stable sort).
    """
    name_l = entry["name"].lower()
    frags = _name_fragments(entry["name"])
    domain = (entry.get("domain") or "").lower()
    return (
        name_l in headline_l,
        any(len(t.split()) > 1 for t in matched_terms),
        any(f in headline_l for f in frags),
        any(f in haystack for f in frags),
        bool(domain) and domain in headline_l,
        any(t in headline_l for t in matched_terms),
        max((len(t) for t in matched_terms), default=0),
    )


def channels_for_article(article, channels):
    """Rights holders this article plausibly belongs to, ranked by
    mapping specificity (see _channel_specificity). Returns [(entry, why)].

    Conservative by design: category must be eligible AND match — a
    match_term hit in headline/body, or the channel name itself named in
    the headline. No mapping, no search, no embed. The full ranked list
    is returned; callers that SEARCH cap themselves at
    MAX_CHANNELS_PER_ARTICLE (discovery users like official_x_candidates
    keep the whole list — handles cost nothing until apply time).
    """
    category = (article.get("category") or "").lower()
    if category not in ELIGIBLE_CATEGORIES:
        return []
    headline = (article.get("headline") or "")
    haystack = (headline + "\n" + (article.get("body") or "")[:2000]).lower()
    headline_l = headline.lower()
    scored = []
    for entry in channels:
        if category not in (entry.get("categories") or []):
            continue
        matched = [t for t in (entry.get("match_terms") or [])
                   if t and t in haystack]
        if matched:
            why = f"match_term '{matched[0]}'"
        elif entry["name"].lower() in headline_l:
            matched = [entry["name"].lower()]
            why = "channel named in headline"
        else:
            continue
        key = _channel_specificity(entry, matched, headline_l, haystack)
        scored.append((key, entry, why))
    scored.sort(key=lambda r: r[0], reverse=True)
    return [(entry, why) for _key, entry, why in scored]


# ─── People / event extraction (for the strong title match) ─────────────────

_CAP_SEQ_RE = re.compile(r"(?:[A-Z][a-zA-Z'’.-]+(?:\s+|$)){2,}")
_NON_PERSON_HEADS = {
    "the", "a", "an", "how", "why", "watch", "live", "breaking",
}
# Tokens that are event/filler words, never a surname — a capitalized
# sequence's last token is often one of these ("Silicon Valley Open",
# "World Champion") and must not become a name-match key on its own.
EVENT_STOPWORDS = {
    "open", "cup", "world", "championship", "championships", "tour",
    "grand", "slam", "series", "trophy", "league", "premier",
    "international", "national", "classic", "masters", "final", "finals",
    "champion", "champions", "time", "star", "stars", "gold", "silver",
    "bronze", "round", "leg", "day", "night",
}


def headline_people(headline):
    """Candidate person/event phrases from the headline.

    Headlines capitalize verbs and adjectives too ("Anahat Singh Stuns
    Eight-Time World Champion El Sherbini"), so a raw capitalized run is
    NOT a name. Names sit at the EDGES of those runs — the subject at
    the start, the opponent at the end — so take each run's first-two
    and last-two tokens as candidates ('Anahat Singh', 'El Sherbini'),
    plus the whole run when it is short (<=3 tokens, e.g. an event name
    like 'Silicon Valley Open'). Candidates feed the search query, the
    scorer's entity, and the strong-match name test; the event phrases
    among them only ever make the gate stricter.
    """
    names = []
    for m in _CAP_SEQ_RE.finditer(headline or ""):
        seq = m.group(0).strip(" -–—,.:")
        parts = seq.split()
        if len(parts) < 2:
            continue
        if parts[0].lower() in _NON_PERSON_HEADS:
            parts = parts[1:]
        if len(parts) < 2:
            continue
        candidates = [" ".join(parts[:2]), " ".join(parts[-2:])]
        if len(parts) <= 3:
            candidates.append(" ".join(parts))
        for cand in candidates:
            if cand not in names:
                names.append(cand)
    return names


def _name_variants(name):
    """Matchable forms of a name: full, surname, space-stripped surname,
    and space-stripped full name ('El Sherbini' -> 'elsherbini', which is
    how SQUASHTV titles render it: 'ElSherbini'). A surname that is an
    event/filler word ('Open', 'World') is NOT offered as a variant."""
    parts = name.split()
    variants = {name.lower()}
    if parts:
        surname = parts[-1].lower()
        if len(surname) >= 4 and surname not in EVENT_STOPWORDS:
            variants.add(surname)
        if len(parts) >= 2:
            last_two = " ".join(parts[-2:]).lower()
            variants.add(last_two)
            variants.add(last_two.replace(" ", ""))
        variants.add(name.lower().replace(" ", ""))
    return {v for v in variants if len(v) >= 4}


def _title_has_name(title, names):
    t = (title or "").lower()
    t_stripped = t.replace(" ", "")
    for name in names:
        for v in _name_variants(name):
            if " " in v:
                if v in t:
                    return name
            elif v in t or v in t_stripped:
                return name
    return None


# ─── YouTube channel-scoped search ───────────────────────────────────────────

def search_channel_videos(token, channel_id, query, max_results=6,
                          published_after=None, published_before=None):
    """YouTube Data API search scoped to ONE channel, via curl.

    Returns result dicts in the shared shape used by embed_placement
    ({videoId, title, channelTitle, channelId, publishedAt}).
    """
    if not token or not channel_id:
        return []
    args = ["curl", "-sS", "https://www.googleapis.com/youtube/v3/search",
            "-H", f"Authorization: Bearer {token}", "-G",
            "--data-urlencode", f"q={query}",
            "-d", "part=snippet", "-d", "type=video",
            "-d", f"channelId={channel_id}",
            "-d", f"maxResults={max_results}", "-d", "order=relevance",
            "-d", "relevanceLanguage=en"]
    if published_after:
        args += ["--data-urlencode", f"publishedAfter={published_after}"]
    if published_before:
        args += ["--data-urlencode", f"publishedBefore={published_before}"]
    try:
        r = subprocess.run(args, capture_output=True, text=True, timeout=20)
        data = json.loads(r.stdout)
    except Exception:
        return []
    if "error" in data:
        return []
    out = []
    for item in data.get("items", []):
        sn = item.get("snippet", {})
        out.append({
            "videoId": item.get("id", {}).get("videoId", ""),
            "title": sn.get("title", ""),
            "channelTitle": sn.get("channelTitle", ""),
            "channelId": sn.get("channelId", ""),
            "publishedAt": sn.get("publishedAt", ""),
        })
    return out


# Team/country names for team-match queries. headline_people() only
# emits multi-word capitalized runs, so a lone country name in a
# headline ('India Eye 2-0 Lead...') never becomes a phrase — and
# person-surname queries find only channel filler on team fixtures,
# whose highlights are titled '<Team> v <Team> | HIGHLIGHTS'. The list
# covers the allowlist's team sports (cricket, rugby league, football).
_TEAM_COUNTRIES = (
    "india", "pakistan", "sri lanka", "bangladesh", "afghanistan",
    "new zealand", "australia", "england", "south africa", "west indies",
    "ireland", "zimbabwe", "scotland", "wales", "netherlands", "namibia",
    "nepal", "oman", "united arab emirates", "papua new guinea",
    "france", "samoa", "tonga", "fiji", "lebanon", "cook islands",
    "argentina", "brazil", "germany", "spain", "italy", "portugal",
    "belgium", "croatia", "uruguay", "mexico", "united states", "canada",
    "japan", "south korea", "morocco", "nigeria", "ghana", "cameroon",
)


def _team_entities(article):
    """Team/country names appearing in the headline, in headline order."""
    headline = (article.get("headline") or "").lower()
    hits = []
    for name in _TEAM_COUNTRIES:
        m = re.search(r"\b" + re.escape(name) + r"\b", headline)
        if m:
            hits.append((m.start(), name))
    hits.sort()
    return [name for _pos, name in hits]


def build_search_queries(article, people):
    """Search queries for a channel-scoped search, most specific first.

    YouTube search is effectively AND-matching: a bag of every headline
    word returns nothing (proven live 2026-10-22 — 'Sherbini Singh Open
    anahat champion eight silicon' found zero videos on SQUASHTV, while
    'Anahat Singh' found the highlight immediately). So: primary =
    surnames + the event phrase ('Singh Sherbini Silicon Valley Open');
    fallback = the lead person's full name ('Anahat Singh'), which is
    how these channels title their uploads.

    Team fixtures get team-match queries AFTER the person pair (person
    queries stay first and unchanged): '<A> <B> highlights',
    '<A> v <B>', '<B> highlights' — the shapes rights holders actually
    title match uploads with ('New Zealand v India | HIGHLIGHTS').
    Queries only SHAPE discovery; the gate in gate_candidate() decides.
    Total queries capped at MAX_QUERIES_PER_ARTICLE.
    """
    person_phrases = [p for p in people
                      if not ({w.lower() for w in p.split()}
                              & EVENT_STOPWORDS)]
    event_phrases = [p for p in people if p not in person_phrases]
    surnames = []
    for p in person_phrases:
        parts = p.split()
        if parts and len(parts[-1]) >= 4:
            surnames.append(parts[-1])
    primary_parts = surnames[:2]
    if event_phrases:
        primary_parts.append(max(event_phrases, key=len))
    elif primary_parts:
        extra = [w for w in sorted(_content_words(article.get("headline")
                                                  or ""))
                 if w not in {s.lower() for s in surnames}][:2]
        primary_parts += extra
    primary = " ".join(primary_parts).strip()
    fallback = person_phrases[0] if person_phrases else None
    queries = []
    for q in (primary, fallback):
        if q and q not in queries:
            queries.append(q)
    teams = _team_entities(article)
    team_queries = []
    if len(teams) >= 2:
        team_queries = [f"{teams[0]} {teams[1]} highlights",
                        f"{teams[0]} v {teams[1]}",
                        f"{teams[1]} highlights"]
    elif teams:
        team_queries = [f"{teams[0]} highlights"]
    for q in team_queries:
        if q not in queries:
            queries.append(q)
    queries = queries[:MAX_QUERIES_PER_ARTICLE]
    return queries or [" ".join(sorted(_content_words(
        article.get("headline") or ""))[:4])]


# ─── The gate ────────────────────────────────────────────────────────────────

def gate_candidate(article, entry, video, people):
    """Decide whether `video` may be embedded in `article` as the official
    video from allowlisted `entry`. Returns (accepted, reason, score).

    Layers, in order — any failure rejects:
      1. Channel identity: video's channelId must equal the allowlist
         ID (or, for ID-less fixture results, channelTitle must equal
         the allowlist name exactly).
      2. Shared gate: embed_placement.youtube_embed_accept (pirate-bait,
         unofficial trailer, first-person/vlog, topical overlap, English
         title, score threshold, >=2 headline-keyword matches).
      3. Strong title match: a named person/event phrase from the
         headline must appear in the video title, AND at least one
         non-name headline content word must appear too.
      4. Recency: published within [article-14d, article+2d].
    """
    # 1 ── channel identity
    want_id = entry.get("channel_id") or ""
    got_id = video.get("channelId") or ""
    if want_id and got_id and got_id != want_id:
        return False, (f"channel id mismatch — video is on "
                       f"'{video.get('channelTitle')}', not the allowlisted "
                       f"{entry['name']}"), 0
    if not got_id and (video.get("channelTitle") or "").strip().lower() \
            != entry["name"].strip().lower():
        return False, (f"channel '{video.get('channelTitle')}' is not the "
                       f"allowlisted official channel '{entry['name']}'"), 0

    headline = article.get("headline") or ""
    keywords = sorted(_content_words(headline))

    # 2 ── shared gate
    entity = people[0] if people else entry["name"]
    score, reason = youtube_embed_accept(video, entity, keywords,
                                         headline=headline)
    if reason:
        return False, f"shared gate: {reason}", score

    # 3 ── strong title match: a PERSON phrase from the headline must
    # hit the title, and at least one further headline content word
    # (event/topic vocabulary) must hit too. Candidate phrases carrying
    # an event/filler token ("Silicon Valley Open", "World Cup Final")
    # count as event phrases, not people; if the headline yields no
    # person phrase at all, an event-phrase hit may stand in.
    title = video.get("title") or ""
    person_phrases = [p for p in people
                      if not ({w.lower() for w in p.split()}
                              & EVENT_STOPWORDS)]
    event_phrases = [p for p in people if p not in person_phrases]
    hit = _title_has_name(title, person_phrases)
    if hit:
        name_words = set()
        for p in person_phrases:
            name_words |= _content_words(p)
    else:
        hit = _title_has_name(title, event_phrases)
        name_words = _content_words(hit) if hit else set()
    if not hit:
        return False, "no headline name (person/event) in video title", score
    title_words = _content_words(title)
    non_name_hits = (set(keywords) - name_words) & title_words
    if not non_name_hits:
        return False, "no non-name headline word in video title", score

    # 4 ── recency window
    try:
        pub = datetime.fromisoformat(
            (video.get("publishedAt") or "").replace("Z", "+00:00"))
        art = datetime.fromisoformat(
            (article.get("published_at") or "").replace("Z", "+00:00"))
        if pub < art - timedelta(days=RECENCY_BEFORE_DAYS) \
                or pub > art + timedelta(days=RECENCY_AFTER_DAYS):
            return False, (f"published {pub.date()} outside window around "
                           f"article date {art.date()}"), score
    except (ValueError, TypeError):
        return False, "unparseable publishedAt / published_at", score

    return True, f"accepted (score {score})", score


# ─── Insertion ───────────────────────────────────────────────────────────────

def insert_after_first_paragraph(body, video_id):
    """Insert <youtube>VIDEO_ID</youtube> after the first body paragraph.

    Skips the key-takeaways div (the placement used for the manual
    Anahat embed, 2026-10-22). Returns the new body unchanged if the
    video is already present.
    """
    tag = f"<youtube>{video_id}</youtube>"
    if tag in (body or ""):
        return body
    start = 0
    kt = re.search(r'<div class="key-takeaways".*?</div>', body or "",
                   re.IGNORECASE | re.DOTALL)
    if kt:
        start = kt.end()
    m = re.search(r"</p>", (body or "")[start:], re.IGNORECASE)
    if m:
        pos = start + m.end()
        return body[:pos] + f"\n\n{tag}\n" + body[pos:]
    return (body or "") + f"\n\n{tag}\n"


# ─── X-embed widening ────────────────────────────────────────────────────────

def official_x_candidates(article, channels, registry_handles=()):
    """Official X handles worth checking for this article.

    Existing discovery is registry-only (enrich-on-publish.match_handles).
    This widens it: when the article maps to an allowlist rights holder
    that carries an official x_handle, that handle is added as a
    candidate. Returns [{handle, source, name}] deduped against
    registry_handles. Candidate DISCOVERY only — at apply time the
    existing find_best_tweet + verify_tweet gates still decide, and the
    embed itself is the existing bare-URL/react-tweet mechanism.
    """
    out, seen = [], {h.lower() for h in registry_handles}
    for entry, why in channels_for_article(article, channels):
        handle = entry.get("x_handle")
        if handle and handle.lower() not in seen:
            seen.add(handle.lower())
            out.append({"handle": handle, "source": "official-allowlist",
                        "name": entry.get("rights_holder") or entry["name"],
                        "why": why})
    return out


# ─── The pass ────────────────────────────────────────────────────────────────

def official_video_for_article(article, token=None, search_fn=None,
                               channels=None, log=print):
    """Run the official-video pass for one article (pure: no writes).

    Returns {status, channel, video_id, title, score, decisions, new_body}
    with status in {accepted, rejected, no_candidates, no_channel,
    skipped_has_embed, skipped_category}. `decisions` logs every
    candidate considered with its accept/reject reason. search_fn is
    injectable for tests: search_fn(entry, query, article) -> [videos].
    """
    body = article.get("body") or ""
    if re.search(r"<youtube>.*?</youtube>", body, re.IGNORECASE):
        return {"status": "skipped_has_embed", "decisions": []}
    category = (article.get("category") or "").lower()
    if category not in ELIGIBLE_CATEGORIES:
        return {"status": "skipped_category", "decisions": []}

    channels = channels if channels is not None else load_official_channels()
    mapped = channels_for_article(article, channels)
    if not mapped:
        return {"status": "no_channel", "decisions": []}

    if search_fn is None:
        token = token or get_youtube_token()
        if not token:
            return {"status": "no_channel",
                    "decisions": [{"reason": "YouTube OAuth token "
                                             "unavailable"}]}

        def _live_search(entry, query, art):
            return search_channel_videos(token, entry.get("channel_id"),
                                         query)
        search_fn = _live_search

    people = headline_people(article.get("headline") or "")
    queries = build_search_queries(article, people)
    decisions, best = [], None
    if len(mapped) > MAX_CHANNELS_PER_ARTICLE:
        decisions.append({
            "reason": f"{len(mapped)} channels mapped; searching top "
                      f"{MAX_CHANNELS_PER_ARTICLE} by specificity: "
                      + ", ".join(e["name"] for e, _w in
                                  mapped[:MAX_CHANNELS_PER_ARTICLE])})
        mapped = mapped[:MAX_CHANNELS_PER_ARTICLE]
    for entry, why in mapped:
        results = []
        for query in queries:
            results = search_fn(entry, query, article)
            if results:
                break
            decisions.append({"channel": entry["name"], "query": query,
                              "reason": "channel search returned nothing"})
        if not results:
            continue
        for video in results:
            ok, reason, score = gate_candidate(article, entry, video, people)
            decisions.append({"channel": entry["name"],
                              "video_id": video.get("videoId"),
                              "title": video.get("title"),
                              "accepted": ok, "reason": reason,
                              "score": score})
            if ok and (best is None or score > best[2]):
                best = (entry, video, score)
    if best:
        entry, video, score = best
        return {"status": "accepted", "channel": entry["name"],
                "video_id": video["videoId"], "title": video["title"],
                "score": score, "decisions": decisions,
                "new_body": insert_after_first_paragraph(body,
                                                         video["videoId"])}
    status = "rejected" if any("video_id" in d for d in decisions) \
        else "no_candidates"
    return {"status": status, "decisions": decisions}


# ─── Supabase (read-only in dry-run; writes gated twice) ─────────────────────

def _sb_env():
    return _load_env_file("~/workspace/.env.supabase")


def fetch_recent_articles(days=3, categories=("sports", "entertainment"),
                          limit=200):
    env = _sb_env()
    url, key = env.get("SUPABASE_URL", ""), env.get("SUPABASE_SERVICE_ROLE_KEY", "")
    since = (datetime.now(timezone.utc) - timedelta(days=days)) \
        .strftime("%Y-%m-%dT%H:%M:%SZ")
    cats = ",".join(categories)
    args = ["curl", "-sS", f"{url}/rest/v1/p2_articles",
            "-H", f"apikey: {key}", "-H", f"Authorization: Bearer {key}", "-G",
            "--data-urlencode",
            "select=id,slug,headline,category,body,published_at",
            "--data-urlencode", "status=eq.published",
            "--data-urlencode", f"category=in.({cats})",
            "--data-urlencode", f"published_at=gte.{since}",
            "--data-urlencode", "order=published_at.desc",
            "--data-urlencode", f"limit={limit}"]
    r = subprocess.run(args, capture_output=True, text=True, timeout=60)
    return json.loads(r.stdout)


def sb_patch_body(article_id, new_body):
    """The ONLY write in this module. Refuses unless the operator set
    VIDESHI_OFFICIAL_VIDEO_PASS_APPLY=1 (the CLI also requires --apply)."""
    if os.environ.get("VIDESHI_OFFICIAL_VIDEO_PASS_APPLY") != "1":
        raise RuntimeError("apply blocked: VIDESHI_OFFICIAL_VIDEO_PASS_APPLY "
                           "is not set")
    env = _sb_env()
    url, key = env.get("SUPABASE_URL", ""), env.get("SUPABASE_SERVICE_ROLE_KEY", "")
    payload = json.dumps({"body": new_body})
    r = subprocess.run(
        ["curl", "-sS", "-X", "PATCH",
         f"{url}/rest/v1/p2_articles?id=eq.{article_id}",
         "-H", f"apikey: {key}", "-H", f"Authorization: Bearer {key}",
         "-H", "Content-Type: application/json",
         "-H", "Prefer: return=minimal", "-d", payload],
        capture_output=True, text=True, timeout=30)
    return r.returncode == 0


# ─── CLI (dry-run by default) ────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description="Official-video embed pass")
    ap.add_argument("--days", type=int, default=3)
    ap.add_argument("--apply", action="store_true",
                    help="write accepted embeds ( ALSO requires env "
                         "VIDESHI_OFFICIAL_VIDEO_PASS_APPLY=1 )")
    args = ap.parse_args()

    articles = fetch_recent_articles(days=args.days)
    channels = load_official_channels()
    token = get_youtube_token()
    print(f"Articles (sports+entertainment, last {args.days}d): {len(articles)}")
    print(f"YouTube token: {'OK' if token else 'UNAVAILABLE'}")

    counts = {}
    searches = 0
    log_rows = []
    for art in articles:
        if re.search(r"<youtube>.*?</youtube>", art.get("body") or "",
                     re.IGNORECASE):
            counts["already_has_embed"] = counts.get("already_has_embed", 0) + 1
            continue
        counts["lacked_embed"] = counts.get("lacked_embed", 0) + 1
        mapped = channels_for_article(art, channels)
        if mapped and searches >= MAX_SEARCHES_PER_RUN:
            counts["search_budget_exhausted"] = \
                counts.get("search_budget_exhausted", 0) + 1
            continue
        if mapped:
            searches += min(len(mapped), MAX_CHANNELS_PER_ARTICLE)
        res = official_video_for_article(art, token=token, channels=channels)
        counts[res["status"]] = counts.get(res["status"], 0) + 1
        x_new = official_x_candidates(art, channels)
        if x_new:
            counts["x_candidates_gained"] = \
                counts.get("x_candidates_gained", 0) + 1
        log_rows.append({"slug": art.get("slug"),
                         "headline": art.get("headline"),
                         "status": res["status"],
                         "video_id": res.get("video_id"),
                         "decisions": res.get("decisions", []),
                         "x_candidates": x_new})
        if res["status"] == "accepted":
            print(f"  ACCEPT {art.get('slug')}: {res['video_id']} "
                  f"<{res['title'][:60]}> via {res['channel']}")
            if args.apply:
                ok = sb_patch_body(art["id"], res["new_body"])
                print(f"    apply: {'patched' if ok else 'PATCH FAILED'}")
        elif res["status"] == "rejected":
            for d in res["decisions"]:
                if d.get("video_id"):
                    print(f"  REJECT {art.get('slug')}: "
                          f"<{(d.get('title') or '')[:50]}> — {d['reason']}")

    print("\nSummary:", json.dumps(counts, indent=1))
    print(f"Channel-scoped searches: {searches} "
          f"(~{searches * SEARCH_UNITS_PER_CALL} API units)")
    os.makedirs(STATE_DIR, exist_ok=True)
    out = os.path.join(
        STATE_DIR, f"official-video-pass-dryrun-"
                   f"{datetime.now(timezone.utc):%Y%m%d-%H%M}.json")
    with open(out, "w") as f:
        json.dump({"counts": counts, "rows": log_rows}, f, indent=1)
    print(f"Decision log: {out}")


if __name__ == "__main__":
    main()

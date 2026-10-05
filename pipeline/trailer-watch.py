#!/usr/bin/env python3
"""Trailer watch — poll official YouTube channel RSS feeds for trailer/teaser drops.

- Reads pipeline/trailer-channels.json (42 verified official channels).
- Fetches each channel's videos.xml via curl (no API key needed).
- Keeps uploads whose titles look like official trailers/teasers.
- Dedupes against pipeline/.state/trailer-watch-seen.json.
- Writes new drops to pipeline/.state/trailer-watch-feed.json (merged into
  the trailers rail by prebuild-feeds.py).
- With --write: generates brief "teaser out" articles for tier-1 (major)
  channels and inserts them via v3-batch-insert.process_article.

First run: videos older than 3 days are marked seen without action, so only
recent drops surface. Subsequent runs: only genuinely new uploads.
"""
import json, os, re, sys, subprocess, html, unicodedata
from datetime import datetime, timezone, timedelta
from xml.etree import ElementTree as ET

PIPE = os.path.expanduser("~/workspace/the-videshi-news/pipeline")
STATE = os.path.join(PIPE, ".state")
SEEN_PATH = os.path.join(STATE, "trailer-watch-seen.json")
FEED_PATH = os.path.join(STATE, "trailer-watch-feed.json")
CHANNELS_PATH = os.path.join(PIPE, "trailer-channels.json")

WRITE = "--write" in sys.argv
LOOKBACK_DAYS_FIRST_RUN = 3
MAX_ARTICLES_PER_RUN = 6

_TITLE_RE = re.compile(r"trailer|teaser", re.IGNORECASE)
_BLOCK_RE = re.compile(
    r"#?shorts?\b|box[\s-]?office|collection|\bvs\.?\b|comparison|reaction|"
    r"review|interview|behind the scenes|\bbts\b|first look|mashup|tribute|"
    r"fancast|day\s*\d+|episode\s*\d+|song|audio|lyrical",
    re.IGNORECASE,
)


def curl_get(url, timeout=25):
    r = subprocess.run(
        ["curl", "-sS", "--max-time", str(timeout), "-A", "TheVideshi/1.0", url],
        capture_output=True, text=True, timeout=timeout + 10)
    return r.stdout if r.returncode == 0 else ""


def load_json(path, default):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return default


def fetch_channel_videos(channel_id):
    xml = curl_get(f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}")
    if not xml or "<feed" not in xml:
        return []
    try:
        root = ET.fromstring(xml)
    except Exception:
        return []
    ns = {"a": "http://www.w3.org/2005/Atom", "yt": "http://www.youtube.com/xml/schemas/2015",
          "m": "http://search.yahoo.com/mrss/"}
    out = []
    for e in root.findall("a:entry", ns):
        vid = (e.findtext("yt:videoId", default="", namespaces=ns) or "").strip()
        title = html.unescape(e.findtext("a:title", default="", namespaces=ns) or "").strip()
        pub = (e.findtext("a:published", default="", namespaces=ns) or "").strip()
        desc = html.unescape(e.findtext("m:group/m:description", default="", namespaces=ns) or "").strip()
        if vid and title:
            out.append({"video_id": vid, "title": title, "published": pub, "description": desc})
    return out


def is_trailer(title):
    return bool(_TITLE_RE.search(title)) and not bool(_BLOCK_RE.search(title))


def parse_dt(s):
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except Exception:
        return None


def split_film_title(title):
    """'Bhogi - Official Teaser | Sharwanand' -> ('Bhogi', 'Sharwanand')."""
    parts = re.split(r"\s*[|\-–—:]\s*", title)
    film = parts[0] if parts else title
    film = re.sub(r"(?i)\s*\(?(official\s+)?(teaser|trailer)(\s+\d+)?\)?\s*$", "", film).strip()
    film = re.sub(r"(?i)^(official\s+)?(teaser|trailer)\s*(of|for)?\s*", "", film).strip()
    rest_bits = [p for p in parts[1:]
                 if p and not _TITLE_RE.search(p) and not re.search(r"(?i)4k|hd|official", p)]
    rest = " | ".join(rest_bits[:2]).strip()
    return film or title, rest


def slugify(s):
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s[:70].strip("-")


_LANG_RE = r"hindi|tamil|telugu|kannada|malayalam|bengali|marathi|punjabi|gujarati|english"


def extract_language(title):
    """'... (Kannada) | Official Trailer' -> 'Kannada'. None if not found."""
    m = re.search(r"\b(" + _LANG_RE + r")\b", title, re.I)
    return m.group(1).capitalize() if m else None


def clean_film_name(film):
    """Strip language tags from a film name: '#418 (Kannada)' -> '#418'."""
    film = re.sub(r"\s*\((?:" + _LANG_RE + r")\)\s*", " ", film, flags=re.I)
    film = re.sub(r"\s*\b(" + _LANG_RE + r")\b\s*$", "", film, flags=re.I)
    return re.sub(r"\s+", " ", film).strip()


def film_key(title):
    """Grouping key: same movie across language versions -> same key."""
    t = unicodedata.normalize("NFKD", title)
    film, _ = split_film_title(t)
    key = re.sub(r"[^a-z0-9]+", "", clean_film_name(film).lower())
    return key or re.sub(r"[^a-z0-9]+", "", t.lower())[:40]


def build_brief_article(drops, channels_by_name):
    """One article per film; every language version listed with its own embed."""
    # Primary = most descriptive title (some channels post stub titles like
    # "#418 - Official Trailer (Hindi)" while others include the subtitle)
    first = max(drops, key=lambda d: len(d.get("title", "")))
    title = unicodedata.normalize("NFKD", first["title"])
    kind = "Teaser" if re.search(r"teas", title, re.I) else "Trailer"
    film, rest = split_film_title(title)
    film = clean_film_name(film) or "New release"
    hook = clean_film_name(rest.split("|")[0].strip()) if rest else ""
    # Don't let a studio/channel name become the headline hook
    if re.search(r"(?i)\b(makers?|films?|studios?|pictures|entertainment|media|music|series|originals)\b", hook):
        hook = ""
    headline = f"{film} {kind} Out" + (f": {hook[:60]}" if hook else "")
    pub = parse_dt(first["published"])
    pub_str = pub.strftime("%B %d, %Y") if pub else "today"

    versions = []
    for d in drops:
        lang = extract_language(unicodedata.normalize("NFKD", d["title"]))
        ch = channels_by_name.get(d["channel"], {})
        lang = lang or ch.get("language") or "Original"
        watch_url = f"https://www.youtube.com/watch?v={d['video_id']}"
        versions.append({"lang": lang, "channel": d["channel"], "url": watch_url,
                         "video_id": d["video_id"]})
    # de-dupe identical uploads, keep language order stable
    uniq, seen_urls = [], set()
    for v in versions:
        if v["url"] not in seen_urls:
            uniq.append(v); seen_urls.add(v["url"])
    versions = uniq
    langs = sorted({v["lang"] for v in versions})

    desc = first.get("description", "")
    desc_line = ""
    if desc:
        first_line = unicodedata.normalize("NFKD", desc).split("\n")[0].strip()
        # Keep it professional: plain-English sentence, no emojis/marketing fluff
        ok_chars = not re.search(r"[^\x00-\x7F\u201c\u201d\u2018\u2019\u2014\u2013\u2026\u20b9]", first_line)
        ok_lang = len(re.findall(r"[A-Za-z]", first_line)) >= 0.6 * max(len(first_line), 1)
        if 20 < len(first_line) < 220 and ok_chars and ok_lang \
                and not re.search(r"(?i)subscribe|follow us|copyright|click here", first_line):
            desc_line = first_line

    main_ch = channels_by_name.get(first["channel"], {})
    takeaways = [
        f"The {kind.lower()} for <b>{html.escape(film)}</b> dropped {pub_str}.",
    ]
    if desc_line:
        takeaways.append(html.escape(desc_line))
    takeaways.append(f"Out in {', '.join(langs)} — pick your language below.")

    body = (
        '<div class="key-takeaways"><ul>'
        + "".join(f"<li>{t}</li>" for t in takeaways)
        + "</ul></div>"
        + f"<p>The makers of <b>{html.escape(film)}</b> have released the official {kind.lower()}, "
        + f"unveiled {pub_str}.</p>"
    )
    if desc_line and len(takeaways) < 3:
        body += f"<p>{html.escape(desc_line)}</p>"
    dest = "streaming" if main_ch.get("industry") == "streamer" else "theaters"
    body += (f"<p>For diaspora audiences tracking the film's US release, the {kind.lower()} is the first "
             f"real look at what's headed to {dest}.</p>")
    for v in versions:
        body += (f"<p><b>{html.escape(v['lang'])}</b> — {html.escape(v['channel'])}</p>"
                 f"<youtube>{v['url']}</youtube>")

    thumb_vid = versions[0]["video_id"]
    return {
        "headline": headline,
        "subheadline": f"Official {kind.lower()} for {film} — out in {', '.join(langs)}.",
        "slug": slugify(headline) or f"trailer-{thumb_vid}",
        "body": body,
        "category": "entertainment",
        "tags": ["trailers", main_ch.get("industry", ""), film] + [l.lower() for l in langs],
        "sources": [{"name": v["channel"], "url": v["url"]} for v in versions],
        "image_url": f"https://i.ytimg.com/vi/{thumb_vid}/hqdefault.jpg",
        "image_caption": f"Still from the official {kind.lower()} of {film}.",
        "image_attribution": f"{html.escape(versions[0]['channel'])} / YouTube",
        "diaspora_angle": "US theatrical release tracking for diaspora audiences.",
    }


def sb_check_slug(slug):
    sb_url = os.environ.get("SUPABASE_URL", "")
    sb_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    if not sb_url or not sb_key:
        return False
    r = subprocess.run(
        ["curl", "-sS", "--max-time", "15",
         f"{sb_url}/rest/v1/p2_articles?select=id&slug=eq.{slug}&limit=1",
         "-H", f"apikey: {sb_key}", "-H", f"Authorization: Bearer {sb_key}"],
        capture_output=True, text=True, timeout=20)
    try:
        return bool(json.loads(r.stdout))
    except Exception:
        return False


def main():
    os.makedirs(STATE, exist_ok=True)
    cfg = load_json(CHANNELS_PATH, {})
    channels = cfg.get("channels", [])
    if not channels:
        print("No channels configured"); return 1
    seen = load_json(SEEN_PATH, {})
    first_run = not seen
    cutoff = datetime.now(timezone.utc) - timedelta(days=LOOKBACK_DAYS_FIRST_RUN)

    new_drops = []
    for ch in channels:
        videos = fetch_channel_videos(ch["channel_id"])
        for v in videos:
            vid = v["video_id"]
            if vid in seen:
                continue
            pub = parse_dt(v["published"])
            if first_run and pub and pub < cutoff:
                seen[vid] = {"title": v["title"], "seen_at": datetime.now(timezone.utc).isoformat(),
                             "seeded": True}
                continue
            if not is_trailer(v["title"]):
                seen[vid] = {"title": v["title"], "seen_at": datetime.now(timezone.utc).isoformat(),
                             "not_trailer": True}
                continue
            seen[vid] = {"title": v["title"], "channel": ch["name"],
                         "seen_at": datetime.now(timezone.utc).isoformat()}
            new_drops.append({"video_id": vid, "title": v["title"], "published": v["published"],
                              "description": v.get("description", ""),
                              "channel": ch["name"], "industry": ch["industry"], "tier": ch["tier"],
                              "thumbnail": f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg"})

    # Merge into persistent watch feed (prebuild merges this into trailers.json)
    feed = load_json(FEED_PATH, [])
    have = {d["video_id"] for d in feed}
    for d in new_drops:
        if d["video_id"] not in have:
            feed.append(d)
    # keep feed fresh: last 30 days only
    fresh_cut = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
    feed = [d for d in feed if d.get("published", "") >= fresh_cut]
    feed.sort(key=lambda d: d.get("published", ""), reverse=True)

    with open(SEEN_PATH, "w") as f:
        json.dump(seen, f, ensure_ascii=False)
    with open(FEED_PATH, "w") as f:
        json.dump(feed, f, ensure_ascii=False, indent=1)

    print(f"Channels polled: {len(channels)} | new trailer/teaser drops: {len(new_drops)}")
    majors = [d for d in new_drops if d["tier"] == 1]
    for d in new_drops:
        print(f"  [{'MAJOR' if d['tier']==1 else 'rail '} ] {d['channel']}: {d['title'][:80]}")

    articles_written = 0
    if WRITE and majors:
        # Import the batch inserter's per-article processor
        sys.path.insert(0, PIPE)
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "v3_batch_insert", os.path.join(PIPE, "v3-batch-insert.py"))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        channels_by_name = {c["name"]: c for c in channels}
        # Group by film: one article per movie, all language versions inside.
        # Prefix-merge handles channels that post stub titles ("#418 - Official
        # Trailer") alongside full ones ("#418 The Last Warning (Hindi) | ...").
        groups = []  # [key, drops]
        for d in majors:
            k = film_key(d["title"])
            placed = False
            for g in groups:
                if k and g[0] and (g[0].startswith(k) or k.startswith(g[0])):
                    if len(k) > len(g[0]):
                        g[0] = k
                    g[1].append(d)
                    placed = True
                    break
            if not placed:
                groups.append([k, [d]])
        for key, drops in groups[:MAX_ARTICLES_PER_RUN]:
            art = build_brief_article(drops, channels_by_name)
            if sb_check_slug(art["slug"]):
                print(f"  skip (slug exists): {art['slug']}")
                continue
            ok = mod.process_article(art)
            articles_written += 1 if ok else 0
        print(f"Brief articles inserted: {articles_written}/{min(len(groups), MAX_ARTICLES_PER_RUN)}")
    elif majors:
        print(f"(dry run — {len(majors)} major drops would get brief articles with --write)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

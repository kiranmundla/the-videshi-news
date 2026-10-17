#!/usr/bin/env python3
"""
sync-theater-roster.py — keep public/data/now-in-theaters.json CURRENT.

Built 2026-10-16 after the roster froze at a September slate and four
surfaces went blind at once (Movies rail, movie-reviews discovery,
build-boxoffice, and daily-happenings get_movie_releases — all read
this one file). Jailer 2, the biggest release of the month, was missed
by every one of them while our own news desk published 8+ stories.

Source: Wikipedia's per-language "List of <Lang> films of 2026" pages —
community-maintained release calendars, fetchable, and exactly right
for all three missed films. A film is ADMITTED to the roster only with
a notability double-signal: it has its own Wikipedia article (bluelink)
AND a market signal — a trailer in our trailers rail or a headline in
our own entertainment coverage. Every other in-window release is
logged as a candidate so misses are visible, never silent.

Merge semantics: ADD-ONLY for existing titles (enrichment fields are
never overwritten). Aging: entries released >70 days ago with no
review_slug are retired (logged). Freshness alarm: if the roster has
no release within ±21 days after sync, a 🚨 line is printed — the
weekly entertainment job surfaces it instead of failing quietly.

Usage: python3 -u sync-theater-roster.py [--apply] [--today YYYY-MM-DD]
Default is a dry run.
"""
import argparse, json, re, subprocess, sys
from datetime import date, timedelta
from pathlib import Path
from urllib.parse import quote

BASE = Path(__file__).resolve().parent.parent
ROSTER = BASE / "public" / "data" / "now-in-theaters.json"
TRAILERS = BASE / "public" / "data" / "trailers.json"
UA = "TheVideshi/1.0"
LISTS = {
    "Tamil": "List_of_Tamil_films_of_2026",
    "Telugu": "List_of_Telugu_films_of_2026",
    "Hindi": "List_of_Hindi_films_of_2026",
    "Malayalam": "List_of_Malayalam_films_of_2026",
    "Kannada": "List_of_Kannada_films_of_2026",
}
_MONTH_NAMES = ["january", "february", "march", "april", "may", "june", "july",
                "august", "september", "october", "november", "december"]
MONTHS = {m: i + 1 for i, m in enumerate(_MONTH_NAMES)}
MONTHS.update({m[:3]: i + 1 for i, m in enumerate(_MONTH_NAMES)})  # 'OCT', 'JAN' …
PAST_DAYS, FUTURE_DAYS = 21, 60


def curl(url, headers=None, timeout=30):
    cmd = ["curl", "-sL", "-A", UA]
    for k, v in (headers or {}).items():
        cmd += ["-H", f"{k}: {v}"]
    cmd.append(url)
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    return r.stdout


def norm_title(t):
    return re.sub(r"[^a-z0-9]", "", (t or "").lower())


def kebab(t):
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", (t or "").lower())).strip("-")


def parse_list(html, language, year):
    """Extract dated releases from the quarterly tables. Month and day
    are carried by rowspan cells, so track them as state."""
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")
    films = []
    for tbl in soup.select("table.wikitable"):
        rows = tbl.find_all("tr")
        if len(rows) < 2:
            continue
        hdr = [c.get_text(" ", strip=True).lower() for c in rows[0].find_all(["th", "td"])]
        if not any(h.startswith("opening") for h in hdr) or not any("title" in h for h in hdr):
            continue
        month = day = None
        for tr in rows[1:]:
            cells = tr.find_all(["td", "th"])
            if not cells:
                continue
            texts = [c.get_text(" ", strip=True) for c in cells]
            i = 0
            compact = re.sub(r"\s+", "", texts[0]).lower() if texts else ""
            if compact in MONTHS:
                month, day = MONTHS[compact], None
                i = 1
            if i < len(texts) and re.fullmatch(r"\d{1,2}", texts[i] or ""):
                day = int(texts[i])
                i += 1
            rest = texts[i:]
            if month is None or day is None or len(rest) < 3:
                continue
            title, director, cast_cell = rest[0], rest[1], rest[2]
            if not title or title.lower() in ("title",):
                continue
            link = cells[i].find("a", href=True) if i < len(cells) else None
            bluelink = bool(link) and "/wiki/" in link.get("href", "") \
                and not link.get("href", "").startswith("/wiki/List_of") \
                and "redlink" not in link.get("href", "") \
                and "action=edit" not in link.get("href", "")
            cast = [c.strip() for c in re.split(r",", cast_cell) if c.strip()][:3]
            try:
                rel = date(year, month, day)
            except ValueError:
                continue
            films.append({"title": title, "director": director, "cast": cast,
                          "language": language, "release_date": rel.isoformat(),
                          "bluelink": bluelink,
                          "wiki": link.get("href") if link else None})
    return films


def load_env(name):
    env = {}
    p = Path.home() / "workspace" / f".env.{name}"
    if p.exists():
        for line in p.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def news_headlines():
    """Recent entertainment headlines from our own article stream —
    the coverage signal (we were publishing Jailer 2 stories while
    the roster slept)."""
    env = load_env("supabase")
    url, key = env.get("SUPABASE_URL", ""), env.get("SUPABASE_SERVICE_ROLE_KEY", "")
    if not url or not key:
        return []
    host = url.replace("https://", "")
    since = (date.today() - timedelta(days=75)).isoformat()
    q = (f"https://{host}/rest/v1/p2_articles?select=headline"
         f"&status=eq.published&category=eq.entertainment&published_at=gte.{since}"
         f"&order=published_at.desc&limit=1000")
    out = curl(q, {"apikey": key, "Authorization": f"Bearer {key}"})
    try:
        return [r.get("headline", "") for r in json.loads(out)]
    except Exception:
        return []


def title_variants(title):
    """Full normalized title + the base title before a subtitle colon —
    Wikipedia lists 'Prahaar: The Untold Story of Ujjwal Nikam' where
    the roster and our headlines just say 'Prahaar'."""
    base = re.split(r"[:–—]", title)[0]
    return {norm_title(title), norm_title(base)}


_STOP = {"the", "and", "for", "part"}
_FILM_CTX = ("film", "movie", "trailer", "teaser", "starrer", "directed",
             "releases", "releasing", "box office", "actor", "actress", "crore")


def headline_covers(headlines, title):
    base = re.split(r"[:–—]", title)[0]
    words = [w for w in re.findall(r"[a-z0-9]+", base.lower())
             if len(w) > 2 and w not in _STOP]
    if not words:
        return False
    for h in headlines:
        hl = h.lower()
        if len(words) == 1:
            # Generic one-word titles (Train, Scene) match everywhere in
            # news — require a film-context word in the same headline.
            if words[0] in hl and any(c in hl for c in _FILM_CTX):
                return True
        elif all(w in hl for w in words):
            return True
    return False


_STREAMING_PLATFORMS = ("netflix", "amazon prime video", "prime video",
                        "jiohotstar", "disney+ hotstar", "zee5", "sonyliv",
                        "apple tv+")


def streaming_premiere(f):
    """Wikipedia's year lists mix theatrical and direct-to-streaming
    premieres, and a streaming premiere's trailer/coverage fires the same
    admission signals (Reporting Live on Netflix and Don't Be Shy on Prime
    Video were rostered as theater releases on 2026-10-16, complete with
    'showtimes near me' ticket links). Detect the premiere from the film's
    own article via any of: an infobox 'Distributed by <platform>', a
    'released/premiered on <platform>' statement in the lead, or an
    explicit direct-to-streaming description. The list's link can be a
    redlink or a differently-suffixed title, so fall back to the common
    article-title variants. Returns the platform name or None."""
    from bs4 import BeautifulSoup
    urls = []
    href = f.get("wiki") or ""
    if href:
        clean = href.split("?")[0]
        urls.append(clean if clean.startswith("http")
                    else "https://en.wikipedia.org" + clean)
    year = (f.get("release_date") or "")[:4]
    for t in (f"{f['title']} ({year} film)", f"{f['title']} (film)", f["title"]):
        u = "https://en.wikipedia.org/wiki/" + quote(t.replace(" ", "_"))
        if u not in urls:
            urls.append(u)
    for u in urls:
        html = curl(u, timeout=30)
        if not html:
            continue
        text = BeautifulSoup(html, "html.parser").get_text(" ", strip=True)
        if len(text) < 4000:
            continue  # redirect stub / missing page — try the next variant
        low = text.lower()
        if "direct-to-streaming" in low or "direct to streaming" in low:
            return "streaming"
        head, lead = low[:4000], low[:9000]
        for p in _STREAMING_PLATFORMS:
            if re.search(r"distributed by\s+" + re.escape(p) + r"\b", head):
                return p
            if re.search(r"(released|premiered|debuted)[^.]{0,80}?\b"
                         + re.escape(p) + r"\b", lead):
                return p
        return None  # a real article with no streaming signal: theatrical
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--today", default=None)
    args = ap.parse_args()
    today = date.fromisoformat(args.today) if args.today else date.today()
    lo, hi = today - timedelta(days=PAST_DAYS), today + timedelta(days=FUTURE_DAYS)

    roster = json.loads(ROSTER.read_text())
    existing = set()
    for m in roster.get("movies", []):
        existing |= title_variants(m["title"])

    trailer_titles = set()
    if TRAILERS.exists():
        try:
            for t in json.loads(TRAILERS.read_text()).get("trailers", []):
                trailer_titles |= title_variants(t.get("title", ""))
        except Exception:
            pass
    headlines = news_headlines()

    found = []
    for lang, page in LISTS.items():
        html = curl(f"https://en.wikipedia.org/wiki/{page}", timeout=45)
        if not html:
            print(f"⚠️ {lang}: list fetch failed")
            continue
        films = parse_list(html, lang, today.year)
        print(f"📋 {lang}: {len(films)} dated releases parsed")
        found.extend(films)

    admitted, candidates, ott, already = [], [], [], 0
    for f in found:
        rel = date.fromisoformat(f["release_date"])
        if not (lo <= rel <= hi):
            continue
        if title_variants(f["title"]) & existing:
            already += 1
            continue
        in_trailer = bool(title_variants(f["title"]) & trailer_titles)
        in_news = headline_covers(headlines, f["title"])
        if f["bluelink"] and (in_trailer or in_news):
            plat = streaming_premiere(f)
            if plat:
                ott.append((f, plat))
                continue
            f["signal"] = "trailer" if in_trailer else "news"
            admitted.append(f)
        else:
            candidates.append(f)

    print(f"\n🪟 Window {lo} → {hi}: {already} already on roster, "
          f"{len(admitted)} admitted, {len(candidates)} candidates (not admitted)")
    for f in admitted:
        print(f"  ➕ {f['release_date']} {f['title']} ({f['language']}) "
              f"dir. {f['director']} — via {f['signal']}")
    for f, plat in ott:
        print(f"  ⏭ {f['release_date']} {f['title']} ({f['language']}) "
              f"— streaming premiere ({plat}), not a theater release")
    near_lo, near_hi = today - timedelta(days=30), today + timedelta(days=30)
    shown = 0
    for f in candidates:
        rel = date.fromisoformat(f["release_date"])
        if near_lo <= rel <= near_hi:
            print(f"  ·  {f['release_date']} {f['title']} ({f['language']}) "
                  f"bluelink={f['bluelink']} — candidate only")
            shown += 1
    if len(candidates) > shown:
        print(f"  ·  …and {len(candidates) - shown} more candidates outside ±30 days (counted, not listed)")

    new_entries = []
    for f in admitted:
        rel = date.fromisoformat(f["release_date"])
        if rel < today - timedelta(days=3):
            status = "now_playing"
        elif rel <= today + timedelta(days=3):
            status = "opening"
        else:
            status = "coming_soon"
        cast_txt = ", ".join(f["cast"][:2])
        entry = {
            "title": f["title"],
            "slug": f"{kebab(f['title'])}-{rel.year}",
            "release_date": f["release_date"],
            "status": status,
            "language": f["language"],
            "director": f["director"],
            "cast": f["cast"],
            "genre": "",
            "is_indian": True,
            "year": rel.year,
            "ticket_url": "https://www.google.com/search?q="
                          + quote(f"{f['title']} showtimes near me"),
            "why_watch": (f"{f['title']} is a {f['language']} film directed by "
                          f"{f['director']}" + (f", starring {cast_txt}." if cast_txt else ".")),
        }
        if status in ("opening", "coming_soon"):
            entry["rating"] = "Opens " + rel.strftime("%b %d").replace(" 0", " ")
            entry["rating_source"] = "Release date"
        new_entries.append(entry)

    # Coming-soon date refresh: unreleased films move (OM Chapter 1 was
    # postponed a month) — the calendar's date wins for coming_soon rows.
    by_variant = {}
    for f in found:
        for v in title_variants(f["title"]):
            by_variant.setdefault(v, f)
    refreshed = []
    for m in roster.get("movies", []):
        if m.get("status") != "coming_soon":
            continue
        hit = next((by_variant[v] for v in title_variants(m["title"])
                    if v in by_variant), None)
        if hit and hit["release_date"] != m.get("release_date"):
            print(f"  📅 {m['title']}: release moved {m.get('release_date')} "
                  f"→ {hit['release_date']} (calendar)")
            m["release_date"] = hit["release_date"]
            refreshed.append(m["title"])

    # Aging: retire stale, unreviewed entries
    retire = []
    kept = []
    for m in roster.get("movies", []):
        try:
            rel = date.fromisoformat(m.get("release_date", ""))
        except ValueError:
            kept.append(m)
            continue
        if rel < today - timedelta(days=70) and not m.get("review_slug") \
                and m.get("status") != "coming_soon":
            retire.append(m)
        else:
            kept.append(m)
    for m in retire:
        print(f"  🗑 retire {m['title']} ({m.get('release_date')}, unreviewed, >70d)")

    final = kept + new_entries
    near = [m for m in final
            if abs((date.fromisoformat(m["release_date"]) - today).days) <= 21
            if m.get("release_date")]
    if not near:
        print("🚨 ROSTER FRESHNESS ALARM: no release within ±21 days on the roster "
              "— the release calendar sync needs a human look.")

    if args.apply and (new_entries or retire or refreshed):
        ROSTER.with_suffix(".json.bak").write_text(ROSTER.read_text())
        roster["movies"] = sorted(final, key=lambda m: m.get("release_date", ""))
        ROSTER.write_text(json.dumps(roster, indent=2, ensure_ascii=False))
        print(f"\n✅ Roster updated: {len(final)} films "
              f"(+{len(new_entries)}, −{len(retire)})")
    elif args.apply:
        print("\n✅ No roster changes needed.")
    else:
        print(f"\n🔍 Dry run — roster would hold {len(final)} films. Re-run with --apply.")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Generate streaming-picks.json for the What to Watch This Week section.

Automatically discovers this week's new Indian/diaspora-relevant streaming
releases via web search + GPT-4o-mini curation. Enriches with Wikipedia
poster images (CC-licensed) and YouTube trailer URLs.

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
                    print(f"  ✅ Wikipedia image: {candidate}")
                    return thumb
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

    # Step 4: Enrich with Wikipedia posters and YouTube trailers
    print(f"\n── Step 4: Enriching with posters and trailers ──")
    for pick in valid_picks:
        title = pick["title"]
        year = pick.get("year", 0)
        media_type = pick.pop("media_type", "auto")
        language = pick.get("language", "")

        print(f"\n  Processing: {title}")

        # Wikipedia poster
        poster = fetch_wikipedia_image(title, year, media_type)
        pick["poster_url"] = poster
        pick["backdrop_url"] = poster  # Same image for backdrop

        # YouTube trailer
        trailer = try_find_youtube_trailer(title, year, language)
        pick["trailer_url"] = trailer

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

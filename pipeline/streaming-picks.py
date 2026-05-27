#!/usr/bin/env python3
"""
Generate streaming-picks.json for the What to Watch This Week section.

Sources poster images from Wikipedia API and trailer URLs from YouTube.
No TMDB dependency — Wikipedia images are CC-licensed, YouTube embeds are standard.

Run: python3 pipeline/streaming-picks.py
Output: public/data/streaming-picks.json
"""
import json, os, sys, re, time
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import quote

try:
    import requests
except ImportError:
    print("Installing requests...")
    os.system(f"{sys.executable} -m pip install requests -q")
    import requests

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "public" / "data" / "streaming-picks.json"

HEADERS = {"User-Agent": "TheVideshi/1.0 (https://thevideshi.com; editorial)"}
WIKI_API = "https://en.wikipedia.org/api/rest_v1/page/summary"


def today_str():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def week_range():
    now = datetime.utcnow()
    monday = now - timedelta(days=now.weekday())
    sunday = monday + timedelta(days=6)
    return f"{monday.strftime('%b %d')} – {sunday.strftime('%b %d, %Y')}"


def fetch_wikipedia_image(title: str, year: int = 0, media_type: str = "auto") -> str:
    """
    Try to get a poster/thumbnail image from Wikipedia for a show or movie.
    Tries multiple title variations. Returns the thumbnail URL or empty string.
    """
    # Build candidate titles to try
    candidates = [title]

    # Clean up title for Wikipedia lookup (remove subtitles after colon for initial try)
    base_title = title.split(":")[0].strip() if ":" in title else title

    if base_title != title:
        candidates.append(base_title)

    # Try with disambiguation suffixes
    type_suffixes = []
    if media_type == "film" or media_type == "auto":
        type_suffixes.append("film")
        if year:
            type_suffixes.append(f"{year} film")
    if media_type == "series" or media_type == "auto":
        type_suffixes.append("TV series")
        if year:
            type_suffixes.append(f"{year} TV series")
        type_suffixes.append("web series")

    for base in [title, base_title]:
        for suffix in type_suffixes:
            candidates.append(f"{base} ({suffix})")

    # Deduplicate while preserving order
    seen = set()
    unique_candidates = []
    for c in candidates:
        if c not in seen:
            seen.add(c)
            unique_candidates.append(c)

    for candidate in unique_candidates:
        try:
            encoded = quote(candidate.replace(" ", "_"), safe="/_:()%")
            url = f"{WIKI_API}/{encoded}"
            resp = requests.get(url, headers=HEADERS, timeout=8)
            if resp.status_code == 200:
                data = resp.json()
                thumb = data.get("thumbnail", {}).get("source", "")
                if thumb:
                    print(f"  ✅ Wikipedia image found: {candidate}")
                    return thumb  # Use AS-IS (330px)
            time.sleep(0.3)  # Be polite to Wikipedia
        except Exception as e:
            print(f"  ⚠️ Wikipedia error for '{candidate}': {e}")
            continue

    print(f"  ❌ No Wikipedia image found for: {title}")
    return ""


def youtube_search_url(title: str, suffix: str = "official trailer") -> str:
    """Build a YouTube search URL for the trailer."""
    query = f"{title} {suffix}".strip()
    return f"https://www.youtube.com/results?search_query={quote(query)}"


def try_find_youtube_trailer(title: str, year: int = 0, language: str = "") -> str:
    """
    Try to find actual YouTube video ID by searching.
    Include language to avoid wrong-language matches.
    Falls back to search URL if we can't find a direct link.
    """
    lang_tag = f" {language}" if language and language != "English" else ""
    queries = [
        f"{title}{lang_tag} official trailer {year}" if year else f"{title}{lang_tag} official trailer",
        f"{title}{lang_tag} trailer",
        f"{title} trailer {year}" if year else f"{title} trailer",
    ]

    for query in queries:
        try:
            search_url = f"https://www.youtube.com/results?search_query={quote(query)}"
            resp = requests.get(search_url, headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                "Accept-Language": "en-US,en;q=0.9",
            }, timeout=10)

            if resp.status_code == 200:
                # Extract video IDs from the page
                video_ids = re.findall(r'"videoId":"([A-Za-z0-9_-]{11})"', resp.text)
                if video_ids:
                    vid = video_ids[0]
                    print(f"  🎬 YouTube trailer found: {vid} for '{title}'")
                    return f"https://www.youtube.com/watch?v={vid}"

            time.sleep(0.5)
        except Exception as e:
            print(f"  ⚠️ YouTube search error for '{title}': {e}")
            continue

    # Fall back to search URL
    print(f"  📎 Using YouTube search URL for: {title}")
    return youtube_search_url(title)


# ── Curated picks for this week (May 25–31, 2026) ──
PICKS = [
    {
        "title": "Dhurandhar: Raw & Undekha",
        "wiki_title": "Dhurandhar (film)",
        "slug": "dhurandhar-raw-and-undekha",
        "platform": "Netflix",
        "platform_icon": "netflix",
        "genre": "Action Thriller",
        "year": 2026,
        "media_type": "film",
        "synopsis": "The extended, uncensored cut of Aditya Dhar's record-breaking spy thriller. Ranveer Singh leads a raw intelligence mission across hostile terrain with Sanjay Dutt and Arjun Rampal in a story that doesn't flinch. The theatrical version shattered box office records — this version goes further.",
        "cast": ["Ranveer Singh", "Sanjay Dutt", "Arjun Rampal", "Sara Arjun"],
        "director": "Aditya Dhar",
        "why_watch": "The biggest Bollywood hit of 2026 just got a longer, uncut version — and it's streaming on Netflix.",
        "is_indian": True,
        "watch_url": "https://www.netflix.com/search?q=dhurandhar",
        "language": "Hindi",
        "trending": True,
    },
    {
        "title": "Jolly LLB 3",
        "wiki_title": "Jolly LLB 3",
        "slug": "jolly-llb-3",
        "platform": "JioHotstar",
        "platform_icon": "hotstar",
        "genre": "Courtroom Comedy-Drama",
        "year": 2025,
        "media_type": "film",
        "synopsis": "Akshay Kumar returns as the lovably incompetent small-town lawyer who stumbles into cases too big for him. This time, Jolly takes on a pharmaceutical giant in a case that hits uncomfortably close to home. The franchise that proved courtroom dramas can be funny.",
        "cast": ["Akshay Kumar", "Arshad Warsi", "Huma Qureshi"],
        "director": "Subhash Kapoor",
        "why_watch": "The Jolly franchise is comfort food for Bollywood fans. Akshay Kumar's David-vs-Goliath courtroom antics never get old.",
        "is_indian": True,
        "watch_url": "https://www.hotstar.com/in/search?q=jolly+llb+3",
        "language": "Hindi",
        "trending": True,
    },
    {
        "title": "Kara",
        "wiki_title": "Kara (2025 film)",
        "slug": "kara-dhanush",
        "platform": "Netflix",
        "platform_icon": "netflix",
        "genre": "Heist Thriller",
        "year": 2025,
        "media_type": "film",
        "synopsis": "Set in 1991 during the Gulf War, a reformed thief in rural Tamil Nadu is forced back into crime when a corrupt bank seizes his family's ancestral land. Dhanush delivers one of his most restrained performances in this slow-burn heist drama.",
        "cast": ["Dhanush", "Mamitha Baiju", "K. S. Ravikumar"],
        "director": "Vignesh Raja",
        "why_watch": "Dhanush at his brooding best. A Tamil heist film now available in five languages on Netflix.",
        "is_indian": True,
        "watch_url": "https://www.netflix.com/search?q=kara+dhanush",
        "language": "Tamil",
        "trending": False,
    },
    {
        "title": "Satrangi",
        "wiki_title": "Satrangi (TV series)",
        "slug": "satrangi-badle-ka-khel",
        "platform": "JioHotstar",
        "platform_icon": "hotstar",
        "genre": "Action Crime",
        "year": 2026,
        "media_type": "series",
        "synopsis": "A gritty revenge saga set across seven interconnected stories. When a family is torn apart by a powerful crime syndicate, each member takes a different path to justice — some legal, some not.",
        "cast": [],
        "director": "",
        "why_watch": "Think Sacred Games meets a revenge anthology. Seven stories, one vendetta — a fresh format for Hindi crime TV.",
        "is_indian": True,
        "watch_url": "https://www.hotstar.com/in/search?q=satrangi",
        "language": "Hindi",
        "trending": False,
    },
    {
        "title": "Jetlee",
        "wiki_title": "Jetlee (film)",
        "slug": "jetlee-telugu",
        "platform": "JioHotstar",
        "platform_icon": "hotstar",
        "genre": "Action Thriller",
        "year": 2026,
        "media_type": "film",
        "synopsis": "A Telugu action thriller that's been generating buzz for its high-octane sequences and layered storytelling. When an ordinary man discovers a conspiracy that goes all the way to the top, he must become something he never imagined to protect his family.",
        "cast": [],
        "director": "",
        "why_watch": "Telugu cinema continues its hot streak. If you loved Pushpa, this scratches the same itch — ordinary man, extraordinary circumstances.",
        "is_indian": True,
        "watch_url": "https://www.hotstar.com/in/search?q=jetlee",
        "language": "Telugu",
        "trending": False,
    },
    {
        "title": "Warrant",
        "wiki_title": "Warrant (TV series)",
        "slug": "warrant-vilangu",
        "platform": "SonyLIV",
        "platform_icon": "sonyliv",
        "genre": "Crime Thriller",
        "year": 2026,
        "media_type": "series",
        "synopsis": "A spinoff from the acclaimed Tamil series Vilangu, following a new case that pulls investigators into a web of corruption and violence. The series expands the universe of one of Tamil television's most critically acclaimed crime dramas.",
        "cast": [],
        "director": "",
        "why_watch": "If Vilangu was your gateway into Tamil crime thrillers, Warrant takes you deeper. Same universe, fresh case, higher stakes.",
        "is_indian": True,
        "watch_url": "https://www.sonyliv.com/search?q=warrant",
        "language": "Tamil",
        "trending": False,
    },
    {
        "title": "Memu Copulam",
        "wiki_title": "Memu Copulam",
        "slug": "memu-copulam",
        "platform": "Zee5",
        "platform_icon": "zee5",
        "genre": "Comedy Crime",
        "year": 2026,
        "media_type": "series",
        "synopsis": "A Telugu comedy-crime series following a group of small-time con artists who accidentally stumble into a much bigger heist than they bargained for. Think Ocean's Eleven meets Telugu slapstick — sharp writing, chaotic energy.",
        "cast": [],
        "director": "",
        "why_watch": "Telugu comedy meets crime caper. Light, fun, and doesn't take itself too seriously — the perfect weekend binge.",
        "is_indian": True,
        "watch_url": "https://www.zee5.com/search?q=memu+copulam",
        "language": "Telugu",
        "trending": False,
    },
    {
        "title": "Spider-Noir",
        "wiki_title": "Spider-Noir (TV series)",
        "slug": "spider-noir",
        "platform": "Prime Video",
        "platform_icon": "prime",
        "genre": "Superhero Noir",
        "year": 2025,
        "media_type": "series",
        "synopsis": "Nicolas Cage stars as Ben Reilly, an aging private investigator in 1933 New York City hired on a case that forces him to confront his past as the city's only superhero. Available in both black-and-white and full color versions.",
        "cast": ["Nicolas Cage", "Brendan Gleeson", "Lamorne Morris"],
        "director": "Harry Bradbeer",
        "why_watch": "Nicolas Cage doing noir detective work with spider powers in the 1930s? Critics are calling it 'Cage at his best.'",
        "is_indian": False,
        "watch_url": "https://www.primevideo.com/search?phrase=spider-noir",
        "language": "English",
        "trending": True,
    },
    {
        "title": "A Good Girl's Guide to Murder",
        "wiki_title": "A Good Girl's Guide to Murder (TV series)",
        "slug": "good-girls-guide-to-murder-s2",
        "platform": "Netflix",
        "platform_icon": "netflix",
        "genre": "Mystery Thriller",
        "year": 2024,
        "media_type": "series",
        "synopsis": "Emma Myers returns as Pip Fitz-Amobi, the amateur detective who can't stop digging. Season 2 takes a darker turn as Pip investigates a new case while dealing with the fallout of her first investigation. Based on Holly Jackson's bestselling trilogy.",
        "cast": ["Emma Myers", "Zain Iqbal", "Rahul Pattni"],
        "director": "Dolly Wells",
        "why_watch": "The YA mystery that became a global hit is back — and this time it's personal.",
        "is_indian": False,
        "watch_url": "https://www.netflix.com/search?q=good+girl+guide+murder",
        "language": "English",
        "trending": False,
    },
    {
        "title": "Dead Man's Wire",
        "wiki_title": "Dead Man's Wire",
        "slug": "dead-mans-wire",
        "platform": "Netflix",
        "platform_icon": "netflix",
        "genre": "Thriller",
        "year": 2026,
        "media_type": "film",
        "synopsis": "A taut psychological thriller about a crisis negotiator who receives a call that changes everything — the voice on the other end knows secrets about her past that no one else should. As the clock ticks down, the line between negotiator and target blurs.",
        "cast": [],
        "director": "",
        "why_watch": "Netflix's latest edge-of-your-seat thriller. If you liked The Call or Buried, this is your cup of chai.",
        "is_indian": False,
        "watch_url": "https://www.netflix.com/search?q=dead+man+wire",
        "language": "English",
        "trending": False,
    },
]


def build():
    print(f"🎬 Building streaming picks for: {week_range()}\n")

    for pick in PICKS:
        print(f"Processing: {pick['title']}")

        # Fetch Wikipedia poster image
        wiki_title = pick.pop("wiki_title", pick["title"])
        media_type = pick.pop("media_type", "auto")
        poster = fetch_wikipedia_image(wiki_title, pick.get("year", 0), media_type)
        pick["poster_url"] = poster
        pick["backdrop_url"] = poster  # Use same image for backdrop

        # Find YouTube trailer
        trailer = try_find_youtube_trailer(pick["title"], pick.get("year", 0), pick.get("language", ""))
        pick["trailer_url"] = trailer

        print()

    # Sort: Indian trending → Indian non-trending → Global trending → Global non-trending
    indian = [p for p in PICKS if p["is_indian"]]
    global_picks = [p for p in PICKS if not p["is_indian"]]

    indian.sort(key=lambda p: (0 if p.get("trending") else 1))
    global_picks.sort(key=lambda p: (0 if p.get("trending") else 1))

    all_sorted = indian + global_picks
    for i, pick in enumerate(all_sorted):
        pick["rank"] = i + 1

    data = {
        "generated_at": today_str(),
        "week_of": week_range(),
        "editorial_intro": "Dhurandhar drops its uncut version on Netflix this week. Dhanush's heist thriller Kara arrives in five languages. Nicolas Cage goes full noir on Prime Video. And if you're looking for regional gems, Telugu and Tamil cinema deliver again.",
        "picks": all_sorted,
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    # Summary
    with_images = sum(1 for p in all_sorted if p.get("poster_url"))
    with_embeds = sum(1 for p in all_sorted if "watch?v=" in p.get("trailer_url", ""))
    print(f"✅ Wrote {len(all_sorted)} streaming picks to {OUT}")
    print(f"   Indian: {len(indian)}, Global: {len(global_picks)}")
    print(f"   With poster images: {with_images}/{len(all_sorted)}")
    print(f"   With embeddable trailers: {with_embeds}/{len(all_sorted)}")
    print(f"   Week: {data['week_of']}")


if __name__ == "__main__":
    build()

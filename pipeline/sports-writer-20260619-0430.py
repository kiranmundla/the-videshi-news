#!/usr/bin/env python3
"""
Sports Writer — June 19, 2026 (04:30 UTC run)
Article: Major League Cricket 2026 opens in Grand Prairie (Dallas). Texas
Super Kings chase down a record 221 against Seattle Orcas, powered by Faf du
Plessis's unbeaten 113 off 52, after Tim Seifert's 104 had given the Orcas a
mammoth 220/2. A record run chase in MLC history to launch Season 4.

ANGLE: This is the RESULT follow-up to the earlier-today MLC season preview
("America's Cricket League Begins Its Fourth Season Tonight"). Diaspora hook:
MLC is built in the US suburbs the Indian/South Asian diaspora calls home,
Grand Prairie/Dallas is its beating heart, and the league is the most
tangible expression of cricket's American chapter. Du Plessis is the TSK
captain; the franchise is co-owned by Chennai Super Kings (India's IPL
juggernaut). Forward look to the 30-game double round-robin and July playoffs.

Hero image: Faf du Plessis has a Wikipedia portrait. Try his page first;
fall back to Tim Seifert, then on-topic Commons cricket imagery.
"""

import os, sys, json, io
from datetime import datetime, timezone

import requests
from PIL import Image

# ── ENV ──
env_supa = os.path.expanduser("~/.env.supabase")
for line in open(env_supa):
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, v = line.split("=", 1)
        os.environ[k] = v.strip().strip('"').strip("'")

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
UA = "TheVideshi/1.0 (thevideshi.com)"
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}


def fetch_wikipedia_person_image(person_name):
    encoded = person_name.replace(" ", "_")
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": UA}, timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  \u2713 Wikipedia image for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  \u26a0 Wikipedia error for '{person_name}': {e}")
    return None


def fetch_wikimedia_commons_images(search_query, limit=8):
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": search_query,
        "gsrnamespace": "6",
        "gsrlimit": str(limit),
        "prop": "imageinfo",
        "iiprop": "url|size|mime",
        "iiurlwidth": "1200",
        "format": "json",
    }
    out = []
    try:
        r = requests.get(
            "https://commons.wikimedia.org/w/api.php",
            params=params, headers={"User-Agent": UA}, timeout=15,
        )
        if r.status_code == 200:
            pages = r.json().get("query", {}).get("pages", {})
            for p in pages.values():
                ii = (p.get("imageinfo") or [{}])[0]
                url = ii.get("thumburl") or ii.get("url")
                mime = ii.get("mime", "")
                if url and mime.startswith("image/") and ii.get("width", 0) >= 800:
                    out.append({"url": url, "title": p.get("title", ""),
                                "w": ii.get("width"), "h": ii.get("height")})
    except Exception as e:
        print(f"  \u26a0 Commons error for '{search_query}': {e}")
    return out


def compress_image(img_bytes, max_width=1200, quality=80):
    img = Image.open(io.BytesIO(img_bytes))
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=quality, optimize=True)
    return buf.getvalue()


def upload_to_supabase(img_url, filename):
    try:
        import subprocess
        tmp = f"/tmp/{filename}"
        subprocess.run(["curl", "-sS", "-A", UA, "-o", tmp, img_url], capture_output=True)
        if not (os.path.exists(tmp) and os.path.getsize(tmp) > 5000):
            print(f"  \u2717 Download failed for {img_url[:80]}")
            return None
        content = open(tmp, "rb").read()
        compressed = compress_image(content)
        print(f"  \U0001f4e6 Compressed to {len(compressed)/1024:.0f} KB")
        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
        resp = requests.post(
            upload_url,
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "image/jpeg",
                "x-upsert": "true",
            },
            data=compressed, timeout=30,
        )
        if resp.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  \u2713 Uploaded: {public_url}")
            return public_url
        else:
            print(f"  \u2717 Upload failed ({resp.status_code}): {resp.text[:200]}")
            return None
    except Exception as e:
        print(f"  \u2717 Upload error: {e}")
        return None


def insert_article(article):
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS, json=article, timeout=30,
    )
    if r.status_code in (200, 201):
        result = r.json()
        art_id = result[0]["id"] if isinstance(result, list) else result.get("id")
        print(f"  \u2713 Inserted article: {article['slug']} (id={art_id})")
        return art_id
    else:
        print(f"  \u2717 Insert failed ({r.status_code}): {r.text[:300]}")
        return None


print("\n" + "="*60)
print("ARTICLE: MLC 2026 opener — du Plessis 113* powers record TSK chase")
print("="*60)

art_slug = "major-league-cricket-2026-opener-texas-super-kings-faf-du-plessis-113-record-chase-seattle-orcas-tim-seifert-grand-prairie-diaspora-nri"
art_headline = "America's Cricket Season Opened With Its Highest-Ever Chase. A 41-Year-Old From Pretoria Made 113 to Win It."
art_subheadline = "Faf du Plessis, captain of the Chennai-owned Texas Super Kings, hauled down a mountainous 221 in 18.3 overs to launch Major League Cricket's fourth season in Grand Prairie — the Dallas suburb that has become the capital of cricket in America."

art_body = """GRAND PRAIRIE, Texas — For one warm Thursday night in a suburb between Dallas and Fort Worth, the highest level of cricket on American soil produced something it had never seen before: a successful chase of 221, completed with nine balls to spare, in front of a sellout crowd that had driven in from across the Metroplex. The fourth season of Major League Cricket did not so much begin as detonate.

The Texas Super Kings hunted down the Seattle Orcas' imposing 220 for 2 — reaching 221 for 4 in 18.3 overs — for the largest run chase in the competition's short history. At the centre of it stood the most familiar figure in franchise cricket worldwide: Faf du Plessis, the Super Kings' 41-year-old captain, who finished unbeaten on 113 from just 52 deliveries.

## A Chase That Should Not Have Been Possible

The night had belonged, briefly, to Seattle. Asked to bat first, the Orcas were propelled by New Zealand wicketkeeper-batter Tim Seifert, whose blistering 104 from 66 balls anchored a total that, on most nights at any ground in the world, would have been more than enough. At the innings break, the Grand Prairie Stadium scoreboard read 220 for 2, and the only question seemed to be the margin of the Orcas' victory.

Du Plessis had other ideas. The South African, who has spent the back nine of his career as a globe-trotting franchise specialist, treated the steepest target in MLC history as a personal invitation. Opening the batting, he found the boundary at will, reaching his hundred off barely more than 45 balls and dragging a chase that began as a long shot into something close to a procession. Rilee Rossouw lent rapid support with a cameo of his own, and the required rate that loomed at nearly 11 an over never had the chance to bite. Marcus Stoinis, the Orcas captain, gamely took a wicket, but the Seattle bowling — Adam Milne went for 41 from his four overs — had no answer to du Plessis in this mood.

## Why Grand Prairie Matters

To understand why this result resonates well beyond the boxscore, you have to understand where it happened. Grand Prairie is not a neutral venue; it is, increasingly, the spiritual home of American cricket. The 7,000-seat stadium — retrofitted from a minor-league baseball park — sits in a slice of North Texas whose population has been transformed by South Asian migration over two decades. The engineers, doctors, and tech workers who filled the stands are precisely the diaspora that MLC was built to serve, and the cheers that greeted every du Plessis boundary carried accents from Hyderabad, Chennai, Lahore, and Colombo as much as from Texas.

That is the quiet genius of Major League Cricket. It did not try to teach baseball-loving America to love cricket. It went, instead, to the suburbs where cricket was already beloved — Dallas, the Bay Area, suburban New Jersey — and built a professional league in the diaspora's backyard. The Super Kings themselves are co-owned by the Chennai Super Kings, the Indian Premier League's most-followed franchise, and the yellow jerseys in the Grand Prairie stands were indistinguishable from those worn at Chepauk.

## A Stacked Season Ahead

The opener is the first of 30 league fixtures across a month-long, double round-robin schedule that will move from Grand Prairie to Oakland and Pomona before the playoffs — Qualifier, Eliminator, Challenger, and a July 18 final — return to Oakland. The six franchises, between them, have assembled a roster of international talent that would not look out of place at a global tournament: Nicholas Pooran, Quinton de Kock, Glenn Maxwell, Sikandar Raza, Finn Allen, and dozens more have signed on for an American summer.

Defending champions MI New York — the New York franchise owned by the Mumbai Indians stable, who beat the Washington Freedom by five runs in last year's final — do not begin their title defence until later in the round. The Super Kings, by contrast, have made the loudest possible opening statement. Two more matches follow on Friday alone, with the Los Angeles Knight Riders facing the San Francisco Unicorns and the Orcas returning to face the Washington Freedom.

## Why the Diaspora Is Watching

For NRIs in the United States, MLC is something subtly different from the cricket beamed in from India at inconvenient hours. It is theirs — played in their time zone, in stadiums they can drive to, by a league that exists because of them. A child raised in Frisco or Fremont can now watch top-tier cricket in person on a Thursday evening and dream of a professional pathway that did not exist a decade ago. USA Cricket's own rise — the national side now features American-raised players of Indian and South Asian heritage — runs directly through this league.

Thursday's record chase was, in that sense, more than a thrilling start to a season. It was a reminder that the fastest-growing chapter of cricket's global story is being written not in Mumbai or Melbourne, but in a Texas suburb where the diaspora finally has a league to call home. And on opening night, a 41-year-old captain in Chennai yellow gave them a hundred to remember it by."""

print(f"\nWord count: ~{len(art_body.split())} words")

print("\nSourcing image...")
img_caption = "Faf du Plessis, captain of the Texas Super Kings, whose unbeaten 113 sealed a record chase on the opening night of Major League Cricket 2026"
img_attribution = "Wikimedia Commons"
img_final = None

# 1) Try Faf du Plessis's own Wikipedia portrait
for person in ["Faf du Plessis", "Tim Seifert"]:
    wiki_img = fetch_wikipedia_person_image(person)
    if wiki_img:
        got = upload_to_supabase(wiki_img, f"{art_slug}.jpg")
        if got:
            img_final = got
            if person == "Faf du Plessis":
                img_caption = "Faf du Plessis, captain of the Texas Super Kings, whose unbeaten 113 sealed a record chase on the opening night of Major League Cricket 2026"
            else:
                img_caption = "Tim Seifert, whose 104 set up Seattle Orcas' total of 220 on the opening night of Major League Cricket 2026"
            break

# 2) Fallback: on-topic Commons imagery
if not img_final:
    commons_queries = [
        "Faf du Plessis",
        "Major League Cricket Grand Prairie",
        "Grand Prairie Stadium cricket",
        "cricket batsman Texas",
    ]
    for q in commons_queries:
        cands = fetch_wikimedia_commons_images(q)
        for c in cands:
            low = c["title"].lower()
            print(f"   candidate: {c['title']} ({c['w']}x{c['h']})")
            if any(bad in low for bad in ["logo", ".svg", ".pdf", "map", "seating",
                                           "letters", "diagram", "chart", "flag", "icon"]):
                continue
            if not any(g in low for g in ["plessis", "cricket", "seifert", "stadium", "grand prairie"]):
                continue
            got = upload_to_supabase(c["url"], f"{art_slug}.jpg")
            if got:
                img_final = got
                if "plessis" in low:
                    img_caption = "Faf du Plessis, captain of the Texas Super Kings, whose unbeaten 113 sealed a record chase on Major League Cricket's opening night"
                else:
                    img_caption = "Cricket in the United States — Major League Cricket opened its fourth season in Grand Prairie, Texas"
                break
        if img_final:
            break

if not img_final:
    print("  \u26a0 No image uploaded \u2014 inserting without image")

art_data = {
    "headline": art_headline,
    "subheadline": art_subheadline,
    "body": art_body,
    "slug": art_slug,
    "category": "sports",
    "vertical": "cricket",
    "status": "review",
    "is_editorial": False,
    "image_url": img_final or "",
    "image_caption": img_caption,
    "image_attribution": img_attribution,
    "sources": json.dumps([
        {"name": "Wikipedia \u2014 2026 Major League Cricket season", "url": "https://en.wikipedia.org/wiki/2026_Major_League_Cricket_season"},
        {"name": "Cricbuzz \u2014 Major League Cricket 2026 schedule, live scores and results", "url": "https://www.cricbuzz.com/cricket-series/major-league-cricket-2026"},
        {"name": "Cricket World \u2014 Major League Cricket 2026: Teams, Full Squads, Fixtures, Schedule, Venues", "url": "https://www.cricketworld.com/"},
        {"name": "Wisden \u2014 MLC 2026 Schedule: Full Fixtures List, Match Timings And Venues", "url": "https://wisden.com/"},
        {"name": "SportsCafe \u2014 TEX vs SEA Major League Cricket Score 19.06.2026", "url": "https://www.sportscafe.in/"},
    ]),
    "diaspora_angle": "Major League Cricket is the most tangible expression of cricket's American chapter \u2014 a professional league built in the US suburbs the Indian and South Asian diaspora calls home, with Grand Prairie near Dallas as its capital. The Texas Super Kings are co-owned by the IPL's Chennai Super Kings, and the record opening-night chase gives NRIs in the US a top-tier league in their own time zone, their own city, and a professional pathway for the next generation that did not exist a decade ago.",
    "published_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
}

art_id = insert_article(art_data)

print("\n" + "="*60)
print("DONE")
print("="*60)
mark = "\u2713" if art_id else "\u2717"
print(f"Article: {mark} {art_slug}")
print(f"Word count: ~{len(art_body.split())} words")
print(f"Image: {img_final or '(none)'}")
print("Set to status='review'")

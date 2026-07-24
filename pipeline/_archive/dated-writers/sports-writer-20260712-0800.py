#!/usr/bin/env python3
"""Sports Writer — July 12, 2026 (8:00 AM PT)
Two articles:
1. India's ODI squad reshuffle after T20I injury blow
2. MLC 2026 playoffs head to Oakland
"""

import json
import os
import re
import subprocess
import sys
import urllib.parse
from datetime import datetime, timezone

# ── Supabase config ──────────────────────────────────────────────────────────
def load_env():
    env_path = os.path.expanduser("~/workspace/.env.supabase")
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ[k] = v.strip().strip('"').strip("'")

load_env()
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}


# ── Image helpers ────────────────────────────────────────────────────────────
def fetch_wikipedia_person_image(person_name):
    """Get an actual photo from Wikipedia REST API."""
    import requests
    encoded = urllib.parse.quote(person_name.replace(" ", "_"))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=10,
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia error for '{person_name}': {e}")
    return None


def fetch_wikimedia_commons_images(query, limit=5):
    """Search Wikimedia Commons for images."""
    import requests
    encoded = urllib.parse.quote(query)
    try:
        r = requests.get(
            f"https://commons.wikimedia.org/w/api.php?action=query&generator=search"
            f"&gsrsearch={encoded}&gsrnamespace=6&gsrlimit={limit}"
            f"&prop=imageinfo&iiprop=url|size|mime&iiurlwidth=1200&format=json",
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=15,
        )
        if r.status_code == 200:
            data = r.json()
            pages = data.get("query", {}).get("pages", {})
            results = []
            for page in pages.values():
                ii = page.get("imageinfo", [{}])[0]
                url = ii.get("thumburl") or ii.get("url")
                mime = ii.get("mime", "")
                width = ii.get("thumbwidth") or ii.get("width", 0)
                if url and "image" in mime and width >= 300:
                    results.append({
                        "url": url,
                        "title": page.get("title", ""),
                        "width": width,
                    })
            return results
    except Exception as e:
        print(f"  ⚠ Commons error for '{query}': {e}")
    return []


def validate_image_url(url):
    """Check an image URL returns 200 with image content-type and decent size."""
    try:
        result = subprocess.run(
            ["curl", "-sS", "-o", "/dev/null", "-w", "%{http_code}|%{content_type}|%{size_download}",
             "-A", "TheVideshi/1.0 (thevideshi.com)", "-L", url],
            capture_output=True, text=True, timeout=15,
        )
        parts = result.stdout.strip().split("|")
        if len(parts) >= 3:
            code, ctype, size = parts[0], parts[1], float(parts[2])
            if code == "200" and "image" in ctype and size > 5000:
                print(f"  ✓ Image validated: {code}, {ctype}, {size:.0f} bytes")
                return True
            else:
                print(f"  ✗ Image failed: code={code}, type={ctype}, size={size:.0f}")
    except Exception as e:
        print(f"  ✗ Image validation error: {e}")
    return False


def make_slug(headline):
    """Generate a URL slug from headline."""
    slug = headline.lower()
    slug = re.sub(r"[''']s\b", "s", slug)
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug.strip())
    slug = re.sub(r"-+", "-", slug)
    # Truncate and add suffix
    if len(slug) > 80:
        slug = slug[:80].rsplit("-", 1)[0]
    slug += "-nri-july-2026"
    return slug


# ── Supabase insert ──────────────────────────────────────────────────────────
def insert_article(article):
    """Insert article into p2_articles."""
    import requests
    payload = json.dumps(article)
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        data=payload,
        timeout=30,
    )
    if r.status_code in (200, 201):
        result = r.json()
        if isinstance(result, list) and result:
            print(f"  ✓ Inserted: {result[0].get('slug', 'unknown')}")
            return True
        print(f"  ✓ Inserted (no body returned)")
        return True
    else:
        print(f"  ✗ Insert failed ({r.status_code}): {r.text[:300]}")
        return False


# ── Dedup check ──────────────────────────────────────────────────────────────
def check_dedup(slug):
    """Check if an article with this slug already exists."""
    import requests
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/p2_articles?select=slug&slug=eq.{slug}&limit=1",
        headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"},
        timeout=10,
    )
    if r.status_code == 200:
        data = r.json()
        if data:
            print(f"  ⚠ Slug already exists: {slug}")
            return True
    return False


# ══════════════════════════════════════════════════════════════════════════════
# ARTICLE 1: India's ODI Squad Reshuffled
# ══════════════════════════════════════════════════════════════════════════════
def build_article_1():
    print("\n━━━ Article 1: India's ODI Squad Reshuffled ━━━")

    headline = "Broken Bodies, Fresh Faces. India Reshuffles Its ODI Squad as England Series Looms."
    subheadline = "Harshit Rana's hamstring rules him out of the three-match series. Prince Yadav gets the call-up. And after a 4-0 T20I whitewash, the big guns — Rohit, Kohli, Bumrah — are back."
    slug = "india-odi-squad-reshuffle-harshit-rana-injury-prince-yadav-england-series-rohit-kohli-bumrah-nri-july-2026"

    if check_dedup(slug):
        return None

    # Image: Shubman Gill (ODI captain)
    image_url = None
    image_caption = ""
    image_attribution = ""

    print("  Sourcing image: Shubman Gill (Wikipedia)...")
    img = fetch_wikipedia_person_image("Shubman Gill")
    if img and validate_image_url(img):
        image_url = img
        image_caption = "Shubman Gill, India's ODI captain for the England series"
        image_attribution = "Wikimedia Commons"

    if not image_url:
        print("  Trying Jasprit Bumrah...")
        img = fetch_wikipedia_person_image("Jasprit Bumrah")
        if img and validate_image_url(img):
            image_url = img
            image_caption = "Jasprit Bumrah returns to India's ODI squad for the England series"
            image_attribution = "Wikimedia Commons"

    if not image_url:
        print("  Trying Commons: India cricket team...")
        results = fetch_wikimedia_commons_images("India national cricket team 2024 2025")
        for r in results:
            if validate_image_url(r["url"]):
                image_url = r["url"]
                image_caption = "India's cricket team during an international series"
                image_attribution = "Wikimedia Commons"
                break

    body = """India's battered touring party received another blow on Saturday when the Board of Control for Cricket in India (BCCI) confirmed that fast bowler Harshit Rana will miss the upcoming three-match One-Day International series against England due to a hamstring injury sustained during the third T20I at Trent Bridge.

The 23-year-old seamer, who had only recently returned from a knee surgery that forced him to miss this year's T20 World Cup, managed just three matches on the tour before his body failed him again. In his place, the BCCI has named Prince Yadav — the young pacer who impressed during the T20I series despite India's dismal 0-4 result — as Rana's replacement in the ODI squad.

## The Injury List Grows

Rana is not the only casualty. Spinner Varun Chakravarthy, who fractured a toe during IPL 2026 and played through pain before suffering a hamstring injury at Trent Bridge, has been ruled out of the upcoming T20I series against Zimbabwe starting July 23. Leg-spinner Ravi Bishnoi will take his spot.

The double injury blow comes at a particularly uncomfortable time for Indian cricket. With Hardik Pandya and Nitish Kumar Reddy already sidelined with leg and quadriceps injuries respectively, India's pace and all-round depth is being stretched thinner with each passing week.

## The Big Guns Return

The ODI series, however, brings a welcome reset. Unlike the experimental T20I squad that was dismantled by Jos Buttler's 131 and Harry Brook's brilliance in Southampton, the ODI unit features India's most experienced core.

Shubman Gill captains. Rohit Sharma and Virat Kohli, rested for the T20I leg, slot back into the top order. Jasprit Bumrah, India's pace spearhead and the world's number-one ranked ODI bowler, leads an attack that includes Arshdeep Singh, Prasidh Krishna, and Kuldeep Yadav. Washington Sundar and Axar Patel provide spin depth and lower-order steel.

The full squad reads: Shubman Gill (captain), Rohit Sharma, Virat Kohli, Shreyas Iyer, KL Rahul, Ishan Kishan, Washington Sundar, Axar Patel, Shivam Dube, Kuldeep Yadav, Jasprit Bumrah, Prasidh Krishna, Arshdeep Singh, Gurnoor Brar, Prince Yadav.

## What's at Stake

The three-match series opens at Edgbaston in Birmingham on July 14, moves to Cardiff on July 16, and culminates at Lord's on July 19. For India, the mission is simple: redemption. The 4-0 T20I whitewash — India's worst bilateral T20I result in England — triggered a BCCI performance review and raised pointed questions about Gautam Gambhir's coaching tenure and the team's batting approach.

In ODIs, India's record in England is considerably stronger. The 50-over format suits Kohli's classical game and gives Bumrah the runway to be devastating with the new ball. Gill, who averages over 60 in ODIs, will be eager to stamp his authority as captain.

## The Diaspora Watch

For the millions of Indian Americans following from across the Atlantic, the shift to ODIs brings the names that matter most. A Kohli century at Lord's remains appointment viewing for NRIs everywhere. The series will be available on Willow TV and JioCinema in the US, with the Birmingham opener coincidentally falling on the same day as the France-Spain World Cup semifinal in Dallas — a busy day on the sports calendar for diaspora fans juggling two obsessions.

Prince Yadav's call-up also represents the next generation knocking on the door. At 22, his raw pace and ability to extract bounce on English surfaces could be exactly what India needs if the senior quicks tire across a demanding schedule."""

    sources = json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com"},
        {"name": "Cricbuzz", "url": "https://www.cricbuzz.com"},
        {"name": "CricketCountry", "url": "https://www.cricketcountry.com"},
    ])

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "slug": slug,
        "body": body,
        "category": "sports",
        "vertical": "cricket",
        "status": "review",
        "is_editorial": False,
        "image_url": image_url,
        "image_caption": image_caption,
        "image_attribution": image_attribution,
        "sources": sources,
        "score_total": 8,
        "diaspora_angle": "Rohit, Kohli, and Bumrah return for the England ODI series — appointment viewing for NRIs worldwide, with the opener on the same day as the World Cup semifinal.",
        "published_at": datetime.now(timezone.utc).isoformat(),
    }

    return article


# ══════════════════════════════════════════════════════════════════════════════
# ARTICLE 2: MLC 2026 Playoffs Head to Oakland
# ══════════════════════════════════════════════════════════════════════════════
def build_article_2():
    print("\n━━━ Article 2: MLC Playoffs Head to Oakland ━━━")

    headline = "Cricket Comes to the Bay. MLC's Playoffs Head to Oakland for the First Time."
    subheadline = "San Francisco Unicorns top the table, four teams are through, and the league's championship stage moves to the West Coast. For Indian Americans in the Bay Area, live cricket has never been closer."
    slug = "mlc-2026-playoffs-oakland-coliseum-unicorns-knight-riders-mi-new-york-freedom-bay-area-nri-july-2026"

    if check_dedup(slug):
        return None

    # Image: Try Oakland Coliseum or a cricket player
    image_url = None
    image_caption = ""
    image_attribution = ""

    # Try Rashid Khan (well-known, plays for Unicorns)
    print("  Sourcing image: Rashid Khan (Wikipedia)...")
    img = fetch_wikipedia_person_image("Rashid Khan (cricketer)")
    if img and validate_image_url(img):
        image_url = img
        image_caption = "Rashid Khan, who plays for San Francisco Unicorns in MLC 2026"
        image_attribution = "Wikimedia Commons"

    if not image_url:
        print("  Trying Oakland Coliseum (Commons)...")
        results = fetch_wikimedia_commons_images("Oakland Coliseum stadium")
        for r in results:
            title_lower = r.get("title", "").lower()
            if "oakland" in title_lower and validate_image_url(r["url"]):
                image_url = r["url"]
                image_caption = "The Oakland Coliseum, which will host MLC 2026 playoffs for the first time"
                image_attribution = "Wikimedia Commons"
                break

    if not image_url:
        print("  Trying Nicholas Pooran (Wikipedia)...")
        img = fetch_wikipedia_person_image("Nicholas Pooran")
        if img and validate_image_url(img):
            image_url = img
            image_caption = "Nicholas Pooran, MI New York's power-hitting star in MLC 2026"
            image_attribution = "Wikimedia Commons"

    body = """Major League Cricket's fourth season has reached its decisive phase, and for the first time in the league's short history, the championship stage is heading to the West Coast. The Oakland Coliseum will host all four playoff matches from July 15 through July 18, bringing live international-standard cricket to one of America's most cricket-passionate regions.

The league confirmed the format earlier this season: a Qualifier and Eliminator on July 15, a Challenger on July 16, and the Championship Final on July 18. After ten weeks of regular-season action across venues in Texas, California, New York, Virginia, and Washington state, the final four is set.

## The Standings

San Francisco Unicorns claimed the top spot with 12 points from ten matches, the only team to win six games this season. Led by South African sensation Lhuan-dre Pretorius — whose 313 runs at a strike rate of 177 have made him the tournament's most exciting bat — the Unicorns have been the most consistent unit all season. They enter the Qualifier as favourites.

The race for second through fourth was brutal. Los Angeles Knight Riders, MI New York, and Washington Freedom all finished on 10 points, separated only by net run rate. The Knight Riders, buoyed by back-to-back wins over the Unicorns and Freedom in July, clinched second place. MI New York edged Freedom for third on NRR, sending Washington into the Eliminator as the fourth seed.

Seattle Orcas, despite Dasun Shanaka's viral double hat-trick against Texas Super Kings and Tim Seifert's 282 runs in eight innings, finished fifth with eight points. Texas Super Kings — the defending champions who brought Faf du Plessis and Sunil Narine to the league — were eliminated with just six points from nine matches.

## The Playoff Picture

**Qualifier (July 15, 2:30 PM PT):** San Francisco Unicorns vs. Los Angeles Knight Riders. The winner goes straight to the final. The Unicorns' Pretorius, Rashid Khan, and Aaron Hardie against Colin Munro's experienced Knight Riders lineup. LAKR already proved they can beat the Unicorns — their 184-run chase on July 11 was a statement.

**Eliminator (July 15, 6:30 PM PT):** MI New York vs. Washington Freedom. Nicholas Pooran and Tim David's explosive middle order against Mitchell Owen's 344-run season. The loser goes home. The winner faces the Qualifier's loser in the Challenger.

**Challenger (July 16):** A second-chance match for the Qualifier loser — but also a knockout for the Eliminator winner.

**Final (July 18, 4:30 PM PT):** The Qualifier winner hosts. The champion gets the trophy at the Oakland Coliseum.

## Why Oakland Matters

The move to Oakland is no accident. The Bay Area is home to one of the largest Indian-American populations in the country, and last season's regular-season games at the Coliseum drew strong crowds and passionate atmospheres. MLC CEO Johnny Grave called the decision a chance to "bring that same playoff intensity to the Oakland Coliseum" after three years of championship finals selling out at Grand Prairie Stadium in Texas.

For NRIs in San Francisco, San Jose, Fremont, and the broader East Bay, this is cricket in their backyard — no flights to Texas or cross-country trips required. The Coliseum, which held its first MLC matches last season, has already proven it can handle a high-scoring cricket spectacle on its baseball-sized outfield.

## The Diaspora Connection

MLC continues to grow as a genuine sporting product for the Indian diaspora. Saurabh Netravalkar — the India-born, Oracle-employed left-arm pacer who became a folk hero during the 2024 T20 World Cup — plays for Washington Freedom and took three wickets in their recent clash with the Knight Riders at the brand-new Knight Riders Cricket Field in Pomona, California.

The league's player pool now includes IPL stars alongside American cricketers, creating a blend of elite talent and local identity that no other cricket league in the world offers. And with tickets priced for families rather than corporate suites, the Oakland playoff weekend could be the most accessible major cricket event in US history.

Whether it's the Unicorns' Bay Area faithful willing their team to a home-turf title, or MINY's Pooran smashing sixes over the Coliseum's deep mid-wicket boundary, the next four days will determine whether MLC's American experiment can deliver a championship moment worthy of the sport's grandest stages."""

    sources = json.dumps([
        {"name": "Cricbuzz", "url": "https://www.cricbuzz.com"},
        {"name": "ESPNcricinfo", "url": "https://www.espncricinfo.com"},
        {"name": "Wikipedia - 2026 MLC Season", "url": "https://en.wikipedia.org/wiki/2026_Major_League_Cricket_season"},
    ])

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "slug": slug,
        "body": body,
        "category": "sports",
        "vertical": "cricket",
        "status": "review",
        "is_editorial": False,
        "image_url": image_url,
        "image_caption": image_caption,
        "image_attribution": image_attribution,
        "sources": sources,
        "score_total": 8,
        "diaspora_angle": "MLC playoffs come to Oakland — live cricket in the Bay Area, home to one of America's largest Indian-American communities. Saurabh Netravalkar and IPL stars make it personal.",
        "published_at": datetime.now(timezone.utc).isoformat(),
    }

    return article


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("═══ Videshi Sports Writer — July 12, 2026 ═══\n")

    articles = []

    a1 = build_article_1()
    if a1:
        articles.append(a1)

    a2 = build_article_2()
    if a2:
        articles.append(a2)

    if not articles:
        print("\n⚠ No articles to insert (all dupes or failed).")
        sys.exit(0)

    print(f"\n━━━ Inserting {len(articles)} articles ━━━")
    success = 0
    for art in articles:
        if art.get("image_url"):
            print(f"\n  → {art['headline'][:60]}...")
            if insert_article(art):
                success += 1
        else:
            print(f"\n  ⚠ Skipping (no image): {art['headline'][:60]}...")
            # Insert anyway — article quality > image
            print(f"  → Inserting without verified image...")
            if insert_article(art):
                success += 1

    print(f"\n═══ Done: {success}/{len(articles)} articles inserted ═══")

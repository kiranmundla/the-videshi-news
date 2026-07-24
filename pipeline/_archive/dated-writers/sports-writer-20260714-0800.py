#!/usr/bin/env python3
"""
Sports Writer — July 14, 2026
Two articles:
1. India's Chess Golden Year (Gukesh + Vaishali World Championship challenges)
2. Netravalkar — Silicon Valley's cricket hero heading to MLC playoffs in Oakland
"""

import os, sys, json, requests, urllib.parse, re, datetime, subprocess, uuid, hashlib, time

# ── Supabase config ──────────────────────────────────────────────
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}
UA = "TheVideshi/1.0 (thevideshi.com)"

# ── Image helpers ────────────────────────────────────────────────

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": UA},
            timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image found for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None


def fetch_wikimedia_commons_images(search_query, limit=5):
    """Search Wikimedia Commons for CC-licensed images."""
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": search_query,
        "gsrnamespace": "6",
        "gsrlimit": str(limit),
        "prop": "imageinfo",
        "iiprop": "url|size|mime",
        "iiurlwidth": "1200",
        "format": "json"
    }
    try:
        r = requests.get(
            "https://commons.wikimedia.org/w/api.php",
            params=params,
            headers={"User-Agent": UA},
            timeout=15
        )
        if r.status_code == 200:
            data = r.json()
            pages = data.get("query", {}).get("pages", {})
            results = []
            for pid, page in sorted(pages.items(), key=lambda x: x[1].get("index", 999)):
                ii = page.get("imageinfo", [{}])[0]
                url = ii.get("thumburl") or ii.get("url")
                title = page.get("title", "")
                mime = ii.get("mime", "")
                if url and "image" in mime:
                    results.append({"url": url, "title": title})
            return results
    except Exception as e:
        print(f"  ⚠ Commons search error: {e}")
    return []


def verify_image_url(url):
    """Verify image URL returns HTTP 200 with image content-type and decent size."""
    if not url:
        return False
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=10, stream=True)
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            print(f"  ✓ Image verified: {r.status_code}, {ct}, {cl} bytes")
            return True
        print(f"  ✗ Image check failed: {r.status_code}, {ct}, {cl} bytes")
    except Exception as e:
        print(f"  ✗ Image verify error: {e}")
    return False


def make_slug(headline):
    """Create a URL slug from headline."""
    s = headline.lower()
    s = re.sub(r'[^a-z0-9\s-]', '', s)
    s = re.sub(r'[\s]+', '-', s.strip())
    s = re.sub(r'-+', '-', s)
    return s[:120]


def insert_article(article):
    """Insert article into Supabase."""
    url = f"{SUPABASE_URL}/rest/v1/p2_articles"
    r = requests.post(url, headers=HEADERS, json=article, timeout=30)
    if r.status_code in (200, 201):
        data = r.json()
        if isinstance(data, list) and data:
            print(f"  ✓ Inserted: {data[0].get('slug', 'unknown')}")
            return True
    print(f"  ✗ Insert failed: {r.status_code} — {r.text[:300]}")
    return False


# ── Article 1: India's Chess Golden Year ──────────────────────────

def build_chess_article():
    print("\n=== Article 1: India's Chess Golden Year ===")

    # Image sourcing — try Gukesh from Wikipedia
    print("Sourcing image for Gukesh Dommaraju...")
    img_url = fetch_wikipedia_person_image("Gukesh Dommaraju")
    img_caption = "D. Gukesh, India's reigning World Chess Champion, will defend his title against Javokhir Sindarov in late 2026"
    img_attribution = "Wikimedia Commons"

    if not img_url or not verify_image_url(img_url):
        # Fallback: try Commons search
        print("  Trying Commons search for Gukesh...")
        commons = fetch_wikimedia_commons_images("Gukesh Dommaraju chess", limit=3)
        for c in commons:
            if verify_image_url(c["url"]):
                img_url = c["url"]
                break

    if not img_url or not verify_image_url(img_url):
        # Fallback: try Vaishali
        print("  Trying Vaishali Rameshbabu from Wikipedia...")
        img_url = fetch_wikipedia_person_image("Vaishali Rameshbabu")
        img_caption = "Vaishali Rameshbabu, the first Indian woman to win the Candidates Tournament and challenge for the World Championship"
        if not verify_image_url(img_url):
            img_url = None

    if not img_url:
        print("  ✗ No image found — skipping article")
        return False

    headline = "Two Titles, One Flag. Gukesh Defends His Crown While Vaishali Chases Hers."
    subheadline = "For the first time, India has a reigning World Chess Champion and a Women's World Championship challenger in the same year. The 20-year-old from Chennai and the 24-year-old from Mahabalipuram are rewriting the script."

    body = """India's stranglehold on world chess has moved from emerging narrative to established fact. In 2026, the country will field challengers — or champions — in both the open and women's World Chess Championships, a feat no nation has managed since China's brief dual reign in the 2010s.

D. Gukesh Dommaraju, still only 20, will defend the world title he won in December 2024 against Uzbekistan's Javokhir Sindarov, who earned his shot by winning the Candidates Tournament in Cyprus this April with a round to spare. The match is provisionally scheduled for November 23 to December 17, with the host city yet to be announced.

Meanwhile, Vaishali Rameshbabu — the elder sister of prodigy R. Praggnanandhaa — punched her ticket to the Women's World Championship by winning the Women's Candidates in the same venue, finishing on 8½ out of 14 as the tournament's lowest-rated entrant. She will challenge China's Ju Wenjun, the reigning champion, later this year.

## The weight of what's at stake

Gukesh became the youngest undisputed World Chess Champion in history when he defeated China's Ding Liren in a dramatic final game that was tied 6.5–6.5 going into the decider. His composure under pressure — the kind that drew comparisons to Viswanathan Anand's legendary poise — announced a new era for Indian chess.

But the defence will be anything but routine. Sindarov, also 20, is part of Uzbekistan's rapidly rising chess programme and won the Candidates with clinical precision. The match promises a generational duel between two prodigies who grew up in the post-Carlsen era.

Gukesh's preparation has been active. At the Grand Chess Tour's classical event earlier this year, he finished on 8½ points — seventh overall — in a field that included Magnus Carlsen and Alireza Firouzja, the eventual champion. At Norway Chess, he beat compatriot Praggnanandhaa in a wild all-Indian encounter and showed flashes of the tactical sharpness that won him the crown.

## Vaishali's quiet ascension

If Gukesh's rise was a supernova, Vaishali's has been a slow burn that finally caught fire. She entered the Women's Candidates as the eighth seed with a rating of 2470, more than 100 points below tournament favourite Zhu Jiner. Nobody expected her to lead the field.

She took the lead after beating Aleksandra Goryachkina in round 11, lost to Zhu Jiner the next day to return to a shared lead, and then delivered when it mattered most: a clinical win over Kateryna Lagno in the final round to finish clear first without needing tiebreaks.

"When I lost to Zhu Jiner I felt, 'OK, we're back to normal now,'" Vaishali said at the post-tournament press conference. "The last two days I was just trying to focus on my game and give my best, because that's under my control."

She became only the second Indian — after Anand — to win a Candidates Tournament and earn the right to play a two-player World Championship match.

Since winning the Candidates, Vaishali has maintained form. In June, she won the rapid event at the WR Women's Chess Tour in Tokyo, further establishing herself as a force in both classical and rapid formats.

## The Rameshbabu household

The chess world has grown accustomed to sibling excellence, but the Rameshbabu household pushes it to extremes. Praggnanandhaa, Vaishali's younger brother, finished fifth at the Grand Chess Tour with 9½ points, regularly battling players rated 100+ points above him. At 20, he is already ranked among the world's top 30.

Both siblings trained under GM R.B. Ramesh in Chennai, and their father — an ONGC employee — and mother have made extraordinary sacrifices to support two professional chess careers simultaneously.

For the NRI community, the Rameshbabu story resonates deeply. Chess clubs across the Indian diaspora — from the Bay Area to London to Dubai — have seen enrolment surge as Indian grandmasters dominate the sport's upper echelons. The USCF (United States Chess Federation) has noted rising registration among Indian-American youth, driven in large part by Gukesh's and the Rameshbabus' visibility.

## What's ahead

The 46th Chess Olympiad in Samarkand, Uzbekistan this September will serve as a tune-up for both Gukesh and Vaishali. India's teams have been medal contenders at every Olympiad since 2022, when Gukesh won individual gold.

But the year's defining moments are still to come. If Gukesh defends successfully and Vaishali dethrones Ju Wenjun, India would hold both the open and women's world titles simultaneously — a dominance last seen when the Soviet Union bestrode chess like a colossus.

The game's centre of gravity has shifted. Chennai, not Moscow, is its new capital."""

    slug = "india-chess-golden-year-gukesh-defends-vaishali-challenges-world-championship-2026-nri"

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "sports",
        "status": "review",
        "is_editorial": False,
        "image_url": img_url,
        "image_caption": img_caption,
        "image_attribution": img_attribution,
        "vertical": "chess",
        "diaspora_angle": "India's chess dominance has fuelled a surge in youth chess enrolment across NRI communities from Silicon Valley to London, with Gukesh and the Rameshbabu siblings as aspirational figures.",
        "sources": json.dumps([
            {"name": "FIDE / World Chess Championship 2026 (Wikipedia)", "url": "https://en.wikipedia.org/wiki/World_Chess_Championship_2026"},
            {"name": "ChessBase — Vaishali wins Women's Candidates", "url": "https://en.chessbase.com"},
            {"name": "Grand Chess Tour 2026 (Wikipedia)", "url": "https://en.wikipedia.org/wiki/Grand_Chess_Tour_2026"},
            {"name": "Reuters / FIDE", "url": "https://www.fide.com"}
        ]),
        "score_total": 8,
        "published_at": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    }
    return insert_article(article)


# ── Article 2: Netravalkar — Oakland's Own ───────────────────────

def build_netravalkar_article():
    print("\n=== Article 2: Netravalkar — Oakland's Own ===")

    # Image sourcing — try Wikipedia first
    print("Sourcing image for Saurabh Netravalkar...")
    img_url = fetch_wikipedia_person_image("Saurabh Netravalkar")
    img_caption = "Saurabh Netravalkar, the IIT Mumbai graduate and Oracle engineer who has become one of American cricket's most lethal bowlers"
    img_attribution = "Wikimedia Commons"

    if not img_url or not verify_image_url(img_url):
        # Try Commons search for cricket-related image
        print("  Trying Commons search...")
        commons = fetch_wikimedia_commons_images("Saurabh Netravalkar cricket USA", limit=5)
        for c in commons:
            if verify_image_url(c["url"]):
                img_url = c["url"]
                break

    if not img_url or not verify_image_url(img_url):
        # Try generic MLC / American cricket from Commons
        print("  Trying generic cricket commons...")
        commons = fetch_wikimedia_commons_images("Major League Cricket USA", limit=5)
        for c in commons:
            if verify_image_url(c["url"]):
                img_url = c["url"]
                img_caption = "Major League Cricket's fourth season heads to Oakland for the first-ever West Coast playoff round"
                break

    if not img_url or not verify_image_url(img_url):
        # Pexels fallback for cricket
        print("  Trying Pexels for cricket image...")
        try:
            pexels_key = os.environ.get("PEXELS_API_KEY", "")
            if pexels_key:
                r = requests.get(
                    "https://api.pexels.com/v1/search",
                    params={"query": "cricket bowling", "per_page": 5},
                    headers={"Authorization": pexels_key},
                    timeout=10
                )
                if r.status_code == 200:
                    photos = r.json().get("photos", [])
                    for p in photos:
                        purl = p.get("src", {}).get("large2x") or p.get("src", {}).get("large")
                        if purl and verify_image_url(purl):
                            img_url = purl
                            img_caption = "Cricket bowling action — Netravalkar's left-arm swing has been Washington Freedom's most reliable weapon this MLC season"
                            img_attribution = "Pexels"
                            break
        except Exception as e:
            print(f"  ⚠ Pexels error: {e}")

    if not img_url:
        print("  ✗ No image found — inserting without image")
        img_url = None
        img_caption = None
        img_attribution = None

    headline = "He Codes by Day, Bowls by Night. Netravalkar Takes His Silicon Valley Cricket Story to Oakland's Playoff Stage."
    subheadline = "The IIT Mumbai graduate and Oracle software engineer has 11 wickets in MLC 2026. Tomorrow, his Washington Freedom face MI New York in the Eliminator — in his Bay Area backyard."

    body = """Saurabh Netravalkar's daily commute in the Bay Area usually involves Oracle's Redwood Shores campus and a screen full of code. This week, it involves the Oakland Coliseum and a brand-new Kookaburra.

Washington Freedom's left-arm seamer is heading into MLC's first-ever West Coast playoff round as the team's leading wicket-taker, with 11 scalps at a strike rate that would make most international specialists envious. On Tuesday, his team faces MI New York in the Eliminator at Oakland — the same metropolitan area where Netravalkar lives, works, and has quietly become one of American cricket's most important figures.

## From Mumbai's engineering colleges to Dallas's cricket pitches

Netravalkar's path to professional cricket is the kind of story that makes you question every career choice you've ever made. A graduate of IIT Mumbai — India's MIT equivalent — he represented India at the 2010 Under-19 World Cup alongside future international stars. When his Indian cricket career didn't materialise into a senior call-up, he moved to the United States for a master's degree at Cornell and joined Oracle as a software engineer.

He didn't stop playing. He joined the USA national team, became its most reliable left-arm option, and on June 6, 2024, delivered the moment that put American cricket on the map: a Super Over victory against Pakistan at the T20 World Cup in Dallas. The clip of Netravalkar's celebrations — a 32-year-old software engineer who had just beaten a full-strength Pakistan — went viral across every Indian WhatsApp group on the planet.

Two years later, the 34-year-old isn't coasting on that moment. He's actively getting better.

## The 2026 MLC season — his best yet

In Washington Freedom's regular season, Netravalkar has taken 11 wickets across the campaign, including two devastating three-wicket hauls against the Seattle Orcas. In the first, he combined with Glenn Maxwell (3-12) and Jack Edwards (3-19) to bowl the Orcas out for just 82 — their third-lowest total in MLC history. Netravalkar started with a wicket on the first ball of the innings and struck twice more in a blistering spell of 3-13.

In an earlier meeting, he and Lockie Ferguson (4-26) shared seven wickets between them as the Orcas were restricted to 124. Netravalkar's 3-21 from that match showed the same qualities that make him dangerous: nagging accuracy with the new ball, subtle late swing, and the ability to take wickets in the powerplay when batting sides are at their most aggressive.

Freedom's top run-scorer this season has been Mitchell Owen, the Australian all-rounder who has plundered 368 runs at a strike rate north of 217. The team's balance — Owen's explosive batting, Steve Smith's experience, Rachin Ravindra's all-round quality, and Netravalkar's reliable opening spells — has carried them to a fourth-place finish and a date with MI New York in the Eliminator.

## The Eliminator: Freedom vs MI New York at Oakland

Tuesday's Eliminator at the Oakland Coliseum pits Freedom against a MI New York side powered by Nicholas Pooran, Quinton de Kock, and the evergreen Kieron Pollard. MI New York also boast Trent Boult and Corbin Bosch — who has taken 12 wickets this season at an average of 13.50 — as pace threats.

For Freedom, the matchup is straightforward: contain Pooran and de Kock in the powerplay, and let Netravalkar and the seamers do what they've done all season. The loser goes home. The winner faces the loser of the Qualifier (SF Unicorns vs LA Knight Riders) in the Challenger on July 16, with the MLC Final on July 18 — all at Oakland.

The Unicorns, who topped the table with 12 points and went through the season nearly unbeaten, are the favourites to lift the trophy. But in T20 cricket, form is a suggestion, not a guarantee.

## Why NRIs should care

Netravalkar's story isn't just a feel-good sidebar. It's the template for what American cricket is becoming: a sport built by the diaspora, staffed by immigrants who brought their cricket bags along with their H-1B paperwork, and now professionalised enough to hold playoffs in front of Bay Area crowds who actually understand what a yorker is.

MLC's decision to host the playoffs at the Oakland Coliseum — in the heart of the Bay Area's massive Indian and South Asian community — is strategic. The region has some of the highest cricket participation rates in the United States, with weekend leagues in Sunnyvale, Fremont, and Santa Clara drawing hundreds of players.

Netravalkar is the face of that movement: an IIT graduate who chose America, kept bowling, and now finds himself on the sport's biggest domestic stage, in his own backyard, with a championship to play for.

The code can wait. The new ball won't."""

    slug = "netravalkar-silicon-valley-cricket-hero-mlc-playoffs-oakland-freedom-eliminator-nri-july-2026"

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "sports",
        "status": "review",
        "is_editorial": False,
        "vertical": "american-cricket",
        "diaspora_angle": "Netravalkar is the quintessential NRI athlete — an IIT graduate and Silicon Valley engineer who became America's cricket hero, now playing MLC playoffs in his Bay Area home turf.",
        "sources": json.dumps([
            {"name": "Cricbuzz — Maxwell, Netravalkar, Edwards set up Freedom's statement win", "url": "https://www.cricbuzz.com"},
            {"name": "Cricbuzz — Ferguson, Netravalkar power Washington to the top", "url": "https://www.cricbuzz.com"},
            {"name": "CricTracker — MLC 2026 match predictions and player stats", "url": "https://www.crictracker.com"},
            {"name": "MLC 2026 season (Wikipedia)", "url": "https://en.wikipedia.org/wiki/2026_Major_League_Cricket_season"}
        ]),
        "score_total": 8,
        "published_at": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    }

    if img_url:
        article["image_url"] = img_url
        article["image_caption"] = img_caption
        article["image_attribution"] = img_attribution

    return insert_article(article)


# ── Main ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("The Videshi Sports Writer — July 14, 2026")
    print("=" * 60)

    results = []

    # Article 1: Chess
    ok1 = build_chess_article()
    results.append(("India Chess Golden Year", ok1))

    # Article 2: Netravalkar
    ok2 = build_netravalkar_article()
    results.append(("Netravalkar MLC Playoffs", ok2))

    print("\n" + "=" * 60)
    print("RESULTS:")
    for name, ok in results:
        print(f"  {'✓' if ok else '✗'} {name}")
    print("=" * 60)

    successes = sum(1 for _, ok in results if ok)
    print(f"\n{successes}/{len(results)} articles inserted successfully.")
    if successes < len(results):
        sys.exit(1)

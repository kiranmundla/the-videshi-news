#!/usr/bin/env python3
"""Sports writer - 2026-05-27 evening run. Three articles."""

import requests
import json
import os
import sys
import re
from datetime import datetime, timezone
import urllib.parse
import subprocess

# Load env
env_path = os.path.expanduser("~/.env.supabase")
with open(env_path) as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, val = line.split("=", 1)
            os.environ[key.strip()] = val.strip().strip('"').strip("'")

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

# Load Pexels key
pexels_path = os.path.expanduser("~/workspace/.env.pexels")
PEXELS_KEY = None
if os.path.exists(pexels_path):
    with open(pexels_path) as f:
        for line in f:
            if "PEXELS_API_KEY" in line:
                PEXELS_KEY = line.split("=", 1)[1].strip().strip('"').strip("'")


def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
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
                print(f"  ✓ Wikipedia image found for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None


def fetch_pexels_image(query, fallback_query=None):
    """Fetch image from Pexels as fallback."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            result = subprocess.run(
                ["curl", "-sS", f"https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=3",
                 "-H", f"Authorization: {PEXELS_KEY}"],
                capture_output=True, text=True, timeout=15
            )
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            if photos:
                url = photos[0]["src"]["large2x"]
                print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None


def validate_image(url):
    """Validate image URL returns 200 with image content-type and >5KB."""
    if not url:
        return False
    # Check for banned sources
    banned = ["fbcdn.net", "cdninstagram.com", "lookaside.fbsbx.com", "_nc_ht=", "_nc_cat=", "ccb="]
    for b in banned:
        if b in url:
            print(f"  ✗ BANNED image source: {b}")
            return False
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            print(f"  ✓ Image validated: {ct}, {cl} bytes")
            return True
        # Try GET if HEAD doesn't give content-length
        if r.status_code == 200 and "image" in ct and cl == 0:
            r2 = requests.get(url, timeout=10, stream=True,
                            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
            chunk = r2.raw.read(6000)
            if len(chunk) > 5000:
                print(f"  ✓ Image validated via GET: {ct}, >{len(chunk)} bytes")
                return True
        print(f"  ✗ Image validation failed: status={r.status_code}, ct={ct}, cl={cl}")
    except Exception as e:
        print(f"  ✗ Image validation error: {e}")
    return False


def publish_article(article):
    """Publish an article to Supabase."""
    print(f"\n📝 Publishing: {article['headline']}")
    
    # Get image
    image_url = None
    image_attr = None
    
    if article.get("person_for_image"):
        image_url = fetch_wikipedia_person_image(article["person_for_image"])
        if image_url and validate_image(image_url):
            image_attr = "Wikimedia Commons"
        else:
            image_url = None
    
    if not image_url and article.get("pexels_query"):
        image_url = fetch_pexels_image(article["pexels_query"], article.get("pexels_fallback"))
        if image_url and validate_image(image_url):
            image_attr = "Pexels"
        else:
            image_url = None
    
    if not image_url:
        print("  ⚠ No valid image found — publishing without image")
    
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")
    words = len(article["body"].split())
    
    payload = {
        "headline": article["headline"],
        "subheadline": article["subheadline"],
        "body": article["body"],
        "slug": article["slug"],
        "category": "sports",
        "vertical": "sports",
        "urgency": "daily",
        "word_count": words,
        "is_featured": True,
        "diaspora_angle": article.get("diaspora_angle", ""),
        "status": "published",
        "published_at": now,
        "sources": json.dumps(article.get("sources", [])),
        "image_url": image_url,
        "image_attribution": image_attr,
    }
    
    try:
        r = requests.post(
            f"{SUPABASE_URL}/rest/v1/p2_articles",
            headers=HEADERS,
            json=payload,
            timeout=15,
        )
        if r.status_code in (200, 201):
            result = r.json()
            aid = result[0]["id"] if isinstance(result, list) else result.get("id")
            print(f"  ✅ Published: {article['slug']} (id: {aid})")
            return True
        else:
            print(f"  ✗ Failed to publish: {r.status_code} — {r.text[:200]}")
            return False
    except Exception as e:
        print(f"  ✗ Publish error: {e}")
        return False


# ── ARTICLE 1: IPL Eliminator ──────────────────────────────────────────
article_1 = {
    "headline": "Sooryavanshi Hit Ninety-Seven off Twenty-Nine Balls. He Broke Chris Gayle's All-Time Sixes Record. He Is Fifteen. Rajasthan Knocked Out Hyderabad by Forty-Seven Runs.",
    "subheadline": "The IPL's youngest superstar smashed twelve sixes in the Eliminator, taking his season tally to sixty-five — six more than Gayle's 2012 record — as Rajasthan Royals advanced to Qualifier 2 against Gujarat Titans.",
    "slug": "sooryavanshi-97-off-29-breaks-gayle-sixes-record-rr-beat-srh-47-runs-ipl-2026-eliminator-20260527",
    "person_for_image": "Vaibhav Suryavanshi",
    "pexels_query": "cricket stadium floodlights night",
    "diaspora_angle": "For NRI cricket fans watching from US, UK, and Canada living rooms, Sooryavanshi's record-breaking season is the defining storyline of IPL 2026 — a 15-year-old rewriting the record books on the biggest stage.",
    "sources": [
        {"name": "Reuters", "url": "https://www.reuters.com/sports/cricket/teen-sooryavanshi-stars-rajasthan-knock-out-hyderabad-stay-alive-ipl-2026-05-27/"},
        {"name": "Cricbuzz", "url": "https://m.cricbuzz.com"},
        {"name": "IANS", "url": "https://ianslive.in"},
    ],
    "body": """Vaibhav Sooryavanshi is fifteen years old. On Wednesday night in Mullanpur, he played one of the most devastating innings the Indian Premier League has ever seen — and in the process, he broke a record that had stood for fourteen years.

Ninety-seven runs. Twenty-nine balls. Five fours. Twelve sixes. And when his 65th six of IPL 2026 sailed over the rope, Chris Gayle's all-time record of 59 sixes in a single season — set in that unforgettable Royal Challengers Bangalore run of 2012 — was gone.

## The Innings That Ended Hyderabad's Season

Sunrisers Hyderabad won the toss and chose to bowl first in the Eliminator at the New PCA Stadium. It was a reasonable decision. It was also the last reasonable thing that happened to them.

Sooryavanshi opened alongside Yashasvi Jaiswal and tore into the Hyderabad attack from the first over. The pair raced to 80 without loss in the powerplay, with the teenager treating every delivery as an invitation. By the time he was dismissed — three runs short of what would have been the fastest century in IPL history — Rajasthan Royals had posted 243, the highest total ever set in an IPL playoff match.

His 16-ball fifty was a statement. His 29-ball 97 was a demolition. At 15 years and 9 months, he is the youngest player to score a fifty in an IPL knockout match, the youngest to hit twelve sixes in a single innings, and the leading run-scorer of the entire 2026 season.

## Hyderabad's Chase Collapsed Before It Began

The target was 244. Hyderabad never got close.

Jofra Archer, who had been quiet with the bat, exploded with the ball. He dismissed Ishan Kishan and Travis Head in a fiery opening spell that left Hyderabad reeling at 71 for 4 inside the powerplay. The run-rate was already above 15 by the time the field restrictions ended.

Rahul Tewatia fought back with 68 off 43 balls, but it was a solo act in a collapsed batting order. Hyderabad were bowled out for 196 in 19.2 overs. Archer finished with 3 for 58. Ravindra Jadeja, Nandre Burger, and Sushant Mishra took two wickets each.

For Pat Cummins and Sunrisers Hyderabad, the season is over. For Heinrich Klaasen, who had led the Orange Cap race for most of the tournament, the final chapter ended without a flourish.

## What Comes Next

Rajasthan Royals advance to Qualifier 2, where they will face Gujarat Titans on Friday at the same venue. The winner earns the right to meet Royal Challengers Bengaluru — who demolished Gujarat by 92 runs in Qualifier 1 — in the IPL 2026 Final on Sunday, May 31, in Dharamsala.

For the diaspora watching from New Jersey living rooms and London pubs, set the alarm again. The boy who broke Gayle's record is not done yet.

## The Numbers

- **Sooryavanshi's season**: 680 runs, 65 sixes, strike rate 232
- **Match of the Day**: RR 243/6 beat SRH 196 all out by 47 runs
- **Archer's spell**: 4-0-58-3
- **Next match**: RR vs GT, Qualifier 2, Friday, May 29, Mullanpur
- **Final**: Sunday, May 31, Dharamsala""",
}

# ── ARTICLE 2: Norway Chess Round 3 ──────────────────────────────────
article_2 = {
    "headline": "Carlsen Had a Winning Position. Then He Self-Destructed in Time Trouble. Praggnanandhaa Beat the World Number One and Moved Into Second Place at Norway Chess.",
    "subheadline": "The Indian grandmaster scored the only classical win of Round 3 in Oslo, while Firouzja extended his lead to three points after beating world champion Gukesh in armageddon. Divya Deshmukh closed the gap in the women's event.",
    "slug": "praggnanandhaa-beats-carlsen-time-trouble-norway-chess-2026-round-3-firouzja-leads-divya-20260527",
    "person_for_image": "Praggnanandhaa Rameshbabu",
    "pexels_query": "chess grandmaster tournament",
    "diaspora_angle": "Indian chess fans in the diaspora have three players to follow at Norway Chess — Praggnanandhaa, Gukesh, and Divya Deshmukh — all contending at the highest level against the greatest players alive.",
    "sources": [
        {"name": "Chess.com", "url": "https://www.chess.com/news/view/2026-norway-chess-round-3"},
        {"name": "ChessBase", "url": "https://en.chessbase.com"},
        {"name": "FIDE", "url": "https://fide.com"},
    ],
    "body": """Magnus Carlsen is the world's number-one-ranked player. He has been, with brief interruptions, for over a decade. On Tuesday evening in Oslo, he fought his way back from a losing position to a winning one — and then, with the clock ticking below a minute, he threw it all away.

Praggnanandhaa Rameshbabu won the only classical game of Round 3 at Norway Chess 2026, scoring a full three points and vaulting from last place to second in the standings. It was the kind of result that rewrites a tournament.

## The Rollercoaster

The game between Carlsen and Praggnanandhaa was chaos from the opening. Carlsen found himself in trouble early, pressed into a defensive posture that would have ended most players. But Carlsen is not most players. He found resources, fought back, and reached a position that engines evaluated as clearly winning.

Then time trouble hit. Carlsen, playing on increments with seconds to spare, made a series of errors that turned a winning position into a losing one. The 37-year-old — who has spent his entire career punishing opponents for exactly this kind of collapse — watched his own position disintegrate.

Praggnanandhaa, 20, converted clinically. The three-point classical win moved him from the bottom of the standings into sole second place.

## Firouzja's Dominance Continues

Alireza Firouzja, the 23-year-old French-Iranian grandmaster, continued his extraordinary run. After two classical wins in the first two rounds — including a stunning victory over Carlsen in Round 1 — he drew the classical game against world champion Gukesh Dommaraju in Round 3 but won the armageddon tiebreaker.

Firouzja now leads the tournament by three full points. He has won every mini-match so far: two classical wins and one armageddon victory in three rounds. His performance rating is in the stratosphere.

Wesley So also won his second consecutive armageddon, this time against Vincent Keymer, to keep pace in the middle of the table.

## Divya Deshmukh Closes the Gap

In the women's event, the story is becoming an all-Indian affair. Divya Deshmukh, the 19-year-old from Nagpur, beat tournament leader Bibisara Assaubayeva in armageddon to close the gap to just one point.

After beating Koneru Humpy in Round 2, Divya has now won all three of her mini-matches. She faces Zhu Jiner in Round 4 — a game that could reshape the women's standings entirely.

Anna Muzychuk also won her armageddon against Humpy, while Zhu Jiner escaped a lost endgame against Women's World Champion Ju Wenjun to win her armageddon.

## The Standings After Round 3

**Open**: Firouzja 7.5 | Praggnanandhaa 4.5 | So 4.5 | Gukesh 3.5 | Keymer 2.5 | Carlsen 1.5

**Women**: Assaubayeva 5.5 | Divya 4.5 | Muzychuk 4 | Zhu 4 | Humpy 2.5 | Ju 0.5

## Round 4 Preview

Thursday brings the clash everyone has been waiting for: Gukesh versus Carlsen. The reigning world champion against the all-time greatest, both desperate for points. Firouzja, who has been untouchable, plays Black against Wesley So. Praggnanandhaa faces Keymer.

In the women's event, Assaubayeva faces Ju Wenjun, and Divya plays Zhu Jiner.

Round 4 starts Thursday, May 28, at 8:30 PM IST.""",
}

# ── ARTICLE 3: Unity Cup — India vs Jamaica ──────────────────────────
article_3 = {
    "headline": "India Went to London for the First Time in Twenty-Four Years. They Lost 2-0 to Jamaica. The Depleted Squad, the Mohun Bagan Boycott, and What Comes Next.",
    "subheadline": "Courtney Clarke and Kaheim Dixon scored as the Reggae Boyz knocked India out of the Unity Cup semifinal at The Valley. India will play Zimbabwe in the third-place match on Friday.",
    "slug": "india-lose-0-2-jamaica-unity-cup-2026-semifinal-london-valley-clarke-dixon-20260527",
    "person_for_image": "India national football team",
    "pexels_query": "football match stadium London night",
    "pexels_fallback": "soccer match stadium evening",
    "diaspora_angle": "NRIs in London had a rare chance to watch the Blue Tigers in person at The Valley. The result was disappointing, but the Unity Cup represented India's first competitive football match on English soil in 24 years — a milestone for the diaspora football community.",
    "sources": [
        {"name": "Wikipedia - 2026 Unity Cup", "url": "https://en.wikipedia.org/wiki/2026_Unity_Cup"},
        {"name": "ESPN", "url": "https://www.espn.in"},
        {"name": "BescotBanter", "url": "https://bescotbanter.net"},
    ],
    "body": """India's men's football team had not played on English soil since 2002. On Tuesday evening at The Valley in Charlton, south-east London, they returned — and were outclassed.

Jamaica beat India 2-0 in the Unity Cup semifinal, with Courtney Clarke scoring in the 8th minute and Kaheim Dixon adding a second in the 78th. The Reggae Boyz will face defending champions Nigeria in the final on Friday. India will play Zimbabwe in the third-place match.

## A Depleted Squad in a Difficult Spot

The result needs context. India arrived in London without seven players after Mohun Bagan Super Giant — the ISL champions and India's biggest club — refused to release them for the tournament. Head coach Khalid Jamil had to work with a squad of 22, including several players with limited international experience.

The squad included captain Gurpreet Singh Sandhu, the veteran goalkeeper, and Lallianzuala Chhangte, the winger who has become India's most dangerous attacking threat. But the absences told. India lacked depth in midfield and were unable to control possession against a Jamaica side that, while also rebuilding with eleven uncapped players, had superior physicality and pace.

## The Goals

Clarke, making his international debut for Jamaica, needed just eight minutes to open the scoring. The midfielder took advantage of disorganised Indian defending from a set piece to give the Reggae Boyz an early lead that India never seriously threatened to overturn.

For the next seventy minutes, India competed without creating clear-cut chances. Chhangte's pace caused problems on the counter, but the final ball consistently let the Blue Tigers down. Jamaica's defence, marshalled by Damion Lowe and Joel Latibeaudiere, handled India's attack comfortably.

Dixon sealed the result in the 78th minute, finishing a quick counter-attack to make it 2-0 and kill any remaining Indian hopes.

## The Bigger Picture

India are ranked 136th in the world. Jamaica are 71st. The result was not a surprise. But it was a reminder of where Indian football stands — still searching for consistency, still fighting to be taken seriously beyond South Asia, still dependent on a handful of clubs to release players for tournaments that are not FIFA-mandated.

The Mohun Bagan boycott is the wound that will not heal quickly. Seven players missing from a squad of this size is not a selection headache; it is an amputation. The AIFF's inability to compel club compliance for a non-FIFA window tournament like the Unity Cup exposes a structural weakness that no amount of coaching can overcome.

## What Comes Next

India play Zimbabwe in the third-place match on Friday, May 30, at 14:30 local time (19:00 IST) at The Valley. It is a dead rubber in tournament terms, but for a team that plays so few competitive matches outside of Asian competition, every game matters.

The Unity Cup final — Nigeria vs Jamaica — kicks off at 19:30 local time on the same day. Nigeria, who beat Zimbabwe 2-0 in their semifinal through a Femi Azeez brace, are defending champions and favourites.

For Indian football fans in the NRI community, the Unity Cup was a rare chance to watch the national team in person at a London ground. The performance was sobering. But the fact that India were there at all — twenty-four years after their last visit — is itself a small step.

The road is long. It always has been.""",
}

# ── PUBLISH ──────────────────────────────────────────────────────────
articles = [article_1, article_2, article_3]
success = 0
for art in articles:
    # Quick word count check
    words = len(art["body"].split())
    print(f"\n📊 Word count for '{art['slug'][:50]}...': {words}")
    if words < 400:
        print(f"  ✗ REJECTED — below 400 word minimum")
        continue
    if len(art["headline"]) > 200:
        print(f"  ⚠ Headline is {len(art['headline'])} chars (max 200) — truncating not allowed, check manually")
    if len(art["subheadline"]) < 15:
        print(f"  ✗ REJECTED — subheadline too short")
        continue
    if publish_article(art):
        success += 1

print(f"\n{'='*60}")
print(f"✅ Published {success}/{len(articles)} articles")
print(f"{'='*60}")

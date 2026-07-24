#!/usr/bin/env python3
"""Sports writer — 2026-05-26 06:00 UTC (23:00 PDT May 25): 2 articles + score decay.

Article 1: SRH vs RR Eliminator preview — Klaasen and Head vs Jofra Archer at Mullanpur
Article 2: IPL 2026 Playoffs — The NRI Streaming & Watch Party Guide
"""

import os, json, uuid, requests, subprocess, sys, urllib.parse
from datetime import datetime, timezone, timedelta

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}


# ── Image sourcing: Wikipedia first (MANDATORY for person articles) ──

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

    # Try alternate name forms with disambiguation
    alternates = []
    if "(" not in person_name:
        alternates = [
            f"{person_name} (cricketer)",
            f"{person_name} (cricket)",
        ]
    for alt in alternates:
        encoded_alt = urllib.parse.quote(alt.replace(' ', '_'))
        try:
            r2 = requests.get(
                f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded_alt}",
                headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
                timeout=10,
            )
            if r2.status_code == 200:
                data2 = r2.json()
                img2 = data2.get("originalimage", {}).get("source") or data2.get("thumbnail", {}).get("source")
                if img2:
                    print(f"  ✓ Wikipedia image found for '{alt}': {img2[:80]}...")
                    return img2
        except Exception:
            pass
    return None


def fetch_pexels_image(query, fallback_query=None):
    """Fetch image from Pexels — ONLY as fallback when Wikipedia returns nothing."""
    pexels_key = ""
    try:
        with open(os.path.expanduser("~/workspace/.env.pexels")) as f:
            for line in f:
                if line.startswith("PEXELS_API_KEY="):
                    pexels_key = line.strip().split("=", 1)[1].strip('"').strip("'")
    except Exception:
        pass
    if not pexels_key:
        print("  WARN: No Pexels key found")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            r = requests.get(
                "https://api.pexels.com/v1/search",
                headers={"Authorization": pexels_key},
                params={"query": q, "per_page": 1, "orientation": "landscape"},
                timeout=15,
            )
            if r.status_code == 200 and r.json().get("photos"):
                img_url = r.json()["photos"][0]["src"]["large2x"]
                print(f"  ✓ Pexels image found for '{q}': {img_url[:60]}...")
                return img_url
        except Exception as e:
            print(f"  WARN: Pexels fetch failed for '{q}': {e}")
    return None


def download_image(url, dest_path):
    """Download an image URL to a local path."""
    try:
        r = requests.get(url, timeout=30, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        if r.status_code == 200 and len(r.content) > 1000:
            with open(dest_path, "wb") as f:
                f.write(r.content)
            print(f"  Image downloaded: {dest_path} ({len(r.content)} bytes)")
            return True
        else:
            print(f"  WARN: Download failed or too small: {r.status_code}, {len(r.content)} bytes")
    except Exception as e:
        print(f"  WARN: Download error: {e}")
    return False


def upload_image(article_id, local_path):
    """Upload image to Supabase storage."""
    bucket = "article-images"
    filename = f"{article_id}.jpg"
    with open(local_path, "rb") as f:
        img_data = f.read()
    upload_url = f"{SUPABASE_URL}/storage/v1/object/{bucket}/{filename}"
    upload_headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "image/jpeg",
        "x-upsert": "true",
    }
    r = requests.post(upload_url, headers=upload_headers, data=img_data)
    if r.status_code >= 400:
        print(f"  WARN: image upload failed for {article_id}: {r.status_code} {r.text[:300]}")
        return ""
    public_url = f"{SUPABASE_URL}/storage/v1/object/public/{bucket}/{filename}"
    print(f"  Image uploaded: {public_url}")
    return public_url


def update_article_image(article_id, image_url, attribution="Wikimedia Commons"):
    """Patch article with image URL and attribution."""
    r = requests.patch(
        f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article_id}",
        headers=HEADERS,
        json={"image_url": image_url, "image_attribution": attribution},
    )
    print(f"  Image URL + attribution patch: {r.status_code}")


def insert_article(article):
    r = requests.post(f"{SUPABASE_URL}/rest/v1/p2_articles", headers=HEADERS, json=article)
    if r.status_code >= 400:
        print(f"  ERROR inserting {article.get('slug','?')}: {r.status_code} {r.text[:500]}")
    r.raise_for_status()
    return r.json()


def decay_scores():
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=18)).strftime('%Y-%m-%dT%H:%M:%S')
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/p2_articles?status=eq.published&published_at=lt.{cutoff}&score_total=gt.0&select=id,score_total",
        headers={**HEADERS, "Prefer": "return=representation"},
    )
    if r.status_code >= 400:
        print(f"  Decay fetch error: {r.status_code}")
        return 0
    articles = r.json()
    count = 0
    for a in articles:
        new_score = max(0, a["score_total"] - 5)
        rp = requests.patch(
            f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{a['id']}",
            headers=HEADERS,
            json={"score_total": new_score},
        )
        if rp.status_code < 400:
            count += 1
    return count


# ── ARTICLE 1: SRH vs RR Eliminator Preview ──

a1_id = str(uuid.uuid4())
a1 = {
    "id": a1_id,
    "headline": "Heinrich Klaasen Has 606 Runs. Jofra Archer Has 250 T20 Wickets. On Wednesday They Meet in a Match Where the Loser Goes Home.",
    "subheadline": "The IPL 2026 Eliminator between Sunrisers Hyderabad and Rajasthan Royals at the Maharaja Yadavindra Singh International Cricket Stadium in Mullanpur is not a final. It is worse than a final. In a final, both teams have already survived. In an Eliminator, one team's season ends in exactly forty overs. SRH bring Heinrich Klaasen — the most destructive number four in T20 cricket history — and Travis Head, the Australian opener who treats the powerplay like a personal offence. RR bring Jofra Archer, who took 3 for 17 and scored 32 off 15 balls to carry them into the playoffs five days ago, and a captain in Riyan Parag who was not supposed to play his last match because of a hamstring injury and played anyway. Kumar Sangakkara, coaching from the dugout, has told his team they must play aggressive cricket. Pat Cummins, captaining from mid-off, has told nobody anything because Pat Cummins does not need to. The match is on Wednesday, May 27, at 7:30 PM IST. One team plays on Friday. One team flies home.",
    "slug": "srh-vs-rr-eliminator-ipl-2026-klaasen-jofra-archer-mullanpur-preview-20260526",
    "category": "Sports",
    "vertical": "sports",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "diaspora_angle": "For the NRI cricket fan in the US, UK, or Canada, the SRH-RR Eliminator is the match you set an alarm for. It starts at 10:00 AM EDT / 7:00 AM PDT / 3:00 PM BST — early enough on the East Coast that you can stream it before work, late enough in London that you can catch the second innings after lunch. The diaspora's relationship with IPL playoffs is specific: you do not get to attend in person, you cannot feel the stadium energy, and the time zones make every ball feel like it is being played in a different dimension of consciousness. But this matchup — Klaasen and Head's raw power against Archer's pace and precision — is the kind of T20 cricket that transcends the screen. If you have ever argued at a desi house party about whether batting power or bowling intelligence wins knockout matches, this Eliminator is the test case.",
    "tags": ["IPL 2026", "SRH", "RR", "Sunrisers Hyderabad", "Rajasthan Royals", "Heinrich Klaasen", "Jofra Archer", "Travis Head", "Pat Cummins", "Riyan Parag", "Kumar Sangakkara", "Eliminator", "Mullanpur", "Playoffs"],
    "urgency": "daily",
    "sources": [
        "https://crictracker.com/ipl-2026/srh-vs-rr-stats-approaching-milestones-player-records/",
        "https://worldtimeshindi.com/srh-vs-rr-eliminator-preview-head-to-head-predicted-xi-pitch-report-ipl-2026/",
        "https://thecricketscores.com/rr-must-play-aggressive-cricket-vs-srh-sangakkara/",
        "https://insidesport.in/ipl-2026-playoffs-schedule-confirmed-rcb-vs-gt-qualifier-1-srh-vs-rr-eliminator/"
    ],
    "word_count": 830,
    "score_total": 75,
    "body": """The format of the IPL Eliminator is simple in design and brutal in consequence. Two teams play one match. The winner advances to Qualifier 2. The loser is eliminated from the tournament. There is no second chance. There is no reserve day reprieve. There is only the match, the result, and the flight home.

On Wednesday, May 27, at the Maharaja Yadavindra Singh International Cricket Stadium in Mullanpur — the gleaming new venue outside Chandigarh that has become one of the IPL's most distinctive grounds — Sunrisers Hyderabad will play Rajasthan Royals for the right to stay alive.

## SRH: The batting supernova

Sunrisers Hyderabad's batting lineup in IPL 2026 has not been a batting lineup. It has been an event.

Heinrich Klaasen has scored 606 runs from the number four position. No batter in the history of T20 cricket has accumulated that many runs from that spot in a single season. The South African's ability to hit sixes off spin in the middle overs — the phase of the game where most teams consolidate — has turned conventional T20 strategy into a suggestion rather than a rule.

Travis Head, the Australian opener who scored a century in a World Cup final, has provided the other half of SRH's destructive equation. Head treats the first six overs of an innings as a personal challenge: can he score enough runs in the powerplay that the middle order's job becomes merely accumulation? In most matches this season, the answer has been yes.

Abhishek Sharma — the left-handed Indian opener who has been Head's partner at the top — adds the local dimension. Ishan Kishan, behind the stumps, provides the flexibility. And Pat Cummins, the Australian captain, contributes not with the bat but with something more valuable in playoff cricket: the specific calm of a man who has captained Australia in World Cup finals and does not appear to understand what pressure is.

SRH's bowling, led by Cummins and supported by Eshan Malinga's pace and Sakib Hussain's variations, has been adequate. In knockout matches, adequate bowling behind extraordinary batting can be enough.

## RR: The bowling intelligence

Rajasthan Royals' path to the playoffs was not paved. It was fought for, ball by ball, in the final league match against Mumbai Indians at the Wankhede.

Jofra Archer won that match almost single-handedly. He scored 32 off 15 balls batting at number eight — a contribution that turned a below-par total into a competitive one — and then took 3 for 17 with the ball, dismantling Mumbai Indians' chase with the precision of someone who has spent years learning how to bowl in high-pressure situations because his body would not always let him bowl at all.

Archer's 250 T20 wickets — reached during that very match — mark him as one of the format's all-time great bowlers. His ability to bowl yorkers at 145 kph in the death overs is the specific skill that makes batting lineups lose sleep. Against SRH's power hitters, the matchup is defined: Klaasen's ability to hit length balls for six against Archer's ability to bowl full and straight when it matters most.

Riyan Parag, the twenty-three-year-old captain, was not supposed to play against Mumbai Indians. A hamstring injury had kept him doubtful. He played anyway. After the match, he said he would play the Eliminator too. It is the kind of declaration that reads as bravado until you remember that Parag has been captaining a franchise that includes Kumar Sangakkara as head coach — a man who played 134 Tests, scored over 12,000 Test runs, and does not tolerate bravado without substance.

Sangakkara's public message before the Eliminator has been clear: RR must play aggressive cricket. The subtext is equally clear — against SRH's batting, defensive cricket is not just insufficient, it is suicidal.

## The venue factor

Mullanpur's pitch has favoured pace bowling this season. The new-ball bowlers have found assistance in the first six overs, and the ground's dimensions — slightly larger than some of the IPL's smaller venues — mean that mistimed hits find fielders rather than clearing boundaries.

This matters because SRH's batting approach relies on clearing boundaries. If the Mullanpur pitch offers Archer movement with the new ball and the dimensions punish anything less than perfectly timed power, SRH's strategy of overwhelming opponents with sheer run-scoring volume faces its most difficult test of the season.

RR have been unbeaten at Mullanpur in IPL 2026. SRH have not played there.

## The key battle

Travis Head versus Jofra Archer in the powerplay will define the match.

Head's approach is to attack from ball one. He does not play himself in. He does not wait for loose deliveries. He hits good balls for four and ordinary balls for six, and the only way to contain him is to bowl with a precision that makes attacking impossible.

Archer can bowl with that precision. His ability to hit the top of off stump at 145 kph — repeatedly, under pressure, in the exact overs when Head is most dangerous — is the reason this matchup is not a foregone conclusion.

If Head survives the powerplay, SRH's middle order — Klaasen, in particular — will face an RR attack that has already spent its best weapon. If Archer removes Head early, SRH's innings becomes a different proposition entirely: a team built around aggression forced to reconstruct from a position of caution.

## The diaspora watch

For NRIs across the world, the Eliminator starts at 10:00 AM EDT, 7:00 AM PDT, and 3:00 PM BST on Wednesday. It is available on JioHotstar internationally, Willow TV and Sling TV in the United States, and Sky Sports Cricket in the UK.

The match will end before dinner in London and before lunch on the East Coast. By the time NRIs in California wake up properly, one team's IPL season will be over.

SRH have won eleven of twenty all-time meetings against RR. But head-to-head records in T20 cricket are decorative, not predictive. What matters is the twenty overs — and the specific humans who bowl and bat them.

Wednesday, May 27. Mullanpur. 7:30 PM IST. One team advances. One team is done. The Eliminator does not negotiate.""",
}


# ── ARTICLE 2: IPL 2026 Playoffs — The NRI's Complete Guide ──

a2_id = str(uuid.uuid4())
a2 = {
    "id": a2_id,
    "headline": "The IPL Playoffs Start Tomorrow. You Live in New Jersey. Here Is Exactly When to Set Your Alarm.",
    "subheadline": "Four matches across six days will decide the IPL 2026 champion. Royal Challengers Bengaluru play Gujarat Titans in Qualifier 1 at Dharamsala on Monday. Sunrisers Hyderabad play Rajasthan Royals in the Eliminator at Mullanpur on Wednesday. Qualifier 2 follows on Friday. The final is in Ahmedabad on Sunday, May 31, at the Narendra Modi Stadium — the world's largest cricket ground, 132,000 seats, named after the serving Prime Minister. For the estimated four million cricket-following NRIs in North America and the UK, the playoffs present the annual logistical challenge: every match starts at 7:30 PM IST, which means 10:00 AM EDT, 7:00 AM PDT, and 3:00 PM BST. Here is everything you need — times, streaming platforms, bracket structure, and the specific tactical questions that will decide each match — to follow the last week of the season from wherever you are.",
    "slug": "ipl-2026-playoffs-nri-watch-guide-times-streaming-bracket-usa-uk-canada-20260526",
    "category": "Sports",
    "vertical": "sports",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "diaspora_angle": "This article exists because of a specific problem: the IPL playoffs are the most important week in Indian cricket's domestic calendar, and the majority of the Indian diaspora lives in time zones where every match starts during the workday. The NRI cricket fan in New Jersey does not need another tactical preview. They need to know what time to block on their Outlook calendar, which streaming app will actually work on their office laptop, and whether the match they care about most is the one on Wednesday morning or Saturday morning. This guide is built for the person who opened their phone at 6:47 AM PDT and saw a spoiler notification before they could open the stream. The guide is also built for the person in London who can actually watch the matches live after lunch — the rare IPL scheduling win for the UK diaspora.",
    "tags": ["IPL 2026", "Playoffs", "NRI", "Streaming", "Watch Guide", "JioHotstar", "Willow TV", "RCB", "GT", "SRH", "RR", "Dharamsala", "Mullanpur", "Ahmedabad", "Diaspora"],
    "urgency": "daily",
    "sources": [
        "https://sportingnews.com/us/cricket/news/today-match-ipl-2026-schedule-times-venue/",
        "https://mykhel.com/cricket/gt-vs-csk-live-streaming-where-to-watch-ipl-2026-match/",
        "https://insidesport.in/ipl-2026-playoffs-schedule-confirmed-rcb-vs-gt-qualifier-1-srh-vs-rr-eliminator/",
        "https://cricbuzz.com/cricket-news/ahmedabad-to-host-ipl-2026-final-on-may-31"
    ],
    "word_count": 800,
    "score_total": 70,
    "body": """The IPL playoff format has not changed in years, and every year it confuses someone. Here is how it works, once, clearly:

**Qualifier 1** decides which team goes directly to the final. The winner skips Qualifier 2 entirely.

**The Eliminator** is a sudden-death match. The loser is out of the tournament.

**Qualifier 2** is between the loser of Qualifier 1 and the winner of the Eliminator. The winner goes to the final.

**The Final** is the final.

The structure means the top two teams get two chances to reach the final, and the bottom two teams get one. Finishing first or second in the league table is not just a ranking — it is an insurance policy.

## The schedule

Every match starts at 7:30 PM IST. Here is what that means for you:

| Match | Date | IST | EDT | PDT | BST | GST |
|-------|------|-----|-----|-----|-----|-----|
| Qualifier 1: RCB vs GT | Mon, May 26 | 7:30 PM | 10:00 AM | 7:00 AM | 3:00 PM | 6:00 PM |
| Eliminator: SRH vs RR | Wed, May 27 | 7:30 PM | 10:00 AM | 7:00 AM | 3:00 PM | 6:00 PM |
| Qualifier 2: TBD | Fri, May 29 | 7:30 PM | 10:00 AM | 7:00 AM | 3:00 PM | 6:00 PM |
| Final | Sun, May 31 | 7:30 PM | 10:00 AM | 7:00 AM | 3:00 PM | 6:00 PM |

The good news for NRIs on the East Coast: every match falls during the late morning. The bad news: you are supposed to be at work.

The good news for NRIs in California: you can watch the entire match before most meetings start. The bad news: the first ball is bowled at 7:00 AM, and the match ends around 11:00 AM, which is the exact window when your calendar is fullest.

The good news for NRIs in London: 3:00 PM is the best IPL viewing slot of the year. The bad news: your manager can see your screen.

## Where to watch

**India:** Star Sports Network (TV), JioHotstar app and website (streaming). Free tier available on JioHotstar for mobile-only viewing.

**United States:** Willow TV (TV and streaming), available through Sling TV's Willow add-on package. JioHotstar International also available.

**United Kingdom:** Sky Sports Cricket (TV), Sky Go and NOW TV (streaming).

**Canada:** Willow TV, available through most cable providers and as a standalone streaming app.

**Middle East / Gulf:** JioHotstar, plus local broadcasters in UAE and Oman.

**Australia:** Willow TV streaming.

The most common NRI complaint about IPL streaming is that the apps buffer at exactly the moment a wicket falls. This is not a technical issue. It is the universe's way of reminding you that you are not at the stadium.

## The venues

**Dharamsala (Qualifier 1, May 26):** The HPCA Stadium sits at 4,600 feet above sea level in the foothills of the Himalayas, with snow-capped peaks visible beyond the boundary. It is the most beautiful cricket ground in India and one of the most beautiful in the world. The altitude means the ball travels further. Sixes that would land in the stands at sea level clear the stadium in Dharamsala. There is a 25% chance of rain.

**Mullanpur (Eliminator, May 27 & Qualifier 2, May 29):** The Maharaja Yadavindra Singh International Cricket Stadium in New Chandigarh is one of the IPL's newest venues. The pitch has favoured pace bowling, the outfield is quick, and the evening dew makes chasing marginally easier. RR are unbeaten at this ground this season.

**Ahmedabad (Final, May 31):** The Narendra Modi Stadium — formerly the Motera Stadium — is the largest cricket ground in the world. Capacity: 132,000. The ground hosted the 2023 World Cup final and the 2023 IPL final. The atmosphere in a full Narendra Modi Stadium during an IPL final is one of the most intense experiences in world sport. For NRIs who have attended, it is unforgettable. For NRIs who have not, it is the match that makes you think about booking a flight for next year.

## The four teams

**Royal Challengers Bengaluru (RCB):** Defending champions. League table toppers. Virat Kohli has 557 runs. Bhuvneshwar Kumar and Kagiso Rabada share 24 wickets each. RCB's strength is balance — they bat deep, bowl with discipline, and have the experience of winning the title last year.

**Gujarat Titans (GT):** Finished second on points with an identical record to RCB. Shubman Gill has 616 runs and has passed Sachin Tendulkar's T20 captaincy record. Sai Sudharsan — the Orange Cap holder with 638 runs — grew up watching the CSK team bus pass his school. GT's bowling attack, led by Mohammed Siraj and Josh Hazlewood, is the deepest in the tournament.

**Sunrisers Hyderabad (SRH):** The most explosive batting team in IPL history. Heinrich Klaasen's 606 runs from number four is a format record. Travis Head and Abhishek Sharma provide pyrotechnics at the top. Pat Cummins captains with the composure of someone who has won World Cups. Their weakness: the bowling is functional rather than exceptional.

**Rajasthan Royals (RR):** Sneaked into the playoffs on the back of Jofra Archer's all-round heroics against Mumbai Indians. Riyan Parag captains through a hamstring injury. Kumar Sangakkara coaches from the dugout. RR's strength is Archer — and the knowledge that in T20 knockout cricket, one great bowler can be worth more than four good batters.

## The week ahead

For the diaspora, the next six days will follow a familiar pattern: morning alarms, muted Slack notifications, bathroom break wicket checks, and the specific agony of seeing a notification that says "WICKET" before you can open the stream.

The IPL final is on Sunday, May 31, in Ahmedabad. By then, two of these four teams will be eliminated. The champion will lift the trophy in front of 132,000 people. The NRI watching from a living room in Edison, New Jersey — or Hounslow, or Brampton, or Fremont — will feel it the same way they feel every Indian sporting moment: viscerally, from six thousand miles away, at an hour that makes no sense for their time zone.

Set your alarms. Block your calendars. The playoffs are here.""",
}


if __name__ == "__main__":
    print("=" * 60)
    print("Sports Writer — 2026-05-26 06:00 UTC (23:00 PDT May 25)")
    print("=" * 60)

    # Check for duplicate slugs first
    for art in [a1, a2]:
        slug = art["slug"]
        r = requests.get(
            f"{SUPABASE_URL}/rest/v1/p2_articles?slug=eq.{slug}&select=id",
            headers=HEADERS,
        )
        if r.status_code == 200 and r.json():
            print(f"  SKIP: slug already exists: {slug}")
            sys.exit(0)

    # ── Insert + image: Article 1 (SRH vs RR Eliminator) ──
    print("\n[1/2] Inserting: SRH vs RR Eliminator Preview...")
    insert_article(a1)
    print(f"  ✓ Inserted: {a1['slug']}")

    # Wikipedia image: Heinrich Klaasen (main subject)
    img1_url = fetch_wikipedia_person_image("Heinrich Klaasen")
    img1_attribution = "Wikimedia Commons"
    if not img1_url:
        img1_url = fetch_wikipedia_person_image("Jofra Archer")
    if not img1_url:
        img1_url = fetch_wikipedia_person_image("Travis Head")
    if not img1_url:
        # Last resort: Pexels with specific terms
        img1_url = fetch_pexels_image("T20 cricket match stadium floodlights", "cricket batsman hitting six IPL")
        img1_attribution = "The Videshi"

    if img1_url:
        img1_path = f"/tmp/{a1_id}.jpg"
        if download_image(img1_url, img1_path):
            uploaded_url = upload_image(a1_id, img1_path)
            if uploaded_url:
                update_article_image(a1_id, uploaded_url, img1_attribution)

    # ── Insert + image: Article 2 (NRI Watch Guide) ──
    print("\n[2/2] Inserting: IPL 2026 NRI Playoffs Watch Guide...")
    insert_article(a2)
    print(f"  ✓ Inserted: {a2['slug']}")

    # This is not a person article — try venue images
    img2_url = fetch_wikipedia_person_image("Narendra Modi Stadium")
    img2_attribution = "Wikimedia Commons"
    if not img2_url:
        img2_url = fetch_wikipedia_person_image("HPCA Stadium")
    if not img2_url:
        img2_url = fetch_pexels_image("cricket stadium India evening floodlights crowd", "IPL cricket match stadium aerial")
        img2_attribution = "The Videshi"

    if img2_url:
        img2_path = f"/tmp/{a2_id}.jpg"
        if download_image(img2_url, img2_path):
            uploaded_url = upload_image(a2_id, img2_path)
            if uploaded_url:
                update_article_image(a2_id, uploaded_url, img2_attribution)

    # ── Score decay ──
    print("\nDecaying old article scores...")
    decayed = decay_scores()
    print(f"  Decayed {decayed} articles")

    print(f"\n{'=' * 60}")
    print(f"Done. 2 articles published.")
    print(f"  1: {a1['slug']}")
    print(f"  2: {a2['slug']}")
    print(f"  IDs: {a1_id}, {a2_id}")

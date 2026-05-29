#!/usr/bin/env python3
"""
The Videshi — Sports Writer (2026-05-29 evening)
3 articles: IPL Final NRI Guide, Rashid Khan worst T20 night, India Women 2nd T20I preview
"""

import json, os, sys, time, uuid, re, subprocess
import requests, urllib.parse
from datetime import datetime, timezone

# === Load env ===
def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    os.environ.setdefault(k.strip(), v.strip())

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

# === Image functions ===

def fetch_wikipedia_person_image(person_name):
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wiki image for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wiki error for '{person_name}': {e}")
    return None

def fetch_pexels_image(query, fallback_query=None):
    if not PEXELS_KEY:
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            result = subprocess.run(
                ["curl", "-sS",
                 f"https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5&orientation=landscape",
                 "-H", f"Authorization: {PEXELS_KEY}"],
                capture_output=True, text=True, timeout=15
            )
            data = json.loads(result.stdout)
            for p in data.get("photos", []):
                url = p.get("src", {}).get("large2x") or p.get("src", {}).get("large")
                if url:
                    print(f"  ✓ Pexels image for '{q}': {url[:80]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

def validate_image(url):
    if not url:
        return False
    try:
        r = requests.get(url, timeout=10, stream=True, headers={"User-Agent": "TheVideshi/1.0"})
        if r.status_code == 200 and "image" in r.headers.get("Content-Type", ""):
            chunk = r.raw.read(6000)
            return len(chunk) > 5000
    except:
        pass
    return False

def get_image(wiki_person, wiki_alt=None, pexels_query=None, pexels_fallback=None):
    """Try Wikipedia first, then Pexels. Return (url, attribution) or (None, None)."""
    for person in [wiki_person, wiki_alt]:
        if person:
            url = fetch_wikipedia_person_image(person)
            if url and validate_image(url):
                return url, "Wikimedia Commons"
    if pexels_query:
        url = fetch_pexels_image(pexels_query, pexels_fallback)
        if url and validate_image(url):
            return url, "Pexels"
    return None, None

# === Supabase ===

def sb_insert(table, data):
    r = requests.post(f"{SUPABASE_URL}/rest/v1/{table}", headers=HEADERS, json=data)
    if r.status_code in (200, 201):
        res = r.json()
        return res[0] if isinstance(res, list) and res else res
    print(f"  ✗ Insert error ({r.status_code}): {r.text[:300]}")
    return None

# ════════════════════════════════════════════════
# ARTICLE 1: IPL 2026 Final NRI Guide
# ════════════════════════════════════════════════

ART1_HEADLINE = "Sunday in Ahmedabad. 132,000 Seats. Kohli Against Gill. The NRI's Guide to the IPL 2026 Final."
ART1_SUBHEADLINE = "Royal Challengers Bengaluru defend their maiden title against Gujarat Titans at the Narendra Modi Stadium. Here is everything diaspora fans need to know about how to watch, when to wake up, and what to expect."
ART1_SLUG = "ipl-2026-final-rcb-vs-gt-ahmedabad-nri-guide-watch-times-streaming-kohli-gill-20260529"
ART1_BODY = """The Indian Premier League finishes where it always finishes — in Ahmedabad, under lights, with the Narendra Modi Stadium swelling to its 132,000-seat capacity. On Sunday evening, **Royal Challengers Bengaluru** will walk out to defend a title they waited sixteen years to win. **Gujarat Titans** will walk out to reclaim one they won four years ago in the same stadium. For the millions of NRI fans scattered across time zones from San Jose to Southall, this is the game that justifies the 4 AM alarms and the group chat that never sleeps.

## The Road Here

RCB destroyed Gujarat by ninety-two runs in Qualifier 1. **Rajat Patidar** smashed 93 not out off 47 balls, and **Josh Hazlewood** dismantled GT's middle order. It was the kind of performance that makes a defending champion look invincible. But GT have always been better as the hunted. They responded three days later with a seven-wicket demolition of Rajasthan Royals in Qualifier 2. **Shubman Gill** scored 104 off 53 balls — fifteen fours, three sixes, zero doubt — and **Sai Sudharsan** added 58 in a 167-run opening partnership that was the second-highest in IPL playoff history.

RCB are riding an eleven-match winning streak that includes the title defence from IPL 2025. GT have won five straight since their one bad night in Dharamshala.

## The Matchups That Matter

**Virat Kohli** against **Kagiso Rabada** in the powerplay. Kohli has scored 487 runs this season at a strike rate above 150, his best IPL campaign in years. Rabada holds the all-time record for powerplay wickets in a single IPL season. Something will break early.

**Rashid Khan** against RCB's middle order. Rashid had his worst-ever T20 outing in Qualifier 2 — 0 for 45 in two overs — but he has a history of responding to bad nights with match-winning spells. His record in IPL finals includes a Player of the Match performance in 2022.

**Gill versus Hazlewood** at the top. Gill is in the form of his life, with a century in his last innings. Hazlewood has been RCB's most economical bowler in the death overs. Whoever wins this duel sets the tone.

## When to Watch — Every Time Zone

The final starts at **7:30 PM IST on Sunday, May 31**. For the diaspora:

- **US East Coast**: 10:00 AM ET — a Sunday brunch game. Pour the chai.
- **US West Coast**: 7:00 AM PT — early, but not impossible. The Bay Area desi restaurants will have it on.
- **United Kingdom**: 3:00 PM BST — prime Sunday afternoon. Expect packed pubs in Wembley, Southall, and Leicester.
- **Canada (Toronto)**: 10:00 AM ET — same as New York.
- **UAE/Gulf**: 10:00 PM GST — a late-night affair for the massive Indian expat community.

## How to Stream

In the United States and Canada, **Willow TV** and **JioCinema** carry the IPL. In the UK, **Sky Sports** and **JioCinema** both have rights. In the Middle East, **JioCinema** is the primary digital option. If your subscription has lapsed, now is the time to reactivate — this final is worth the price.

## The Venue Factor

The Narendra Modi Stadium hosted the 2022 IPL final when GT beat Rajasthan Royals by seven wickets. It hosted the 2023 ODI World Cup final. It hosted the 2026 T20 World Cup semifinals. It is Gill's adopted fortress. But Kohli — born in Delhi, shaped in Bengaluru — has a way of making every stadium his own when the lights come on and the stakes go up.

The pitch is expected to favour batting early before slowing through the middle overs. Dew could be a factor after 9 PM, making chasing the marginally safer option. Temperatures will hover around 33°C with clear skies.

## The Diaspora Stakes

For NRI cricket fans, the IPL final is more than a match. It is the Sunday phone call with family that does not need a reason. It is the group watch at the cousin's house in New Jersey, the WhatsApp status that stays up for days, the argument about Kohli versus Gill that stretches from generation to generation. RCB fans have waited sixteen years for their first title and barely had time to celebrate before defending it. GT fans carry the swagger of a franchise that has reached the final three times in four years.

This is the biggest game of the IPL 2026 season. For NRIs, it is also one of the few sporting events that still genuinely connects the old country and the new one. Set your alarm. Call your people. Sunday in Ahmedabad will be worth it.

*Sources: IPLT20.com, Reuters, Sporting News India*"""

ART1_SOURCES = [
    {"name": "IPLT20.com", "url": "https://www.iplt20.com"},
    {"name": "Reuters", "url": "https://www.reuters.com/sports/cricket/gill-ton-steers-gujarat-past-rajasthan-into-ipl-final-2026-05-29/"},
    {"name": "Sporting News India", "url": "https://www.sportingnews.com/in/cricket"}
]

# ════════════════════════════════════════════════
# ARTICLE 2: Rashid Khan Worst T20 Night
# ════════════════════════════════════════════════

ART2_HEADLINE = "Rashid Khan Recorded His Worst T20 Figures in 524 Innings. Gujarat Titans Won Anyway."
ART2_SUBHEADLINE = "The Afghan leg-spinner conceded 45 runs in two overs against Rajasthan Royals, including 27 in the final over. It did not matter. That is what makes Gujarat dangerous heading into Sunday's final."
ART2_SLUG = "rashid-khan-worst-t20-figures-524-innings-gt-still-won-qualifier-2-ipl-2026-final-20260529"
ART2_BODY = """For nine years and 524 T20 innings, **Rashid Khan** had never been this expensive. On Friday night in Mullanpur, in an IPL Qualifier 2 match that was supposed to decide everything, the Afghan wizard bowled two overs, took no wickets, and conceded 45 runs at an economy rate of 22.5. It was the worst T20 performance of his remarkable career. And it changed absolutely nothing about the outcome.

Gujarat Titans chased down 215 in 18.4 overs. **Shubman Gill** scored 104 off 53 balls. **Sai Sudharsan** made 58. They won by seven wickets. Rashid's nightmare was a footnote.

## The Carnage in Numbers

It started in the ninth over. **Riyan Parag** launched Rashid over deep mid-wicket for six. **Vaibhav Sooryavanshi**, the fifteen-year-old who has spent this IPL treating every bowler like a net session, pulled the next delivery over deep backward square leg for another maximum. That over went for 18 runs.

Then came the twentieth over. **Donovan Ferreira**, the South African finisher who had been quiet until that point, decided to end Rashid's evening in the most brutal way possible. Four sixes. Twenty-seven runs. The second ball was short; Ferreira pulled it over long-on. The third was a googly; Ferreira slog-swept it with the turn. The fourth was outside off; Ferreira hammered it flat over long-off. The sixth was full; Ferreira lofted it inside-out over extra cover. Each shot was more violent than the last.

Those 27 runs equalled the most expensive over bowled by a spinner in IPL playoff history, matching **Ravi Bishnoi's** 27 against RCB in the 2022 Eliminator. Rashid's total figures of 0/45 in two overs surpassed his previous worst economy of 18.00, set against Lucknow Super Giants in IPL 2025.

## The Longer Story

**Anil Kumble** warned before the season that "the novelty of Rashid Khan has worn off a little." The legendary Indian spinner pointed to Rashid's underwhelming IPL 2025 — nine wickets in fifteen matches at an economy of 9.35, with 33 sixes conceded in a single season, the most by any bowler. Rashid himself has linked his decline to the back surgery he underwent in late 2023 after the ODI World Cup. He returned too quickly, never fully regained his bowling rhythm, and spent two seasons searching for the control that once made him the most feared T20 bowler alive.

But here is the thing about Rashid Khan and IPL finals: in 2022, at this same Narendra Modi Stadium in Ahmedabad, Rashid scored 11 crucial runs and took a key wicket as GT won the title in their debut season. He has a history of responding to bad nights with extraordinary ones.

## Why It Does Not Matter — Yet

Gujarat's transformation this season has been built precisely on the principle that they cannot depend on Rashid alone. Gill's batting has been otherworldly — seven half-centuries and now a playoff century. Sudharsan has been the most consistent opener in the tournament. **Kagiso Rabada** has taken the death-overs burden that Rashid once carried. **Mohammed Siraj** provides genuine pace. **Jason Holder** adds all-round depth.

When your best spinner concedes 45 in two overs and you still chase 215 with eight balls to spare, it means your batting lineup can absorb anything. That is a message for Sunday's opponents. Royal Challengers Bengaluru will study Ferreira's assault on Rashid and believe they can do the same. But they will also have to contend with a Gujarat top order that scored 167 runs before losing a single wicket.

## The Afghan Connection

For the Afghan diaspora — scattered across Pakistan, Iran, the UK, Germany, Australia, and increasingly the United States — Rashid Khan remains a symbol of what cricket can mean for a country that has had precious little to celebrate. He has played 85 IPL matches for Gujarat Titans, more than he has played for Afghanistan in some formats. His bad night in Mullanpur will make headlines, but it will not define him. What defines him is what happens next.

The IPL 2026 final is on Sunday. The same stadium where he won his first title. Against the same franchise that demolished his team five days ago. If there is one thing Rashid Khan has earned across 524 T20 innings, it is the right to be judged on what he does when it matters most.

*Sources: IPLT20.com, LatestLY (ANI), Cricbuzz, Sportskeeda*"""

ART2_SOURCES = [
    {"name": "IPLT20.com", "url": "https://www.iplt20.com"},
    {"name": "LatestLY/ANI", "url": "https://www.latestly.com/sports/cricket/"},
    {"name": "Cricbuzz", "url": "https://www.cricbuzz.com"},
    {"name": "Sportskeeda", "url": "https://www.sportskeeda.com/cricket/"}
]

# ════════════════════════════════════════════════
# ARTICLE 3: India Women 2nd T20I Preview
# ════════════════════════════════════════════════

ART3_HEADLINE = "India Women Can Seal the Series in Bristol Tomorrow. Then the Real Tournament Begins."
ART3_SUBHEADLINE = "After a commanding 38-run win at Chelmsford, Smriti Mandhana's side faces England in the second T20I on Saturday. A series win in English conditions would be the perfect warm-up for the T20 World Cup that starts in thirteen days."
ART3_SLUG = "india-women-2nd-t20i-england-bristol-series-seal-mandhana-t20-world-cup-prep-nri-20260529"
ART3_BODY = """The math is simple. Win at Bristol on Saturday, and India's women seal their first bilateral T20I series victory in England. Lose, and the contest goes to a decider at Lord's on June 2 with the T20 World Cup looming thirteen days away. **Smriti Mandhana**, captaining in place of the rested **Harmanpreet Kaur**, would very much prefer the first option.

## What Happened at Chelmsford

India dominated the first T20I on Wednesday. Batting first, they posted 188 for 7 — an imposing total built on aggressive intent from the top order. Mandhana set the tone with a fluent 43 off 30 balls, and **Jemimah Rodrigues** provided the middle-overs acceleration that India's women's team has sometimes lacked in overseas conditions. **Deepti Sharma** contributed a handy cameo lower down, ensuring India batted deep.

In reply, England never found their rhythm. **Heather Knight** made 31, and **Alice Capsey** showed flashes of her considerable talent, but the rest of the order crumbled against India's bowling variety. **Renuka Singh** was particularly impressive with the new ball, moving it both ways in helpful Chelmsford conditions. England were bowled out for 150, giving India a 38-run victory that was more comfortable than even the margin suggests.

## The Bristol Challenge

The County Ground in Bristol offers different conditions. The outfield is typically quicker, the boundaries slightly shorter, and the square tends to offer more pace and bounce than Chelmsford. For India, that could mean higher scores — but also more risk against England's pace bowlers, particularly **Lauren Bell** and **Issy Wong**, both of whom generated uncomfortable bounce in the first match without the reward their efforts deserved.

England captain Knight will almost certainly make changes. The top-order approach was too cautious in Chelmsford, and the hosts need more from **Sophia Dunkley** and **Danielle Gibson** in the middle overs. A World Cup on home soil starts in less than two weeks; England cannot afford to enter it on a series defeat.

## Why This Matters for the World Cup

The ICC Women's T20 World Cup 2026 runs from June 12 to 29 across England and Wales. India are in Group A alongside Pakistan, whom they play on June 14 in Birmingham. The conditions India are experiencing right now — English pitches, English weather, English crowds — are exactly what they will face in the tournament. Every innings Mandhana plays, every spell Renuka bowls, every fielding position tested in Bristol builds the muscle memory that matters when the stakes are highest.

India have been on an upward trajectory in women's T20I cricket. They reached the semifinals of the 2023 T20 World Cup in South Africa, and their recent bilateral record has been strong. But winning in England has always been a challenge. An English summer can flatten any advantage if the conditions turn — overcast skies, a bit of swing, a slow outfield after rain — and India's batters need to prove they can adapt.

## The NRI Viewing Guide

For diaspora fans in the UK, this is a rare opportunity. India Women are playing in Bristol — tickets are affordable, the ground is accessible, and the atmosphere at women's internationals in England has improved dramatically in the last two years. If you are in the South West or anywhere within train distance of Bristol, this is worth the trip.

For NRIs in North America, the timing works in your favour. The match starts at **6:30 AM Pacific / 9:30 AM Eastern** on Saturday — early enough to catch it before weekend plans, late enough that the caffeine has kicked in. Streaming options include Willow TV and JioCinema.

## The Bigger Picture

Mandhana's captaincy in this series is its own storyline. With Harmanpreet managing her workload before the World Cup, Mandhana has a chance to prove she can lead at the highest level. Her tactical decisions in Chelmsford — an aggressive field in the powerplay, bowling Deepti through the middle, trusting Renuka with the death overs — showed a captain who is growing into the role rather than merely occupying it.

If India win on Saturday, the conversation shifts. It stops being about a bilateral series and starts being about whether this team is ready to win a World Cup in England. The signs, so far, say they might be.

*Sources: ESPN Cricinfo, ICC Women's T20 World Cup 2026 schedule, Sportradar*"""

ART3_SOURCES = [
    {"name": "ESPN Cricinfo", "url": "https://www.espncricinfo.com"},
    {"name": "ICC", "url": "https://www.icc-cricket.com/tournaments/t20-world-cup-women"},
    {"name": "Sportradar", "url": "https://www.sportradar.com"}
]

# === Main ===

def main():
    print("=" * 60)
    print("The Videshi Sports Writer — 2026-05-29 Evening")
    print("=" * 60)

    articles = [
        {
            "headline": ART1_HEADLINE, "subheadline": ART1_SUBHEADLINE,
            "slug": ART1_SLUG, "body": ART1_BODY, "sources": ART1_SOURCES,
            "wiki_person": "Virat Kohli", "wiki_alt": "Shubman Gill",
            "pexels_q": "cricket stadium night India", "pexels_fb": "cricket match stadium"
        },
        {
            "headline": ART2_HEADLINE, "subheadline": ART2_SUBHEADLINE,
            "slug": ART2_SLUG, "body": ART2_BODY, "sources": ART2_SOURCES,
            "wiki_person": "Rashid Khan (cricketer)",  "wiki_alt": "Rashid Khan",
            "pexels_q": "cricket spinner bowling", "pexels_fb": "cricket bowling"
        },
        {
            "headline": ART3_HEADLINE, "subheadline": ART3_SUBHEADLINE,
            "slug": ART3_SLUG, "body": ART3_BODY, "sources": ART3_SOURCES,
            "wiki_person": "Smriti Mandhana", "wiki_alt": None,
            "pexels_q": "women cricket India", "pexels_fb": "cricket match"
        }
    ]

    published = 0

    for i, art in enumerate(articles):
        print(f"\n{'─' * 50}")
        print(f"Article {i+1}/{len(articles)}: {art['headline'][:70]}...")
        print(f"{'─' * 50}")

        # Word count check
        words = len(art['body'].split())
        print(f"  Words: {words}")
        if words < 400:
            print(f"  ✗ Too short ({words} words), skipping")
            continue

        # Image sourcing
        img_url, img_attr = get_image(
            art.get("wiki_person"), art.get("wiki_alt"),
            art.get("pexels_q"), art.get("pexels_fb")
        )

        if img_url:
            # Check for banned sources
            banned = ["fbcdn.net", "cdninstagram.com", "lookaside.fbsbx.com", "_nc_ht=", "_nc_cat="]
            if any(b in img_url for b in banned):
                print(f"  ✗ Banned image source, removing")
                img_url, img_attr = None, None

        # Build record
        now_iso = datetime.now(timezone.utc).isoformat()
        art_id = str(uuid.uuid4())

        record = {
            "id": art_id,
            "headline": art["headline"],
            "subheadline": art["subheadline"],
            "body": art["body"],
            "slug": art["slug"],
            "category": "sports",
            "vertical": "sports",
            "status": "published",
            "published_at": now_iso,
            "sources": json.dumps(art["sources"]),
            "image_attribution": img_attr or "The Videshi"
        }
        if img_url:
            record["image_url"] = img_url

        result = sb_insert("p2_articles", record)
        if result:
            print(f"  ✓ PUBLISHED: {art['headline'][:70]}...")
            print(f"    ID: {art_id}")
            print(f"    Image: {img_attr or 'none'} — {(img_url or 'N/A')[:60]}")
            published += 1
        else:
            print(f"  ✗ FAILED to publish")

        time.sleep(1)

    print(f"\n{'=' * 60}")
    print(f"Done: {published}/{len(articles)} articles published")
    print(f"{'=' * 60}")

if __name__ == "__main__":
    main()

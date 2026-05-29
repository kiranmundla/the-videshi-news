#!/usr/bin/env python3
"""Sports writer for The Videshi — May 29, 2026 batch."""

import json
import os
import re
import uuid
import subprocess
import urllib.parse
from datetime import datetime, timezone

# Load env
def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                if line.startswith('export '):
                    line = line[7:]
                key, val = line.split('=', 1)
                val = val.strip().strip('"').strip("'")
                os.environ[key] = val

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
PEXELS_API_KEY = os.environ.get('PEXELS_API_KEY', '')

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        result = subprocess.run(
            ['curl', '-sS', f'https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}',
             '-H', 'User-Agent: TheVideshi/1.0 (thevideshi.com)'],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            img = data.get('originalimage', {}).get('source') or data.get('thumbnail', {}).get('source')
            if img:
                print(f"  ✓ Wikipedia image found for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None

def fetch_pexels_image(query, fallback_query=None):
    """Fetch a relevant image from Pexels API."""
    if not PEXELS_API_KEY:
        print("  ⚠ No Pexels API key")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            result = subprocess.run(
                ['curl', '-sS',
                 f'https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=3&orientation=landscape',
                 '-H', f'Authorization: {PEXELS_API_KEY}'],
                capture_output=True, text=True, timeout=15
            )
            if result.returncode == 0:
                data = json.loads(result.stdout)
                photos = data.get('photos', [])
                if photos:
                    url = photos[0]['src']['large2x']
                    print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

def validate_image_url(url):
    """Verify that an image URL returns HTTP 200 with proper content type and size."""
    if not url:
        return False
    try:
        result = subprocess.run(
            ['curl', '-sS', '-o', '/dev/null', '-w', '%{http_code} %{content_type} %{size_download}',
             '-L', '--max-time', '10', url,
             '-H', 'User-Agent: TheVideshi/1.0 (thevideshi.com)'],
            capture_output=True, text=True, timeout=15
        )
        parts = result.stdout.strip().split()
        if len(parts) >= 3:
            status = parts[0]
            content_type = parts[1]
            size = float(parts[2])
            if status == '200' and 'image' in content_type and size > 5000:
                print(f"  ✓ Image validated: {status}, {content_type}, {size:.0f} bytes")
                return True
            else:
                print(f"  ✗ Image validation failed: {status}, {content_type}, {size:.0f} bytes")
    except Exception as e:
        print(f"  ⚠ Image validation error: {e}")
    return False

def publish_article(article):
    """Publish an article to Supabase."""
    payload = json.dumps(article)
    result = subprocess.run(
        ['curl', '-sS', '-X', 'POST',
         f'{SUPABASE_URL}/rest/v1/p2_articles',
         '-H', f'apikey: {SUPABASE_KEY}',
         '-H', f'Authorization: Bearer {SUPABASE_KEY}',
         '-H', 'Content-Type: application/json',
         '-H', 'Prefer: return=representation',
         '-d', payload],
        capture_output=True, text=True, timeout=30
    )
    if result.returncode == 0 and ('"id"' in result.stdout or result.stdout.startswith('[')):
        print(f"  ✓ Published: {article['headline'][:60]}...")
        return True
    else:
        print(f"  ✗ Publish failed: {result.stdout[:200]}")
        print(f"  stderr: {result.stderr[:200]}")
        return False

# ============================================================
# ARTICLE 1: Sooryavanshi India Debut Debate
# ============================================================
print("\n" + "="*60)
print("ARTICLE 1: Sooryavanshi India Debut Debate")
print("="*60)

img1 = fetch_wikipedia_person_image("Vaibhav Suryavanshi")
if not validate_image_url(img1):
    img1 = fetch_pexels_image("cricket batsman hitting six")
    if not validate_image_url(img1):
        img1 = None

article1_body = """He has 680 runs in a single IPL season. He has hit 65 sixes, shattering Chris Gayle's twelve-year-old record of 59. He leads the Orange Cap race by a comfortable margin, batting at a strike rate north of 242. He has scored a 29-ball 97 in a knockout match, hitting twelve sixes before falling three runs short of what would have been the fastest IPL century in history.

And he turned fifteen in March.

**Vaibhav Sooryavanshi** is, by every statistical measure, the most devastating T20 batsman in the world right now. The question that has consumed Indian cricket for the past fortnight is no longer whether he is good enough. It is whether India's selectors should pick him for the upcoming T20I series against Ireland and England — and whether doing so would be wise.

## The Case for Patience

Former India opener **Aakash Chopra** has emerged as the most prominent voice counselling restraint. Speaking after Sooryavanshi's record-breaking 97 in the IPL Eliminator against Sunrisers Hyderabad, Chopra acknowledged the teenager's extraordinary talent but drew a clear line.

"He is special, no doubt about that," Chopra said. "But his India debut can wait. He is fifteen. He will play for India — there is no question about that. But the selectors should not replace established top-order batsmen like Abhishek Sharma and Sanju Samson just because a fifteen-year-old has had one incredible IPL season."

Chopra's argument rests on precedent. Sachin Tendulkar debuted at sixteen, but in Test cricket, a format that rewards patience and technique. T20 international cricket, with its compressed schedules and relentless travel, places different demands on young bodies and minds. The IPL, for all its intensity, is played over two months within the confines of India. International cricket means hotels in Dublin and Cardiff, fourteen-hour flights, and the cumulative pressure of representing your country.

## The Case for Now

On the other side, **Suryakumar Yadav**, India's T20I captain, has made no effort to hide his admiration. After watching Sooryavanshi dismantle Pat Cummins for three consecutive sixes in the Eliminator, SKY was asked about the youngster and responded with the understated enthusiasm of a man who knows he may soon be batting alongside him: "You can see what he does. Everyone can see it."

Former India wicketkeeper **Kiran More** went further, drawing a direct comparison to Tendulkar. "I remember watching Sachin bat for the first time," More said. "I got the same feeling. This boy has been made by God for this sport."

The numbers support the enthusiasm. Sooryavanshi's 680 runs have come against every bowling attack in the IPL, including the world's best fast bowlers. He has faced Jasprit Bumrah, Josh Hazlewood, Mitchell Starc, and Pat Cummins — and scored freely against all of them. His strike rate of 242.85 is not a small-sample anomaly; it has been sustained across 15 matches.

## The Diaspora Is Watching

For NRIs who grew up on the mythology of Tendulkar's debut, Sooryavanshi's emergence has a resonance that transcends statistics. Every uncle at every watch party in New Jersey and Sunnyvale and Brampton has an opinion on when the boy should play for India. WhatsApp groups that normally debate Kohli's form have pivoted entirely to whether a fifteen-year-old should be on the plane to Dublin.

The India T20I squad for the Ireland series — **Hardik Pandya** is expected to lead — will be announced after the IPL Final. That announcement will tell us what Indian cricket thinks about Sooryavanshi's readiness. The smart money says he waits. The heart says otherwise.

## What Comes Next

Sooryavanshi has at least one more IPL match left this season — Rajasthan Royals face Gujarat Titans in Qualifier 2 on Thursday at Mullanpur, with the winner meeting RCB in Sunday's final at Ahmedabad. If he delivers another performance like the one against Hyderabad, the selection debate will become impossible to ignore.

At fifteen, Vaibhav Sooryavanshi has already rewritten the IPL record books. The question is not if he will play for India. The question is whether India can afford to wait — and whether waiting is, in fact, the most loving thing Indian cricket can do for the most exciting young cricketer it has produced since Tendulkar.

*Sources: Reuters, IANS, Cricbuzz, Wisden, CricTracker*"""

article1 = {
    "headline": "He Has 680 Runs and 65 Sixes at Fifteen. India's Selectors Should Still Make Him Wait.",
    "subheadline": "Vaibhav Sooryavanshi is the most exciting young cricketer since Tendulkar. Experts are divided on whether he belongs in India's T20I squad — and the diaspora has strong opinions.",
    "body": article1_body,
    "slug": "sooryavanshi-india-debut-debate-fifteen-selectors-chopra-sky-tendulkar-comparison-20260529",
    "category": "sports",
    "vertical": "sports",
    "status": "published",
    "published_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "image_url": img1 if img1 else "",
    "image_caption": "Vaibhav Sooryavanshi — 680 runs, 65 sixes, and still only fifteen years old" if img1 else "",
    "image_attribution": "Wikimedia Commons" if img1 and "wikimedia" in (img1 or "") else "Pexels",
    "sources": [{"name": "Reuters"}, {"name": "IANS"}, {"name": "Cricbuzz"}, {"name": "Wisden"}, {"name": "CricTracker"}],
}

if img1:
    publish_article(article1)
else:
    print("  ⚠ Skipping article 1 — no valid image found")

# ============================================================
# ARTICLE 2: IPL Final Preview — RCB's Back-to-Back Quest
# ============================================================
print("\n" + "="*60)
print("ARTICLE 2: IPL Final Preview — RCB's Back-to-Back Quest")
print("="*60)

# Use Narendra Modi Stadium image
img2 = "https://upload.wikimedia.org/wikipedia/commons/c/cb/Narendra_Modi_Stadium_view_from_the_gallery.jpg"
if not validate_image_url(img2):
    img2 = fetch_pexels_image("cricket stadium packed crowd", "IPL cricket")
    if not validate_image_url(img2):
        img2 = None

article2_body = """The numbers from Qualifier 1 do not need embellishment. Royal Challengers Bengaluru posted 254 for 5 — the highest playoff total in IPL history — and bowled Gujarat Titans out for 162 in 19.3 overs. The margin was 92 runs. It was not a match. It was a statement.

On Sunday, May 31, at the **Narendra Modi Stadium** in Ahmedabad — the world's largest cricket ground, with a capacity of 132,000 — RCB will walk out for the IPL 2026 Final with a chance to become the first team to win back-to-back titles since Chennai Super Kings in 2010 and 2011.

Their opponent will be determined on Thursday, when Gujarat Titans face Rajasthan Royals in Qualifier 2 at Mullanpur. But in Bengaluru's dressing room, the focus is not on who shows up. It is on finishing what they started.

## The Patidar Factor

**Rajat Patidar** is the heartbeat of this RCB side. Three years ago, he was an uncapped walk-in who had been released by his previous franchise. Today, he is the captain who just scored 93 not out off 33 balls in a playoff match — an innings that included 8 sixes and broke every aggression metric in IPL knockout history.

"This team doesn't depend on just one person," Patidar said after Qualifier 1, with the quiet confidence of a man who knows that statement applies most of all to himself. The 2025 IPL Final was won by Kohli's brilliance. The 2026 run has been built on something broader — on Patidar's captaincy, on **Krunal Pandya**'s reinvention as a middle-order enforcer, on **Rasikh Salam**'s emergence as one of the most lethal death bowlers in the tournament.

## Kohli's Quiet Dominance

**Virat Kohli** has done what Virat Kohli always does. His 600-plus runs this season made him the first player in IPL history to score 600 runs in four consecutive seasons — a record that speaks to consistency so sustained it has become almost unremarkable. In Qualifier 1, his 43 set the platform before Patidar detonated.

For NRIs watching from time zones that turn IPL matches into midnight vigils, Kohli's continued excellence is a form of comfort. He has been the constant in Indian cricket for fifteen years. In what may well be among his final IPL seasons, he is playing as well as ever — unburdened by captaincy, free to bat, smiling more than he has in years.

## The Opposition

If **Gujarat Titans** come through Qualifier 2, RCB will face a team they just demolished. **Shubman Gill**'s GT side was blown apart by RCB's batting in Dharamsala, and their bowling — despite **Kagiso Rabada**'s record-breaking 26 powerplay wickets — had no answers. A second meeting in three days would test GT's psychological resilience as much as their skills.

If **Rajasthan Royals** advance, the narrative shifts to Sooryavanshi. The fifteen-year-old prodigy, leading the Orange Cap race with 680 runs, would bring the chaos that GT could not. RR's batting, powered by Sooryavanshi and **Yashasvi Jaiswal**, is capable of matching RCB's firepower. Their bowling, led by **Trent Boult** and **Yuzvendra Chahal**, offers variety that GT lacked.

## The Stage

The Narendra Modi Stadium is not a neutral venue — it is the home ground of the Gujarat Titans. If GT make it through, RCB will effectively be playing an away final. But RCB have shown throughout this season that they are indifferent to context. They have won eleven matches in a row. They have beaten every team in the tournament. They have the best bowling attack, the most prolific top order, and a captain who scores 93 off 33 in knockout matches.

## Where NRIs Can Watch

For the diaspora, the IPL Final is the one match that justifies setting an alarm at 4 AM (US East Coast) or 1 AM (US West Coast). The match will be broadcast on **Willow TV** in the US and Canada, and is available on **JioCinema** (VPN may be required from outside India). Many NRI community centers and Indian restaurants in major metros — Edison, Sunnyvale, Irving, Brampton — host watch parties for the final.

If RCB win on Sunday, they will have completed something no franchise has achieved in over a decade. The team that was synonymous with heartbreak for the first fifteen years of the IPL has become the machine that does not stop.

*Sources: Cricbuzz, ESPNcricinfo, Reuters, SportsKeeda*"""

article2 = {
    "headline": "RCB Demolished GT by Ninety-Two Runs. Now They Wait in Ahmedabad for Sunday's Final.",
    "subheadline": "Rajat Patidar's record-breaking 93 off 33 balls powered the highest playoff total in IPL history. The defending champions are one win from becoming the first back-to-back IPL winners in fifteen years.",
    "body": article2_body,
    "slug": "rcb-ipl-2026-final-preview-ahmedabad-patidar-kohli-back-to-back-20260529",
    "category": "sports",
    "vertical": "sports",
    "status": "published",
    "published_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "image_url": img2 if img2 else "",
    "image_caption": "The Narendra Modi Stadium in Ahmedabad — the world's largest cricket ground — hosts the IPL 2026 Final on Sunday" if img2 else "",
    "image_attribution": "Wikimedia Commons" if img2 and "wikimedia" in (img2 or "") else "Pexels",
    "sources": [{"name": "Cricbuzz"}, {"name": "ESPNcricinfo"}, {"name": "Reuters"}, {"name": "SportsKeeda"}],
}

if img2:
    publish_article(article2)
else:
    print("  ⚠ Skipping article 2 — no valid image found")

# ============================================================
# ARTICLE 3: Indian Sport's Biggest Week — Everything Happening Now Through Sunday
# ============================================================
print("\n" + "="*60)
print("ARTICLE 3: Indian Sport's Biggest Week")
print("="*60)

# Use a Pexels image for this multi-sport overview
img3 = fetch_pexels_image("cricket match stadium night", "sports stadium crowd")
if not validate_image_url(img3):
    # Fallback to Virat Kohli Wikipedia
    img3 = "https://upload.wikimedia.org/wikipedia/commons/9/9b/Virat_Kohli_in_PMO_New_Delhi.jpg"
    if not validate_image_url(img3):
        img3 = None

article3_body = """Across four countries, five sports, and every time zone where the Indian diaspora gathers around screens, the next four days represent the most concentrated burst of elite Indian sport in recent memory. Here is everything happening between now and Sunday night — and how NRIs can follow it all.

## Thursday, May 29

### IPL 2026 Qualifier 2: Gujarat Titans vs Rajasthan Royals
**When:** 7:30 PM IST (10:00 AM ET / 7:00 AM PT)
**Where:** Maharaja Yadavindra Singh International Cricket Stadium, Mullanpur (New Chandigarh)
**Watch:** Willow TV (US/Canada), JioCinema (India)
**Stakes:** The winner faces RCB in Sunday's final.

This is the match everyone wants to watch. **Vaibhav Sooryavanshi** — fifteen years old, 680 runs, 65 sixes, the Orange Cap leader — against Gujarat Titans' bowling attack led by **Kagiso Rabada** (26 wickets, the Purple Cap frontrunner). GT come into this match smarting from a 92-run demolition by RCB in Qualifier 1. RR come in riding the momentum of Sooryavanshi's 97 off 29 balls in the Eliminator. Something has to give.

### Singapore Open Badminton: Quarterfinals and Semifinals
**Where:** Singapore Indoor Stadium
**Watch:** BWF TV, JioHotstar

India has an unprecedented presence at this Super 750 event. **PV Sindhu**, **Lakshya Sen**, **HS Prannoy**, and the men's doubles pair of **Satwik-Chirag** all reached the quarterfinals — the deepest Indian run at a Super 750 tournament in years. The quarterfinals and early semifinals will play out through Thursday and Friday, with Indian matches spread across both days.

### India Women vs England: 2nd T20I
**When:** 6:30 PM BST (1:00 PM ET / 10:00 AM PT)
**Where:** County Ground, Bristol
**Watch:** Willow TV, JioCinema

India won the first T20I by 38 runs at Chelmsford on Wednesday, with **Jemimah Rodrigues** (69 off 40) and **Yastika Bhatia** (54 off 40) rescuing the innings after captain **Smriti Mandhana** was dismissed for a golden duck on the very first ball. Harmanpreet Kaur, rested for the opener, may return. The Women's T20 World Cup starts in England on June 12 — this series is the final dress rehearsal.

## Saturday, May 30

### Norway Chess: Round 5
**When:** 5:00 PM CEST (11:00 AM ET / 8:00 AM PT)
**Where:** Oslo, Norway
**Watch:** Chess24 (YouTube, Twitch)

Five Indians are competing across the open and women's tournaments. **Alireza Firouzja** leads the open section with 10 points after four rounds, with **Praggnanandhaa** in second (6.5 points) and **Gukesh** (the reigning World Champion) in mid-table after losing to **Magnus Carlsen** in Round 4. In the women's event, **Divya Deshmukh** — at nineteen, the youngest player in the field — started with three consecutive wins before a Round 4 loss after hanging her queen.

Round 5 pairings include Firouzja vs Keymer and potentially pivotal matchups for the Indians. With six rounds remaining after the rest day (Friday), the tournament is approaching its crucial phase.

### French Open: Round 3 / Round 4
**Where:** Roland Garros, Paris
**Watch:** Tennis Channel, TNT, Peacock (US)

The biggest story at Roland Garros is who is *not* there. **Carlos Alcaraz** withdrew before the tournament with injury. **Jannik Sinner**, the world number one, was eliminated in the second round in one of the most stunning collapses in Grand Slam history — up two sets and 5-1 in the third before losing 18 consecutive points and ultimately falling in five sets.

With both top seeds gone, **Alexander Zverev** has emerged as the betting favourite. **Novak Djokovic**, at thirty-nine, is the last remaining previous champion. For Indian tennis, **Yuki Bhambri** and **Sriram Balaji** are alive in the men's doubles draw.

## Sunday, May 31

### IPL 2026 Final
**When:** 7:30 PM IST (10:00 AM ET / 7:00 AM PT)
**Where:** Narendra Modi Stadium, Ahmedabad (capacity: 132,000)
**Watch:** Willow TV (US/Canada), JioCinema (India)
**Stakes:** The title.

RCB attempt to become the first team since CSK in 2010-11 to win back-to-back IPL titles. **Rajat Patidar**'s side have won eleven consecutive matches. **Virat Kohli** has 600-plus runs for the fourth straight season. The opposition — whoever survives Thursday's Qualifier 2 — will need to produce something historic to stop them.

For NRIs planning watch parties, the final typically starts at 10:00 AM Eastern / 7:00 AM Pacific, making it the one IPL match of the year that does not require sacrificing sleep. Indian restaurants and community centres in Edison, Sunnyvale, Irving, Houston, and Brampton traditionally host final-day gatherings. If you are in the Bay Area, check with your local cricket club — many organise outdoor screenings.

## The Big Picture

What makes this particular stretch extraordinary is not just the density of events but the calibre. India's women are preparing for a World Cup in England. India's chess prodigies are battling the world's best in Norway. A fifteen-year-old cricketer is rewriting IPL history. And the world's largest cricket stadium is preparing to host the biggest match of the season.

For the Indian diaspora, spread across time zones from London to San Francisco, the next four days offer a rare chance to watch Indian athletes compete at the highest level in nearly every major sport. Set the alarms. Clear the calendar. This is as good as it gets.

*Sources: Cricbuzz, BWF, FIDE/Chess.com, Roland Garros, ESPNcricinfo*"""

article3 = {
    "headline": "From Mullanpur to Oslo to Roland Garros. The Biggest Week in Indian Sport Peaks on Sunday in Ahmedabad.",
    "subheadline": "IPL playoffs, Norway Chess, the French Open, Singapore Open badminton, and India Women's T20Is — four days, five sports, and every time zone where the diaspora is watching. Here is your complete guide.",
    "body": article3_body,
    "slug": "indian-sport-biggest-week-ipl-final-norway-chess-french-open-singapore-nri-guide-20260529",
    "category": "sports",
    "vertical": "sports",
    "status": "published",
    "published_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "image_url": img3 if img3 else "",
    "image_caption": "The IPL Final on Sunday caps the biggest week in Indian sport this year" if img3 else "",
    "image_attribution": "Pexels" if img3 and "pexels" in (img3 or "") else "Wikimedia Commons",
    "sources": [{"name": "Cricbuzz"}, {"name": "BWF"}, {"name": "FIDE/Chess.com"}, {"name": "Roland Garros"}, {"name": "ESPNcricinfo"}],
}

if img3:
    publish_article(article3)
else:
    print("  ⚠ Skipping article 3 — no valid image found")

print("\n" + "="*60)
print("DONE — Sports writer batch complete")
print("="*60)

#!/usr/bin/env python3
"""Sports writer for The Videshi — 2026-05-28 batch (fixed)"""

import json, os, sys, time, uuid, re, subprocess
from datetime import datetime, timezone

import requests

# ── env ──────────────────────────────────────────────────────────────
def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if line.startswith('export '):
                line = line[7:]
            if '=' in line:
                k, v = line.split('=', 1)
                v = v.strip().strip('"').strip("'")
                os.environ.setdefault(k.strip(), v)

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SB_URL = os.environ['SUPABASE_URL']
SB_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

HEADERS = {
    'apikey': SB_KEY,
    'Authorization': f'Bearer {SB_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation',
}

# ── helpers ──────────────────────────────────────────────────────────
def sb_insert(table, data):
    r = requests.post(f'{SB_URL}/rest/v1/{table}', headers=HEADERS, json=data, timeout=30)
    if r.status_code in (200, 201):
        result = r.json()
        return result[0] if isinstance(result, list) and result else result
    print(f'  ✗ Insert to {table} failed ({r.status_code}): {r.text[:500]}')
    return None

def fetch_wikipedia_person_image(person_name):
    encoded = requests.utils.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f'https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}',
            headers={'User-Agent': 'TheVideshi/1.0 (thevideshi.com)'},
            timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get('originalimage', {}).get('source') or data.get('thumbnail', {}).get('source')
            if img:
                print(f"  ✓ Wikipedia image for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia error for '{person_name}': {e}")
    return None

def fetch_pexels_image(query, fallback_query=None):
    if not PEXELS_KEY:
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            cmd = [
                'curl', '-sS', '-H', f'Authorization: {PEXELS_KEY}',
                f'https://api.pexels.com/v1/search?query={requests.utils.quote(q)}&per_page=5&orientation=landscape'
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            if result.returncode == 0:
                data = json.loads(result.stdout)
                for p in data.get('photos', []):
                    url = p.get('src', {}).get('large2x') or p.get('src', {}).get('large')
                    if url:
                        print(f"  ✓ Pexels image for '{q}': {url[:80]}...")
                        return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

def validate_image_url(url):
    if not url:
        return False
    banned = ['fbcdn.net', 'cdninstagram.com', 'lookaside.fbsbx.com']
    if any(b in url for b in banned):
        return False
    try:
        r = requests.get(url, timeout=10, stream=True,
                        headers={'User-Agent': 'TheVideshi/1.0 (thevideshi.com)'})
        ct = r.headers.get('Content-Type', '')
        if 'image' not in ct:
            print(f'  ⚠ Not an image: ct={ct}')
            return False
        chunk = r.raw.read(6000)
        if len(chunk) > 5000:
            return True
        print(f'  ⚠ Image too small: {len(chunk)} bytes')
    except Exception as e:
        print(f'  ⚠ Validation error: {e}')
    return False

# ── articles ─────────────────────────────────────────────────────────
articles = []

# ── ARTICLE 1: Virat Kohli 600+ Runs Record ────────────────────────
articles.append({
    'headline': "Virat Kohli Becomes the First Player in IPL History to Score 600 Runs in Four Consecutive Seasons",
    'subheadline': "The 37-year-old reached the milestone in Qualifier 1 against Gujarat Titans, adding another line to a record book that increasingly reads like autobiography",
    'slug': 'virat-kohli-600-runs-four-consecutive-ipl-seasons-record-rcb-2026-20260528',
    'category': 'sports',
    'vertical': 'sports',
    'tags': ['Virat Kohli', 'IPL', 'RCB', 'IPL 2026', 'cricket records', 'batting milestone'],
    'urgency': 'daily',
    'score_total': 78,
    'sources': [
        {'name': 'Cricbuzz', 'url': 'https://www.cricbuzz.com'},
        {'name': 'ESPNcricinfo', 'url': 'https://www.espncricinfo.com'},
        {'name': 'Mykhel', 'url': 'https://www.mykhel.com'}
    ],
    'body': """Virat Kohli does not chase records. Records simply happen to orbit the same places he occupies. On Monday night at the HPCA Stadium in Dharamsala, with the Himalayas framing the floodlights behind him, Kohli stroked 43 off 25 balls against Gujarat Titans in IPL 2026 Qualifier 1. It was not his most spectacular innings. It was not the decisive one — that belonged to his captain Rajat Patidar, who smashed an unbeaten 93 off 33 balls. But buried inside those 43 runs was a number that matters more than any single knock: 600.

Kohli has now scored 600 or more runs in four consecutive IPL seasons. No one in the tournament's 19-year history has done this before. Chris Gayle managed three straight 600-plus seasons. KL Rahul did it three times as well. Kohli has gone past both.

## The Numbers Behind the Milestone

His 2026 tally stands at 600 runs across 15 matches, with a strike rate of 164.38. He has four fifties and one century — a magnificent 105 not out against Kolkata Knight Riders earlier in the season that reminded the cricket world he still has gears most batters have never found.

The four-season arc tells the story of an athlete who refuses to decline on anyone else's schedule. In 2023, when many expected him to slow down, he piled on 639 runs. In 2024, he scored a tournament-record 741. In 2025, the year RCB finally won their first-ever IPL title, he contributed 708. And now, in 2026, another 600.

Across his IPL career, Kohli has now crossed 9,000 runs — a threshold no other player has reached. He has also become the first batter to score 500 runs specifically against Gujarat Titans, a team that has existed for only five seasons.

## What It Means for RCB's Title Defence

The milestone came at the perfect time. RCB's 92-run demolition of Gujarat Titans in Qualifier 1 sent them straight to the IPL 2026 final, scheduled for Saturday, May 31, at Mullanpur. They are chasing back-to-back titles — something only Mumbai Indians and Chennai Super Kings have achieved in IPL history.

Kohli's form is a significant reason why RCB enter the final as favourites. While Patidar has taken over the explosive role and Bhuvneshwar Kumar leads a formidable bowling attack with 26 wickets, Kohli provides the stability that allows the rest of the lineup to take risks. His 43 in Qualifier 1 came at a crucial point: he put on a rapid opening stand that set the platform for Patidar's assault.

## The Diaspora Angle

For the millions of Indian cricket fans watching from the United States, the United Kingdom, Canada, and the Gulf, Kohli's longevity is personal. He was the player many NRI families grew up watching — the teenager who led India to the 2008 Under-19 World Cup, the man who inherited Sachin Tendulkar's mantle, the captain who made run-chases look like destiny.

Now 37, Kohli is playing in what many believe could be his final IPL season, though he has said nothing about retirement. Every innings carries a quiet weight for diaspora fans who have followed him for nearly two decades across time zones and streaming services and 3 AM alarm clocks.

## What Comes Next

RCB await the winner of Thursday's Qualifier 2 between Gujarat Titans and Rajasthan Royals. If GT progress, Kohli will face Kagiso Rabada and Jofra Archer for the second time in the playoffs. If RR advance, the 15-year-old Vaibhav Sooryavanshi — who has already broken Chris Gayle's all-time sixes record this season — could be the man standing between Kohli and a second consecutive title.

Either way, when Kohli walks out for the final at Mullanpur, the number 600 will already be stitched into the record. And for a player who has made the IPL his personal stage for 18 seasons, four straight 600-run campaigns may be the achievement that ages best of all.""",
    'person_for_image': 'Virat Kohli',
    'image_caption': 'Virat Kohli during IPL 2026 — the first player to score 600+ runs in four consecutive seasons',
    'image_attribution': 'Wikimedia Commons',
})

# ── ARTICLE 2: IPL September-October Window ─────────────────────────
articles.append({
    'headline': "The IPL Could Move to September. For NRIs, That Changes Everything.",
    'subheadline': "BCCI chairman Arun Dhumal confirms discussions about shifting the tournament to a September-October window, citing extreme heat, broadcaster interest, and the pull of Diwali-season advertising",
    'slug': 'ipl-september-october-window-dhumal-bcci-schedule-shift-nri-impact-20260528',
    'category': 'sports',
    'vertical': 'sports',
    'tags': ['IPL', 'BCCI', 'Arun Dhumal', 'IPL schedule', 'NRI', 'cricket calendar', 'Diwali'],
    'urgency': 'daily',
    'score_total': 75,
    'sources': [
        {'name': 'BestMediaInfo', 'url': 'https://www.bestmediainfo.com'},
        {'name': 'Cricbuzz', 'url': 'https://www.cricbuzz.com'},
        {'name': 'CricTracker', 'url': 'https://www.crictracker.com'},
        {'name': 'CricketAddictor', 'url': 'https://www.cricketaddictor.com'}
    ],
    'body': """The Indian Premier League has been a March-to-May institution since its first season in 2008. For eighteen years, the tournament has occupied the hottest months of the Indian calendar — a scheduling reality that has produced heatstroke scares, exhausted cricketers, and, for diaspora fans in the Northern Hemisphere, an overlap with the end of the American and European work year that makes following every match a logistical challenge.

That may be about to change.

In a series of interviews this week, IPL chairman Arun Dhumal confirmed that the BCCI is actively discussing a shift to a September-October window. The conversations involve broadcasters, franchise owners, and the ICC's Future Tours Programme committee. Nothing has been decided. But the direction of travel is unmistakable.

## Why the Change Is Being Considered

Three factors are driving the discussion.

**Heat.** The 2026 season has been one of the most punishing on record. Multiple IPL matches this season were played in temperatures exceeding 42°C. The Qualifier 1 in Dharamsala — a hill station — was deliberately chosen partly for its cooler climate. The BCCI can no longer ignore the medical reality of asking athletes to perform at peak intensity in Indian summer conditions.

**Player fatigue.** The modern cricketer plays year-round. The IPL's March-May slot clashes with the end of the international summer in Australia and South Africa, forcing overseas stars to fly in mid-season. A September-October window would sit between the English summer and the Australian home season, potentially improving squad availability.

**Advertising.** This is the factor that may ultimately decide the outcome. Dhumal explicitly mentioned the Diwali advertising season as a commercial draw. September-October places the IPL's final stages in the weeks before Diwali, when Indian brands spend most aggressively. From a broadcaster's perspective, this is the most valuable advertising inventory window in the Indian market.

## The Two-Window Model

Dhumal also floated a more radical idea: splitting the IPL across two windows. One phase — perhaps February to early April — would host the league stage. A second phase in September-October would cover the playoffs and final. This would shorten each concentrated block of matches, reduce player workload, and create two annual spikes of IPL viewership rather than one.

The two-window model has precedent. The English Premier League effectively operates with a winter break. Formula 1 splits its season across nine months. The idea is not as alien as it might sound to cricket traditionalists.

## What It Means for the Diaspora

For the estimated 32 million Indians living abroad, a September-October IPL window has immediate practical implications.

**Better time zones for North America.** The current March-May window puts most IPL matches at inconvenient times for US and Canadian viewers — early morning on the East Coast, pre-dawn on the West Coast. September-October in India would overlap with autumn in North America, and the shorter days could make afternoon matches more accessible.

**Diwali season alignment.** For NRI families, the IPL final happening in the week before Diwali would create a cultural super-event. Cricket and Diwali are already the two most unifying threads of diaspora identity. Combining them into a single season could transform how NRI communities gather and celebrate.

**Fantasy and betting markets.** The growing legal sports betting market in North America has begun to include IPL. A September-October window would reduce competition with the NBA and NHL playoffs (which dominate March-May) and instead compete with the NFL regular season — a period when cricket could carve out a distinct niche among South Asian audiences.

## The Obstacles

Not everyone is convinced. Franchise owners who have invested in stadium infrastructure designed for pre-monsoon conditions would face the challenge of September rain — monsoon season typically ends in late September across much of India. The IPL has never been played during the monsoon, and the logistics of indoor-quality drainage across fourteen venues are nontrivial.

The ICC's crowded calendar is another hurdle. September-October overlaps with bilateral series that generate revenue for smaller cricket boards. The BCCI's leverage within the ICC is substantial, but unilaterally shifting the IPL would provoke resistance from boards that depend on that window for their own fixtures.

## What Happens Now

Dhumal was careful to frame this as a discussion, not a decision. The earliest any change could take effect is IPL 2028, given existing broadcast contracts and the ICC's scheduling cycle. But the fact that the BCCI chairman is speaking publicly about it — rather than letting it leak as a rumour — suggests the conversation is further along than the cautious language implies.

For NRI cricket fans who have spent eighteen years setting 4 AM alarms and muting Slack channels to avoid spoilers, the prospect of an autumn IPL is more than a scheduling change. It is a recognition that the diaspora audience matters enough to rethink the calendar.""",
    'person_for_image': None,
    'pexels_query': 'cricket stadium night lights',
    'pexels_fallback': 'cricket match stadium India',
    'image_caption': 'The IPL may move to a September-October window as the BCCI considers scheduling changes',
    'image_attribution': 'Pexels',
})

# ── ARTICLE 3: Kagiso Rabada Powerplay Record ──────────────────────
articles.append({
    'headline': "Kagiso Rabada Now Holds the All-Time IPL Record for Powerplay Wickets in a Season",
    'subheadline': "The South African fast bowler took his 18th powerplay wicket in Qualifier 1, surpassing Mohammed Shami's 2023 mark and confirming his status as the most dangerous new-ball bowler in IPL 2026",
    'slug': 'kagiso-rabada-ipl-powerplay-wickets-record-18-shami-gt-2026-20260528',
    'category': 'sports',
    'vertical': 'sports',
    'tags': ['Kagiso Rabada', 'IPL', 'Gujarat Titans', 'fast bowling', 'IPL 2026', 'powerplay', 'cricket records'],
    'urgency': 'daily',
    'score_total': 72,
    'sources': [
        {'name': 'Cricbuzz', 'url': 'https://www.cricbuzz.com'},
        {'name': 'Wisden', 'url': 'https://www.wisden.com'},
        {'name': 'ESPNcricinfo', 'url': 'https://www.espncricinfo.com'}
    ],
    'body': """The wicket that broke the record was not even particularly dramatic. Second over of RCB's innings in Qualifier 1 at Dharamsala. Venkatesh Iyer, the tall left-hander who had been promoted up the order, pushed at a ball outside off stump. Edge. Gone. Kagiso Rabada did not celebrate extravagantly. He simply walked back to his mark, adjusted his collar, and prepared to bowl the next ball.

That was powerplay wicket number 18 in IPL 2026. No bowler in the tournament's history has ever taken more in a single season.

## The Record That Was

Mohammed Shami set the previous benchmark in IPL 2023, when he took 17 wickets in the first six overs across Gujarat Titans' title-winning campaign. It was a record built on raw pace and the ability to move the new ball both ways — skills that made Shami virtually unplayable in those first six overs.

Rabada has matched those skills and added something else: relentless accuracy under pressure. His 18 powerplay wickets have come across 15 matches, at an economy rate of 8.34 in the first six overs — remarkable when you consider that powerplay scoring rates across IPL 2026 have averaged over 9 runs per over.

## How He Does It

Rabada's method in the powerplay is deceptively simple. He bowls at the stumps. He hits the length that forces batters to play. And he varies his pace just enough — between 140 and 148 km/h — to create the hesitation that produces edges, bowled dismissals, and LBW decisions.

What makes him particularly effective in 2026 is his partnership with Jofra Archer at the other end. Gujarat Titans' new-ball pairing of Rabada and Archer has been the best in the tournament. Archer has 24 wickets of his own, and between them, the two fast bowlers have taken 50 wickets — nearly half of GT's entire tournament tally.

The numbers tell only part of the story. Rabada's powerplay wickets have often come at critical moments. He dismissed Ruturaj Gaikwad in the first over against CSK. He removed Yashasvi Jaiswal inside the powerplay against Rajasthan Royals. He got Virat Kohli early in the league stage meeting between GT and RCB. The best batters in the tournament have all fallen to him before the field spreads.

## The Qualifier 1 Performance

In the match where he broke the record, Rabada's overall figures were modest by his standards — 2 for 43 in four overs. But the damage he did was in the context of the game. His early removal of Iyer disrupted RCB's middle-order timing, and his second wicket — Jitesh Sharma, caught behind off a rising delivery — came at a moment when GT were trying to slow the run rate.

It was not enough. RCB scored 254 for 5, the highest total in IPL playoff history. Rajat Patidar's unbeaten 93 off 33 balls was simply too good for any bowling attack. GT were bowled out for 162, losing by 92 runs.

But Rabada's record survived the defeat. Personal landmarks rarely depend on team results, and this one is significant enough to stand on its own.

## A Quiet Giant

Rabada is not an IPL showman. He does not have a signature celebration. He does not court the cameras. He joined Gujarat Titans before the 2024 season and has been their most consistent performer since — a fact that gets lost in the noise around Shubman Gill's captaincy and Rashid Khan's spin wizardry.

At 30, Rabada is in the prime of his fast-bowling career. He has 26 wickets in IPL 2026, tied with Bhuvneshwar Kumar at the top of the Purple Cap standings. He has been GT's most valuable player in a season where they have reached the playoffs despite a middle-order that has been inconsistent at best.

## What Comes Next

Gujarat Titans face Rajasthan Royals in Qualifier 2 on Thursday at Mullanpur. If GT progress to the final, Rabada will bowl the powerplay overs against RCB for the second time in a week. The record will already be his. The question is whether he can add to it — and whether those first six overs can help GT overturn a 92-run deficit from the last time these two teams met.

For diaspora fans who appreciate the craft of fast bowling — the seam position, the wrist angle, the controlled aggression that defines the art — Rabada's 18 powerplay wickets are a season-defining achievement. In a tournament increasingly dominated by batters and sixes and strike rates above 200, the South African has proven that the new ball still belongs to the bowler who knows how to use it.""",
    'person_for_image': 'Kagiso Rabada',
    'person_for_image_alt': 'Kagiso Rabada (cricketer)',
    'pexels_query': 'fast bowling cricket',
    'pexels_fallback': 'cricket bowler action',
    'image_caption': 'Kagiso Rabada — holder of the IPL all-time powerplay wickets record with 18 in a single season',
    'image_attribution': 'Wikimedia Commons',
})

# ── publish ──────────────────────────────────────────────────────────
print(f'\n{"="*60}')
print(f'Sports Writer — {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")}')
print(f'Articles to publish: {len(articles)}')
print(f'{"="*60}\n')

for i, art in enumerate(articles, 1):
    print(f'\n── Article {i}/{len(articles)}: {art["headline"][:70]}...')

    # Image sourcing
    img_url = None
    img_attr = art.get('image_attribution', '')

    # Try Wikipedia for person articles
    if art.get('person_for_image'):
        person = art['person_for_image']
        print(f'  → Wikipedia: {person}')
        img_url = fetch_wikipedia_person_image(person)
        if not img_url and art.get('person_for_image_alt'):
            print(f'  → Wikipedia alt: {art["person_for_image_alt"]}')
            img_url = fetch_wikipedia_person_image(art['person_for_image_alt'])
        if img_url:
            img_attr = 'Wikimedia Commons'

    # Pexels fallback
    if not img_url and art.get('pexels_query'):
        print(f'  → Pexels: {art["pexels_query"]}')
        img_url = fetch_pexels_image(art['pexels_query'], art.get('pexels_fallback'))
        if img_url:
            img_attr = 'Pexels'

    # Validate
    if img_url:
        if validate_image_url(img_url):
            print(f'  ✓ Image OK')
        else:
            print(f'  ✗ Image failed validation, trying fallback...')
            img_url = None
            # Try pexels as fallback for failed wikipedia images
            if art.get('pexels_query'):
                img_url = fetch_pexels_image(art['pexels_query'], art.get('pexels_fallback'))
                if img_url and validate_image_url(img_url):
                    img_attr = 'Pexels'
                    print(f'  ✓ Fallback image OK')
                else:
                    img_url = None

    # Build record
    now_iso = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S+00:00')
    record = {
        'headline': art['headline'],
        'subheadline': art['subheadline'],
        'slug': art['slug'],
        'category': art['category'],
        'vertical': art['vertical'],
        'body': art['body'],
        'sources': art['sources'],
        'tags': art['tags'],
        'urgency': art['urgency'],
        'score_total': art['score_total'],
        'image_url': img_url,
        'image_caption': art.get('image_caption', ''),
        'image_attribution': img_attr if img_url else None,
        'status': 'published',
        'published_at': now_iso,
        'created_at': now_iso,
    }

    result = sb_insert('p2_articles', record)
    if result:
        art_id = result.get('id', 'unknown')
        print(f'  ✓ Published: id={art_id}')
        print(f'    slug={art["slug"]}')
    else:
        print(f'  ✗ FAILED to publish')

    time.sleep(1)

print(f'\n{"="*60}')
print('Sports writer complete.')
print(f'{"="*60}')

#!/usr/bin/env python3
"""The Videshi Sports Writer — May 29, 2026"""

import json, os, sys, time, uuid, re, urllib.parse
import requests
from datetime import datetime, timezone

# ── Load env ──────────────────────────────────────────
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
            key, _, val = line.partition('=')
            val = val.strip().strip('"').strip("'")
            os.environ.setdefault(key.strip(), val)

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SB_URL = os.environ['SUPABASE_URL']
SB_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

HEADERS = {
    'apikey': SB_KEY,
    'Authorization': f'Bearer {SB_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

# ── Wikipedia image ───────────────────────────────────
def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
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
                print(f"  ✓ Wikipedia image found for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None

# ── Pexels fallback ───────────────────────────────────
def fetch_pexels_image(query, fallback_query=None):
    """Fetch image from Pexels using curl (Python urllib gets 403)."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            import subprocess
            result = subprocess.run(
                ['curl', '-sS', '-H', f'Authorization: {PEXELS_KEY}',
                 f'https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=3&orientation=landscape'],
                capture_output=True, text=True, timeout=15
            )
            data = json.loads(result.stdout)
            photos = data.get('photos', [])
            for p in photos:
                url = p.get('src', {}).get('large2x') or p.get('src', {}).get('large')
                if url:
                    print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

# ── Image validation ──────────────────────────────────
def validate_image_url(url):
    """Check URL returns a valid image >5KB."""
    if not url:
        return False
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                          headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get('Content-Type', '')
        cl = int(r.headers.get('Content-Length', 0))
        if 'image' in ct and cl > 5000:
            return True
        # Try GET for servers that don't return Content-Length on HEAD
        if 'image' in ct:
            r2 = requests.get(url, timeout=10, stream=True,
                              headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
            chunk = r2.raw.read(6000)
            if len(chunk) > 5000:
                return True
    except:
        pass
    return False

# ── Banned URL check ──────────────────────────────────
def is_banned_url(url):
    if not url:
        return True
    banned = ['fbcdn.net', 'cdninstagram.com', 'lookaside.fbsbx.com']
    banned_params = ['_nc_ht=', '_nc_cat=', 'ccb=']
    for b in banned:
        if b in url:
            return True
    for p in banned_params:
        if p in url:
            return True
    return False

# ── Supabase insert ───────────────────────────────────
def sb_insert(data):
    """Insert article into p2_articles."""
    r = requests.post(
        f"{SB_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=data,
        timeout=30
    )
    if r.status_code in (200, 201):
        result = r.json()
        if isinstance(result, list) and result:
            return result[0].get('id')
        return None
    print(f"  ✗ Insert failed: {r.status_code} {r.text[:300]}")
    return None

# ── Articles ──────────────────────────────────────────

articles = []

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ARTICLE 1: Norway Chess — Gukesh Birthday Blues
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

art1_body = """The last time Magnus Carlsen faced D Gukesh at Norway Chess, the Norwegian slammed the table after blundering a winning position. The clip went viral, played on loop across Indian chess Twitter, and became the defining image of the 2025 tournament. A year later, Carlsen got his revenge — and this time, there was no drama. Only clinical precision.

Carlsen beat the reigning World Classical Champion in 42 moves in Round 4 on Thursday, climbing from last place to sole fourth with 4.5 points. Gukesh, who turned twenty just hours after the defeat, dropped to the bottom of the standings with 3.5 points — the worst position of his career at an elite super-tournament.

"I wouldn't say I was super-motivated today," Carlsen told reporters afterward. "I didn't have a lot of expectations, but I was happy with the way things went in the opening."

The game began with Gukesh choosing an ambitious setup with the white pieces, pushing for an early advantage. But Carlsen, playing black, gradually took control. A key rook manoeuvre gave the five-time world champion a dominant central post, and from there, Gukesh's ambition worked against him.

"He sometimes plays a little too ambitiously and I think he did that today as well," Carlsen said. "He wanted to prove a serious advantage, and I'm not sure there was one. Eventually, he played himself into some trouble and I gradually took over."

The decisive moment came on move 28, when Carlsen played f4, launching a fierce kingside attack. Gukesh found the best defensive move in Bd3 but faltered one move later, and the game slipped away. After Carlsen's passed a-pawn became unstoppable, Gukesh resigned on move 42. He left the playing hall through a side exit, avoiding scores of young fans waiting for autographs.

## Pragg's Quiet Ascent

While the world champion struggled, his compatriot R Praggnanandhaa continued building an increasingly impressive campaign. A day after beating Carlsen classically in Round 3 — when the Norwegian self-destructed from a winning position in a sequence eerily similar to the 2025 table-slam game — Pragg followed up by defeating Vincent Keymer in Armageddon in Round 4, sealing 1.5 points in just 17 moves.

"The Armageddon went smooth," Praggnanandhaa said, understating what has been the most composed Indian performance at Norway Chess in years.

Pragg now sits in sole second place on 6 points, 2.5 behind tournament leader Alireza Firouzja. The temperamental contrast between India's two top players has become the narrative of the event: Gukesh overreaches, Pragg absorbs pressure and converts.

## Firouzja Survives, Barely

Firouzja maintained his lead despite his first setback of the tournament. Wesley So stopped the French-Iranian's winning streak by drawing the classical game and prevailing in Armageddon. But Firouzja still collected a point to extend his total to 8.5 — a comfortable 2.5-point cushion over Pragg.

The standings heading into Friday's rest day: Firouzja 8.5, Praggnanandhaa 6, So 5.5, Carlsen 4.5, Keymer 4, Gukesh 3.5.

## India's Women Falter

In the women's section, Divya Deshmukh suffered her first Armageddon loss after three consecutive tiebreak wins, going down to defending champion Anna Muzychuk. The defeat dropped the World Cup winner from sole second to a three-way tie for third on 5.5 points. Koneru Humpy continued to struggle at the bottom of the six-player field after another Armageddon loss to Zhu Jiner.

## What Comes Next

After the rest day, Gukesh faces Praggnanandhaa in Round 5 — a head-to-head between India's world champion and the player who has looked sharper in every way at this tournament. For the millions of Indian chess fans across the diaspora who have followed Gukesh's rise since his prodigious teenage years, the question is no longer whether he can win Norway Chess. It is whether he can avoid finishing last.

For NRIs following from the US, the next round begins Saturday. Norway Chess streams on Chess24 and the official tournament channel.

*Sources: Chess.com, Chessbase, PTI via Devdiscourse, Swadesi News*"""

articles.append({
    "headline": "Gukesh Turned Twenty Hours After Losing to Carlsen. He Is Last at Norway Chess. Pragg Is Second.",
    "subheadline": "The world champion's birthday present was a classical defeat in 42 moves. Praggnanandhaa has quietly become India's strongest player in Oslo. Their Round 5 head-to-head is next.",
    "body": art1_body.strip(),
    "slug": "gukesh-turns-20-loses-carlsen-last-norway-chess-2026-pragg-second-firouzja-leads-20260529",
    "category": "sports",
    "sources": ["Chess.com", "Chessbase", "PTI/Devdiscourse", "Swadesi News"],
    "person_for_image": "D Gukesh",
    "image_attribution": "Wikimedia Commons",
    "diaspora_angle": "Gukesh and Praggnanandhaa are global icons for the Indian chess diaspora. Millions of NRIs follow Norway Chess — the drama between India's two best players defines the narrative.",
    "vertical": "sports",
    "tags": ["chess", "norway-chess", "gukesh", "praggnanandhaa", "carlsen", "firouzja", "divya-deshmukh"],
    "urgency": "medium",
    "score_total": 82
})

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ARTICLE 2: Singapore Open — Indian Doubles Surge
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

art2_body = """India's best week in international badminton this year entered a new stage on Friday at the Singapore Open, with Satwiksairaj Rankireddy and Chirag Shetty reaching the men's doubles semifinals and the mixed doubles pair of Dhruv Kapila and Tanisha Crasto continuing their remarkable run into the last four.

It is a rare achievement for India to have multiple pairs in the semifinal stages of a BWF Super 750 event — the second-highest tier on the World Tour. For a country whose badminton identity has long been defined by singles stars like PV Sindhu and Saina Nehwal, the doubles breakthrough represents something structural. Indian badminton is getting deeper.

## Satwik-Chirag Grind Through a Test

The fourth-seeded Satwik and Chirag advanced to the semifinals after navigating what has been a demanding draw. In the round of 16, they came through a three-game battle against Chinese Taipei's Lee Jhe-huei and Yang Po-hsuan, losing the second game 11-21 before pulling together a tense 21-18 deciding game to win the match. The victory extended their head-to-head record over the Taipei pair to 7-0, but neither the score nor the record reflected how tight the contest was.

Their semifinal opponents are the top seeds, South Korea's Kim Won-ho and Seo Seung-jae — a pair ranked higher than any duo Satwik and Chirag have beaten at this tournament. It will be one of the biggest doubles matches of the year for Indian badminton. A win would put them in a Super 750 final.

## Dhruv-Tanisha's Run Continues

The story of India's Singapore Open has been Dhruv Kapila and Tanisha Crasto. After their stunning comeback victory over an Olympic medal-winning pair in the second round — losing the first game 8-21 before storming back to win the next two — the mixed doubles duo have continued to advance through the bracket.

Their semifinal run in a Super 750 event is a career milestone. Indian mixed doubles has traditionally been the weakest of the five disciplines, and seeing Kapila and Crasto deep in the draw of a major tournament signals a shift that the Badminton Association of India and national coaches have long worked toward.

## Sindhu's Eight-Match Hoodoo

PV Sindhu arrived in the quarterfinals in superb form, dropping just 21 points across her first two matches. The two-time Olympic medallist demolished Japan's Riko Gunji 21-9, 21-12 in just 37 minutes after eliminating Indonesian fifth seed Putri Kusuma Wardani in the opening round.

But her quarterfinal opponent was the wall she has never scaled: An Se-young, the reigning Olympic champion and world number one. Their head-to-head stood at 0-8 in the South Korean's favour — the most lopsided record of Sindhu's career against any active top player. Breaking that streak at a Super 750 tournament would have been a statement of intent; failing to break it is no surprise, but still painful.

## Lakshya's Quiet Passage

Lakshya Sen advanced to the quarterfinals after Thailand's Kunlavut Vitidsarn retired after just two points of their round-of-16 encounter. The anticlimactic progression meant Sen barely broke a sweat, which could prove a double-edged sword — fresh legs but no match rhythm heading into a quarterfinal against Japan's Koki Watanabe.

## Why This Matters for the Diaspora

For the Indian badminton fan base abroad — sizable and growing, especially in the UK and Southeast Asian NRI communities — the Singapore Open results offer a rare moment of depth. It is no longer just one Indian star carrying the flag at international tournaments. Satwik-Chirag are a genuine world-class pair. Dhruv-Tanisha are emerging fast. And Sindhu, even at this stage of her career, keeps reaching deep rounds at major events.

The Singapore Open semifinals are scheduled for Saturday. The men's doubles semifinal between Satwik-Chirag and Kim-Seo will be one of the most-watched badminton matches by Indian fans this month.

*Sources: IANS, MyKhel, BWF Singapore Open official draw*"""

articles.append({
    "headline": "Satwik-Chirag Are in the Singapore Open Semifinals. Dhruv Kapila and Tanisha Crasto Are One Round From the Final.",
    "subheadline": "India has multiple doubles pairs in the last four of a BWF Super 750 event. Sindhu faced the world number one in the quarterfinals. Lakshya Sen advanced through a walkover.",
    "body": art2_body.strip(),
    "slug": "satwik-chirag-singapore-open-semifinals-dhruv-tanisha-mixed-doubles-india-badminton-super750-20260529",
    "category": "sports",
    "sources": ["IANS", "MyKhel", "BWF Singapore Open draw"],
    "person_for_image": "Satwiksairaj Rankireddy",
    "image_attribution": "Wikimedia Commons",
    "diaspora_angle": "Indian badminton's depth is a source of diaspora pride. NRIs in the UK and Southeast Asia follow Satwik-Chirag closely. The emergence of multiple Indian pairs in Super 750 semifinals is a generational shift.",
    "vertical": "sports",
    "tags": ["badminton", "singapore-open", "satwik-chirag", "dhruv-kapila", "tanisha-crasto", "pv-sindhu", "lakshya-sen"],
    "urgency": "medium",
    "score_total": 78
})

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ARTICLE 3: GT vs RR Qualifier 2 Match-Day Guide
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

art3_body = """Friday night in Mullanpur is the last stop before the IPL 2026 final. Gujarat Titans and Rajasthan Royals meet in Qualifier 2 at the Maharaja Yadavindra Singh International Cricket Stadium, with the winner earning the right to face Royal Challengers Bengaluru in Sunday's title decider in Ahmedabad. The loser goes home.

Both teams arrive bruised. Gujarat were demolished by RCB in Qualifier 1, conceding 254 and losing by 92 runs in what was the most lopsided playoff result of the season. Rajasthan are riding high after crushing Sunrisers Hyderabad by 47 runs in the Eliminator at this very ground, powered by Vaibhav Sooryavanshi's astonishing 97 off 29 balls. The contrast in momentum could not be sharper.

## The Matchup That Decides Everything

The entire contest distills to two individual battles.

**Sooryavanshi vs Rabada.** The fifteen-year-old leads the IPL with 680 runs and 65 sixes this season — both records for a player his age. In the Eliminator, he scored a 16-ball fifty, tying Suresh Raina's record for the fastest half-century in an IPL playoff, and broke Chris Gayle's all-time record for most sixes in a single IPL season. But Kagiso Rabada is the tournament's most lethal powerplay bowler: 26 wickets this season, 18 of them inside the first six overs. How Rabada handles Sooryavanshi with the new ball in the first three overs will likely determine the shape of the match.

**Archer vs Gill.** Jofra Archer's 3-for-58 in the Eliminator was a masterclass of pace bowling — Abhishek Sharma out for a duck on the second ball, Travis Head bowled for 17, Ishan Kishan caught off a top-edge for 33. Archer has 24 wickets this season and bowls with venom that few IPL attacks can match. Shubman Gill, Gujarat's captain, has 618 runs this season and 614 career runs against RR — he knows this opposition intimately. His ability to negotiate Archer's pace and bounce in the powerplay is Gujarat's clearest path to a competitive total.

## Head-to-Head: Gujarat Lead 7-3

Gujarat's historical dominance against Rajasthan is significant. In ten previous meetings, the Titans have won seven. In this season, the teams split their league-phase encounters: RR edged a six-run thriller in Ahmedabad, GT responded with a comprehensive 77-run win in Jaipur. The Titans are the more experienced playoff team, having reached at least the qualifier stage in every season of their existence.

## The Venue Favours Runs

The Mullanpur pitch has been a batting paradise in IPL 2026. The Eliminator between RR and SRH saw 439 runs scored. Rajasthan posted 243-for-8 and still won comfortably. With short square boundaries and a true surface that rewards clean hitting, teams batting first at this venue in the playoffs have found totals of 230-plus defensible — but only with quality bowling. Gujarat's attack of Rabada, Mohammed Siraj, Rashid Khan, and Jason Holder has the diversity to apply pressure, but they leaked 254 against RCB in Dharamsala just days ago.

## What Gujarat Need

Gujarat need Sai Sudharsan to bat deep. The left-hander has accumulated 652 runs this season and is the team's anchor. His ability to rotate strike against Jadeja and Punja in the middle overs — where Rajasthan's spin has been excellent — will determine whether Gujarat can build a competitive total. Washington Sundar's all-round contribution is also critical: his off-spin could be key against Sooryavanshi, who has been less dominant against spinners who bowl into his body.

## What Rajasthan Need

Rajasthan need Yashasvi Jaiswal to contribute. In the Eliminator, the opener made 29 off 29 balls while Sooryavanshi blazed at the other end. For RR to win tonight, they need both openers firing — Jaiswal provides the platform, Sooryavanshi provides the acceleration. Ravindra Jadeja's 221 runs and 10 wickets make him the quiet difference-maker: his tight bowling in overs 7-15 strangles opposition scoring rates, and his lower-order hitting has rescued RR multiple times.

## NRI Viewing Guide

The match starts at 7:30 PM IST, which is 10:00 AM Eastern, 7:00 AM Pacific, 3:00 PM BST, and 7:00 PM Dubai time. Live coverage is available on Star Sports and JioHotstar. For NRIs in the US, Willow TV carries the broadcast. The toss is at 7:00 PM IST.

If rain forces a washout and no result is possible even with the 120-minute extension, Gujarat advance to the final by virtue of finishing higher in the league standings (second vs fourth).

*Sources: Cricbuzz, CricTracker, Sporting News, Livemint*"""

articles.append({
    "headline": "Sooryavanshi's 680 Runs Against Rabada's 26 Wickets. Everything About Tonight's Qualifier 2 in Mullanpur.",
    "subheadline": "Gujarat Titans and Rajasthan Royals meet at 7:30 PM IST for a place in Sunday's IPL final against RCB in Ahmedabad. Here is the match-day guide.",
    "body": art3_body.strip(),
    "slug": "gt-vs-rr-qualifier-2-match-day-guide-sooryavanshi-rabada-ipl-2026-mullanpur-20260529",
    "category": "sports",
    "sources": ["Cricbuzz", "CricTracker", "Sporting News", "Livemint"],
    "person_for_image": "Vaibhav Suryavanshi",
    "image_attribution": "Wikimedia Commons",
    "diaspora_angle": "The IPL playoffs are appointment viewing for NRIs worldwide. Tonight's Qualifier 2 determines who faces RCB in Sunday's final — the match times and streaming info for US, UK, and Dubai time zones are included.",
    "vertical": "sports",
    "tags": ["ipl", "ipl-2026", "gt-vs-rr", "qualifier-2", "sooryavanshi", "rabada", "shubman-gill", "jofra-archer"],
    "urgency": "high",
    "score_total": 85
})

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PUBLISH
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

published = 0
now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

for i, art in enumerate(articles, 1):
    print(f"\n{'='*60}")
    print(f"Article {i}: {art['headline'][:80]}...")
    print(f"{'='*60}")

    # Word count check
    wc = len(art['body'].split())
    print(f"  Word count: {wc}")
    if wc < 400:
        print(f"  ✗ SKIPPED — body too short ({wc} words, need 400+)")
        continue

    # Image sourcing
    img_url = None
    person = art.get('person_for_image')
    if person:
        print(f"  Trying Wikipedia for '{person}'...")
        img_url = fetch_wikipedia_person_image(person)
        if not img_url and '(' not in person:
            # Try with disambiguation
            for suffix in ['(chess player)', '(cricketer)', '(badminton)']:
                img_url = fetch_wikipedia_person_image(f"{person} {suffix}")
                if img_url:
                    break

    if not img_url:
        # Pexels fallback with specific terms
        if 'chess' in art['slug']:
            img_url = fetch_pexels_image("chess tournament grandmaster", "chess board game competition")
        elif 'badminton' in art['slug']:
            img_url = fetch_pexels_image("badminton tournament smash", "badminton court shuttlecock")
        elif 'ipl' in art['slug'] or 'cricket' in art['slug']:
            img_url = fetch_pexels_image("cricket stadium T20 match", "cricket batsman hitting six")

    # Validate image
    if img_url and is_banned_url(img_url):
        print(f"  ✗ Banned URL detected, skipping: {img_url[:60]}")
        img_url = None
    
    if img_url and not validate_image_url(img_url):
        print(f"  ✗ Image validation failed: {img_url[:60]}")
        img_url = None

    if img_url:
        print(f"  ✓ Final image URL: {img_url[:80]}...")
    else:
        print(f"  ⚠ No image — publishing without image (better than wrong image)")

    # Build article record
    sources_json = json.dumps([{"name": s} for s in art["sources"]])
    record = {
        "headline": art["headline"],
        "subheadline": art["subheadline"],
        "body": art["body"],
        "slug": art["slug"],
        "category": art["category"],
        "status": "published",
        "published_at": now,
        "sources": sources_json,
        "image_url": img_url,
        "image_attribution": art.get("image_attribution") if img_url else None,
        "diaspora_angle": art.get("diaspora_angle", ""),
        "vertical": art.get("vertical", "sports"),
        "tags": art.get("tags", []),
        "urgency": art.get("urgency", "medium"),
        "score_total": art.get("score_total", 75),
    }

    art_id = sb_insert(record)
    if art_id:
        print(f"  ✓ Published! ID: {art_id}")
        published += 1
    else:
        print(f"  ✗ Failed to publish")

print(f"\n{'='*60}")
print(f"Done. Published {published}/{len(articles)} articles.")
print(f"{'='*60}")

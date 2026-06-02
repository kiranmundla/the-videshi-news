#!/usr/bin/env python3
"""Sports writer - publishes 2 articles for The Videshi."""

import json, os, requests, urllib.parse
from datetime import datetime, timezone

def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, val = line.split('=', 1)
                    os.environ[key.strip()] = val.strip().strip('"').strip("'")

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

def wiki_img(name):
    encoded = urllib.parse.quote(name.replace(' ', '_'))
    try:
        r = requests.get(f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, timeout=10)
        if r.status_code == 200:
            d = r.json()
            return d.get("originalimage",{}).get("source") or d.get("thumbnail",{}).get("source")
    except: pass
    return None

def validate_img(url):
    try:
        r = requests.head(url, timeout=10, allow_redirects=True, headers={"User-Agent":"TheVideshi/1.0"})
        ct = r.headers.get('Content-Type','')
        cl = int(r.headers.get('Content-Length',0))
        return r.status_code == 200 and 'image' in ct and cl > 5000
    except: return False

def insert(article):
    r = requests.post(f"{SUPABASE_URL}/rest/v1/p2_articles", headers=HEADERS, json=article)
    if r.status_code in (200,201):
        data = r.json()
        aid = data[0]['id'] if isinstance(data, list) else data['id']
        print(f"  ✓ Published: {aid}")
        return aid
    print(f"  ✗ Failed: {r.status_code} {r.text[:500]}")
    return None

now = datetime.now(timezone.utc).isoformat()

# ============ ARTICLE 1 ============
print("ARTICLE 1: India Draw 4th Test at Old Trafford")
img1 = wiki_img("Shubman Gill") or wiki_img("Ravindra Jadeja")
if img1 and not validate_img(img1): img1 = None
print(f"  Image: {img1[:60] if img1 else 'None'}")

body1 = """It took seven hours. It took three centuries. It took a partnership of 203 that England could not break. India have drawn the fourth Test at Old Trafford, and the series is going to The Oval.

## From Disaster to Defiance

On Saturday evening, the situation looked beyond retrieval. England had piled up 669 in their first innings — their fifth-highest Test total in history — built around Ben Stokes's magnificent 141 and his haul of 5-72 in India's first-innings 358. Chris Woakes then struck with successive deliveries in the opening over of India's second innings, removing Yashasvi Jaiswal and Sai Sudharsan for ducks. India were 0-2, trailing by more than 300 runs, staring at a series-ending defeat.

Shubman Gill walked in to face a hat-trick ball. He survived it. He survived the next ball too, and the next session, and the next day. What followed was the most determined rearguard of this remarkable series.

## The Gill-Rahul Foundation

Gill and KL Rahul shut out everything for over forty overs on Saturday evening, taking India to 174-2 at stumps. Rahul, who has been the series's most consistent performer alongside Gill, looked set for his third hundred of the campaign before Stokes nipped one back off the pitch to trap him lbw for 90 on Sunday morning.

Gill batted for seven hours in total. His 103 off 228 balls — a marathon of concentration, not pyrotechnics — was his fourth century of the series. With 722 runs this campaign, Gill has surpassed Yashasvi Jaiswal's 712 from the 2023-24 home series against England to set a new record for runs by an Indian batter in a series against England. In his first campaign as captain, the young opener has answered every question about his temperament.

## The Partnership That Saved India

Gill's departure at 222-4 could have been the moment England forced the issue. Instead, it was the moment India began to take the match away entirely.

Ravindra Jadeja, reprieved first ball when Joe Root dropped a tough chance at slip, went on to make 107 not out — his first century of the series after four fifties. At the other end, Washington Sundar compiled an unbeaten 101, his maiden Test hundred, pulling Stokes for a six and a four off successive balls to bring up his fifty.

Their unbroken stand of 203 on a pitch that had flattened considerably since the first two days frustrated a toiling, increasingly fractious England side. Even Stokes, who had put himself through the pain barrier to bowl despite cramping while batting on Saturday, could not prise them apart.

## Records and Context

India have now scored 11 individual hundreds this series — the most by any visiting side in a series in England. Their eventual dominance on Sunday was such that there was no need to send the injured Rishabh Pant, who suffered a severe foot injury in the first innings, out to bat.

The match ended in slightly farcical circumstances. With both Jadeja and Sundar closing in on their centuries, Harry Brook was brought on to bowl. Jadeja smashed a Brook delivery for six to reach his hundred; Sundar then completed his own landmark off the same bowler. The closing overs belonged entirely to India.

## The Oval Awaits

England remain 2-1 up in this five-match series, but the quick turnaround to Thursday's start at The Oval means there is no time for the hosts to reset. An India victory in South London would square the series at 2-2 — a result that seemed almost impossible when Woakes had Jaiswal and Sudharsan in his pocket on Saturday morning.

For the hundreds of thousands of Indian-origin fans in the UK who have made this series a cultural event — filling grounds from Lord's to Old Trafford — the decider is the match they have been waiting for.

## What NRIs Should Know

The fifth and final Test begins Thursday at The Oval, Kennington, South London. Sky Sports has the UK broadcast rights. For fans in the US, Willow TV carries live coverage. Tickets for all five days sold out within hours but resale and returns are available through the Surrey County Cricket Club website."""

id1 = insert({
    "headline": "Jadeja and Sundar Made Hundreds. India Drew the Fourth Test. The Series Goes to The Oval.",
    "subheadline": "From 0-2 in the first over of the second innings to a record-setting draw at Old Trafford — Gill's men have kept the five-match series alive at 2-1",
    "slug": "india-draw-4th-test-old-trafford-jadeja-sundar-centuries-gill-722-runs-oval-decider-nri",
    "body": body1,
    "category": "sports",
    "vertical": "sports",
    "status": "published",
    "published_at": now,
    "image_url": img1,
    "image_attribution": "Wikimedia Commons" if img1 else None,
    "is_editorial": False,
    "is_featured": False,
    "sources": "Flashscore, theScore, Reuters, Sky Sports Cricket",
    "tags": []
})

# ============ ARTICLE 2 ============
print("\nARTICLE 2: Norway Chess Round 7")
img2 = wiki_img("Rameshbabu Praggnanandhaa") or wiki_img("Praggnanandhaa") or wiki_img("Gukesh Dommaraju")
if img2 and not validate_img(img2): img2 = None
print(f"  Image: {img2[:60] if img2 else 'None'}")

body2 = """Round seven of Norway Chess 2026 in Oslo was the day India's chess prodigies showed both their brilliance and their anguish. Praggnanandhaa Rameshbabu inflicted a second consecutive classical loss on Alireza Firouzja. World Champion Gukesh Dommaraju achieved a winning position against tournament leader Wesley So — and could not convert it. And Divya Deshmukh, in the women's event, admitted she "saw ghosts" in a game she dominated but failed to win in classical time.

## Praggnanandhaa's Clinical Takedown

After being beaten by Wesley So in round six, Praggnanandhaa responded with the kind of performance that explains why he is considered one of the most dangerous players in world chess. Facing Firouzja — who entered the round in second place and had been the tournament leader just days ago — Praggnanandhaa played a patient Italian Opening that gradually shifted in his favor.

The key moment came at move 35, when Praggnanandhaa uncorked a stunning exchange sacrifice with Ra1, giving up material to expose the French grandmaster's king. With just two minutes on his clock, Firouzja could not defend the resulting attack. Praggnanandhaa rounded up the exposed king and scored his second classical win of the event, after beating Magnus Carlsen in round three.

This is the second classical loss in a row for Firouzja, who is playing the tournament with an ankle injury. He drops 2.5 points behind So, but with three rounds remaining, the gap is not insurmountable in a format where a classical win is worth three points.

## Gukesh's Heartbreak Against So

The World Champion had every reason to believe he could beat the tournament leader. Playing with the white pieces, Gukesh sacrificed a pawn out of the opening in Marshall Attack style and gradually built a commanding position. The broadcast commentators praised his 28th move, Kf1, as a masterclass in using the king as an active piece in the middlegame.

The problem was the clock. By the time Gukesh had achieved a winning position, he had just 18 minutes left to So's nearly 60. The American grandmaster sacrificed an exchange and fought to equalize. In the final position, with Gukesh under one minute against So's 20, the tournament leader offered a draw — and Gukesh accepted.

Grandmaster David Howell, commentating on the broadcast, noted: "I think Wesley, if he doesn't win the tournament, will regret that moment."

Gukesh salvaged a point by winning the armageddon game with a bold pawn grab on the queenside, but it was cold comfort. Despite showing he can outplay the tournament leader, the World Champion sits in last place in the standings.

## Divya's Ghosts

In the women's event, Divya Deshmukh played a hyper-aggressive Benko Gambit against compatriot Koneru Humpy and achieved full compensation for the sacrificed pawn. By move 19, she had found a devastating queen maneuver targeting the holes around Humpy's king. It looked like a matter of time.

Then, in Divya's own words: "I started seeing ghosts and that's the only reason I didn't win. Nothing was going on in the position and I saw every winning move. Actually, when I played Bd4, I wanted to go c4, but my mind hallucinated and I instead went Bd4."

She recovered to win the armageddon and remains in second place, 2.5 points behind leader Bibisara Assaubayeva of Kazakhstan. The crucial matchup comes in round eight on Tuesday — Divya has the white pieces against Assaubayeva. A classical win would put her back in the lead.

## Carlsen Draws, Then Wins Armageddon

Magnus Carlsen played the King's Indian Defense against Vincent Keymer and admitted afterwards he was "obviously worse at the get-go." In an amusing detail from the broadcast, Carlsen revealed he had discussed this exact opening plan with commentator David Howell in a hot tub after a tournament in Stockholm — and that Howell had won with white. Despite the theoretical disadvantage, both players scored above 98 percent accuracy and the game ended in a draw. Carlsen then won the armageddon to pick up 1.5 points.

With three rounds remaining, the Norwegian said he would "keep trying" but acknowledged he would "need a lot of classical wins."

## Standings After Round 7

In the open section, Wesley So leads with a comfortable margin. Firouzja remains second despite two consecutive losses. Carlsen, Keymer, Praggnanandhaa, and Gukesh are bunched behind.

In the women's event, Assaubayeva extended her lead to 2.5 points after pouncing on a blunder by Zhu Jiner. Divya is second, with Muzychuk edging into sole third after inflicting a sixth consecutive armageddon loss on Women's World Champion Ju Wenjun.

Round eight starts Tuesday, June 2, at 8:30 PM IST.

## The NRI Angle

Norway Chess is streamed free on Chess24's YouTube and Twitch channels. Three of the six players in the open section are Indian, as are two of six in the women's event — a measure of how deeply Indian players now dominate the upper echelons of world chess. The question is whether any of them can catch Wesley So before the final round on June 5."""

id2 = insert({
    "headline": "Praggnanandhaa Beat Firouzja in Classical. Gukesh Had So on the Ropes but Ran Out of Time. Norway Chess Is Wide Open.",
    "subheadline": "Round seven in Oslo belonged to the Indian teenager who scored his second classical win of the tournament — while the World Champion was left ruing a missed chance against the leader",
    "slug": "norway-chess-2026-round-7-praggnanandhaa-beats-firouzja-gukesh-misses-so-divya-nri",
    "body": body2,
    "category": "sports",
    "vertical": "sports",
    "status": "published",
    "published_at": now,
    "image_url": img2,
    "image_attribution": "Wikimedia Commons" if img2 else None,
    "is_editorial": False,
    "is_featured": False,
    "sources": "Chess.com, ChessBase, Norway Chess, Checkmate Daily, Khel Now",
    "tags": []
})

print(f"\n{'='*40}")
print(f"Published: {sum(1 for x in [id1, id2] if x)}/2")
if id1: print(f"  1: {id1}")
if id2: print(f"  2: {id2}")

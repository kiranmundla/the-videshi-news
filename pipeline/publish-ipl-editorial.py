#!/usr/bin/env python3
"""
Publish IPL 2026 Editorial + swap editorial flags.
"""

import os, json, sys, requests, subprocess, urllib.parse
from datetime import datetime, timezone

# Load env
for env_path in [os.path.expanduser("~/.env.supabase"), os.path.expanduser("~/workspace/.env.supabase")]:
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, val = line.split('=', 1)
                    os.environ.setdefault(key.strip(), val.strip().strip('"').strip("'"))

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

pexels_path = os.path.expanduser("~/workspace/.env.pexels")
PEXELS_KEY = None
if os.path.exists(pexels_path):
    with open(pexels_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, val = line.split('=', 1)
                if 'PEXELS' in key.upper():
                    PEXELS_KEY = val.strip().strip('"').strip("'")

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

def fetch_pexels_image(query, fallback_query=None):
    if not PEXELS_KEY:
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            result = subprocess.run(
                ["curl", "-sS", "-H", f"Authorization: {PEXELS_KEY}",
                 f"https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5&orientation=landscape"],
                capture_output=True, text=True, timeout=15
            )
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            for photo in photos:
                url = photo.get("src", {}).get("large2x") or photo.get("src", {}).get("large")
                if url:
                    print(f"  ✓ Pexels image: {url[:80]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error: {e}")
    return None

# ==================== STEP 1: Clear old editorial flag ====================
print("=== Step 1: Clear old editorial flags ===")
r = requests.get(
    f"{SUPABASE_URL}/rest/v1/p2_articles?is_editorial=eq.true&select=id,headline,slug",
    headers=HEADERS, timeout=10
)
old_editorials = r.json() if r.status_code == 200 else []
print(f"Found {len(old_editorials)} current editorial(s)")

for old in old_editorials:
    print(f"  Demoting: {old.get('headline', 'unknown')[:60]}...")
    r = requests.patch(
        f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{old['id']}",
        headers=HEADERS,
        json={"is_editorial": False},
        timeout=10
    )
    print(f"  → {'✓ Done' if r.status_code in (200, 204) else f'✗ {r.status_code}'}")

# ==================== STEP 2: Source image ====================
print("\n=== Step 2: Source hero image ===")
img_url = fetch_pexels_image("IPL cricket trophy celebration India", "cricket stadium celebration night")
img_attr = "Pexels" if img_url else ""

# Also try Wikipedia for IPL
if not img_url:
    try:
        encoded = urllib.parse.quote("Indian_Premier_League")
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            img_url = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img_url:
                img_attr = "Wikimedia Commons"
                print(f"  ✓ Wikipedia image: {img_url[:80]}...")
    except Exception as e:
        print(f"  ⚠ Wikipedia error: {e}")

if not img_url:
    print("  ⚠ No image found — publishing without hero image")

# ==================== STEP 3: Publish editorial ====================
print("\n=== Step 3: Publish IPL editorial ===")

BODY = """Virat Kohli limped between the wickets. He'd been hobbling since the powerplay, his right knee strapped, his movement visibly limited. None of it mattered. With 12 balls remaining and RCB needing a handful of runs, Kohli lofted Rashid Khan over long-on for six. The ball disappeared into the Ahmedabad night. Kohli didn't scream. He didn't cry — not this time. He simply raised his bat, looked at the dugout, and smiled.

Last year, the tears flowed. Seventeen seasons of heartbreak, three lost finals, a franchise synonymous with beautiful failure — all of it had poured out in a single, cathartic moment at the Chinnaswamy. But this year was different. This wasn't relief. This was confirmation.

Royal Challengers Bengaluru are back-to-back IPL champions.

## The Final

The setting was poetic: the Narendra Modi Stadium in Ahmedabad, Gujarat Titans' fortress, their captain Shubman Gill's backyard. RCB won the toss and chose to bowl — a statement of intent that proved prophetic.

Gujarat never got going. Gill fell for 10, Sai Sudharsan for 12, and Jos Buttler's 19 off 23 balls did more harm than good to the run rate. Only Washington Sundar, with an unbeaten 50 off 37, gave the innings any respectability. GT crawled to 155/8.

The chase was clinical. Venkatesh Iyer blazed through the powerplay. When wickets fell in a middle-order wobble — Padikkal, Patidar, and Krunal Pandya departing in quick succession — the crowd sensed a twist. But Kohli, batting with a bad knee and a calm mind, had other plans. His unbeaten 75 off 42 balls — including his fastest-ever IPL fifty in 25 deliveries — was a masterclass in big-game batting. He finished it the way he'd always dreamed: hitting the winning runs himself.

"I've thought of this moment many times," Kohli said afterwards. "To be standing there hitting the winning runs. It's a dream day."

## The Dynasty Question

With this win, RCB enter one of cricket's most exclusive clubs. Only two franchises have ever retained the IPL title: Chennai Super Kings under MS Dhoni (2010-11) and Mumbai Indians under Rohit Sharma (2019-20). Now Rajat Patidar — the man who was once an injury replacement, who captained a team that went 17 seasons without a trophy — sits alongside those two legends.

The numbers speak for themselves. RCB finished the league stage at the top of the table (9-5, NRR +0.783). They hammered GT by 92 runs in Qualifier 1. And in the final, their bowling unit — Bhuvneshwar Kumar (2/29), Josh Hazlewood, and the electrifying Rasikh Salam Dar (3/27) — strangled a batting lineup that simply couldn't cope.

Bhuvneshwar finished the tournament with 28 wickets, the second-highest tally behind GT's Kagiso Rabada (29). Rasikh Salam Dar took 19 — the most by any uncapped Indian bowler this season. And Kohli's 675 runs took his career IPL tally to 9,336, the most by any player in the tournament's history.

From meme franchise to monarch. The arc is complete.

## The Season's True Star: Vaibhav Sooryavanshi

But if this was RCB's season to celebrate, it was Vaibhav Sooryavanshi's season to announce himself to the world.

The numbers are absurd. The 15-year-old from Sambalpur, Odisha, finished with 776 runs at a strike rate of 237.31. He hit 72 sixes — shattering Chris Gayle's all-time single-season record of 59 that had stood since 2012. He scored a century off 37 balls against Sunrisers Hyderabad and three times came agonizingly close to hundreds, scoring in the 90s. In the Eliminator against SRH, he smashed 97 off 29 balls, hitting 12 sixes including three consecutive off Pat Cummins.

He won the Orange Cap. The MVP award. Emerging Player of the Season. Super Striker of the Season. The Super Sixes award. He swept virtually every individual honour the IPL has to give.

And when his Rajasthan Royals were eliminated by GT in Qualifier 2, the cameras caught him in tears — the raw, unfiltered emotion of a teenager who had given everything and come up just short. Two days later, he sat in the VIP box at the Narendra Modi Stadium alongside ICC Chair Jay Shah, watching the final as a guest of honour. The BCCI knows what they have.

James Franklin, SRH's assistant coach, said it best: "I don't think anyone's ever seen a talent like this. It's freakish. To think he's potentially got 25 years left in his career — it's quite scary."

Kumar Sangakkara, Sooryavanshi's coach at the Royals, backed him for an immediate India call-up. The tri-series in Sri Lanka with India A awaits. The senior team won't be far behind.

For the diaspora watching from living rooms in New Jersey and living rooms in London, Sooryavanshi is the reminder that Indian cricket's production line is not just intact — it's accelerating.

## The Lowlights: A Season of Captaincy Carnage

For every fairy tale, there were cautionary tales.

**Mumbai Indians** finished ninth — their worst-ever IPL placement. The five-time champions won just 4 of 14 matches. Hardik Pandya, whose captaincy tenure has been marked by dysfunction and division, confirmed he would step down. The dressing room leaks that plagued MI all season painted a picture of a franchise in crisis — "the division and bitterness have been unusually high since Hardik returned," one insider told the Times of India.

The most damning stat: Jasprit Bumrah, widely regarded as the greatest fast bowler in any format, took just 4 wickets in 13 matches at an average of 102.50 — the worst single-season bowling average in T20 history for any bowler delivering 40-plus overs. The world's best, rendered toothless not by a loss of ability, but by a total absence of support. Four wickets. Thirteen games. For Bumrah. Let that sink in.

**Lucknow Super Giants** fared even worse, finishing dead last at 4-10. Rishabh Pant was released from the captaincy, described as "clueless" in the role.

It was, by most accounts, the worst season for IPL captains in memory. Ajinkya Rahane (KKR, 7th), Ruturaj Gaikwad (CSK, 8th), and Riyan Parag (RR) all faced backlash. Parag's case was particularly stark: Rajasthan made the playoffs despite their captain, not because of him. The team was carried almost single-handedly by a 15-year-old.

And then there was Sai Sudharsan — who became the first player in IPL history to be dismissed hit-wicket in back-to-back matches, doing so in consecutive playoff games. A bizarre, unwanted record for an otherwise fine batsman who finished with the most fours in the tournament (75).

## What This Means

The IPL is 19 seasons old. It has produced generational talents, built billion-dollar franchises, and changed cricket forever. But IPL 2026 feels like a turning point.

RCB's transformation from lovable losers to ruthless champions is the story every underdog franchise dreams of. Kohli, at 37, proved that longevity in T20 cricket isn't just about power — it's about intelligence. And Sooryavanshi, at 15, proved that the next era of Indian cricket isn't coming. It's already here.

The winning six from Kohli's bat sailed into the Ahmedabad night. Somewhere, 17 years of ghosts went quiet.

E Sala Cup Namde. Again.

---

## IPL 2026: By the Numbers

| Award | Winner |
|-------|--------|
| **Champions** | Royal Challengers Bengaluru |
| **Orange Cap** | Vaibhav Sooryavanshi — 776 runs |
| **Purple Cap** | Kagiso Rabada — 29 wickets |
| **MVP** | Vaibhav Sooryavanshi |
| **Emerging Player** | Vaibhav Sooryavanshi |
| **Player of the Final** | Virat Kohli — 75* (42) |
| **Fair Play Award** | Punjab Kings |
| **Most Sixes** | Vaibhav Sooryavanshi — 72 |
| **Most Fours** | Sai Sudharsan — 75 |

### Final Standings

| Pos | Team | W | L | Pts |
|-----|------|---|---|-----|
| 1 | RCB (C) | 9 | 5 | 18 |
| 2 | GT (R) | 9 | 5 | 18 |
| 3 | SRH | 9 | 5 | 18 |
| 4 | RR | 8 | 6 | 16 |
| 5 | PBKS | 7 | 6 | 15 |
| 6 | DC | 7 | 7 | 14 |
| 7 | KKR | 6 | 7 | 13 |
| 8 | CSK | 6 | 8 | 12 |
| 9 | MI | 4 | 10 | 8 |
| 10 | LSG | 4 | 10 | 8 |"""

payload = {
    "headline": "From Memes to Monarchy: RCB's Dynasty Has Arrived",
    "subheadline": "Royal Challengers Bengaluru retain the IPL title with a five-wicket demolition of Gujarat Titans in Ahmedabad — and a 15-year-old from Sambalpur might just have stolen the entire season.",
    "body": BODY,
    "slug": "rcb-ipl-2026-champions-back-to-back-dynasty-kohli-sooryavanshi-editorial",
    "category": "sports",
    "vertical": "sports",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "sources": "The Videshi Editorial Desk",
    "is_editorial": True,
    "image_url": img_url,
    "image_attribution": img_attr,
}

# Remove None values
payload = {k: v for k, v in payload.items() if v is not None}

r = requests.post(
    f"{SUPABASE_URL}/rest/v1/p2_articles",
    headers=HEADERS,
    json=payload,
    timeout=15
)

if r.status_code in (200, 201):
    result = r.json()
    art_id = result[0]["id"] if isinstance(result, list) and result else result.get("id", "unknown")
    print(f"✓ Editorial published! ID: {art_id}")
    print(f"  Headline: {payload['headline']}")
    print(f"  Slug: {payload['slug']}")
    print(f"  Image: {img_url or 'none'}")
else:
    print(f"✗ Failed: {r.status_code} - {r.text[:300]}")
    sys.exit(1)

print("\n=== Done! Old editorial demoted, new IPL editorial is live. ===")

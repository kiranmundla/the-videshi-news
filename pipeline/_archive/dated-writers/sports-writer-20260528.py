#!/usr/bin/env python3
"""The Videshi Sports Writer — 2026-05-28 evening run"""

import json, os, sys, uuid, requests, urllib.parse, re
from datetime import datetime, timezone

# ── Load env ──
def load_env(path):
    if not os.path.exists(path):
        return
    for line in open(path):
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        k, v = line.split('=', 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
PEXELS_KEY   = os.environ.get('PEXELS_API_KEY', '')

HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation',
}

# ── Wikipedia image fetcher ──
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

# ── Pexels fallback ──
def fetch_pexels_image(query, fallback_query=None):
    """Fetch a relevant image from Pexels. Returns URL or None."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            r = requests.get(
                "https://api.pexels.com/v1/search",
                headers={"Authorization": PEXELS_KEY},
                params={"query": q, "per_page": 5, "orientation": "landscape"},
                timeout=10
            )
            if r.status_code == 200:
                photos = r.json().get("photos", [])
                for p in photos:
                    url = p.get("src", {}).get("large2x") or p.get("src", {}).get("large")
                    if url:
                        print(f"  ✓ Pexels image for '{q}': {url[:80]}...")
                        return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

# ── Supabase helpers ──
def sb_insert(table, data):
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/{table}",
        headers=HEADERS,
        json=data,
        timeout=30
    )
    if r.status_code in (200, 201):
        result = r.json()
        if isinstance(result, list) and result:
            return result[0]
        return result
    print(f"  ✗ Insert to {table} failed ({r.status_code}): {r.text[:300]}")
    return None

def sb_patch(table, filters, data):
    url = f"{SUPABASE_URL}/rest/v1/{table}?"
    url += "&".join(f"{k}={v}" for k, v in filters.items())
    r = requests.patch(url, headers=HEADERS, json=data, timeout=30)
    if r.status_code in (200, 204):
        return True
    print(f"  ✗ Patch {table} failed ({r.status_code}): {r.text[:300]}")
    return False

def validate_image(url):
    """Check image URL returns 200 with image content > 5KB."""
    if not url:
        return False
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get('Content-Type', '')
        cl = int(r.headers.get('Content-Length', 0))
        if r.status_code == 200 and 'image' in ct and cl > 5000:
            return True
        # Some servers don't return Content-Length on HEAD
        if r.status_code == 200 and 'image' in ct:
            return True
    except:
        pass
    return False

# ── Banned URL check ──
BAD_DOMAINS = ['fbcdn.net', 'cdninstagram.com', 'lookaside.fbsbx.com']
BAD_PARAMS = ['_nc_ht=', '_nc_cat=', 'ccb=']

def is_banned_url(url):
    if not url:
        return True
    for d in BAD_DOMAINS:
        if d in url:
            return True
    for p in BAD_PARAMS:
        if p in url:
            return True
    return False

# ── Articles ──
articles = []

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ARTICLE 1: India Women beat England in 1st T20I at Chelmsford
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
articles.append({
    "headline": "India Won by Thirty-Eight Runs. Without Harmanpreet. In England's Backyard. The T20 World Cup Starts in Two Weeks.",
    "subheadline": "Smriti Mandhana captained India to a dominant 188/7 against England's 150/8 in the first T20I at Chelmsford. With the Women's T20 World Cup in England starting June 14, India just sent the loudest possible message.",
    "slug": "india-women-beat-england-38-runs-1st-t20i-chelmsford-mandhana-captain-world-cup-prep-20260528",
    "category": "sports",
    "image_person": "Smriti Mandhana",
    "image_pexels_query": "women cricket batting",
    "image_pexels_fallback": "cricket match stadium",
    "body": """India did not need Harmanpreet Kaur to take apart England in their own backyard.

At the County Cricket Ground in Chelmsford on Thursday, India's women posted 188 for 7 in their 20 overs, then bowled England out for 150 for 8, winning the first T20I of the three-match series by 38 runs. Smriti Mandhana, captaining in Harmanpreet's absence, set the tone from the first over.

## A Statement Batting Display

India's total of 188 was built on aggression from the top. Mandhana, who has become the most consistent run-scorer in women's T20I cricket over the past eighteen months, led from the front with the bat and with her field placements. The middle order contributed with purpose — there was no period in the innings where the scoring rate dropped below eight an over.

England won the toss and chose to bowl, backing their seamers in helpful early-morning conditions. For the first three overs, the decision looked sound. Then India accelerated, and never stopped.

Yastika Bhatia's cameo of 21 off just 8 balls in the death overs pushed the total past the 185 mark and into territory that has historically been near-impossible to chase at Chelmsford. Nandini Sharma, making her T20I debut, also contributed with both bat and ball — a promising sign for India's World Cup squad depth.

## England's Chase Falls Apart

England needed the best powerplay of their T20I history to stay in the game. They did not get it.

India's new-ball bowlers extracted movement off the surface, and England's top order — Heather Knight, Sophia Dunkley, and Alice Capsey — all got starts without converting them into the kind of innings the chase demanded. Sophie Ecclestone hit a quickfire 12 off 6 balls late in the innings, but it was cosmetic. At 150 for 8 after 19.6 overs, England were well short.

The 38-run margin flatters England, if anything. India were in control for thirty-nine of the forty overs.

## Harmanpreet's Absence, Mandhana's Authority

The decision to rest Harmanpreet for the opening match was a calculated one. India's coaching staff wanted to test their leadership depth before the T20 World Cup, and Mandhana delivered exactly the kind of performance that suggests India's World Cup campaign will not rise or fall on any single player.

Harmanpreet, who was recently honoured with the Padma Shri, is expected to return for the second T20I in Bristol on Saturday. But Mandhana's captaincy — composed, aggressive, tactically sharp — may have opened a genuine conversation about India's long-term leadership transition plan.

## The World Cup Is Two Weeks Away

This series is not a standalone event. It is the final rehearsal before the ICC Women's T20 World Cup, which begins on June 14 in England. India's Group A opener against Pakistan in Birmingham is exactly seventeen days away.

For NRI fans across the US, UK, and Canada, this result changes the pre-tournament calculus. India entered the England tour with concerns about their death bowling and their ability to defend totals on English pitches. This match addressed both.

The second T20I is in Bristol on Saturday, May 30. The third is in Taunton on June 2. Then the World Cup begins.

India came to England early. They came without their captain. And they won by 38 runs. That is not a warm-up performance. That is a declaration.

---

*Sources: ICC Cricket, Cricbuzz, ESPN Cricinfo*""",
    "sources_json": [
        {"name": "ICC Cricket", "url": "https://www.icc-cricket.com"},
        {"name": "Cricbuzz", "url": "https://www.cricbuzz.com"},
        {"name": "ESPN Cricinfo", "url": "https://www.espncricinfo.com"}
    ],
    "diaspora_angle": "For NRI women's cricket fans in the US and UK, India winning in England without Harmanpreet — two weeks before a T20 World Cup hosted on English soil — is the strongest signal yet that this team has the depth to compete anywhere. Chelmsford, Bristol, and Taunton are all within driving distance of major Indian diaspora hubs in England.",
    "urgency": "breaking",
    "score_total": 85,
    "tags": ["women's cricket", "India women", "T20I", "England tour", "Smriti Mandhana", "T20 World Cup 2026", "Chelmsford"]
})

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ARTICLE 2: French Open Day 5 — Shelton Upset + Tiafoe Survival
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
articles.append({
    "headline": "A Twenty-Year-Old Frenchman Beat the Seventh Seed in Straight Sets. Tiafoe Survived Five. The French Open Keeps Breaking Seeds.",
    "subheadline": "Raphael Collignon stunned Ben Shelton 6-4, 7-5, 6-4 on Court Suzanne Lenglen. Frances Tiafoe saved his tournament in a five-set epic against Hubert Hurkacz. After Sinner's exit, Day 5 at Roland Garros thinned the field even further.",
    "slug": "french-open-2026-day-5-collignon-beats-shelton-tiafoe-five-sets-hurkacz-seeds-falling-20260528",
    "category": "sports",
    "image_person": "Ben Shelton (tennis)",
    "image_pexels_query": "Roland Garros clay court tennis",
    "image_pexels_fallback": "tennis clay court match",
    "body": """One day after Jannik Sinner's collapse against Juan Manuel Cerundolo, the 2026 French Open continued breaking seeds.

On Day 5 at Roland Garros, Raphael Collignon — a twenty-year-old Frenchman playing on home soil — beat seventh seed Ben Shelton 6-4, 7-5, 6-4 on Court Suzanne Lenglen. The crowd carried Collignon from the first game to the last. Shelton, the big-serving American who reached the US Open semifinal in 2023 and has been a consistent top-ten presence since, had no answer for Collignon's movement and court craft on the clay.

## Collignon: The Name to Remember

Collignon is not a complete unknown. He has been climbing the lower tiers of the ATP Tour for two years, winning Challenger-level events in France and building a game specifically suited to clay. But beating a top-ten player in straight sets, in a Grand Slam second round, on Philippe Chatrier's neighbouring court — that is a different order of magnitude.

His six aces matched Shelton's power, but it was the 24 groundstroke winners — 12 forehand, 12 backhand — that told the real story. He hit through Shelton, not around him. The American's movement, always his weakness on clay, was exposed by Collignon's ability to redirect the ball at acute angles.

Collignon broke Shelton three times. Shelton broke him zero.

## Tiafoe's Five-Set War

At the other end of the American spectrum, Frances Tiafoe refused to go quietly. The nineteenth seed survived a five-set battle against Hubert Hurkacz, winning 6-7(5), 7-6(7), 6-4, 6-7(1), 6-4 in a match that lasted over four hours.

Tiafoe was two tiebreak losses into the match when a lesser player would have folded. Instead, he found another gear in the third set, broke Hurkacz twice in the fifth, and secured his place in the third round with the kind of gritty, physical tennis that has made him one of the most watchable players in the draw.

The win keeps alive his best French Open run since 2022, and with Sinner now out of his section of the draw, Tiafoe's path to the quarterfinals has opened up considerably.

## Learner Tien's Comeback

Eighteenth seed Learner Tien also survived a scare, beating Facundo Diaz Acosta 7-5, 4-6, 3-6, 7-6(4), 6-3. The twenty-year-old American, who burst onto the scene at the Australian Open this year, showed the kind of resilience that separates Grand Slam contenders from Grand Slam passengers. Down two sets to one, he found his serve and his forehand in the fourth-set tiebreak and never looked back.

## The Bigger Picture

Through five days, the 2026 French Open has lost its world number one (Sinner), multiple seeds, and had four on-court medical incidents related to the unseasonable Paris heat. The draw is thinning in ways no one predicted.

For the remaining seeds — including Novak Djokovic, Carlos Alcaraz, and Alexander Zverev — the path to the final has become simultaneously easier and more dangerous. Easier because the top of the draw has been gutted. More dangerous because the players who are surviving are battle-tested, physically resilient, and playing without fear.

Day 6 brings the third round. The question is no longer who will win Roland Garros. It is who will still be standing by the second week.

---

*Sources: Roland Garros official, ATP Tour, USA Today*""",
    "sources_json": [
        {"name": "Roland Garros Official", "url": "https://www.rolandgarros.com"},
        {"name": "ATP Tour", "url": "https://www.atptour.com"},
        {"name": "USA Today Sports", "url": "https://www.usatoday.com/sports/tennis/"}
    ],
    "diaspora_angle": "The French Open's seed carnage has cleared paths for underdogs across the draw. For Indian-American tennis fans who follow the ATP closely, the Shelton upset is a reminder that clay-court tennis rewards craft over power — and that the generation coming up behind the Big Three plays without fear on any surface.",
    "urgency": "daily",
    "score_total": 78,
    "tags": ["French Open", "Roland Garros", "Ben Shelton", "Raphael Collignon", "Frances Tiafoe", "tennis upset", "Grand Slam 2026"]
})

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ARTICLE 3: Thunder vs Spurs Game 6 — Can Wembanyama force Game 7?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
articles.append({
    "headline": "Victor Wembanyama's Season Is on the Line Tonight. The Thunder Are One Win From the NBA Finals.",
    "subheadline": "Oklahoma City leads San Antonio 3-2 in the Western Conference Finals. Game 6 tips off Thursday at Frost Bank Center. For the Spurs, it is win or go home. For Wembanyama, it is the biggest game of his career.",
    "slug": "thunder-spurs-game-6-western-conference-finals-wembanyama-sga-nba-playoffs-20260528",
    "category": "sports",
    "image_person": "Victor Wembanyama",
    "image_pexels_query": "NBA basketball playoffs arena",
    "image_pexels_fallback": "basketball court arena game",
    "body": """At 7:30 PM Central Time on Thursday night, Victor Wembanyama will walk onto the court at Frost Bank Center in San Antonio with his season, and possibly his franchise's immediate future, hanging on forty-eight minutes of basketball.

The Oklahoma City Thunder lead the San Antonio Spurs 3-2 in the Western Conference Finals. A Thunder win tonight sends them to the NBA Finals against the New York Knicks. A Spurs win forces a decisive Game 7 in Oklahoma City on Saturday.

## How We Got Here

The series has been a study in contrasts. The Spurs stole Game 1 in Oklahoma City, 122-115, behind a dominant Wembanyama performance. The Thunder responded by winning Games 2 and 3 decisively, with Shai Gilgeous-Alexander scoring at will and the OKC defence suffocating San Antonio's perimeter shooters.

Game 4 in San Antonio was a Spurs blowout — 103-82 — the kind of emphatic home win that suggested the series would go the distance. But Game 5 flipped the script. Back in Oklahoma City, SGA dropped 32 points and 9 assists, Jared McCain — making his first playoff start — hit two clutch threes in the fourth quarter, and the Thunder won 127-114 to take a 3-2 lead.

Alex Caruso added 22 points off the bench in Game 5. Chet Holmgren had 16 points and 11 rebounds. The Thunder's depth, which has been their calling card all season, showed up when it mattered most.

## The Injury Factor

Oklahoma City's injury report is the one variable that could tilt this game. Jalen Williams, the Thunder's second-best player and a critical two-way wing, is listed as questionable with a left hamstring strain. He missed Game 5 entirely. Ajay Mitchell, the backup point guard, remains out with a right soleus strain.

If Williams plays, the Thunder are heavy favourites. If he sits again, San Antonio's home crowd and Wembanyama's brilliance could be enough to force a Game 7.

The Spurs, by contrast, have a clean injury report. Everyone is available. Everything is on the table.

## Wembanyama's Defining Moment

Victor Wembanyama is twenty-two years old. He has been the most transformative player to enter the NBA since LeBron James, a 7-foot-4 unicorn who blocks shots, drills threes, and runs the floor like a guard. His regular-season numbers — including averages north of 27 points, 10 rebounds, and 3.5 blocks — were historically unprecedented for a third-year player.

But the playoffs are different. And this is the game where Wembanyama either extends his season or watches from home as the Thunder and Knicks play for the championship.

The Spurs have not been to the NBA Finals since 2014, the year they dismantled the Miami Heat in five games. That team had Tim Duncan, Tony Parker, and Manu Ginobili. This team has Wembanyama and a supporting cast that has exceeded every expectation. But exceeding expectations is not enough tonight. Only winning is.

## For NRI Fans: How to Watch

The NBA has seen explosive growth in India over the past five years. Wembanyama's combination of skill and spectacle has made him one of the most followed athletes among young Indian sports fans. The game airs on NBC and Peacock in the US, and is available on the NBA app and NBA League Pass internationally.

Tip-off is 7:30 PM CT — that is 6:00 AM IST on Friday morning for viewers in India, and 5:30 PM PDT for NRIs on the US West Coast.

The stakes are simple. Win, and the Spurs live to fight one more game. Lose, and Wembanyama's season ends in the conference finals for the second time. The Thunder, meanwhile, are forty-eight minutes from a Finals rematch against New York.

Thursday night in San Antonio. Elimination basketball. Everything on the line.

---

*Sources: NBA.com, The Oklahoman, Sporting News*""",
    "sources_json": [
        {"name": "NBA.com", "url": "https://www.nba.com"},
        {"name": "The Oklahoman", "url": "https://www.oklahoman.com"},
        {"name": "Sporting News", "url": "https://www.sportingnews.com"}
    ],
    "diaspora_angle": "The NBA's Indian fanbase has grown explosively, with Wembanyama as the single most-searched international athlete among 18-34 Indian viewers. For NRIs on the West Coast, Game 6 tips at 5:30 PM PDT — prime evening viewing. For fans in India, the 6 AM IST start is the kind of appointment television that cricket fans understand instinctively.",
    "urgency": "daily",
    "score_total": 76,
    "tags": ["NBA", "Western Conference Finals", "Victor Wembanyama", "Shai Gilgeous-Alexander", "Thunder", "Spurs", "NBA Playoffs 2026"]
})

# ── Publish ──
now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
published = 0

for i, art in enumerate(articles):
    print(f"\n{'='*60}")
    print(f"Article {i+1}: {art['headline'][:70]}...")
    
    # Image sourcing
    img_url = None
    img_attr = None
    
    # Try Wikipedia first for person articles
    person = art.get('image_person')
    if person:
        img_url = fetch_wikipedia_person_image(person)
        if img_url and not is_banned_url(img_url):
            if validate_image(img_url):
                img_attr = "Wikimedia Commons"
            else:
                print(f"  ⚠ Wikipedia image failed validation for {person}")
                img_url = None
        elif img_url and is_banned_url(img_url):
            print(f"  ⚠ Wikipedia returned banned URL for {person}")
            img_url = None
    
    # Pexels fallback
    if not img_url:
        pq = art.get('image_pexels_query')
        pfb = art.get('image_pexels_fallback')
        img_url = fetch_pexels_image(pq, pfb)
        if img_url and not is_banned_url(img_url):
            img_attr = "Pexels"
        elif img_url:
            print(f"  ⚠ Pexels returned banned URL")
            img_url = None
    
    if not img_url:
        print(f"  ⚠ No image found — publishing without image (no image > wrong image)")

    # Prepare article data
    art_data = {
        "headline": art["headline"],
        "subheadline": art["subheadline"],
        "slug": art["slug"],
        "category": "sports",
        "vertical": "sports",
        "body": art["body"].strip(),
        "status": "published",
        "published_at": now,
        "sources": art.get("sources_json", []),
        "diaspora_angle": art.get("diaspora_angle", ""),
        "urgency": art.get("urgency", "daily"),
        "score_total": art.get("score_total", 80),
        "tags": art.get("tags", []),
        "image_attribution": img_attr,
    }
    if img_url:
        art_data["image_url"] = img_url
    
    result = sb_insert("p2_articles", art_data)
    if result:
        art_id = result.get("id", "unknown")
        print(f"  ✓ Published: {art['slug']} (id: {art_id})")
        published += 1
    else:
        print(f"  ✗ Failed to publish: {art['slug']}")

print(f"\n{'='*60}")
print(f"Done. Published {published}/{len(articles)} articles.")

#!/usr/bin/env python3
"""Sports writer run — 2026-06-02"""

import json, os, sys, time, uuid, re, subprocess
import requests, urllib.parse

# Load env
def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    if line.startswith('export '):
                        line = line[7:]
                    k, v = line.split('=', 1)
                    v = v.strip().strip('"').strip("'")
                    os.environ[k] = v

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY', '')
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

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

def fetch_pexels_image(query, fallback_query=None):
    """Fetch an image from Pexels."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            r = subprocess.run(
                ['curl', '-sS', f'https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5',
                 '-H', f'Authorization: {PEXELS_KEY}'],
                capture_output=True, text=True, timeout=15
            )
            data = json.loads(r.stdout)
            photos = data.get('photos', [])
            if photos:
                url = photos[0]['src']['large2x']
                print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

def validate_image(url):
    """Validate an image URL returns 200 with image content > 5KB."""
    try:
        r = requests.head(url, timeout=10, allow_redirects=True, 
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get('Content-Type', '')
        cl = int(r.headers.get('Content-Length', 0))
        if r.status_code == 200 and 'image' in ct and cl > 5000:
            print(f"  ✓ Image validated: {r.status_code}, {ct}, {cl} bytes")
            return True
        # Try GET for servers that don't support HEAD well
        r = requests.get(url, timeout=10, stream=True,
                        headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get('Content-Type', '')
        chunk = r.raw.read(6000)
        if r.status_code == 200 and len(chunk) > 5000:
            print(f"  ✓ Image validated via GET: {r.status_code}, {len(chunk)}+ bytes")
            return True
        print(f"  ✗ Image failed validation: status={r.status_code}, ct={ct}, size={len(chunk)}")
    except Exception as e:
        print(f"  ✗ Image validation error: {e}")
    return False

def sb_insert(table, data):
    """Insert a row into Supabase."""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/{table}",
        headers=HEADERS,
        json=data
    )
    if r.status_code in (200, 201):
        result = r.json()
        if isinstance(result, list) and result:
            return result[0]
        return result
    print(f"  ✗ Insert failed ({r.status_code}): {r.text[:300]}")
    return None

def sb_patch(table, filters, data):
    """Patch a row in Supabase."""
    params = '&'.join(f"{k}={v}" for k, v in filters.items())
    r = requests.patch(
        f"{SUPABASE_URL}/rest/v1/{table}?{params}",
        headers=HEADERS,
        json=data
    )
    if r.status_code in (200, 204):
        return True
    print(f"  ✗ Patch failed ({r.status_code}): {r.text[:300]}")
    return False


# ============================================================
# ARTICLE 1: Rishabh Pant stripped of Test vice-captaincy
# ============================================================

article1 = {
    "headline": "Pant Has Lost the Test Vice-Captaincy. He Has Been Dropped from ODIs. The Selectors Say They Still Rate Him.",
    "subheadline": "KL Rahul replaces Rishabh Pant as Shubman Gill's deputy for the Afghanistan Test. The BCCI says the move is about helping Pant become 'the best Test player he has always been.' The ODI squad tells a different story.",
    "slug": "rishabh-pant-stripped-test-vice-captaincy-kl-rahul-deputy-odi-dropped-afghanistan-nri",
    "category": "sports",
    "status": "published",
    "is_editorial": False,
    "sources": json.dumps([
        "CricTracker", "Sporting News", "Inside Sport India", "India Today"
    ]),
    "body": """Rishabh Pant walked into the IPL 2026 season as India's Test vice-captain and a fixture in the ODI middle order. He walks out of it with neither role.

The BCCI's selection committee, led by Ajit Agarkar, announced India's squads for the upcoming Afghanistan series on May 19 — a one-off Test in Mullanpur starting June 6, followed by three ODIs in Dharamsala, Lucknow, and Chennai. Pant's name appears in the Test squad. It does not appear in the ODI squad. And where his name once sat next to "(Vice-Captain)," KL Rahul's name now sits instead.

## The Shift in Leadership

The decision carries weight far beyond a single series. Pant had assumed the Test vice-captaincy during India's home series against South Africa earlier this year, stepping in when captain Shubman Gill was sidelined with injury. By most accounts, the experiment did not go well. India lost the series, and the team management was reportedly unhappy with the tactical decisions Pant made in Gill's absence.

Agarkar addressed the change directly in his press conference, but the framing was careful. "We want him to become the best Test player that he has always been," the chief selector said. "I don't think there is any concern with his spot in the Test team. He is one of our main batters in that line-up. He had a really good tour of England till he got injured. So, I am sure he would like a few more runs. But he has always been very good in Test cricket."

The message: Pant remains central to India's Test plans. But the leadership dimension has been removed. The selectors want him focused on runs, not captaincy.

## Rahul Steps Up

KL Rahul, at 34, is not the future of Indian cricket in the way he once seemed to be. But he brings experience, calm, and a track record of stepping into leadership roles without drama. He has captained India in limited-overs matches before and has been a steady presence in the Test middle order during the recent England tour.

The full Test squad reflects a blend of veterans and fresh faces. Gill leads, Rahul is his deputy, and two uncapped players — Harsh Dubey of Vidarbha and Gurnoor Brar of Punjab — have earned their maiden call-ups. Manav Suthar joins the spin contingent. Jasprit Bumrah has been rested entirely, kept fresh for the England tour that follows.

## The ODI Omission

If the vice-captaincy switch can be explained as a tactical reset, Pant's exclusion from the ODI squad is harder to frame gently. The selectors have chosen KL Rahul and Ishan Kishan as their wicketkeeping options in 50-over cricket, a clear statement that Pant's white-ball place is no longer guaranteed.

The ODI squad features Rohit Sharma and Virat Kohli returning for limited-overs duty, with Hardik Pandya's inclusion subject to a fitness clearance from the Centre of Excellence. It is, in many ways, a squad that looks forward — testing combinations ahead of the 2027 ODI World Cup, which is still 15 to 16 months away.

Agarkar was direct about the timeline. The selectors, he said, want to give opportunities to youngsters while there is still room to experiment. That experimentation, apparently, extends to life without Pant in ODIs.

## The LSG Factor

The timing is impossible to separate from Pant's turbulent IPL season with Lucknow Super Giants. Reports have surfaced that Pant had already decided to step down as LSG captain midway through the campaign, frustrated by what he perceived as too many voices in the dressing room — head coach Justin Langer, director Tom Moody, assistant coach Lance Klusener, and strategic advisor Kane Williamson all occupied space around the captain's chair.

Pant is an instinctive leader. He thrives on making decisions in the moment and owning the consequences. At LSG, that freedom was reportedly curtailed. The Pooran Super Over decision — sending Nicholas Pooran to bat ahead of form players against KKR — became a symbol of the dysfunction. Pooran scored a duck.

## What It Means for NRIs

For the Indian diaspora, Pant remains one of cricket's most compelling figures. His recovery from the life-threatening car accident in December 2022, his return to international cricket, and his natural audacity at the crease have made him a symbol of resilience that resonates well beyond India's borders.

The demotion does not diminish any of that. But it does introduce uncertainty into a career that seemed, until recently, to be on an inexorable upward trajectory. At 28, Pant has time. The question is whether the selectors' patience will match his own.

The Afghanistan Test begins Friday, June 6, at the Maharaja Yadavindra Singh International Cricket Stadium in Mullanpur. Pant will bat. He will keep wicket. He will not lead. For the first time in a while, that may be exactly what he needs.""",
    "vertical": "sports",
    "image_attribution": "Wikimedia Commons"
}

# ============================================================
# ARTICLE 2: Auqib Nabi — J&K's Ranji Trophy hero, called as backup
# ============================================================

article2 = {
    "headline": "He Took 104 Wickets in Two Ranji Seasons. He Won Player of the Tournament. The BCCI Called Him — as a Backup.",
    "subheadline": "Auqib Nabi, the 24-year-old pace spearhead who led Jammu & Kashmir to their first Ranji Trophy title, has been named as a backup player for India's Test against Afghanistan. Not in the squad. Not as a reserve. As a standby.",
    "slug": "auqib-nabi-india-test-backup-player-jammu-kashmir-ranji-trophy-104-wickets-afghanistan-nri",
    "category": "sports",
    "status": "published",
    "is_editorial": False,
    "sources": json.dumps([
        "Livemint", "India Today", "CricTracker", "Sporting News"
    ]),
    "body": """The numbers are staggering by any standard. In the 2025-26 Ranji Trophy season, Auqib Nabi took 60 wickets in 17 innings at an average of 12.56 and an economy rate of 2.65. He claimed seven five-wicket hauls. He was named Player of the Tournament. And he did it while bowling Jammu & Kashmir to their first-ever Ranji Trophy title — a triumph that remains one of Indian domestic cricket's most unlikely stories.

Add the previous season's tally and Nabi has 104 first-class wickets across two Ranji Trophy campaigns. For context, that is more than most international fast bowlers manage in an entire career.

The BCCI has now called him up for India's one-off Test against Afghanistan, which begins on June 6 at the Maharaja Yadavindra Singh International Cricket Stadium in Mullanpur. But not as a member of the squad. As a backup player.

## The Selection That Wasn't

When the 15-member Test squad was announced, Nabi's absence was the talking point. Chief selector Ajit Agarkar acknowledged the omission directly: "At this point, we have gone with the three that we have picked. But there was certainly a chat around that. There is no doubt. He has had some incredible performances for Jammu & Kashmir."

The three pacers selected were Mohammed Siraj, Prasidh Krishna, and Gurnoor Brar. Siraj, the experienced spearhead. Krishna, the tall seamer who has been on the fringes. Brar, the Punjab left-armer earning a maiden call-up. All credible selections. None with domestic numbers remotely close to Nabi's.

The complicating factor is Jasprit Bumrah's absence. India's best fast bowler has been rested entirely for the Afghanistan assignment — both the Test and the subsequent ODI series — to keep him fresh for the England tour. With Akash Deep injured and Harshit Rana also unavailable, the pace cupboard was thinner than usual. Even so, Nabi did not make the cut.

## A Career Built in Obscurity

Nabi's story is inseparable from Jammu & Kashmir cricket's broader transformation. The region has never been a traditional powerhouse. Infrastructure has lagged behind the major cricket associations. Opportunities for exposure against top-tier opposition have been limited. Players from J&K have had to be not just good but exceptional to get noticed.

Nabi has been precisely that. A right-arm fast-medium bowler who generates awkward bounce and moves the ball both ways, he has been the single most destructive force in Indian domestic cricket over the past two years. His ability to bowl long spells without losing accuracy or pace has drawn comparisons to the workhorse seamers who thrive in Test cricket — the Ishant Sharmas and Umesh Yadavs who may not generate headlines but win matches through relentless pressure.

The Ranji Trophy title was the culmination of years of steady progress. J&K beat teams with far greater resources and far longer histories of success. Nabi was the difference in match after match, taking wickets in clusters and never allowing opposition batters to settle.

## The Backup Designation

Being named a backup player is not quite the same as being ignored. It means the selectors see Nabi as the next in line — the first call if a squad member breaks down during the match or in the lead-up. It keeps him in the environment, around the coaching staff and the senior players, absorbing the rhythms of international cricket preparation.

But it is not a cap. It is not even a squad number. It is, functionally, a promise that may or may not be kept. Many backup players have gone through entire series without crossing the boundary rope in anything other than practice.

For Nabi, the frustration must be acute. He has done everything domestic cricket can ask of a bowler. The runs scored against him are few. The wickets are plentiful. The big occasion — a national title — has been conquered. What more evidence could a selector need?

## What Comes Next

The Afghanistan Test is, by design, a low-stakes affair. India are massive favorites. The series is a single match. If there was ever a moment to blood a young fast bowler with irrefutable domestic credentials, this is it.

Whether Nabi gets his chance may depend on factors beyond his control — the fitness of the three selected pacers, the Mullanpur pitch, the weather. If everything goes smoothly, he may spend the entire Test carrying drinks and bowling in the nets.

But the conversation has started. Agarkar's public acknowledgment — "There was certainly a chat around that" — is significant. It means the selectors know. They know the numbers. They know the story. The question is not whether Auqib Nabi deserves an India cap. The question is when.

The Test begins Friday. Nabi will be there. Not quite in the team. Not quite outside it. Waiting, as he has waited before, for a system built around bigger names and bigger associations to make room for a fast bowler from Jammu & Kashmir who has earned his place the hardest way possible.""",
    "vertical": "sports",
    "image_attribution": "Wikimedia Commons"
}


# ============================================================
# PUBLISH
# ============================================================

articles = [article1, article2]

for i, art in enumerate(articles, 1):
    print(f"\n{'='*60}")
    print(f"ARTICLE {i}: {art['headline'][:70]}...")
    print(f"{'='*60}")
    
    # Extract primary person for Wikipedia image
    person_map = {
        1: "Rishabh Pant",
        2: "Auqib Nabi"
    }
    
    person = person_map.get(i)
    img_url = None
    
    if person:
        print(f"\n  📸 Sourcing image for: {person}")
        img_url = fetch_wikipedia_person_image(person)
        
        # For Auqib Nabi, try disambiguation if needed
        if not img_url and person == "Auqib Nabi":
            img_url = fetch_wikipedia_person_image("Auqib Nabi (cricketer)")
        
        if img_url and not validate_image(img_url):
            print(f"  ⚠ Wikipedia image failed validation, trying Pexels...")
            img_url = None
    
    # Pexels fallback with specific queries
    if not img_url:
        pexels_queries = {
            1: ("Rishabh Pant cricket wicketkeeper", "cricket wicketkeeper India"),
            2: ("fast bowling cricket India", "cricket pace bowler India red ball")
        }
        q1, q2 = pexels_queries.get(i, ("cricket", "sports"))
        img_url = fetch_pexels_image(q1, q2)
        if img_url:
            if not validate_image(img_url):
                img_url = None
            else:
                art['image_attribution'] = "The Videshi"
    
    if img_url:
        art['image_url'] = img_url
        print(f"  ✓ Final image: {img_url[:80]}...")
    else:
        print(f"  ⚠ No valid image found — publishing without image")
    
    # Set published_at
    art['published_at'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    
    # Insert
    print(f"\n  📝 Inserting article...")
    result = sb_insert('p2_articles', art)
    if result:
        art_id = result.get('id', 'unknown')
        print(f"  ✓ Published: {art['slug']} (id: {art_id})")
    else:
        print(f"  ✗ FAILED to publish: {art['slug']}")
    
    # Small delay between inserts
    time.sleep(1)

print(f"\n{'='*60}")
print("Sports writer run complete.")
print(f"{'='*60}")

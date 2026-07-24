#!/usr/bin/env python3
"""Sports writer for The Videshi — June 11, 2026 run (batch B)"""
import json, os, requests, urllib.parse
from datetime import datetime, timezone

def load_env(path):
    if not os.path.exists(path): return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                if line.startswith('export '): line = line[7:]
                key, _, val = line.partition('=')
                os.environ[key.strip()] = val.strip('"').strip("'")

load_env(os.path.expanduser('~/.env.supabase'))
SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}
UA = 'TheVideshi/1.0 (thevideshi.com)'

def wiki_image(name):
    encoded = urllib.parse.quote(name.replace(' ', '_'))
    try:
        r = requests.get(f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
                         headers={"User-Agent": UA}, timeout=10)
        if r.status_code == 200:
            data = r.json()
            return data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
    except: pass
    return None

def validate_image(url):
    try:
        r = requests.head(url, headers={"User-Agent": UA}, timeout=10, allow_redirects=True)
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            return True
        if r.status_code == 200 and "image" in ct:
            r2 = requests.get(url, headers={"User-Agent": UA}, timeout=10, stream=True)
            chunk = r2.raw.read(6000)
            return len(chunk) > 5000
    except: pass
    return False

def insert_article(a):
    r = requests.post(f"{SUPABASE_URL}/rest/v1/p2_articles", headers=HEADERS, json=a, timeout=30)
    if r.status_code in (200, 201):
        data = r.json()
        if isinstance(data, list) and data:
            print(f"  ✓ Inserted: {a['slug']} (id={data[0].get('id','?')})")
            return True
    print(f"  ✗ Insert failed ({r.status_code}): {r.text[:400]}")
    return False

now = datetime.now(timezone.utc).isoformat()

# ═══ ARTICLE 1: India Asian Games Squad ═══
print("\n═══ Article 1: India Asian Games Squad ═══")

img1 = wiki_image("Jasprit Bumrah")
if img1 and validate_image(img1):
    print(f"  ✓ Bumrah image: {img1[:80]}...")
    img1_caption = "Jasprit Bumrah, selected to spearhead India's bowling attack at the 2026 Asian Games in Japan"
    img1_attr = "Wikimedia Commons"
else:
    img1 = wiki_image("Shreyas Iyer")
    if img1 and validate_image(img1):
        print(f"  ✓ Iyer image: {img1[:80]}...")
        img1_caption = "Shreyas Iyer, named captain of India's cricket squad for the 2026 Asian Games"
        img1_attr = "Wikimedia Commons"
    else:
        print("  ✗ No image found, skipping article 1")
        img1 = None

if img1:
    body1 = """India have sent a message ahead of the 2026 Asian Games in Nagoya, Japan. The squad, announced by the BCCI on June 6, is no afterthought — Jasprit Bumrah, arguably the finest fast bowler on the planet, will spearhead the pace attack. Shreyas Iyer, the newly-appointed T20I captain, will lead the side.

The last time India played cricket at the Asian Games, in Hangzhou in 2023, they sent a second-string team while the first-choice players prepared for the ODI World Cup. Ruturaj Gaikwad captained that squad to a gold medal. This time, the BCCI has made a different calculation entirely.

## A Full-Strength Commitment

The 15-member squad reads like an all-star roster. Bumrah, who has been rested for the upcoming Ireland and England tours, returns exclusively for the Asian Games. Alongside him, Arshdeep Singh and Harshit Rana form a pace battery that would trouble any international lineup on its day.

The batting is stacked from top to bottom. Abhishek Sharma, who announced himself on the world stage with explosive performances in IPL 2026, opens alongside the versatile Sanju Samson. Tilak Varma, named vice-captain at just 23, anchors the middle order alongside Iyer, while Nitish Kumar Reddy and Shivam Dube provide all-round depth in the lower middle.

The spin department features three options: Axar Patel, Washington Sundar, and Varun Chakravarthy, with Ravi Bishnoi offering a wrist-spin alternative. Ishan Kishan is the backup wicketkeeper — his inclusion, after years in the wilderness since the 2023 ODI World Cup, is another quiet story worth tracking.

## Sooryavanshi: The Teenager in the Room

Perhaps the most intriguing selection is Vaibhav Sooryavanshi. At 17, the left-handed opener from Uttar Pradesh made headlines when he became the youngest player ever bought in an IPL mega auction. Now he is headed to Nagoya as part of a full-strength Indian squad.

This is not a reward. The selectors see Sooryavanshi as part of India's T20I future, and the Asian Games — with its multi-sport atmosphere and lower-pressure cricket environment — is the ideal stage to give him experience in India colours before the higher-stakes bilateral series and ICC events. He has been named in both the Asian Games and the Ireland-England T20I squads, confirming his place in the long-term plans.

## The Bumrah vs Farhan Subplot

Pakistan, too, have announced their Asian Games squad, led by Sahibzada Farhan. Cricket fans will remember that Farhan was the first batter to hit Bumrah for multiple sixes in a T20I — a record-breaking moment during the Asia Cup 2025 that ended Bumrah's streak of never being hit for a maximum in the format. A potential India-Pakistan clash in Nagoya, with Bumrah looking for payback against Farhan, adds a layer of intensity that no other multi-sport event can offer.

## Why This Matters for the Diaspora

For the estimated 40,000-strong Indian community in Japan — many of them IT professionals and business executives in the Nagoya-Tokyo-Osaka corridor — this squad represents a rare chance to watch India's best cricketers live, without flying to a neutral venue or back home.

The tournament runs from September 19 to October 4 in Aichi Prefecture. For NRIs across East and Southeast Asia — Singapore, Hong Kong, Tokyo, Seoul — a weekend trip to watch Bumrah bowl in an India shirt may be the most accessible live international cricket experience of the decade.

## The Full Squad

**India squad for 2026 Asian Games (September, Japan):** Shreyas Iyer (C), Tilak Varma (VC), Abhishek Sharma, Sanju Samson (WK), Ishan Kishan (WK), Shivam Dube, Nitish Kumar Reddy, Axar Patel, Washington Sundar, Varun Chakravarthy, Ravi Bishnoi, Jasprit Bumrah, Harshit Rana, Arshdeep Singh, Vaibhav Sooryavanshi.

**India A squad for Sri Lanka multi-day matches:** Dhruv Jurel (C, WK), Devdutt Padikkal (VC), Sai Sudharsan, Ruturaj Gaikwad, N Jagadeesan (WK), Aman Mokhade, Shaik Rasheed, Ayush Pandey, Harsh Dubey, Saransh Jain, Gurnoor Brar, Auqib Nabi, Yash Thakur, Anshul Kamboj, Zeeshan Ansari.

The message from the BCCI is unambiguous: India are not treating the Asian Games as a development exercise. They are going to Japan to win."""

    a1 = {
        "headline": "Bumrah Named in Full-Strength India Squad for 2026 Asian Games in Japan",
        "subheadline": "Seventeen-year-old Sooryavanshi joins India's best as BCCI sends a first-choice team to Nagoya — a first for cricket at the Asian Games",
        "body": body1.strip(),
        "slug": "bumrah-india-asian-games-2026-japan-squad-iyer-sooryavanshi-nri",
        "category": "sports",
        "status": "review",
        "is_editorial": False,
        "image_url": img1,
        "image_caption": img1_caption,
        "image_attribution": img1_attr,
        "sources": json.dumps([
            {"name": "Cricbuzz", "url": "https://www.cricbuzz.com/cricket-news/139058/bumrah-picked-for-2026-asian-games"},
            {"name": "Reuters", "url": "https://www.reuters.com"},
            {"name": "CricTracker", "url": "https://www.crictracker.com"},
            {"name": "Cricket Addictor", "url": "https://www.cricketaddictor.com"}
        ]),
        "published_at": now
    }
    insert_article(a1)


# ═══ ARTICLE 2: Serena Williams Comeback ═══
print("\n═══ Article 2: Serena Williams Comeback ═══")

img2 = wiki_image("Serena Williams")
if img2 and validate_image(img2):
    print(f"  ✓ Serena image: {img2[:80]}...")
    img2_caption = "Serena Williams, who returned to professional tennis at 44 with a doubles win at Queen's Club"
    img2_attr = "Wikimedia Commons"
else:
    print("  ✗ No image found, skipping article 2")
    img2 = None

if img2:
    body2 = """She had not played a professional match since September 2022. Four years of retirement. Two children. A business empire that includes a venture capital firm, a fashion line, and now a meal delivery partnership. A Super Bowl halftime performance. And then, on a Tuesday afternoon at Queen's Club in London, Serena Williams walked back onto a tennis court and won.

Williams, 44, partnered with 19-year-old Canadian Victoria Mboko to beat the No. 3 seeds Erin Routliffe and Nicole Melichar-Martinez 7-6 (2), 6-2 in the first round of the HSBC Championships. The crowd at Queen's Club — a venue that historically hosted only men's events until it opened to women recently — gave the 23-time Grand Slam champion a standing ovation before she had hit a ball.

## The Match

The opening set was tight. Routliffe, a top-10 doubles player, and Melichar-Martinez, a veteran of the circuit, pushed Williams and Mboko to a tiebreak. But at 6-6, Williams found another gear. She served a 113 mph ace — a speed that would have been competitive at any point in her career — and the pair ran away with the tiebreak 7-2.

The second set was more emphatic. With Williams anchoring net play and Mboko providing pace from the baseline, they broke twice and closed out 6-2. The match lasted just over an hour.

"I was nervous, but I didn't really think about it," Williams said afterward. "I just thought about having fun, which I did today. I get nervous right before the match, like 30 minutes before. Then I just let it go."

When asked why she came back, Williams was characteristically direct: "I never got to play here. It was always just the men. It feels really special to play somewhere so iconic. I got tired of sitting at home. My kids are out of school for the summer, so why not?"

## The 25-Year Gap

Williams' choice of partner was deliberate. Mboko is one of Canada's fastest-rising tennis stars — ranked ninth in singles with two WTA titles already (the 2025 Canadian Open and the 2025 Hong Kong Open). She grew up watching Williams on television. The 25-year age gap only amplified the narrative: the greatest women's player in history, returning alongside a teenager who idolised her.

On Instagram, Mboko posted a photo from their first practice session with the caption: "Can't name a better way to start the grass szn."

## Family in the Stands

Williams' husband, Reddit co-founder Alexis Ohanian, watched from the stands with their daughters Olympia, 8, and Adira, 2. Olympic skier Lindsey Vonn — who famously un-retired herself and competed in her 40s — was also in attendance.

Williams and Mboko next face Laura Siegemund and Leylah Fernandez in the quarterfinals on Thursday. Williams has confirmed she will also play doubles at the Berlin Tennis Open starting June 15. She has not ruled out singles.

## What It Means for Indian Tennis Fans

For a generation of Indian tennis fans who grew up watching Sania Mirza carry the flag for South Asian tennis, Williams' return resonates beyond sport. Mirza, who retired in 2023 at 36, was a doubles specialist in her final years, and the two shared a warm friendship — practising together, attending the same events, and speaking publicly about the challenges of balancing motherhood with elite sport.

The timing is significant. With Wimbledon less than three weeks away, and the Women's T20 World Cup starting in England this week, Indian broadcasters are building a summer around powerful female athletes — Harmanpreet Kaur chasing a T20 World Cup title, PV Sindhu preparing for another Olympic push, and now Williams reminding everyone that greatness does not have an expiry date.

For NRI families in the US, UK, and Canada — where tennis academies are filled with young South Asian children whose parents grew up watching Mirza and Williams in the same draw — this comeback is more than a sports story. It is a statement about what remains possible at 44, with two children, after a life that had already moved on.

Williams is not the same player she was in 2017, or even 2022. She knows that. But at Queen's Club, for one warm London afternoon, the result was exactly the same. She walked onto the court, and she won."""

    a2 = {
        "headline": "She Had Not Played in Four Years. At 44, Serena Williams Walked Back On Court and Won.",
        "subheadline": "The 23-time Grand Slam champion partnered with a 19-year-old Canadian to beat the No. 3 seeds at Queen's Club — and she is not done yet",
        "body": body2.strip(),
        "slug": "serena-williams-comeback-44-queens-club-doubles-win-mboko-nri",
        "category": "sports",
        "status": "review",
        "is_editorial": False,
        "image_url": img2,
        "image_caption": img2_caption,
        "image_attribution": img2_attr,
        "sources": json.dumps([
            {"name": "Men's Journal", "url": "https://www.mensjournal.com/news/serena-williams-announced-major-new-partnership-before-tennis-return"},
            {"name": "People", "url": "https://people.com"},
            {"name": "Palm Beach Post", "url": "https://www.palmbeachpost.com"},
            {"name": "ESPN", "url": "https://www.espn.com"}
        ]),
        "published_at": now
    }
    insert_article(a2)

print("\n═══ Sports writer batch B complete ═══")

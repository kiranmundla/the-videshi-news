#!/usr/bin/env python3
"""
The Videshi — Sports Writer (2026-05-30 afternoon run)
Articles:
1. Vaibhav Sooryavanshi's record-breaking IPL 2026 season + India call-up talk
2. BCCI bans smart goggles in IPL — tech meets cricket integrity
3. India Women's T20 World Cup 2026 preview — NRI diaspora watch guide
"""

import json, os, sys, uuid, re, time
from datetime import datetime, timezone

# --- env ---
env_path = os.path.expanduser("~/workspace/.env.supabase")
with open(env_path) as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ[k] = v

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

pexels_env = os.path.expanduser("~/workspace/.env.pexels")
PEXELS_KEY = None
if os.path.exists(pexels_env):
    with open(pexels_env) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                if k.strip() == "PEXELS_API_KEY":
                    PEXELS_KEY = v.strip()

import requests, urllib.parse

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

# --- image helpers ---
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
    """Fetch a specific image from Pexels using curl (urllib gets 403)."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key found")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            import subprocess
            cmd = [
                "curl", "-sS", "-H", f"Authorization: {PEXELS_KEY}",
                f"https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5&orientation=landscape"
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            if result.returncode == 0:
                data = json.loads(result.stdout)
                photos = data.get("photos", [])
                for photo in photos:
                    url = photo.get("src", {}).get("large2x") or photo.get("src", {}).get("large")
                    if url:
                        # Verify size
                        head = requests.head(url, timeout=10)
                        cl = int(head.headers.get("Content-Length", 0))
                        ct = head.headers.get("Content-Type", "")
                        if cl > 5000 and "image" in ct:
                            print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                            return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None


def upload_to_supabase_storage(image_url, filename):
    """Download image and upload to Supabase article-images bucket."""
    try:
        r = requests.get(image_url, timeout=15, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        if r.status_code != 200 or len(r.content) < 5000:
            print(f"  ⚠ Download failed or too small: {r.status_code}, {len(r.content)} bytes")
            return None
        ct = r.headers.get("Content-Type", "image/jpeg")
        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
        upload_headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": ct,
            "x-upsert": "true",
        }
        resp = requests.post(upload_url, data=r.content, headers=upload_headers, timeout=15)
        if resp.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {public_url[:80]}...")
            return public_url
        else:
            print(f"  ⚠ Upload failed: {resp.status_code} {resp.text[:200]}")
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
    return None


def validate_image_url(url):
    """Validate that a URL returns a real image."""
    if not url:
        return False
    banned = ["fbcdn.net", "cdninstagram.com", "lookaside.fbsbx.com", "_nc_ht=", "_nc_cat=", "ccb="]
    for b in banned:
        if b in url:
            print(f"  ❌ Banned source detected: {b}")
            return False
    try:
        r = requests.head(url, timeout=10, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, allow_redirects=True)
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if "image" in ct and cl > 5000:
            return True
        # Some servers don't return Content-Length on HEAD; try GET with range
        if "image" in ct and cl == 0:
            r2 = requests.get(url, timeout=10, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)", "Range": "bytes=0-10000"}, stream=True)
            chunk = r2.content
            if len(chunk) > 5000:
                return True
    except Exception as e:
        print(f"  ⚠ Validation error: {e}")
    return False


def insert_article(article):
    """Insert an article into Supabase."""
    url = f"{SUPABASE_URL}/rest/v1/p2_articles"
    r = requests.post(url, json=article, headers=HEADERS, timeout=15)
    if r.status_code in (200, 201):
        data = r.json()
        if isinstance(data, list) and data:
            return data[0].get("id")
        return data.get("id") if isinstance(data, dict) else None
    else:
        print(f"  ❌ Insert failed: {r.status_code} {r.text[:300]}")
        return None


def patch_article(article_id, updates):
    """Patch an existing article."""
    url = f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article_id}"
    r = requests.patch(url, json=updates, headers=HEADERS, timeout=15)
    if r.status_code in (200, 204):
        print(f"  ✓ Patched article {article_id}")
    else:
        print(f"  ⚠ Patch failed: {r.status_code} {r.text[:200]}")


# ========== ARTICLE 1: Sooryavanshi Season Retrospective ==========
print("\n=== Article 1: Sooryavanshi Season Retrospective ===")

art1_slug = "vaibhav-sooryavanshi-776-runs-orange-cap-india-call-up-ipl-2026-season-record"
art1_headline = "Seven Hundred and Seventy-Six Runs at Fifteen. Vaibhav Sooryavanshi's IPL 2026 Season Was Unlike Anything Cricket Has Seen."
art1_subheadline = "The Rajasthan Royals opener broke Chris Gayle's all-time sixes record, became the joint second-fastest to 1,000 IPL runs, and now Sangakkara says he is ready for India."

art1_body = """Vaibhav Sooryavanshi is fifteen years old. He finishes this IPL season with 776 runs from 16 innings at a strike rate of 237.30, the Orange Cap around his neck and Chris Gayle's record for most sixes in a single IPL season in the bin.

The numbers are absurd. Sixty-five sixes. One century. Five half-centuries. A batting average of 48.50. The joint second-fastest player in IPL history to reach 1,000 career runs, alongside Lendl Simmons in 23 innings — only Shaun Marsh, in 21, got there quicker.

## The Season in Full

It started early. Sooryavanshi had announced himself last year by hitting the first ball he faced in the IPL for six, aged fourteen, before becoming the youngest player to score a Twenty20 hundred. But IPL 2025 was a trailer. IPL 2026 was the film.

He opened every match for Rajasthan Royals and set about tormenting some of the best bowlers alive. When the Orange Cap first sat on his head — after a 36-ball century against Sunrisers Hyderabad in which he hit five fours and twelve sixes — he had 357 runs from eight matches, level with KL Rahul, who had just scored 152 not out to claim it hours earlier. Sooryavanshi snatched it straight back.

He never let go.

## The Records

The big one came in the Eliminator against Sunrisers Hyderabad. Sooryavanshi smashed 97 off 29 balls — twelve sixes in a single innings — and in doing so surpassed Gayle's 59 sixes from the 2012 season. James Franklin, the Hyderabad assistant coach, watched it happen from the other dugout and said what everybody was thinking.

"I don't think anyone's ever seen a talent like this. It's freakish what he's doing at the moment. To think that he's potentially got 25 years left in the career, it's quite scary. He's only going to get better, stronger and more mature with how he bats."

In the Qualifier 2 against Gujarat Titans, Sooryavanshi made 96 off 47 balls — including being hit on the head by a Kagiso Rabada bouncer before racing from 50 to 96 in sixteen deliveries. Rajasthan lost that match. Gujarat chased 210-plus with Shubman Gill and Sai Sudharsan putting on a record-breaking 167-run stand. Sooryavanshi's campaign was over.

But the statement had been made.

## The India Question

Kumar Sangakkara, the Rajasthan head coach and Sri Lankan great, left no ambiguity after the Qualifier 2 defeat.

"The guy, at fifteen years old, he's very mature, he reads the game really well, he reads situations well, and he's got no fear," Sangakkara said. "We are very, very proud of the season that he's had. I think he's going to be even better as the years go by."

Asked directly whether Sooryavanshi was ready for India, Sangakkara was unequivocal: "With everything Vaibhav has shown against some of the best bowlers in the world, I think he's more than ready to take on any challenge that you throw at him. And I'm sure that he'll get that call-up very, very soon."

Sooryavanshi has already been called up to the India A developmental squad. The noise around a senior T20I call-up — potentially for the England tour later this summer — grows louder by the day.

## The Diaspora Angle

For NRI cricket fans, Sooryavanshi represents something remarkable: the possibility that the next great Indian batting prodigy is already here, already delivering, and doing it at an age when most academy players are still learning to deal with pace. He has been compared to Sachin Tendulkar's debut at sixteen, to Shahid Afridi's explosive arrival, to Gayle's six-hitting supremacy. None of the comparisons quite capture what he is.

Devdutt Padikkal, his RCB counterpart, put it simply: "What Vaibhav Suryavanshi does is truly unique. At his age, to have that kind of power and explosiveness in his batting is special. Honestly, it would be foolish for anyone to try to copy him."

## What Comes Next

The IPL Final takes place on Sunday in Ahmedabad — RCB against GT, Kohli against Gill — and Sooryavanshi will not be in it. But his season will be remembered long after the trophy is lifted. Seven hundred and seventy-six runs. Sixty-five sixes. The Orange Cap. And he turns sixteen in December.

Cricket's next chapter is being written by a teenager. The question is not whether he will play for India. It is when.

---

*Sources: Reuters, Cricbuzz, The Times, Wisden, Sporting News*"""

# Image: try Wikipedia for Sooryavanshi
print("  Sourcing image for Sooryavanshi...")
img1 = fetch_wikipedia_person_image("Vaibhav Suryavanshi")
if not img1:
    img1 = fetch_wikipedia_person_image("Vaibhav Sooryavanshi")
if not img1:
    img1 = fetch_wikipedia_person_image("Vaibhav Suryavanshi (cricketer)")

img1_final = None
img1_attr = None
if img1:
    fname1 = f"{art1_slug}.jpg"
    img1_final = upload_to_supabase_storage(img1, fname1)
    img1_attr = "Wikimedia Commons"

if not img1_final:
    # Fallback to Pexels — specific cricket image
    img1 = fetch_pexels_image("cricket batsman six hitting IPL", "cricket stadium India T20")
    if img1:
        fname1 = f"{art1_slug}.jpg"
        img1_final = upload_to_supabase_storage(img1, fname1)
        img1_attr = "The Videshi"

art1 = {
    "headline": art1_headline,
    "subheadline": art1_subheadline,
    "body": art1_body,
    "slug": art1_slug,
    "category": "sports",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "sources": "Reuters, Cricbuzz, Wisden, The Times",
    "vertical": "sports",
    "image_url": img1_final,
    "image_attribution": img1_attr,
}

art1_id = insert_article(art1)
if art1_id:
    print(f"  ✅ Article 1 published: {art1_id}")
else:
    print("  ❌ Article 1 failed to publish")


# ========== ARTICLE 2: BCCI Smart Goggles Ban ==========
print("\n=== Article 2: BCCI Smart Goggles Ban ===")

art2_slug = "bcci-bans-smart-goggles-ipl-2026-meta-ray-bans-anti-corruption-pmoa-nri"
art2_headline = "The BCCI Has Banned Smart Glasses From IPL Dugouts. Here Is Why It Matters Beyond Cricket."
art2_subheadline = "Meta Ray-Bans, live-streaming eyewear, and the growing tension between wearable technology and sports integrity — the IPL's anti-corruption unit draws a hard line."

art2_body = """The BCCI's Anti-Corruption and Security Unit has issued a directive that no player or match official may possess or use smart sunglasses inside the Players and Match Officials Area during IPL matches. The ban, issued to all ten franchises this week, treats smart eyewear the same as mobile phones and smartwatches: devices that must be surrendered to the Security Liaison Officer before entering the dugout.

The timing is deliberate. The IPL Final between Royal Challengers Bengaluru and Gujarat Titans is on Sunday.

## What Prompted the Ban

The ACSU said it had "observed companies marketing and selling smart sunglasses to players and support staff." The advisory named no specific brand, but the products in question — smart glasses with live-streaming, text messaging, and audio and video calling capabilities over mobile data or Wi-Fi — describe consumer wearables already popular with tech-savvy consumers. Products like Meta Ray-Bans, which look identical to ordinary sunglasses but can stream live to Instagram, are exactly the kind of device the BCCI is worried about.

"These devices are equipped with advanced communication features, including live streaming, sending and receiving text messages, as well as audio and video calling capabilities through mobile data or Wi-Fi networks," the advisory stated. "Accordingly, under the PMOA Minimum Standards, such goggles/glasses are classified both as an 'Audio/Video Recording Device' and a 'Communication Device'."

Players and support staff must now deposit smart eyewear with the Security Liaison Officer alongside their phones and smartwatches. Failure to comply "shall be deemed a breach of the PMOA protocols and may result in penalties under the PMOA Minimum Standards for IPL 2026."

## A Season of Crackdowns

This is not the BCCI's first intervention on technology this season. Earlier in IPL 2026, Rajasthan Royals team manager Romi Bhinder was fined Rs 1 lakh — roughly $1,200 — and issued a formal warning after CCTV footage showed him using a mobile phone in the team dugout during a live match.

The board has also tightened off-field regulations, including restrictions on late-night outings without security clearance and limitations on visitors in team hotels. The smart goggles ban is part of a broader pattern: the IPL's anti-corruption framework is updating itself in real time as wearable technology evolves faster than most regulatory bodies can keep up.

## The NRI Tech Angle

The ban sits at an interesting intersection for the Indian diaspora. Many NRIs working in Silicon Valley, Seattle, London, and Toronto are early adopters of exactly the kind of wearable technology the BCCI is now banning. Meta Ray-Bans are commonplace in the Bay Area. Google's smart glasses are in development. Apple's Vision Pro ecosystem is expanding.

The concern is not about fans — spectators in the stands can still wear whatever they want. But the BCCI's worry about covert communication channels inside restricted areas reflects a broader anxiety that is spreading across professional sports worldwide. The NFL, Premier League, and Olympic movement have all grappled with similar questions about how to regulate wearable tech in competition environments.

For cricket specifically, the stakes are high. Match-fixing and spot-fixing remain existential threats to the sport's credibility, particularly in franchise T20 leagues where the volume of betting is enormous. A pair of glasses that can live-stream footage from the dressing room to an outside party, invisibly and in real time, represents exactly the kind of technology that anti-corruption units were designed to prevent — before those units knew the technology would exist.

## What Happens Next

The ban applies strictly to the PMOA — dressing rooms, dugouts, player viewing areas, and warm-up zones — on match days. It does not extend to practice sessions, travel, or personal time. And it does not apply to fans, creating what one technology journalist called "an interesting gap" between who is regulated and who is not.

For now, the message from the BCCI is clear: cricket's most lucrative league is not ready to let technology blur the line between fair competition and potential corruption. The glasses come off before you walk into the dugout. No exceptions.

---

*Sources: BCCI ACSU advisory, Best Media Info, Digit.in, Yardbarker, The Sports 247*"""

# Image: Pexels for smart glasses/cricket intersection
print("  Sourcing image for smart goggles article...")
img2 = fetch_pexels_image("smart glasses technology wearable", "cricket sunglasses sport")
img2_final = None
img2_attr = None
if img2:
    fname2 = f"{art2_slug}.jpg"
    img2_final = upload_to_supabase_storage(img2, fname2)
    img2_attr = "The Videshi"

art2 = {
    "headline": art2_headline,
    "subheadline": art2_subheadline,
    "body": art2_body,
    "slug": art2_slug,
    "category": "sports",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "sources": "BCCI ACSU, Best Media Info, Digit.in, Yardbarker",
    "vertical": "sports",
    "image_url": img2_final,
    "image_attribution": img2_attr,
}

art2_id = insert_article(art2)
if art2_id:
    print(f"  ✅ Article 2 published: {art2_id}")
else:
    print("  ❌ Article 2 failed to publish")


# ========== ARTICLE 3: India Women T20 World Cup Preview ==========
print("\n=== Article 3: India Women T20 World Cup Preview ===")

art3_slug = "india-women-t20-world-cup-2026-england-nri-watch-guide-schedule-squad-mandhana-harmanpreet"
art3_headline = "India Women Play Their T20 World Cup Opener in Three Weeks. The NRI's Complete Guide to the Tournament in England."
art3_subheadline = "Schedule, squad, match times for every US and UK timezone, how to watch on Willow TV, and why this Indian team might be the most complete women's side the country has ever produced."

art3_body = """The ICC Women's T20 World Cup 2026 begins on June 12 in England. India's first match is on June 21 against South Africa at Old Trafford in Manchester. For a generation of Indian women's cricket fans — many of them now watching from living rooms in New Jersey, Dallas, the Bay Area, and Toronto — this tournament arrives at a moment of genuine hope.

India won the ODI World Cup last year. Harmanpreet Kaur's team is now ranked among the top three T20I sides in the world. The squad that will walk out at Old Trafford has experience, depth, and a teenager named Nandni Sharma who takes wickets for fun.

## The Squad

India's T20 World Cup squad is built around a core that has been playing together for years. Smriti Mandhana opens. Shafali Verma opens alongside her. Jemimah Rodrigues bats at three or four. Harmanpreet Kaur anchors the middle order. Richa Ghosh keeps wicket and finishes innings. Deepti Sharma controls the middle overs with off-spin.

The new faces — Yastika Bhatia, who returned from an eight-month injury layoff to hit a fifty in the first T20I against England; Nandni Sharma, who took three wickets in that same match; Kranti Gaud — add depth that previous Indian squads lacked. This is not a two-player team.

**Key players:**
- **Smriti Mandhana** — India's most elegant batter, now the senior opening partner
- **Harmanpreet Kaur** — Captain, middle-order power hitter, rested for the series opener but expected back for the World Cup
- **Jemimah Rodrigues** — The glue at No. 3, consistent and unflappable
- **Deepti Sharma** — All-rounder who controls the middle overs
- **Shafali Verma** — Explosive opener who can change matches in the powerplay
- **Richa Ghosh** — Wicketkeeper-batter who has matured into a genuine finisher
- **Yastika Bhatia** — The comeback story; returned from ACL rehab to immediate impact

## The Schedule — India's Group Matches

India are in Group A alongside South Africa, Bangladesh, and the Netherlands.

| Date | Match | Venue | IST | US Eastern | US Pacific | UK |
|------|-------|-------|-----|------------|------------|-----|
| June 21 | India vs South Africa | Old Trafford, Manchester | 6:00 PM | 8:30 AM | 5:30 AM | 1:30 PM |
| June 25 | India vs Bangladesh | Old Trafford, Manchester | 6:00 PM | 8:30 AM | 5:30 AM | 1:30 PM |
| June 28 | India vs Australia | Lord's, London | 6:00 PM | 8:30 AM | 5:30 AM | 1:30 PM |

The semi-finals are on June 30 and July 2 at The Oval. The timing works well for NRIs on the East Coast — most matches start at 8:30 AM ET, meaning you can catch the first innings before heading to work.

## How to Watch from the US, UK, and Canada

- **United States and Canada:** Willow TV has the live broadcast rights. Available on cable, the Willow TV app, and streaming packages.
- **United Kingdom:** Sky Sports Cricket will carry all matches live, with streaming on Sky Go and NOW TV.
- **India:** Sony Sports Network (Sony Sports Ten 1, Ten 3, Ten 4) on TV, Sony LIV for streaming. Free-to-air coverage on DD Sports.
- **Australia:** Fox Cricket and Kayo Sports.

## The Current Form — England Tour

India arrived in England on a high. In the first T20I at Chelmsford, they posted 188/7 — powered by fifties from Yastika Bhatia and Jemimah Rodrigues — and then bowled England out for 150 to win by 38 runs. Nandni Sharma, a teenager who bowls with genuine fire, took three wickets.

The second T20I is being played today in Bristol. The third is on June 2 in Taunton. These matches serve as direct preparation for the World Cup — same conditions, same opponents, same grounds. India will also have warm-up fixtures before the tournament begins on June 12.

## Why This Team Is Different

Previous Indian women's teams have arrived at World Cups with talent but without the depth to sustain a tournament run. This side is different. The ODI World Cup victory last year gave the squad a champion's mentality. The batting lineup is six-deep. The bowling attack has pace (Renuka Singh, Arundhati Reddy), spin variety (Deepti Sharma, Radha Yadav, Shreyanka Patil), and genuine all-round options.

The selection dilemma — where to bat Yastika Bhatia without displacing Jemimah Rodrigues — is a good problem to have. It speaks to the embarrassment of riches that India women's cricket now enjoys.

## The Diaspora Connection

For NRI women and girls who grew up watching cricket but rarely saw women play it on a major stage, this tournament matters. The Women's T20 World Cup is hosted in England — accessible, well-broadcast, and in a timezone that works for viewers in North America. India vs Australia at Lord's on June 28 has the potential to be one of the biggest women's cricket matches ever played.

The Indian women's team has earned this moment. Three weeks from now, they walk out at Old Trafford to begin their campaign. If you have Willow TV, set your alarm for 5:30 AM Pacific on June 21. It will be worth the early morning.

---

*Sources: SportsCafe, ICC, Cricbuzz, Latestly, RevSportz*"""

# Image: try Wikipedia for Smriti Mandhana or Harmanpreet Kaur
print("  Sourcing image for India Women T20 WC article...")
img3 = fetch_wikipedia_person_image("Smriti Mandhana")
if not img3:
    img3 = fetch_wikipedia_person_image("Harmanpreet Kaur")

img3_final = None
img3_attr = None
if img3:
    fname3 = f"{art3_slug}.jpg"
    img3_final = upload_to_supabase_storage(img3, fname3)
    img3_attr = "Wikimedia Commons"

if not img3_final:
    img3 = fetch_pexels_image("women cricket match India", "cricket women sport")
    if img3:
        fname3 = f"{art3_slug}.jpg"
        img3_final = upload_to_supabase_storage(img3, fname3)
        img3_attr = "The Videshi"

art3 = {
    "headline": art3_headline,
    "subheadline": art3_subheadline,
    "body": art3_body,
    "slug": art3_slug,
    "category": "sports",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "sources": "SportsCafe, ICC, Cricbuzz, Latestly, RevSportz",
    "vertical": "sports",
    "image_url": img3_final,
    "image_attribution": img3_attr,
}

art3_id = insert_article(art3)
if art3_id:
    print(f"  ✅ Article 3 published: {art3_id}")
else:
    print("  ❌ Article 3 failed to publish")


# --- Summary ---
print("\n=== Summary ===")
published = sum(1 for x in [art1_id, art2_id, art3_id] if x)
print(f"Published: {published}/3 articles")
if art1_id:
    print(f"  1. {art1_headline[:80]}...")
if art2_id:
    print(f"  2. {art2_headline[:80]}...")
if art3_id:
    print(f"  3. {art3_headline[:80]}...")

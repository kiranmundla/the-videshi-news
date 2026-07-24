#!/usr/bin/env python3
"""
Sports writer for The Videshi — July 13, 2026 4pm PT run.
3 articles:
  1. India's coaching staff overhaul after England T20I whitewash
  2. Experts blast India's T20I system — Manjrekar, Gavaskar, Karthik reactions
  3. MLC 2026 playoffs locked: Hassan Khan's 10-ball blitz seals SF Unicorns' top spot
"""

import os, json, requests, uuid, re, time, subprocess
from datetime import datetime, timezone
from io import BytesIO

# ---- env ----
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
            k, _, v = line.partition('=')
            v = v.strip().strip('"').strip("'")
            os.environ[k.strip()] = v

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

UA = {"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}

# ---- helpers ----

def fetch_wikipedia_person_image(person_name):
    import urllib.parse
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers=UA, timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None


def fetch_wikimedia_commons_images(search_query, limit=5):
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": search_query,
        "gsrnamespace": "6",
        "gsrlimit": str(limit),
        "prop": "imageinfo",
        "iiprop": "url|size|mime",
        "iiurlwidth": "1200",
        "format": "json"
    }
    try:
        r = requests.get(
            "https://commons.wikimedia.org/w/api.php",
            params=params, headers=UA, timeout=15
        )
        if r.status_code == 200:
            data = r.json()
            pages = data.get("query", {}).get("pages", {})
            results = []
            for pid, page in pages.items():
                ii = page.get("imageinfo", [{}])[0]
                mime = ii.get("mime", "")
                if not mime.startswith("image/") or mime == "image/svg+xml":
                    continue
                if ii.get("width", 0) < 300:
                    continue
                results.append({
                    "url": ii.get("thumburl") or ii.get("url", ""),
                    "original_url": ii.get("url", ""),
                    "title": page.get("title", ""),
                    "width": ii.get("width", 0),
                    "height": ii.get("height", 0),
                })
            return results
    except Exception as e:
        print(f"  ⚠ Wikimedia Commons error: {e}")
    return []


def compress_and_upload(img_url, filename):
    """Download, compress via PIL, upload to Supabase article-images bucket."""
    try:
        # Try requests first, fall back to curl on 429
        r = requests.get(img_url, headers=UA, timeout=20)
        if r.status_code == 429:
            print(f"  ⚠ 429 from requests, trying curl...")
            tmp = f"/tmp/img_{uuid.uuid4().hex[:8]}.jpg"
            subprocess.run(["curl", "-sS", "-A", "TheVideshi/1.0 (thevideshi.com)",
                            "-o", tmp, img_url], timeout=30)
            if os.path.exists(tmp) and os.path.getsize(tmp) > 5000:
                with open(tmp, "rb") as f:
                    raw = f.read()
                os.remove(tmp)
            else:
                print(f"  ⚠ curl fallback failed")
                return None
        elif r.status_code != 200:
            print(f"  ⚠ Download failed ({r.status_code}): {img_url[:80]}")
            return None
        else:
            raw = r.content

        if len(raw) < 5000:
            print(f"  ⚠ Image too small ({len(raw)} bytes)")
            return None

        from PIL import Image
        img = Image.open(BytesIO(raw))
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        max_w = 1200
        if img.width > max_w:
            ratio = max_w / img.width
            img = img.resize((max_w, int(img.height * ratio)), Image.LANCZOS)
        buf = BytesIO()
        img.save(buf, format='JPEG', quality=80, optimize=True)
        compressed = buf.getvalue()
        print(f"  ✓ Compressed to {len(compressed)//1024}KB ({img.width}x{img.height})")

        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
        up_headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "image/jpeg",
            "x-upsert": "true"
        }
        ur = requests.post(upload_url, headers=up_headers, data=compressed, timeout=30)
        if ur.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded: {public_url[:80]}...")
            return public_url
        else:
            print(f"  ⚠ Upload failed ({ur.status_code}): {ur.text[:200]}")
            return None
    except Exception as e:
        print(f"  ⚠ compress_and_upload error: {e}")
        return None


def validate_image_url(url):
    """Check that image URL returns 200 with image content-type and >5KB."""
    if not url:
        return False
    try:
        r = requests.get(url, headers=UA, timeout=10, stream=True)
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            return True
        # For chunked responses without Content-Length
        if r.status_code == 200 and "image" in ct:
            chunk = r.raw.read(6000)
            if len(chunk) > 5000:
                return True
    except:
        pass
    return False


def insert_article(article):
    """Insert article into p2_articles."""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=article,
        timeout=30
    )
    if r.status_code in (200, 201):
        data = r.json()
        art_id = data[0]['id'] if isinstance(data, list) else data['id']
        print(f"  ✓ Article inserted: {art_id}")
        return art_id
    else:
        print(f"  ✗ Insert failed ({r.status_code}): {r.text[:300]}")
        return None


# ============================================================
# ARTICLE 1: India's Coaching Staff Overhaul
# ============================================================

def write_coaching_overhaul():
    print("\n=== ARTICLE 1: India's Coaching Staff Overhaul ===")

    slug = "india-coaching-overhaul-morkel-absent-bahutule-interim-nayar-returns-gambhir-sri-lanka-nri-july-2026"
    headline = "Out With Morkel, In With Bahutule. India's Coaching Staff Gets a Post-Whitewash Facelift."
    subheadline = "Morne Morkel will miss the Sri Lanka tour for personal reasons. Sairaj Bahutule steps in as interim bowling coach. Abhishek Nayar returns. And Gambhir's backroom is starting to look very different from the one that walked into the England disaster."

    body = """The wreckage of India's 4-0 T20I humiliation in England is still being catalogued, but the coaching staff is already changing shape. As the team prepares to depart for Sri Lanka on Monday for a six-match white-ball series, at least one key face from the England tour will be missing — and a familiar one is walking back in.

Morne Morkel, the former South Africa fast bowler who served as India's bowling coach through the England debacle, will not travel to Colombo. According to Cricbuzz, Morkel has flown to Pretoria to attend to his unwell father. The BCCI has confirmed that Sairaj Bahutule, a former India leg-spinning all-rounder currently on the staff of the National Cricket Academy in Bengaluru, will serve as interim bowling coach for the Sri Lanka assignment.

The move is not entirely a surprise. Morkel's two-year contract with the BCCI was already under review, and while talks about a formal extension remain ongoing, the immediate priority was finding someone who could handle India's spin-heavy bowling attack on Sri Lankan surfaces. Bahutule, who played two Tests and eight ODIs between 1997 and 2003, fits that brief precisely.

## Nayar Returns, T Dilip Stays

The more significant shift involves the assistant coaching positions. Abhishek Nayar, the former India all-rounder who was part of Gambhir's original coaching setup before being relieved after the 2025 Champions Trophy, is set to rejoin the team as assistant coach. Ryan ten Doeschate, the former Dutch international who has been coaching the LA Knight Riders in MLC, will also continue as assistant coach.

T Dilip, the fielding coach who survived the transition from Rahul Dravid's regime and was initially reported to be on his way out, will stay. Despite India's fielding being widely criticised during the England tour — the team dropped 48 extras compared to England's 22 across the T20I series — Dilip's value as a dressing room influence appears to have saved his position. Sources close to the team describe him as "very good at team bonding exercises," a factor the BCCI considers essential in an environment where competitive pressure can fracture relationships.

## The Bigger Picture

The coaching reshuffle raises questions about the stability of Gambhir's setup. When he took charge in July 2024 after Dravid's departure, Gambhir hand-picked his own staff from IPL connections: Nayar and ten Doeschate from Kolkata Knight Riders, Morkel from Lucknow Super Giants. Two years later, that core has been disrupted. Nayar was dropped and is now being recalled. Morkel's future is uncertain. Sitanshu Kotak, who replaced Nayar as batting coach, is part of the setup, but the overall structure is in flux.

Adding to the complexity is the decision to send VVS Laxman, head of the BCCI's Centre of Excellence, to oversee India's T20I team in Zimbabwe later this month and then again for the Asian Games in September. This effectively creates a parallel coaching track — one for the senior team under Gambhir, another for the second-string squad under Laxman. Some BCCI officials have privately questioned why Gambhir's staff needs rest between assignments, particularly given they already had downtime during IPL 2026.

"I don't quite understand the need to send VVS Laxman to Zimbabwe," one source told the Times of India. "There is clearly more than meets the eye."

## What NRIs Should Watch

For the Indian diaspora watching from North America, the coaching musical chairs matter because they signal institutional uncertainty at a moment when India's cricket stocks are at their lowest in years. The T20I team just lost its world No. 1 ranking to England. The batting unit has been exposed on overseas tracks. The ODI series starting this week — with Rohit Sharma, Virat Kohli, and Jasprit Bumrah recalled — is as much a reputational rescue mission as it is a cricket series.

The Sri Lanka ODIs will be Bahutule's first assignment with the senior team, and Nayar's first since his departure. If India produce another limp display, the questions won't just be about the players — they'll be about whether Gambhir's entire coaching philosophy can survive the scrutiny.

The ODI squad — led by Shubman Gill with Rohit and Kohli in the ranks — departs for Colombo on Monday. Whether the coaching staff can gel quickly enough to arrest India's slide is anyone's guess. The only certainty is that the backroom now looks nothing like the one Gambhir originally assembled."""

    # Source image: Gambhir (head coach central to the story)
    print("  Sourcing image...")
    img_url = fetch_wikipedia_person_image("Gautam Gambhir")
    img_caption = "India head coach Gautam Gambhir faces a reshaped coaching staff after the England T20I whitewash"
    img_attribution = "Wikimedia Commons"

    if not img_url:
        # Fallback: Wikimedia Commons search
        commons = fetch_wikimedia_commons_images("Gautam Gambhir cricket coach", limit=3)
        if commons:
            img_url = commons[0]["url"]

    final_url = None
    if img_url:
        final_url = compress_and_upload(img_url, f"sports/{slug}.jpg")

    if not final_url:
        print("  ⚠ No image available — inserting without hero image")

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "sports",
        "vertical": "cricket",
        "status": "review",
        "is_editorial": False,
        "image_url": final_url or "",
        "image_caption": img_caption if final_url else "",
        "image_attribution": img_attribution if final_url else "",
        "diaspora_angle": "India's coaching instability directly affects whether the team NRIs support can recover its dominance on the world stage.",
        "sources": json.dumps([
            {"name": "Cricbuzz", "url": "https://www.cricbuzz.com"},
            {"name": "Cricket Addictor", "url": "https://www.cricketaddictor.com"},
            {"name": "Times of India", "url": "https://timesofindia.indiatimes.com"},
            {"name": "myKhel", "url": "https://www.mykhel.com"}
        ]),
        "score_total": 8,
        "published_at": datetime.now(timezone.utc).isoformat(),
    }
    return insert_article(article)


# ============================================================
# ARTICLE 2: Experts Blast India's T20I System
# ============================================================

def write_experts_blast():
    print("\n=== ARTICLE 2: Experts Blast India's T20I System ===")

    slug = "manjrekar-gavaskar-blast-india-t20i-system-ipl-makeup-batters-ranking-drop-england-whitewash-nri-july-2026"
    headline = "Manjrekar Says the IPL 'Puts Heavy Makeup' on Indian Batters. Gavaskar Agrees the System Is Broken."
    subheadline = "After a 4-0 whitewash by England — their worst-ever T20I series defeat — India have lost the world No. 1 ranking. The backlash from legends and experts goes far beyond the dressing room."

    body = """The final scorecard was bad enough: England 257/3, India 201/8, a 56-run defeat, and a 4-0 series whitewash. But what has followed the fifth T20I at Southampton is something India's cricket establishment hasn't faced in a long time — a full-spectrum critique of the system that produces its players.

Sanjay Manjrekar, the former India batsman turned commentator, fired the sharpest salvo. "The easy thing would be to hold players responsible for this overseas T20 setback," Manjrekar wrote on X on July 12. "The right thing would be to hold those responsible who have made the IPL such that it puts a heavy makeup on Indian batters."

It's a devastating line, and it cuts to the heart of a growing unease about the gap between IPL performance and international capability. Indian batsmen dominate the IPL — flat pitches, short boundaries, home conditions — and then struggle to replicate that output on English tracks with more bounce, movement, and variable dimensions.

## The Numbers Don't Lie

The statistical gulf between the two sides during the T20I series was enormous. England's bowlers claimed 39 wickets; India managed just 17. England's bowling economy was 8.9 runs per over; India's was 11.1. England picked up a wicket every 14 balls; India needed 26 deliveries per dismissal. England's bowling average was 20.9; India's was an alarming 47.5.

And then there were the extras. England conceded 22 extras across the series. India gifted away 48, including costly no-balls that released pressure at critical moments.

"The batting has to really come to the party, because the batting is the strongest part of this Indian team," said Sunil Gavaskar, the former India captain and one of the greatest batsmen in history. "If the strongest part is not doing well, then no wonder it has an effect on your bowling as well as your catching."

## The Adaptation Problem

Dinesh Karthik, the wicketkeeper-batsman turned commentator, pointed to a specific technical weakness. "I think India have a problem adapting to a little bit of extra bounce," he told Cricbuzz. "The middle order looks wobbly, not confident, and it is definitely not the Indian team that we saw during the World Cup or before it in bilateral series, where they took down opponents and actually imposed a lot of fear. Where has that gone?"

Captain Shreyas Iyer, who now has six losses and one no-result in seven T20Is as captain, acknowledged the failure. "We kept on going from one venue to another, and we kept on facing challenges, especially in terms of the dimensions, the grounds, the conditions," Iyer said at the post-match press conference. "Just to adapt to it as quickly as we could have anticipated — that didn't happen."

Commentator Harsha Bhogle called the defeat a potential "wake-up call" — but even that framing has drawn pushback. India had already been whitewashed 2-0 by Ireland before the England series. If two consecutive series defeats without a single completed-match victory doesn't constitute a wake-up call, what does?

## The Ranking Drop

The immediate consequence is institutional. England have replaced India at the top of the ICC Men's T20I rankings — just months after India won the T20 World Cup. The world champions are now world No. 2, and the gap is not marginal. England's dominance across all three departments during the series makes the ranking change feel entirely justified.

The BCCI has ordered a performance review and has already sacked fielding coach T Dilip, according to initial reports — though subsequent reporting from Cricbuzz suggests Dilip may in fact be retained. Either way, the message is clear: the board is not treating this as a blip.

## Why NRIs Should Pay Attention

For Indian Americans who grew up watching India dominate white-ball cricket, this is a sobering moment. The team that won the T20 World Cup less than a year ago looks unrecognisable overseas. The IPL — which many diaspora fans follow religiously — is being identified as part of the problem, not the solution. And the leadership pipeline is under strain: Iyer's captaincy is being questioned, Gambhir's coaching setup is being reshuffled, and the BCCI is simultaneously running a parallel team under VVS Laxman for the Zimbabwe T20Is.

The ODI series against England, starting this week with Rohit Sharma, Virat Kohli, and Jasprit Bumrah back in the squad, is India's chance to change the narrative. But Manjrekar's "makeup" metaphor will linger. Until Indian batsmen prove they can perform away from the IPL's flat decks and short boundaries, the question will remain: is the system building cricketers, or just entertainers?"""

    # Source image: Shreyas Iyer (captain at centre of the storm)
    print("  Sourcing image...")
    img_url = fetch_wikipedia_person_image("Shreyas Iyer")
    img_caption = "India T20I captain Shreyas Iyer has six losses in seven matches at the helm after the England whitewash"
    img_attribution = "Wikimedia Commons"

    if not img_url:
        # Try Sanjay Manjrekar or generic
        img_url = fetch_wikipedia_person_image("Sanjay Manjrekar")
        if img_url:
            img_caption = "Commentator Sanjay Manjrekar accused the IPL of putting 'heavy makeup' on Indian batters"

    if not img_url:
        commons = fetch_wikimedia_commons_images("India cricket T20 England 2026", limit=3)
        if commons:
            img_url = commons[0]["url"]
            img_caption = "India's T20I team during the England tour"

    final_url = None
    if img_url:
        final_url = compress_and_upload(img_url, f"sports/{slug}.jpg")

    if not final_url:
        print("  ⚠ No image — inserting without hero")

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "sports",
        "vertical": "cricket",
        "status": "review",
        "is_editorial": False,
        "image_url": final_url or "",
        "image_caption": img_caption if final_url else "",
        "image_attribution": img_attribution if final_url else "",
        "diaspora_angle": "The IPL — followed religiously by NRIs — is being blamed for India's overseas batting failures, raising uncomfortable questions about the league diaspora fans love.",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com"},
            {"name": "Cricbuzz", "url": "https://www.cricbuzz.com"},
            {"name": "Cricket Addictor", "url": "https://www.cricketaddictor.com"},
            {"name": "myKhel", "url": "https://www.mykhel.com"}
        ]),
        "score_total": 8,
        "published_at": datetime.now(timezone.utc).isoformat(),
    }
    return insert_article(article)


# ============================================================
# ARTICLE 3: MLC 2026 Playoffs — Hassan Khan's 10-Ball Blitz
# ============================================================

def write_mlc_hassan_khan():
    print("\n=== ARTICLE 3: MLC Playoffs — Hassan Khan's 10-Ball Blitz ===")

    slug = "mlc-2026-hassan-khan-10-ball-36-sf-unicorns-playoffs-final-standings-american-cricket-nri-july-2026"
    headline = "Six, Four, Four, Six. Hassan Khan's Ten-Ball Demolition Seals the MLC Playoff Picture."
    subheadline = "San Francisco Unicorns clinch the top seed with 12 points. LA Knight Riders and MI New York complete the playoff bracket. And a 22-year-old's unbeaten 36 off 10 balls might be the most electrifying cameo in MLC history."

    body = """In ten deliveries, Hassan Khan turned a stuttering chase into a statement. With San Francisco Unicorns needing 47 off the last four overs against Seattle Orcas on Saturday night at Grand Prairie Stadium, the 22-year-old walked in at No. 6 and proceeded to dismantle the bowling with a clarity that belied the pressure.

First, back-to-back sixes against Tanveer Sangha in the 18th over. Then, in the 19th, Marcus Stoinis tried three slow bouncers — and watched each one sail to the boundary: six, four, four, six. The first hit was a pristine lofted cover drive. The last was an emphatic pull. In between, Stoinis — who had taken a career-best five-wicket haul in his previous match — finished with 0/48, the most expensive spell of his MLC career.

Hassan Khan ended unbeaten on 36 off 10 balls, striking at 360. The Unicorns chased down 191 with six wickets and an over to spare. Seattle Orcas were eliminated from playoff contention.

## The Final Standings

With the league phase now complete, the MLC 2026 playoff picture is set:

**1. San Francisco Unicorns** — 12 points (6 wins, 1 loss, 3 no results). The dominant force of the tournament, led by consistent performances from Finn Allen (65 off 31 on Saturday), Matt Short, and Lhuan-dre Pretorius. Their only loss came to LA Knight Riders. They enter the playoffs as heavy favourites.

**2. LA Knight Riders** — 8 points (4 wins, 1 loss, 5 no results). A resilient campaign defined by quality wins and an ability to avoid defeats in rain-affected matches. Their sole loss came early, and they've won their last two matches to lock in second place.

**3. MI New York** — 6 points (3 wins, 3 losses, 4 no results). The most inconsistent of the qualifiers, but a crucial win over Seattle Orcas — powered by Tajinder Singh's unbeaten 66 off 27 balls — kept them in the hunt. Kieron Pollard's 54 in that match was a reminder that experience still counts in franchise cricket.

**4-6. Washington Freedom, Seattle Orcas, Texas Super Kings** — All on 4 points. The bottom three were separated by net run rate but ultimately couldn't generate enough wins to challenge for the top three.

## The Oakland Factor

The playoffs will take the tournament to Oakland Coliseum — the first time MLC has staged knockout matches in the Bay Area. For the Indian diaspora concentrated in the San Francisco-San Jose corridor, this is a landmark moment. The SF Unicorns are the local franchise, and a home playoff run is the kind of event that could deepen cricket's roots in a market where the sport is already culturally resonant.

The Unicorns' roster is built for this moment. Allen provides explosive starts, Short anchors the middle overs, and the depth of options — as Hassan Khan demonstrated — means the batting doesn't depend on any single player. Their bowling, led by Peter Siddle's experience and Xavier Bartlett's pace, has been the tournament's most disciplined unit.

## Hassan Khan: The Name to Watch

Khan's cameo against Seattle wasn't his first impact in MLC 2026 — he scored a quickfire 16 earlier in the tournament — but the manner of Saturday's innings marked him as a player with a future. At 22, he showed the composure of someone who has been in these situations before. His bat swing is clean, his decision-making under pressure was flawless, and his willingness to target the best bowler on the field (Stoinis) suggests a mindset that coaches value.

In the context of American cricket's growth, players like Hassan Khan matter. They're the highlight-reel moments that convert curious viewers into fans. In a tournament that has already seen Dasun Shanaka's double hat-trick and Pretorius's blistering hundreds, Hassan Khan's 10-ball blitz is the latest addition to MLC's growing library of genuinely great cricket.

## What's Next

The playoff format sees the top-two seeds face off in a qualifier, with the loser getting a second chance against the third-place finisher. For NRIs in the Bay Area, the schedule means accessible, affordable live cricket in their backyard — a proposition that was unthinkable five years ago. The MLC may still be finding its audience, but nights like Saturday prove the product is there. All it needs is more Hassan Khans."""

    # Source image: Try Wikimedia Commons for MLC or cricket stadium
    print("  Sourcing image...")
    # Try specific cricket commons images
    img_url = None
    img_caption = ""
    img_attribution = "Wikimedia Commons"

    # Try Oakland Coliseum or Grand Prairie Stadium
    commons = fetch_wikimedia_commons_images("Grand Prairie Stadium cricket Texas", limit=3)
    if commons:
        img_url = commons[0]["url"]
        img_caption = "Grand Prairie Stadium in Texas, home of MLC 2026 league-stage matches"

    if not img_url:
        commons = fetch_wikimedia_commons_images("Major League Cricket USA", limit=5)
        if commons:
            img_url = commons[0]["url"]
            img_caption = "Major League Cricket has completed its 2026 league phase with San Francisco Unicorns topping the table"

    if not img_url:
        commons = fetch_wikimedia_commons_images("cricket T20 batting six", limit=3)
        if commons:
            img_url = commons[0]["url"]
            img_caption = "Hassan Khan's 10-ball 36 sealed San Francisco Unicorns' place atop the MLC 2026 standings"

    final_url = None
    if img_url:
        final_url = compress_and_upload(img_url, f"sports/{slug}.jpg")

    if not final_url:
        print("  ⚠ No image — inserting without hero")

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "sports",
        "vertical": "cricket",
        "status": "review",
        "is_editorial": False,
        "image_url": final_url or "",
        "image_caption": img_caption if final_url else "",
        "image_attribution": img_attribution if final_url else "",
        "diaspora_angle": "MLC playoffs in Oakland give Bay Area NRIs their first-ever home cricket playoff, with the local SF Unicorns as top seeds — live cricket in the diaspora's backyard.",
        "sources": json.dumps([
            {"name": "Cricbuzz", "url": "https://www.cricbuzz.com"},
            {"name": "CricketAddictor", "url": "https://www.cricketaddictor.com"},
            {"name": "SportsCafe", "url": "https://www.sportscafe.in"},
            {"name": "CricketNmore", "url": "https://www.cricketnmore.com"}
        ]),
        "score_total": 8,
        "published_at": datetime.now(timezone.utc).isoformat(),
    }
    return insert_article(article)


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("The Videshi Sports Writer — July 13, 2026 4pm PT")
    print("=" * 60)

    results = []
    results.append(("Coaching Overhaul", write_coaching_overhaul()))
    results.append(("Experts Blast T20I System", write_experts_blast()))
    results.append(("MLC Hassan Khan", write_mlc_hassan_khan()))

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for name, art_id in results:
        status = f"✓ {art_id}" if art_id else "✗ FAILED"
        print(f"  {name}: {status}")
    print("=" * 60)

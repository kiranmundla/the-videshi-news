#!/usr/bin/env python3
"""Sports writer for The Videshi - June 4, 2026 evening run"""

import json
import os
import requests
import subprocess
import urllib.parse
from datetime import datetime, timezone

# Load env
def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, val = line.split('=', 1)
                    key = key.replace('export ', '').strip()
                    val = val.strip().strip('"').strip("'")
                    os.environ[key] = val

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY', '')
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
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

def fetch_wikimedia_commons_images(search_query, limit=5):
    """Search Wikimedia Commons for CC-licensed images."""
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": search_query,
        "gsrnamespace": "6",
        "gsrlimit": str(limit),
        "prop": "imageinfo",
        "iiprop": "url|size|mime|extmetadata",
        "iiurlwidth": "1200",
        "format": "json"
    }
    try:
        r = requests.get(
            "https://commons.wikimedia.org/w/api.php",
            params=params,
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=15
        )
        if r.status_code == 200:
            data = r.json()
            pages = data.get("query", {}).get("pages", {})
            results = []
            for pid, page in pages.items():
                ii = page.get("imageinfo", [{}])[0]
                mime = ii.get("mime", "")
                if not mime.startswith("image/"):
                    continue
                if mime == "image/svg+xml" or ii.get("width", 0) < 300:
                    continue
                results.append({
                    "url": ii.get("thumburl") or ii.get("url", ""),
                    "original_url": ii.get("url", ""),
                    "title": page.get("title", ""),
                    "width": ii.get("width", 0),
                    "height": ii.get("height", 0),
                    "mime": mime
                })
            if results:
                print(f"  ✓ Wikimedia Commons: {len(results)} images found for '{search_query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Wikimedia Commons error for '{search_query}': {e}")
    return []

def fetch_pexels_image(query):
    """Fetch an image from Pexels using curl (Python urllib gets 403)."""
    try:
        result = subprocess.run(
            ['curl', '-sS', '-H', f'Authorization: {PEXELS_KEY}',
             f'https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page=3'],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            photos = data.get('photos', [])
            if photos:
                url = photos[0].get('src', {}).get('large2x') or photos[0].get('src', {}).get('large')
                if url:
                    print(f"  ✓ Pexels image found for '{query}': {url[:80]}...")
                    return url
    except Exception as e:
        print(f"  ⚠ Pexels error for '{query}': {e}")
    return None

def validate_image(url):
    """Validate that a URL returns a real image."""
    try:
        r = requests.head(url, headers={"User-Agent": "TheVideshi/1.0"}, timeout=10, allow_redirects=True)
        content_type = r.headers.get('Content-Type', '')
        content_length = int(r.headers.get('Content-Length', 0))
        if r.status_code == 200 and 'image' in content_type and content_length > 5000:
            print(f"  ✓ Image validated: {content_length} bytes, {content_type}")
            return True
        else:
            print(f"  ✗ Image validation failed: status={r.status_code}, type={content_type}, size={content_length}")
            return False
    except Exception as e:
        print(f"  ✗ Image validation error: {e}")
        return False

def publish_article(article):
    """Insert article into Supabase."""
    url = f"{SUPABASE_URL}/rest/v1/p2_articles"
    try:
        r = requests.post(url, headers=HEADERS, json=article, timeout=30)
        if r.status_code in (200, 201):
            result = r.json()
            if isinstance(result, list) and result:
                print(f"  ✓ Published: {result[0].get('headline', 'unknown')[:60]}...")
                return True
        print(f"  ✗ Publish failed: {r.status_code} - {r.text[:200]}")
    except Exception as e:
        print(f"  ✗ Publish error: {e}")
    return False


# ============================================================
# ARTICLE 1: Hariharan-Arjun reach maiden Super 1000 QF
# ============================================================
print("\n" + "="*60)
print("ARTICLE 1: Hariharan-Arjun Indonesia Open QF")
print("="*60)

# Image sourcing - try multiple approaches
art1_image_url = None
art1_image_caption = None
art1_image_attribution = None

# Try Wikimedia Commons for Indonesia Open / badminton
commons_results = fetch_wikimedia_commons_images("Indonesia Open badminton 2024 doubles")
if not commons_results:
    commons_results = fetch_wikimedia_commons_images("badminton doubles men")
if not commons_results:
    commons_results = fetch_wikimedia_commons_images("Istora Senayan Jakarta badminton")

for img in commons_results:
    if validate_image(img["url"]):
        art1_image_url = img["url"]
        art1_image_caption = "Badminton doubles action at the Istora Senayan in Jakarta"
        art1_image_attribution = "Wikimedia Commons"
        break

if not art1_image_url:
    pexels_url = fetch_pexels_image("badminton doubles match professional")
    if pexels_url and validate_image(pexels_url):
        art1_image_url = pexels_url
        art1_image_caption = "Badminton doubles players in action during a professional tournament"
        art1_image_attribution = "Pexels"

art1_body = """Hariharan Amsakarunan and MR Arjun have reached the quarterfinals of the Indonesia Open 2026, the first time an Indian men's doubles pair other than Satwiksairaj Rankireddy and Chirag Shetty has advanced this deep at a BWF Super 1000 event.

The milestone came at the Istora Senayan in Jakarta on Thursday, where the Indian duo fought back from a game down to beat Malaysia's Aaron Tai and Kang Khai Xing 16–21, 21–15, 21–19 in one hour and 12 minutes.

## A Comeback Built on Nerve

The opening game was all Malaysia. Tai and Kang controlled the net, forcing Hariharan and Arjun into defensive positions with sharp smashes and deceptive drops. The Indians lost the first game 16–21 and looked under pressure.

The second game told a different story. Arjun stepped up his service returns, and Hariharan began finding angles past the Malaysian front court. The Indian pair won 21–15, levelling the match with noticeably better control of the rallies.

The decider was tense. The Malaysians led 11–8 at the interval, and for five minutes after the change of ends, every point mattered. Trailing 8–11, Hariharan and Arjun won four consecutive points to draw level at 12–12. That sequence — patient defence followed by sudden aggression — encapsulated how the pair has been playing through the 2026 season. They never trailed again, closing out the game 21–19.

## Why This Matters for Indian Badminton

India's men's doubles programme has been a one-pair story for the better part of four years. Satwik and Chirag have been magnificent — world No. 4, Singapore Open champions last week, Olympic medallists — but they retired hurt from their opening-round match at this very tournament after Satwik aggravated a shoulder injury.

That meant India's doubles hopes in Jakarta rested entirely on Hariharan and Arjun. The pair, both still in their early twenties, answered the call.

They had already won their first-round match against the unranked pairing of Ade Tan and Nicky Azriyn 21–18, 21–10 on Tuesday. But the Round of 16 was a different test — Aaron Tai and Kang Khai Xing had beaten the fourth-seeded Satwik-Chirag pair's replacements in the draw to reach that stage and brought genuine attacking intent to every rally.

## A Breakthrough at the Right Time

Hariharan and Arjun had been building quietly. They reached the second round at the Swiss Open earlier this year and had shown improved consistency across mid-tier events. But a Super 1000 quarterfinal — at the Indonesia Open, one of the five marquee stops on the World Tour — is a different calibre entirely.

They will next face the seventh-seeded Malaysian pair of Goh Sze Fei and Nur Izzuddin, former world No. 1 contenders who are comfortable playing at this level. Regardless of that result, the milestone has already been reached.

## The Diaspora Angle

For Indian badminton fans in the US, UK, and Canada, the development of a second competitive men's doubles pair is long overdue. India has historically produced strong singles players — Saina Nehwal, PV Sindhu, Kidambi Srikanth — but depth in doubles has been thin. The success of Hariharan and Arjun at this level suggests the coaching infrastructure at the Gopichand Academy and elsewhere is beginning to produce results beyond the established names.

## Singles Campaign Over

India's singles challenge ended on the same day. PV Sindhu lost to world No. 1 An Se Young 17–21, 15–21 — extending her winless record against the Korean to ten consecutive matches. Ayush Shetty fell to Hong Kong's Lee Cheuk Yiu 21–16, 13–21, 14–21, unable to sustain his first-game momentum.

With both singles players eliminated, Hariharan and Arjun carry the last Indian flag still flying in Jakarta.

*Sources: Badminton World Federation official results; Revsportz; The Bridge*"""

article1 = {
    "headline": "Satwik and Chirag Were Out. Hariharan and Arjun Stepped In. India Has a Second Doubles Pair at the Super 1000 Level.",
    "subheadline": "MR Arjun and Hariharan Amsakarunan fought back from a game down to reach the Indonesia Open quarterfinals — a first for any Indian men's doubles pair outside the Satwik-Chirag partnership at a BWF Super 1000 event.",
    "slug": "hariharan-arjun-indonesia-open-2026-quarterfinal-maiden-super-1000-doubles-nri",
    "body": art1_body,
    "category": "sports",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "is_editorial": False,
    "image_url": art1_image_url,
    "image_caption": art1_image_caption,
    "image_attribution": art1_image_attribution,
    "sources": json.dumps(["Badminton World Federation", "Revsportz", "The Bridge"]),
    "vertical": "sports",
}

if art1_image_url:
    print("\n→ Publishing Article 1...")
    publish_article(article1)
else:
    print("\n✗ Skipping Article 1 — no valid image found")


# ============================================================
# ARTICLE 2: KS Bharat retires from international cricket
# ============================================================
print("\n" + "="*60)
print("ARTICLE 2: KS Bharat Retires from International Cricket")
print("="*60)

# Image sourcing - Wikipedia first for person article
art2_image_url = fetch_wikipedia_person_image("KS Bharat")
if not art2_image_url:
    art2_image_url = fetch_wikipedia_person_image("KS Bharat (cricketer)")
if not art2_image_url:
    art2_image_url = fetch_wikipedia_person_image("Kona Srikar Bharat")

art2_image_caption = None
art2_image_attribution = None

if art2_image_url and validate_image(art2_image_url):
    art2_image_caption = "KS Bharat during an international match for India"
    art2_image_attribution = "Wikimedia Commons"
else:
    art2_image_url = None
    # Try Wikimedia Commons
    commons_results = fetch_wikimedia_commons_images("KS Bharat India cricket")
    if not commons_results:
        commons_results = fetch_wikimedia_commons_images("India Test cricket wicketkeeper")
    for img in commons_results:
        if validate_image(img["url"]):
            art2_image_url = img["url"]
            art2_image_caption = "India's Test cricket wicketkeeper in action"
            art2_image_attribution = "Wikimedia Commons"
            break

    if not art2_image_url:
        pexels_url = fetch_pexels_image("cricket wicketkeeper India test match")
        if pexels_url and validate_image(pexels_url):
            art2_image_url = pexels_url
            art2_image_caption = "A wicketkeeper in action during a cricket test match"
            art2_image_attribution = "Pexels"

art2_body = """KS Bharat announced his retirement from international cricket on Thursday, stepping away from the game at the age of 32 with seven Test caps, 221 runs, and the memory of keeping wicket for India in a World Test Championship final.

The Visakhapatnam-born wicketkeeper-batter shared an emotional farewell note on Instagram, thanking his family, the BCCI, Virat Kohli, Rohit Sharma, and former head coach Rahul Dravid. It was a quiet ending for a player whose career was shaped more by timing and circumstance than by any deficiency in his craft.

## The Path That Almost Wasn't

Bharat's route to international cricket was anything but linear. He first received an India call-up in 2019 but did not make his debut for four more years. It was Rishabh Pant's devastating car accident in December 2022 that opened the door — Bharat was selected for the home Border-Gavaskar Trophy against Australia in early 2023 and played all four Tests of the series.

He then made the squad for the World Test Championship final at The Oval against Australia in June 2023. Standing behind the stumps on that stage, with Pat Cummins and Steve Smith at the crease, was the culmination of more than a decade of domestic cricket.

His final international appearance came against England in his hometown of Visakhapatnam in February 2024. After that, the door that Pant's absence had opened quietly closed again as Pant returned and Dhruv Jurel emerged as another option.

## Seven Tests, One Final, No Regrets

The numbers are modest: 221 runs at 20.09, with a highest score of 44. Eighteen catches and one stumping. But statistics tell an incomplete story. Bharat's value lay in his reliability behind the stumps, honed through more than a hundred First-Class matches for Andhra, where he accumulated 6,102 runs at 36.53 with eleven centuries and 380 catches.

"In a family of four, we all lived the same dream over two decades," Bharat wrote. "A big heart to my sister, Mom and Dad for creating an environment and support system they have been. I am a product of their love, discipline and hard work."

He singled out Kohli for giving him his IPL opportunity with Royal Challengers Bengaluru in 2021, where he memorably hit a last-ball six to beat Delhi Capitals — a knock that brought him into national conversation. He thanked Rohit Sharma, under whose captaincy he made his Test debut, and Dravid, whose mentorship stretched back to India A tours.

## What It Means for the Wicketkeeping Debate

Bharat's retirement does not alter India's immediate plans. Pant is the first-choice keeper across formats, and Jurel — selected in the squad for Friday's Test against Afghanistan at Mullanpur — is the established backup. Ishan Kishan, recalled for the ODI leg against Afghanistan, adds a third option.

But Bharat's career underscores a broader truth about Indian cricket's wicketkeeping depth. Between Dhoni's retirement and Pant's emergence, the position churned through Saha, Bharat, Samson, and Kishan with no settled hierarchy. Bharat happened to be the one holding the gloves at one of India's most significant moments — the WTC final — and he performed with composure.

## The Diaspora Connection

For NRI cricket fans, Bharat's story is familiar in a different way. The idea of waiting years for a chance, finally getting it under unexpected circumstances, and then performing with quiet professionalism resonates beyond cricket. His farewell note — humble, family-centred, grateful — reads like a letter many first-generation diaspora professionals might write.

His journey in the game continues. At 32, with over 6,000 First-Class runs and elite domestic pedigree, Bharat will remain a fixture in the Andhra setup and could still contribute at the IPL level. The India cap is put away, but the cricket goes on.

*Sources: BCCI; CricTracker; Khel Now; ESPN Cricinfo*"""

article2 = {
    "headline": "'In a Family of Four, We All Lived the Same Dream.' KS Bharat Retires From International Cricket at 32.",
    "subheadline": "The Visakhapatnam wicketkeeper-batter played seven Tests for India, including the 2023 WTC final at The Oval, before stepping away with an emotional note thanking Kohli, Rohit, and Dravid.",
    "slug": "ks-bharat-retirement-international-cricket-seven-tests-wtc-final-nri",
    "body": art2_body,
    "category": "sports",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "is_editorial": False,
    "image_url": art2_image_url,
    "image_caption": art2_image_caption,
    "image_attribution": art2_image_attribution,
    "sources": json.dumps(["BCCI", "CricTracker", "Khel Now", "ESPN Cricinfo"]),
    "vertical": "sports",
}

if art2_image_url:
    print("\n→ Publishing Article 2...")
    publish_article(article2)
else:
    print("\n✗ Skipping Article 2 — no valid image found")


print("\n" + "="*60)
print("Sports writer run complete.")
print("="*60)

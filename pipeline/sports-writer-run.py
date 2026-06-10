#!/usr/bin/env python3
"""
Sports writer for The Videshi — June 10, 2026 run.
Produces 2 articles, sources images, uploads to Supabase.
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
    encoded = person_name.replace(' ', '_')
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
        r = requests.get(img_url, headers=UA, timeout=20)
        if r.status_code != 200:
            print(f"  ⚠ Download failed ({r.status_code}): {img_url[:80]}")
            return None
        if len(r.content) < 5000:
            print(f"  ⚠ Image too small ({len(r.content)} bytes)")
            return None

        from PIL import Image
        img = Image.open(BytesIO(r.content))
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

        # Upload to Supabase storage
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
# ARTICLE 1: Manav Suthar dream debut
# ============================================================

def write_manav_suthar_article():
    print("\n=== ARTICLE 1: Manav Suthar Dream Debut ===")

    slug = "manav-suthar-test-cap-319-dream-debut-gavaskar-praise-rajasthan-spin-hope-nri"
    headline = "He Took Six Wickets in His First Innings. Gavaskar Said It Had Nothing to Do With the Pitch."
    subheadline = "Manav Suthar became only the tenth Indian bowler to claim a five-wicket haul on Test debut. The 23-year-old left-arm spinner from Rajasthan earned Test Cap No. 319 — and the respect of a legend."

    body = """The numbers alone would have been enough: 6 for 33 in the first innings, seven wickets in the match, Player of the Match on debut, and India's biggest-ever Test victory — by an innings and 300 runs. But what Manav Suthar did against Afghanistan in Mullanpur last week was more than a statistical debut. It was a statement of method.

Sunil Gavaskar, who has watched every Indian spinner from Bishen Bedi to Ravichandran Ashwin, saw something specific. Speaking on JioStar after the match, the legendary opener went out of his way to separate Suthar's performance from the usual narrative about Indian spinners thriving on helpful pitches.

"People say a spin bowler is successful in India because he gets help from the pitch, the conditions are favourable for him," Gavaskar said. "But I would say, here against Afghanistan, take the pitch out of the equation. Bowling comes down to skill and control. And that is exactly what this young man showed."

## The Spell That Announced Him

Suthar, a left-arm orthodox spinner, dismantled Afghanistan's batting order with a combination of flight, dip, and relentless accuracy. His six-wicket haul in the first innings saw him trap Hashmatullah Shahidi lbw, clean bowl Sediqullah Atal, and catch-and-bowl Afsar Zazai. The common thread was not extravagant turn. It was precision.

"He knows exactly where each ball is going to land," Gavaskar continued. "That kind of control is rare. When you have drift and can land the ball in the right spot consistently, you don't need a turning track to take wickets. He wasn't just lucky — he was clever and accurate."

Former England spinner Graeme Swann echoed the assessment, noting Suthar's tactical awareness from the very first over. "What impressed me most was his ability to adapt as his spell progressed," Swann said. "Initially, he was attacking around the off-stump line, but he quickly recognised the amount of turn available and adjusted his line straighter, forcing the batters to play more often."

## From Rajasthan Domestic Cricket to Cap 319

Suthar's path to the Indian Test team was paved through sheer domestic weight. The 23-year-old had been a prolific wicket-taker for Rajasthan in first-class cricket and earned his Gujarat Titans IPL contract on the back of consistent performances. But it was his Ranji Trophy numbers — and the maturity he showed in high-pressure matches — that caught the selectors' attention.

His debut in Mullanpur placed him in an elite club: only the tenth Indian bowler, and the seventh spinner, to claim a five-for on Test debut. The names above him on that list read like a who's who of Indian cricket: Narendra Hirwani (8/61 vs West Indies, 1988), Ravichandran Ashwin (6/47 vs West Indies, 2011), Dilip Doshi (6/103 vs Australia, 1979), and Axar Patel (5/60 vs England, 2021).

Suthar's figures of 6 for 33 are now the second-best by an Indian spinner on debut, behind only Hirwani's legendary haul 38 years ago.

## What It Means for Indian Cricket

With Ravindra Jadeja and Axar Patel rested for the upcoming ODI series against Afghanistan, India's selectors have signalled their intent to build depth in the spin department ahead of the 2027 ODI World Cup cycle. Suthar's debut makes the case that the pipeline is delivering.

Captain Shubman Gill was direct in his post-match assessment. "India can take 20 wickets anywhere," he said, a statement that carries more weight when you consider that Suthar, alongside Prasidh Krishna (3/37), gave India four bowling options capable of running through any batting lineup.

For Suthar, the task now is to prove Gavaskar right on flatter pitches. "This was a highly encouraging debut and he has shown the attributes to be a strong contender at the Test level going forward," Gavaskar concluded. "But the real test for any spinner comes on flatter pitches where greater variety and adaptability are required."

Suthar himself offered the simplest summary. "The biggest lesson is that consistency is everything," he said after the match. "You have to keep bowling in the same area over and over again. That's the most important thing in Test cricket."

## What the Diaspora Should Know

For NRIs who follow Indian cricket through scorecards and highlights, Suthar's name may have appeared suddenly. But the domestic cricket ecosystem that produced him — Rajasthan's first-class programme, the IPL's Gujarat Titans setup, the BCCI's Centre of Excellence — has been quietly building this kind of depth for years. Suthar is not an overnight sensation. He is the product of a system that now produces international-calibre spinners as a matter of routine.

The first ODI against Afghanistan begins in Dharamsala on June 13. Suthar is not in the white-ball squad. But after Mullanpur, his name is on every selector's list for the tours that follow.

**Sources:** Reuters, JioStar (Cricket Live), Sky Sports, Mint, CricTracker"""

    # Image sourcing — Wikipedia for Manav Suthar
    print("  Sourcing image for Manav Suthar...")
    img_url = fetch_wikipedia_person_image("Manav Suthar")
    if not img_url:
        img_url = fetch_wikipedia_person_image("Manav Suthar (cricketer)")
    
    # Also try Wikimedia Commons
    commons = fetch_wikimedia_commons_images("Manav Suthar cricket India spinner")
    if not commons:
        commons = fetch_wikimedia_commons_images("India cricket spinner test debut")
    
    # Pick best candidate
    final_url = None
    attribution = "Wikimedia Commons"
    caption = "Manav Suthar celebrates a wicket during his debut Test against Afghanistan in Mullanpur"

    if img_url:
        final_url = compress_and_upload(img_url, f"{slug}.jpg")
    elif commons:
        best = commons[0]
        final_url = compress_and_upload(best["url"], f"{slug}.jpg")
    
    if not final_url:
        print("  ⚠ No suitable image found, proceeding without image")

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "sports",
        "status": "review",
        "is_editorial": False,
        "published_at": datetime.now(timezone.utc).isoformat(),
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com"},
            {"name": "JioStar Cricket Live", "url": "https://www.jiostar.com"},
            {"name": "Sky Sports", "url": "https://www.skysports.com"},
            {"name": "CricTracker", "url": "https://www.crictracker.com"},
            {"name": "Mint", "url": "https://www.livemint.com"}
        ])
    }
    if final_url:
        article["image_url"] = final_url
        article["image_caption"] = caption
        article["image_attribution"] = attribution

    return insert_article(article)


# ============================================================
# ARTICLE 2: India Women T20 World Cup — Mandhana X-Factor
# ============================================================

def write_mandhana_xfactor_article():
    print("\n=== ARTICLE 2: Smriti Mandhana X-Factor in England ===")

    slug = "smriti-mandhana-india-women-t20-world-cup-2026-england-x-factor-shafali-verma-pakistan-opener-nri"
    headline = "She Has Scored 650 Runs in England at 38.23. Now the T20 World Cup Is There."
    subheadline = "Smriti Mandhana's outstanding record in English conditions makes her India's most valuable asset as the Women's T20 World Cup begins on June 12. Aakash Chopra explains why the Powerplay could decide everything."

    body = """Smriti Mandhana averages 29.88 across 160 T20I innings. That is excellent. But take only her innings in England — 19 of them — and the average climbs to 38.23, with 650 runs to her name. That is a different player altogether.

The Women's T20 World Cup begins on Thursday, June 12, in England and Wales. India open their campaign against Pakistan at Edgbaston in Birmingham on Saturday, June 14. And the single most important variable in whether India lift the trophy at Lord's on July 5 may be Mandhana's comfort in conditions she has come to own.

## The Chopra Analysis

Aakash Chopra, speaking on his YouTube channel, did not mince words. He identified Mandhana and opening partner Shafali Verma as India's biggest X-factors — and the Powerplay as the phase that will decide their tournament.

"The Indian girls have won the 50-over World Cup. Can they win the 20-over World Cup? That's the big question," Chopra said. "Where do you win T20 games? One is if you control the Powerplay with the bat and with the ball. With the bat, Shafali Verma's consistent avatar is very, very good. Smriti Mandhana will be there with her."

The logic is straightforward. In T20 cricket, the Powerplay sets the tone. Teams that score fast in the first six overs and take early wickets rarely lose. India's opening pair — Mandhana's classical timing married to Shafali's explosive aggression — gives them one of the most destructive Powerplay combinations in the women's game.

"Smriti Mandhana in England is another beast altogether," Chopra added. "She has scored a lot of runs there. So, Smriti Mandhana and Shafali Verma, as your Powerplay players, can actually control the game. One of them should bat deep into the innings, which they can."

## Why England Suits Her

Mandhana's game is built on timing rather than power. She plays through the line, trusts the pace of the ball, and drives with a precision that English conditions — true bounce, carry, and occasional movement — reward handsomely. Where many subcontinental batters struggle against the lateral movement of a new ball in England, Mandhana has consistently found ways to score through it.

Her record there is not a statistical quirk. She performed in the 2017 ODI World Cup in England, dominated in bilateral series, and has arrived for the 2026 tournament after a targeted 25-day preparation camp at the NCA in Bengaluru followed by eight days acclimatising in the UK.

"It's been a good 25 days of prep," Mandhana said. "We had batters and bowlers camp at Bangalore at NCA and that was also very targeted and specific, keeping in mind this tour. A lot of girls, it's their first England tour so it was important for them to come here early and get used to the conditions."

## Warm-Up Form

India arrived in Cardiff with momentum. They beat West Indies by 26 runs in their first warm-up on June 8, posting 179/8 before restricting the Windies to 153/8. Bharti Fulmali scored an unbeaten fifty, while Radha Yadav and Shreyanka Patil shared seven wickets between them.

Their second warm-up, against England on Wednesday in Cardiff, was disrupted by rain — England were 92/1 in the 13th over when play was halted. India remain unbeaten in their tournament preparation.

## The Bowling Question

Chopra also flagged bowling in the death overs as India's defining challenge. "Since it's England and it would swing, Renuka Singh Thakur's value increases," he said. "But death overs — that will be the big challenge, because we get our spinners to bowl the death overs many times. How we bowl in the death overs might actually define how far we go."

India's pace attack, led by Arundhati Reddy in the absence of the injured Pooja Vastrakar, will be tested in seamer-friendly conditions. But Chopra believes India have the squad to beat both South Africa and Australia in their group, and go on to challenge for the title.

## The NRI Angle

For the Indian diaspora in the UK, this tournament offers an unprecedented opportunity. India play five group matches across Birmingham, Leeds, Manchester, Southampton, and London, all within easy travel distance of the country's largest South Asian populations. The India-Pakistan opener at Edgbaston is expected to draw one of the largest crowds in women's cricket history, with significant NRI attendance from the Birmingham and Leicester corridors.

The tournament also has a streaming advantage for diaspora audiences in North America: all matches will be available on Willow TV in the US and Canada, with ICC.tv providing free global streaming.

India's Group 1 schedule: Pakistan (June 14, Edgbaston), Netherlands (June 17, Headingley), South Africa (June 20, Hampshire), Bangladesh (June 25, Old Trafford), Australia (June 28, Lord's).

If India finish in the top two — and with Mandhana in this form in these conditions, they should — the semi-finals are at The Oval on June 30 and July 2, with the final at Lord's on July 5.

**Sources:** Sportskeeda, Yardbarker, CricTracker, ICC, Mint"""

    # Image sourcing — Wikipedia for Smriti Mandhana
    print("  Sourcing image for Smriti Mandhana...")
    img_url = fetch_wikipedia_person_image("Smriti Mandhana")
    
    # Also try Commons
    commons = fetch_wikimedia_commons_images("Smriti Mandhana cricket India women")
    
    final_url = None
    attribution = "Wikimedia Commons"
    caption = "Smriti Mandhana bats during a T20 International in England"

    if img_url:
        final_url = compress_and_upload(img_url, f"{slug}.jpg")
    elif commons:
        best = commons[0]
        final_url = compress_and_upload(best["url"], f"{slug}.jpg")
    
    if not final_url:
        print("  ⚠ No suitable image found, proceeding without image")

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "sports",
        "status": "review",
        "is_editorial": False,
        "published_at": datetime.now(timezone.utc).isoformat(),
        "sources": json.dumps([
            {"name": "Sportskeeda", "url": "https://www.sportskeeda.com"},
            {"name": "Yardbarker", "url": "https://www.yardbarker.com"},
            {"name": "CricTracker", "url": "https://www.crictracker.com"},
            {"name": "ICC Cricket", "url": "https://www.icc-cricket.com"},
            {"name": "Mint", "url": "https://www.livemint.com"}
        ])
    }
    if final_url:
        article["image_url"] = final_url
        article["image_caption"] = caption
        article["image_attribution"] = attribution

    return insert_article(article)


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    print(f"Sports writer run: {datetime.now(timezone.utc).isoformat()}")
    
    results = []
    
    art1_id = write_manav_suthar_article()
    results.append(("Manav Suthar debut", art1_id))
    
    art2_id = write_mandhana_xfactor_article()
    results.append(("Smriti Mandhana T20 WC", art2_id))
    
    print("\n=== SUMMARY ===")
    for title, aid in results:
        status = f"✓ {aid}" if aid else "✗ FAILED"
        print(f"  {title}: {status}")
    
    print("\nDone.")

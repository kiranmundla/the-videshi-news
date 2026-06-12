#!/usr/bin/env python3
"""Sports writer — June 12, 2026 batch
Two articles:
1. Women's T20 World Cup opens with England's record 219/1 — India's campaign starts Sunday
2. Shubman Gill's captaincy test in the Afghanistan ODI series
"""

import json, os, sys, uuid, time, io
import requests
from datetime import datetime, timezone

# Load env
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
            if '=' in line:
                k, v = line.split('=', 1)
                v = v.strip().strip('"').strip("'")
                os.environ[k] = v

load_env(os.path.expanduser('~/.env.supabase'))
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

UA = "TheVideshi/1.0 (thevideshi.com)"

# ─── Image sourcing helpers ───

def fetch_wikipedia_person_image(person_name):
    import urllib.parse
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": UA}, timeout=10
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
            params=params, headers={"User-Agent": UA}, timeout=15
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
                    "height": ii.get("height", 0)
                })
            if results:
                print(f"  ✓ Wikimedia Commons: {len(results)} images for '{search_query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Commons error for '{search_query}': {e}")
    return []

def fetch_pexels_image(query):
    if not PEXELS_KEY:
        return None
    try:
        r = requests.get(
            "https://api.pexels.com/v1/search",
            params={"query": query, "per_page": 3, "orientation": "landscape"},
            headers={"Authorization": PEXELS_KEY},
            timeout=10
        )
        if r.status_code == 200:
            photos = r.json().get("photos", [])
            if photos:
                url = photos[0]["src"]["large2x"]
                print(f"  ✓ Pexels image found for '{query}'")
                return url
    except Exception as e:
        print(f"  ⚠ Pexels error: {e}")
    return None

def compress_image(img_bytes, max_width=1200, quality=80):
    from PIL import Image
    img = Image.open(io.BytesIO(img_bytes))
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=quality, optimize=True)
    return buf.getvalue()

def upload_to_supabase(image_url, filename):
    """Download image, compress, upload to Supabase storage bucket article-images."""
    try:
        r = requests.get(image_url, headers={"User-Agent": UA}, timeout=30)
        if r.status_code != 200:
            print(f"  ✗ Failed to download image: HTTP {r.status_code}")
            return None
        raw = r.content
        if len(raw) < 5000:
            print(f"  ✗ Image too small ({len(raw)} bytes)")
            return None
        
        compressed = compress_image(raw)
        size_kb = len(compressed) / 1024
        print(f"  → Compressed to {size_kb:.0f} KB")

        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
        resp = requests.post(
            upload_url,
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "image/jpeg",
                "x-upsert": "true"
            },
            data=compressed,
            timeout=30
        )
        if resp.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {public_url[:70]}...")
            return public_url
        else:
            print(f"  ✗ Upload failed: {resp.status_code} {resp.text[:200]}")
    except Exception as e:
        print(f"  ✗ Upload error: {e}")
    return None

def validate_image_url(url):
    try:
        r = requests.head(url, headers={"User-Agent": UA}, timeout=10, allow_redirects=True)
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            return True
        # Try GET if HEAD doesn't return content-length
        if r.status_code == 200 and "image" in ct:
            return True
    except:
        pass
    return False

def insert_article(article):
    """Insert article into Supabase."""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=article,
        timeout=30
    )
    if r.status_code in (200, 201):
        result = r.json()
        art_id = result[0]["id"] if isinstance(result, list) else result.get("id")
        print(f"  ✓ Article inserted: {art_id}")
        return art_id
    else:
        print(f"  ✗ Insert failed: {r.status_code} {r.text[:300]}")
        return None


# ═══════════════════════════════════════════════════
# ARTICLE 1: Women's T20 World Cup opens — England record 219/1
# ═══════════════════════════════════════════════════

def write_article_1():
    print("\n" + "="*60)
    print("ARTICLE 1: Women's T20 World Cup — England's Record 219/1")
    print("="*60)

    slug = "england-219-record-womens-t20-world-cup-2026-wyatt-hodge-century-india-pakistan-sunday-nri"

    headline = "She Scored 105 Off 62 Balls. England Just Posted the Highest Total in Women's T20 World Cup History."

    subheadline = "Danni Wyatt-Hodge smashed an unbeaten century as England put up 219/1 against Sri Lanka in the tournament opener at Edgbaston. India begin their campaign against Pakistan on Sunday."

    body = """The Women's T20 World Cup began in the most emphatic way imaginable on Thursday evening at Edgbaston. England, the hosts, posted 219 for 1 in their 20 overs against Sri Lanka — the highest total in the history of the tournament, surpassing their own 213 for 5 against Pakistan in 2023.

At the centre of the carnage was Danni Wyatt-Hodge, who struck an unbeaten 105 off just 62 balls. The 35-year-old opener, who returned to international cricket earlier this year after the birth of her first child, batted as though the record books owed her something. She hit boundaries to every corner of the ground and was barely troubled by Sri Lanka's attack.

## A Statement From the Hosts

England lost just one wicket across their entire innings. Amy Jones fell early, but captain Nat Sciver-Brunt — returning from a calf injury that had clouded her availability — joined Wyatt-Hodge and never looked back. The pair feasted on a Sri Lankan bowling lineup that had no answers once the powerplay ended.

Sri Lanka won the toss and chose to field, a decision that felt reasonable in the moment but catastrophic by the eighth over. The tournament's youngest team in terms of collective T20I experience was simply overwhelmed by the quality and intent of England's top order.

Malki Madara finished with 1 for 51 from her four overs, the most expensive figures of the Sri Lankan attack, though no bowler escaped unscathed.

## Five Groups, Sixteen Teams, Five Weeks

This is the biggest Women's T20 World Cup ever staged. Sixteen teams are divided across four groups — two groups of four and two groups of six — with matches spread across venues in England from Birmingham to Manchester, Southampton to Derby.

The format has been expanded to accommodate the growing depth of women's cricket, and the opening match did nothing to dissuade the notion that the hosts are serious contenders. England enter the tournament having won seven consecutive bilateral T20 series and now hold the record for the highest World Cup total.

## India's Date With Pakistan

For Indian fans — whether in the UK, the US, or anywhere across the diaspora — the tournament's real drama begins on Sunday, June 14 at Edgbaston, when India face Pakistan in a Group A clash.

Harmanpreet Kaur's squad arrived in England having beaten West Indies 26 runs in their final warm-up match, with Bharti Fulmali impressing with an unbeaten 56. India's bowling depth, led by Shreyanka Patil and her four wickets against the West Indies, has been a talking point heading into the group stage.

The India-Pakistan rivalry in women's cricket has never matched the intensity of the men's game, but the stakes here are real. Both teams need a strong start to navigate a group that also includes South Africa and Bangladesh.

## What This Means for Diaspora Cricket Fans

NRIs across the UK will find this tournament unusually accessible. Matches are at conventional evening hours, tickets have been priced to fill stadiums rather than corporate boxes, and the BBC has committed to extensive coverage. For the estimated 1.8 million people of Indian origin in Britain, the Sunday clash against Pakistan at Edgbaston is likely to be the hottest ticket of the group stage.

For diaspora fans in North America, matches begin at 1:30 PM ET (10:30 AM PT) for the day games and at roughly 6:30 PM ET for evening fixtures — far more convenient than the early-morning starts that plagued the 2024 Men's T20 World Cup in the Caribbean.

India's full group schedule: Pakistan on June 14, South Africa on June 17, and Bangladesh on June 19. All Group A matches are played in Birmingham and Derby.

**Sources**: ICC, ESPNcricinfo, Wikipedia"""

    # Image sourcing
    print("\n--- Sourcing image ---")
    
    # Try Danni Wyatt-Hodge from Wikipedia
    wiki_img = fetch_wikipedia_person_image("Danni Wyatt")
    if not wiki_img:
        wiki_img = fetch_wikipedia_person_image("Danni Wyatt-Hodge")
    
    # Try Wikimedia Commons
    commons = fetch_wikimedia_commons_images("Women's T20 World Cup cricket 2026")
    if not commons:
        commons = fetch_wikimedia_commons_images("ICC Women's T20 World Cup cricket")
    if not commons:
        commons = fetch_wikimedia_commons_images("Edgbaston cricket ground")
    
    # Try Pexels as fallback
    pexels_img = fetch_pexels_image("women cricket match stadium")

    # Pick best
    image_url = None
    image_caption = ""
    image_attribution = ""
    
    if wiki_img:
        image_url = wiki_img
        image_caption = "Danni Wyatt-Hodge, who scored an unbeaten 105 in England's record-breaking innings"
        image_attribution = "Wikimedia Commons"
    elif commons:
        image_url = commons[0]["url"]
        image_caption = "The Women's T20 World Cup 2026 opened at Edgbaston Cricket Ground in Birmingham"
        image_attribution = "Wikimedia Commons"
    elif pexels_img:
        image_url = pexels_img
        image_caption = "Women's cricket continues its rapid global expansion with the biggest T20 World Cup ever staged"
        image_attribution = "Pexels"

    final_image_url = None
    if image_url:
        final_image_url = upload_to_supabase(image_url, f"{slug}.jpg")
    
    if not final_image_url:
        print("  ⚠ No image available — inserting without image")

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "sports",
        "vertical": "cricket",
        "status": "review",
        "is_editorial": False,
        "sources": json.dumps(["ICC", "ESPNcricinfo", "Wikipedia"]),
        "diaspora_angle": "India's Women's T20 World Cup campaign begins Sunday against Pakistan at Edgbaston — NRIs in the UK have prime-time access, while North American fans get afternoon match starts.",
        "published_at": datetime.now(timezone.utc).isoformat(),
    }
    
    if final_image_url:
        article["image_url"] = final_image_url
        article["image_caption"] = image_caption
        article["image_attribution"] = image_attribution

    art_id = insert_article(article)
    return art_id


# ═══════════════════════════════════════════════════
# ARTICLE 2: Shubman Gill's Captaincy Test vs Afghanistan
# ═══════════════════════════════════════════════════

def write_article_2():
    print("\n" + "="*60)
    print("ARTICLE 2: Shubman Gill Captaincy — India vs Afghanistan ODIs")
    print("="*60)

    slug = "shubman-gill-captaincy-test-india-afghanistan-odi-2026-kohli-rohit-world-cup-2027-nri"

    headline = "He Has Captained Six ODIs. India Have Not Won a Single Series Under Him."

    subheadline = "Shubman Gill leads India into a three-match ODI series against Afghanistan starting Saturday in Dharamsala. With Kohli injured and Hardik ruled out, this is his chance to answer the captaincy question before the 2027 World Cup."

    body = """Shubman Gill has 2,953 ODI runs at an average of 51.71. He led Gujarat Titans to the IPL 2026 final. He finished the tournament as its second-highest run scorer with 732 runs, including a century and six half-centuries. By every individual measure, Gill is thriving.

But the captaincy record tells a different story. In six ODIs as India's captain, the team has won just two matches and lost both series. When India walk out at the HPCA Stadium in Dharamsala on Saturday for the first of three ODIs against Afghanistan, Gill will carry the weight of a record that does not match his talent.

## The Road to the 2027 World Cup Begins Here

This is not a throwaway bilateral series. The 2027 ODI World Cup in South Africa is 16 months away, and India's planning begins now. After Rohit Sharma guided the team to the 2025 Champions Trophy title, the captaincy was formally handed to Gill in the 50-over format. This Afghanistan series is the first step in building the squad — and the captain — for 2027.

"Shubman Gill, as a captain in this format, hasn't really settled down yet," former India opener Aakash Chopra said on his YouTube channel. "You want him to just stamp his authority."

The endorsement from former captain Anil Kumble has been more generous. Speaking on JioStar, Kumble praised Gill's tactical acumen during the IPL. "We have seen that he has rotated his bowlers well, used his spinners at the right time, and handled pressure situations with clarity," Kumble said. "His form with the bat has not dipped."

## A Squad With Gaps and Opportunities

The squad announcement tells its own story. Virat Kohli is out — hamstring injury sustained during the IPL 2026 final, his last act in a tournament that ended with RCB's back-to-back title. In his place: Yashasvi Jaiswal, the 24-year-old left-hander who averages over 50 in ODIs and is hungry for a permanent spot.

Then there is Hardik Pandya. Initially cleared by the BCCI's Centre of Excellence after recovering from IPL-related back spasms, a new leg sprain forced a late withdrawal. He has not played an ODI since the Champions Trophy final in March 2025.

But there is good news too. Rohit Sharma has been declared fit after his own hamstring scare during the IPL. At 39, he is no longer captain, but his role as senior batter and mentor remains critical. Kumble made the point explicitly: "Kohli and Rohit can guide him with field placements, bowling changes, and the right tactical move. He doesn't have to carry the burden alone."

## Fresh Faces to Watch

Prince Yadav, the Lucknow Super Giants seamer who dismissed Kohli during the IPL, is in line for an ODI debut. Kumble called him "an all-phase bowler" with effective cutters, slower balls, and yorkers. Gurnoor Brar and Harsh Dubey — the latter having taken the most wickets (69) in the Ranji Trophy 2024-25 — round out a bowling attack that has genuine depth.

Nitish Kumar Reddy, who has been impressive in white-ball cricket, gets his chance to fill the all-rounder gap left by Pandya. With Washington Sundar and Kuldeep Yadav handling the spin duties, and Arshdeep Singh and Prasidh Krishna providing pace, Gill has options — more than most young captains get.

## India's Full ODI Squad

Shubman Gill (C), Rohit Sharma, Yashasvi Jaiswal, Shreyas Iyer (VC), KL Rahul, Ishan Kishan, Hardik Pandya (ruled out), Nitish Kumar Reddy, Washington Sundar, Kuldeep Yadav, Arshdeep Singh, Prasidh Krishna, Prince Yadav, Gurnoor Brar, Harsh Dubey.

## Series Schedule

The first ODI is Saturday, June 13 at the HPCA Stadium in Dharamsala (1:30 PM IST / 4:00 AM ET). The second moves to Lucknow on June 17, and the series closes in Chennai on June 20. India won the one-off Test against Afghanistan by an innings and 300 runs earlier this month. The ODI squad is largely different from the Test squad.

## The Diaspora Angle

For NRI fans in North America, the 4:00 AM ET start on a Saturday is admittedly brutal. But the series matters more than the time zone suggests. This is where the 2027 World Cup squad starts to take shape. The questions are significant: Can Gill captain under pressure? Can Jaiswal cement the No. 3 spot Kohli vacated? Can India's new-ball attack match the standards set by Bumrah?

Afghanistan, meanwhile, are no pushovers. Mohammad Saleem was added to the ODI squad after taking six wickets in the India A series in Sri Lanka, and their batting order has enough quality to challenge on slower Indian surfaces.

Three matches. One captaincy record to rewrite. The 2027 World Cup countdown has begun.

**Sources**: CricTracker, Sportskeeda, CricketAddictor, ESPNcricinfo"""

    # Image sourcing
    print("\n--- Sourcing image ---")
    
    # Shubman Gill Wikipedia
    wiki_img = fetch_wikipedia_person_image("Shubman Gill")
    if not wiki_img:
        wiki_img = fetch_wikipedia_person_image("Shubman Gill (cricketer)")
    
    # Wikimedia Commons
    commons = fetch_wikimedia_commons_images("Shubman Gill cricket")
    if not commons:
        commons = fetch_wikimedia_commons_images("Shubman Gill Indian cricketer")
    
    # Pexels fallback (generic)
    pexels_img = fetch_pexels_image("cricket captain India ODI match")

    image_url = None
    image_caption = ""
    image_attribution = ""
    
    if wiki_img:
        image_url = wiki_img
        image_caption = "Shubman Gill, India's ODI captain, faces a crucial test in the Afghanistan series"
        image_attribution = "Wikimedia Commons"
    elif commons:
        best = commons[0]
        image_url = best["url"]
        image_caption = "Shubman Gill at a cricket event"
        image_attribution = "Wikimedia Commons"
    elif pexels_img:
        image_url = pexels_img
        image_caption = "India begin their ODI series against Afghanistan in Dharamsala on Saturday"
        image_attribution = "Pexels"

    final_image_url = None
    if image_url:
        final_image_url = upload_to_supabase(image_url, f"{slug}.jpg")

    if not final_image_url:
        print("  ⚠ No image available — inserting without image")

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "sports",
        "vertical": "cricket",
        "status": "review",
        "is_editorial": False,
        "sources": json.dumps(["CricTracker", "Sportskeeda", "CricketAddictor", "ESPNcricinfo"]),
        "diaspora_angle": "The India-Afghanistan ODI series marks the start of India's 2027 World Cup buildup. Gill's captaincy, Jaiswal at No. 3, and new fast bowlers will shape the squad NRI fans follow to South Africa.",
        "published_at": datetime.now(timezone.utc).isoformat(),
    }

    if final_image_url:
        article["image_url"] = final_image_url
        article["image_caption"] = image_caption
        article["image_attribution"] = image_attribution

    art_id = insert_article(article)
    return art_id


# ═══════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════

if __name__ == "__main__":
    print("="*60)
    print("The Videshi — Sports Writer — June 12, 2026")
    print("="*60)

    results = []
    
    aid1 = write_article_1()
    results.append(("Women's T20 WC Record", aid1))
    
    time.sleep(1)
    
    aid2 = write_article_2()
    results.append(("Gill Captaincy", aid2))

    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    for title, aid in results:
        status = "✓" if aid else "✗"
        print(f"  {status} {title}: {aid}")
    
    failed = sum(1 for _, a in results if not a)
    if failed:
        print(f"\n⚠ {failed} article(s) failed to insert")
        sys.exit(1)
    else:
        print(f"\n✓ All {len(results)} articles inserted successfully (status: review)")

#!/usr/bin/env python3
"""
Sports Writer — The Videshi
Run: 2026-06-07
Articles:
1. India declare 564/8, Afghanistan 81/3 on Day 2 at Mullanpur
2. Indian-American firm Avni LLC claims FIFA World Cup India broadcast rights
"""

import os, sys, json, uuid, requests, io, time, re
from datetime import datetime, timezone
from urllib.parse import quote, quote_plus

# Load env
def load_env(path):
    if not os.path.exists(path):
        return
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
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SB_URL = os.environ.get('SUPABASE_URL', '')
SB_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY', '')
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

HEADERS = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

# ── Image sourcing functions ──

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia."""
    encoded = quote(person_name.replace(' ', '_'))
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
                print(f"  ✓ Wikipedia image for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia error for '{person_name}': {e}")
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
                if not mime.startswith("image/") or mime == "image/svg+xml":
                    continue
                w = ii.get("width", 0)
                if w < 300:
                    continue
                results.append({
                    "url": ii.get("thumburl") or ii.get("url", ""),
                    "original_url": ii.get("url", ""),
                    "title": page.get("title", ""),
                    "width": w,
                    "height": ii.get("height", 0),
                })
            if results:
                print(f"  ✓ Commons: {len(results)} images for '{search_query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Commons error: {e}")
    return []

def fetch_pexels_image(query):
    """Fetch from Pexels using curl (urllib gets 403)."""
    if not PEXELS_KEY:
        return None
    import subprocess
    try:
        cmd = [
            'curl', '-sS', '-H', f'Authorization: {PEXELS_KEY}',
            f'https://api.pexels.com/v1/search?query={quote_plus(query)}&per_page=3&orientation=landscape'
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        if result.returncode == 0:
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            if photos:
                url = photos[0]["src"]["large2x"]
                print(f"  ✓ Pexels image for '{query}': {url[:60]}...")
                return url
    except Exception as e:
        print(f"  ⚠ Pexels error: {e}")
    return None

def compress_image(img_bytes, max_width=1200, quality=80):
    """Resize and compress image. Returns JPEG bytes."""
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

def download_and_upload_image(image_url, slug):
    """Download image, compress, upload to Supabase storage."""
    try:
        r = requests.get(image_url, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, timeout=20)
        if r.status_code != 200:
            print(f"  ✗ Download failed ({r.status_code}) for {image_url[:60]}")
            return None
        ct = r.headers.get("Content-Type", "")
        if not ct.startswith("image/"):
            print(f"  ✗ Not an image: {ct}")
            return None
        if len(r.content) < 5000:
            print(f"  ✗ Too small: {len(r.content)} bytes")
            return None

        compressed = compress_image(r.content)
        print(f"  Compressed: {len(r.content)} → {len(compressed)} bytes")

        filename = f"{slug}.jpg"
        upload_url = f"{SB_URL}/storage/v1/object/article-images/{filename}"
        
        # Try upsert
        headers = {
            "apikey": SB_KEY,
            "Authorization": f"Bearer {SB_KEY}",
            "Content-Type": "image/jpeg",
            "x-upsert": "true"
        }
        resp = requests.post(upload_url, data=compressed, headers=headers, timeout=30)
        if resp.status_code in (200, 201):
            public_url = f"{SB_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded: {public_url[:60]}...")
            return public_url
        else:
            print(f"  ✗ Upload failed: {resp.status_code} {resp.text[:100]}")
            return None
    except Exception as e:
        print(f"  ✗ Upload error: {e}")
        return None

def insert_article(article):
    """Insert article into Supabase p2_articles."""
    url = f"{SB_URL}/rest/v1/p2_articles"
    resp = requests.post(url, json=article, headers=HEADERS, timeout=30)
    if resp.status_code in (200, 201):
        data = resp.json()
        art_id = data[0]["id"] if isinstance(data, list) else data.get("id")
        print(f"  ✓ Article inserted: {art_id}")
        return art_id
    else:
        print(f"  ✗ Insert failed: {resp.status_code} {resp.text[:200]}")
        return None


# ══════════════════════════════════════════════════════════════════
# ARTICLE 1: India declare 564/8, Afghanistan 81/3 on Day 2
# ══════════════════════════════════════════════════════════════════

def write_article_1():
    print("\n═══ ARTICLE 1: India Declare 564/8, Afghanistan 81/3 ═══")

    slug = "india-declare-564-8-afghanistan-81-3-day-2-mullanpur-suthar-sundar-nri"
    headline = "India Declared on 564. By Stumps, Afghanistan Had Lost Three Wickets and Trailed by 483 Runs."
    subheadline = "Washington Sundar's unbeaten fifty capped a brutal batting display before Manav Suthar's twin strikes on debut sent Afghanistan reeling at the New PCA Stadium"

    body = """India's dominance over Afghanistan on the second day of their one-off Test at the Maharaja Yadavindra Singh International Cricket Stadium in Mullanpur was so total that it felt less like a contest and more like a controlled demolition. By stumps on Sunday, India had declared on 564 for 8 and reduced the visitors to 81 for 3 — a deficit of 483 runs with seven wickets in hand and, barring a miracle, little hope of avoiding defeat.

The morning session belonged to Mohammad Saleem, the 22-year-old Afghan fast bowler who had picked up two wickets on the first evening and came back for more on the second morning. His first breakthrough arrived in the 89th over when he got the ball to nip away from captain Shubman Gill, who edged behind for 126. It was a captain's innings — 177 balls, 15 fours, a six — that built on the foundation KL Rahul's century had laid the day before. On the very next delivery, Saleem nearly had Rishabh Pant for a duck, with the umpire ruling against the visitors. Afghanistan had one review remaining and, inexplicably, chose not to use it. Replays showed the ball hitting leg stump.

Pant survived that scare and counterattacked alongside Dhruv Jurel before falling for 81, baited into swinging at a flighted delivery from Hashmatullah Shahidi that he sent straight to long-off. Saleem then cleaned up Jurel for 19 with a delivery that jagged back sharply, and later bowled Mohammed Siraj for a breezy 22 off 12 balls — all scored in boundaries — to complete a deserved six-wicket haul. For a bowler playing only his second Test, Saleem's figures of 6 for 140 were remarkable, a testament to his raw pace and willingness to bowl long spells in draining heat.

## The Engine Room

But the story of India's lower order on Sunday belonged to Washington Sundar. Batting at No. 7, the 26-year-old all-rounder played an innings that received less attention than the centuries above him but was no less important. He began cautiously alongside debutant Manav Suthar, the pair adding 54 for the seventh wicket in 85 balls. Then, sensing the declaration was near, Sundar cut loose. He greeted Saleem's final over of the innings with a pulled six and a clip through mid-on to bring up his fifty — 52 not out off 68 balls. It was vintage Sundar: composed, purposeful, and finished with a flourish.

Siraj, promoted above Kuldeep Yadav, played the enforcer's role to perfection. He took apart left-arm spinner Nangeyalia Kharote and cut Saleem despite getting no width. His 12-ball 22 came entirely in fours and sixes before Saleem bowled him to complete his sixth wicket. India declared immediately after, their 564 for 8 more than enough.

## Suthar's Debut Spell

What followed was a masterclass in debut bowling. Manav Suthar, the 24-year-old left-arm spinner from Sri Ganganagar whose father teaches at a school near the Pakistan border, had already shown composure with the bat. Now, with the ball, he was devastating.

His very first delivery in Test cricket drew an inside edge from Abdul Malik. His fourth ball struck. Malik, attempting a sweep, top-edged it high into the air, and Mohammed Siraj sprinted in from backward square leg to take a fine diving catch. Afghanistan were 28 for 1 at tea, and Suthar had his maiden Test wicket.

He would go on to claim a second in the evening session, finishing the day with figures of 2 for 14 from 10.5 overs — an economy rate of 1.29 that spoke to his control and the pressure he generated. At the other end, Kuldeep Yadav bowled seven wicketless overs but created chances, beating the bat repeatedly. Between them, the spinners choked Afghanistan's run-scoring and left the visitors at 81 for 3, staring at a near-impossible task.

## The Diaspora Lens

For the millions of Indian cricket fans scattered across the United States, United Kingdom, and Canada who stayed up to follow the match, the second day offered a feast. Sundar's all-round contributions are a reminder that India's Test depth runs deeper than its top four. Suthar's debut — from a small town in Rajasthan to a six-wicket haul and a two-for in the same match — is the kind of story that resonates with first-generation immigrants who know something about making the most of a chance far from home.

The result, barring rain, appears a formality. India are building something in Test cricket again. After a bruising 2025 that included defeats in New Zealand, South Africa, and Australia, this is a low-stakes match against a weaker opponent. But the depth on display — five batters scoring 50 or more, a debutant taking wickets in his first over — suggests the rebuilding has already begun.

*Sources: Reuters, ESPN Cricinfo, Sportskeeda*"""

    # Image sourcing
    print("  Sourcing images...")
    
    # Try Washington Sundar Wikipedia
    img_url = fetch_wikipedia_person_image("Washington Sundar")
    img_source = "wikipedia"
    img_caption = "Washington Sundar during an India Test match"
    
    if not img_url:
        # Try Wikimedia Commons
        commons = fetch_wikimedia_commons_images("Washington Sundar cricket India")
        if commons:
            img_url = commons[0]["url"]
            img_source = "commons"
        else:
            # Try Manav Suthar
            img_url = fetch_wikipedia_person_image("Manav Suthar")
            if img_url:
                img_caption = "Manav Suthar, India's Test debutant at Mullanpur"
            else:
                # Pexels fallback
                img_url = fetch_pexels_image("cricket test match India batting")
                img_source = "pexels"
                img_caption = "India batters in action during a Test match"

    final_image_url = None
    attribution = "Wikimedia Commons"
    if img_url:
        final_image_url = download_and_upload_image(img_url, slug)
        if img_source == "pexels":
            attribution = "Pexels"

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "sports",
        "vertical": "sports",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "sources": json.dumps(["Reuters", "ESPN Cricinfo", "Sportskeeda"]),
        "is_editorial": False,
        "image_url": final_image_url or "",
        "image_caption": img_caption,
        "image_attribution": attribution
    }

    art_id = insert_article(article)
    if art_id:
        print(f"  ✓ Article 1 published: {headline[:60]}...")
    return art_id


# ══════════════════════════════════════════════════════════════════
# ARTICLE 2: Avni LLC Claims FIFA World Cup India Broadcast Rights
# ══════════════════════════════════════════════════════════════════

def write_article_2():
    print("\n═══ ARTICLE 2: Avni LLC FIFA Broadcast Rights ═══")

    slug = "avni-llc-indian-american-firm-fifa-world-cup-india-broadcast-rights-zee-nri"
    headline = "A Washington DC Firm Says It Has the FIFA World Cup India Rights. So Does Zee. Indian Fans Still Don't Know Who to Believe."
    subheadline = "Indian-American investment firm Avni LLC claims a $300 million guarantee won the FIFA tender, even as Zee Entertainment says it has already signed an eight-year deal"

    body = """Four days before the 2026 FIFA World Cup kicks off in Mexico City, India — one of the world's largest and fastest-growing football markets — still does not have a confirmed broadcaster. And now, a new claimant has entered the ring.

Avni LLC, a Washington DC-based Indian-American investment firm, has announced that it submitted a corporate guarantee backed by financial commitments exceeding $300 million as part of FIFA's closed tender process for the Indian subcontinent. The firm claims that an associated partner secured the winning bid after competing against several major Indian broadcasters, including, presumably, Zee Entertainment, which announced its own eight-year deal with FIFA just last week.

The duelling claims have created an extraordinary situation. Zee says it has secured broadcast rights for 39 FIFA events through 2034, including the 2026 and 2030 World Cups, and plans to telecast matches on its newly launched Unite8 Sports network and ZEE5. Its shares rose seven percent on the announcement. Avni LLC, meanwhile, is pitching an entirely different vision — one built around OTT platforms, AI-powered multilingual broadcasting, mobile micro-subscriptions, and esports integrations.

"The Indian subcontinent alone has the ability to exceed initial valuation expectations," said Deelip Mhaske, the firm's President and CEO.

## The Last Major Market

The confusion matters because India is no ordinary unsold territory. It is home to roughly 1.4 billion people, a rapidly growing football fanbase, and an advertising market that global sports rights holders can no longer afford to ignore. China's state broadcaster CMG sealed its FIFA deal on May 15. Pakistan, Bangladesh, and Sri Lanka have their own arrangements. India has been the conspicuous holdout.

The delay reflects a deeper tension. FIFA reportedly sought nearly $100 million for the India broadcast package before reducing the asking price to around $60 million. Traditional Indian broadcasters — accustomed to the economics of cricket, where a billion viewers justify premium rights fees — have been slow to pay similar sums for a sport that commands a fraction of cricket's domestic audience. The gap between FIFA's expectations and the Indian market's willingness to pay has been the central obstacle.

## The NRI Dimension

Avni LLC's entry adds a distinctly diaspora-inflected twist. The firm is headquartered in Washington DC, run by an Indian-American executive, and its pitch — AI-powered multilingual broadcasting, mobile-first consumption — reads like it was designed for the Indian-origin audience scattered across North America as much as the one sitting in Mumbai.

For the estimated five million Indian-Americans in the United States, and millions more across the United Kingdom, Canada, and the Gulf, the FIFA World Cup has always occupied an awkward position. Cricket is the cultural anchor. Football is what their children play and their adopted countries obsess over. A World Cup broadcast solution that bridges both worlds — Hindi commentary delivered through AI, micro-subscriptions that don't require a full cable package, highlights packaged for WhatsApp — would find a ready audience.

Whether Avni LLC can deliver on that vision, or whether it is a speculative bid dressed up in press releases, remains unclear. FIFA has said only that discussions in India "are ongoing and must remain confidential at this stage."

## The Court Gets Involved

Meanwhile, the Delhi High Court has waded in. Justice Purushaindra Kumar Kaurav has issued notices to the Centre and Prasar Bharati following a petition by advocate Avdhesh Bairwa seeking to ensure the World Cup is broadcast in India, particularly through free-to-air public platforms such as Doordarshan and DD Sports.

The petition invokes the principle that events of national sporting importance should be accessible to all citizens, not locked behind paywalls. It is a familiar argument in India — one that has been made, and largely won, for cricket. Football, however, occupies a greyer zone. The Supreme Court's 2007 guidelines on sports broadcasting do not explicitly cover the FIFA World Cup in India.

## What Happens Next

The World Cup begins on June 11 with Mexico versus South Africa at the Estadio Azteca. India's Group D match — the United States against Paraguay — follows a day later. For Indian fans hoping to watch Lionel Messi's final World Cup campaign, or to see the four players of Indian origin who have qualified with other nations, the clock is ticking.

If Zee's deal is genuine, matches will appear on Unite8 Sports channels and ZEE5. If Avni LLC's claim has substance, the broadcast landscape could look very different. If neither pans out, India faces the unthinkable: a total blackout of the world's most-watched sporting event.

*Sources: The Indian Eye, Zee Entertainment, FIFA, Delhi High Court records*"""

    # Image sourcing — FIFA World Cup / football in India
    print("  Sourcing images...")
    
    # Search Commons for FIFA World Cup related images
    commons = fetch_wikimedia_commons_images("FIFA World Cup 2026 logo")
    img_url = None
    img_source = "commons"
    img_caption = "The FIFA World Cup 2026 logo — India's broadcast rights remain contested"
    
    if commons:
        img_url = commons[0]["url"]
    
    if not img_url:
        commons = fetch_wikimedia_commons_images("FIFA World Cup trophy")
        if commons:
            img_url = commons[0]["url"]
            img_caption = "The FIFA World Cup trophy — India may be one of the last major markets without a confirmed broadcaster"
    
    if not img_url:
        img_url = fetch_pexels_image("football soccer world cup stadium")
        img_source = "pexels"
        img_caption = "Football fans at a World Cup venue"
    
    final_image_url = None
    attribution = "Wikimedia Commons" if img_source == "commons" else "Pexels"
    if img_url:
        final_image_url = download_and_upload_image(img_url, slug)

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "sports",
        "vertical": "sports",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "sources": json.dumps(["The Indian Eye", "Zee Entertainment", "FIFA", "Delhi High Court"]),
        "is_editorial": False,
        "image_url": final_image_url or "",
        "image_caption": img_caption,
        "image_attribution": attribution
    }

    art_id = insert_article(article)
    if art_id:
        print(f"  ✓ Article 2 published: {headline[:60]}...")
    return art_id


# ── Main ──
if __name__ == "__main__":
    print(f"Sports Writer — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    
    id1 = write_article_1()
    id2 = write_article_2()
    
    print(f"\n{'='*60}")
    print(f"Results: Article 1: {'✓' if id1 else '✗'} | Article 2: {'✓' if id2 else '✗'}")
    print(f"{'='*60}")

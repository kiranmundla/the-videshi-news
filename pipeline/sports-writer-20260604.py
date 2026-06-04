#!/usr/bin/env python3
"""Sports writer for The Videshi — 2026-06-04 batch"""

import json, os, sys, time, uuid, re, requests, urllib.parse
from datetime import datetime, timezone

# Load env
def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

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
        "iiprop": "url|size|mime",
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
            for page_id, page_data in pages.items():
                imageinfo = page_data.get("imageinfo", [{}])[0]
                url = imageinfo.get("thumburl") or imageinfo.get("url")
                mime = imageinfo.get("mime", "")
                if url and mime.startswith("image/") and "svg" not in mime:
                    results.append({
                        "url": url,
                        "title": page_data.get("title", ""),
                        "width": imageinfo.get("thumbwidth", imageinfo.get("width", 0)),
                        "height": imageinfo.get("thumbheight", imageinfo.get("height", 0))
                    })
            if results:
                print(f"  ✓ Wikimedia Commons found {len(results)} images for '{search_query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Wikimedia Commons error for '{search_query}': {e}")
    return []

def fetch_pexels_image(query):
    """Search Pexels for an image. Returns URL or None."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None, None
    try:
        import subprocess
        result = subprocess.run(
            ["curl", "-sS", f"https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page=5",
             "-H", f"Authorization: {PEXELS_KEY}"],
            capture_output=True, text=True, timeout=15
        )
        data = json.loads(result.stdout)
        photos = data.get("photos", [])
        for photo in photos:
            url = photo.get("src", {}).get("large2x") or photo.get("src", {}).get("large")
            if url:
                print(f"  ✓ Pexels image found for '{query}': {url[:80]}...")
                return url, photo.get("photographer", "Pexels")
    except Exception as e:
        print(f"  ⚠ Pexels error for '{query}': {e}")
    return None, None

def validate_image(url):
    """Validate image URL returns 200 with image content and > 5KB."""
    try:
        r = requests.head(url, headers={"User-Agent": "TheVideshi/1.0"}, timeout=10, allow_redirects=True)
        content_type = r.headers.get("Content-Type", "")
        content_length = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in content_type and content_length > 5000:
            print(f"  ✓ Image validated: {content_length} bytes, {content_type}")
            return True
        # Try GET if HEAD doesn't return content-length
        if r.status_code == 200 and "image" in content_type and content_length == 0:
            r2 = requests.get(url, headers={"User-Agent": "TheVideshi/1.0"}, timeout=10, stream=True)
            size = 0
            for chunk in r2.iter_content(8192):
                size += len(chunk)
                if size > 5000:
                    print(f"  ✓ Image validated via GET: >{size} bytes")
                    return True
    except Exception as e:
        print(f"  ⚠ Image validation error: {e}")
    return False

def source_image(person_name=None, wiki_search=None, pexels_query=None):
    """Multi-source image search: Wikipedia person → Wikimedia Commons → Pexels"""
    best_url = None
    attribution = None
    caption = None

    # 1. Wikipedia person image
    if person_name:
        url = fetch_wikipedia_person_image(person_name)
        if url and validate_image(url):
            return url, "Wikimedia Commons", f"{person_name}"

    # 2. Wikimedia Commons search
    if wiki_search:
        results = fetch_wikimedia_commons_images(wiki_search)
        for r in results:
            if r["url"] and validate_image(r["url"]):
                return r["url"], "Wikimedia Commons", r["title"].replace("File:", "").rsplit(".", 1)[0]

    # 3. Pexels fallback
    if pexels_query:
        url, photographer = fetch_pexels_image(pexels_query)
        if url and validate_image(url):
            return url, f"Pexels / {photographer}" if photographer else "Pexels", pexels_query

    return None, None, None

def insert_article(article):
    """Insert article into Supabase."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")
    payload = {
        "headline": article["headline"],
        "subheadline": article["subheadline"],
        "slug": article["slug"],
        "body": article["body"],
        "category": "sports",
        "vertical": "sports",
        "image_url": article.get("image_url"),
        "image_caption": article.get("image_caption"),
        "image_attribution": article.get("image_attribution"),
        "sources": json.dumps(article.get("sources", [])),
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "created_at": now,
        "updated_at": now
    }

    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=payload,
        timeout=15
    )
    if r.status_code in (200, 201):
        data = r.json()
        aid = data[0]["id"] if isinstance(data, list) and data else "unknown"
        print(f"  ✓ Published: '{article['headline']}' (id: {aid})")
        return True
    else:
        print(f"  ✗ Failed to publish: {r.status_code} — {r.text[:300]}")
        return False

# ─────────────────────────────────────────────────────────
# ARTICLE 1: Ayush Shetty's Comeback at Indonesia Open
# ─────────────────────────────────────────────────────────
def write_ayush_shetty_article():
    print("\n=== Article 1: Ayush Shetty Indonesia Open ===")

    image_url, image_attr, image_cap = source_image(
        person_name="Ayush Shetty (badminton)",
        wiki_search="Indonesia Open badminton 2026 Istora Senayan",
        pexels_query="badminton player smash court"
    )

    article = {
        "headline": "He Lost the First Game 8-21. Forty Minutes Later, Ayush Shetty Was the Last Indian Man Standing in Jakarta.",
        "subheadline": "The 20-year-old from Mangaluru rallied from a one-sided opening loss to stun China's world No. 15, keeping India's men's singles hopes alive at the Indonesia Open after Lakshya, Srikanth, and Prannoy all exited early.",
        "slug": "ayush-shetty-comeback-indonesia-open-2026-last-indian-man-singles-nri",
        "body": """When the first game ended at the Istora Senayan on Tuesday — 8-21, over in a blink — Ayush Shetty looked like the fourth Indian man in three days to pack his bags in Jakarta. China's Weng Hong Yang, ranked 15th in the world, had dismantled him with cross-court smashes and aggressive net play that left the Indian retrieving rather than attacking.

What happened next was the kind of reversal that makes a career.

## The Turnaround Nobody Expected

Trailing in the second game and seemingly headed for a straight-games exit, Shetty made a tactical adjustment that shifted the entire match. He began extending rallies, using the drift in the arena to his advantage, and forced Weng into the kind of long exchanges the Chinese shuttler had been avoiding.

At 15-20 in the second game, with match point looming, Shetty held his nerve. He saved the first match point, then the second, then clawed back to 20-20. The 22-20 second-game win was not just a rescue act — it was a declaration.

The decider was no contest. Shetty dictated from the start, mixing drops with deep smashes, racing to a 21-15 victory in 66 minutes that announced his arrival at the Super 1000 level.

## The Weight on His Shoulders

Shetty's win carried significance beyond the scoreline. By the time he walked onto court, India's men's singles campaign at the Indonesia Open had already suffered three blows. Lakshya Sen, the highest-ranked Indian man in the draw, lost in the first round. Kidambi Srikanth followed him out. Then HS Prannoy, who has made a career of performing at major events, fell to Ireland's Nhat Nguyen 17-21, 21-16, 19-21 in a match that could have gone either way.

That left Shetty — the 20-year-old Asian Championships silver medallist from Mangaluru — as the sole surviving Indian in men's singles. He will face Hong Kong's Lee Cheuk Yiu in the pre-quarterfinals.

## Bright Spots Elsewhere

The day was not entirely bleak for India. In mixed doubles, Rohan Kapoor and Ruthvika Gadde delivered one of the most convincing wins of the round, beating Chinese Taipei's Yang Po Hsuan and Hu Ling Fang 21-14, 21-14 in just 36 minutes. They will next face France's fourth-seeded Thom Gicquel and Delphine Delrue.

PV Sindhu, meanwhile, remains in the women's singles draw and faces a massive test — a Round of 16 clash against world No. 1 An Se Young, the player who has beaten her nine consecutive times.

## The Satwik-Chirag Concern

The most worrying development came in men's doubles, where Satwiksairaj Rankireddy and Chirag Shetty — fresh off their Singapore Open title win just six days ago — were forced to retire from their opening match after barely seven minutes. Trailing 6-11 against Malaysia's Aaron Tai and Kang Khai Xing, Satwik pointed to his shoulder and signalled discomfort, the same shoulder that has troubled him intermittently throughout the season.

For India's premier doubles pair, the timing could not be worse. The Commonwealth Games and Asian Games are months away, and a recurring shoulder injury for Satwik raises questions about their ability to sustain a full calendar of Super 1000 events.

## What It Means for NRI Fans

For the diaspora following Indian badminton's fortunes, the Indonesia Open has crystallised a generational question. The old guard — Srikanth at 33, Prannoy at 33 — are finding it harder to compete at the Super 1000 level. Lakshya Sen, once seen as the future, has been inconsistent. The burden is shifting to a new cohort, and Ayush Shetty's comeback in Jakarta suggests the next chapter may already be writing itself.

He plays Lee Cheuk Yiu next. If Tuesday was anything to go by, writing him off early would be unwise.

**Sources:** Badminton World Federation; RevSportz; ESPN India""",
        "sources": ["Badminton World Federation", "RevSportz", "ESPN India"],
        "image_url": image_url,
        "image_caption": image_cap or "Ayush Shetty in action at the Indonesia Open 2026",
        "image_attribution": image_attr or "Wikimedia Commons"
    }

    if not article["image_url"]:
        print("  ⚠ No image found, trying broader search...")
        image_url, image_attr, _ = source_image(
            wiki_search="Istora Senayan badminton stadium Jakarta",
            pexels_query="badminton court competition"
        )
        if image_url:
            article["image_url"] = image_url
            article["image_caption"] = "Istora Senayan in Jakarta, venue for the Indonesia Open 2026"
            article["image_attribution"] = image_attr

    return insert_article(article)

# ─────────────────────────────────────────────────────────
# ARTICLE 2: India A Tri-Series with Sooryavanshi
# ─────────────────────────────────────────────────────────
def write_india_a_tri_series_article():
    print("\n=== Article 2: India A Tri-Series in Sri Lanka ===")

    image_url, image_attr, image_cap = source_image(
        person_name="Vaibhav Sooryavanshi",
        wiki_search="Vaibhav Sooryavanshi cricket IPL 2026",
        pexels_query="cricket batsman stadium"
    )

    article = {
        "headline": "Sooryavanshi, Tilak, and Gaikwad Board the Plane to Dambulla. India A's Tri-Series Is the World Cup Audition Nobody Is Calling an Audition.",
        "subheadline": "A 15-player squad led by Tilak Varma leaves for Sri Lanka next week for a seven-match ODI tri-series against Sri Lanka A and Afghanistan A — and at least half the names on the list are playing for a senior spot in 2027.",
        "slug": "india-a-tri-series-sri-lanka-2026-sooryavanshi-tilak-varma-gaikwad-world-cup-audition-nri",
        "body": """The Board of Control for Cricket in India has named a 15-member India A squad for the ODI tri-series in Sri Lanka that begins on June 9 in Dambulla. On paper, it is a development tour. In practice, it is the first real audition for the 2027 ODI World Cup, and the selectors have stacked the cast accordingly.

Tilak Varma, the 23-year-old left-hander who has already played 14 ODIs for India, will captain the side. Ruturaj Gaikwad, the Chennai Super Kings stalwart who has been on the fringes of the senior ODI squad for two years, is his deputy. And then there is the name that will generate the most conversation: Vaibhav Sooryavanshi.

## The Sooryavanshi Question

Three months ago, Sooryavanshi was a 15-year-old schoolboy who happened to play domestic cricket for Madhya Pradesh. Then the IPL happened.

In a season where he swept all five individual awards — the Orange Cap with 776 runs, the MVP award, the Emerging Player of the Season, the Super Striker award with a strike rate of 237.30, and the record for most sixes in a single season at 72, breaking Chris Gayle's long-standing mark — Sooryavanshi did not just announce himself. He redefined what was possible for a teenager in professional cricket.

Now he is in an India A squad, on his way to his first overseas assignment. The tri-series in Dambulla will test him on slow, turning pitches against unfamiliar bowling attacks — conditions that reward patience and tactical awareness rather than raw power. It is a different kind of examination from the one he passed in the IPL.

## The Full Squad

The rest of the 15 tells its own story. Priyansh Arya and Ayush Badoni, both of whom have been prolific in domestic cricket, will compete for batting spots. Nishant Sindhu and Suryansh Shedge add left-arm spin and power-hitting options. Prabhsimran Singh and Kumar Kushagra share wicketkeeping duties.

The bowling attack features Vipraj Nigam, the left-arm wrist spinner, alongside pace options in Yash Thakur, Yudhvir Singh, Anshul Kamboj, Arshad Khan, and Anukul Roy.

**India A squad:** Tilak Varma (C), Ruturaj Gaikwad (VC), Priyansh Arya, Vaibhav Sooryavanshi, Ayush Badoni, Nishant Sindhu, Suryansh Shedge, Prabhsimran Singh (WK), Kumar Kushagra (WK), Vipraj Nigam, Yash Thakur, Yudhvir Singh, Anshul Kamboj, Arshad Khan, Anukul Roy.

## The Schedule

The tri-series runs from June 9 to June 21, with all seven matches played at the Rangiri Dambulla International Stadium. India A face Sri Lanka A first, then Afghanistan A on June 11, before the round-robin continues through a final on June 21.

Sri Lanka A, captained by Sahan Arachchige with Niroshan Dickwella as vice-captain, bring experienced domestic performers including Avishka Fernando and Chamika Karunaratne. Afghanistan A, led by Darwish Rasooli, include several players who have represented the senior team in bilateral series.

## Why NRI Fans Should Watch

For the diaspora, the subtext is hard to miss. India's 2027 World Cup planning has officially begun, and the selectors are using every available window to test their options. The senior squad is in India playing Afghanistan. The A team is in Sri Lanka running a parallel evaluation.

At least five or six players from this India A squad — Tilak Varma, Gaikwad, Sooryavanshi, Badoni, Vipraj Nigam — have realistic paths to the senior ODI team within the next 12 months. How they perform against quality opposition in overseas conditions will carry weight when Ajit Agarkar's selection committee meets later this year.

The matches will be streamed on SonyLiv in India. For NRI fans, the series represents a chance to see the next generation of Indian cricket stars before they become household names.

**Sources:** CricTracker; Sports Yaari; The Indian EYE""",
        "sources": ["CricTracker", "Sports Yaari", "The Indian EYE"],
        "image_url": image_url,
        "image_caption": image_cap or "Vaibhav Sooryavanshi selected for India A's tri-series in Sri Lanka",
        "image_attribution": image_attr or "Wikimedia Commons"
    }

    if not article["image_url"]:
        print("  ⚠ No image found, trying Tilak Varma or cricket grounds...")
        image_url, image_attr, _ = source_image(
            person_name="Tilak Varma",
            wiki_search="Rangiri Dambulla cricket stadium Sri Lanka",
            pexels_query="cricket stadium Sri Lanka"
        )
        if image_url:
            article["image_url"] = image_url
            article["image_caption"] = "Tilak Varma will captain India A in the Sri Lanka tri-series"
            article["image_attribution"] = image_attr

    return insert_article(article)

# ─────────────────────────────────────────────────────────
# ARTICLE 3: SAFF Women's Final Preview
# ─────────────────────────────────────────────────────────
def write_saff_women_final_article():
    print("\n=== Article 3: SAFF Women's Final Preview ===")

    image_url, image_attr, image_cap = source_image(
        wiki_search="India women's national football team 2026",
        pexels_query="women football team celebration"
    )

    article = {
        "headline": "India Beat Bangladesh 3-0 in the Group Stage. They Meet Again on Friday in Goa. This Time, the Trophy Is on the Line.",
        "subheadline": "The Blue Tigresses face defending champions Bangladesh in the SAFF Women's Championship final on June 6 in Margao, seeking their sixth title at home after a semifinal scare against Bhutan.",
        "slug": "india-bangladesh-saff-women-championship-final-2026-goa-blue-tigresses-preview-nri",
        "body": """When India and Bangladesh walk out at the Pandit Jawaharlal Nehru Stadium in Margao on Friday evening, it will be the second time in six days that these two teams have faced each other. The first meeting, on May 31, ended 3-0 to India. The context was different — that was a group stage fixture with both teams already through to the semifinals. Friday is the final.

The SAFF Women's Championship trophy is on the line, and for the Blue Tigresses, there is a record to protect.

## The Road to the Final

India's path to the title match has been dominant in stretches and uncomfortable in others. They opened with an 11-0 demolition of Maldives that saw Aveka Singh score four goals and provide two assists, Priyangka Devi Naorem mark her return from an ACL injury with a brace, and Karishma Shirvoikar add two more. It was the kind of performance that makes you forget the opposition.

The Bangladesh group match — a 3-0 win — was more controlled but still convincing. India dictated play, created chances at will, and never looked troubled.

Then came the semifinal against Bhutan, and the narrative shifted.

## The Bhutan Scare

India were expected to cruise past Bhutan in Wednesday's semi. Instead, they spent 57 frustrating minutes unable to break down a side that sat deep, defended in numbers, and showed no interest in engaging in open play. The Istora Senayan crowd — small but vocal — grew restless as chance after chance went begging.

Sanfida Nongrum's 58th-minute goal was the only breakthrough. India won 1-0, but head coach Crispin Chettri would have noted the warning signs. Against a team with nothing to lose and everything to defend, India's creative players struggled to find the final pass.

Bangladesh, to their credit, navigated their own semifinal test. They beat Nepal 2-1 in the other semi, showing the kind of resilience under pressure that won them the title last time around.

## The Key Matchups

India's strength lies in their attacking depth. Aveka Singh, who leads the tournament in goal contributions, operates between the lines with a combination of movement, vision, and finishing that Bangladesh will need to contain. Priyangka Devi Naorem, playing her first major tournament since her ACL reconstruction, has added pace and directness to the left side of India's attack.

In midfield, Sangita Basfore provides the engine room that allows India's forwards to roam. Her work rate off the ball — pressing, intercepting, recycling possession — is often overlooked but critical to how this team functions.

Bangladesh's danger comes from set pieces and transitions. In the group stage, they created their best chances on the counter, and their aerial presence from corners troubled India's defence briefly before the hosts reasserted control.

## What Is at Stake

For India, a sixth SAFF Women's Championship title would underline their dominance in the region. But Chettri has spoken repeatedly about using this tournament to prepare for bigger challenges — the Asian Games later this year and the pathway to the Women's Asian Cup.

For NRI fans, the final represents something broader: the continued growth of women's football in India. The squad includes players from domestic clubs, I-League teams, and — in Manisha Kalyan — a player who competes professionally in Peru's top flight with Alianza Lima. The diversity of backgrounds reflects a sport that is expanding its reach across the country.

The match kicks off at 18:30 IST on Friday, June 6, at the Pandit Jawaharlal Nehru Stadium in Margao, Goa. It will be streamed live on FanCode. Entry is free.

**Sources:** All India Football Federation (AIFF); FanCode; ESPN India""",
        "sources": ["All India Football Federation (AIFF)", "FanCode", "ESPN India"],
        "image_url": image_url,
        "image_caption": image_cap or "India women's football team during the SAFF Championship 2026 in Goa",
        "image_attribution": image_attr or "Wikimedia Commons"
    }

    if not article["image_url"]:
        print("  ⚠ No image found, trying broader search...")
        image_url, image_attr, _ = source_image(
            wiki_search="Pandit Jawaharlal Nehru Stadium Margao Goa football",
            pexels_query="women soccer football match"
        )
        if image_url:
            article["image_url"] = image_url
            article["image_caption"] = "Pandit Jawaharlal Nehru Stadium in Margao, venue for the SAFF final"
            article["image_attribution"] = image_attr

    return insert_article(article)

# ─────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"Sports Writer — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 60)

    results = []
    results.append(("Ayush Shetty Indonesia Open", write_ayush_shetty_article()))
    results.append(("India A Tri-Series Sri Lanka", write_india_a_tri_series_article()))
    results.append(("SAFF Women's Final Preview", write_saff_women_final_article()))

    print("\n" + "=" * 60)
    print("SUMMARY")
    for name, success in results:
        status = "✓ Published" if success else "✗ Failed"
        print(f"  {status}: {name}")
    
    failures = sum(1 for _, s in results if not s)
    if failures:
        print(f"\n⚠ {failures} article(s) failed")
        sys.exit(1)
    else:
        print(f"\n✓ All {len(results)} articles published successfully")

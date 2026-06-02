#!/usr/bin/env python3
"""
Sports writer for The Videshi — 2026-06-02 batch
Articles:
1. Indonesia Open Day 1: Sindhu wins, Srikanth and Bansod exit
2. Kamali Moorthy wins surfing double at Indian Open
"""

import json, os, sys, uuid, re, time
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
load_env(os.path.expanduser('~/workspace/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

import requests
import urllib.parse

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

def sb_insert(table, data):
    r = requests.post(f"{SUPABASE_URL}/rest/v1/{table}", headers=HEADERS, json=data, timeout=30)
    if r.status_code in (200, 201):
        result = r.json()
        if isinstance(result, list) and result:
            return result[0]
        return result
    print(f"  ✗ Insert error {r.status_code}: {r.text[:300]}")
    return None

def sb_patch(table, filters, data):
    url = f"{SUPABASE_URL}/rest/v1/{table}?{filters}"
    r = requests.patch(url, headers=HEADERS, json=data, timeout=30)
    if r.status_code in (200, 204):
        return True
    print(f"  ✗ Patch error {r.status_code}: {r.text[:300]}")
    return False

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
            # Prefer thumbnail (330px, always works) over originalimage (may 429)
            img = data.get("thumbnail", {}).get("source") or data.get("originalimage", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image found for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None

def fetch_pexels_image(query, fallback_query=None):
    """Fetch an image from Pexels API."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            import subprocess
            result = subprocess.run(
                ['curl', '-sS', f'https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5&orientation=landscape',
                 '-H', f'Authorization: {PEXELS_KEY}'],
                capture_output=True, text=True, timeout=15
            )
            data = json.loads(result.stdout)
            photos = data.get('photos', [])
            for photo in photos:
                src = photo.get('src', {}).get('large2x') or photo.get('src', {}).get('original')
                if src:
                    print(f"  ✓ Pexels image found for '{q}': {src[:80]}...")
                    return src
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

def upload_image_to_supabase(image_url, filename):
    """Download image and upload to Supabase storage bucket 'article-images'."""
    try:
        resp = requests.get(image_url, timeout=15, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        if resp.status_code != 200:
            print(f"  ✗ Image download failed: HTTP {resp.status_code}")
            return None
        content_type = resp.headers.get('Content-Type', 'image/jpeg')
        if not content_type.startswith('image/'):
            print(f"  ✗ Not an image: {content_type}")
            return None
        if len(resp.content) < 5000:
            print(f"  ✗ Image too small: {len(resp.content)} bytes")
            return None

        upload_headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'Content-Type': content_type,
            'x-upsert': 'true'
        }
        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
        r = requests.post(upload_url, headers=upload_headers, data=resp.content, timeout=30)
        if r.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {public_url[:80]}...")
            return public_url
        else:
            print(f"  ✗ Upload failed: {r.status_code} {r.text[:200]}")
            return None
    except Exception as e:
        print(f"  ✗ Upload error: {e}")
        return None

def validate_image_url(url):
    """Validate that a URL returns a real image."""
    if not url:
        return False
    try:
        r = requests.head(url, timeout=10, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, allow_redirects=True)
        ct = r.headers.get('Content-Type', '')
        cl = int(r.headers.get('Content-Length', 0))
        if 'image' in ct and cl > 5000:
            return True
        # Try GET if HEAD doesn't give Content-Length
        if 'image' in ct:
            r2 = requests.get(url, timeout=10, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, stream=True)
            chunk = r2.raw.read(6000)
            if len(chunk) >= 5000:
                return True
    except:
        pass
    return False

# ============================================================
# ARTICLE 1: Indonesia Open Day 1
# ============================================================

def write_article_1():
    print("\n=== ARTICLE 1: Indonesia Open Day 1 ===")

    slug = "indonesia-open-2026-day-1-sindhu-wins-srikanth-bansod-eliminated-jakarta-nri"
    headline = "Sindhu Saved Two Game Points and Won. Srikanth and Bansod Were Gone by Afternoon. Indonesia Open Day One Belonged to the Veterans."
    subheadline = "PV Sindhu rallied from 19-23 down in the first game to beat Ongbamrungphan, while Kidambi Srikanth and Malvika Bansod fell in straight games on the opening day of the BWF Super 1000 in Jakarta."

    body = """The Indonesia Open, the third BWF Super 1000 tournament of the 2026 season, opened in Jakarta on Tuesday with a mixed bag for the Indian contingent. PV Sindhu delivered a fighting first-round victory, but Kidambi Srikanth and Malvika Bansod were both eliminated in straight games, leaving India's singles challenge already thinner than expected.

## Sindhu Digs Deep Against Ongbamrungphan

Sindhu, now ranked world No. 12, found herself in trouble early against Thailand's Busanan Ongbamrungphan. The first game was a knife-edge affair. Ongbamrungphan moved ahead and held game points at 23-22, but Sindhu — showing the kind of composure that once carried her to Olympic glory — saved both and clawed the game back to win it 25-23.

The second game was more straightforward. Having survived the scare, Sindhu took control early and closed it out 21-16. The win sets up a likely second-round clash with top seed An Se-young of South Korea, the reigning Olympic champion. It would be a rematch of their Singapore Open quarter-final last week, which An won comfortably.

For NRI fans streaming on Jio Hotstar across North America and the UK, the timing is demanding — Jakarta is 12 hours ahead of US Eastern time — but Sindhu's gutsy win will make the early alarm worth it.

## Srikanth's Quiet Exit

Kidambi Srikanth's run in Jakarta lasted one match. The former world No. 1, now firmly in the twilight of a career that peaked with four Super Series titles in 2017, lost to Japan's Yuto Tanaka 19-21, 15-21. Tanaka was sharper in the rallies and Srikanth never found his rhythm, going down in 38 minutes.

At 33, Srikanth remains a sentimental figure for Indian badminton fans — the Guntur boy who once beat every top-10 player in the world in a single season. But at Super 1000 level, the legs are no longer enough. His Indonesia Open, a tournament he won memorably in 2017, is over before the second round.

## Bansod Outclassed by Chochuwong

Malvika Bansod's first-round draw was brutal: seventh seed Pornpawee Chochuwong of Thailand, a former All England finalist. The result was predictable. Chochuwong dominated from the start, winning 21-12, 21-10 in a match that lasted barely 30 minutes. Bansod, ranked outside the top 30, struggled with Chochuwong's deceptive drops and net play.

## What's Ahead This Week

The bigger Indian storylines are still to come. Satwiksairaj Rankireddy and Chirag Shetty, fresh from their historic Singapore Open title — the first by an Indian men's doubles pair — begin their campaign on Wednesday. They arrive in Jakarta riding the confidence of a comeback final win over Indonesia's own Fajar Alfian and Muhammad Fikri, and will be among the favourites for the title.

In men's singles, Lakshya Sen, HS Prannoy, and Ayush Shetty are yet to play their openers. Prannoy, in particular, showed sharp form in Singapore with a notable win over Indonesia's world No. 5 Jonatan Christie. In women's doubles, Treesa Jolly and Gayatri Gopichand return to the circuit after a three-month injury layoff — their first BWF World Tour appearance since March.

In mixed doubles, Dhruv Kapila and Tanisha Crasto face the daunting Malaysian world champions Chen Tang Jie and Toh Ee Wei in their opener.

The Indonesia Open runs through June 7. For the diaspora watching from afar, Day 1 offered one reason to cheer and two reminders that Super 1000 badminton is unforgiving."""

    sources = json.dumps([
        {"name": "BWF / Indonesia Open 2026 Draw", "url": "https://en.wikipedia.org/wiki/2026_Indonesia_Open"},
        {"name": "The Bridge", "url": "https://thebridge.in"},
        {"name": "Devdiscourse / ANI", "url": "https://devdiscourse.com"}
    ])

    # Image: PV Sindhu from Wikipedia
    print("  Sourcing image for PV Sindhu...")
    img_url = fetch_wikipedia_person_image("P. V. Sindhu")
    if not img_url:
        img_url = fetch_wikipedia_person_image("PV Sindhu")
    if not img_url:
        img_url = fetch_wikipedia_person_image("Pusarla Venkata Sindhu")

    art_id = str(uuid.uuid4())
    final_image_url = None
    if img_url:
        final_image_url = upload_image_to_supabase(img_url, f"{art_id}.jpg")

    article = {
        "id": art_id,
        "headline": headline,
        "subheadline": subheadline,
        "slug": slug,
        "body": body,
        "category": "sports",
        "vertical": "sports",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "sources": sources,
        "is_editorial": False,
        "is_featured": False,
        "image_url": final_image_url,
        "image_attribution": "Wikimedia Commons" if final_image_url else None
    }

    result = sb_insert("p2_articles", article)
    if result:
        print(f"  ✓ Article 1 published: {headline[:60]}...")
        return art_id
    else:
        print("  ✗ Article 1 failed to publish")
        return None


# ============================================================
# ARTICLE 2: Kamali Moorthy surfing double
# ============================================================

def write_article_2():
    print("\n=== ARTICLE 2: Kamali Moorthy Surfing Double ===")

    slug = "kamali-moorthy-double-title-indian-open-surfing-2026-asian-games-mangaluru-nri"
    headline = "She Is a Teenager From Tamil Nadu. She Just Won Two National Surfing Titles in One Weekend. And She May Represent India at the Asian Games."
    subheadline = "Kamali Moorthy swept the Women's Open and U-18 Girls at the Indian Open of Surfing in Mangaluru, cementing her place in the conversation for India's squad at the Aichi-Nagoya Asian Games."

    body = """Kamali Moorthy stood on the beach at Blue Bay Tannirbhavi in Mangaluru on Sunday, having just completed something no Indian woman surfer has done before in quite this fashion: she won both the Women's Open and the Under-18 Girls titles at the NMPA Indian Open of Surfing 2026, the premier event on India's national surfing calendar.

## The Double

In the Women's Open final, Kamali posted a score of 13.17 to hold off Sugar Shanti Banarse (11.73) and Shrishti Selvam (8.50). It was a title defence — she won the same event last year — but this time, the margin was comfortable and the performance more polished. She read the waves with the patience of a surfer twice her age, choosing her moments rather than chasing every swell.

Hours later, she was back in the water for the Under-18 Girls final. If fatigue was a factor, it did not show. Kamali posted 14.83 — the highest score of the entire tournament's junior divisions — to finish well clear of Karnataka's Saanvi Hegde (5.67) and Aadya Singh (2.73).

"I'm thrilled to have won both titles," Kamali said afterward. "With the Asian Games selection process approaching, I'm excited for what's ahead and will continue working hard to earn my place in Team India."

## From Mahabalipuram to Mangaluru

Kamali's story is one that transcends sport. She grew up in the fishing village of Mahabalipuram on Tamil Nadu's Coromandel Coast, where surfing is not a weekend hobby but a relationship with the sea that begins in childhood. She learned to surf before she learned the alphabet, riding foam boards donated by foreign tourists before anyone thought to give her a proper one.

Her journey from there to international competition has been covered by documentary filmmakers and newspaper feature writers, but the sporting substance is often lost in the human-interest framing. The substance is this: Kamali secured India's surfing quota for the upcoming Asian Games in Aichi-Nagoya, Japan. She is not a curiosity. She is India's best female surfer, and she is getting better.

## Asian Games Selection Looms

The Indian Open results feed directly into the selection matrix for the Asian Games squad. The Surfing Federation of India will consider performances at this championship alongside the inaugural Andaman Little Pro 2026, coaching camp evaluations, international results, and overall national rankings.

Kamali's double gives her an almost unassailable case. But India's surfing depth is growing. Kishore Kumar of Tamil Nadu won the Men's Open with a tournament-best 15.20, beating Ramesh Budihal (12.87) and Sivaraj Babu (11.90) in a tightly contested final. In the junior categories, Harish P dominated the Under-14 Boys with 17.23 points, while Dhamayanthi Sriram won the Under-14 Girls.

The emergence of competitive junior surfers — many of them from coastal Tamil Nadu and Karnataka — suggests Indian surfing is no longer a one-person sport. The federation's decision to introduce Under-14 categories this year was designed to build the pipeline, and the quality of performances suggests the pipeline is starting to flow.

## What NRI Fans Should Know

Surfing will be contested at the Aichi-Nagoya Asian Games later this year, only the second time the sport has appeared at the Games after its Hangzhou debut. For diaspora fans accustomed to tracking India's medal hopes in cricket, badminton, and wrestling, surfing remains unfamiliar territory. But Kamali Moorthy is the kind of athlete who makes you pay attention — not because of where she came from, but because of how she competes.

The next major selection event, the Andaman Little Pro, is expected later this summer. The Asian Games surfing competition will take place at a venue yet to be confirmed in the Aichi region."""

    sources = json.dumps([
        {"name": "Press Trust of India / Nagaland Post", "url": "https://nagalandpost.com"},
        {"name": "The Bridge", "url": "https://thebridge.in"},
        {"name": "LatestLY / ANI", "url": "https://latestly.com"}
    ])

    # Image: Try Pexels for surfing since Kamali likely doesn't have a Wikipedia page
    print("  Sourcing image for Kamali Moorthy...")
    img_url = fetch_wikipedia_person_image("Kamali Moorthy")
    if not img_url:
        img_url = fetch_pexels_image("Indian surfer ocean waves", "surfing beach India")

    art_id = str(uuid.uuid4())
    final_image_url = None
    if img_url:
        final_image_url = upload_image_to_supabase(img_url, f"{art_id}.jpg")

    article = {
        "id": art_id,
        "headline": headline,
        "subheadline": subheadline,
        "slug": slug,
        "body": body,
        "category": "sports",
        "vertical": "sports",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "sources": sources,
        "is_editorial": False,
        "is_featured": False,
        "image_url": final_image_url,
        "image_attribution": "Wikimedia Commons" if final_image_url and "wikipedia" in (final_image_url or "").lower() else "Pexels" if final_image_url else None
    }

    result = sb_insert("p2_articles", article)
    if result:
        print(f"  ✓ Article 2 published: {headline[:60]}...")
        return art_id
    else:
        print("  ✗ Article 2 failed to publish")
        return None


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    print(f"Sports Writer — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 60)

    results = []
    a1 = write_article_1()
    if a1:
        results.append(a1)

    a2 = write_article_2()
    if a2:
        results.append(a2)

    print(f"\n{'=' * 60}")
    print(f"Done. Published {len(results)}/{2} articles.")
    if not results:
        sys.exit(1)

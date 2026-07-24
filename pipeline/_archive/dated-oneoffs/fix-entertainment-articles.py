#!/usr/bin/env python3
"""Fix published articles — update draft article 2 to published, add image to article 1."""
import requests, json, os, subprocess, urllib.parse, time
from datetime import datetime, timezone

def load_env(path):
    path = os.path.expanduser(path)
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

load_env('~/.env.supabase')
load_env('~/workspace/.env.supabase')
load_env('~/workspace/.env.pexels')

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

# =========================================
# Fix Article 2: Update draft to published
# =========================================
art2_id = "9e8d950d-ec52-412c-9d1b-edeab4a7d36d"

body2 = """Varun Dhawan's upcoming romantic comedy **Hai Jawani Toh Ishq Hona Hai** was supposed to be a feel-good summer release. Instead, it's walking into a legal firestorm.

Veteran producer **Vashu Bhagnani's** Puja Entertainment has filed a \u20b9400 crore lawsuit in the Bombay High Court against **Tips Industries Limited**, producers **Ramesh Taurani** and **Kumar S Taurani**, and director **David Dhawan** over the alleged unauthorized use of two songs from the 1999 blockbuster **Biwi No. 1** \u2014 *Chunnari Chunnari* and *Ishq Sona Hai*.

The suit seeks urgent injunctive relief to restrain the release, distribution, exhibition, streaming, and commercial exploitation of the film and all promotional material featuring the disputed songs. The court has reportedly permitted filing and will hear the matter soon \u2014 potentially before the film's scheduled June 5 release date.

## What's at Stake

This isn't a routine Bollywood squabble. At \u20b9400 crore, it's being described as one of the largest copyright claims in Indian film history. And it strikes at the heart of a practice the industry has leaned on heavily: **remaking or remixing iconic 90s songs** to drive nostalgia-fueled marketing.

The dispute centres on who actually owns the rights to the songs. Bhagnani's lawyers argue that Tips was granted only audio rights in the original agreements from the late 1990s, not visual rights. In 2018, Tips reportedly emailed Bhagnani requesting visual rights, but the conversation never reached a resolution. Despite this, the songs were allegedly used in the new film.

Tips Industries has called the allegations "baseless," but the legal machinery is already in motion.

## The Remake Economy Under Threat

For NRI audiences who grew up on 90s Bollywood soundtracks, *Chunnari Chunnari* isn't just a song \u2014 it's a cultural touchstone. And the broader issue here will resonate with anyone who's watched Bollywood's relentless remix engine churn through classic after classic.

The lawsuit could set a precedent for how music rights from the analogue era \u2014 when agreements were simpler and less precise \u2014 are handled in the streaming age. If the court rules in Bhagnani's favour, it could complicate dozens of projects currently in production that rely on recreated versions of classic tracks.

## A Film Caught in the Crossfire

**Hai Jawani Toh Ishq Hona Hai** marks the fourth collaboration between Varun Dhawan and his father David Dhawan, following *Main Tera Hero*, *Judwaa 2*, and *Coolie No. 1*. The film also stars **Mrunal Thakur** and **Pooja Hegde**, alongside Jimmy Shergill, Chunky Panday, and Mouni Roy.

The release date has already been shuffled multiple times \u2014 originally April 2026, then June 12, briefly May 22, and finally settled on June 5. This lawsuit adds another layer of uncertainty.

Industry watchers are divided. Some believe the court is unlikely to issue a stay on a completed film just days before release, particularly when the rights ownership is contested. Others point out that Bombay High Court has previously intervened in music copyright disputes with injunctive relief.

## Why Diaspora Audiences Should Care

For Indians abroad, Bollywood's music library isn't just entertainment \u2014 it's the soundtrack of weddings, Diwali parties, and identity. The question of who owns these songs, and who can profit from them, matters beyond the courtroom. If the 90s music catalogue becomes a legal minefield, the remix-driven marketing that currently defines Bollywood releases could face a reckoning.

The hearing is expected before June 5. Whether Varun Dhawan dances to *Chunnari Chunnari* on screen or not may depend entirely on what happens in court this week."""

update_data = {
    "headline": "Vashu Bhagnani Just Filed a \u20b9400 Crore Lawsuit to Block Varun Dhawan's Next Film. The Fight Is Over Two 1999 Songs.",
    "subheadline": "Chunnari Chunnari and Ishq Sona Hai from Biwi No. 1 are at the centre of one of Bollywood's biggest copyright battles. Hai Jawani Toh Ishq Hona Hai releases June 5 \u2014 if the court allows it.",
    "body": body2,
    "vertical": "entertainment",
    "category": "entertainment",
    "sources": [{"name": "Bollywood Hungama"}, {"name": "India Forums"}, {"name": "Zoom TV"}, {"name": "MensXP"}],
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "image_attribution": "Wikimedia Commons"
}

r = requests.patch(
    f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{art2_id}",
    headers=HEADERS, json=update_data, timeout=30
)
print(f"Article 2 update: {r.status_code}")

# =========================================
# Fix Article 1: Add image
# =========================================
art1_id = "3403f706-ff69-4bb3-ae2a-ef21c864b977"

# Try Pexels for a cinema/theater image
result = subprocess.run([
    'curl', '-sS', '-H', f'Authorization: {PEXELS_KEY}',
    f'https://api.pexels.com/v1/search?query={urllib.parse.quote("cinema movie theater audience")}&per_page=5&orientation=landscape'
], capture_output=True, text=True, timeout=15)
data = json.loads(result.stdout)
photos = data.get('photos', [])
img_url = None
for p in photos:
    url = p.get('src', {}).get('large2x') or p.get('src', {}).get('large')
    if url:
        img_url = url
        break

if img_url:
    r_img = requests.get(img_url, timeout=15)
    if r_img.status_code == 200 and len(r_img.content) > 5000:
        ct = r_img.headers.get('content-type', 'image/jpeg')
        upload_headers = {
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'Content-Type': ct,
            'x-upsert': 'true'
        }
        up = requests.post(
            f"{SUPABASE_URL}/storage/v1/object/article-images/drishyam-3-200-crore-worldwide-overseas-mohanlal-nri-diaspora-20260531.jpg",
            headers=upload_headers, data=r_img.content, timeout=30
        )
        if up.status_code in (200, 201):
            final_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/drishyam-3-200-crore-worldwide-overseas-mohanlal-nri-diaspora-20260531.jpg"
            r2 = requests.patch(
                f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{art1_id}",
                headers=HEADERS,
                json={"image_url": final_url, "image_attribution": "Pexels"},
                timeout=30
            )
            print(f"Article 1 image update: {r2.status_code}")
        else:
            print(f"Upload failed: {up.status_code} {up.text[:100]}")
    else:
        print(f"Download failed: {r_img.status_code}")
else:
    print("No Pexels image found, trying Wikipedia...")
    time.sleep(3)
    r_wiki = requests.get(
        "https://en.wikipedia.org/api/rest_v1/page/summary/Mohanlal",
        headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com; editorial)"},
        timeout=10
    )
    if r_wiki.status_code == 200:
        wiki_data = r_wiki.json()
        wiki_img = wiki_data.get("thumbnail", {}).get("source")
        if wiki_img:
            r2 = requests.patch(
                f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{art1_id}",
                headers=HEADERS,
                json={"image_url": wiki_img, "image_attribution": "Wikimedia Commons"},
                timeout=30
            )
            print(f"Article 1 Wiki image: {r2.status_code}")
    else:
        print(f"Wikipedia: {r_wiki.status_code}")

print("\nDone!")

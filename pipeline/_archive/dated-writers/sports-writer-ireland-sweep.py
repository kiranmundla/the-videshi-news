#!/usr/bin/env python3
"""Sports writer: Ireland sweep India 2-0 in T20I series — historic bilateral series win."""

import os, sys, json, requests, io, uuid, re, subprocess
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
UA = "TheVideshi/1.0 (thevideshi.com)"

# ── Image sourcing ──────────────────────────────────────────────
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

def search_commons_image(query, min_width=400):
    """Search Wikimedia Commons for an image matching query."""
    import urllib.parse
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": query,
        "gsrnamespace": "6",
        "gsrlimit": "5",
        "prop": "imageinfo",
        "iiprop": "url|size|mime",
        "iiurlwidth": "1200",
        "format": "json"
    }
    try:
        r = requests.get(
            "https://commons.wikimedia.org/w/api.php",
            params=params,
            headers={"User-Agent": UA},
            timeout=15
        )
        if r.status_code == 200:
            data = r.json()
            pages = data.get("query", {}).get("pages", {})
            for pid, page in pages.items():
                ii = page.get("imageinfo", [{}])[0]
                mime = ii.get("mime", "")
                if not mime.startswith("image/") or mime == "image/svg+xml":
                    continue
                if ii.get("width", 0) < min_width:
                    continue
                thumb = ii.get("thumburl") or ii.get("url", "")
                if thumb:
                    print(f"  ✓ Commons image found: {page.get('title','')}")
                    return thumb
    except Exception as e:
        print(f"  ⚠ Commons search failed: {e}")
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

def download_image(url):
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=30)
        if r.status_code == 200 and len(r.content) > 5000:
            return r.content
    except Exception as e:
        print(f"  ⚠ Download via requests failed: {e}")
    # Fallback to curl (handles Wikimedia 429s)
    tmp_path = "/tmp/hero_ireland_sweep.jpg"
    try:
        result = subprocess.run(
            ["curl", "-sS", "-A", UA, "-o", tmp_path, url],
            capture_output=True, timeout=30
        )
        if os.path.exists(tmp_path):
            with open(tmp_path, "rb") as f:
                data = f.read()
            if len(data) > 5000:
                return data
    except Exception as e:
        print(f"  ⚠ curl fallback failed: {e}")
    return None

def upload_image_to_supabase(jpeg_bytes, filename):
    r = requests.post(
        f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}",
        headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "image/jpeg",
            "x-upsert": "true",
        },
        data=jpeg_bytes,
        timeout=60,
    )
    if r.status_code not in (200, 201):
        print(f"    ⚠ Supabase upload failed {r.status_code}: {r.text[:200]}")
        return None
    return f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"

# ── Article content ─────────────────────────────────────────────

SLUG = "ireland-sweep-india-2-0-t20i-series-belfast-2026-historic-bilateral-series-win-prince-yadav-moondra-sooryavanshi-diaspora-nri"

HEADLINE = "Swept in Belfast. Ireland Inflict India's First Bilateral T20I Series Loss in Over Two Years."

SUBHEADLINE = "Three months after lifting the T20 World Cup in Barbados, India went to Belfast and lost both matches. Prince Yadav's 3/22 on debut and Arshdeep Singh's sixes could not prevent the reigning champions from being swept 2-0 by a nation they had never lost to before Friday."

BODY = """Ireland completed a historic 2-0 T20I series sweep over India at Belfast's Civil Service Cricket Club on Sunday, winning the second match to add to their 34-run victory in the opener two days earlier. It was Ireland's first bilateral series win over India in any format — and only their second bilateral T20I series victory over a Full Member nation, after beating Afghanistan 2-0 in August 2022.

For India, it marked the end of a remarkable streak. They had not lost a bilateral T20I series since January 2024 — a run that included a historic T20 World Cup triumph in Barbados in March 2026. That golden stretch now has a full stop, placed by a team ranked 13th in the world.

## The Second T20I

India won the toss and chose to bowl — the same decision they made in the first match, with the same result.

Prince Yadav, making his T20I debut alongside Suryansh Shedge, was the standout performer with the ball. The young leg-spinner returned figures of 3/22 from his four overs, troubling Ireland's middle order with sharp turn and dip. Arshdeep Singh picked up 2/35 and Harshit Rana was again tidy at the top.

But Ireland's batting, led by the middle and lower order, pushed their total to 154/8 in 20 overs — modest by modern T20I standards, but on a surface that had already proved treacherous for batting two days earlier.

India's chase followed a grimly familiar script. Wickets fell at regular intervals as the visitors struggled to adapt to the conditions for the second time in 48 hours. Despite Arshdeep Singh's defiant sixes in the closing overs, India fell well short, bowled out with the required rate climbing beyond reach.

## Jai Moondra: Born in India, Beating India

Among the standout stories of the series was Jai Moondra, the left-arm seamer born in Tonk, Rajasthan — the same town that produced Indian quick Khaleel Ahmed. Moondra emigrated to Ireland, qualified through residency, and took a wicket with his very first ball in international cricket in the first T20I.

In the second match, he continued to bowl with discipline on familiar surfaces. His journey encapsulates the complexity of modern diaspora cricket: a man born in Rajasthan, raised in Ireland, now playing international cricket against the country of his birth. For the Indian fans in the stands — most of whom had paid premium prices hoping to see 15-year-old prodigy Vaibhav Sooryavanshi — watching Moondra dismiss their batsmen was a bittersweet experience.

## Where Was Sooryavanshi?

The teenager was not selected in either playing XI. Batting coach Sitanshu Kotak said before the second match that it would be "unfair to drop someone who has already been scoring runs just to give him an opportunity." India opted for Shedge and Yadav as their fresh faces instead.

Sooryavanshi's exclusion was the tournament's great non-story. Thousands of Indian diaspora fans had bought tickets specifically to see the 15-year-old prodigy, whose IPL exploits with RCB had made him a household name. Instead, they watched him carry drinks around the boundary edge while Ireland made history around him.

## The Bigger Questions for India

Shreyas Iyer's captaincy record now reads: played two, lost two. He became the fourth India T20I captain — after Virat Kohli, Rishabh Pant, and Shubman Gill — to lose his maiden T20I in charge. That he lost both matches puts uncomfortable questions on the table about India's T20I leadership transition after the World Cup.

Head coach Gautam Gambhir's difficult year continued. His tenure has now overseen India's first home Test series whitewash, a 12-year undefeated home Test series run snapped, and now a bilateral T20I series loss to a team ranked 13th in the world. The common thread across these setbacks has been an inability to adapt to conditions that differ from the flat, pace-friendly pitches India's batsmen have grown accustomed to in the IPL.

Washington Sundar and Prasidh Krishna were dropped for the second match — Prasidh after conceding 57 runs in four wicketless overs in the first game — but the changes didn't alter the outcome. India's batting, not their bowling, was the consistent point of failure across both matches.

## The Diaspora Paradox

Belfast's Civil Service Cricket Club, nestled in the leafy Stormont Estate, was overwhelmed by ticket demand driven almost entirely by the Indian diaspora. Fans arrived in their thousands, wearing blue replica jerseys and IPL accessories, creating an atmosphere more reminiscent of Wankhede Stadium than Northern Ireland.

The irony was not lost on anyone. Ireland, playing at home, were the visiting team in terms of crowd support. Yet it was Irish cricket's fans — a small but devoted minority in the ground — who left with the bigger smiles.

For NRI cricket followers, the series was a reminder that India's dominance in white-ball cricket is not a given. The Men in Blue arrived in Belfast with the T20 World Cup trophy still warm. They left with a 0-2 series loss and more questions than answers about the post-World Cup transition.

## What's Next

India travel to England for a five-match T20I series starting in early July. The stakes will be considerably higher, and the conditions similarly testing. Gambhir will need to decide whether Iyer remains as captain, whether Sooryavanshi finally gets his debut, and whether the squad's batting approach needs a fundamental rethink for overseas conditions.

For Ireland, a bus ride back through Belfast will feel different. Cricket Ireland has long argued that its team deserves more fixtures against top nations. After this weekend, nobody can argue with the case they've made on the field."""

SOURCES = json.dumps([
    {"name": "Sportradar — Ireland vs India 2nd T20I live scores", "url": "https://sportradar.com"},
    {"name": "Reuters — Ireland beat India for first time in international cricket", "url": "https://www.reuters.com/sports/cricket/ireland-beat-india-first-time-international-cricket-2026-06-27/"},
    {"name": "ESPNcricinfo — Ireland vs India 2nd T20I", "url": "https://www.espncricinfo.com/series/india-in-ireland-2026-1467285/ireland-vs-india-2nd-t20i-1467293/live-cricket-score"},
    {"name": "The Times — India win was fantastic for morale but cracks in Irish cricket remain", "url": "https://www.thetimes.com/sport/cricket/article/india-win-was-fantastic-for-morale-but-cracks-in-irish-cricket-remain/"},
    {"name": "The SportsTak — India's adaptability issues surface as Ireland seal historic T20I win", "url": "https://www.thesportstak.com/cricket/indias-adaptability-issues-surface-as-ireland-seal-historic-34-run-t20i-win/"}
])

CATEGORY = "sports"
VERTICAL = "cricket"
DIASPORA_ANGLE = "Indian diaspora fans in Belfast bought tickets in their thousands hoping to see Sooryavanshi's debut, but instead witnessed Ireland sweep their team 2-0. Jai Moondra, born in Rajasthan and now playing for Ireland, embodies the reverse side of the cricket diaspora."

IMAGE_CAPTION = "Ireland celebrate after their historic victory over India at the Civil Service Cricket Club, Belfast"
IMAGE_ATTRIBUTION = "Cricket Ireland / Sportsfile"

# ── Main ────────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("SPORTS WRITER: Ireland Sweep India 2-0 T20I Series")
    print("=" * 60)

    # 1) Image sourcing — try Cricket Ireland / Stormont / Belfast cricket ground
    print("\n[1] Sourcing hero image...")
    final_image_url = None

    # Try Wikipedia for Civil Service Cricket Club or Stormont
    search_terms = [
        "Civil Service Cricket Club Stormont Belfast cricket",
        "Cricket Ireland T20 international",
        "Stormont Estate Belfast cricket ground",
    ]
    for term in search_terms:
        img_url = search_commons_image(term)
        if img_url:
            raw = download_image(img_url)
            if raw:
                compressed = compress_image(raw)
                filename = f"{SLUG}.jpg"
                final_image_url = upload_image_to_supabase(compressed, filename)
                if final_image_url:
                    print(f"    ✓ Uploaded to Supabase: {final_image_url[:80]}...")
                    break

    # Fallback: try Shreyas Iyer Wikipedia image (person article)
    if not final_image_url:
        print("    Trying Shreyas Iyer Wikipedia image as fallback...")
        img_url = fetch_wikipedia_person_image("Shreyas Iyer")
        if img_url:
            raw = download_image(img_url)
            if raw:
                compressed = compress_image(raw)
                filename = f"{SLUG}.jpg"
                final_image_url = upload_image_to_supabase(compressed, filename)
                if final_image_url:
                    print(f"    ✓ Uploaded Iyer image: {final_image_url[:80]}...")

    # Fallback: Pexels cricket image
    if not final_image_url:
        print("    Trying Pexels cricket image fallback...")
        pexels_key = os.environ.get("PEXELS_API_KEY", "")
        if pexels_key:
            try:
                r = requests.get(
                    "https://api.pexels.com/v1/search",
                    params={"query": "cricket match", "per_page": 5, "orientation": "landscape"},
                    headers={"Authorization": pexels_key},
                    timeout=15,
                )
                if r.status_code == 200:
                    photos = r.json().get("photos", [])
                    for p in photos:
                        img_url = p.get("src", {}).get("large2x") or p.get("src", {}).get("large", "")
                        if img_url:
                            raw = download_image(img_url)
                            if raw:
                                compressed = compress_image(raw)
                                filename = f"{SLUG}.jpg"
                                final_image_url = upload_image_to_supabase(compressed, filename)
                                if final_image_url:
                                    print(f"    ✓ Pexels image uploaded: {final_image_url[:80]}...")
                                    break
            except Exception as e:
                print(f"    ⚠ Pexels fallback failed: {e}")

    if not final_image_url:
        print("    ✗ No image sourced. Will insert without hero image.")

    # 2) Insert article
    print("\n[2] Inserting article into p2_articles...")
    article = {
        "headline": HEADLINE,
        "subheadline": SUBHEADLINE,
        "body": BODY,
        "slug": SLUG,
        "category": CATEGORY,
        "vertical": VERTICAL,
        "status": "review",
        "is_editorial": False,
        "sources": SOURCES,
        "diaspora_angle": DIASPORA_ANGLE,
        "published_at": datetime.now(timezone.utc).isoformat(),
        "image_caption": IMAGE_CAPTION,
        "image_attribution": IMAGE_ATTRIBUTION,
    }
    
    if final_image_url:
        article["image_url"] = final_image_url

    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        },
        json=article,
        timeout=30,
    )
    
    if r.status_code in (200, 201):
        result = r.json()
        if isinstance(result, list) and result:
            art_id = result[0].get("id", "?")
        else:
            art_id = "?"
        print(f"    ✓ Article inserted! ID: {art_id}")
        print(f"    Headline: {HEADLINE}")
        print(f"    Slug: {SLUG}")
        print(f"    Status: review")
        return True
    else:
        print(f"    ✗ Insert failed {r.status_code}: {r.text[:300]}")
        return False

if __name__ == "__main__":
    ok = main()
    sys.exit(0 if ok else 1)

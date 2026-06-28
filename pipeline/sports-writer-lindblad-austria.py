#!/usr/bin/env python3
"""Sports writer: Arvid Lindblad P10 at Austrian Grand Prix 2026."""

import os, sys, json, requests, io, uuid, re
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
        print(f"  ⚠ Download failed: {e}")
    # Fallback to curl
    import subprocess
    result = subprocess.run(
        ["curl", "-sS", "-A", UA, "-o", "/tmp/lindblad_hero.jpg", url],
        capture_output=True, timeout=30
    )
    if os.path.exists("/tmp/lindblad_hero.jpg"):
        with open("/tmp/lindblad_hero.jpg", "rb") as f:
            data = f.read()
        if len(data) > 5000:
            return data
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

SLUG = "arvid-lindblad-p10-austrian-grand-prix-red-bull-ring-racing-bulls-indian-heritage-punjab-f1-2026-diaspora-nri"

HEADLINE = "Lindblad Finishes P10 in Austria. India's Closest Thing to an F1 Driver Just Keeps Collecting Points."

SUBHEADLINE = "The 18-year-old Racing Bulls rookie with Punjabi roots scored his fifth points finish at the Red Bull Ring, extending a debut season that has Indian motorsport fans watching F1 closer than they have in 15 years."

BODY = """George Russell won the Austrian Grand Prix from pole position on Sunday, holding off Max Verstappen and championship leader Kimi Antonelli in a tense, heat-soaked race at the Red Bull Ring. But nestled inside the top 10, just behind his Racing Bulls teammate Liam Lawson, was a name that has been quietly rewriting the Indian connection to Formula 1: Arvid Lindblad.

The 18-year-old finished P10 at Spielberg, scoring one world championship point to bring his career total to 14 across eight races. It was another composed, mistake-free afternoon for the youngest driver on the grid — and for the growing number of Indian fans who have adopted him as their own.

## From Surrey to Spielberg — via Punjab

Arvid Anand Olof Lindblad was born in Virginia Water, Surrey, to a Swedish father and a British Indian mother whose family hails from Punjab. He carries an Indian tricolour on his helmet — a detail that has made him a cult figure among Indian motorsport followers who have waited since Karun Chandhok's final F1 appearance in 2011 for someone, anyone, to represent the subcontinent on the grid.

Lindblad does not hold an Indian racing licence. He competes under the British flag for Racing Bulls, the Red Bull junior outfit. But his heritage is woven into his identity. Before his debut at Melbourne in March, he visited Delhi for a Red Bull event and told reporters he intended to "bring a bit of India back to the F1 grid." His grandparents, originally from Punjab, watched that debut from England. He finished eighth and scored four points.

## The Austrian Weekend

Qualifying at the Red Bull Ring brought drama. Verstappen crashed at the penultimate corner on his final Q3 lap, triggering yellow flags that briefly put Russell's pole under investigation. Amid the chaos, Lindblad calmly put in a 1:07.007 to claim P10 on the grid — making Q3 for the fourth time in eight races.

The race itself was a Mercedes masterclass. Russell led from start to finish despite a failed drinks system in what was declared the season's first "heat hazard" race. Verstappen charged from fifth to second, battling Hamilton wheel-to-wheel in the process. Antonelli completed the podium, 0.3 seconds behind.

Further back, both Racing Bulls finished in the points. Lawson took P9 and Lindblad held station in P10 — matching his grid position — to deliver another solid result for the Faenza-based team. No fireworks, no errors, just the kind of clean, point-scoring race that builds a career.

## The Bigger Picture

Eight races into his rookie season, Lindblad has 14 career points. For context, Narain Karthikeyan — the only Indian-passport holder to race in F1 — scored five points across 46 race starts over two stints in the championship. Chandhok started 11 races and scored none.

Lindblad is, of course, in a more competitive car. Racing Bulls are sixth in the constructors' standings, and the team's Red Bull Ford power unit is a significant step up from what Jordan or HRT offered India's previous drivers. But the comparison matters because it illustrates something that has changed: there is now a driver with Indian blood in a car capable of scoring points every weekend.

The championship standings tell the story of a season Mercedes are dominating. Antonelli leads with 171 points, Russell has 131, and Hamilton sits third on 125. But for Indian fans scanning the lower reaches of the table, Lindblad's steady accumulation of points represents something more personal — proof that Indian heritage and the pinnacle of motorsport are no longer mutually exclusive.

## What's Next

The F1 circus heads to Silverstone next weekend for the British Grand Prix — effectively a home race for Lindblad. The Surrey-born teenager will drive in front of family and friends for the first time as an F1 driver. Russell, buoyed by his Austrian victory, will arrive as the hometown favourite. But the Indian flag on car number 41 will draw its own crowd.

Lindblad still has not passed his road driving test. He can lap the Red Bull Ring at 220 mph but cannot legally drive his mother's car unaccompanied. It is the kind of absurd detail that captures the strangeness of an 18-year-old's life at the top of global motorsport — and the kind of story that makes him irresistible to a diaspora audience searching for heroes in unexpected places."""

SOURCES = json.dumps([
    {"name": "Reuters", "url": "https://www.reuters.com/sports/formula1/russell-wins-austria-trim-antonellis-lead-2026-06-28/"},
    {"name": "Wikipedia — 2026 Austrian Grand Prix", "url": "https://en.wikipedia.org/wiki/2026_Austrian_Grand_Prix"},
    {"name": "Wikipedia — Arvid Lindblad", "url": "https://en.wikipedia.org/wiki/Arvid_Lindblad"},
    {"name": "The Times — Arvid Lindblad profile", "url": "https://www.thetimes.com/article/arvid-lindblad-f1-racing-bulls-interview/"},
    {"name": "LatestLY — Lindblad Indian roots", "url": "https://www.latestly.com/sports/know-all-about-arvid-lindblad-and-his-indian-roots-ahead-of-his-f1-debut/"}
])

CATEGORY = "sports"
VERTICAL = "motorsport"
DIASPORA_ANGLE = "Lindblad, whose mother is of Indian descent and whose grandparents hail from Punjab, is the closest thing India has had to an F1 driver since Karun Chandhok in 2010 — and he's collecting points at 18."

IMAGE_CAPTION = "Arvid Lindblad at the 2026 Australian Grand Prix"
IMAGE_ATTRIBUTION = "Wikimedia Commons"

# ── Main ────────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("SPORTS WRITER: Arvid Lindblad Austrian GP P10")
    print("=" * 60)

    # 1) Image sourcing
    print("\n[1] Sourcing hero image...")
    img_url = fetch_wikipedia_person_image("Arvid Lindblad")
    
    final_image_url = None
    if img_url:
        print(f"    Downloading from Wikipedia: {img_url[:80]}...")
        raw = download_image(img_url)
        if raw:
            print(f"    Downloaded {len(raw)} bytes, compressing...")
            compressed = compress_image(raw)
            print(f"    Compressed to {len(compressed)} bytes")
            filename = f"{SLUG}.jpg"
            final_image_url = upload_image_to_supabase(compressed, filename)
            if final_image_url:
                print(f"    ✓ Uploaded to Supabase: {final_image_url[:80]}...")
    
    if not final_image_url:
        print("    ⚠ Wikipedia image failed, trying Wikimedia Commons...")
        # Try Commons search
        import urllib.parse
        params = {
            "action": "query",
            "generator": "search",
            "gsrsearch": "Arvid Lindblad Formula One racing",
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
                    if ii.get("width", 0) < 300:
                        continue
                    thumb = ii.get("thumburl") or ii.get("url", "")
                    if thumb:
                        raw = download_image(thumb)
                        if raw:
                            compressed = compress_image(raw)
                            filename = f"{SLUG}.jpg"
                            final_image_url = upload_image_to_supabase(compressed, filename)
                            if final_image_url:
                                print(f"    ✓ Commons image uploaded: {final_image_url[:80]}...")
                                break
        except Exception as e:
            print(f"    ⚠ Commons search failed: {e}")

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

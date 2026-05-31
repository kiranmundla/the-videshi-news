#!/usr/bin/env python3
"""Entertainment writer for The Videshi — publishes 3 articles with images."""

import json, os, re, requests, time, uuid, urllib.parse
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
        return result[0] if isinstance(result, list) else result
    print(f"  ✗ Insert failed ({r.status_code}): {r.text[:200]}")
    return None

def sb_patch(table, match, data):
    params = '&'.join(f"{k}={v}" for k, v in match.items())
    r = requests.patch(f"{SUPABASE_URL}/rest/v1/{table}?{params}", headers=HEADERS, json=data, timeout=30)
    if r.status_code in (200, 204):
        return True
    print(f"  ✗ Patch failed ({r.status_code}): {r.text[:200]}")
    return False

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com; editorial)"},
            timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            # Use thumbnail (330px, always works) — originalimage may 429
            img = data.get("thumbnail", {}).get("source") or data.get("originalimage", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image found for '{person_name}': {img[:80]}...")
                return img
        elif r.status_code == 429:
            print(f"  ⚠ Wikipedia rate limited for '{person_name}', retrying after delay...")
            time.sleep(3)
            r2 = requests.get(
                f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
                headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com; editorial)"},
                timeout=10
            )
            if r2.status_code == 200:
                data = r2.json()
                img = data.get("thumbnail", {}).get("source") or data.get("originalimage", {}).get("source")
                if img:
                    print(f"  ✓ Wikipedia image found on retry for '{person_name}': {img[:80]}...")
                    return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None

def fetch_pexels_image(query, fallback_query=None):
    """Fetch an image from Pexels using curl (urllib gets 403)."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    import subprocess
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            result = subprocess.run([
                'curl', '-sS', '-H', f'Authorization: {PEXELS_KEY}',
                f'https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5&orientation=landscape'
            ], capture_output=True, text=True, timeout=15)
            data = json.loads(result.stdout)
            photos = data.get('photos', [])
            for p in photos:
                url = p.get('src', {}).get('large2x') or p.get('src', {}).get('large')
                if url:
                    print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

def validate_image(url):
    """Validate image URL returns 200 and is > 5KB."""
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get('content-type', '')
        cl = int(r.headers.get('content-length', 0))
        if r.status_code == 200 and 'image' in ct and cl > 5000:
            return True
        # Try GET if HEAD doesn't return content-length
        if r.status_code == 200 and 'image' in ct and cl == 0:
            r2 = requests.get(url, timeout=10, stream=True,
                             headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
            chunk = r2.raw.read(6000)
            r2.close()
            if len(chunk) > 5000:
                return True
        print(f"  ⚠ Image validation failed: status={r.status_code}, ct={ct}, cl={cl}")
    except Exception as e:
        print(f"  ⚠ Image validation error: {e}")
    return False

def upload_to_supabase_storage(image_url, filename):
    """Download image and upload to Supabase storage bucket."""
    try:
        r = requests.get(image_url, timeout=15,
                        headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        if r.status_code != 200 or len(r.content) < 5000:
            print(f"  ⚠ Download failed: {r.status_code}, size={len(r.content)}")
            return None
        
        ct = r.headers.get('content-type', 'image/jpeg')
        upload_headers = {
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'Content-Type': ct,
            'x-upsert': 'true'
        }
        up = requests.post(
            f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}",
            headers=upload_headers, data=r.content, timeout=30
        )
        if up.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {public_url[:80]}...")
            return public_url
        print(f"  ⚠ Upload failed: {up.status_code} {up.text[:100]}")
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
    return None

# ============================================================
# ARTICLES
# ============================================================

articles = []

# -------- Article 1: Drishyam 3 crosses 200 crore worldwide --------
articles.append({
    "headline": "Drishyam 3 Crosses ₹200 Crore Worldwide in 9 Days. Overseas Collections Are Outpacing India.",
    "subheadline": "Mohanlal's third consecutive blockbuster of 2026 hits the milestone faster than every Malayalam film except L2 Empuraan. For NRI audiences, this is their franchise too — and the numbers prove it.",
    "slug": "drishyam-3-200-crore-worldwide-overseas-mohanlal-nri-diaspora-20260531",
    "category": "entertainment",
    "sources": [{"name": "Sacnilk"}, {"name": "Pinkvilla"}, {"name": "Filmfare"}, {"name": "Zoom TV"}],
    "person_for_image": "Mohanlal",
    "pexels_query": "Malayalam cinema theater audience",
    "body": """Georgekutty is back, and this time, the world is watching.

Mohanlal's **Drishyam 3**, directed by Jeethu Joseph, has crossed the ₹200 crore mark at the worldwide box office within just nine days of its theatrical release — making it the first film in the franchise to hit the milestone and the second-fastest Malayalam film ever to do so, trailing only Mohanlal's own **L2: Empuraan**, which got there in five days.

The numbers tell a story that should matter to every Indian abroad. Of the ₹208 crore worldwide gross collected by Day 9, approximately ₹108 crore — more than half — came from **overseas markets**. North America, the Middle East, Europe, and Australia have driven collections at a pace that outstripped domestic earnings for most of the run. Drishyam 3 also became the first South Indian film of 2026 to cross $10 million at the overseas box office.

## The Franchise That Travels

The original Drishyam (2013) was a masterclass in slow-burn suspense that became a pan-Indian phenomenon, spawning remakes in Hindi (starring Ajay Devgn), Telugu, Kannada, and Tamil. But the third instalment's overseas dominance signals something deeper: the Malayalam original now draws its own global audience, without needing a Hindi intermediary.

For the Indian diaspora — particularly in the Gulf, where Malayalam-speaking communities are deeply rooted, and in North America, where Indian-language cinema is having its strongest theatrical moment ever — Drishyam 3's performance validates a shift. Regional cinema doesn't need Bollywood's stamp anymore.

## Three Films, Three Blockbusters

What makes 2026 extraordinary for Mohanlal is the consistency. Earlier this year, **L2: Empuraan** entered the ₹200 crore club. **Thudarum** followed. Drishyam 3 is now his third film to cross the mark in a single calendar year — a feat virtually no Indian actor has achieved.

Domestically, Drishyam 3 has grossed approximately ₹100 crore in India (the 8th Malayalam film to do so), with Kerala contributing around ₹62.70 crore and the rest of India adding ₹32.50 crore. The film is now the sixth-highest-grossing Malayalam film of all time in India.

## Mixed Reviews, Massive Turnout

The road wasn't entirely smooth. Before release, some questioned whether the franchise needed a third chapter after Drishyam 2's seemingly definitive conclusion. Critics were divided. But audiences showed up anyway — driven by curiosity about Georgekutty's fate and the emotional weight of a family that has become one of Indian cinema's most beloved.

Rather than relying solely on nostalgia, the third chapter explores the long-term psychological consequences of the events that defined the family. Mohanlal himself wrote on social media: "Three films. Three chapters. One unbroken bond. Thank you for walking with Georgekutty and family."

## What This Means for NRI Audiences

Drishyam 3's overseas success is a reminder that the Indian diaspora doesn't just consume Bollywood — it actively drives box office for films in Malayalam, Tamil, Telugu, and Kannada. The ₹108 crore overseas haul suggests that theatrical distribution for Indian-language films in markets like the US, UK, Canada, and the Gulf is maturing rapidly.

Trade analysts project the film will comfortably clear ₹250 crore worldwide during its full run, with some suggesting it could challenge **Lokah Chapter One: Chandra's** ₹300 crore lifetime. Whether it gets there or not, Drishyam 3 has already proven something important: the franchise that started as a quiet Malayalam thriller about a cable operator outsmarting the police has become a global phenomenon — and the diaspora owns a bigger share of it than India itself."""
})

# -------- Article 2: ₹400 crore lawsuit over Biwi No. 1 songs --------
articles.append({
    "headline": "Vashu Bhagnani Just Filed a ₹400 Crore Lawsuit to Block Varun Dhawan's Next Film. The Fight Is Over Two 1999 Songs.",
    "subheadline": "Chunnari Chunnari and Ishq Sona Hai from Biwi No. 1 are at the centre of one of Bollywood's biggest copyright battles. Hai Jawani Toh Ishq Hona Hai releases June 5 — if the court allows it.",
    "slug": "vashu-bhagnani-400-crore-lawsuit-biwi-no-1-songs-hai-jawani-varun-dhawan-nri-20260531",
    "category": "entertainment",
    "sources": [{"name": "Bollywood Hungama"}, {"name": "India Forums"}, {"name": "Zoom TV"}, {"name": "MensXP"}],
    "person_for_image": "Varun Dhawan",
    "pexels_query": None,
    "body": """Varun Dhawan's upcoming romantic comedy **Hai Jawani Toh Ishq Hona Hai** was supposed to be a feel-good summer release. Instead, it's walking into a legal firestorm.

Veteran producer **Vashu Bhagnani's** Puja Entertainment has filed a ₹400 crore lawsuit in the Bombay High Court against **Tips Industries Limited**, producers **Ramesh Taurani** and **Kumar S Taurani**, and director **David Dhawan** over the alleged unauthorized use of two songs from the 1999 blockbuster **Biwi No. 1** — *Chunnari Chunnari* and *Ishq Sona Hai*.

The suit seeks urgent injunctive relief to restrain the release, distribution, exhibition, streaming, and commercial exploitation of the film and all promotional material featuring the disputed songs. The court has reportedly permitted filing and will hear the matter soon — potentially before the film's scheduled June 5 release date.

## What's at Stake

This isn't a routine Bollywood squabble. At ₹400 crore, it's being described as one of the largest copyright claims in Indian film history. And it strikes at the heart of a practice the industry has leaned on heavily: **remaking or remixing iconic 90s songs** to drive nostalgia-fueled marketing.

The dispute centres on who actually owns the rights to the songs. Bhagnani's lawyers argue that Tips was granted only audio rights in the original agreements from the late 1990s, not visual rights. In 2018, Tips reportedly emailed Bhagnani requesting visual rights, but the conversation never reached a resolution. Despite this, the songs were allegedly used in the new film.

Tips Industries has called the allegations "baseless," but the legal machinery is already in motion.

## The Remake Economy Under Threat

For NRI audiences who grew up on 90s Bollywood soundtracks, *Chunnari Chunnari* isn't just a song — it's a cultural touchstone. And the broader issue here will resonate with anyone who's watched Bollywood's relentless remix engine churn through classic after classic.

The lawsuit could set a precedent for how music rights from the analogue era — when agreements were simpler and less precise — are handled in the streaming age. If the court rules in Bhagnani's favour, it could complicate dozens of projects currently in production that rely on recreated versions of classic tracks.

## A Film Caught in the Crossfire

**Hai Jawani Toh Ishq Hona Hai** marks the fourth collaboration between Varun Dhawan and his father David Dhawan, following *Main Tera Hero*, *Judwaa 2*, and *Coolie No. 1*. The film also stars **Mrunal Thakur** and **Pooja Hegde**, alongside Jimmy Shergill, Chunky Panday, and Mouni Roy.

The release date has already been shuffled multiple times — originally April 2026, then June 12, briefly May 22, and finally settled on June 5. This lawsuit adds another layer of uncertainty.

Industry watchers are divided. Some believe the court is unlikely to issue a stay on a completed film just days before release, particularly when the rights ownership is contested. Others point out that Bombay High Court has previously intervened in music copyright disputes with injunctive relief.

## Why Diaspora Audiences Should Care

For Indians abroad, Bollywood's music library isn't just entertainment — it's the soundtrack of weddings, Diwali parties, and identity. The question of who owns these songs, and who can profit from them, matters beyond the courtroom. If the 90s music catalogue becomes a legal minefield, the remix-driven marketing that currently defines Bollywood releases could face a reckoning.

The hearing is expected before June 5. Whether Varun Dhawan dances to *Chunnari Chunnari* on screen or not may depend entirely on what happens in court this week."""
})

# -------- Article 3: Desi Bling Netflix debate --------
articles.append({
    "headline": "Desi Bling Is Netflix's Most Divisive Indian Show Right Now. It's Also the Most Honest.",
    "subheadline": "The reality series about ultra-wealthy Indian expats in Dubai has ignited a national debate about marriage, patriarchy, and what 'traditional values' really mean when there's gold involved.",
    "slug": "desi-bling-netflix-debate-marriage-patriarchy-dubai-indians-nri-20260531",
    "category": "entertainment",
    "sources": [{"name": "The Hollywood Reporter India"}, {"name": "India Forums"}, {"name": "Zoom TV"}, {"name": "The Tab"}],
    "person_for_image": None,
    "pexels_query": "Dubai luxury skyline night",
    "pexels_fallback": "luxury gold lifestyle",
    "body": """It starts with a foot massage in the Burj Khalifa and ends with half the internet arguing about what it means to be a good wife in 2026.

**Desi Bling**, Netflix's new reality series about ultra-wealthy Indian expats living in Dubai, premiered on May 20 with seven episodes and has since become the platform's most talked-about Indian show — not because of the Lamborghinis or the couture, but because of a woman named **Tabinda "Binda" Sanpal** and the things she said about her marriage.

In the show's opening episode, Binda — wife of billionaire businessman **Satish Sanpal**, founder of ANAX Holding — reveals that she massages her husband's feet every morning, cuts his nails, and wakes him up "like a prince." She explains it as an act of devotion rooted in Hindu tradition, adding that she believes touching her husband's feet brings wealth.

The internet lost its mind.

## The Great Marriage Debate

Social media split into two irreconcilable camps. One side defended Binda's right to express love however she chooses, arguing that personal gestures within a marriage shouldn't be policed by strangers. The other saw her comments as a public endorsement of patriarchal norms — the kind of messaging that reinforces the expectation that wives should prioritize their husband's comfort above everything else.

The debate turned Binda into Desi Bling's breakout star, which is exactly what reality television is designed to do. But the conversation it sparked touches something deeper for the Indian diaspora: the tension between "traditional values" and evolving gender norms that plays out in living rooms from Dubai to Dallas.

## Inside the Bubble

The show itself is a lavish, unapologetic look at how money, culture, and ambition collide in Dubai's Indian community. The cast includes **Karan Kundrra** and **Tejasswi Prakash** (whose on-camera proposal became a major storyline), socialites **Lailli Mirza** and **Pamela Serena** (whose pre-existing feud the producers knew about before filming), and businessman **Adil Poonawala** ("AP"), who runs a luxury car empire.

Showrunner **Marcel Dufour** and executive producer **Mazen Laham** told The Hollywood Reporter India that the show is largely unscripted — though they admitted to knowing where the drama already existed before cameras rolled. "We had no idea things would spiral as far as divorce," Marcel said, referring to cast members Dyuti and Iryna, whose marriage unravelled on camera.

The production model is controlled chaos: after filming one episode, the team builds the next one around whatever is currently exploding in the cast's lives. It's reality television at its most transparent about its own manipulation — and somehow, that honesty makes it more watchable, not less.

## The NRI Mirror

What makes Desi Bling significant for diaspora audiences isn't the wealth — it's the cultural friction it exposes. The show's cast are NRIs themselves, people who've built fortunes abroad while holding onto (or performatively displaying) Indian traditions. When Satish Sanpal describes himself as a school dropout from Jabalpur who now lives in the Burj Khalifa, it's an immigrant success story. When his wife cuts his nails on camera and calls it devotion, it becomes a referendum on what success costs.

For Indian expats watching from the US, UK, or Canada, the show holds up an unflattering but recognizable mirror: the constant negotiation between the culture you inherited and the one you live in, the way money amplifies rather than resolves those tensions, and the public performance of identity that social media has made mandatory.

## More Than Guilty Pleasure

Desi Bling is absolutely a guilty pleasure. The show peddles in "sexism, elitism, gluttony of wealth, gendered desires, and backbiting," as one review put it, "without shame or apology." But it's also the first major Indian reality show set in the diaspora that doesn't feel like a tourism ad.

Whether the debate around Binda's marriage philosophies changes any minds is beside the point. What matters is that a Netflix show about rich Indians in Dubai has become a genuine cultural conversation about gender, tradition, and the contradictions of the NRI experience.

Season 2 hasn't been announced yet. Given the numbers, it's a matter of when, not if."""
})

# ============================================================
# PUBLISH
# ============================================================

print(f"\n{'='*60}")
print(f"Entertainment Writer — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
print(f"{'='*60}\n")

published = 0

for i, art in enumerate(articles, 1):
    print(f"\n--- Article {i}: {art['headline'][:60]}... ---")
    
    # Source image
    img_url = None
    img_attribution = None
    
    if art.get('person_for_image'):
        img_url = fetch_wikipedia_person_image(art['person_for_image'])
        if img_url:
            img_attribution = "Wikimedia Commons"
    
    if not img_url and art.get('pexels_query'):
        img_url = fetch_pexels_image(art['pexels_query'], art.get('pexels_fallback'))
        if img_url:
            img_attribution = "Pexels"
    
    # Validate and upload
    final_image_url = None
    if img_url:
        # For Wikimedia thumbnail URLs, skip validation (known good) and upload directly
        if 'upload.wikimedia.org' in img_url:
            filename = f"{art['slug']}.jpg"
            uploaded = upload_to_supabase_storage(img_url, filename)
            if uploaded:
                final_image_url = uploaded
            else:
                # Wikimedia is permanent, safe to use directly
                final_image_url = img_url
        elif validate_image(img_url):
            ext = 'jpg'
            if '.png' in img_url.lower():
                ext = 'png'
            filename = f"{art['slug']}.{ext}"
            uploaded = upload_to_supabase_storage(img_url, filename)
            if uploaded:
                final_image_url = uploaded
            elif 'images.pexels.com' in img_url:
                final_image_url = img_url
        else:
            print(f"  ⚠ Image validation failed, skipping image")
    
    if not final_image_url:
        print(f"  ⚠ No valid image found for this article")
    
    # Build article record
    article_data = {
        "headline": art["headline"],
        "subheadline": art["subheadline"],
        "slug": art["slug"],
        "body": art["body"],
        "category": art["category"],
        "vertical": "entertainment",
        "sources": art["sources"],
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "image_url": final_image_url,
        "image_attribution": img_attribution
    }
    
    result = sb_insert("p2_articles", article_data)
    if result:
        art_id = result.get('id', 'unknown')
        print(f"  ✓ Published: {art['slug']} (id: {art_id})")
        published += 1
    else:
        print(f"  ✗ Failed to publish: {art['slug']}")
    
    # Small delay between articles
    time.sleep(2)

print(f"\n{'='*60}")
print(f"Done. Published {published}/{len(articles)} articles.")
print(f"{'='*60}")

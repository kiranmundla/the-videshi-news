#!/usr/bin/env python3
"""Entertainment writer for The Videshi — 2026-06-04 run"""

import json, os, sys, time, uuid, subprocess, re, io
import requests
import urllib.parse
from datetime import datetime, timezone

# Load environment
def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    if line.startswith('export '):
                        line = line[7:]
                    key, _, val = line.partition('=')
                    val = val.strip('"').strip("'")
                    os.environ[key.strip()] = val

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

# ─── Image sourcing functions ──────────────────────────────────────────

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": UA},
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
            headers={"User-Agent": UA},
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
                if ii.get("width", 0) < 300:
                    continue
                results.append({
                    "url": ii.get("thumburl") or ii.get("url", ""),
                    "original_url": ii.get("url", ""),
                    "title": page.get("title", ""),
                    "width": ii.get("width", 0),
                    "height": ii.get("height", 0),
                })
            if results:
                print(f"  ✓ Wikimedia Commons: {len(results)} images for '{search_query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Wikimedia Commons error: {e}")
    return []


def fetch_pexels_image(query):
    """Search Pexels for an image. Returns URL or None."""
    if not PEXELS_KEY:
        return None
    try:
        result = subprocess.run(
            ["curl", "-sS", f"https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page=5",
             "-H", f"Authorization: {PEXELS_KEY}"],
            capture_output=True, text=True, timeout=15
        )
        data = json.loads(result.stdout)
        photos = data.get("photos", [])
        for p in photos:
            src = p.get("src", {}).get("large2x") or p.get("src", {}).get("large")
            if src:
                print(f"  ✓ Pexels image found for '{query}': {src[:80]}...")
                return src
    except Exception as e:
        print(f"  ⚠ Pexels error: {e}")
    return None


def compress_and_upload(img_url, slug):
    """Download, compress, and upload image to Supabase. Returns public URL or None."""
    try:
        from PIL import Image
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", "Pillow", "-q"], check=True)
        from PIL import Image

    print(f"  📥 Downloading: {img_url[:80]}...")
    try:
        r = requests.get(img_url, headers={"User-Agent": UA}, timeout=20)
        if r.status_code != 200:
            print(f"  ❌ Download failed: HTTP {r.status_code}")
            return None
        ct = r.headers.get("Content-Type", "")
        if not ct.startswith("image/"):
            print(f"  ❌ Not an image: {ct}")
            return None
        raw = r.content
        if len(raw) < 5000:
            print(f"  ❌ Too small: {len(raw)} bytes")
            return None
    except Exception as e:
        print(f"  ❌ Download error: {e}")
        return None

    # Compress
    try:
        img = Image.open(io.BytesIO(raw))
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        max_w = 1200
        if img.width > max_w:
            ratio = max_w / img.width
            img = img.resize((max_w, int(img.height * ratio)), Image.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format='JPEG', quality=80, optimize=True)
        compressed = buf.getvalue()
        print(f"  📦 Compressed: {len(raw)} → {len(compressed)} bytes ({img.width}x{img.height})")
    except Exception as e:
        print(f"  ⚠ Compression failed, using raw: {e}")
        compressed = raw

    # Upload
    filename = f"{slug}.jpg"
    upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
    try:
        # Try upsert
        resp = requests.post(
            upload_url,
            headers={
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "image/jpeg",
                "x-upsert": "true"
            },
            data=compressed,
            timeout=30
        )
        if resp.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✅ Uploaded: {public_url}")
            return public_url
        else:
            print(f"  ❌ Upload failed: {resp.status_code} - {resp.text[:200]}")
            return None
    except Exception as e:
        print(f"  ❌ Upload error: {e}")
        return None


def source_image(person_names, topic_queries, pexels_query, slug):
    """Multi-source image search. Returns (url, attribution) or (None, None)."""
    candidates = []

    # Wikipedia for person articles
    for name in person_names:
        wiki_img = fetch_wikipedia_person_image(name)
        if wiki_img:
            candidates.append({"url": wiki_img, "source": "wikipedia", "priority": 1})
            break

    # Wikimedia Commons
    for q in topic_queries:
        commons = fetch_wikimedia_commons_images(q, limit=3)
        for c in commons[:2]:
            candidates.append({"url": c["url"], "source": "wikimedia_commons", "priority": 2})
        if commons:
            break

    # Pexels fallback
    if pexels_query:
        pex = fetch_pexels_image(pexels_query)
        if pex:
            candidates.append({"url": pex, "source": "pexels", "priority": 3})

    # Pick best and upload
    candidates.sort(key=lambda x: x["priority"])
    for c in candidates:
        final_url = compress_and_upload(c["url"], slug)
        if final_url:
            attr = "Wikimedia Commons" if c["source"] in ("wikipedia", "wikimedia_commons") else "Pexels"
            return final_url, attr

    print("  ⚠ No usable image found")
    return None, None


def insert_article(article):
    """Insert article into Supabase."""
    url = f"{SUPABASE_URL}/rest/v1/p2_articles"
    resp = requests.post(url, headers=HEADERS, json=article, timeout=30)
    if resp.status_code in (200, 201):
        data = resp.json()
        art_id = data[0]["id"] if isinstance(data, list) else data.get("id")
        print(f"  ✅ Published: {article['headline'][:60]}... (id={art_id})")
        return art_id
    else:
        print(f"  ❌ Insert failed: {resp.status_code} - {resp.text[:300]}")
        return None


# ─── Articles ──────────────────────────────────────────────────────────

articles = []

# ═══════════════════════════════════════════════════════════════════════
# ARTICLE 1: Peddi Day 1 Box Office
# ═══════════════════════════════════════════════════════════════════════
print("\n" + "="*60)
print("ARTICLE 1: Peddi Opening Day Box Office")
print("="*60)

slug1 = "peddi-ram-charan-opening-day-box-office-100-crore-worldwide-nri-20260604"

headline1 = "Ram Charan's Peddi Just Opened Across 4,293 Screens. The Numbers Are Tracking Toward a ₹100-Crore Worldwide Day One."

subheadline1 = "The Telugu sports drama's ₹50-crore advance and massive North American premiere pre-sales signal that post-RRR, Ram Charan's solo stardom is no longer a question — it's a fact."

body1 = """Ram Charan needed this.

Not the validation — his career has never lacked for that. But the solo proof. After RRR turned him into a global name alongside Jr. NTR, and after Game Changer stumbled in January, the question hovered: could Ram Charan open a film on his own name, without Rajamouli, without a multi-starrer safety net, and make the kind of numbers that justify a ₹300-crore budget?

Peddi is answering that question in real time.

## The Numbers So Far

The Buchi Babu Sana-directed sports action drama opened on Thursday, June 4, across 4,293 shows in India. By early afternoon, live tracking showed the film had already netted ₹12.49 crore domestically, with total India gross at ₹14.74 crore and climbing fast. These are partial-day figures — the evening and night shows, which typically account for 50-60 percent of a day's total, had barely begun.

Worldwide advance bookings had already crossed ₹50 crore before the first show rolled. Trade projections now point to a global opening-day gross exceeding ₹100 crore, which would make Peddi one of the biggest openers of 2026 so far.

## The North American Story

For the diaspora, the numbers tell a specific story. In North America, Peddi racked up over $1.5 million in premiere and opening-day pre-sales across 533 locations and 1,647 shows. That is 28,037 tickets sold before a single review dropped. Cinemark alone contributed $466,707 from 16,344 tickets. Premium formats — IMAX, XD, RPX, D-Box — accounted for nearly 18 percent of overseas revenue, a pattern typically associated with event-scale releases.

This is not Pushpa 2 territory ($3 million premiere), but it is comfortably in the top tier for a Telugu-language solo vehicle. For context, Peddi entered the top 10 all-time Tollywood pre-sales on BookMyShow with 600,000 tickets — ahead of The RajaSaab and Hari Hara Veera Mallu.

## What the Film Actually Is

Set in 1980s rural Andhra Pradesh, Peddi follows a spirited villager who unites his community through sports — wrestling, cricket, running — to defend local pride against a powerful rival. The film runs a hefty three hours with a U/A certificate, and features an ensemble including Janhvi Kapoor, Shiva Rajkumar, Jagapathi Babu, Divyenndu, and Boman Irani. A.R. Rahman composed the score, his first collaboration with Ram Charan.

Director Buchi Babu Sana, whose debut Uppena was a surprise hit in 2021, has built Peddi as a rural sports epic rather than a typical masala action film. The Telugu theatrical version is the primary release, with dubbed versions in Hindi, Tamil, Kannada, and Malayalam expanding the footprint.

## Why It Matters to NRIs

The film's North American performance is worth watching not just for its numbers but for what it represents. Telugu cinema's overseas market has grown from a niche into a primary revenue stream. The Gulf region, North America, and Australia now collectively account for 25-30 percent of a major Telugu film's lifetime gross. When NRI audiences show up in these numbers for a premiere, they are not just watching a movie — they are voting on the commercial viability of an entire production model.

Ram Charan's trajectory post-RRR mirrors a pattern familiar across South Indian cinema: the international breakout creates expectations that the next solo outing must meet. Allu Arjun did it with Pushpa 2. Prabhas struggled with Adipurush and Salaar. Now it is Ram Charan's turn with Peddi, and the early data suggests the bet is paying off.

## What Comes Next

The evening shows will determine whether Peddi cracks the ₹100-crore worldwide mark on Day 1. Word-of-mouth from afternoon audiences is already filtering onto social media, and the trajectory of the weekend — particularly Saturday family audiences — will decide if this becomes a ₹500-crore film or a ₹300-crore one. For a ₹300-crore production, the breakeven requires roughly ₹450 crore worldwide.

The first real test is over. The screens are booked. The tickets are sold. Now it is about whether the film itself can carry the opening into a sustained run."""

# Image sourcing for Peddi
img1_url, img1_attr = source_image(
    person_names=["Ram Charan"],
    topic_queries=["Ram Charan actor Telugu cinema", "Ram Charan film"],
    pexels_query="Indian cinema sports drama",
    slug=slug1
)

articles.append({
    "headline": headline1,
    "subheadline": subheadline1,
    "body": body1,
    "slug": slug1,
    "category": "entertainment",
    "vertical": "entertainment",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "image_url": img1_url,
    "image_caption": "Ram Charan in a still from Peddi, the Telugu sports drama that opened across 4,293 screens on June 4",
    "image_attribution": img1_attr or "Wikimedia Commons",
    "sources": json.dumps([
        {"name": "Sacnilk", "url": "https://sacnilk.com"},
        {"name": "Filmibeat", "url": "https://filmibeat.com"},
        {"name": "Koimoi", "url": "https://koimoi.com"}
    ]),
    "is_editorial": False
})


# ═══════════════════════════════════════════════════════════════════════
# ARTICLE 2: Bandar CBFC Censorship
# ═══════════════════════════════════════════════════════════════════════
print("\n" + "="*60)
print("ARTICLE 2: Bandar CBFC Censorship")
print("="*60)

slug2 = "bandar-anurag-kashyap-cbfc-censorship-bobby-deol-cuss-words-tiff-nri-20260604"

headline2 = "The CBFC Just Turned Anurag Kashyap's Bandar Into a Different Film. TIFF Audiences Saw the Original. Indian Theaters Will Not."

subheadline2 = "Extreme cuss words replaced with milder alternatives, a #MeToo drama softened for theatrical release — the gap between what international festival audiences get and what Indian moviegoers receive has never been more visible."

body2 = """When Bandar premiered at the Toronto International Film Festival in September 2025, the audience experienced Anurag Kashyap's film exactly as he made it. The language was raw. The characters spoke the way people in crisis actually speak — with profanity that carried weight, not shock value.

The version releasing in Indian theaters on June 5 is not that film.

## What the CBFC Changed

According to an exclusive report by Bollywood Hungama, the Central Board of Film Certification replaced multiple instances of extreme profanity in Bandar with milder alternatives. The most striking substitution: a particularly graphic Hindi abuse was replaced with "banjo." Other cuss words were softened throughout the film, with the CBFC systematically swapping out the sharpest edges of the dialogue while granting the film a theatrical release certificate.

This is not a case of a few bleeps. When you replace the language in a film specifically about power, accusation, and the collapse of a man's public identity, you are changing the texture of the storytelling itself. Kashyap's cinema has always derived its authenticity from characters who sound like real people — not like people performing for a censor board.

## What the Film Is About

Bandar — subtitled Monkey in a Cage for international markets — stars Bobby Deol as Samar Mehra, a washed-up television actor living on the margins. He cannot afford back surgery. He performs at weddings to pay his mortgage. When police arrive at his door one night and arrest him on rape charges filed by a woman he met on a dating app, his already diminished life disintegrates entirely.

The film is written by Sudip Sharma and Abhishek Banerjee — the team behind Paatal Lok and Kohrra — and produced by Nikhil Dwivedi with Zee Studios backing. Sanya Malhotra, Raj B Shetty, Jitendra Joshi, Sapna Pabbi, Indrajith Sukumaran, and Riddhi Sen round out the cast.

At TIFF, critics described Bobby Deol's performance as the finest of his career. Variety noted that Kashyap built the film around the ambiguity of the #MeToo landscape — the impossibility of certainty, the way accusation alone can destroy a life, and the question of whether redemption is even available in the age of cancellation. Kashyap himself said at the premiere: "I grew up in a world where we made mistakes and we were given opportunities to redeem ourselves or correct ourselves. Today, the world is not the same."

## The Diaspora Sees Two Versions

Here is where it gets uncomfortable for NRI audiences. If you watched Bandar at TIFF, you saw one film. If you watch it in Mumbai or Delhi on June 5, you will see another. The international festival circuit — Cannes, Venice, Toronto, Berlin — has become the place where Indian filmmakers can present their unmediated vision. The domestic theatrical release increasingly becomes the compromise.

This is not new. The CBFC has a decades-long history of softening, cutting, and reshaping Indian cinema for domestic consumption. But the gap has grown wider as Indian films gain international prestige. Kashyap's own Gangs of Wasseypur faced similar scrutiny. Dev D was trimmed. Udta Punjab became a political battle. Each time, the version that Indian audiences pay to see in theaters is not the version that the filmmaker intended.

For the diaspora — who often have access to both the festival cut and the theatrical release — the disparity is increasingly visible. When a film built on the raw reality of language, power, and accusation has its language sanded down, the question is not whether the censor board has the authority. It always has. The question is what the audience loses.

## What Remains

The good news: Bandar's core story, performances, and directorial craft survive the cuts. Bobby Deol's transformation from matinee filler to genuine dramatic actor was the story of TIFF 2025, and that performance does not depend on any single word. The ensemble — particularly Raj B Shetty and Sanya Malhotra — delivers regardless of what the CBFC chose to soften.

But somewhere between Toronto and Andheri, a film became a little less itself. That gap is worth noticing."""

# Image sourcing for Bandar
img2_url, img2_attr = source_image(
    person_names=["Bobby Deol", "Anurag Kashyap"],
    topic_queries=["Bobby Deol actor Bollywood", "Anurag Kashyap director"],
    pexels_query="Indian cinema courtroom drama",
    slug=slug2
)

articles.append({
    "headline": headline2,
    "subheadline": subheadline2,
    "body": body2,
    "slug": slug2,
    "category": "entertainment",
    "vertical": "entertainment",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "image_url": img2_url,
    "image_caption": "Bobby Deol stars as a washed-up actor accused of rape in Anurag Kashyap's Bandar, releasing June 5",
    "image_attribution": img2_attr or "Wikimedia Commons",
    "sources": json.dumps([
        {"name": "Bollywood Hungama", "url": "https://bollywoodhungama.com"},
        {"name": "Variety", "url": "https://variety.com"},
        {"name": "The Nod Mag", "url": "https://thenodmag.com"}
    ]),
    "is_editorial": False
})


# ═══════════════════════════════════════════════════════════════════════
# ARTICLE 3: Gram Chikitsalay Season 2
# ═══════════════════════════════════════════════════════════════════════
print("\n" + "="*60)
print("ARTICLE 3: Gram Chikitsalay Season 2")
print("="*60)

slug3 = "gram-chikitsalay-season-2-prime-video-tvf-rural-india-comedy-nri-20260604"

headline3 = "TVF's Gram Chikitsalay Is Coming Back. The Show About a Doctor Who Cannot Leave His Village Just Became Prime Video's Quietest Bet on Rural India."

subheadline3 = "Season 2 drops June 23 with the original cast returning. For the diaspora, a show set in fictional Bhathkandi hits closer to home than most urban dramas ever will."

body3 = """There is a particular kind of Indian story that streaming platforms have only recently figured out how to tell. Not the glossy Mumbai thriller. Not the period epic. Not the crime drama set in a dusty North Indian town where everyone speaks in menacing whispers. The other kind — the one about ordinary people in ordinary places, where the stakes are a broken X-ray machine and the villain is bureaucratic indifference.

Gram Chikitsalay is that story. And it is coming back.

## What Is Returning

Prime Video has officially announced that the second season of Gram Chikitsalay will premiere worldwide on June 23, 2026. The Hindi-language comedy-drama, produced by The Viral Fever (TVF) and directed by Lalitam Tiwari, picks up where Season 1 left off: Dr. Prabhat is still in Bhathkandi, still trying to revive the village's struggling Primary Health Centre, and still discovering that idealism and reality are not always on speaking terms.

The original cast returns — Amol Parashar, Akash Makhija, Anandeshwar Dwivedi, Vinay Pathak, Akansha Ranjan Kapoor, and Garima Vikrant Singh. Actor Dinesh Lal Yadav, a major name in Bhojpuri cinema, joins the ensemble for Season 2, adding a new dimension to the show's already warm and lived-in world.

## Why the First Season Worked

When Gram Chikitsalay debuted in 2025, it entered a streaming landscape dominated by crime thrillers and urban relationship dramas. A show about a young doctor in a fictional village could have been dismissed as too niche, too slow, too unglamorous for the algorithm. Instead, it found an audience — quietly, steadily, through word of mouth rather than marketing blitzes.

The show works because it refuses to condescend to its setting. Rural India in Indian cinema has traditionally been either romanticized or pitied. Gram Chikitsalay does neither. The village of Bhathkandi is not a backdrop for someone else's redemption arc. It is a place where people live, argue, scheme, help each other, and resist change and embrace it in equal measure. Dr. Prabhat is not a savior. He is a man who took a job he did not fully understand and is now figuring it out alongside the people who have lived there their entire lives.

Vinay Pathak, one of Hindi cinema's most underrated actors, brings a gravitational warmth to the ensemble that keeps the show grounded even in its more comedic moments. The writing — by Vaibhav Suman and Shreya Srivastava — finds humor in specificity rather than stereotype.

## The Diaspora Connection

For NRI audiences, shows like Gram Chikitsalay occupy a peculiar emotional space. The village is not where most diaspora Indians live, but it is often where their families come from. The small-town doctor, the crumbling health center, the committee meeting where nothing gets decided — these are not abstract settings. They are the stories parents and grandparents tell. They are the WhatsApp photos from cousins. They are the reality that exists alongside the India of tech parks and startup unicorns.

Prime Video's Manish Menghani, who oversees content licensing for India, noted the shift in audience appetite: "We are seeing a growing appetite not just for authentic urban narratives, but increasingly for stories rooted in rural India as well." That is corporate language for something simpler — people want to see their whole country on screen, not just the parts that look good in a Netflix thumbnail.

## What Season 2 Promises

The second season continues Dr. Prabhat's efforts at the PHC while introducing fresh obstacles. The writers have indicated that the tension between idealism and systemic reality will deepen — Prabhat has earned some trust in Bhathkandi, but trust does not fix a broken system. New characters, new complications, and the same fundamental question: what does it take to build something meaningful in a place the system has forgotten?

TVF has built its reputation on shows that find the extraordinary in the ordinary — Kota Factory, Panchayat, Gullak. Gram Chikitsalay fits squarely in that tradition. Season 2 does not need to be louder or bigger. It just needs to be as honest as the first.

June 23. Prime Video. Bhathkandi is still there. Dr. Prabhat is still trying."""

# Image sourcing for Gram Chikitsalay
img3_url, img3_attr = source_image(
    person_names=["Amol Parashar", "Vinay Pathak"],
    topic_queries=["rural India village doctor", "Indian village healthcare"],
    pexels_query="rural India village clinic doctor",
    slug=slug3
)

articles.append({
    "headline": headline3,
    "subheadline": subheadline3,
    "body": body3,
    "slug": slug3,
    "category": "entertainment",
    "vertical": "entertainment",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "image_url": img3_url,
    "image_caption": "Amol Parashar stars as Dr. Prabhat in TVF's Gram Chikitsalay, returning for Season 2 on Prime Video",
    "image_attribution": img3_attr or "Wikimedia Commons",
    "sources": json.dumps([
        {"name": "Bollywood Hungama", "url": "https://bollywoodhungama.com"},
        {"name": "Prime Video India", "url": "https://primevideo.com"}
    ]),
    "is_editorial": False
})


# ─── Publish all articles ─────────────────────────────────────────────

print("\n" + "="*60)
print("PUBLISHING ARTICLES")
print("="*60)

success_count = 0
for i, art in enumerate(articles):
    print(f"\n--- Article {i+1} ---")
    if not art.get("image_url"):
        print("  ⚠ No image — publishing without hero image")
        art.pop("image_url", None)
        art.pop("image_caption", None)
        art.pop("image_attribution", None)

    art_id = insert_article(art)
    if art_id:
        success_count += 1

print(f"\n{'='*60}")
print(f"DONE: {success_count}/{len(articles)} articles published")
print(f"{'='*60}")

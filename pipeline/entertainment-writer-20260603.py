#!/usr/bin/env python3
"""Entertainment writer for The Videshi — 2026-06-03 batch"""

import os, json, sys, time, uuid, re, traceback
import requests
from datetime import datetime, timezone

# ── Load env ──
def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                key, val = line.split('=', 1)
                key = key.replace('export ', '').strip()
                val = val.strip().strip('"').strip("'")
                os.environ[key] = val

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.supabase'))
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

UA = {"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}

# ── Image sourcing functions ──

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    import urllib.parse
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers=UA,
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
    import urllib.parse
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
            headers=UA,
            timeout=15
        )
        if r.status_code == 200:
            data = r.json()
            pages = data.get("query", {}).get("pages", {})
            results = []
            for pid, page in pages.items():
                ii = page.get("imageinfo", [{}])[0]
                mime = ii.get("mime", "")
                if not mime.startswith("image/"):
                    continue
                if mime == "image/svg+xml" or ii.get("width", 0) < 300:
                    continue
                results.append({
                    "url": ii.get("thumburl") or ii.get("url", ""),
                    "original_url": ii.get("url", ""),
                    "title": page.get("title", ""),
                    "width": ii.get("width", 0),
                    "height": ii.get("height", 0),
                    "mime": mime
                })
            if results:
                print(f"  ✓ Wikimedia Commons: {len(results)} images for '{search_query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Wikimedia Commons error: {e}")
    return []


def fetch_pexels_image(*queries):
    """Search Pexels for a relevant image. Returns URL or None."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    for q in queries:
        try:
            import subprocess
            result = subprocess.run(
                ["curl", "-sS", "-H", f"Authorization: {PEXELS_KEY}",
                 f"https://api.pexels.com/v1/search?query={requests.utils.quote(q)}&per_page=3&orientation=landscape"],
                capture_output=True, text=True, timeout=15
            )
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            if photos:
                url = photos[0].get("src", {}).get("large2x") or photos[0].get("src", {}).get("original")
                if url:
                    print(f"  ✓ Pexels image for '{q}': {url[:60]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None


def upload_image_to_supabase(image_url, filename):
    """Download image and upload to Supabase storage bucket 'article-images'."""
    try:
        print(f"  Downloading image: {image_url[:80]}...")
        r = requests.get(image_url, headers=UA, timeout=20)
        if r.status_code != 200:
            print(f"  ⚠ Download failed: HTTP {r.status_code}")
            return None
        
        content_type = r.headers.get('Content-Type', 'image/jpeg')
        if not content_type.startswith('image/'):
            content_type = 'image/jpeg'
        
        img_data = r.content
        if len(img_data) < 5000:
            print(f"  ⚠ Image too small ({len(img_data)} bytes), skipping")
            return None
        
        print(f"  Uploading {filename} ({len(img_data)} bytes) to Supabase...")
        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
        upload_r = requests.post(
            upload_url,
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": content_type,
                "x-upsert": "true"
            },
            data=img_data,
            timeout=30
        )
        
        if upload_r.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to: {public_url[:70]}...")
            return public_url
        else:
            print(f"  ⚠ Upload failed: HTTP {upload_r.status_code} {upload_r.text[:200]}")
            return None
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
        return None


def validate_image_url(url):
    """Check that URL returns a valid image."""
    try:
        r = requests.head(url, headers=UA, timeout=10, allow_redirects=True)
        ct = r.headers.get('Content-Type', '')
        cl = int(r.headers.get('Content-Length', 0))
        if 'image' in ct and cl > 5000:
            return True
        # Try GET for servers that don't support HEAD
        r = requests.get(url, headers=UA, timeout=10, stream=True)
        ct = r.headers.get('Content-Type', '')
        cl = int(r.headers.get('Content-Length', 0))
        return 'image' in ct and cl > 5000
    except:
        return False


def source_image(person_name, topic_terms, slug):
    """Multi-source image search: Wikipedia → Wikimedia Commons → Pexels. Upload best to Supabase."""
    candidates = []
    
    # Source 1: Wikipedia (for person articles)
    if person_name:
        wiki_img = fetch_wikipedia_person_image(person_name)
        if wiki_img:
            candidates.append({"url": wiki_img, "source": "wikipedia", "relevance": 3})
    
    # Source 2: Wikimedia Commons
    search_terms = f"{person_name} {topic_terms}" if person_name else topic_terms
    commons = fetch_wikimedia_commons_images(search_terms)
    if not commons and person_name:
        commons = fetch_wikimedia_commons_images(person_name)
    for c in commons[:2]:
        candidates.append({"url": c["url"], "source": "wikimedia_commons", "relevance": 2})
    
    # Source 3: Pexels
    pexels_img = fetch_pexels_image(topic_terms)
    if pexels_img:
        candidates.append({"url": pexels_img, "source": "pexels", "relevance": 1})
    
    # Sort by relevance (highest first)
    candidates.sort(key=lambda x: x["relevance"], reverse=True)
    
    # Try uploading best candidate to Supabase
    for cand in candidates:
        filename = f"{slug}.jpg"
        result = upload_image_to_supabase(cand["url"], filename)
        if result:
            attribution = "Wikimedia Commons" if cand["source"] in ("wikipedia", "wikimedia_commons") else "The Videshi"
            return result, attribution
    
    print("  ⚠ No suitable image found from any source")
    return None, None


def insert_article(article):
    """Insert article into p2_articles."""
    url = f"{SUPABASE_URL}/rest/v1/p2_articles"
    r = requests.post(url, headers=HEADERS, json=article, timeout=30)
    if r.status_code in (200, 201):
        data = r.json()
        if isinstance(data, list) and data:
            art_id = data[0].get('id', 'unknown')
            print(f"  ✓ Published: {article['headline'][:60]}... (id: {art_id})")
            return art_id
        print(f"  ✓ Published: {article['headline'][:60]}...")
        return True
    else:
        print(f"  ✗ FAILED ({r.status_code}): {r.text[:300]}")
        return None


# ═══════════════════════════════════════════════════════
# ARTICLE 1: Ram Charan's Peddi — Telugu Mega Release
# ═══════════════════════════════════════════════════════

def write_peddi_article():
    print("\n" + "="*60)
    print("ARTICLE 1: Ram Charan's Peddi")
    print("="*60)
    
    slug = "ram-charan-peddi-june-4-advance-booking-north-america-telugu-diaspora-nri-20260603"
    headline = "Ram Charan's Peddi Opens Tomorrow With ₹40 Crore in Global Pre-Sales. North America Alone Is Closing in on a Million Dollars."
    subheadline = "Buchi Babu Sana's sports-action drama has sold 28,000 tickets across 533 US locations before a single screening. For the Telugu diaspora, this isn't just a movie — it's a Thursday night pilgrimage."
    
    body = """The numbers were still climbing when the trackers stopped counting.

As of Tuesday night, Ram Charan's *Peddi* had crossed ₹40 crore in worldwide advance bookings for its premiere and opening day, with projections suggesting the final tally could push past ₹50 crore before the first show lights up on June 4. In North America alone, the film had pulled in $784,611 from 533 locations and 1,647 shows — roughly 28,000 tickets sold — and was closing in on the $1 million premiere pre-sales milestone with two days still to go.

The figures tell a familiar story about Telugu cinema's relationship with its diaspora, but the details matter. Cinemark has emerged as the biggest contributor at $466,707 from over 16,000 tickets, followed by Regal at $160,766. Premium formats — XD, RPX, D-Box, and other PLF screens — have collectively added nearly $280,000, a trend trade analysts typically associate with "event releases" rather than standard fare. At one point, BookMyShow reported that over 40,000 tickets were being sold per hour in the Telugu states.

## The Film Behind the Frenzy

*Peddi* is Buchi Babu Sana's second directorial after the critically acclaimed *Uppena* (2021), and it represents the kind of bet that only works when every variable aligns. Ram Charan plays Peddi Raju, a daily-wage construction worker in rural Andhra Pradesh whose natural athletic gift becomes a source of pride — and conflict — for his community. Janhvi Kapoor stars opposite him as Achiyamma, with Shiva Rajkumar, Jagapathi Babu, Divyenndu Sharma, and Boman Irani rounding out an ensemble that spans languages and industries.

The music, composed by A.R. Rahman, has already made its mark. The track "Hellallallo," featuring a special appearance by Shruti Haasan, launched at a massive concert in Bhopal on June 3 that doubled as a promotional event and a cultural gathering. Rahman performing live alongside Ram Charan in central India — not Hyderabad, not a metro — was a deliberate signal about the film's ambitions beyond the Telugu heartland.

## Why the Diaspora Is Watching

For the roughly four million Telugu-speaking NRIs in North America, a Ram Charan release has become what an IPL final is for cricket fans — a communal experience that happens in real time, in theaters, with friends and family. The advance booking patterns reflect this. Standard screens contributed $505,045, but the premium format numbers suggest families are willing to pay more for the experience.

The Telangana market, notably, has been slower to open due to pending ticket price approvals — a regulatory wrinkle that has suppressed what could have been even larger pre-sale figures. Trade analysts point out that *Peddi* is still trailing Ram Charan's previous release *Game Changer*, which hit ₹26 crore in advance bookings for its Sankranti release window. But *Game Changer* had the benefit of festival timing and ultimately underperformed at the box office. *Peddi* is launching mid-week, without a holiday buffer, which makes its advance numbers more telling.

## What Comes Next

The film releases across Telugu, Tamil, Hindi, and other Indian language markets simultaneously on June 4. With a reported production budget of ₹350 crore, the pressure to perform is significant — but the pre-release theatrical business has already de-risked much of the investment through territory rights and overseas distribution deals.

For the Telugu diaspora planning their Thursday evening, the math is simple: *Peddi* is the biggest Telugu release since *Pushpa 2*, the tickets are moving fast, and the premium seats are going first. The reviews will come Friday morning. The community will have its verdict Thursday night.

*Sources: Sacnilk, Zoom TV, Venky Box Office, Filmfare, Bollywood Hungama*"""
    
    # Source image
    img_url, img_attr = source_image("Ram Charan", "Ram Charan Telugu movie Peddi", slug)
    
    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "entertainment",
        "vertical": "entertainment",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "source_urls": json.dumps([
            "https://www.herzindagi.com",
            "https://www.zoomtventertainment.com",
            "https://www.sacnilk.com",
            "https://www.filmibeat.com"
        ]),
        "is_editorial": False,
        "image_url": img_url or "",
        "image_attribution": img_attr or ""
    }
    
    return insert_article(article)


# ═══════════════════════════════════════════════════════
# ARTICLE 2: Aamir Khan Marrying Gauri Spratt
# ═══════════════════════════════════════════════════════

def write_aamir_marriage_article():
    print("\n" + "="*60)
    print("ARTICLE 2: Aamir Khan & Gauri Spratt Marriage")
    print("="*60)
    
    slug = "aamir-khan-gauri-spratt-marriage-july-5-third-wedding-bollywood-nri-20260603"
    headline = "Aamir Khan Will Marry Gauri Spratt on July 5. No Reception. No Spectacle. Just a Signing at Home."
    subheadline = "The actor's third marriage will be a registered ceremony at his residence, attended by family and a handful of friends. Gauri's grandfather was a British Communist who fought for Indian independence. Some love stories don't need a three-act structure."
    
    body = """Aamir Khan is getting married again. And this time, he appears to have no interest in making it a production.

According to multiple reports published on June 3 — including from Filmfare, India Today, and Bollywood Hungama, all citing sources close to the family — the 60-year-old actor will marry his partner Gauri Spratt in a private registered ceremony at his Mumbai residence on July 5. The guest list is reportedly limited to immediate family and a small circle of close friends. There will be no grand reception. No industry function. No destination wedding.

"Aamir and Gauri have been living together as a family for a little over a year now," a source told Filmfare. "They have built a happy, stable life together and simply decided to mark it formally with their families present."

## The Backstory

Gauri Spratt, 47, is not from the film industry. She is the mother of a seven-year-old son, Quinn, from a previous marriage, and has known Aamir for approximately 25 years — a friendship that evolved into something deeper only recently. Aamir publicly introduced her during his 60th birthday celebrations in March 2025, surprising even close industry colleagues who had not been aware of the relationship.

In a recent interview with Screen (Indian Express), Aamir confirmed the seriousness of their bond with characteristic directness: "Gauri and I are really serious about each other and we are in a very committed space. We are partners. We are together." When asked about formalizing the relationship, he added: "In my heart, I'm already married to her. So whether we formalize it or not is something that I will decide as we go along."

He has, apparently, decided.

## A Family History That Reads Like a Novel

What makes this story resonate beyond the celebrity gossip cycle is Gauri's family history. Her grandfather was Philip Spratt, a British-born Communist who arrived in India in the 1920s, was arrested in the Meerut Conspiracy Case of 1929 alongside prominent Indian labor leaders, and spent years in prison for his role in organizing the Indian working class. He eventually settled in India permanently, choosing the country's cause over his own homeland.

There is something quietly fitting about his granddaughter now making India her home in the most personal sense — marrying one of its most recognizable citizens, in a private ceremony, with no cameras and no fanfare.

## For the Diaspora, a Different Kind of Celebrity Marriage

Aamir was previously married to Reena Dutta, his first wife with whom he has two children — Junaid and Ira Khan. That marriage ended in 2002. He then married filmmaker Kiran Rao in 2005, and the two co-parented their son Azad before announcing their separation in 2021.

For the Indian diaspora, Aamir's personal life has always drawn attention not because it is scandalous but because it is unconventional. A three-time married Bollywood superstar who prefers a quiet home ceremony over a Jodhpur palace — who introduces his partner to the press during a birthday celebration rather than through a coordinated PR campaign — is a different kind of celebrity story.

Industry sources suggest Shah Rukh Khan and Salman Khan may attend the ceremony, though no guest list has been officially confirmed. Neither Aamir nor Gauri has commented publicly on the reports.

The wedding, if it proceeds as described, will be everything a Bollywood wedding usually is not: small, quiet, and entirely on their own terms.

*Sources: Filmfare, Bollywood Hungama, India Today, LatestLY, IANS*"""
    
    # Source image
    img_url, img_attr = source_image("Aamir Khan", "Aamir Khan Bollywood actor", slug)
    
    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "entertainment",
        "vertical": "entertainment",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "source_urls": json.dumps([
            "https://www.filmfare.com",
            "https://www.bollywoodhungama.com",
            "https://www.latestly.com",
            "https://www.indiaforums.com"
        ]),
        "is_editorial": False,
        "image_url": img_url or "",
        "image_attribution": img_attr or ""
    }
    
    return insert_article(article)


# ═══════════════════════════════════════════════════════
# ARTICLE 3: Kangana Ranaut's Bharat Bhhagya Viddhaata
# ═══════════════════════════════════════════════════════

def write_kangana_article():
    print("\n" + "="*60)
    print("ARTICLE 3: Kangana Ranaut / Bharat Bhhagya Viddhaata")
    print("="*60)
    
    slug = "kangana-ranaut-bharat-bhhagya-viddhaata-26-11-cama-hospital-trailer-nri-20260603"
    headline = "Kangana Ranaut Plays a Nurse Who Saved 400 Lives During 26/11. The Trailer Just Dropped. The Film Opens June 12."
    subheadline = "Bharat Bhhagya Viddhaata tells the story of the Cama Hospital staff who held the line while Mumbai burned. For the diaspora, 26/11 is not history — it is a wound. This film chooses to show the people who stitched it."
    
    body = """The trailer for *Bharat Bhhagya Viddhaata* dropped on June 2, and it does something that most 26/11 films have not attempted. It ignores the terrorists. It ignores the commandos. It ignores the politicians and the anchors and the phone calls from burning hotels. Instead, it walks into Cama Hospital and stays there, telling the story of the nurses, ward boys, cleaners, lift operators, and security guards who kept nearly 400 people alive while two gunmen roamed the corridors.

Kangana Ranaut plays the lead — a staff nurse who is overlooked at home and occasionally dismissed by her patients, until the night of November 26, 2008, when her quiet competence becomes the difference between life and death. It is, by all appearances, the kind of role that Kangana has spent the last few years arguing she deserves: complex, grounded, and built on stillness rather than spectacle.

## A Film Originally Called "Nurses of Cama"

The project began under a different name. Director Manoj Tapadia had initially titled it *Nurses of Cama*, a straightforward description of its subject. But when Kangana came aboard — as both lead actress and co-producer — she pushed for a title that reflected the film's larger theme. "When we heard the story, I felt it reflects the spirit of India," she explained at the trailer launch. "The title should be Bharat Bhhagya Viddhaata."

There was a complication. The title had already been registered by John Abraham. Kangana called him directly. Within a day, Abraham released the rights without charging a single rupee. "I was told that often people don't give away a title so easily," Kangana said at the event, adding a rare note of public gratitude toward a colleague.

## What the Diaspora Remembers

For Indians living abroad, particularly those in the US, UK, and Canada, the 26/11 attacks occupy a specific place in collective memory. It was not the first terror attack on Indian soil, but it was the first one that played out in real time on global television, in a city that many NRIs had personal ties to. The Taj, the Oberoi, CST station — these were not abstract locations. They were places people had stayed in, walked through, eaten at.

Cama Hospital, by contrast, was barely mentioned in the international coverage. The staff who barricaded doors, moved patients to upper floors, switched off lights to avoid detection, and kept the wounded stable through the night did so in near-total obscurity. Most of their names never made the papers.

*Bharat Bhhagya Viddhaata* aims to change that. The film features an ensemble cast — Girija Oak, Smita Tambe, Amrutha Namdev, Esha Dey, Priya Berde, Asha Shelar, and Suhita Thatte — that represents the backbone of Marathi and Hindi cinema's character actor tradition. The casting is deliberate: these are not glamorous faces, but they are the kind of actors who make you believe a story.

## Kangana's Complicated Return

This is Kangana Ranaut's first significant theatrical release since *Emergency* and her entry into active politics as a BJP Member of Parliament from Mandi. Her political career has been polarizing, and the overlap between her public persona and her film career has made every release a cultural event of a different kind.

At the trailer launch, she steered the conversation back to the material: "So many of us make the mistake of underestimating the power of ordinary people capable of extraordinary courage. The will to stand your ground in the face of fear, the instinct to serve humanity — all of that comes from within."

The film is presented by PEN Studios and produced by Kangana's Manikarnika Films alongside Paramhans Creations, Eunoia Films, and Floating Rocks Entertainment. It releases in cinemas on June 12 — the same date as the *Lagaan* 25th anniversary re-release and Diljit Dosanjh's *Main Vaapas Aaunga*, making for one of the most crowded Thursdays in recent memory.

Whether it finds its audience in that traffic will depend on word of mouth. But the story it tells — of ordinary people who did not run — has always been worth telling.

*Sources: Bollywood Hungama, Zoom TV, IANS, Sacnilk, Filmfare*"""
    
    # Source image
    img_url, img_attr = source_image("Kangana Ranaut", "Kangana Ranaut actress Bollywood", slug)
    
    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "entertainment",
        "vertical": "entertainment",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "source_urls": json.dumps([
            "https://www.bollywoodhungama.com",
            "https://www.zoomtventertainment.com",
            "https://www.ianslive.in",
            "https://www.sacnilk.com"
        ]),
        "is_editorial": False,
        "image_url": img_url or "",
        "image_attribution": img_attr or ""
    }
    
    return insert_article(article)


# ═══════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════

if __name__ == "__main__":
    print(f"Entertainment Writer — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"Supabase URL: {SUPABASE_URL[:40]}...")
    
    results = []
    
    for writer_fn in [write_peddi_article, write_aamir_marriage_article, write_kangana_article]:
        try:
            result = writer_fn()
            results.append(result)
        except Exception as e:
            print(f"\n✗ ERROR: {e}")
            traceback.print_exc()
            results.append(None)
    
    successes = sum(1 for r in results if r)
    print(f"\n{'='*60}")
    print(f"Done. Published {successes}/{len(results)} articles.")
    print(f"{'='*60}")

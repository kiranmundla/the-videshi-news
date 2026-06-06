#!/usr/bin/env python3
"""Entertainment writer for The Videshi — 2026-06-06 batch"""

import json, os, sys, time, uuid, re, subprocess, io
from datetime import datetime, timezone

import requests
from PIL import Image

# ── env ──
def source_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            k, v = line.split('=', 1)
            k = k.replace('export ', '').strip()
            v = v.strip().strip('"').strip("'")
            os.environ[k] = v

source_env(os.path.expanduser('~/.env.supabase'))
source_env(os.path.expanduser('~/workspace/.env.supabase'))
source_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')
UA = "TheVideshi/1.0 (thevideshi.com)"

HEADERS_SB = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

# ── Image helpers ──
def fetch_wikipedia_person_image(person_name):
    """Fetch actual photo from Wikipedia. Returns URL or None."""
    import urllib.parse
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": UA}, timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            # Prefer thumbnail (330px, reliable) over original (may 429)
            img = data.get("thumbnail", {}).get("source") or data.get("originalimage", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia error for '{person_name}': {e}")
    return None


def fetch_wikimedia_commons(query, limit=5):
    """Search Wikimedia Commons. Returns list of dicts with url, title."""
    try:
        r = requests.get(
            "https://commons.wikimedia.org/w/api.php",
            params={
                "action": "query", "generator": "search",
                "gsrsearch": query, "gsrnamespace": "6", "gsrlimit": str(limit),
                "prop": "imageinfo", "iiprop": "url|size|mime",
                "iiurlwidth": "1200", "format": "json"
            },
            headers={"User-Agent": UA}, timeout=15
        )
        if r.status_code == 200:
            pages = r.json().get("query", {}).get("pages", {})
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
                    "width": ii.get("width", 0)
                })
            if results:
                print(f"  ✓ Commons: {len(results)} images for '{query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Commons error: {e}")
    return []


def fetch_pexels(query):
    """Fetch best Pexels image via curl. Returns URL or None."""
    if not PEXELS_KEY:
        return None
    try:
        result = subprocess.run([
            'curl', '-sS', '-H', f'Authorization: {PEXELS_KEY}',
            f'https://api.pexels.com/v1/search?query={requests.utils.quote(query)}&per_page=3'
        ], capture_output=True, text=True, timeout=15)
        data = json.loads(result.stdout)
        photos = data.get('photos', [])
        if photos:
            url = photos[0]['src']['large2x']
            print(f"  ✓ Pexels image for '{query}': {url[:60]}...")
            return url
    except Exception as e:
        print(f"  ⚠ Pexels error: {e}")
    return None


def compress_image(img_bytes, max_width=1200, quality=80):
    """Resize and compress to JPEG."""
    img = Image.open(io.BytesIO(img_bytes))
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=quality, optimize=True)
    return buf.getvalue()


def download_and_upload(image_url, slug):
    """Download image, compress, upload to Supabase article-images bucket. Returns public URL."""
    try:
        r = requests.get(image_url, headers={"User-Agent": UA}, timeout=20)
        if r.status_code != 200:
            print(f"  ⚠ Download failed ({r.status_code}): {image_url[:60]}")
            return None
        ct = r.headers.get('Content-Type', '')
        if not ct.startswith('image/'):
            print(f"  ⚠ Not an image: {ct}")
            return None
        if len(r.content) < 5000:
            print(f"  ⚠ Too small ({len(r.content)} bytes)")
            return None

        compressed = compress_image(r.content)
        filename = f"{slug}.jpg"
        
        # Upload to Supabase storage
        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
        upload_headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "image/jpeg",
            "x-upsert": "true"
        }
        ur = requests.post(upload_url, headers=upload_headers, data=compressed, timeout=30)
        if ur.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded: {filename} ({len(compressed)//1024}KB)")
            return public_url
        else:
            print(f"  ⚠ Upload failed ({ur.status_code}): {ur.text[:100]}")
            return None
    except Exception as e:
        print(f"  ⚠ Download/upload error: {e}")
        return None


def source_image(person_name, topic_terms, slug):
    """Multi-source image: Wikipedia → Commons → Pexels. Returns (url, attribution) or (None, None)."""
    candidates = []
    
    # Source 1: Wikipedia (for person articles)
    if person_name:
        wiki = fetch_wikipedia_person_image(person_name)
        if wiki:
            candidates.append({"url": wiki, "source": "Wikimedia Commons", "priority": 1})
    
    # Source 2: Wikimedia Commons
    for q in topic_terms[:2]:
        commons = fetch_wikimedia_commons(q, limit=3)
        for c in commons[:2]:
            candidates.append({"url": c["url"], "source": "Wikimedia Commons", "priority": 2})
    
    # Source 3: Pexels
    for q in topic_terms[:1]:
        pex = fetch_pexels(q)
        if pex:
            candidates.append({"url": pex, "source": "Pexels", "priority": 3})
    
    # Pick best and upload
    for c in sorted(candidates, key=lambda x: x["priority"]):
        final_url = download_and_upload(c["url"], slug)
        if final_url:
            return final_url, c["source"]
    
    return None, None


def insert_article(article):
    """Insert article into Supabase."""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS_SB,
        json=article,
        timeout=30
    )
    if r.status_code in (200, 201):
        data = r.json()
        art_id = data[0]['id'] if isinstance(data, list) else data.get('id')
        print(f"  ✓ Published: {article['headline'][:60]}... (id: {art_id})")
        return art_id
    else:
        print(f"  ✗ Insert failed ({r.status_code}): {r.text[:200]}")
        return None


# ═══════════════════════════════════════
# ARTICLE 1: Shilpa Shinde False Harassment Confession
# ═══════════════════════════════════════
def write_article_1():
    print("\n═══ Article 1: Shilpa Shinde False Harassment Confession ═══")
    
    slug = "shilpa-shinde-false-harassment-confession-sanjay-kohli-backlash-nri-20260606"
    
    headline = "Shilpa Shinde Has Confessed to Filing a False Harassment Case. The Man She Accused Died Three Years Ago."
    
    subheadline = "The Bigg Boss winner admitted on a podcast that her 2016 sexual harassment complaint against Bhabiji Ghar Par Hain producer Sanjay Kohli was fabricated. Men's rights groups want her arrested. The industry is split."
    
    body = """Shilpa Shinde sat across from Bharti Singh and Harsh Limbachiyaa on their podcast and said the thing she had been carrying for nearly a decade. The sexual harassment allegations she had levelled against Bhabiji Ghar Par Hain producer Sanjay Kohli in 2016 — the complaint that consumed headlines, ended her run on one of Indian television's most-watched shows, and triggered legal battles that dragged on for years — were not true.

"The person on whom I put the blame knows what happened. I am sorry," Shinde said. "The word 'sorry' is very small, but he also knows the situation I was in. At that time, I felt I had no other option."

Except Sanjay Kohli does not know. He died in 2023. He is not alive to accept the apology, dispute her account, or speak for himself. That detail has turned what might have been a complicated conversation about truth and pressure into something far more combustible.

## The Fallout Was Immediate

Within hours, the National Council for Men Affairs, a Delhi-based NGO, demanded Mumbai Police arrest Shinde for filing a false complaint. The All India Cine Workers Association has asked the Chief Minister to intervene. On X, the discourse split predictably: some praised her for finally telling the truth, others asked why she waited until the accused was dead to tell it.

Hina Khan, who clashed with Shinde during Bigg Boss 11, issued a pointed response. Without naming Shinde directly, she called the confession "a crime, not courage," and accused her of using the revelation as a publicity stunt. Khan, who has been public about her battle with stage 3 breast cancer, appeared to reference Shinde's subsequent video in which the actress made what many interpreted as a veiled dig at colleagues who "use their own illnesses and the deaths of their family members" for attention.

Shinde did not back down. In an Instagram video posted the same day, she said the backlash was being driven by "paid PR" and that critics were "passing judgment on a single line without watching the entire podcast."

## What She Says Happened

Shinde's account, pieced together from the podcast and her subsequent video, describes a woman who felt cornered. By 2016, she had left Bhabiji Ghar Par Hain amid disputes over her contract and working conditions. She says the production house had turned the industry against her, and no one was willing to support her publicly.

Drawing on the traditional Indian framework of Saam, Daam, Dand, and Bhed — persuasion, inducement, punishment, and division — she said she had exhausted every avenue and resorted to the harassment complaint as a last weapon. She described being in a mental state where she was "contemplating suicide."

She said a turning point came years later, after winning Bigg Boss, when a man told her his father had died by suicide after being falsely accused. That encounter, she said, planted the seed for her eventual confession.

## The Larger Reckoning

The timing has made this more than a celebrity scandal. India's entertainment industry has spent the last several years grappling with its own version of the #MeToo movement, where accusations against powerful men were met with a mix of solidarity, scepticism, and legal threats. Shinde's confession hands ammunition to those who argue that false allegations undermine genuine survivors — an argument that has been wielded, sometimes cynically, to discredit women who come forward.

Karan Oberoi, an actor who was himself falsely accused of sexual assault in 2019, weighed in. "A false case is more anti-women than anti-men," he said. "One false case has the propensity to cast aspersions on a hundred genuine cases."

The counterargument, made by several commentators and women's rights advocates, is equally sharp: Shinde's case is the exception, not the rule, and treating it as representative of a systemic pattern of false accusations is both statistically wrong and dangerous for the women who are still fighting to be believed.

## What Happens Next

Whether Shinde faces legal consequences remains unclear. Filing a false police complaint is a criminal offence under Indian law, punishable by up to seven years in prison. But prosecuting a case where the complainant has voluntarily recanted, the accused is dead, and the original complaint was filed a decade ago presents obvious legal complications.

For the Indian diaspora watching from abroad, the case touches on something that resonates beyond Bollywood gossip. The tension between false accusations and genuine harassment is not unique to India, but the visibility of this case — a nationally known actress, a deceased producer, a confession delivered as content on a comedy podcast — makes it impossible to ignore.

Shinde, for her part, says she is done caring. "Nobody supported me then, so I don't expect anyone's support now," she said. "I am ready to face all of this."

The question is whether the system is ready to face her."""

    sources = json.dumps([
        {"name": "IANS", "url": "https://ianslive.in"},
        {"name": "MensXP", "url": "https://mensxp.com"},
        {"name": "Bollywood Life", "url": "https://bollywoodlife.com"},
        {"name": "India Forums", "url": "https://indiaforums.com"},
        {"name": "The Bridge Chronicle", "url": "https://thebridgechronicle.com"}
    ])
    
    # Image sourcing
    print("  Sourcing image...")
    img_url, img_attr = source_image(
        "Shilpa Shinde",
        ["Shilpa Shinde actress", "Shilpa Shinde Bigg Boss"],
        slug
    )
    
    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "entertainment",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "sources": sources,
        "image_url": img_url,
        "image_caption": "Shilpa Shinde at a public event in Mumbai" if img_url else None,
        "image_attribution": img_attr,
        "is_editorial": False,
        "vertical": "entertainment"
    }
    
    return insert_article(article)


# ═══════════════════════════════════════
# ARTICLE 2: Bobby Deol's Bandar — The Dark Horse
# ═══════════════════════════════════════
def write_article_2():
    print("\n═══ Article 2: Bobby Deol's Bandar ═══")
    
    slug = "bobby-deol-bandar-anurag-kashyap-tiff-reviews-dark-horse-nri-20260606"
    
    headline = "Bobby Deol Just Delivered the Performance of His Career. The Film Got 500 Screens. It Might Not Need More."
    
    subheadline = "Anurag Kashyap's Bandar premiered at TIFF, earned four-star reviews, and opened to rave word-of-mouth. But in a week dominated by Peddi and franchise sequels, it is fighting for every screen it can get."
    
    body = """Bobby Deol has made more than 30 films. Most of them are forgettable. A few — Gupt, Soldier, a cameo in Animal that became a cultural moment — punctuated an otherwise unremarkable career with flashes of something harder and more interesting than the roles he was typically given. Bandar is the film that finally gives him the full canvas.

Directed by Anurag Kashyap and co-written by Sudip Sharma and Abhishek Banerjee, Bandar tells the story of Samar, a fading television star whose life collapses when his ex-girlfriend accuses him of rape. The film is not interested in making the audience comfortable. It is interested in making them think.

## What the Critics Are Saying

The early reviews have been striking. Multiple critics have awarded the film four stars or higher. The consensus: Kashyap has delivered one of his most disciplined films, and Deol has given a performance that rewrites what anyone thought he was capable of.

The supporting cast — Sanya Malhotra, Sapna Pabbi, Saba Azad, Indrajith Sukumaran, Jitendra Joshi, Raj B. Shetty — has been praised for bringing texture to a narrative that could have easily become one-note. At 2 hours and 16 minutes, the film apparently does not waste a frame.

Bandar had its world premiere at the Toronto International Film Festival in September 2025, where it drew significant attention for its subject matter and performances. For Indian cinema to send a film this thematically confrontational to one of the world's most prestigious festivals, and for that festival to programme it prominently, says something about where the industry's best work is heading.

## The Screen Battle

The problem, as always, is distribution. Bandar released on June 5 alongside Ram Charan's Peddi and Varun Dhawan's Hai Jawani Toh Ishq Hona Hai. In the screen allocation war, a mid-budget Anurag Kashyap film about sexual assault and a corrupt justice system was never going to win against a ₹100-crore Telugu action film.

Zee Studios, which is distributing Bandar, made a calculated decision. Rather than chase a wide release and get crushed in the first weekend, the studio is rolling out in 500-600 screens with a strategy built around word-of-mouth. Girish Johar, the studio's distribution and revenue head, said they asked multiplexes for 3-4 shows per screen post 1 PM — a modest request that still met resistance from chains packed with bigger-budget releases.

The production budget is estimated at ₹10-15 crore, which means the film needs roughly ₹25 crore at the box office to be considered a hit. That is a reachable target if the word-of-mouth holds — and so far, it is holding.

## Why the Diaspora Should Care

For NRI audiences who have spent years complaining that Bollywood only exports franchise sequels and song-and-dance spectacles, Bandar is the kind of film that makes the complaint look lazy. It is a tightly constructed crime thriller with real performances, a real director, and a willingness to sit with moral ambiguity.

The international title — Monkey in a Cage — signals the kind of audience Kashyap is after. This is not a film designed to be streamed as background noise. It is designed to leave the audience arguing about it in the parking lot.

Whether that audience shows up in theatres during one of the most crowded release weeks of the year is another question. But if Bandar finds its legs — and the critical response suggests it will — it could become 2026's defining sleeper hit.

## The Bobby Deol Question

There is something worth noting about the trajectory. After years of direct-to-streaming obscurity, Deol reinvented himself through the web series Ashram, found a second wind through a brief but unforgettable turn in Animal, and is now anchoring a film that serious critics are calling one of the year's best.

He is 57 years old. His career should, by any conventional measure, be winding down. Instead, it appears to be starting over. That might be the most interesting story Bandar tells — not the one on screen, but the one behind it."""

    sources = json.dumps([
        {"name": "Pinkvilla", "url": "https://pinkvilla.com"},
        {"name": "Gadgets360", "url": "https://gadgets360.com"},
        {"name": "Sacnilk", "url": "https://sacnilk.com"},
        {"name": "Zoom TV Entertainment", "url": "https://zoomtventertainment.com"},
        {"name": "Bollywood Life", "url": "https://bollywoodlife.com"}
    ])
    
    # Image sourcing
    print("  Sourcing image...")
    img_url, img_attr = source_image(
        "Bobby Deol",
        ["Bobby Deol actor Bollywood", "Anurag Kashyap director"],
        slug
    )
    
    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "entertainment",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "sources": sources,
        "image_url": img_url,
        "image_caption": "Bobby Deol at a film event" if img_url else None,
        "image_attribution": img_attr,
        "is_editorial": False,
        "vertical": "entertainment"
    }
    
    return insert_article(article)


# ═══════════════════════════════════════
# ARTICLE 3: Main Vaapas Aaunga — Diljit's Partition Film
# ═══════════════════════════════════════
def write_article_3():
    print("\n═══ Article 3: Main Vaapas Aaunga ═══")
    
    slug = "main-vaapas-aaunga-diljit-dosanjh-imtiaz-ali-ar-rahman-partition-nri-20260606"
    
    headline = "Diljit Dosanjh Premiered the Trailer of His Partition Film at a Packed Toronto Stadium. Advance Bookings Have Opened in North America First."
    
    subheadline = "Imtiaz Ali's Main Vaapas Aaunga reunites Diljit with A.R. Rahman after Chamkila, tells a love story across 1947 and the present, and is releasing in North American theatres a week before India. The diaspora is the audience."
    
    body = """During a stop on his ongoing AURA Tour 2026, Diljit Dosanjh did something that has become increasingly common for Indian stars playing to diaspora crowds but has never been done quite like this. He played the trailer of his upcoming film Main Vaapas Aaunga on the giant screens of a packed Toronto stadium. The crowd roared. Videos went viral. And within days, the film's producers announced that advance bookings in the United States and Canada would open a full week before India.

That sequencing is not accidental. It is a statement about who this film is for.

## The Film

Main Vaapas Aaunga — I Will Return — is directed by Imtiaz Ali and is set across two timelines: pre-Partition Punjab and the present day. It stars Diljit Dosanjh, Naseeruddin Shah, Vedang Raina, and Sharvari. The score is by A.R. Rahman, with lyrics by Irshad Kamil. If you are counting collaborations, this is Imtiaz and Diljit's second film together after Amar Singh Chamkila, their 2024 Netflix biographical drama that became one of the most acclaimed Indian films of that year.

The trailer, which dropped in late May and has been gathering momentum since, paints a picture of lives torn apart by the Partition of 1947 — families separated, memories frozen, promises that survived decades even as the people who made them did not. The emotional register is unmistakably Imtiaz Ali: yearning, displacement, love that outlasts geography.

## The Music

Four songs have been released so far, and the album is already building the kind of conversation that A.R. Rahman's best work generates. The latest single, Ishq Mastana, dropped on Vedang Raina's birthday and blends Punjabi folk traditions with 1940s jazz and swing influences. Its central refrain draws from the verses of Sant Kabir — "Haman Hai Ishq Mastana, Haman Ko Hoshiyari Kya" — and the result is a track that feels both historical and immediate.

Mohit Chauhan returns to an Imtiaz Ali soundtrack for the first time in years. If you were there for Rockstar, you know what that means.

The earlier tracks — Kya Kamaal Hai (sung by Diljit), Maskara, and Vo Nahin — have each carved their own space. What is emerging is not just a collection of songs but a sonic world: undivided India before the line was drawn, rendered in melody.

## Why the Diaspora Gets It First

The decision to open North American advance bookings before India is commercially pragmatic — the NRI market for Hindi films has never been larger — but it also reflects something deeper about the film's subject matter. Partition is not ancient history for the Indian diaspora. It is the reason many of them exist where they do.

The story of families split between India and Pakistan, of ancestral villages that became foreign countries overnight, of promises to return that were never kept — this is the living memory of millions of people in the US, Canada, and the UK. A film called I Will Return, set against Partition and screened first for the diaspora, knows exactly what it is doing.

## The June 12 Clash

Main Vaapas Aaunga releases on June 12 alongside Kangana Ranaut's 26/11 thriller Bharat Bhhagya Vidhaata, Manoj Bajpayee's Governor, and the postponed David Dhawan comedy Hai Jawani Toh Ishq Hona Hai. It is, by any measure, one of the most crowded release weeks in recent Bollywood history.

The irony of Diljit and Kangana releasing on the same day has not been lost on anyone. The two had a public and acrimonious clash on Twitter in 2020 over the farmers' protests, a confrontation that turned both of them into avatars for opposing political positions. Five and a half years later, they are competing for the same screens on the same Friday.

Trade analysts give Main Vaapas Aaunga the advantage. The Imtiaz Ali-Diljit-Rahman combination is commercially proven, the trailer has generated genuine excitement, and the music is already working. But June 2026 is a month where ₹1,400 crore is reportedly at stake across nine major releases, and no one is safe from the screen-sharing bloodbath.

## What Is at Stake

For Imtiaz Ali, this is a return to the theatrical canvas after years of mixed results. For Diljit, it is a chance to prove that Chamkila was not a one-off and that he can carry a Hindi-language theatrical release with the same authority he brings to a stadium. For Rahman, it is another chapter in a filmography that has defined what Indian cinema sounds like.

And for the diaspora audience watching from Toronto and New Jersey and the Bay Area, it is a film that says: this story is yours, and we are telling it for you first."""

    sources = json.dumps([
        {"name": "Filmfare", "url": "https://filmfare.com"},
        {"name": "Bollywood Hungama", "url": "https://bollywoodhungama.com"},
        {"name": "BollySpice", "url": "https://bollyspice.com"},
        {"name": "India Forums", "url": "https://indiaforums.com"},
        {"name": "Wikipedia", "url": "https://en.wikipedia.org/wiki/Main_Vaapas_Aaunga"}
    ])
    
    # Image sourcing
    print("  Sourcing image...")
    img_url, img_attr = source_image(
        "Diljit Dosanjh",
        ["Diljit Dosanjh singer actor", "Imtiaz Ali director Bollywood"],
        slug
    )
    
    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "entertainment",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "sources": sources,
        "image_url": img_url,
        "image_caption": "Diljit Dosanjh performing during his AURA Tour" if img_url else None,
        "image_attribution": img_attr,
        "is_editorial": False,
        "vertical": "entertainment"
    }
    
    return insert_article(article)


# ═══════════════════════════════════════
# MAIN
# ═══════════════════════════════════════
if __name__ == "__main__":
    print(f"Entertainment writer run: {datetime.now(timezone.utc).isoformat()}")
    
    results = []
    
    aid1 = write_article_1()
    results.append(("Shilpa Shinde Confession", aid1))
    time.sleep(1)
    
    aid2 = write_article_2()
    results.append(("Bobby Deol Bandar", aid2))
    time.sleep(1)
    
    aid3 = write_article_3()
    results.append(("Main Vaapas Aaunga", aid3))
    
    print("\n═══ SUMMARY ═══")
    for title, aid in results:
        status = "✓" if aid else "✗"
        print(f"  {status} {title}: {aid}")
    
    success = sum(1 for _, a in results if a)
    print(f"\nPublished {success}/{len(results)} articles")

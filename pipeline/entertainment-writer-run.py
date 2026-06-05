#!/usr/bin/env python3
"""
Entertainment Writer — June 5, 2026 run
Writes 3 articles:
1. Aamir Khan confirms wedding with Gauri Spratt on July 5
2. Bandar — Bobby Deol + Anurag Kashyap neo-noir releasing June 5
3. Main Vaapas Aaunga — Imtiaz Ali's partition film deep dive
"""

import json, os, sys, time, uuid, subprocess, urllib.parse, io, re
from datetime import datetime, timezone

# Load env
def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    if line.startswith('export '):
                        line = line[7:]
                    key, val = line.split('=', 1)
                    val = val.strip('"').strip("'")
                    os.environ[key] = val

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

import requests
from PIL import Image

SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY', '')
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

HEADERS_SB = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

UA = 'TheVideshi/1.0 (thevideshi.com)'

# ─── Image Functions ───

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
    """Search Pexels for images using curl (urllib gets 403)."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    try:
        result = subprocess.run(
            ['curl', '-sS', '-H', f'Authorization: {PEXELS_KEY}',
             f'https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page=3&orientation=landscape'],
            capture_output=True, text=True, timeout=15
        )
        data = json.loads(result.stdout)
        photos = data.get('photos', [])
        if photos:
            url = photos[0]['src']['large2x']
            print(f"  ✓ Pexels image found for '{query}': {url[:80]}...")
            return url
    except Exception as e:
        print(f"  ⚠ Pexels error: {e}")
    return None


def compress_image(img_bytes, max_width=1200, quality=80):
    """Resize and compress image. Returns JPEG bytes."""
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
    """Download image bytes from URL."""
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=20)
        if r.status_code == 200 and len(r.content) > 5000:
            ct = r.headers.get('Content-Type', '')
            if 'image' in ct or url.endswith(('.jpg', '.jpeg', '.png', '.webp')):
                print(f"  ✓ Downloaded {len(r.content)} bytes")
                return r.content
        else:
            print(f"  ⚠ Download failed: status={r.status_code}, size={len(r.content)}")
    except Exception as e:
        print(f"  ⚠ Download error: {e}")
    return None


def upload_to_supabase(img_bytes, filename):
    """Upload image to Supabase storage bucket 'article-images'. Returns public URL."""
    url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
    headers = {
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'image/jpeg',
        'x-upsert': 'true'
    }
    try:
        r = requests.post(url, headers=headers, data=img_bytes, timeout=30)
        if r.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {public_url[:80]}...")
            return public_url
        else:
            print(f"  ⚠ Supabase upload failed: {r.status_code} - {r.text[:200]}")
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
    return None


def source_image(person_name, topic_queries, slug):
    """Multi-source image sourcing: Wikipedia → Wikimedia Commons → Pexels"""
    candidates = []

    # Source 1: Wikipedia (for person articles)
    if person_name:
        wiki_img = fetch_wikipedia_person_image(person_name)
        if wiki_img:
            candidates.append({"url": wiki_img, "source": "wikipedia", "relevance": 3})

    # Source 2: Wikimedia Commons
    for q in topic_queries[:2]:
        commons = fetch_wikimedia_commons_images(q, limit=3)
        for c in commons[:2]:
            candidates.append({"url": c["url"], "source": "wikimedia_commons", "relevance": 2})

    # Source 3: Pexels
    if topic_queries:
        pexels_img = fetch_pexels_image(topic_queries[0])
        if pexels_img:
            candidates.append({"url": pexels_img, "source": "pexels", "relevance": 1})

    # Pick best candidate and process
    candidates.sort(key=lambda x: x["relevance"], reverse=True)
    
    for candidate in candidates:
        print(f"  Trying {candidate['source']}: {candidate['url'][:80]}...")
        raw = download_image(candidate["url"])
        if raw:
            compressed = compress_image(raw)
            size_kb = len(compressed) / 1024
            print(f"  Compressed to {size_kb:.0f} KB")
            if size_kb < 10:
                print(f"  ⚠ Too small after compression, skipping")
                continue
            filename = f"{slug}.jpg"
            final_url = upload_to_supabase(compressed, filename)
            if final_url:
                attribution = "Wikimedia Commons" if candidate["source"] in ("wikipedia", "wikimedia_commons") else "Pexels"
                return final_url, attribution
    
    print("  ✗ No suitable image found")
    return None, None


def insert_article(article):
    """Insert article into Supabase."""
    url = f"{SUPABASE_URL}/rest/v1/p2_articles"
    r = requests.post(url, headers=HEADERS_SB, json=article, timeout=30)
    if r.status_code in (200, 201):
        data = r.json()
        art_id = data[0]['id'] if isinstance(data, list) else data.get('id', 'unknown')
        print(f"  ✓ Article inserted: {art_id}")
        return art_id
    else:
        print(f"  ✗ Insert failed: {r.status_code} - {r.text[:300]}")
        return None


# ─── Article Definitions ───

now = datetime.now(timezone.utc)
pub_time = now.strftime('%Y-%m-%dT%H:%M:%S+00:00')

articles = []

# ── ARTICLE 1: Aamir Khan Wedding ──
print("\n" + "="*60)
print("ARTICLE 1: Aamir Khan Wedding with Gauri Spratt")
print("="*60)

article1_slug = "aamir-khan-gauri-spratt-wedding-july-5-third-marriage-nri-20260605"
article1_body = """Aamir Khan has confirmed that he is getting married for the third time. The actor, currently traveling in the United States, told Variety India that he will wed his partner Gauri Spratt on July 5, 2026. "The news about the marriage is true. It's on July 5," he said simply, putting months of speculation to rest with a single sentence.

The ceremony will be a registered marriage at Aamir's residence in Mumbai. No Bollywood spectacle. No thousand-guest extravaganza. Just the two families, a handful of close friends, and a quiet signing in the living room where, by all accounts, their shared life has already been unfolding for over a year.

## A Friendship That Became Something More

Aamir and Gauri have known each other for nearly 25 years. They were friends first — the kind of friendship that runs long and quiet before it turns into something else entirely. They reconnected after years of being out of touch, and the friendship gradually deepened into romance. Aamir introduced Gauri publicly on the eve of his 60th birthday in March 2025, describing her with an openness that surprised an industry used to his carefully guarded private life.

"Gauri and I are really serious about each other and we are in a very committed space," he said in a later interview with Indian Express. "In my heart, I'm already married to her. So whether we formalize it or not is something that I will decide as we go along."

They decided to go along.

## Who Is Gauri Spratt?

For the diaspora, Gauri Spratt's story carries a quiet resonance that goes beyond celebrity gossip. Originally from Bengaluru, she has a professional background in fashion, beauty, and wellness. She is a mother to a seven-year-old son, Quinn, from a previous marriage.

Her family history reads like a novel. Her grandfather, Philip Spratt, was a British-born communist who arrived in India in the 1920s — not as a colonial administrator, but as a revolutionary. He was involved in the Meerut Conspiracy Case and spent years fighting for Indian independence, eventually making India his permanent home. There is something poetic about his granddaughter now formalizing her own commitment to an Indian household, crossing cultural lines in a way that echoes a family tradition of choosing conviction over convention.

## The Marriages That Came Before

Aamir's personal life has been lived in chapters, each one public whether he wanted it to be or not. He married childhood sweetheart Reena Dutta in 1986. They have two children together — Junaid Khan, now an established actor, and Ira Khan, who married fitness trainer Nupur Shikhare in 2024 in a ceremony Aamir attended alongside Kiran Rao. The first marriage ended in divorce in 2002.

He married Kiran Rao in 2005. They have a son, Azad Rao Khan. When they announced their separation in 2021 after 15 years of marriage, the joint statement was widely praised for its maturity and warmth. They continue to co-parent Azad and collaborate professionally through their production company, Paani Foundation.

Now, at 61, Aamir is entering a third chapter — not with the grand gestures of a Bollywood romance, but with the quiet certainty of two people who have already built a life and are simply making it official.

## What This Means for the Diaspora

For NRIs who have watched Aamir evolve from the reluctant star of the 1990s to the socially conscious filmmaker of the 2000s to the man who walked away from a second marriage with grace, this third wedding carries weight. It is a reminder that reinvention does not have an expiry date, that love after heartbreak is not a scandal but a second chance, and that choosing a private ceremony over public spectacle says more about a person than any press conference ever could.

The wedding is set for July 5 in Mumbai. No grand reception for industry members is planned. True to form, Aamir Khan is doing this entirely on his own terms.

*Sources: Variety India, Filmfare, Pinkvilla, Bollywood Hungama*"""

img1_url, img1_attr = source_image(
    "Aamir Khan",
    ["Aamir Khan actor", "Aamir Khan Bollywood"],
    article1_slug
)

articles.append({
    "headline": "Aamir Khan Is Getting Married Again. The Ceremony Will Be at Home, the Guest List Will Be Tiny, and the Date Is July 5.",
    "subheadline": "The actor confirmed his wedding to Gauri Spratt, a Bengaluru-born partner whose grandfather once crossed an ocean to fight for Indian independence. The couple has known each other for 25 years.",
    "slug": article1_slug,
    "body": article1_body,
    "category": "entertainment",
    "status": "published",
    "published_at": pub_time,
    "is_editorial": False,
    "image_url": img1_url,
    "image_caption": "Aamir Khan at a public appearance in Mumbai",
    "image_attribution": img1_attr or "Wikimedia Commons",
    "sources": json.dumps(["Variety India", "Filmfare", "Pinkvilla", "Bollywood Hungama", "Indian Express"]),
})


# ── ARTICLE 2: Bandar ──
print("\n" + "="*60)
print("ARTICLE 2: Bandar — Bobby Deol + Anurag Kashyap")
print("="*60)

article2_slug = "bandar-bobby-deol-anurag-kashyap-neo-noir-tiff-reviews-nri-20260605"
article2_body = """Bobby Deol has spent the last five years quietly rebuilding himself into one of Bollywood's most interesting actors. With Bandar, releasing in theaters today, he completes the transformation. The early reviews are in, and they are the kind of reviews most actors wait an entire career to receive.

Directed by Anurag Kashyap and co-written by Sudip Sharma and Abhishek Banerjee, Bandar is a neo-noir crime thriller that follows Sameer Mehra, a fading television star who finds his life dismantled when his ex-girlfriend accuses him of sexual assault. The film premiered at the Toronto International Film Festival in September 2025, where it drew significant critical attention. It now arrives in Indian theaters as one of the most anticipated mid-budget releases of the year.

## The Reviews Are Saying What Everyone Hoped

Critic Kuldeep Gadhvi awarded Bandar four out of five stars, calling it "a powerful crime thriller that keeps you guessing till the end while delivering stellar performances and a sharp commentary on the justice system." He described Bobby Deol's work as "mature, controlled, vulnerable, and emotionally powerful" — adjectives that would have seemed unlikely just a few years ago when Deol was primarily known for the meme economy that surrounded his career downturn.

Bollywood Bubble's review went further, calling it Kashyap's return to familiar territory with "a dark and unsettling neo-noir thriller that explores the fragile line between guilt, innocence, public perception, and systemic failure." The consensus emerging from early screenings is that this is Deol at his absolute best — restrained, grounded, and devastatingly honest.

The supporting cast has drawn praise as well. Sanya Malhotra, described as "absolutely outstanding," plays a pivotal role. Indrajith Sukumaran delivers what reviewers call "a commanding performance," while Saba Azad, playing Sameer's current girlfriend, brings layered complexity to a role that in lesser hands could have been peripheral. Sapna Pabbi, as the ex-girlfriend whose accusation sets the story in motion, and Raj B. Shetty and Jitendra Joshi round out an ensemble that Kashyap has assembled with his signature precision.

## Bobby Deol on Working with Kashyap

The actor himself has been candid about what this project meant to him. "I didn't increase my fee for this film," Deol told Wion. "When a project truly excites me as an actor, money isn't the first thing I think about." He described the experience of working with Kashyap as transformative: "Anurag wasn't looking for theatrics or embellishment — he wanted honesty and authenticity. Working with him felt like being part of an acting workshop. Every single day on set, I learnt something new."

It is a striking admission from an actor who once headlined the kind of films that Kashyap has spent his career railing against. But that is what makes this collaboration so compelling — it is the meeting of an actor who has shed his ego and a director who has never had patience for anything but the raw truth.

## The CBFC Complication

The path to Indian theaters has not been entirely smooth. The Central Board of Film Certification required cuts to the film, prompting Kashyap to publicly note that the version Indian audiences will see differs from the one that played at TIFF. For international audiences, the film is titled Monkey in a Cage. For Indian audiences, the title is Bandar — simpler, more direct, and carrying a colloquial edge that fits Kashyap's sensibility.

The film runs 2 hours and 16 minutes. It is produced by Nikhil Dwivedi's Saffron Magicworks and released by Zee Studios. It faces a competitive weekend at the box office, with showcase allocation reportedly tilted toward larger releases. The producers have focused on a quality-over-quantity strategy, banking on word of mouth to carry the film past its opening days.

## Why This Matters for the Diaspora

Bobby Deol's career arc mirrors a story the diaspora understands intuitively — the long struggle to be taken seriously after being written off, the quiet work that happens when nobody is watching, and the vindication that comes not from volume but from a single, undeniable piece of work. Bandar appears to be that piece of work.

For NRIs who remember Deol from the Soldier era and have watched his reinvention through Ashram, Animal, and Class of '83, this is the culmination. Not every comeback needs fireworks. Sometimes, the best ones arrive in a darkened theater on a Thursday morning, carried by nothing more than the weight of a performance that refuses to be ignored.

*Sources: Bollywood Bubble, Filmibeat, Zoom TV, IndiaForums, Wion*"""

img2_url, img2_attr = source_image(
    "Bobby Deol",
    ["Bobby Deol actor Bollywood", "Bandar film Anurag Kashyap 2026"],
    article2_slug
)

articles.append({
    "headline": "Bandar Is in Theaters Today. Bobby Deol Has Never Been This Good. The Reviews Confirm What TIFF Audiences Already Knew.",
    "subheadline": "Anurag Kashyap's neo-noir crime thriller about a fading star accused of assault earned four-star reviews and a standing ovation at Toronto. Now Indian audiences finally get to see it — with CBFC cuts.",
    "slug": article2_slug,
    "body": article2_body,
    "category": "entertainment",
    "status": "published",
    "published_at": pub_time,
    "is_editorial": False,
    "image_url": img2_url,
    "image_caption": "Bobby Deol at a film event in Mumbai",
    "image_attribution": img2_attr or "Wikimedia Commons",
    "sources": json.dumps(["Bollywood Bubble", "Filmibeat", "Zoom TV Entertainment", "Wion", "IndiaForums"]),
})


# ── ARTICLE 3: Main Vaapas Aaunga ──
print("\n" + "="*60)
print("ARTICLE 3: Main Vaapas Aaunga — Imtiaz Ali Partition Film")
print("="*60)

article3_slug = "main-vaapas-aaunga-imtiaz-ali-diljit-ar-rahman-partition-june-12-nri-20260605"
article3_body = """There is a film arriving on June 12 that, on paper, should not need any help generating excitement. It is directed by Imtiaz Ali. The music is by A.R. Rahman. The lyrics are by Irshad Kamil. Diljit Dosanjh and Naseeruddin Shah star alongside Vedang Raina and Sharvari. It is a partition story that moves between 1947 and the present day. And it reunites the director-actor pair that gave us Amar Singh Chamkila, one of the most acclaimed Indian films of the last decade.

Main Vaapas Aaunga is not just another Bollywood release. It is a bet that Indian cinema can tell the most painful story in the subcontinent's history — the Partition of 1947 — and make it personal enough to fill theaters in 2026.

## What We Know About the Film

The details have been released in careful, deliberate drops. Imtiaz Ali has spoken about the film as a story of love and longing that spans two timelines. The 1947 sections are set in pre-Partition Punjab — a world of shared streets, mixed neighborhoods, and the fragile peace that was about to shatter. The present-day sections trace the emotional afterlife of that rupture, following characters who are still carrying wounds that were never theirs to begin with but became theirs anyway.

Diljit Dosanjh plays a central role, though the precise nature of his character has been kept under wraps. Naseeruddin Shah, at 76, brings the kind of gravitas that transforms even a brief appearance into something indelible. Vedang Raina and Sharvari carry the younger timeline, and their chemistry — visible in the music videos released so far — suggests Imtiaz has found a pairing that can shoulder the emotional weight the story demands.

The film is produced by Birla Studios and Applause Entertainment in collaboration with Window Seat Films.

## The Music Is Already a Conversation

A.R. Rahman's score for Main Vaapas Aaunga has been rolling out in stages, and each new song has landed like a statement. The latest, Ishq Mastana, dropped on Vedang Raina's birthday and immediately became the most discussed track of the week. Sung by Mohit Chauhan alongside Nargis and Pooja Tiwari, the song draws on Sant Kabir's verses — "Haman Hai Ishq Mastana, Haman Ko Hoshiyari Kya" — and folds centuries-old poetry into a melody that blends Punjabi folk traditions with jazz and swing influences that once drifted across undivided India.

It is a conscious choice. The music is not just scoring a film; it is rebuilding a soundscape that partition erased. Previous tracks — Kya Kamaal Hai, Maskara, and Vo Nahin — have already demonstrated that Rahman and Irshad Kamil are working at a level of intent and precision that goes beyond standard Bollywood soundtrack work.

Mohit Chauhan's reunion with Rahman and Imtiaz completes a circle that started with Rockstar. For longtime fans of that collaboration, the sound of Chauhan's voice over Rahman's arrangements in the context of an Imtiaz Ali story about love and loss carries an almost unfair amount of emotional weight.

## The Chamkila Connection

Main Vaapas Aaunga marks the second collaboration between Imtiaz Ali and Diljit Dosanjh after Amar Singh Chamkila, the 2024 Netflix biographical drama that earned widespread critical acclaim and cemented Diljit's status as a serious actor beyond his music career. That film worked because it treated its subject — a murdered Punjabi folk singer — with a specificity and tenderness that refused to simplify. If Imtiaz brings the same approach to Partition, the results could be extraordinary.

For Diljit, who has spent the last two years oscillating between sold-out global concert tours and increasingly ambitious film choices, Main Vaapas Aaunga represents a chance to prove that Chamkila was not an anomaly but a turning point.

## Why This Film Matters to the Diaspora

Partition is not ancient history for the Indian diaspora. It is the reason entire communities exist where they do. It is the story behind the grandmother who never went back, the grandfather who never stopped talking about a street in Lahore, the family recipe that came across the border in someone's memory because there was no time to pack anything else. For NRIs in the US, UK, and Canada, Partition is not a chapter in a textbook. It is the opening line of a family story that is still being written.

A film that approaches this subject with the emotional intelligence of Imtiaz Ali, the musical vocabulary of A.R. Rahman, and the cross-generational appeal of a cast that spans Naseeruddin Shah to Vedang Raina has the potential to be more than a box office event. It could be the kind of film that families watch together and that finally gives younger diaspora members a cinematic entry point into a history they have only ever heard secondhand.

Main Vaapas Aaunga releases on June 12. Mark it.

*Sources: Bollywood Hungama, IndiaForums, IWMBuzz, Zoom TV Entertainment*"""

img3_url, img3_attr = source_image(
    "Diljit Dosanjh",
    ["Diljit Dosanjh singer actor", "Main Vaapas Aaunga film"],
    article3_slug
)

articles.append({
    "headline": "Main Vaapas Aaunga Arrives June 12. Imtiaz Ali, Diljit, AR Rahman, and a Partition Story the Diaspora Has Been Waiting For.",
    "subheadline": "The Chamkila duo reunites for a film that moves between 1947 Punjab and the present day. The music draws on Sant Kabir. The cast spans Naseeruddin Shah to Vedang Raina. And the subject is the wound that built the diaspora.",
    "slug": article3_slug,
    "body": article3_body,
    "category": "entertainment",
    "status": "published",
    "published_at": pub_time,
    "is_editorial": False,
    "image_url": img3_url,
    "image_caption": "Diljit Dosanjh performing at a concert event",
    "image_attribution": img3_attr or "Wikimedia Commons",
    "sources": json.dumps(["Bollywood Hungama", "IndiaForums", "IWMBuzz", "Zoom TV Entertainment"]),
})


# ─── Insert Articles ───
print("\n" + "="*60)
print("INSERTING ARTICLES")
print("="*60)

success_count = 0
for i, art in enumerate(articles):
    print(f"\n--- Article {i+1}: {art['headline'][:60]}... ---")
    
    # Validate
    if not art.get('image_url'):
        print("  ⚠ No image — inserting without image")
    
    body_words = len(art['body'].split())
    print(f"  Body: {body_words} words")
    if body_words < 400:
        print(f"  ✗ REJECTED: Body too short ({body_words} < 400)")
        continue
    
    if len(art['headline']) > 200:
        print(f"  ⚠ Headline too long ({len(art['headline'])} chars), truncating")
        art['headline'] = art['headline'][:197] + "..."
    
    if not art.get('subheadline') or len(art['subheadline']) < 15:
        print(f"  ✗ REJECTED: Missing or too-short subheadline")
        continue
    
    result = insert_article(art)
    if result:
        success_count += 1

print(f"\n{'='*60}")
print(f"DONE: {success_count}/{len(articles)} articles published")
print(f"{'='*60}")

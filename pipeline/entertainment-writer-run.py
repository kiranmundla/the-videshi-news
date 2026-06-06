#!/usr/bin/env python3
"""Entertainment writer — 3 articles for The Videshi (2026-06-06 run)"""

import json, os, sys, time, uuid, re, io, subprocess
from datetime import datetime, timezone

# Load env
def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    os.environ[k.strip()] = v.strip().strip('"').strip("'")

# Load workspace env first (has GOOGLE_PLACES etc), then home env last (has proper JWT keys)
load_env(os.path.expanduser('~/workspace/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))
load_env(os.path.expanduser('~/.env.supabase'))  # JWT keys — must be last to override

SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY', '')
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

import requests
from PIL import Image

HEADERS_SB = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

UA = "TheVideshi/1.0 (thevideshi.com)"

# ---- Image sourcing functions ----

def fetch_wikipedia_person_image(person_name):
    """Fetch person's actual photo from Wikipedia. Returns image URL or None."""
    import urllib.parse
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": UA},
            timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            # Use thumbnail.source AS-IS (330px) — do not modify
            img = data.get("thumbnail", {}).get("source")
            if not img:
                img = data.get("originalimage", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia error for '{person_name}': {e}")
    return None

def fetch_wikimedia_commons_images(search_query, limit=5):
    """Search Wikimedia Commons for CC images."""
    try:
        r = requests.get(
            "https://commons.wikimedia.org/w/api.php",
            params={
                "action": "query",
                "generator": "search",
                "gsrsearch": search_query,
                "gsrnamespace": "6",
                "gsrlimit": str(limit),
                "prop": "imageinfo",
                "iiprop": "url|size|mime",
                "iiurlwidth": "1200",
                "format": "json"
            },
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
                    "height": ii.get("height", 0)
                })
            if results:
                print(f"  ✓ Wikimedia Commons: {len(results)} images for '{search_query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Wikimedia Commons error: {e}")
    return []

def fetch_pexels_image(query):
    """Fetch image from Pexels using curl (urllib gets 403)."""
    try:
        result = subprocess.run(
            ["curl", "-sS", "-H", f"Authorization: {PEXELS_KEY}",
             f"https://api.pexels.com/v1/search?query={requests.utils.quote(query)}&per_page=3"],
            capture_output=True, text=True, timeout=15
        )
        data = json.loads(result.stdout)
        photos = data.get("photos", [])
        if photos:
            url = photos[0]["src"]["large2x"]
            print(f"  ✓ Pexels image for '{query}': {url[:80]}...")
            return url
    except Exception as e:
        print(f"  ⚠ Pexels error: {e}")
    return None

def compress_image(img_bytes, max_width=1200, quality=80):
    """Resize and compress image. Returns JPEG bytes."""
    img = Image.open(io.BytesIO(img_bytes))
    if img.mode in ('RGBA', 'P', 'LA'):
        img = img.convert('RGB')
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=quality, optimize=True)
    return buf.getvalue()

def download_image(url):
    """Download image bytes."""
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=20)
        if r.status_code == 200 and len(r.content) > 5000:
            ct = r.headers.get("Content-Type", "")
            if "image" in ct or len(r.content) > 10000:
                return r.content
        print(f"  ⚠ Image download failed: status={r.status_code}, size={len(r.content)}")
    except Exception as e:
        print(f"  ⚠ Image download error: {e}")
    return None

def upload_to_supabase(img_bytes, filename):
    """Upload image to Supabase article-images bucket. Returns public URL."""
    # Try upsert
    url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
    headers = {
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "image/jpeg",
        "x-upsert": "true"
    }
    r = requests.post(url, headers=headers, data=img_bytes, timeout=30)
    if r.status_code in (200, 201):
        public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
        print(f"  ✓ Uploaded to Supabase: {filename}")
        return public_url
    else:
        # Try PUT
        r2 = requests.put(url, headers=headers, data=img_bytes, timeout=30)
        if r2.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase (PUT): {filename}")
            return public_url
        print(f"  ⚠ Supabase upload failed: {r.status_code} {r.text[:200]}")
    return None

def source_image(person_names, topic_queries, slug):
    """Multi-source image search. Returns (supabase_url, attribution, caption) or (None,None,None)."""
    candidates = []
    
    # Source 1: Wikipedia for person articles
    for name in person_names:
        wiki_img = fetch_wikipedia_person_image(name)
        if wiki_img:
            candidates.append({"url": wiki_img, "source": "wikimedia", "person": name, "relevance": 3})
            break
    
    # Source 2: Wikimedia Commons
    for query in topic_queries[:2]:
        commons = fetch_wikimedia_commons_images(query, limit=3)
        for c in commons[:2]:
            candidates.append({"url": c["url"], "source": "wikimedia", "person": None, "relevance": 2})
    
    # Source 3: Pexels fallback
    if not candidates:
        for query in topic_queries[:2]:
            pexels = fetch_pexels_image(query)
            if pexels:
                candidates.append({"url": pexels, "source": "pexels", "person": None, "relevance": 1})
                break
    
    if not candidates:
        print("  ✗ No image found from any source")
        return None, None, None
    
    # Pick best candidate (highest relevance)
    candidates.sort(key=lambda x: x["relevance"], reverse=True)
    best = candidates[0]
    
    # Download, compress, upload
    img_bytes = download_image(best["url"])
    if not img_bytes:
        # Try next candidate
        for c in candidates[1:]:
            img_bytes = download_image(c["url"])
            if img_bytes:
                best = c
                break
    
    if not img_bytes:
        print("  ✗ All image downloads failed")
        return None, None, None
    
    compressed = compress_image(img_bytes)
    if len(compressed) < 5000:
        print(f"  ⚠ Compressed image too small ({len(compressed)} bytes)")
        return None, None, None
    
    filename = f"{slug}.jpg"
    supabase_url = upload_to_supabase(compressed, filename)
    attribution = "Wikimedia Commons" if best["source"] == "wikimedia" else "Pexels"
    
    return supabase_url, attribution, best.get("person")


def insert_article(article):
    """Insert article into Supabase."""
    url = f"{SUPABASE_URL}/rest/v1/p2_articles"
    r = requests.post(url, headers=HEADERS_SB, json=article, timeout=30)
    if r.status_code in (200, 201):
        data = r.json()
        art_id = data[0]["id"] if isinstance(data, list) else data.get("id")
        print(f"  ✓ Article inserted: {article['slug']} (id: {art_id})")
        return art_id
    else:
        print(f"  ✗ Insert failed: {r.status_code} {r.text[:300]}")
        return None


# ========== ARTICLE 1: Drishyam 3 Box Office ==========
def write_article_1():
    print("\n=== ARTICLE 1: Drishyam 3 Box Office ===")
    
    slug = "drishyam-3-box-office-230-crore-worldwide-mohanlal-first-south-indian-10-million-overseas-nri-20260606"
    headline = "Drishyam 3 Has Crossed ₹230 Crore Worldwide. It Is the First South Indian Film of 2026 to Hit $10 Million Overseas."
    subheadline = "Georgekutty's final chapter is slowing down domestically but the diaspora has turned it into a record-breaking overseas hit for Malayalam cinema."
    
    body = """Mohanlal's Drishyam 3, the final installment of Jeethu Joseph's crime thriller franchise, has crossed ₹230 crore in worldwide gross collections after 15 days in theatres. The film has also become the first South Indian release of 2026 to breach the $10 million mark in overseas markets, a milestone that underlines the extraordinary pull of the Drishyam brand among diaspora audiences.

The numbers tell two different stories. Domestically, Drishyam 3 has grossed approximately ₹119 crore in India, with its second-week collections showing a steady decline. Daily collections have dropped from the ₹5-6 crore range during the second weekend to around ₹1 crore on weekdays, a pattern that suggests the mixed word-of-mouth is catching up with the film's initial goodwill. On its 15th day, the film registered 1,341 shows across the country, with Kerala remaining its strongest market.

## The Overseas Story Is Different

The international market has been Drishyam 3's real triumph. With over ₹111 crore gross from overseas territories, the film has benefited enormously from strong performances in the Gulf countries, North America, and the United Kingdom. The $10 million overseas milestone is particularly significant because it places the film ahead of every other South Indian release this year in international markets. For a Malayalam-language film, these are extraordinary numbers that reflect the franchise's deep connection with the global Malayali diaspora.

## The 250 Crore Question

The film now needs roughly ₹20 crore more to breach the ₹250 crore worldwide mark, a target that remains realistic but far from certain. Industry analysts note that Drishyam 3 is unlikely to surpass Mohanlal's own Empuraan, which holds the record for the second-highest-grossing Malayalam film at ₹266 crore. The dream of reaching ₹300 crore, which seemed possible during the film's explosive opening week when it crossed ₹100 crore in just three days, now appears out of reach.

What the film will almost certainly do is overtake Vaazha 2's ₹235 crore to become the highest-grossing Malayalam release of 2026 so far. That would make it the sixth Malayalam title ever to cross ₹200 crore worldwide, joining an exclusive club that includes Lokah Chapter 1 (₹303 crore), Empuraan (₹266 crore), Manjummel Boys (₹241 crore), and Thudarum (₹235 crore).

## What It Means for the Franchise

Drishyam 3 marks the end of Georgekutty's journey, a character who has become one of the most iconic figures in Indian cinema over the past decade. The franchise that started as a modest Malayalam thriller in 2013 went on to spawn a Tamil remake (Papanasam), a Hindi remake (Drishyam, starring Ajay Devgn), and sequels in both languages. Together, the franchise has generated well over ₹1,000 crore across all versions.

For Mohanlal, the film arrives at a time when he is enjoying one of the most commercially successful stretches of his five-decade career. Between Empuraan and Drishyam 3, the superstar has delivered two ₹200-crore-plus grossers within months of each other. At 65, he remains the most bankable star in Malayalam cinema.

## The Diaspora Takeaway

The overseas performance of Drishyam 3 reinforces a pattern that has become impossible for the industry to ignore. Malayalam cinema's diaspora audience, concentrated in the Gulf, North America, and the UK, is not just a bonus market anymore. For a film like Drishyam 3, where international collections account for nearly half of the worldwide gross, the diaspora is a co-equal market. The $10 million overseas figure is a landmark that signals Malayalam cinema's growing commercial footprint beyond India's borders, something the Hindi film industry, with its much larger domestic base, has been slower to achieve on a per-film basis.

The franchise may be over, but the audience Georgekutty built is not going anywhere."""

    # Image sourcing
    img_url, img_attr, _ = source_image(
        ["Mohanlal"],
        ["Mohanlal actor", "Drishyam Mohanlal Malayalam"],
        slug
    )
    
    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "entertainment",
        "vertical": "entertainment",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "sources": json.dumps([
            {"name": "Sacnilk", "url": "https://sacnilk.com/articles/mollywood/Drishyam_3_Box_Office"},
            {"name": "The Daily Jagran", "url": "https://thedailyjagran.com/entertainment/bollywood/drishyam-3-box-office-collection-day-15"},
            {"name": "Wikipedia", "url": "https://en.wikipedia.org/wiki/Drishyam_3"}
        ]),
        "tags": ["drishyam-3", "mohanlal", "malayalam-cinema", "box-office", "overseas-collections", "jeethu-joseph"],
        "score_total": 80,
        "urgency": "medium",
        "diaspora_angle": "Drishyam 3's overseas collections account for nearly half its worldwide gross, with the Gulf, North America, and UK driving the $10M milestone — reflecting the Malayalam diaspora's growing box office power.",
        "is_editorial": False,
        "image_url": img_url,
        "image_caption": "Mohanlal, who plays Georgekutty in the Drishyam franchise",
        "image_attribution": img_attr or "Wikimedia Commons"
    }
    
    return insert_article(article)


# ========== ARTICLE 2: Indian Actors in Hollywood ==========
def write_article_2():
    print("\n=== ARTICLE 2: Indian Actors Building Hollywood Careers ===")
    
    slug = "indian-actors-hollywood-careers-adarsh-gourav-ali-fazal-ishaan-khatter-diaspora-nri-20260606"
    headline = "Five Indian Actors Are Building Real Hollywood Careers. Not Cameos. Careers."
    subheadline = "From Alien: Earth to The Knife, Adarsh Gourav, Ali Fazal, Ishaan Khatter, Riccha Sinha, and Disha Patani are no longer crossing over. They are staying."
    
    body = """For decades, the story of Indian actors in Hollywood followed a depressingly familiar script. A brief appearance in a big-budget film. A press tour. A return to Mumbai. The crossover was always the headline, never the career. That pattern is finally breaking, and the actors doing it are not the ones most people would have predicted.

## Adarsh Gourav: The Quiet Frontrunner

Adarsh Gourav's trajectory is the most remarkable of the lot. His BAFTA-nominated turn in The White Tiger in 2021 was supposed to be his introduction. What followed has been a methodical expansion into territory no Indian actor of his generation has occupied. Apple TV+'s Extrapolations put him alongside Keri Russell, who was reportedly so struck by his work mid-shoot that she sought out the director to ask who he was. Then came Alien: Earth, the FX series created by Noah Hawley and produced by Ridley Scott, where Gourav plays one of the leads. Not a supporting role. Not a cultural tokenism casting. A lead in a Ridley Scott production.

Three major international productions, each in a different genre, with different casts and different creative ecosystems. That is not luck. That is range, and it is the kind of body of work that opens doors to scripts that never reach Indian actors' desks. He is currently working on Voices of the Land, a docu-series set to stream on JioHotstar, while also maintaining his Bollywood presence.

## Ali Fazal: The Long Game

Ali Fazal has been at this longer than anyone. Furious 7 in 2015 was a foot in the door. Victoria & Abdul opposite Judi Dench in 2017 was the moment critics noticed. Death on the Nile in 2022 proved he could hold his own in an ensemble. Kandahar showed he could anchor action. His most recent international outing, Rule Breakers, directed by two-time Oscar winner Bill Guttentag and co-starring Phoebe Waller-Bridge, is the kind of mid-budget, story-driven project that defines a career rather than decorates it.

What makes Fazal's approach distinctive is its simultaneity. He has never abandoned his Indian career to chase Hollywood. Mirzapur remains one of the most-watched Hindi web series, and he continues to take on Indian projects between international shoots. The dual-track career, once considered impossible to sustain, has become his signature.

## Ishaan Khatter: The Breakout Bet

Ishaan Khatter's Hollywood play is newer but aggressive. His casting in major international productions signals a bet by Western studios on a younger, more contemporary Indian face. The advantage Khatter brings is generational: he grew up bilingual, culturally fluid, and deeply embedded in both Bollywood (as Shahid Kapoor's brother and a Majidi/Bhardwaj-trained actor) and global pop culture. That fluency shows in audition rooms and on set in ways that earlier generations of Indian actors had to work much harder to project.

## Riccha Sinha and Disha Patani: Expanding the Map

The less expected names on this list are Riccha Sinha and Disha Patani. Sinha, relatively unknown to mainstream Indian audiences, has been quietly building a body of international work that bypasses Bollywood entirely. Patani, better known as a commercial Hindi cinema star, has pivoted toward international projects that leverage her action training and physical presence in ways her Indian filmography rarely did.

## What It Means for the Diaspora

For Indian Americans and NRIs who grew up watching Bollywood while consuming Hollywood, these careers represent something new. For the first time, there are Indian actors who belong to both industries without being visitors in either. That changes what stories get told, what characters get written, and what audiences get to see.

The generation of Irrfan Khan and Priyanka Chopra opened the door. The generation of Adarsh Gourav, Ali Fazal, and Ishaan Khatter is the first to walk through it and not walk back. The crossover is no longer the story. The body of work is."""

    # Image sourcing — try Adarsh Gourav
    img_url, img_attr, _ = source_image(
        ["Adarsh Gourav", "Ali Fazal"],
        ["Indian actors Hollywood international cinema", "Bollywood actors international"],
        slug
    )
    
    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "entertainment",
        "vertical": "entertainment",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "sources": json.dumps([
            {"name": "Filmibeat", "url": "https://www.filmibeat.com/bollywood/features/how-ali-fazal-ishaan-khatter-adarsh-gourav-building-global-careers.html"},
            {"name": "Bollywood Hungama", "url": "https://www.bollywoodhungama.com/news/features/adarsh-gourav-alien-earth-ridley-scott/"}
        ]),
        "tags": ["adarsh-gourav", "ali-fazal", "ishaan-khatter", "hollywood", "diaspora-actors", "alien-earth"],
        "score_total": 78,
        "urgency": "medium",
        "diaspora_angle": "For Indian Americans who grew up watching Bollywood while consuming Hollywood, these actors represent the first generation to build genuine dual-industry careers — changing what stories get told and what characters get written.",
        "is_editorial": False,
        "image_url": img_url,
        "image_caption": "Adarsh Gourav, who plays a lead role in Ridley Scott's Alien: Earth series",
        "image_attribution": img_attr or "Wikimedia Commons"
    }
    
    return insert_article(article)


# ========== ARTICLE 3: Welcome To The Jungle ==========
def write_article_3():
    print("\n=== ARTICLE 3: Welcome To The Jungle ===")
    
    slug = "welcome-to-the-jungle-akshay-kumar-june-26-24-cast-comedy-franchise-nri-20260606"
    headline = "Welcome To The Jungle Has 24 Stars, a June 26 Date, and Akshay Kumar's Best Comic Instincts. Bollywood Is Betting Big on Nostalgia."
    subheadline = "The third Welcome film arrives with the biggest ensemble cast in recent Hindi cinema history and a distribution deal that covers theatres, TV, and streaming in one sweep."
    
    body = """At a time when Hindi cinema is packed with intense actioners, dark dramas, spy thrillers, and heavy-duty emotional stories, Welcome To The Jungle is preparing to offer something that audiences have been starved of: a full-blown, large-scale, family-friendly stress-buster. The film is scheduled to arrive in cinemas on June 26, and with Akshay Kumar leading a 24-member ensemble, it has already positioned itself as the most anticipated comedy of 2026.

## The Franchise That Refuses to Die

The original Welcome, released in 2007, was not supposed to become a franchise. Directed by Anees Bazmee, it was a chaotic comedy about gangsters, mistaken identities, and absurd situations that somehow became one of the most-quoted Hindi films of the 2000s. Welcome Back followed in 2015, and while it did not match the original's cult status, it proved the franchise had commercial legs.

Welcome To The Jungle, directed by Ahmed Khan, takes the franchise into new territory. Literally. The setting has shifted from cityscapes to a jungle backdrop, adding a survival-comedy element to the franchise's trademark slapstick. The teaser, dropped without prior announcement in mid-May, was filled with the kind of over-the-top comedic chaos that fans of the series expect, and social media reception was overwhelmingly positive.

## The Cast Is the Selling Point

No Hindi film in recent memory has assembled this many recognizable faces. The lineup reads like a who's who of Bollywood comedy: Akshay Kumar, Suniel Shetty, Paresh Rawal, Sanjay Dutt, Arshad Warsi, Raveena Tandon, Lara Dutta, Jacqueline Fernandez, Disha Patani, Johnny Lever, Rajpal Yadav, Tusshar Kapoor, Shreyas Talpade, Krushna Abhishek, and Kiku Sharda, among others.

The challenge with multi-starrers of this scale is always screen time. Every actor needs a moment that justifies their presence, and the risk of overcrowding is real. But the Welcome franchise has always thrived on ensemble chaos. The appeal is not any single performance but the collective madness of everyone playing off each other. If Ahmed Khan can manage the traffic, the sheer star power on screen could be electric.

## Akshay Kumar's Comic Comeback

For Akshay Kumar, Welcome To The Jungle arrives at a moment of renewed commercial confidence. His recent film Bhooth Bangla has already crossed Sooryavanshi's worldwide numbers, making it his second-highest post-COVID grosser. The horror-comedy proved that audiences still respond to Akshay when he is operating in the zone he built his career in: comedy with physical energy and impeccable timing.

Long before action universes and pan-India spectacles became the order of the day, Akshay had built a comic legacy through films like Hera Pheri, Garam Masala, Bhagam Bhag, and the original Welcome. His ability to surrender to madness, react with a straight face in the middle of chaos, and elevate absurd situations with his timing has always been one of his biggest strengths. Welcome To The Jungle is positioned as a full return to that vintage energy.

## The Business Side

The film's distribution structure reflects the modern economics of Hindi cinema. JioStar has acquired domestic theatrical rights along with satellite and OTT rights, giving the company complete control over the film's India lifecycle from theatres to television premiere to streaming on JioHotstar. On the international front, Pen Marudhar is in advanced talks for overseas theatrical rights, with strong interest driven by the franchise's popularity among diaspora audiences in the Middle East, the UK, and North America.

This bundled deal structure ensures substantial cost recovery before release, significantly reducing financial risk for the makers and allowing the film to enter theatres in a comfortable position. It is a model that other big-budget comedies will likely study.

## Why the Diaspora Should Pay Attention

The Welcome franchise has always been disproportionately popular with overseas Indian audiences. The original became a staple of family movie nights across NRI households, its dialogues entering the shared vocabulary of a generation. The franchise's appeal to the diaspora is partly nostalgic and partly practical: these are films that entire families can watch together without anyone feeling excluded, a rarity in an era of R-rated thrillers and dark dramas.

Welcome To The Jungle, with its June 26 release date, is perfectly positioned for the summer moviegoing window when diaspora families are most likely to visit theatres together. If the film delivers even half the laughs that its teaser promises, it could become the Hindi comedy event of the year."""

    # Image sourcing
    img_url, img_attr, _ = source_image(
        ["Akshay Kumar"],
        ["Akshay Kumar comedy actor", "Welcome Bollywood comedy film"],
        slug
    )
    
    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "entertainment",
        "vertical": "entertainment",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "sources": json.dumps([
            {"name": "Bollywood Hungama", "url": "https://www.bollywoodhungama.com/news/features/welcome-to-the-jungle-bollywoods-biggest-stressbuster-2026/"},
            {"name": "Sacnilk", "url": "https://sacnilk.com/articles/bollywood/Welcome_To_The_Jungle_Teaser"},
            {"name": "Sacnilk", "url": "https://sacnilk.com/articles/bollywood/Welcome_To_The_Jungle_Distribution_Deals"}
        ]),
        "tags": ["akshay-kumar", "welcome-to-the-jungle", "bollywood-comedy", "ensemble-cast", "june-2026"],
        "score_total": 76,
        "urgency": "medium",
        "diaspora_angle": "The Welcome franchise has always been disproportionately popular with overseas Indian audiences, becoming a staple of NRI family movie nights. The June 26 release targets the summer window when diaspora families are most likely to visit theatres together.",
        "is_editorial": False,
        "image_url": img_url,
        "image_caption": "Akshay Kumar, who leads the 24-member cast of Welcome To The Jungle",
        "image_attribution": img_attr or "Wikimedia Commons"
    }
    
    return insert_article(article)


# ========== MAIN ==========
if __name__ == "__main__":
    print(f"Entertainment writer run: {datetime.now(timezone.utc).isoformat()}")
    
    results = []
    
    art1_id = write_article_1()
    results.append(("Drishyam 3 Box Office", art1_id))
    time.sleep(2)
    
    art2_id = write_article_2()
    results.append(("Indian Actors Hollywood", art2_id))
    time.sleep(2)
    
    art3_id = write_article_3()
    results.append(("Welcome To The Jungle", art3_id))
    
    print("\n=== RESULTS ===")
    for title, aid in results:
        status = "✓" if aid else "✗"
        print(f"  {status} {title}: {aid}")
    
    success_count = sum(1 for _, aid in results if aid)
    print(f"\n{success_count}/3 articles published successfully")

#!/usr/bin/env python3
"""
Entertainment writer for The Videshi — June 3, 2026
3 articles:
1. Cocktail 2 trailer drops — Shahid Kapoor, Kriti Sanon, Rashmika Mandanna
2. Maa Behen — Madhuri Dixit dark comedy on Netflix (June 4)
3. Taylor Swift x Toy Story 5 — "I Knew It, I Knew You" song, Indian release June 19
"""

import os, json, time, uuid, hashlib, requests, urllib.parse, subprocess
from datetime import datetime, timezone
from io import BytesIO

# ── env ──────────────────────────────────────────────────────────────
def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                k = k.replace('export ', '').strip()
                v = v.strip().strip('"').strip("'")
                os.environ[k] = v

load_env(os.path.expanduser('~/workspace/.env.supabase'))
load_env(os.path.expanduser('~/.env.supabase'))  # Load AFTER workspace — has correct JWT keys
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SB_URL = os.environ.get('SUPABASE_URL', '')
SB_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY', '')
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

def sb_headers():
    return {
        "apikey": SB_KEY,
        "Authorization": f"Bearer {SB_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }

# ── image sourcing ──────────────────────────────────────────────────
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
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
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
                w = ii.get("width", 0)
                if w < 300:
                    continue
                results.append({
                    "url": ii.get("thumburl") or ii.get("url", ""),
                    "original_url": ii.get("url", ""),
                    "title": page.get("title", ""),
                    "width": w,
                    "height": ii.get("height", 0),
                    "mime": mime
                })
            if results:
                print(f"  ✓ Wikimedia Commons: {len(results)} images for '{search_query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Wikimedia Commons error: {e}")
    return []

def fetch_pexels_image(query):
    """Search Pexels with curl (urllib gets 403)."""
    if not PEXELS_KEY:
        return None
    try:
        cmd = [
            'curl', '-sS', '-H', f'Authorization: {PEXELS_KEY}',
            f'https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page=3&orientation=landscape'
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        if result.returncode == 0:
            data = json.loads(result.stdout)
            photos = data.get('photos', [])
            if photos:
                url = photos[0]['src']['large2x']
                print(f"  ✓ Pexels image found for '{query}': {url[:60]}...")
                return url
    except Exception as e:
        print(f"  ⚠ Pexels error: {e}")
    return None

def download_and_compress(url, max_width=1200, quality=80):
    """Download image and compress to JPEG."""
    try:
        r = requests.get(url, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, timeout=20)
        if r.status_code != 200:
            print(f"  ⚠ Download failed: HTTP {r.status_code}")
            return None
        ct = r.headers.get('Content-Type', '')
        if 'image' not in ct and len(r.content) < 5000:
            print(f"  ⚠ Not a valid image (Content-Type: {ct}, size: {len(r.content)})")
            return None
        from PIL import Image
        img = Image.open(BytesIO(r.content))
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        if img.width > max_width:
            ratio = max_width / img.width
            img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
        buf = BytesIO()
        img.save(buf, format='JPEG', quality=quality, optimize=True)
        data = buf.getvalue()
        size_kb = len(data) / 1024
        print(f"  ✓ Compressed: {img.width}x{img.height}, {size_kb:.0f} KB")
        if len(data) < 5000:
            print(f"  ⚠ Too small after compression ({len(data)} bytes), skipping")
            return None
        return data
    except Exception as e:
        print(f"  ⚠ Download/compress error: {e}")
        return None

def upload_to_supabase(img_bytes, filename):
    """Upload image bytes to Supabase storage bucket 'article-images'."""
    url = f"{SB_URL}/storage/v1/object/article-images/{filename}"
    headers = {
        "Authorization": f"Bearer {SB_KEY}",
        "Content-Type": "image/jpeg",
        "x-upsert": "true"
    }
    try:
        r = requests.post(url, data=img_bytes, headers=headers, timeout=30)
        if r.status_code in (200, 201):
            public_url = f"{SB_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {public_url[:70]}...")
            return public_url
        else:
            print(f"  ⚠ Upload failed: {r.status_code} {r.text[:200]}")
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
    return None

def source_image(person_name=None, topic_queries=None, pexels_query=None, slug="article"):
    """Multi-source image search: Wikipedia > Wikimedia Commons > Pexels. Returns (url, attribution)."""
    candidates = []

    # Source 1: Wikipedia (for person articles)
    if person_name:
        wiki_img = fetch_wikipedia_person_image(person_name)
        if wiki_img:
            candidates.append({"url": wiki_img, "source": "wikipedia", "relevance": 3})

    # Source 2: Wikimedia Commons
    if topic_queries:
        for q in topic_queries[:3]:
            commons = fetch_wikimedia_commons_images(q)
            for c in commons[:2]:
                candidates.append({"url": c["url"], "source": "wikimedia_commons", "relevance": 2})

    # Source 3: Pexels
    if pexels_query:
        pex = fetch_pexels_image(pexels_query)
        if pex:
            candidates.append({"url": pex, "source": "pexels", "relevance": 1})

    # Pick best candidate and upload
    candidates.sort(key=lambda x: x["relevance"], reverse=True)
    for c in candidates:
        print(f"  Trying {c['source']}: {c['url'][:70]}...")
        img_bytes = download_and_compress(c["url"])
        if img_bytes:
            filename = f"{slug}.jpg"
            sb_url = upload_to_supabase(img_bytes, filename)
            if sb_url:
                attr = "Wikimedia Commons" if c["source"] in ("wikipedia", "wikimedia_commons") else "Pexels"
                return sb_url, attr

    print("  ✗ No image found from any source")
    return None, None

def insert_article(article):
    """Insert article into p2_articles."""
    url = f"{SB_URL}/rest/v1/p2_articles"
    r = requests.post(url, json=article, headers=sb_headers(), timeout=30)
    if r.status_code in (200, 201):
        data = r.json()
        art_id = data[0]['id'] if isinstance(data, list) else data.get('id')
        print(f"  ✓ Inserted article: {article['slug']} (id: {art_id})")
        return art_id
    else:
        print(f"  ✗ Insert failed: {r.status_code} {r.text[:300]}")
        return None


# ═══════════════════════════════════════════════════════════════════
# ARTICLE 1: Cocktail 2 Trailer
# ═══════════════════════════════════════════════════════════════════
def write_cocktail2():
    print("\n═══ Article 1: Cocktail 2 Trailer ═══")
    slug = "cocktail-2-trailer-shahid-kapoor-kriti-sanon-rashmika-mandanna-june-19-nri-20260603"

    # Image sourcing
    print("  Sourcing image...")
    img_url, img_attr = source_image(
        person_name="Shahid Kapoor",
        topic_queries=["Cocktail 2 Bollywood film 2026", "Shahid Kapoor actor"],
        pexels_query="cocktail party friends celebration",
        slug=slug
    )

    headline = "The Cocktail 2 Trailer Just Dropped. For NRIs Who Grew Up on the Original, This One Hits Different."
    subheadline = "Shahid Kapoor, Kriti Sanon, and Rashmika Mandanna step into a love triangle that updates the 2012 formula for a generation that dates through apps and lives across continents."

    body = """Fourteen years after Saif Ali Khan, Deepika Padukone, and Diana Penty made an entire generation rethink what a Bollywood love triangle could look like, director Homi Adajania is back with a fresh cast and a sharper premise. The trailer for Cocktail 2 dropped on June 2, and if you lived through the original — whether in a Mumbai multiplex or a rented-out theater in Edison, New Jersey — you already know why this matters.

The new film stars Shahid Kapoor as Kunal, Kriti Sanon as Ally, and Rashmika Mandanna as Diya. The setup will feel familiar: three people, overlapping feelings, and the slow realization that friendship and romance don't always coexist peacefully. But Adajania, working from a script by Tarun Jain and Luv Ranjan, has clearly moved the story forward. This isn't the London of the original. The characters are navigating modern Indian urban life — dating apps, professional ambition, and the pressure to define relationships on someone else's timeline.

## What the Trailer Gets Right

The chemistry between Shahid and Kriti, who previously worked together on the hit Teri Baaton Mein Aisa Uljha Jiya, is immediate and electric. Their scenes together carry a breezy confidence that the trailer leans into hard. Rashmika's Diya, meanwhile, brings an emotional weight that grounds the comedy. When the iconic "Tum Hi Ho Bandhu" kicks in — reworked for this film — it's a direct shot of nostalgia that ties the sequel to its predecessor without leaning on it as a crutch.

Music director Pritam Chakraborty has already released two tracks, "Mashooka" and "Tujhko," both of which have been generating significant buzz. "Mashooka" is the summer anthem, shot in Sicily, while "Tujhko" is an Arijit Singh ballad that reportedly left media attendees at a preview event visibly emotional. Lyrics by Amitabh Bhattacharya complete a team that knows exactly how to make a Hindi film song land.

## Why This Matters to the Diaspora

The original Cocktail was a landmark for NRI audiences. It was one of the first mainstream Bollywood films to acknowledge that Indian women living abroad might be messy, independent, and uninterested in fitting a traditional mold — and that this was not a character flaw. Deepika's Veronica became an icon precisely because she refused to apologize for who she was, even as the script ultimately softened her edges.

Cocktail 2 isn't a direct sequel — it's a spiritual successor with entirely new characters. But the themes it explores — loyalty, self-worth, the chaos of feelings that don't follow a script — resonate deeply with a diaspora audience that has spent the last decade navigating those same questions across cultures. The trailer hints that this version will be less interested in resolution and more interested in the mess itself.

## The Business Side

Produced by Maddock Films and Luv Films, Cocktail 2 releases in theaters on June 19. That puts it in direct competition with Toy Story 5, which opens the same day in India. The counter-programming is deliberate: families go to Pixar, couples and friend groups go to Cocktail. For NRI audiences, both films will be available in North American theaters, creating a rare weekend where Indian and Hollywood releases compete for the same diaspora wallet.

Shahid Kapoor has been on a strong run, and this film positions him as the anchor of what could become Bollywood's most commercially reliable romantic franchise. Kriti Sanon continues her steady ascent from rom-com star to bonafide box office draw. And Rashmika Mandanna, already a massive draw in Telugu and Kannada markets, gets her most prominent Hindi role yet.

The original Cocktail grossed over ₹150 crore worldwide and became a cultural touchstone. Whether the sequel can replicate that isn't really the question. The question is whether it can speak to the generation that grew up on the first one and has since moved to a different country, a different phase of life, and a different understanding of love. Based on the trailer, Adajania seems to understand the assignment.

*Cocktail 2 releases in theaters worldwide on June 19, 2026.*

Sources: Bollywood Hungama, Filmfare, Pinkvilla"""

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "entertainment",
        "vertical": "entertainment",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "sources": json.dumps(["https://www.bollywoodhungama.com", "https://www.filmfare.com", "https://www.pinkvilla.com"]),
        "image_url": img_url,
        "image_attribution": img_attr,
        "is_editorial": False
    }

    return insert_article(article)


# ═══════════════════════════════════════════════════════════════════
# ARTICLE 2: Maa Behen on Netflix
# ═══════════════════════════════════════════════════════════════════
def write_maa_behen():
    print("\n═══ Article 2: Maa Behen on Netflix ═══")
    slug = "maa-behen-madhuri-dixit-triptii-dimri-netflix-dark-comedy-june-4-nri-20260603"

    print("  Sourcing image...")
    img_url, img_attr = source_image(
        person_name="Madhuri Dixit",
        topic_queries=["Madhuri Dixit actress Bollywood", "Triptii Dimri actress"],
        pexels_query="Indian mother daughters kitchen comedy",
        slug=slug
    )

    headline = "Madhuri Dixit Hides a Body in Her Kitchen. Triptii Dimri Helps. Netflix Drops Maa Behen Tomorrow."
    subheadline = "Suresh Triveni's dark comedy reunites Bollywood's most graceful star with its most in-demand newcomer — and gives NRI audiences exactly the kind of Hindi film they can stream at home on a weeknight."

    body = """There is a dead body in Rekha's kitchen. Rekha is played by Madhuri Dixit. This is not a sentence anyone expected to write in 2026, but here we are.

Maa Behen, directed by Suresh Triveni and premiering globally on Netflix on June 4, is a Hindi-language dark comedy-thriller about a widowed mother and her two estranged daughters who must work together to conceal a crime that occurs in the most domestic of settings. The premise is simple, the execution — based on the trailer and early buzz — is anything but.

## The Cast That Makes It Work

Madhuri Dixit plays Rekha, a woman who has spent decades holding her family together through sheer force of respectability. When that respectability is threatened by a corpse, she does what any resourceful Indian mother would do: she calls her daughters. Triptii Dimri plays Jaya, the elder daughter, and Dharna Durga plays Sushma, the younger one. The three have clearly not been in the same room for a while. The crime forces them back together, and the comedy comes from the collision of their very different survival instincts.

For Madhuri, this is the most interesting role she has taken in years. Her filmography over the last decade has been careful — sometimes too careful. Maa Behen asks her to be funny, desperate, morally compromised, and still unmistakably herself. Early reports suggest she delivers. For Triptii Dimri, who has been on a remarkable run since Animal and Bhool Bhulaiyaa 3, this is a chance to work in a register she hasn't yet explored: deadpan comedy alongside a screen legend.

The supporting cast — Ravi Kishan, Geetanjali Kulkarni, Arunoday Singh, and Jatin Sarna — fills out a small-town ecosystem where everyone knows everyone's business, and where hiding anything requires a level of coordination that this family simply does not possess.

## Suresh Triveni's Track Record

Triveni directed Tumhari Sulu, the Vidya Balan comedy that became one of 2017's most loved Hindi films, and Jalsa, the Vidya Balan-Shefali Shah thriller on Amazon. His sensibility is consistent: stories about women who are smarter than the systems they live in, told with warmth but without condescension. Maa Behen fits that template while adding a much darker edge. A woman who has to hide a body isn't just navigating social expectations — she is fighting for her freedom.

## Why This Is a Big Deal for Streaming

The Netflix India slate has been uneven. For every Sacred Games, there have been films that felt like theatrical rejects given a streaming window. Maa Behen is different. It was conceived for Netflix, shot for the platform's global audience, and designed to work in the intimate setting of a living room screen. The runtime is tight (reportedly under two hours), the tone is precise, and the cast is calibrated for both star power and acting chops.

For NRI audiences, the appeal is obvious. This is the kind of Hindi film that works perfectly for a weeknight watch — sharp, self-contained, and anchored by faces you trust. Madhuri Dixit remains one of the most beloved figures in the Indian diaspora. Seeing her in a genuinely surprising role, available globally on the same day, is exactly the kind of moment that justifies paying for a Netflix subscription.

## The Bigger Picture

Maa Behen joins a week that already includes Dhurandhar 2 on JioHotstar, Gullak Season 5 on SonyLIV, Patriot on ZEE5, and Brown (starring Karisma Kapoor) also on ZEE5. For diaspora audiences with subscriptions to multiple platforms, this is the most stacked OTT week of 2026 so far. The question isn't whether there's enough to watch. The question is whether there's enough time.

Madhuri Dixit hiding a body in a kitchen. Triptii Dimri helping her clean up. Nosy neighbors closing in. This is the Hindi dark comedy we didn't know we needed.

*Maa Behen premieres globally on Netflix on June 4, 2026.*

Sources: Decider, Filmfare, FilmiBeat"""

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "entertainment",
        "vertical": "entertainment",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "sources": json.dumps(["https://decider.com", "https://www.filmfare.com", "https://www.filmibeat.com"]),
        "image_url": img_url,
        "image_attribution": img_attr,
        "is_editorial": False
    }

    return insert_article(article)


# ═══════════════════════════════════════════════════════════════════
# ARTICLE 3: Taylor Swift x Toy Story 5
# ═══════════════════════════════════════════════════════════════════
def write_taylor_toy_story():
    print("\n═══ Article 3: Taylor Swift x Toy Story 5 ═══")
    slug = "taylor-swift-toy-story-5-i-knew-it-i-knew-you-india-release-june-19-nri-20260603"

    print("  Sourcing image...")
    img_url, img_attr = source_image(
        person_name=None,
        topic_queries=["Toy Story 5 Pixar 2026", "Toy Story Woody Buzz Lightyear Pixar"],
        pexels_query="animated toys colorful childhood Pixar",
        slug=slug
    )

    headline = "Taylor Swift Wrote a Song for Toy Story 5. The Film Opens in India on June 19. Here's Why NRI Families Should Care."
    subheadline = "The biggest pop star in the world meets the most beloved animated franchise. For Indian diaspora families raising kids between two cultures, this is the summer movie event that actually matters."

    body = """The longest-running tease in recent entertainment history ended on June 2 when Taylor Swift confirmed what the internet had been guessing for weeks: she has written and produced a new original song, "I Knew It, I Knew You," for Disney and Pixar's Toy Story 5. The song, co-produced with Jack Antonoff, drops on June 5. The film opens worldwide — including in India, in English and Hindi — on June 19.

The buildup was vintage Swift. Cryptic billboards featuring "TS" appeared in Los Angeles, Chicago, San Francisco, Toronto, Mexico City, and London. On TikTok, searching "Taylor Swift" triggered Toy Story clouds floating across the screen. The seagulls on her 1989 album cover were quietly replaced with clouds across streaming platforms. Every "S" and "T" in her Apple Music essentials playlist was capitalized. And her curated playlist included only the fifth track from each of her albums. The number 13 — Swift's lucky number — appeared alongside the clouds on Pixar's own billboards.

## Why This Collaboration Works

It is easy to be cynical about corporate synergies. But the Swift-Pixar partnership makes genuine creative sense. Toy Story 5 is built around the idea that playtime itself is under threat — that a tablet device named Lilypad, voiced by Greta Lee, could replace the physical toys that have defined Bonnie's childhood. The film's emotional core is about what it means to be outgrown, to become irrelevant, to fight for a place in someone's life. That territory is pure Swift.

"I fell instantly in love with Toy Story 5 when I was lucky enough to see it in its early stages, and I wrote this song as soon as I got home from the screening," Swift wrote on Instagram. "Sometimes you just know, right?"

Director Andrew Stanton, who helmed WALL·E and Finding Nemo, was equally direct: "Her connection to Jessie and the immediate way she understood what the character was going through was undeniable. The song is so deeply connected to Toy Story. On first listen, it instantly felt like it had always belonged there, like a long-lost family member. It was kismet."

## The India Angle

Toy Story 5 releases in India on June 19 in English and Hindi. For NRI families in the US, UK, and Canada, this is the summer movie event that transcends the usual Bollywood-vs-Hollywood divide. Indian diaspora kids who grew up watching Woody and Buzz are now parents themselves. The franchise's theme — that toys carry memory, that childhood objects hold emotional weight — resonates differently when you are raising children in a culture that isn't the one you grew up in.

The Hindi dub extends the reach to families who prefer watching animation in their home language. Pixar's Hindi dubs have historically been well-received, and Toy Story's universal themes translate without losing nuance.

## The Business Equation

Toy Story 5 opens the same day as Cocktail 2, creating a rare split-audience weekend where families and couples are effectively choosing between two major releases. In India, Pixar films have historically underperformed relative to their global numbers — but Toy Story carries more brand equity than any other animated franchise in the country. The Taylor Swift partnership, which has already generated billions of impressions across social media, changes the math. Swift's Indian fanbase is substantial and vocal. A Pixar film soundtracked by Swift is not the same proposition as a standard animated sequel.

Collector's edition CDs of the single — featuring standard, piano, and acoustic versions — went on sale on Swift's website on June 3, available for 48 hours. The marketing machine is running at full capacity.

## What to Expect

Tom Hanks returns as Woody, Tim Allen as Buzz Lightyear, and Joan Cusack as Jessie. Bad Bunny has a voice cameo as "Pizza with Sunglasses." Randy Newman, who has scored all five Toy Story films, returns to compose the original score. The film is directed by Stanton, co-directed by Kenna Harris, and produced by Lindsey Collins.

For Indian audiences — both in India and across the diaspora — this is not just another sequel. It is a generational handoff moment. The parents who watched the first Toy Story in 1995 are now taking their own children to see the fifth. Taylor Swift, who was five years old when the original came out, wrote a song about exactly that feeling. The symmetry is deliberate, and it works.

*Toy Story 5 releases in theaters in India on June 19, 2026, in English and Hindi. "I Knew It, I Knew You" drops on June 5.*

Sources: USA Today, People, Entertainment Weekly"""

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "entertainment",
        "vertical": "entertainment",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "sources": json.dumps(["https://www.usatoday.com", "https://people.com", "https://ew.com"]),
        "image_url": img_url,
        "image_attribution": img_attr,
        "is_editorial": False
    }

    return insert_article(article)


# ═══════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("=" * 60)
    print("The Videshi — Entertainment Writer — June 3, 2026")
    print("=" * 60)

    results = []

    art_id = write_cocktail2()
    results.append(("Cocktail 2 Trailer", art_id))

    art_id = write_maa_behen()
    results.append(("Maa Behen Netflix", art_id))

    art_id = write_taylor_toy_story()
    results.append(("Taylor Swift x Toy Story 5", art_id))

    print("\n" + "=" * 60)
    print("RESULTS:")
    for title, aid in results:
        status = f"✓ {aid}" if aid else "✗ FAILED"
        print(f"  {title}: {status}")
    print("=" * 60)

    failed = [t for t, a in results if not a]
    if failed:
        print(f"\n⚠ {len(failed)} article(s) failed: {', '.join(failed)}")
    else:
        print(f"\n✓ All {len(results)} articles published successfully")

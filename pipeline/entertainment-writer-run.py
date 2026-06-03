#!/usr/bin/env python3
"""Entertainment writer for The Videshi - June 3, 2026 evening run"""

import json, os, sys, time, uuid, re, io
import requests
from datetime import datetime, timezone

# Load env
def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, val = line.split('=', 1)
                    os.environ[key.strip()] = val.strip().strip('"').strip("'")

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

UA = "TheVideshi/1.0 (thevideshi.com)"

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
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
                print(f"  ✓ Wikimedia Commons: {len(results)} images found for '{search_query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Wikimedia Commons error for '{search_query}': {e}")
    return []


def fetch_pexels_image(query):
    """Search Pexels for a relevant image. Uses curl subprocess to avoid 403."""
    import subprocess
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    try:
        import urllib.parse
        encoded_q = urllib.parse.quote(query)
        result = subprocess.run(
            ["curl", "-sS", f"https://api.pexels.com/v1/search?query={encoded_q}&per_page=3",
             "-H", f"Authorization: {PEXELS_KEY}"],
            capture_output=True, text=True, timeout=15
        )
        data = json.loads(result.stdout)
        photos = data.get("photos", [])
        if photos:
            url = photos[0]["src"]["large2x"]
            print(f"  ✓ Pexels image found for '{query}': {url[:80]}...")
            return url
    except Exception as e:
        print(f"  ⚠ Pexels error for '{query}': {e}")
    return None


def compress_image(img_bytes, max_width=1200, quality=80):
    """Resize and compress image. Returns JPEG bytes."""
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


def upload_to_supabase_storage(img_url, filename):
    """Download image, compress, and upload to Supabase storage. Returns public URL."""
    try:
        r = requests.get(img_url, headers={"User-Agent": UA}, timeout=20)
        if r.status_code != 200:
            print(f"  ⚠ Failed to download image: HTTP {r.status_code}")
            return None
        content_type = r.headers.get('Content-Type', '')
        if not content_type.startswith('image/'):
            print(f"  ⚠ Not an image: {content_type}")
            return None
        if len(r.content) < 5000:
            print(f"  ⚠ Image too small: {len(r.content)} bytes")
            return None

        compressed = compress_image(r.content)
        print(f"  📦 Compressed: {len(r.content)} → {len(compressed)} bytes")

        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
        up_headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "image/jpeg",
            "x-upsert": "true"
        }
        up_r = requests.post(upload_url, headers=up_headers, data=compressed, timeout=30)
        if up_r.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {public_url[:80]}...")
            return public_url
        else:
            print(f"  ⚠ Upload failed: {up_r.status_code} {up_r.text[:200]}")
            return None
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
        return None


def source_image(person_names, topic_queries, slug):
    """Multi-source image search: Wikipedia → Wikimedia Commons → Pexels. Returns (url, attribution)."""
    candidates = []

    # Source 1: Wikipedia for person articles
    for name in person_names:
        wiki_img = fetch_wikipedia_person_image(name)
        if wiki_img:
            candidates.append({"url": wiki_img, "source": "wikipedia", "name": name})
            break

    # Source 2: Wikimedia Commons
    for query in topic_queries:
        commons = fetch_wikimedia_commons_images(query, limit=3)
        for c in commons[:2]:
            candidates.append({"url": c["url"], "source": "wikimedia_commons", "title": c.get("title", "")})
        if commons:
            break

    # Source 3: Pexels
    for query in topic_queries:
        pexels_img = fetch_pexels_image(query)
        if pexels_img:
            candidates.append({"url": pexels_img, "source": "pexels"})
            break

    # Pick best: Wikipedia > Wikimedia Commons > Pexels
    if not candidates:
        print("  ❌ No image candidates found")
        return None, None

    best = candidates[0]
    filename = f"{slug}.jpg"
    final_url = upload_to_supabase_storage(best["url"], filename)
    if final_url:
        attribution = "Wikimedia Commons" if best["source"] in ("wikipedia", "wikimedia_commons") else "The Videshi"
        return final_url, attribution

    # Try fallbacks
    for c in candidates[1:]:
        final_url = upload_to_supabase_storage(c["url"], filename)
        if final_url:
            attribution = "Wikimedia Commons" if c["source"] in ("wikipedia", "wikimedia_commons") else "The Videshi"
            return final_url, attribution

    return None, None


def insert_article(article):
    """Insert article into Supabase."""
    url = f"{SUPABASE_URL}/rest/v1/p2_articles"
    r = requests.post(url, headers=HEADERS, json=article, timeout=30)
    if r.status_code in (200, 201):
        data = r.json()
        art_id = data[0]["id"] if isinstance(data, list) and data else "unknown"
        print(f"  ✅ Published: {article['headline'][:60]}... (id: {art_id})")
        return art_id
    else:
        print(f"  ❌ Insert failed: {r.status_code} {r.text[:300]}")
        return None


# ============================================================
# ARTICLE 1: Cocktail 2 - Trailer drops, June 19 release
# ============================================================
def write_cocktail_2():
    print("\n📝 Writing: Cocktail 2")
    slug = "cocktail-2-shahid-kapoor-kriti-sanon-rashmika-trailer-june-19-nri-20260603"
    
    # Source image
    print("  🖼 Sourcing image...")
    img_url, attribution = source_image(
        person_names=["Shahid Kapoor", "Homi Adajania"],
        topic_queries=["Cocktail 2 Bollywood film", "Shahid Kapoor actor", "Bollywood romantic comedy"],
        slug=slug
    )

    body = """The trailer for *Cocktail 2* landed on June 2, and it delivered exactly what Homi Adajania promised: something funny, messy, emotional, and a little reckless. Fourteen years after the original *Cocktail* turned Deepika Padukone into a superstar, the franchise returns with an entirely new cast — Shahid Kapoor, Kriti Sanon, and Rashmika Mandanna — and a release date of June 19.

The two-and-a-half-minute trailer introduces three central characters: Kunal, Diya, and Ally. Their trajectories are immediately familiar to anyone who has navigated the chaos of modern relationships in their twenties — friendships that blur into attraction, attraction that complicates everything, and the emotional wreckage that follows when loyalty and desire pull in different directions. The trailer leans into this tension without resolving it, which is the point. Adajania is not interested in clean endings. He never was.

## What the Trailer Reveals

Maddock Films has positioned this as a spiritual successor rather than a direct sequel. There is no continuation of the Meera-Veronica-Gautam triangle from 2012. Instead, *Cocktail 2* revisits the franchise's core preoccupation — the messiness of young love in contemporary urban India — through a fresh lens. The film was shot partly in Sicily, Italy, and the Mediterranean light visible in the trailer gives it a visual warmth that the original, set mostly in London, deliberately avoided.

The music is already doing heavy promotional lifting. Composer Pritam, lyricist Amitabh Bhattacharya, and singer Arijit Singh have delivered two early standouts: *Mashooka*, an upbeat romantic number featuring Shahid and Kriti shot across Sicilian locations, and *Tujhko*, a slower, more emotionally charged track built around Shahid and Rashmika's characters. The trailer also teases a reimagined version of *Tumhi Ho Bandhu* from the original film, which drew the loudest online reaction within hours of the drop.

## The Cast Equation

Shahid Kapoor's involvement is the commercial anchor. He has not done a pure romantic drama in years, and the trailer suggests a return to the effortless charm of his earlier career — a mode that social media users were quick to call "old Shahid Kapoor era." Kriti Sanon, fresh off a productive stretch that includes her role in the upcoming *Cocktail 2* as a confident, sharp-tongued counterpoint to Shahid's more impulsive character, appears to be carrying the film's emotional center. Rashmika Mandanna, making her second major Hindi appearance after *Animal*, rounds out the triangle as the disruptive element.

The production team is stacked. Writer-producer Luv Ranjan co-wrote the screenplay alongside Tarun Jain and serves as creative lead. Producer Dinesh Vijan, who backed the original, called the reunion with Adajania a natural fit.

## The Diaspora Angle

For NRI audiences, the original *Cocktail* occupied a specific cultural moment. It was one of the first mainstream Bollywood films to openly portray a modern Indian woman who drank, partied, and owned her choices without being punished by the narrative — at least until the third act. The sequel arrives in a different cultural climate, and the trailer suggests it is aware of that shift. The relationship dynamics feel less judgmental, the comedy less reliant on shock, and the women less likely to be sorted into neat archetypes.

The June 19 release puts *Cocktail 2* in a crowded month. It opens between Imtiaz Ali's *Main Vaapas Aaunga* on June 12 and Akshay Kumar's *Welcome To The Jungle* on June 26. For diaspora audiences with limited theatrical windows, it is competing directly for the summer date-night slot. The Pritam soundtrack gives it an edge — Bollywood films that travel internationally almost always travel on their music first.

Advance bookings have not opened yet, but the trailer's reception — trending across Indian YouTube and Twitter within hours — suggests Maddock Films has a genuine crowd-puller on its hands. Whether *Cocktail 2* can match the cultural impact of the original is an open question. Whether it can match the box office is a likelier bet.

*Cocktail 2 releases in theaters on June 19, 2026.*"""

    article = {
        "headline": "Cocktail 2 Just Dropped Its Trailer. Shahid Kapoor, Kriti Sanon, and Rashmika Mandanna Are Betting on Messy Modern Love.",
        "subheadline": "Homi Adajania's sequel to the 2012 hit arrives June 19 with Pritam's music, Sicilian locations, and a love triangle built for a generation that grew up on the original.",
        "body": body,
        "slug": slug,
        "category": "entertainment",
        "vertical": "entertainment",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "is_editorial": False,
        "image_url": img_url,
        "image_attribution": attribution,
        "sources": json.dumps([
            {"name": "Bollywood Hungama", "url": "https://www.bollywoodhungama.com"},
            {"name": "Hollywood Reporter India", "url": "https://www.hollywoodreporterindia.com"},
            {"name": "Filmfare", "url": "https://www.filmfare.com"}
        ])
    }
    return insert_article(article)


# ============================================================
# ARTICLE 2: Main Vaapas Aaunga - Imtiaz Ali + Diljit + AR Rahman
# ============================================================
def write_main_vaapas_aaunga():
    print("\n📝 Writing: Main Vaapas Aaunga")
    slug = "main-vaapas-aaunga-imtiaz-ali-diljit-dosanjh-ar-rahman-june-12-nri-20260603"
    
    print("  🖼 Sourcing image...")
    img_url, attribution = source_image(
        person_names=["Diljit Dosanjh", "Imtiaz Ali"],
        topic_queries=["Diljit Dosanjh film", "Imtiaz Ali director", "Bollywood romance Punjab"],
        slug=slug
    )

    body = """Imtiaz Ali has spent the last two decades making films about people who leave home and then spend the rest of their lives trying to figure out what they left behind. With *Main Vaapas Aaunga*, releasing June 12, he is doing it again — except this time, the longing has a historical spine. The film is set partly in pre-Partition Punjab, and it stars Diljit Dosanjh, Naseeruddin Shah, Vedang Raina, and Sharvari in a story that spans generations, geographies, and the kind of emotional distances that no flight can close.

The advance bookings for North America opened a full week before India. That detail alone tells you who this film was partly made for.

## The Imtiaz Ali-Diljit Reunion

This is the second collaboration between Ali and Dosanjh after *Amar Singh Chamkila* in 2024, a film that turned Diljit from a global concert sensation into someone the Indian film establishment could no longer politely ignore. The reunion was inevitable. Ali has always been drawn to performers who carry real-world cultural weight, and Diljit — who debuted his *Main Vaapas Aaunga* trailer mid-concert during his AURA Tour stop in Toronto to a crowd of thousands — is the rare actor whose fan base does not need to be manufactured. It already exists, and it exists overwhelmingly among the diaspora.

Naseeruddin Shah's involvement adds a different kind of gravity. At this stage of his career, Shah does not sign on to anything that does not interest him. His presence in the trailer, in what appears to be the older timeline of the story, suggests the film's emotional weight rests on the consequences of choices made decades earlier.

## The Music Is Already Winning

A.R. Rahman composed the score. Irshad Kamil wrote the lyrics. Mohit Chauhan sings. If you have watched an Imtiaz Ali film in the last fifteen years, this combination needs no introduction. It is the team behind *Kun Faya Kun*, *Tum Ho* from *Rockstar*, and *Patakha Guddi* from *Highway*.

The album has rolled out steadily: *Kya Kamaal Hai*, *Maskara* (which went viral on social media), *Vo Nahin*, and most recently *Ishq Mastana*, released on Vedang Raina's birthday. The latest track blends Punjabi folk traditions with jazz and swing influences, built around a refrain borrowed from the 15th-century poet Sant Kabir: "Haman Hai Ishq Mastana, Haman Ko Hoshiyari Kya." That a mainstream Hindi film in 2026 is threading Kabir through A.R. Rahman through the story of undivided Punjab is either wildly ambitious or exactly what Imtiaz Ali does best. Possibly both.

## The Pre-Partition Setting

The trailer makes clear that the film operates across two timelines. The younger timeline features Vedang Raina and Sharvari in what looks like pre-Partition Punjab — colourful, communal in the older sense of the word, and alive with the kind of sensory detail that Ali's best films nail. The older timeline, anchored by Naseeruddin Shah and presumably Diljit, carries the cost of what Partition severed.

For the Indian diaspora, this is not abstract history. It is family history. The Partition of 1947 is the foundational rupture of countless NRI family trees — the reason grandparents speak of villages they cannot visit, the reason certain surnames cluster in certain cities in the UK and Canada. A film that dramatises that rupture through Imtiaz Ali's particular brand of romantic longing — not political, not polemical, just deeply personal — has the potential to connect with diaspora audiences in ways that most Bollywood films cannot.

## The Box Office Picture

*Main Vaapas Aaunga* arrives on June 12, a week after the *Toxic* and *Hai Jawani Toh Ishq Hona Hai* face-off and a week before *Cocktail 2*. The fact that North American advance bookings opened before India's is a strategic acknowledgment of Diljit's international fanbase — a fanbase that turned his Dil-Luminati and AURA tours into record-breaking events across North America and Europe.

Produced by Birla Studios and Applause Entertainment, with music on Tips, the film's commercial floor is set by its soundtrack. Its ceiling depends on whether Ali has made another *Rockstar* or another *Tamasha* — two films with very different commercial outcomes but, notably, the same long-term cultural footprint.

*Main Vaapas Aaunga releases in cinemas on June 12, 2026.*"""

    article = {
        "headline": "Imtiaz Ali, Diljit Dosanjh, and A.R. Rahman Made a Film About Partition. North America Gets to See It First.",
        "subheadline": "Main Vaapas Aaunga opens advance bookings in the US and Canada a week before India. For the diaspora, this is not just a movie — it is the family story nobody filmed until now.",
        "body": body,
        "slug": slug,
        "category": "entertainment",
        "vertical": "entertainment",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "is_editorial": False,
        "image_url": img_url,
        "image_attribution": attribution,
        "sources": json.dumps([
            {"name": "Bollywood Hungama", "url": "https://www.bollywoodhungama.com"},
            {"name": "India Forums", "url": "https://www.indiaforums.com"},
            {"name": "Koimoi", "url": "https://www.koimoi.com"}
        ])
    }
    return insert_article(article)


# ============================================================
# ARTICLE 3: Welcome To The Jungle - Akshay Kumar ensemble
# ============================================================
def write_welcome_jungle():
    print("\n📝 Writing: Welcome To The Jungle")
    slug = "welcome-to-the-jungle-akshay-kumar-ensemble-comedy-june-26-nri-20260603"
    
    print("  🖼 Sourcing image...")
    img_url, attribution = source_image(
        person_names=["Akshay Kumar", "Ahmed Khan (director)"],
        topic_queries=["Akshay Kumar comedy film", "Welcome Bollywood film franchise", "Bollywood ensemble comedy"],
        slug=slug
    )

    body = """Bollywood has spent the last two years producing spy universes, period epics, and action franchises calibrated for global box office records. *Welcome To The Jungle* is none of those things. It is a loud, overstuffed, unapologetically commercial comedy starring Akshay Kumar and approximately everyone else in the industry, and it arrives in theaters on June 26 at a moment when audiences might genuinely need it.

The film is the third installment of the *Welcome* franchise, which began in 2007 with Anees Bazmee's original — a slapstick comedy that became a permanent fixture on Indian television and, by extension, on the cultural hard drive of every NRI household with a cable connection and a tolerance for absurdity.

## The Cast Is the Pitch

Director Ahmed Khan has assembled a cast list that reads less like a credit sheet and more like a wedding guest list for a Bollywood producer's daughter: Akshay Kumar, Suniel Shetty, Paresh Rawal, Arshad Warsi, Raveena Tandon, Lara Dutta, Jacqueline Fernandez, Disha Patani, Johnny Lever, Rajpal Yadav, Tusshar Kapoor, Shreyas Talpade, and Bhojpuri star Akshara Singh, whose inclusion via the track *Ghis Ghis Ghis* has already made waves.

This is, by any reasonable count, the largest ensemble in a Hindi film this year. Khan has said the film contains five songs, and producer Firoz Nadiadwala — who backed the entire franchise — has been called "gutsy" for greenlighting a production of this scale in a climate where mid-budget films are struggling to fill seats.

The title track, a recreation of the 2007 original, dropped in late May and immediately became the subject of memes, Instagram reels, and wedding playlist debates. Khan described its making as "pure nostalgia." For the franchise's core audience, that is the entire selling proposition.

## Akshay Kumar's Comedy Recalibration

For Akshay Kumar, *Welcome To The Jungle* represents something more specific than a franchise sequel. It is a deliberate return to the comic mode that made him a household name long before *Sooryavanshi* or *Bell Bottom* or any of his more recent forays into patriotic action. The films that built his initial stardom — *Hera Pheri*, *Garam Masala*, *Bhagam Bhag*, the original *Welcome* — relied on his ability to play chaos with a straight face, to react rather than dominate, and to make absurd situations feel lived-in rather than scripted.

His most recent release, *Bhooth Bangla*, a horror-comedy that has crossed ₹171 crore net in India after five weeks, proved that the audience appetite for Kumar in this register has not diminished. *Welcome To The Jungle* doubles down on that bet.

## The NRI Living Room Factor

The original *Welcome* has a specific afterlife among diaspora audiences that no box office number can capture. It is the film that plays during Diwali dinner clean-up. It is the film that uncles quote at family gatherings. It is the film that second-generation NRI kids discovered on YouTube compilations before they ever saw it in full. The comedy is broad, the setups are ridiculous, and the punchlines land because they were never trying to be clever — they were trying to be funny, which is harder.

*Welcome To The Jungle* is banking on that inherited goodwill. The jungle setting, visible in Akshay's promotional images — a man in a dark suit walking down a red carpet through dense foliage — promises the same brand of absurdist comedy transplanted into a more exotic visual landscape. Khan has hinted at a blend of action and comedy, but make no mistake: this is a comedy first. The action exists to service the jokes, not the other way around.

## June's Crowded Calendar

The film releases on June 26, the last major theatrical date in a month that includes *Toxic* (June 4), *Hai Jawani Toh Ishq Hona Hai* (June 5), *Main Vaapas Aaunga* (June 12), *Cocktail 2* (June 19), and *Toy Story 5* (June 19). For NRI audiences who may only make it to the theater once or twice a month, the choice between a pre-Partition love story, a modern relationship drama, and a full-blown slapstick franchise sequel depends entirely on what they are in the mood for.

*Welcome To The Jungle* does not need to win that argument on artistic merit. It needs to win it on the promise of two hours where nobody has to think, everyone laughs, and the drive home involves quoting dialogue back and forth. For a certain kind of audience — and that audience is large, loyal, and disproportionately diasporic — that is enough.

*Welcome To The Jungle releases in theaters on June 26, 2026.*"""

    article = {
        "headline": "Welcome To The Jungle Has Akshay Kumar, Fifteen Co-Stars, and the Promise That Nobody Has to Think for Two Hours.",
        "subheadline": "The third installment of Bollywood's most quotable franchise arrives June 26 with the biggest ensemble cast of the year and a bet that NRI nostalgia still fills seats.",
        "body": body,
        "slug": slug,
        "category": "entertainment",
        "vertical": "entertainment",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "is_editorial": False,
        "image_url": img_url,
        "image_attribution": attribution,
        "sources": json.dumps([
            {"name": "Bollywood Hungama", "url": "https://www.bollywoodhungama.com"},
            {"name": "Sacnilk", "url": "https://www.sacnilk.com"},
            {"name": "Filmfare", "url": "https://www.filmfare.com"}
        ])
    }
    return insert_article(article)


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("The Videshi Entertainment Writer - June 3, 2026 evening")
    print("=" * 60)
    
    results = []
    
    art1 = write_cocktail_2()
    results.append(("Cocktail 2", art1))
    
    art2 = write_main_vaapas_aaunga()
    results.append(("Main Vaapas Aaunga", art2))
    
    art3 = write_welcome_jungle()
    results.append(("Welcome To The Jungle", art3))
    
    print("\n" + "=" * 60)
    print("RESULTS:")
    for name, art_id in results:
        status = f"✅ {art_id}" if art_id else "❌ FAILED"
        print(f"  {name}: {status}")
    
    success = sum(1 for _, a in results if a)
    print(f"\n{success}/{len(results)} articles published")
    print("=" * 60)

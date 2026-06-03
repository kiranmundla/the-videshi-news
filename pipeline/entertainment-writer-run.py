#!/usr/bin/env python3
"""Entertainment writer for The Videshi — June 3, 2026 evening run."""

import json, os, sys, time, uuid, re, io, urllib.parse
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
                    k, v = line.split('=', 1)
                    v = v.strip().strip('"').strip("'")
                    os.environ[k] = v

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

import requests
from PIL import Image

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

UA = "TheVideshi/1.0 (thevideshi.com)"

# ── Image sourcing functions ──

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
        print(f"  ⚠ Wikimedia Commons error for '{search_query}': {e}")
    return []


def fetch_pexels_image(query):
    """Search Pexels for an image. Returns URL or None."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    try:
        r = requests.get(
            "https://api.pexels.com/v1/search",
            params={"query": query, "per_page": 3, "orientation": "landscape"},
            headers={"Authorization": PEXELS_KEY},
            timeout=10
        )
        if r.status_code == 200:
            photos = r.json().get("photos", [])
            if photos:
                url = photos[0]["src"]["large2x"]
                print(f"  ✓ Pexels image found for '{query}': {url[:80]}...")
                return url
    except Exception as e:
        print(f"  ⚠ Pexels error for '{query}': {e}")
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


def download_and_upload_image(image_url, slug):
    """Download image, compress, upload to Supabase storage. Returns public URL or None."""
    try:
        r = requests.get(image_url, headers={"User-Agent": UA}, timeout=15)
        if r.status_code != 200:
            print(f"  ✗ Download failed ({r.status_code}): {image_url[:80]}")
            return None
        ct = r.headers.get("Content-Type", "")
        if not ct.startswith("image/"):
            print(f"  ✗ Not an image ({ct}): {image_url[:80]}")
            return None
        if len(r.content) < 5000:
            print(f"  ✗ Image too small ({len(r.content)} bytes)")
            return None

        compressed = compress_image(r.content)
        filename = f"{slug}.jpg"
        print(f"  → Uploading {filename} ({len(compressed)} bytes)...")

        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
        up = requests.post(
            upload_url,
            headers={
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "image/jpeg",
                "x-upsert": "true"
            },
            data=compressed,
            timeout=20
        )
        if up.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded: {public_url[:80]}")
            return public_url
        else:
            print(f"  ✗ Upload failed ({up.status_code}): {up.text[:200]}")
            return None
    except Exception as e:
        print(f"  ✗ Image pipeline error: {e}")
        return None


def source_image(person_names, topic_queries, pexels_query, slug):
    """Multi-source compare: Wikipedia > Wikimedia Commons > Pexels."""
    candidates = []

    # Source 1: Wikipedia person images
    for name in person_names:
        img = fetch_wikipedia_person_image(name)
        if img:
            candidates.append({"url": img, "source": "wikipedia", "name": name})
            break  # first found person is usually the main subject

    # Source 2: Wikimedia Commons
    for q in topic_queries:
        results = fetch_wikimedia_commons_images(q, limit=3)
        for r in results[:2]:
            candidates.append({"url": r["url"], "source": "wikimedia_commons", "title": r.get("title", "")})
        if results:
            break

    # Source 3: Pexels
    pimg = fetch_pexels_image(pexels_query)
    if pimg:
        candidates.append({"url": pimg, "source": "pexels"})

    # Pick best: wikipedia > commons > pexels
    for c in candidates:
        url = download_and_upload_image(c["url"], slug)
        if url:
            attr = "Wikimedia Commons" if c["source"] in ("wikipedia", "wikimedia_commons") else "The Videshi"
            return url, attr

    print(f"  ✗ No image found for {slug}")
    return None, None


def insert_article(article):
    """Insert an article into Supabase."""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=article,
        timeout=15
    )
    if r.status_code in (200, 201):
        data = r.json()
        art_id = data[0]["id"] if isinstance(data, list) and data else "unknown"
        print(f"  ✓ Published: {article['headline'][:60]}... (id: {art_id})")
        return art_id
    else:
        print(f"  ✗ Insert failed ({r.status_code}): {r.text[:300]}")
        return None


# ── Article definitions ──

articles_to_write = []

# ═══════════════════════════════════════════════════════
# ARTICLE 1: IMAX Returns to Hyderabad
# ═══════════════════════════════════════════════════════

art1_slug = "imax-returns-hyderabad-amb-cinemas-mahesh-babu-varanasi-nri-20260603"
art1_headline = "IMAX Is Coming Back to Hyderabad After a Decade. Mahesh Babu's AMB Cinemas Just Made It Official."
art1_subheadline = "Three new IMAX with Laser screens are on the way — the first timed perfectly for Rajamouli's Varanasi. For the Telugu diaspora, the city that builds India's biggest films finally gets the screen they deserve."
art1_body = """Hyderabad has not had an IMAX screen in over ten years. For a city that houses Ramoji Film City, anchors the Telugu film industry, and has produced some of the highest-grossing Indian films of the past decade — including the Baahubali franchise and RRR — that absence has been, to put it gently, absurd.

On June 1, IMAX Corporation and Asian Cinemas announced a deal that ends the drought. Three new IMAX with Laser locations will open under the AMB Cinemas brand, the luxury chain co-owned by Mahesh Babu. Two of the three screens will be in Hyderabad. The first, at AMB Classic, will open before the end of 2026. The remaining two are planned for 2028.

## The Varanasi Connection

The timing is not accidental. SS Rajamouli's Varanasi — the globe-spanning epic starring Mahesh Babu, Priyanka Chopra, and Prithviraj Sukumaran — is scheduled for worldwide release on April 7, 2027. The film was shot on IMAX-certified digital cameras. Rajamouli himself, during the Varanasi glimpse launch, had publicly called it "surprising" that Hyderabad lacked an IMAX screen despite producing some of India's biggest cinematic spectacles.

Now his own lead actor's cinema chain is solving that problem. The Varanasi official X account confirmed the news immediately: "Experience VARANASI in IMAX in HYDERABAD and worldwide on April 7th, 2027."

## Why This Matters Beyond One Film

IMAX's return to Hyderabad signals something larger about the economics of Indian exhibition. Rich Gelfond, the CEO of IMAX, said in his announcement that 2025 was IMAX's best year ever at the Indian box office, "powered by a dynamic slate of Hollywood and Indian films." The demand, according to Gelfond, is coming from both filmmakers and audiences.

That demand is not abstract. Films like Toxic (Yash), Raaka (Allu Arjun with Atlee), Kalki 2, and the rumored God of War adaptation are all high-visual-ambition projects that would benefit enormously from IMAX presentations. Telugu cinema has been making films at global scale for years. It just hasn't had the local screens to match.

Sunil Narang and Bharat Narang, the managing directors of AMB Cinemas, called the IMAX partnership "a matter of great honour and pride" and described it as the natural next step in AMB's push for cinematic excellence.

## The NRI Viewing Gap

For the Telugu diaspora in the United States, United Kingdom, and the Middle East, this story cuts both ways. NRIs have long had access to IMAX screenings of Telugu blockbusters in their local markets — from AMC and Regal chains in the US to Cineworld in the UK. The irony was always that you could watch a Tollywood spectacle in IMAX in New Jersey but not in Hyderabad.

That gap is now closing. And for the diaspora community that regularly travels back to India and follows Telugu cinema culture as closely as cricket, the upgrade of the home market's exhibition infrastructure matters. A first-run IMAX experience in Hyderabad will change how Telugu films are marketed, screened, and talked about — on both sides of the ocean.

## What Comes Next

The first AMB Classic IMAX screen is expected to be operational by late 2026, well ahead of Varanasi's April 2027 date. The two additional screens arriving by 2028 will further expand Hyderabad's premium exhibition capacity during a period when Telugu cinema's global footprint is at its highest point.

For a city that has quietly become the epicentre of India's most commercially ambitious filmmaking, the return of IMAX is not just an upgrade. It is a correction long overdue.

*Sources: IMAX Corporation press release (June 1, 2026); Bollywood Hungama; Hollywood Reporter India; Gulte*"""

art1_sources = ["IMAX Corporation press release (June 1, 2026)", "Bollywood Hungama", "Hollywood Reporter India", "Gulte"]

articles_to_write.append({
    "slug": art1_slug,
    "headline": art1_headline,
    "subheadline": art1_subheadline,
    "body": art1_body,
    "person_names": ["Mahesh Babu"],
    "topic_queries": ["IMAX Hyderabad cinema", "AMB Cinemas Hyderabad"],
    "pexels_query": "IMAX cinema theater screen",
    "sources": art1_sources
})

# ═══════════════════════════════════════════════════════
# ARTICLE 2: Drishyam 3 Hindi Wraps Shoot
# ═══════════════════════════════════════════════════════

art2_slug = "drishyam-3-hindi-wraps-shoot-ajay-devgn-october-2-jaideep-ahlawat-nri-20260603"
art2_headline = "Drishyam 3 Has Wrapped. Ajay Devgn's Version Promises a Very Different Film From the One Mohanlal Just Made."
art2_subheadline = "Director Abhishek Pathak says the Hindi adaptation leans into family thriller territory, not the drama-heavy approach of the Malayalam original. October 2 is the date. Jaideep Ahlawat and Prakash Raj are the new additions."
art2_body = """The Hindi Drishyam 3 has finished filming. Director Abhishek Pathak confirmed the wrap on June 2 with an emotional Instagram post, bringing to a close months of production across Mumbai and Goa. The film is now in post-production with a confirmed theatrical release on October 2, 2026 — the Gandhi Jayanti holiday window that Bollywood has traditionally treated as prime territory.

The announcement arrives at a uniquely interesting moment. The Malayalam Drishyam 3, starring Mohanlal and directed by Jeethu Joseph, released recently and has already crossed ₹225 crore worldwide. Audiences who have seen it know how that story ends. The question now is how different the Hindi version will be — and Pathak has been surprisingly direct about the answer.

## A Different Track for Hindi Audiences

In an interview with Pinkvilla, Pathak and producer Kumar Mangat Pathak revealed that the Hindi version will chart its own path. "What people are seeing right now in Malayalam Drishyam is different," the director said. "For the Hindi audience, I have created a completely different track that will work beautifully here. The Malayalam version focuses more on family drama, while the Hindi version will lean more towards a family thriller. That's the fabric of the film."

This is significant. The first two Hindi Drishyam films closely followed the Malayalam originals, with adjustments for tone and cultural context. A deliberate departure in the third installment suggests that Pathak is treating the franchise as its own entity now — one that can take narrative risks without being judged purely as a remake.

## The Cast Additions

Ajay Devgn returns as Vijay Salgaonkar, the small-town cable operator whose extraordinary ability to think under pressure has turned him into one of Bollywood's most unusual protagonists. Tabu reprises her role as Inspector General Meera Deshmukh, and Shriya Saran returns as Nandini Salgaonkar. Ishita Dutt and Rajat Kapoor round out the returning ensemble.

The new additions are where it gets interesting. Jaideep Ahlawat — last seen dominating the screen in Paatal Lok and earning a National Award for his performance — joins in a pivotal role that has not yet been revealed. Prakash Raj, who recently completed his portions, expressed confidence that the film would resonate with audiences.

The Ahlawat casting is particularly intriguing. Known for playing layered, morally complex characters, his presence suggests that Drishyam 3 will introduce a new adversary or complication that goes beyond the police procedural dynamic of the first two films.

## The Box Office Context

Drishyam 2 (Hindi) was a massive commercial success, earning over ₹240 crore worldwide against a modest budget. It proved that mid-budget, story-driven thrillers could compete with tentpole spectacles — a lesson the industry has repeatedly forgotten and relearned.

The October 2 release places Drishyam 3 in a window with relatively thin competition. The Gandhi Jayanti holiday provides a four-day opening weekend, and the film's franchise value ensures strong advance booking interest, particularly in multiplexes.

## For the Diaspora

The Drishyam franchise has a unique position in the NRI market. It is one of the few Hindi-language properties that consistently draws non-traditional Bollywood audiences — older viewers, couples, families — who might not turn up for a Yash action film or a Ranveer Singh spectacle but will absolutely show up for Ajay Devgn quietly outsmarting the law for two hours.

With the Malayalam version already in circulation and widely discussed in diaspora WhatsApp groups, the Hindi adaptation faces an unusual challenge: audiences who already know the broad strokes but are being promised a different experience. Pathak is betting that the "family thriller" pivot will be enough to justify the ticket. October 2 will tell us if he is right.

*Sources: Pinkvilla; Bollywood Hungama; Sacnilk; Zoom TV Entertainment*"""

art2_sources = ["Pinkvilla", "Bollywood Hungama", "Sacnilk", "Zoom TV Entertainment"]

articles_to_write.append({
    "slug": art2_slug,
    "headline": art2_headline,
    "subheadline": art2_subheadline,
    "body": art2_body,
    "person_names": ["Ajay Devgn", "Jaideep Ahlawat"],
    "topic_queries": ["Drishyam 3 Hindi film", "Ajay Devgn Drishyam"],
    "pexels_query": "Indian cinema thriller suspense",
    "sources": art2_sources
})

# ═══════════════════════════════════════════════════════
# ARTICLE 3: Jee Le Zaraa Is Finally Happening
# ═══════════════════════════════════════════════════════

art3_slug = "jee-le-zaraa-farhan-akhtar-priyanka-alia-katrina-road-trip-nri-20260603"
art3_headline = "Farhan Akhtar Is Location Scouting in Rajasthan. After Five Years of Delays, Jee Le Zaraa Looks Like It's Actually Happening."
art3_subheadline = "The Priyanka Chopra-Alia Bhatt-Katrina Kaif road trip film that was announced in 2021 is finally in active pre-production. Farhan Akhtar has shared scouting photos from the desert. There are even Shah Rukh Khan cameo rumours."
art3_body = """There is a long list of Bollywood films that were announced with great fanfare and then quietly disappeared into development limbo. Jee Le Zaraa has spent the last five years near the top of that list. But as of late May 2026, there are concrete signs that Farhan Akhtar's female-led road trip drama is finally moving beyond the idea stage.

Akhtar recently posted a photograph from what appears to be the Rajasthan desert, captioned simply: "Searching for gold." The post confirmed what industry sources had been reporting for weeks — that he has begun active location scouting for the film, with shooting expected to begin soon.

## The Long Road to Here

Jee Le Zaraa was announced in August 2021 with a cast that seemed almost too good to be real: Priyanka Chopra, Alia Bhatt, and Katrina Kaif, together for the first time, in a road trip film directed by Farhan Akhtar and co-written by Zoya Akhtar and Reema Kagti. Production was supposed to start in 2022.

It did not. The three leads had wildly conflicting schedules. Priyanka was between Citadel seasons in the US and UK. Alia was navigating motherhood and a packed Bollywood slate. Katrina married Vicky Kaushal and stepped back from the spotlight. At one point, there were reports that the original cast might not return at all.

By September 2025, Farhan addressed the speculation directly. "I can't comment on the cast anymore," he told a podcast, "but will the film happen? The film will happen." He confirmed that location scouting and music recording had already been completed, calling the script "too delicious" to abandon.

## What's Happening Now

The latest developments suggest the cast question has been resolved — or at least resolved enough to move forward. Alia and Priyanka are both between major projects (Alia just wrapped Alpha; Priyanka has Varanasi in post-production). Katrina, who has been the quietest of the three publicly, appears to have cleared her schedule as well.

The most tantalising development is the rumour that Shah Rukh Khan may appear in a cameo. SRK has form here — his brief appearances in Brahmastra and Rocketry were among the most talked-about moments in those films. A cameo in a Farhan Akhtar-directed film would fit neatly into the Excel Entertainment universe that includes Don, Don 2, and the original Dil Chahta Hai.

Neither the Khan camp nor the producers have confirmed the cameo. But the rumour alone tells you something about the scale of expectation around this project.

## The Zindagi Na Milegi Dobara Parallel

Jee Le Zaraa exists in the shadow of Zindagi Na Milegi Dobara, Zoya Akhtar's 2011 masterpiece about three friends on a road trip through Spain. That film was not just a box office hit — it became a cultural touchstone for an entire generation of Indian travellers, credited with single-handedly boosting tourism to Spain from India.

Jee Le Zaraa is being positioned as the female counterpart to that legacy. The idea, reportedly, originated with Katrina Kaif during the making of ZNMD, when she suggested a version with women in the lead. Fifteen years later, the concept has not lost its appeal. If anything, the hunger for a female-led ensemble film with actual star power — not a token indie casting — has only grown.

## Why NRIs Should Pay Attention

Priyanka Chopra is the most globally visible Indian actress of her generation. Her involvement automatically gives Jee Le Zaraa a diaspora marketing footprint that few Bollywood films can match. Add Alia Bhatt — who has her own significant NRI fanbase — and Katrina Kaif, whose appeal with diaspora audiences has been consistent since Namastey London, and you have a film that could be one of the biggest diaspora events of 2027.

For NRI audiences who have watched Bollywood's promised female ensemble projects fall apart before (Veere Di Wedding aside), Jee Le Zaraa's tortured journey to the starting line actually adds to the stakes. This is not a film that was casually greenlit. It has been fought for, delayed, defended, and now — apparently — rescued.

The desert photos suggest that Rajasthan will be a key location, fitting the road trip genre perfectly. If Farhan can capture even a fraction of the wanderlust that made ZNMD iconic, this time through a female lens, the film could become the defining Bollywood ensemble of the decade.

Shooting is expected to begin in the coming months, with a 2027 release likely.

*Sources: Sacnilk; Pinkvilla; Bollywood Hungama; Zoom TV Entertainment*"""

art3_sources = ["Sacnilk", "Pinkvilla", "Bollywood Hungama", "Zoom TV Entertainment"]

articles_to_write.append({
    "slug": art3_slug,
    "headline": art3_headline,
    "subheadline": art3_subheadline,
    "body": art3_body,
    "person_names": ["Farhan Akhtar", "Priyanka Chopra"],
    "topic_queries": ["Jee Le Zaraa Bollywood film", "Farhan Akhtar road trip film"],
    "pexels_query": "Rajasthan desert road trip India",
    "sources": art3_sources
})


# ── MAIN EXECUTION ──

def main():
    now = datetime.now(timezone.utc)
    published_at = now.strftime("%Y-%m-%dT%H:%M:%SZ")

    for i, art in enumerate(articles_to_write):
        print(f"\n{'='*60}")
        print(f"Article {i+1}: {art['headline'][:60]}...")
        print(f"{'='*60}")

        # Image sourcing
        print("\n📷 Sourcing image...")
        image_url, image_attr = source_image(
            art["person_names"],
            art["topic_queries"],
            art["pexels_query"],
            art["slug"]
        )

        # Build article payload
        payload = {
            "headline": art["headline"],
            "subheadline": art["subheadline"],
            "body": art["body"],
            "slug": art["slug"],
            "category": "entertainment",
            "vertical": "entertainment",
            "status": "published",
            "published_at": published_at,
            "is_editorial": False,
            "sources": art["sources"]
        }

        if image_url:
            payload["image_url"] = image_url
            payload["image_attribution"] = image_attr

        # Validate
        word_count = len(art["body"].split())
        if word_count < 400:
            print(f"  ✗ REJECTED: body too short ({word_count} words)")
            continue
        if len(art["headline"]) > 200:
            print(f"  ✗ REJECTED: headline too long ({len(art['headline'])} chars)")
            continue
        if len(art["subheadline"]) < 15:
            print(f"  ✗ REJECTED: subheadline too short")
            continue

        print(f"  Word count: {word_count}")
        print(f"  Headline: {len(art['headline'])} chars")
        print(f"  Image: {'✓' if image_url else '✗ none'}")

        # Insert
        print("\n📝 Publishing...")
        art_id = insert_article(payload)
        if art_id:
            print(f"  ✓ DONE: {art['slug']}")
        else:
            print(f"  ✗ FAILED: {art['slug']}")

        time.sleep(1)  # small delay between inserts

    print(f"\n{'='*60}")
    print("Entertainment writer run complete.")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()

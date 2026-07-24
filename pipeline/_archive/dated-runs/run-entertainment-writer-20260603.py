#!/usr/bin/env python3
"""Entertainment writer - June 3, 2026 run
Articles:
1. Salman Khan's legal battle with Kala Hiran makers — personality rights
2. Dhurandhar 2 arrives on JioHotstar — India's second-biggest grosser hits streaming
3. Karisma Kapoor's Brown on ZEE5 — neo-noir comeback
"""

import json, os, sys, uuid, datetime, time, re
import requests
from urllib.parse import quote

# === ENV ===
def load_env(path):
    if not os.path.exists(path):
        print(f"⚠ Env file not found: {path}")
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, val = line.split('=', 1)
                val = val.strip().strip('"').strip("'")
                os.environ[key] = val

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

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

# === IMAGE SOURCING ===
def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = quote(person_name.replace(' ', '_'))
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
        "iiprop": "url|size|mime|extmetadata",
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


def fetch_pexels_image(*search_terms):
    """Search Pexels for a relevant image. Returns URL or None."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    for term in search_terms:
        try:
            r = requests.get(
                "https://api.pexels.com/v1/search",
                params={"query": term, "per_page": 5, "orientation": "landscape"},
                headers={"Authorization": PEXELS_KEY},
                timeout=10
            )
            if r.status_code == 200:
                photos = r.json().get("photos", [])
                for p in photos:
                    url = p.get("src", {}).get("large2x") or p.get("src", {}).get("large")
                    if url:
                        print(f"  ✓ Pexels image found for '{term}': {url[:80]}...")
                        return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{term}': {e}")
    return None


def validate_image_url(url):
    """Validate that image URL returns HTTP 200 with image content > 5KB."""
    try:
        r = requests.head(url, headers={"User-Agent": UA}, timeout=10, allow_redirects=True)
        ct = r.headers.get('Content-Type', '')
        cl = int(r.headers.get('Content-Length', 0))
        if r.status_code == 200 and 'image' in ct and cl > 5000:
            return True
        # Sometimes HEAD doesn't give content-length, try GET with range
        if r.status_code == 200 and 'image' in ct:
            r2 = requests.get(url, headers={"User-Agent": UA, "Range": "bytes=0-10000"}, timeout=10, stream=True)
            chunk = r2.content
            if len(chunk) > 5000:
                return True
    except Exception as e:
        print(f"  ⚠ Image validation error: {e}")
    return False


def upload_to_supabase_storage(image_url, filename):
    """Download image and upload to Supabase storage bucket."""
    try:
        r = requests.get(image_url, headers={"User-Agent": UA}, timeout=30)
        if r.status_code != 200 or len(r.content) < 5000:
            print(f"  ⚠ Download failed or too small: {len(r.content)} bytes")
            return None

        ct = r.headers.get('Content-Type', 'image/jpeg')
        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
        resp = requests.post(
            upload_url,
            headers={
                'apikey': SUPABASE_KEY,
                'Authorization': f'Bearer {SUPABASE_KEY}',
                'Content-Type': ct,
                'x-upsert': 'true'
            },
            data=r.content,
            timeout=30
        )
        if resp.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase storage: {public_url[:80]}...")
            return public_url
        else:
            print(f"  ⚠ Upload failed: {resp.status_code} {resp.text[:200]}")
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
    return None


def source_image(person_names=None, topic_terms=None, pexels_terms=None, slug=""):
    """Multi-source image search with compare logic."""
    candidates = []

    # Source 1: Wikipedia person images
    if person_names:
        for name in person_names:
            wiki_img = fetch_wikipedia_person_image(name)
            if wiki_img:
                candidates.append({"url": wiki_img, "source": "wikipedia", "relevance": "high", "person": name})
                break

    # Source 2: Wikimedia Commons
    if topic_terms:
        for term in topic_terms:
            commons = fetch_wikimedia_commons_images(term, limit=3)
            for c in commons[:2]:
                candidates.append({"url": c["url"], "source": "wikimedia_commons", "relevance": "medium"})

    # Source 3: Pexels
    if pexels_terms:
        pexels_img = fetch_pexels_image(*pexels_terms)
        if pexels_img:
            candidates.append({"url": pexels_img, "source": "pexels", "relevance": "low"})

    # Pick best and upload to Supabase
    for cand in candidates:
        url = cand["url"]
        print(f"  Trying candidate from {cand['source']}: {url[:80]}...")
        if validate_image_url(url):
            ext = "jpg"
            if ".png" in url.lower():
                ext = "png"
            filename = f"{slug}.{ext}"
            final_url = upload_to_supabase_storage(url, filename)
            if final_url:
                attribution = "Wikimedia Commons" if cand["source"] in ("wikipedia", "wikimedia_commons") else "The Videshi"
                return final_url, attribution
        else:
            print(f"  ✗ Validation failed for {cand['source']} candidate")

    print("  ✗ No valid image found from any source")
    return None, None


def insert_article(article):
    """Insert article into Supabase."""
    resp = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS_SB,
        json=article,
        timeout=30
    )
    if resp.status_code in (200, 201):
        data = resp.json()
        art_id = data[0]['id'] if isinstance(data, list) and data else data.get('id', 'unknown')
        print(f"  ✓ Inserted article: {article['slug']} (id: {art_id})")
        return art_id
    else:
        print(f"  ✗ Insert failed: {resp.status_code} {resp.text[:300]}")
        return None


def update_article_image(article_id, image_url, attribution):
    """Patch article with image."""
    resp = requests.patch(
        f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article_id}",
        headers=HEADERS_SB,
        json={"image_url": image_url, "image_attribution": attribution},
        timeout=15
    )
    if resp.status_code in (200, 204):
        print(f"  ✓ Image updated for {article_id}")
    else:
        print(f"  ⚠ Image update failed: {resp.status_code}")


# ============================================================
# ARTICLE 1: Salman Khan Kala Hiran Legal Battle
# ============================================================
def write_article_1():
    print("\n=== ARTICLE 1: Salman Khan vs Kala Hiran ===")

    slug = "salman-khan-kala-hiran-legal-notice-personality-rights-blackbuck-nri-20260603"
    headline = "Salman Khan Wants a Film About the Blackbuck Case Killed Before It Starts. The Producer Says He Won't Blink."
    subheadline = "A legal notice, a personality rights claim, and a producer who calls it intimidation — the Kala Hiran standoff is testing where Bollywood's right to tell stories ends and a star's right to control his own narrative begins."

    body = """A poster dropped online last week for a film called *Kala Hiran: The Battle for Legacy*. It showed a man standing in forest terrain with a sniper rifle. He wore a turquoise bracelet. His build looked familiar. Within days, Salman Khan's legal team sent a notice demanding the project be shut down.

The notice, dated April 24, 2026, was served on casting director Akshay Pandey and demands an immediate halt to all production, promotion, and release activity related to the film. The legal arguments are sharp: the film is "defamatory in nature," constitutes a "gross violation of personality rights," and risks interfering with the ongoing judicial proceedings of the blackbuck poaching case, which remains pending before the Rajasthan High Court.

## The Legal Core

Salman Khan's legal team has framed this fight around two pillars. The first is personality rights — the legal doctrine that a public figure can control the commercial use of their name, image, and likeness. The second is sub judice interference — the argument that depicting events from a pending criminal case could prejudice the court of public opinion and compromise his right to a fair trial.

The notice explicitly states that Khan has "neither authorised nor consented to the use of his name, persona, or the alleged incident associated with him in the proposed film." It further demands an unconditional written apology from the filmmakers.

Indian courts have increasingly recognized personality rights in recent years, with the Delhi High Court issuing landmark orders protecting the likenesses of Amitabh Bachchan, Anil Kapoor, and others from unauthorized commercial exploitation. Khan's team appears to be building on this evolving precedent.

## The Producer's Defiance

Producer Amit Jani of Jani Firefox Media Private Limited is not backing down. In a public statement, he accused Khan of using star power to intimidate small filmmakers. "The intent of this legal notice is just intimidation so that people surrender to glamour," Jani said. "It is my nature to not be intimidated."

Jani insists the film is not a biopic and focuses instead on the Bishnoi community and wildlife conservation. The filmmakers have announced that the teaser will release on June 20 as planned, and the film is targeting an October 2 theatrical release.

## Why This Matters for the Diaspora

The standoff taps into a larger debate that has echoed across Bollywood for years: where does creative freedom end and an individual's right to control their narrative begin? For Indian audiences in the US, UK, and Canada — many of whom followed the original blackbuck trial through decades of courtroom updates — the case carries both legal and cultural weight.

Bollywood's legal landscape is shifting. The Don 3 dispute between Ranveer Singh and FWICE. The Pushpa trademark fight. Now Kala Hiran. Each case is drawing new boundaries around what filmmakers can and cannot do with real-life stories and living public figures.

## What Comes Next

If neither side backs down — and right now, neither is showing signs of it — this could head to court. Khan's team has warned of "stringent legal action and escalating litigation" if their demands are not met. The teaser date of June 20 will be the first real test of whether the producers can withstand the legal pressure.

For now, Kala Hiran exists in a strange limbo: a film that cannot yet be seen, built around a case that has not yet been resolved, about a man who insists it has nothing to do with him."""

    sources = json.dumps([
        "Mint - Salman Khan sends legal notice to Kala Hiran makers",
        "Bollywood Bubble - Salman Khan Sues Kala Hiran Makers Over Alleged Unauthorised Use Of His Persona",
        "Hollywood Reporter India - Salman Khan Sends Legal Notice to Kala Hiran Makers",
        "MensXP - Salman Khan Issues Legal Notice Against Kala Hiran Movie"
    ])

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "entertainment",
        "vertical": "entertainment",
        "status": "published",
        "published_at": datetime.datetime.utcnow().isoformat() + "Z",
        "sources": sources,
        "is_editorial": False,
        "image_url": None,
        "image_attribution": None
    }

    art_id = insert_article(article)
    if not art_id:
        return

    # Image sourcing
    img_url, attr = source_image(
        person_names=["Salman Khan"],
        topic_terms=["Salman Khan Bollywood", "Salman Khan actor"],
        pexels_terms=["Indian court legal gavel", "Bollywood star"],
        slug=slug
    )
    if img_url:
        update_article_image(art_id, img_url, attr)


# ============================================================
# ARTICLE 2: Dhurandhar 2 OTT on JioHotstar
# ============================================================
def write_article_2():
    print("\n=== ARTICLE 2: Dhurandhar 2 OTT Debut ===")

    slug = "dhurandhar-2-jiohotstar-ott-release-june-4-ranveer-singh-streaming-nri-20260603"
    headline = "Dhurandhar 2 Hits JioHotstar Tomorrow. India's Second-Biggest Film Ever Just Became a Living Room Event."
    subheadline = "After ₹1,800 crore at the box office and 11 weeks in theatres, Ranveer Singh's spy blockbuster arrives on streaming — with a staggered dual-platform strategy that puts JioHotstar first and Netflix India two weeks later."

    body = """For 77 days, the only way to watch *Dhurandhar 2: The Revenge* was in a theatre. Starting June 4, Ranveer Singh's all-time blockbuster lands on JioHotstar in India, and the streaming wars just got a new front.

The film arrives as a JioHotstar exclusive for its first two weeks. Netflix India gets it on June 19. Internationally, both platforms have already been carrying the film — Netflix picked it up for global territories while JioHotstar holds Indian digital rights. The staggered domestic rollout is a first for a film of this scale, designed to maximize subscriber acquisition across both platforms.

## The Numbers That Got It Here

*Dhurandhar 2* is not just another blockbuster. With approximately ₹1,800 crore in worldwide gross and ₹1,185 crore net in India alone, it is the second-highest-grossing Indian film in history. It entered the global top 10 for 2026, sitting alongside *Pegasus 3*, *Project Hail Mary*, and *The Super Mario Galaxy Movie*.

The film's overseas performance was equally historic. It crossed ₹400 crore gross in international markets — the highest ever for an Indian film outside India (excluding China). In North America, it became the first Indian title to surpass $25 million, and it was still earning over ₹30 lakh daily in its ninth week when the OTT window was finalized.

## What Makes It a Streaming Event

For the Indian diaspora in North America, the UK, and the Gulf, the Netflix window has already been open. But for viewers in India — particularly those in smaller towns and cities who may have missed the theatrical run — the JioHotstar premiere is effectively the film's second opening day.

Director Aditya Dhar's sequel picks up Ranveer Singh's character Jaskirat Singh Rangi, now operating under the alias Hamza Ali Mazari in Karachi's organized crime underworld, targeting terror cells linked to the 26/11 attacks. R. Madhavan, Sanjay Dutt, and Arjun Rampal round out the ensemble.

The film's nearly four-hour runtime — 3 hours and 55 minutes — was a talking point in theatres. On streaming, it may actually benefit: viewers can pause, split the watch, and return to the film's dense second half without the commitment of a single sitting.

## The Dual-Platform Playbook

The JioHotstar-first, Netflix-later model is worth watching for the industry. It signals a future where mega-grossers don't simply land on one platform after their theatrical window. Instead, studios can extract value twice — first from the platform that paid for domestic streaming rights, then from the global platform that wants the title for its own library.

For JioHotstar, the timing could not be better. The platform needs marquee content to compete with Netflix's aggressive Indian slate — which, this same week, includes *Maa Behen* starring Madhuri Dixit.

## The Week Ahead

*Dhurandhar 2* joins a stacked OTT week that also includes *Gullak Season 5* on SonyLIV, *Brown* starring Karisma Kapoor on ZEE5, *Patriot* with Mammootty and Mohanlal on ZEE5, and *Made in India: A Titan Story* on Amazon MX Player. It is, without exaggeration, one of the densest streaming weeks Indian OTT has ever seen.

But the headline act is clear. Tomorrow, India's second-biggest film walks into your living room."""

    sources = json.dumps([
        "Sacnilk - Dhurandhar 2 OTT Release Date: Ranveer Singh Starrer Gets Extended Theatrical Run As JioHotstar Confirms June 4 Release",
        "Sacnilk - Dhurandhar 2 OTT Release Date: To Stream Both On JioHotstar and Netflix In India",
        "ZoomTV - Recent OTT Launches June 1-7: From Dhurandhar 2 to Patriot",
        "MensXP - Dhurandhar 2, Gullak S5, HJTIHH: 16 OTT, Theatrical Releases To Watch This Week"
    ])

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "entertainment",
        "vertical": "entertainment",
        "status": "published",
        "published_at": datetime.datetime.utcnow().isoformat() + "Z",
        "sources": sources,
        "is_editorial": False,
        "image_url": None,
        "image_attribution": None
    }

    art_id = insert_article(article)
    if not art_id:
        return

    # Image sourcing - Ranveer Singh
    img_url, attr = source_image(
        person_names=["Ranveer Singh"],
        topic_terms=["Ranveer Singh actor Bollywood"],
        pexels_terms=["streaming television screen", "movie premiere"],
        slug=slug
    )
    if img_url:
        update_article_image(art_id, img_url, attr)


# ============================================================
# ARTICLE 3: Karisma Kapoor's Brown on ZEE5
# ============================================================
def write_article_3():
    print("\n=== ARTICLE 3: Karisma Kapoor Brown ZEE5 ===")

    slug = "karisma-kapoor-brown-zee5-neo-noir-kolkata-comeback-nri-20260603"
    headline = "Karisma Kapoor Plays a Washed-Up Alcoholic Cop in Kolkata. Her ZEE5 Debut Drops Thursday."
    subheadline = "The '90s queen trades chiffon for whiskey-stained grit in Brown, a neo-noir thriller adapted from a Kolkata murder mystery novel — and directed by the man who made Delhi Belly."

    body = """There is a particular kind of courage required when a star known for shimmer decides to show up haggard. Karisma Kapoor, whose name is practically synonymous with the high-energy Bollywood of the 1990s — *Dil To Pagal Hai*, *Raja Hindustani*, *Hum Saath Saath Hain* — has chosen the opposite of nostalgia for her streaming debut.

In *Brown*, which premieres on ZEE5 on June 5, she plays Rita Brown: a disgraced, alcoholic former cop in Kolkata who gets pulled back into the system when a series of brutal murders shakes the city. The first victim is the daughter of an influential businessman. Rita's investigation becomes her shot at redemption — and the audience's window into a city rotting from within.

## The Source Material

*Brown* is adapted from Abheek Barua's novel *City of Death*, a noir tale set against Kolkata's crumbling colonial architecture and moral decay. The adaptation is directed by Abhinay Deo, best known for the raucous irreverence of *Delhi Belly* in 2011 — a film that felt like it arrived from a parallel Bollywood universe. With *Brown*, Deo pivots from comedy to psychological dread, though the two share an appetite for subverting audience expectations.

The series has pedigree: it premiered at the Berlin International Film Festival as part of the Berlinale Series Market, where its raw tone and Kapoor's de-glamourised performance attracted attention from international programmers.

## The Cast

Joining Kapoor is Surya Sharma as Inspector Arjun, a grieving junior officer who becomes Rita's reluctant partner. Jisshu Sengupta — a mainstay of Bengali cinema and a face familiar to diaspora audiences from *Mardaani* and *Barfi!* — brings Kolkata authenticity to the ensemble. Soni Razdan, Helen, and Shaan round out a cast that mixes industry veterans with actors rooted in the Bengali film tradition.

## Why It Matters

For the diaspora audience, *Brown* represents something that Indian streaming has been slow to deliver: genuine noir. Not a thriller dressed up in noir's visual language, but a story where the detective is as broken as the crime she investigates. Where Kolkata is not a backdrop but a character — humid, corrupt, beautiful, suffocating.

Karisma Kapoor's casting is the hook, but the substance is in the writing. Deo has spoken about wanting the series to feel like "the officer is the drama" — the investigation matters, but Rita Brown's psychological descent and fight to pull herself back from the brink matters more.

## The Streaming Context

*Brown* arrives in a week that is almost absurdly competitive for Indian OTT. *Dhurandhar 2* dominates JioHotstar. *Maa Behen* gives Netflix its latest Hindi-language play. *Gullak Season 5* brings SonyLIV's most loyal fanbase back for another round. *Patriot* unites Mammootty and Mohanlal on ZEE5 the same day.

Within ZEE5's own slate, *Brown* has to share oxygen with a spy thriller featuring three of Malayalam cinema's biggest stars. That is a difficult double bill. But the two shows serve entirely different audiences: *Patriot* is a mass entertainer, while *Brown* is built for viewers who want their crime fiction slow, atmospheric, and psychologically uncomfortable.

## The Bigger Picture

The broader trend is unmistakable. Indian OTT platforms are no longer just parking lots for theatrical leftovers. They are commissioning original content that would have been unthinkable for Indian television a decade ago. A Karisma Kapoor show where she clutches a cigarette and pours whiskey at noon is not fan service — it is a bet that audiences are ready for something harder.

Whether that bet pays off will depend on how many people press play on Thursday. But the fact that the bet is being made at all says something about where Indian streaming is headed."""

    sources = json.dumps([
        "ZEE5 Global - Karisma Kapoor Headlines ZEE5's Noir Thriller Brown",
        "The Marquee - Karisma Kapoor Brown Trailer: Gritty Neo-Noir Transformation",
        "Filmfare - Exclusive: Karisma Kapoor was like a kid in a candy store says Brown director Abhinay Deo",
        "Bharat Affairs - OTT Releases June 1-5 2026: Maa Behen Gullak 5 Brown and More",
        "Pinkvilla - 6 Hindi Films and OTT Releases This Week"
    ])

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "entertainment",
        "vertical": "entertainment",
        "status": "published",
        "published_at": datetime.datetime.utcnow().isoformat() + "Z",
        "sources": sources,
        "is_editorial": False,
        "image_url": None,
        "image_attribution": None
    }

    art_id = insert_article(article)
    if not art_id:
        return

    # Image sourcing - Karisma Kapoor
    img_url, attr = source_image(
        person_names=["Karisma Kapoor"],
        topic_terms=["Karisma Kapoor actress", "Kolkata noir"],
        pexels_terms=["Kolkata streets atmospheric", "noir detective"],
        slug=slug
    )
    if img_url:
        update_article_image(art_id, img_url, attr)


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    print(f"Entertainment writer starting at {datetime.datetime.utcnow().isoformat()}Z")
    print(f"Supabase URL: {SUPABASE_URL[:30]}...")

    write_article_1()
    time.sleep(1)
    write_article_2()
    time.sleep(1)
    write_article_3()

    print(f"\n✓ Entertainment writer complete at {datetime.datetime.utcnow().isoformat()}Z")

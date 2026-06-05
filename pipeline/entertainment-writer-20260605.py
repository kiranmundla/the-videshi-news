#!/usr/bin/env python3
"""Entertainment writer for The Videshi — 2026-06-05 batch"""

import json, os, sys, time, uuid, re
from datetime import datetime, timezone
import requests
from urllib.parse import quote

# Load env
def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, _, val = line.partition('=')
                val = val.strip().strip('"').strip("'")
                os.environ.setdefault(key.strip(), val)

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.supabase'))
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

# ── Image helpers ───────────────────────────────────────────────

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


def fetch_pexels_image(query):
    """Search Pexels for a relevant image. Returns URL or None."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    try:
        r = requests.get(
            "https://api.pexels.com/v1/search",
            params={"query": query, "per_page": 5, "orientation": "landscape"},
            headers={"Authorization": PEXELS_KEY},
            timeout=10
        )
        if r.status_code == 200:
            photos = r.json().get("photos", [])
            for p in photos:
                url = p.get("src", {}).get("large2x") or p.get("src", {}).get("large")
                if url:
                    print(f"  ✓ Pexels image found for '{query}': {url[:80]}...")
                    return url
    except Exception as e:
        print(f"  ⚠ Pexels error for '{query}': {e}")
    return None


def validate_image(url):
    """Validate an image URL returns HTTP 200 with image content > 5KB."""
    try:
        r = requests.head(url, headers={"User-Agent": UA}, timeout=10, allow_redirects=True)
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            return True
        # Try GET if HEAD doesn't have Content-Length
        if r.status_code == 200 and "image" in ct and cl == 0:
            r2 = requests.get(url, headers={"User-Agent": UA}, timeout=10, stream=True)
            chunk = r2.raw.read(6000)
            r2.close()
            if len(chunk) > 5000:
                return True
    except Exception as e:
        print(f"  ⚠ Image validation error: {e}")
    return False


def get_best_image(person_name=None, search_terms=None):
    """Multi-source image search. Returns (url, attribution) or (None, None)."""
    candidates = []
    
    # Wikipedia person image
    if person_name:
        wiki_url = fetch_wikipedia_person_image(person_name)
        if wiki_url and validate_image(wiki_url):
            candidates.append((wiki_url, "Wikimedia Commons", "wikipedia"))
    
    # Wikimedia Commons
    if search_terms:
        for term in (search_terms if isinstance(search_terms, list) else [search_terms]):
            commons = fetch_wikimedia_commons_images(term, limit=3)
            for c in commons:
                url = c.get("url") or c.get("original_url")
                if url and validate_image(url):
                    candidates.append((url, "Wikimedia Commons", "commons"))
                    break
            if any(c[2] == "commons" for c in candidates):
                break
    
    # Pexels fallback
    if search_terms:
        pexels_query = search_terms[0] if isinstance(search_terms, list) else search_terms
        pex_url = fetch_pexels_image(pexels_query)
        if pex_url and validate_image(pex_url):
            candidates.append((pex_url, "Pexels", "pexels"))
    
    # Pick best: Wikipedia > Commons > Pexels
    priority = {"wikipedia": 0, "commons": 1, "pexels": 2}
    candidates.sort(key=lambda x: priority.get(x[2], 99))
    
    if candidates:
        print(f"  ★ Selected image from {candidates[0][2]}: {candidates[0][0][:80]}...")
        return candidates[0][0], candidates[0][1]
    
    return None, None


# ── Article insertion ───────────────────────────────────────────

def insert_article(article):
    """Insert an article into Supabase."""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS_SB,
        json=article,
        timeout=30
    )
    if r.status_code in (200, 201):
        result = r.json()
        if isinstance(result, list) and result:
            print(f"  ✓ Inserted: {result[0].get('slug', 'unknown')}")
            return True
        print(f"  ✓ Inserted (no body returned)")
        return True
    else:
        print(f"  ✗ Insert failed ({r.status_code}): {r.text[:300]}")
        return False


# ── Articles ────────────────────────────────────────────────────

def write_articles():
    now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S+00:00')
    articles = []

    # ─── Article 1: Aishwarya Rai Bachchan JW Marriott ───
    print("\n=== Article 1: Aishwarya Rai Bachchan JW Marriott ===")
    img1_url, img1_attr = get_best_image(
        person_name="Aishwarya Rai",
        search_terms=["Aishwarya Rai Bachchan", "Aishwarya Rai Cannes"]
    )
    
    article1_body = """JW Marriott has named Aishwarya Rai Bachchan as its Global Brand Ambassador. The announcement, made on June 3, positions the internationally acclaimed actor at the center of the luxury hotel brand's worldwide "Stay in the Moment" campaign — a platform built around mindful travel, well-being, and presence.

This is not a regional endorsement or a limited-run campaign. Aishwarya will front international brand campaigns spanning film, print, and digital platforms, and will participate in curated brand experiences across India and select global markets. The creative direction centers on moments of reflection and quiet sophistication within JW Marriott spaces, designed to foster clarity and calm.

## Why This Partnership Matters for Indian Travelers

The timing is deliberate. Indian travelers are now the fastest-growing outbound luxury segment globally, and domestic demand for premium travel continues to accelerate. JW Marriott currently operates more than 130 properties worldwide, with India representing one of its most dynamic portfolios and development pipelines. The brand is betting that as India's influence on global hospitality deepens, having Aishwarya as its face makes strategic sense beyond mere celebrity association.

"Travel has always been an important part of my life, both personally and professionally," Aishwarya said in the official statement. "The most meaningful experiences are often the quietest ones, when you are fully aware of where you are and who you are with. JW Marriott's philosophy of being present and in the moment speaks to that awareness."

Bruce Rohr, Vice President and Global Brand Leader at JW Marriott, framed the choice as intentional: "Aishwarya's global stature, warmth, and authenticity make her a natural embodiment of JW Marriott. She brings a thoughtful, grounded presence that reflects the way our guests seek to travel — with intention and a sense of connection."

## The Diaspora Angle

For NRI travelers — many of whom already frequent JW Marriott properties from New York to Mumbai to Dubai — the appointment carries cultural weight. Aishwarya has spent over two decades representing India on the global stage, from Cannes to international fashion weeks, and her public image has consistently carried a sense of composure rather than spectacle. That alignment with "intentional luxury" is what separates this from a typical celebrity deal.

The partnership also reflects a broader industry shift. Indian luxury consumers no longer simply want five-star amenities. They want experiences that feel personal and culturally grounded. JW Marriott is signaling that it understands this evolution, and it is using India's most globally recognized female face to say so.

## What This Means Going Forward

As Marriott International strengthens its presence across India's key cities and resort destinations, this appointment is part of a longer play. The brand is expanding rapidly in markets shaped by Indian travelers — the Middle East, Southeast Asia, Europe — and Aishwarya's name opens doors across all of them. The collaboration is expected to unfold over a sustained period, with new campaign content rolling out across platforms through 2026 and beyond.

For a brand built on the legacy of J. Willard Marriott and a philosophy of holistic well-being, the choice of Aishwarya Rai Bachchan is less about star power and more about what she represents: presence, balance, and a life that has stayed grounded despite the spotlight. In the crowded landscape of celebrity endorsements, that distinction matters."""

    articles.append({
        "headline": "Aishwarya Rai Bachchan Is Now the Global Face of JW Marriott. The Deal Says More About India's Luxury Travelers Than About the Star.",
        "subheadline": "The hotel chain's 'Stay in the Moment' campaign targets India's fastest-growing luxury travel segment — and Aishwarya embodies the pitch.",
        "body": article1_body,
        "slug": "aishwarya-rai-bachchan-jw-marriott-global-brand-ambassador-luxury-travel-nri-20260605",
        "category": "entertainment",
        "vertical": "entertainment",
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": img1_url,
        "image_caption": "Aishwarya Rai Bachchan at a public appearance",
        "image_attribution": img1_attr,
        "sources": json.dumps([
            {"name": "Hollywood Reporter India", "url": "https://hollywoodreporterindia.com"},
            {"name": "Bollywood Hungama", "url": "https://bollywoodhungama.com"},
            {"name": "Femina", "url": "https://femina.in"}
        ])
    })

    # ─── Article 2: Ranveer Singh Don 3 FWICE ───
    print("\n=== Article 2: Ranveer Singh Don 3 FWICE ===")
    img2_url, img2_attr = get_best_image(
        person_name="Ranveer Singh",
        search_terms=["Ranveer Singh actor Bollywood", "Ranveer Singh film"]
    )

    article2_body = """The Federation of Western India Cine Employees has withdrawn its non-cooperation directive against Ranveer Singh. The reversal, announced on June 3, came after the actor sent a formal legal notice to FWICE and multiple industry bodies — including the Indian Motion Picture Producers' Association, the Producers Guild of India, and the Cine & TV Artistes' Association — intervened to broker a resolution.

The directive had been issued on May 25 after Farhan Akhtar and producer Ritesh Sidhwani filed a complaint with the Indian Film and Television Directors' Association, which then referred the matter to FWICE. The complaint alleged that Ranveer's abrupt exit from Don 3, which had been in development for three years, had caused financial losses estimated at ₹45 crore in pre-production costs. FWICE had instructed all its members across every craft and department not to work on any project involving Ranveer Singh.

## What Happened Behind the Scenes

The public back-and-forth between FWICE and Ranveer's team lasted roughly ten days. FWICE advisor Ashoke Pandit had initially struck a hard line: "None of our workers or members, across all crafts, will work on any of his projects. We have requested that all producers take a stand, join us in solidarity." The language was aggressive, even if FWICE later clarified it should not be called a "ban."

Ranveer's team responded with a measured official statement: "Ranveer Singh holds the highest regard for the film fraternity and for everyone associated with the Don franchise. He has consciously chosen to maintain silence, believing that professional discussions and personal equations are best handled with dignity, maturity and mutual respect."

Behind that public restraint, however, came a formal legal notice. The details of the notice have not been made public, but it was effective. FWICE president BN Tiwari announced the withdrawal shortly after: "We are taking back our non-cooperative directive from immediate effect. No one has won or lost in this matter."

## The Kangana Ranaut Subplot

The controversy also drew Kangana Ranaut into the conversation. At the trailer launch of her upcoming film Bharat Bhhagya Viddhaata, Kangana offered an unexpected defense of Ranveer: "It's impossible not to make enemies when you are successful. Today, Ranveer Singh should think about what he has achieved in his career. When a person moves forward, they will face numerous obstacles."

Ashoke Pandit was unimpressed. Speaking at a FWICE press conference, he fired back directly: "Kangana also said something. I said, 'You talk nonsense, that's why I banned you.' There is a big issue of the industry here. You don't even know the issue."

Ram Gopal Varma and Sanjay Gupta also voiced support for Ranveer during the standoff, adding to the sense that FWICE's directive was creating fault lines across the industry rather than building consensus.

## Why the Timing Mattered

The withdrawal came just one day before Dhurandhar 2 — Ranveer's massive blockbuster sequel — began streaming on JioHotstar. With the film having earned ₹1,850 crore at the worldwide box office, Ranveer's commercial position made the non-cooperation directive difficult to sustain. No producer in the industry would voluntarily walk away from the biggest male star at the box office over a dispute that had not gone through formal arbitration.

## What It Means for the Industry

The Don 3 saga is far from over. Farhan Akhtar's ₹45 crore claim remains unresolved, and the project's future is uncertain. But FWICE's rapid retreat — from aggressive directive to quiet withdrawal in under two weeks — exposes a structural weakness in how the Indian film industry handles contractual disputes. The federation's tools are blunt instruments: public shaming and work stoppages that collapse the moment a star's legal team pushes back.

For NRI audiences watching from abroad, the episode is a reminder of how much Bollywood still runs on relationships and informal agreements rather than the contractual frameworks that govern Hollywood productions. The industry is getting bigger — Dhurandhar 2 just proved that — but its dispute resolution mechanisms have not kept pace.

The legal notice from Ranveer's camp will still need a formal response from FWICE. But for now, the directive is gone, the star is back in business, and Don 3 remains a franchise looking for its next chapter."""

    articles.append({
        "headline": "FWICE Just Backed Down on Ranveer Singh. The Don 3 Dispute Is Not Over, but the Non-Cooperation Directive Is.",
        "subheadline": "A legal notice, four industry bodies, and Kangana Ranaut's unsolicited opinion later, the ten-day standoff has ended — with no resolution on the ₹45-crore claim.",
        "body": article2_body,
        "slug": "ranveer-singh-fwice-non-cooperation-withdrawn-don-3-legal-notice-kangana-nri-20260605",
        "category": "entertainment",
        "vertical": "entertainment",
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": img2_url,
        "image_caption": "Ranveer Singh at a film event",
        "image_attribution": img2_attr,
        "sources": json.dumps([
            {"name": "Filmfare", "url": "https://filmfare.com"},
            {"name": "Livemint", "url": "https://livemint.com"},
            {"name": "Bollywood Hungama", "url": "https://bollywoodhungama.com"},
            {"name": "LatestLY / ANI", "url": "https://latestly.com"}
        ])
    })

    # ─── Article 3: Netflix South Indian Mega Slate 2026 ───
    print("\n=== Article 3: Netflix South Indian Slate 2026 ===")
    img3_url, img3_attr = get_best_image(
        person_name=None,
        search_terms=["Netflix India streaming", "Indian cinema theater", "South Indian film industry"]
    )
    
    article3_body = """Netflix has unveiled its Telugu and Tamil slates for 2026, and the lineup reads like a who's who of South Indian cinema. Across the two announcements, the platform confirmed post-theatrical streaming deals with nearly every major star in the South — Nani, Pawan Kalyan, Venkatesh, Vijay Deverakonda, Suriya, Dhanush, and Karthi among them. For NRI audiences who have historically relied on delayed digital premieres and region-locked platforms, this is the clearest signal yet that Netflix is treating South Indian cinema as a primary content vertical, not a secondary acquisition.

## The Telugu Slate

The Telugu lineup anchors around four marquee projects. First is Nani's Paradise, a collaboration that signals Netflix's confidence in the actor's crossover appeal. Then there is Adarsha Kutumbam (commonly called AK47), pairing Venkatesh Daggubati with director Trivikram Srinivas for a family entertainer backed by Haarika & Hassine Creations, with Srinidhi Shetty as the female lead and music by Harshavardhan Rameshwar.

The most ambitious project on the Telugu list may be VD14, Vijay Deverakonda's reunion with Taxiwala director Rahul Sankrityan. The film is a period epic set between 1854 and 1878 during British colonial rule in the Rayalaseema region, produced by Mythri Movie Makers on a budget exceeding ₹100 crore. South African actor Arnold Vosloo — best known for The Mummy franchise — is reported to play a British officer, while Rashmika Mandanna and Amitabh Bachchan are linked to pivotal roles. Ajay-Atul are composing the score. This is Pan-India scale, and Netflix has already locked the post-theatrical rights.

Rounding out the slate is 418 from director Charan Lakkaraju, and Pawan Kalyan's Ustaad, adding political star power to the lineup.

## The Tamil Slate

Netflix's Tamil announcements are equally stacked. Suriya dominates with two projects: Suriya 46 (the previously rumored KGF-producer collaboration) and S47, a quirky action-comedy thriller directed by Aavesham fame Jithu Madhavan, where Suriya plays a suspended police officer who relocates to Kerala with an incompetent team. Nazriya Nazim and Naslen round out the cast.

Karthi brings Marshal, a pirate-themed period action-adventure set in 1960s-70s Rameswaram, directed by Tamizh of Taanakkaran fame. The ensemble includes Kalyani Priyadarshan, Sathyaraj, and Prabhu, with production by Dream Warrior Pictures. And Dhanush's Kara completes the high-profile Tamil slate.

## What This Means for the Diaspora

For NRI viewers, the implications are practical. These streaming deals mean guaranteed digital access to the biggest South Indian films within weeks of their theatrical runs. The days of waiting months for an OTT release, or worse, relying on pirated prints, are effectively ending for top-tier content. Netflix is positioning itself as the definitive post-theatrical home for both Telugu and Tamil cinema's biggest productions.

The financial scale is notable too. When Netflix locks streaming rights for a film like VD14 — budgeted at ₹100 crore with international cast members — the deal sizes are approaching Hollywood territory. These are not bargain acquisitions. Netflix is paying premium prices because the South Indian diaspora is one of its fastest-growing subscriber bases, and theatrical windows for these films generate genuine excitement that drives streaming subscriptions.

## The Platform Wars Context

Netflix's aggressive South Indian push comes as JioHotstar continues to hold the Dhurandhar franchise and other major Hindi-language titles, while Amazon Prime Video has its own Tamil and Telugu pipeline. The platform fragmentation means NRI audiences may need multiple subscriptions to cover the full spectrum — but it also means more content is getting premium treatment.

The 2026 slates also reflect a structural shift in how South Indian films are financed. OTT deals are now factored into production budgets from day one, allowing filmmakers to greenlight more ambitious projects. A film like Marshal — a pirate period drama that would have been considered too risky a decade ago — gets made because Netflix's streaming floor reduces the downside risk.

For South Indian cinema, the Netflix slates represent legitimacy on a global platform. For Netflix, they represent a bet on the audience that has been the most consistent theatrical force in Indian cinema for the past five years. For the diaspora, they represent something simpler: the best South Indian films of the year, available everywhere, on time."""

    articles.append({
        "headline": "Netflix Just Announced Its Telugu and Tamil Slates for 2026. Every Major South Indian Star Is on the List.",
        "subheadline": "Nani, Pawan Kalyan, Vijay Deverakonda, Suriya, Dhanush, Karthi, and Venkatesh — the streaming giant is treating South Indian cinema as a primary content vertical.",
        "body": article3_body,
        "slug": "netflix-telugu-tamil-2026-slate-nani-suriya-dhanush-vijay-deverakonda-nri-20260605",
        "category": "entertainment",
        "vertical": "entertainment",
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": img3_url,
        "image_caption": "A cinema screen representing the new wave of South Indian streaming content",
        "image_attribution": img3_attr,
        "sources": json.dumps([
            {"name": "Sacnilk", "url": "https://sacnilk.com"},
            {"name": "Sacnilk - Tamil Slate", "url": "https://sacnilk.com"},
            {"name": "Bollywood Hungama", "url": "https://bollywoodhungama.com"}
        ])
    })

    # ── Insert all articles ──
    print("\n=== Inserting articles ===")
    success_count = 0
    for i, a in enumerate(articles):
        print(f"\nArticle {i+1}: {a['headline'][:60]}...")
        if not a.get('image_url'):
            print(f"  ⚠ No image found, skipping article")
            continue
        ok = insert_article(a)
        if ok:
            success_count += 1
        time.sleep(1)
    
    print(f"\n=== Done: {success_count}/{len(articles)} articles published ===")
    return success_count


if __name__ == '__main__':
    write_articles()

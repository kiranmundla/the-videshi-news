#!/usr/bin/env python3
"""Entertainment writer for The Videshi — 2026-05-31 run.

Three articles:
1. A.R. Rahman & Shekhar Kapur reunite for Masoom: The New Generation
2. Cocktail 2 trailer delayed to June 2 — Shahid, Kriti, Rashmika starrer releasing June 19
3. The Royals Season 2 gets creative overhaul — Darlings director Jasmeet K. Reen replaces original director
"""

import json, os, requests, urllib.parse, uuid, sys
from datetime import datetime, timezone

# --- Supabase env ---
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS_KEY = os.environ.get("PEXELS_API_KEY", "")
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

def sb_insert(table, payload):
    r = requests.post(f"{SUPABASE_URL}/rest/v1/{table}", headers=HEADERS, json=payload, timeout=30)
    if r.status_code not in (200, 201):
        print(f"  ✗ INSERT {table} failed ({r.status_code}): {r.text[:600]}")
        return None
    data = r.json()
    return data[0] if isinstance(data, list) and data else data

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=10,
        )
        if r.status_code == 200:
            data = r.json()
            # Use thumbnail AS-IS (330px) to avoid 429 rate limits on original images
            img = data.get("thumbnail", {}).get("source") or data.get("originalimage", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image found for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None

def fetch_pexels_image(query, fallback_query=None):
    """Fetch image from Pexels as fallback."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key available")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            r = requests.get(
                "https://api.pexels.com/v1/search",
                headers={"Authorization": PEXELS_KEY},
                params={"query": q, "per_page": 5, "orientation": "landscape"},
                timeout=10,
            )
            if r.status_code == 200:
                photos = r.json().get("photos", [])
                for p in photos:
                    url = p.get("src", {}).get("large2x") or p.get("src", {}).get("large")
                    if url:
                        print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                        return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

def validate_image(url):
    """Check that image URL returns HTTP 200 with image content-type and > 5KB."""
    if not url:
        return False
    try:
        r = requests.head(url, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, timeout=10, allow_redirects=True)
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            print(f"  ✓ Image validated: {ct}, {cl} bytes")
            return True
        else:
            print(f"  ✗ Image validation failed: status={r.status_code}, type={ct}, size={cl}")
            return False
    except Exception as e:
        print(f"  ⚠ Image validation error: {e}")
        return False

def now_iso():
    return datetime.now(timezone.utc).isoformat()

# ─── ARTICLES ─────────────────────────────────────────────────

articles = []

# ── Article 1: AR Rahman + Shekhar Kapur → Masoom: The New Generation ──

articles.append({
    "headline": "A.R. Rahman and Shekhar Kapur Are Reuniting for Masoom: The New Generation. It's About Migration, Identity, and Coming Home.",
    "subheadline": "The Oscar-winning composer joins as co-producer alongside Naseeruddin Shah, Shabana Azmi, Manoj Bajpayee, and Nithya Menen in a modern reimagining of the 1983 classic.",
    "slug": "ar-rahman-shekhar-kapur-masoom-new-generation-migration-identity-nri-20260531",
    "category": "entertainment",
    "vertical": "entertainment",
    "status": "published",
    "is_editorial": False,
    "published_at": now_iso(),
    "sources": json.dumps(["Bollywood Hungama", "Cinema Express", "Variety India"]),
    "body": """The announcement that A.R. Rahman and Shekhar Kapur are working together again would be significant under any circumstances. That they're doing it on a film explicitly about migration and identity makes it essential viewing for the Indian diaspora.

**Masoom: The New Generation** is a contemporary reimagining of Kapur's 1983 classic — the film that introduced a generation to the quiet devastation of family secrets. The original, adapted from Erich Segal's *Man, Woman and Child*, starred Naseeruddin Shah and Shabana Azmi as a couple whose marriage fractures when a child from the husband's past affair arrives at their doorstep. It remains one of Hindi cinema's most emotionally precise films.

Both Shah and Azmi are returning for the new version. They'll be joined by Manoj Bajpayee, Nithya Menen, and Kaveri Kapur — Shekhar Kapur's daughter, making this a genuinely multi-generational project in front of and behind the camera.

## What's Different This Time

The original *Masoom* was about guilt and innocence within a single household. The new film expands those themes outward — into questions of migration, displacement, and what happens to family bonds when people scatter across countries and cultures. For anyone who has navigated the distance between where they were born and where they live, those themes need no explanation.

"Families, relationships, identity — these ideas have evolved so much, and cinema must evolve with them," Kapur said in a statement. It's the kind of quote that could feel hollow from most filmmakers. From the man who made *Bandit Queen* and *Elizabeth*, it carries weight.

## Rahman as Co-Producer, Not Just Composer

The bigger structural news is Rahman's role. He's not just scoring the film — he's co-producing it. Their collaboration stretches back to *Elizabeth: The Golden Age* (2007) and includes the stage productions *Bombay Dreams* and *Why? The Musical*. But those were projects where Rahman provided the music and moved on. Here, he's embedded in the creative architecture from the start.

"Working with Shekhar has always been a deeply enriching experience — he has been a mentor and a creative force in many ways," Rahman said. "When he shared the vision for this film, I felt compelled to be involved beyond the music. There's something timeless about *Masoom*, and reinterpreting that emotional world for a new generation feels both exciting and necessary."

## Why NRIs Should Pay Attention

The original *Masoom* resonated because it told a universal story through a specifically Indian lens — joint family pressures, the weight of respectability, the impossibility of honest conversation in cultures built on silence. The new film promises to layer diaspora reality on top of that foundation. Migration as an emotional event, not just a logistical one. Identity as something that shifts depending on which country you woke up in.

Pre-production is underway, with filming expected to begin later this year and a worldwide theatrical release anticipated in 2026. For a generation of NRIs who grew up watching the original on VHS tapes passed between relatives, this one is personal.

*Sources: Bollywood Hungama, Cinema Express, Zoom TV Entertainment, Devdiscourse*""",
    "image_person": "A. R. Rahman",
    "image_fallback_query": "Indian film music composer recording studio",
})

# ── Article 2: Cocktail 2 trailer delayed to June 2 ──

articles.append({
    "headline": "Cocktail 2 Drops Its Trailer June 2. Shahid Kapoor, Kriti Sanon, and Rashmika Mandanna's Summer Romance Hits Theatres June 19.",
    "subheadline": "Maddock Films' spiritual successor to the 2012 hit delayed its trailer from May 29 to June 2 in what appears to be a tighter marketing strategy. Three songs are already out.",
    "slug": "cocktail-2-trailer-june-2-shahid-kriti-rashmika-release-date-nri-20260531",
    "category": "entertainment",
    "vertical": "entertainment",
    "status": "published",
    "is_editorial": False,
    "published_at": now_iso(),
    "sources": json.dumps(["Sacnilk", "Filmibeat", "Zoom TV Entertainment"]),
    "body": """If you've been anywhere near Indian social media this past week, you've already seen the clip. Shahid Kapoor playfully refusing to let Rashmika Mandanna rest her hand on his shoulder during a promotional event — a callback to her doing the same thing to him at the Cocktail 2 trailer launch event days earlier. The teasing went viral, and the film isn't even out yet.

**Cocktail 2** releases in theatres on June 19, and its trailer — originally scheduled for May 29 — has been pushed to June 2. The delay, according to Maddock Films, is strategic rather than problematic. They want a compact promotional window leading directly into the theatrical debut.

## Not a Direct Sequel

This is important to understand upfront: Cocktail 2 is a spiritual successor, not a continuation. The original 2012 film starred Saif Ali Khan, Deepika Padukone, and Diana Penty in a love triangle set in London that became a sleeper hit largely on the strength of its music and Deepika's breakout performance as the free-spirited Veronica. Director Homi Adajania returns, but the cast, characters, and setting are entirely new.

Shahid Kapoor, Kriti Sanon, and Rashmika Mandanna headline the new film, which Maddock describes as "a contemporary perspective on love, friendship, and emotional complexities." Rashmika plays a Hyderabadi character, while the production shot across locations in Sicily, Italy.

## Three Songs Already Creating Buzz

The marketing strategy has been music-first — a smart play given how central the soundtrack was to the original Cocktail's success. Three tracks are already out:

- **Jab Talak** — the character-introduction track
- **Mashooqa** — a high-energy romantic number featuring Shahid and Kriti, shot in Sicily
- **Tujhko** — a soulful Arijit Singh ballad centered on Shahid and Rashmika's characters

At a media preview event, *Tujhko* reportedly left journalists visibly moved. Pritam Chakraborty composed the album, reuniting with Adajania after their work on the original.

## The Promotional Buzz

The real genius of Cocktail 2's marketing has been letting the cast chemistry do the heavy lifting. Shahid, Kriti, and Rashmika have been doing joint promotional appearances where their off-screen banter generates clips that rack up millions of views before anyone even asks about the plot.

The shoulder-touch incident — where Rashmika wouldn't let Shahid put his arm around her at the trailer launch, and he returned the favor at a later event — has become a running gag that feels genuinely unscripted. Whether it is or isn't barely matters; it's given the film a social media presence that most campaigns spend crores trying to manufacture.

## What Diaspora Audiences Should Know

Cocktail 2 enters a June calendar that's already stacked. Bobby Deol's *Bandar* and Varun Dhawan's *Hai Jawani Toh Ishq Hona Hai* arrive June 5. Imtiaz Ali's *Main Vaapas Aaunga*, Manoj Bajpayee's *Governor*, and Kangana Ranaut's *Bharat Bhhagya Viddhaata* all land June 12. *Welcome to the Jungle* closes the month on June 26.

But Cocktail 2 has the advantage of being the month's most mainstream romantic entertainer — the kind of film that NRI families can watch together on a weekend outing without anyone needing to Google the plot. The trailer drops June 2. The film follows 17 days later.

*Sources: Sacnilk, Filmibeat, Zoom TV Entertainment, Tupaki English*""",
    "image_person": "Shahid Kapoor",
    "image_fallback_query": "Bollywood romantic film poster couple",
})

# ── Article 3: The Royals Season 2 creative overhaul ──

articles.append({
    "headline": "Netflix Just Gutted The Royals. New Director, No Bhumi Pednekar, and a Complete Genre Pivot for Season 2.",
    "subheadline": "Darlings director Jasmeet K. Reen replaces the original director. Bhumi Pednekar has exited. The rom-com is now a family power drama starring Ishaan Khatter, Sakshi Tanwar, and Zeenat Aman.",
    "slug": "the-royals-season-2-netflix-jasmeet-reen-bhumi-pednekar-exit-overhaul-nri-20260531",
    "category": "entertainment",
    "vertical": "entertainment",
    "status": "published",
    "is_editorial": False,
    "published_at": now_iso(),
    "sources": json.dumps(["Bollywood Hungama", "Variety India", "Blaze Trends"]),
    "body": """Netflix India has done something rare: it's keeping a show's brand while throwing out almost everything that defined it. The Royals Season 2 is happening, but it will look nothing like Season 1.

Here's what's changed, and why it matters.

## The Director Swap

Filmmaker Jasmeet K. Reen — who directed the acclaimed Alia Bhatt–starrer *Darlings* in 2022 — has been brought on to direct Season 2. She replaces Nupur Asthana, who co-directed Season 1 alongside Priyanka Ghose. Asthana has stepped away due to prior commitments; she's currently working on another Netflix series produced under Ekta Kapoor's banner. Priyanka Ghose is expected to continue her involvement.

The choice of Reen signals intent. *Darlings* was a dark domestic drama that balanced tension with dark humor — tonally the opposite of The Royals Season 1's breezy romantic comedy. You don't hire the *Darlings* director to make another rom-com.

## Bhumi Pednekar's Exit

The bigger headline is who's leaving. Bhumi Pednekar, who played the female lead opposite Ishaan Khatter in Season 1, will not return for Season 2. In a recent interview, she revealed that the trolling she received for The Royals left her "emotionally depleted" and led to a nine-month break from acting. "I had lost perspective of who I am," she said.

Her departure isn't just a casting change — it's the reason Netflix could justify scrapping the original storyline entirely. With the central romance gone, the writers had a clean runway to reimagine the show from the ground up.

## From Rom-Com to Power Drama

When The Royals premiered in May 2025, it was built as a glossy romantic comedy centered on the chemistry between Khatter and Pednekar. The show pulled strong viewership numbers and dominated regional charts, but critics and audiences were brutal about the writing and performances. The gap between its commercial performance and its critical reception created an unusual problem: the show was too popular to cancel but too flawed to continue unchanged.

The solution is a complete genre pivot. Season 2 will reportedly focus on internal power struggles within the royal household, prioritizing the character arcs of Ishaan Khatter, Sakshi Tanwar, and veteran actress Zeenat Aman. It's a shift from a relationship drama to a family saga — think *Succession* in a palace rather than *Bridgerton* in Mumbai.

## What's Next for Reen

Pre-production is underway, with filming expected to begin in July 2026. Reen is also attached to direct a period drama based on the life of legendary actress Madhubala, backed by Sanjay Leela Bhansali, with *Dhurandhar* actress Sara Arjun in the lead. Reports suggest she'll complete The Royals Season 2 before moving on to the Madhubala biopic later this year.

## Why NRIs Should Watch This Space

For diaspora audiences who subscribe to Netflix partly for Indian content, this overhaul is a test case. Netflix India has historically been cautious about course-correcting underperforming shows — they tend to either quietly cancel or push ahead with the same formula. The Royals Season 2 represents a third option: keeping the IP alive while fundamentally changing what it is.

If it works — if Reen can transform a polarizing rom-com into a compelling family drama — it could become the template for how Netflix India handles its growing slate of original series. If it doesn't, it'll confirm what skeptics have argued: that some shows can't be saved by a director swap alone.

Either way, it's worth watching.

*Sources: Bollywood Hungama, Variety India, Blaze Trends, The Popular Story*""",
    "image_person": "Jasmeet K. Reen",
    "image_fallback_query": "Netflix India streaming series director",
    "image_person_alt": "Ishaan Khatter",
})

# ─── PUBLISH ──────────────────────────────────────────────────

print(f"\n{'='*60}")
print(f"Entertainment Writer — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
print(f"{'='*60}\n")

published = 0
for i, art in enumerate(articles, 1):
    print(f"\n--- Article {i}/{len(articles)} ---")
    print(f"  Headline: {art['headline'][:80]}...")
    
    # Image sourcing
    person = art.pop("image_person", None)
    person_alt = art.pop("image_person_alt", None)
    fallback = art.pop("image_fallback_query", None)
    
    img_url = None
    attribution = None
    
    # Try Wikipedia first for the primary person
    if person:
        img_url = fetch_wikipedia_person_image(person)
        if img_url:
            attribution = "Wikimedia Commons"
    
    # Try alternate person if first didn't work
    if not img_url and person_alt:
        img_url = fetch_wikipedia_person_image(person_alt)
        if img_url:
            attribution = "Wikimedia Commons"
    
    # Pexels fallback
    if not img_url and fallback:
        img_url = fetch_pexels_image(fallback)
        if img_url:
            attribution = "Pexels"
    
    # Validate
    if img_url and validate_image(img_url):
        art["image_url"] = img_url
        art["image_attribution"] = attribution
        print(f"  ✓ Image set: {attribution}")
    elif img_url:
        print(f"  ✗ Image failed validation, publishing without image")
    else:
        print(f"  ⚠ No image found, publishing without image")
    
    # Insert
    result = sb_insert("p2_articles", art)
    if result:
        art_id = result.get("id", "unknown")
        print(f"  ✓ Published: {art['slug']} (id: {art_id})")
        published += 1
    else:
        print(f"  ✗ Failed to publish: {art['slug']}")

print(f"\n{'='*60}")
print(f"Done. Published {published}/{len(articles)} articles.")
print(f"{'='*60}")

#!/usr/bin/env python3
"""Entertainment writer for The Videshi — 2026-05-29 evening batch."""

import json, os, re, sys, time, uuid, urllib.parse
import requests
from datetime import datetime, timezone

# ── Load env file ──
def load_env(path):
    with open(os.path.expanduser(path)) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ[k.strip()] = v.strip().strip('"').strip("'")

load_env("~/.env.supabase")

# ── Supabase credentials ──
SB_URL = os.environ["SUPABASE_URL"]
SB_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS_KEY = None
try:
    with open(os.path.expanduser("~/workspace/.env.pexels")) as f:
        for line in f:
            if "PEXELS_API_KEY" in line:
                PEXELS_KEY = line.strip().split("=", 1)[1].strip().strip('"').strip("'")
except Exception:
    pass

HEADERS = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

def sb_insert(table, row):
    r = requests.post(f"{SB_URL}/rest/v1/{table}", headers=HEADERS, json=row, timeout=30)
    if r.status_code in (200, 201):
        data = r.json()
        return data[0] if isinstance(data, list) and data else data
    print(f"  ✗ Insert failed ({r.status_code}): {r.text[:300]}")
    return None

def sb_patch(table, match, patch):
    params = "&".join(f"{k}={v}" for k, v in match.items())
    r = requests.patch(f"{SB_URL}/rest/v1/{table}?{params}", headers=HEADERS, json=patch, timeout=30)
    if r.status_code in (200, 204):
        return True
    print(f"  ✗ Patch failed ({r.status_code}): {r.text[:300]}")
    return False

# ── Image sourcing ──
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

def fetch_pexels_image(query, fallback_query=None):
    """Fetch image from Pexels as fallback."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key available")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            import subprocess
            result = subprocess.run(
                ["curl", "-sS", f"https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=3",
                 "-H", f"Authorization: {PEXELS_KEY}"],
                capture_output=True, text=True, timeout=15
            )
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            for photo in photos:
                url = photo.get("src", {}).get("large2x") or photo.get("src", {}).get("original")
                if url:
                    print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

def validate_image_url(url):
    """Validate image URL returns 200 with image content-type and reasonable size."""
    if not url:
        return False
    # Check for banned sources
    banned = ["fbcdn.net", "cdninstagram.com", "lookaside.fbsbx.com"]
    if any(b in url for b in banned):
        print(f"  ✗ Banned image source: {url[:80]}")
        return False
    banned_params = ["_nc_ht=", "_nc_cat=", "ccb="]
    if any(p in url for p in banned_params):
        print(f"  ✗ Signed Meta URL: {url[:80]}")
        return False
    try:
        r = requests.head(url, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, timeout=10, allow_redirects=True)
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            return True
        # Some servers don't return Content-Length on HEAD, try GET
        if r.status_code == 200 and "image" in ct:
            return True
        print(f"  ⚠ Image validation failed: status={r.status_code}, ct={ct}, cl={cl}")
    except Exception as e:
        print(f"  ⚠ Image validation error: {e}")
    return False

# ── Articles ──
articles = []

# ── ARTICLE 1: Helen Returns to Acting After 14 Years in "Brown" ──
articles.append({
    "headline": "Helen Hasn't Acted in 14 Years. She Just Came Back for Karisma Kapoor's ZEE5 Noir Thriller.",
    "subheadline": "Brown premieres June 5 on ZEE5 — a Berlinale-selected Kolkata-set crime series that also marks singer Shaan's OTT debut.",
    "slug": "helen-14-year-comeback-brown-karisma-kapoor-zee5-berlinale-noir-nri-20260529",
    "category": "entertainment",
    "vertical": "entertainment",
    "body": """Helen, the legendary dancer and actress who defined an era of Hindi cinema cabaret, has returned to acting after a 14-year absence. Her last screen appearance was in 2012. The occasion: a cameo in *Brown*, the ZEE5 neo-noir crime thriller that premieres on June 5.

## What She Said About Coming Back

"It's been such a long time since I faced the camera," Helen said in a statement released this week. "Returning to acting, even for a small role in Brown, has been delightful. Sometimes, it's not about the length of the role, but the joy of being part of something special."

Her character, she added, provides comic relief in what is otherwise a deeply intense show. "My character brings in moments of lightness and comic relief. I'm so glad I was considered for this part — it gave me the chance to reconnect with my craft and relive the magic of being on set."

## The Show

*Brown* is directed by Abhinay Deo and based on Abheek Barua's acclaimed novel *City of Death*. Set in the dark underbelly of Kolkata, the series follows Rita Brown (Karisma Kapoor), a suicidal, alcoholic police officer who partners with a grieving widower to track down a serial killer driven by a perceived divine purpose.

It marks Karisma Kapoor's return to the OTT space after *Mentalhood* in 2020. The ensemble cast includes Surya Sharma, Soni Razdan, Jisshu Sengupta, and K.K. Raina. Singer Shaan also appears in a cameo — his first acting role on a streaming platform.

## Why the Diaspora Should Care

*Brown* holds a rare distinction: it is the only Indian web series ever selected for the Berlinale Series Market Selects at the Berlin International Film Festival. That puts it in a different league from the typical Indian OTT crime thriller.

For NRIs, ZEE5 is available globally — the platform has been aggressively expanding its international footprint. A Kolkata-set noir with Berlinale credentials, a 90s icon leading the cast, and a genuine living legend in a supporting role makes this one of the most interesting Indian streaming premieres of the summer.

## Helen's Legacy

Born Helen Ann Richardson in 1939 to an Anglo-Indian father and a Burmese mother, Helen became one of Bollywood's most iconic screen presences across the 1960s, 70s, and 80s. Her dance numbers — *Mehbooba Mehbooba*, *Piya Tu Ab To Aaja*, *Mungda* — are embedded in Indian pop culture. She married filmmaker Salim Khan in 1981 and was awarded the Padma Shri in 2009.

At 87, she is still choosing her roles with intention. "Working with Soni and Karisma was an absolute pleasure," she said. "I've known them both for years, and sharing the screen with them felt so natural and full of warmth."

*Brown* premieres June 5 on ZEE5 worldwide.""",
    "sources": json.dumps([
        {"name": "Filmfare", "url": "https://www.filmfare.com/news/bollywood/helen-makes-special-cameo-in-karisma-kapoor-starrer-brown-calls-it-delightful-84189.html"},
        {"name": "Bollywood Hungama", "url": "https://www.bollywoodhungama.com/news/bollywood/brown-helen-talks-about-returning-to-acting-after-14-years-with-karisma-kapoor-starrer/"},
        {"name": "TollyBollyHulchul", "url": "https://tollybollyhulchul.com/karisma-kapoor-steps-out-of-her-comfort-zone-in-abhinay-deos-crime-drama-brown/"}
    ]),
    "image_person": "Helen (actress)",
    "image_fallback_query": "Kolkata noir crime film dark moody",
    "image_fallback_query2": "Kolkata night city",
})

# ── ARTICLE 2: HYBE India Building Girl Group from Indian Diaspora ──
articles.append({
    "headline": "BTS's Parent Company Is Auditioning Indian Girls Across Five Countries. The Diaspora Is the Target.",
    "subheadline": "HYBE India's 15-city global audition tour hits New York, Toronto, London, Singapore, and Sydney alongside 10 Indian cities — the largest K-pop talent hunt ever launched on the subcontinent.",
    "slug": "hybe-india-girl-group-audition-diaspora-kpop-bts-global-tour-nri-20260529",
    "category": "entertainment",
    "vertical": "entertainment",
    "body": """HYBE — the South Korean entertainment giant behind BTS, SEVENTEEN, LE SSERAFIM, and NewJeans — is building a girl group from India and the Indian diaspora. And it is not doing this quietly.

## The Scale

The HYBE India Audition is a 15-city global tour running from May through July 2026. The Indian leg covers Guwahati, Mumbai, Pune, Hyderabad, Bengaluru, Delhi, Chennai, Ahmedabad, Kolkata, and Chandigarh. The international leg — and this is the part that matters for NRIs — includes Toronto (May 23-24), New York (May 30), Singapore (June 13), Sydney (June 20), and London (July 4-5).

The auditions are open to female participants born between 2005 and 2011. Categories include singing, dancing, rap, and modelling. Online auditions remain open until July 31.

## More Than Auditions

Each city stop includes a Pop-up Park — an immersive, fan-first experience featuring Random Play Dance sessions, K-pop music zones, live artist performances, Weverse Fan Letter stations, and walk-in audition booths. Previous editions in Mumbai, Guwahati, Pune, and Hyderabad drew massive crowds.

Corporate partners include Samsung, H&M, Kia, Nongshim, Shoppers Stop, and Snapchat — a signal that HYBE sees India not as a test market but as a serious commercial bet.

## Why This Matters

"India has never lacked talent or ambition — what's been missing is a consistent pathway to the global stage," said Damien Woochang Lee, CEO of HYBE India, in an interview with Rolling Stone India. "This audition is where that process begins."

The company's internal research pointed to what diaspora families have observed for years: a generation of young Indian women who consume K-pop voraciously, are trained in dance and vocals, but have no realistic route to the kind of pop career structure that South Korea has perfected.

HYBE's model — intense multi-year training, strategic global debuts, massive digital-first fan ecosystems — has already been applied to Katseye, its American girl group. Applying it to India and the Indian diaspora is a natural extension.

## The Diaspora Dimension

The inclusion of five international cities (Toronto, New York, Singapore, Sydney, London) makes the intent unmistakable. HYBE is not just looking for talent in India — it is looking for talent among Indians abroad. Second-generation diaspora kids who grew up on both Bollywood and BTS, who code-switch between cultures, who have the bilingual fluency and performance instincts that global pop demands.

LE SSERAFIM has already publicly backed the initiative. Source Music, HYBE's subsidiary that manages the group, is actively supporting the prospective candidates.

For NRI parents who have watched their daughters obsess over K-pop choreography for years, this is an unusual moment: a global entertainment company worth billions is specifically looking for your kid.

The Delhi stop is scheduled for June 13-14. The New York audition is May 30. Online applications close July 31 at india.hybeaudition.com.""",
    "sources": json.dumps([
        {"name": "Bollywood Hungama", "url": "https://www.bollywoodhungama.com/news/bollywood/reble-to-perform-at-hybe-india-pop-up-park-in-delhi-during-global-talent-hunt/"},
        {"name": "Rolling Stone India / Mirchi", "url": "https://www.mirchi.in/music/hybe-launches-nationwide-search-for-new-girl-group-in-india"},
        {"name": "Filmibeat", "url": "https://www.filmibeat.com/bollywood/news/hybe-india-announces-15-city-global-audition-tour-with-pop-up-parks-across-india-for-fans-344413.html"}
    ]),
    "image_person": None,
    "image_fallback_query": "K-pop dance audition stage performance",
    "image_fallback_query2": "young women dance performance stage",
})

# ── ARTICLE 3: Sonakshi Sinha Rents Luxury Apartment to Kuwait Consulate ──
articles.append({
    "headline": "Sonakshi Sinha Just Rented Her Bandra Apartment to the Kuwait Consulate. The Rent Is ₹16 Lakh a Month.",
    "subheadline": "Property documents reveal the 4,350 sq ft luxury flat in 81 Aureate will house Kuwait's Consul General for one year at a total cost of ₹1.92 crore.",
    "slug": "sonakshi-sinha-bandra-apartment-kuwait-consulate-16-lakh-rent-nri-20260529",
    "category": "entertainment",
    "vertical": "entertainment",
    "body": """When Bollywood real estate makes news, it usually involves a purchase. This time it is a lease — and the tenant is a foreign government.

Sonakshi Sinha has rented out her luxury apartment in Mumbai's Bandra West to the Consulate General of the State of Kuwait for a monthly rent of ₹16 lakh (approximately $19,000). The total 12-month lease is worth ₹1.92 crore, according to property registration documents accessed by CRE Matrix.

## The Property

The apartment is located on a high floor of 81 Aureate, a premium residential tower in Bandra West — one of Mumbai's most sought-after addresses. It spans 4,350 square feet of carpet area, plus a 27 sq ft servant's quarters. The unit comes with three dedicated parking spaces.

Building amenities available to the tenant at no extra cost include a gymnasium, library, conference room, two swimming pools (separate for men and women), walking and jogging tracks, a banquet hall, three garden spaces, a yoga studio, an open-sky fitness centre, a children's play area, and a clubhouse.

## The Tenant

The lease names Kuwait's Consul General Emad Abdul Aziz Al-Kharaz as the occupant, along with his family and staff. The agreement was registered on May 25, 2026, with a stamp duty of ₹96,000 and a registration fee of ₹1,000. The lease runs from June 7, 2026 to June 6, 2027.

Because the tenant holds diplomatic status, Al-Kharaz was granted an exemption from appearing personally at the local Sub-Registrar office under Section 88 of the Indian Registration Act.

Under the terms, Sonakshi continues to pay standard society maintenance charges, municipal taxes, and water taxes, while the Consulate covers all routine utility bills and common area maintenance during the lease.

## What It Tells You About Mumbai Real Estate

₹16 lakh a month for a rental in Bandra West is at the extreme high end of Mumbai's residential market, but it reflects the going rate for premium inventory of this size in the area. Diplomatic tenants are generally considered ideal lessors — they pay on time, maintain properties well, and rarely breach lease terms.

For context, fellow Bollywood actor Arjun Kapoor recently sold his Bandra flat for ₹16 crore. The neighborhood has long been the preferred address for the film industry, and property values there have appreciated significantly over the past decade.

## Sonakshi's Current Work

Sonakshi Sinha is currently appearing in *System*, a courtroom drama on Prime Video that marks her first role as a lawyer. The film, which also stars Jyothika and Ashutosh Gowariker, premiered on May 22. She plays Neha, an ambitious young attorney who must prove her capabilities before earning a partnership at her father's law firm.

Between a diplomatic lease and a legal drama, it has been a week of unusual paperwork for Sonakshi.""",
    "sources": json.dumps([
        {"name": "Bollywood Hungama", "url": "https://www.bollywoodhungama.com/news/bollywood/sonakshi-sinha-rents-out-mumbai-apartment-to-kuwait-consulate-at-rs-16-lakhs-per-month-report/"},
        {"name": "Blaze Trends", "url": "https://blazetrends.com/sonakshi-sinha-leases-sea-facing-mumbai-apartment-to-kuwait-consul-general-for-rs-16-lakh-rent/"},
        {"name": "7Globe", "url": "https://7globe.in/sonakshi-sinha-rents-out-bandra-luxury-home-to-kuwait-consulate-for-rs-1-92-crore-report/"}
    ]),
    "image_person": "Sonakshi Sinha",
    "image_fallback_query": "Mumbai Bandra luxury apartment skyline",
    "image_fallback_query2": "Mumbai skyscraper luxury residential",
})

# ── Process and publish ──
now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

for i, art in enumerate(articles, 1):
    print(f"\n{'='*60}")
    print(f"Article {i}: {art['headline'][:80]}...")
    print(f"{'='*60}")

    # Image sourcing
    img_url = None
    if art.get("image_person"):
        img_url = fetch_wikipedia_person_image(art["image_person"])
        if not img_url and art["image_person"] != art.get("image_person"):
            # try alternate forms
            pass

    if not img_url:
        img_url = fetch_pexels_image(art.get("image_fallback_query"), art.get("image_fallback_query2"))

    if img_url and not validate_image_url(img_url):
        print(f"  ⚠ Image failed validation, skipping")
        img_url = None

    if img_url:
        print(f"  ✓ Final image: {img_url[:80]}...")
    else:
        print(f"  ⚠ No image found — publishing without image")

    # Build row
    row = {
        "headline": art["headline"],
        "subheadline": art["subheadline"],
        "slug": art["slug"],
        "category": art["category"],
        "vertical": art["vertical"],
        "body": art["body"].strip(),
        "sources": json.loads(art["sources"]),
        "image_url": img_url,
        "status": "published",
        "published_at": now,
    }

    result = sb_insert("p2_articles", row)
    if result:
        art_id = result.get("id")
        print(f"  ✓ Published: {art['slug']} (id={art_id})")
    else:
        print(f"  ✗ FAILED to publish: {art['slug']}")

    time.sleep(1)

print(f"\n{'='*60}")
print(f"Done. {len(articles)} articles processed.")
print(f"{'='*60}")

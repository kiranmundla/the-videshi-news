#!/usr/bin/env python3
"""
News writer for The Videshi — June 2, 2026 batch
Produces 3 articles in the 'news' category.
"""

import json, os, uuid, requests, urllib.parse, time
from datetime import datetime, timezone

# --- ENV ---
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS_KEY = os.environ.get("PEXELS_API_KEY", "")

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

# --- IMAGE HELPERS ---

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
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image found for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None


def fetch_pexels_image(query, fallback_query=None):
    """Fetch a relevant image from Pexels via curl (Python urllib gets 403)."""
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            import subprocess
            result = subprocess.run(
                ["curl", "-sS", "-H", f"Authorization: {PEXELS_KEY}",
                 f"https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5&orientation=landscape"],
                capture_output=True, text=True, timeout=15,
            )
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            for p in photos:
                url = p.get("src", {}).get("large2x") or p.get("src", {}).get("large")
                if url:
                    print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None


def validate_image(url):
    """Validate image URL returns 200 with image content-type and >5KB."""
    if not url:
        return False
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                          headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            return True
        # Some servers don't support HEAD well, try GET
        r2 = requests.get(url, timeout=10, stream=True, allow_redirects=True,
                          headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct2 = r2.headers.get("Content-Type", "")
        # Read first chunk to check size
        chunk = r2.raw.read(6000)
        if r2.status_code == 200 and "image" in ct2 and len(chunk) > 5000:
            return True
    except Exception as e:
        print(f"  ⚠ Image validation failed for {url[:60]}: {e}")
    return False


def upload_to_supabase_storage(image_url, filename):
    """Download image and upload to Supabase article-images bucket."""
    try:
        r = requests.get(image_url, timeout=20, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        if r.status_code != 200 or len(r.content) < 5000:
            print(f"  ⚠ Download failed for {image_url[:60]}: status={r.status_code}, size={len(r.content)}")
            return None

        content_type = r.headers.get("Content-Type", "image/jpeg")
        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
        resp = requests.post(
            upload_url,
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": content_type,
                "x-upsert": "true",
            },
            data=r.content,
            timeout=30,
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


def insert_article(article):
    """Insert article into p2_articles."""
    url = f"{SUPABASE_URL}/rest/v1/p2_articles"
    r = requests.post(url, headers=HEADERS, json=article, timeout=30)
    if r.status_code in (200, 201):
        data = r.json()
        aid = data[0]["id"] if isinstance(data, list) and data else "unknown"
        print(f"  ✓ Inserted: {article['slug']} (id={aid})")
        return aid
    else:
        print(f"  ✗ Insert failed for {article['slug']}: {r.status_code} {r.text[:300]}")
        return None


# ========== ARTICLES ==========

articles = []

# -----------------------------------------------------------------------
# ARTICLE 1: AirTrunk $21 billion data center in Maharashtra
# -----------------------------------------------------------------------
print("\n=== Article 1: AirTrunk $21B data center ===")

art1_slug = "airtrunk-21-billion-data-center-maharashtra-blackstone-ai-india-20260602"
art1_headline = "A Blackstone-Backed Firm Just Committed $21 Billion to Build a Data Centre on the Outskirts of Mumbai."
art1_subheadline = "AirTrunk's deal in Maharashtra is part of a $630 billion wave of tech investments that is turning India into Asia's AI infrastructure hub — and the biggest construction site the cloud industry has ever seen."

art1_body = """India's ambition to become a global AI powerhouse just received its largest single commitment yet.

AirTrunk, the Australian hyperscale data centre operator backed by Blackstone, has signed a letter of intent with the Maharashtra government to build a 3 GW data centre campus in the Raigad Pen Growth Centre, just outside Mumbai. The investment: ₹2 lakh crore, or roughly $21 billion.

Maharashtra Chief Minister Devendra Fadnavis announced the deal after meeting AirTrunk founder and CEO Robin Khuda, alongside Australian Consul General Paul Murphy. "A massive Rs 2 Lakh Crore investment with 3 GW capacity," Fadnavis said in a post on X, calling it a milestone for the state's digital infrastructure ambitions.

## The Scale of It

To put 3 GW in perspective: that is roughly twice the entire installed data centre capacity of India today. The country currently has about 1.5 GW of operational data centre power, and industry projections suggest it will need around 10 GW by 2030. AirTrunk alone is committing to nearly a third of that future demand in a single campus.

The company already operates hyperscale facilities in Hong Kong, Japan, Malaysia, and Singapore. It entered India earlier this year through the acquisition of Lumina CloudInfra, which gave it access to a 600 MW pipeline across Mumbai, Chennai, and Hyderabad.

## A Wider Flood of Capital

AirTrunk's deal is the latest in a staggering wave of foreign technology investment washing over India. According to Reuters, more than $630 billion in commitments are expected from US tech giants this year alone, driven in part by Indian tax breaks for foreign firms operating domestic data centres.

India's own conglomerates are matching the pace. Reliance committed $110 billion to AI and data infrastructure in February. Adani pledged $100 billion in the same month. Amazon, Microsoft, and Google have all announced multi-billion-dollar expansions of their Indian cloud networks.

The investments are being steered at the highest levels. The India-US technology partnership in semiconductors and AI is now jointly overseen by the National Security Advisors of both countries, merging commercial digitisation with strategic competition against China.

## Why It Matters for the Diaspora

For the roughly 4.4 million Indian-Americans in the United States and millions more NRIs worldwide, the data centre boom represents something tangible: a bet by the world's largest technology investors that India's digital infrastructure will be globally competitive within this decade.

The implications ripple outward. More data centres mean more engineering jobs in India. More cloud capacity means Indian startups can train and deploy AI models domestically rather than renting compute from Singapore or Virginia. And more foreign capital flowing into Indian real estate, power, and construction means a broader economic multiplier that touches everything from steel demand to suburban land prices near Mumbai.

Blackstone, AirTrunk's parent, has already directed nearly 40 percent of its $50 billion India investment portfolio into Maharashtra. The state is positioning itself as the country's primary data centre corridor, competing with Hyderabad and Chennai for a market that barely existed five years ago.

## The Catch

There is one. India's power grid will need to keep up. A 3 GW data centre campus requires reliable, round-the-clock electricity at a scale that rivals small cities. India's renewable energy buildout is accelerating, but grid reliability in many states remains uneven. Blackstone CEO Stephen Schwarzman himself has warned that electricity shortages could constrain AI expansion globally.

For now, the deal is a letter of intent — not a construction contract. The timeline for build-out has not been disclosed. But the signal is unmistakable: the world's largest infrastructure investors believe India is where the next generation of AI will be built.

*Sources: Reuters, ANI, AirTrunk, Maharashtra CMO, Blackstone.*"""

# Image: Pexels for data center / server room
img1 = fetch_pexels_image("data center server room", "hyperscale data center")
img1_final = None
if img1 and validate_image(img1):
    img1_final = upload_to_supabase_storage(img1, f"{art1_slug}.jpg")
if not img1_final and img1 and validate_image(img1):
    img1_final = img1  # Use Pexels direct link as fallback

articles.append({
    "headline": art1_headline,
    "subheadline": art1_subheadline,
    "body": art1_body,
    "slug": art1_slug,
    "category": "news",
    "vertical": "economy",
    "status": "published",
    "is_editorial": False,
    "published_at": datetime.now(timezone.utc).isoformat(),
    "image_url": img1_final,
    "image_attribution": "The Videshi" if img1_final and "supabase" in (img1_final or "") else "Pexels",
    "sources": json.dumps(["Reuters", "ANI", "AirTrunk", "Maharashtra CMO"]),
})


# -----------------------------------------------------------------------
# ARTICLE 2: India rewires oil supply chain to Latin America & Africa
# -----------------------------------------------------------------------
print("\n=== Article 2: India oil diversification ===")

art2_slug = "india-oil-imports-latin-america-africa-venezuela-hormuz-diversification-20260602"
art2_headline = "India Is Quietly Rewiring Its Entire Oil Supply Chain. Venezuela Is Now Its Fourth-Largest Supplier."
art2_subheadline = "Three months into the Hormuz blockade, Indian refiners have shifted billions of dollars in crude purchases to Latin America and Africa — a move that looks less like a stopgap and more like a permanent realignment."

art2_body = """Before the Iran war, India's oil map was simple. Roughly half of its crude came from the Middle East, flowing through the Strait of Hormuz. Russia and Iraq filled in the rest. The Gulf was gravity — automatic, familiar, cheap.

Three months later, that map has been redrawn.

## The New Suppliers

Indian refiners have sharply increased crude oil purchases from Venezuela, Brazil, Angola, and Nigeria to cover shortfalls caused by the near-total shutdown of commercial shipping through the Strait of Hormuz, according to Kpler shipping data cited in multiple reports this week.

Venezuela is the most striking addition. The South American producer, long hobbled by US sanctions and internal dysfunction, is now on track to become India's fourth-largest crude supplier in May — a position it has never held before. Indian demand for Venezuela's heavy crude has surged as Gulf flows remain constrained and refiners scramble for compatible grades.

Brazil, Angola, and Nigeria have also seen significant increases in shipments to India in April and May. The diversification has happened fast, driven by state refiners like Indian Oil Corporation, Bharat Petroleum, and Hindustan Petroleum, all acting under government encouragement to reduce dependence on a single chokepoint.

## Russia Stays, But the Mix Changes

Russia remains India's largest individual supplier, with about 1.9 million barrels per day expected in May. Iraq, despite its proximity to the conflict zone, is still delivering roughly 41,000 bpd — a fraction of its pre-war volumes, but a sign that some Basra-grade shipments are finding alternate routes.

The overall picture is of a supply chain that has been fundamentally rebalanced. India's oil basket no longer tilts toward the Gulf. It spans four continents.

## The Oman Corridor

Adding to the shift, the India-Oman Comprehensive Economic Partnership Agreement took effect on June 1, opening what trade analysts are calling a "Hormuz bypass." Oman's major ports — Salalah and Duqm — sit on the Arabian Sea, entirely outside the Strait of Hormuz. While every other Gulf exporter's shipments must transit the blockaded waterway, Oman's do not.

The numbers reflect this. India's imports from Oman skyrocketed from $430 million in April 2025 to nearly $1.5 billion in April 2026, according to the Global Trade Research Initiative. GTRI founder Ajay Srivastava noted that Oman has granted India zero-duty access on 98 percent of its tariff lines, covering 99 percent of India's exports by value.

## Structural, Not Temporary

Government officials and refinery executives have privately signalled that the diversification is not a short-term fix. Even if the Strait of Hormuz reopens — a prospect that remains uncertain as US-Iran peace talks stall — India intends to maintain relationships with Latin American and African suppliers as a permanent hedge against future disruptions.

The Finance Ministry's latest monthly economic review, published last week, noted that "the Hormuz disruption remains the most consequential variable for India's external and price outlook." Crude oil and petroleum products accounted for 53.9 percent of India's total merchandise imports from the Gulf Cooperation Council in FY26.

## What This Means for NRIs

For the Indian diaspora watching from abroad, the oil supply chain reshuffle has direct implications. Energy prices affect everything from airline ticket costs between New York and Mumbai to the inflation rate that determines how far remittance rupees stretch.

Goldman Sachs identified India as the most exposed major economy to the Hormuz disruption, with a potential GDP hit of 3.6 percent — worse than Turkey, South Korea, or any other large country. The diversification strategy is India's primary defence against that scenario.

The question is whether it is enough. Brent crude hovered near $95 a barrel on Monday. Inventories are falling globally. And Iran's Revolutionary Guards have now threatened to extend their blockade to the Bab el-Mandeb Strait at the mouth of the Red Sea — a second chokepoint that would strangle even the alternate routes India has worked so hard to build.

*Sources: Kpler, Reuters, GTRI, India Finance Ministry, The Indian Eye, Goldman Sachs.*"""

# Image: Pexels for oil tanker / refinery
img2 = fetch_pexels_image("oil tanker ship ocean", "crude oil refinery")
img2_final = None
if img2 and validate_image(img2):
    img2_final = upload_to_supabase_storage(img2, f"{art2_slug}.jpg")
if not img2_final and img2 and validate_image(img2):
    img2_final = img2

articles.append({
    "headline": art2_headline,
    "subheadline": art2_subheadline,
    "body": art2_body,
    "slug": art2_slug,
    "category": "news",
    "vertical": "economy",
    "status": "published",
    "is_editorial": False,
    "published_at": datetime.now(timezone.utc).isoformat(),
    "image_url": img2_final,
    "image_attribution": "The Videshi" if img2_final and "supabase" in (img2_final or "") else "Pexels",
    "sources": json.dumps(["Kpler", "Reuters", "GTRI", "India Finance Ministry", "The Indian Eye", "Goldman Sachs"]),
})


# -----------------------------------------------------------------------
# ARTICLE 3: Goldman Sachs says India most exposed to Hormuz crisis
# -----------------------------------------------------------------------
print("\n=== Article 3: Goldman Sachs India exposure ===")

art3_slug = "goldman-sachs-india-most-exposed-economy-hormuz-3-6-percent-gdp-hit-20260602"
art3_headline = "Goldman Sachs Just Named India the Most Vulnerable Major Economy on Earth. The Number Is 3.6%."
art3_subheadline = "A new Goldman analysis maps exactly how much economic damage the Hormuz blockade can inflict country by country — and India tops the list, above Turkey, South Korea, and every G7 nation."

art3_body = """Goldman Sachs has done the math that everyone in Delhi has been trying to avoid.

In a sweeping analysis published on May 29, the investment bank mapped the economic fallout from the Strait of Hormuz blockade across every major economy. The finding that matters most for India: a potential GDP hit of 3.6 percent — the highest of any large country in the world.

## The Numbers

Goldman's note breaks the damage into two channels. The first is oil prices, which have risen roughly 50 percent since the conflict began. The second, less discussed, is the broader supply chain disruption: base chemicals are up more than 60 percent (the fastest rate ever recorded), helium prices have doubled, methanol is up 40 percent, and sulfur and sulfuric acid have surged 60 percent.

India's 3.6 percent exposure is the combined effect of both channels. Turkey comes second at 3.3 percent. South Korea is at 3.1 percent. The United States, cushioned by its own oil production and distance from the chokepoint, faces just 0.3 percent.

Vessel counts through the Strait of Hormuz are down more than 90 percent from normal levels, three months into the conflict. Some Asian petrochemical plants have already declared force majeure. Goldman's analysts warn that chemical supply disruptions could extend through 2027, even if the strait reopens tomorrow.

## Why India Is Most Exposed

India imports nearly 90 percent of its crude oil. Before the war, the Gulf accounted for more than half of that supply. The Hormuz closure hit India's traditional import routes harder than almost any other country's.

But the exposure goes beyond oil. India's manufacturing sector — which just posted its strongest PMI reading in three months — depends on imported chemicals, industrial gases, and specialty inputs that flow through the same Gulf chokepoint. When those inputs are disrupted, factories either slow down or pay dramatically more, squeezing margins even as output rises.

The rupee tells the story. It has fallen roughly 5 percent since the war began, hitting a record low of ₹96.95 per dollar before recovering slightly to ₹95. Foreign investors have pulled $26.4 billion from Indian equities in 2026 alone — more than the entire record annual outflow of 2025 — driven by the combination of high oil prices, a weakening currency, and geopolitical uncertainty.

## The RBI's Impossible Choice

This backdrop frames the Reserve Bank of India's rate decision on Friday, which Goldman's analysis makes even more consequential. The central bank has held rates at 5.25 percent since December, following 125 basis points of cuts last year.

Nearly 80 percent of economists in a Reuters poll expect the RBI to hold again. But interest rate swaps are pricing in nearly 100 basis points of tightening over the next 12 months — a market signal that traders believe the central bank will have to act eventually, even if it does not move this week.

BofA's chief India economist, Rahul Bajoria, described the dilemma as "whether to respond to market pressures or incoming data." Inflation remains below the RBI's 4 percent target for now, but fuel prices have already been hiked, the monsoon forecast is the weakest in 11 years, and food prices are expected to climb.

## The German Precedent

Goldman's note includes one cautious note of optimism. When Russia cut off gas to Germany in 2022, the most pessimistic models predicted a 12 percent GDP hit. The actual result was a slight technical recession — households and firms adapted far faster than anyone expected.

Goldman explicitly cites this as a reason to believe India's 3.6 percent figure may overstate the ultimate damage. Countries find workarounds. Supply chains reroute. Demand adjusts. India is already doing this — shifting crude purchases to Venezuela, Brazil, and Africa, signing new trade corridors with Oman, and stockpiling through strategic reserves.

But the German analogy has limits. Germany had ready access to LNG terminals, wealthy EU neighbours, and a mild winter. India faces a weak monsoon, 90 percent oil import dependence, and the constant risk that the conflict escalates further. Iran's Revolutionary Guards have now threatened to extend the blockade to the Bab el-Mandeb Strait — a move that would disrupt even the alternative shipping routes India has been building.

Goldman's realistic estimate for the global GDP headwind from the crisis is about 0.4 to 0.5 percent from non-oil disruptions, plus another 0.5 percentage points from the oil price itself. For India, the floor is higher and the ceiling is darker.

*Sources: Goldman Sachs (May 29 note), Reuters, BofA Global Research, CareEdge Ratings, The Street.*"""

# Image: Pexels for Indian financial district / stock market
img3 = fetch_pexels_image("Mumbai financial district skyline", "India stock exchange trading")
img3_final = None
if img3 and validate_image(img3):
    img3_final = upload_to_supabase_storage(img3, f"{art3_slug}.jpg")
if not img3_final and img3 and validate_image(img3):
    img3_final = img3

articles.append({
    "headline": art3_headline,
    "subheadline": art3_subheadline,
    "body": art3_body,
    "slug": art3_slug,
    "category": "news",
    "vertical": "economy",
    "status": "published",
    "is_editorial": False,
    "published_at": datetime.now(timezone.utc).isoformat(),
    "image_url": img3_final,
    "image_attribution": "The Videshi" if img3_final and "supabase" in (img3_final or "") else "Pexels",
    "sources": json.dumps(["Goldman Sachs", "Reuters", "BofA Global Research", "CareEdge Ratings", "The Street"]),
})


# ========== INSERT ALL ==========
print("\n=== Inserting articles ===")
for art in articles:
    insert_article(art)
    time.sleep(0.5)

print("\n✅ News writer batch complete.")

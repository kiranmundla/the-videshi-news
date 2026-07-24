#!/usr/bin/env python3
"""Videshi Writer — 2 fresh NEWS articles for 2026-05-26 ~21:30 PDT batch
Topics: 1) India bars piped gas customers from buying LPG cylinders —
           33M tonnes annual LPG, 60% imported, 90% from Middle East,
           government forces PNG users to surrender LPG within 30 days,
           India also waived restrictions for 2 Iranian LPG cargoes
        2) India rewires oil supply chain — Latin America & Africa fill
           Hormuz gap, Venezuela becomes #5 supplier (set to be #4 in May),
           Russia down from 50% to 35%, UAE rebounded, Iranian oil after
           7-year gap via US waiver, OPEC share 30%→45.2%, UAE exits OPEC
"""

import json, os, uuid, re, requests, urllib.parse
from datetime import datetime, timezone, timedelta
from pathlib import Path

env_file = Path.home() / ".env.supabase"
for line in env_file.read_text().strip().splitlines():
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

SB_URL = os.environ["SUPABASE_URL"]
SB_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

def sb_post(table, data):
    r = requests.post(f"{SB_URL}/rest/v1/{table}", headers=HEADERS, json=data, timeout=30)
    r.raise_for_status()
    return r.json()

def sb_get(table, params):
    r = requests.get(f"{SB_URL}/rest/v1/{table}", headers=HEADERS, params=params, timeout=30)
    r.raise_for_status()
    return r.json()

def sb_patch(table, params, data):
    h = {**HEADERS, "Prefer": "return=representation"}
    r = requests.patch(f"{SB_URL}/rest/v1/{table}", headers=h, params=params, json=data, timeout=30)
    r.raise_for_status()
    return r.json()

def make_slug(slug_base, date_suffix="20260526"):
    slug = slug_base.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    slug = slug[:70].rstrip('-')
    return f"{slug}-{date_suffix}"

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

pexels_env = Path.home() / "workspace" / ".env.pexels"
PEXELS_KEY = None
if pexels_env.exists():
    for line in pexels_env.read_text().strip().splitlines():
        if line.startswith("PEXELS_API_KEY="):
            PEXELS_KEY = line.split("=", 1)[1].strip()

def fetch_pexels_image(query, fallback_query=None):
    if not PEXELS_KEY:
        print("  ⚠ No Pexels key found")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            r = requests.get(
                "https://api.pexels.com/v1/search",
                headers={"Authorization": PEXELS_KEY},
                params={"query": q, "per_page": 5, "orientation": "landscape"},
                timeout=15
            )
            if r.status_code == 200:
                photos = r.json().get("photos", [])
                if photos:
                    url = photos[0]["src"]["large2x"]
                    print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

def upload_image_to_supabase(image_url, filename):
    try:
        img_data = requests.get(image_url, timeout=20, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}).content
        content_type = "image/jpeg"
        upload_url = f"{SB_URL}/storage/v1/object/article-images/{filename}"
        h = {
            "apikey": SB_KEY,
            "Authorization": f"Bearer {SB_KEY}",
            "Content-Type": content_type,
            "x-upsert": "true",
        }
        r = requests.post(upload_url, headers=h, data=img_data, timeout=30)
        if r.status_code in (200, 201):
            public_url = f"{SB_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {filename}")
            return public_url
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
    return image_url

# --- Dedup check ---
existing = sb_get("p2_articles", {
    "select": "headline,slug",
    "status": "eq.published",
    "published_at": "gte.2026-05-23T00:00:00Z",
    "order": "published_at.desc",
    "limit": "80"
})
existing_slugs = {a["slug"] for a in existing}
existing_headlines_lower = {a["headline"].lower()[:60] for a in existing}
print(f"Found {len(existing)} recent articles for dedup check")

now = datetime.now(timezone.utc)
now_iso = now.isoformat().replace('+00:00', 'Z')

articles = []

# ============================================================
# ARTICLE 1: India Bars PNG Customers from Buying LPG Cylinders
# — Cooking Gas Crisis Deepens as Hormuz Blockade Chokes Supply
# ============================================================
slug1 = make_slug("india-bars-png-customers-lpg-cylinders-cooking-gas-crisis")
if slug1 not in existing_slugs and not any("lpg" in h and "png" in h for h in existing_headlines_lower) and not any("lpg" in h and "bar" in h for h in existing_headlines_lower) and not any("cooking gas" in h and "bar" in h for h in existing_headlines_lower):
    headline1 = "India Just Banned 10 Million Piped Gas Households from Buying LPG Cylinders. The Cooking Gas Crisis Is Now a Kitchen-Table Emergency."
    subheadline1 = "A government order on Monday bars anyone with a PNG connection from refilling LPG — effective immediately. Consumers have 30 days to surrender their LPG connection or take a transfer voucher. India imported 90% of its cooking gas from the Middle East before the Hormuz blockade. It has now waived sanctions to accept two Iranian LPG cargoes."
    body1 = """India's petroleum ministry issued a gazette notification on Monday barring households with piped natural gas connections from purchasing liquefied petroleum gas cylinders — with immediate effect.

The order is not a suggestion. It is a prohibition. If you have a PNG connection and you try to refill your LPG cylinder, you cannot. You have 30 days to either surrender your LPG connection entirely or take a transfer voucher that allows you to restore it if you move to an area without piped gas infrastructure.

"A person or household having a domestic LPG connection and subsequently having obtained a piped natural gas connection shall not forthwith take a refill of domestic LPG cylinder," the notification states.

The language is bureaucratic. The reality is not. India consumes 33.15 million metric tons of LPG per year. About 60 percent of that is imported. And about 90 percent of those imports came from the Middle East — through the Strait of Hormuz, which has been effectively closed since the U.S.-Israel war on Iran began on February 28.

## Why This Order, Why Now

The government has been trying to shift PNG customers off LPG since March, when the petroleum ministry first asked piped gas consumers to voluntarily give up their cylinder connections within three months. That was a request. Monday's gazette notification is a legal mandate.

The reason is arithmetic. India's LPG supply chain is broken. The Strait of Hormuz carried the cooking gas that heated Indian kitchens — and now it doesn't. The government has been rationing industrial LPG allocations to prioritize households, but even with rationing, the math doesn't work if millions of PNG-connected homes are also drawing down LPG stocks.

The petroleum ministry said supply remains "affected by the prevailing geopolitical situation in West Asia" but insisted that household delivery is being prioritized. Joint Secretary Sujata Sharma said 1.72 crore LPG cylinders were delivered over the preceding four days against bookings of 1.66 crore — meaning deliveries are keeping pace with demand, for now.

But the government is clearly preparing for a scenario where they don't. Forcing PNG customers off LPG is a conservation measure — freeing up cylinders for the roughly 300 million households that have no piped gas alternative.

## Iran's LPG Cargoes — A Quiet Policy Reversal

In a parallel development that underscores how dire the supply situation has become, India quietly waived restrictions on two Iranian LPG cargoes, allowing vessels — including one under international sanctions — to enter Indian ports.

India had not imported Iranian LPG in years, following U.S. sanctions pressure. The decision to grant waivers, confirmed by two officials familiar with the matter, represents a significant policy shift driven by necessity. India is the world's second-largest LPG importer, and its worst cooking gas crisis in decades is forcing New Delhi to balance sanctions compliance against kitchen-level energy security.

The waivers were issued on a case-by-case basis for vessels meeting safety standards, according to the officials. But the signal is unmistakable: India will take gas from wherever it can get it.

The government has also diversified LPG sourcing to the United States, Canada, and Norway — markets that are more expensive and farther away, but reachable without transiting Hormuz.

## What Ready-to-Eat Has to Do with Cooking Gas

One of the less-discussed consequences of the gas crisis is a surge in demand for ready-to-eat and frozen foods across Indian households. When cooking gas becomes unreliable — whether through rationing, delivery delays, or price uncertainty — families adapt by cooking less.

This is not a lifestyle choice. It is a coping mechanism. And it disproportionately affects lower-income and middle-class households, where LPG is the primary cooking fuel and where every rupee spent on a packaged meal is a rupee not spent on something else.

The government's push toward piped gas is, in theory, the right long-term move. PNG is domestically sourced, cheaper per unit than LPG, and not dependent on Middle Eastern shipping lanes. But PNG infrastructure covers only a fraction of India's geography. The Petroleum and Natural Gas Regulatory Board has been expanding city gas distribution networks, but even in connected cities, coverage is uneven — concentrated in newer residential complexes and unavailable in older neighborhoods.

## What NRIs Should Know

For diaspora families sending money home or managing households in India, the LPG ban has immediate practical implications.

If your family in India has both a PNG connection and an LPG cylinder — common in many urban households as a backup — they now have 30 days to decide. Surrendering the LPG connection means losing the safety net. Taking a transfer voucher preserves the option to reconnect if they move, but eliminates access to cylinders at their current address.

The transfer voucher provision was specifically designed for "transferable employees, migrant households, tenants, students, and families shifting to non-PNG areas," according to the ministry — an acknowledgment that India's workforce is mobile and that a one-size-fits-all energy policy doesn't fit a country where people move between piped-gas cities and cylinder-dependent towns.

The broader picture is that India's energy crisis is no longer just about petrol prices and industrial output. It has reached the kitchen. The Hormuz blockade has disrupted not just crude oil but also the cooking gas that 300 million Indian households depend on daily. The government is managing this through rationing, forced migration to piped gas, quiet diplomacy with Iran, and diversified imports from three continents.

For families in India, the question is practical: does your neighbourhood have reliable piped gas? For NRIs, the question is whether the monthly remittance now needs to account for higher food costs, backup electric induction cooktops, or simply the stress of a cooking fuel system that was stable for decades and now isn't."""
    article1 = {
        "id": str(uuid.uuid4()),
        "slug": slug1,
        "headline": headline1,
        "subheadline": subheadline1,
        "body": body1,
        "category": "news",
        "vertical": "nri-world",
        "diaspora_angle": "NRI families with dual PNG+LPG connections in India must decide within 30 days. Transfer voucher option for mobile households. Monthly remittances may need to cover higher food costs or backup cooking equipment. Cooking gas crisis has reached the kitchen — not just industrial/macro level. Iran LPG waiver signals desperation. Ready-to-eat food surge is a coping mechanism affecting lower/middle-income households.",
        "tags": ["lpg", "png", "cooking gas", "hormuz", "iran", "energy crisis", "piped gas", "rationing", "nri", "kitchen", "petroleum ministry", "ready to eat"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters — India bars piped natural gas customers from buying LPG cylinders, order shows", "url": "https://www.reuters.com/business/energy/india-bars-piped-natural-gas-customers-buying-lpg-cylinders-order-shows-2026-05-25/"},
            {"name": "Livemint — Govt bars piped gas users from buying cooking gas cylinders", "url": "https://www.livemint.com/news/govt-bars-png-consumers-from-buying-lpg-cylinder-west-asia-war-choked-energy-imports-piped-gas-11779725342378.html"},
            {"name": "Whispers in the Corridors — India Waives Restrictions for Iranian LPG Cargoes in A Change of Policy", "url": "https://whispersinthecorridors.in/detail/156773-India+Waives+Restrictions+for+Iranian+LPG+Cargoes+in+A+Change+of+Policy+!.html"},
            {"name": "Glance — Gas Shortage Fuels Surge in Ready-to-Eat and Frozen Foods Across Indian Homes", "url": "https://trends.glance.com/trends/gas-shortage-fuels-surge-in-ready-to-eat-and-frozen-foods-across-indian-homes"}
        ]),
        "score_total": 88,
        "status": "published",
        "published_at": now_iso,
        "image_url": None,
        "image_attribution": None,
    }
    # Image sourcing — Not about a specific person. Try Pexels with specific terms.
    img_url = fetch_pexels_image("LPG cooking gas cylinder India kitchen", "gas cylinder blue domestic cooking")
    if img_url:
        filename = f"{article1['id']}.jpg"
        final_url = upload_image_to_supabase(img_url, filename)
        article1["image_url"] = final_url
        article1["image_attribution"] = "The Videshi"
    sb_post("p2_articles", article1)
    articles.append(slug1)
    print(f"✓ Published: {headline1}")
else:
    print(f"⊘ Skipped (dedup): LPG/PNG ban article")

# ============================================================
# ARTICLE 2: India Rewires Its Entire Oil Supply Chain — Latin
# America, Africa, and Even Iran Fill the Hormuz Gap
# ============================================================
slug2 = make_slug("india-oil-supply-chain-latin-america-africa-venezuela-hormuz")
if slug2 not in existing_slugs and not any("latin america" in h and "oil" in h for h in existing_headlines_lower) and not any("venezuela" in h and "oil" in h for h in existing_headlines_lower) and not any("oil supply" in h and "africa" in h for h in existing_headlines_lower):
    headline2 = "India Has Quietly Rewired Its Entire Oil Supply Chain in Three Months. Venezuela Is Now Its Fifth-Largest Supplier. Iranian Oil Is Flowing for the First Time in Seven Years."
    subheadline2 = "Kpler data shows India imported 4.57 million barrels per day in April — down 15.5% from a year ago. Russia's share fell from 50% to 35%. The UAE rebounded to 670,000 bpd after exiting OPEC in May. Brazil and Venezuela are filling the gap. And Washington quietly granted India a waiver to buy Iranian crude — the first shipment since 2019."
    body2 = """Three months into the Strait of Hormuz crisis, India's oil supply chain looks nothing like it did on February 27.

Before the U.S.-Israel war on Iran closed the strait, India's oil import map was simple: Russia at the top, the Gulf states filling the middle, and everyone else at the margins. India bought most of its crude from nearby Middle Eastern producers — Kuwait, Iraq, Qatar, the UAE, Saudi Arabia — because the geography was obvious. Cheap, close, reliable.

That map has been redrawn. The data, compiled by energy intelligence firm Kpler and confirmed by trade sources to Reuters, tells the story of a country scrambling to keep 4.57 million barrels per day flowing into its refineries from wherever it can find them.

## The New Supplier Rankings

Russia remains India's top oil supplier, but its share has dropped sharply — from nearly 50 percent of India's imports to about 35 percent. Part of this is the Hormuz disruption, which has redirected global oil flows. Part of it is specific: Nayara Energy, the Vadodara-based refinery partly owned by Rosneft, shut its 400,000-barrel-per-day facility for maintenance in April, cutting Russian crude intake by 29.4 percent from March to 1.6 million bpd. In May, Russian volumes are expected to recover to about 1.9 million bpd.

The UAE has surged to second place, with imports rebounding to 669,700 bpd in April from just 230,600 bpd in March. Saudi Arabia held steady at about 619,500 bpd. The reason both Gulf producers can still ship to India is geography: the UAE and Saudi Arabia are the only Gulf oil states with pipeline infrastructure that bypasses the Strait of Hormuz entirely. Kuwait, Iraq, Qatar, and Bahrain rely on the waterway — and their exports to India have been disrupted or halted.

Iraq's case is instructive. India skipped Iraqi purchases entirely last month after exports were halted. Iraq was India's second-largest supplier before the war. Now it is functionally offline.

Brazil has climbed to fourth place. Venezuela is fifth — and Kpler data shows it is on course to become the fourth-largest supplier in May. These are not traditional Indian oil partners. Until recently, Venezuelan crude was barely present in India's import mix. Now it is a structural necessity.

Angola and Nigeria have also increased their share, as Indian refiners reach across the Atlantic to fill the gap left by the Gulf.

## The Iranian Oil Waiver — First Shipment Since 2019

Perhaps the most consequential shift is also the quietest. India received Iranian crude oil in April — the first shipment in seven years, since India halted Iranian purchases in 2019 under pressure from U.S. sanctions.

The resumption came via a temporary waiver granted by Washington, ostensibly to help stabilize global oil prices. The waiver is narrow and time-limited, but its existence signals how severely the Hormuz closure has strained the global oil market. The United States is fighting a war against Iran while simultaneously granting India permission to buy Iranian oil — a contradiction that reflects the desperation of the supply situation.

India received about 41,000 bpd of Iraqi oil in May as well, according to preliminary Kpler data — suggesting some cautious resumption of Gulf flows as a handful of tankers have navigated the strait in recent days, though HSBC cautioned in a research note that "there is still considerable uncertainty about how and when the Strait of Hormuz will return to its normal pre-war operations."

## OPEC's Shifting Share — and the UAE's Exit

The Organization of the Petroleum Exporting Countries' share of India's imports jumped to 45.2 percent in April from about 30 percent in March — driven almost entirely by the UAE's rebound.

But that number comes with an asterisk. The UAE exited OPEC in May, freeing itself from the cartel's output quotas. Abu Dhabi has been expanding production capacity for years, building toward 5 million bpd by 2027, and the Hormuz crisis gave it the political cover to leave. For India, the UAE's OPEC exit is broadly positive: a major supplier that is no longer constrained by production cuts and that has the infrastructure to ship oil without transiting the strait.

Russia, meanwhile, has moved in the opposite direction. Its share declined from nearly half of India's imports to about a third. This is not because India wants less Russian oil — it is because the global oil market is being reorganized by a war, and Russian crude is being competed for by China, Turkey, and other buyers who are also scrambling for non-Hormuz supply.

## The Cost of Diversification

India imported 4.57 million bpd in April — unchanged from March, but down 15.5 percent from a year earlier. That is not a small decline. It means Indian refineries are running below capacity, which means less domestically produced fuel, which means more pressure on retail prices, which means the ₹102-per-litre petrol and the four fuel price hikes in ten days.

The diversification itself is expensive. Latin American crude is heavier, more sour, and requires more refining. African crude is lighter but costs more to ship. Brazilian and Venezuelan supply routes add weeks of transit time compared to the three-to-five-day run from the Gulf. Every extra day at sea is extra cost, extra insurance, extra working capital tied up in floating inventory.

Indian banks are already asking the Reserve Bank of India for hedging cost subsidies to raise dollar funding — a sign that even the financial infrastructure supporting oil imports is under strain.

## What NRIs Should Know

India's oil supply chain is the plumbing that makes everything else work — petrol, diesel, cooking gas, fertiliser feedstock, petrochemicals, plastics, pharmaceuticals. When the plumbing gets rerouted in three months, everything downstream is affected.

For NRIs, the practical implications are:

Remittance value is shifting. The rupee has dropped 4.7 percent against the dollar since the war began. NRI remittances buy more nominal rupees — but the purchasing power of those rupees is being eroded by fuel-driven inflation.

Fuel costs are structural, not temporary. India is paying more for oil that travels farther and costs more to refine. Even if Hormuz reopens tomorrow, the supply chain will take months to normalize. Contracts, shipping schedules, and refinery configurations have all been changed.

Venezuela and Iran are now part of India's energy story. For NRIs in the United States, this creates a complicated overlap between India's energy security and U.S. foreign policy. The Iranian waiver in particular is a diplomatic tightrope that could be revoked at any time.

The 15.5 percent decline in oil imports is not a conservation success story — it is a refining capacity problem. Indian refineries are not choosing to process less oil. They are processing less oil because less oil is available at prices they can afford, through routes that actually work. The downstream effects — from petrol prices to manufacturing costs to job creation in oil-dependent industries — will compound over the coming quarters."""
    article2 = {
        "id": str(uuid.uuid4()),
        "slug": slug2,
        "headline": headline2,
        "subheadline": subheadline2,
        "body": body2,
        "category": "news",
        "vertical": "nri-world",
        "diaspora_angle": "Rupee down 4.7% erodes remittance value. Oil supply disruption structural not temporary — Latin America/Africa routes more expensive, adds weeks. Venezuela + Iran in India's energy mix creates US foreign policy overlap for American NRIs. 15.5% import decline = refinery capacity problem → downstream effects on manufacturing, jobs, prices. Banks asking RBI for hedging subsidies.",
        "tags": ["oil", "hormuz", "venezuela", "brazil", "iran", "russia", "uae", "opec", "crude", "supply chain", "kpler", "refinery", "latin america", "africa", "nri", "rupee"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters — India turns to Latin American, African oil after Hormuz disruption", "url": "https://www.reuters.com/business/energy/india-turns-latin-american-african-oil-after-hormuz-disruption-2026-05-25/"},
            {"name": "Reuters — Oil and LNG tankers exit Hormuz, heading for Pakistan and China", "url": "https://www.reuters.com/business/energy/oil-lng-tankers-exit-hormuz-heading-pakistan-china-2026-05-26/"},
            {"name": "Reuters — Brent crude jumps 4% as US strikes set back hopes for Hormuz re-opening", "url": "https://www.reuters.com/business/energy/brent-crude-jumps-4-us-strikes-iran-set-back-hopes-hormuz-re-opening-2026-05-27/"},
            {"name": "Reuters — Indian banks seek hedging cost subsidy from RBI to raise dollar funding", "url": "https://www.reuters.com/markets/currencies/indian-banks-seek-hedging-cost-subsidy-rbi-raise-dollar-funding-2026-05-26/"},
            {"name": "HSBC — Hormuz uncertainty research note (via Reuters)", "url": "https://www.reuters.com/markets/asia/indian-shares-set-open-higher-oil-drops-mideast-peace-talk-hopes-2026-05-26/"}
        ]),
        "score_total": 90,
        "status": "published",
        "published_at": (now + timedelta(minutes=1)).isoformat().replace('+00:00', 'Z'),
        "image_url": None,
        "image_attribution": None,
    }
    # Image sourcing — Not about a specific person. Try Pexels with specific terms.
    img_url = fetch_pexels_image("oil tanker ship ocean cargo", "crude oil refinery industrial")
    if img_url:
        filename = f"{article2['id']}.jpg"
        final_url = upload_image_to_supabase(img_url, filename)
        article2["image_url"] = final_url
        article2["image_attribution"] = "The Videshi"
    sb_post("p2_articles", article2)
    articles.append(slug2)
    print(f"✓ Published: {headline2}")
else:
    print(f"⊘ Skipped (dedup): Oil supply chain article")

print(f"\nDone. Published {len(articles)} articles: {articles}")

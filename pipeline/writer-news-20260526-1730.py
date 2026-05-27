#!/usr/bin/env python3
"""Videshi Writer — 2 fresh NEWS articles for 2026-05-26 ~17:30 PDT batch
Topics: 1) India's fuel crisis: Four price hikes in 10 days, petrol crosses ₹100, cumulative ₹7.5/litre — state retailers waited for elections to end, OMCs losing ₹600 crore/day, India pivoting oil imports to Latin America/Africa after Hormuz closure
        2) WHO declares Ebola a global health emergency — Bundibugyo strain with no vaccine, 968 suspected cases, India issues travel advisory, Canada imposes travel ban, NRI travel implications
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
# ARTICLE 1: India's Fuel Crisis — Four Price Hikes in 10 Days
# ============================================================
slug1 = make_slug("india-petrol-crosses-100-four-hikes-10-days-hormuz-oil-crisis")
if slug1 not in existing_slugs and not any("petrol" in h and "hike" in h for h in existing_headlines_lower) and not any("fuel" in h and "price" in h for h in existing_headlines_lower):
    headline1 = "Petrol Just Crossed ₹100 Again. India Has Raised Fuel Prices Four Times in Ten Days — and the Hikes Started the Day Elections Ended."
    subheadline1 = "Cumulative increase: ₹7.50 per litre. State oil companies waited until voting was over in key states before passing through the Iran war's crude oil costs. India's oil imports are down 15.5 percent. Venezuela is now the country's fifth-largest oil supplier."
    body1 = """Petrol in Delhi costs ₹102.12 per litre. Diesel costs ₹95.20. If those numbers feel familiar, it is because India crossed the ₹100 mark once before — in 2022. It took four years of subsidized prices to bring it back under control. It took ten days to undo it.

India's three state-owned fuel retailers — Indian Oil Corporation, Bharat Petroleum, and Hindustan Petroleum, which together control 90 percent of the market — have raised petrol and diesel prices four times since May 15. The cumulative hike: ₹7.50 per litre for both fuels.

The timing is not subtle. May 15 was the day after elections ended in several key states. The companies had held prices steady for 76 consecutive days before that, absorbing losses that Indian Oil said reached ₹1,000 crore per day.

## The War That Changed India's Oil Map

The price hikes are a direct consequence of the Iran war, which began on February 28 when Israel and the United States launched operations against Iran. The war shut down the Strait of Hormuz — the 33-kilometre chokepoint through which roughly 20 percent of the world's oil passes.

India, the world's third-largest oil importer and consumer, bought most of its crude from the Middle East until the strait closed. Now, according to shipping data from Kpler reviewed by Reuters, India's oil map has been redrawn.

In April and May, Indian refiners raised imports from Venezuela, Brazil, Angola, and Nigeria to compensate. Venezuela — a country India had barely purchased oil from in recent years — is on course to become India's fourth-largest oil supplier in May, behind Russia, the UAE, and Saudi Arabia.

Iraq, once among India's top three suppliers, has been shut out entirely. India skipped all Iraqi purchases in April because Iraqi exports were halted. Imports from Russia fell 29.4 percent in April to 1.6 million barrels per day after Nayara Energy shut its 400,000-bpd refinery for maintenance.

Overall, India imported 4.57 million barrels per day of crude oil in April — down 15.5 percent from a year earlier.

The only Gulf producers still reliably supplying India are the UAE and Saudi Arabia, which are the only two with pipelines that bypass the Strait of Hormuz entirely. The UAE's share rebounded in April to 669,700 bpd from 230,600 bpd in March. Saudi Arabia held steady at about 619,500 bpd.

## The Austerity Nobody Asked For

The price hikes are accompanied by something India hasn't seen in years: formal austerity measures. New Delhi has introduced fuel consumption curbs and is actively trying to contain its oil import bill. Retail fuel sales have surged — IOC said its diesel retail sales in the first three weeks of May were up 18 percent from a year earlier, and petrol was up 14 percent — partly because bulk customers are switching to cheaper retail pumps, causing shortages in some areas.

Brent crude futures have risen to nearly $100 per barrel. The rupee has slipped against the dollar. Indian bond yields have risen. Foreign portfolio investors have pulled $23.86 billion from Indian equities this year — already surpassing last year's record annual outflows.

The Reserve Bank of India has been intervening to defend the rupee, but the pressure is structural. India imports more than 85 percent of its crude oil. Every dollar increase in the price of Brent crude adds roughly $2 billion to India's annual import bill.

## What It Means for the Diaspora

For NRIs sending money home, the fuel crisis cuts both ways. The weaker rupee means remittances stretch further in nominal terms — but the purchasing power of those rupees is being eroded by the very inflation the fuel hikes are feeding.

Every sector of the Indian economy that touches transportation — which is every sector — is absorbing the impact. Vegetable prices, which are already elevated due to the heatwave, will rise further. School bus operators and delivery fleets will pass costs to consumers. Auto-rickshaw and taxi fares will increase in cities that allow pass-through pricing.

For families in India, a ₹7.50 per litre increase in petrol means roughly ₹375 more per tank for a standard car. For the two-wheeler commuter who fills up twice a week, the monthly cost increase is around ₹600 — not catastrophic in isolation, but cumulative with food inflation, electricity bills, and an economy where white-collar hiring is slowing.

India held fuel prices steady through election season, then raised them four times in ten days once voting ended. The war in the Strait of Hormuz is three months old. The price of the war is now at the pump."""
    article1 = {
        "id": str(uuid.uuid4()),
        "slug": slug1,
        "headline": headline1,
        "subheadline": subheadline1,
        "body": body1,
        "category": "news",
        "vertical": "markets-finance",
        "diaspora_angle": "Weaker rupee boosts nominal remittance value but purchasing power eroded by fuel-driven inflation. Every sector touching transport passes costs to consumers. ₹7.50/litre increase means ~₹375 more per car tank, ~₹600/month more for two-wheeler commuters. FPI outflows of $23.86B this year. Venezuela now India's 5th oil supplier — the energy map that NRI families depended on has been redrawn.",
        "tags": ["petrol", "diesel", "fuel prices", "india", "iran war", "hormuz", "oil", "crude", "rupee", "inflation", "venezuela", "nri", "economy"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters — Indian retailers raise fuel prices a fourth time to rein in losses", "url": "https://www.reuters.com/business/energy/indian-retailers-raise-fuel-prices-fourth-time-amid-iran-war-2026-05-25/"},
            {"name": "Reuters — India turns to Latin American, African oil after Hormuz disruption", "url": "https://www.reuters.com/business/energy/india-turns-latin-american-african-oil-after-hormuz-disruption-2026-05-25/"},
            {"name": "Reuters — Indian shares jump to two-week high as oil drops on Mideast peace talk hopes", "url": "https://www.reuters.com/markets/asia/indian-shares-set-open-higher-oil-drops-mideast-peace-talk-hopes-2026-05-25/"},
            {"name": "Reuters — Rupee slips with Asian peers as hopes of imminent U.S.-Iran peace deal falter", "url": "https://www.reuters.com/markets/currencies/rupee-slips-with-asian-peers-hopes-imminent-us-iran-peace-deal-falter-2026-05-26/"}
        ]),
        "score_total": 90,
        "status": "published",
        "published_at": now_iso,
        "image_url": None,
        "image_attribution": None,
    }
    # Image sourcing — Not about a specific person. Use Pexels with specific terms.
    img_url = fetch_pexels_image("Indian petrol pump fuel station", "fuel station India gasoline")
    if img_url:
        filename = f"{article1['id']}.jpg"
        final_url = upload_image_to_supabase(img_url, filename)
        article1["image_url"] = final_url
        article1["image_attribution"] = "The Videshi"
    sb_post("p2_articles", article1)
    articles.append(slug1)
    print(f"✓ Published: {headline1}")
else:
    print(f"⊘ Skipped (dedup): Fuel price crisis article")

# ============================================================
# ARTICLE 2: WHO Declares Ebola a Global Health Emergency — India Issues Travel Advisory
# ============================================================
slug2 = make_slug("who-ebola-global-emergency-india-travel-advisory-bundibugyo")
if slug2 not in existing_slugs and not any("ebola" in h for h in existing_headlines_lower):
    headline2 = "The WHO Just Declared Ebola a Global Health Emergency. India Has Issued a Travel Advisory. There Is No Vaccine for This Strain."
    subheadline2 = "The Bundibugyo strain spreading through Congo and Uganda has killed at least 216 people. Canada has imposed a travel ban. The United States is screening passengers at Atlanta. India has advised against all non-essential travel to three African countries."
    body2 = """The World Health Organization declared the Ebola outbreak in the Democratic Republic of the Congo and Uganda a Public Health Emergency of International Concern on May 17. It is the highest alarm the WHO can sound. The last time it was triggered for Ebola was during the 2018-2020 outbreak in eastern Congo that killed over 2,200 people.

This outbreak is different. The strain is Bundibugyo — a species of Ebola for which there is no licensed vaccine and no approved treatment. The Zaire strain, which caused the West African epidemic that killed 11,000 people between 2013 and 2016, now has two approved vaccines. Bundibugyo has none.

As of May 23, the outbreak has produced 968 suspected cases and 216 confirmed deaths across the DRC and Uganda. The Africa CDC has declared a Public Health Emergency of Continental Security. Uganda reported three new cases in the most recent reporting period, indicating the virus is crossing borders.

## What India Has Done

India's Ministry of Health issued a formal travel advisory urging citizens to avoid all non-essential travel to the Democratic Republic of the Congo, Uganda, and South Sudan. The advisory was issued within days of the WHO's PHEIC declaration.

India's airport authorities have activated enhanced screening protocols at international entry points, focusing on passengers arriving from or transiting through affected regions. Temperature screening, health declaration forms, and symptom-based triage have been introduced at major airports including Delhi, Mumbai, Bengaluru, and Hyderabad.

India has a relatively small travel footprint to central and eastern Africa, but the concern is transit. Dubai, Doha, and Nairobi — all major hubs for Indian travellers — handle significant traffic from the affected region.

## What Other Countries Have Done

Canada announced an entry ban effective May 30 on all foreign nationals who have been in the affected areas in the past 21 days. Canadian citizens and permanent residents returning from those areas will be required to quarantine for 21 days.

The Bahamas is expected to announce a similar ban. The United States has imposed enhanced screening at Hartsfield-Jackson Atlanta International Airport — the country's busiest — and has separately introduced Ebola-related travel restrictions that apply to green card holders returning from affected countries.

The Trump administration's travel restrictions are broader than the specific Ebola response. Executive orders signed earlier this year had already restricted entry from several African countries. The Ebola overlay adds quarantine requirements to those existing restrictions, creating a layered system that immigration attorneys say is difficult for travellers to navigate.

## Why Bundibugyo Is Different

The Bundibugyo species was first identified in 2007 in the Bundibugyo district of western Uganda. It has a lower fatality rate than the Zaire species — roughly 25 to 30 percent compared to Zaire's 50 to 90 percent — but its lower lethality is precisely what makes it harder to contain.

People infected with Bundibugyo survive longer while symptomatic, which means they can transmit the virus over a wider period and across greater distances. The virus spreads through direct contact with bodily fluids — blood, vomit, sweat, saliva — of symptomatic individuals.

The WHO's Director-General, Tedros Adhanom Ghebreyesus, said the outbreak is "likely to get worse" and that new cases are outpacing first responders' ability to contain them. Health authorities across east and southern Africa have begun border screening at major crossings.

## What NRIs Should Know

For Indians travelling to or through Africa, the immediate guidance is clear: avoid the DRC, Uganda, and South Sudan entirely. For those with travel plans to neighbouring countries — Rwanda, Kenya, Tanzania, Burundi — check with airlines and transit airports for any screening requirements that may cause delays.

For NRIs in the United States, the Trump administration's Ebola-related travel restrictions may interact with existing immigration enforcement in unpredictable ways. Green card holders who have recently travelled to affected countries face additional scrutiny upon re-entry. The 21-day incubation period means that even a brief layover in a hub airport processing traffic from the affected region could trigger secondary screening.

For NRIs in Canada, the 21-day quarantine requirement for citizens and permanent residents returning from affected areas is mandatory and enforceable.

For families in India, the risk level remains low. India has strong experience with Ebola preparedness from the 2014 response, when isolation wards and testing protocols were stood up at short notice. The country has not recorded a single case of Ebola in its history. But a WHO PHEIC means the outbreak has been judged to pose a risk beyond the affected countries, and India's response reflects that assessment.

The Bundibugyo strain has no vaccine. That single fact changes the calculus for every country's response. This is not 2014, when the Zaire strain could be fought with experimental vaccines deployed at scale. This is a different species, and the world is starting from zero."""
    article2 = {
        "id": str(uuid.uuid4()),
        "slug": slug2,
        "headline": headline2,
        "subheadline": subheadline2,
        "body": body2,
        "category": "news",
        "vertical": "nri-world",
        "diaspora_angle": "India travel advisory to DRC, Uganda, South Sudan. NRIs in US face layered travel restrictions from Trump's Ebola orders + existing immigration enforcement. Canada 21-day quarantine for returning residents. Transit through Dubai/Doha/Nairobi hubs could trigger screening. No vaccine exists for Bundibugyo strain — unlike 2014 Zaire response. India itself low risk but airport screening activated.",
        "tags": ["ebola", "who", "global health emergency", "india", "travel advisory", "bundibugyo", "congo", "uganda", "nri", "canada", "immigration"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters — Canada imposes Ebola-related travel ban", "url": "https://www.reuters.com/world/canada-imposes-ebola-related-travel-ban-bahamas-plans-similar-move-2026-05-26/"},
            {"name": "WHO — Ongoing outbreak in the Democratic Republic of the Congo", "url": "https://www.afro.who.int/countries/democratic-republic-of-congo/news/ongoing-outbreak-democratic-republic-congo"},
            {"name": "LatestLY — WHO Declares Ebola Outbreak 'Public Health Emergency' of International Concern; India Advises Against Non-Essential Travel", "url": "https://www.latestly.com/lifestyle/health-wellness/who-declares-ebola-outbreak-public-health-emergency-of-international-concern-india-advises-against-non-essential-travel-to-affected-african-nations-6690050.html"},
            {"name": "India Outbound — India issues travel alert for Uganda, DRC, South Sudan amid Ebola outbreak", "url": "https://www.indiaoutbound.info/india-issues-travel-alert-for-uganda-drc-south-sudan-amid-ebola-outbreak/"}
        ]),
        "score_total": 86,
        "status": "published",
        "published_at": (now + timedelta(minutes=1)).isoformat().replace('+00:00', 'Z'),
        "image_url": None,
        "image_attribution": None,
    }
    # Image sourcing — Not about a specific person. Use Pexels with specific terms.
    img_url = fetch_pexels_image("Ebola health workers protective equipment Africa", "medical health emergency hazmat")
    if img_url:
        filename = f"{article2['id']}.jpg"
        final_url = upload_image_to_supabase(img_url, filename)
        article2["image_url"] = final_url
        article2["image_attribution"] = "The Videshi"
    sb_post("p2_articles", article2)
    articles.append(slug2)
    print(f"✓ Published: {headline2}")
else:
    print(f"⊘ Skipped (dedup): WHO Ebola emergency article")

print(f"\nDone. Published {len(articles)} articles: {articles}")

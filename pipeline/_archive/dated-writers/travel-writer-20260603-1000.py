#!/usr/bin/env python3
"""Travel writer — 2026-06-03 10:00 UTC run. Two articles."""

import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# Load env
env_file = Path.home() / "workspace" / ".env.supabase"
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

now = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

def make_slug(base):
    slug = base.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    return slug[:70].rstrip('-') + "-" + datetime.now().strftime("%Y%m%d")

# ──────────────────────────────────────────────
# Article 1: Sri Lanka Free ETA
# ──────────────────────────────────────────────

art1_body = """Sri Lanka has scrapped visa fees for tourists from 40 countries, including India, in a move that makes the island nation one of the cheapest international getaways within reach of a three-hour flight from Chennai or Bengaluru. The free Electronic Travel Authorization, effective since May 25, removes a $50 processing fee that had quietly nudged the cost of a short Sri Lanka trip into "might as well go to Thailand" territory.

## What Changed — and What Didn't

Under the new policy, citizens of 40 countries — from the United States and United Kingdom to Saudi Arabia, Japan, Germany, and India — can now obtain a 30-day tourist ETA at no charge. The authorization is still required before boarding; what's gone is the fee.

Indian passport holders had already enjoyed a fee waiver under an earlier bilateral arrangement, but the formalization within a 40-country framework signals Colombo's intent to compete seriously for short-haul Asian tourism. The move follows a rocky patch: tourist arrivals in March 2026 fell 22 percent year-on-year, with daily visitor numbers dropping from 7,407 to 6,068, largely due to disrupted flight routes and higher fares caused by Middle East tensions.

Still, India remains Sri Lanka's biggest source market, accounting for 26 percent of all arrivals. The free ETA is designed to keep that pipeline flowing.

## Why NRIs Should Pay Attention

For the Indian American diaspora, Sri Lanka occupies a sweet spot: culturally familiar, geographically close to family in South India, and meaningfully cheaper than Bali or the Maldives. A round-trip from Chennai to Colombo can be had for under $150 on budget carriers, and a week at a beachside guesthouse in Unawatuna or Mirissa costs less than a weekend at a mid-range hotel in Goa during peak season.

The free ETA removes one more logistical hurdle for NRIs visiting family in Tamil Nadu or Kerala who want to tack on a four-day Sri Lanka detour. Sigiriya, Galle Fort, Yala National Park, and the Kandy-Ella railway — widely regarded as one of the most scenic train rides in Asia — are all within a compact enough geography to cover in a long weekend.

NRIs holding American, British, or Canadian passports also benefit directly from the expanded 40-country list. Previously, a US passport holder visiting Sri Lanka needed to pay the full ETA fee even for a brief stopover. That friction is now gone.

## The Fine Print

A few things to keep in mind before booking:

- **ETA is still mandatory.** The fee is waived, not the authorization. Apply online at least 48 hours before departure through Sri Lanka's official Electronic Travel Authorization portal.
- **The stay limit is 30 days.** Extensions are available through Sri Lanka's immigration department, with applicable fees.
- **You need a passport valid for at least six months**, proof of a return or onward flight, and accommodation details (though the itinerary is optional).
- **Payments made before May 25 are not refundable.** If you already paid the $50 fee for a trip this summer, that money is not coming back.

## The Bigger Picture

Sri Lanka's visa play is part of a broader Asian trend. Malaysia has extended its visa-free program for Indians through December 2026. The Philippines offers a two-tier visa-free scheme — 14 days for all Indians, 30 days for those with valid US, UK, Schengen, or Australian visas. Thailand, which briefly went visa-free for Indians in 2024, has settled on visa-on-arrival as the default.

For NRIs, the upshot is simple: a growing list of countries within striking distance of India are actively competing for their travel dollars, and the barriers to a short, spontaneous trip are lower than they have been in years. Sri Lanka, with its proximity, its prices, and its now fee-free entry, may be the most compelling option of the lot.

The first three months of 2026 saw 708,348 visitors to the island — a 4.45 percent increase over the same period last year — suggesting the strategy is working, even as monthly numbers wobble. If the free ETA sticks and air connectivity holds, Colombo's bet on accessibility over exclusivity could pay off handsomely."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Sri Lanka Just Dropped Visa Fees for 40 Countries — NRIs Now Have a Free Pass to the Island",
    "subheadline": "The free ETA, effective since May 25, removes a $50 processing fee and makes Colombo one of the easiest international getaways for a long weekend from South India.",
    "slug": make_slug("sri-lanka-free-eta-40-countries-nri-travel"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "NRIs visiting family in Tamil Nadu or Kerala can now tack on a 4-day Sri Lanka detour with zero visa cost. US, UK, and Canadian passport holders also benefit directly from the expanded free ETA list.",
    "tags": ["travel", "sri-lanka", "visa", "eta", "nri"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/saudi-arabia-joins-united-states-united-kingdom-india-australia-china-and-japan-as-sri-lanka-launches-free-tourist-eta-for-40-countries/"},
        {"name": "Lifestyle Asia", "url": "https://www.lifestyleasia.com/bk/travel/travel-news/sri-lanka-scraps-visa-fee-for-tourists-from-40-countries/"},
        {"name": "Travelobiz", "url": "https://www.travelobiz.com/sri-lanka-plans-free-eta-for-40-countries-as-tourist-arrivals-drop-in-2026/"}
    ]),
    "score_total": 78,
    "status": "published",
    "published_at": now,
    "is_editorial": False,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/e/e6/Sigiriya_%28141688197%29.jpeg",
    "image_attribution": "Wikimedia Commons",
    "body": art1_body.strip()
}

# ──────────────────────────────────────────────
# Article 2: Schengen Visa Landscape for Indians
# ──────────────────────────────────────────────

art2_body = """India filed 1.15 million Schengen visa applications in 2025, making it the third-largest source of European visa demand in the world. For the first time, Switzerland — not France, not Germany — topped the list of destinations Indians applied to visit, with 226,044 applications. The data, released by the European Commission, offers NRIs a practical map of where European doors are opening and where they are quietly closing.

## Switzerland Takes the Crown

The Bollywood effect is real. Decades of Swiss Alps featuring as the backdrop to romantic song sequences — from Yash Chopra's films to more recent productions — have cemented Switzerland's place in the Indian imagination. But the numbers now reflect something more substantive: improved air connectivity, the appeal of scenic rail journeys like the Glacier Express, and a growing luxury and wellness tourism market that India's upper-middle class is eager to access.

Switzerland's non-issuance rate for Indian applicants stands at 13.6 percent — high enough to give pause, but moderate compared to the worst performers. The country processed more applications from Indians in 2025 than in any previous year.

## Where the Odds Are Best

For NRIs planning a European trip and deciding which consulate to apply through, the approval rate data is revealing. Denmark leads with the lowest non-issuance rate at 6.9 percent, followed by Belgium at 7.7 percent, Germany at 10.5 percent, and Italy at 12.7 percent. These are not obscure consulates; they represent real European destinations that Indians want to visit and where the visa process appears to be working relatively smoothly.

The practical implication is significant. If you are planning a multi-country European itinerary, the consulate you apply through matters. A trip that includes Paris, Zurich, and Copenhagen should probably route the visa application through Denmark — your principal destination or not — if the approval numbers give you better odds.

To be clear: approval depends on the individual application, not the consulate alone. Strong documentation, clear travel plans, and evidence of ties to your country of residence still determine outcomes. But the data suggests that some consulates are structurally more generous than others.

## Where to Be Careful

At the other end of the scale, Slovenia, Bulgaria, and Greece recorded the highest rejection rates for Indian applicants in 2025. These are popular with Indian tourists — Greek islands and Bulgarian ski resorts have seen rising interest — but the visa pathway remains narrower.

NRIs holding US green cards or valid US visas sometimes assume they will breeze through the Schengen process. That is not always the case. European consulates evaluate each application independently, and a US immigration status carries no formal weight in Schengen adjudication, though it may be noted as a positive signal of travel history and financial stability.

## The Germany Transit Bonus

Adding to the good news for Indian travelers, Germany officially dropped its airport transit visa requirement for Indian passport holders, effective June 3. This follows France, which had already eliminated the same requirement. The change means Indians connecting through Frankfurt or Munich no longer need to secure a separate transit authorization — a logistical headache that has tripped up diaspora travelers booking multi-leg European flights for years.

The announcement was formalized in Germany's Federal Law Gazette on June 2 and stems from discussions between Prime Minister Modi and Chancellor Friedrich Merz during the latter's visit to India in January 2026.

For NRIs who frequently route through European hubs on the way to India, this removes a real bottleneck. Frankfurt alone handles over 60 million passengers a year, and a significant share of India-bound traffic from North America connects there.

## What NRIs Should Do

India's 1.15 million Schengen applications represent a massive and growing pool of demand. For those in the diaspora still holding Indian passports — and many do, even after years in the United States or Canada — the practical takeaways are straightforward.

Apply early: processing times average 15 days but can stretch to 30. Choose your consulate wisely, using approval rate data as one input alongside your actual travel itinerary. Keep documentation airtight, especially bank statements and employment letters. And if your European trip includes a Frankfurt or Paris layover, scratch the transit visa off your to-do list for good."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "India Filed 1.15 Million Schengen Visa Applications in 2025 — Here's Where NRIs Should (and Shouldn't) Apply",
    "subheadline": "Switzerland is now the top Schengen destination for Indians, but Denmark and Belgium quietly offer the best approval odds — data every NRI planning a Europe trip should know.",
    "slug": make_slug("india-schengen-visa-applications-2025-switzerland-nri"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "Many NRIs still hold Indian passports and need Schengen visas. Approval rate data by country helps them pick the smartest consulate to apply through for multi-country European trips.",
    "tags": ["travel", "schengen", "visa", "europe", "switzerland", "nri"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/switzerland-joins-germany-italy-and-denmark-in-emerging-as-easier-schengen-visa-gateways/"},
        {"name": "Inshorts", "url": "https://inshorts.com/en/news/indians-ranked-third-in-schengen-visa-applications-for-2025"},
        {"name": "IANS", "url": "https://ianslive.in/india-welcomes-germanys-visa-free-transit-for-indian-travellers/"},
        {"name": "European Commission", "url": "https://ec.europa.eu/"}
    ]),
    "score_total": 80,
    "status": "published",
    "published_at": now,
    "is_editorial": False,
    "image_url": "https://images.pexels.com/photos/27981933/pexels-photo-27981933.jpeg",
    "image_attribution": "The Videshi",
    "body": art2_body.strip()
}

# ──────────────────────────────────────────────
# Publish
# ──────────────────────────────────────────────

articles = [art1, art2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

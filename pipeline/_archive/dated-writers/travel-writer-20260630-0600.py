#!/usr/bin/env python3
"""Travel writer – 2026-06-30 batch (2 articles)."""

import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# Load env
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

now = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

def make_slug(base):
    slug = base.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    return slug[:70].rstrip('-') + "-" + datetime.now().strftime("%Y%m%d")

# ──────────────────────────────────────────────
# ARTICLE 1: EVA Air Taipei-Delhi
# ──────────────────────────────────────────────
art1_body = """Taiwan's EVA Air has filed for regulatory approval to launch nonstop flights between Taipei Taoyuan and Delhi's Indira Gandhi International Airport from early December — a move its president framed explicitly as a play for Indian software engineers commuting to Silicon Valley.

EVA Air President Sun Chia-ming announced the route while in Washington, D.C., following the carrier's maiden nonstop to the American capital on Friday. Delhi's "strategic location," he told reporters, makes it an ideal gateway for passengers traveling between South Asia and North America.

## The Taipei Funnel

The arithmetic is straightforward. EVA Air operates 98 weekly round-trip flights to ten North American cities: Houston, Dallas, New York, Los Angeles, Chicago, Seattle, San Francisco, Vancouver, Toronto, and Washington, D.C. Most depart Taipei in the early morning, which means a passenger arriving from Delhi the night before can make a seamless onward connection — often with a transit time shorter than what Cathay Pacific offers through Hong Kong or Singapore Airlines through Changi.

That matters to the roughly 300,000 Indian-born tech workers in the Bay Area and Seattle corridor alone. Today, their options for one-stop India travel run through the Gulf carriers, Cathay, and Singapore Airlines. EVA is betting it can undercut them on both price and elapsed journey time by routing through a smaller, faster hub.

Sun said the Delhi service would "strengthen EVA Air's ability to compete with Cathay Pacific and Singapore Airlines in the growing North America to South Asia transit market." North America already generates 40 per cent of EVA's passenger revenue and about 70 per cent of its cargo revenue — but with Taiwan's domestic population at 23 million, the airline needs international transit passengers to keep growing.

## Transit Numbers Back the Bet

Taipei Taoyuan Airport handled 6.69 million transit passengers in 2025, up sharply from 5.32 million in 2019. In the first five months of 2026, transit traffic was already 3.29 million — a 51 per cent increase over the same period in 2019. Transit passengers now account for 15.2 per cent of all traffic through the airport, up from 10.7 per cent pre-pandemic.

For NRIs flying between the West Coast and North India, the Delhi-Taipei routing could offer a meaningfully different proposition: a modern 787 on a relatively short hop to Taipei, a quick connection, and then EVA's well-regarded service across the Pacific. The carrier currently holds a 4-Star Skytrax rating and consistently ranks among the world's top 10 airlines for service quality.

## What NRIs Should Watch

The route is subject to regulatory approval from both India's Directorate General of Civil Aviation and Taiwan's Civil Aeronautics Administration. Frequency and aircraft type have not been disclosed, though EVA's long-haul fleet consists primarily of Boeing 787-9s, 787-10s, and 777-300ERs — all widebodies with competitive premium cabins.

If approved, the December launch would give NRIs planning winter trips to India a new routing option — one that avoids the Gulf entirely and offers a hub where connections to San Francisco, Seattle, and Los Angeles are measured in minutes, not hours.

EVA also expects its cargo business to keep growing, noting that AI-related shipments currently generate 40 to 50 per cent of its cargo revenue. The airline plans to expand its dedicated cargo fleet from nine to twelve aircraft by 2028."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "EVA Air Wants to Fly Taipei to Delhi by December — and It's Coming for Silicon Valley's NRI Engineers",
    "subheadline": "The Taiwanese carrier is betting that a quick connection through Taipei can lure Indian tech workers away from Gulf and Southeast Asian hubs on the India-to-America run.",
    "slug": make_slug("eva-air-taipei-delhi-silicon-valley-nri-transit"),
    "category": "travel",
    "vertical": "airlines",
    "diaspora_angle": "EVA Air is explicitly targeting Indian software engineers in Silicon Valley with a Taipei-Delhi nonstop that connects to 10 North American cities — a new one-stop alternative to Gulf and Southeast Asian carriers for NRIs flying between the US West Coast and North India.",
    "tags": ["travel", "airlines", "eva-air", "delhi", "silicon-valley", "nri"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Aviation A2Z", "url": "https://aviationa2z.com/index.php/2026/06/29/eva-air-to-launch-direct-delhi-flights-eyes-indias-growing-north-america-transit-market/"},
        {"name": "Focus Taiwan", "url": "https://focustaiwan.tw"},
        {"name": "IANS via India News Stream", "url": "https://ianslive.in"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/0/08/20240107_Boeing_787-10_of_EVA_Air_%28B-17813%29_at_SHA_01.jpg",
    "image_caption": "An EVA Air Boeing 787-10 at Shanghai Hongqiao Airport",
    "image_attribution": "Wikimedia Commons",
    "body": art1_body.strip(),
}

# ──────────────────────────────────────────────
# ARTICLE 2: India-UK Trade Deal Mobility
# ──────────────────────────────────────────────
art2_body = """India's most comprehensive free trade agreement to date takes effect on July 15 — and buried in the tariff schedules is a provision that will directly reshape how tens of thousands of Indian professionals move between Delhi and London.

Under the India-UK Comprehensive Economic and Trade Agreement, Indian workers on temporary assignments in Britain will be exempt from paying UK social security contributions for up to five years. The provision, known as the Double Contribution Convention, means an Indian IT consultant posted to London will no longer pay simultaneously into both India's and Britain's social security systems. The government estimates that roughly 75,000 Indian professionals and more than 900 Indian companies operating in the UK will benefit.

## The Money Math

Social security contributions in the UK can run upward of 13.8 per cent of an employee's salary on the employer side alone. For Indian IT firms that deploy thousands of engineers on client sites in London, Manchester, and Edinburgh, the five-year exemption — extended from the three years India originally secured — is a material reduction in deployment costs. Industry analysts say 90 to 95 per cent of Indian professionals sent to Britain by Indian companies will qualify.

Commerce Minister Piyush Goyal, speaking at UK-India Week in London on June 27, called it "the most comprehensive agreement that India has entered into so far." The deal eliminates import duties on 99 per cent of Indian exports to the UK, but for the Indian diaspora in Britain, the mobility chapter matters more than any tariff line.

## Who Gets to Move More Easily

The trade agreement locks in and, in some sectors, expands the existing business mobility framework between the two countries. Professionals covered include:

- **Contractual service suppliers** — Indian firms can deploy staff to deliver contracted services in the UK
- **Intra-corporate transferees** — employees moving within the same multinational, with partners and dependent children receiving the right to work
- **Business visitors** — short-term travel for meetings, conferences, and commercial discussions
- **Independent professionals** — a category that specifically names yoga instructors, musicians, and chefs alongside engineers and accountants

No new visa routes have been created. The UK government has stressed that its points-based immigration system remains unchanged. But the deal guarantees that existing access will not be rolled back — a hedge that matters in an era of tightening immigration politics.

## What It Means for NRIs

For the 1.5 million people of Indian origin living in the UK, the deal arrives at a moment when the India-UK corridor is already humming. Air India, Vistara (before its merger), and British Airways together operate dozens of weekly flights between London, Delhi, Mumbai, Bengaluru, and Hyderabad. The German transit visa waiver — which took effect on June 3 — has already made connecting through Frankfurt and Munich easier for Indians.

The social security exemption lowers the cost of doing business across the corridor, which should mean more Indian professionals on UK assignments, more business travel between the two countries, and — eventually — more demand on the already-busy London-India air routes.

For NRIs in the US who also do business in the UK, the deal is worth watching as a template. India is simultaneously negotiating trade agreements with the EU and Australia, and a bilateral trade agreement with the United States is in its final stretch. The mobility provisions India has secured with the UK — particularly the social security exemption and the explicit protection of intra-corporate transfers — will likely set the floor for what Delhi demands in every subsequent deal.

The India-UK FTA and the Double Contribution Convention take effect simultaneously on July 15. Indian companies should ensure their HR and payroll teams are ready for the transition."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "India's Trade Deal With Britain Takes Effect July 15 — and 75,000 NRIs Stand to Save on Every UK Posting",
    "subheadline": "A five-year social security exemption, expanded professional mobility, and duty-free access for 99 per cent of Indian exports — the India-UK FTA is the most sweeping deal Delhi has signed.",
    "slug": make_slug("india-uk-trade-deal-july-mobility-social-security-nri"),
    "category": "travel",
    "vertical": "immigration",
    "diaspora_angle": "The India-UK FTA's social security exemption directly benefits 75,000 Indian professionals in Britain — mostly IT workers — by eliminating dual contributions for up to five years, lowering the cost of UK postings for Indian companies and their employees.",
    "tags": ["travel", "uk", "india", "trade-deal", "visa", "mobility", "nri"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com"},
        {"name": "The Indian Eye", "url": "https://theindianeye.com"},
        {"name": "PRNewswire / India Global Forum", "url": "https://www.prnewswire.com"},
        {"name": "GOV.UK", "url": "https://www.gov.uk/government/publications/uk-india-free-trade-agreement-business-mobility-explainer"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6d/Heathrow_Airport_Terminal_5.jpg/1280px-Heathrow_Airport_Terminal_5.jpg",
    "image_caption": "Heathrow Airport Terminal 5 in London, a major hub for India-UK air traffic",
    "image_attribution": "Wikimedia Commons",
    "body": art2_body.strip(),
}

# ──────────────────────────────────────────────
# Insert articles
# ──────────────────────────────────────────────
articles = [art1, art2]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['headline'][:80]}...")
        print(f"   slug: {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"   Response: {e.response.text[:300]}")

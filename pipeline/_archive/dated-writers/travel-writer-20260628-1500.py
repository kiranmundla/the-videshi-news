#!/usr/bin/env python3
"""Videshi Travel Writer — 2026-06-28 15:00 PT run"""

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


# ─── ARTICLE 1: Thailand Visa Downgrade ───────────────────────────────

art1_body = """Thailand's Cabinet dropped a policy bomb on May 19 that most Indian travellers still haven't absorbed. Under a sweeping "one country, one visa privilege" overhaul, India has been removed from Thailand's visa-free list entirely and reclassified into a four-country Visa on Arrival bracket alongside Azerbaijan, Belarus, and Serbia. The old 60-day visa-free window — which had made Bangkok the most-searched international destination for Indian passport holders — is gone.

The new terms: 15 days on arrival, single entry, THB 2,000 (roughly ₹4,600–₹5,800) in cash at the immigration counter. No extension. No re-entry privilege. If your trip exceeds two weeks, you need a pre-approved Tourist Visa from a Thai consulate before you board.

## What Triggered the Reversal

The generous 60-day regime, introduced in July 2024 as a post-pandemic tourism boost, applied to 93 countries. Thailand's security agencies flagged it within months. Briefings to Bangkok's Cabinet linked the extended window to a spike in drug trafficking networks, human-trafficking rings operating under tourist cover, and foreigners running illegal businesses while ostensibly on holiday.

"Work under the tourist radar" was the phrase officials used. The Cabinet's response was blunt: scrap the 93-country scheme, replace it with a tiered system of 30-day visa-free access for 54 countries, and push a handful of nationalities — India prominently among them — into the restricted VoA lane.

The countries that kept 30-day or longer access? Europe, North America, Japan, South Korea, and ASEAN neighbours. The hierarchy is clear: regional partners and high-spending Western tourists sit in one tier; everyone else, including India, sits below.

## Why This Hits NRIs Harder Than It Looks

For the Indian American diaspora, Thailand is not just a holiday destination. It's the default layover break on India trips routed through Bangkok. It's the honeymoon add-on booked alongside two weeks in Kerala. It's the family reunion halfway point when relatives can't get US visas.

A 15-day VoA sounds adequate for a standard Bangkok-Pattaya-Phuket circuit. And for a pure beach holiday, it probably is — most packaged trips clock in at five to seven nights. But the change bites in less obvious places:

- **Visa-run expats** who used Thailand as a reset button for India or US stays now face a cash-only, single-entry, non-extendable stamp.
- **Digital nomads and remote workers** who wintered in Chiang Mai on the 60-day window have lost their cushion entirely.
- **Wedding and conference travellers** whose itineraries stretch past two weeks must now apply at a Thai consulate weeks in advance — a meaningful hassle for NRIs juggling US work schedules.

## What You Need at the Counter

If you're entering Thailand on VoA after the new rules take effect, here's the checklist:

1. **Passport valid for at least six months** from date of entry
2. **THB 2,000 in cash** (Thai Baht only — no cards, no dollars)
3. **Return or onward ticket** within 15 days
4. **Confirmed hotel booking** for at least the first night
5. **Proof of funds**: THB 10,000 per person or THB 20,000 per family (immigration may ask)
6. **One passport-sized photo** (some counters still require it)

The VoA queue at Suvarnabhumi and Don Mueang can run 45 minutes to two hours during peak arrival windows. Budget accordingly.

## The Bigger Picture for Indian Passport Holders

India's Ministry of External Affairs has been quietly — and genuinely — working to improve the passport's global standing. The Henley Index shows steady progress: 30-plus visa-free destinations, up from a dismal 25 a few years ago. But Thailand's move is a reminder that progress is fragile. Bilateral warmth at the diplomatic level doesn't automatically translate into immigration privilege. Host nations make these calls on domestic security terms, and India's passport still sits near the bottom of global mobility rankings.

For NRIs holding US passports or green cards, the impact is nil — American citizens keep 30-day visa-free access to Thailand. But for family members travelling on Indian passports, especially elderly parents joining a holiday, the new VoA adds friction, cost, and a layer of anxiety at the immigration counter that didn't exist six weeks ago.

The practical advice: if Thailand is on your 2026 itinerary and your trip exceeds 10 days, apply for a Tourist Visa through the Thai consulate in advance. The e-Visa system is functional, if slow. And carry the THB 2,000 in cash even if you've pre-booked everything electronically — immigration officers have wide discretion at the VoA counter, and being turned away at Suvarnabhumi is not how anyone wants to start a holiday."""


art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Thailand Just Kicked India Off Its Visa-Free List — Here's What Every NRI Traveller Needs to Know",
    "subheadline": "India is now one of only four countries requiring a Visa on Arrival in Thailand, with just 15 days and a THB 2,000 fee replacing the old 60-day free entry.",
    "slug": make_slug("thailand-visa-downgrade-india-voa-nri-travel"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "NRIs who add Thailand stopovers to India trips, plan family reunions in Bangkok, or use the 60-day window for extended stays now face a 15-day cap, cash fees, and consulate paperwork — hitting elderly parents on Indian passports hardest.",
    "tags": ["travel", "visa", "thailand", "indian-passport", "nri"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "VisaHQ", "url": "https://www.visahq.com/"},
        {"name": "ThaiLawOnline", "url": "https://thailawonline.com/thailand-tourist-visa-guide-2026/"},
        {"name": "DocuPro", "url": "https://docupro.in/"},
        {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/88/Suvarnabhumi_Airport_Terminal_E_interior_at_dusk.jpg/1280px-Suvarnabhumi_Airport_Terminal_E_interior_at_dusk.jpg",
    "image_caption": "Suvarnabhumi Airport terminal interior in Bangkok, where Indian travellers now face Visa on Arrival queues",
    "image_attribution": "Wikimedia Commons",
    "body": art1_body.strip()
}


# ─── ARTICLE 2: Riyadh Air + Air India Partnership ───────────────────

art2_body = """Riyadh Air, Saudi Arabia's newest national carrier backed by the kingdom's sovereign wealth fund, launches its first commercial flights to London Heathrow on July 1. But the airline's ambitions extend well beyond Britain. An MoU signed with Air India in June positions India as the centrepiece of Riyadh Air's global network — and gives the Indian diaspora a new corridor between South Asia, the Gulf, and Europe that didn't exist a year ago.

The deal, announced jointly by Air India CEO Campbell Wilson and Riyadh Air CEO Tony Douglas, lays the groundwork for codeshare agreements, coordinated scheduling, and reciprocal frequent-flyer benefits across both airlines' networks. Douglas called India "one of the most important and dynamic aviation markets in the world." Wilson framed it as unlocking "complementary strengths" — Air India's 25 codeshare partnerships and 120-plus interline agreements feeding into Riyadh Air's brand-new fleet.

## Five Indian Cities, Nonstop from Riyadh

Riyadh Air has confirmed direct services to Delhi, Mumbai, Bengaluru, Hyderabad, and Chennai from its hub at King Khalid International Airport. The airline plans to deploy Airbus A321neo aircraft on these 3.5-to-5-hour routes, with wider fleet plans that include 60 A321neos, 25 Airbus A350-1000s, and 39 Boeing 787-9 Dreamliners on order.

The inclusion of Bengaluru and Chennai is strategically significant. Both cities are currently underserved on the Riyadh corridor — no carrier offers high-frequency nonstop service from either city to the Saudi capital. For the estimated 2.6 million Indians living and working in Saudi Arabia, many of whom hail from Karnataka, Tamil Nadu, and Telangana, these routes plug a real gap.

## Why NRIs Should Pay Attention

The India-Gulf-Europe routing has long been dominated by Emirates (via Dubai), Qatar Airways (via Doha), and Etihad (via Abu Dhabi). Riyadh Air's entry creates a fourth competitive axis: India to Riyadh, then onward to London, and eventually to further European and North American destinations as the network expands.

For NRIs in the US and UK, this matters in three concrete ways:

**Lower fares on the India leg.** More capacity on India-Gulf routes means more competition. Air India's own Gulf services have been running at 30–40% below pre-conflict seat counts this summer, partly due to airspace restrictions and fuel costs. Riyadh Air's fresh capacity — backed by a sovereign wealth fund with no legacy cost burdens — could push fares down on routes where Indian carriers are pulling back.

**A credible premium product.** Riyadh Air is positioning itself as a full-service, design-forward carrier. Its 787 Dreamliners feature lie-flat business class, and Tony Douglas (formerly of Etihad) has built the airline's service model around the Gulf premium standard. For NRIs accustomed to choosing between Air India's improving-but-still-uneven product and the established Gulf Three, a fourth option with new aircraft and competitive pricing is welcome.

**The London connection.** Riyadh Air's July 1 London Heathrow launch creates an immediate India-Riyadh-London pathway. Indian passengers connecting through Riyadh can use Air India's domestic network to reach the capital, then fly Riyadh Air onward. For the estimated 1.6 million British Indians who travel to India regularly, and for the NRIs in the US who route through London, this is another card in the hand.

## Flyadeal Targets the Other End of the Market

While Riyadh Air chases premium travellers, its low-cost sibling is making a parallel play. Flyadeal, a subsidiary of Saudia, has confirmed plans to launch services to up to six Indian cities — including Mumbai, Delhi, and Jaipur — from hubs in Jeddah, Riyadh, and Dammam. The airline operates 42 Airbus A320-family aircraft and has 10 wide-body A330neos on order for delivery from mid-2027.

Flyadeal's CEO, Steven Greenway, has described India as one of the "most hyper-competitive markets" in the world, signalling aggressive pricing to win market share. The airline is also exploring a codeshare with an Indian domestic carrier — which would allow passengers from smaller Indian cities to book a single ticket through to Saudi Arabia, eliminating the self-connection through Mumbai or Delhi that most travellers currently endure.

For the blue-collar Indian workforce in Saudi Arabia — construction workers, healthcare staff, hospitality employees — Flyadeal's budget positioning could meaningfully reduce the cost of trips home. And for NRI families sending relatives to Umrah or Hajj, a low-cost Jeddah connection from tier-2 Indian cities is a practical improvement.

## The Bigger Competitive Picture

Saudi Arabia's aviation push is part of Vision 2030, the kingdom's plan to diversify beyond oil. The target: 330 million passengers annually by 2030, up from roughly 100 million today. India, with its 1.4 billion people, growing middle class, and massive Gulf-based workforce, is the single most important feeder market for that ambition.

For Indian travellers and the diaspora, the arithmetic is simple: more airlines competing on India-Gulf routes means more seats, better prices, and — eventually — better service. Air India's partnership with Riyadh Air is an acknowledgement that the competitive map is shifting, and that India's flag carrier would rather be inside the tent than watching from outside it."""


art2 = {
    "id": str(uuid.uuid4()),
    "headline": "Riyadh Air Launches This Week — and Its India Play Could Reshape How NRIs Fly to the Gulf",
    "subheadline": "Saudi Arabia's new national carrier has signed a partnership with Air India and plans nonstop flights to five Indian cities, creating a fresh India-Riyadh-London corridor.",
    "slug": make_slug("riyadh-air-launch-air-india-mou-nri-gulf-corridor"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "NRIs gain a fourth Gulf routing option for India trips, with Riyadh Air's premium product and Air India codeshare creating competitive pressure on the India-Gulf-Europe corridor that could push fares down.",
    "tags": ["travel", "airlines", "riyadh-air", "air-india", "gulf", "saudi-arabia", "nri"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Travel Trade Journal", "url": "https://www.traveltradejournal.com/"},
        {"name": "Wego Travel Blog", "url": "https://blog.wego.com/flyadeal-riyadh-air-india-routes-2026/"},
        {"name": "Air India Newsroom", "url": "https://www.airindia.com/in/en/newsroom/press-release/Air-India-rationalises-international-route-network-through-August-2026.html"},
        {"name": "TravelBiz Monitor", "url": "https://www.travelbizmonitor.com/"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4f/Riyadh_Air_Boeing_787_at_Dubai_Airshow_2023.jpg/1280px-Riyadh_Air_Boeing_787_at_Dubai_Airshow_2023.jpg",
    "image_caption": "A Riyadh Air Boeing 787 Dreamliner on display at the Dubai Airshow",
    "image_attribution": "Wikimedia Commons",
    "body": art2_body.strip()
}


# ─── INSERT ───────────────────────────────────────────────────────────

articles = [art1, art2]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

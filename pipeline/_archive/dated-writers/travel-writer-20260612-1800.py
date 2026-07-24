#!/usr/bin/env python3
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

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Saudi Arabia's Newest Budget Airline Just Picked Hyderabad as Its First Indian Destination",
        "subheadline": "Flyadeal launches daily nonstop Riyadh-Hyderabad service on July 1, with an Indian-origin CEO and plans for more Indian cities. For NRIs routing through the Gulf, a new low-cost option just entered the game.",
        "slug": make_slug("flyadeal-riyadh-hyderabad-daily-nonstop-nri"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "Hyderabad is a gateway city for Telugu diaspora — the largest Indian-American community after Gujaratis. A budget Riyadh-Hyderabad link offers cheaper connections through the Gulf for NRIs flying home, and a direct lifeline for the 2M+ Indian workers in Saudi Arabia.",
        "tags": ["travel", "airlines", "saudi-arabia", "hyderabad", "flyadeal"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Travel and Tour World", "url": "https://www.travelandtourworld.com/news/article/saudi-arabia-flyadeal-launches-riyadh-hyderabad-flights/"},
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/economy/logistics/air-india-to-launch-hub-and-spoke-international-connectivity-flights-from-june-25/article69660973.ece"}
        ]),
        "score_total": 72,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/2958530/pexels-photo-2958530.jpeg",
        "image_caption": "An airport terminal at sunset with parked aircraft on the tarmac",
        "image_attribution": "Pexels",
        "body": """Flyadeal, Saudi Arabia's low-cost carrier and a subsidiary of the Saudia Group, will begin daily nonstop flights between Riyadh and Hyderabad on July 1 — its first-ever scheduled service to India.

The airline will deploy Airbus A320neo aircraft configured with 186 all-economy seats on the route, positioning itself squarely against the Gulf's established budget carriers on one of the most heavily trafficked corridors between India and the Middle East.

## Why Hyderabad, and Why Now

Hyderabad was not a random pick. The city generates enormous two-way traffic with the Gulf states, driven by a combination of migrant workers, IT professionals on project rotations, and family visits. Rajiv Gandhi International Airport handled over 25 million passengers last year, and a disproportionate share of its international traffic flows to and from Saudi Arabia, the UAE, and Qatar.

Flyadeal's acting CEO, Sanjiv Kapoor — a veteran Indian aviation executive who previously led Vistara and Jet Airways — has signalled that India will anchor the airline's international expansion. A second Indian destination is expected to be announced within months.

"India will play a key role in Flyadeal's long-term growth plans," Kapoor said, in a statement that reads less like a press release and more like a market-entry declaration.

## What This Means for NRIs

For the estimated 2.4 million Indian nationals living and working in Saudi Arabia, the new route offers something straightforward: a daily budget option on a corridor that has long been dominated by full-service fares. Until now, flying Riyadh to Hyderabad meant booking Air India, IndiGo (via connecting hubs), or Saudia's mainline service — all at prices that could spike during Eid, Diwali, and summer holiday windows.

Flyadeal's entry injects low-cost competition into the mix. The A320neo's fuel efficiency keeps operating costs down, and the airline's Saudi backing gives it staying power that smaller Gulf budget carriers have historically lacked.

For Indian Americans — particularly the large Telugu diaspora concentrated in the New York–New Jersey corridor, the Bay Area, and Dallas — the knock-on effect matters too. Many NRIs routing through Gulf hubs like Riyadh, Jeddah, or Dubai to reach Hyderabad now have a cheaper final leg to consider, especially when connecting on Saudia codeshares.

## The Bigger Gulf-India Picture

Flyadeal's move comes during a broader push by Gulf carriers to deepen their India footprint. Riyadh Air, the Saudi sovereign wealth fund's brand-new premium carrier, made its maiden flight to London last week and has openly discussed Indian routes. Air Arabia, flydubai, and Jazeera Airways continue to add Indian cities.

India is now the world's third-largest aviation market by domestic passenger volume, and Gulf carriers see its 1.4 billion people — including a massive diaspora across the Middle East — as a growth engine that will outlast the oil economy.

For NRIs, the practical takeaway is simple: more airlines competing on India-Gulf routes means lower fares, more schedule options, and fewer excuses to delay that trip home. The budget era on the Riyadh-Hyderabad corridor starts July 1."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Your US Visa Unlocks 30+ Countries Visa-Free — and Most NRIs Don't Use It",
        "subheadline": "Indian passport holders with a valid US visa can skip the embassy line for Mexico, Colombia, the Caribbean, the Balkans, and more. With the World Cup in full swing and Europe looking expensive, here's the cheat sheet.",
        "slug": make_slug("us-visa-visa-free-countries-nri-travel-guide"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "Every Indian American has a US visa or green card — but few realize it doubles as a travel pass to 30+ countries. With Modi urging Indians to skip Europe and the World Cup pulling fans to Mexico, this is the most practical guide for NRI summer travel.",
        "tags": ["travel", "visa", "nri", "mexico", "caribbean", "world-cup"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Wikipedia - Visa Requirements for Indian Citizens", "url": "https://en.wikipedia.org/wiki/Visa_requirements_for_Indian_citizens"},
            {"name": "Marble Law - Green Card Holder Travel Guide", "url": "https://marble.co/resources/articles/where-green-card-holders-can-travel-visa-free"},
            {"name": "Atlys - Countries with US Visa Access", "url": "https://www.atlys.com/post/countries-you-can-visit-with-a-us-visa-on-an-indian-passport"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/20210498/pexels-photo-20210498.jpeg",
        "image_caption": "Aerial view of Cancún's beachfront resorts and turquoise Caribbean waters",
        "image_attribution": "Pexels",
        "body": """If you hold a valid US visa — B1/B2, H-1B, L-1, or even an expired stamp with valid I-94 status — you are carrying a second passport that most Indians never fully use. Over 30 countries waive their visa requirements entirely for Indian passport holders who can show a valid American visa, and the list includes some of the best summer destinations on the planet.

With FIFA World Cup matches drawing crowds to Mexico and Canada, European airfares sitting at punishing levels thanks to the Hormuz crisis, and Prime Minister Modi's appeal still ringing in ears, this is the summer to actually use that US visa stamp for what it's quietly worth.

## The Americas: Your Backyard, Visa-Free

**Mexico** is the headliner. Indian citizens with a valid US multiple-entry visa can enter for up to 180 days — no Mexican visa, no appointment, no fee beyond the standard FMM form (usually bundled into your airline ticket). With World Cup matches kicking off in Mexico City, Guadalajara, and Monterrey, this is immediately relevant. Cancún, Tulum, and Oaxaca are all accessible without a single embassy visit.

**Colombia** allows visa-free entry for up to 90 days. Bogotá and Cartagena have become popular with Indian travelers who discover them during US-based layovers. **Peru** offers 180 days — enough to do Machu Picchu properly. **Costa Rica** grants 90 days. **Panama**, 30 days. **Chile and Argentina** are also on the list.

In the Caribbean, the **Bahamas, Dominican Republic, Belize, Aruba, Curaçao, Cayman Islands, and Bermuda** all accept Indian passport holders with valid US visas. For NRI families in the Northeast, a long weekend in the Bahamas or Dominican Republic requires nothing more than your passport, US visa, and a direct flight from Miami or JFK.

## Beyond the Western Hemisphere

The US visa trick works in some unexpected places. **Singapore** grants visa-free transit and short stays for Indians with valid US visas — useful for NRIs routing through Changi on their way to India. **South Korea** offers similar transit privileges.

In Europe's backyard, the **Balkans** have opened wide. **Albania, Serbia, Montenegro, North Macedonia, and Georgia** all waive visas for Indians with US stamps. Georgia is particularly generous — up to one full year. Serbia and Albania offer 90 days each. These are not obscure destinations: Tbilisi's food scene rivals Lisbon's, Dubrovnik-adjacent Montenegro costs a fraction of Croatia, and Tirana is one of Europe's best-kept secrets.

**Turkey** offers e-visas with simplified processing for US visa holders. Several Gulf states — **Bahrain, Oman, Saudi Arabia, and the UAE** — grant visa-on-arrival to Indians with valid US visas.

## The Fine Print

A few rules apply universally. Your US visa must be valid (not expired) and, in most cases, must have been used at least once — meaning you need to have entered the US before using the visa for third-country travel. Some countries require a multiple-entry visa specifically. Always carry a return ticket, proof of accommodation, and sufficient funds.

Green card holders get an even broader set of privileges, but the principles are the same: your US immigration document is doing double duty as a travel credential.

## The NRI Calculation

Indian Americans collectively hold millions of active US visas. Yet the default vacation playbook — India in winter, Europe in summer — persists out of habit rather than necessity. This summer, with European flights running 40-60% above pre-crisis levels, the math points elsewhere.

A week in Cancún costs less than three days in Barcelona. A Bogotá-Cartagena loop is cheaper than a weekend in London. And none of it requires a consulate appointment, a Schengen application, or a six-week wait.

The US visa in your passport is not just permission to enter America. It is a key to a surprisingly large chunk of the world — and this is the summer to turn it."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Vietjet Now Connects Five Indian Cities to Vietnam — and NRIs Should Pay Attention",
        "subheadline": "Direct flights from Delhi, Mumbai, Ahmedabad, Hyderabad, and Bengaluru to Hanoi and Ho Chi Minh City are making Vietnam the most accessible Southeast Asian destination for Indian travelers. Here's why it matters for diaspora families.",
        "slug": make_slug("vietjet-five-indian-cities-vietnam-nri-family"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "Vietnam is emerging as the easiest and cheapest add-on trip for NRIs visiting India. With direct flights from 5 cities, e-visa access, and prices that undercut Thailand and Bali, it's the short-haul escape NRI families should be booking mid-trip.",
        "tags": ["travel", "airlines", "vietnam", "vietjet", "southeast-asia"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Travel and Tour World", "url": "https://www.travelandtourworld.com/news/article/vietjet-india-vietnam-connectivity/"},
            {"name": "Skift", "url": "https://skift.com/2026/05/20/modi-india-middle-class-stay-home-foreign-travel/"}
        ]),
        "score_total": 70,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/35883685/pexels-photo-35883685.jpeg",
        "image_caption": "Boats on the turquoise waters of Ha Long Bay surrounded by limestone karst islands",
        "image_attribution": "Pexels",
        "body": """Vietnam has been quietly climbing the charts as India's fastest-growing outbound tourism destination, and the infrastructure just caught up with the demand. Vietjet, Vietnam's largest low-cost carrier, now operates direct flights from five major Indian cities — Delhi, Mumbai, Ahmedabad, Hyderabad, and Bengaluru — to Hanoi and Ho Chi Minh City, making it the most connected Southeast Asian destination from India outside of Thailand and Singapore.

The expansion comes at a moment when Indian arrivals in Vietnam surged nearly 49% year-on-year in 2025, according to Vietnam's tourism authority data cited by Skift. That growth rate outpaced every other major source market for Vietnam, including China and South Korea.

## Five Cities, Two Hubs, No Visa Hassle

The route map tells the story. From Delhi, Mumbai, and Bengaluru — India's three largest international gateways — Vietjet flies nonstop to both Hanoi and Ho Chi Minh City. Ahmedabad and Hyderabad, both fast-growing international airports, connect to at least one Vietnamese hub.

For Indian passport holders, Vietnam offers an e-visa that takes roughly three business days to process online and costs $25. No embassy appointment, no paper application, no sponsor letter. The e-visa is valid for 90 days with multiple entries — generous enough to cover a two-week holiday or even a remote-work stint.

Compare that to Thailand (which just went visa-free for Indians but capped stays at 60 days), Bali (visa-on-arrival with limited extensions), or Japan (which still requires a full embassy application). Vietnam's combination of easy entry and direct flights from five Indian cities is hard to beat.

## Why NRIs Should Care

Here is the angle most travel articles miss: Vietnam is not just a destination for India-based travelers. It is rapidly becoming the smartest add-on trip for NRIs visiting India.

Consider the math. An NRI family flying from the US to India for a summer visit typically spends two to three weeks between family obligations, weddings, and temple visits. By the second week, the parents want a break. The kids are restless. Everyone has eaten enough biryani to last until Thanksgiving.

A four-night side trip to Vietnam — Ha Long Bay, Hoi An's lantern-lit old town, Ho Chi Minh City's street food scene — costs roughly $600-800 per person including flights and hotels, departing from whichever Indian city the family happens to be in. That is less than a domestic flight to Ladakh during peak season, with better weather certainty and zero altitude sickness.

Vietjet's fares from Indian cities to Vietnam start as low as ₹5,000-8,000 one way during promotional windows. Even at regular pricing, a round trip rarely crosses ₹20,000 — a fraction of what a Southeast Asian trip costs when booked from the US.

## The Vietnam Advantage Over Thailand and Bali

Thailand has been the default Southeast Asian escape for Indian travelers for years, but Vietnam is gaining ground for several reasons.

First, it is cheaper. Hotel rates in Hanoi and Ho Chi Minh City run 30-40% below Bangkok. Street food — already legendary — costs a fraction of Thai equivalents. A proper phở breakfast costs less than a dollar.

Second, it is less crowded with Indian tourists, which paradoxically makes it more appealing for the kind of NRI traveler who wants discovery rather than the well-trodden Bangkok-Phuket-Pattaya circuit.

Third, the cultural depth rivals India's own. The Mekong Delta, the imperial city of Hue, the cave systems of Phong Nha — these are not beach-and-bar destinations. They reward the kind of curious, historically minded traveler that the Indian diaspora produces in abundance.

## The Practical Upshot

Vietnam's government has invested heavily in tourism infrastructure, and it shows. Da Nang's international airport handles direct flights from across Asia. High-speed rail projects are underway. New resort developments along the central coast are targeting the premium segment without the Maldives price tag.

For NRI families planning their next India trip, the play is straightforward: book your US-India flights as usual, then add a Vietjet segment from Delhi, Mumbai, or Bengaluru to Hanoi or Ho Chi Minh City. Apply for the e-visa online before you leave the US. Pack light for four nights. Come back to India rested, with photos that will outperform anything from Shimla on Instagram.

Vietnam is no longer a niche destination for backpackers. For the Indian diaspora, it is the most accessible international escape hiding in plain sight — and five direct flight corridors just made it impossible to ignore."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

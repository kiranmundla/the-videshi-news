#!/usr/bin/env python3
"""Travel writer — 2026-06-08 14:00 UTC batch."""

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
    # ── Article 1: Delta-IndiGo Partnership ──
    {
        "id": str(uuid.uuid4()),
        "headline": "Delta Is Coming Back to India — and This Time It's Riding IndiGo's Network",
        "subheadline": "A new four-airline mega-partnership between IndiGo, Delta, Air France-KLM, and Virgin Atlantic will link 30+ Indian cities to dozens of destinations across North America and Europe — with Delta eyeing a nonstop Atlanta-Delhi service.",
        "slug": make_slug("delta-indigo-partnership-atlanta-delhi-nri"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "For the 400,000+ Indian Americans in the US Southeast — Atlanta, Charlotte, Nashville, Raleigh — this partnership could deliver the first nonstop US-carrier link to India in years. Delta's Atlanta hub is the world's busiest airport, and a direct Delhi route would eliminate the Gulf-carrier layovers that add 6-10 hours to every trip home.",
        "tags": ["travel", "airlines", "delta", "indigo", "codeshare", "nri"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "The Indian Eye", "url": "https://theindianeye.com/2025/06/02/delta-air-lines-returns-to-india-with-indigo-led-global-partnership/"},
            {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/corporate/indigo-bets-big-on-international-growth-targets-200-mn-passengers-by-fy30"},
            {"name": "Drift Travel", "url": "https://drifttravel.com/partnership-for-flights-to-india-from-north-america-and-europe/"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/37540293/pexels-photo-37540293.jpeg",
        "image_caption": "Airplanes on the tarmac at Delhi's Indira Gandhi International Airport",
        "image_attribution": "Pexels",
        "body": """Delta Air Lines has not flown its own metal to India since 2015, when it quietly dropped its Amsterdam-routed connections and ceded the market to Gulf carriers and Air India. For a decade, Indian Americans in Delta's sprawling US network — particularly those based in the Southeast — have been stuck routing through Dubai, Doha, or Abu Dhabi to get home.

That era appears to be ending. IndiGo, Delta, Air France-KLM, and Virgin Atlantic have announced a sweeping four-airline partnership that will link India's largest domestic network with three of the West's most powerful long-haul carriers. The deal is built around IndiGo's rapidly expanding international operations and Delta's stated intention to resume nonstop US-India service, with Atlanta to Delhi as the flagship route.

## What the Partnership Actually Does

The mechanics matter more than the press release. Once regulatory approvals clear and IndiGo begins selling partner flights under its own 6E marketing codes, an IndiGo customer booking a ticket from, say, Ahmedabad or Kochi will be able to connect seamlessly onto Delta flights across the Atlantic, KLM flights within Europe, or Virgin Atlantic services from the UK.

The reverse works too. A Delta customer in Atlanta, Detroit, or Minneapolis will eventually be able to book a single ticket through to 30+ Indian cities via IndiGo's domestic web. Right now, Air France and KLM already sell IndiGo connections beyond their Indian gateways — the Delta addition dramatically expands the North American side of the map.

IndiGo CEO Pieter Elbers framed it as a step toward making the airline "a global carrier by 2030." Delta CEO Ed Bastian was more direct: "We look forward to restarting Delta's direct service from the U.S. to India in the near future."

## Why Atlanta-Delhi Changes Everything

Delta's hub in Atlanta is the world's busiest airport by passenger traffic, processing over 100 million travelers a year. It's also the gateway for Indian communities across the US South — a region that has seen explosive growth in the Indian American population over the past decade. Cities like Atlanta, Charlotte, Raleigh-Durham, Nashville, and Tampa have all seen their desi populations surge, driven by tech hiring, healthcare, and the expansion of corporate offices.

Yet the South remains stubbornly underserved for India flights. There are no nonstop India routes from any Southeastern US airport. Every trip requires a connection through JFK, Newark, San Francisco, or a Gulf hub — adding hours, layovers, and cost.

A Delta nonstop from Atlanta to Delhi would cut travel time to roughly 16 hours, comparable to the JFK-Delhi corridor. For families dragging luggage and children through connecting airports twice a year, that is a material quality-of-life improvement.

## IndiGo's Expanding Long-Haul Fleet Makes It Possible

The partnership wouldn't work without IndiGo's aggressive push into long-haul flying. The airline currently operates six damp-leased Boeing 787 Dreamliners on European routes, and has firm orders for 30 Airbus A350-900 widebody jets — with options for 70 more. Nine Airbus A321XLR deliveries are expected this fiscal year, unlocking routes to Athens, Istanbul, Bali, and Seoul.

International capacity is projected to reach 40 percent of IndiGo's total by 2030, up from a fraction of that just two years ago. The airline carried 123 million passengers in FY26 and is targeting 200 million by FY30.

For NRIs, this transformation means the airline they've always used for ₹3,000 Bangalore-to-Goa hops is now building the infrastructure to carry them from Athens to Amritsar on a single booking.

## What NRIs Should Watch For

The partnership is still in MoU stage. Regulatory approvals from both US and Indian aviation authorities are required before codeshare tickets go on sale. Delta has not announced a launch date for Atlanta-Delhi, and the service is "subject to government approval."

But the direction is unmistakable. With Air India under Tata's aggressive expansion, IndiGo building a widebody fleet, and now Delta re-entering the market, Indian Americans are about to have more options for flying home than at any point in aviation history. The days of Emirates and Qatar Airways as the default choice are numbered — and for NRIs in the American South, that shift cannot come soon enough."""
    },

    # ── Article 2: IndiGo FY30 Widebody Ambitions ──
    {
        "id": str(uuid.uuid4()),
        "headline": "IndiGo Wants to Fly You From Delhi to Bali on a Widebody — and It's Not Joking",
        "subheadline": "India's largest airline just unveiled a FY30 roadmap that includes 200 million passengers, A350 widebodies, nine new A321XLR jets this year, and a premium product that would have been unthinkable five years ago. For NRIs who've always seen IndiGo as a domestic shuttle, the airline is asking for a rethink.",
        "slug": make_slug("indigo-fy30-widebody-a350-a321xlr-nri"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "NRIs have long treated IndiGo as the reliable-but-basic airline for domestic Indian connections. That mental model is about to break. With A350 widebodies and A321XLR jets, IndiGo is positioning itself to compete directly on routes NRIs actually fly — Delhi to London, Mumbai to Athens, and eventually long-haul to North America. The premium IndiGoStretch product and loyalty integration with Delta/AF-KLM means the airline wants your international ticket, not just your ₹3,000 Bangalore hop.",
        "tags": ["travel", "airlines", "indigo", "widebody", "a350", "a321xlr", "premium"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/corporate/indigo-bets-big-on-international-growth-targets-200-mn-passengers-by-fy30"},
            {"name": "Ainvest", "url": "https://www.ainvest.com/news/indigo-441-aircraft-as-of-march-31-901-yet-to-be-delivered/"},
            {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/dvhieign497b/"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b8/VT-IUV_IndiGo_Airbus_A321-271NX_9396_VGHS.jpg/1280px-VT-IUV_IndiGo_Airbus_A321-271NX_9396_VGHS.jpg",
        "image_caption": "An IndiGo Airbus A321neo at the airport — the airline's workhorse as it pushes into long-haul flying",
        "image_attribution": "Wikimedia Commons",
        "body": """There is a particular kind of cognitive dissonance that hits you when IndiGo — the airline of 28-inch seat pitch, no free water, and boarding announcements in three languages — tells investors it plans to fly widebody jets to three continents. And yet, at its Analyst Day 2026 presentation last week, that is precisely what India's largest airline laid out.

The numbers are ambitious even by Indian aviation's historically optimistic standards: 200 million passengers by FY30, up from 123 million in FY26. Daily departures rising from 2,200 to 3,000. A fleet expanding past 550 aircraft. And the headline figure — international capacity reaching 40 percent of the airline's total output, up from a small fraction just two years ago.

## The Hardware That Makes It Real

IndiGo's international pivot rests on two aircraft types that represent a fundamental departure from the A320neo fleet that built the airline.

The first is the Airbus A321XLR, the ultra-long-range variant of the narrowbody workhorse. IndiGo expects nine deliveries this fiscal year. These jets can fly roughly 8-9 hours nonstop, which opens up destinations like Athens, Istanbul, Bali, and Seoul — cities that sit just beyond the range of a standard A321neo. IndiGo has already launched service to Athens with the XLR, featuring 195 seats with a new IndiGoStretch premium cabin, in-seat power, and wireless entertainment streaming.

The second is the Airbus A350-900, a proper twin-aisle widebody. IndiGo has 30 on firm order with options for 70 more, and deliveries are expected to begin in 2027. These are the aircraft that could theoretically put IndiGo on routes like Delhi-New York or Mumbai-San Francisco — territory that has belonged exclusively to Air India, United, and the Gulf carriers.

## Cutting Routes While Planning New Ones

The tension at the heart of IndiGo's strategy is visible right now. Even as it unveils a FY30 vision of global dominance, the airline has suspended six Southeast Asian routes — Hong Kong, Shanghai, Ho Chi Minh City, Langkawi, Krabi, and Siem Reap — for the July-September period, citing weak demand and high costs. It has also killed its Manchester route after just 14 months.

IndiGo frames this as disciplined capital allocation: pulling back from routes that don't work to preserve resources for routes that will. The airline ended FY26 with a free cash balance of ₹362 billion, and management has emphasized that growth will remain "financially disciplined."

For observers, though, the pattern raises a question: if IndiGo can't sustain a Boeing 787 route to Manchester — a city with one of the UK's largest Indian communities — how will it fill an A350 to New York?

## What It Means for the Diaspora

The NRI relationship with IndiGo has always been transactional. You land in Delhi on Air India or Emirates, clear customs, then book a ₹3,000 IndiGo flight to Lucknow or Coimbatore. The airline was the reliable domestic connector, never the one carrying you across an ocean.

That is changing. IndiGo now flies to London, Amsterdam, Copenhagen, and Athens on its own branding (via damp-leased 787s and its own XLRs). Its partnership with Delta, Air France-KLM, and Virgin Atlantic means an IndiGo booking can now connect you to dozens of North American and European cities.

The IndiGoStretch product — with 4,300 daily premium seats projected by March 2027 — signals that the airline is chasing higher-yield passengers, not just volume. The BluChip loyalty program has crossed 11 million members and is being positioned as a cross-airline currency.

## The Competitive Landscape

IndiGo's push comes at a moment when competition for the NRI traveler has never been fiercer. Air India, under Tata, is merging with Vistara and rebuilding its widebody fleet with new A350s and 787s. Emirates and Qatar remain formidable on price and service. United has expanded its India network. Delta is planning to re-enter with an Atlanta-Delhi nonstop.

IndiGo's bet is that scale, price, and network breadth can overcome its service reputation. With 441 aircraft, 901 more on order, and a domestic market share above 60 percent, no airline has more leverage over India's aviation infrastructure.

Whether it can translate that into a compelling international product — one that NRIs would choose over a lie-flat Emirates seat — remains the open question. But dismissing the ambition would be a mistake. Five years ago, IndiGo flying to Athens would have been a punchline. Today, it's a scheduled service."""
    },

    # ── Article 3: Monsoon Slow Travel ──
    {
        "id": str(uuid.uuid4()),
        "headline": "The Monsoon Just Hit Kerala — and NRIs Who Book Now Will Pay Half What They Would in December",
        "subheadline": "India's southwest monsoon arrived on June 4, kicking off the country's most underrated travel season. For Indian Americans planning a summer trip home, the math is compelling: lower airfares, empty hotels, Ayurveda at a fraction of peak cost, and landscapes that look nothing like the dusty India of March.",
        "slug": make_slug("monsoon-india-travel-nri-kerala-slow-season"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "Most NRIs default to December-January for India trips — school breaks, weddings, pleasant weather. But that's also when flight prices peak ($1,200-1,800 round trip), hotels charge full rack rates, and tourist sites are shoulder-to-shoulder. Monsoon season flips the equation: flights drop 30-40%, luxury resorts offer deep discounts, and iconic destinations like Kerala, Coorg, and Rajasthan reveal an entirely different face. For NRIs with flexible summer schedules — remote workers, academics, retirees — June through August is the smartest travel window that almost nobody uses.",
        "tags": ["travel", "monsoon", "kerala", "slow-travel", "nri", "india"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/world/india/indian-monsoon-reaches-kerala-three-days-later-than-usual-2026-06-04/"},
            {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/dvhieign497b/"},
            {"name": "Ainvest", "url": "https://www.ainvest.com/news/indias-monsoon-2026-kerala-karnataka-goa-expect-heavy-rainfall/"}
        ]),
        "score_total": 75,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/31852050/pexels-photo-31852050.jpeg",
        "image_caption": "A canoe glides through the lush backwaters of Alappuzha, Kerala during monsoon season",
        "image_attribution": "Pexels",
        "body": """The southwest monsoon made landfall in Kerala on June 4 — three days later than the textbook date of June 1 — and is now advancing steadily northward across Karnataka, Goa, and the western coast. The India Meteorological Department has flagged this as a potentially El Niño-weakened season, with total rainfall projected to be the lowest in 11 years.

For most Indians, that's concerning news — agriculture depends on these rains. But for NRIs thinking about a summer trip home, the forecast actually works in your favor: lighter-than-usual rainfall means fewer flight disruptions, less flooding, and more manageable travel conditions, while still delivering the lush green landscapes and cool temperatures that make monsoon India a different country from the one you visit in December.

## The Economics of Off-Season India

The price differential between December and monsoon travel to India is stark. Round-trip fares on the SFO-Delhi corridor that hit $1,500-1,800 during the winter wedding season drop to $800-1,100 in June and July. Hotels that charge ₹15,000 a night in peak season offer the same rooms for ₹6,000-8,000. Ayurveda retreats in Kerala — where monsoon is traditionally considered the ideal season for treatment, as humidity opens pores and enhances oil absorption — run at 40-50 percent below their October-March rates.

This isn't a lesser version of an India trip. It's a fundamentally different one. And for NRIs with the flexibility to travel outside the December-January window — remote workers, academics on summer break, retirees, or families with young children not yet locked into school calendars — it may be the better one.

## Five Destinations That Peak in the Rain

**Kerala backwaters, Alleppey and Kumarakom.** The monsoon transforms the backwaters from a pleasant boat ride into a cinematic experience — overcast skies, rain drumming on houseboat roofs, paddy fields luminous green. Cochin International Airport is 85 km from Alleppey. A three-night houseboat package that costs ₹45,000 in December drops to ₹20,000-25,000 in July.

**Coorg (Kodagu), Karnataka.** Coffee plantations at their most fragrant, waterfalls at full power, and plantation homestays that serve filter coffee and pork curry with a view of mist rolling through the valleys. Mangalore Airport is 150 km away, and the drive through the Western Ghats in monsoon is half the reason to go. Estate bungalows that charge ₹8,000 in season drop to ₹4,000-5,000.

**Chikmagalur, Karnataka.** Adjacent to Coorg but less touristed, Chikmagalur sits at the foothills of the Mullayanagiri range. The monsoon months of June and July turn the coffee hills into a deep green blanket. Agritourism homestays let you watch the coffee cultivation process between rain showers. Budget ₹3,000-5,000 per night.

**Udaipur, Rajasthan.** Most people associate Rajasthan with dry heat, but monsoon Udaipur is something else entirely — Lake Pichola fills to the brim, the Aravalli hills turn green, and the city's famous rooftop restaurants serve meals against a backdrop of dramatic storm clouds. Heritage hotels drop rates by 30-40 percent, and the crowds that choke the City Palace in winter are gone.

**Lonavala and Mahabaleshwar, Maharashtra.** The Western Ghats hill stations closest to Mumbai undergo a complete transformation during monsoon — seasonal waterfalls appear, the Sahyadri range vanishes into cloud, and the entire landscape turns emerald. Located 90 km from Mumbai Airport, these are the closest monsoon getaways for NRIs landing in the city. Weekend packages run ₹5,000-10,000 for two nights, a fraction of peak rates.

## Practical Considerations

Monsoon travel in India requires a different packing list and a different mindset. Waterproof bags, quick-dry clothing, and insect repellent are non-negotiable. Road conditions in hilly areas can deteriorate — the Coorg and Chikmagalur ghat roads occasionally see landslides, and it's worth checking local conditions before driving.

Domestic flights within India are generally reliable during monsoon, though delays of 30-60 minutes are common at Mumbai and Kochi airports. The smart play is to build buffer days into your itinerary rather than scheduling tight connections.

The IMD's El Niño forecast adds a wrinkle this year. A weaker monsoon means drier conditions overall, which could mean less dramatic waterfalls but also fewer travel disruptions. For a first-time monsoon visitor, that's arguably the ideal setup — enough rain to see the green, not enough to strand you.

## The Bottom Line

December India is the India that NRIs know: weddings, relatives, temple visits, and $1,500 flights. Monsoon India is the one they're missing — empty roads, transformed landscapes, Ayurveda at half price, and the particular magic of watching rain hit a Kerala backwater from a houseboat with nowhere to be. The monsoon has arrived. The window is open through August. And for NRIs willing to break the December habit, the math has never been better."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

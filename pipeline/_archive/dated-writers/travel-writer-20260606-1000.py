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
        "headline": "A Delhi Hotel Fire Killed 21 People — and NRIs Should Think Twice About Where They Book",
        "subheadline": "The Malviya Nagar blaze exposed what many long-time India travelers already know: budget hotels near major hospitals routinely flout fire safety rules, and the consequences can be fatal.",
        "slug": make_slug("delhi-hotel-fire-nri-safety-budget-stays"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "NRIs visiting India frequently book budget hotels and B&Bs near hospitals when accompanying elderly relatives for medical care. The Malviya Nagar fire exposed systemic safety violations in these establishments — operating 25 rooms on a 6-room license, jammed electronic locks, no visible fire exits. Diaspora travelers need to know how to vet accommodations before booking.",
        "tags": ["travel", "delhi", "hotel-safety", "nri", "india"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/world/india/delhi-crack-down-fire-safety-violations-after-blaze-that-killed-21-2026-06-04/"},
            {"name": "Livemint", "url": "https://www.livemint.com/news/india/malviya-nagar-fire-incident-flourish-stay-bnb-25-rooms-6-room-license-11780570000000.html"},
            {"name": "Dainik Jagran English", "url": "https://english.dainikjagranmpcg.com/national/delhi-hotel-fire-kills-21-17-foreign-nationals-among-dead"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/29568751/pexels-photo-29568751.jpeg",
        "image_caption": "An emergency exit sign above a closed door — the kind of basic safety feature missing from many budget Indian hotels",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": """On the morning of June 3, a fire ripped through the Flourish Stay B&B in Delhi's Malviya Nagar, killing 21 people and injuring dozens more. The five-storey building — wedged into a narrow lane in the Hauz Rani neighbourhood — was engulfed in smoke within minutes, trapping guests on upper floors as electronic door locks jammed and stairwells filled with toxic fumes.

Among the dead were 17 foreign nationals, mostly from Bangladesh and African countries, along with eight members of a Gurugram family who had been staying at the hotel while visiting an ailing relative at the nearby Max Hospital.

For NRIs who routinely fly to India to accompany aging parents to medical appointments, the details are chilling — and familiar.

## What Went Wrong at Flourish Stay

The preliminary investigation has painted a damning picture. The Flourish Stay B&B held a license for six rooms but was operating 25. The building had no fire NOC — the mandatory no-objection certificate from Delhi Fire Services. Emergency exits were either absent or inaccessible. Electronic locks on room doors malfunctioned during the blaze, trapping guests inside. The narrow lane outside complicated fire tender access, delaying rescue by critical minutes.

The fire began in the ground-floor Lemon Green restaurant around 8:30 AM, when breakfast was being served to more than 60 people. Flames raced upward through the building, and within minutes, the upper floors were smoke-locked.

Delhi Police have filed an FIR under culpable homicide charges and issued a lookout circular for co-owner Lovkesh Bajaj, who fled after the incident. Delhi's chief minister has ordered a city-wide crackdown on guest houses and hotels violating fire safety norms.

## A Pattern NRIs Should Recognise

The Malviya Nagar fire is not an isolated incident. India's budget hospitality sector — the sprawling ecosystem of guest houses, B&Bs, and small hotels clustered around hospitals, railway stations, and pilgrimage sites — has long operated with minimal oversight.

A 2024 audit by Delhi Fire Services found that fewer than 40 percent of hotels in the capital held valid fire safety certificates. Across India, the compliance rate is thought to be even lower. The problem is structural: municipal bodies issue business licenses without cross-checking fire clearances, and enforcement is reactive rather than preventive.

For NRIs, the risk is particularly acute. Medical tourism trips — where family members fly from the US to Delhi, Mumbai, or Chennai to accompany relatives through surgeries or extended treatments — often involve booking the cheapest available accommodation within walking distance of a hospital. These are precisely the establishments most likely to cut corners on safety.

## What NRIs Should Do Before Booking

The Delhi government's crackdown will likely produce a wave of sealed properties and prosecutions in the coming weeks. But systemic change takes years. In the meantime, diaspora travelers can take practical steps to protect themselves.

**Check for fire safety certification.** Any hotel or guest house in India is required to hold a fire NOC from the local fire department. Ask for it at check-in. If the front desk cannot produce one, leave. No amount of convenience justifies the risk.

**Avoid buildings with a single narrow staircase.** The Flourish Stay had one way in and one way out. Look for properties with at least two independent exit routes and external fire escapes. In older urban neighbourhoods, this often means choosing a standalone building over one squeezed into a commercial lane.

**Book through platforms with safety verification.** Major hotel aggregators like OYO, MakeMyTrip, and Booking.com have begun requiring fire safety documentation from listed properties, though enforcement is inconsistent. Branded hotel chains — even budget ones like Ginger or Lemon Tree — maintain centralised safety standards that independent operators do not.

**Carry a portable smoke detector.** They cost under $15 on Amazon and can be placed on a nightstand. It is a small investment for a trip where you may be sleeping in an unfamiliar building with unknown wiring and ventilation.

**Know the hospital accommodation options.** Most major hospitals in Delhi, Mumbai, and Bengaluru offer patient-attendant rooms or have formal tie-ups with nearby hotels that meet safety standards. Ask the hospital's international patient services desk before booking independently.

## The Bigger Picture

India handled roughly 20 million international tourist arrivals last year, and a significant share of those are diaspora visitors returning for family, medical, or religious reasons. The country's airport network has doubled to over 150 facilities in a decade, and the government is spending billions on tourism infrastructure.

But the gap between India's aviation ambitions and its ground-level hospitality safety standards remains wide. The Malviya Nagar fire is a stark reminder that getting to India has never been easier — but once you land, the basics still matter more than the boarding pass."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "IndiGo Has Quietly Overtaken Air India in the Fight for India's International Skies",
        "subheadline": "DGCA data shows IndiGo led the Air India group on international routes in three of the first four months of 2026 — a reversal from last year that has everything to do with the Iran War and the future of how NRIs fly home.",
        "slug": make_slug("indigo-overtakes-air-india-international-routes-nri"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "For millions of NRIs booking annual trips to India, the IndiGo-Air India rivalry directly affects route availability, pricing, and service quality on key corridors like JFK-DEL, SFO-BOM, and ORD-HYD. IndiGo's international growth and Air India's struggles under war-driven cost pressure could reshape the competitive landscape on diaspora routes within two years.",
        "tags": ["travel", "airlines", "indigo", "air-india", "nri"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Livemint", "url": "https://www.livemint.com/companies/indigo-air-india-international-routes-west-asia-war-aviation-dgca-11780548641184.html"},
            {"name": "Reuters", "url": "https://www.reuters.com/business/aerospace-defense/indias-indigo-cuts-six-international-routes-amid-rising-costs-airspace-restrictions-2026-06-05/"},
            {"name": "Aviation A2Z", "url": "https://www.aviationa2z.com/indigo-cancels-flights-to-these-6-international-destinations/"}
        ]),
        "score_total": 76,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/0/06/IndiGo_VT-IJB_A320neo_Mumbai_Apr22_R16_05934.jpg",
        "image_caption": "An IndiGo Airbus A320neo at Mumbai airport — the airline now leads Air India in international passenger numbers",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": """For decades, flying between the United States and India meant flying Air India. The Maharaja was the default, the only carrier that offered nonstop service on the routes that mattered to the diaspora — Newark to Delhi, JFK to Mumbai, SFO to Bengaluru. IndiGo, India's largest domestic carrier, was the airline you took after you landed.

That division is eroding faster than most NRIs realise.

## The Numbers Tell the Story

Directorate General of Civil Aviation data released in late May shows that IndiGo carried 0.87 million international passengers in April 2026, edging past the Air India group's 0.85 million. IndiGo operated 5,607 international departures during the month — 385 more than Air India and Air India Express combined.

This was not a one-off. IndiGo has led Air India on international routes in three of the first four months of 2026. The only exception was March, when Air India briefly regained the lead after IndiGo scaled back some Middle East operations.

The reversal is striking because Air India held a clear lead for the full calendar year of 2025, with 17.21 million international passengers against IndiGo's 16.46 million. The shift happened rapidly, driven by a combination of geopolitics, cost structures, and network strategy.

## Why Air India Is Bleeding

The Iran War, which escalated in late February, has hit Indian aviation hard — but Air India disproportionately so. Airspace restrictions over West Asia and Pakistan's continued ban on Indian overflights have forced long-haul carriers to reroute, adding hours of flying time and thousands of crores in fuel costs.

Air India, whose international network is built around wide-body, long-haul flights to North America, Europe, and Australia, has borne the heaviest burden. The airline's additional operating costs from rerouting are estimated at Rs 4,000-5,000 crore. Its international departures fell 23 percent year-on-year in April. Air India Express, which operates heavily on Gulf routes, slashed international departures by 68 percent.

The Tata-owned carrier is now expected to report nearly $3 billion in losses for FY26. Its ambitious transformation plan — new aircraft deliveries, cabin refurbishments, service upgrades — is running headlong into a geopolitical headwind it cannot control.

IndiGo, by contrast, reported a loss of Rs 2,394 crore for FY26 but kept its international network relatively stable. The airline operates primarily short-haul international services, connecting Indian cities to Southeast Asia, Central Asia, and the Gulf, and feeds traffic to partners like Qatar Airways and Turkish Airlines for long-haul connections.

## What This Means for NRI Travellers

The IndiGo-Air India rivalry has direct implications for the 4.5 million Indian Americans who fly between the US and India each year.

**Air India remains the only Indian carrier with nonstop US-India service.** Its routes from Newark, JFK, SFO, Chicago, and Washington to Delhi, Mumbai, and Bengaluru are irreplaceable for travellers who prioritise direct flights. But the quality and frequency of that service is under pressure. Air India cut 22 percent of domestic flights in June and July and has reduced several international routes.

**IndiGo is building a connecting alternative.** The airline's growing international network — now exceeding 1,800 weekly flights — means NRIs can increasingly fly IndiGo from a Gulf or Southeast Asian hub to their hometown in India, often at significantly lower fares than Air India's direct service. For travellers headed to tier-2 Indian cities that Air India does not serve nonstop from the US, IndiGo's one-stop connections via Doha, Dubai, or Singapore are already competitive.

**Competition is keeping fares from going even higher.** IATA has warned that global airfares will rise 8-12 percent this summer due to the conflict. But on India routes, the IndiGo-Air India rivalry — combined with Emirates, Qatar Airways, and United — means NRIs have more options than travellers to most other South Asian destinations.

## The Road Ahead

IndiGo's ambition is not modest. The airline's management has stated a target of increasing international capacity from 28 percent of total available seat kilometres to 40 percent by FY30. If it succeeds, IndiGo will transform from a domestic giant with international ambitions into a genuinely global carrier.

Air India, meanwhile, is betting on its fleet renewal — over 400 new aircraft on order from Airbus and Boeing — to emerge from the current crisis as a fundamentally different airline. The merger with Vistara and Air India Express is designed to create a full-service carrier that can compete on every segment.

For NRIs, the best outcome is both airlines thriving. More carriers, more routes, and more competition on the corridors that connect the diaspora to home. The worst outcome would be one faltering badly enough to cede routes — because on India-US flights, there is no surplus capacity to absorb the loss."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Bengaluru to Mangaluru by Vande Bharat: India's 13th Semi-High-Speed Route in Karnataka Begins Trials",
        "subheadline": "The completion of electrification on the mountainous Sakleshpur-Kukke Subramanya stretch has unlocked a route that Kannadiga NRIs have wanted for years — a fast, comfortable train from India's tech capital to the Konkan coast.",
        "slug": make_slug("bengaluru-mangaluru-vande-bharat-trial-run-karnataka"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "Bengaluru is home to India's largest concentration of tech companies and a major origin point for US-bound NRIs. Mangaluru and the Konkan coast are ancestral home territory for hundreds of thousands of Kannadiga, Konkani, and Tulu-speaking diaspora families. A fast Bengaluru-Mangaluru train means NRIs flying into Kempegowda International Airport can reach the coast without a grueling 8-hour bus ride or booking a separate domestic flight.",
        "tags": ["travel", "vande-bharat", "karnataka", "trains", "india", "bengaluru", "mangaluru"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Pingara.com", "url": "https://pingara.com/vande-bharat-train-trial-run-to-begin-from-june-3/"},
            {"name": "The Indian Eye", "url": "https://theindianeye.com/20-coach-vande-bharat-train-starts-jammu-srinagar-service-amid-rising-demand-ashwini-vaishnaw/"},
            {"name": "HelloRail", "url": "https://hellorail.in/category/vande-bharat/"}
        ]),
        "score_total": 72,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/5/5a/Vande_Bharat_Express_around_Mumbai.jpg",
        "image_caption": "A Vande Bharat Express train — Karnataka's 13th such service will connect Bengaluru to Mangaluru",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": """For anyone who has endured the Bengaluru-Mangaluru bus journey — eight hours on winding Western Ghat roads, often through monsoon rain and landslide diversions — the news that a Vande Bharat Express trial run has begun on this route lands with genuine relief.

Union Minister of State for Railways V. Somanna confirmed on June 1 that the trial run of the Bengaluru-Mangaluru Vande Bharat Express would commence on June 3, following the completion of electrification on the 55-kilometre Sakleshpur-Kukke Subramanya stretch. Full commercial service is expected to begin within 15 to 20 days.

This will be Karnataka's 13th Vande Bharat service and the first to connect the state capital to the Konkan coast by semi-high-speed rail.

## Why This Route Matters

The Bengaluru-Mangaluru corridor is one of the most travelled in South India, linking the country's tech capital to a coastal city that serves as the gateway to the Konkan belt — a region stretching from Goa through Karnataka's coast that is home to Konkani, Tulu, and Kannada-speaking communities with deep diaspora roots in the US, the Gulf, and the UK.

For decades, the only practical options were an overnight bus, a 90-minute flight on a turboprop, or a painfully slow conventional train that took upwards of 10 hours due to the mountainous terrain and single-track sections through the Western Ghats. The corridor's geography — steep gradients, tight curves, and over 50 tunnels — made it one of the last major routes in Karnataka to receive electrification.

The Vande Bharat Express is expected to cut the journey time to roughly five hours, running at speeds that the existing infrastructure can sustain safely while offering the air-conditioned comfort, onboard catering, and punctuality that the service has become known for.

## The Electrification Breakthrough

The route's transformation was bottlenecked by a single technical challenge: electrifying the Sakleshpur-Kukke Subramanya section, a stretch that passes through some of the most rugged terrain in the Western Ghats. Dense forests, steep gradients, and the logistical challenge of stringing overhead electrical equipment through tunnels and across mountain bridges slowed the project for years.

Somanna confirmed that 99 percent of Karnataka's rail network is now electrified, with only marginal work remaining. The completion of this final stretch was the result of multiple rounds of intervention between the railway ministry and Southern Railway officials.

The electrification is significant beyond the Vande Bharat service. It allows Indian Railways to deploy electric locomotives across the entire Bengaluru-Mangaluru section, reducing fuel costs, emissions, and transit times for freight and conventional passenger services alike.

## What NRIs Should Know

For diaspora travellers, the Bengaluru-Mangaluru Vande Bharat fills a gap that has frustrated trip planning for years.

**Reaching ancestral towns gets simpler.** NRIs flying into Bengaluru's Kempegowda International Airport from the US — currently served by nonstop flights from SFO and connecting flights from most major US cities — will be able to reach Mangaluru without booking a separate domestic flight or enduring a bus journey that eats an entire day. From Mangaluru, local transport to towns like Udupi, Kasaragod, Kundapura, and Karwar is straightforward.

**Monsoon travel becomes viable.** The Bengaluru-Mangaluru highway is notoriously dangerous during the June-September monsoon, with landslides regularly closing the Shiradi and Charmadi Ghat sections. The rail route, while not immune to weather disruptions, is significantly more reliable and safer during heavy rains. For NRIs planning summer India trips — which often coincide with monsoon season — the train is a material upgrade in safety.

**Comfort matters on family trips.** Vande Bharat coaches feature reclining seats, onboard WiFi, charging points at every seat, and a pantry car — a far cry from the cramped Rajahamsas and KSRTC Airavats that have served this route for decades. For NRI families travelling with elderly parents or young children, the difference is substantial.

## Karnataka's Rail Moment

The Bengaluru-Mangaluru Vande Bharat is part of a broader expansion. Karnataka now operates 12 Vande Bharat services connecting the state capital to Dharwad, Mysuru, Hubballi, Goa, Chennai, and other destinations. Five Amrit Bharat trains also run in the state, offering a budget-tier semi-high-speed option.

Nationally, the Vande Bharat programme has become one of Indian Railways' most visible modernisation efforts. The Jammu-Srinagar Vande Bharat, launched in late April, carried over one lakh passengers in its first 22 days — a sign of pent-up demand for fast, comfortable rail travel in regions where roads are unreliable. Indian Railways is also developing a standard-gauge version of the Vande Bharat for export to international markets.

For Kannadiga NRIs who grew up making the Bengaluru-Mangaluru journey by bus — and who still dread it — the Vande Bharat will not just be a train. It will be the end of a very long wait."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

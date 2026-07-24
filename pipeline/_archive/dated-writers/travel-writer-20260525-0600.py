#!/usr/bin/env python3
"""Videshi Travel Writer — 2026-05-25 batch"""
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
    # ── Article 1: Kashmir Vande Bharat ──────────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "Kashmir by Rail: The Jammu-Srinagar Vande Bharat Crossed 100,000 Passengers in Just 22 Days",
        "subheadline": "At ₹730 a ticket versus ₹9,000-plus for a flight, India's newest semi-high-speed train is rewriting how the Valley connects to the rest of the country — and how the diaspora can finally visit without white-knuckling the Jammu highway.",
        "slug": make_slug("kashmir-vande-bharat-100k-passengers-jammu-srinagar"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "For NRIs planning a Kashmir trip, the Vande Bharat eliminates the most dreaded part of the journey — the landslide-prone Jammu-Srinagar highway. Fly into Jammu, board a comfortable semi-high-speed train, and reach Srinagar in 4.5 hours. No more cancelled Srinagar flights during fog season, no more 12-hour highway crawls.",
        "tags": ["travel", "kashmir", "vande-bharat", "indian-railways", "tourism"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "DevDiscourse", "url": "https://www.devdiscourse.com/article/business/3919514-over-1-lakh-passengers-opt-for-jammu-srinagar-vande-bharat-service-in-22-days-of-operation"},
            {"name": "Indian Railways / Northern Railway", "url": "https://indianrailways.gov.in"}
        ]),
        "score_total": 78,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/16468819/pexels-photo-16468819.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "body": """The numbers landed like a headline writer's gift: 1,01,050 passengers in 22 days. That is the tally for India's Jammu-Srinagar Vande Bharat Express since commercial services began on May 2, a figure that tells you less about railway statistics and more about decades of pent-up demand for a reliable way into the Kashmir Valley.

## The Route That Changed Everything

The train covers Jammu to Srinagar in roughly four and a half hours, slicing through the Pir Panjal range via the engineering marvel that is the Banihal-Qazigund tunnel — the longest transportation tunnel in India at 12.75 kilometres. Compare that with the Jammu-Srinagar National Highway, a route so famously unreliable that "highway closed due to landslide" might as well be Kashmir's unofficial weather report. Road travel between the two cities can stretch anywhere from 8 to 14 hours on a good day, and flights into Srinagar — when fog does not cancel them — run ₹9,000 to ₹15,000 one way.

The Vande Bharat ticket? ₹730 in AC Chair Car, excluding catering.

## Why NRIs Should Care

For the Indian American planning a summer or autumn Kashmir trip, this changes the calculus entirely. The old playbook — fly into Delhi, catch a connecting flight to Srinagar, pray for clear skies — carried real cancellation risk. Srinagar's airport shuts down frequently during bad weather. The alternative, landing in Jammu and hiring a car for the highway, was an endurance test that most NRIs with jet lag and aging parents in tow understandably avoided.

Now the itinerary rewrites itself. Fly into Jammu (which has far fewer weather disruptions), walk to the adjacent railway station, and board a modern semi-high-speed train with GPS-based passenger information, upgraded interiors, and — in a touch that signals the railway's seriousness about the route — a special vegetarian Kashmiri menu developed by IRCTC. Passengers can opt out of the meal at booking and have catering charges deducted.

## What the Demand Curve Tells Us

Over 100,000 passengers in three weeks is not normal for a new Indian railway service. Northern Railway officials called it a "landmark moment in the region's transportation history," but the subtext is economic. The train is already being credited with boosting tourism bookings and enabling faster transport of Kashmiri horticulture produce and handicrafts to markets across India. For a Valley whose economy has lurched between shutdowns and curfews for years, dependable connectivity is not a luxury — it is infrastructure that underwrites recovery.

Railway officials say the service has maintained punctual operations since launch, a claim worth watching as monsoon season approaches and the infrastructure faces its first real stress test.

## Practical Details for Your Next Trip

- **Route**: Jammu Tawi → Srinagar (via Katra, Banihal)
- **Duration**: ~4 hours 30 minutes
- **Frequency**: Daily service
- **Fare**: ₹730 AC Chair Car (catering extra, opt-out available)
- **Booking**: IRCTC website or app — book early, demand is high
- **Best pairing**: Fly SFO/JFK/ORD → Delhi → Jammu (domestic connection), then Vande Bharat to Srinagar

The Jammu-Srinagar Vande Bharat is not just a train. For the diaspora, it is the removal of the single biggest friction point in visiting Kashmir — and at ₹730, the most consequential travel bargain in India right now."""
    },

    # ── Article 2: Rajasthan Rail Boom ───────────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "Rajasthan's Rail Renaissance: Jodhpur-Delhi Vande Bharat Goes 20 Coaches, Jaisalmer Joins the Network",
        "subheadline": "A ₹10,000-crore railway budget, a 150% capacity boost on the desert's busiest train, and direct service to the Golden City — India is betting big on making Rajasthan easier to explore by rail.",
        "slug": make_slug("rajasthan-rail-jodhpur-delhi-vande-bharat-jaisalmer"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "Rajasthan is the single most popular Indian state for NRIs hosting visiting friends and family. The rail upgrades mean you can now plan a Delhi-Jodhpur-Jaisalmer circuit entirely by train, in comfort, without hiring a driver for the desert stretch. The expanded Vande Bharat means fewer sold-out trains during peak Diwali and winter season.",
        "tags": ["travel", "rajasthan", "vande-bharat", "jaisalmer", "indian-railways", "tourism"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Insight Pulse", "url": "https://insightpulse.news/indian-railways-upgrades-rajasthan-network-jodhpur-delhi-vande-bharat-expanded-to-20-coaches-new-jaisalmer-coach-care-complex-launched/"},
            {"name": "The Daily Jagran", "url": "https://thedailyjagran.com"},
            {"name": "LatestLY", "url": "https://www.latestly.com/india/news/jodhpur-delhi-cantt-vande-bharat-to-run-with-20-coaches-sabarmati-jodhpur-express-extended-to-jaisalmer-6749253.html"}
        ]),
        "score_total": 75,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/35130760/pexels-photo-35130760.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "body": """On May 22, Railway Minister Ashwini Vaishnaw stood at Jodhpur Railway Station and rattled off a number that tells you everything about how India views Rajasthan's rail future: ₹10,000 crore. That is the state's current railway development budget, up from ₹700-800 crore in previous years — a twelvefold increase that is showing up in concrete ways across the desert state.

## The Jodhpur-Delhi Upgrade

The headline move: the Jodhpur-Delhi Cantonment Vande Bharat Superfast Express, one of Rajasthan's most popular services, expanded from 8 coaches to 20 as of May 24. The new configuration runs 16 AC Chair Cars, 2 Executive Chair Cars, and 2 Driver Power Cars — a 150% increase in seating capacity on a route that was routinely sold out weeks in advance.

For anyone who has tried booking a Jodhpur-Delhi train during Pushkar Fair, Diwali, or peak winter tourist season, this is meaningful relief. The 8-coach rake was a bottleneck on a corridor that serves not just Jodhpur residents but the entire western Rajasthan tourism economy.

## Jaisalmer Gets Connected

The second significant development: the Sabarmati-Jodhpur Express has been extended all the way to Jaisalmer, creating direct rail service between Gujarat and the Golden City for the first time. Simultaneously, Indian Railways inaugurated a ₹67-crore Coach Care Complex in Jaisalmer, giving the city the maintenance infrastructure to handle more incoming trains safely.

This matters because Jaisalmer — with its Sonar Fort, Patwa Ki Haveli, and Thar Desert camps — has long been the most difficult major Rajasthan destination to reach by train. Most visitors flew into Jodhpur and then endured a 5-6 hour drive across flat desert highway. Direct rail changes that equation.

## The NRI Rajasthan Playbook

Rajasthan is, by a wide margin, the Indian state that NRIs are most likely to visit with non-Indian friends and family. The "Golden Triangle" (Delhi-Agra-Jaipur) is the default itinerary, but the real Rajasthan — Jodhpur's blue city, Jaisalmer's sand dunes, Udaipur's lakes — requires venturing west, which until now meant hiring a private car and driver for days.

The rail upgrades open a new circuit: fly into Delhi, Vande Bharat to Jodhpur (comfortable, fast, bookable on IRCTC), then onward to Jaisalmer by the new extended express. Vaishnaw also confirmed that a Jodhpur-to-Haridwar Vande Bharat service is scheduled to launch within 10 months, which would connect western Rajasthan to the spiritual tourism corridor.

A new coaching terminal in Jodhpur and a dedicated Vande Bharat Sleeper Terminal at Bhagat Ki Kothi are under development for future long-distance routes to Chennai, Pune, Hyderabad, and Mumbai. That is the direction of travel: Rajasthan as a rail-first tourism state.

## Stations Getting a Cultural Facelift

The infrastructure push extends to station architecture. Jaisalmer's station redevelopment is complete, Jaipur is being remodelled around its "Pink City" aesthetic, and Pali station is undergoing rapid transformation. Track doubling is progressing on key stretches including Ajmer-Chittorgarh and Sawai Madhopur-Jaipur.

## Practical Details

- **Jodhpur-Delhi Vande Bharat**: Train 26481/26482, now 20 coaches, daily service
- **Sabarmati-Jaisalmer Express**: Train 20485/20486, daily, direct Gujarat-Jaisalmer
- **Booking**: IRCTC — book 2-3 weeks ahead for peak season
- **Best NRI itinerary**: Delhi → Jodhpur (Vande Bharat) → Jaisalmer (express) → fly out of Jodhpur or return to Delhi
- **Coming soon**: Jodhpur-Haridwar Vande Bharat (~10 months), sleeper services to Mumbai, Chennai, Hyderabad

For NRIs planning a winter 2026 Rajasthan trip, the message is clear: put down the car rental quote and check IRCTC first."""
    },

    # ── Article 3: Caribbean/Mexico NRI Guide ────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "Cancún, Jamaica, and Beyond: The NRI's Guide to Caribbean Getaways That Need No Extra Visa",
        "subheadline": "Indian passport holders with a valid US visa or green card can skip the visa queue for a dozen-plus sun-and-sand destinations. Here is what actually works, what does not, and how to plan a hassle-free beach weekend.",
        "slug": make_slug("caribbean-mexico-visa-free-nri-us-visa-guide"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "Most Indian Americans assume international beach vacations require weeks of visa paperwork. In reality, your US visa or green card unlocks visa-free or visa-on-arrival access to Mexico, Jamaica, several Caribbean islands, and more — destinations that are a 3-4 hour flight from most US metros.",
        "tags": ["travel", "caribbean", "mexico", "visa-free", "nri", "beach", "vacation"],
        "urgency": "low",
        "sources": json.dumps([
            {"name": "Wikipedia - Visa requirements for Indian citizens", "url": "https://en.wikipedia.org/wiki/Visa_requirements_for_Indian_citizens"},
            {"name": "Wikipedia - Visa policy of Mexico", "url": "https://en.wikipedia.org/wiki/Visa_policy_of_Mexico"},
            {"name": "PolicyBazaar", "url": "https://www.policybazaar.com/travel-insurance/articles/visa-free-islands-for-indian-passport-holders/"},
            {"name": "Turks and Caicos Tourism", "url": "https://turksandcaicostourism.com/plan-your-trip/faqs/"}
        ]),
        "score_total": 70,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/35985280/pexels-photo-35985280.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "body": """Here is a scene that plays out in Indian American group chats every long weekend: someone suggests a quick beach trip, the group gets excited, and then someone remembers — "Wait, do we need a visa?" The conversation dies. Everyone goes to Monterey instead.

It does not have to be this way. If you hold a valid US visa (any category — H-1B, B1/B2, L-1, even F-1) or a green card, a surprising number of Caribbean and Latin American destinations let you in with no additional visa. The flight times from major US metros are shorter than flying to LA from New York. Here is your cheat sheet.

## Mexico: The Obvious One

Indian passport holders with a valid US visa of any type — including expired US visas with valid I-94 status, in some cases — can enter Mexico visa-free for up to 180 days. Mexico issues an electronic authorization (SAE) that you can obtain online before travel, though many airlines will let you board with just your valid US visa stamp.

**Best for NRIs**: Cancún (direct flights from most US hubs, 3-4 hours), Mexico City (world-class food, culture), Tulum (the Instagram beach town), Los Cabos (Pacific-side luxury). Cancún in particular has become a de facto NRI weekend destination — you will find Indian restaurants on the hotel strip, and the Riviera Maya resorts increasingly cater to vegetarian diets.

**Watch out for**: If your US visa is expired but you have a valid I-797 approval notice, carry both. Immigration officers at Mexican airports generally honour valid US visa status, but the SAE system is cleaner. Apply at [INM's SAE portal](https://www.inm.gob.mx/sae/) before your trip.

## Jamaica: No Visa, No Hassle

Jamaica grants visa-free entry for up to 30 days to Indian passport holders. That is right — you do not even need a US visa for this one, though having one simplifies transit. Kingston and Montego Bay have direct flights from Miami, Fort Lauderdale, JFK, and Atlanta.

**Best for NRIs**: Montego Bay's all-inclusive resorts are tailor-made for the "let's just not think about anything for four days" trip. Ocho Rios for families, Negril for couples. Jamaican cuisine shares enough spice DNA with Indian food that your palate will not revolt.

## Maldives: The NRI Honeymoon Default

Maldives grants 30-day visa-on-arrival to all Indian passport holders. No US visa needed. Male has direct flights from several Indian cities, so the smartest NRI play is to combine a Maldives stop with your next India trip — fly SFO-Delhi-Male and back.

**Best for NRIs**: Honeymooners, anniversary trips, or anyone who wants to post turquoise-water photos without a single visa form. Budget options have expanded significantly with guesthouses on local islands running $80-150 per night.

## The Under-the-Radar Options

- **Turks and Caicos**: Visa-free for up to 90 days for citizens of many countries, but Indian passport holders should check the latest requirements — TCI has expanded visa waivers to tourists from the US, Canada, and Europe. If you hold a US green card, you are treated as a US resident for entry purposes.
- **Bahamas**: Similar treatment — green card holders enter visa-free. Indian passport holders may need a visa, but processing is straightforward through the Bahamas embassy.
- **Aruba, Curaçao, Bonaire** (Dutch Caribbean): Indian passport holders with a valid US visa can enter these islands without a separate Dutch visa for up to 30 days.
- **Costa Rica**: Visa-free entry for Indian passport holders with a valid US visa, up to 30 days. A nature lover's paradise and only 5 hours from Houston.
- **Panama**: Valid US visa holders from India can enter visa-free for up to 180 days. Panama City has excellent flight connections and a surprisingly cosmopolitan dining scene.
- **Colombia**: Indian passport holders with a valid US visa get visa-free entry for up to 90 days. Cartagena's old city is one of the most photogenic places in the Americas.

## Planning Tips

1. **Always verify current rules** before booking. Visa policies change — Thailand just dropped its visa-free arrangement for Indians this month. Use your country's embassy website, not travel blogs, for the final word.
2. **Carry printed proof** of your US visa status (I-797, I-94 printout) even for destinations that technically do not require it. Immigration officers in smaller airports appreciate paper.
3. **Book from US hubs**: Miami, Houston, Dallas, and Atlanta have the densest Caribbean flight networks. Spirit and Frontier often run sub-$200 round trips to Cancún and San Juan.
4. **Travel insurance**: Do not skip it. Medical evacuation from a Caribbean island can cost $50,000+, and your US health insurance likely does not cover international emergencies.
5. **Memorial Day, July 4th, Labor Day**: These long weekends are prime time for a quick Caribbean trip. Book flights 3-4 weeks ahead for best fares.

The Caribbean is closer, cheaper, and more accessible to Indian Americans than most realize. Your US visa is not just a work document — it is a travel pass to half the Western Hemisphere."""
    },
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

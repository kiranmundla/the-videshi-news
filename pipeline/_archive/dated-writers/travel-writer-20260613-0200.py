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
        "headline": "Jaipur Just Got India's First Japanese-Inspired Luxury Resort — and NRI Wedding Season Will Never Be the Same",
        "subheadline": "The 351-room Ananta Spa & Resort brings the Japanese philosophy of Omotenashi to the Aravali foothills, staking a claim as Rajasthan's largest experiential resort and a new contender for diaspora destination weddings.",
        "slug": make_slug("ananta-jaipur-japanese-luxury-resort-nri-weddings"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "With an estimated $100 billion Indian wedding economy and NRIs increasingly booking multiday destination weddings back home, the Ananta's 12 event venues and 19,000 sq ft ballroom position Jaipur as a serious alternative to Udaipur — at a fraction of the palace-hotel markup.",
        "tags": ["travel", "hotels", "rajasthan", "weddings", "luxury", "jaipur"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Hotelier India", "url": "https://hotelierindia.com"},
            {"name": "Outlook Traveller", "url": "https://outlooktraveller.com"},
            {"name": "Travel And Tour World", "url": "https://travelandtourworld.com"}
        ]),
        "score_total": 72,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/4/41/East_facade_Hawa_Mahal_Jaipur_from_ground_level_%28July_2022%29_-_img_01.jpg",
        "image_caption": "Hawa Mahal in Jaipur, the city now home to India's first Japanese-inspired luxury resort",
        "image_attribution": "Wikimedia Commons",
        "body": """Jaipur's hospitality landscape has operated on a familiar formula for decades: heritage palaces, Mughal-arched courtyards, camels at sunset. The Ravi Surya Group is now betting that the Pink City's next chapter looks nothing like its last.

The Ananta Spa & Resort Jaipur, managed by Black Rock Hotels & Resorts, has opened on 40 acres of the Aravali foothills along the Delhi-Jaipur Highway. With 351 rooms spread across five accommodation categories — including private pool suites and presidential residences spanning up to 3,600 square feet — it is among the largest luxury resort developments in Rajasthan.

What sets it apart is its design language. Positioned as India's first large-scale Japanese-inspired luxury resort, the property draws on the philosophy of *Omotenashi* — the Japanese concept of wholehearted, anticipatory hospitality — rather than the palace-and-haveli aesthetic that dominates Rajasthan's upper-tier hotels. Zen-influenced landscaping, minimalist interiors, and contemplative wellness spaces replace the maximalist opulence of the state's heritage stays.

## The Wedding Play

The real strategic bet, however, is not on leisure travelers. It is on the Indian wedding economy.

The resort houses 12 event venues, including the 19,000-square-foot Sakura Ballroom and the 70,000-square-foot Suijin Lawn, encircled by waterfalls and plunge pools. A dedicated 16-pillared ceremonial pagoda has been designed specifically for baraat processions and traditional wedding rituals — a deliberate nod to the growing demand for multiday, large-scale celebrations that blend spectacle with sophistication.

For NRI families planning destination weddings back in India, this matters. Udaipur and Jodhpur command eye-watering premiums during peak wedding season, with marquee properties often booked two years out. The Ananta enters the market with comparable scale, better highway access from Delhi (roughly four hours by road, an hour from Jaipur Airport), and a price point that undercuts the palace-hotel circuit. At 351 keys, it can absorb a 300-person wedding without displacing other guests — a persistent pain point at boutique heritage properties.

## Beyond the Mandap

The resort is not a single-use wedding factory. Its wellness infrastructure — luxury spa facilities, a fitness centre, and EV charging stations — signals a play for the growing segment of travelers who want both celebration and restoration in the same trip.

A dedicated kids' zone acknowledges the reality of NRI family travel: multigenerational groups where grandparents, parents, and children need to be entertained simultaneously. Multiple dining venues and celebration zones are designed for the kind of extended, leisurely stays that diaspora families favor when they finally make it back to India.

The property's location also places it within easy reach of Jaipur's cultural attractions — Amber Fort, the City Palace, Nahargarh — without the traffic and density of staying inside the city. For families combining a wedding with a few days of sightseeing, the Aravali setting offers a natural buffer.

## Rajasthan's Luxury Arms Race

The Ananta's opening comes amid an extraordinary burst of luxury hospitality investment in Rajasthan. Marriott International just opened its 10,000th property globally — the JW Marriott Ranthambore Resort & Spa — less than 400 kilometers southeast. The Oberoi Group's restored Rajgarh Palace in nearby Khajuraho (across the Madhya Pradesh border) is drawing international attention. Rajasthan now hosts more five-star keys than at any point in its history.

For the Indian diaspora, this arms race translates directly into better options, competitive pricing, and properties that understand the specific rhythms of NRI travel — the two-week trip home, the wedding that doubles as a family reunion, the desire for world-class amenities without losing the feeling of being in India.

The Ananta's Japanese-inspired bet is a calculated gamble that the next generation of NRI travelers wants something different from their parents' palace stays. Whether Jaipur's market agrees remains to be seen, but 351 rooms and a 70,000-square-foot lawn suggest the Ravi Surya Group is not hedging."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "A 350-Year-Old Maharaja's Palace Is Now an Oberoi — and NRIs Finally Have a Reason to Visit Khajuraho",
        "subheadline": "The Oberoi Rajgarh Palace sits on 76 acres of forest and lake in Madhya Pradesh, minutes from a tiger reserve and the UNESCO temples that most diaspora travelers have heard of but never bothered to see.",
        "slug": make_slug("oberoi-rajgarh-palace-khajuraho-nri-heritage"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "Khajuraho's UNESCO temples are on every NRI's 'someday' list but almost no one's itinerary. A world-class Oberoi property with tiger safaris and fine dining removes the last excuse — and positions central India as a credible luxury alternative to the overcrowded Rajasthan circuit.",
        "tags": ["travel", "hotels", "luxury", "heritage", "madhya-pradesh", "wildlife", "oberoi"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Business Traveller", "url": "https://businesstraveller.com"},
            {"name": "Hotelier Buzz", "url": "https://hotelierbuzz.com"},
            {"name": "Oberoi Hotels", "url": "https://oberoihotels.com"},
            {"name": "Hospitality Net", "url": "https://hospitalitynet.org"}
        ]),
        "score_total": 75,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/e/e7/1_Khajuraho.jpg",
        "image_caption": "The UNESCO World Heritage temples of Khajuraho, now minutes from the new Oberoi Rajgarh Palace",
        "image_attribution": "Wikimedia Commons",
        "body": """Ask any NRI about Khajuraho and you will get one of two responses: a vague memory of those temple sculptures from a school textbook, or a slightly embarrassed acknowledgment that they have been meaning to visit for years. The Oberoi Group is betting that the missing ingredient was never interest — it was infrastructure.

The Oberoi Rajgarh Palace occupies a restored 350-year-old hilltop fortress originally built by Maharaja Hindu Pat of the Bundela Dynasty. The property sprawls across 76 acres of Sal and Palash forests on the slopes of the Maniyagarh Hills, with a natural lake and sweeping views of the Vindhyachal ranges. It opened late last year and is now fully operational, with 65 rooms and suites, private pool villas, and the kind of meticulous service that has made Oberoi a byword for Indian luxury worldwide.

Business Traveller featured the property this week among the world's best heritage hotel conversions — alongside the Imperial Hotel Kyoto and the renovated Waldorf Astoria New York — calling it one of the "spectacular second lives" of historic buildings reborn as luxury stays.

## Location as Strategy

The palace's location is its sharpest asset. Panna National Park and Tiger Reserve sits minutes away, offering morning safari drives that routinely produce tiger sightings — guests report the hotel provides hot-water bottles and blankets for 6 AM departures into the reserve. Khajuraho's UNESCO World Heritage temples, among the finest examples of medieval Indian temple architecture, are a short drive in the other direction.

This combination — world-class wildlife, thousand-year-old temples, and a palace hotel — exists nowhere else in India in such concentrated proximity. Ranthambore has the tigers and the new JW Marriott but no UNESCO temples. Hampi has the ruins but no tigers. Khajuraho, until now, had the temples but nowhere worth staying.

## What the Stay Looks Like

The restoration preserved the palace's Bundela-era architecture — arched corridors, stone courtyards, terraced gardens — while integrating contemporary comforts with the kind of restraint that separates a good heritage conversion from a theme park. The Kohinoor Suite offers two bedrooms and a private pool. Palace Rooms provide 360-degree views of hills, forests, and the lake.

Dining leans into regional identity. Maanya serves traditional recipes from the region in an indoor-outdoor layout overlooking the Maniyagarh Hills, open exclusively for dinner. Neerangan, set along the lake's edge, runs through the day with Indian and international options and live evening entertainment. Amrava, overlooking the palace courtyard, offers cocktails and small plates in a setting that feels more like a private club than a hotel bar.

The Oberoi has also invested in sustainability: solar power, solar-heated water in all rooms, 100% LED illumination, on-site vegetable cultivation, an organic waste converter, and an in-house water bottling plant that eliminates the carbon footprint of shipped drinking water.

## The NRI Calculation

For diaspora travelers, Khajuraho has always suffered from a positioning problem. It is not on the Golden Triangle. It does not have Goa's beaches or Kerala's backwaters. It requires a domestic flight from Delhi or a long drive, and until recently, the accommodation options ranged from adequate to forgettable.

The Oberoi changes that math entirely. A three-night itinerary — temple day, safari day, palace day — now rivals anything in Rajasthan for depth of experience, without the crowds that have turned Jaipur and Udaipur into peak-season obstacle courses. Flights from Delhi to Khajuraho run daily, and the hotel arranges transfers.

For NRI families who have done the Taj Mahal, done Rajasthan, and are looking for something that feels genuinely undiscovered, Khajuraho with the Oberoi Rajgarh Palace is the strongest pitch central India has ever made. The temples alone justify the trip. The tigers are a bonus. The palace is the reason you will want to stay longer than you planned.

Rates start steep — this is an Oberoi, after all — but early reviews on TripAdvisor from international and domestic guests suggest the property is already delivering on its promise. One guest from the UK described the sunrise over the Gomati River and a tiger sighting in the same morning as "worth every rupee." For the diaspora, that is exactly the kind of trip that turns a visit home into a story worth telling."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

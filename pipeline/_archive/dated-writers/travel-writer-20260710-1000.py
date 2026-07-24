#!/usr/bin/env python3
"""Travel writer for The Videshi — July 10, 2026 run."""
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
    # ── Article 1: Indian Passport Henley Index July 2026 ──
    {
        "id": str(uuid.uuid4()),
        "headline": "India's Passport Slips Two Spots — but 56 Doors Stay Open",
        "subheadline": "The July 2026 Henley Passport Index nudges India down to 80th, though Indian travellers still enjoy visa-free or visa-on-arrival access to 56 destinations. For NRIs holding US or Schengen stamps, the real number is much higher.",
        "slug": make_slug("india-passport-henley-index-july-2026-nri-visa-free"),
        "category": "travel",
        "vertical": "travel-advisory",
        "diaspora_angle": "NRIs with valid US visas or Schengen stamps unlock 30+ additional countries on top of the Indian passport's base list — making the practical travel footprint far larger than the headline ranking suggests.",
        "tags": ["travel", "passport", "visa", "henley passport index", "indian passport", "visa-free"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Outlook Traveller", "url": "https://www.outlooktraveller.com/"},
            {"name": "Henley & Partners", "url": "https://www.henleyglobal.com/passport-index"},
            {"name": "Livemint", "url": "https://www.livemint.com/"},
            {"name": "Global Citizen Solutions", "url": "https://www.globalcitizensolutions.com/"}
        ]),
        "score_total": 72,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Indian_Passport_%28e-Passport%2C_2024%29.svg/500px-Indian_Passport_%28e-Passport%2C_2024%29.svg.png",
        "image_caption": "India's e-Passport, introduced in 2024, now grants visa-free or visa-on-arrival access to 56 destinations",
        "image_attribution": "Wikimedia Commons",
        "body": """India's passport has dipped two places to 80th in the July 2026 edition of the Henley Passport Index — a slide that, on paper, looks like a step backward for Indian travellers. In practice, the number of destinations accessible without a traditional visa beforehand remains unchanged at 56.

The Henley index, compiled from International Air Transport Association data, ranks 199 passports against 227 travel destinations. Singapore holds the top spot with visa-free access to 192 countries. Japan and South Korea share second place at 187. India's neighbours paint a familiar picture: the Maldives leads South Asia, while Pakistan and Afghanistan anchor the bottom of the global table.

## What the numbers actually mean

Those 56 destinations break down into three tiers. A handful — Bhutan, Nepal, Jamaica, Macau — grant unconditional visa-free entry. A larger group, including Thailand, Malaysia, Mauritius, Maldives, Fiji, and Kazakhstan, allows stays of 14 to 90 days without pre-arranged paperwork. Then come the visa-on-arrival countries — Indonesia, Cambodia, Sri Lanka, Qatar, Jordan, Tanzania, and others — where a stamp at the immigration counter is all it takes.

The separate Global Passport Index 2026, released by Global Citizen Solutions on July 7, places India at 125th using a broader methodology that factors in investment potential and quality of life alongside mobility. That ranking is harsher, but it measures a different question.

## The NRI multiplier

Here is where the story diverges sharply for Indian Americans. The Indian passport's base score tells only half the tale. Holders of a valid US visa — even a stamped B1/B2 — unlock visa-free or visa-on-arrival entry to more than 30 additional countries, including Mexico, Colombia, Peru, Turkey, the Philippines, South Korea, Oman, the UAE, and Saudi Arabia.

A multiple-entry Schengen visa adds another layer: Albania, Georgia, Bosnia and Herzegovina, Serbia, North Macedonia, and several Caribbean territories open up. Between the two stamps, the practical travel footprint for an NRI carrying an Indian passport and a US green card or visa is closer to 90 destinations than 56.

## What changed — and what didn't

India's two-place drop reflects not a loss of bilateral agreements but the relative gains of other countries. Several African and Central Asian nations negotiated new visa-waiver deals with third parties, nudging their scores past India's. No country revoked visa-free access for Indian passport holders in this cycle.

The trajectory over the past two years has been quietly positive. India climbed from 85th in 2025 to 80th in January 2026 on the back of new bilateral deals with Angola, Barbados, and Fiji. The July correction is a natural pause, not a reversal.

## What to watch

Three developments could reshape the Indian passport's standing by year-end. The ETIAS system for European travel — originally slated for 2025 and now expected in late 2026 — will require Indian travellers to pre-register online before entering the Schengen zone, adding a step but not a traditional visa. India's ongoing negotiations with the EU over a free-trade agreement could eventually include mobility provisions. And a quiet push by the Ministry of External Affairs to expand visa-waiver agreements with Pacific Island and Caribbean nations may add three to five more visa-free destinations before the January 2027 update.

For now, the passport's rank matters less than what it opens. Fifty-six doors is a smaller number than a Singaporean enjoys — but for the Indian American planning a monsoon holiday, a Diwali trip, or a quick weekend in Bali, most of those doors are already the ones that count."""
    },

    # ── Article 2: Noida/Jewar Airport Rapid Expansion ──
    {
        "id": str(uuid.uuid4()),
        "headline": "Jewar Airport Hits 48 Daily Flights — Just Four Weeks After Opening",
        "subheadline": "Noida International Airport has quadrupled its flight count since its June 15 launch, now connecting 16 Indian cities. International services are expected later this year, giving NRIs a genuine alternative to the chaos of Delhi's IGI.",
        "slug": make_slug("noida-jewar-airport-expansion-48-flights-nri"),
        "category": "travel",
        "vertical": "aviation",
        "diaspora_angle": "For NRIs flying into Delhi-NCR to visit family in Noida, Greater Noida, Ghaziabad, or western UP — or heading onward to Agra and the Taj Mahal — Jewar could soon eliminate the two-hour slog across Delhi from IGI.",
        "tags": ["travel", "airport", "noida", "jewar", "aviation", "indigo", "delhi-ncr"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/"},
            {"name": "FareEagle", "url": "https://www.fareeagle.com/"},
            {"name": "TravTalk India", "url": "https://www.travtalkindia.com/"},
            {"name": "Wikipedia", "url": "https://en.wikipedia.org/wiki/Noida_International_Airport"}
        ]),
        "score_total": 75,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/4/4e/Prime_Minister_of_Bharat%2C_Shri_Narendra_Damodardas_Modi_at_the_inauguration_ceremony_of_the_Noida_International_Airport%2C_Jewar.jpg",
        "image_caption": "Prime Minister Modi at the inauguration of Noida International Airport at Jewar in March 2026",
        "image_attribution": "Wikimedia Commons",
        "body": """When Noida International Airport launched commercial operations on June 15 with a single IndiGo flight from Lucknow, it was easy to dismiss it as yet another ribbon-cutting in India's infrastructure blitz. Four weeks later, the airport — code DXN, located along the Yamuna Expressway at Jewar in Uttar Pradesh — is handling roughly 48 daily aircraft movements across 16 domestic destinations. That is not a soft opening. That is a sprint.

## The network so far

IndiGo is the anchor tenant, operating flights to Lucknow, Hyderabad, Bengaluru, Amritsar, Jammu, Bhopal, Dehradun, Dharamshala, Pantnagar, Jodhpur, Bareilly, Jaipur, Kishangarh, Srinagar, and Chandigarh. Akasa Air covers Bengaluru, Mumbai, and Navi Mumbai. Six new destinations were added from July 1 alone, with Chandigarh joining from July 13. Extra frequencies are already being slotted in to match demand — Chandigarh gets additional Monday and Tuesday flights starting mid-July.

The airport started with 12 daily flights in its first week. By the end of June, it was handling 24. The ramp to 48 by early July came faster than even its own management projected publicly. Nitu Samra, Jewar's CEO, had told media in June that 40-42 flights would be the July target.

## Why NRIs should pay attention

For the roughly 800,000 Indian Americans who live in or regularly visit the Delhi-NCR region, the practical reality of flying into India has been a single, groaning bottleneck: Indira Gandhi International Airport. IGI processed over 73 million passengers in 2025. On a bad day, the immigration queue stretches an hour, and the taxi ride from the airport to Noida or Greater Noida adds another 90 minutes to two hours.

Jewar changes the math. Sitting at the intersection of the Yamuna Expressway and the upcoming Delhi-Varanasi high-speed rail corridor, the airport is 40 minutes from central Noida, 90 minutes from Agra and the Taj Mahal, and directly accessible from Ghaziabad, Aligarh, and Mathura. For NRI families visiting relatives in the western UP belt — or planning a side trip to Agra that currently requires a pre-dawn Delhi departure — the geography alone is compelling.

## International flights: when, not if

The airport's first phase, built at a cost of ₹11,200 crore ($1.3 billion), includes a single runway and passenger terminal. International operations are expected to begin later in 2026. Christoph Schnellmann, executive vice chairman of the airport's board, confirmed in June that discussions with foreign carriers are active. The management projects five million passengers in its first full year — ambitious for a greenfield facility, but the traffic catchment area covers 60 million people within a two-hour drive.

For NRIs, the international launch will be the real inflection point. Once airlines like Emirates, Etihad, or even Air India begin routing through Jewar, it becomes a legitimate alternative to IGI for the SFO-DEL, JFK-BOM, and ORD-HYD crowd — especially those whose final destination is anywhere south or east of Delhi.

## The cost question

There is a catch, though it is a modest one. The Airport Economic Regulatory Authority has approved a ₹490 user development fee for domestic departing passengers — higher than what some smaller airports charge, reflecting the greenfield premium. Samra has argued the fee is competitive given the infrastructure. For an NRI accustomed to paying $40 for a Priority Pass lounge visit, ₹490 ($5.80) is rounding error.

## What comes next

Phase 2 planning is already underway, with a second runway and expanded terminal capacity that would bring annual capacity to 30 million passengers. The airport also began cargo operations from day one — a signal that it intends to compete with Delhi for logistics traffic, not just leisure and VFR travel.

The pattern is familiar from other Indian airport launches: start small, prove demand, scale fast. Bengaluru's Kempegowda and Hyderabad's Rajiv Gandhi both followed this playbook. The difference is speed. Jewar's four-week trajectory suggests Delhi-NCR's second airport may not stay secondary for long."""
    },

    # ── Article 3: Monsoon Travel Guide for NRIs ──
    {
        "id": str(uuid.uuid4()),
        "headline": "The NRI's Guide to Monsoon India — Where to Go, What to Skip, and Why July Is the Smartest Month to Visit",
        "subheadline": "Domestic fares drop 30-50%, hotel rates crater, and India's most dramatic landscapes come alive. Here is how to plan a monsoon trip home that is memorable for the right reasons.",
        "slug": make_slug("nri-monsoon-india-travel-guide-july-2026"),
        "category": "travel",
        "vertical": "travel-guide",
        "diaspora_angle": "July and August are when most NRIs visit India — school breaks align, family obligations pile up, and the assumption is that monsoon means misery. In reality, it is the cheapest, least crowded, and most visually stunning time to travel the country.",
        "tags": ["travel", "monsoon", "india", "nri", "kerala", "ladakh", "valley of flowers", "coorg", "budget travel"],
        "urgency": "low",
        "sources": json.dumps([
            {"name": "Outlook Traveller", "url": "https://www.outlooktraveller.com/"},
            {"name": "StayVista Journal", "url": "https://stayvista.com/"},
            {"name": "Wego Travel Blog", "url": "https://blog.wego.com/"},
            {"name": "Femina", "url": "https://www.femina.in/"}
        ]),
        "score_total": 68,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/17141643/pexels-photo-17141643.jpeg",
        "image_caption": "Lush green Kerala backwaters during monsoon season, when India's landscape transforms",
        "image_attribution": "Pexels",
        "body": """Every NRI who has booked a July flight to India has heard the warning: "Why are you going in monsoon?" The question comes from people who have never stood on a Coorg coffee estate as the first rains roll in, never watched the Valley of Flowers bloom in alpine Technicolor, never driven through Rajasthan when the desert turns improbably green. The Indian monsoon is not an obstacle to travel. It is a reason to travel.

And it comes with a price tag that makes the math irresistible. Domestic flights drop 30-50% from winter peak pricing. Hotels across the country discount aggressively from July through early September. The crowds that choke Goa's beaches and Jaipur's forts in December simply vanish.

## The rain-free escapes

Not everywhere in India gets drenched in July. The Himalayan rain-shadow belt — Ladakh, Spiti Valley, and parts of upper Himachal — stays dry and clear while the plains below are awash. July is peak season in Leh-Ladakh, with all high passes open, blue skies over Pangong Lake, and road conditions at their best on the Manali-Leh and Srinagar-Leh highways.

Spiti Valley, a cold desert of 1,000-year-old monasteries and moonscape valleys, sees almost no rain. The Shimla-Kinnaur approach is the safer route during monsoon. Budget six to nine days for a proper Spiti circuit, and book inner-line permits for restricted areas in advance.

For NRIs who want a Himalayan fix without the altitude commitment, Almora in Uttarakhand's Kumaon region offers misty green hillsides, colonial-era lanes, and Himalayan views — greener and quieter in July, and well away from the landslide-prone high routes.

## The monsoon showpieces

Then there are the places that exist *because* of the monsoon.

The Valley of Flowers in Uttarakhand — a UNESCO-listed alpine meadow — erupts into a carpet of wildflowers from mid-July to mid-August. It is the single most July-specific reason to travel in India. Entry permits are ₹200 for Indians, with a daily cap of 300 visitors. The trek from Govindghat to the base camp at Ghangaria takes a day; apply early on the official portal.

Kerala runs an official monsoon tourism campaign promoting June through August as the best season for Ayurvedic Panchakarma treatments, when the humid climate makes the body more receptive. Kochi and Alleppey's houseboat cruises through rain-swollen backwaters hit their visual peak. Munnar's tea plantations turn an electric green that simply does not exist in winter photographs.

Coorg in Karnataka delivers coffee plantation walks, waterfalls at full force, and a six-family-at-a-time wilderness retreat called Beforest's Monsoon Welcome that might be the most immersive nature experience in the country right now.

## The quick getaways

For NRIs based with family in Mumbai or Pune, the Western Ghats are a two-hour monsoon playground. Lonavala and Mahabaleshwar offer valley views, waterfalls, and easy highway access. Malshej Ghat has flamingo sightings and cloud-level drives. Matheran — India's only car-free hill station — is reached by toy train or a short trek.

Goa in monsoon is a secret its residents try to keep. Empty beaches, lush green interiors, dramatically discounted hotel rates, and the Sao Joao festival in late June. Expect afternoon downpours and some beach shack closures, but the trade-off is having Palolem or Arambol almost entirely to yourself.

## The practical NRI checklist

**Flights**: Book India-US legs at least three weeks out; monsoon is off-peak for international routes too, so fares are 15-20% below Diwali or Christmas pricing. Domestic connections on IndiGo and Air India are aggressively discounted — Mumbai to Goa can be had for under ₹3,000.

**Packing**: A lightweight waterproof jacket beats an umbrella. Quick-dry shoes for treks. Waterproof phone pouch. Mosquito repellent rated for tropical conditions — the monsoon breeds them fast.

**Health**: Carry oral rehydration salts and a basic stomach kit. Avoid street food in areas with standing water. If doing Ayurveda in Kerala, book a NABH-accredited centre rather than a roadside spa.

**Timing**: The monsoon typically reaches Kerala by late May, Mumbai by early June, Delhi by late June, and achieves full coverage by mid-July. August is the wettest month across most of the country. September brings a retreat that leaves everything washed clean.

**What to skip**: Avoid coastal treks in Maharashtra during red-alert rainfall warnings. The Amarnath Yatra route is prone to landslides and flash floods — check MEA and state advisories daily. River rafting in Rishikesh shuts down when the Ganges swells beyond safe levels.

The monsoon is India at its most theatrical. For the NRI who has only ever seen the country in winter or during Diwali, a July visit is a revelation — cheaper, emptier, and more beautiful than the brochure version most visitors settle for."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['headline']}")
        print(f"   slug: {art['slug']}")
    except Exception as e:
        print(f"❌ {art['headline']}: {e}")

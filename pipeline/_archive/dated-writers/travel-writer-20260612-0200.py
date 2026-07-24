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
        "headline": "India's Newest Airport Opens Sunday — and It Halves the Journey to the Taj Mahal",
        "subheadline": "Noida International Airport at Jewar begins commercial flights on June 15 with 140 weekly departures to 15 cities. For the millions of NRIs who route through Delhi every year, it promises less congestion, faster connections, and a two-hour drive to Agra.",
        "slug": make_slug("noida-jewar-airport-opens-nri-taj-mahal"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "NRIs flying into Delhi-NCR now have a second airport option that eases IGI congestion and cuts travel time to Agra, Mathura, and western UP destinations by half — critical for the peak summer homecoming season.",
        "tags": ["travel", "airports", "aviation", "noida", "jewar", "infrastructure"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/ampstories/news/noida-international-airport-set-for-june-15-launch-indigo-akasa-air-lead-operations"},
            {"name": "Aviation A2Z", "url": "https://aviationa2z.com/index.php/2026/06/11/noida-international-airport-completes-aircraft-turnaround-trial-ahead-of-launch/"},
            {"name": "The Sun UK", "url": "https://www.thesun.co.uk/travel/33910729/new-mega-airport-asia-biggest-120million-passengers/"},
            {"name": "Travel and Leisure Asia", "url": "https://www.travelandleisureasia.com/in/news/air-india-easy-connect-flights-immigration-tier-2-cities/"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/4/4e/Prime_Minister_of_Bharat%2C_Shri_Narendra_Damodardas_Modi_at_the_inauguration_ceremony_of_the_Noida_International_Airport%2C_Jewar.jpg",
        "image_caption": "The inauguration ceremony of Noida International Airport at Jewar, Uttar Pradesh",
        "image_attribution": "Wikimedia Commons",
        "body": """For years, every NRI flying into Delhi has shared the same bottleneck: Indira Gandhi International Airport. The single hub serves more than 70 million passengers annually, and anyone who has spent two hours inching through immigration at Terminal 3 after a 16-hour transpacific flight knows the arithmetic is broken.

On Sunday, June 15, that arithmetic changes. Noida International Airport — built on 5,000 hectares of land at Jewar in western Uttar Pradesh — begins commercial operations, becoming the National Capital Region's second major airport and, by site area, one of the largest greenfield airports in Asia.

## What Opens on Day One

The launch is measured, not spectacular. IndiGo will operate the inaugural flight — a service from Lucknow touching down at 8:05 AM — and will run 126 weekly flights connecting 15 domestic destinations. Akasa Air follows on June 16 with 14 weekly departures. That gives Jewar 140 scheduled flights per week at launch, with an initial capacity of 12 million passengers per year.

Air India Express, originally expected to join the opening roster, has postponed its entry indefinitely as the airline focuses on cost restructuring. The Tata-owned carrier cut 27 percent of its flights year-on-year in June, and Jewar is simply not a priority while the balance sheet bleeds.

International routes are not part of the opening phase. But the airport's master plan envisions a full-scale international hub capable of handling 120 million passengers annually across multiple phases — a figure that would rival the busiest airports in Southeast Asia.

## Why NRIs Should Pay Attention

The immediate draw is geography. Jewar sits roughly 100 kilometres southeast of Delhi, placing it just two hours by road from Agra — half the current four-hour drive from IGI. For the lakhs of diaspora families who combine a Delhi homecoming with a Taj Mahal visit, the math is straightforward: less driving, less fatigue, less wasted time.

The longer game is congestion relief. IGI has been operating above comfortable capacity for years, and every NRI who has watched their connecting flight board while they were still in the immigration queue understands the stakes. A second airport distributes that load. It also opens up Noida, Greater Noida, Ghaziabad, Aligarh, and Mathura — cities with large diaspora networks — as direct catchment areas rather than afterthoughts on the other side of Delhi traffic.

There is also the tunnel. The Ministry of Road Transport is studying a direct tunnel link between IGI and Jewar, which would make cross-airport connections seamless. If approved, it would create a genuine two-airport system for NCR, similar to what London and New York have operated for decades.

## The Hub-and-Spoke Connection

Jewar's opening coincides with another structural shift in Indian aviation. On June 25, Air India launches its "Easy Connect" service — a hub-and-spoke model starting with Varanasi that lets passengers from smaller cities complete immigration and baggage check-in at their home airport before connecting internationally through Delhi.

Civil Aviation Minister Ram Mohan Naidu called the Varanasi corridor the beginning of India's hub-and-spoke aviation vision. Within four hours of arriving at Delhi, Easy Connect passengers can board onward flights to 17 international destinations — London Heathrow, Frankfurt, Singapore, Dubai, and a dozen others.

For NRIs with family in tier-two cities, this is the real headline. A parent in Varanasi or Lucknow will no longer need to navigate IGI's domestic-to-international transfer maze. And as Jewar matures and wins its own international routes, the hub-and-spoke model could extend there too, creating a second gateway that bypasses Delhi entirely.

## What to Expect (and What Not To)

The honest assessment: Jewar will be quiet for the first several months. Two airlines, domestic-only routes, and a new-airport learning curve mean early adopters should expect some operational friction. Retail, food, and ground transport options will be limited at launch.

But the bones are solid. The June 9 turnaround trial — a full-scale simulation of aircraft arrival, passenger processing, baggage handling, refuelling, and departure — validated the airport's critical infrastructure, including instrument landing systems and visual docking guidance.

For NRIs planning summer trips to Delhi, the practical advice is simple: if your final destination is anywhere south or east of NCR — Agra, Mathura, Lucknow, Aligarh — watch for Jewar route additions over the next quarter. The airport is designed to grow fast, and airlines will follow demand. The decades-long monopoly of a single Delhi airport is over."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Five Monsoon Destinations That NRIs Keep Promising to Visit — This Is the Year",
        "subheadline": "India's monsoon season coincides perfectly with the American summer break, and a new wave of off-peak travel is turning Goa, Munnar, Coorg, Valley of Flowers, and Cherrapunji into serious June-through-August destinations. Flights are cheaper, crowds are thinner, and the landscapes are at their most dramatic.",
        "slug": make_slug("india-monsoon-destinations-nri-summer-break"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "India's monsoon season aligns perfectly with US school summer break and PTO windows, offering NRIs cheaper flights, thinner crowds, and destinations at their most stunning — a combination most diaspora families never think to exploit.",
        "tags": ["travel", "monsoon", "india", "destinations", "nri", "summer"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Travel and Tour World", "url": "https://www.travelandtourworld.com/news/article/qawppktitwac/"},
            {"name": "Travel and Tour World - Second City Tourism", "url": "https://www.travelandtourworld.com/news/article/india-joins-portugal-japan-italy-south-korea-spain-thailand-vietnam-and-indonesia-in-leading-the-global-second-city-tourism-movement/"},
            {"name": "Mordor Intelligence - Heritage Tourism", "url": "https://www.mordorintelligence.com/industry-reports/heritage-tourism-market"}
        ]),
        "score_total": 72,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/9/99/Tea_plantations_in_Munnar.jpg",
        "image_caption": "Tea plantations in Munnar, Kerala, during the green season",
        "image_attribution": "Wikimedia Commons",
        "body": """Every Indian American knows the drill. You book your India trip for December or March, when the weather is predictable and the wedding invitations stack up. You fight for overpriced seats on the usual SFO-DEL or JFK-BOM routes, land in dry heat or pleasant winter air, and do the circuit: family, temples, shopping, one nice dinner out. The monsoon never enters the conversation.

It should. India's rainy season — roughly June through September — coincides almost perfectly with the American summer break. Flights are meaningfully cheaper (Delhi round-trips from major US hubs drop $200-400 versus the December peak). Crowds at major tourist sites thin out dramatically. And the landscapes transform into something most NRIs haven't seen since childhood, if ever.

A growing body of travel data confirms the shift. Five-star hotel bookings in India more than doubled in April year-on-year, according to Cleartrip. Monsoon-specific destinations are reporting early-season surges. And India is now part of a global "second-city tourism" movement, with travellers actively seeking alternatives to overcrowded hotspots.

Here are five destinations worth the detour.

## Goa: The Version You Haven't Seen

Most NRIs think of Goa as beaches and nightlife — the Baga-Calangute corridor in peak season. Monsoon Goa is a different state entirely. The beaches empty, the inland hills turn electric green, and Dudhsagar Falls — a 310-metre cascade on the Karnataka border — runs at full, thundering force.

The real appeal is pace. Spice plantations open for rain-season walks. Village cafés serve fresh catch without the tourist markup. The drives through Ponda and Sanguem feel like Kerala without the crowds. A family of four can rent a heritage villa in Assagao for less than a mid-range Airbnb in Anjuna costs in January.

The caveat: beach swimming is largely off-limits during monsoon. Currents are strong, lifeguard coverage drops, and the Arabian Sea turns rough. Come for the green side, not the tan.

## Munnar: Tea Gardens in High Definition

Kerala's hill station is photogenic year-round, but monsoon turns it cinematic. Mist rolls through the tea estates every morning, waterfalls that were trickles in March become roaring cascades, and the temperature hovers around 15-20°C — practically sweater weather while your friends in Dallas bake at 42.

Echo Point, Top Station, and the Eravikulam National Park plateau all hit their visual peak during the rains. Munnar also works logistically: it is a four-hour drive from Kochi airport, and the new Kochi-Munnar highway improvements have cut that further. A three-night stay covers the essential circuit comfortably.

Practical note: book a driver rather than self-driving. Hill roads get slick, visibility drops fast after 4 PM, and hairpin turns in fog are not for the unfamiliar.

## Coorg: Coffee Country at Its Fragrant Best

Kodagu district in Karnataka operates on a different rhythm from the rest of India's tourist map. There are no monuments to tick off, no must-see temples dominating the itinerary. The draw is atmospheric: coffee estates that smell richer after rain, Abbey Falls at peak flow, home-cooked Coorgi pandi curry at family-run estates, and drives where the forest canopy closes overhead.

For NRIs based in the Bay Area or Seattle — people accustomed to green, misty landscapes — Coorg feels oddly familiar. It is also only five hours from Bengaluru, making it an easy add-on to a South India trip. Estate stays range from ₹3,000 to ₹15,000 per night, a fraction of comparable mountain retreats worldwide.

## Valley of Flowers: The Trek You Keep Postponing

This UNESCO World Heritage Site in Uttarakhand opens only from June to October, when over 600 species of wildflowers carpet a high-altitude Himalayan meadow. The trek — roughly 17 kilometres from Govindghat to the valley — is moderate by Himalayan standards, manageable for reasonably fit adults and older teenagers.

The monsoon is not optional here; it is the entire point. The flowers bloom because of the rain. The valley is inaccessible in winter, barren in spring, and at its most spectacular in July and August. NRI families with children aged 12 and up often find this to be the single most memorable experience of an India trip — more striking than any fort or palace.

Logistics: fly into Dehradun or Jolly Grant Airport, drive to Joshimath, then to Govindghat. Local porters and guides are available and recommended. Carry rain gear, sturdy boots, and layers.

## Cherrapunji: Where Rain Is the Attraction

Sohra — still better known by its colonial name, Cherrapunji — receives some of the highest rainfall on Earth. For most of the year, that is a weather statistic. During monsoon, it becomes an experience: waterfalls everywhere, living root bridges dripping with moss, and a landscape that feels more tropical Scotland than subcontinental India.

Nohkalikai Falls, at 340 metres, is India's tallest plunge waterfall and peaks dramatically during the rains. The living root bridges of Nongriat — bioengineered over generations by the Khasi people — add a cultural dimension that no other monsoon destination matches.

Meghalaya is the least-visited state on this list, which is precisely the point. For NRIs tired of showing visiting relatives the same Golden Triangle circuit, Cherrapunji offers something genuinely new — a part of India that most Indians, let alone the diaspora, have never seen.

## The Practical Case

Round-trip flights from the US to India in July average $900-1,100 on major carriers — roughly 25-30 percent below December peak pricing. Domestic connections to these five destinations range from ₹3,000 to ₹8,000. Hotel rates drop 30-50 percent at monsoon-season properties compared to winter.

The tradeoff is real: rain delays happen, roads close temporarily, and outdoor plans require flexibility. But for the NRI family that has done the winter-wedding-and-monuments trip three times over, the monsoon offers something the dry season cannot — an India that feels alive, unhurried, and startlingly beautiful."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

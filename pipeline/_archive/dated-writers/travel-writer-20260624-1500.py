#!/usr/bin/env python3
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# Load env
env_file = Path.home() / ".env.supabase"
if not env_file.exists():
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

# ---------------------------------------------------------------------------
# ARTICLE 1 — Air India "Easy Connect" hub-and-spoke from Varanasi
# ---------------------------------------------------------------------------
body1 = """When Air India's flight AI1111 lifts off from Varanasi on June 25, it will look, on a departure board, like an unremarkable domestic hop to Delhi. It is anything but. The flight is the first to operate under India's new hub-and-spoke aviation framework, branded by the airline as "Easy Connect," and it quietly rewires how a passenger from a small Indian city reaches the rest of the world.

The mechanics are the whole story. A traveller flying out of Varanasi will check a bag through to the final international destination, clear immigration at Varanasi itself, and arrive in Delhi as an international transit passenger — no baggage to collect and re-tag, no second immigration queue, no scramble across terminals. AI1111 is timed to land in Delhi around 11:00 a.m., positioned so that, within four hours, a connecting passenger can pick up one of 18 long-haul departures: London Heathrow, Frankfurt, Milan, Rome, Zurich, Singapore, Kuala Lumpur, Bangkok, Riyadh and Dubai among them.

## Why this is a structural shift, not a route launch

For two decades, the cheapest and often only way for a family in Varanasi, Lucknow or Patna to reach New Jersey or London was to route through a Gulf hub — Dubai, Doha, Abu Dhabi — on a foreign carrier. Indian aviation ceded that connecting traffic because its own airports could not process a Tier-2 passenger seamlessly onto an international flight. Easy Connect is Air India's bid, backed by the government's hub-and-spoke guidelines, to keep that traffic inside India and turn Delhi into the kind of transfer machine that Dubai has been for a generation.

CEO Campbell Wilson framed it bluntly to *businessline*: the goal is to make the world "accessible to Bharat," reducing the need for Indians to transit "through unfamiliar environments." The re-engineering required was not trivial — new immigration-at-origin protocols coordinated with the Bureau of Immigration and Customs, baggage systems that tag through to a foreign endpoint, and schedule "banks" at Delhi built to keep connection times competitive with the Gulf carriers.

## What it means for the diaspora

For Indian Americans, the payoff is felt at the other end of the family tree. The hardest leg of a trip home is rarely the ocean crossing — it is the last 400 miles to the ancestral town, and the elderly parent or in-law who has to navigate a chaotic domestic-to-international transfer alone in the opposite direction.

Easy Connect changes that calculus. A grandmother flying from Varanasi to visit family in Chicago can now check in once at her home airport, clear immigration there with help from relatives who can stand with her until the gate, and step off in Delhi already cleared for her onward flight. The single-ticket structure also means that if the Varanasi–Delhi leg is delayed, the onward international flight is Air India's problem to re-accommodate, not the passenger's — a protection that piecing together two separate tickets never offered.

Varanasi is only the start. Air India has said it will roll the model out in phases to more Tier-2 and Tier-3 cities over the coming months, with airports, government agencies and the airline working through the same immigration-at-origin plumbing city by city. For the diaspora, the watch-list is straightforward: the next spoke cities to come online — likely candidates among Lucknow, Amritsar, Ahmedabad, Coimbatore and other regional hubs with large overseas communities — will determine which relatives finally get a clean, single-ticket path to the gate.

## The catch worth knowing

Easy Connect does not add a new nonstop; it makes an existing connection seamless. The international leg still departs from Delhi, so the model's usefulness depends entirely on whether Air India's long-haul schedule serves the city the diaspora actually lives in. The 18-destination connection bank is heavy on Europe, the Gulf and Southeast Asia; North American connections from Delhi exist but are fewer and time-sensitive. Before booking a parent through Varanasi, check that the Delhi connection lands within the four-hour window onto a flight that actually goes to your city — and that the fare, sold as a single itinerary, beats the familiar Gulf-carrier alternative. For many regional travellers, for the first time, it will.
"""

# ---------------------------------------------------------------------------
# ARTICLE 2 — Argentina visa-free for Indians with a US visa / Green Card
# ---------------------------------------------------------------------------
body2 = """The Indian diaspora in America has long known the open secret of its passports: a valid US visa or Green Card is itself a travel document, unlocking Mexico, much of the Caribbean and a handful of other countries without a separate application. As of April 2026, that list quietly gained its most spectacular entry yet — Argentina.

Under a policy that took effect this spring, Indian citizens who hold a valid US visa of type B2, B1, J, O, P (P1–P3), E or H-1B — or a US Green Card — may enter Argentina without obtaining an Argentine visa in advance. For the hundreds of thousands of Indian passport-holders living and working in the United States, a country that previously required a paid, document-heavy e-visa or consular visa just became a fly-and-arrive destination.

## What the policy actually covers

The waiver is tied to the US document, not to Indian citizenship alone. An Indian national still on an Indian passport — but carrying, say, an unexpired H-1B stamp or a Green Card — qualifies. The categories are specifically enumerated: B1/B2 (business and tourism), J (exchange), O and P (the talent and performer visas), E (treaty trader/investor) and H-1B (the visa that defines a large slice of the Indian-American professional class). Crucially, the H-1B inclusion means the typical Indian software engineer in the Bay Area or the tri-state area can plan a Patagonia trip without a trip to a consulate first.

Travellers should carry the physical proof — a valid visa stamp in the passport, or the Green Card — and confirm the document's validity extends through the trip, since the entry right collapses the moment the underlying US status lapses. As with all US-document-based entry schemes, the prudent move is to verify the current terms with the airline and Argentina's immigration authority before booking, because these arrangements are revised without much fanfare.

## Why Argentina is worth the long flight

Argentina is not a quick hop — it is a 10-to-14-hour haul from the US, typically via a connection in a US gateway or São Paulo. But it rewards the distance like few places do. Buenos Aires offers a European-grade capital at a favourable exchange rate, with steak, tango and a café culture that runs past midnight. The northeast holds Iguazú Falls, a wall of water wider and, by many accounts, more overwhelming than Niagara. The south opens into Patagonia — the Perito Moreno glacier, the peaks of El Chaltén, and some of the most dramatic trekking on the planet.

For the diaspora, the calculus is about value and timing. Argentina's chronic inflation has made it, for dollar-earners, one of the cheaper world-class destinations going — a meal, a wine, a night in a good hotel all stretch unusually far on a US salary. And the seasons are flipped: when the US Northeast is buried in January snow, Buenos Aires and Patagonia are in the warm heart of their summer, making Argentina a genuine winter-escape option for an Indian-American family that has already done Cancún and the Caribbean a dozen times.

## The bigger pattern for NRI travellers

Argentina joins a growing roster of countries that treat a US visa as a fast-pass for Indian passport-holders — alongside Mexico, much of the Caribbean, and several Central American and Balkan states. The strategic lesson for the diaspora is to stop thinking of the Indian passport in isolation. For an Indian citizen living in the US, the real travel document is the *combination* of the passport and the US status, and that pairing now opens far more of the map than the Henley index, which ranks the Indian passport alone, would suggest.

The practical takeaway: before assuming a destination needs a visa run, check whether a US visa or Green Card waives it. Increasingly, for the Indian-American traveller, it does — and Argentina is the newest, and arguably the grandest, place where it now works.
"""

# ---------------------------------------------------------------------------
# ARTICLE 3 — Nepal as the diaspora's cool-weather monsoon escape
# ---------------------------------------------------------------------------
body3 = """While much of northern India swelters and the monsoon stutters across the subcontinent, a quieter travel story is unfolding just over the border. Nepal is recording a strong summer surge of Indian visitors, with hotels in Pokhara reporting near-full occupancy and the safari lodges of Chitwan posting their busiest "off-season" in years. For the Indian-American family planning the long trip home, it is a reminder that the best leg of an India vacation may not be in India at all.

## Why Nepal, why now

The driver is simple: heat. As temperatures spike across the Gangetic plains and the monsoon turns Indian cities into a slog of waterlogging and flight delays, Nepal's hill destinations offer cool air, lake views and open mountain horizons. Pokhara — cradled beneath the Annapurna range on the shore of Phewa Lake — has become the headline beneficiary, drawing both independent travellers and organised tour groups looking for an affordable, cooler holiday within easy reach.

Tour operators describe a shift in the seasonal pattern itself: what used to be a sleepy monsoon lull has turned into a profitable window. Many Indian visitors are arriving by road, others on tour buses, and a large share are stitching Nepal into multi-destination journeys that pair leisure with religious circuits — Pokhara and Phewa Lake alongside Muktinath, and Kathmandu's heritage sites. Chitwan National Park, meanwhile, is pulling wildlife-tourism demand with jeep safaris that promise one-horned rhino, elephant and rich birdlife, even through the rains.

## The diaspora advantage hiding in plain sight

Here is the part most NRIs overlook: Nepal is, for the Indian passport-holder, one of the most frictionless international trips on earth. Indian citizens need no visa to enter Nepal — a valid photo ID suffices for those crossing by land, and the open border makes it one of the few genuinely paperwork-free destinations for an Indian traveller. For a diaspora family already flying into Delhi, Lucknow or Patna to see relatives, Nepal is a short add-on that delivers a completely different landscape — high Himalaya, alpine lakes, a foreign stamp on the trip without the foreign hassle.

The seasonal logic compounds the appeal. A family arriving in India in July or August to visit aging parents will run straight into peak heat and monsoon disruption. Carving out four or five days in Pokhara or Chitwan turns the dead, sweaty middle of the trip into its highlight — and does so at monsoon-discounted rates, since this is technically Nepal's shoulder season too.

## How to do it well

A few practicalities separate a good Nepal monsoon trip from a soggy one. The rains are real: Pokhara and Chitwan see genuine downpours, so build flexible days and treat clear mountain mornings as the prize they are — the Annapurna and Machhapuchhre (Fishtail) peaks often reveal themselves at dawn before cloud closes in. Phewa Lake boat rides, the Sarangkot viewpoint and the World Peace Pagoda are the Pokhara staples; in Chitwan, the jeep safaris and canoe trips run through the season. Roads from the Indian border and from Kathmandu can be slow and slide-prone in heavy rain, so domestic flights between Kathmandu and Pokhara are worth the modest premium for anyone travelling with elderly parents or young children.

For NRIs weighing where to spend the unglamorous middle of a summer trip home, Nepal makes an unusually strong case: cooler than the plains, visa-free for the Indian passport, cheap in the monsoon, and close enough to fold into an existing itinerary. The crowds catching on this summer are the evidence — the diaspora would do well to follow the same instinct.
"""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Air India's 'Easy Connect' Starts From Varanasi June 25 — One Check-In From a Small City to the World",
        "subheadline": "A new hub-and-spoke model lets Tier-2 travellers clear immigration and check bags at home, then transit Delhi as international passengers onto 18 long-haul flights.",
        "slug": make_slug("air-india-easy-connect-varanasi-hub-spoke-tier2-international-nri"),
        "category": "travel",
        "vertical": "aviation",
        "diaspora_angle": "It gives the diaspora's elderly relatives in small Indian cities a single-ticket, single-immigration path to the gate — removing the chaotic domestic-to-international transfer that makes the last leg home the hardest part of the trip.",
        "tags": ["travel", "airlines", "air india", "varanasi", "nri"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Air India Newsroom", "url": "https://www.airindia.com/in/en/about-us/press-release.html"},
            {"name": "The Hindu BusinessLine — Air India to make foreign travel more accessible to 'Bharat'", "url": "https://www.thehindubusinessline.com/economy/logistics/air-india-to-make-foreign-travel-more-accessible-to-bharat-ai-ceo/article69000000.ece"},
            {"name": "Outlook Traveller — Air India's New 'Easy Connect' Service", "url": "https://www.outlooktraveller.com/destinations/india/air-indias-new-easy-connect-service-to-simplify-international-travel-from-varanasi"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ab/Scindia_Ghat_in_morning%2C_Varanasi%2C_Uttar_Pradesh%2C_India_%282012%29.jpg/1280px-Scindia_Ghat_in_morning%2C_Varanasi%2C_Uttar_Pradesh%2C_India_%282012%29.jpg",
        "image_caption": "Scindia Ghat on the Ganges at dawn in Varanasi, the first 'spoke' city in Air India's hub-and-spoke network",
        "image_attribution": "Wikimedia Commons",
        "body": body1
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Argentina Now Lets Indians In Visa-Free — If They Hold a US Visa or Green Card",
        "subheadline": "Since April 2026, an H-1B, B1/B2, J, O, P or E visa, or a US Green Card, opens Buenos Aires, Iguazú and Patagonia to Indian passport-holders with no Argentine visa needed.",
        "slug": make_slug("argentina-visa-free-indians-us-visa-green-card-h1b-patagonia-nri"),
        "category": "travel",
        "vertical": "immigration",
        "diaspora_angle": "For Indian citizens living in the US on an H-1B or Green Card, their US document now doubles as an Argentine entry pass — adding a world-class, dollar-friendly winter-escape destination with zero consular paperwork.",
        "tags": ["travel", "visa", "argentina", "us visa", "nri"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Wikipedia — Visa requirements for Indian citizens (2026 changes)", "url": "https://en.wikipedia.org/wiki/Visa_requirements_for_Indian_citizens"},
            {"name": "Ministry of External Affairs, Government of India", "url": "https://www.mea.gov.in/"}
        ]),
        "score_total": 76,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/54/A_view_of_Iguazu_Falls_from_the_Argentina_side.jpg/1280px-A_view_of_Iguazu_Falls_from_the_Argentina_side.jpg",
        "image_caption": "Iguazú Falls seen from the Argentine side, one of the country's marquee draws now reachable visa-free for US-visa-holding Indians",
        "image_attribution": "Wikimedia Commons",
        "body": body2
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Nepal Is Quietly Booming This Monsoon — and It's the Visa-Free Escape the Diaspora's India Trip Is Missing",
        "subheadline": "As Indian heat and rains peak, Pokhara and Chitwan are near-full with Indian visitors. For NRIs, Nepal needs no visa and folds easily into a summer trip home.",
        "slug": make_slug("nepal-monsoon-tourism-surge-pokhara-chitwan-visa-free-nri-escape"),
        "category": "travel",
        "vertical": "tourism",
        "diaspora_angle": "Nepal is visa-free for Indian passport-holders and a short add-on to any India trip — turning the hot, monsoon-disrupted middle of a summer visit home into a cool Himalayan highlight at shoulder-season rates.",
        "tags": ["travel", "nepal", "monsoon", "pokhara", "nri"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Travel And Tour World — Nepal Records Strong Summer Tourism Surge", "url": "https://www.travelandtourworld.com/news/article/nepal-now-records-strong-summer-tourism-surge-as-indian-travellers-escape-heatwaves/"},
            {"name": "Reuters — India monsoon revives after two-week stall", "url": "https://www.reuters.com/world/india/india-monsoon-revives-after-two-week-stall-heads-into-central-belt-2026-06-23/"}
        ]),
        "score_total": 70,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0c/Phewa_Lake_of_Pokhara_city.jpg/1280px-Phewa_Lake_of_Pokhara_city.jpg",
        "image_caption": "Phewa Lake at Pokhara beneath the hills, the centre of Nepal's summer tourism surge among Indian visitors",
        "image_attribution": "Wikimedia Commons",
        "body": body3
    }
]

# Word-count sanity check
for art in articles:
    wc = len(re.sub(r'[#*>\n]', ' ', art["body"]).split())
    print(f"  [{wc} words] {art['headline'][:60]}")

print("---- inserting ----")
ok = 0
for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
        ok += 1
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
print(f"DONE: {ok}/{len(articles)} inserted")

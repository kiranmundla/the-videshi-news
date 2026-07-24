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
        "headline": "Europe's New Border System Is Turning Airports Into Nightmares — and NRIs Have It Worse Than Most",
        "subheadline": "The EU's Entry-Exit System has caused multi-hour delays at airports across the Schengen zone. For Indian passport holders who already need visas, the biometric gauntlet adds another layer of pain to summer travel.",
        "slug": make_slug("eu-ees-border-system-airport-delays-nri-schengen-summer"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "Indian passport holders face a double burden: Schengen visa requirements plus new EES biometric registration, making Europe trips significantly more time-consuming at borders",
        "tags": ["travel", "europe", "schengen", "visa", "airports", "ees"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "People", "url": "https://people.com/visitors-to-europe-being-hit-with-hours-long-lines-due-to-eus-entry-exit-system-11739108"},
            {"name": "New York Post", "url": "https://nypost.com/2025/05/28/travel/european-airport-plagued-by-enormous-lines-after-new-system-causes-travel-chaos/"},
            {"name": "European Parliament", "url": "https://www.europarl.europa.eu/doceo/document/E-10-2026-000679_EN.html"},
            {"name": "The Sun", "url": "https://www.thesun.co.uk/travel/34817529/european-country-allow-brits-e-gates-skip-queues/"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/2612113/pexels-photo-2612113.jpeg",
        "body": """If you are planning a Euro summer, add two hours to your arrival time. Maybe three.

The European Union's Entry-Exit System — EES for short — went fully operational across all 29 Schengen countries on April 10, and it has turned airport arrivals into an endurance event. The system replaces the old passport stamp with a digital process that captures fingerprints, a facial scan, personal details, and exact entry and exit timestamps for every non-EU citizen crossing into the bloc.

The theory was modernisation. The reality, at least so far, is chaos.

## What happened at Lisbon

CNN's chief international correspondent Clarissa Ward posted video on May 28 of snaking immigration queues at Lisbon Airport that stretched for what she described as "the longest line I have ever seen in my life." She missed her flight. So did many others. Airport staff only let passengers on TAP Portugal flights cut the line, leaving everyone else stranded.

Ward is not alone. Travellers at Faro Airport in Portugal reported five-hour waits. Greece briefly announced it would suspend EES entirely before reversing course. Airlines across Europe have formally petitioned airports to pause the biometric checks during peak summer traffic. A European Commission spokesperson told Newsweek that the system has processed nearly 80 million crossings since launch and flagged 900 security threats — but acknowledged the "stabilisation" is still uneven.

In February, members of the European Parliament filed a formal question asking the Commission whether member states could suspend EES implementation until October 2026.

## Why NRIs have it worse

For American and British passport holders, EES is a new inconvenience layered onto what used to be a quick stamp-and-go process. For Indian passport holders, it is an additional layer on top of an already heavy process.

Indians need a Schengen visa to enter any of the 29 EES countries. That means a VFS Global appointment, biometric submission during the visa application, a stack of bank statements, insurance proof, and a two-to-four-week wait — before you even get to the airport. Now, on arrival, you face EES biometric registration again: fingerprints, facial scan, and data entry, processed at kiosks that many airports have not fully deployed.

The silver lining for frequent NRI travellers is the EU's cascade visa regime adopted in April 2024, which grants two-year and then five-year multi-entry Schengen visas to Indians with established travel histories. If you have used two Schengen visas in the past three years, you qualify. The longer visa at least means fewer VFS appointments — but it does nothing to shorten the EES queue at Charles de Gaulle.

## What NRIs should do right now

**Arrive earlier than you think.** If your airline says three hours before departure for international flights, make it four for any Schengen arrival through a busy hub. Lisbon, Barcelona, Amsterdam Schiphol, and Rome Fiumicino have all reported significant delays.

**Register on your first crossing and it gets faster.** EES captures your biometrics on the first entry. Subsequent crossings within the same trip — say, flying into Paris and then hopping to Barcelona — should be quicker since your data is already in the system.

**France is adapting fastest.** French airports including Nice are now letting non-EU passengers use e-gates after a quick pre-registration at an EES kiosk, cutting wait times dramatically. If you have flexibility on routing, consider entering the Schengen zone through a French airport.

**Use ETIAS when it launches.** The EU Travel Information and Authorisation System, expected in autumn 2026, will add a pre-travel authorisation requirement — but may eventually smooth the arrival process by front-loading some data collection.

**Fly off-peak hours.** Early morning and late evening arrivals tend to hit shorter queues. Midday arrivals at major hubs are the worst.

## The bigger picture

India is now the EU's largest source of Schengen visa applicants, with over 1.1 million applications filed annually. The diplomatic push for easier visa access — longer validity, higher approval rates — has made Europe more accessible to Indian travellers than at any point in the past decade. But the airport experience at the other end risks undoing that goodwill.

For the estimated 4.5 million Indian Americans who travel internationally each year, a significant share of whom include Europe in their itinerary, EES is a system designed for security and efficiency that has so far delivered neither on the efficiency front. Pack your patience alongside your passport."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "From Jaisalmer's Dunes to Ranthambore's Tigers — India's Luxury Hotel Boom Means NRIs No Longer Have to Settle",
        "subheadline": "The Leela, JW Marriott, Hilton, and Radisson are all opening flagship properties across India in 2026. For diaspora travellers used to five-star standards abroad, the homecoming experience is finally catching up.",
        "slug": make_slug("india-luxury-hotel-boom-leela-jaisalmer-jw-marriott-nri"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "NRIs visiting India have long faced a gap between the hospitality standards they are used to abroad and what was available domestically. The 2026 hotel opening wave closes that gap across leisure and transit destinations.",
        "tags": ["travel", "hotels", "india", "luxury", "leela", "marriott", "hilton"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Travel+Leisure Asia", "url": "https://www.travelandleisureasia.com/in/new-hotels-in-india-2026/"},
            {"name": "HOTELSMag", "url": "https://hotelsmag.com/news/the-leela-jaisalmer-to-open-in-2026/"},
            {"name": "Business Traveller", "url": "https://www.businesstraveller.com/features/the-best-new-hotels-around-the-world-february-2026/"},
            {"name": "TravMedia", "url": "https://www.travmedia.com/newsroom/press-releases/preview-marriott-internationals-most-anticipated-hotels-resorts-opening-across-asia-pacific-excluding-china-in-2026"}
        ]),
        "score_total": 75,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/4/47/Jaisalmer_forteresse.jpg",
        "body": """For years, the NRI trip back to India came with a hospitality compromise. You could stay at a heritage haveli that was atmospheric but functionally stuck in the 1990s, or book a business hotel in a commercial district that could have been anywhere in the world. Finding a property that was both distinctly Indian and genuinely world-class required either deep local knowledge or a travel agent with a very thick rolodex.

That gap is closing — and 2026 may be the year it closes for good.

## The openings that matter

**The Leela Jaisalmer** is the headline act. Spread across 30 acres of Thar Desert landscape near the UNESCO-listed Jaisalmer Fort, this 80-room property marks The Leela's first desert resort. The design trades the ornate Rajasthani heritage style for a contemporary vernacular — clean lines, tented villas set apart in the dunes for privacy, a man-made lake, and a pillarless ballroom engineered for the large-scale NRI weddings that Rajasthan has become a magnet for. The Leela now has three properties across Rajasthan's luxury circuit: Udaipur, Jaipur, and Jaisalmer, creating a seamless triangle itinerary for travellers who want to see the state without sacrificing comfort.

**JW Marriott Ranthambore Resort & Spa** opens in Q4 with 127 sanctuaries including tented suites and family tents on the edge of Ranthambore National Park. The property is pitched at families — a kids' club, safari lounge, and six distinct dining concepts including produce from an on-site JW Garden. For NRI families bringing children who have never seen a tiger outside a zoo, this is the kind of property that turns a wildlife trip from an adventure into a luxury experience.

**DoubleTree by Hilton Bengaluru Airport** is less glamorous but arguably more useful for the diaspora traveller. At 304 rooms, it is India's largest DoubleTree, positioned 15 minutes from Kempegowda International Airport in Bengaluru's Aerospace Park. For the hundreds of thousands of NRIs who transit through Bengaluru on US-India routes — particularly those connecting to smaller South Indian cities — a quality airport hotel with a pool and proper dining eliminates the uncomfortable choice between an overpriced lounge nap and a long drive into the city.

## The numbers behind the boom

India is projected to lead Asia Pacific in hotel openings through 2026, with over 610 projects and 75,000 rooms in the pipeline — 30 percent of the entire Asia Pacific total excluding China. Hotel investment volumes in India hit $401 million recently, a fourfold increase from 2022. The growth is driven by a convergence of rising domestic demand, the wedding economy, and a strategic bet by international chains that India's luxury traveller base is expanding faster than any other market in the region.

The Leela alone has 10 properties in development across Agra, Ayodhya, Bandhavgarh, Mumbai, Ranthambore, Sikkim, Srinagar, and Dubai. Radisson is targeting a property within a two-hour drive of anywhere in India, with new openings in Raipur, Hyderabad, and Ujjain in 2026. Minor Hotels plans 50 properties in India over the next decade.

## What this means for NRIs

The diaspora travel pattern to India has shifted. A decade ago, most NRI trips were family visits — fly in, stay at the ancestral home or a relative's flat, fly out. Increasingly, NRIs are combining family visits with leisure extensions: a few days in Rajasthan after the Delhi family stop, a beach week in Goa after the Bengaluru visit, a tiger safari tacked onto a Hyderabad wedding.

This pattern requires a hospitality infrastructure that simply did not exist at scale five years ago. The 2026 wave of openings fills specific gaps: desert luxury in Jaisalmer, wildlife luxury in Ranthambore, airport convenience in Bengaluru, spiritual tourism infrastructure in Ayodhya and Katra.

For the NRI planning a trip home this year, the practical takeaway is simple: book early. These properties are launching into a market where domestic demand already exceeds supply during peak seasons — October through March for Rajasthan, year-round for Bengaluru transit. The wedding season alone will consume significant inventory at the Leela Jaisalmer and JW Marriott Ranthambore.

India's luxury hospitality was once a story of a few iconic properties — the Taj in Mumbai, the Oberoi in Udaipur, the Imperial in Delhi. It is now a story of breadth. The NRI who wants a world-class stay no longer needs to limit themselves to three cities."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Vande Bharat Express Is Quietly Reshaping How NRIs Explore India — Five Routes Worth Booking",
        "subheadline": "India's semi-high-speed train network now connects pilgrimage sites, beach towns, and cultural capitals. For diaspora visitors accustomed to Amtrak and the Shinkansen, the Vande Bharat is the first Indian train that does not require lowering expectations.",
        "slug": make_slug("vande-bharat-express-nri-routes-india-travel"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "NRIs visiting India can now use Vande Bharat trains to add premium side trips to family visits — Delhi to Vaishno Devi, Chennai to Mysuru, Mumbai to Goa — without the discomfort that historically made Indian rail travel a dealbreaker for diaspora families",
        "tags": ["travel", "india", "trains", "vande-bharat", "railways", "tourism"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Newz9", "url": "https://newz9.com/explore-india-in-2026-vande-bharat-express-connects-5-must-visit-destinations/"},
            {"name": "New South Wales Tourism News", "url": "https://newsouthwalestourism.com/tourism-news/jammu-srinagar-vande-bharat-express-upgrade/"},
            {"name": "TripAdvisor", "url": "https://www.tripadvisor.ca/Attraction_Review-d10030947-Reviews-Vande_Bharat.html"}
        ]),
        "score_total": 72,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/12217338/pexels-photo-12217338.jpeg",
        "body": """The NRI relationship with Indian trains has always been complicated. There is deep nostalgia for the Rajdhani rattling through the night, chai vendors calling out at every platform, the hypnotic rhythm of the tracks. And then there is the reality of returning as an adult with children who have grown up on the Acela and finding that the nostalgia does not extend to the toilets.

The Vande Bharat Express is changing that calculation. India's semi-high-speed, fully air-conditioned train service has expanded rapidly, and the network now connects enough destinations that an NRI visiting family can realistically add a premium train trip to their itinerary without the logistical anxiety that rail travel in India traditionally involves.

## Five routes NRIs should know about

**Delhi to Katra (Vaishno Devi)** — The pilgrimage route that used to mean an overnight sleeper in a crowded berth is now a comfortable day journey. The Vande Bharat covers this corridor with automatic doors, reclining seats, charging points at every seat, and onboard catering. The Vaishno Devi shrine draws over 15 million visitors annually, and this train has driven a 25 percent increase in repeat visits according to railway ministry data. For NRI families bringing elderly parents on the yatra, the comfort gap between this and the old alternative is enormous.

**Chennai to Mysuru** — The four-hour run connects South India's tech capital to one of its most beautiful heritage cities. Bookings for Mysuru tourism packages surged 40 percent after this Vande Bharat launched. For NRIs visiting family in Chennai, Mysuru is now a genuine weekend side trip: Friday evening arrival, two days of palaces and Chamundi Hill, Sunday evening return.

**Howrah to Puri** — Puri's Jagannath Temple and its beaches have always been a draw, but getting there from Kolkata was a production. The Vande Bharat on this route has helped Odisha's accommodation bookings rise nearly 30 percent. The train makes a Puri day trip from Kolkata ambitious but possible, and an overnight stay comfortable and well-connected.

**Mumbai to Goa** — Perhaps the most anticipated route for the diaspora crowd. The coastal scenery on this corridor is spectacular — Western Ghats, Konkan coast, tunnel after tunnel through green hills. The Vande Bharat has turned what was a 10-12 hour ordeal on the Konkan Railway into a scenic journey that visitors from Mumbai are now taking for weekend getaways. Reports indicate a 35 percent jump in Mumbai-origin visitors to Goa since the train launched.

**Srinagar to Katra** — The completion of the Udhampur-Srinagar-Baramulla Rail Link was an engineering milestone, and the Vande Bharat on this route offers a premium option through some of India's most dramatic mountain terrain. An upgrade to extend the service with additional coaches is currently on hold while infrastructure modifications are completed, but the existing eight-car service continues to connect the Kashmir Valley to the pilgrimage corridor.

## What makes it different

The Vande Bharat is not the Shinkansen. It maxes out around 160 km/h, and Indian railway infrastructure means it rarely sustains that speed for long stretches. But that is not really the point. What it offers is a clean, modern, reliable train experience: automatic doors, comfortable seating, functional toilets with touchless fixtures, Wi-Fi on many services, and housekeeping staff who maintain the coaches throughout the journey.

For NRIs, the significance is less about speed and more about removing excuses. The train trip from Mumbai to Goa or Delhi to Katra was never impossible — it was just uncomfortable enough that most diaspora visitors defaulted to flying. The Vande Bharat makes the train a genuine first choice for routes under six hours, and the introduction of sleeper versions on longer routes is extending that window.

## Practical tips for booking

**Book on IRCTC** — The official Indian Railways website (irctc.co.in) is the only reliable booking platform. NRIs can register with their passport number. Book as early as possible; Vande Bharat trains fill up fast, especially on weekend departures.

**Executive Class is worth it** — The price premium over Chair Car is modest, and you get wider seats, better meals, and a quieter coach. On a four-to-six-hour journey, the difference matters.

**Check the sleeper version** — For longer routes, Vande Bharat Sleeper trains operate with berths and overnight schedules. These are a step change from the traditional AC First Class sleeper, with better bedding, privacy curtains, and individual charging points.

**Pair with a flight** — The smart NRI itinerary combines flights for the long haul (US to Delhi or Mumbai) with Vande Bharat for the regional exploration. A Delhi-Katra-Delhi Vande Bharat loop adds three days to a family visit and costs under ₹3,000 round trip.

India's rail network carries over eight billion passengers a year. For the first time, a meaningful share of those journeys can be taken in a coach that an NRI would not feel the need to apologise for to their American-born children."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

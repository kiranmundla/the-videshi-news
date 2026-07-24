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

bali_body = """Bali has spent the past two years adding paperwork to a holiday that Indians once treated as a passport-and-go affair. Now it is adding a currency rule with teeth.

Indonesian authorities this week stepped up enforcement of a long-standing law requiring that every domestic transaction — hotel nights, villa rents, tour bookings, spa treatments, scooter rentals — be settled in Indonesian rupiah. Officials in Bali and Denpasar told tourism operators that quoting or accepting foreign currency directly, including US dollars, is now under active scrutiny, with hotels and travel agencies the first in line for checks.

### What actually changed

The underlying law is not new. Indonesia has required rupiah-only settlement for domestic transactions for years. What changed on June 22 is enforcement: the provincial government is moving from polite reminders to inspections, and businesses that price services in dollars or take card payments routed through foreign accounts are the target.

For a tourist, the practical effect is narrow but real. You can still bring dollars and change them. You can still tap an international card at a licensed merchant, where the charge is processed in rupiah and your bank handles the conversion. What you cannot rely on anymore is the informal villa host or driver who quotes "$60 a night" and pockets dollars in cash — that grey economy is exactly what the crackdown is aimed at.

### Why this lands on Indian travellers specifically

Bali is not a fringe destination for Indians. It is one of the single largest outbound leisure markets from India, fuelled by direct and one-stop flights, visa-on-arrival access, and a wedding-and-honeymoon industry that books the island months in advance. For NRIs, Bali is the rare destination that works as a midpoint — close enough for relatives flying from India, exotic enough for a family already living in California or New Jersey to justify the trip.

That midpoint role is the catch. NRI families often arrive carrying US dollars rather than rupees or rupiah, expecting to convert on the ground or simply hand over greenbacks the way they might in parts of Southeast Asia. Under tighter enforcement, dollars become a thing you exchange at a licensed money-changer, not a thing you spend. Villa operators that quietly ran on dollar cash — popular with diaspora travellers booking through WhatsApp and Instagram rather than big platforms — are the most exposed to a sudden "rupiah only" conversation at checkout.

### The wider Bali paperwork stack

The currency push does not arrive alone. Indians heading to Bali in 2026 already face a stack of pre-arrival steps that did not exist a few years ago:

- **The All Indonesia arrival card**, a digital form that replaced the separate health and customs declarations, must be filed within 72 hours of arrival. It is free, but skipping it means delays at Ngurah Rai airport.
- **The tourism levy** of IDR 150,000 — roughly ₹800 — is a one-time charge per visit, payable online through the official Love Bali platform before you land.
- **Proof of funds and onward tickets** are now requested more often at immigration, a shift from Bali's old wave-through reputation.

Stack the rupiah rule on top, and the lesson for diaspora travellers is the same one that applies across Southeast Asia in 2026: visa-free does not mean friction-free.

### How to land clean

The fixes are mundane and cheap. Change a working float of rupiah at a licensed money-changer — look for the authorised Bank Indonesia logo, not the back-alley booth offering a suspiciously good rate. Pay larger bills like hotels by card so the conversion is handled by your bank at a fair rate. Pre-pay the tourism levy and file the arrival card before you fly. And if you are booking a villa through a diaspora contact rather than a platform, confirm in writing that the final bill will be in rupiah, so there is no awkward currency standoff with luggage already in the car.

None of this makes Bali harder to enjoy. It makes Bali harder to wing. For a generation of NRI travellers used to treating the island as a low-effort escape, the message from Denpasar is that the island is professionalising its tourism economy — and expects visitors to play by the same rules as everyone else.

**Sources:** Travel And Tour World; Trip.com Bali Tourist Tax guide; Pickyourtrail Bali 2026 entry checklist."""

fares_body = """If you have been quoted four figures for a summer flight home, the smartest move this year is to stop looking at summer. The cheapest window to fly from the United States to India in 2026 is opening in September — and the gap between peak-season and shoulder-season fares is wide enough to fund a domestic leg once you land.

Fare data aggregated across the major booking engines tells a consistent story. Round-trip economy from the New York area to Delhi or Mumbai is landing around \$711–\$820 for September departures, against \$1,400-plus for the same routes during the late-June to mid-July school-holiday crush. From San Francisco, September fares to Delhi sit near \$850, with Mumbai close behind — roughly \$500 below what the same itinerary commands in peak summer. Booking engines peg September as the single cheapest month to fly the India–US corridor, with March a close second.

### Why September is the sweet spot

The logic is seasonal, not magical. The summer rush — families travelling with school-age children, students flying out for the fall semester — clears by Labor Day. The festival surge around Dussehra and Diwali has not yet begun; those fares spike from mid-October. That leaves a three-to-four-week trough in September when planes still fly full schedules but demand dips, and airlines discount to fill seats.

For the diaspora, that trough overlaps with something useful: weather. September is the tail of the monsoon across most of India, which means greener landscapes, thinner tourist crowds, and the start of the pleasant pre-winter stretch in the north. A traveller who can decouple the trip home from the school calendar — retirees, remote workers, couples without young kids — has the most to gain.

### Reading the fare tables without getting fooled

A few patterns are worth internalising before you book.

**Nonstops cost a premium, but a shrinking one.** Air India's nonstops from Delhi and Mumbai to JFK, Newark, Chicago and San Francisco anchor the top of the market, but on shoulder-season dates the one-stop European and Gulf carriers — Lufthansa, Air France, Emirates, Qatar — undercut them sharply. If a 20-hour one-stop saves \$400, that is a real decision, not an obvious one.

**The cheapest fare is rarely the cheapest trip.** A \$711 JFK–Delhi headline often hides a long layover, a basic-economy fare with no checked bag, or return dates that do not match how families actually travel. Price the bag and seat before you celebrate.

**Mixed metros can beat loyalty.** Diaspora travellers tend to fly their home airport on autopilot. But a Bay Area family open to flying out of Los Angeles, or a tri-state traveller willing to use Newark instead of JFK, frequently finds the better fare. The savings can exceed the cost of the connecting hop.

### The diaspora-specific playbook

The single biggest lever NRIs control is flexibility on the India end. Fares to Delhi and Mumbai are almost always lower than to second-tier metros like Hyderabad, Bengaluru, Kochi or Ahmedabad, where September prices can run \$1,000-plus. A traveller heading to Hyderabad who books US–Delhi on the cheap international fare, then adds a separate domestic ticket on IndiGo or Akasa, often beats the through-fare — and gains a buffer night in case the long-haul leg slips.

Two cautions. Keep a comfortable connection if you self-transfer onto a separate domestic ticket; a missed link is on you, not the airline. And watch the routing: Pakistani airspace closures continue to stretch some US–India flight times past 16 hours and occasionally force a fuel stop in Europe, which can turn a "nonstop" into a longer day than the schedule implies.

### Bottom line

The cheapest seats home this year are not gone — they are in September, and to a lesser extent next March. For diaspora travellers with any latitude on dates, shifting the annual trip a few weeks past the summer wall is the closest thing to a guaranteed several-hundred-dollar saving in a market where almost nothing else is predictable.

**Sources:** momondo US–India fare data 2026; Travelocity cheap flights to India; Trip.com DEL–SFO fares."""

monsoon_body = """For most of the diaspora, the trip home is a summer ritual locked to the school calendar — fly in June, melt through July, fly back before Labor Day. It is also the worst-value way to see India. The smarter window, for anyone who can move it, is the monsoon: late June through September, when the country turns electric green, hotel rates collapse, and the crowds thin out.

The catch is knowing where the rain is a feature and where it is a problem. Monsoon India rewards the prepared and punishes the improviser. Here is where it works.

### The south: Kerala and the coffee country

Kerala is the original monsoon destination, and not by accident. The state's own tourism board markets June through August as peak season for Ayurveda, on the logic that the humid air makes the body more receptive to treatments like Panchakarma. For an NRI carrying a parent who wants a genuine wellness reset rather than a spa afternoon, this is the season to book a proper clinic stay in Kochi or the backwater belt.

Beyond the treatment table, Munnar's tea plantations turn an almost unreal green, and the Alleppey backwaters swell to their fullest for houseboat cruises. Across the border in Karnataka, Coorg — the "Scotland of India" — delivers coffee-estate walks and waterfalls at full roar. Wayanad in northern Kerala has reopened to visitors and offers misty forests with a fraction of Munnar's crowds, though the Chooralmala–Mundakkai area remains restricted after the 2024 landslides.

### The Western Ghats: weekend range from Mumbai and Pune

For NRIs basing a trip around family in Mumbai or Pune, the Ghats are a two-hour escape. Lonavala and Mahabaleshwar deliver waterfalls and valley views with easy highway access; Malshej Ghat draws flamingos and cloud-level drives; and Matheran, India's only car-free hill station, is reached by toy train or a short trek — a genuine novelty for diaspora kids raised on American road trips. Goa in the monsoon is its quiet alter ego: empty beaches, emerald interiors, steeply discounted hotels, and the Sao Joao festival in late June.

### The dramatic north and northeast

Two destinations justify a longer detour. The **Valley of Flowers** in Uttarakhand, a UNESCO World Heritage site, blooms only during the monsoon — 600-plus alpine species across a single short season, paired with the Hemkund Sahib pilgrimage nearby. And **Cherrapunji** in Meghalaya, among the wettest places on earth, offers the living-root bridges and thundering Nohkalikai Falls at their most spectacular. Both are for travellers who treat the rain as the point, not an inconvenience.

### Udaipur: the palace city, transformed

Rajasthan in summer is brutal and dry. In the monsoon, Udaipur's lakes — Pichola and Fateh Sagar — fill to the brim, the Aravalli hills green over, and the palace reflections that fill every postcard finally appear. For a diaspora traveller who skipped Rajasthan because of the heat, this is the workaround.

### What the monsoon demands of you

The savings and the scenery come with rules, and diaspora travellers — often planning from abroad with thin local knowledge — get caught most.

- **Build slack into the itinerary.** Landslides and waterlogging close Ghat roads and hill routes with little warning. Do not stack tight connections or single-night stops in hill country.
- **Pack for it properly.** A real raincoat, waterproof footwear, and a dry bag for electronics beat the souvenir umbrella every time.
- **Mind the flights.** The same monsoon that greens the hills snarls domestic aviation. Leave a long buffer between any domestic hop and an international departure — a delayed Kochi–Delhi leg should never threaten your flight back to the US.
- **Skip the wrong places.** The monsoon is miserable in the desert proper and along the storm-lashed open coast. Choose hills, backwaters, and lakes, not exposed beaches on red-alert days.

For families chained to the summer calendar, none of this is actionable this year. But for the growing share of NRIs who work remotely, travel without school-age kids, or simply want their rupees and their photographs to go further, the monsoon is India at its most beautiful and its best value — provided you respect the rain.

**Sources:** Wego Travel Blog, Best Monsoon Destinations in India 2026; Tripoto monsoon destinations; Triveni Cabs monsoon road trips guide."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Bali Just Started Enforcing Its Rupiah-Only Rule — and the NRI Dollar No Longer Works at the Villa Door",
        "subheadline": "Indonesia is cracking down on foreign-currency payments across Bali's tourism economy. For diaspora travellers used to spending dollars on the island, it's one more layer in a holiday that keeps getting more paperwork.",
        "slug": make_slug("bali-rupiah-only-enforcement-foreign-currency-nri-dollar-villa"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "Bali is one of the largest outbound leisure destinations for Indians and NRIs, and many diaspora travellers arrive carrying US dollars expecting to spend them directly — a habit the new rupiah-only enforcement now penalizes.",
        "tags": ["travel", "bali", "indonesia", "visa", "currency", "southeast-asia"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/bali-and-denpasar-tighten-tourism-payment-rules/"},
            {"name": "Trip.com — Bali Tourist Tax 2026", "url": "https://sg.trip.com/guide/info/bali-tourist-tax.html"},
            {"name": "Pickyourtrail — Bali Trip Checklist for Indians 2026", "url": "https://pickyourtrail.com/blog/bali-trip-checklist-for-indians"}
        ]),
        "score_total": 76,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8d/TanahLot_2014.JPG/1280px-TanahLot_2014.JPG",
        "image_caption": "Tanah Lot temple on the coast of Bali, one of the island's most-visited landmarks",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": bali_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The Cheapest Flights Home to India in 2026 Aren't in Summer — They're in September",
        "subheadline": "Shoulder-season fares from New York and San Francisco to Delhi and Mumbai are running hundreds of dollars below the summer crush. For NRIs who can move the trip off the school calendar, the savings are real.",
        "slug": make_slug("cheapest-flights-india-september-2026-shoulder-season-fares-nri"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "Most NRI families fly home in summer at peak prices because of the school calendar; this lays out the September fare trough and a booking playbook that can save diaspora travellers several hundred dollars per ticket.",
        "tags": ["travel", "airlines", "flight-deals", "air-india", "fares"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "momondo — Cheap Flights from the US to India 2026", "url": "https://www.momondo.com/cheap-flights/united-states/india/"},
            {"name": "Travelocity — Cheap Flights to India", "url": "https://www.travelocity.com/lp/flights/178294/india-flights"},
            {"name": "Trip.com — DEL to SFO Flights 2026", "url": "https://www.trip.com/flights/new-delhi-to-san-francisco/airfares-del-sfo/"}
        ]),
        "score_total": 72,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/36681344/pexels-photo-36681344.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "An airport departure board displaying international flight information",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": fares_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Skip the Summer Crush: The Monsoon Is India's Best-Value Season — If You Know Where the Rain Is a Feature",
        "subheadline": "Green hills, half-price hotels, and empty trails from June to September — but the monsoon rewards the prepared and punishes the improviser. A diaspora guide to where the rain works.",
        "slug": make_slug("monsoon-travel-india-2026-best-value-destinations-nri-guide"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "NRIs overwhelmingly fly home in summer at peak cost; this guide makes the case for monsoon travel and flags the connection-planning and packing pitfalls that catch diaspora travellers planning from abroad.",
        "tags": ["travel", "monsoon", "india-tourism", "kerala", "destinations"],
        "urgency": "low",
        "sources": json.dumps([
            {"name": "Wego Travel Blog — Best Monsoon Destinations in India 2026", "url": "https://blog.wego.com/best-monsoon-destinations-in-india/"},
            {"name": "Tripoto — Top 5 Monsoon Destinations in India", "url": "https://www.tripoto.com/india/trips/top-5-monsoon-destinations-in-india"},
            {"name": "Triveni Cabs — Monsoon Road Trips in North India 2026", "url": "https://trivenicabs.in/blog/monsoon-road-trips-north-india"}
        ]),
        "score_total": 68,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b9/Munnar_Overview.jpg/1280px-Munnar_Overview.jpg",
        "image_caption": "Tea plantations covering the hills of Munnar in Kerala, lush during the monsoon season",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": monsoon_body
    }
]

for art in articles:
    wc = len(art["body"].split())
    print(f"… {art['slug']} ({wc} words)")
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

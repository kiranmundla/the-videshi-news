#!/usr/bin/env python3
"""Travel writer for The Videshi — July 12, 2026 run."""
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
    # ── ARTICLE 1: Navi Mumbai Airport Goes International ──
    {
        "id": str(uuid.uuid4()),
        "headline": "Navi Mumbai Airport Gets Its First International Flight on Tuesday",
        "subheadline": "Air India Express will fly twice weekly to Abu Dhabi from July 15, making Maharashtra's newest airport an international gateway — and giving Mumbai's eastern suburbs a far shorter ride to the Gulf.",
        "slug": make_slug("navi-mumbai-airport-first-international-flight-abu-dhabi"),
        "category": "travel",
        "vertical": "aviation",
        "diaspora_angle": "For NRIs from Navi Mumbai, Thane, and Pune — especially the large Maharashtrian and Gujarati diaspora in the Gulf — this eliminates the painful trek across Mumbai to Chhatrapati Shivaji airport.",
        "tags": ["travel", "airlines", "airports", "navi-mumbai", "air-india-express", "uae"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com/economy/logistics/air-india-express-launches-navi-mumbai-abu-dhabi-flights-from-july-15/article69719946.ece"},
            {"name": "Travel and Leisure Asia", "url": "https://www.travelandleisureasia.com/in/getting-there/air-india-express-navi-mumbai-abu-dhabi-flights/"},
            {"name": "Travel Trade Journal", "url": "https://www.traveltradejournal.com/air-india-express-becomes-first-airline-to-launch-international-flights-from-navi-mumbai-airport/"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/62/Navi_Mumbai_Airport_%2896252%29.jpg/1280px-Navi_Mumbai_Airport_%2896252%29.jpg",
        "image_caption": "Navi Mumbai International Airport terminal building in Maharashtra",
        "image_attribution": "Wikimedia Commons",
        "body": """Seven months after opening its doors to domestic travellers, Navi Mumbai International Airport is about to stamp its first overseas passport.

Air India Express will launch direct flights between Navi Mumbai and Abu Dhabi on July 15, becoming the first airline to operate international services from Maharashtra's newest airport. The route starts with two weekly flights — Wednesdays and Fridays — stepping up to three per week from July 29 with an added Sunday service.

## A Second Gateway for Mumbai's Millions

The timing is deliberate. Navi Mumbai airport, which began domestic operations in December 2025, currently handles about 20,000 passengers daily across 149 flights to 46 destinations. Services are expected to double to 300 daily flights by the winter schedule. Adding international operations marks the next phase of what the Adani Group-managed facility hopes will become a full-service aviation hub for western India.

For the Mumbai Metropolitan Region — home to roughly 25 million people — the practical impact is straightforward. Residents of Navi Mumbai, Thane, Panvel, and the eastern suburbs no longer need to cross the city to reach Chhatrapati Shivaji Maharaj International Airport for a Gulf flight. In a city where an airport commute can take two hours in traffic, that is not a minor convenience.

The schedule is built around early-morning slots: the Navi Mumbai departure leaves at 2:55 AM local time and arrives in Abu Dhabi at 4:35 AM, while the return departs Abu Dhabi at 5:45 AM and lands at 10:20 AM. The red-eye timing follows the established pattern for India-Gulf routes, optimised for business travellers and those connecting onward from Abu Dhabi.

## Why the Gulf Route First

The choice of Abu Dhabi as the inaugural international destination is no accident. Western India has one of the country's densest concentrations of Gulf-bound travellers — workers, business operators, and families visiting relatives across the UAE, Saudi Arabia, Oman, and Bahrain. Air India Express already operates one of India's largest networks to West Asia, connecting multiple cities with destinations across six Gulf states.

With the Abu Dhabi service, Air India Express will operate 30 weekly flights from Navi Mumbai, connecting the airport to Abu Dhabi, Bengaluru, and Delhi. The airline's Maharashtra footprint now includes over 95 weekly flights from Mumbai's main airport, more than 100 from Pune, and 14 from Nagpur.

## What It Means for NRIs

For the Indian diaspora in the Gulf — estimated at over 8.5 million people, the largest expatriate community in the region — Navi Mumbai adds a second gateway to one of India's busiest travel corridors. Maharashtrian and Gujarati families who have long endured congested terminals and cross-city drives now have an alternative that is closer to home and, for the moment, far less crowded.

The airport also plans to launch freighter operations from July 15, with cargo services expected to ramp up to 18 flights per week. For NRI entrepreneurs shipping goods between India and the Gulf, that adds a logistics dimension that Mumbai's main airport has struggled to expand.

Both Air India Express and IndiGo are expected to expand international operations from Navi Mumbai in the coming months. More Gulf routes are likely first, followed by Southeast Asian destinations as the airport's runway and terminal capacity scales up.

The question is no longer whether Navi Mumbai can compete with Mumbai's legacy airport. It is how quickly it can absorb the demand that the older facility can barely contain."""
    },

    # ── ARTICLE 2: Air India Slashes US Routes ──
    {
        "id": str(uuid.uuid4()),
        "headline": "Air India Cuts Flights to Chicago, San Francisco, and Toronto as Fuel Costs Bite",
        "subheadline": "India's flag carrier has suspended Delhi-Chicago entirely and reduced frequencies on other key North American routes through August, leaving diaspora travellers scrambling for alternatives during peak summer.",
        "slug": make_slug("air-india-cuts-us-routes-fuel-costs-diaspora"),
        "category": "travel",
        "vertical": "aviation",
        "diaspora_angle": "The Delhi-Chicago suspension and SFO/Toronto reductions directly hit NRI corridors — Chicago has one of America's largest Indian populations, and SFO serves the Bay Area's massive tech diaspora.",
        "tags": ["travel", "airlines", "air-india", "us-india-flights", "diaspora-routes", "fuel-prices"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Air India Newsroom", "url": "https://www.airindia.com/in/en/newsroom.html"},
            {"name": "Reuters", "url": "https://www.reuters.com/business/aerospace-defense/indigo-air-india-cut-june-july-domestic-flights-amid-high-jet-fuel-prices-sources-2026-05-27/"},
            {"name": "LiveMint", "url": "https://www.livemint.com/companies/news/air-india-cuts-international-flights-fuel-costs-airspace-closures-11746168671289.html"},
            {"name": "Aviation Week", "url": "https://aviationweek.com/air-transport/routes-networks/routes-networks-latest-rolling-daily-updates-wc-july-6-2026"}
        ]),
        "score_total": 85,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/5/55/Air_India%2C_VT-ANP%2C_Boeing_787-8_Dreamliner.jpg",
        "image_caption": "An Air India Boeing 787-8 Dreamliner on the tarmac",
        "image_attribution": "Wikimedia Commons",
        "body": """If you are planning to fly Air India to the United States this summer, check your booking again. India's flag carrier has quietly slashed its North American schedule, and some of the cuts land squarely on the routes Indian Americans use most.

## The Damage

Air India has announced what it calls a "temporary rationalisation" of its international network through August 2026. The full list of North American reductions reads like a map of the Indian diaspora:

- **Delhi-Chicago**: temporarily suspended entirely
- **Delhi-San Francisco**: reduced from 10 weekly flights to 7
- **Delhi-Toronto**: cut from 10 weekly to 5 through July, rising to daily in August
- **Delhi-Vancouver**: reduced from 7 weekly to 5
- **Mumbai-New York (JFK)**: frequency reductions on select dates

The airline says it will continue operating more than 1,200 international flights per month, including 33 weekly flights to North America. But those aggregate numbers mask the pain on specific city pairs. Chicago — home to one of America's largest Indian populations, anchored by suburbs like Naperville, Schaumburg, and Skokie — loses its only nonstop link to India entirely.

## What Is Driving the Cuts

Two forces are squeezing Air India simultaneously. The first is jet fuel prices, which have surged in the wake of the West Asia conflict. Fuel accounts for up to 40% of airline operating expenses, and the spike has been especially punishing for long-haul flights.

The second is the continued closure of Pakistani airspace, which forces India-bound flights from Europe and North America to take longer, more expensive routing. Air India's CEO Campbell Wilson told staff that the combination has rendered many international routes commercially unviable. The airline group recorded estimated losses exceeding ₹22,000 crore in the financial year ended March 2026.

IndiGo, India's largest domestic carrier, has also trimmed 7-10% of its domestic flights for the period. But its international network, which skews toward shorter Gulf and Southeast Asian routes, has been less affected.

## What NRIs Should Do

Affected passengers are being offered rebooking on alternative Air India flights, free date changes, or full refunds. The airline's 24/7 contact centre and digital channels are handling requests. But rebooking options are limited — the remaining SFO flights are likely to fill fast, and Chicago passengers may need to route through Newark or connect via a Gulf carrier.

A few practical alternatives for diaspora travellers on disrupted routes:

**Chicago**: United operates nonstop Delhi-Newark daily; from there, connections to O'Hare are plentiful. Emirates and Qatar Airways both serve Chicago with one-stop options via Dubai or Doha, though at higher fares. Air India's own Newark service remains intact.

**San Francisco**: With seven weekly flights still operating, the route is not gone — just tighter. United flies Delhi-SFO nonstop and remains unaffected. Singapore Airlines via Changi is a popular alternative.

**Toronto**: The cut to five weekly flights through July is painful for the large Punjabi and Gujarati communities in the Greater Toronto Area. Air Canada's Delhi-Toronto nonstop continues, and the frequency rises again in August.

## The Bigger Picture

Air India is midway through a multibillion-dollar transformation under Tata Group ownership, including fleet renewal with new Boeing 787-9 aircraft, cabin retrofits, and service upgrades. The irony is that the cuts come just as the airline's product is improving — retrofitted 787s with modern cabins are replacing older jets on routes like Mumbai-London and Delhi-Melbourne.

The airline insists the reductions are temporary. "Air India will continue to monitor demand and operating conditions closely, with a view to restoring frequencies as conditions stabilise," a spokesperson said.

For the 4.4 million Indian Americans who travel between the US and India every year, "temporary" cannot come soon enough."""
    },

    # ── ARTICLE 3: Georgia for NRIs ──
    {
        "id": str(uuid.uuid4()),
        "headline": "Georgia Is Europe's Best-Kept Secret for NRIs — and Your US Visa Gets You In",
        "subheadline": "Indian visitor arrivals to Georgia surged 40% last year. Visa-free entry for US, UK, and Schengen visa holders, direct IndiGo flights from Delhi, and costs that undercut Western Europe by half are turning Tbilisi into a diaspora favourite.",
        "slug": make_slug("georgia-europe-hidden-gem-nri-visa-free-travel"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "NRIs holding US, UK, or Schengen visas can enter Georgia visa-free for up to a year — no additional paperwork, no e-visa fees. Combined with IndiGo's nonstop Delhi-Tbilisi flights and costs 50-60% below Western Europe, it's an ideal short-break for diaspora families.",
        "tags": ["travel", "georgia", "visa-free", "europe", "nri-travel", "tbilisi", "budget-travel"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Travel and Tour World", "url": "https://www.travelandtourworld.com/news/article/georgia-joins-indias-growing-outbound-travel-boom/"},
            {"name": "Meridian Nomad", "url": "https://meridiannomad.com/georgia-visa-free-indian-citizens/"},
            {"name": "VisaVerge", "url": "https://www.visaverge.com/immigration-news/georgia-introduces-visa-free-entry-for-indian-citizens-with-global-visas/"},
            {"name": "Wego Travel Blog", "url": "https://blog.wego.com/indigo-international-flights/"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ae/20110421_Tbilisi_Georgia_Panoramic.jpg/1280px-20110421_Tbilisi_Georgia_Panoramic.jpg",
        "image_caption": "Panoramic view of Tbilisi, Georgia's capital, with the Kura River and historic Old Town",
        "image_attribution": "Wikimedia Commons",
        "body": """There is a European country where your Indian passport and US visa are all you need to walk through immigration. Where a three-course dinner with Georgian wine costs under $15. Where the landscape shifts from Caucasus snow peaks to Black Sea beaches in a four-hour drive. And where Indian visitor numbers jumped 40% last year.

Georgia is not on most NRI travel lists yet. It should be.

## The Visa Advantage

The single biggest draw for Indian Americans: if you hold a valid US visa, UK visa, or Schengen visa, Georgia grants you visa-free entry for up to 365 days per year. No application, no fee, no embassy appointment. You show your Indian passport and qualifying visa at Tbilisi airport, and you are in.

This is not a new policy, but awareness among NRIs remains surprisingly low. Georgia extended visa-free access to Indian citizens with qualifying third-country visas in mid-2025, and the policy remains in force through 2026. For NRIs who already carry a US B1/B2, H-1B, or green card, it means one of Europe's most photogenic countries is as accessible as Mexico or the Caribbean.

For Indian citizens without a qualifying visa, Georgia offers an e-visa through evisa.gov.ge — approximately $20-50, processed in 5-10 working days. Not quite as frictionless, but far simpler than a Schengen application.

## Getting There

IndiGo now flies nonstop from Delhi to Tbilisi, part of the carrier's aggressive push into Central Asian and Caucasus destinations. The A321XLR-powered route puts Tbilisi within roughly five hours of Delhi — shorter than most flights to Southeast Asia. IndiGo also connects Tbilisi from Mumbai with one stop in Delhi.

Georgian tourism officials completed roadshows in Chennai and Bengaluru earlier this month under the tagline "Yeh Dil Phir Jeene Laga," pitching the country to southern India's tour operators. The outreach is deliberate: Georgia's National Tourism Administration reported that Indian visitor arrivals increased 40% in the most recent year, building on 5.8 million total international visitors in 2025.

## What Your Dollar Buys

The cost advantage over Western Europe is dramatic. A mid-range hotel in Tbilisi runs $40-70 per night — less than half what a comparable room costs in Paris, London, or Rome. A meal at a traditional Georgian restaurant, including khinkali dumplings, khachapuri cheese bread, and a bottle of Saperavi wine from the Kakheti region, comes to $10-15 per person.

Georgia's currency, the lari, has remained stable against the dollar, keeping costs predictable for NRIs paid in USD. A week in Georgia — flights excluded — can comfortably run under $500 per person, a fraction of what a comparable Western European trip demands.

## Why NRIs Should Care

Beyond the price and the visa convenience, Georgia offers something harder to quantify: a destination that feels genuinely different from the standard NRI travel circuit of London-Dubai-Singapore-Bangkok.

The country sits at the crossroads of Europe and Asia, and its culture reflects both. Orthodox churches perch on cliffsides above Soviet-era apartment blocks. The wine tradition predates France's by thousands of years — Georgia claims 8,000 years of continuous viticulture, with qvevri clay-pot fermentation now on UNESCO's intangible heritage list. The food is robust, meat-heavy, and instantly familiar to Indian palates that appreciate bread, cheese, and dumplings.

For families, the Caucasus mountains offer summer hiking and winter skiing. The Black Sea coast around Batumi has resort infrastructure that caters to budget-conscious travellers. And Tbilisi itself — with its sulphur baths, winding old town, and rapidly modernising restaurant scene — is compact enough to explore in two to three days.

## Practical Tips

A few things NRIs should know before booking:

**Insurance is mandatory.** Georgia requires valid travel and health insurance for entry. Buy it before you fly — policies are cheap and available from Indian insurers.

**Carry documentation.** Even with visa-free entry, immigration may ask for return tickets, proof of accommodation, and evidence of sufficient funds. Have these on your phone or printed.

**Mind the calendar.** The 365-day visa-free stay is generous, but it applies per rolling year. Overstays carry fines and future entry bans.

**Connectivity is good.** Wi-Fi is strong across Tbilisi, and local SIM cards with data are available at the airport for under $5.

Georgia may not stay off the radar forever. Indian tour operators are already packaging Tbilisi alongside Baku and Yerevan for Caucasus multi-country trips, and IndiGo's route expansion suggests the airline sees sustained demand. For NRIs looking for a European break that does not require a Schengen visa, a second mortgage, or a two-week vacation, Georgia is the answer hiding in plain sight."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['headline']}")
        print(f"   slug: {art['slug']}")
    except Exception as e:
        print(f"❌ {art['headline']}")
        print(f"   Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"   Response: {e.response.text[:500]}")

print(f"\nDone. {len(articles)} articles submitted for review.")

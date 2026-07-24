#!/usr/bin/env python3
"""Travel writer — 2026-07-08 10:00 PT batch"""
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
    # -------------------------------------------------------------------
    # Article 1: Air India route restoration + fuel surcharge cuts
    # -------------------------------------------------------------------
    {
        "id": str(uuid.uuid4()),
        "headline": "Air India Is Reviewing Route Restorations — and Slashing Fuel Surcharges by $80",
        "subheadline": "After months of cuts to key NRI corridors like Delhi-Chicago, Delhi-SFO, and Delhi-Newark, the Tata-owned carrier says easing Gulf tensions and cheaper fuel could bring flights back. Meanwhile, surcharges on North America and Europe routes have already dropped.",
        "slug": make_slug("air-india-route-restoration-fuel-surcharge-cut-nri"),
        "category": "travel",
        "vertical": "aviation",
        "diaspora_angle": "NRIs on the US East and West Coasts who rely on Air India's direct Delhi flights have faced suspensions and reduced frequencies since June. Restoration of these routes and lower surcharges directly affect fall travel plans to India.",
        "tags": ["travel", "airlines", "air-india", "flights", "fuel-surcharge", "nri"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "The Indian Eye", "url": "https://theindianeye.com/2026/06/28/air-india-reviewing-resumption-of-international-flights-paused-due-to-gulf-war/"},
            {"name": "Travel and Tour World", "url": "https://www.travelandtourworld.com/news/article/0vyjuqxhx423/"},
            {"name": "Skift", "url": "https://skift.com/2026/05/13/air-india-scales-back-international-flights/"},
            {"name": "Air India Newsroom", "url": "https://airindia.com/press-releases/air-india-rationalises-international-route-network"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fc/VT-JRF_-_Airbus_A350-941_-_Air_India_LHR_200326.jpg/1280px-VT-JRF_-_Airbus_A350-941_-_Air_India_LHR_200326.jpg",
        "image_caption": "An Air India Airbus A350-941 on the tarmac at London Heathrow Airport",
        "image_attribution": "Wikimedia Commons",
        "body": """If you've been tracking Air India's international schedule this summer, the view has been grim. Delhi-Chicago — suspended. Delhi-Newark — suspended. Mumbai-JFK — gone. Delhi-San Francisco — trimmed from ten weekly flights to seven. Delhi-Toronto — halved.

Now, after weeks of disruption, there are signs the carrier is preparing to reverse course.

## What Happened

In May, Air India announced one of its broadest international schedule pullbacks since the Tata Group took over in 2022. The airline cited two converging pressures: airspace restrictions over parts of the Middle East following the West Asia conflict, and record-high jet fuel prices that made several long-haul routes commercially unviable.

The cuts were surgical but consequential. North America bore the brunt: Delhi-Chicago was temporarily suspended entirely. Delhi-Newark and Mumbai-JFK followed. Frequencies on Delhi-San Francisco, Delhi-Toronto, and Delhi-Vancouver were all reduced. European routes took hits too — Delhi-Paris was halved from 14 weekly flights to seven, and services to Copenhagen, Vienna, Zurich, and Rome were trimmed.

Despite the reductions, Air India maintained over 1,200 international flights per month — 33 weekly to North America, 47 to Europe, 57 to the UK, and eight to Australia.

## The Turnaround Signal

Air India CEO Campbell Wilson confirmed the airline is now reviewing its international network and may restore some of the suspended services. Two factors are driving the reassessment: easing tensions in the Gulf have improved airspace availability, and a decline in global fuel prices has improved the economics of long-haul flying.

"The decision will depend on operational feasibility, passenger demand and continued stability in the region," Wilson said.

The Gulf's airspace is critical — many international routes between India and Europe or North America route through it. When that corridor was restricted, airlines had to take longer paths, burning more fuel and adding flight time. With conditions stabilising, the math on these routes is changing.

## Fuel Surcharges Already Falling

Even before route restoration, NRIs are seeing a financial benefit. Air India has cut its fuel surcharge across all three major diaspora corridors:

- **North America**: Surcharge reduced from approximately $280 to $200 — an $80 cut per ticket
- **Europe**: Down from roughly $205 to $125 — also an $80 reduction
- **Australia**: Matching the North America cut, from $280 to $200

On key routes like Delhi-San Francisco, Delhi-New York, Mumbai-Toronto, Delhi-London, and Delhi-Sydney, the lower surcharge translates to meaningfully cheaper tickets. For families booking four or five round-trips for a holiday visit home, that adds up.

## What NRIs Should Watch

The next few weeks will be telling. Air India's route rationalization runs through August 2026, but the airline's language has shifted from defending cuts to exploring restorations. If Gulf stability holds and fuel prices stay down, routes like Delhi-Chicago and Delhi-Newark could return before the busy Diwali travel season.

In the meantime, Mumbai-Newark has actually been upgraded — from three weekly flights to daily service — to absorb some of the displaced traffic. Delhi-JFK continues at seven weekly flights.

For NRIs planning fall travel to India, the advice is straightforward: book on routes that are currently operating (Delhi-SFO, Delhi-JFK, Mumbai-Newark), watch for restoration announcements on suspended routes, and take advantage of the lower surcharges while they last. The corridor is recovering — slowly, but in the right direction."""
    },
    # -------------------------------------------------------------------
    # Article 2: Thailand visa changes
    # -------------------------------------------------------------------
    {
        "id": str(uuid.uuid4()),
        "headline": "Thailand Just Cut Visa-Free Stays Back to 30 Days — What NRIs Need to Know",
        "subheadline": "The 60-day visa-free entry that made Thailand an easy getaway for Indian passport holders is gone. Here's the new paperwork, the cash-carry requirement, and why your next trip needs more planning than the last one.",
        "slug": make_slug("thailand-visa-30-days-india-nri-travel-advisory"),
        "category": "travel",
        "vertical": "visa-policy",
        "diaspora_angle": "Thailand is one of the most popular vacation destinations for NRIs visiting from the US, especially families planning stopovers before or after India trips. The halved visa-free stay and new documentation rules change how NRIs should plan these holidays.",
        "tags": ["travel", "visa", "thailand", "nri", "immigration"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Outlook Traveller", "url": "https://www.outlooktraveller.com/News/planning-a-thailand-trip-indian-embassy-issues-fresh-travel-advisory-for-visitors"},
            {"name": "Reuters", "url": "https://www.reuters.com/world/asia-pacific/thailand-cut-visa-free-stay-30-days-tourists-93-countries-2026-05-13/"},
            {"name": "Travel and Tour World", "url": "https://www.travelandtourworld.com/news/article/thailand-surpasses-vietnam-singapore/"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/30540817/pexels-photo-30540817.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Bangkok skyline with traditional Thai architecture alongside modern buildings",
        "image_attribution": "Pexels",
        "body": """Thailand is no longer the effortless getaway it was six months ago — at least not on paper.

In May 2026, Thai authorities rolled back the generous 60-day visa-free stay that had been introduced in July 2024 for nationals of 93 countries, including India. The new limit is 30 days. And that's not the only change: a fresh travel advisory from the Indian Embassy in Bangkok adds several documentation requirements that travellers need to sort before they board.

For the 1.19 million Indians who have already visited Thailand in the first half of 2026 alone, this is a meaningful shift. For NRIs accustomed to using Thailand as an easy family holiday or a stopover between the US and India, it means a bit more homework.

## The New Rules

The headline change is the visa-free stay. Indian passport holders can still enter Thailand without a pre-approved visa, but the window has been halved to 30 days. Anyone planning a longer trip — and multi-week holidays in Phuket or Chiang Mai are popular with Indian families — will need to apply through the Thai eVisa portal in advance.

Beyond the duration, here's what's new or newly enforced:

**Thailand Digital Arrival Card (TDAC):** This is now mandatory. Travellers must complete the form online within 72 hours of landing. It generates a QR code that immigration officials may scan at arrival. This replaces the old paper arrival card.

**Cash-carry requirement:** Immigration authorities can ask visitors to show proof of sufficient funds. The threshold is THB 20,000 per person in cash — roughly ₹58,000 or about $700. This isn't new to international travel (many countries have it), but Thailand is now enforcing it more visibly.

**Documentation checklist:** The embassy advisory asks travellers to carry confirmed return tickets, hotel bookings, and a clear itinerary. Each person in a family or group should carry their own documents — immigration won't accept one person holding everything for a party.

## Why the Rollback?

Thailand's foreign minister, Sihasak Phuangketkaeow, framed the change as a security measure. The 60-day window, while great for tourism, had been exploited — with some visitors using tourist entry to work illegally or overstay. Between January and May 2026, Thailand received 12.4 million foreign tourists, down 3.4% year-on-year, but authorities are prioritising compliance over volume.

Tighter arrival regulations have also been paired with strengthened immigration checks to manage overstays. Transit passengers now need to carry all onward tickets, visas, and documents for their final destination, as Thai officials may verify them at arrival.

## The NRI Angle

For Indian Americans, Thailand trips often fit into a specific pattern: a five-to-seven-day break in Bangkok, Phuket, or Krabi tacked onto an India visit. The 30-day window is more than sufficient for that. The bigger change is the paperwork.

NRIs who hold US passports won't face these restrictions — the US is typically on a different visa-free tier. But for those travelling on Indian passports (including OCI holders who also carry Indian travel documents), the new rules apply in full.

If you're an NRI planning to bring parents or extended family who hold Indian passports, the TDAC requirement and cash-carry threshold are worth flagging early. Getting turned away at immigration for missing a QR code is the kind of holiday-ruiner nobody needs.

## Practical Checklist

Before your next Thailand trip on an Indian passport:

1. Confirm your passport has at least six months' validity from your arrival date
2. Complete the TDAC online form within 72 hours of departure — save the QR code
3. Carry at least THB 20,000 (~$700) in cash per person
4. Have return tickets, hotel bookings, and a day-by-day itinerary printed or readily accessible
5. If staying more than 30 days, apply through the Thai eVisa portal before travelling
6. If you have a Thai job offer, get a proper employment visa — entering on tourist status for work violates immigration rules

Thailand still wants Indian tourists. It welcomed 2.49 million Indian visitors in 2025 and expects about the same this year, generating an estimated $2.8 billion in tourism revenue. India is one of its top three source markets. But the days of showing up at Suvarnabhumi with nothing but a passport and a vague plan are over."""
    },
    # -------------------------------------------------------------------
    # Article 3: India outbound travel boom
    # -------------------------------------------------------------------
    {
        "id": str(uuid.uuid4()),
        "headline": "Everyone Wants Indian Tourists — 32.7 Million Trips and $55 Billion Says Why",
        "subheadline": "From Thailand to Australia to Japan, countries are rewriting tourism strategy around India's booming outbound market. A Livemint analysis shows the numbers — and why Germany just scrapped transit visas for Indian travellers.",
        "slug": make_slug("india-outbound-tourism-boom-global-competition-nri"),
        "category": "travel",
        "vertical": "tourism",
        "diaspora_angle": "The global competition for Indian tourists is reshaping visa policies and airline routes that directly benefit NRIs travelling between the US and India — or anywhere else. Germany's new visa-free airport transit and new Lufthansa routes are particularly relevant for diaspora travellers connecting through European hubs.",
        "tags": ["travel", "tourism", "india", "outbound", "visa", "germany", "nri"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Livemint", "url": "https://www.livemint.com/companies/news/india-outbound-travel-international-tourism-west-asia-war-overseas-travel-indian-tourists-thailand-tourism-11783222543135.html"},
            {"name": "Breaking Travel News", "url": "https://www.breakingtravelnews.com/news/article/lufthansa-group-welcomes-visa-free-airport-transit-for-indian-nationals-via/"},
            {"name": "Travel and Tour World", "url": "https://www.travelandtourworld.com/news/article/thailand-surpasses-vietnam-singapore/"},
            {"name": "Japan National Tourism Organization", "url": "https://www.jnto.go.jp/"}
        ]),
        "score_total": 75,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/12717154/pexels-photo-12717154.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Passengers checking a departure board at an international airport terminal",
        "image_attribution": "Pexels",
        "body": """India is no longer just a market that tourism boards occasionally court with brochures. It has become the market everyone is redesigning their strategy around.

The numbers are hard to argue with. Indian nationals made 32.71 million overseas departures in 2025, up 5.9% from 30.89 million the previous year, according to India's Ministry of Tourism. In just the first quarter of 2026, the Directorate General of Civil Aviation recorded 19.07 million international passenger movements — 9.77 million outbound, 9.3 million inbound. And a FICCI-Nangia report projects India's outbound tourism market will nearly triple, from $18.8 billion in 2024 to $55.4 billion by 2034.

That kind of growth has countries competing for Indian arrivals the way they once competed for Chinese tourists.

## The Destination Scramble

Thailand remains the dominant short-haul choice. Between January and June 2026, 1.19 million Indians visited the country — on track for 2.5 million for the full year, generating an estimated $2.8 billion in tourism revenue. India is one of Thailand's top three source markets. Despite recent visa tightening, the fundamentals — high-frequency flights, affordability, and cultural familiarity — keep it on top.

Japan recorded an all-time high of 315,100 Indian visitors in 2025, up from 233,000 the year before — a 35% jump driven by K-pop-adjacent cultural curiosity, food tourism, and the falling yen making luxury travel more accessible.

Australia is seeing Indians spend more, not just visit more. Close to 450,000 Indian visitors arrived in the year ending March 2026, spending A$2.5 billion ($1.61 billion). India's arrivals have grown at a compound annual rate of 10.3% since 2010, outpacing Australia's overall inbound tourism growth of 8%. The country's Economic Strategy projects 1.2 million Indian visitors by 2035.

Singapore received over 1.21 million Indian visitors in 2025, with the tourism board now expanding outreach beyond India's metros into tier-I cities to attract first-time visitors. South Korea saw Indian arrivals climb to nearly 200,000, up 13% year-on-year. Even South Africa — not an obvious choice — welcomed close to 70,000 Indian visitors in 2025.

In the US, India was the second-largest overseas source market in 2025, with 2.06 million visitors, and ranked third between January and May 2026.

## The Visa Wars

Countries aren't just running ad campaigns. They're changing immigration policy.

Germany abolished airport transit visa requirements for Indian nationals travelling via German airports, effective June 3, 2026. This is a practical win for the millions of Indian-passport holders who connect through Frankfurt and Munich en route to other European destinations. Previously, even a two-hour layover in Germany required a transit visa — a friction point that pushed travellers toward Dubai, Doha, or Istanbul hubs instead.

The Lufthansa Group, which operates more than 70 weekly flights between India and Europe, called the move a reinforcement of "Germany's role as a leading gateway between India, Europe and the world." The group is also deploying its new Allegris business cabins on Boeing 787-9 services from Delhi and Hyderabad, and launching SWISS's first-ever Bengaluru-Zurich nonstop in the winter 2026 schedule.

Thailand, despite tightening its rules, still offers visa-free entry for up to 30 days. Vietnam has seen 18% year-on-year growth in Indian arrivals. Indonesia is growing at 15%. The competition is real and structural.

## What This Means for the Diaspora

For NRIs, the global competition for Indian tourists translates into tangible benefits: more direct routes, cheaper fares, easier visa processes, and better airline products on India-linked corridors. Germany's transit visa removal alone makes European stopovers far more practical for anyone on an Indian passport.

The broader trend — India replacing Russia and China as the world's most sought-after source market — also means tourism boards are increasingly tailoring offerings to Indian preferences. Vegetarian-friendly hotels, Bollywood-themed events, Hindi-language tourism apps, and curated heritage-plus-shopping itineraries are becoming standard rather than niche.

As one luxury travel operator put it: "In the post-war period, all eyes have turned to India. Outbound travel is no longer confined to standard hotel and sightseeing bookings — it now extends into wellness, culinary, sports, and experiential tourism."

For a diaspora that straddles two worlds, this is a good problem to have. The world is getting easier to navigate on an Indian passport — slowly, unevenly, but unmistakably."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

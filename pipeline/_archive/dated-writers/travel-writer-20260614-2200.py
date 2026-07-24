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
        "headline": "Vietnam Is Stealing Thailand's Crown — and NRIs Are Leading the Charge",
        "subheadline": "Thailand's reinstated visa fees and overtourism are pushing Indian travelers toward Vietnam's cheaper e-visas, uncrowded beaches, and surprisingly good phở.",
        "slug": make_slug("vietnam-stealing-thailand-crown-nri-travelers"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "NRI families planning Southeast Asian holidays are finding Vietnam delivers more for the rupee — and the e-visa process is far simpler than Thailand's reinstated airport queues.",
        "tags": ["travel", "vietnam", "thailand", "visa", "southeast-asia", "nri"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Travel and Tour World", "url": "https://www.travelandtourworld.com/news/article/rfl5ekummce8/"},
            {"name": "Wego Travel Blog", "url": "https://blog.wego.com/vietnam-visa-free-countries/"},
            {"name": "Vietnam National Authority of Tourism", "url": "https://vietnamtourism.gov.vn/"}
        ]),
        "score_total": 80,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/7/79/Ha_Long_Bay_in_2019.jpg",
        "image_caption": "Limestone karsts rising from emerald waters at Ha Long Bay, Vietnam",
        "image_attribution": "Wikimedia Commons",
        "body": """For the better part of two decades, Thailand was the default international holiday for Indian families looking to spend a week abroad without breaking the bank. Phuket, Krabi, Bangkok — the playbook was well-worn. But 2026 is rewriting the script, and the new destination of choice has a different area code entirely: Vietnam.

The numbers tell the story before anyone else can. Indian visitor arrivals to Vietnam have surged past 500,000, a year-on-year jump exceeding 60 percent. That makes India one of Vietnam's fastest-growing source markets — and it's happening at the exact moment Thailand is losing its grip on the budget-conscious Indian traveler.

## Thailand's Own Goal

The catalyst is straightforward. Thailand ended its temporary visa-free arrangement for Indian passport holders and reinstated a Visa-on-Arrival fee of 2,000 Thai Baht — roughly ₹5,500 per person. For a solo backpacker, that's a mild annoyance. For a family of four, it's ₹22,000 before you've even left the airport.

The timing couldn't have been worse for Bangkok. The fee returned just as overtourism complaints in Phuket and Pattaya reached a fever pitch — longer queues at temples, packed beaches, and hotel rates that no longer feel like a steal.

Vietnam, meanwhile, went the opposite direction. Its fully digital e-visa system lets Indian travelers apply online, get approval within days, and skip airport queues entirely. The 90-day validity with single or multiple entry options gives it a flexibility that Thailand's system simply doesn't match.

## The Value Equation Has Flipped

Cost comparisons between the two countries now consistently favor Vietnam. Mid-range hotels in Da Nang and Hoi An run 20-30 percent cheaper than equivalent properties in Phuket. Street food in Hanoi — arguably the best in Southeast Asia — costs a fraction of what you'd spend in Bangkok's tourist zones. And domestic flights within Vietnam on carriers like VietJet and Bamboo Airways are remarkably cheap, making multi-city itineraries practical even on tight budgets.

For NRIs accustomed to converting dollars to rupees to local currency and mentally benchmarking everything, Vietnam's pricing feels like a revelation. A luxury resort experience in Nha Trang that would cost $200 a night in Koh Samui runs closer to $80-100 in Vietnam.

## Beyond Beaches: Why Vietnam Keeps NRIs Coming Back

Thailand's tourism pitch has always leaned heavily on beaches and nightlife. Vietnam offers something broader. Ha Long Bay's limestone karsts are a UNESCO World Heritage Site that photographs like nowhere else on earth. Hoi An's lantern-lit ancient town feels like stepping into a living museum. Sapa's terraced rice fields in the northern highlands offer trekking that rivals anything in Nepal — at a tenth of the altitude sickness risk.

The food is the clincher. Vietnamese cuisine — fresh, herb-heavy, and endlessly varied — resonates deeply with Indian palates accustomed to complex flavors. Phở for breakfast, bánh mì for lunch, and a seafood feast in Da Nang for dinner, all for under $15 a day.

## What NRIs Should Know Before Booking

The practical details matter. India doesn't have extensive direct flight connectivity to Vietnam yet — most routes go through Bangkok, Singapore, or Kuala Lumpur. IndiGo and VietJet have been adding capacity on the Delhi-Hanoi and Mumbai-Ho Chi Minh City corridors, and one-stop options through Singapore keep fares competitive at $350-500 roundtrip from major Indian cities.

The e-visa application is at [evisa.xuatnhapcanh.gov.vn](https://evisa.xuatnhapcanh.gov.vn) — the official portal. Processing takes 3-5 business days, so apply at least two weeks before travel. For NRIs with US green cards or valid US visas, the process is even simpler, as several transit hubs offer visa-free stopovers.

Vietnam's monsoon season runs from May through October in the south and September through January in the north, so timing matters. The sweet spot for NRI families planning a summer trip is central Vietnam — Da Nang and Hoi An get their best weather from June through August.

## The Bigger Picture

The Thailand-to-Vietnam shift isn't just about one country losing share to another. It reflects a broader maturation in how Indian travelers — particularly NRIs with higher disposable income and more travel experience — evaluate destinations. Convenience, authenticity, and value are winning over brand familiarity.

Thailand isn't going anywhere. It still has decades of tourism infrastructure, a massive hotel inventory, and Bangkok remains one of Asia's great cities. But for the growing number of Indian families asking "where should we go this year?" — Vietnam is increasingly the answer that keeps coming up."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Abu Dhabi Is Quietly Becoming the Most Important Airport in Every NRI's Journey",
        "subheadline": "A new mega-alliance wave at Zayed International links IndiGo's domestic network to Condor, Etihad, Air France, and British Airways — giving Indian travelers one-ticket access to 200+ global destinations.",
        "slug": make_slug("abu-dhabi-mega-hub-nri-indigo-etihad-alliance"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "NRIs connecting through Abu Dhabi can now book single-ticket journeys from tier-2 Indian cities to European destinations via IndiGo and its alliance partners — cheaper and faster than routing through Delhi or Mumbai.",
        "tags": ["travel", "airlines", "abu-dhabi", "indigo", "etihad", "nri", "connectivity"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Travel and Tour World", "url": "https://www.travelandtourworld.com/news/article/3tmlhaodl9lr/"},
            {"name": "Aviation Week Network", "url": "https://aviationweek.com/air-transport/airlines-lessors/indigo-introduces-new-direct-flights-abu-dhabi"},
            {"name": "Wego Travel Blog", "url": "https://blog.wego.com/indigo-abu-dhabi-flights/"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0c/Abu_Dhabi_%28UAE%29%2C_Zayed_International_Airport%2C_Terminal_A_%2803%29.jpg/1280px-Abu_Dhabi_%28UAE%29%2C_Zayed_International_Airport%2C_Terminal_A_%2803%29.jpg",
        "image_caption": "Terminal A at Zayed International Airport in Abu Dhabi",
        "image_attribution": "Wikimedia Commons",
        "body": """There was a time when connecting through Abu Dhabi meant one thing: an Etihad flight with a long layover and an overpriced airport sandwich. That era is emphatically over. Zayed International Airport is transforming into something far more ambitious — a global super-hub where budget Indian carriers, European leisure airlines, and Gulf megacarriers converge to create routing options that didn't exist two years ago.

The latest catalyst arrived at the IATA Annual General Meeting in Rio de Janeiro, where German leisure carrier Condor and Etihad Airways announced a major expansion of their partnership. The centerpiece: a new daily Condor service between Abu Dhabi and Bangkok, operated under Fifth Freedom rights with Airbus A330neo aircraft. But the real story isn't the Bangkok route — it's what it signals about Abu Dhabi's role as the connective tissue of global aviation.

## The Alliance That Isn't Called an Alliance

What's forming at Zayed International Airport defies traditional airline categorization. It's not Star Alliance. It's not oneworld. It's something newer and, for passengers, potentially better.

The lineup now includes Etihad as the anchor carrier, Condor operating daily widebody rotations from Frankfurt and Berlin, Air France running coordinated transatlantic schedules, British Airways connecting high-yield premium traffic from Heathrow, and TAROM feeding Eastern European cities like Bucharest, Cluj-Napoca, and Sofia into the hub. At the bottom of this stack, doing the heaviest lifting for Indian travelers, sits IndiGo.

India's largest airline has expanded aggressively into Abu Dhabi, with over 100 weekly flights from 15 Indian cities before the recent Gulf airspace disruptions. Key routes connect Delhi, Mumbai, Hyderabad, Kochi, Bengaluru, Chennai, Kozhikode, Lucknow, and Ahmedabad directly to Zayed International — and from there, to everywhere.

## Why This Matters for NRIs

The math is simple. An NRI family in Kochi wanting to visit relatives in Frankfurt used to face two options: an expensive nonstop on Lufthansa or Air India through Delhi, or a budget IndiGo flight to Dubai followed by a separate ticket on a European carrier. Both involved hassle, multiple bookings, and the risk of misconnected bags.

The Abu Dhabi hub model changes this equation. IndiGo's coordinated scheduling with Etihad's partner network means a traveler from Kochi, Hyderabad, or Ahmedabad can now book a single-ticket journey through Abu Dhabi to Frankfurt, Paris, London, or Bucharest — with bags checked through and connection times under 45 minutes.

For the large Malayali, Telugu, and Gujarati diaspora communities that have historically relied on Gulf airports as transit points, this isn't just a convenience upgrade. It's a fundamental restructuring of how India connects to Europe and beyond.

## The Numbers Behind the Hub

Abu Dhabi Airports has logged 19 consecutive quarters of double-digit passenger growth, pushing annual traffic beyond 33 million. Much of that growth is being driven by Indian traffic — IndiGo alone was feeding thousands of passengers daily into the hub before Gulf airspace restrictions temporarily reduced capacity.

Those restrictions, triggered by the US-Iran conflict in February 2026, disrupted Middle East routing for weeks. But IndiGo has been steadily restoring services, prioritizing Delhi and Mumbai rotations first, with secondary cities coming back online on a rolling basis. The temporary setback may have actually accelerated the hub's development, as airlines that had been weighing Abu Dhabi partnerships were forced to commit during the recovery phase.

## What's Different About This Model

Traditional airline alliances — Star Alliance, SkyTeam, oneworld — are membership clubs with extensive bureaucracies, shared IT systems, and rigid rules. What's emerging at Abu Dhabi is lighter and more pragmatic. Airlines keep their independence, integrate their loyalty programs selectively (Etihad Guest members can earn and redeem across Condor's network), and coordinate schedules without surrendering commercial autonomy.

For passengers, the practical result is the same: seamless connections, through-checked bags, and loyalty points that actually accumulate. For airlines, it means faster market entry without the overhead of a formal alliance.

Condor's deployment of Fifth Freedom rights — flying commercially between two countries that are neither its home base — demonstrates how creative the routing has become. A German airline flying Abu Dhabi to Bangkok using an Airbus A330neo, selling individual tickets to passengers connecting from an Indian low-cost carrier. Five years ago, that sentence would have needed a footnote. In 2026, it's just how the hub works.

## The NRI Playbook

For Indian Americans planning trips home or onward to Europe, Abu Dhabi deserves a serious look as a transit hub. Etihad's premium lounge access, the new Terminal A's modern facilities, and connection times that rival or beat Dubai make it competitive for both business and leisure travelers.

The sweet spot is tier-2 connectivity. If you're flying from a US city to Kochi, Ahmedabad, or Hyderabad, Abu Dhabi routing via Etihad and IndiGo often undercuts the Delhi connection on Air India — and the single-terminal experience at Zayed International is considerably less chaotic than IGI Terminal 3.

As more partner airlines pile into the hub — and IndiGo continues restoring its pre-conflict network — Abu Dhabi's position as the NRI traveler's most versatile transit point is only going to strengthen."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India's First Vande Bharat Sleeper Launches Between Mumbai and Bengaluru — and NRIs Should Care",
        "subheadline": "The overnight train connecting India's financial capital to its tech hub will run at 160 km/h with airline-style sleeper berths, and it's the beginning of a rail revolution NRIs will actually use.",
        "slug": make_slug("vande-bharat-sleeper-mumbai-bengaluru-nri-rail"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "NRIs visiting family in Mumbai or Bengaluru — India's two largest diaspora origin cities — now have a premium overnight rail option that rivals short-haul flights and eliminates airport hassle.",
        "tags": ["travel", "india", "railways", "vande-bharat", "mumbai", "bengaluru", "nri"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Travel and Leisure Asia", "url": "https://www.travelandleisureasia.com/in/news/mumbai-bengaluru-travel-set-to-get-faster-with-new-vande-bharat-sleeper/"},
            {"name": "Metro Rail News", "url": "https://metrorailnews.in/centre-approves-jammu-srinagar-vande-bharat-express-to-halt-at-anantnag/"},
            {"name": "The Kashmir Horizon", "url": "https://thekashmirhorizon.com/2026/06/11/vande-bharat-express-route-diverted-via-gurdaspur-batala-weekly-off-changed-to-saturday/"}
        ]),
        "score_total": 75,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/5/5a/Vande_Bharat_Express_around_Mumbai.jpg",
        "image_caption": "A Vande Bharat Express train near Mumbai",
        "image_attribution": "Wikimedia Commons",
        "body": """Indian Railways has spent decades promising world-class train travel. For most of that time, "world-class" meant marginally cleaner sheets on Rajdhani Express berths. But the Vande Bharat Sleeper launching between Mumbai's Chhatrapati Shivaji Maharaj Terminus and Bengaluru's KSR station marks something genuinely different — and for the millions of NRIs who shuttle between India's financial capital and its tech hub every year, it's worth paying attention to.

The new service, approved in April 2026 by Railway Minister Ashwini Vaishnaw and confirmed for operations beginning this month, will cover the Mumbai-Bengaluru corridor at speeds up to 160 km/h. That's not bullet-train territory, but it's a significant jump from the 12-16 hours the existing overnight trains take on this route. The Vande Bharat Sleeper is expected to cut that to roughly 8-9 hours — making it competitive with flying when you factor in airport commutes, security lines, and the inevitable delays at Mumbai's perpetually congested CSMIA.

## What Makes This Train Different

The Vande Bharat Sleeper isn't just a faster version of the Rajdhani. It represents a fundamentally different approach to overnight rail travel in India.

The trains feature semi-high-speed bogies designed for smoother rides at sustained higher speeds. Sleeper berths are wider and better insulated than existing designs, with individual reading lights, charging points at every berth, and bio-vacuum toilets that actually function. The sound insulation — a notorious weakness on Indian overnight trains — has been significantly upgraded.

Think of it as the difference between a budget hotel and a boutique one. The bones are similar, but the execution is a generation ahead.

Maharashtra Chief Minister Devendra Fadnavis publicly thanked Prime Minister Modi and Railway Minister Vaishnaw for the approval, calling it a "good news" moment for both cities. The political enthusiasm isn't just ceremony — the Mumbai-Bengaluru corridor carries some of the highest passenger volumes in the country, and the existing train options have been inadequate for years.

## The NRI Calculation

For NRIs visiting India, the Mumbai-Bengaluru corridor is one of the most-traveled domestic routes. Families split between the two cities, tech workers with offices in both, and the constant flow of business travel between Dalal Street and Koramangala make this one of India's most commercially significant connections.

Flying has been the default for time-pressed travelers, but anyone who's endured the 5 AM taxi to Mumbai airport, the security queue, the inevitable fog delay (in winter) or thunderstorm delay (in monsoon), and then the crawl from Bengaluru's KIA to the city center knows the real travel time is often 5-6 hours door to door.

The Vande Bharat Sleeper offers a different proposition: board at a city-center station after dinner, sleep in a proper berth, and arrive in the city center the next morning. No airport transfers. No baggage carousel. No 6 AM wake-up call. For NRIs who've experienced European sleeper trains — the Nightjet between Vienna and Berlin, or the Caledonian Sleeper in Scotland — the appeal is immediately obvious.

## Part of a Bigger Expansion

The Mumbai-Bengaluru sleeper is part of a broader Vande Bharat rollout that's reshaping India's rail map. The Jammu-Srinagar Vande Bharat, which launched regular service in May 2026, has already been expanded from 8 to 20 coaches to meet surging demand. Railway Minister Vaishnaw recently approved a new halt at Anantnag, connecting one of Kashmir's key economic hubs to the high-speed network.

Meanwhile, the Katra-Amritsar Vande Bharat resumes June 16 with a new route through Gurdaspur and Batala — a boon for pilgrims heading to Vaishno Devi who previously had to reach Jammu or Pathankot first.

The common thread across all these expansions is a shift from "trains as transport for people who can't afford flights" to "trains as a premium travel choice." For NRIs accustomed to European or Japanese rail standards, India's network is finally starting to close the gap.

## What to Watch

The Mumbai-Bengaluru Vande Bharat Sleeper's success will hinge on execution. Indian Railways has a history of launching premium services that gradually deteriorate — the Tejas Express, for instance, started strong but maintenance issues eroded its reputation within months.

The key metrics to watch: on-time performance (the existing trains on this route average 70-80 percent punctuality), cleanliness standards at the 6-month mark, and whether the sleeper berths hold up to the volume of passengers this corridor generates.

Ticket pricing hasn't been finalized, but existing Vande Bharat services price at a modest premium over Rajdhani — typically ₹1,500-2,500 for a chair car. Sleeper berths will likely land in the ₹2,500-4,000 range, making it significantly cheaper than last-minute flights on the same route.

For NRIs who've been quietly envious of Japan's Shinkansen or Europe's TGV network, the Vande Bharat Sleeper isn't quite that. But it's the first Indian train that doesn't require an apology when you describe it to friends abroad. And on the Mumbai-Bengaluru corridor, that's a bigger deal than it sounds."""
    },
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

#!/usr/bin/env python3
"""Travel writer for The Videshi — 2026-06-07 14:00 UTC run."""
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
        "headline": "Delhi's Second Airport Opens for Business Next Week — and NRIs Finally Have a Way Around IGI's Chaos",
        "subheadline": "Noida International Airport at Jewar begins commercial flights on June 15, giving the 60-million-strong NCR region a second gateway and the Indian diaspora a long-overdue alternative to India's most congested terminal.",
        "slug": make_slug("noida-jewar-airport-commercial-flights-nri"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "NRIs flying into Delhi-NCR have long endured IGI's overcrowded terminals and two-hour immigration queues. Jewar offers a fresh entry point — especially for those headed to Noida, Greater Noida, Agra, or anywhere along the Yamuna Expressway corridor.",
        "tags": ["travel", "airports", "noida", "delhi", "infrastructure", "indigo"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Wikipedia - Noida International Airport", "url": "https://en.wikipedia.org/wiki/Noida_International_Airport"},
            {"name": "Bhaskar English", "url": "https://bhaskarenglish.in"},
            {"name": "NewsPoint - Akasa Air bookings", "url": "https://newspointapp.com"},
            {"name": "Medium - Jewar Airport analysis", "url": "https://medium.com"}
        ]),
        "score_total": 85,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/4/4e/Prime_Minister_of_Bharat%2C_Shri_Narendra_Damodardas_Modi_at_the_inauguration_ceremony_of_the_Noida_International_Airport%2C_Jewar.jpg",
        "image_caption": "Prime Minister Modi at the inauguration of Noida International Airport at Jewar in March 2026",
        "image_attribution": "Wikimedia Commons",
        "body": """India's National Capital Region is about to stop being a one-airport town. On June 15, Noida International Airport — built on the flat farmland of Jewar in Uttar Pradesh's Gautam Buddha Nagar district — will open its runway to paying passengers for the first time. IndiGo will operate the inaugural flight, with Akasa Air and Air India Express following within days.

The airport, inaugurated by Prime Minister Narendra Modi on March 28, has been a decade in the making. Phase one delivers a single 3,900-metre runway — long enough for wide-body jets — and a terminal designed for 12 million passengers annually. Operated by a subsidiary of Zurich Airport International, it carries the IATA code DXN and positions itself as the second node in Delhi-NCR's dual-airport system, mirroring models in London, New York, and Shanghai.

## What's flying on day one

IndiGo's launch schedule prioritises high-traffic domestic routes: Mumbai, Bengaluru, Hyderabad, and Lucknow. Akasa Air has already opened bookings for daily nonstop service to Navi Mumbai and Bengaluru starting June 16, with four daily flights priced competitively against IndiGo's Delhi offerings.

Air India Express is expected to announce its schedule shortly. International services — likely beginning with Dubai, Singapore, and Zurich — are targeted for late 2026 once the terminal's international processing infrastructure clears regulatory approval.

## Why NRIs should pay attention

For the Indian diaspora, Jewar is more than an airport — it is an escape from the bottleneck that Indira Gandhi International has become. IGI handled 73 million passengers in 2025, well above its designed capacity, resulting in immigration queues that routinely stretch past two hours during peak arrivals.

Jewar's immediate catchment is different from IGI's, and that matters. If your family is in Noida, Greater Noida, Ghaziabad, Agra, or Mathura, this airport is closer by an hour or more. The Yamuna Expressway provides direct road access, and metro connectivity is planned for the next phase.

For NRIs who have routed through Delhi for decades simply because it was the only option, the arithmetic is about to change. Once international flights launch, a Kannadiga in New Jersey flying to Bengaluru may find Jewar's shorter security lines worth the stopover — even if the initial route options are limited.

## The bigger picture

India is in the middle of an airport-building spree that has few parallels globally. Navi Mumbai Airport opened earlier this year. Daman's NAMO Airport was inaugurated on June 5. Bihar is building five airports simultaneously. Jewar is the most consequential of these because of the sheer density of the population it serves — an estimated 60 million people within a two-hour drive.

The airport's four-phase master plan envisions an eventual capacity of 70 million passengers per year, which would make it one of Asia's largest. For now, Phase one is modest but functional. Airlines are watching load factors closely; if demand materialises as expected, frequency increases could come as soon as the winter schedule.

## What to expect if you book

Ticketing is live on IndiGo and Akasa Air's websites and through major OTAs. Terminal facilities are new but basic — expect limited lounge options and food and beverage outlets in the opening weeks. Road access is smooth via the Yamuna Expressway, but ride-hailing availability from Jewar may be inconsistent initially, so pre-arranged transport is advised.

For NRIs planning summer trips home, the immediate value proposition is straightforward: if your destination is anywhere in western UP or the eastern NCR belt, Jewar will likely save you time, frustration, and possibly money compared to routing through IGI's Terminal 3."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India's Banks Are Locking Airport Lounges Behind Spending Walls — and NRIs Flying Home Will Feel the Squeeze",
        "subheadline": "HDFC, ICICI, Axis, and SBI have all tightened lounge access rules in 2026, turning what was once a free perk into a spend-to-earn privilege — and the changes hit hardest during peak summer travel.",
        "slug": make_slug("india-airport-lounge-access-credit-card-changes-nri"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "NRIs who maintain Indian credit cards for travel convenience — especially HDFC Regalia, Diners Club, and ICICI premium cards — are about to discover their complimentary lounge access depends on quarterly spending they may not hit while living abroad.",
        "tags": ["travel", "airports", "credit-cards", "lounge", "hdfc", "banking"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Outlook Money", "url": "https://outlookmoney.com"},
            {"name": "Desidime - HDFC changes", "url": "https://desidime.com"},
            {"name": "Bajaj Finserv Markets - Lounge guide", "url": "https://bajajfinservmarkets.in"},
            {"name": "NPCI RuPay guidelines", "url": "https://npci.org.in"}
        ]),
        "score_total": 72,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/2612117/pexels-photo-2612117.jpeg",
        "image_caption": "A premium airport lounge with leather seating — a perk that Indian banks are increasingly restricting",
        "image_attribution": "Pexels",
        "body": """Walk into any Indian airport lounge in 2025 and you would have seen a familiar scene: premium credit card holders breezing past the desk with a quick card tap, no questions asked. In 2026, that tap may not work — and the reason has nothing to do with your card being declined.

India's largest banks have spent the first half of this year systematically dismantling the free lounge access that made premium credit cards worth their annual fees. The changes are incremental, but their combined effect is significant: what was once a guaranteed perk is now a conditional benefit tied to how much you spend each quarter.

## The HDFC overhaul

Starting July 1, 2026, HDFC Bank's Regalia Gold cardholders must spend at least ₹60,000 in the preceding quarter to unlock three domestic lounge visits. Miss that threshold between April and June, and your July-to-September lounge access simply vanishes. The six international visits per year through Priority Pass remain untouched — for now.

HDFC's Diners Club Privilege card faces similar conditions: two domestic and one international lounge visit per quarter, gated behind the same spending requirement. BizPower users are capped at two visits per quarter regardless.

To soften the blow, HDFC has introduced the "Boarding Edge Programme" for Regalia Gold users — upload your boarding pass on the SmartBuy portal and choose two benefits per quarter, including complimentary spa access, Uber airport transfers, or hotel upgrades. It is a creative workaround, but not a replacement for the frictionless lounge swipe.

## The industry-wide pattern

HDFC is not acting alone. ICICI Bank and Axis Bank introduced spend-based conditions on select cards earlier this year. Most eligible Axis Bank credit card holders now need ₹50,000 in transactions over the previous three months to access domestic lounges for free. Axis went further and removed lounge access entirely from its Airtel co-branded card starting April 2026.

SBI Card restructured its domestic lounge programme from January 2026, splitting participating lounges into two tiers — Set A and Set B — with card-specific eligibility rules that require a spreadsheet to decode.

The most dramatic cut came from the debit card side. The National Payments Corporation of India revised its guidelines to strip complimentary lounge access — both domestic and international — from RuPay Platinum debit cardholders as of April 1, 2026. Punjab National Bank confirmed the same for its Mastercard Platinum debit cards from June 1.

## Why this hits NRIs differently

If you live in the US, UK, or Canada and maintain an Indian credit card primarily for trips home, the quarterly spend threshold is a trap. Your card may sit unused for months between visits, making it nearly impossible to hit ₹60,000 in the quarter before your summer trip. The irony is sharp: the people who most value lounge access during 14-hour layovers at Delhi or Mumbai are the least likely to qualify under the new rules.

The workaround is obvious but inconvenient — route your Indian subscriptions, insurance premiums, or family utility payments through the card to build up qualifying spend. Some NRIs have started using their Regalia cards for online purchases on Indian e-commerce platforms, shipped to family addresses, to maintain the threshold.

## The infrastructure shuffle

Behind the scenes, the lounge ecosystem has been quietly rewired. DreamFolks, the aggregator that once handled lounge access for most Indian banks, discontinued its domestic lounge services in September 2025. Banks now contract directly with lounge operators — Encalm, Travel Food Services, and Adani Lounges — which has fragmented the experience.

At Adani-operated airports like Ahmedabad, Lucknow, and Jaipur, you now need the Adani One app with your card registered. At GMR airports — Delhi, Hyderabad, Bengaluru Terminal 2, and Goa Mopa — it is the HOI app. At TFS-operated lounges in Mumbai, Kolkata, and Chennai, your physical card still works. The unifying QR code system that DreamFolks provided is gone.

The practical advice: download Adani One and HOI before you reach the airport. The registration requires an OTP to your Indian mobile number, which can be a problem if your Indian SIM is not active.

## The silver lining

There is one quiet improvement amid the restrictions. Because banks now pay lounge operators directly rather than through DreamFolks' margin, some have actually increased their free visit allocations. HDFC expanded Regalia coverage from eight to twelve domestic visits per year in early 2026 — you just have to earn them now.

For NRIs unwilling to play the spending game, the HDFC Marriott Bonvoy card — launched in June 2026 — offers 12 domestic and 12 international lounge visits with no spend conditions. The annual fee is steep, but for frequent India travelers, the math may work out."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Indian Airlines Are Quietly Winning the International Sky — and NRIs Are the Biggest Beneficiaries",
        "subheadline": "IndiGo now commands 17.6% of India's international market share, Air India is resurgent under Tata, and Middle Eastern carriers that once dominated diaspora routes are losing ground for the first time in a decade.",
        "slug": make_slug("indian-airlines-international-market-share-nri"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "For two decades, NRIs had little choice but to route through Dubai, Doha, or Abu Dhabi to reach tier-2 Indian cities. The rise of IndiGo and Air India's Tata-era transformation means more nonstop options, competitive pricing, and routes that actually match where the diaspora lives and where their families are.",
        "tags": ["travel", "airlines", "indigo", "air-india", "emirates", "market-share"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Indian Eye", "url": "https://theindianeye.com"},
            {"name": "Aviation A2Z - IndiGo international traffic", "url": "https://aviationa2z.com"},
            {"name": "DGCA - April 2026 traffic data", "url": "https://dgca.gov.in"},
            {"name": "Brightsun Travel - Air India 2026 routes", "url": "https://brightsun.co.in"}
        ]),
        "score_total": 78,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4d/IndiGo_Airbus_A320neo_F-WWDG_%28to_VT-ITI%29_%2828915135713%29.jpg/3840px-IndiGo_Airbus_A320neo_F-WWDG_%28to_VT-ITI%29_%2828915135713%29.jpg",
        "image_caption": "An IndiGo Airbus A320neo — the airline now carries more international passengers than any other Indian carrier",
        "image_attribution": "Wikimedia Commons",
        "body": """Something has shifted in the competitive order of international aviation from India, and for once, the shift favours the people who fly the most: the diaspora.

Fresh data from the Directorate General of Civil Aviation shows IndiGo carried approximately 870,000 international passengers in April 2026, narrowly overtaking the Air India group's 850,000. Together, the two Indian carrier groups now command a combined share that would have been unthinkable five years ago — well over 30% of all international capacity from India, eating directly into the dominance of Emirates, Qatar Airways, and Etihad.

Emirates' share has slipped to around 8.3%, down from double digits just three years ago. The Gulf carrier's slide is not about service quality — it remains one of the world's finest airlines — but about geography, pricing, and the simple mathematics of a market that Indian carriers now understand better than anyone.

## How IndiGo got here

IndiGo's international playbook has been aggressive and deliberate. The airline added dozens of destinations over the past two years, from Central Asian capitals to Southeast Asian beach towns. It now holds approximately 17.6% of India's international market share — making it the single largest carrier for international flights from India, a title that belonged to Emirates for the better part of a decade.

The strategy relies on volume and frequency rather than premium cabins. IndiGo's A321neo fleet offers competitive fares on routes where Gulf carriers charge a premium for a one-stop itinerary that adds six hours of travel time. For a family of four flying Delhi to Bangkok, the ₹15,000-per-ticket difference between a nonstop IndiGo flight and a Dubai-routed Emirates connection adds up fast.

That said, IndiGo is not immune to the pressures of international operations. The airline announced the temporary suspension of six routes — Hong Kong, Shanghai, Ho Chi Minh City, Langkawi, Krabi, and Siem Reap — between July and September 2026, citing rising fuel costs, airspace restrictions from the ongoing West Asia situation, and softer seasonal demand. The Manchester route from Mumbai was also dropped. These are tactical retreats, not strategic reversals. The airline expects to resume all routes by October.

## Air India's Tata-era transformation

Air India's resurgence under Tata Group ownership has been slower but structurally deeper. The airline is not just adding routes — it is rebuilding its product from the ground up.

The Maharaja Lounge, Air India's first flagship lounge facility, opened at Delhi's Terminal 3 in February 2026 with 16,000 square feet of premium space designed by Hirsch Bedner Associates. The Aviator's Bar, with its ceiling modelled after the propeller of JRD Tata's historic 1932 Puss Moth aircraft, is the kind of brand storytelling that Gulf carriers have excelled at — and that Air India has never attempted before.

On the network side, Air India launched Delhi-Rome nonstop in March, resumed Delhi-Shanghai after a six-year absence, and will begin London Heathrow-Bengaluru nonstop on the A350-900 from August 1. SWISS, part of the Lufthansa Group, adds Bengaluru-Zurich nonstop this winter. These are not vanity routes. They connect tech-heavy diaspora corridors that Gulf carriers have served only through their hubs.

## What this means for NRIs

The practical impact is already visible in three ways.

**More nonstop options.** A decade ago, reaching Hyderabad or Kochi from the US almost certainly meant a connection through Dubai or Doha. Today, Air India flies nonstop from several US gateways to multiple Indian cities, and IndiGo's expanding international network provides onward connectivity from hubs like Delhi and Mumbai without the Gulf detour.

**Price competition.** Emirates, Qatar Airways, and Etihad have historically set the floor price on US-India routes because they controlled the most convenient connections. With Indian carriers offering competitive alternatives — and often shorter total travel times — Gulf carriers are being forced to match or risk losing the value-conscious NRI traveller.

**Route relevance.** Gulf carriers optimised their networks for global connectivity, not for Indian diaspora geography. A Malayali nurse in Dallas and a Gujarati entrepreneur in Edison have different destination needs. Indian carriers are adding routes that match these patterns — Thiruvananthapuram, Ahmedabad, Amritsar — in ways that hub-and-spoke Gulf models never prioritised.

## The road ahead

The shift is not complete, and it comes with caveats. Indian carriers still lag on premium cabin products, frequent-flyer programmes, and the kind of seamless transfer experience that makes a Doha or Dubai connection effortless. IndiGo does not offer a business class on most international routes. Air India's fleet renewal is ongoing but unfinished.

But the trend line is unmistakable. India's international aviation market is growing faster than almost any other in the world, and for the first time, Indian airlines are capturing that growth rather than ceding it to foreign carriers. For the four-million-strong Indian diaspora in the US alone, that means more choice, better prices, and flights that go where they actually need to go."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

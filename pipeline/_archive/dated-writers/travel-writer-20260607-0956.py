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
        "headline": "Air India and Riyadh Air Just Signed a Deal — and It Could Reshape How NRIs Travel Through the Middle East",
        "subheadline": "A new MoU between India's flag carrier and Saudi Arabia's premium startup airline opens the door to codeshares, loyalty benefits, and smoother connections through Riyadh — a corridor that matters to millions of Indians.",
        "slug": make_slug("air-india-riyadh-air-mou-nri-saudi-codeshare"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "Over 2.6 million Indians live and work in Saudi Arabia, making the India-Saudi corridor one of the busiest in the world. Add Hajj and Umrah pilgrims, business travelers, and families visiting relatives in the Gulf, and this partnership directly affects a massive slice of the NRI population. Codeshare arrangements would mean single-booking convenience through Riyadh to Europe and beyond — a real alternative to the Dubai and Doha hubs that currently dominate.",
        "tags": ["travel", "airlines", "air-india", "riyadh-air", "saudi-arabia", "codeshare", "nri"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Aviation Week", "url": "https://aviationweek.com"},
            {"name": "Travel and Tour World", "url": "https://travelandtourworld.com"},
            {"name": "Arabian Gulf Business Insight", "url": "https://agbi.com"},
            {"name": "Devdiscourse", "url": "https://devdiscourse.com"},
            {"name": "Hospitality News India", "url": "https://hospitalitynews.in"}
        ]),
        "score_total": 78,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9e/HZ-RXX_Boeing_787-9_Dreamliner_Riyadh_Air_LHR_4.1.26_%2855027186633%29.jpg/3840px-HZ-RXX_Boeing_787-9_Dreamliner_Riyadh_Air_LHR_4.1.26_%2855027186633%29.jpg",
        "image_caption": "A Riyadh Air Boeing 787-9 Dreamliner at London Heathrow Airport",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": """Air India and Riyadh Air have signed a Memorandum of Understanding that, on paper, reads like any airline partnership announcement. Codeshares. Interline ticketing. Loyalty program cooperation. Cargo collaboration. The usual.

But look past the corporate language and the contours of something consequential emerge: two of the fastest-growing aviation markets in the world — India and Saudi Arabia — are building a bridge that could reroute how millions of Indians travel internationally.

## What the deal actually says

The MoU, signed in early June, lays the groundwork for interline and codeshare arrangements between Air India and Riyadh Air, subject to regulatory approvals. In practice, this means passengers could eventually book a single ticket from, say, Hyderabad to London with a connection in Riyadh — baggage checked through, loyalty miles accruing, and no need to re-clear security.

https://x.com/airindia/status/2062423722611634513

The two airlines will leverage hubs in Delhi, Mumbai, and Riyadh. Beyond passenger flights, the agreement covers cargo services, operational support, and joint digital initiatives. Campbell Wilson, Air India's CEO, called it "a natural partnership" between "two important growth markets in global aviation."

Riyadh Air CEO Tony Douglas was equally direct: India is "one of the most important aviation markets in the world."

## Why Riyadh Air matters

Riyadh Air is not yet another Gulf startup. Backed by Saudi Arabia's Public Investment Fund — the same sovereign wealth vehicle behind NEOM and the Premier League's Newcastle United — it launched its inaugural flights to London on July 1 and is positioning Riyadh as a rival to Dubai, Doha, and Abu Dhabi as a global transit hub.

The airline operates Boeing 787-9 Dreamliners with a premium-heavy configuration, targeting the lucrative business and first-class segments that Emirates and Qatar Airways have dominated. Its fleet order book runs to over 100 widebody aircraft.

For Riyadh, the play is strategic: Saudi Arabia wants to diversify beyond oil, and aviation is central to Vision 2030. Capturing India's outbound traffic — one of the world's largest — is essential to that plan.

## What this means for NRIs

The India-Saudi Arabia air corridor is already enormous. Over 2.6 million Indians live in the kingdom, and travel demand is driven by business, religious pilgrimages (Hajj and Umrah draw hundreds of thousands of Indian Muslims annually), and family connections that run generations deep.

But the bigger NRI play is onward connectivity. Riyadh sits roughly equidistant between India and Europe, making it a natural transit point. If codeshare flights materialize, an NRI in Chicago could book a single Air India itinerary that connects through Delhi and Riyadh to reach, say, Cairo or Casablanca — markets where Indian carriers have limited direct presence.

Air India has expanded aggressively since returning to the Tata Group in 2022. It now has 25 codeshare partnerships and over 120 interline agreements covering more than 1,000 destinations. The Riyadh Air tie-up slots into a broader strategy of using partnerships to extend reach without deploying metal.

## The catch

Analysts note that the biggest constraint on India-Saudi aviation isn't a lack of airline partnerships — it's government-imposed bilateral limits on flights and seats. John Grant, a partner at Midas Aviation, told Arabian Gulf Business Insight that Riyadh Air will be "hoping to get a better hearing in any future discussions around capacity growth between the two countries."

A codeshare between Saudia (Saudi Arabia's existing flag carrier) and Air India took effect in February, giving Saudia passengers access to Indian cities via Delhi and Mumbai. Adding Riyadh Air to the mix creates competition within the Saudi aviation ecosystem itself — a dynamic the Indian government may leverage in future bilateral negotiations.

## The bottom line

This MoU is a statement of intent, not an operational launch. Regulatory approvals, schedule alignment, and technology integration will take months. But the direction is clear: India's airline market and Saudi Arabia's aviation ambitions are converging, and NRIs stand to benefit from cheaper fares, better connections, and more options on one of the world's most-traveled corridors.

For the 4.5 million-strong Indian community in the Gulf — and the millions more who transit through it every year — a third competitive hub in Riyadh is not just convenient. It is overdue."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Summer Flights From the US Just Got 22% More Expensive — Here's How NRIs Can Still Get Home Without Breaking the Bank",
        "subheadline": "Jet fuel prices driven by the Iran conflict have pushed international fares to their highest levels in years. But timing, routing, and a few booking tricks can still save Indian Americans hundreds on their annual trip home.",
        "slug": make_slug("summer-flight-prices-surge-nri-india-booking-tips"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "The annual summer trip to India is a non-negotiable for millions of NRI families — kids are out of school, grandparents are waiting, and wedding season beckons. But with international fares from the US up 22% year-over-year according to KAYAK data, the SFO-DEL or JFK-BOM round trip that cost $900 last June now runs well over $1,100. This guide breaks down what's driving the spike and what NRIs can actually do about it.",
        "tags": ["travel", "flights", "fares", "summer-travel", "iran-conflict", "nri", "booking-tips"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://reuters.com"},
            {"name": "Associated Press via Barchart", "url": "https://barchart.com"},
            {"name": "Wall Street Journal", "url": "https://wsj.com"},
            {"name": "WebProNews", "url": "https://webpronews.com"},
            {"name": "Indian Eagle", "url": "https://indianeagle.com"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/2833379/pexels-photo-2833379.png",
        "image_caption": "Airport flight information board showing international departures and arrivals",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": """If you have been staring at flight search results for your summer India trip and wondering whether the screen is lying, it is not. International flights from the US are running 22% higher than the same period last year, according to KAYAK search data. Domestic fares are up as much as 31%.

The culprit is not seasonal demand, though that has not helped. It is jet fuel — and the war that made it expensive.

## What happened to fuel prices

Since the US-Israeli military operations against Iran began in late February, jet fuel prices have surged from roughly $99 per barrel to a peak above $150 in April. They have since eased to around $142, according to the International Air Transport Association, but remain far above anything airlines budgeted for.

The mechanism is straightforward: the Strait of Hormuz, through which one-fifth of the world's crude and refined fuel once flowed, is effectively restricted. Europe previously sourced about 60% of its jet fuel from Persian Gulf refineries. That supply is now trapped, and global markets have scrambled to fill the gap.

US refineries have responded by shifting production toward jet fuel at the expense of gasoline and diesel. American jet fuel exports hit a record 455,000 barrels per week in recent data, but the ripple effect means higher gas prices at the pump too — a double hit for NRI families planning road trips as an alternative to flying.

## The airline response

Airlines are not absorbing these costs quietly. US carriers collectively face an estimated $24 billion increase in fuel bills this year, with only about $8.4 billion offset through hedging and surcharges, according to a Deutsche Bank analysis.

The practical fallout for travelers:

- **American Airlines** suspended six domestic routes in August and September, citing elevated fuel costs. It also hiked checked baggage fees and trimmed economy perks.
- **Delta** cut capacity by 3.5% and projected $2 billion in additional fuel expenses for Q2 alone.
- **IndiGo** suspended flights to six international destinations (Hong Kong, Shanghai, Ho Chi Minh City, Langkawi, Krabi, Siem Reap) from July through September and pulled out of Manchester entirely.
- **British Airways** is running a June sale with reduced transatlantic fares — but the discounts are relative to inflated base prices.

The pattern is consistent: fewer seats, thinner schedules, and less flexibility when something goes wrong.

## What NRIs are actually paying

The India-US corridor has not been spared. Round-trip fares on key diaspora routes tell the story:

- **SFO/LAX to Delhi:** $1,050–$1,400 economy (up from $850–$1,050 last summer)
- **JFK/EWR to Mumbai:** $950–$1,300 economy
- **ORD to Hyderabad:** $1,100–$1,500 with one stop
- **IAD to Bengaluru:** Starting around $900 on budget carriers with multiple stops, $1,200+ on majors

One-stop options through Gulf hubs (Emirates via Dubai, Etihad via Abu Dhabi, Qatar via Doha) remain the cheapest on many routes, though transit times have lengthened as airlines reroute around restricted airspace.

## How to save — realistically

No one is getting 2024 prices this summer. But there are strategies that actually work:

**Book midweek departures.** Tuesday and Wednesday flights on the US-India corridor consistently price 10–15% lower than Friday and Sunday departures. The difference on a family of four adds up fast.

**Consider positioning flights.** If you are in a secondary US city, a separate domestic ticket to a major gateway (JFK, SFO, ORD) plus an international fare can sometimes beat the through-fare. Use separate bookings and give yourself a buffer day.

**Use consolidator deals.** Indian Eagle is running a June 5–12 sale with flat $40 off Turkish Airlines and $30 off Emirates through coupon codes IETBTK40 and IETBEK30. These stack with the site's negotiated "Eagle Deal" fares. For a family booking four tickets, that is $120–$160 in savings with minimal effort.

**Look at Kuwait Airways and Oman Air.** They consistently show lower fares ($333–$435 one-way to Mumbai on recent searches) but with longer layovers in Kuwait City or Muscat. If you have schedule flexibility, the savings can be substantial.

**Fly in late July or August.** Peak NRI travel demand hits in the first two weeks of June (post-school) and again in mid-December. Late July and August see softer demand on the India corridor as monsoon season deters some travelers — but that is precisely when fares dip.

**Set price alerts now.** If your travel is in August or later, set alerts on Google Flights or Momondo. Fuel prices have been declining from their April peak, and any ceasefire developments around Iran could trigger a rapid fare correction.

## The bigger picture

The International Energy Agency has warned that Europe has roughly six weeks of jet fuel supply remaining at current consumption rates. If the Strait of Hormuz situation worsens, fares could climb further. If diplomatic progress materializes, a correction could come quickly — airlines would rush to fill seats on routes they have been underserving.

For NRIs, the calculus is familiar: the trip home is not optional, but the price of getting there has rarely been this volatile. Book strategically, stay flexible on dates, and do not wait for fares to return to 2024 levels. They will not — at least not this summer."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

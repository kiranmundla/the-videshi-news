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
        "headline": "Europe's New Border System Is Melting Down This Summer — and It Sits Right on the Diaspora's Cheapest Route Home",
        "subheadline": "The EU's biometric Entry/Exit System is producing waits of up to six hours at the Frankfurt and Amsterdam hubs NRIs use to reach India. Here is how to route around the worst of it.",
        "slug": make_slug("europe-ees-border-delays-summer-frankfurt-amsterdam-nri-india-transit"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "The cheapest one-stop flights from the US East Coast to India route through Frankfurt, Munich and Amsterdam — exactly the Schengen hubs now buckling under the EU's new biometric border checks this summer.",
        "tags": ["travel", "europe", "ees", "schengen", "transit", "airlines"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "The Times — EES launch failures", "url": "https://www.thetimes.com/business/companies-markets/article/ees-entry-exist-system-eu-passports-travel-fv7c8mj8v"},
            {"name": "The Hindu BusinessLine — Lufthansa & Germany transit visa", "url": "https://www.thehindubusinessline.com/economy/logistics/lufthansa-eyes-higher-india-traffic-after-germany-scraps-airport-transit-visa-requirement/article69000000.ece"},
            {"name": "EEAS — ETIAS & EES official guidance", "url": "https://www.eeas.europa.eu/eeas/travelling-europe-etias_en"}
        ]),
        "score_total": 80,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/32176062/pexels-photo-32176062.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A passenger waits at an airport immigration control counter",
        "image_attribution": "Pexels",
        "body": """The European Union's long-delayed Entry/Exit System (EES) — the biometric border regime that fingerprints and photographs every non-EU traveller entering the Schengen area — was supposed to make Europe's frontiers smarter. Instead, it is making them slower. British and European officials are now warning of queues of up to six hours at some crossings this summer, and a blunt internal verdict has surfaced as to why: the system was rolled out without ever being tested end to end.

For most Americans that is a holiday headache. For the Indian diaspora it is something more specific, because the corridor this affects is the one a large share of NRIs use to get home.

## Why this lands on the diaspora's doorstep

Air India's nonstop network out of the US has thinned this year, with frequencies trimmed on Delhi–San Francisco, Delhi–Chicago and Delhi–Vancouver and block times stretched by airspace detours. The slack has been taken up by European carriers. Lufthansa now flies more than 70 weekly services from India, over 50 of them to Germany, feeding Frankfurt and Munich. Swiss has expanded sharply through Zurich, and KLM through Amsterdam. For an NRI in New York, Boston or Washington, the realistic one-stop home is increasingly a European hub — precisely where EES is being switched on.

The friction is not on the India leg. It is in transit. A traveller connecting Newark–Frankfurt–Bengaluru who has to clear a biometric border kiosk during a tight layover is exposed to exactly the delays now being reported.

## The one piece of genuinely good news

There is a meaningful offset, and it is recent. Germany has scrapped its airport transit visa requirement for Indian nationals, a change Lufthansa says removes a long-standing friction point and expects to lift passenger flows through Frankfurt and Munich, particularly onward to the UK. In plain terms: Indian passport holders connecting through German airports no longer need a separate transit visa to change planes. That makes Frankfurt and Munich more attractive on paper — but it does nothing about the EES kiosk queues once you are inside the Schengen border. The two changes pull in opposite directions, and travellers need to hold both in their heads.

## What this means for your next trip home

A few concrete moves for the summer and autumn booking window:

- **Pad your connection.** If you are routing through a Schengen hub, treat any layover under two hours as risky. The EES checks hit at the point you cross into the Schengen zone, and that is where the six-hour horror stories originate.
- **Prefer hubs where you stay airside.** A through-connection that keeps you on the same side of the border avoids the worst of the kiosks. Itineraries that force you to re-clear immigration are the ones to scrutinise.
- **Weigh the non-Schengen alternatives.** For West Coast NRIs, Cathay Pacific through Hong Kong and the Gulf carriers through Dubai, Doha and Abu Dhabi sidestep Europe entirely. Etihad and Emirates are not affected by EES at all, and Abu Dhabi even offers US preclearance on the way out.
- **Don't confuse EES with ETIAS.** ETIAS — the €7 online travel authorisation — is a separate system aimed at visa-exempt visitors and is still not live; it is expected only in late 2026. Indian passport holders, who already need a Schengen visa to enter Europe, are not the target of ETIAS. EES, the biometric border check, is the one causing the queues now.

The deeper point for diaspora travellers is that the "default" route home has quietly shifted. For years the move was to book the national carrier nonstop and not think about it. With Air India's US schedule lighter and Europe's borders gummed up, the smart booking in 2026 is the one that looks hardest at the middle of the journey — the hub, the layover, and which border you are made to cross.

## What's next

The European Commission insists EES "works well at almost all border crossing points," a claim contradicted by the queues now forming outside school holidays. The system is meant to reach full force across the bloc this year. Until the plumbing is fixed, the practical advice for NRIs is unglamorous but reliable: build in time, scrutinise the connection, and remember that the cheapest fare home is not the cheapest if you miss the second flight standing in a biometric line."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Etihad Just Doubled Chicago and Pushed Charlotte to Daily — Quietly Rerouting the Diaspora Around Air India's Pullback",
        "subheadline": "From June 15, Abu Dhabi gets a second daily Chicago flight and a daily Charlotte service, opening one-stop access to 11 Indian cities just as Air India trims its US nonstops.",
        "slug": make_slug("etihad-chicago-double-daily-charlotte-daily-abu-dhabi-india-nri-route"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "As Air India cuts US nonstops, Etihad's expanded Chicago and Charlotte service hands Midwest and Southeast NRIs a fresh one-stop path to 11 Indian cities — including the smaller metros Air India never served directly.",
        "tags": ["travel", "airlines", "etihad", "abu-dhabi", "india-routes"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "FTN News — Etihad boosts US network", "url": "https://ftnnews.com/aviation/etihad-airways-boosts-u-s-network-with-more-chicago-and-charlotte-flights"},
            {"name": "TTN Worldwide — Etihad US growth", "url": "https://ttnworldwide.com/"},
            {"name": "Air Traveler Club — Charlotte–Abu Dhabi route", "url": "https://airtraveler.club/etihad-charlotte-abu-dhabi-route/"}
        ]),
        "score_total": 76,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/7/77/Etihad_Boeing_787-9_A6-BNE_IAD_VA2.jpg",
        "image_caption": "An Etihad Airways Boeing 787-9 Dreamliner, the type operating the expanded Chicago and Charlotte routes",
        "image_attribution": "Wikimedia Commons",
        "body": """Etihad Airways has turned up the volume on its US network at exactly the moment the Indian diaspora needs more seats. From June 15, the Abu Dhabi carrier moved Chicago O'Hare to double-daily service and upgraded Charlotte from four-weekly to a daily flight — one of the fastest route ramp-ups in the airline's history. Both routes fly the Boeing 787-9 Dreamliner, configured with 32 Business and 271 Economy seats.

On its own, that reads like ordinary airline capacity housekeeping. Read against what is happening at Air India, it is a meaningful shift in how NRIs in the American heartland and the Southeast will get home.

## The context: Air India is shrinking where Etihad is growing

Air India spent this summer rationalising its long-haul map, citing airspace restrictions and high fuel costs. Delhi–Chicago was suspended temporarily, Delhi–San Francisco cut from 10x to 7x weekly, and Delhi–Vancouver and Delhi–Toronto trimmed. For a traveller in Chicago who relied on the nonstop to Delhi, that route simply is not there right now.

Etihad's move fills part of that vacuum from the other direction. The second daily Chicago frequency opens a wider band of departure times and, crucially, connects through Abu Dhabi to 11 Indian gateways — Ahmedabad, Bengaluru, Chennai, Delhi, Hyderabad and Mumbai among them. That list matters: it includes the second-tier metros that Air India's US nonstops never served at all. A Hyderabadi family in Chicago that used to fly Chicago–Delhi–Hyderabad on two carriers can now do Chicago–Abu Dhabi–Hyderabad on one ticket, one airline, one baggage policy.

## Charlotte: a city that had nothing

The Charlotte story is the more striking one. Until Etihad launched the route on March 20, Charlotte had zero nonstop Middle East service; a traveller bound for Delhi or Mumbai had to backtrack to a European hub, adding four to eight hours. Pushing the route to daily after barely three months signals genuine demand from the growing South Asian population across the Carolinas and the wider Southeast.

There is a practical sweetener here that diaspora travellers consistently undervalue: Etihad's Abu Dhabi hub offers US Customs and Border Protection preclearance. Passengers clear US immigration in Abu Dhabi on the way back and arrive into Charlotte — or Chicago — as a domestic flight, skipping the customs queue stateside after a 14-hour journey. For families travelling with elderly parents or young children, that alone can be worth choosing the routing.

## What this means for your next trip home

- **Midwest NRIs:** With Delhi–Chicago nonstop suspended, the double-daily Abu Dhabi service is now one of the most flexible one-stops to North and South India out of O'Hare. Compare it against the Frankfurt and Amsterdam routings, which are exposed to Europe's summer border delays.
- **Southeast NRIs:** Charlotte's daily flight removes the European backtrack entirely. The daily schedule runs through September 8, so it is built for the summer-visit and back-to-school window.
- **Mind the seat caps.** Etihad has been candid that its India growth is constrained by bilateral traffic rights, not demand — its CEO has said the airline would add five to seven Indian destinations and double frequencies if granted the rights. Translation: these expanded US flights connect to a fixed pool of India seats, so book the onward leg early during peak weeks.

## What's next

Etihad views India as a pillar of its growth strategy, projecting that 15–20% of its future expansion will come from the country if traffic rights open up. For now, the diaspora benefits from the US end of the network growing faster than the India end. The booking lesson for 2026 is the same one that keeps recurring: with the national carrier pulling back, the savvy move is to shop the Gulf and European one-stops rather than defaulting to a nonstop that may no longer exist on your route."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Air India's New Mumbai–Tokyo Nonstop Quietly Fixes One of the Diaspora's Most Annoying Layovers",
        "subheadline": "Four weekly Dreamliner flights to Haneda — Tokyo's close-in airport — open a cleaner one-stop between the US West Coast and Mumbai, with ANA connections to six Japanese cities.",
        "slug": make_slug("air-india-mumbai-tokyo-haneda-nonstop-nri-west-coast-japan-connection"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "For West Coast NRIs whose families are in Mumbai, a clean Pacific routing through Tokyo Haneda is an alternative to the congested Gulf and Europe hubs — and to Air India's lengthening westbound nonstops.",
        "tags": ["travel", "airlines", "air-india", "japan", "mumbai", "tokyo"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Travel Span — Air India Mumbai–Haneda launch", "url": "https://travelspan.in/air-india-mumbai-tokyo-haneda/"},
            {"name": "AeroRoutes — Air India adds Mumbai–Tokyo", "url": "https://aeroroutes.com/"},
            {"name": "Air India Newsroom — Asia network expansion", "url": "https://www.airindia.com/in/en/about-us/press-release.html"}
        ]),
        "score_total": 72,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/b/b8/Boeing_787_Dreamliner_-_Air_India_-_VT-ANP_%2849570132022%29.jpg",
        "image_caption": "An Air India Boeing 787-8 Dreamliner, the aircraft type operating the new Mumbai–Tokyo Haneda route",
        "image_attribution": "Wikimedia Commons",
        "body": """Air India has begun nonstop flights between Mumbai and Tokyo's Haneda Airport, adding a fourth-weekly Boeing 787-8 Dreamliner service that, on the surface, looks like a routine Asia expansion. Dig into the geography of how the diaspora actually flies, and it solves a specific, long-standing irritation: the lack of a clean Pacific routing between Mumbai and the US West Coast.

The route launched on June 15, operating four times a week, and complements Air India's existing daily Delhi–Tokyo service. Introductory economy return fares started around ₹57,700.

## Why Haneda, not Narita, matters

Air India deliberately chose Haneda, and that detail is the whole point. Haneda sits roughly 15 km from central Tokyo, against 50–60 km for Narita. For a connecting passenger, that does not directly help — but Haneda's slot-controlled, premium status means tighter schedules and better onward connections. Through Air India's codeshare with Star Alliance partner All Nippon Airways (ANA), arriving passengers can connect onward to Fukuoka, Hiroshima, Nagoya, Okinawa, Osaka and Sapporo.

## The diaspora angle: a third way across the Pacific

Here is where it gets interesting for NRIs. The West Coast Indian community — heavily Mumbai- and Gujarat-connected in the Bay Area and Los Angeles — has, for years, faced an awkward choice flying home. Either take Air India's lengthening westbound nonstops (now stretched by airspace detours), or backtrack across the Atlantic to a European hub, or thread through the Gulf. None of those is a natural Pacific path.

Tokyo is a natural Pacific path. There are abundant nonstops from San Francisco, Los Angeles, Seattle and San Jose to Tokyo on US and Japanese carriers. With Air India now flying Tokyo–Mumbai nonstop, the building blocks exist for a West-Coast-to-Mumbai itinerary that crosses one ocean instead of two and never touches the congested European or Gulf hubs. That is a genuinely cleaner geometry for anyone whose family is in Mumbai rather than Delhi.

It also dovetails with a broader Air India push into Asia. The airline recently added Delhi–Hanoi and has been deepening its Japan presence; Indian arrivals to Japan jumped roughly 35% in 2025. The Mumbai–Haneda flight is part of positioning Mumbai as a second international hub behind Delhi.

## What this means for your next trip home

- **Bay Area and LA NRIs with Mumbai ties:** Watch for the Tokyo connection as an alternative to the Gulf and Europe one-stops, especially during the summer when European borders are slow. A SFO–Tokyo–Mumbai itinerary keeps you on the Pacific side.
- **Mind the frequency.** At four weekly flights, the Mumbai–Haneda leg does not operate daily yet, so connection-building requires matching days. Check that your trans-Pacific flight lands in time for the onward Air India departure.
- **Use the ANA codeshare.** If your family is in a Japanese city rather than passing through, the six-city ANA network out of Haneda makes Japan a viable stopover destination on the way to or from India — a two-in-one trip that is hard to assemble through the Gulf.
- **Premium travellers:** The 787-8 carries Air India's evolving cabin product. Business-class return fares were around ₹2 lakh at launch, competitive against the Gulf carriers' premium offerings on India–US routings.

## What's next

Air India's Japan build-out is unlikely to stop at four weekly Mumbai flights if demand holds; the Delhi–Tokyo route has already moved to daily. For the West Coast diaspora, the strategic takeaway is that a credible Pacific corridor to Mumbai is finally taking shape. It will not suit everyone — the frequency is thin and the connection needs planning — but for families tired of the trans-Atlantic-then-Gulf zigzag, a single ocean and a Tokyo stopover is a welcome new option on the map."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

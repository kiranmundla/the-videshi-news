#!/usr/bin/env python3
"""Videshi Travel Writer — 2026-06-05 14:03 UTC run"""

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


# ── ARTICLE 1 ──────────────────────────────────────────────────────────

art1_body = """SWISS will launch its first-ever nonstop service between Bengaluru and Zurich this winter, giving south India's technology capital a direct link to Switzerland that it has never had. The route is the sharpest signal yet that the Lufthansa Group — which celebrates its centenary this year — sees India not as a volume play, but as a premium market worth its best hardware.

The Bengaluru-Zurich nonstop, scheduled for the Winter 2026 timetable, will be operated by SWISS using additional Airbus A330 capacity. The airline will simultaneously add more A330 frequencies on its established Delhi-Zurich service. Meanwhile, Lufthansa's mainline brand is deploying its acclaimed Allegris cabin — a product built around suites with closing doors and bespoke lighting — on Boeing 787-9 services from both Delhi and Hyderabad. And for the Mumbai corridor, the carrier is expanding Airbus A380 operations to Munich, responding to what executives describe as "strong demand from both business and leisure travellers."

The moves come days after Germany scrapped its airport transit visa requirement for Indian nationals, effective June 3. Indian travellers connecting through Frankfurt, Munich, or Zurich no longer need a separate transit document — removing a paperwork barrier that had long made Gulf hubs more attractive for one-stop journeys to Europe.

## What it means for the diaspora

For the estimated 300,000-plus Indian tech professionals and their families in the Bay Area, Seattle, and other US tech corridors who trace their roots to Karnataka, the SWISS nonstop to Zurich changes the math on Europe connections. Today, reaching Bengaluru from the US via Europe means a minimum of two connections — typically through London, Dubai, or Doha. A Zurich gateway adds a European hub that plugs directly into Switzerland's banking, pharma, and engineering centres, all of which employ significant Indian-origin talent.

The Allegris deployment on Hyderabad routes is equally significant. Hyderabad's Rajiv Gandhi International Airport handles a growing share of the US-India diaspora traffic, particularly for families in the southeastern United States. Premium cabin access on a 787-9 with closing-door suites represents a product that, until recently, was reserved for routes like London or New York.

Lufthansa Group now operates more than 70 weekly flights between India and Europe, making it the largest European airline group on India routes. The scale matters because it offers NRIs connecting flexibility that no single carrier can match — a missed connection in Frankfurt can often be rebooked onto a Munich or Zurich departure within hours, on the same ticket.

## The competitive picture

The expansion arrives at a moment when India's aviation market is under acute pressure. The Iran conflict has forced airspace rerouting, pushed up fuel costs, and triggered route cuts by IndiGo and Air India alike. But Lufthansa Group appears to be reading through the turbulence: India's long-haul premium demand is structural, not cyclical, driven by a diaspora that now numbers over five million in Europe and North America combined.

Air India, for its part, is rolling out retrofitted 787-8 aircraft with premium economy on the Bengaluru-London Heathrow route from August and upgrading its Toronto service with factory-new 787-9s. The two airline groups are effectively racing to capture the same high-value passenger: the NRI who flies business class twice a year and wants a product that matches Emirates or Singapore Airlines.

For NRIs booking winter travel to India, the practical advice is straightforward. The SWISS Bengaluru nonstop opens a new one-stop option from any US city with Zurich service — and United, a Star Alliance partner, feeds dozens of US cities into Zurich daily. The transit visa removal means no extra paperwork, no consulate visit, no six-week wait. Europe just became a viable alternative to the Gulf for getting home."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "SWISS Will Fly Bengaluru-Zurich Nonstop This Winter — and Lufthansa Group Is Making India Its Premium Frontier",
    "subheadline": "A first-ever direct link to Switzerland, Allegris suites on Hyderabad flights, and A380s on the Mumbai-Munich run: the Lufthansa Group's centenary bet on India's diaspora corridors.",
    "slug": make_slug("swiss-bengaluru-zurich-nonstop-lufthansa-india-premium"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "Bengaluru's tech diaspora — and NRIs across the US — get a new one-stop European gateway. The transit visa removal and SWISS nonstop together eliminate the paperwork and connection penalties that made Gulf hubs the default for India-bound travel.",
    "tags": ["travel", "airlines", "europe", "switzerland", "lufthansa", "swiss"],
    "urgency": "medium",
    "sources": [
        {"name": "Aviation A2Z", "url": "https://aviationa2z.com"},
        {"name": "Devdiscourse", "url": "https://devdiscourse.com/article/international/3323793-germany-eases-transit-for-indian-flyers-boosting-air-links"},
        {"name": "Aerospace Global News", "url": "https://aerospaceglobalnews.com"}
    ],
    "score_total": 78,
    "status": "published",
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fd/HB-JNB_Boeing_777-300_Swissair_LHR_4.11.20.jpg/3840px-HB-JNB_Boeing_777-300_Swissair_LHR_4.11.20.jpg",
    "image_caption": "A SWISS Boeing 777-300ER at London Heathrow Airport",
    "image_attribution": "Wikimedia Commons",
    "is_editorial": False,
    "body": art1_body.strip()
}


# ── ARTICLE 2 ──────────────────────────────────────────────────────────

art2_body = """Somewhere beneath the Zoji La pass, at nearly 12,000 feet above sea level, tunnel-boring crews have already punched through more than 12 kilometres of Himalayan rock. When the remaining stretch is connected — breakthrough is targeted for mid-2026 — the Zoji La Tunnel will become the world's longest single-tube, bi-directional road tunnel at high altitude, and the single most consequential piece of infrastructure for Ladakh tourism in a generation.

For NRIs who have spent years squeezing Ladakh trips into the narrow June-to-September window when the mountain passes are open, this changes everything.

## The numbers

The tunnel runs 13.15 kilometres between Sonamarg in Jammu & Kashmir's Ganderbal district and Dras in Kargil, Ladakh. It sits on National Highway 1, the Srinagar-Leh corridor that is currently severed by snow for up to seven months every year. Once operational, the tunnel will reduce the Sonamarg-to-Dras journey from a harrowing three-to-four-hour drive over the 11,650-foot pass to a 15-minute drive through a horseshoe-shaped, 9.5-metre-wide, two-lane bore.

Construction began in October 2020 under the Hyderabad-based engineering firm MEIL, with a budget of roughly ₹6,800 crore (about $815 million). As of early 2026, physical progress stands at approximately 64 per cent, with excavation advancing from both the Baltal and Minamarg portals. The completion date has been revised to February 2028, pushed back from the original September 2026 target by pandemic delays, security incidents, and the sheer difficulty of blasting through avalanche-prone Himalayan terrain.

The Zoji La is not a standalone project. It is part of a broader ₹25,000-crore programme to build 19 tunnels across Jammu & Kashmir, plus 12 more in Ladakh. The adjacent Z-Morh Tunnel, a 6.5-kilometre bore between Gagangir and Sonamarg, is already complete. Together, they will create the first all-weather road corridor from Srinagar to Ladakh.

## Why NRIs should care

Ladakh has long occupied a mythical place in the Indian imagination — Pangong Lake's shifting blues, the monasteries of the Indus Valley, Khardung La's thin air. But for the diaspora, the destination comes with a logistics tax. Flights to Leh are limited, expensive, and frequently cancelled due to weather. The road from Srinagar is a bone-rattling ordeal that older parents and young children cannot easily endure. The result: most NRIs who visit India skip Ladakh entirely, or attempt it once and never return.

Year-round road access fundamentally alters the calculus. A family visiting relatives in Srinagar during a December trip could drive to Ladakh in a day. Winter Ladakh — with frozen rivers, snow leopard sightings, and the famous Chadar trek on the frozen Zanskar — becomes accessible without the gamble of unreliable winter flights.

## Ladakh's tourism pitch is evolving

At SATTE 2026, India's largest travel trade exhibition held in New Delhi earlier this year, Ladakh's Lieutenant Governor Kavinder Gupta presented the region as a "rapidly rising global tourism hotspot." The pitch went well beyond Pangong and Nubra Valley. Gupta highlighted Hanle, home to the Indian Astronomical Observatory, as a dark-sky tourism destination — the site hosts one of the world's highest optical telescopes and the MACE gamma-ray telescope, offering some of the clearest night skies in India for astrophotography and stargazing.

Magnetic Hill, Tso Moriri, Hemis Monastery, Zanskar Valley, and Drass were presented as part of an expanding circuit designed to spread tourism revenue beyond Leh town. New road infrastructure reaching remote border areas is making lesser-known valleys accessible for the first time.

## The practical timeline

NRIs planning ahead should note: the tunnel will not open before early 2028. But the adjacent Z-Morh Tunnel is operational now, and road conditions on the Srinagar-Leh highway have improved measurably. For summer 2026, the road option remains seasonal but better than it has been in years. For those willing to wait, the winter of 2028-29 could be the first season when Ladakh is genuinely year-round — and the rush to book will be fierce."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "Ladakh's Year-Round Dream Is Being Drilled Through a Mountain — What NRIs Need to Know About the Zoji La Tunnel",
    "subheadline": "The world's longest high-altitude road tunnel is 64 per cent complete. When it opens, NRIs will no longer need to gamble on summer weather to reach Pangong, Nubra, and the monasteries of the Indus Valley.",
    "slug": make_slug("ladakh-zoji-la-tunnel-year-round-nri-travel"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "NRIs currently have a narrow June-September window to visit Ladakh overland. The Zoji La Tunnel will provide year-round access from Srinagar, making winter Ladakh — frozen rivers, snow leopards, the Chadar trek — reachable for families visiting India during December holidays.",
    "tags": ["travel", "ladakh", "infrastructure", "tunnel", "tourism"],
    "urgency": "medium",
    "sources": [
        {"name": "Tunnel Builder", "url": "https://tunnelbuilder.com"},
        {"name": "Tourism Cairns News (SATTE 2026)", "url": "https://tourismcairns.com.au"},
        {"name": "Observer Research Foundation", "url": "https://orfonline.org"},
        {"name": "Wikipedia — Zoji La Tunnel", "url": "https://en.wikipedia.org/wiki/Zoji-la_Tunnel"}
    ],
    "score_total": 75,
    "status": "published",
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8b/Pangong_Tso_2.jpg/3840px-Pangong_Tso_2.jpg",
    "image_caption": "Pangong Tso lake in Ladakh, currently accessible only during the summer months",
    "image_attribution": "Wikimedia Commons",
    "is_editorial": False,
    "body": art2_body.strip()
}


# ── ARTICLE 3 ──────────────────────────────────────────────────────────

art3_body = """When Salil Panigrahi left his career in Maldivian resort management to co-found Atmosphere Core, his pitch was simple: bring the Maldives formula — isolated luxury, curated experiences, anticipatory service — to destinations that tourists actually live near. A decade and nine Maldivian resorts later, his company has signed nearly 30 hotel projects across India, and the map of where those properties are going tells a story about where Indian travel is headed.

Goa and Rajasthan, predictably, are on the list. But so are Coorg, Kannur, Odisha, Bhopal, and — most strikingly — the Northeast. Atmosphere Core's Guwahati property, The Dhar, a 207-key resort at the Assam-Meghalaya border, represents the company's bet that India's northeastern states are about to have their tourism moment. Seven to eight additional projects across Assam and Meghalaya are in various stages of signing.

"The leisure sector lacks quality hotels, which is why we will be chasing developments in resort locations," Panigrahi told Mint this week. "India needs at least 25-30 per cent more five-star and quality hotels to meet demand for leisure travel."

## A market gap NRIs know intimately

Anyone who has tried to book a quality resort in India for a family reunion or a parents' anniversary trip understands the problem. Outside the Taj, Oberoi, and Leela portfolios — concentrated in metros and a handful of heritage destinations — the options thin out rapidly. The beach resort in Goa that looks stunning on Instagram turns out to have intermittent hot water. The heritage haveli in Rajasthan has charm but no reliable Wi-Fi. The gap between what NRIs are accustomed to abroad and what they find at home remains wide, particularly in emerging destinations.

Atmosphere Core is not alone in seeing the opportunity. IHG Hotels & Resorts this week signed a management agreement for a 350-key InterContinental in Mumbai's Goregaon corridor, bringing its India pipeline to 98 properties across seven brands. The Fern Hotels reached 190 properties with a new Kerala signing. And Summit Hotels launched The Mandir Collection, a brand specifically targeting India's booming spiritual tourism market, starting with a 70-room property near the Salasar Balaji Temple.

The numbers are striking. India's spiritual tourism economy alone is projected to reach $135 billion by 2034, according to Summit's estimates. Boutique resorts with limited room inventory are commanding average daily rates of ₹40,000-60,000 ($470-700), with operating margins above 45 per cent — figures that would be exceptional in any global market.

## Why the Northeast matters

For decades, India's northeastern states have been travel afterthoughts — distant, poorly connected, and associated more with security concerns than scenic beauty. That is changing fast. New airports, upgraded highways, and direct flights from Delhi and Mumbai have made Guwahati, Shillong, and Kaziranga accessible in ways they were not five years ago.

Atmosphere Core's presence in the region signals institutional confidence. The company is not dabbling: its Guwahati resort is designed for corporate retreats, destination weddings, and high-end leisure — the three demand segments that sustain premium pricing. The bet is that Indian travellers, and NRIs in particular, will choose Meghalaya's living root bridges and Assam's tea gardens over a fourth trip to Bali, if the hotel product matches.

## What NRIs should watch for

Atmosphere Core's India properties will operate under management contracts rather than full ownership, an asset-light model that allows faster scaling. The company is taking a direct development role in only three projects — Mussoorie, Puri, and Kannur — together worth about ₹1,000 crore. Most properties are being developed by high-net-worth investors and managed by Atmosphere's team.

For NRIs planning trips home in 2026 and 2027, the practical implication is that India's leisure hotel map is expanding faster than most people realize. Destinations that once required compromising on comfort — Coorg, Ladakh approaches, the Konkan coast, Odisha's temple circuit — are getting the kind of properties that make a week-long family stay not just possible but appealing.

The Maldives operator building resorts in Meghalaya is not a curiosity. It is the market's verdict on where Indian travel is going next."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "The Maldives' Biggest Hotel Group Is Building 30 Resorts Across India — and NRIs Won't Recognize the Options",
    "subheadline": "Atmosphere Core, which operates nine luxury resorts in the Maldives, has signed nearly 30 Indian properties from Goa to Guwahati. The bet: India's leisure market is vastly underserved, and the diaspora is the target customer.",
    "slug": make_slug("atmosphere-core-maldives-india-30-resorts-nri-luxury"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "NRIs returning to India for family visits have long struggled with a thin luxury hotel market outside metros. A Maldives operator bringing 30 properties to emerging leisure destinations — including India's Northeast — signals a structural upgrade that makes extended family trips more viable.",
    "tags": ["travel", "hotels", "luxury", "maldives", "northeast-india"],
    "urgency": "medium",
    "sources": [
        {"name": "Livemint", "url": "https://www.livemint.com/companies/news/why-this-maldives-hotel-chain-is-chasing-india-s-leisure-destinations-11749022108449.html"},
        {"name": "Travel Trends Today", "url": "https://traveltrendstoday.in/atmosphere-core-set-for-northeast-india-debut-in-2026/"},
        {"name": "CoStar", "url": "https://www.costar.com"}
    ],
    "score_total": 72,
    "status": "published",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/258154/pexels-photo-258154.jpeg",
    "image_caption": "A luxury tropical resort with swimming pool and palm trees at dusk",
    "image_attribution": "Pexels",
    "is_editorial": False,
    "body": art3_body.strip()
}


# ── INSERT ──────────────────────────────────────────────────────────────

articles = [art1, art2, art3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

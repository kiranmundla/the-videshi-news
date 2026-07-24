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
        "headline": "Germany Just Scrapped the Transit Visa for Indians — and It Quietly Reshapes the Cheapest Way Home",
        "subheadline": "From June 3, Indian passport holders can change planes at Frankfurt, Munich and three other German hubs en route to the US, UK or Canada without a separate Schengen transit visa — opening up Lufthansa's network as a low-friction path between North America and India.",
        "slug": make_slug("germany-transit-visa-waiver-indians-frankfurt-munich-nri"),
        "category": "travel",
        "vertical": "immigration",
        "diaspora_angle": "For the millions of Indian passport holders in the US, UK and Canada who fly home via Europe, Germany's transit-visa waiver removes a €90 fee, weeks of paperwork and the real risk of being denied boarding — turning Frankfurt and Munich into genuinely viable connecting hubs to India.",
        "tags": ["travel", "visa", "germany", "airlines", "lufthansa"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Outlook Traveller", "url": "https://www.outlooktraveller.com/destinations/international/germany-removes-airport-transit-visa-rule-for-indians-from-june-2026"},
            {"name": "Breaking Travel News (Lufthansa Group)", "url": "https://www.breakingtravelnews.com/news/article/lufthansa-group-welcomes-visa-free-airport-transit-for-indian-nationals-via-germany/"},
            {"name": "iVisa", "url": "https://www.ivisa.com/germany-blog/germany-drops-transit-visa-for-indian-travelers"}
        ]),
        "score_total": 84,
        "status": "review",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/14/Airport%2C_Frankfurt_%28P1180126%29.jpg/1280px-Airport%2C_Frankfurt_%28P1180126%29.jpg",
        "image_caption": "The terminal at Frankfurt Airport, one of five German hubs now open to Indian travelers for airside transit without a visa",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": """Until this month, an Indian engineer in New Jersey who found a cheap Lufthansa fare to Hyderabad faced a hidden tax that never showed up on the booking page: the Schengen Airport Transit Visa. Even if you never left the secure transit zone of Frankfurt or Munich, Germany required Indian passport holders to apply in advance — roughly €90, a stack of documents, travel insurance, and a processing window that could stretch past two weeks. Get it wrong and the penalty was brutal: denied boarding at departure, or a forced return flight on arrival.

That requirement is gone. As of June 3, 2026, Indian nationals no longer need an airport transit visa to change flights at a German airport while traveling onward to a country outside the Schengen area. The change was published in Germany's Federal Law Gazette on June 2 and took effect the next day.

## What actually changed

The waiver is narrow but powerful. It applies only to **airside transit** — passengers who stay inside the international transit zone and connect to a non-Schengen destination such as the United States, Canada or the United Kingdom. It does not let you leave the airport, clear immigration, or enter Germany or any other Schengen country. For that, the regular Schengen visa rules still apply.

In practice, the exemption covers five German airports with international transit zones: Frankfurt, Munich, Berlin-Brandenburg, Hamburg (4:30 a.m. to 11:30 p.m. only) and Düsseldorf (6 a.m. to 9 p.m., subject to airline-security arrangements). Frankfurt and Munich — Lufthansa's twin fortresses and two of Europe's busiest hubs — are where it matters most.

## Why this matters to NRIs

The diaspora math is simple. Indians in the US, UK and Canada are among the heaviest users of one-stop routings to India, and Europe is the natural midpoint for east-coast and trans-Atlantic itineraries. Lufthansa alone runs more than 70 weekly flights between India and Europe, with onward connections from Frankfurt and Munich to North America, Britain, Africa and Latin America. Until now, the transit-visa rule effectively walled off those itineraries for anyone who didn't want to gamble on paperwork — pushing diaspora flyers toward Gulf hubs like Dubai and Doha instead.

The German embassy framed the move as the outcome of Chancellor Friedrich Merz's January 2026 visit to India, part of a broader package of 19 bilateral agreements. India's Ministry of External Affairs welcomed it as a boost to "people-to-people ties." The Lufthansa Group, marking its 100th anniversary, called Germany a "leading gateway between India, Europe and the world" and is leaning in — deploying its premium Allegris cabins on more Boeing 787-9 services from Delhi and Hyderabad, launching SWISS's first Bengaluru-Zurich route this winter, and adding A380 capacity between Mumbai and Munich.

## The bigger pattern

Germany is not acting alone. France operationalized an identical airport-transit-visa waiver for Indians on April 10, 2026, following President Emmanuel Macron's earlier visit. Together, the two waivers crack open continental Europe's two largest connecting systems — Air France-KLM through Paris and the Lufthansa Group through Frankfurt, Munich and Zurich — for Indian travelers routing to the Americas.

For a Kannadiga family in Toronto or a software team lead in San Francisco, the upshot is concrete: more fare options, fewer single-points-of-failure on the Gulf carriers, and no €90 surprise. The next time a Lufthansa or Air France itinerary undercuts the Emirates fare to Bengaluru by a few hundred dollars, it's now a clean booking rather than a bureaucratic trap.

## What to keep in mind

Two cautions. First, the waiver is strictly for staying airside — if your layover requires leaving the terminal (an overnight in the city, a baggage re-check that pushes you landside), you still need the appropriate Schengen visa. Second, always confirm your specific connection qualifies; the time-of-day restrictions at Hamburg and Düsseldorf are real, and airlines remain the final arbiter at the gate. But for the core use case — a same-terminal connection through Frankfurt or Munich to a US, UK or Canadian city — the friction that quietly shaped a decade of diaspora bookings has just disappeared.
"""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Air India and Thai Airways Are Joining Codes — and It Opens a Smoother Southeast Asian Door for NRIs",
        "subheadline": "The two Star Alliance carriers signed an MoU at the IATA summit in Rio to build a 2026 codeshare, letting passengers book seamless one-ticket journeys between India, Thailand and onward across Asia, Europe and North America.",
        "slug": make_slug("air-india-thai-airways-codeshare-mou-star-alliance-nri"),
        "category": "travel",
        "vertical": "airlines",
        "diaspora_angle": "For NRIs who treat Bangkok as a layover, a stopover or a family-reunion midpoint, an Air India-Thai Airways codeshare means single-ticket protection, coordinated baggage and smoother missed-connection handling on routes that today often require two separate, unprotected bookings.",
        "tags": ["travel", "airlines", "air-india", "thai-airways", "star-alliance"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Travel Trade Journal", "url": "https://traveltradejournal.com/air-india-and-thai-airways-sign-mou-to-strengthen-connectivity-between-india-and-thailand/"},
            {"name": "Asian Aviation", "url": "https://asianaviation.com/air-india-thai-airways-deepen-cooperation/"},
            {"name": "Breaking Travel News", "url": "https://www.breakingtravelnews.com/news/article/air-india-and-thai-airways-deepen-partnership/"}
        ]),
        "score_total": 72,
        "status": "review",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b2/Suvarnabhumi_Airport%2C_Sunset%2C_Bangkok%2C_Thailand.jpg/1280px-Suvarnabhumi_Airport%2C_Sunset%2C_Bangkok%2C_Thailand.jpg",
        "image_caption": "Sunset over Suvarnabhumi Airport in Bangkok, Thai Airways' home hub and a frequent NRI connecting point",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": """Bangkok has long been the diaspora's favorite in-between: a long-weekend escape from Bengaluru, a soft-landing stopover on the way to India, a neutral meeting point for families split across continents. Yet booking through it has often meant two separate tickets — one on Air India, one on Thai Airways — with no protection if the first leg ran late and you watched the second push back from the gate.

That gap is about to narrow. Air India and Thai Airways International (THAI) signed a Memorandum of Understanding on June 7, 2026, on the sidelines of the IATA Annual General Meeting in Rio de Janeiro, committing the two Star Alliance carriers to a deeper partnership built on their existing interline agreement. The headline outcome: a codeshare agreement they intend to put in place later in 2026, subject to regulatory approval.

## What a codeshare actually buys you

The distinction between an interline and a codeshare sounds like airline jargon, but it changes the passenger experience in ways NRIs feel directly. Under the planned arrangement, Air India and THAI will place their own designator codes — "AI" and "TG" — on each other's flights between India and Thailand, and on select international routes from both countries. A single booking reference, through-checked baggage, coordinated schedules, and — critically — the airline's responsibility to rebook you if a delay breaks your connection.

The carriers say the codeshare will reach beyond the India-Thailand sectors to give customers "convenient access to several destinations across Asia, North America and Europe." Because both airlines belong to Star Alliance, the partnership also dovetails with a much larger network — and with Air India's own ongoing push to rebuild its long-haul system under the Tata group.

## Why it matters to the diaspora

For the roughly 31 million people of Indian origin spread across the world, connectivity is rarely about a single nonstop. It is about the web of one-stop options that make a trip affordable and a missed connection survivable. Bangkok's Suvarnabhumi is one of Asia's great connecting hubs, and THAI feeds it from across Southeast Asia, Australia and East Asia. Pairing that with Air India's thickening domestic and international map means a traveler from, say, Sydney or Melbourne could reach a second-tier Indian city on one protected ticket rather than gambling on self-transfers.

Air India CEO Campbell Wilson tied the deal to the airline's broader ambition: "As Asia reinforces its position at the centre of global growth, deeper collaboration between leading airlines will be key... It also supports Air India's broader ambition to strengthen India's connectivity with the world." THAI chief executive Chai Eamsiri called it "a meaningful milestone" in strengthening regional connectivity for passengers moving between Thailand, India and beyond.

## The fine print

This is still an MoU, not a live product. The specific routes, the booking-system integration and the regulatory sign-offs are all to come, and the carriers say terms "will be announced in due course." Expect the first codeshare flights to surface on India-Bangkok trunk routes — Delhi, Mumbai, Bengaluru — before extending to longer international pairings.

There is also a competitive backdrop worth noting. Thailand recently trimmed its visa-free stay for Indian travelers, and rivals like Vietnam and Malaysia are courting Indian tourists aggressively. A tighter Air India-THAI tie-up is partly a bet that Bangkok remains a magnet for Indian flyers — as a destination and as a hub — even as Southeast Asia's tourism map gets more competitive.

For now, the practical advice is simple: if your India trips routinely route through Bangkok, watch for AI- and TG-coded itineraries to start appearing later this year. When they do, the same journey you book today as two nervous, unprotected legs becomes one ticket the airline is obliged to make whole.
"""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Qatar Airways' Biggest-Ever Network Kicks In This Week — With Four New US Gateways That Matter to NRIs",
        "subheadline": "From June 16, the Doha carrier connects 150-plus destinations and adds Atlanta, Boston, Los Angeles and San Francisco service, deepening one-stop options to India for diaspora hubs on both US coasts.",
        "slug": make_slug("qatar-airways-150-destinations-us-gateways-doha-india-nri"),
        "category": "travel",
        "vertical": "airlines",
        "diaspora_angle": "New and expanded Qatar Airways service from Atlanta, Boston, Los Angeles and San Francisco gives US-based NRIs more one-stop routings to Indian cities through Doha — useful redundancy as fares on India-US trunk routes climb and Gulf hubs compete for diaspora traffic.",
        "tags": ["travel", "airlines", "qatar-airways", "doha", "india-us"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Travel + Leisure Asia", "url": "https://www.travelandleisureasia.com/global/news/qatar-airways-resumes-flights-expands-network/"},
            {"name": "Qatar Airways", "url": "https://www.qatarairways.com/en/press-releases.html"}
        ]),
        "score_total": 70,
        "status": "review",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d3/Hamad_International_Airport_Doha_Qatar_1.jpg/1280px-Hamad_International_Airport_Doha_Qatar_1.jpg",
        "image_caption": "Hamad International Airport in Doha, Qatar Airways' hub and a major connecting point for India-bound diaspora travelers",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": """For US-based Indians, the route home has quietly become a question of which Gulf hub to trust. Emirates through Dubai, Etihad through Abu Dhabi, Qatar Airways through Doha — each offers a one-stop path to Indian cities that nonstops still don't reach, and the competition among them shapes what diaspora families pay. This week, Qatar Airways made its move.

From June 16, 2026, the Doha carrier operates what it bills as its largest-ever network: more than 150 destinations, with new routes and added frequencies under a summer schedule that runs through September 15. For US flyers, the additions are pointed — the airline has been steadily rebuilding its American gateways, with Los Angeles service from June 7 and San Francisco from June 11, joining a wave of US points that includes Atlanta and Boston coming online from June 16.

## Why the US gateways matter

Read the diaspora map and the logic is obvious. **Atlanta** anchors the fast-growing South Asian population across the Southeast. **Boston** serves the dense academic-and-tech corridor of New England, full of Indian students, researchers and H-1B professionals. **Los Angeles** and **San Francisco** cover the two biggest concentrations of Indian-origin residents on the West Coast — and SFO in particular is a battleground, with Air India flying nonstop to Delhi, Mumbai and Bengaluru and the Gulf carriers fighting for the connecting traffic.

A West Coast NRI weighing options to Kochi, Ahmedabad or Lucknow — cities without US nonstops — gains another credible one-stop routing through Doha's Hamad International, consistently ranked among the world's best airports. For East Coast travelers, Boston and Atlanta service shortens the path to Qatar's deep India map, which includes not just the metros but secondary points like Goa (back online from May 16) and Kozhikode (from May 1), both heavily used by diaspora families.

## The timing is the story

The expansion lands at a pointed moment. India-US airfares have run roughly 30% higher this summer, squeezed by capacity constraints, fuel costs and rerouting around West Asian airspace. Air India itself has trimmed some international flying between June and August to protect its economics. When the home carrier pulls back and trunk-route fares climb, additional Gulf-hub capacity is exactly the pressure-release valve diaspora travelers want — more seats and more competition tend to soften prices, especially on the price-sensitive secondary-city routes where Indian families concentrate.

Qatar Airways is also expanding well beyond the US. The summer schedule reinstates and adds points across Africa (Marrakesh, Seychelles, Alexandria), Asia (Almaty, Osaka, Tashkent) and Europe, reinforcing Doha's role as a global crossroads. For an NRI, that breadth means the same ticket that takes you home can be stretched into a multi-stop trip — a few days in the Seychelles or a stopover in Doha — without switching carriers.

## What to watch

A few practical notes. The 150-plus network is a schedule valid through mid-September, so confirm your specific city pair and dates rather than assuming year-round service; some additions are seasonal. Qatar Airways advises travelers to keep contact details current and check the app, since Gulf-region schedules have seen disruption tied to regional tensions. And as always with Gulf one-stops, weigh the total journey time — a Doha connection can add hours versus a nonstop, a trade-off that makes sense when the fare gap is real but less so when Air India or United is only marginally pricier.

Still, the direction is clear. With four US gateways in play and the deepest India map of any Gulf carrier, Qatar Airways has positioned itself for the summer rush — and for the steady, year-round flow of diaspora travelers for whom the route home is never quite a straight line.
"""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        wc = len(art["body"].split())
        print(f"✅ {art['slug']}  ({wc} words)")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

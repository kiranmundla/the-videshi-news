#!/usr/bin/env python3
"""Travel writer — 2026-06-11 22:00 UTC run. Three articles."""

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

# ─── ARTICLE 1 ────────────────────────────────────────────────────────────────
art1_body = """IndiGo, the airline that taught 1.4 billion Indians to fly for the price of a train ticket, is building a business class for its long-haul fleet. The carrier's latest investor presentation confirms that a dedicated premium cabin is "under development" for the Airbus A350-900, with the first of 60 widebodies due to arrive in 2027. The primary targets: London, Paris, Frankfurt, and Amsterdam.

This is not IndiGo's first brush with the front of the cabin. Its "IndiGoStretch" product already sits on 53 Airbus A321neos, and the airline runs non-stop India-to-Europe flights on damp-leased Boeing 787-9s operated with Norse Atlantic Airways. But a purpose-built A350 business class would be a different animal — a full widebody product designed to compete directly with Air India, British Airways, and Lufthansa on routes that carry some of the densest NRI traffic in the world.

## What we know so far

IndiGo has revealed almost nothing about seat configuration, cabin layout, or pricing. The investor slide says "under development" and leaves it there. What is clear is the scale of the commitment: 30 A350-900s ordered in 2024, doubled to 60 in 2025. That is enough to blanket every major India-Europe corridor and still deploy aircraft to Southeast Asia and the Middle East.

The airline's current business-class seat count stands at 2,800 and is projected to hit 4,300 by March 2027 through the narrowbody IndiGoStretch expansion. The A350 fleet would add substantially to that number, though IndiGo has not specified how many premium seats each widebody will carry.

## The fleet economics

IndiGo is also reshuffling how it finances its aircraft. About 75 percent of its current 441-plane fleet sits on operating leases. The airline wants to push the combined share of owned and finance-leased aircraft to between 30 and 40 percent by 2030 — a shift designed to cut long-term costs and give IndiGo more operational flexibility as it scales up its widebody operations.

## Why NRIs should pay attention

The India-Europe corridor is dominated by three tiers: the Gulf carriers (Emirates, Qatar, Etihad) offering one-stop luxury through Dubai and Doha; European legacy carriers (BA, Lufthansa, Air France) flying direct at premium prices; and Air India, which has been rebuilding its product under Tata Group ownership.

IndiGo's entry would add a fourth option — a carrier with the cost discipline that made it India's largest domestic airline by a wide margin. For the roughly 1.8 million NRIs in the UK and hundreds of thousands across continental Europe, that could mean meaningfully cheaper business-class fares on direct routes. IndiGo's narrowbody business class already undercuts Air India on domestic trunk routes by 15 to 25 percent. If it brings that same pricing philosophy to long-haul, the competitive pressure on Air India's newly retrofitted fleet will be intense.

The first A350 delivery is still about a year away. But for NRIs who have been locked into a narrow set of expensive options on the India-Europe run, IndiGo's widebody ambitions represent the most significant competitive shake-up since Air India's privatization."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "IndiGo Is Building a Business Class for Its Long-Haul Fleet — and NRIs Flying to Europe Should Watch Closely",
    "subheadline": "India's largest airline has 60 Airbus A350s on order and a premium cabin under development. The first targets: London, Paris, Frankfurt, and Amsterdam.",
    "slug": make_slug("indigo-a350-business-class-europe-nri"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "IndiGo's cost-disciplined entry into long-haul business class could significantly undercut Air India and European carriers on routes that carry the densest NRI traffic between India and Europe.",
    "tags": ["travel", "airlines", "IndiGo", "business class", "A350", "Europe"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Aviation A2Z", "url": "https://aviationa2z.com/index.php/2026/06/09/indigo-teases-new-business-class-for-airbus-a350-fleet/"},
        {"name": "Travel and Tour World", "url": "https://www.travelandtourworld.com/news/article/indigo-a350-business-class/"},
        {"name": "Flight Global", "url": "https://www.flightglobal.com"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4d/IndiGo_Airbus_A320neo_F-WWDG_%28to_VT-ITI%29_%2828915135713%29.jpg/3840px-IndiGo_Airbus_A320neo_F-WWDG_%28to_VT-ITI%29_%2828915135713%29.jpg",
    "image_caption": "An IndiGo Airbus A320neo — the carrier's workhorse narrowbody, soon to be joined by 60 widebody A350-900s",
    "image_attribution": "Wikimedia Commons",
    "body": art1_body
}

# ─── ARTICLE 2 ────────────────────────────────────────────────────────────────
art2_body = """If you fly Singapore Airlines from India and then transfer to a separate domestic carrier to reach your final US destination, the process just got simpler. Southwest Airlines and Singapore Airlines have launched an interline partnership that stitches their networks together with a single ticket, checked-through baggage, and coordinated connections at three West Coast gateways: Los Angeles, San Francisco, and Seattle.

The arrangement is not a codeshare — Southwest does not sell seats on Singapore Airlines flights, and vice versa. It is an interline agreement, which means passengers can book a combined itinerary through a travel advisor, an online booking platform, or Singapore Airlines directly. The key advantage: one ticket covering the SQ long-haul leg and the Southwest domestic leg, with bags moving between the two carriers without the passenger having to collect and recheck them.

## How it works for NRIs

Singapore Airlines operates daily non-stops from Delhi, Mumbai, Bengaluru, Chennai, Kolkata, Hyderabad, and Ahmedabad to Singapore's Changi hub. From Changi, the airline flies to LAX, SFO, and SEA — the same three airports where the Southwest interline kicks in. Southwest then connects to roughly 120 domestic US destinations, many of which are not served by traditional international carriers.

For an NRI in Hyderabad flying to, say, Albuquerque or Nashville, the old process involved booking Singapore Airlines to SFO, then finding a separate Southwest flight and re-checking bags. The new interline means a single booking, a single luggage handoff, and a single set of protections if something goes wrong with the connection.

## The broader pattern

Southwest has been adding interline partners at a clip. This is its eighth since early 2025, joining Turkish Airlines, Icelandair, and All Nippon Airways on the roster. The strategy is straightforward: Southwest's massive domestic network becomes more valuable when it connects to international long-haul carriers, and those carriers gain access to smaller US cities without operating their own domestic flights.

For Singapore Airlines, the partnership deepens its already strong position in the India-US corridor. SQ has long been a preferred transit option for NRIs who want to avoid the Gulf carriers' one-stop model through Dubai or Doha, and the Southwest link removes the last friction point — the awkward domestic connection on the US side.

## What it does not cover

A few caveats. These itineraries cannot be booked through Southwest's own website or app — only through Singapore Airlines or third-party platforms. The interline does not include frequent flyer reciprocity, so Rapid Rewards points will not accrue on the SQ leg and KrisFlyer miles will not accrue on the Southwest leg. And the partnership covers connections at LAX, SFO, and SEA only — NRIs arriving at JFK or Newark via SQ will not benefit.

Still, for the large NRI populations in the Bay Area, Los Angeles, and the Pacific Northwest, this is a practical upgrade. One booking, one bag drop, one itinerary — and a direct line from India through Changi to destinations across the American interior."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "Southwest and Singapore Airlines Just Linked Their Networks — and NRIs Get a Single Ticket From India to 120 US Cities",
    "subheadline": "The new interline partnership connects Singapore Airlines' India flights with Southwest's domestic US network at LAX, SFO, and SEA — with checked bags flowing through on one booking.",
    "slug": make_slug("southwest-singapore-airlines-interline-nri"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "NRIs who fly Singapore Airlines from India can now connect seamlessly to 120+ US domestic destinations on Southwest with a single ticket and checked-through luggage at LAX, SFO, and SEA.",
    "tags": ["travel", "airlines", "Singapore Airlines", "Southwest", "interline", "NRI"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Travel and Tour World", "url": "https://www.travelandtourworld.com/news/article/ymbjsos7cu7k/"},
        {"name": "Southwest Airlines", "url": "https://www.southwest.com"}
    ]),
    "score_total": 74,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/9/9a/Singapore_Airlines_Airbus_A350-941_F-WZFD_to_9V-SMF.jpg",
    "image_caption": "A Singapore Airlines Airbus A350, the type that connects Indian cities to the carrier's Changi hub",
    "image_attribution": "Wikimedia Commons",
    "body": art2_body
}

# ─── ARTICLE 3 ────────────────────────────────────────────────────────────────
art3_body = """Germany has scrapped its airport transit visa requirement for Indian nationals, effective June 3. France did the same in April. Together, these two moves dismantle a bureaucratic barrier that has frustrated millions of Indian travelers routing through Europe's busiest hubs on their way to destinations in the Americas, Africa, and beyond.

The German Embassy in New Delhi confirmed the change in a statement published on June 2. "Indian nationals will no longer need a transit visa when travelling to another country with a layover at a German airport," the embassy said. The exemption was published in Germany's Federal Law Gazette and traces directly to discussions between Prime Minister Narendra Modi and German Chancellor Friedrich Merz during the latter's visit to India in January.

## What changes — and what does not

The transit visa exemption applies exclusively to passengers who remain in the international transit zone of a German airport while catching a connecting flight to a third country. It does not grant entry into Germany or the wider Schengen area. Travelers who need to exit the airport, collect and recheck luggage on a separate booking, or change terminals still require a Schengen visa.

France enacted an identical change in April, following President Macron's visit to India. The practical effect is that Indian passport holders can now transit through Frankfurt, Munich, Paris-Charles de Gaulle, and other major European hubs without a separate piece of paperwork — provided their onward destination does not require them to leave the secure zone.

## Why this matters for NRIs

For the 4.5 million Indian Americans who regularly fly between the US and India, Germany and France are critical transit corridors. Frankfurt alone handles more than 60 million passengers a year and serves as Lufthansa's primary hub. The Lufthansa Group — which includes SWISS, Austrian Airlines, and Brussels Airlines — operates more than 70 weekly flights between India and Europe. Many of those flights connect through Frankfurt or Munich to destinations across the Americas.

Until now, Indian citizens booking a Lufthansa flight from, say, Hyderabad to Chicago with a connection at Frankfurt needed a separate airport transit visa — even if they never left the terminal. The visa required an application, a fee, supporting documents, and processing time, sometimes adding weeks to trip planning. Multiply that by the hundreds of thousands of Indians transiting through German airports annually, and the friction was significant.

Lufthansa has publicly welcomed the change, calling it a measure that will "simplify travel and improve connectivity, reinforcing Germany's role as a leading gateway between India, Europe and the world." The airline also flagged upcoming developments: SWISS will launch its first-ever direct Bengaluru-to-Zurich service in the 2026 winter schedule, and Lufthansa's new Allegris business-class cabins will roll out on additional Boeing 787-9 services from Delhi and Hyderabad.

## The broader diplomatic context

The transit visa removals are part of a deliberate diplomatic pattern. India has been negotiating easier mobility agreements with European governments in exchange for deeper economic and strategic ties. Germany's decision followed the Modi-Merz summit in Ahmedabad in January. France's followed the Macron visit. Both governments framed the changes as steps toward strengthening people-to-people ties — diplomatic language for a practical calculation that smoother transit makes trade and investment flow more easily.

For NRI families juggling international travel logistics — parents visiting from India, return trips to multiple destinations, holiday routing through European cities — two fewer visa applications per year is a meaningful reduction in friction. Frankfurt and Paris are now as simple to transit as Dubai or Doha, without the paperwork overhead that used to make Gulf hubs the path of least resistance."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "Germany and France Have Both Dropped Transit Visa Requirements for Indians — and NRIs Routing Through Europe Just Lost a Major Headache",
    "subheadline": "Indian passport holders can now transit through Frankfurt, Munich, and Paris without a separate visa. For the millions of NRIs who fly through European hubs, the paperwork just got lighter.",
    "slug": make_slug("germany-france-transit-visa-dropped-indians-nri"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "Millions of NRIs route through Frankfurt and Paris on Lufthansa and Air France connections between the US and India — the transit visa removal eliminates a costly paperwork step that made Gulf hubs more attractive.",
    "tags": ["travel", "visa", "Germany", "France", "transit", "Schengen", "NRI", "Lufthansa"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "NewsPoint", "url": "https://newspoint.tv/germany-scraps-airport-transit-visa-for-indians/"},
        {"name": "NewKerala", "url": "https://www.newkerala.com"},
        {"name": "APAC News Network", "url": "https://apacnewsnetwork.com"},
        {"name": "Bhasha Times", "url": "https://bhashatimes.com"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/14/Airport%2C_Frankfurt_%28P1180126%29.jpg/1280px-Airport%2C_Frankfurt_%28P1180126%29.jpg",
    "image_caption": "Frankfurt Airport terminal — one of Europe's busiest transit hubs for Indian travelers",
    "image_attribution": "Wikimedia Commons",
    "body": art3_body
}

# ─── INSERT ───────────────────────────────────────────────────────────────────
articles = [art1, art2, art3]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

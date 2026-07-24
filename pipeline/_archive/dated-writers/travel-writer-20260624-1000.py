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
        "headline": "Navi Mumbai's First International Flight Is a Gulf Run — and a Preview of Where Your Relatives Will Land",
        "subheadline": "Air India Express opens the new greenfield airport to overseas traffic on July 15 with a twice-weekly Abu Dhabi service, the first crack in Mumbai's single-airport bottleneck.",
        "slug": make_slug("navi-mumbai-airport-first-international-flight-abu-dhabi-air-india-express-nri"),
        "category": "travel",
        "vertical": "aviation",
        "diaspora_angle": "For the western-India diaspora flying home through a chronically congested Mumbai airport, a second international gateway across the harbour means a real alternative — and a Gulf hub that connects onward to North America and Europe.",
        "tags": ["travel", "airlines", "airports", "air india express", "navi mumbai"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/air-india-express-launches-historic-navi-mumbai-international-airport-to-abu-dhabi-direct-flights/"},
            {"name": "Travel + Leisure Asia", "url": "https://www.travelandleisureasia.com/in/news/air-india-express-navi-mumbai-abu-dhabi-direct-flights/"},
            {"name": "Aviation A2Z", "url": "https://aviationa2z.com/index.php/2026/06/21/air-india-express-launching-new-flights-from-navi-mumbai/"}
        ]),
        "score_total": 80,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/62/Navi_Mumbai_Airport_%2896252%29.jpg/1280px-Navi_Mumbai_Airport_%2896252%29.jpg",
        "image_caption": "The terminal at Navi Mumbai International Airport, which begins international service on July 15, 2026",
        "image_attribution": "Wikimedia Commons",
        "body": """Air India Express will fly the first international service out of Navi Mumbai International Airport on July 15, a twice-weekly run to Abu Dhabi that turns India's newest mega-airport from a domestic curiosity into a working overseas gateway. Flights begin on Wednesdays and Fridays, with a third weekly frequency added from July 29 as bookings firm up.

It is a modest schedule for a story that is anything but modest. Navi Mumbai opened for domestic traffic only in December 2025, and it is already handling roughly 20,000 passengers a day, with operators projecting 50,000 daily movements by year-end. Air India Express alone plans 30 weekly flights from the airport, linking Abu Dhabi with Bengaluru and Delhi on the domestic side.

## Why a Gulf Route Goes First

The choice of Abu Dhabi is not sentimental. The UAE is consistently the single largest international destination for Indian travellers — a blend of work, family, tourism and trade — and the western-India catchment around Mumbai is one of the densest sources of that traffic. A low-cost carrier on a high-volume Gulf sector is the safest possible way to prove a brand-new airport's customs, immigration and ground systems before the long-haul carriers arrive.

A customs readiness review on June 16 cleared the airport for international passenger processing, cargo handling and security — the regulatory greenlight without which no overseas launch could proceed. The airport had originally targeted a March 2026 international debut, delayed by the spring's geopolitical disruptions in West Asia.

## What It Means for the Diaspora

For NRIs, the significance is less about the Abu Dhabi flight itself and more about what it signals. Chhatrapati Shivaji Maharaj International Airport in Mumbai has run at the edge of its capacity for years, and the experience of connecting home through it — long taxi queues, congested airspace, tight transfer windows — is a familiar grievance for anyone flying in from the Gulf, Europe or North America.

Navi Mumbai is the pressure valve. Operated under Adani Group stewardship with a minority stake held by CIDCO, it is designed to absorb the western region's overflow rather than compete head-to-head with the old airport. Abu Dhabi matters here because it is itself a connecting hub: from Zayed International, onward networks reach North America, Europe and Africa. A Bay Area or tri-state Gujarati or Maharashtrian family could, in time, route home via Abu Dhabi and land at an uncongested terminal 40 kilometres from south Mumbai.

## The Catch, For Now

The early schedule is thin, and the airport is scaling into congestion rather than out of it. Industry watchers expect a rush of domestic and international carriers to announce Navi Mumbai routes over the coming operational cycle, which will stress ground infrastructure and immigration throughput before the second runway and full terminal capacity come online. IndiGo, the launch partner for the airport, has said it will eventually run up to 79 daily departures from Navi Mumbai, including 14 international.

For travellers booking this summer, the practical advice is simple: the Abu Dhabi flight is real and bookable, but Navi Mumbai's value as a homecoming gateway will compound over the next 12 to 18 months as more carriers and more destinations come on. Keep an eye on which airport your inbound ticket actually lands at — for the western-India diaspora, that line on the itinerary is about to start mattering a great deal.

## What's Next

Air India Express adds its third weekly Abu Dhabi frequency on July 29. Freighter operations are expected to scale toward 18 weekly flights, and more carriers are likely to announce international routes from Navi Mumbai before the winter schedule. The longer-term test is whether the airport's immigration and customs capacity can keep pace with a passenger curve that is rising faster than almost any greenfield airport in the world."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Sri Lanka's Tourist Visa Is Free for Indians Again — and the Catch Is Smaller Than the Saving",
        "subheadline": "Colombo has waived the ETA fee for Indian passport holders and 39 other nationalities, handing the diaspora's easiest South Asian beach-and-heritage trip an extra incentive.",
        "slug": make_slug("sri-lanka-free-eta-tourist-visa-indians-2026-nri-beach-heritage"),
        "category": "travel",
        "vertical": "visa-policy",
        "diaspora_angle": "For NRIs stitching a Sri Lanka stop into a trip home to South India, a free 30-day double-entry ETA removes a per-head cost that quietly adds up across a family booking — and makes the island a genuine rival to Thailand and Bali.",
        "tags": ["travel", "visa", "sri lanka", "eta", "south asia"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Sri Lanka Department of Immigration & Emigration", "url": "https://www.immigration.gov.lk/"},
            {"name": "Travel + Leisure Asia", "url": "https://www.travelandleisureasia.com/in/news/sri-lanka-waives-eta-fees-40-nations-including-india/"},
            {"name": "BAL Global Immigration", "url": "https://www.bal.com/bal-news/sri-lanka-tourist-visa-fee-waiver-introduced-for-40-countries/"}
        ]),
        "score_total": 74,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7b/Colombo_Lotus_Tower_seen_Galle_Road.jpg/1280px-Colombo_Lotus_Tower_seen_Galle_Road.jpg",
        "image_caption": "The Colombo Lotus Tower seen from Galle Road, a landmark of Sri Lanka's capital",
        "image_attribution": "Wikimedia Commons",
        "body": """Sri Lanka has waived the tourist visa fee for Indian passport holders, part of a 40-country fee waiver that took effect on May 25 and has now been extended toward the next tourism season. Indian travellers still need an Electronic Travel Authorisation (ETA) before flying, but the application charge — the part that actually cost money — is gone. The authorisation is valid for 30 days with a double-entry facility.

For a destination India can reach in under a few hours from most southern metros, the change is a meaningful sweetener. Colombo is leaning hard on Indian arrivals as the centrepiece of its tourism revival, and India is comfortably its largest inbound market.

## What Actually Changed

The mechanics are worth getting right, because "free visa" headlines tend to oversimplify. Indians must still apply for the ETA online through the official Sri Lankan immigration portal before departure — the requirement to obtain authorisation has not been scrapped, only the fee. The ETA grants a 30-day stay with double entry within that window, which is genuinely useful for travellers using Sri Lanka as a base for a wider South Asian itinerary or hopping out to the Maldives and back.

A few practical guardrails remain. Your passport should be valid for at least six months from the date of arrival, and immigration officers may still ask for confirmed return tickets and accommodation details on landing. Crucially, apply through the official government portal rather than the third-party sites that crowd search results and layer on their own service charges — the entire point of the waiver is to pay nothing, and a lookalike site will quietly undo that.

## Why It Matters to the Diaspora

For the Indian-American family, the appeal is less about the absolute saving than about the convenience math. An NRI travelling home to Chennai, Bengaluru or Kochi can fold a four- or five-day Sri Lanka leg onto an existing India trip without a separate long-haul fare and without a visa fee per family member. Earlier, that ETA charge added up across a booking of four or five; with it waived, the island competes directly with the Southeast Asian destinations — Thailand, Bali — that have spent years courting Indian outbound travel.

The double-entry feature is the underrated part. It lets a traveller enter Sri Lanka, slip out to a neighbouring destination, and return within the 30-day window on the same authorisation — exactly the kind of flexibility a multi-stop diaspora itinerary rewards.

## The Itinerary Case

Sri Lanka packs an unusual amount into a small island: the beaches of the south and east coasts, the hill-country tea estates and the Nine Arches Bridge at Ella, the ancient rock fortress at Sigiriya, the wildlife circuits at Yala and Udawalawe, and the cultural triangle around Kandy and Anuradhapura. For families with older relatives, the short flight and gentle pace make it a softer option than a long-haul Southeast Asia trip.

## What's Next

The fee waiver has been positioned as part of Colombo's longer tourism push rather than a one-off, with the eligibility window extended toward the next high season. Travellers should still confirm the current ETA rules on the official immigration portal before booking, since Sri Lanka's visa system has seen operational wobbles in recent years — including a contested switch between ETA operators. For now, the deal is straightforward and real: apply online, pay nothing, get 30 days and two entries."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Germany Just Dropped the Airport Transit Visa for Indians — One Less Form Between You and the Connection",
        "subheadline": "From June 3, Indian passport holders no longer need a transit visa to change planes at a German airport, smoothing one of Europe's busiest connecting points for diaspora travel.",
        "slug": make_slug("germany-airport-transit-visa-removed-indians-frankfurt-munich-nri"),
        "category": "travel",
        "vertical": "visa-policy",
        "diaspora_angle": "Frankfurt and Munich are major one-stop gateways between India and North America; scrapping the transit visa removes paperwork, cost and delay for NRIs routing home through Lufthansa's German hubs.",
        "tags": ["travel", "visa", "germany", "transit", "europe"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Travel + Leisure Asia", "url": "https://www.travelandleisureasia.com/in/news/german-transit-visa-removed-for-indian-passport-holders/"},
            {"name": "Ministry of External Affairs (India)", "url": "https://www.mea.gov.in/"}
        ]),
        "score_total": 72,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/14/Airport%2C_Frankfurt_%28P1180126%29.jpg/1280px-Airport%2C_Frankfurt_%28P1180126%29.jpg",
        "image_caption": "Frankfurt Airport, one of Europe's busiest connecting hubs for India-to-North America travel",
        "image_attribution": "Wikimedia Commons",
        "body": """Germany has removed the airport transit visa requirement for Indian passport holders, a small-sounding change that quietly improves one of the diaspora's most-used connecting routes. The exemption took effect on June 3, after publication in Germany's Federal Law Gazette (the Bundesgesetzblatt), and applies to Indians transiting through any German airport by air on the way to a third country.

The Ministry of External Affairs welcomed the move, noting it stemmed from discussions between Prime Minister Narendra Modi and German Chancellor Friedrich Merz during the latter's January visit to India. It is the kind of bilateral housekeeping that rarely makes front pages but reshapes the daily experience of travel.

## What the Transit Visa Was — and Why It Annoyed Travellers

An airport transit visa is required, in some countries, even when a passenger never leaves the secure international zone of an airport and simply changes planes. For Indian travellers connecting through Germany to a non-Schengen destination, that previously meant extra paperwork, an extra fee and the attendant risk of delay — all for the privilege of walking from one gate to another.

Removing it means an Indian passport holder can now transit airside through Frankfurt, Munich or another German airport without applying for anything, provided they are not entering Germany itself. (Travellers who plan to leave the airport or stay in the Schengen area still need the appropriate Schengen visa — the change is strictly about airside transit.)

## Why It Matters to the Diaspora

Frankfurt is one of the principal one-stop gateways between India and the United States and Canada, and Lufthansa's German hubs at Frankfurt and Munich carry a large share of India–North America connecting traffic. For an NRI flying, say, Delhi or Bengaluru to a US city via Frankfurt, the old transit-visa requirement was an avoidable friction point — particularly for travellers whose itineraries shifted at the last minute onto a German-hub routing.

Germany's move also fits a broader pattern of Europe easing the path for Indian travellers. The EU's Schengen visa "cascade" regime already lets frequent Indian visitors graduate to two-year and then five-year multiple-entry visas after an established travel history, and France has extended post-study visa rights for Indian graduates. The transit-visa waiver is a narrower change, but it removes a recurring irritant for exactly the connecting journeys the diaspora makes most.

## The Practical Read

If you are booking a one-stop ticket home or onward through Germany this summer, the German leg no longer carries a transit-visa box to tick. That said, the usual cautions apply: confirm whether your specific routing keeps you airside, check that your onward destination's entry rules are in order, and remember that any plan to actually enter Germany or the wider Schengen zone still requires a Schengen visa.

## What's Next

The exemption is now reflected in German law and operational at German airports. With Lufthansa and partner carriers continuing to anchor India–North America connectivity through Frankfurt and Munich, the change should make German-hub routings marginally more attractive on price and hassle — a quiet win for a diaspora that spends a lot of its life in transit halls."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

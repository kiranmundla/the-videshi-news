#!/usr/bin/env python3
"""Travel writer — 2026-06-07 batch"""
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


# ────────────────────────────────────────────
# ARTICLE 1: Air India + Riyadh Air MoU
# ────────────────────────────────────────────

art1_body = """Air India and Saudi Arabia's Riyadh Air have signed a memorandum of understanding that, if regulators approve, will create codeshare and interline arrangements linking Delhi, Mumbai, and Riyadh into a single booking network. The deal, announced on June 5, also covers loyalty programme reciprocity, cargo cooperation, and joint digital initiatives.

The timing is deliberate. Riyadh Air — Saudi Arabia's new premium national carrier, established in 2023 — launches its inaugural commercial flights to London Heathrow on July 1 and is positioning Riyadh as a global aviation hub to rival Dubai, Doha, and Abu Dhabi. Air India, now three years into its post-Tata transformation, has already built 25 codeshare partnerships and more than 120 interline agreements covering over 1,000 destinations worldwide. A Saudi tie-up adds a missing corridor to that map.

x-official:https://x.com/airindia/status/2062423722611634513

## What NRIs Should Actually Expect

For Indian Americans, the practical benefits are still years away from full fruition. The MoU is a statement of intent, not an operational launch. Codeshare flights — where you book an Air India ticket and fly a Riyadh Air leg, or vice versa — require bilateral regulatory approval that has historically moved slowly between India and Saudi Arabia.

The two countries last expanded their air services agreement in 2008, capping weekly capacity at 20,000 seats and 75 services. That ceiling has frustrated Gulf carriers for over a decade. "Partnerships like this widen the door; only bilaterals can make it bigger," Linus Bauer, founder of consultancy BAA & Partners, told AGBI.

Saj Ahmad, chief analyst at StrategicAero Research, was more blunt: "Riyadh Air is still in its infancy and has almost nothing to offer Air India in return at present."

## Why It Still Matters to the Diaspora

India and Saudi Arabia share one of the world's densest migration corridors. An estimated 2.6 million Indians live and work in the Kingdom — the largest expatriate community in Saudi Arabia. For NRIs in the US making multi-stop journeys through the Gulf, a functional codeshare between Air India and Riyadh Air would mean single-ticket itineraries, smoother luggage transfers, and loyalty points that actually accumulate rather than evaporate across separate bookings.

The religious travel angle is equally significant. Roughly 200,000 Indian Muslims travel for Hajj and Umrah annually, and that number is growing. Better connectivity through Riyadh — rather than the traditional Dubai and Doha routing — adds competition to a corridor where pricing has historically favoured the incumbent Gulf carriers.

Campbell Wilson, Air India's CEO, called India and Saudi Arabia "two important growth markets in global aviation" with "scale and momentum" that make the partnership natural. Riyadh Air CEO Tony Douglas described India as "one of the most important aviation markets in the world."

## The Bigger Picture

The MoU arrives against a backdrop of escalating Gulf competition. Saudia, the Kingdom's existing flag carrier, already activated a codeshare with Air India in February. Emirates has been trimming capacity due to Middle East airspace disruptions. And Air India itself is in the middle of a fleet modernisation that includes 250+ aircraft on order.

For NRIs booking travel between the US and India through Gulf hubs, the deal signals that Riyadh is serious about becoming a third viable transit option alongside Dubai and Doha. Whether the bilateral seat caps loosen fast enough to make that real before 2028 remains the open question."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Air India and Riyadh Air Sign a Deal That Could Reshape How NRIs Fly Through the Gulf",
    "subheadline": "A new MoU promises codeshares, loyalty perks, and single-ticket bookings through Riyadh — but bilateral seat caps between India and Saudi Arabia remain the real bottleneck.",
    "slug": make_slug("air-india-riyadh-air-mou-nri-gulf-travel"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "2.6 million Indians in Saudi Arabia, Hajj/Umrah corridor, and NRIs transiting through Gulf hubs on US-India routes stand to benefit from codeshare and loyalty reciprocity — once bilateral caps loosen.",
    "tags": ["travel", "airlines", "air-india", "riyadh-air", "saudi-arabia", "codeshare", "gulf"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "AGBI", "url": "https://www.agbi.com/analysis/aviation/2026/06/riyadh-airs-deal-with-air-india-takes-a-long-term-view/"},
        {"name": "DevDiscourse", "url": "https://www.devdiscourse.com/article/headlines/3378521-air-india-and-riyadh-air-forge-strategic-alliance-for-seamless-global-connectivity"},
        {"name": "The Indian News NZ", "url": "https://indiannews.nz/air-india-riyadh-air-sign-agreement/"},
        {"name": "Aviation Week", "url": "https://aviationweek.com/air-transport/airlines-lessors/riyadh-air-air-india-pursue-codeshare-interline-collaboration"}
    ]),
    "score_total": 78,
    "status": "published",
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/4/45/VT-JRF_%40_JFK%2C_2024-11-04.png",
    "image_caption": "An Air India Boeing 777 on the tarmac at New York JFK",
    "image_attribution": "Wikimedia Commons",
    "is_editorial": False,
    "body": art1_body
}


# ────────────────────────────────────────────
# ARTICLE 2: Gulf Carrier Rebooking Amid Middle East Disruptions
# ────────────────────────────────────────────

art2_body = """If you are an NRI with summer flights routed through Dubai, Doha, Abu Dhabi, or Jeddah, your itinerary is no longer a certainty. Ongoing geopolitical tensions across the Middle East — including airspace closures over Kuwait and disrupted flight paths near Iran — have forced Qatar Airways, Emirates, Etihad, Gulf Air, and Saudia to introduce emergency rebooking and refund policies. Here is what each airline is offering, and what you should do now.

## The Problem: Gulf Hubs Are the Backbone of US-India Travel

The Middle East handles a disproportionate share of traffic between the United States and India. For NRIs flying from secondary US cities — think Cleveland, Tampa, Pittsburgh, Raleigh — Gulf carriers often provide the only one-stop options to Indian cities beyond Delhi and Mumbai. When airspace closes or schedules shift, the cascading impact is enormous: 414 flights were cancelled and 6,188 delayed across Asian hubs in a single recent day, according to consolidated operational data.

The IATA's vice president for the Middle East, Kamil Al-Awadhi, told Reuters that a recent Iranian attack on Kuwait's airport damaged a terminal used by foreign carriers, with repairs likely to "take ages." Global airlines are raising fares and slashing capacity to offset higher fuel and rerouting costs.

## What Each Airline Is Offering

**Qatar Airways** has the most generous policy: up to two free date changes and travel validity extended through October 31, 2026. If your flight was impacted, you can rebook or claim a full refund.

**Emirates** is allowing one complimentary date change and processing refunds within approximately 15 days. The policy applies to eligible bookings with travel completion by June 15.

**Etihad** has a narrower window: rebooking fee waivers apply only to tickets purchased before February 28 with travel scheduled through April 15. Refunds are available for those who no longer wish to transit through Abu Dhabi.

**Gulf Air** is waiving change and cancellation fees for eligible passengers, with a travel completion deadline of June 30, 2026.

**Saudia** lets affected passengers reschedule within 14 days of service resumption, retain ticket value as credit, or request a one-time cancellation fee waiver.

x-official:https://x.com/IndiGo6E/status/2062904837382242458

## What NRIs Should Do Right Now

**Check your routing.** If your summer ticket transits through any Gulf hub, log into your airline account and check for schedule change notifications. Some itineraries have been quietly shifted without a separate email alert.

**Don't wait on refunds.** If you are eligible, initiate the process now. Emirates says 15 days; other carriers may take longer during peak disruption periods.

**Consider direct alternatives.** Air India operates nonstops from JFK and Newark to Delhi and Mumbai. United flies SFO-Delhi nonstop. These avoid Gulf airspace entirely and, while typically pricier, eliminate transit risk. One-way fares from JFK to Mumbai are currently available from around $560 on Air India.

**Buy travel insurance if you haven't.** With airspace closures escalating, policies that cover trip interruption and flight cancellation are no longer optional for Gulf-routed itineraries.

**Watch visa validity.** If your rebooked dates push travel beyond your visa's validity window, you may need to reapply. This is especially relevant for Indian tourists on short-validity e-visas visiting family.

## The Bigger Picture

India's government has already moved to insulate domestic carriers with a ₹10,000 crore ATF Price Stabilisation Fund — a direct response to fuel costs surging from Middle East instability. But for individual NRI travelers, the practical question is simpler: is your summer trip home still happening on the dates you planned? For many, the answer requires a phone call to your airline this week."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "Your Gulf-Routed Flight Home May Not Happen as Planned — Here's What Every NRI Needs to Know",
    "subheadline": "Qatar Airways, Emirates, Etihad, Gulf Air, and Saudia have rolled out emergency rebooking and refund policies as Middle East airspace disruptions upend the US-India travel corridor.",
    "slug": make_slug("gulf-airlines-rebooking-refund-nri-middle-east-disruptions"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "Most NRIs fly to India through Gulf hubs. With airspace closures and cancellations escalating, understanding each carrier's rebooking and refund policy is urgent for anyone with summer travel planned.",
    "tags": ["travel", "airlines", "gulf", "middle-east", "flights", "refund", "rebooking", "nri"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/d6s7wyjeg09f/"},
        {"name": "Reuters", "url": "https://www.reuters.com/business/aerospace-defense/not-wise-middle-eastern-carriers-defer-deliveries-due-war-airlines-vp-says-2026-06-07/"},
        {"name": "Travel And Tour World (UAE Disruptions)", "url": "https://www.travelandtourworld.com/news/article/uae-middle-east-travel-disruptions/"}
    ]),
    "score_total": 85,
    "status": "published",
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/6/6e/1_Dubai_International_Airport_Terminal_3.jpg",
    "image_caption": "Dubai International Airport Terminal 3, a key transit hub for US-India travelers",
    "image_attribution": "Wikimedia Commons",
    "is_editorial": False,
    "body": art2_body
}


# ────────────────────────────────────────────
# ARTICLE 3: IndiGo Exits Manchester
# ────────────────────────────────────────────

art3_body = """IndiGo will suspend all flights between India and Manchester on August 31, 2026 — just 14 months after launching the route — leaving Manchester Airport without a single direct scheduled service to the subcontinent. The airline currently operates three weekly flights from Delhi and four from Mumbai, all using Boeing 787-9 Dreamliners wet-leased from Norse Atlantic Airways.

The carrier blamed "continuing international airspace constraints leading to significantly increased flight duration and a challenging cost environment." Translation: Middle East airspace disruptions are forcing longer routings, burning more fuel, and stretching crew schedules past the point where the economics work.

## Why Manchester Matters for NRIs in Britain

Manchester is home to the UK's second-largest Indian-origin population outside London. The 2021 census recorded over 180,000 people of Indian, Pakistani, and Bangladeshi heritage in Greater Manchester, and the wider North of England — Leeds, Bradford, Birmingham — adds hundreds of thousands more. For these communities, direct flights to Delhi and Mumbai eliminated the mandatory Heathrow transfer that turned every trip home into a two-airport ordeal.

IndiGo launched the route in July 2025 specifically to tap this market, betting that demand from the diaspora would sustain premium pricing on a route no other carrier was serving. The demand was there. "We witnessed very encouraging demand response," said Abhijit Dasgupta, IndiGo's SVP of Network Planning. But demand alone cannot overcome the cost arithmetic when flight times balloon by 90+ minutes due to airspace rerouting.

## The Cost Squeeze Is Real

IndiGo's Manchester exit is not an isolated decision. In the same week, the airline suspended flights to six Southeast Asian destinations — Hong Kong, Shanghai, Ho Chi Minh City, Langkawi, Krabi, and Siem Reap — effective July 1 through September 30. It had already pulled Copenhagen in February and trimmed Delhi-London Heathrow frequencies.

The common thread is the Boeing 787-9 fleet. IndiGo leased six of these widebodies from Norse Atlantic as a bridge until its own Airbus A350s arrive. With only six aircraft and rising per-flight costs, every uneconomic route cannibalises schedule reliability for the remaining long-haul network. Returning one 787 to Norse is the airline's way of right-sizing capacity to match what it can profitably operate.

Industry-wide, the numbers are stark. Aviation turbine fuel costs have surged amid Iran-linked instability. Foreign exchange volatility has compounded the problem for rupee-denominated carriers. And airspace restrictions over parts of the Middle East mean flights that used to take 9 hours from Delhi to Manchester now take upwards of 10.5 hours — a cost increase that passengers do not see but airlines absorb on every sector.

## What UK-Based NRIs Should Do

**If you have bookings after August 31:** IndiGo says it will contact affected passengers with rebooking or refund options. Don't wait — initiate contact through the app or website now.

**Alternative routings:** Air India operates Delhi-London Heathrow and Mumbai-London Heathrow nonstops. British Airways serves Heathrow-Delhi and Heathrow-Mumbai. From Manchester, you will need to connect through Heathrow, or route via a Gulf hub on Emirates (Dubai), Qatar Airways (Doha), or Etihad (Abu Dhabi). Each adds 3-6 hours to total travel time compared to IndiGo's direct service.

**Will the route come back?** IndiGo says the suspension is "temporary in nature" and that it is "exploring innovative solutions." The most likely scenario: the route returns when IndiGo takes delivery of its own A350 fleet and Middle East airspace normalises — neither of which has a firm timeline.

## The Lesson for India's Long-Haul Ambitions

IndiGo's Manchester experiment was always a calculated risk. The airline built its empire on domestic short-haul efficiency, and stretching into 9-hour sectors with leased widebodies was a departure from its core competence. The encouraging demand response proves the market exists. The retreat proves that operating in it requires either your own fleet or airspace conditions that don't destroy your cost base. For now, Manchester's Indian diaspora is back to connecting through London or the Gulf — and paying the time penalty that comes with it."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "IndiGo Pulls Out of Manchester After 14 Months — and Britain's Biggest Indian Community Outside London Loses Its Only Direct Link Home",
    "subheadline": "Rising fuel costs, Middle East airspace disruptions, and a leased widebody fleet that couldn't absorb the overruns have ended IndiGo's first major European experiment.",
    "slug": make_slug("indigo-manchester-exit-uk-nri-diaspora"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "Manchester's 180,000+ South Asian residents and the wider North of England diaspora lose direct flights to Delhi and Mumbai, forcing a return to Heathrow connections or Gulf hub routings.",
    "tags": ["travel", "airlines", "indigo", "manchester", "uk", "nri", "boeing-787"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Secret Manchester", "url": "https://secretmanchester.com/major-airline-announces-suspension-of-all-flights-from-manchester-airport/"},
        {"name": "Aviation A2Z", "url": "https://www.aviationa2z.com/indigo-cancels-flights-to-these-6-international-destinations/"},
        {"name": "Rust Tourism News", "url": "https://www.rustourismnews.com/indigo-to-end-manchester-flights/"},
        {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com/economy/logistics/indigo-to-suspend-copenhagen-operations-trims-flights-on-delhi-manchester-route/article69193248.ece"}
    ]),
    "score_total": 72,
    "status": "published",
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4d/IndiGo_Airbus_A320neo_F-WWDG_%28to_VT-ITI%29_%2828915135713%29.jpg/3840px-IndiGo_Airbus_A320neo_F-WWDG_%28to_VT-ITI%29_%2828915135713%29.jpg",
    "image_caption": "An IndiGo Airbus A320neo — the airline's long-haul Manchester route used leased Boeing 787-9s",
    "image_attribution": "Wikimedia Commons",
    "is_editorial": False,
    "body": art3_body
}

# ────────────────────────────────────────────
# PUBLISH
# ────────────────────────────────────────────
articles = [art1, art2, art3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

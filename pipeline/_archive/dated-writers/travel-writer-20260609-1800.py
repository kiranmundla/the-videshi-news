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
        "headline": "The World Cup Starts Thursday — Here's What Indians With Indian Passports Need to Know Before Boarding",
        "subheadline": "No special FIFA visa exists, ICE enforcement is at an all-time high, and failing to carry your I-94 is now a federal misdemeanor. A practical checklist for Indian fans flying stateside.",
        "slug": make_slug("world-cup-2026-indian-passport-visa-entry-guide"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "Tens of thousands of Indians are expected to fly to the US for the 2026 FIFA World Cup. Indian passport holders face stricter entry requirements than VWP-eligible nationals, and the current US immigration climate demands meticulous document preparation.",
        "tags": ["travel", "visa", "fifa-world-cup", "immigration", "indian-passport"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Fragomen", "url": "https://www.fragomen.com/insights/us-visitor-visa-rules-for-the-2026-fifa-world-cup-what-fans-should-know.html"},
            {"name": "Dickinson Wright Immigration Blog", "url": "https://immigration.dickinson-wright.com/2026/04/01/fifa-world-cup-2026-your-guide-to-u-s-visas-and-travel/"},
            {"name": "The Travel", "url": "https://www.thetravel.com/us-world-cup-visitors-warned-carry-passports/"},
            {"name": "U.S. Department of State", "url": "https://travel.state.gov/content/travel/en/us-visas/tourism-visit/visitor.html"}
        ]),
        "score_total": 85,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/34201725/pexels-photo-34201725.jpeg",
        "image_caption": "Aerial view of a packed football stadium during a World Cup match",
        "image_attribution": "Pexels",
        "body": """The 2026 FIFA World Cup kicks off on Thursday in the United States, and for Indian football fans, the logistics of getting there are more complicated than deciding which group-stage match to attend. India is not part of the Visa Waiver Program, which means there is no ESTA shortcut — every Indian passport holder needs a valid B1/B2 visitor visa stamped in their passport before they board.

## No Special World Cup Visa Exists

FIFA does not issue travel authorizations. The US government has created no special exemption, fast-track lane, or event-specific visa for the tournament. Whether you are attending one match in San Francisco or following a team across eleven host cities over six weeks, the standard B1/B2 tourist visa rules apply in full.

That means the usual checklist: a valid passport with at least six months of remaining validity beyond your planned stay, a completed DS-160 application, proof of ties to India (employment letter, property documents, family obligations), evidence of sufficient funds, and confirmed hotel bookings or a letter of invitation from a US-based host.

## Appointment Backlogs and the Time Crunch

Here is the hard reality for procrastinators: B1/B2 interview wait times at US consulates in India have ranged from a few days at smaller posts to several weeks at high-demand locations like Mumbai and New Delhi. With the tournament running from June 11 through July 19, anyone who has not already secured their visa is cutting it dangerously close. Expedited appointments are available in limited circumstances, but "I bought a match ticket" is not among the qualifying criteria.

For those who already hold a valid ten-year B1/B2 visa — common among frequent NRI visitors and business travelers — the path is simpler. Ensure your visa sticker is physically intact and your passport has not expired. If your visa is in an old passport, carry both the old and new passports together.

## Carry Your Documents — It Is Now Federal Law

This is the part most Indian travelers underestimate. Under current US law, every foreign national aged 18 or older must carry registration documents proving legal presence at all times. For B1/B2 visitors, that means your I-94 admission record, which you must download from the CBP website (i94.cbp.dhs.gov) after clearing immigration at your port of entry.

Failing to carry your I-94 is classified as a Class B federal misdemeanor, punishable by a fine of up to $5,000 and up to 30 days in jail. This is not a theoretical risk. Multiple foreign governments — including the UK, Australia, and Canada — have issued explicit warnings to their citizens traveling to the US for the World Cup, advising them to carry passports and proof of legal status at all times.

The UK government's advisory is blunt: "Always carry a passport showing you have permission to enter or remain in the US." Australia's Smartraveller website warns that "US authorities actively pursue, detain, and deport people who are in the country illegally" and that visitors should "be prepared to show documents proving your legal presence."

## Biometrics at the Border

Most US ports of entry now use facial recognition technology to verify traveler identities. Indian passport holders will also be subject to digital fingerprinting. None of this is new, but the sheer volume of arrivals during a 39-day, 78-match tournament across eleven cities means longer processing times at immigration counters are virtually guaranteed.

If you are arriving at one of the host-city airports — SFO, LAX, JFK/EWR, ATL, IAH, DFW, SEA, MIA, PHL, BOS, or Kansas City — expect heavier-than-usual queues. Arrive with all documents organized: passport, visa page, printed I-94 (download immediately after entry), hotel confirmation, match tickets, and proof of return travel.

## What NRIs Should Tell Their Relatives

For the millions of Indian Americans whose parents, siblings, or friends are flying in from India for the tournament, this is a practical conversation to have now — not at the departure gate. Walk them through the I-94 download process. Remind them that a match ticket is not a travel document. And if they are planning to cross into Mexico or Canada during the trip, ensure they understand re-entry requirements — a valid US visa does not automatically guarantee readmission.

The World Cup is a once-in-a-generation event on American soil. The football will be spectacular. But for Indian passport holders, the paperwork needs to be just as solid as the game plan.

*Sources: Fragomen LLP, Dickinson Wright Immigration Insights, Australian Government Smartraveller, UK Foreign Office Travel Advice*"""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India's Monsoon Waterfalls Just Came Alive — Six Cascades NRIs Should Add to Their Trip Home",
        "subheadline": "The southwest monsoon has reached Kerala and is marching north. For NRIs timing a summer visit to India, these six waterfalls are at their most dramatic right now — and half of them are virtually crowd-free.",
        "slug": make_slug("india-monsoon-waterfalls-nri-travel-guide"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "NRIs visiting India during June-September typically chase weddings, festivals, and family time. Few realize that monsoon season transforms India's waterfalls into world-class natural spectacles — at a fraction of December airfare prices.",
        "tags": ["travel", "monsoon", "waterfalls", "india", "nature", "offbeat"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The New Indian Express / Indulge", "url": "https://www.indulgexpress.com/travel/india/2026/Jun/08/6-best-waterfalls-in-india-before-the-monsoon-rains-arrive-43625.html"},
            {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/india-just-became-the-hottest-global-trend-for-slow-travel-enthusiasts/"},
            {"name": "Agoda Travel Data", "url": "https://www.travelandtourworld.com/news/article/indian-travellers-abandon-crowded-cities-and-beaches/"}
        ]),
        "score_total": 72,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/81/The_View_of_the_Athirapally_Falls_during_the_onset_of_Monsoon.jpg/3840px-The_View_of_the_Athirapally_Falls_during_the_onset_of_Monsoon.jpg",
        "image_caption": "Athirappilly Falls in Kerala during the onset of monsoon season",
        "image_attribution": "Wikimedia Commons",
        "body": """The southwest monsoon hit the Kerala coast last week, right on schedule. Within days, it will push through Karnataka, Goa, and Maharashtra, and by mid-July it will drench Meghalaya's Cherrapunji — one of the wettest places on Earth. For NRIs planning a summer trip to India, this is not a reason to postpone. It is the reason to go.

India's waterfalls spend most of the year as modest trickles or dry rock faces. The monsoon turns them into roaring, mist-throwing spectacles that rival anything in Iceland or Patagonia. And unlike those destinations, a domestic flight from Delhi or Mumbai plus a short drive gets you there for a fraction of the cost.

## Athirappilly Falls, Kerala

Often called the "Niagara of India" — a comparison that undersells it — Athirappilly is a 24-metre horseshoe cascade on the Chalakudy River in Thrissur district. During monsoon, the falls widen to their full breadth and the surrounding rainforest turns an almost violent green. A recently upgraded walkway leads to both the top and bottom viewpoints. The nearest luxury option is a resort perched above the gorge, where you can watch the falls from your room. Fly into Kochi (COK), drive 90 minutes.

**NRI tip:** Athirappilly is roughly two hours from Kochi's tech corridor, making it an easy weekend add-on if you are visiting family in Ernakulam.

## Dudhsagar Falls, Goa

At 310 metres, Dudhsagar is one of India's tallest waterfalls, and during peak monsoon it earns its name — "Sea of Milk" — as white water cascades down a four-tiered rock face into a deep green pool. The classic approach is by jeep through the Bhagwan Mahaveer Sanctuary from Castle Rock or Collem. The railway bridge arching over the falls is one of the most photographed spots in the Western Ghats.

**NRI tip:** Combine Dudhsagar with a Goa beach week. The falls are at their peak from July through September, which is also when Goa's beaches are empty and hotels are cheapest.

## Nohkalikai Falls, Meghalaya

Meghalaya's crown jewel is India's tallest plunge waterfall at 340 metres, dropping into a startlingly turquoise pool in Cherrapunji. The viewpoint is a short walk from the road, but the real experience is the hike down to the pool's edge — steep, muddy, and absolutely worth it. Meghalaya receives its heaviest rainfall in June and July, and Nohkalikai is at its most thunderous during these weeks.

**NRI tip:** Pair this with the living root bridges of Nongriat, a two-hour trek from Cherrapunji. The double-decker root bridge is a UNESCO tentative list site and one of the most extraordinary things you can see in India.

## Courtallam Falls, Tamil Nadu

Known as the "Spa of South India," Courtallam's falls flow through dense forests full of medicinal herbs, and locals believe the water has ayurvedic properties. The main falls and the five-falls complex draw huge crowds during monsoon — mostly domestic pilgrims — but the old falls and the tiger falls nearby are quieter. The surrounding market sells herbal oils and handloom textiles.

**NRI tip:** Courtallam is under three hours from Madurai airport. If you are attending a family wedding in Tamil Nadu during monsoon season, this is the side trip.

## Unchalli Falls, Karnataka

Also called Lushington Falls, this 116-metre cascade in Uttara Kannada district is one of Karnataka's best-kept secrets. The trek to the falls passes through dense forest and involves a moderately challenging descent. New tourist infrastructure — including improved trail markers and a parking area — has made access easier without attracting mass tourism. During monsoon, the falls produce a mist cloud visible from kilometres away.

**NRI tip:** Unchalli is roughly four hours from Hubli airport. Combine it with Jog Falls (India's second-highest plunge waterfall, 253 metres) for a two-day Western Ghats waterfall circuit.

## Sathodi Falls, Karnataka

Tucked deep in the Western Ghats near the Kodasalli dam, Sathodi is a wide, curtain-style waterfall surrounded by dense forest. The approach requires a jungle trek that filters out casual visitors, so you are likely to have the falls largely to yourself even during peak season. The pool at the base is swimmable when water levels are moderate.

**NRI tip:** Sathodi is best combined with an Agumbe or Shimoga itinerary. The roads are rough during heavy rain, so a high-clearance vehicle is essential.

## The Practical Case for Monsoon Travel

Round-trip flights from the US to India are currently 30-40% cheaper for July-August travel compared to the December holiday peak. Hotel rates at monsoon destinations drop even further. And according to Agoda's latest search data, Indian travelers are already surging toward nature destinations — Leh searches are up 143%, Kasol up sharply, and hill station bookings are climbing fast.

For NRIs, the monsoon is India's most underrated season. The crowds thin, the landscape transforms, and the waterfalls deliver the kind of raw spectacle that no five-star resort can manufacture.

*Sources: The New Indian Express, Travel And Tour World, Agoda*"""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "IndiGo Is Building a Widebody Business Class — and It Could Reshape How NRIs Fly to India",
        "subheadline": "India's largest airline just teased a dedicated premium cabin for its incoming Airbus A350 fleet. With 60 widebodies on order and long-haul routes to Europe already live, a budget-price business class on NRI corridors is no longer a fantasy.",
        "slug": make_slug("indigo-a350-business-class-nri-long-haul"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "IndiGo's entry into true widebody business class could break the Air India/Emirates duopoly on premium NRI routes and force fares down on corridors like DEL-LHR, BOM-AMS, and eventually DEL-JFK.",
        "tags": ["travel", "airlines", "indigo", "business-class", "aviation"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Aviation A2Z", "url": "https://www.aviationa2z.com/index.php/2026/06/09/indigo-teases-new-business-class-for-airbus-a350-fleet/"},
            {"name": "Storyboard18", "url": "https://www.storyboard18.com/brand-marketing/indigo-charts-global-expansion-push-targets-200-million-passengers-and-550-aircraft-fleet-by-2030-63208.htm"},
            {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/corporate/indigo-bets-big-on-international-growth-targets-200-mn-passengers-by-fy30"},
            {"name": "Airbus", "url": "https://www.airbus.com/en/newsroom/press-releases/2025-10-indigo-orders-30-more-a350-900s"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4d/IndiGo_Airbus_A320neo_F-WWDG_%28to_VT-ITI%29_%2828915135713%29.jpg/3840px-IndiGo_Airbus_A320neo_F-WWDG_%28to_VT-ITI%29_%2828915135713%29.jpg",
        "image_caption": "An IndiGo Airbus A320neo in the airline's signature blue livery",
        "image_attribution": "Wikimedia Commons",
        "body": """IndiGo, the airline that built India's largest domestic network on a relentless commitment to no-frills efficiency, just dropped a slide in its latest investor presentation that should make NRI frequent flyers sit up. A dedicated business-class product is "under development" for its incoming Airbus A350-900 fleet, with the first aircraft due in 2027.

The details are deliberately thin — no seat type, no cabin layout, no configuration. But the signal is unmistakable: India's dominant carrier is done being a domestic shuttle service. It wants the premium long-haul passenger, and it is building the product to get them.

## From IndiGoStretch to True Business Class

IndiGo already operates a premium product called IndiGoStretch on 53 of its A321neo narrowbodies. It offers 38 inches of pitch, five inches of recline, complimentary vegetarian meals, and priority boarding. Respectable for a two-hour Delhi-Mumbai hop, but a far cry from what a business traveler expects on a 10-hour flight to London.

The airline plans to nearly double the IndiGoStretch fleet to over 100 A321neos, pushing daily premium seat count from 2,800 currently to over 4,300 by March 2027. But the A350 product will be something different entirely — a widebody cabin designed for routes where IndiGo will compete head-to-head with Air India's newly refurbished Airbus A350s, Emirates' flagship service, and the Gulf carriers that currently own the NRI corridor.

IndiGo has ordered 60 A350-900s — 30 confirmed in 2024, another 30 firmed up in October 2025. That is not a toe-in-the-water experiment. That is a fleet large enough to serve a dozen long-haul routes simultaneously.

## Why NRIs Should Care

For years, the NRI travel experience has been shaped by a small oligopoly. Air India and its Vistara merger offered the only nonstop options on most India-US and India-UK routes. Emirates, Qatar Airways, and Etihad controlled the one-stop market through their Gulf hubs. Competition existed, but it was competition among full-service carriers charging full-service prices.

IndiGo's entry changes the calculus. The airline's cost per available seat kilometre (CASK) is among the lowest of any major carrier globally. If it can deliver even a competent lie-flat business class at fares 20-30% below Air India or the Gulf carriers, the price disruption on corridors like Delhi-London, Mumbai-Amsterdam, and eventually Delhi-New York will be significant.

The airline has already launched long-haul services to Manchester and Amsterdam using damp-leased Boeing 787-9s operated with Norse Atlantic Airways. It is preparing routes to London, Copenhagen, and Athens. The A321XLR — a longer-range narrowbody arriving in FY27, with nine deliveries expected — will push into Bali, Seoul, and Istanbul.

## The Fleet Is Not the Question — The Product Is

IndiGo's track record on product has been mixed. IndiGoStretch is functional but basic — no in-flight entertainment, no footrest, only cold vegetarian meals (the airline still does not have ovens on its narrowbodies). Aviation analysts have noted that it is "strictly a budget business product, not true business class."

The A350 is a different aircraft in every sense. It is designed for 12-15 hour missions, typically carries an onboard galley capable of hot meal service, and comes standard with entertainment systems. The question is not whether IndiGo can install a business-class cabin — it is whether the airline's legendarily cost-conscious DNA will permit the kind of soft product (service, catering, lounge access) that premium passengers actually pay for.

For NRIs who currently route through Dubai or Doha because Air India's hard product does not justify its pricing, IndiGo's entry creates a compelling new option — if the execution is right. A lie-flat seat with decent catering on a nonstop Delhi-London at ₹80,000-₹1,00,000 round-trip would be a category-defining proposition.

## The Loyalty Play

Quietly, IndiGo has also been building the other half of the premium puzzle. Its BluChip loyalty programme has crossed 11 million members since launch, making it one of the fastest-growing airline loyalty programmes in Asia. The programme is open to all bookings (not just co-branded credit card holders), and while tier benefits and elite status are still evolving, the foundation for a frequent-flyer ecosystem is in place.

For NRIs who fly to India two to four times a year, the ability to earn and burn points on an airline that actually serves the routes they fly — and does so at lower fares — is the missing piece. Air India's revamped Flying Returns programme is playing catch-up after years of neglect. IndiGo, starting from scratch, has the advantage of designing a modern programme without legacy baggage.

## The Timeline

The first A350s arrive in 2027. Long-haul European routes are already live via wet-lease. The premium narrowbody fleet is scaling fast. The business-class product reveal could come as early as late 2026 or early 2027.

For NRIs, the practical advice is simple: watch this space. IndiGo may not be your airline today, but it is building to be your airline by 2028.

*Sources: Aviation A2Z, Storyboard18, Outlook Business, Airbus*"""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

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
        "headline": "Delhi-NCR Just Got a Third Airport at Jewar — and It's the One Your Relatives Will Actually Fly You Into",
        "subheadline": "Noida International Airport opened to commercial flights on June 15 with IndiGo as launch carrier; international links to Dubai, Singapore and Zurich are slated for the September-October window.",
        "slug": make_slug("noida-international-airport-jewar-dxn-ncr-third-airport-nri"),
        "category": "travel",
        "vertical": "infrastructure",
        "diaspora_angle": "For the millions of NRIs whose families sit in western UP, Agra and the eastern NCR fringe, Jewar finally puts a modern airport on their side of the megacity — cutting the brutal cross-Delhi drive to IGI that has long defined the trip home.",
        "tags": ["travel", "airports", "noida", "delhi-ncr", "indigo", "infrastructure"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Aviation Week", "url": "https://aviationweek.com/air-transport/airports-networks/indigo-set-first-commercial-flights-noida-airport"},
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/economy/logistics/noida-international-airport-to-start-commercial-flights-from-june-15/article70928276.ece/amp/"},
            {"name": "Outlook Traveller", "url": "https://www.outlooktraveller.com/News/noida-airport-flight-network-current-routes-and-upcoming-international-destinations"}
        ]),
        "score_total": 82,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/392265/pexels-photo-392265.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A bright, glass-walled airport terminal of the kind India's new greenfield hubs are built around",
        "image_attribution": "Pexels",
        "body": """After more than a decade of broken deadlines and political wrangling, the Delhi capital region finally has its third airport. Noida International Airport — carrying the IATA code DXN and built at Jewar in Uttar Pradesh, roughly 70 kilometres southeast of central Delhi — began commercial flights on June 15, with IndiGo operating the inaugural service. Akasa Air and Air India Express are following close behind.

Inaugurated by Prime Minister Narendra Modi in March, the greenfield project opens with a single runway and one terminal rated for 12 million passengers a year. The long game is far bigger: four phases of expansion eventually pushing capacity past 70 million, which would make Jewar one of the largest airports in the country. It is operated by Yamuna International Airport Private Limited, a subsidiary of Zurich Airport International, and the operator has been quick to brand it India's first net-zero greenfield hub.

## What's flying, and when

For now, DXN is a domestic story. IndiGo is rolling out service to more than 16 destinations, leading with Amritsar and Hyderabad from day one and adding Bengaluru and Jammu on June 16. A larger phase from July 1 is expected to push the airport to around 40 daily flights, adding Chandigarh, Dehradun, Dharamshala, Jaipur, Bhopal and a clutch of tier-two cities including Jodhpur, Bareilly and Kishangarh.

The international piece — the part the diaspora actually cares about — is penciled in for the end of the third quarter, with September and October the working window. The first overseas routes lined up are Zurich, Dubai and Singapore. Zurich is no accident: the airport's own operator runs Zurich's airport, and that link is meant to anchor a European long-haul build-out over time.

## The catch: it costs more to fly out of Jewar

Here is the awkward part nobody leads with. Flying out of Noida is, at launch, more expensive than flying out of Delhi's Indira Gandhi International (IGI). The airport's user development fees and charges have been set higher than IGI's, which means the headline fare on a Jewar departure can run above the equivalent IGI ticket on the same route. For a price-sensitive market, that gap matters, and it will shape how quickly airlines and passengers migrate east.

## Why this lands for NRIs

For decades, the trip home for families in Agra, Mathura, Aligarh, Greater Noida and the eastern arc of the National Capital Region has carried a hidden tax: the drive across or around Delhi to reach IGI, a slog that can swallow three to four hours in bad traffic and turns a tight connection into a missed one. Jewar rewrites that geometry. A returning NRI landing at DXN — once the long-haul routes open — would skip the cross-city haul entirely for relatives on the Yamuna Expressway corridor.

There is a second, quieter benefit. IGI is among the most congested airports in the country, and a third NCR field (alongside IGI and the smaller Hindon airport) spreads that load. More gates and more runway capacity across the region should, over time, mean fewer holding patterns, fewer tarmac delays and a little more slack in a system that the diaspora's summer and Diwali surges routinely push to the brink.

The honest near-term advice is patience. Until the Dubai, Singapore and Zurich routes actually start in the autumn, an NRI flying in from the US, the UK or the Gulf still arrives at IGI and, if their family is on the eastern side, still faces the drive. DXN's domestic network does open one useful option now: fly the long haul into IGI, then connect onward — or have family connect — through Jewar to a tier-two city without crossing Delhi.

## What's next

Watch the autumn route announcements. The Gulf corridor is the single biggest diaspora artery into India, and a Jewar-Dubai or Jewar-Abu Dhabi nonstop would be the moment DXN stops being a domestic convenience and starts being a genuine gateway home. Zurich's European link and a Singapore hop would round out the first international wave. If the fee gap with IGI narrows as volumes build — and operators usually blink on pricing once competition arrives — Jewar could become the default airport for a large slice of the NCR diaspora within a couple of years.
"""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The US Will Now Sell You a Visa Interview Within 10 Days — for $750 on Top of the Fee",
        "subheadline": "A State Department pilot running July through December lets B1/B2 applicants buy an expedited appointment. It buys speed, not approval, and the list of participating posts in India hasn't been confirmed.",
        "slug": make_slug("us-expedited-visa-interview-750-fee-pilot-b1b2-india-nri"),
        "category": "travel",
        "vertical": "immigration",
        "diaspora_angle": "Indians face some of the longest US visa interview backlogs in the world, so the chance to pay for a guaranteed slot within 10 business days speaks directly to NRI families racing to bring parents over for a birth, a wedding or a medical emergency.",
        "tags": ["travel", "visa", "us-visa", "immigration", "b1-b2"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Outlook Traveller", "url": "https://www.outlooktraveller.com/News/need-a-us-visa-quickly-a-new-premium-appointment-service-is-coming-but-at-a-cost"},
            {"name": "U.S. Department of State (travel.state.gov)", "url": "https://travel.state.gov/content/travel/en/us-visas.html"}
        ]),
        "score_total": 79,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/33500646/pexels-photo-33500646.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A US Embassy sign on a city street, where visa applicants schedule their interviews",
        "image_attribution": "Pexels",
        "body": """The United States is about to put a price on jumping the visa interview queue. Under a pilot announced by the State Department, eligible applicants for B1/B2 visitor visas will be able to pay an extra fee to secure an interview appointment within 10 business days. The program runs from July 1 to December 31, 2026.

The cost is steep. The expedited service is priced at USD 750, paid on top of the standard USD 185 visa application fee — nearly five times the base charge. For that, an applicant gets one thing and one thing only: a faster slot in front of a consular officer.

## What the money does, and doesn't, buy

Read the fine print carefully, because the distinction matters. The $750 buys an earlier interview. It does not buy a visa, and it does not shorten anything that happens after the interview. Background checks, administrative processing (the dreaded "221(g)" holds), and the final adjudication all proceed on the same timelines as before. An applicant who pays for speed and then gets pulled into administrative review can still wait weeks or months for a decision.

In other words, this is a tool for one specific problem — the wait to be seen — and not a shortcut through the system. For a market where ordinary B1/B2 interview wait times have at points stretched into many months, that single problem is often the binding one. But anyone treating the fee as a guarantee of travel is misreading it.

## The India question

Here is the catch for the diaspora: the State Department has not yet published which embassies and consulates will take part, and India is not confirmed. Given that India is one of the highest-demand and longest-wait visa markets on the planet, it would be a natural candidate. But until the participating-post list is out, NRIs cannot assume their parents in Delhi, Mumbai, Chennai, Hyderabad or Kolkata will be able to use it.

That uncertainty is the story for now. If India is included, the five US consular posts there — plus the embassy in New Delhi — would suddenly offer a paid fast lane that could reshape how families plan urgent visits. If it is not, the pilot is academic for most of this audience.

## Why this hits home for NRIs

The US visa interview backlog is not an abstraction for Indian Americans — it is the thing that decides whether grandparents make it for a grandchild's birth, whether parents attend a wedding, whether a sibling can come for surgery. When a slot is six months out and the event is in eight weeks, the math is brutal. A guaranteed appointment within 10 business days, even at $750, would be an easy yes for a family facing a fixed date.

There is a fairness wrinkle worth naming. A premium fast lane, by design, advantages those who can absorb a four-figure surcharge. For a working-class applicant the $750 is prohibitive; for a tech professional flying parents over, it is a rounding error against the cost of the trip. The pilot effectively introduces tiered access to a government service, and the diaspora — which spans both ends of that income spread — will feel the split.

## What to do now

If you have a parent or relative with a pending or upcoming B1/B2 application and a hard deadline this autumn, watch for the participating-post announcement before July 1. Have the standard application and DS-160 ready so that, if the fast lane opens in India, you can act on day one rather than scrambling. And budget honestly: the $750 secures the interview, not the visa, so build in a contingency for administrative processing if the officer flags the case.

For everyone else, the old playbook still applies — apply early, watch for appointment slots opening as the system rebalances, and treat the expedited fee as an emergency lever, not a default.
"""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India Just Opened Nine New Airports to e-Visa Arrivals — and Added 11 Countries to the List",
        "subheadline": "The Ministry of Home Affairs has rebranded its e-Tourist Visa as a broader 'e-Visa' program, widening eligibility and adding ports of arrival from Calicut to Coimbatore that NRIs' visiting friends now route through.",
        "slug": make_slug("india-evisa-new-ports-arrival-countries-calicut-coimbatore-nri"),
        "category": "travel",
        "vertical": "immigration",
        "diaspora_angle": "For NRIs whose foreign-passport-holding spouses, friends and in-laws fly into second-tier Indian cities, the new arrival ports mean they no longer have to enter through a metro gateway just to satisfy the e-Visa rulebook.",
        "tags": ["travel", "visa", "e-visa", "india-tourism", "immigration"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Fragomen", "url": "https://www.fragomen.com/insights/additional-countries-and-ports-of-arrival-added-to-e-visa-program.html"},
            {"name": "Ministry of Tourism, Government of India", "url": "https://tourism.gov.in/news-and-updates/e-tourist-visa-facility-extended-166-more-countries"},
            {"name": "Fragomen — E-Visa Program to be Expanded", "url": "https://www.fragomen.com/insights/e-visa-program-to-be-expanded.html"}
        ]),
        "score_total": 72,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/4922356/pexels-photo-4922356.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "An open passport showing travel stamps, the document at the centre of India's e-Visa overhaul",
        "image_attribution": "Pexels",
        "body": """India has quietly broadened one of the most useful tools its diaspora's foreign friends and family rely on. The Ministry of Home Affairs has folded its e-Tourist Visa into a wider, rebranded 'e-Visa' program, adding new categories, opening eligibility to 11 more countries, and — most practically — designating nine additional airports and seaports where e-Visa holders can land.

## The new arrival ports

Until now, e-Visa holders could enter India only through a fixed set of major gateways. The latest expansion adds Bagdogra, Calicut, Chandigarh, Coimbatore, Guwahati, Nagpur and Pune airports, plus the seaports at Kochi, Goa and Mangalore. (Mangalore gets both airport and seaport designation.) Travelers on the e-Visa must still enter through an approved port — but they can exit from any authorized immigration check post.

That list reads like a map of the diaspora's home districts. Calicut and Kochi anchor Kerala, the source state for a huge share of Gulf and Western NRIs. Coimbatore serves the Kongu belt of Tamil Nadu. Guwahati opens the Northeast. Chandigarh covers Punjab and the surrounding region. For families whose roots are in these places, a visiting foreign-passport-holder no longer has to fly into Delhi, Mumbai, Chennai or Bengaluru and connect onward simply to comply with the e-Visa's port rules — they can land where the family actually lives.

## Who can now apply

The eligibility net has widened to 11 additional countries: Angola, Azerbaijan, Burundi, Cameroon, Cyprus, Italy, Mali, Niger, Rwanda, Sierra Leone and Uzbekistan. The inclusion of Italy is notable — it brings a major Western European market with its own sizable Indian community into the streamlined online process, and it follows India's broader push, under the "Visit India" tourism drive, to keep adding nationalities to the program.

The e-Visa covers the usual band of purposes: sightseeing, visiting friends and relatives, short medical visits, and short-term yoga programs. On the business side, e-Visa holders can attend meetings, trade fairs and exhibitions, recruit, and lecture under the Global Initiative for Academic Networks. The government is also building out new subcategories — an e-Conference Visa for those attending government-sponsored events and an e-Medical Attendant Visa for people accompanying patients on medical-visa trips — though the exact durations and requirements for those have not yet been published.

## Why this matters to NRIs

The e-Visa is, in practice, the diaspora's family-reunion document. It is what an NRI's American spouse, a German son-in-law or an Italian friend uses to come along on the trip home without grinding through an embassy appointment. The application is fully online: a form, a passport scan, a photo, payment by card, and an electronic authorization back — typically within 72 hours.

By adding second-tier arrival ports, India has removed a small but real friction. Consider a Bay Area family from Kerala: previously, a non-Indian-passport-holding partner on an e-Visa might have had to route through a metro gateway to enter legally before continuing to Kochi. Now they can fly straight into Kochi or Calicut. It shaves a connection, a few hours, and a layer of planning off the trip — exactly the kind of detail that makes the difference between a relative coming along and staying home.

## What to watch

The published rollout still has loose ends. The full list of nationalities eligible under the further expansion has not been released, and the rules for the new e-Conference and e-Medical Attendant categories are pending. NRIs planning to bring foreign-passport relatives this year should confirm three things before booking: that the traveler's nationality is on the current eligible list, that their intended arrival airport is among the approved e-Visa ports, and that their passport carries at least six months' validity, since no physical sticker is issued. Get those right and the trip home just got a little shorter for the whole family.
"""
    }
]

for art in articles:
    wc = len(art["body"].split())
    print(f"  [{art['slug']}] ~{wc} words")

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

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

def validate_image(url):
    """Check that image URL returns HTTP 200 with image content type and >5KB."""
    try:
        r = requests.head(url, timeout=10, allow_redirects=True)
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            print(f"  ✓ Image validated: {url[:80]}... ({cl} bytes)")
            return True
        else:
            print(f"  ⚠ Image validation failed: status={r.status_code}, type={ct}, size={cl}")
            return False
    except Exception as e:
        print(f"  ⚠ Image validation error: {e}")
        return False

# ─── Article 1: DHS Sanctuary City Airport Threat ───

art1_body = """The federal government's threat to pull Customs and Border Protection officers from airports in "sanctuary cities" has become the most consequential travel story for Indian Americans this summer — and most haven't heard about it yet.

Department of Homeland Security Secretary Markwayne Mullin announced in late May that the administration was drawing up plans to halt processing of international travelers and cargo at airports in cities that refuse to cooperate with federal immigration enforcement. The airports on the potential chopping block read like an NRI frequent-flyer's route map: Newark, JFK, LAX, San Francisco, Boston, Chicago O'Hare, and Seattle-Tacoma.

## The Direct Routes That Could Vanish Overnight

Consider what a CBP withdrawal would mean in practice. Newark handles Air India's daily Mumbai nonstop and United's Delhi service. JFK processes Air India flights to Delhi and Mumbai. SFO runs the flagship Air India Delhi nonstop plus United's Delhi service. LAX connects to Hyderabad and Bengaluru via one-stop carriers. Chicago O'Hare handles Air India's Delhi route.

If CBP officers are reassigned from even one of these hubs, every inbound international flight to that airport would be unable to clear passengers into the United States. Airlines would be forced to cancel or divert. For the roughly 1.5 million NRIs who fly to India and back each year — many of them through exactly these airports — the disruption would be immediate and severe.

## $70 Billion at Stake

The U.S. Travel Association has put a number on it: shutting down international processing at the 18 airports serving sanctuary cities would cost the economy more than $70 billion and affect 68 million international passengers annually. Newark alone accounts for $8 billion in annual international visitor spending and nearly 50,000 tourism-related jobs.

Six major airlines — Delta, United, American, Southwest, JetBlue, and Alaska — have issued a joint warning that the move could "grind international flights to a halt." The FAA and Department of Transportation have publicly opposed the plan. Transportation Secretary Sean Duffy has reportedly cautioned that suspending air travel over political disagreements would trigger enormous economic consequences.

## The World Cup Complicates Everything

The timing could not be worse. The 2026 FIFA World Cup kicks off on June 11 across the United States, Canada, and Mexico. The final is scheduled for July 19 at MetLife Stadium in East Rutherford, New Jersey — roughly 12 miles from Newark Liberty International Airport. Millions of international visitors are expected, and India's cricket-loving diaspora has shown strong crossover interest in the tournament.

A Reuters report on June 1 noted that DHS Secretary Mullin appeared to walk back the Newark-specific threat, saying he sees "no need" to stop processing there. But the broader policy toward other sanctuary cities remains unresolved, and California Governor Gavin Newsom has been scrambling to prepare contingency plans for LAX and SFO.

## What NRIs Should Do Now

The threat has not been implemented, and it may never be. But the uncertainty alone warrants preparation. NRIs with summer India trips booked through SFO, JFK, or Newark should monitor their airline's advisories closely. Travel insurance that covers policy-driven cancellations — not just weather or mechanical issues — is worth the investment this season. And anyone booking new flights should consider routing flexibility: Dallas-Fort Worth, Houston, and Washington Dulles are not on any sanctuary city list and offer India connections via Gulf carriers.

The sanctuary city standoff is a domestic political fight. But for the Indian American community, whose travel patterns run overwhelmingly through the airports in the crosshairs, it is a practical crisis waiting to happen."""

art2_body = """The World Health Organization declared a Public Health Emergency of International Concern on May 17 after an Ebola outbreak — linked to the Bundibugyo strain — spread for weeks across eastern Congo and into Uganda before wider detection. Two weeks later, the ripple effects have reached every major international airport in the United States, and NRIs traveling this summer need to understand what has changed.

## Four US Airports Now Funnel All Affected Travelers

The Centers for Disease Control and Prevention, working with the Department of Homeland Security, has designated four airports for enhanced Ebola entry screening: Washington Dulles International, John F. Kennedy International, Hartsfield-Jackson Atlanta International, and George Bush Intercontinental in Houston. All travelers who have visited the Democratic Republic of Congo, South Sudan, or Uganda within the past 21 days are now rerouted to one of these four airports for mandatory processing.

Upon arrival, passengers are escorted to designated isolation and screening areas. The process includes a comprehensive travel-history questionnaire, mandatory temperature checks, and visual observation for early symptoms. The CDC has deployed dedicated teams at each airport. For those cleared, a 21-day monitoring protocol follows, with daily symptom check-ins.

## Entry Bans Extend Beyond Foreign Nationals

The restrictions go further than screening. The United States has banned entry for non-citizens who have recently visited the three affected countries. Critically, this ban has been extended to green card holders — permanent residents who have traveled to the outbreak zones within the past 21 days. For the estimated 80,000 Indian-origin permanent residents with business, family, or humanitarian ties to East and Central Africa, this is a material change.

Canada has implemented its own 90-day ban effective May 27, with a mandatory 21-day quarantine for citizens and permanent residents arriving from high-risk countries. Mexico has reinforced airport screening and required 21-day quarantine for DRC arrivals. The containment net is tightening across all three World Cup host nations simultaneously.

## Air India and IndiGo Issue Travel SOPs

India's own aviation regulators have acted. The Directorate General of Civil Aviation has issued broader advisory notices discouraging non-essential travel to outbreak zones. Both Air India and IndiGo have communicated standard operating procedures to passengers, aligning with government screening requirements. Emirates, which connects thousands of India-origin passengers through Dubai, has issued its own travel advisory urging passengers to review updated health protocols before departure.

For NRIs transiting through Gulf hubs — Dubai, Abu Dhabi, Doha — to reach African destinations, the layered screening requirements mean that connecting flights could involve additional documentation checks and potential delays at both transit and arrival points.

## The Risk Is Low, but the Disruption Is Real

Public health experts stress that Ebola spreads through direct contact with infected bodily fluids, not through the air. The risk to the general American population remains low. But the operational disruption is genuine: rerouted flights, longer processing times at the four designated airports, and the practical inconvenience of daily monitoring check-ins for 21 days.

For NRIs planning summer travel, the practical advice is straightforward. Avoid non-essential travel to the DRC, Uganda, and South Sudan. If you hold a green card and have upcoming travel to East Africa, consult with an immigration attorney about re-entry implications before departing. Check whether your airline has adjusted transit procedures through Gulf or African hubs. And if your US entry airport is one of the four screening hubs — particularly JFK, which already handles heavy India-bound traffic — budget extra time for arrival processing.

The last global Ebola scare, in 2014, taught the travel industry that early, aggressive screening prevents the kind of panic-driven shutdown that hurts everyone. This time, the infrastructure is better. But the inconvenience is real, and NRIs should plan accordingly."""

art3_body = """Turkey was the hot destination for Indian travelers. Cappadocia's balloon rides filled Instagram feeds. Istanbul's Grand Bazaar was a staple of every group tour itinerary. In 2024, 2.87 lakh Indians visited Turkey, making it one of the fastest-growing outbound destinations from India.

That is over now. Following Turkey's diplomatic alignment with Pakistan during Operation Sindoor — Ankara publicly criticized India's military response to the Pahalgam terror attack — Indian travel agencies have effectively shut down Turkey as a destination. The numbers tell the story: an 80 percent drop in bookings, a 250 percent surge in cancellations on MakeMyTrip, and every major platform from EaseMyTrip to Cox & Kings pulling Turkey off their shelves.

## The Boycott Goes Corporate

This is not just social media outrage translating into a temporary dip. India's largest travel platforms have made institutional decisions. EaseMyTrip suspended all bookings to Turkey and Azerbaijan — which also backed Pakistan — and offered free cancellations. Co-founder Nishant Pitti framed the move in economic terms: "Every rupee spent abroad is a vote. Spend it where our values are respected."

Cox & Kings removed Turkey, Azerbaijan, and Uzbekistan from its offerings. Travomint stopped accepting travel packages to both countries. Ixigo and Pickyourtrail suspended bookings entirely. The message from India's travel industry is unified and unambiguous.

For NRIs, the impact is more personal. Many Indian Americans had been planning summer trips that combined Istanbul with family visits in India — the geography made it a natural stopover on routes through the Gulf. Turkish Airlines' extensive hub at Istanbul had become a preferred connection point for price-conscious NRIs flying to smaller Indian cities.

## The Visa Money Is Gone Too

The collateral damage extends beyond flight bookings. Turkey's e-visa for Indian passport holders costs approximately $50 and is non-refundable once issued. Travelers who had already obtained visas for cancelled trips are unlikely to recover that money. For group tours — which can involve 15 to 20 participants with visa fees, hotel deposits, and internal flight bookings — the financial losses add up fast.

Archana Gupta, founder of Pack n Fly Travellers Club, had to cancel a 12-person women's trip to Turkey after more than half her group pulled out. "You cannot do a trip for just four people," she told Forbes India. "We all had to put up with financial losses."

Azerbaijan, which received 2.43 lakh Indian visitors last year and where tourism contributes 7.6 percent of GDP, has been caught in the same backlash. The country's positioning as a Caucasus alternative to European trips has been severely damaged by its alignment with Pakistan in the conflict.

## Where NRIs Are Going Instead

Travel agents report that displaced demand is flowing to Southeast Asia — Vietnam, Thailand (despite its recent visa-free cut from 60 to 30 days), and Bali remain strong — and to European destinations accessible with Schengen visas. Greece, Portugal, and Croatia are absorbing some of the Istanbul-bound leisure traffic. For NRIs seeking cultural-historical richness comparable to Cappadocia and the Bosphorus, Jordan and Egypt are emerging as alternatives, with the added advantage of proximity to Gulf transit hubs.

Domestically within India, the boycott has been a tailwind for the hospitality sector. Hill stations and spiritual destinations have reported a 69 percent and 41 percent year-over-year increase respectively, according to Radisson data. The message from Indian travelers — both resident and diaspora — is clear: geopolitics now shapes vacation planning, and Turkey's tourism industry will feel it long after the diplomatic dust settles."""


articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "The Airports NRIs Fly Through Are at the Center of a Federal Standoff — Here's What Could Go Wrong",
        "subheadline": "DHS has threatened to pull customs officers from sanctuary city airports including SFO, JFK, and Newark — the exact hubs that handle nearly every nonstop to India.",
        "slug": make_slug("dhs-sanctuary-city-airports-nri-india-flights"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "SFO, JFK, EWR, LAX, ORD — the airports facing CBP withdrawal threats are the same ones that handle virtually every nonstop flight between the US and India. A disruption at any of them would directly strand NRI travelers.",
        "tags": ["travel", "airports", "dhs", "nri", "immigration", "world-cup"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/world/us/us-homeland-security-chief-sees-no-need-stop-international-flight-processing-2026-06-01/"},
            {"name": "Travel and Tour World", "url": "https://www.travelandtourworld.com/news/article/b1wzez5js5fi/"},
            {"name": "U.S. Travel Association", "url": "https://www.ustravel.org/"}
        ]),
        "score_total": 88,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/37847918/pexels-photo-37847918.jpeg",
        "body": art1_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Ebola Screening Hits Four US Airports — What NRIs Need to Know Before Flying This Summer",
        "subheadline": "The CDC has funneled all travelers from three African nations to JFK, Dulles, Atlanta, and Houston for mandatory health checks. Green card holders are included in the entry ban.",
        "slug": make_slug("ebola-screening-us-airports-nri-travel-cdc"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "NRIs with business, family, or humanitarian ties to East and Central Africa face entry bans and 21-day monitoring. Air India and IndiGo have issued SOPs, and Gulf transit routes now carry additional screening layers.",
        "tags": ["travel", "ebola", "airports", "cdc", "health", "nri"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "CDC", "url": "https://www.cdc.gov/ebola/"},
            {"name": "Reuters", "url": "https://www.reuters.com/"},
            {"name": "Travel and Tour World", "url": "https://www.travelandtourworld.com/"},
            {"name": "Devdiscourse", "url": "https://www.devdiscourse.com/article/health/3399929-global-travel-restrictions-intensify-amid-drc-ebola-outbreak"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b9/JFK_Aerial_Nov_14_2018.jpg/3840px-JFK_Aerial_Nov_14_2018.jpg",
        "body": art2_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Turkey Was the Hot Indian Vacation — Then Geopolitics Killed It",
        "subheadline": "An 80 percent booking collapse, platform-wide suspensions, and a unified corporate boycott have erased Turkey from India's travel map. Here's where NRIs are going instead.",
        "slug": make_slug("india-boycott-turkey-tourism-nri-alternatives"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "Many NRIs used Istanbul as a stopover on India routes via Turkish Airlines. The boycott has disrupted group tours, destination weddings, and transit routing for price-conscious diaspora travelers.",
        "tags": ["travel", "turkey", "boycott", "geopolitics", "nri", "alternatives"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Forbes India", "url": "https://www.forbesindia.com/article/news/how-turkey-and-azerbaijan-fell-off-indian-tourists-travel-radar/96937/1"},
            {"name": "Storyboard18", "url": "https://www.storyboard18.com/brand-marketing/indians-boycott-travel-to-turkey-azerbaijan-amid-indo-pak-tensions-cancellations-surge-250-on-makemytrip-59561.htm"},
            {"name": "The Indian Eye", "url": "https://theindianeye.com/boycott-turkey-movement-gains-traction-in-india/"}
        ]),
        "score_total": 78,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/28764621/pexels-photo-28764621.jpeg",
        "body": art3_body
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

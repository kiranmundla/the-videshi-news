#!/usr/bin/env python3
"""Travel writer — July 1, 2026 03:00 PT run.
Two articles: Mumbai floating hotel, World Cup knockout round NRI guide.
"""
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


# ─────────────────────────────────────────────
# Article 1: Mumbai Floating Hotel
# ─────────────────────────────────────────────

art1_body = """Mumbai is not short of audacious proposals, but a 520-room floating hotel anchored two nautical miles off Nariman Point belongs in its own category. The Maharashtra Coastal Zone Management Authority (MCZMA) recommended Coastal Regulation Zone clearance for the project on June 16, advancing what could become India's first seven-star floating hotel — and one of the most unusual hospitality plays anywhere in Asia.

## What Is Actually Being Built

The floating hotel is the centrepiece of a larger marina complex proposed by Rashmi Developments off Cuffe Parade. Beyond the hotel itself, the project envisions a modern yacht club, a 1,530-seat theatre, multiple fine-dining restaurants, luxury lounges, serviced apartments, conference centres, art galleries and premium retail — all integrated into a waterfront precinct that would double as an inland water transport terminal.

Guests would arrive by speedboat, helicopter or seaplane. Plans also include infrastructure for future VTOL (vertical take-off and landing) aircraft, suggesting the developers are building for a decade-out transport reality, not just today's.

The on-land component includes an eight-storey structure — two basement levels, six above ground — spanning roughly 35,000 square metres of built-up area. Because it exceeds the 20,000-square-metre threshold, the project requires both Environmental Clearance from the State Environment Impact Assessment Authority and composite CRZ approvals before any construction begins.

## Why NRIs Should Pay Attention

For the Indian American diaspora, Mumbai's waterfront has always been equal parts nostalgia and frustration — the Queen's Necklace dazzles at night but delivers little in public amenity by day. This project, if realised, would change that equation substantially.

The marina's inland water transport terminal is designed to offer an alternative to Mumbai's famously gridlocked roads and overcrowded suburban rail. For NRI families landing at Chhatrapati Shivaji Maharaj International Airport and heading to South Mumbai — a journey that routinely takes ninety minutes or more by car — a sea transfer from a future helipad or seaplane dock could compress the trip to under twenty minutes.

The serviced apartments, offered in studio through three-bedroom configurations, address a gap that returning NRIs know well: finding quality short-stay accommodation in SoBo that does not involve paying ₹40,000 a night at the Taj or Oberoi. A marina-adjacent apartment with yacht club access offers something closer to Dubai Marina than anything Mumbai currently has.

## The Approval Gauntlet

Enthusiasm should be tempered by Mumbai's track record with waterfront megaprojects. The Nariman Point floatel concept has surfaced before — most recently when Ports Minister Nitesh Rane ordered the Maharashtra Maritime Board to prepare a detailed project report by September 2025. In 2018, a similar proposal was referred to a Bombay High Court committee and rejected on grounds that a jetty would create traffic problems on Marine Drive and damage the promenade's ambience.

The MCZMA recommendation is a necessary but not sufficient step. The proposal now heads to the Union Ministry of Environment, Forest and Climate Change for CRZ clearance. The reclamation component — construction within a CRZ-IV area — will face additional environmental scrutiny. History suggests a multi-year timeline, with no guarantee of final approval.

## The Bigger Picture

Mumbai's ambition is not happening in isolation. Navi Mumbai's international airport goes operational on July 15. The Atal Setu bridge has already cut travel time to Navi Mumbai. The Coastal Road is open. Taken together, these projects are reshaping how the city connects to its waterfront. A floating hotel and marina off Nariman Point would be the most dramatic expression yet of Mumbai's pivot toward the sea — and a signal that India's financial capital is serious about competing with Dubai, Singapore and Hong Kong as a waterfront destination.

For now, the floating hotel remains a proposal on paper. But it is a proposal that has cleared its first regulatory hurdle, and one that aligns with a city-wide infrastructure push that is finally, genuinely, happening.

*Sources: Outlook Traveller, Curly Tales, NDTV, Maharashtra Maritime Board*"""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Mumbai Wants to Anchor a Seven-Star Floating Hotel Off Nariman Point — Here's What NRIs Need to Know",
    "subheadline": "A 520-room floating hotel with speedboat and seaplane access just cleared its first regulatory hurdle. If it survives Mumbai's approval gauntlet, it could reshape how diaspora families experience South Mumbai.",
    "slug": make_slug("mumbai-floating-hotel-nariman-point-marina-nri"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "The proposed marina complex includes serviced apartments and sea-based transfers that could dramatically improve the SoBo arrival experience for returning NRIs, while competing with Dubai Marina for waterfront lifestyle appeal.",
    "tags": ["travel", "mumbai", "hotels", "luxury", "real-estate", "infrastructure"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Outlook Traveller", "url": "https://www.outlooktraveller.com/News/a-seven-star-floating-hotel-may-soon-transform-mumbais-waterfront"},
        {"name": "Curly Tales", "url": "https://curlytales.com/mumbai-first-7-star-floating-hotel/"},
        {"name": "Inshorts", "url": "https://inshorts.com/en/news/indias-first-7star-floating-hotel-could-be-built-in-mumbai-soon-report-1751178713903"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/7096209/pexels-photo-7096209.jpeg?auto=compress&cs=tinysrgb&w=1200",
    "image_caption": "Mumbai's skyline and waterfront as seen from the Arabian Sea",
    "image_attribution": "Pexels",
    "body": art1_body
}


# ─────────────────────────────────────────────
# Article 2: World Cup Knockout Round NRI Travel Guide
# ─────────────────────────────────────────────

art2_body = """The group stage is over. Forty-eight teams entered. Thirty-two remain. And starting today, the 2026 FIFA World Cup shifts into its knockout phase — a three-week sprint across sixteen American, Canadian and Mexican stadiums that will test the travel stamina of even the most seasoned NRI sports fan.

If you are among the estimated 6 million visitors in North America for the tournament, or if you are an Indian American thinking of catching a knockout match in your own city, here is the practical travel intelligence you need right now.

## The Knockout Map

The Round of 32 kicks off on July 1, with matches spread across venues including MetLife Stadium in New Jersey, Levi's Stadium in Santa Clara, AT&T Stadium in Dallas, and stadiums in Miami, Houston, Philadelphia, Seattle, Atlanta, Los Angeles and Mexico City. The semi-finals will be played on July 14 and 15, with the final at MetLife Stadium on July 19.

For NRIs on the West Coast, Levi's Stadium in Santa Clara — barely forty minutes from downtown San Francisco — hosts multiple knockout matches, including USA vs. Bosnia and Herzegovina today. On the East Coast, MetLife Stadium is the tournament's anchor venue, hosting matches through the final.

## Airfare Reality Check

Do not expect last-minute deals. Airfares between match cities have surged — domestic economy fares on key corridors like SFO–JFK, LAX–MIA and DFW–SEA are running 40-60% above their typical July levels, according to travel data from multiple booking platforms. International inbound fares are even steeper: round-trip economy from Delhi to New York is hovering around $1,100-$1,500 on United and Air India, well above the $800-$900 that was standard just two months ago.

Private jet demand has shattered records. Charter company Elevate Jet reported demand exceeding predictions by double digits, with more than 73,000 match-day private flights projected across the tournament, generating an estimated $274 million in additional charter revenue.

The practical move: book connecting cities in advance, consider secondary airports (Newark instead of JFK, Oakland instead of SFO, Fort Worth instead of Dallas Love Field), and build in schedule buffer. A tight connection on match day is a recipe for missing kickoff.

## The Three-Country Visa Trap

This is the detail that catches Indian passport holders off guard. The United States, Canada and Mexico are three sovereign nations with three separate immigration systems. Travelling between matches across borders requires separate documentation for each country.

**United States:** Your existing visa (B1/B2, H-1B, L-1, etc.) or Green Card covers you.

**Canada:** Indian passport holders need a visitor visa or an Electronic Travel Authorization (eTA). If you hold a valid US visa, you may be eligible for a Canadian visa exemption under certain conditions, but this depends on your specific status. Check before you book.

**Mexico:** Here is the good news. If you hold a valid multiple-entry visa or permanent residence from the United States, Canada, the UK, Japan, or any Schengen country, you can enter Mexico visa-free for up to 180 days. For the roughly 4.8 million Indian Americans in the US, most of whom hold valid US visas or Green Cards, Mexico matches are visa-free.

A word of caution: border processing times are expected to double during the tournament. Leave a minimum four-hour cushion on any itinerary involving a cross-border connection. Carry physical copies of your visa documents — immigration officers at land borders and secondary airports do not always have patience for phone screens.

## Where to Watch if You Cannot Attend

For NRIs who cannot get tickets or do not want to navigate match-day travel chaos, every match is broadcast on FOX (English) and Telemundo (Spanish) in the US, with streaming available on Peacock Premium and Fubo TV. Most major US cities have dedicated fan zones and public screenings — check your city's official FIFA Fan Fest page for locations.

Indian restaurants and cricket-turned-football bars across the diaspora belt — Edison, Fremont, Sugar Land, Devon Avenue — are running World Cup watch parties through the final. It is, perhaps, the first World Cup where Indian Americans are as likely to be watching in their own neighbourhoods as from a living room couch.

## The Bottom Line

The knockout round is the best phase of any World Cup — single elimination, no safety net, pure drama. For NRIs living in host cities, this is a once-in-a-generation chance to attend a World Cup match without crossing an ocean. For those willing to travel between cities, the logistics are manageable but demand advance planning.

Book now. Fly early. Carry your papers. And do not, under any circumstances, assume that a US visa gets you into Canada without checking first.

*Sources: FIFA, Travel And Tour World, Mansion Global, Trip.com, Travelocity*"""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "The World Cup Knockout Round Starts Today — an NRI Travel Survival Guide",
    "subheadline": "Thirty-two teams, sixteen stadiums, three countries, one Indian passport. Here is everything diaspora fans need to know about airfares, visas and cross-border logistics as the 2026 FIFA World Cup enters its decisive phase.",
    "slug": make_slug("world-cup-knockout-nri-travel-guide-visa-airfare"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "For 4.8 million Indian Americans living in World Cup host cities, this is a once-in-a-generation opportunity to attend a global tournament without leaving the continent — but navigating three-country visa rules and surging airfares requires advance planning.",
    "tags": ["travel", "world-cup", "fifa", "visa", "airlines", "sports"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/fifa-world-cup-2026-travel-surge/"},
        {"name": "Mansion Global", "url": "https://www.mansionglobal.com/articles/wealthy-world-cup-goers-private-jet-travel-2026"},
        {"name": "FIFA", "url": "https://www.fifa.com/fifaplus/en/tournaments/mens/worldcup/canadamexicousa2026"},
        {"name": "BTW Visas", "url": "https://btwvisas.com/mexico-visa-for-indians"}
    ]),
    "score_total": 85,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fc/MetLife_Stadium_Exterior%2C_2026_FIFA_World_Cup_%28June_20%2C_2026%29_%28cropped%29.jpg/1280px-MetLife_Stadium_Exterior%2C_2026_FIFA_World_Cup_%28June_20%2C_2026%29_%28cropped%29.jpg",
    "image_caption": "MetLife Stadium in East Rutherford, New Jersey, during the 2026 FIFA World Cup",
    "image_attribution": "Wikimedia Commons",
    "body": art2_body
}


# ─────────────────────────────────────────────
# Insert
# ─────────────────────────────────────────────

articles = [art1, art2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

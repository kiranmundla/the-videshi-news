#!/usr/bin/env python3
"""Videshi Travel Writer — July 3, 2026 afternoon run."""

import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# Load env
env_file = Path.home() / "workspace" / ".env.supabase"
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
    # ── Article 1: July 4th National Parks Free Entry ──
    {
        "id": str(uuid.uuid4()),
        "headline": "Every US National Park Is Free This Weekend — Here's an NRI Family's Game Plan",
        "subheadline": "America turns 250 on July 4th. The National Park Service is waiving all entrance fees from July 3 through 5, and 72 million Americans are hitting the road. Here's how to beat the crowds.",
        "slug": make_slug("national-parks-free-july-4-america-250-nri-family"),
        "category": "travel",
        "vertical": "travel",
        "is_editorial": False,
        "diaspora_angle": "For NRI families who never quite got around to visiting America's national parks, the July 4th fee waiver — combined with the semiquincentennial celebrations — is the cheapest and most patriotic entry point to a quintessentially American experience.",
        "tags": ["travel", "national parks", "july 4", "road trip", "NRI families", "america 250"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "National Park Service", "url": "https://www.nps.gov/planyourvisit/fee-free-parks.htm"},
            {"name": "AAA Travel Forecast", "url": "https://newsroom.aaa.com/"},
            {"name": "FOX 13 Seattle", "url": "https://www.q13fox.com/news/free-entry-national-parks-fourth-july-weekend"},
            {"name": "INRIX Traffic Data", "url": "https://inrix.com/"}
        ]),
        "score_total": 82,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6d/Yellowstone_National_Park_%28WY%2C_USA%29%2C_Grand_Prismatic_Spring_--_2022_--_2514.jpg/1280px-Yellowstone_National_Park_%28WY%2C_USA%29%2C_Grand_Prismatic_Spring_--_2022_--_2514.jpg",
        "image_caption": "The Grand Prismatic Spring at Yellowstone National Park, one of over 400 NPS sites offering free entry this weekend",
        "image_attribution": "Wikimedia Commons",
        "body": """The National Park Service has thrown open every gate in the country. From Friday, July 3 through Sunday, July 5, all 423 national park sites — from Yellowstone to the Statue of Liberty — will waive their entrance fees. The occasion: America's 250th birthday, the semiquincentennial that has turned this Fourth of July into something larger than a long weekend.

For Indian American families, most of whom live within a day's drive of at least one major national park, the timing couldn't be better. Parks that normally charge $35 per vehicle — Yellowstone, Grand Canyon, Yosemite, Zion — cost nothing to enter. Campsite reservations and guided tour fees still apply, but the gate itself is free.

## 72 million on the road

AAA projects 72.2 million Americans will drive at least 50 miles this weekend, making it one of the busiest travel periods of the year. Another 4.9 million will travel by bus, train, or cruise. Gas prices sit around $3.83 nationally — higher than last summer, partly thanks to fuel cost spill-over from the Iran situation — but still manageable for a tank-up-and-go trip.

The traffic data firm INRIX has mapped the worst and best windows for hitting the road:

- **Friday, July 3**: Worst from noon to 7 p.m. Leave before 11 a.m.
- **Saturday, July 4**: Worst from 10 a.m. to 2 p.m. Afternoon clears up after 3 p.m.
- **Sunday, July 5**: Worst from noon to 6 p.m. Best before 11 a.m.

The lesson is old but still true: leave early, drive light, skip the midday jam.

## Five parks NRI families should consider

**Yellowstone** (Wyoming/Montana/Idaho): The original national park. Geysers, hot springs, bison herds, and the Grand Prismatic Spring — the kind of landscape that makes children forget their phones exist. Drive from Salt Lake City (5 hours) or fly into Bozeman or Jackson Hole. Free entry July 3–5; reservations not required.

**Grand Canyon** (Arizona): The South Rim is a 4.5-hour drive from Las Vegas and 3.5 hours from Phoenix — both cities with significant desi populations. Sunrise at Mather Point is worth the early alarm. Pack water; temperatures will exceed 100°F at the rim this weekend.

**Yosemite** (California): NRIs in the Bay Area and Central Valley are within striking distance. Half Dome, Yosemite Falls, and the Tunnel View are all accessible without a backcountry permit. Timed entry reservations may apply — check recreation.gov before driving.

**Great Smoky Mountains** (Tennessee/North Carolina): America's most-visited national park is always free, but the July 4th weekend adds ranger-led programs and special interpretive walks. A 3-hour drive from Atlanta, home to one of the largest Indian American communities in the Southeast.

**Shenandoah** (Virginia): The 105-mile Skyline Drive through the Blue Ridge Mountains is one of the most scenic road trips on the East Coast. Reachable in 90 minutes from the D.C. metro area — where a large share of the Indian American professional class lives.

## Heat, crowds, and what to pack

A brutal heat wave is gripping the eastern United States. New York City is under an extreme heat warning through July 4th, with temperatures expected to hit 101°F. Philadelphia, D.C., and the Southeast aren't much better. For any park visit this weekend, carry more water than you think you need, wear sun protection, and avoid strenuous hikes between 11 a.m. and 3 p.m.

For families with younger children, stick to paved trails and visitor-centre areas. Most major parks have Junior Ranger programs — free activity booklets that keep kids engaged while earning them an official NPS badge.

## The bigger picture

America's 250th is a once-in-a-lifetime marker. Washington, D.C. is hosting a massive "Salute to America 250" celebration on the National Mall, with fireworks starting around 11 p.m. and free Metro rides after 5 p.m. on July 4th. For NRI families who have built lives in this country, the weekend is as much a chance to belong as it is to explore.

Three more fee-free days remain in 2026 after this weekend, including Constitution Day in September — recently designated by Congress through the STARS Act. But for sheer spectacle, nothing beats celebrating America's quarter-millennium in the middle of a national park, with a geyser or a canyon or a mountain ridge doing what fireworks try to imitate."""
    },

    # ── Article 2: World Cup Travel for NRIs ──
    {
        "id": str(uuid.uuid4()),
        "headline": "The World Cup Is Happening in Your Backyard — An NRI's Guide to Catching a Match",
        "subheadline": "The 2026 FIFA World Cup is playing out across 16 cities in the US, Canada, and Mexico right now. India didn't qualify, but four million Indian Americans live within driving distance of a host stadium.",
        "slug": make_slug("world-cup-2026-nri-guide-tickets-host-cities"),
        "category": "travel",
        "vertical": "travel",
        "is_editorial": False,
        "diaspora_angle": "India didn't qualify, but this is the first World Cup on American soil in 32 years. NRIs in metro areas like New York, LA, Dallas, Houston, and the Bay Area are a short drive from knockout-round matches — and the tournament ends July 19.",
        "tags": ["travel", "world cup", "FIFA", "sports travel", "NRI", "2026"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "FIFA", "url": "https://www.fifa.com/fifaplus/en/tournaments/mens/worldcup/canadamexicousa2026"},
            {"name": "Sporting News", "url": "https://www.sportingnews.com/us/soccer/news/how-buy-fifa-world-cup-2026-tickets-guide/"},
            {"name": "StubHub", "url": "https://www.stubhub.com/fifa-world-cup-tickets/"},
            {"name": "AAA Travel", "url": "https://newsroom.aaa.com/"}
        ]),
        "score_total": 80,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5b/2026_FIFA_World_Cup_Match_4%2C_United_States_v_Paraguay_%28stadium_3_hours_before%29.jpg/1280px-2026_FIFA_World_Cup_Match_4%2C_United_States_v_Paraguay_%28stadium_3_hours_before%29.jpg",
        "image_caption": "A 2026 FIFA World Cup stadium in the US fills up before a group-stage match between the United States and Paraguay",
        "image_attribution": "Wikimedia Commons",
        "body": """The biggest sporting event on Earth is playing out across North America right now, and most Indian Americans are close enough to drive to it.

The 2026 FIFA World Cup kicked off on June 11 and runs through July 19, with 48 teams competing across 16 host cities in the United States, Canada, and Mexico. The tournament has already moved past the group stage — the Round of 32 wrapped up this week, and the Round of 16 begins July 4. Quarter-finals start July 9, the semi-finals are on July 14 and 15, and the final is at MetLife Stadium in New Jersey on July 19.

India didn't qualify. But this is the first World Cup held on American soil since 1994, and for the roughly four million Indian Americans scattered across the country's major metros, it's a once-in-a-generation chance to experience the tournament in person — no transatlantic flight required.

## The NRI geography advantage

Eleven of the 16 host cities are in the United States, and they map almost perfectly onto the Indian American population centres:

- **New York/New Jersey** (MetLife Stadium): Hosts the final on July 19. The tri-state area is home to over 600,000 Indian Americans.
- **San Francisco Bay Area** (Levi's Stadium, Santa Clara): Semi-final on July 14. Silicon Valley's desi population needs no introduction.
- **Houston** (NRG Stadium) and **Dallas** (AT&T Stadium): Texas's two host cities sit in the heart of a fast-growing Indian American corridor.
- **Los Angeles** (SoFi Stadium): Eight matches, including two USA group-stage games already played. LA County's Indian American community exceeds 100,000.
- **Atlanta** (Mercedes-Benz Stadium), **Seattle** (Lumen Field), **Philadelphia** (Lincoln Financial Field), **Boston** (Gillette Stadium), **Miami** (Hard Rock Stadium), **Kansas City** (Arrowhead Stadium): All cities with established desi communities and matches still to come.

Canada adds **Toronto** and **Vancouver**; Mexico adds **Guadalajara**, **Mexico City**, and **Monterrey**. For NRIs with a valid US visa, Mexico's three host cities are visa-free (Mexico waives the visa requirement for holders of a valid US, Canadian, UK, Japanese, or Schengen visa).

## How to get tickets now

The official FIFA ticket lottery windows have closed, but seats are still available through secondary markets. StubHub, SeatGeek, and Vivid Seats all list World Cup matches. Prices vary wildly by stage and city:

- **Round of 16 matches** (July 4–6): Starting around $80–150 for upper-level seats in less glamorous matchups.
- **Quarter-finals** (July 9–12): $150–400 depending on the teams.
- **Semi-finals** (July 14–15 in San Francisco and Philadelphia): $300–700+.
- **The final** (July 19, MetLife Stadium): $800 and up, with premium seats crossing $5,000.

A FIFA ID (free to create at fifa.com) is required to activate any ticket, whether purchased officially or through resale. Tickets are mobile-only — no print-at-home.

## What NRI families should know

**It's a family event.** FIFA's Code of Conduct applies at all venues, and stadiums are designed for all ages. Children under two enter free; kids' tickets (ages 2–16) are discounted in official sales.

**Fan zones are free.** Every host city operates a FIFA Fan Festival — giant outdoor screens, food vendors, live music, and a carnival atmosphere — open to the public at no charge. If you can't get stadium tickets, the fan zone is the next best thing.

**Combine it with a road trip.** The World Cup's geography makes multi-city trips feasible. Drive from Dallas to Houston (4 hours), New York to Philadelphia (2 hours), or fly Bay Area to Seattle (2 hours). Stack a match with a national park visit (see our July 4th national parks guide) for a proper American summer.

**Watch for scams.** Only buy from verified resale platforms. Avoid parking-lot ticket sellers and social media offers. If a deal looks too cheap, it probably is.

## The emotional case

Cricket is India's sport, and the World Cup is football's. But for the generation of Indian Americans who grew up watching Beckham, Ronaldo, and Messi on grainy TV streams, this tournament landing in their own cities carries weight. It's the kind of shared cultural moment — like a desi wedding in a midwestern suburb — where two identities overlap without apology.

The group stage drew record-breaking crowds. Egypt vs. Australia today at AT&T Stadium in Dallas drew 70,000. Ghana vs. Colombia kicks off tonight in Kansas City. France plays Paraguay tomorrow in Philadelphia. The spectacle is real, it's here, and it doesn't need a 16-hour flight to reach."""
    },

    # ── Article 3: Mexico Visa-Free for NRIs ──
    {
        "id": str(uuid.uuid4()),
        "headline": "Mexico Without a Visa — Why Indian Americans Are Discovering Cancún, CDMX, and the Riviera Maya",
        "subheadline": "Indian passport holders with a valid US visa can enter Mexico for up to 180 days without applying for a single additional document. Here's what NRIs need to know before booking.",
        "slug": make_slug("mexico-visa-free-indian-us-visa-cancun-cdmx-nri"),
        "category": "travel",
        "vertical": "travel",
        "is_editorial": False,
        "diaspora_angle": "Most Indian Americans don't realize their US visa doubles as a Mexico entry pass. With direct flights from major US cities starting under $200 round-trip, Mexico is the easiest international trip an NRI can take without paperwork.",
        "tags": ["travel", "mexico", "visa-free", "NRI", "cancun", "caribbean", "US visa"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Mexican Consulate — Visa Exemptions", "url": "https://consulmex.sre.gob.mx/washington/index.php/ligavisos/15-informacion/156-visas-espanol"},
            {"name": "Wikipedia — Visa Policy of Mexico", "url": "https://en.wikipedia.org/wiki/Visa_policy_of_Mexico"},
            {"name": "US State Department — Automatic Revalidation", "url": "https://travel.state.gov/content/travel/en/us-visas/visa-information-resources/visa-expiration-date/auto-revalidate.html"},
            {"name": "Columbia ISSO — Caribbean Travel Guide", "url": "https://isso.columbia.edu/content/returning-canada-mexico-and-adjacent-caribbean-islands"}
        ]),
        "score_total": 78,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d8/Cancun_Strand_Luftbild_%2822143397586%29.jpg/1280px-Cancun_Strand_Luftbild_%2822143397586%29.jpg",
        "image_caption": "Aerial view of Cancún's turquoise shoreline along the Hotel Zone on Mexico's Caribbean coast",
        "image_attribution": "Wikimedia Commons",
        "body": """There is a travel hack hiding in plain sight for the four million Indian Americans living in the United States, and most of them don't know about it.

If you hold an Indian passport and a valid US visa — any category: B1/B2, H-1B, L-1, F-1, even an expired visa with valid status — you can enter Mexico as a tourist for up to 180 days without applying for a Mexican visa. No consulate appointment. No additional paperwork beyond your passport and the Multiple Immigration Form (FMM) handed to you on the plane or at the border.

This isn't a loophole. It's official Mexican government policy, published on the consulate's own website: "All foreign visitors, regardless of their nationality, traveling to Mexico for tourism, business or in transit, are exempt from presenting a Mexican visa as long as they have a valid visa issued by the United States, Canada, Japan, the United Kingdom, or any Schengen Area country." Permanent residents of these countries also qualify.

## Why this matters for NRIs

For Indian passport holders — who face visa requirements for most international travel — Mexico represents a rare exception. A weekend in Cancún requires less paperwork than a trip to most European countries. And the geography helps: direct flights from major NRI hubs run daily.

- **Dallas to Cancún**: 2 hours 40 minutes, fares from $180 round-trip on Spirit and Frontier
- **Houston to Mexico City**: 2 hours 30 minutes, fares from $200 on United and Volaris
- **Los Angeles to Cabo San Lucas**: 2 hours 30 minutes, from $220 on Southwest
- **New York JFK to Cancún**: 3 hours 40 minutes, from $250 on JetBlue and Delta
- **Chicago to Mexico City**: 4 hours, from $230 on Aeromexico

These are summer 2026 prices, and they make Mexico one of the cheapest international trips available from the United States — often cheaper than flying to India's own beach destinations from the same US cities.

## What to see

**Cancún and the Riviera Maya**: The obvious choice. Turquoise Caribbean water, all-inclusive resorts, and Mayan ruins at Tulum and Chichén Itzá. The Hotel Zone is walkable, English-friendly, and built for international tourists. Water temperatures hover around 82°F in July. The food is extraordinary — think fresh ceviche, mole, and street tacos that put Taco Bell out of your vocabulary permanently.

**Mexico City (CDMX)**: One of the world's great cities, and wildly underappreciated by Indian travellers. The food scene rivals any global capital. The Museo Nacional de Antropología is among the finest museums anywhere. Condesa and Roma Norte are walkable, café-lined neighbourhoods that feel like a Latin American Brooklyn. And with World Cup matches at Estadio Azteca, the city has been electric all month.

**Oaxaca**: For the culturally curious NRI who has already done Cancún. Mezcal distilleries, indigenous Zapotec ruins at Monte Albán, some of Mexico's best mole, and a quieter pace. A 50-minute flight from Mexico City.

**San Miguel de Allende**: A colonial-era town in the highlands, popular with American expats. Cobblestone streets, art galleries, excellent restaurants, and a climate that stays in the mid-70s year-round. A 3.5-hour drive from Mexico City.

## The automatic revalidation bonus

Here's a detail that matters for NRIs on expired US visas: the US government's "automatic revalidation" rule allows F-1 and J-1 visa holders — and in many cases other nonimmigrant categories — to travel to Mexico (and Canada and certain Caribbean islands) and re-enter the United States with an expired visa stamp, as long as they maintain valid status, don't stay longer than 30 days, and don't apply for a new visa while abroad.

This means Indian students and workers whose visa stamps have expired but whose I-94 status is current can take a Mexican vacation and return to the US without needing a new visa appointment — a huge relief given the 12-to-18-month wait times at some US consulates in India.

The eligible Caribbean islands under this rule include the Bahamas, Bermuda, Jamaica, Barbados, Dominican Republic, Trinidad and Tobago, and several British, French, and Dutch territories. That's a meaningful expansion of the "visa-free" world for NRIs who thought their travel options were limited to domestic flights and Canada.

## What to watch out for

**The FMM form**: Fill it out completely. You'll get it on your flight or at the land border. For stays of seven days or more, there's a fee of about $32 (around ₹2,700). Shorter stays are free.

**Travel insurance**: Mexico doesn't require it, but carry it anyway. US health insurance rarely covers treatment abroad, and a hospital stay in Cancún without coverage can run $5,000–20,000 depending on the issue.

**Safety**: Stick to tourist areas. The State Department's travel advisory for Mexico is nuanced — resort areas like Cancún, Riviera Maya, and San Miguel de Allende are generally safe. Avoid driving at night in unfamiliar areas, use authorised taxis or Uber, and keep valuables out of sight.

**Your visa must be valid**: The exemption requires a *valid* (unexpired) US visa or permanent resident card. If your visa stamp has expired, automatic revalidation applies only under specific conditions — check the State Department's website or consult an immigration attorney before booking.

Mexico has been sitting next door this whole time, asking nothing more than a passport and the visa you already carry. For a community that knows what it's like to fill out a DS-160, that's not just convenient — it's liberating."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['headline']}")
        print(f"   slug: {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

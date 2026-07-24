#!/usr/bin/env python3
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# Load env (try home then workspace)
for cand in [Path.home() / ".env.supabase", Path.home() / "workspace" / ".env.supabase"]:
    if cand.exists():
        for line in cand.read_text().strip().splitlines():
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())
        break

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

akasa_body = """Akasa Air took delivery of its 39th Boeing 737 MAX on Monday, the eighth aircraft the four-year-old carrier has added in 2026 alone. The jet, registered VT-YBP, ferried in from Seattle via Reykjavik and Cairo before landing in Bengaluru — an unglamorous milestone that nonetheless tells you where Indian aviation is heading.

While the headlines belong to Air India's long-haul ambitions, the quieter story is the scrappy expansion of India's youngest airline at exactly the moment the flag carrier is pulling back. For the diaspora, that matters more than it sounds.

## Why Akasa Is Growing While Air India Retrenches

Air India has spent 2026 trimming some international flying as it digests aircraft delays, retrofits and the operational hangover from a difficult year. Into that gap have stepped India's low-cost carriers. Akasa now connects 27 domestic and seven international destinations, and it has 187 more 737 MAX jets on order for delivery over the next six years — a backlog that guarantees the network keeps widening.

The international map is the part to watch. Five of Akasa's first six overseas routes pointed at the Gulf — Doha, Jeddah, Riyadh, Abu Dhabi and Kuwait City — the corridors that carry millions of Indian workers to and from the Middle East. With Gulf expansion temporarily frozen by regional instability, Akasa pivoted to Southeast Asia: Phuket first, and from September 4, a four-times-weekly Mumbai–Hanoi service that makes Vietnam reachable without a connection.

## What This Means for NRIs

For Indian Americans, Akasa is not an airline you will board in San Francisco or New Jersey — it flies narrowbodies, not transpacific widebodies. Its relevance is on the other side of the journey, after you land in India.

The single biggest friction in a trip home is rarely the long-haul leg; it is the last connection. A family flying SFO–Delhi often still needs to reach Indore, Lucknow, Guwahati or Goa. More frequencies and more carriers on those domestic and short-haul international legs mean cheaper fares, more schedule choices and fewer overnight layovers when the inbound widebody lands at 2 a.m. Akasa's push into greenfield airports — it began daily Noida (Jewar) service to Bengaluru and Navi Mumbai on June 16, complete with a maintenance base — is precisely the kind of capacity that decongests Delhi and Mumbai and gives returning families a smoother last hop.

The Southeast Asia routes matter too. A growing number of NRI families now meet relatives halfway, picking a visa-friendly third country for a reunion rather than everyone converging on India. Vietnam, Thailand and Bali are emerging as those neutral grounds, and a direct Mumbai–Hanoi flight makes a Vietnam reunion a genuine option for the India-based half of a family.

## The Caveats

Akasa remains a low-cost, single-aircraft-type operator. It has no first or business cabin, no flat beds and no through-checked interline deals with the US carriers most NRIs fly across the Pacific. Bags generally have to be re-checked, and a missed Akasa connection is your problem, not the long-haul airline's. Travelers should treat an Akasa segment as a separate ticket and build in a generous buffer — three to four hours — when stitching it to an international arrival.

There is also a fragility to the international story. The same Gulf turbulence that froze Akasa's westward plans could disrupt the Southeast Asia pivot if fuel prices climb. And a fleet that is still adding its 39th aircraft has thin reserves; a single grounded jet ripples across the schedule faster than it would at IndiGo, which operates more than ten times as many planes.

## What's Next

Akasa has signaled it will keep adding both domestic and international points from Noida, and industry watchers expect more Southeast Asian and Gulf destinations once bilateral capacity opens up. For the diaspora, the practical takeaway is simple: the menu of ways to get around India — and to meet family in the region — is getting longer and cheaper, even as the marquee long-haul carrier pulls in its horns. When you book your next trip home, the smartest itinerary may no longer route everything through a single airline.

Sources: The Hindu BusinessLine, Skift, AirInsight, traveltrendstoday.in."""

ladakh_body = """For decades Ladakh was the reward at the end of a punishing journey — a two-day drive over passes that close half the year, or a white-knuckle flight into Leh's high-altitude airport. That calculus is changing fast, and at the SATTE 2026 travel trade show this month, Ladakh pitched itself not as a bucket-list extreme but as a mainstream destination on the verge of all-weather access.

For Indian American families who have long parked Ladakh in the "someday, when the kids are older" column, several pieces are finally falling into place.

## The Infrastructure Story

The headline project is the Zoji La Tunnel, a 14-kilometer bi-directional tube being bored under the pass on the Srinagar–Leh corridor. Today that pass shuts for months each winter, severing the road link and leaving Leh dependent on flights. Once the tunnel opens, Ladakh gets year-round road connectivity for the first time in its history — a transformation for trade, for locals and for the tourism season, which could stretch well beyond the current summer window.

At SATTE, Ladakh's administration leaned into a wider road-building push from Leh out to remote border valleys, the kind of access that spreads visitors — and tourist money — beyond the handful of famous spots. The pitch paired the icons (Pangong Lake, Nubra Valley, Khardung La, Leh's old town) with quieter additions: Tso Moriri, Hemis Monastery, Zanskar, Lamayuru and the war-memorial town of Drass.

## The Dark-Sky Angle

The most distinctive new draw is Hanle, home to the Indian Astronomical Observatory and one of the world's highest optical telescopes. Sitting under some of the clearest, darkest skies anywhere in India, Hanle has been developed as a dark-sky reserve, and astrophotography, stargazing and monastery culture now combine into a niche but fast-growing itinerary. For diaspora parents raising kids in light-polluted American suburbs, a night under the Milky Way at 14,000 feet is the kind of experience that justifies the trip on its own.

## Why It Matters for NRIs

Ladakh has always been a hard sell for the diaspora for two practical reasons: access and acclimatization. Better roads and a lengthening season chip away at the first. The second still demands respect — Leh sits at roughly 3,500 meters, and the high passes and lakes climb well past 4,000. NRI families arriving jet-lagged from a US west-coast flight should budget two full days in Leh to acclimatize before attempting Pangong or Khardung La, and travelers with heart or lung conditions, or with very young children, should consult a doctor first. Altitude sickness does not care how fit you are.

There is a paperwork wrinkle too. Several border areas — Pangong, Nubra, Tso Moriri, Hanle — require Inner Line Permits. Indian citizens, including OCI cardholders traveling on their Indian-origin documents, and foreign nationals face slightly different permit rules, and the regulations have tightened in recent months. Build a buffer day in Leh to arrange permits through a local agent rather than assuming you can sort it at the trailhead.

## Timing the Trip

The sweet spot remains June through September, when the passes are open and the weather is stable — which conveniently overlaps with the US and Canadian school summer break. That alignment is exactly why Ladakh works for diaspora families who can only travel on the academic calendar. Book Leh hotels and homestays early; the season is short and demand at the marquee properties outstrips supply.

The all-weather access that the Zoji La tunnel promises is still a year or two out, so a road trip in from Srinagar this summer still means timing the pass. But the direction of travel is unmistakable. Ladakh is moving from an expedition to a holiday, and the families who go in the next couple of seasons will get the landscapes before the crowds that easier access will inevitably bring.

## What's Next

Watch for the Zoji La tunnel's completion timeline, expanded flight capacity into Leh, and a steady build-out of mid-range accommodation as the administration courts higher volumes. For now, Ladakh rewards the early and the prepared — go acclimatized, go permitted, and go before the tunnel changes everything.

Sources: Tourism Cairns News (SATTE 2026 coverage), Press Information Bureau, Travel And Tour World."""

indigo_body = """IndiGo, India's largest airline, has quietly expanded its codeshare with Australia's Jetstar to cover the budget carrier's flights between Bali (Denpasar) and eight Australian cities. The new routes — Denpasar to Sydney, Melbourne, Brisbane, Perth, Adelaide, the Gold Coast, Cairns and Darwin — went live in stages through late June, and they sketch the outline of something bigger: a one-ticket bridge between India and Australia, routed through Southeast Asia.

It is a small announcement with an outsized signal for the Indian community in Australia, one of the fastest-growing diaspora populations in the world.

## How the Codeshare Works

A codeshare lets one airline sell seats on another's flights under its own flight number, on a single ticket. Under the expanded deal, an IndiGo passenger can book an itinerary that flies IndiGo into Denpasar and continues on Jetstar to an Australian city, with the whole journey on one booking. That means coordinated ticketing and, crucially, the ability to combine an Indian carrier's dense domestic network with onward access to Australia without buying two separate, unconnected tickets.

IndiGo already serves Bali from India, and it has been aggressively building international reach — long-haul flights to Manchester and Amsterdam, new links to Central Asia, and a daily Mumbai–London Heathrow service launching October 26. The Jetstar tie-up extends that ambition eastward, using Bali as a connecting hub rather than forcing everything through the Gulf.

## Why It Matters for the Diaspora

For the roughly one million people of Indian origin in Australia, the trip "home" has long meant a Gulf connection — Dubai, Abu Dhabi, Doha or Singapore — on full-service carriers. Those remain the comfortable, well-trodden options. What the IndiGo–Jetstar bridge adds is a low-cost alternative for budget-conscious travelers: students flying back for a semester break, young families watching every dollar, and visitors making the trip more than once a year.

It also reframes Bali as a meeting point. Indian families split between Australia and India increasingly choose a neutral, visa-friendly destination for reunions, and Bali — beautiful, affordable, and now connected to both countries on a single budget itinerary — fits perfectly. A grandmother flying from Delhi and a grandchild flying from Melbourne can converge on Denpasar without anyone enduring the full India–Australia haul.

## The Fine Print

Budget travel comes with budget rules, and the diaspora should read them carefully. Low-cost interline and codeshare itineraries often have tighter baggage allowances, fees for seat selection and meals, and less generous rebooking protection than the Gulf full-service carriers. Travelers should confirm exactly how bags are handled at the Denpasar transfer — whether they are checked through or must be collected and re-cleared — because Indonesia's transit rules can require picking up luggage and passing immigration depending on the booking.

There is a visa point too. Indian passport holders need a visa on arrival for Indonesia (currently around 500,000 rupiah, payable at the airport or online beforehand) even for a short transit that involves leaving the airside zone. Anyone connecting through Bali on separate tickets, or whose bags are not through-checked, may technically enter Indonesia and should budget for the VOA and the time it takes. Australia, of course, requires its own visa (an ETA or visitor visa) arranged well in advance — the codeshare changes the flying, not the paperwork.

## What's Next

The Jetstar expansion does not yet amount to a true India–Australia network, but it is a deliberate step. IndiGo has made no secret of its widebody ambitions, with long-haul Airbus and Boeing aircraft on order that could one day support nonstop India–Australia flying. Until then, the Bali bridge is the practical workaround — and a sign that the budget carriers, not just the legacy airlines, are now competing for the diaspora's loyalty on the longest routes.

For Indian Australians planning the next trip back, it is worth pricing the IndiGo–Jetstar routing alongside the usual Gulf options. The cheapest path home may now run through a Balinese beach.

Sources: AeroRoutes, AirInsight, Skift."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Akasa Air Just Took Its 39th Jet — and It's Filling the Gap Air India Is Leaving Behind",
        "subheadline": "India's youngest airline is expanding at home and into Southeast Asia exactly as the flag carrier pulls back. For NRIs, the payoff is on the last leg of the journey home.",
        "slug": make_slug("akasa-air-39th-jet-expansion-air-india-scaleback-nri-domestic"),
        "category": "travel",
        "vertical": "aviation",
        "diaspora_angle": "More low-cost capacity on India's domestic and short-haul routes means cheaper fares, more schedule choices and fewer brutal layovers on the final leg of an NRI's trip home.",
        "tags": ["travel", "airlines", "akasa air", "domestic flights", "aviation"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/"},
            {"name": "Skift", "url": "https://skift.com/"},
            {"name": "AirInsight", "url": "https://airinsight.com/"}
        ]),
        "score_total": 72,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/6/6c/Akasa_Air_737_max_8-200.jpg",
        "image_caption": "An Akasa Air Boeing 737 MAX 8-200, the aircraft type the carrier is rapidly adding to its fleet",
        "image_attribution": "Wikimedia Commons",
        "body": akasa_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Ladakh Is About to Get Easier to Reach — and the Diaspora's 'Someday' Trip Just Moved Up",
        "subheadline": "A new all-weather tunnel, fresh roads and a high-altitude dark-sky reserve are turning Ladakh from an expedition into a holiday. Here's how NRI families should plan it.",
        "slug": make_slug("ladakh-tourism-zoji-la-tunnel-hanle-dark-sky-nri-family-trip"),
        "category": "travel",
        "vertical": "destinations",
        "diaspora_angle": "Better access and a lengthening season finally make Ladakh viable for NRI families traveling on the US school calendar — if they plan for altitude and permits.",
        "tags": ["travel", "ladakh", "india tourism", "destinations", "road trip"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Tourism Cairns News (SATTE 2026)", "url": "https://www.tourismcairns.com.au/"},
            {"name": "Press Information Bureau", "url": "https://pib.gov.in/"},
            {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/"}
        ]),
        "score_total": 70,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/c/c9/Late_afternoon_at_the_Pangong_Tso_%2810035239163%29.jpg",
        "image_caption": "Late afternoon light over Pangong Tso, the high-altitude lake on Ladakh's tourist circuit",
        "image_attribution": "Wikimedia Commons",
        "body": ladakh_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "IndiGo Just Built a Budget Bridge From India to Australia — Through a Beach in Bali",
        "subheadline": "An expanded IndiGo–Jetstar codeshare links India and eight Australian cities via Denpasar on a single ticket, opening a low-cost path home for the diaspora Down Under.",
        "slug": make_slug("indigo-jetstar-codeshare-bali-australia-india-bridge-nri-budget"),
        "category": "travel",
        "vertical": "aviation",
        "diaspora_angle": "For the million-strong Indian community in Australia, the codeshare adds a budget alternative to Gulf carriers and turns Bali into a natural reunion point for families split across both countries.",
        "tags": ["travel", "airlines", "indigo", "australia", "bali"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "AeroRoutes", "url": "https://www.aeroroutes.com/"},
            {"name": "AirInsight", "url": "https://airinsight.com/"},
            {"name": "Skift", "url": "https://skift.com/"}
        ]),
        "score_total": 71,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/f/f5/IndiGo_A320neo_%28VT-ITZ%29_%40_GAU%2C_Sept_2019_%2801%29.jpg",
        "image_caption": "An IndiGo Airbus A320neo, the workhorse of India's largest airline as it expands its international codeshare network",
        "image_attribution": "Wikimedia Commons",
        "body": indigo_body
    }
]

for art in articles:
    wc = len(art["body"].split())
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']} ({wc} words)")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

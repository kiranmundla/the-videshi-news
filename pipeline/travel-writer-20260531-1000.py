#!/usr/bin/env python3
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
    {
        "id": str(uuid.uuid4()),
        "headline": "India Boots Turkey's Çelebi from Nine Major Airports — What NRIs Flying This Summer Need to Know",
        "subheadline": "The abrupt revocation of Çelebi Aviation's security clearance is forcing India's biggest airports to scramble for new ground handlers, and travel agencies have stopped booking Turkey and Azerbaijan entirely.",
        "slug": make_slug("india-boots-celebi-turkey-airports-nri-summer"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "NRIs flying through Delhi, Mumbai, Bengaluru, and Hyderabad this summer may face baggage and cargo delays as airports transition ground handling away from Çelebi. Istanbul — a popular NRI stopover and layover hub — is now effectively off the itinerary as Indian agencies halt bookings.",
        "tags": ["travel", "airlines", "airports", "india-turkey", "ground-handling"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "The Indian Eye", "url": "https://theindianeye.com/major-indian-airports-rush-to-ensure-smooth-operations-as-turkish-firm-celebi-aviation-blocked/"},
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/economy/logistics/bl-explainer-why-did-india-withdraw-security-clearance-of-turkish-ground-handling-firm-celebi/article69633271.ece"},
            {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/1381416/pexels-photo-1381416.jpeg",
        "body": """India's Bureau of Civil Aviation Security has revoked the security clearance of Çelebi Aviation, the Turkish-founded ground-handling giant that operates at nine of the country's busiest airports. The decision — a direct consequence of India-Turkey diplomatic tensions following Ankara's vocal support for Pakistan during Operation Sindoor — has sent airports from Delhi to Goa into emergency transition mode.

## The Scale of the Disruption

Çelebi is not a marginal operator. The company handles roughly 160 flights daily across Delhi, Mumbai, Bengaluru, Hyderabad, Ahmedabad, Goa, Kochi, Kolkata, and Pune. At Delhi alone, it runs one of the airport's two cargo terminals through a joint venture. Over 10,000 employees are now being transitioned to alternative providers — AISATS, Bird Group, and AI Airport Services — with airport operators promising "immediate effect" continuity.

Delhi International Airport Limited (DIAL) has confirmed that all Çelebi staff will be absorbed by new employers under existing terms. Bengaluru's Kempegowda International Airport and Goa's Manohar International Airport have issued similar assurances.

But industry analysts are less sanguine. "While the passenger-facing side — check-in counters, boarding gates — can be transitioned relatively quickly, cargo handling is a different beast," one aviation consultant told business media. Cargo terminal operations require specialized equipment, trained handlers, and established workflows that cannot be replicated overnight.

## What This Means for NRIs Flying This Summer

For Indian Americans booking summer trips home, the immediate risk is modest but real. Baggage handling delays are the most likely inconvenience, particularly at Delhi and Mumbai during the peak June-August travel window. Cargo shipments — including the boxes of electronics, clothing, and gifts that NRIs routinely send ahead of family visits — could face processing delays at Delhi's cargo terminal.

The bigger shift is Istanbul's disappearing act from the Indian travel map. Turkish Airlines' Istanbul hub has long been a popular connection point for NRIs flying between the US and India, offering competitive fares and a convenient geographic midpoint. Now, Indian travel agencies have halted bookings to Turkey and Azerbaijan entirely, citing the deteriorating bilateral relationship and potential visa complications.

## The Geopolitical Backdrop

The Çelebi ban is the latest in a cascade of retaliatory measures between New Delhi and Ankara. Turkey's criticism of India's military strikes against terrorist infrastructure in Pakistan triggered a diplomatic downgrade that has now spilled into commercial aviation. Çelebi's CEO Dave Dorner personally met Civil Aviation Ministry officials to argue the company has no political affiliation with the Turkish government. The India operations head separately wrote to Mumbai airport making the same case. Neither effort succeeded.

## Practical Advice

NRIs with upcoming India trips should check whether their itinerary routes through Istanbul and consider alternatives — Abu Dhabi, Doha, and Dubai remain stable connecting hubs with no diplomatic complications. For those flying directly into Delhi or Mumbai, arriving with only carry-on luggage during the first few weeks of the transition would eliminate the baggage-handling risk entirely.

Civil Aviation Minister Ram Mohan Naidu has publicly assured travelers that "no passenger will face disruption," but transitions of this scale rarely happen without friction. The 10,000 employees being reshuffled and the cargo terminal being reassigned represent the largest single disruption to Indian airport ground operations in recent memory.

For the 4.5 million Indian Americans who fly to India at least once a year, the advice is simple: book direct when you can, avoid Istanbul for now, and pack light."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "France Drops Airport Transit Visa for Indians — Paris CDG Just Became the Best European Hub for NRIs",
        "subheadline": "A quiet rule change in April means Indian passport holders can now connect through French airports without extra paperwork, reshaping the cheapest routes between America and India.",
        "slug": make_slug("france-drops-transit-visa-indians-cdg-nri"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "NRIs connecting through Paris CDG on routes like JFK-CDG-DEL or SFO-CDG-BOM no longer need an Airport Transit Visa, eliminating a $90 fee, a consulate visit, and weeks of processing time. This puts Air France and partner airlines back in the running for price-conscious diaspora travelers.",
        "tags": ["travel", "visa", "france", "transit", "europe", "schengen"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/the-united-states-joins-canada-france-germany-cyprus-australia-israel-kenya-and-india-in-enforcing-radical-2026-expat-travel-rules-immediately-along-with-automated-border-shifts/"},
            {"name": "France-Visas Portal", "url": "https://france-visas.gouv.fr/"},
            {"name": "Henley Passport Index 2026", "url": "https://www.henleyglobal.com/passport-index"}
        ]),
        "score_total": 75,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/2612113/pexels-photo-2612113.jpeg",
        "body": """For years, connecting through Paris Charles de Gaulle Airport has been one of those experiences Indian passport holders just learned to avoid. Even if you never left the international transit zone — never set foot on French soil, never glanced at a customs officer — you still needed an Airport Transit Visa (ATV). That meant a consulate appointment, biometrics, a €80 fee, and three to four weeks of processing time, all for the privilege of walking from Gate E to Gate F.

As of April 10, 2026, that requirement is gone.

## What Changed

Official directives published through the France-Visas portal confirm that Indian nationals traveling from India no longer need to secure an ATV when transiting through French international airports. The exemption applies to passengers who remain inside the international transit zone without crossing into French border control territory.

The change is part of a broader 2026 overhaul of transit regulations across multiple countries. France joins a growing list of nations modernizing border policies through digital pre-authorization systems, and for Indians specifically, the ATV removal addresses a longstanding friction point that had made CDG less attractive than Gulf hubs like Dubai and Doha.

## Why This Matters for NRIs

The practical impact is significant. Air France, in partnership with Delta through the SkyTeam alliance, operates some of the most competitive one-stop fares between the US East Coast and India. Routes like JFK-CDG-DEL, BOS-CDG-BOM, and ATL-CDG-HYD have consistently appeared in fare searches — but many NRIs dismissed them outright because of the ATV requirement.

Consider the math. A family of four flying JFK to Delhi previously faced $360 in ATV fees alone (€80 per person at current exchange rates), plus four separate consulate visits or VFS Global appointments, plus the risk of a transit visa delay torpedoing an already-booked itinerary. For a route where the savings over a Gulf carrier might only be $200-300 per ticket, the transit visa wiped out any price advantage.

Now, that entire calculation changes. NRIs can book Air France connections through CDG with the same ease as booking through Abu Dhabi or Doha — show up with your passport and boarding pass, walk to your connecting gate, and fly on.

## The Broader Transit Landscape in 2026

France is not the only country rethinking transit rules. The year has brought a wave of digital border reforms that affect Indian travelers:

**Kenya** has made its electronic Travel Authorization (eTA) mandatory for all arrivals, replacing its former visa-free framework. **Israel** now enforces an ETA-IL system for visa-exempt travelers. **Canada** continues to refine its eTA system, and **Australia's** digital visitor authorization has been operational for several years.

For Indian passport holders, the net effect is a shift from paper-and-consulate processes to digital-first authorizations — some adding friction (Kenya, Israel), others removing it (France).

## Best Routes Through CDG for NRIs

With the ATV gone, here are the CDG connections worth watching:

**JFK-CDG-DEL**: Air France's flagship corridor. Competitive fares, modern A350 service, and CDG Terminal 2E is one of the better-connected transit hubs in Europe.

**SFO-CDG-BOM/BLR**: Longer routing than Gulf options, but Air France frequently runs promotional fares on the SFO-CDG leg that make the total competitive.

**ORD-CDG-HYD**: Chicago's NRI community has limited nonstop options to South India. CDG offers a one-stop alternative to the Gulf carrier two-stop.

The CDG transit experience itself has improved. Terminal 2E's international connections area has been expanded, and Air France's Salon lounges offer decent food and rest options for long layovers.

## One Caveat

The ATV exemption applies to passengers transiting airside — meaning you stay within the international zone. If your connection requires clearing French immigration (different terminals, overnight stays, or checked bags that need rechecking), you still need a Schengen visa. For most one-stop NRI itineraries, this is not an issue, but read your booking carefully before assuming you are covered.

For the roughly 2.7 million Indian passport holders in the United States, this quiet rule change could redirect thousands of bookings toward CDG every year. Paris just went from "avoid the connection" to "check the fare first.\""""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Airlines Are Launching Match-Day Flights for the IPL Final — Cricket Tourism Has Officially Arrived",
        "subheadline": "Akasa Air's special red-eye services for the GT-RCB final in Ahmedabad show how Indian aviation is finally treating cricket as a travel vertical, not just a television event.",
        "slug": make_slug("ipl-final-match-day-flights-cricket-tourism-nri"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "NRIs visiting India during IPL season now have same-day fly-in-fly-out options for marquee matches — a format pioneered by European football and NFL travel packages that Indian aviation is only now adopting. For diaspora fans planning trips around IPL 2027, match-day flights signal a new era of cricket-centered travel planning.",
        "tags": ["travel", "cricket", "ipl", "airlines", "akasa-air", "sports-tourism"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Travel and Tourism Times", "url": "https://www.thetravelandtourismtimes.com/2026/05/aviation-akasa-air-adds-special-flights-to-ahmedabad-for-cricket-fans/"},
            {"name": "NewsPoint", "url": "https://newspointapp.com/ipl-2026-final-akasa-air-launches-special-flights-from-mumbai-bengaluru/"},
            {"name": "Akasa Air", "url": "https://www.akasaair.com/"}
        ]),
        "score_total": 70,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/c/cb/Narendra_Modi_Stadium_view_from_the_gallery.jpg",
        "body": """When Akasa Air announced special flights from Bengaluru and Navi Mumbai to Ahmedabad for the IPL 2026 final — Gujarat Titans versus Royal Challengers Bengaluru at the Narendra Modi Stadium — the details told a story that goes well beyond cricket scheduling.

The Bengaluru-Ahmedabad flight departs at 9:30 AM on match day, arriving at 11:50 AM, giving fans a comfortable cushion before the 7:30 PM first ball. The return? A 4:10 AM red-eye, landing in Bengaluru by 6:35 AM — early enough for Monday morning meetings. The Navi Mumbai service follows the same logic: depart at 2:45 PM, arrive at 4:15 PM, return at 3:10 AM.

This is not how Indian airlines have traditionally operated. It is, however, exactly how European football and the NFL have worked for decades — dedicated match-day travel services designed to eliminate overnight hotel stays and let fans experience the event as a day trip rather than a weekend commitment.

## Why This Matters

The IPL has been India's most-watched sporting event for over a decade, but it has never been a significant driver of air travel. Most fans watch from home. Those who attend typically drive or take the train, and when they fly, they book standard scheduled services and plan around available inventory.

Akasa's match-day flights represent a philosophical shift. The airline is treating cricket not as background context for existing routes but as a standalone demand generator — a travel vertical that justifies chartering special services, pricing them for event demand, and marketing them directly to fans.

The economics make sense. Hotel prices in Ahmedabad surge during IPL playoffs, with rooms near the Narendra Modi Stadium routinely exceeding ₹15,000 per night for semifinals and finals. A match-day return flight that eliminates the hotel bill entirely is a compelling value proposition, especially for corporate fans and families who would otherwise spend more on accommodation than on the match tickets themselves.

## The Navi Mumbai Connection

The fact that the match-day service operates from Navi Mumbai International Airport rather than Mumbai's Chhatrapati Shivaji Maharaj International Airport is itself significant. NMIA, which began operations in December 2025, is actively positioning itself as a more agile alternative to Mumbai's congested main hub. Special-event flights — where schedule flexibility and rapid turnaround matter more than legacy slot rights — play directly to NMIA's strengths.

Akasa Air has been one of NMIA's most aggressive early tenants, with plans to scale to 300 domestic and 50 international weekly departures from the airport. Using NMIA as the base for cricket tourism flights is an early proof point for the airport's utility beyond scheduled service.

## What NRIs Should Watch

For the roughly 4.5 million Indian Americans in the US, the IPL has always been a "watch at odd hours" experience — 6 AM start times on the East Coast, 3 AM on the West Coast. But a growing subset of the diaspora plans India trips around the IPL season, combining family visits with live matches.

Match-day flights change the calculus for these trips. Instead of needing to be in the host city for the full duration of a playoff series, NRIs visiting India can now plan surgical one-day trips to marquee matches from wherever they are staying. Flying Bengaluru to Ahmedabad for a final and returning the same night is the kind of flexibility that turns a "maybe" into a booking.

The larger trend is the professionalization of cricket tourism in India. The BCCI's push toward dedicated cricket stadiums (as opposed to multi-sport venues), combined with airline willingness to operate event-specific flights, is creating an infrastructure that mirrors what the English Premier League and Champions League have built in Europe.

## Looking Ahead to IPL 2027

If Akasa's match-day flights prove commercially viable — and early booking reports suggest strong demand — expect IndiGo, Air India, and SpiceJet to follow with similar offerings for IPL 2027. The format could extend beyond cricket to major concerts (Arijit Singh tours routinely sell out across multiple cities), festivals (Durga Puja in Kolkata, Ganesh Chaturthi in Mumbai), and even destination weddings.

For NRIs planning India trips in early 2027, the advice is simple: check the IPL schedule before booking your dates. The era of flying in for the match and flying home before sunrise has officially begun."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

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
        "headline": "Germany Just Dropped the Transit Visa for Indians — and Frankfurt Is Now a Cleaner Route Home",
        "subheadline": "From June 3, Indian passport holders can connect through German airports without the Type A transit visa. Paired with France's April change, the two biggest European hubs are now both open for airside layovers.",
        "slug": make_slug("germany-airport-transit-visa-removed-indians-frankfurt-munich-nri"),
        "category": "travel",
        "vertical": "immigration",
        "diaspora_angle": "Many US-based NRIs fly Lufthansa or connect through Frankfurt and Munich on the way to and from India; they no longer need to budget time, money, or paperwork for a German transit visa on airside layovers.",
        "tags": ["travel", "visa", "germany", "schengen", "airlines"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Federal Foreign Office (Germany)", "url": "https://uk.diplo.de/"},
            {"name": "Livemint", "url": "https://www.livemint.com/"},
            {"name": "Business Travel News Europe", "url": "https://www.businesstravelnewseurope.com/"},
            {"name": "Travel + Leisure Asia", "url": "https://www.travelandleisureasia.com/"}
        ]),
        "score_total": 80,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ed/Frankfurt_Flughafen%2C_Terminal_1%2C_Abflughalle_B.jpg/1280px-Frankfurt_Flughafen%2C_Terminal_1%2C_Abflughalle_B.jpg",
        "image_caption": "Departures hall at Frankfurt Airport Terminal 1, Germany's largest international transit hub",
        "image_attribution": "Wikimedia Commons",
        "body": """Germany has scrapped one of the small but stubborn frictions of flying between the United States and India through Europe. As of **June 3, 2026**, Indian nationals no longer need an airport transit visa to connect through German airports on their way to a third country. The change, published in Germany's Federal Law Gazette (the *Bundesgesetzblatt*) on June 2, makes Frankfurt and Munich open for airside layovers without the Type A Schengen visa that used to be mandatory even for passengers who never left the terminal.

It is the second major European hub to drop the requirement in a matter of weeks. France did the same in April. Together, the two countries operate the bulk of one-stop European connections between North America and the subcontinent, which is exactly why this matters far beyond Delhi.

## What actually changed

Until this month, an Indian passport holder routing, say, San Francisco–Frankfurt–Bengaluru on a single ticket technically needed a German airport transit visa (the "Type A" Schengen) — a separate application, a fee, an appointment, and the risk of a delay that could derail a trip. That requirement is gone. Indian travelers can now sit in the international transit zone at Frankfurt or Munich and board their onward flight with nothing more than a valid onward ticket.

The German government tied the move directly to Chancellor Friedrich Merz's visit to India in January 2026, framing it as part of deepening economic and people-to-people ties. India's Ministry of External Affairs welcomed the step, and the Lufthansa Group — which runs more than 70 weekly flights between India and Europe — called it a measure that will "simplify travel, improve connectivity and further reinforce Germany's role as a leading gateway between India, Europe and the world."

## The fine print NRIs should not skip

This is an **airside transit** exemption, and the boundaries are strict. It does *not* let you enter Germany or the wider Schengen area. The waiver does not apply if you:

- need to pass through border control,
- have to collect checked baggage and re-check it,
- must change airports, or
- are connecting through two or more Schengen airports on the same journey.

In plain terms: if your bags are checked through to your final destination and you stay inside the international zone, you are fine. If your itinerary forces you to clear immigration — to overnight in Germany, switch terminals that require entry, or pick up and re-drop luggage — you still need a standard Schengen visa. Travelers on open-jaw or "open ticket" itineraries should confirm with the airline before assuming they qualify.

## Why this is a quiet win for the US diaspora

For Indian Americans, the European connection has always been a workhorse alternative to the Gulf hubs. Lufthansa, with Frankfurt and Munich as its twin engines, feeds dozens of US cities and a deep Indian network — Delhi, Mumbai, Bengaluru, Hyderabad, Chennai. The transit-visa rule was a needless tax on that convenience, especially for green-card holders and H-1B families who travel on Indian passports and book multi-leg tickets months in advance.

Removing it does three things. It cuts cost and paperwork for anyone choosing a German routing. It makes last-minute fare deals on Lufthansa and its partners genuinely usable, because you no longer have to factor in visa lead time. And it strengthens Frankfurt and Munich as fallback options when Gulf carriers spike around Diwali and the December holidays.

There is a subtler benefit too. Travelers who were nervous about a tight European connection — worried that a missed flight could strand them visa-less in a Schengen terminal — now have more flexibility to rebook onward without a bureaucratic trap waiting on the other side.

## What to do with it

If you are planning a winter trip home, it is worth pricing a one-stop European itinerary alongside the usual Gulf options. The transit-visa removal does not change fares directly, but it removes the hidden friction that often pushed NRIs toward Dubai, Doha, or Abu Dhabi by default. With both France and Germany now open for airside transit, the European route is back to being a clean, paperwork-free choice — not just a backup.

As always, book through-checked bags, keep your onward boarding pass handy, and confirm the routing qualifies as a single airside transit before you rely on the waiver. For the right itinerary, Europe just got noticeably simpler."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Your US Visa Is Now a Free Pass to Argentina — Patagonia and Buenos Aires Without the Consulate Run",
        "subheadline": "Indian passport holders with a valid US visa or Green Card can enter Argentina for up to 90 days with no separate Argentine visa or ETA. With the country co-hosting big-ticket 2026 sport, the timing is ideal.",
        "slug": make_slug("argentina-visa-free-indians-us-visa-green-card-patagonia-nri"),
        "category": "travel",
        "vertical": "immigration",
        "diaspora_angle": "Bay Area and tri-state NRIs on H-1B, B1/B2, or Green Cards can now add South America to their travel map without a separate Argentine visa, turning a once-complicated bucket-list trip into a long-weekend-friendly option.",
        "tags": ["travel", "visa", "argentina", "south-america", "us-visa"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "KPMG Global Mobility", "url": "https://kpmg.com/"},
            {"name": "BTW Visas", "url": "https://www.btwvisas.com/"},
            {"name": "Argentina Dirección Nacional de Migraciones (Resolution 353/2025)", "url": "https://www.argentina.gob.ar/migraciones"}
        ]),
        "score_total": 74,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/64/Obelisco_de_Buenos_Aires_at_sunset.jpg/1280px-Obelisco_de_Buenos_Aires_at_sunset.jpg",
        "image_caption": "The Obelisco at sunset in downtown Buenos Aires, Argentina",
        "image_attribution": "Wikimedia Commons",
        "body": """For years, Argentina sat in the awkward middle of the Indian traveler's bucket list — close enough to dream about from the US, far enough behind a consular process that most never bothered. That calculus has quietly changed. Indian citizens who hold a **valid US visa in an eligible category — or a US Green Card — can now enter Argentina for up to 90 days without a separate Argentine visa or electronic travel authorization (AVE/ETA)**.

The rule comes from Resolution 353/2025, issued by Argentina's national immigration office and published in the country's Official Gazette in August 2025. A January 2026 update extended the same benefit to US Green Card holders. For the roughly 5 million-strong Indian American community — heavy with H-1B professionals, students, and B1/B2 visa holders — it turns a complicated trip into a passport-and-go one.

## Who qualifies

The exemption is specific. To enter Argentina visa-free, an Indian passport holder must carry a currently valid US visa in one of these categories:

- **B1/B2** (business or tourist)
- **H-1B** (specialty worker)
- **J** (exchange visitor)
- **O** (extraordinary ability)
- **P (P1–P3)** (athletes, artists, performers)
- **E** (treaty trader/investor)

— or a valid **US Green Card**. Holders of any of these can stay up to 90 days for tourism or short-stay business, with a one-time extension possible for an equivalent period at the discretion of Argentina's immigration office.

Two cautions. First, the US visa must be genuinely valid — not expired, not a categories outside the list above. Student F-1 visas, for example, are not named in the resolution, so travelers in other categories should verify their eligibility against the official list before booking. Second, the entry permission does **not** allow a change of immigration status inside Argentina; anyone seeking work or residence must go through the regular process.

And there is good news even for Indians who do not hold a qualifying US document: under a bilateral arrangement, the standard Argentine tourist visa fee is **waived entirely** for Indian nationals (₹0 versus the roughly $150 charged to many other nationalities). So Argentina is cheaper to enter for Indians across the board — the US-visa route simply removes the paperwork too.

## Why this lands now

Argentina is having a moment with Indian travelers, and not by accident. The country is a marquee South American destination at exactly the price point and season that works for the diaspora: its summer runs December through February, lining up neatly with the US holiday break when many NRIs already take long trips.

The draw is the variety. **Buenos Aires** offers a European-flavored capital — tango, steak, and the Recoleta and Palermo neighborhoods — at a fraction of European prices, especially with the peso's long slide making dollar-denominated travel a bargain. **Patagonia**, shared with Chile, delivers glaciers, the Perito Moreno ice field, and trekking around El Chaltén that rivals anything in the Himalayas. **Iguazú Falls** on the Brazil border is a genuine world wonder. For wine lovers, **Mendoza's** Malbec country sits in the Andes' shadow.

## How to fit it into a US itinerary

The practical path for most US-based NRIs is a nonstop or one-stop from a major hub. United flies Houston–Buenos Aires, American connects via Miami, and several Latin American carriers feed the route through São Paulo, Bogotá, or Lima. Because the visa friction is gone, the trip now plans like any other long-haul vacation: pick dates, price the fare, and go.

A few logistics worth noting. Carry your physical passport plus the valid US visa or Green Card — Argentine border officers will check both, since the visa-free entry is contingent on the US document. Build in the 90-day ceiling if you are combining Argentina with neighboring Chile, Brazil, or Uruguay, each of which has its own rules. And remember the stay is for tourism or short business, not work.

For a community that has steadily ticked off Europe, Southeast Asia, and the Gulf, Argentina has been the conspicuous gap on the map. With a US visa already in the passport, that gap just closed."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Diwali 2026 Falls on November 8 — Here's the Booking Window NRIs Should Lock Before Fares Spike",
        "subheadline": "Peak-season demand on US–India routes is already building for the October–November festival rush. The data points to a clear advance-purchase sweet spot — and a few routing tricks to beat the worst of the surge.",
        "slug": make_slug("diwali-2026-us-india-flight-booking-window-fares-nri"),
        "category": "travel",
        "vertical": "economy",
        "diaspora_angle": "For US-based Indian families planning to be home for Diwali, the difference between booking now and booking in October can be hundreds of dollars per ticket on SFO/JFK/ORD–India routes; this is the practical timing guide they need.",
        "tags": ["travel", "airlines", "diwali", "flight-deals", "festival-travel"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Alternative Airlines (Diwali 2026 dates)", "url": "https://www.alternativeairlines.com/"},
            {"name": "Upstox (festive airfare analysis)", "url": "https://upstox.com/"},
            {"name": "Air India Newsroom", "url": "https://www.airindia.com/"}
        ]),
        "score_total": 76,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/8887279/pexels-photo-8887279.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Lit clay diyas during Diwali, the festival that drives India's peak travel season",
        "image_attribution": "Pexels",
        "body": """Mark the date: **Diwali 2026 falls on Sunday, November 8**, with the five-day festival running November 6 (Dhanteras) through November 10 (Bhai Dooj). For the millions of Indian Americans who try to be home for the lights, that single Sunday is the gravitational center of the year's most expensive travel window — and the clock on getting a sane fare is already ticking.

Here is the uncomfortable truth about US–India flights around Diwali: by the time the festival is "soon," the cheap seats are long gone. The good news is that the pattern is predictable enough to game, if you act on it now.

## The booking sweet spot

For ultra-long-haul routes like SFO–DEL, JFK–BOM, ORD–HYD, and LAX–BLR, fare data points to an optimal purchase window of roughly **four to seven months before departure**. For a November 8 Diwali, that means the window is open right now and starts closing through summer. Wait past September and you are firmly in the danger zone, where last-minute demand drives prices up sharply.

The seasonal math is brutal around the festival. October, November, and December are consistently the costliest months to fly to India — the weather in the north is pleasant, and the Indian festival calendar collides with US Thanksgiving and the December holidays. Roundtrip economy fares that sit near $850–$1,000 in the September shoulder season routinely climb to $1,500–$1,800 or higher for peak Diwali-week travel.

## Routing tricks that actually move the needle

A few strategies reliably beat the surge:

- **Fly the shoulder, not the peak.** If your schedule has any give, travel a week before November 6 or a week after November 10. Fares drop noticeably the moment you step outside the festival corridor. September remains the single cheapest month to fly to India.
- **Use secondary gateways.** Departing from Newark (EWR) instead of JFK, or landing in Bengaluru (BLR) instead of Mumbai, can shave meaningful dollars off the fare. Tier-2 Indian arrival cities are often cheaper than the big three.
- **Consider a "reverse layover."** Routing through Istanbul (Turkish), Doha (Qatar), or Frankfurt/Munich (Lufthansa) frequently undercuts nonstops during peak weeks — and with France and Germany having just dropped the airport transit visa for Indian nationals, the European one-stop is now paperwork-free for airside connections.
- **Shift to midweek.** Tuesday and Wednesday departures average lower fares than Friday-to-Sunday travel, when business and leisure demand overlap.

## What the airlines are doing

Expect the familiar festive playbook from Indian carriers as autumn approaches. In past years, Air India and Air India Express have added scores of extra flights on high-demand domestic legs — Patna, Lucknow, and other festival-heavy destinations — to absorb the Diwali and Chhath Puja rush, and India's civil aviation ministry has publicly pressed airlines to keep fares "reasonable" and add capacity. None of that, however, reliably tames the long-haul international fare; the discipline still falls on the traveler to book early.

Watch, too, for bank-linked promotions. Air India has run limited-window instant-discount offers with HDFC Bank tied to bookings made in the first half of October. Those can help at the margins, but they are no substitute for buying into the four-to-seven-month window.

## The bottom line

If being home for Diwali 2026 is non-negotiable, treat the next several weeks as your real deadline — not October. Price the major US gateways against the Gulf and European one-stops, keep your dates flexible by a few days around November 8 if you can, and set fare alerts on your core route today. The families who lock fares in the summer window will spend the festival lighting diyas. The ones who wait will spend it refreshing fare pages and wincing at the total."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

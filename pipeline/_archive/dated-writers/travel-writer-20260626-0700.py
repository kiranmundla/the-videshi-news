#!/usr/bin/env python3
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# Load env
env_file = Path.home() / ".env.supabase"
if not env_file.exists():
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
        "headline": "Your Japan Visa Is Quietly a Passport to Seven More Countries — and India's Diaspora Should Read the Fine Print",
        "subheadline": "After last week's Motegi–Jaishankar talks, a valid Japan visa now eases Indian entry into Mexico, Taiwan, Georgia and more. The catch is in the conditions, not the headline.",
        "slug": make_slug("japan-visa-unlocks-seven-countries-indians-mexico-taiwan-georgia-nri"),
        "category": "travel",
        "vertical": "immigration",
        "diaspora_angle": "For Indian-passport NRIs who travel on US green cards or H-1Bs, a multiple-entry Japan visa is now a low-cost backdoor into Mexico, Taiwan and Georgia without separate consular runs.",
        "tags": ["travel", "visa", "japan", "india", "diaspora"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The World Opinion", "url": "https://theworldopinion.com/"},
            {"name": "The Economic Times (ETNRI)", "url": "https://economictimes.indiatimes.com/nri"},
            {"name": "Ministry of Foreign Affairs of Japan", "url": "https://www.mofa.go.jp/"}
        ]),
        "score_total": 78,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/Japan_Immigration_Visa_Entry_Exit_Stamp_in_1996.jpg/1280px-Japan_Immigration_Visa_Entry_Exit_Stamp_in_1996.jpg",
        "image_caption": "A Japanese immigration entry and exit stamp inside a passport, the document at the centre of the new travel arrangement.",
        "image_attribution": "Wikimedia Commons",
        "body": """A valid Japanese visa has always opened the door to Japan. As of this week, it opens several more — and for the millions of Indian passport holders scattered across the United States, Britain and Canada, that quiet expansion is worth understanding before anyone books a multi-country trip on the strength of a headline.

The change follows a three-day visit to New Delhi by Japanese Foreign Minister Toshimitsu Motegi, who concluded talks with his Indian counterpart S. Jaishankar last week. Tucked inside the broader strategic agenda — semiconductors, critical minerals, clean energy — was a piece of travel housekeeping that matters far more to ordinary families than to ministries: Indian citizens holding a valid Japan visa can now use it to simplify entry into a clutch of other countries.

## What the Japan visa actually unlocks

The list spans four continents, but each entry carries its own conditions. Travellers should treat the destination's own rule as the law, not the convenience.

- **Mexico** is the headline prize. An Indian passport holder with a valid *multiple-entry* Japan visa may enter Mexico without applying separately, for stays of up to 180 days, subject to passport validity. For green-card-less NRIs who still travel on an Indian passport, this removes a notoriously fiddly consular step.
- **Taiwan** grants entry via the ROC Travel Authorisation Certificate, allowing stays of up to 14 days at a time with multiple entries inside a 90-day window.
- **The Philippines** permits 14 days, extendable by seven, on a valid Japan visa, with a six-month passport and an onward ticket.
- **Georgia** allows up to 90 days within any 180-day period — a generous window for a country fast becoming a budget favourite.
- **Montenegro** offers 30 days, though its rules shift and should be confirmed.
- **Singapore** is the most misread of the set: the Japan visa qualifies travellers only for the Visa-Free Transit Facility of up to 96 hours, not a tourist stay.
- **The UAE** grants visa-on-arrival to Indians holding a valid Japan visa, with fees scaled to the length of stay.

Several of these arrangements predate the Motegi visit; what changed is the diplomatic emphasis and the publicity, as both governments lean into the 75th anniversary of their strategic partnership in 2027.

## Why this lands differently for the diaspora

For an Indian American who naturalised years ago, none of this applies — a US passport already clears most of these borders. The people who should pay attention are the large cohort of NRIs who remain Indian citizens: H-1B and L-1 workers, recent graduates on OPT, parents visiting on long-term US visas, and the green-card holders who never surrendered their Indian passports.

For that group, the Japan visa becomes a kind of utility document. A family that flies India–US via Tokyo, or that already holds a multiple-entry Japan visa from an earlier trip, can fold a Mexico beach week or a Taiwan stopover into an itinerary without a fresh consular appointment, fresh fees, or the weeks of lead time that Indian passport holders have learned to dread.

## The fine print that trips people up

Two distinctions matter. First, **single-entry versus multiple-entry**: Mexico's 180-day benefit hinges on a *multiple-entry* Japan visa. A one-off tourist visa will not do. Second, **the visa must be valid** — not merely once-issued. Several of these countries check that the Japan visa has remaining validity, and Singapore additionally wants at least one month left on it.

There is also a cost the other way. Japan is raising its own visa fees from 1 July 2026, with the multiple-entry visa jumping from ¥6,000 to ¥30,000, and a forthcoming JESTA pre-travel authorisation will add a screening layer even for visa-exempt arrivals. So the document that unlocks these side trips is itself getting pricier — an argument for getting maximum mileage out of each one.

## The bottom line

This is not visa-free travel, and it is not a shortcut everyone can use. But for the Indian-passport-holding slice of the diaspora — the people for whom every consulate visit is a half-day lost — a valid multiple-entry Japan visa just became one of the most useful pages in the book. Confirm each country's current rule through its embassy before flying, carry proof of the Japan visa's validity, and treat the 180-day Mexico window as the standout. The rest is gravy."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Delhi-NCR Finally Has a Second Airport — Here's What Noida's New Hub Means Before the International Flights Arrive",
        "subheadline": "Noida International Airport at Jewar is now flying, scaling to 40-plus daily departures by July. International service comes later this year — and the diaspora has a stake in both.",
        "slug": make_slug("noida-international-airport-jewar-dxn-operational-delhi-ncr-nri"),
        "category": "travel",
        "vertical": "aviation",
        "diaspora_angle": "For NRIs whose families live in western UP or eastern Delhi-NCR, Jewar can eventually cut the brutal cross-city slog to IGI — but only once long-haul carriers commit later this year.",
        "tags": ["travel", "airports", "noida", "india", "aviation"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/"},
            {"name": "Livemint", "url": "https://www.livemint.com/"},
            {"name": "The Daily Jagran", "url": "https://english.jagran.com/"}
        ]),
        "score_total": 74,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/Prime_Minister_of_Bharat%2C_Shri_Narendra_Damodardas_Modi_at_the_inauguration_ceremony_of_the_Noida_International_Airport%2C_Jewar.jpg/1280px-Prime_Minister_of_Bharat%2C_Shri_Narendra_Damodardas_Modi_at_the_inauguration_ceremony_of_the_Noida_International_Airport%2C_Jewar.jpg",
        "image_caption": "Prime Minister Narendra Modi at the inauguration ceremony of Noida International Airport at Jewar, Uttar Pradesh.",
        "image_attribution": "Wikimedia Commons",
        "body": """After more than a decade of missed deadlines and political wrangling, Delhi-NCR's long-promised second airport is real. Noida International Airport — IATA code **DXN**, sited at Jewar in western Uttar Pradesh — began commercial flights on 15 June 2026, with IndiGo operating the inaugural service and Akasa Air and Air India Express following close behind.

For India's most congested aviation market, this is a genuine milestone. Indira Gandhi International (IGI) has carried the entire region's traffic for years; Jewar, about 100 km southeast of central Delhi, finally gives it a sister. Phase 1 is built to handle 12 million passengers a year on a single runway and one terminal, with the operator — Yamuna International Airport Private Limited, a subsidiary of Zurich Airport International — pitching it as India's first net-zero greenfield hub.

## The ramp-up, in plain numbers

Do not picture a fully formed mega-hub yet. The airport's chief executive, Nitu Samra, told *businessline* that DXN will run roughly 12 daily flights in June, scaling to 40–42 daily departures through July as more routes switch on. IndiGo plans to connect Jewar to more than 16 domestic destinations — Bengaluru, Hyderabad and Navi Mumbai among the metros, plus Amritsar, Chandigarh, Dharamshala, Jaipur, Lucknow, Pantnagar and Srinagar.

The number that matters most to the diaspora, though, is the one that is not here yet: **international flights are not expected until later this year**, with the international terminal slated for completion around October. Foreign carriers have, in the operator's words, "evinced interest," but no long-haul schedule has been confirmed, and Air India has yet to announce its Jewar plans at all.

## Why an NRI should care about a domestic-only airport

The honest answer for now is: location, and the trip home. A large share of the Indian American community traces its roots to western Uttar Pradesh and the broader NCR belt — Noida, Greater Noida, Ghaziabad, Meerut, Aligarh. For families in those towns, the existing routine is grim: land at IGI on the far western edge of Delhi, then face a one-to-two-hour cross-city haul, often after a 15-hour flight. A working second airport on their side of the region is exactly the relief they have wanted.

The catch is sequencing. Until a long-haul carrier commits to Jewar, the diaspora's direct benefit is indirect — better domestic connectivity for the final leg. An NRI flying SFO or JFK to Delhi can already use Jewar today for an onward IndiGo hop to, say, Lucknow or Srinagar, sometimes more conveniently than from IGI. The bigger prize — a nonstop from a Gulf or European hub straight into Jewar — is a later-2026 story at the earliest.

## The cost asterisk

There is one detail worth flagging before anyone reroutes a trip on principle. Jewar's user development fee for departing domestic passengers has been set at ₹490, and early analysis suggested flying out of Noida could cost more than out of Delhi on some routes. Samra has pushed back, arguing the fee is reasonable for a brand-new greenfield airport and that passengers now simply have a choice based on where they live and what time they fly. For a price-sensitive NRI booking six tickets for a family visit, that asterisk is not trivial — compare the all-in fare, not just the convenience.

## What to watch next

Three signals will tell the diaspora when Jewar truly changes their India trip. First, the **international terminal opening**, expected around October. Second, the **first foreign-carrier announcement** — a Gulf airline or Air India committing to a long-haul or Gulf-hub route into DXN. Third, **metro and expressway connectivity** maturing, so that "second airport" means "closer airport" rather than "another airport across town."

For now, treat Noida International as a promising work in progress. It already shortens the final domestic leg for travellers headed into western UP, and by the end of the year it may do far more. Book the family's onward hop through Jewar if it shaves the cross-city slog — but keep flying the long-haul into IGI until the international gates at Jewar actually open."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The Cheapest Window to Fly India–US Is Hiding in Plain Sight — and It's Not the One You're Booking",
        "subheadline": "September-to-October shoulder fares from US gateways to India are landing hundreds below peak summer. For flexible NRIs, the savings dwarf any flash sale.",
        "slug": make_slug("india-us-shoulder-season-fares-september-october-cheapest-nri-2026"),
        "category": "travel",
        "vertical": "economy",
        "diaspora_angle": "NRIs who can shift a India trip from July's peak into the September-October shoulder are seeing round-trip fares fall by $400-$1,000 per ticket on the exact same SFO/JFK routes.",
        "tags": ["travel", "flight deals", "airfare", "india", "diaspora"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "United Airlines", "url": "https://www.united.com/"},
            {"name": "Travelocity", "url": "https://www.travelocity.com/"},
            {"name": "momondo", "url": "https://www.momondo.com/"}
        ]),
        "score_total": 72,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/615060/pexels-photo-615060.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "An airplane wing against a vibrant sky, the kind of long-haul leg that connects US gateways to India.",
        "image_attribution": "Pexels",
        "body": """Every NRI knows the summer routine: book the India trip when school lets out, pay whatever the fare gods demand, and wince at the total. What fewer travellers act on is that the same routes — SFO–Delhi, JFK–Bengaluru, IAH–Mumbai — cost dramatically less just a few weeks later, in a shoulder season that flexible families routinely overlook.

The current fare boards make the gap impossible to miss. The arithmetic, not a flash sale, is where the real money is.

## The numbers on the board

Pull up the live fares and the pattern is stark. On Travelocity's boards this week, SFO–Delhi for September 20–October 20 was listing from about **$809** round trip, while a comparable June 20–July 13 departure on the same route sat near **$1,523** — almost double. JFK–Bengaluru showed roughly **$692** for early-September travel against four-figure fares for late-June dates. JFK–Delhi for a September window came in around **$711**.

United's own boards tell the same story from the India side: Delhi–San Francisco from about **$1,102** round trip, Mumbai–Newark near **$954**, and Delhi–Chicago around **$994** for July–September travel windows — and these soften further as the calendar moves past the summer crush. Out of Houston, momondo was surfacing Qatar Airways IAH–Mumbai itineraries for September and October in the **$981–$991** band, one-stop, against the much higher peak-summer prints.

The headline: on a single route, an NRI family that can shift travel from peak July into late September or October is frequently saving **$400 to $1,000 per ticket**. For four or six travellers, that is the difference between a fare and a down payment.

## Why the window opens

The shoulder season exists because demand collapses just as the routes stay fully scheduled. Summer-holiday family travel ends as US and UK school terms resume in late August and September. The festival rush — Diwali falls later in the autumn — has not yet spiked fares. And the long-haul carriers, having added capacity for summer, keep flying through the lull. More seats, fewer buyers, lower prices.

There is a weather bonus, too. Late September into October is when the monsoon retreats across most of India, leaving green landscapes, washed-clean air and far gentler temperatures than the May–June furnace. The diaspora's own off-season case — that India in the shoulder is cheaper and more pleasant — applies squarely to airfare as well.

## The catch, and how to play it

Two constraints decide whether this works for any given family. The first is **school**: households with young children are often locked into the summer break, and no fare chart changes that. The second is **Diwali**: book too late into October and you collide with the festive-season surge, when fares snap back up and award seats vanish. The sweet spot is the genuine lull — roughly the second week of September through the first half of October — before the Diwali curve bends upward.

A few tactics sharpen the savings. Price the trip as an **open-jaw** if your family is spread across cities; one-way components into Bengaluru or Hyderabad and out of Delhi can beat a rigid round trip. Watch the **one-stop Gulf and European carriers** — Qatar, Etihad, ITA — which often undercut the nonstops by a wide margin for travellers who do not mind a connection. And set a **price alert** the moment you have candidate dates, because shoulder fares move, and the sub-$800 SFO–Delhi prints do not last.

## The bottom line

The cheapest way to fly home is not a coupon code or a 48-hour sale — it is the calendar. For the slice of the diaspora with flexibility — empty-nesters, remote workers, anyone without a school-term anchor — moving the India trip into the September–October shoulder is the single highest-value decision available, worth more than any promo. Lock the dates before Diwali demand arrives, compare the one-stop carriers against the nonstops, and let the off-season do the discounting."""
    }
]

inserted = []
for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"OK {art['slug']}")
        inserted.append(art['headline'])
    except Exception as e:
        print(f"FAIL {art['slug']}: {e}")

print(f"\nInserted {len(inserted)}/{len(articles)} articles")
for h in inserted:
    print(" -", h)

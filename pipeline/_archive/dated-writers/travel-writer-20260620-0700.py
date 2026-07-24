#!/usr/bin/env python3
import json, os, uuid, re, requests, urllib.parse, subprocess
from datetime import datetime, timezone
from pathlib import Path

# ---------- Env ----------
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
UA = "TheVideshi/1.0 (thevideshi.com)"

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

# ---------- Image sourcing ----------
def commons_images(query, limit=6):
    params = {
        "action": "query", "generator": "search", "gsrsearch": query,
        "gsrnamespace": "6", "gsrlimit": str(limit), "prop": "imageinfo",
        "iiprop": "url|size|mime", "iiurlwidth": "1280", "format": "json",
    }
    try:
        r = requests.get("https://commons.wikimedia.org/w/api.php", params=params,
                         headers={"User-Agent": UA}, timeout=20)
        if r.status_code != 200:
            return []
        pages = r.json().get("query", {}).get("pages", {})
        out = []
        for _, pg in pages.items():
            ii = pg.get("imageinfo", [{}])[0]
            mime = ii.get("mime", "")
            if not mime.startswith("image/") or mime == "image/svg+xml":
                continue
            if ii.get("width", 0) < 800:
                continue
            url = ii.get("thumburl") or ii.get("url", "")
            if url:
                out.append({"url": url, "w": ii.get("width", 0), "title": pg.get("title", "")})
        return out
    except Exception as e:
        print(f"  ⚠ Commons error '{query}': {e}")
        return []

def validate_img(url):
    """GET (not HEAD — Wikimedia 400s on HEAD). Confirm image/* and >5KB."""
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=20, stream=True)
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", "0") or 0)
        if r.status_code == 200 and ct.startswith("image/"):
            if cl == 0:
                # read a bit to confirm bytes exist
                chunk = next(r.iter_content(8192), b"")
                return len(chunk) > 4000
            return cl > 5000
    except Exception as e:
        print(f"  ⚠ validate error: {e}")
    return False

def pick_commons(queries):
    for q in queries:
        for cand in commons_images(q):
            if validate_img(cand["url"]):
                print(f"  ✓ Commons image: {cand['title']} ({cand['w']}px) for '{q}'")
                return cand["url"]
    return None

# ---------- Articles ----------
buenos_aires_img = pick_commons([
    "Buenos Aires Obelisco", "Perito Moreno Glacier Argentina", "Iguazu Falls Argentina"
])
frankfurt_img = pick_commons([
    "Frankfurt Airport terminal", "Frankfurt Airport aerial", "Munich Airport terminal"
])
sfo_img = pick_commons([
    "Air India Boeing 777", "San Francisco International Airport international terminal",
    "Air India aircraft"
])

print(f"\nImages → Argentina: {buenos_aires_img}\nTransit: {frankfurt_img}\nSFO: {sfo_img}\n")

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Your US Visa Is Now an Argentina Visa Too — and Patagonia Just Got a Lot Closer",
        "subheadline": "Indians holding a valid US tourist visa or a Green Card can now enter Argentina visa-free for 90 days. For the H-1B and student crowd, South America's most photogenic country just dropped its biggest barrier.",
        "slug": make_slug("argentina-visa-free-indians-us-visa-green-card-patagonia-nri"),
        "category": "travel",
        "vertical": "immigration",
        "diaspora_angle": "The hundreds of thousands of Indians on US visas and Green Cards can now visit Argentina without a separate consular visa or ETA, turning a once-bureaucratic South America trip into a passport-and-go affair.",
        "tags": ["travel", "visa", "argentina", "nri", "us-visa"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "KPMG — Simplified Entry for Indian Nationals (Resolution 353/2025)", "url": "https://kpmg.com/xx/en/our-insights/gms-flash-alert/flash-alert-2025-176.html"},
            {"name": "Argentine Consulate New York — Green Card entry notice", "url": "https://cnyor.cancilleria.gob.ar/en/visas"},
            {"name": "Livemint — Indians with valid US visas can now visit Argentina", "url": "https://www.livemint.com/news/india/indian-citizens-with-valid-us-visas-can-now-visit-argentina-without-a-separate-visa-11756291200000.html"},
        ]),
        "score_total": 80,
        "status": "review",
        "published_at": now,
        "image_url": buenos_aires_img,
        "image_caption": "Buenos Aires, the gateway for Indian travelers now entering Argentina visa-free on a US visa.",
        "image_attribution": "Wikimedia Commons",
        "body": """Argentina has quietly become one of the easiest big-ticket trips an Indian on a US visa can make. Under a resolution that took effect last year and was widened this January, Indian passport holders who carry a valid US visa — or a US Green Card — can enter Argentina for up to 90 days without applying for any separate Argentine visa or electronic travel authorization.

For the diaspora, that is a meaningful shortcut. Argentina has long sat on the harder end of the visa spectrum for Indian citizens, requiring either a consular visa or an AVE electronic permit that meant paperwork, fees and waiting. Now, for a large slice of Indian Americans, the US document already in their passport does the work.

## What changed, and when

The first move came in August 2025, when Argentina's national immigration office published Resolution 353/2025 in the Official Gazette. It allowed Indian citizens holding a valid US visa in a comparable category to enter Argentina without an Argentine consular visa or the AVE. The qualifying US categories are specific: B1/B2 (business/tourist), J, O, P (P1–P3), E, and H-1B.

The second move, effective January 15, 2026, extended the same courtesy to US Green Card holders of Indian nationality. The Argentine Consulate in New York now states plainly that US permanent residence cards are "valid and sufficient to authorize and facilitate entry" for Indian nationals under the Tourist and Businesspersons categories — no consular visa needed.

The permission is for short stays: up to 90 days, extendable once for an equivalent period at the discretion of the immigration office. It does not allow a change of immigration status inside the country, so this is strictly a tourism-and-short-business door, not a back route to residency or work.

## Who exactly qualifies

The rule rewards the most common diaspora visa types. An H-1B worker in Seattle, a J-1 researcher in Boston, an O-1 in Los Angeles, or any Green Card holder can fly to Buenos Aires on the strength of that US status. The visa must be currently valid — an expired US visa does not count.

The categories that do not qualify matter just as much. F-1 students are not on Argentina's listed categories, so a student visa alone does not unlock visa-free entry; those travelers fall back to the regular Argentine tourist visa. The good news there: under a long-standing bilateral arrangement, Argentina waives the visa fee entirely for Indian nationals, charging ₹0 against the roughly $150 most other nationalities pay.

## Why this matters for NRIs

South America has always been the diaspora's hardest continent to reach casually. Distances are long, visa regimes are stiff, and a trip needs planning months out. Argentina removing the visa step for US-visa holders turns it into the kind of place a Bay Area or tri-state family can add onto a longer break without a consular appointment.

It also pairs neatly with the way Indian Americans already travel. Many hold the exact US visa categories Argentina now accepts, and the country offers the sort of trip that photographs well and spans interests: the glaciers and trekking of Patagonia, the wine country around Mendoza, the thunder of Iguazú Falls on the Brazilian border, and the tango-and-steak rhythm of Buenos Aires.

There is a practical caveat worth underlining. The exemption is Argentina-specific. Neighboring Brazil, Chile and Peru each run their own rules, and a US visa does not automatically open all of them — Brazil, for instance, reintroduced visa requirements for several nationalities. Travelers planning a multi-country South America loop should check each border separately rather than assume the Argentine rule travels with them.

## The fine print before you book

A few things to confirm before counting on visa-free entry. The US visa or Green Card must be valid for the full duration of the Argentine stay. Airlines and Argentine border officers will check the underlying US document, so carry it and any supporting paperwork. And because immigration policy can shift, verify the current rule on the Argentine consulate's site close to departure — the categories listed above reflect the resolution as published, but enforcement details occasionally get clarified.

For a diaspora that already keeps a US visa in the drawer, Argentina has effectively turned that document into a second passport stamp. It is one of the more generous travel openings Indian travelers have seen in years, and it lands just as the southern-hemisphere ski and trekking seasons get going.
"""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Europe Just Got Easier to Fly Through: Germany and France Drop Transit Visas for Indians",
        "subheadline": "As of June 3, Indian passport holders no longer need an airport transit visa to connect through German airports — weeks after France did the same. For NRIs routing home via Frankfurt or Paris, a whole layer of paperwork is gone.",
        "slug": make_slug("germany-france-drop-airport-transit-visa-indians-frankfurt-nri"),
        "category": "travel",
        "vertical": "immigration",
        "diaspora_angle": "Indian Americans who connect through Frankfurt, Munich or Paris on the way to India or onward to the UK no longer need a Schengen Type A transit visa, removing a recurring cost and paperwork headache from a popular routing.",
        "tags": ["travel", "visa", "germany", "france", "schengen", "transit"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "German Federal Foreign Office — A-Transit requirement lifted for Indian nationals", "url": "https://uk.diplo.de/uk-en/news/-/2697894"},
            {"name": "The Hindu BusinessLine — Lufthansa eyes higher India traffic after Germany scraps transit visa", "url": "https://www.thehindubusinessline.com/economy/logistics/lufthansa-eyes-higher-india-traffic-after-germany-scraps-airport-transit-visa-requirement/article69000000.ece"},
            {"name": "Livemint — After France, Germany lifts airport transit visa requirement", "url": "https://www.livemint.com/news/india/big-relief-for-indian-flyers-after-france-germany-lifts-airport-transit-visa-requirement-11748800000000.html"},
        ]),
        "score_total": 78,
        "status": "review",
        "published_at": now,
        "image_url": frankfurt_img,
        "image_caption": "Frankfurt Airport, a major transit hub for Indian travelers connecting onward to the UK and the Americas.",
        "image_attribution": "Wikimedia Commons",
        "body": """Two of Europe's busiest air hubs have, within weeks of each other, removed a small but persistent obstacle for Indian travelers. Germany lifted its airport transit visa requirement for Indian nationals on June 3, 2026, following France, which did the same in April. For anyone who connects through Frankfurt, Munich or Paris en route to a third country, the Type A Schengen transit visa is no longer needed.

It sounds like a technicality. For frequent flyers in the diaspora, it removes a recurring cost, a form, and a quiet anxiety about getting paperwork right for an airport you never actually leave.

## What was lifted

Until now, an Indian passport holder transiting "airside" through a German or French airport — never crossing into the country, simply changing planes in the international zone — could still be required to hold an airport transit visa, the Type A Schengen permit. It applied even when the traveler had no intention of entering the Schengen area.

Germany published the change in its Federal Law Gazette (Bundesgesetzblatt) on June 2, with effect from June 3. The German Embassy in New Delhi tied the move to Federal Chancellor Friedrich Merz's January visit to India, framing it as part of deepening German-Indian ties. France operationalized an identical removal on April 10, after Prime Minister Narendra Modi and President Emmanuel Macron agreed to it during Macron's February visit to India.

## What it does not cover

The exemption is narrow and worth reading carefully. It applies only to airside transit — staying within the international zone while connecting between flights. It does not authorize entry into Germany, France or the wider Schengen area.

So if a traveler needs to pass through immigration, collect and recheck baggage, switch airports, or stay overnight outside the secure zone, the standard Schengen visa rules still apply. The change strips out one specific permit for one specific situation; it does not turn a layover into a free Europe visa.

## Why it matters for the diaspora

European hubs are central to how the diaspora moves. A large share of US- and Canada-to-India itineraries, and especially onward connections to the UK, route through Frankfurt, Munich or Paris. Lufthansa alone runs more than 70 weekly flights from India, over 50 of them to Germany, feeding onward to more than 200 destinations through its two German hubs.

Lufthansa was quick to read the change as a tailwind. The group's South Asia sales director, Kevin Markette, told the Hindu BusinessLine that the removal takes out "a long-standing friction point" and should strengthen one-stop demand via Frankfurt and Munich, naming the UK and South American markets such as Brazil as clear beneficiaries.

For an NRI booking a one-stop ticket, the practical upshot is simpler decision-making. A connection through Germany or France no longer carries the asterisk of "check whether you need a transit visa," which in the past pushed some travelers toward Gulf hubs like Dubai, Doha or Abu Dhabi precisely to avoid Schengen paperwork. The European routings are now back on a level footing.

## The wider trend

These two moves are part of a visible warming in how major economies treat the Indian passport. Argentina now admits Indians on a valid US visa. France and Germany have cleared transit. Each is modest on its own, but together they reflect a calculation: India is one of the world's fastest-growing sources of outbound travelers, students and professionals, and the countries that make movement frictionless capture more of that traffic.

For the diaspora specifically, the benefit is concentrated where it is felt most — on the long, multi-leg journeys between an adopted home and the family home in India. A traveler flying San Francisco to London via Frankfurt, or New York to Delhi via Munich, can now treat the European stop as exactly what it is: a place to stretch their legs and grab a coffee, not a visa to apply for.

A reminder before booking: the rule covers airside transit only, and Schengen entry rules are unchanged. But for the millions of journeys that never leave the transit zone, Europe just got noticeably simpler to fly through.
"""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Air India Opens Its First Lounge Outside India — and It Picked San Francisco",
        "subheadline": "The new Maharaja Lounge at SFO is the airline's first signature lounge on foreign soil, a 3,300-square-foot bet on the Bay Area's outsized role in its North America network.",
        "slug": make_slug("air-india-maharaja-lounge-sfo-first-overseas-bay-area-nri"),
        "category": "travel",
        "vertical": "aviation",
        "diaspora_angle": "For the Bay Area's huge Indian-American population flying Air India's nonstops to Delhi, Mumbai and Bengaluru, the airline's first overseas premium lounge means a markedly better pre-flight experience on the long haul home.",
        "tags": ["travel", "air-india", "sfo", "lounge", "nri", "bay-area"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Points Guy — Inside Air India's new Maharaja Lounge at SFO", "url": "https://thepointsguy.com/news/air-india-maharaja-lounge-sfo/"},
            {"name": "Global Traveler — Air India Opens First International Signature Lounge at SFO", "url": "https://www.globaltravelerusa.com/air-india-opens-first-international-signature-lounge-at-sfo/"},
            {"name": "The Hindu BusinessLine — Air India opens first overseas Maharaja Lounge at San Francisco", "url": "https://www.thehindubusinessline.com/economy/logistics/air-india-opens-first-overseas-maharaja-lounge-at-san-francisco-airport/article69000000.ece"},
        ]),
        "score_total": 74,
        "status": "review",
        "published_at": now,
        "image_url": sfo_img,
        "image_caption": "An Air India Boeing 777, the workhorse of the carrier's North America network out of San Francisco.",
        "image_attribution": "Wikimedia Commons",
        "body": """When Air India chose where to open its first signature lounge outside India, it skipped London, New York and Dubai and went to San Francisco. The Maharaja Lounge at SFO, opened May 23 in the International Terminal near the A Gates, is the airline's first lounge on foreign soil since the Tata Group took the carrier back in 2022 — and the choice says a lot about where the diaspora's center of gravity sits.

## A bet on the Bay Area

Air India operates roughly 65 weekly flights between North America and India, and the West Coast is a disproportionate share of that demand. San Francisco anchors nonstops that feed the Bay Area's enormous Indian-American population — engineers, founders and families clustered across Silicon Valley who fly home on the long Pacific routes to Delhi, Mumbai and Bengaluru.

Putting the airline's first overseas lounge here, rather than at a legacy hub like Heathrow, is a recognition that the Bay Area is now one of its most valuable markets. It follows the flagship Maharaja Lounge that opened at Delhi's Indira Gandhi International Airport earlier in 2026; SFO is the second in a planned series of signature lounges.

## What's inside

The lounge spans more than 3,300 square feet and was designed by Hirsch Bedner Associates, the global hospitality firm behind many luxury hotels. It blends contemporary design with Indian heritage elements, and a few touches stand out from the usual airport-lounge template.

There is Aviator's Bar, a speakeasy-style cocktail lounge with a custom architectural ceiling and a hand-picked cellar of premium whiskies and wines. A "lounge within a lounge" zone is reserved for first-class passengers. Live cooking stations and curated culinary spaces aim to capture Indian hospitality rather than serve generic buffet fare, and several art installations were built from upcycled aircraft components. Much of the seating and dining offers tarmac views.

It sits postsecurity near the A gates: after clearing security, travelers turn left, pass the Air France lounge, take the escalators up a level, and follow the signage. Expected hours run roughly 6:30 a.m. to 10 p.m., though they flex with flight schedules.

## Who gets in

Access is for Air India's First and Business Class travelers, along with Platinum and Gold members of its Maharaja Club loyalty program. That makes it most relevant to the premium-cabin and frequent-flyer end of the diaspora — but it also raises the floor for the whole SFO–India experience, since these are the travelers who most often face the longest journeys.

## Part of a bigger transformation

The lounge is one piece of Air India's broader overhaul under Tata. Since privatization, the airline has poured money into new aircraft, refreshed cabins, better service and premium airport experiences, all in service of becoming, as CEO Campbell Wilson likes to put it, "a world-class airline with an Indian heart." Mohit Gandhi, who heads lounge strategy, framed the SFO opening as the next step in turning the carrier into a global airline with an Indian core.

For NRIs, the symbolism is hard to miss. For years, flying the national carrier home meant accepting a thinner ground experience than the Gulf and European competition offered. A signature lounge at SFO — and the promise of more to follow at key gateways — signals that Air India intends to compete for the premium diaspora traveler on experience, not just on the convenience of a nonstop.

The practical takeaway is narrower but real: if you are flying Air India business or first out of San Francisco, or you hold Maharaja Club Gold or Platinum status, the pre-flight wait just got considerably more pleasant. And the choice of SFO as the debut city is a quiet acknowledgment of who fills those premium seats on the route home.
"""
    },
]

inserted = []
for art in articles:
    if not art.get("image_url"):
        print(f"⚠ No image for {art['slug']} — inserting without hero image")
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
        inserted.append(art["headline"])
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

print(f"\n=== Inserted {len(inserted)} articles ===")
for h in inserted:
    print(f"  • {h}")

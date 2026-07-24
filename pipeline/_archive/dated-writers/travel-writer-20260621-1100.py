#!/usr/bin/env python3
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

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

# ---------------- ARTICLE 1: ETIAS ----------------
etias_body = """The cheapest summer most NRI families ever booked to Europe — a long layover in Frankfurt, a few days in Paris on the way to Delhi — is about to come with a new line item. The European Union has confirmed that its long-delayed travel authorization system, ETIAS, will go live in the last quarter of 2026, and the fee has been reset upward to **€20**, nearly triple the €7 originally promised.

For the Indian diaspora, this is not the same story it is for everyone else. An Indian passport holder still needs a full Schengen visa to enter Europe, and ETIAS changes nothing for them. But the diaspora is not one passport. The naturalized American, the British citizen of Indian origin, the Canadian on a fresh blue passport — the people who fly home to India every year and routinely break the journey in Europe — are exactly who ETIAS targets.

## What ETIAS actually is

ETIAS is not a visa. It is a pre-travel authorization, closer to the United States' ESTA or the UK's ETA, required of visa-exempt nationals before they board a flight to any of 30 European countries. You apply online, link it to your passport, and in most cases get approval within minutes. It is valid for up to three years or until the passport expires, and it permits short stays of up to 90 days in any 180-day window. It does not, the EU stresses, guarantee entry — a border guard still makes the final call.

Crucially, ETIAS rides on top of the **Entry/Exit System (EES)**, the EU's biometric border program that became fully operational on 10 April 2026. EES already replaced the old passport stamp with facial images and fingerprints at the Schengen frontier. ETIAS is the second half of that architecture: EES tracks who crosses, ETIAS pre-screens who is allowed to try.

## Why this lands on the diaspora differently

Consider the practical map. An Indian-American family in New Jersey flying United through Frankfurt, or a British-Indian household routing London–Amsterdam–Hyderabad on KLM, will need a valid ETIAS for every traveler on a US, UK, Canadian, or Australian passport — including children, who are exempt from the fee but not from the authorization itself. A green-card holder traveling on an Indian passport, by contrast, still needs the full Schengen visa as before.

That split runs straight through mixed-status families, which describe a large share of the diaspora: a naturalized parent, a spouse still on the Indian passport, kids born American. One household, two completely different pre-departure checklists.

## The scam warning is the real headline

The EU has been blunt about the danger that matters most here. There is exactly **one** official site — europa.eu/etias — and the only legitimate cost is €20. A thicket of copycat sites already use the EU logo, harvest passport and card details, and tack on "service fees." For a community that books heavily through WhatsApp-forwarded links and third-party travel agents, this is the part to internalize now, months before launch.

## What to do before Q4

- **Check every passport in the house.** ETIAS is tied to the specific passport. Renew anything expiring within the next year before you apply, or you will pay twice.
- **Don't apply yet.** The system is not live, and any site taking your money today is a scam. The EU says it will announce the exact start date several months in advance.
- **Budget the buffer.** Most approvals are instant, but the EU warns some take up to 96 hours, and a small share trigger manual review of up to 30 days. For peak-season travel, treat ETIAS like a document, not a formality.
- **Indian passport holders: ignore the noise.** Your Schengen visa requirement is unchanged. ETIAS is not for you — yet.

For families who have spent years optimizing the Europe-stopover route home, none of this is a dealbreaker. €20 every three years is rounding error against a transatlantic fare. But it is one more box to tick, one more scam vector to dodge, and one more place where a single household's passports no longer all travel the same way.

Sources: European Commission Migration and Home Affairs; EEAS official ETIAS information; The Points Guy."""

# ---------------- ARTICLE 2: Vande Bharat Kashmir ----------------
vb_body = """For decades, the Kashmir Valley was the one corner of India you could not reach by train. The mountains were too steep, the gorges too deep, the engineering too daunting. That barrier is gone. A 20-coach Vande Bharat Express is now running between Jammu and Srinagar, crossing the **Chenab Rail Bridge** — the highest railway bridge in the world, arching 359 meters above the river, taller than the Eiffel Tower — and turning a white-knuckle road journey into a four-and-a-half-hour ride in a heated, fully air-conditioned coach.

Railways Minister Ashwini Vaishnaw confirmed the expansion to a 20-coach configuration "amid rising demand," and the service now originates at Jammu Tawi after being extended from its earlier Katra start. For the diaspora, this is one of those infrastructure stories that quietly rewrites a family itinerary.

## What the new line actually does

The train runs on the **Udhampur–Srinagar–Baramulla rail link**, a 272-km project that finally stitches the Kashmir Valley into India's national rail network. It connects Jammu Tawi, Udhampur, SMVD Katra, Reasi, Banihal, and Srinagar, covering the core 267-km stretch in about four hours and 35 minutes, six days a week. The coaches are built for the climate — heating systems rated for sub-zero temperatures and a driver's windscreen with embedded heating elements to defrost in a Himalayan winter.

Two landmarks define the route. The Chenab Bridge is the headline, but the **Banihal Tunnel** is the workhorse, boring through the mountain wall that historically sealed the valley off from rail. Together they do something no road can promise: a reliable, weather-resilient connection that does not shut down with the first heavy snow on the Jammu–Srinagar highway.

## Why this matters to NRIs

Two diaspora itineraries change immediately.

**The Vaishno Devi pilgrimage.** Katra, the base for the Mata Vaishno Devi shrine, is one of the most visited pilgrimage stops for NRI families returning home, especially around school holidays. It now sits on the same modern line as Srinagar, meaning a family can fold a shrine visit and a Valley holiday into one clean rail leg instead of arranging separate cars and drivers.

**Kashmir without the road.** For years the standard advice to relatives flying in from the US or UK was to fly Delhi–Srinagar and never attempt the road in winter. The train offers a third option — scenic, predictable, and far cheaper than a domestic flight — that lets older parents and grandparents reach the Valley in comfort. For multigenerational trips, that reliability is the whole point.

There is also a softer pull. For Kashmiri Pandit families and Valley-origin NRIs who left decades ago, a one-seat train ride from Jammu into Srinagar is an emotionally different homecoming than a flight. The route reconnects them to the land at ground level, through the same gorges and bridges their parents could only cross by road.

## The practical caveats

This is new infrastructure, and it behaves like it. The service runs six days a week (not Tuesdays, when the rake is serviced), and seats on a single daily train into a high-demand destination sell out fast in peak season — book the moment the window opens. Maximum operating speeds are still being confirmed after the commercial run, so journey times may tighten further. And the Valley remains a region where security conditions can shift; NRIs should check the latest Indian government and home-country advisories before locking plans.

None of that dims the larger shift. The Kashmir Valley, for the first time in history, is on the map of places you can reach from the rest of India by rail — and the diaspora's summer-and-pilgrimage circuit just gained a route that did not exist a year ago.

Sources: The Indian Eye; Wikipedia (Jammu Tawi–Srinagar Vande Bharat Express); Travel And Tour World."""

# ---------------- ARTICLE 3: IndiGo Europe push ----------------
indigo_body = """India's largest airline built its empire on short hops. Now IndiGo is flying single-aisle jets to the edge of Europe and wet-leasing widebodies to go further, and this autumn the strategy reaches a milestone that matters to the diaspora: nonstop service from Mumbai to **Copenhagen** launches 8 October, and **London Heathrow** follows on 26 October. Behind those routes sits a quieter prize — a partnership that lets IndiGo sell onward flights into the United States.

## The fast build-out

IndiGo's long-haul map has filled in at a pace few carriers match. It has already launched its first European destinations — Manchester and Amsterdam — using Boeing 787-9s damp-leased from Norse Atlantic Airways, and added Athens as the debut route for its new **Airbus A321XLR** narrowbodies. Copenhagen, launching 8 October with three weekly flights from Mumbai, becomes IndiGo's debut in Scandinavia and its 44th international destination. CEO Pieter Elbers frames it as a Nordic gateway; the airline's stated goal is to fly 40% of its capacity internationally by 2030, up from roughly 30% today.

The aircraft strategy is the real story. The A321XLR — a single-aisle jet capable of nearly 8,700 km — lets IndiGo open thin long-haul markets that never justified a widebody, while six leased 787s carry the heavier routes until IndiGo's own 30 A350s and 70 A321XLRs start arriving from 2026–27.

## The codeshare that reaches America

Here is the part the diaspora should read closely. IndiGo has deepened a partnership with **Delta, Air France-KLM, and Virgin Atlantic** that, once regulatory work clears, will let IndiGo sell — under its own 6E codes — onward connections including Delta and KLM flights from Amsterdam to the US and Canada, and Virgin Atlantic flights from Manchester to the US.

Translated: a traveler in a Tier-2 Indian city IndiGo already serves could, in principle, book a single 6E itinerary from their hometown through Amsterdam or Manchester and onward to a US gateway. For the NRI who has spent years stitching together a domestic IndiGo ticket plus a separate international one — and eating the risk of a missed connection and lost bag in between — a through-fare on one airline code is a genuine convenience.

## Why it matters to the diaspora

IndiGo's domestic network reaches more than 90 Indian cities, far beyond the dozen or so that Air India and the Gulf carriers serve nonstop from abroad. The bottleneck for diaspora travel has never been the metro airports; it is the last leg to Indore, Coimbatore, Lucknow, or Madurai. By plugging its vast domestic web into European hubs and, through partners, into North America, IndiGo is positioning itself to carry NRIs closer to their actual hometowns on one ticket.

The catch is timing and scope. The transatlantic codeshares depend on commercial contracts and regulatory approvals still being finalized, and Delta's own direct US–India service — last flown briefly in early 2020 — remains a "near future" promise rather than a schedule. IndiGo's own US flights wait on widebody deliveries that don't begin until 2027.

## What to watch

- **Copenhagen (Oct 8) and Heathrow (Oct 26)** are the concrete near-term additions from Mumbai.
- **Onward US/Canada connections** via Amsterdam and Manchester are coming but not yet bookable as single 6E fares — watch for the regulatory green light.
- **A321XLR routes** will keep opening secondary European cities; expect more Greek and Central European points.

For now, IndiGo remains a feeder and a European specialist, not a US carrier. But the architecture is being laid for the day an NRI books one airline from a small Indian city all the way to a North American doorstep — and that day is visibly closer than it was a year ago.

Sources: Aviation Week; Delta News Hub; Simple Flying; Travel Weekly."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Europe Just Set a Price on Its New Travel Permit — and It Hits the Diaspora's Cheapest Route Home",
        "subheadline": "ETIAS launches in late 2026 at €20, nearly triple the original fee. It changes nothing for Indian passports — but everything for the naturalized NRIs who break the trip home in Europe.",
        "slug": make_slug("etias-europe-travel-authorization-2026-fee-nri-naturalized-passport"),
        "category": "travel",
        "vertical": "immigration",
        "diaspora_angle": "ETIAS will require US, UK, Canadian, and Australian passport holders of Indian origin to get pre-travel authorization for Europe — splitting mixed-status NRI families' pre-departure checklists in two.",
        "tags": ["travel", "visa", "europe", "etias", "schengen"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "European Commission — Migration and Home Affairs", "url": "https://home-affairs.ec.europa.eu/policies/schengen-borders-and-visa/smart-borders/european-travel-information-and-authorisation-system-etias_en"},
            {"name": "EEAS — Information on ETIAS", "url": "https://www.eeas.europa.eu/"},
            {"name": "The Points Guy — ETIAS launch and fee", "url": "https://thepointsguy.com/"}
        ]),
        "score_total": 80,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/c/cd/Border_control_at_Copenhagen_Airport.jpg",
        "image_caption": "Border control hall at Copenhagen Airport, a Schengen entry point where ETIAS authorization will be checked from late 2026.",
        "image_attribution": "Wikimedia Commons",
        "body": etias_body,
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "You Can Finally Take a Train Into the Kashmir Valley — and It Crosses the World's Highest Rail Bridge",
        "subheadline": "A 20-coach Vande Bharat now runs Jammu to Srinagar over the Chenab Bridge, turning a white-knuckle mountain road into a 4.5-hour air-conditioned ride — and rewriting the diaspora's pilgrimage-and-Valley itinerary.",
        "slug": make_slug("vande-bharat-jammu-srinagar-kashmir-chenab-bridge-nri-pilgrimage"),
        "category": "travel",
        "vertical": "tourism",
        "diaspora_angle": "For the first time NRI families can reach Katra's Vaishno Devi shrine and the Kashmir Valley on one modern rail line, giving older parents a reliable, all-weather alternative to the Jammu–Srinagar highway.",
        "tags": ["travel", "india", "kashmir", "vande-bharat", "railways"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Indian Eye — 20-coach Vande Bharat Jammu-Srinagar", "url": "https://theindianeye.com/"},
            {"name": "Wikipedia — Jammu Tawi–Srinagar Vande Bharat Express", "url": "https://en.wikipedia.org/wiki/Jammu_Tawi%E2%80%93Srinagar_Vande_Bharat_Express"},
            {"name": "Travel And Tour World — Vande Bharat North India routes", "url": "https://www.travelandtourworld.com/"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/3/34/Chenab_Rail_Bridge%2C_Reasi_district%2C_Jammu_and_Kashmir%2C_India.jpg",
        "image_caption": "The Chenab Rail Bridge in Reasi district, Jammu and Kashmir — the world's highest railway bridge, carrying the new Vande Bharat into the Kashmir Valley.",
        "image_attribution": "Wikimedia Commons",
        "body": vb_body,
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "IndiGo Is Pushing Into Europe on Single-Aisle Jets — and Quietly Building a Path to America",
        "subheadline": "Mumbai–Copenhagen starts October 8 and Heathrow follows October 26, but the real prize for NRIs is a Delta and KLM partnership that will let IndiGo sell onward flights to the US on one ticket.",
        "slug": make_slug("indigo-europe-expansion-copenhagen-heathrow-delta-codeshare-nri-us"),
        "category": "travel",
        "vertical": "aviation",
        "diaspora_angle": "IndiGo's plan to plug its 90-plus-city Indian network into European hubs and, via Delta and KLM, onward to North America could finally let NRIs book a single ticket from a Tier-2 hometown to a US gateway.",
        "tags": ["travel", "airlines", "indigo", "europe", "codeshare"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Aviation Week — IndiGo Copenhagen and European expansion", "url": "https://aviationweek.com/"},
            {"name": "Delta News Hub — IndiGo, Delta, Air France-KLM, Virgin Atlantic partnership", "url": "https://news.delta.com/"},
            {"name": "Simple Flying — IndiGo A321XLR routes", "url": "https://simpleflying.com/"},
            {"name": "Travel Weekly — IndiGo first US codesharing", "url": "https://www.travelweekly.com/"}
        ]),
        "score_total": 76,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fa/IndiGo_Airbus_A321neo_VT-IUD_Abu_Dhabi%2C_2019_%2801%29.jpg/1280px-IndiGo_Airbus_A321neo_VT-IUD_Abu_Dhabi%2C_2019_%2801%29.jpg",
        "image_caption": "An IndiGo Airbus A321neo — the single-aisle jet family the airline is using to open new long-haul routes into Europe.",
        "image_attribution": "Wikimedia Commons",
        "body": indigo_body,
    },
]

for art in articles:
    wc = len(art["body"].split())
    print(f"… {art['slug']}  ({wc} words)")
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

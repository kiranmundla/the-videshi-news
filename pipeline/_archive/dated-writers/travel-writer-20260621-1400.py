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

NPS_BODY = """For the diaspora, the great American road trip is a rite of passage — the summer when relatives fly in from Hyderabad or Ahmedabad, pile into a rented SUV, and finally see Yosemite's granite walls or the Grand Canyon at sunrise. Starting this year, the price of that trip depends on a question the family may never have had to ask before: who in the car is a U.S. resident, and who is a visitor.

## What changed

Under an executive order signed in 2025 and rolled out from **January 1, 2026**, the National Park Service created a two-tier pricing system that, for the first time, asks for proof of residency to access America's public lands.

The America the Beautiful annual pass — the $80 card that covers entry to every national park for a full vehicle — now costs **$80 for U.S. residents and $250 for nonresidents**. On top of that, nonresidents aged 16 and up who don't hold an annual pass must pay a **$100-per-person surcharge** to enter 11 of the most-visited parks, including Yosemite, Sequoia, Kings Canyon, and the Grand Canyon, *in addition* to the standard entrance fee.

The fee-free days changed too. The 2026 calendar dropped Juneteenth and Martin Luther King Jr. Day, replacing them with what the Interior Department calls "patriotic" dates — Flag Day (June 14), Independence Day weekend, the park service's 110th birthday on August 25, Constitution Day, and Veterans Day. Crucially, those free days now apply **only to U.S. citizens and permanent residents**; nonresidents pay full freight regardless.

## Why this matters to NRIs

Here is where the diaspora needs to read the fine print, because the line between "resident" and "nonresident" runs straight through a typical Indian American family.

Green card holders and naturalized citizens are residents. They pay $80 for the annual pass, qualify for the free days, and face no surcharge. The Park Service verifies status with a photo ID — a passport, state ID, or green card — shown at the point of use.

The people most affected are **visiting parents and relatives on B-2 tourist visas**. A mother and father visiting from India for the summer are nonresidents in the eyes of the new rule. If the family drives them into Yosemite, each adult visitor can owe the $100 surcharge on top of the gate fee — turning a single park visit for two grandparents into a $200-plus line item that did not exist a year ago.

The status of long-term visa holders is the genuinely murky part. The Park Service ties eligibility to residency rather than citizenship, which suggests H-1B and other long-term visa holders who actually live in the United States should qualify for the $80 resident rate. But the agency's guidance leans on showing a green card or state ID, so an H-1B family is wise to carry a driver's license and be ready to make the case at the kiosk.

## The math for a multi-generational trip

Run the numbers for a common scenario: a green-card couple, their two kids, and two visiting parents on tourist visas, planning to see three of the marquee parks.

The residents are covered by one $80 pass. The two visiting grandparents, as nonresidents, are the cost driver — either a $250 nonresident annual pass between them if they'll see several surcharge parks, or the $100-per-person surcharge at each of the 11 flagship parks. For a trip hitting Yosemite, Sequoia, and the Grand Canyon, the nonresident annual pass at $250 is the cheaper route the moment two surcharge parks are on the itinerary.

The practical move: decide before you go whether your visiting relatives will see two or more of the 11 surcharge parks. If yes, buy them the $250 nonresident annual pass up front. If it's a single park, pay the per-person surcharge and skip the pass.

## What's next

The fees are not settled politics. A group of senators led by California's Alex Padilla has demanded the administration pause the rollout, arguing it was implemented without proper public notice and will deter international visitors; a separate inquiry is probing whether park entrance-fee revenue is being diverted to unrelated projects in Washington rather than reinvested in the parks. There is even a proposal to restore Juneteenth as a fee-free day.

None of that changes what a diaspora family pays at the gate this summer. Passes bought before January 1, 2026 are honored on their original terms, so a nonresident relative holding a 2025 annual pass is covered for its full 12 months. For everyone else planning the classic summer loop, the new rule rewards one habit: know each traveler's status before you reach the entrance booth, and buy the right pass in advance."""

SAUDI_BODY = """The flight home to India from the U.S. is a punishing thing — sixteen hours or more in the air, usually broken by a dead layover in a Gulf hub where you wander the duty-free, doze at the gate, and wait. Saudi Arabia is now offering the diaspora a way to turn that wasted layover into something else entirely: up to four days in the Kingdom, on a free visa, with the option to perform Umrah along the way.

## What's on offer

Saudi Arabia's Ministry of Foreign Affairs, working with national carriers **Saudia and Flynas**, runs a Stopover Visa Program that issues a free electronic visa to passengers transiting through Saudi airports. The visa permits a single entry for **up to 96 hours** — four days — and is valid for 90 days from issue, so you can apply well ahead of travel.

What you can do on it is the striking part. The stopover visa lets you leave the airport, travel domestically within the country, attend tourism events, visit the Prophet's Mosque in Medina, and **perform Umrah** — the pilgrimage to Mecca that many in the diaspora plan entire separate trips around. The Ministry has even published ready-made 24-, 48-, 72-, and 96-hour itineraries, from Jeddah's restored Al-Balad old town to the UNESCO-listed At-Turaif district in Diriyah.

The visa itself is free. You'll pay a small mandatory charge for administrative processing and health insurance — roughly SAR 40–95, or about $10–25 — calculated automatically during booking, with the system assigning you an insurer. The e-visa is typically emailed within four hours of approval and can be saved to a phone wallet.

## How it works for U.S.-based travelers

The mechanics are simple, with one firm rule: the visa is only issued **while you book your ticket** on Saudia or Flynas, not separately afterward.

The United States is on the eligible-origin list, alongside Canada, the UK, and much of Europe. You book a Saudia or Flynas itinerary from the U.S. to India that routes through a Saudi airport, select the stopover option on the booking page, choose your stay length up to 96 hours, and the application passes automatically to the national visa platform. You need a passport with at least six months' validity and a confirmed onward flight — Saudi Arabia cannot be your final destination.

A few limits matter for NRI families. The stopover visa is **not extendable** — you must exit within 96 hours. Children under 18 cannot hold their own stopover visa but can be included as companions on a parent's application. And it is not issued to anyone who already holds a valid Saudi visa or qualifies for visa-on-arrival. If you want to perform Umrah, you register separately through the official **Nusuk** platform; the stopover visa permits Umrah but cannot be used for Hajj.

## Why this matters to NRIs

For the Indian American community, this lands at the intersection of two things the diaspora already does constantly: fly home, and plan pilgrimages.

A huge share of U.S.–India traffic already connects through the Gulf, and Saudi Arabia has been muscling into that market as it chases a target of 100 million annual visits under its Vision 2030 tourism push — the country drew a record number of visitors in 2025. For a Muslim NRI family, the proposition is unusually efficient: instead of mounting a dedicated, expensive Umrah trip, you fold the pilgrimage into a journey you were already taking, on a visa that costs nothing but the insurance fee.

Even for non-pilgrims, the appeal is real. A 72-hour stop to show the kids Diriyah or the Red Sea coast of Jeddah breaks an exhausting long-haul into two manageable legs — and arguably beats a sleepless night on an airport bench in a third country.

## What's next

The program is live now and bookable directly through both carriers' websites. The thing to plan around is timing and logistics: build in real buffer for the drive between Jeddah and Mecca or Medina, book accommodation in advance since some cities expect proof of where you're staying, and coordinate any Umrah slot through Nusuk before you fly. Treat the 96 hours as a hard ceiling — the visa won't be extended, and the clock starts the moment you land."""

AIRPORT_BODY = """Ask anyone in the diaspora to name a beautiful airport and they'll reach for Singapore's Changi or one of the Gulf's glass cathedrals. This year, for the first time, the honest answer might be two airports in India — and one of them isn't even fully open yet.

## What happened

On June 18, **Prix Versailles**, the international architecture and design award supported by UNESCO, unveiled its list of the seven most beautiful airports of 2026. Two Indian airports made the cut: **Terminal 1 of Navi Mumbai International Airport** and **Terminal 2 of Lokpriya Gopinath Bordoloi International Airport in Guwahati**.

They share the list with some serious company — Terminal 3 of Guangzhou Baiyun in China, Terminal 3 of Frankfurt, Cambodia's new Techo International in Phnom Penh, and two U.S. hubs, Terminal 1 of San Diego International and a freshly rebuilt Pittsburgh International. The jury judged the airports not only on architecture but on innovation, passenger experience, environmental sustainability, and how well each reflects local cultural identity.

Prix Versailles described the seven winners as projects that "illustrate how airports are now turning away from the old standards in order to offer the world a richer, more harmonious point of view." For India to place two of the seven — the most of any country this year — is a genuine statement about where the country's infrastructure ambitions have arrived.

## What makes them special

The two Indian winners could hardly be more different, and that's the point.

**Navi Mumbai International Airport** draws its design from the lotus, the enduring symbol woven through Indian art and culture. The terminal is built around extensive green spaces and floods of natural light, presented as a contemporary expression of Indian architecture rather than a pastiche of it. It's also the surprise of the list: the airport only began domestic operations in December 2025 and is still ramping up — international passenger flights, starting with Air India Express to Abu Dhabi, are expected to begin around July 15, 2026.

**Guwahati's Terminal 2** is the cultural counterpoint, a love letter to India's northeast. Its defining feature is a bamboo-inspired interior — a nod to the material that runs through the region's craft and architecture — complemented by local art, folklore, and traditional craftsmanship. For a part of India that rarely features in the diaspora's mental map, it's a striking debut on a global stage.

## Why this matters to NRIs

For NRIs, airports are not abstractions. They are where the trip home begins and ends — the first lungful of Indian air, the place where parents wait at arrivals, the last hug before the long flight back. The quality of that experience shapes the whole journey, and for years the diaspora's honest verdict on Indian airports was patience rather than pride.

That has been shifting fast, and this list is the external validation. Navi Mumbai matters most directly: it gives the Mumbai metro a genuine second gateway, which over time should mean shorter immigration lines, less congestion at the overstretched Chhatrapati Shivaji Maharaj International, and more route choice for families flying into Maharashtra. A diaspora traveler routing through it in the next year is walking through an award-winning terminal at the very start of its life.

Guwahati's recognition carries a different weight. For NRIs with roots in Assam and the northeast — a smaller but real slice of the diaspora — a world-class gateway closer to home is the difference between flying into the region with dignity and treating it as an afterthought tacked onto a Delhi or Kolkata trip.

## What's next

The Prix Versailles list refreshes every year and focuses on recently completed projects, so neither airport is guaranteed a return — the recognition is a snapshot of this moment in Indian aviation, not a standing trophy. The more meaningful timeline is operational: watch for Navi Mumbai's international flights to come online from mid-July, which is when the diaspora will actually start passing through the terminal the world just called one of its most beautiful. For once, the airport at the start of the trip home is worth slowing down to look at."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "America's National Parks Just Got a Two-Tier Price Tag — and It Splits Right Through an NRI Family",
        "subheadline": "From January 1, the U.S. charges nonresidents $250 for the annual pass and a $100-per-person surcharge at 11 flagship parks. Here's who in your car pays what — and why visiting parents are the catch.",
        "slug": make_slug("us-national-parks-nonresident-fee-2026-nri-visiting-parents-surcharge"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "The new resident/nonresident split runs straight through a typical Indian American family: green-card holders and citizens pay $80, but parents and relatives visiting on B-2 tourist visas are nonresidents who can owe a $100-per-person surcharge at Yosemite, Sequoia, Kings Canyon and the Grand Canyon — turning a multi-generational road trip into a budgeting question NRIs never had to ask before.",
        "tags": ["travel", "national-parks", "fees", "visiting-parents", "nri"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "U.S. Department of the Interior — Modernized, More Affordable National Park Access", "url": "https://www.doi.gov/"},
            {"name": "U.S. National Park Service — Nonresident Fees", "url": "https://www.nps.gov/planyourvisit/passes.htm"},
            {"name": "USA Today — Why national parks aren't free on Juneteenth", "url": "https://www.usatoday.com/"},
            {"name": "Senator Alex Padilla — Demand to pause nonresident park fees", "url": "https://www.padilla.senate.gov/"}
        ]),
        "score_total": 80,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/13/Tunnel_View%2C_Yosemite_Valley%2C_Yosemite_NP_-_Diliff.jpg/1280px-Tunnel_View%2C_Yosemite_Valley%2C_Yosemite_NP_-_Diliff.jpg",
        "image_caption": "Tunnel View over Yosemite Valley — Yosemite is one of 11 flagship U.S. national parks now carrying a $100-per-person surcharge for nonresidents",
        "image_attribution": "Wikimedia Commons / Diliff",
        "is_editorial": False,
        "body": NPS_BODY
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Saudi Arabia Will Now Give You 96 Free Hours on the Way Home to India — Umrah Included",
        "subheadline": "A free stopover e-visa from Saudia and Flynas lets U.S.-based travelers break the long-haul to India with up to four days in the Kingdom — and perform Umrah without a separate trip.",
        "slug": make_slug("saudi-96-hour-free-stopover-visa-nri-umrah-layover-hack"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "A free 96-hour stopover visa, issued while booking Saudia or Flynas tickets from the U.S., lets NRI families turn a dead Gulf layover into up to four days in Saudi Arabia — and, for Muslim NRIs, fold Umrah into a trip they were already taking instead of mounting a separate, expensive pilgrimage.",
        "tags": ["travel", "visa", "saudi-arabia", "umrah", "stopover", "nri"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Fragomen — Saudi Arabia Stopover Visa Program for transiting passengers", "url": "https://www.fragomen.com/"},
            {"name": "Saudia — Saudi Transit Visa Guide & Eligibility", "url": "https://www.saudia.com/"},
            {"name": "Flynas — Stopover Visa Guide", "url": "https://www.flynas.com/"},
            {"name": "Wego Travel Blog — Saudi transit visa, fees and eligibility", "url": "https://blog.wego.com/"}
        ]),
        "score_total": 78,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/49/At-Turaif_District_of_Diriyah%2C_Saudi_Arabia.jpg/1280px-At-Turaif_District_of_Diriyah%2C_Saudi_Arabia.jpg",
        "image_caption": "The UNESCO-listed At-Turaif district in Diriyah, one of the sites Saudi Arabia highlights on its 96-hour stopover itineraries",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": SAUDI_BODY
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Two Indian Airports Just Made the World's Most Beautiful List — and One Isn't Even Fully Open",
        "subheadline": "Prix Versailles named Navi Mumbai and Guwahati among the seven most beautiful airports of 2026. For the diaspora, the gateway home is finally worth slowing down to look at.",
        "slug": make_slug("navi-mumbai-guwahati-worlds-most-beautiful-airports-2026-prix-versailles-nri"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "Airports are where the diaspora's trip home begins and ends; Prix Versailles naming Navi Mumbai and Guwahati among the world's seven most beautiful airports of 2026 is external validation of India's infrastructure leap — and Navi Mumbai's looming July international launch gives Maharashtra-bound NRIs an award-winning second gateway with shorter lines.",
        "tags": ["travel", "airports", "navi-mumbai", "guwahati", "india", "nri"],
        "urgency": "low",
        "sources": json.dumps([
            {"name": "New York Post — World's most beautiful airports revealed", "url": "https://nypost.com/"},
            {"name": "Travel And Tour World — India dominates World's Most Beautiful Airports 2026", "url": "https://www.travelandtourworld.com/"},
            {"name": "The Sun — World's most beautiful airports revealed", "url": "https://www.thesun.co.uk/"},
            {"name": "Outlook Business — Air India Express to launch international flights from Navi Mumbai", "url": "https://www.outlookbusiness.com/"}
        ]),
        "score_total": 72,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/62/Navi_Mumbai_Airport_%2896252%29.jpg/1280px-Navi_Mumbai_Airport_%2896252%29.jpg",
        "image_caption": "Navi Mumbai International Airport, whose lotus-inspired Terminal 1 was named among the world's seven most beautiful airports of 2026 by Prix Versailles",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": AIRPORT_BODY
    }
]

for art in articles:
    wc = len(art["body"].split())
    print(f"  [{art['slug']}] ~{wc} words")
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

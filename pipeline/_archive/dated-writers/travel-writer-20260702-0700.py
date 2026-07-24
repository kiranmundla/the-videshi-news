#!/usr/bin/env python3
"""Travel writer — 2026-07-02 batch. Three articles."""

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
    # ── Article 1: Air India 787-9 Mumbai-London ──────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "Air India's Brand-New 787-9 Lands on Mumbai–London — and It Finally Feels Like a Global Airline",
        "subheadline": "The carrier's first factory-fresh Dreamliner brings private business suites, premium economy, and 4K screens to its busiest diaspora corridor.",
        "slug": make_slug("air-india-787-9-mumbai-london-dreamliner-premium-economy-nri"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "The UK is home to 1.6 million people of Indian origin — and Air India's 57 weekly nonstop flights between five Indian cities and three British airports are the single largest air bridge between the two countries. This cabin upgrade directly affects every NRI booking a trip home.",
        "tags": ["travel", "airlines", "air-india", "london", "boeing-787", "premium-economy"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Outlook Traveller", "url": "https://www.outlooktraveller.com/News/air-indias-new-boeing-787-9-now-flies-mumbai-london-heathrow-heres-whats-new"},
            {"name": "Aviation A2Z", "url": "https://www.aviationa2z.com/index.php/2026/07/02/air-india-deploys-new-787-to-most-connected-airport-in-the-world/"},
            {"name": "Business Traveller", "url": "https://www.businesstraveller.com/airlines/air-india-debuts-redesigned-cabins-on-new-boeing-787-9/"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/57/VT-ANS_Boeing_787-9_Dreamliner_Air_India_LHR_191018.jpg/1280px-VT-ANS_Boeing_787-9_Dreamliner_Air_India_LHR_191018.jpg",
        "image_caption": "An Air India Boeing 787-9 Dreamliner on the tarmac at London Heathrow",
        "image_attribution": "Wikimedia Commons",
        "body": """For years, flying Air India long-haul meant accepting a trade-off: reasonable fares, decent frequency, questionable hardware. That bargain just shifted. On July 1, Air India deployed its first factory-fresh Boeing 787-9 Dreamliner on the Mumbai–London Heathrow route, introducing cabins that were designed on Boeing's assembly line rather than retrofitted onto ageing airframes.

Flights AI131 and AI130 now operate with a 296-seat, three-class aircraft that brings private business suites, a dedicated premium economy cabin, and 4K entertainment screens to one of the airline's most competitive corridors. The second daily Mumbai–Heathrow service continues with an upgraded Boeing 777-300ER that retains first class, giving passengers a choice between two distinct premium products on the same route.

## What the new cabins actually look like

Business class is configured 1-2-1 with the Elevate Ascent suite — fully flat 79-inch beds, sliding privacy doors, wireless charging, and a 17-inch 4K QLED HDR touchscreen. The seats have direct aisle access on every row, so the window-seat climb-over is gone. Storage is generous: a softly lit cubby with a vanity mirror and a feature lamp using Air India's signature *jaali* lattice motif, which runs through the entire cabin as a design thread.

Premium economy — the real headline for most travellers — seats 28 passengers in a 2-3-2 layout with 38 inches of pitch, adjustable calf and leg rests, and 13.3-inch 4K screens. For anyone who finds economy unbearable on a ten-hour red-eye but cannot justify business fares, this is the cabin that changes the arithmetic. It is the first time premium economy has been available on the Mumbai–London route.

Economy gets a quieter but meaningful refresh: RECARO seats in a 3-3-3 layout with 32 inches of pitch, 11.6-inch 4K touchscreens, and universal charging ports. Every seat on the aircraft — regardless of class — connects to the Thales AVANT Up entertainment platform with Bluetooth pairing, so passengers can use their own wireless headphones across more than 3,000 hours of content.

## Why it matters for NRIs

The UK remains Air India's largest overseas market by frequency. The airline operates 57 weekly nonstop flights connecting Delhi, Mumbai, Bengaluru, Ahmedabad, and Amritsar with London Heathrow, London Gatwick, and Birmingham. For the 1.6 million-strong British Indian community — and for US-based NRIs routing through London — the quality of these flights has long been a sore point relative to Emirates, Qatar Airways, and British Airways.

This deployment is part of a broader fleet overhaul. From August, Bengaluru–London Heathrow will also receive retrofitted 787-8 aircraft with the same three-cabin layout, including premium economy. Delhi–Melbourne is getting upgraded 777-300ERs with first class. And Delhi–Toronto will see the new 787-9 product on most of its ten weekly services by summer's end.

Air India CEO Campbell Wilson has said the new cabin interiors will become "the standard across our entire Boeing 787 fleet." If that promise holds, the airline's long-haul product will look materially different within 12 months.

## The practical takeaway

NRIs booking Mumbai–London should look for AI131/AI130 to get the new aircraft. The 777-300ER on the second daily service is upgraded but does not have premium economy. For families splitting costs — one parent in premium economy, kids in economy — the 787-9 service is the one to book. Fares on the premium economy cabin have not been publicly benchmarked yet, but industry watchers expect them to sit roughly 40-60% above economy and well below business, consistent with other carriers on the route.

Air India's transformation has been slow and uneven, but the hardware arriving now — factory-built, not patched together — is the clearest signal yet that the Tata-owned carrier is serious about competing on product, not just price."""
    },

    # ── Article 2: Air India Express eyes Georgia ─────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "Air India Express Eyes Georgia — and NRIs with a US Visa Can Get In Without One",
        "subheadline": "The Tata-owned low-cost carrier is evaluating nonstop flights to Tbilisi for winter 2026, marking its first foray into Europe and opening a corridor to one of the fastest-growing Indian tourist destinations.",
        "slug": make_slug("air-india-express-georgia-tbilisi-europe-nri-us-visa"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "NRIs holding valid US, Schengen, or UK visas can enter Georgia visa-free for up to 90 days. A direct flight from India would make Tbilisi a cheap, easy add-on to any India trip — or a stand-alone long-weekend destination routed through the Gulf.",
        "tags": ["travel", "airlines", "air-india-express", "georgia", "tbilisi", "visa-free", "europe"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/economy/logistics/air-india-express-eyes-europe-expansion-plans-georgia-entry/article69749108.ece"},
            {"name": "Aviation A2Z", "url": "https://www.aviationa2z.com/index.php/2026/07/01/air-india-express-plans-to-launch-flights-to-this-new-market/"},
            {"name": "Hopping Tales (Georgia visa guide)", "url": "https://hoppingtales.in/georgia-visa-for-indians/"}
        ]),
        "score_total": 74,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/45/View_of_Tbilisi_from_Tabori_Church_2023-10-08-2.jpg/1280px-View_of_Tbilisi_from_Tabori_Church_2023-10-08-2.jpg",
        "image_caption": "Tbilisi's Old Town and the Mtkvari river valley seen from Tabori Church",
        "image_attribution": "Wikimedia Commons",
        "body": """Air India Express is preparing to do something its parent airline never has: fly to Europe. The Tata Group-owned low-cost carrier is actively evaluating the launch of nonstop flights to Tbilisi, Georgia, for the winter 2026 schedule, according to industry sources cited by *The Hindu BusinessLine*. If confirmed, it would mark the airline's first entry into the European continent and extend its network well beyond the Gulf and Southeast Asian routes it has dominated for two decades.

The airline has not officially confirmed the plan, but the signal is clear enough. Air India Express has restored nearly 80 percent of its West Asia operations and currently serves 13 Gulf destinations. Southeast Asia is getting attention too — Bangkok and Phuket flights are already running, and Malaysia expansion is under review. Georgia represents a logical next step: a short-to-medium-haul market with fast-growing Indian demand and limited competition.

## Why Georgia, and why now

Indian arrivals in Georgia surged roughly 40 percent in the first half of 2025, making Indians one of the fastest-growing visitor segments to the country. The reasons are not hard to find. Tbilisi is cheap — a good dinner for two costs under $20, a night in a boutique Old Town hotel runs $40-60, and a bottle of excellent local wine is $5. The Caucasus mountains offer alpine scenery without the Alpine price tag. And the country has a functioning e-visa system that costs around $36 and processes in five to seven days.

But the real draw for NRIs is even simpler: if you hold a valid US, Schengen, or UK visa or residence permit, you do not need a Georgian visa at all. You can enter for up to 90 days, no application required. For the roughly 4.5 million Indian-born residents of the United States, a valid B1/B2 stamp is enough to walk through Tbilisi immigration.

That makes Georgia one of the most accessible European destinations for Indian passport holders — a category where options remain frustratingly limited. The Schengen zone requires a visa. The UK requires a visa. Georgia asks for nothing more than the visa you already have.

## What a direct flight would change

Currently, Indians reach Tbilisi through Gulf hubs — primarily via Dubai (flydubai, Emirates), Abu Dhabi (Air Arabia), or Doha (Qatar Airways). Flight times from Delhi run eight to nine hours with a connection, and fares hover around $260-850 depending on season and advance purchase. A nonstop from a major Indian city could cut travel time to roughly five hours and, on a low-cost carrier, potentially push fares well below $300 round-trip.

Air India Express has traditionally operated with Boeing 737-800 and 737 MAX aircraft, which have the range to cover Delhi–Tbilisi (approximately 3,500 km) comfortably. The airline's cost structure — no-frills service, tight seat pitch, aggressive pricing — would position it as the budget option against Gulf carriers that route through their hubs.

For NRIs, a direct India–Georgia flight opens another possibility: tacking on Tbilisi as a side trip during an India visit. A three- or four-day detour to the Caucasus during a two-week trip home becomes trivially easy if there is a nonstop from Delhi or Mumbai.

## The broader picture

Air India Express is also preparing to launch at least five new domestic stations in 2026, part of a push to build one of India's largest short-haul international networks. The Georgia evaluation fits a broader strategy of targeting underserved "visiting friends and relatives" markets and leisure destinations where established carriers have not built dense capacity.

The move also reflects a generational shift in Indian travel preferences. A decade ago, NRI holiday planning defaulted to Thailand, Bali, or Dubai. Today, social media has pushed destinations like Georgia, Azerbaijan, Armenia, and Central Asia into the mainstream Indian travel conversation. Georgia's Old Town cobblestones, sulphur baths, and Kakheti wine country have become staples of Indian travel Instagram.

If Air India Express confirms the route for winter 2026, Tbilisi could join the short list of European cities accessible from India without a connecting flight, a Schengen appointment, or a premium fare. For NRIs already holding a US visa, it is effectively a walk-on destination — and that combination of access, affordability, and scenery is hard to beat."""
    },

    # ── Article 3: Airport lounge access changes July 2026 ───────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "India's Airport Lounge System Just Got Overhauled — Here's What NRIs Need to Know Before Flying Home",
        "subheadline": "New spend thresholds, new apps, and a fragmented access system mean the days of flashing a credit card at the lounge door are over.",
        "slug": make_slug("india-airport-lounge-access-overhaul-hdfc-nri-guide"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "NRIs flying through Indian airports multiple times a year rely on credit card lounge access to make long layovers bearable. The new rules — effective July 1, 2026 — change the game, especially for those whose Indian credit cards see limited local spending between trips.",
        "tags": ["travel", "airport", "lounge", "credit-cards", "hdfc", "india-airports", "nri-guide"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Outlook Money", "url": "https://www.outlookmoney.com/credit-cards/airport-lounge-access-gets-harder-to-unlock-for-indian-credit-card-users"},
            {"name": "Bajaj Finserv Markets", "url": "https://www.bajajfinservmarkets.in/credit-card/articles/top-lounge-access-credit-cards-in-india.html"},
            {"name": "HDFC Bank", "url": "https://www.hdfcbank.com/personal/pay/cards/credit-cards/airport-lounge-access"}
        ]),
        "score_total": 72,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/14212023/pexels-photo-14212023.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
        "image_caption": "A modern airport lounge interior with seating and natural light",
        "image_attribution": "Pexels",
        "body": """If you have been walking into Indian airport lounges by tapping your credit card at the desk, that era is ending. A wave of changes that took effect on July 1, 2026 — led by HDFC Bank, India's largest credit card issuer — has added spending requirements, new apps, and operator-specific entry systems that make lounge access meaningfully harder to unlock. For NRIs who keep an Indian credit card partly for the lounge perks during annual trips home, the new rules demand attention.

## What changed on July 1

The headline change comes from HDFC Bank, which controls roughly a third of India's credit card market. Starting July 1, Regalia Gold cardholders must spend at least ₹60,000 (approximately $710) on their card in the previous quarter to receive three complimentary domestic airport lounge visits in the current quarter. If you did not hit that threshold between April and June, your card will not get you into a lounge between July and September — regardless of the annual fee you pay.

HDFC Diners Club Privilege cards face similar spend-based conditions, while HDFC BizPower users are now capped at two visits per quarter. The six international lounge visits per year through Priority Pass remain unaffected for Regalia Gold holders, but the domestic benefit — the one NRIs actually use during layovers in Delhi, Mumbai, or Bengaluru — is now conditional.

HDFC is not alone. Several Indian banks have been tightening lounge access over the past year, shifting from unlimited or generous allotments to spend-linked entitlements. The trend is driven by economics: lounge operators charge banks ₹1,000-2,000 per visit, and with credit card adoption surging, the cost of "free" lounge access has ballooned.

## The new app maze

The access mechanism has also changed. India's major airport operators have moved away from DreamFolks, the third-party platform that used to provide a single QR-code-based lounge entry system. In its place, each airport operator now runs its own access channel:

**Adani Airports** (Ahmedabad, Lucknow, Jaipur, Mangalore, Guwahati, Thiruvananthapuram, and others): download the Adani One app, register your credit card, and show the in-app QR code at the lounge.

**GMR Airports** (Delhi IGI, Hyderabad, Bengaluru T2, Goa Mopa): download the HOI app, link your card, and present the code at entry.

**TFS-operated lounges** (Mumbai T1/T2, Kolkata, Chennai, Pune, Bengaluru T1): swipe your physical credit card directly with the lounge staff. No app needed.

**Encalm lounges** (select airports including Hyderabad domestic): card or bank app confirmation, depending on the bank.

The practical upshot: an NRI flying Delhi–Mumbai–Ahmedabad on a single trip may need two different apps and a physical card swipe across three airports. Downloading and registering these apps requires an Indian mobile number for OTP verification — a detail that catches many NRIs off guard at the lounge entrance.

## The NRI-specific problem

These changes hit NRIs harder than resident cardholders for a structural reason: most NRIs do not spend ₹60,000 a quarter on their Indian credit cards. An Indian credit card kept alive for lounge access, the occasional Swiggy order during visits, and insurance renewals might see ₹10,000-15,000 of quarterly activity — nowhere near the new threshold.

The result is a quiet erosion of one of the main reasons NRIs maintain Indian bank accounts and credit cards. Without meeting the spend requirement, the card becomes a piece of plastic that charges an annual fee but delivers none of the perks that justified keeping it.

## What to do about it

A few options are worth considering. First, check whether your card's international lounge benefit (typically Priority Pass) still works without a spend requirement — for many premium cards, it does, and Priority Pass lounges exist at Delhi T3, Mumbai T2, and Bengaluru. Second, if you hold an Infinia or Diners Club Black card, those top-tier products still offer unlimited domestic lounge access without spend conditions, though annual fees run ₹10,000-12,500.

Third, for NRIs who fly through Adani or GMR airports, download the Adani One and HOI apps before you land — not at the lounge door. Registration takes a few minutes, requires an OTP to your registered mobile number, and is considerably less pleasant in a queue with a boarding pass in one hand and luggage in the other.

The silver lining in all of this: because banks now deal directly with lounge operators rather than paying DreamFolks' margin, some have quietly increased free visit caps. HDFC expanded Regalia coverage from eight to twelve domestic visits per year in early 2026. The visits are still there — you just have to earn them now.

For NRIs used to casual lounge access as a given, the adjustment is real. The days of walking in with any premium card and a boarding pass are over. What replaces them is a system that rewards active cardholders and penalises the rest — which, for a card you use three weeks a year, is not a comfortable place to be."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

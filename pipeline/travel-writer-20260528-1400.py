#!/usr/bin/env python3
"""Travel writer — 2026-05-28 14:00 UTC run"""
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
        "headline": "India's OCI Card Just Went Fully Digital — Here's What Every NRI Must Do Before Their Next Trip Home",
        "subheadline": "The new e-OCI system, effective May 1, replaces physical blue booklets with digital QR codes — but a 90-day passport update window and $25 penalties mean procrastinating NRIs could face trouble at immigration.",
        "slug": make_slug("india-eoci-digital-card-nri-passport-update-rules"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "Every OCI-holding NRI in the US is directly affected — the 90-day passport update rule means you must log in and update your OCI record online within three months of getting any new passport, or pay a $25 penalty. Some travelers have already been questioned at Delhi and Bengaluru immigration.",
        "tags": ["travel", "oci", "visa", "nri", "immigration", "india"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Wego Travel Blog — e-OCI Guide", "url": "https://blog.wego.com/what-is-e-oci/"},
            {"name": "VisaVerge — India OCI Rules 2026", "url": "https://visaverge.com/immigration/india-oci-rules-2026/"},
            {"name": "India Policy Hub — 2026 Digital e-OCI Guide", "url": "https://indiapolicyhub.in/"},
            {"name": "VisaHQ — India e-OCI Platform Launch", "url": "https://visahq.com/"},
            {"name": "Indian Eagle — India Launches Digital e-OCI", "url": "https://indianeagle.com/"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/5405596/pexels-photo-5405596.jpeg",
        "image_caption": "The new e-OCI replaces the familiar blue booklet with a digital QR code linked to India's IVFRT 2.0 immigration system.",
        "body": """India's Overseas Citizen of India card — the blue booklet that has for two decades been the diaspora's ticket to visa-free entry — is no longer a piece of paper. On May 1, 2026, the Ministry of Home Affairs activated a fully digital replacement called the e-OCI, and the shift carries real consequences for the roughly 4 million OCI holders worldwide, a disproportionate share of whom live in the United States.

## What Actually Changed

The Citizenship (Amendment) Rules, 2026, notified on April 30, did three things at once. First, every new OCI registration is now processed through a single online portal — ociservices.gov.in — and issued as an electronic record in a new format called Form XXIX. No more duplicate paper submissions, no more mailing physical documents to consulates for routine updates. Second, the government created a centralised electronic register (Form XXX) of all OCI holders, which feeds directly into India's Immigration, Visa & Foreigners Registration & Tracking (IVFRT) 2.0 platform — the same system that powers biometric e-gates at Delhi, Mumbai, Bengaluru, and Hyderabad airports. Third, the processing timeline has been slashed: the MHA expects turnaround under 15 working days, down from the months-long waits that plagued the old system.

Existing physical OCI cards remain valid for travel. There is no mandatory conversion. But the next time any OCI holder files for any service — a passport update, a re-issuance, a replacement — the system will issue an e-OCI by default.

## The 90-Day Rule That Will Trip People Up

The change most likely to cause boarding denials at SFO or JFK: **every time you receive a new passport, you must update your OCI record online within 90 days**. Miss the window, and the free update becomes a $25 penalty. More importantly, an out-of-sync OCI record can cause delays or refusals at Indian immigration counters. Travelers at Delhi and Bengaluru have already been asked to show proof of their most recent update.

The update itself is simple — log into the portal, upload your new passport's bio page and a photo taken within 30 days, e-sign, submit. No consulate visit required. But "simple" and "something people actually do" are rarely the same thing, and every NRI who has ever let their OCI update slide for a year knows the gap.

## The Fee Overhaul

Fresh OCI registration now costs $275 (up from previous rates), plus a $3 ICWF surcharge and a 1.01% processing charge on debit card payments. The first mandatory re-issuance — triggered when you get your first new passport after turning 20 — costs $25. Replacing a lost or damaged card runs $100. PIO-to-OCI conversions remain at $100.

The silver lining: the free 90-day passport update means routine maintenance costs nothing, as long as you do it on time.

## Why This Matters to NRIs Specifically

The typical Indian American OCI holder renews their US passport every ten years, their children's every five. Each renewal triggers the 90-day clock. For a family of four with two minor children, that means multiple update windows over any decade — and each missed deadline stacks a $25 penalty plus the risk of an immigration flag.

The e-OCI also introduces a rule for minors that Indian American parents need to understand: **a minor cannot simultaneously hold an Indian passport and a foreign passport**. This doesn't affect most OCI families, but those who have applied for an Indian passport for a child born abroad must surrender any foreign passport first. For families navigating dual-identity paperwork, this adds a compliance layer.

## The Biometric Future

The e-OCI's integration with IVFRT 2.0 is the real long-term play. Once your digital record is synced, you're eligible for automated e-gate entry at participating Indian airports — the same fast-track lanes that DigiYatra users access with facial recognition. For NRIs who have spent years watching foreign passport holders breeze through while they wait in OCI lines, this is a material improvement.

Indian Eagle reports that the system will integrate facial recognition for airport entry by late 2026, meaning the e-OCI holder's phone could eventually replace the physical card entirely.

## What to Do Right Now

If you hold an OCI card and have renewed your passport in the last three months, go to ociservices.gov.in and file your update immediately — it's free within the 90-day window. If you renewed your passport more than 90 days ago and haven't updated, file anyway and pay the $25 before your next trip. And if you're traveling to India this summer, carry both your current passport and a printout of your e-OCI Form XXIX acknowledgement, just in case.

The paper era is over. The digital one has a 90-day deadline."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India Just Committed $3.4 Billion to Regional Airports — and NRIs Visiting Tier-2 Hometowns Stand to Gain the Most",
        "subheadline": "The Modified UDAN scheme, approved for 2026–2036, will develop 100 new airports from unserved airstrips and more than double the existing route network — a direct fix for the six-hour drive that awaits most NRIs after they land.",
        "slug": make_slug("modified-udan-regional-airports-nri-tier-2-hometowns"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "For the millions of NRIs whose ancestral homes sit in tier-2 and tier-3 India — places like Jharsuguda, Kalaburagi, Hubli, Tirupati, or Cooch Behar — the expansion means a potential end to the exhausting post-landing road trip that has defined every India visit.",
        "tags": ["travel", "udan", "airports", "india", "infrastructure", "nri"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Aviation Week — India Expands UDAN", "url": "https://aviationweek.com/special-topics/small-narrowbody-jets/india-expands-udan-boosting-regional-airport-connectivity"},
            {"name": "Travel And Tour World — Star Air UDAN Expansion", "url": "https://travelandtourworld.com/"},
            {"name": "PIB — UDAN Regional Connectivity Scheme", "url": "https://pib.gov.in/"},
            {"name": "The Hindu Business Line — Bengaluru Regional Flights Resume", "url": "https://thehindubusinessline.com/"},
            {"name": "DevDiscourse — Star Air Flight Relaunch", "url": "https://devdiscourse.com/"}
        ]),
        "score_total": 75,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/35644200/pexels-photo-35644200.jpeg",
        "image_caption": "India's Modified UDAN scheme aims to develop 100 new airports from existing unserved airstrips over the next decade.",
        "body": """Every NRI knows the drill. You survive the 17-hour flight from Newark or San Francisco. You clear immigration. You collect your bags. And then begins the real journey — the four-to-eight-hour car ride from the nearest metro airport to the town where your family actually lives. India's Cabinet just approved a plan that could eventually end that second leg.

## The Modified UDAN Scheme

The Union Cabinet has greenlit Modified UDAN with an outlay of ₹28,840 crore ($3.4 billion) over a decade, running from FY 2026–27 to FY 2035–36. The program will develop 100 airports from existing unserved airstrips, more than doubling the 95 airports, heliports, and water aerodromes currently connected under the original UDAN scheme, which has launched 663 routes since its inception.

UDAN — an acronym whose Hindi translation loosely means "let the ordinary people fly" — was designed to subsidise flights on routes that wouldn't survive on pure commercial economics. The modified version keeps the core mechanism: airlines operating on unviable routes receive Viability Gap Funding (VGF) for five years, with a taper starting in year three and route exclusivity limited to three years. The total VGF allocation is ₹10,043 crore over the decade.

"Modified UDAN has been envisioned as a further enabler for connecting Tier 2 and 3 cities to the country's aviation map in a sustainable manner," aviation minister Kinjarapu Ram Mohan Naidu said.

## What's Already Moving

The program isn't just a policy announcement — routes are already being operationalised. In May 2026, Star Air resumed six weekly flights on the Hyderabad–Jharsuguda–Bhubaneswar corridor, reconnecting Odisha's industrial heartland to Telangana's capital. Karnataka announced ₹28.47 crore in state support to restart suspended Bengaluru-to-Bidar and Bengaluru-to-Kalaburagi services, both UDAN routes that had been halted due to low occupancy but were deemed essential for the Kalyana Karnataka region's economic development.

Meanwhile, Akasa Air — India's fastest-growing carrier — is set to launch daily flights from the brand-new Noida International Airport in June 2026, with Bengaluru and Navi Mumbai as its first routes. The twin openings of Noida and Navi Mumbai airports are themselves products of India's broader airport-building ambitions.

Star Air, with seven Embraer E175 jets, remains the only Indian carrier operating the regional jet type — but that may change. Embraer and Adani Defence & Aerospace signed an MoU in January to set up an E175 final assembly line in India, contingent on 200 firm orders. Embraer estimates India will need around 500 aircraft in the 80–146 seat category over the next two decades.

## Why NRIs Should Care

The NRI travel pattern is distinctive. You don't fly to India to stay in Delhi or Mumbai — you fly there to reach Mangalore, Hubli, Tirupati, Vijayawada, Raipur, Ranchi, or a hundred other places that the international route map has never served directly. The original UDAN connected some of these dots, but with only 95 operational airports, vast swathes of tier-2 and tier-3 India remained road-trip territory.

Modified UDAN's 100 new airports change the math. If your family is in Jharsuguda, you no longer need to fly to Bhubaneswar and drive four hours. If they're in Kalaburagi, the Bengaluru connection shaves five hours off the ground leg. For the millions of NRIs whose homecoming includes an overnight train or a bone-rattling highway drive, these routes aren't a convenience — they're a transformation.

The impact extends beyond convenience. Shorter domestic connections mean NRIs can visit more frequently during shorter US vacations. A tier-2 city with direct flights from a metro hub becomes viable for a five-day trip; without that flight, the same visit demands seven days minimum, two of which are spent in transit.

## The Viability Question

The obvious concern: UDAN routes have a mixed track record. Several have been suspended after subsidies ran out and airlines found the load factors unsustainable. The Bengaluru-Bidar service is a case in point — launched, suspended, now revived with fresh state funding. Critics argue that subsidising permanently unviable routes amounts to burning cash.

The Modified UDAN's answer is the tapered VGF model: five years of support with declining subsidies after year three, forcing airlines to build demand or exit. The three-year exclusivity cap also prevents monopoly pricing on thin routes.

Whether this works depends on something outside any government's control: whether enough Indians actually fly these routes once the seats are available. India's domestic passenger numbers have grown roughly 12% annually over the past five years, and the aviation ministry projects 350–400 operational airports by 2047. If even half of the projected growth materialises in tier-2 cities, the economics could work.

## What to Watch

For NRIs planning India trips in 2027 and beyond, the practical advice is simple: before booking that connecting car from the metro airport, check whether a UDAN route now serves your hometown directly. The network is expanding faster than most diaspora travellers realise. Star Air, Alliance Air, FLY91, and Akasa Air are all adding regional routes.

India's aviation ambitions have always been big. Modified UDAN's $3.4 billion bet is that the country's smallest airports — not its biggest — are where the next wave of growth will come from. For the NRI who has spent two decades enduring the post-landing road trip, that bet couldn't come soon enough."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

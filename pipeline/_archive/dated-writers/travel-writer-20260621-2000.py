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

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "IndiGo Is Adding Six New International Cities on Narrowbody Jets — and Quietly Building the Hub the Diaspora Will Connect Through",
        "subheadline": "Nairobi, Jakarta, Tbilisi, Baku, Tashkent and Almaty join the network between July and September, and the new Bali nonstops show how single-aisle jets are rewriting India's map.",
        "slug": make_slug("indigo-six-new-international-routes-nairobi-jakarta-central-asia-bali-a321xlr-nri"),
        "category": "travel",
        "vertical": "aviation",
        "diaspora_angle": "For NRIs who already route through Delhi or Mumbai to reach family, IndiGo's widening spoke network and long-range narrowbodies mean more one-stop options home and a cheaper alternative to the Gulf carriers that have dominated diaspora connections.",
        "tags": ["travel", "airlines", "indigo", "international-routes", "central-asia"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Airways Magazine", "url": "https://airwaysmag.com/"},
            {"name": "Simple Flying", "url": "https://simpleflying.com/"},
            {"name": "Aviation Week", "url": "https://aviationweek.com/"}
        ]),
        "score_total": 76,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/ba/VT-ILY_-_IndiGo_-_Airbus_A321-251NX_-_MSN_10490_-_VGHS.jpg/1280px-VT-ILY_-_IndiGo_-_Airbus_A321-251NX_-_MSN_10490_-_VGHS.jpg",
        "image_caption": "An IndiGo Airbus A321neo, the workhorse behind the airline's new long-range narrowbody routes",
        "image_attribution": "Wikimedia Commons",
        "body": """IndiGo, India's largest airline, is opening six new international destinations between late July and September, threading direct flights from Mumbai and Delhi to cities most NRIs have only ever reached on a connection. The additions add up to 174 new weekly international flights in a single summer — the clearest sign yet that the carrier that built its empire on 45-minute domestic hops is now serious about long-haul.

The new cities split neatly into two camps. From Mumbai, IndiGo will fly nonstop to **Nairobi** in Kenya and **Jakarta** in Indonesia in late July and early August. From Delhi, it adds **Tbilisi** (Georgia, three times a week) and **Baku** (Azerbaijan, four times a week) in August, followed by **Tashkent** (Uzbekistan, four times a week) and **Almaty** (Kazakhstan, three times a week) in September. Ticket sales open as government approvals clear.

## The narrowbody trick

What makes this possible is a single aircraft: the Airbus A321XLR. IndiGo is also using it to convert two of its busiest leisure routes — Delhi and Mumbai to **Bali (Denpasar)** — from one-stop A320neo services into true nonstops. Westbound block times back to India will run as long as seven hours and 55 minutes, placing them among the longest single-aisle flights anywhere in the world.

Historically, a route that long demanded a widebody jet and the fat fixed costs that come with it. The A321XLR, capable of roughly 8,700 km, lets IndiGo open thinner markets profitably and test demand before committing widebody metal. The airline now operates around 2,200 daily flights to 141 destinations, and its stated goal is to fly 40% of its capacity internationally by 2030, up from nearly 30% today.

## Why the diaspora should pay attention

On the surface, a Delhi–Tbilisi flight has little to do with a software engineer in Sunnyvale or a physician in New Jersey. Look closer. IndiGo's strategy is to turn Delhi and Mumbai into genuine connecting hubs, and every new spoke makes the airline a more credible option for the long leg home.

The Central Asian additions matter for a second reason: airspace. Since the closure of Pakistani airspace, flights between India and Europe or the Americas have taken longer, costlier detours. Hubs like Tashkent and Almaty sit on viable northern routings, and a stronger IndiGo presence there hints at how Indian carriers are rebuilding connectivity around the closure rather than waiting for it to lift.

There is also a straightforward price argument. For decades, the cheapest way from the US East Coast to a second-tier Indian city ran through Dubai, Doha or Abu Dhabi on a Gulf carrier. As IndiGo layers international spokes onto its unrivalled domestic grid, a diaspora traveler can increasingly fly one international carrier to Delhi or Mumbai and connect onward on the same ticket, the same airline, the same baggage tag — exactly the seamlessness the Gulf hubs sold.

https://x.com/IndiGo6E

## The catch

IndiGo's long-haul ambitions still rest on borrowed wings. Its first European routes to Manchester and Amsterdam, and the upcoming London and Copenhagen services, lean on Boeing 787s wet-leased from Norse Atlantic Airways, while the A321XLRs handle the medium-haul work until the airline's own A350s arrive from 2027. That makes the current network a bridge, not a destination — capacity can shift quickly if a lease ends or an approval stalls.

For now, the practical takeaway for NRI families is to widen the search. The next time you price a summer trip to Hyderabad, Kochi or Ahmedabad, check whether an IndiGo connection through Delhi or Mumbai undercuts the reflexive Emirates or Qatar Airways booking. The answer, increasingly, is yes — and the list of cities where it holds true is growing by the month.

**What's next:** Watch for IndiGo to confirm its mystery London airport and firm up Central Asian schedules as slots are approved. With 174 new weekly flights landing in one quarter, the airline is betting that the diaspora's appetite for one-stop access has outgrown the Gulf detour."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Global Entry Is Testing a Walk-Through Camera at Six US Airports — and It Changes the Best Perk of the Indian Diaspora's Favorite Program",
        "subheadline": "CBP is piloting face capture on approach to passport control, skipping the kiosk pose. For the millions of Indians enrolled in Global Entry, the line home just got faster.",
        "slug": make_slug("global-entry-camera-capture-pilot-six-us-airports-indian-citizens-nri"),
        "category": "travel",
        "vertical": "immigration",
        "diaspora_angle": "Indian citizens are eligible for Global Entry, and the program is the single biggest time-saver for NRIs and visiting parents clearing US immigration after a 16-hour flight — so a faster, kiosk-free arrival is a tangible upgrade for the community.",
        "tags": ["travel", "global-entry", "airports", "cbp", "trusted-traveler"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Points Guy", "url": "https://thepointsguy.com/"},
            {"name": "U.S. Customs and Border Protection", "url": "https://www.cbp.gov/global-entry/about"}
        ]),
        "score_total": 72,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/81/APC_and_Global_Entry_Kiosks_%2815152962014%29.jpg/1280px-APC_and_Global_Entry_Kiosks_%2815152962014%29.jpg",
        "image_caption": "Global Entry and Automated Passport Control kiosks in a US airport arrivals hall",
        "image_attribution": "Wikimedia Commons",
        "body": """US Customs and Border Protection is quietly testing a change to Global Entry that could erase one of the few remaining friction points in the program: the kiosk. At six major US airports, the agency is piloting camera-capture technology that photographs travelers as they approach passport control, rather than asking them to stop and pose at a machine. For the large and growing number of Indian travelers enrolled in Global Entry, it is a small tweak with an outsized payoff.

## What is actually changing

Global Entry has relied on biometric photos for years. The kiosk you use after a long-haul flight snaps a picture and matches it against the one you submitted when you applied. The pilot does not add surveillance so much as move the moment: instead of stopping to have your photo taken at a kiosk, the capture happens as you walk toward the booth — often without travelers noticing it at all.

CBP frames the goal plainly. With more than four million members and enrollment still climbing, the agency wants to keep crowds moving on busy arrival banks. In testers' experience, the camera does its work somewhere on the approach to the officer, and the kiosk pause largely disappears.

Privacy-conscious travelers retain an opt-out. As with TSA checkpoint photos, participating in the camera-capture step is optional — though anyone uneasy with biometrics should remember that Global Entry has always been a photo-based program at its core.

## Why this lands hard for the diaspora

Global Entry is not an abstraction for the Indian community. CBP extended eligibility to Indian citizens years ago, making India one of a short list of countries whose nationals can enroll, and the program has since become the default arrival tool for NRIs, green-card holders and frequently visiting parents. After a 15-to-17-hour flight from Delhi, Mumbai or Bengaluru, the difference between a 40-minute immigration crawl and a two-minute walk-through is the difference between catching and missing a domestic connection at SFO, EWR or ORD.

The membership math is also favorable. Global Entry costs $100 for five years, includes TSA PreCheck for the outbound leg, and pays for itself the first time a jet-lagged family of four skips the main hall. A faster, kiosk-free arrival simply sharpens a value proposition that already made sense.

## The fine print NRIs still need to know

Two cautions are worth carrying through the airport. First, Global Entry is not a force field. Even trusted travelers can be pulled for additional screening, and the dreaded "SSSS" code — Secondary Security Screening Selection — can appear on any boarding pass, including those of Global Entry and PreCheck members. It can be triggered by a last-minute one-way ticket, a cash purchase, travel to or from a flagged country, or simply a random draw. If you see it, budget an extra 15 to 45 minutes.

Second, the camera pilot does not change enrollment, which remains the program's real bottleneck. Interview slots are scarce, though Enrollment on Arrival lets conditionally approved applicants complete the interview with a CBP officer when they land at a participating airport — a route worth using if you are already approved and flying in.

## What's next

CBP describes the pilot as a step toward enhancing efficiency while maintaining security standards, and successful trials at the initial six airports typically precede a wider rollout. For the diaspora, the advice is unchanged but newly urgent: if you fly the India–US corridor even once or twice a year and are not yet enrolled, the program's best perk — getting out of the airport fast — is about to get faster still. The line you skip this winter may be shorter than the one you skipped last year."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Your US Visa Doesn't Stop Being Reviewed After You Get It — and Indian Travelers Are Learning That the Hard Way",
        "subheadline": "The US Embassy in India is reminding visa holders that screening is continuous, even after approval. Here's what that means before your next trip — and the four letters that can still derail it.",
        "slug": make_slug("us-visa-continuous-screening-after-approval-india-ssss-nri-travel-advisory"),
        "category": "travel",
        "vertical": "immigration",
        "diaspora_angle": "Millions of Indians hold US tourist, work and student visas, and a reminder that approval is not permanent — combined with practical airport realities like the SSSS code — directly affects how NRIs and their visiting families plan trips.",
        "tags": ["travel", "visa", "us-immigration", "advisory", "nri"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Indian EYE", "url": "https://theindianeye.com/"},
            {"name": "The Columbus Dispatch", "url": "https://www.dispatch.com/"}
        ]),
        "score_total": 74,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d6/CBP_Preclearance_Media_Availability_%2830248743283%29.jpg/1280px-CBP_Preclearance_Media_Availability_%2830248743283%29.jpg",
        "image_caption": "A US Customs and Border Protection officer at a passport control inspection booth",
        "image_attribution": "Wikimedia Commons",
        "body": """A short notice from the US Embassy in India carries a longer warning for the diaspora: getting a US visa is not the end of the screening process. In a public post, the embassy reminded Indian visa holders that vetting continues even after a visa is granted, and that the government uses "all available information" to identify travelers who may have become inadmissible. For a community that holds millions of B1/B2 tourist, H-1B work and F-1 student visas, it is a reminder worth reading twice.

## What "continuous vetting" means in practice

A US visa has always been a permission to travel to a port of entry, not a guarantee of admission — that final call belongs to the CBP officer at the booth. What is new is the emphasis on the gap in between. The State Department and Department of Homeland Security now stress that the record behind a visa stays live: a visa can be reviewed, flagged or revoked after issuance if new information surfaces, from a legal matter to a status problem to a data mismatch.

The embassy paired the reminder with reassurance. Amid a sweeping 2025 travel ban that bars nationals of 12 countries and partially restricts seven more, **India is not on either list.** US consulates continue to process Indian applications across all categories — tourist, work and student. The pressure point for Indians remains time, not eligibility: interview slots at several consulates are booked 10 to 12 months out, and demand keeps outrunning capacity.

## The four letters that still catch trusted travelers

Continuous vetting has a visible cousin at the airport: the boarding-pass code **"SSSS,"** short for Secondary Security Screening Selection. Find it printed on your pass and you will be pulled aside for extra screening — bags opened, electronics swabbed, sometimes a brief interview.

Crucially, it is not reserved for the unknown traveler. Even members of Trusted Traveler programs like Global Entry and TSA PreCheck, and CLEAR subscribers, can be tagged. Common triggers include a last-minute ticket, a one-way fare paid in cash, travel to or from a country flagged by the State Department, or a simple random selection. The practical rule: if you see SSSS, give yourself 15 to 45 extra minutes at the checkpoint, and never assume your PreCheck lane makes you immune.

## A checklist before you fly

For NRIs and the parents and relatives who visit them, the takeaways are concrete rather than alarming:

- **Keep your status clean and current.** Because vetting is continuous, an unresolved legal issue, an overstay on a prior trip, or a lapsed status can resurface at the worst moment. Travel with documents that prove your current standing.
- **Carry your paper trail.** Visiting parents on B1/B2 visas should keep return tickets, proof of ties to India and the host's details handy; students and workers should travel with current I-20s, I-797s or employment letters.
- **Build in airport buffer.** Between the possibility of an SSSS pull and the general congestion of summer travel, the old advice to arrive early is now a hedge against a specific, documented risk.
- **Apply early for everything.** With consular interviews booked the better part of a year out, a renewal or a relative's first visa is a months-ahead project, not a few-weeks one.

## What's next

None of this signals a shift in India's standing with the United States; officials have been explicit that Indian travelers remain welcome across visa categories. What has changed is the messaging — a clear, on-the-record reminder that a US visa is a living document, reviewed continuously, and that the smoothest trips belong to travelers whose paperwork and status can withstand a second look at any point in the journey. For a diaspora that crosses this border constantly, that is less a warning than a planning instruction."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

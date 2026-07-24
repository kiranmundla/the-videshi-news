#!/usr/bin/env python3
"""Travel writer batch — 2026-07-01 19:00 PDT
Topics:
1. Srinagar Airport Mon/Tue closures through September
2. Thailand ends visa-free for Indians — new 15-day VoA
3. IndiGo suspends 7 international routes amid fuel-cost squeeze
"""

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


# ── Article 1: Srinagar Airport Closures ──────────────────────────────
art1_body = """Kashmir's busiest airport is about to get a lot harder to fly into. Starting today — July 1, 2026 — Srinagar Airport will shut its runway every Monday and Tuesday for Indian Air Force maintenance work. The partial closures will run through September 30, followed by a complete 16-day shutdown from October 1 to October 16.

For the roughly 35 to 40 daily flights that normally move through Srinagar, the math is brutal: two lost days a week wipes out nearly 30 per cent of weekly capacity during what is ordinarily Kashmir's peak tourist season.

## What's actually happening

The Indian Air Force is resurfacing the runway at Sheikh ul-Alam International Airport, a dual-use military-civilian facility. The work has been under way since April, when a NOTAM restricted civilian flights to an 8 AM–5 PM window. Now the project enters its most disruptive phase:

- **July 1 – September 30**: No flights on Mondays and Tuesdays. Operations continue Wednesday through Sunday within the existing daytime window.
- **October 1 – October 16**: Full runway closure — no civilian flights at all for 16 days.

Airlines including IndiGo, Air India, SpiceJet and GoFirst have begun adjusting schedules, compressing departures into the five available days. Fares on remaining slots have already started creeping upward.

## Why Kashmir's tourism industry is worried

The timing could hardly be worse. July through October is when Kashmir sees its heaviest tourist traffic — families escaping the plains heat, trekkers heading to Sonamarg and Gulmarg, and pilgrims on the Amarnath Yatra. The October shutdown falls squarely on Durga Puja and Navaratri, traditionally one of the biggest domestic tourism windows of the year.

"People are trying to escape the punishing heat in various Indian states and are increasingly choosing Kashmir as their destination," Mohammad Imran, a Srinagar-based transporter, told The Hindu BusinessLine. "Any disruption in air connectivity will affect tourist arrivals and hit transporters, hoteliers, tour operators and other businesses dependent on tourism."

The Kashmir Economic Alliance, an umbrella body of trade organisations, has urged the government to reconsider the October closure, arguing it would devastate the Valley's tourism-dependent economy.

## What NRIs planning a Kashmir trip should do

If you are an NRI with a summer or autumn Kashmir trip on the calendar, here is the practical reality:

**Book mid-week flights.** With Monday and Tuesday off the table, Wednesday and Thursday morning departures will be the least crowded. Avoid Sunday evening returns — that will be the bottleneck as five days of visitors funnel out simultaneously.

**Consider Jammu as a backup gateway.** Jammu Airport, about 260 km south, remains fully operational. The Jammu–Srinagar National Highway is in better shape than it has been in years, and the drive takes roughly seven to eight hours. Several NRIs already use Jammu as a stopover to visit Vaishno Devi before continuing north.

**Avoid October entirely.** The 16-day complete shutdown from October 1 to 16 means no flights in or out. If your trip overlaps with this window, you will need to be in Kashmir before October 1 and plan to leave only after the 16th — or reroute through Jammu.

**Monitor airline apps closely.** Srinagar Airport has urged passengers to follow official channels and airlines directly rather than relying on third-party booking platforms, which may not reflect real-time schedule changes during the maintenance period.

The runway work, while disruptive, is long overdue. The resurfaced runway will eventually support heavier aircraft and longer-range operations — potentially opening the door to future international charter flights. For now, though, NRIs planning their annual Kashmir pilgrimage or family holiday need to plan around a shrinking flight calendar."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Srinagar Airport Goes Dark Two Days a Week — What NRIs Planning Kashmir Trips Need to Know",
    "subheadline": "Indian Air Force runway maintenance will shut Kashmir's only major airport every Monday and Tuesday through September, with a full 16-day closure in October that collides with Durga Puja and Navaratri.",
    "slug": make_slug("srinagar-airport-closure-kashmir-nri-travel-guide"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "NRIs planning summer or autumn Kashmir trips face sharply reduced flight options and must rebook around a five-day weekly schedule or reroute through Jammu.",
    "tags": ["travel", "kashmir", "airports", "srinagar", "nri-travel"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Travel and Leisure Asia", "url": "https://www.travelandleisureasia.com/in/news/srinagar-airport-closure/"},
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/economy/logistics/runway-closure-plan-at-srinagar-airport-raises-concerns-among-kashmir-businesses/article69651483.ece"},
        {"name": "Livemint", "url": "https://www.livemint.com/news/india/srinagar-airport-update-why-srinagar-airport-will-remain-closed-two-days-a-week-all-you-need-to-know-11748859539671.html"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/2/22/Lapangan_terbang_Srinagar.jpg",
    "image_caption": "Srinagar Airport runway with the Pir Panjal mountains in the background",
    "image_attribution": "Wikimedia Commons",
    "body": art1_body
}


# ── Article 2: Thailand Visa Changes ──────────────────────────────────
art2_body = """For the past two years, Thailand was the easiest international trip an Indian passport could buy. Show up at Suvarnabhumi, get stamped in for 60 days, no visa, no fee, no paperwork. That era is over.

On May 19, 2026, Thailand's Cabinet approved a sweeping overhaul of its immigration framework. India has been stripped from the visa-free list entirely and placed into a new Visa on Arrival category — alongside Azerbaijan, Belarus and Serbia — capping stays at 15 days and charging a THB 2,000 fee (roughly ₹4,600–₹5,800) payable in cash at the airport counter.

## What exactly changed

The shift is significant on paper but manageable in practice for most holidaymakers. Here is the before-and-after:

| | Old rules (2024–May 2026) | New rules (2026 onwards) |
|---|---|---|
| **Entry type** | Visa-free | Visa on Arrival (VoA) |
| **Max stay** | 60 days + 30-day extension | 15 days, single entry |
| **Cost** | Free | THB 2,000 (~₹5,800) in cash |
| **Extension** | 30-day extension available | Not extendable |

For Indians planning a standard five-to-seven-day Bangkok–Pattaya–Phuket trip, the new rules add a fee and a queue at immigration but do not fundamentally change the trip. The 15-day window covers any typical holiday package.

The real pain falls on long-stay visitors — digital nomads, retirees splitting time between India and Thailand, and the growing community of Indians who used the 60-day stamp for extended workations. Those travellers now need either a Tourist Visa from the Thai Embassy (up to 60 days, ~₹1,200–₹4,000, 14-day processing) or a Thailand e-Visa (up to 30 days, ~₹6,000, apply 3–4 weeks ahead).

## Why Thailand tightened the rules

Bangkok framed the decision as a security-driven reset. Thai officials cited "misuse" of the visa-free scheme — people exploiting long stays for unofficial residency and informal work rather than genuine tourism. The broader overhaul cuts visa-exempt countries from 93 to 54 and trims the VoA list from 31 nations to just four.

Ravi Gosain, president of the Indian Association of Tour Operators, put it in perspective: "The requirement to apply for a visa will require Indian travellers to plan, document and pay for their trips, making spontaneous trips less likely. But Thailand will continue to be a very popular destination because of proximity, price, ease of access and variety."

## What NRIs should do now

**Short trips? Carry THB 2,000 in cash.** The VoA fee is payable at the airport counter in Thai Baht only — no cards, no dollars. Exchange before you fly or withdraw Baht from an ATM in the arrivals hall before joining the VoA queue.

**Trips longer than two weeks? Apply for an e-Visa early.** The Thai e-Visa portal (thaievisa.go.th) takes about 14 working days to process. If you want 30 days, plan at least a month ahead. For 60 days, you'll need the traditional Tourist Visa through the Thai Embassy or Consulate.

**US-based NRIs have an alternative route.** If you hold a valid US visa (B1/B2, H-1B, or Green Card), Thailand's VoA is your only option for visa-free-esque entry. However, your US status does unlock visa-free or VoA access to dozens of other Southeast Asian destinations — Malaysia (30 days free), Indonesia (30 days VoA), and Vietnam (45 days e-Visa) — all of which remain unchanged and may now look more attractive for spontaneous getaways.

**Don't panic if you're already booked.** If you are currently in Thailand under the old 60-day stamp, you are not affected — you can complete your stay as originally planned. The new rules apply only to entries after the formal gazette date.

Thailand remains a fantastic destination for Indian travellers. The visa change adds a small friction cost but does not close the door. For NRIs who visit once or twice a year for a week at a time, this is a minor adjustment. For those who treated Bangkok as a second home, it is time to explore the e-Visa option — or start looking at Bali."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "Thailand Ends Its Visa-Free Welcome for Indians — Here's What the New 15-Day VoA Means",
    "subheadline": "After two years of 60-day visa-free access, Indian passport holders now face a THB 2,000 fee and a 15-day cap. Short holidays are barely affected; long stays need a rethink.",
    "slug": make_slug("thailand-visa-on-arrival-india-15-days-nri-guide"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "Thailand is among the most popular international destinations for Indian Americans, and many NRIs used the 60-day visa-free window for extended stays. The new 15-day VoA cap and fee require replanning.",
    "tags": ["travel", "visa", "thailand", "nri-travel", "southeast-asia"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Lexology / Tilleke & Gibbins", "url": "https://www.lexology.com/library/detail.aspx?g=4e4d1d51-3d10-4a9d-8c6e-0c7f7b8d9e2a"},
        {"name": "Medium / Emily Cooper", "url": "https://medium.com/@emilycooper/thailand-ends-60-day-visa-free-entry-what-indian-travellers-need-to-know-in-2026"},
        {"name": "Pickyourtrail", "url": "https://www.pickyourtrail.com/blog/thailand-visa-for-indians/"},
        {"name": "The Traveler", "url": "https://thetraveler.org/thailand-restores-visa-on-arrival-fee-for-indians/"}
    ]),
    "score_total": 85,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c1/Wat_Phra_Kaew_by_Ninara_TSP_edit_crop.jpg/1280px-Wat_Phra_Kaew_by_Ninara_TSP_edit_crop.jpg",
    "image_caption": "The Grand Palace and Wat Phra Kaew temple complex in Bangkok, Thailand",
    "image_attribution": "Wikimedia Commons",
    "body": art2_body
}


# ── Article 3: IndiGo Route Suspensions ───────────────────────────────
art3_body = """India's largest airline is shrinking its international map. IndiGo has suspended flights to seven overseas destinations starting this week, the sharpest pullback in its decade-long push beyond domestic borders.

The cuts, announced in phases through June, take effect between July 1 and August 31:

- **July 1**: Hong Kong, Shanghai, Langkawi (Malaysia), Krabi (Thailand), Ho Chi Minh City (Vietnam)
- **July 3**: Siem Reap (Cambodia)
- **August 31**: Manchester (UK)

All six Asian routes are suspended until September 30, with IndiGo pledging to reopen bookings from October 1 "subject to an improved environment." Manchester is being dropped indefinitely, with the airline returning one of its wet-leased Boeing 787-9 Dreamliners to Norse Atlantic Airways.

## The triple squeeze

Three forces are converging on Indian aviation simultaneously.

**Fuel costs.** The Iran conflict has driven jet fuel prices sharply higher, and fuel accounts for up to 40 per cent of an airline's operating costs. IndiGo reported a ₹2,536 crore ($265 million) loss in Q4 FY26, largely because of the fuel spike. Air India, its main rival, is bleeding too.

**Airspace closures.** Pakistan's ban on Indian carriers overflying its territory — imposed during military tensions last year — adds 30 to 90 minutes to westbound flights, burning more fuel and eating into crew duty hours. Routes to the Gulf, Europe and the UK are all affected. The Iran conflict has separately closed airspace over parts of the Middle East, forcing further reroutings.

**Soft demand.** The July-to-September quarter is traditionally weaker for leisure travel to Southeast Asia (monsoon season in the region, summer holidays winding down). IndiGo cited "traditionally softer demand" as a factor alongside costs.

The result: IndiGo has cut 7–10 per cent of its planned domestic flights for June and July. Air India has gone further, slashing 22 per cent of domestic capacity. Together, the two carriers — which control roughly 90 per cent of India's domestic air market — have removed about 250 daily flights from the schedule.

## What this means for NRI travellers

Despite the cuts, IndiGo says it still operates more than 1,800 weekly international flights. The suspended routes are predominantly leisure-focused and relatively thin. But the ripple effects matter.

**Hong Kong and Shanghai.** NRIs who connected through these cities to reach mainland China or used Hong Kong as a weekend stopover from India will need to reroute. Cathay Pacific, China Eastern and Air China still serve India directly, though fares on those routes have risen.

**Southeast Asian beach destinations.** Langkawi, Krabi, Ho Chi Minh City and Siem Reap were popular add-ons for NRIs visiting family in India — a quick side trip on the way home. With IndiGo out until October, travellers should look at AirAsia, Thai Airways and Vietnam Airlines, all of which maintain direct or one-stop services from Indian metros.

**Manchester.** This is the most consequential cut for the diaspora. IndiGo's Delhi–Manchester route, launched in 2025 using 787 Dreamliners, served a large Punjabi and Gujarati community in northwest England. With the route gone, travellers revert to connecting via London Heathrow (Air India, IndiGo, British Airways) or via Gulf hubs (Emirates, Etihad).

**Domestic connections.** Fewer domestic flights mean tighter schedules and higher fares on trunk routes like Delhi–Mumbai, Delhi–Bengaluru and Mumbai–Chennai. NRIs flying into India on long-haul legs should build in longer connection buffers — a two-hour window that was comfortable in April may no longer be enough.

## The bigger picture

IndiGo's retreat is temporary but telling. The airline spent the past three years expanding aggressively overseas, leasing wide-body aircraft for the first time, adding European cities, and pushing toward a goal of 40 per cent international capacity by 2030. Air India, under Tata ownership, was simultaneously rebuilding into a global premium carrier.

Both are now pulling back, at least temporarily, from some of those ambitions. IndiGo's CFO Gaurav Negi has said the airline may consider fuel hedging for the first time. Air India has "temporarily rationalised operations on certain domestic routes" between June and August.

For NRIs, the practical takeaway is simple: book early, build in flexibility, and check airline apps before heading to the airport. The Indian aviation boom has not ended, but it is catching its breath."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "IndiGo Pulls Back from Seven International Routes as Fuel Costs and Airspace Closures Bite",
    "subheadline": "India's largest airline suspends flights to Hong Kong, Shanghai, Manchester and four Southeast Asian cities through September — the sharpest retreat in its international expansion.",
    "slug": make_slug("indigo-suspends-international-routes-fuel-costs-nri"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "NRIs who used IndiGo for connecting flights through Hong Kong, Southeast Asian stopovers, or the Delhi-Manchester service need to reroute. Domestic connection windows should also be extended.",
    "tags": ["travel", "airlines", "indigo", "aviation", "nri-travel"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/business/aerospace-defense/indias-indigo-cuts-six-international-routes-amid-rising-costs-airspace-restrictions-2026-06-05/"},
        {"name": "Skift", "url": "https://skift.com/2026/06/10/indigo-suspends-7-international-routes-whats-behind-the-cutbacks/"},
        {"name": "Livemint", "url": "https://www.livemint.com/companies/news/indigo-temporarily-suspends-operations-to-6-international-destinations-here-s-why-11748954474937.html"},
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/economy/logistics/indigo-suspends-flights-to-six-asian-destinations/article69645261.ece"}
    ]),
    "score_total": 80,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4d/IndiGo_Airbus_A320neo_F-WWDG_%28to_VT-ITI%29_%2828915135713%29.jpg/1280px-IndiGo_Airbus_A320neo_F-WWDG_%28to_VT-ITI%29_%2828915135713%29.jpg",
    "image_caption": "An IndiGo Airbus A320neo, the backbone of the airline's domestic and short-haul fleet",
    "image_attribution": "Wikimedia Commons",
    "body": art3_body
}


articles = [art1, art2, art3]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

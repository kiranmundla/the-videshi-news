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

# ============================================================================
# ARTICLE 1 — Navi Mumbai International Airport begins international ops July 15
# ============================================================================
body1 = """Mumbai is about to become a two-airport city in the way that matters most to the diaspora: international departures. Navi Mumbai International Airport (NMIA), the long-delayed second gateway built across the harbour in Ulwe, will begin international passenger and cargo operations on July 15, 2026, according to officials cited by The Times of India. The first overseas flights will be short-haul services to the Gulf — the busiest single international market for travellers out of Mumbai.

For now, the launch is deliberately modest. NMIA opened to domestic traffic in December 2025, and the international debut is "subject to the completion of final regulatory formalities," officials said. Customs authorities have already inspected the airport's readiness, and the remaining clearances are being processed. Expect the Gulf carriers and Indian low-cost airlines that dominate the Mumbai–Gulf corridor to anchor the early schedule, with long-haul widebody routes to Europe and North America following in phases rather than on day one.

## Why a second Mumbai airport matters

Chhatrapati Shivaji Maharaj International Airport (CSMIA) has been running at the edge of its capacity for years. A single main runway and chronic peak-hour congestion mean that delays at CSMIA ripple across the whole network — and anyone who has missed a connection at Mumbai while flying home knows the cost in hours and stress. NMIA is designed to take pressure off that bottleneck. Its Terminal 2, the dedicated international terminal, is being redesigned from an original 30-million-passenger plan into a 50-million-passenger facility, with nearly half of projected traffic expected to be international.

The airport is also being wired into the rest of the metro region in a way CSMIA never was: Metro Line 8, proposed high-speed rail links, expanded road infrastructure and even water transport are all planned to feed NMIA. For travellers coming from Pune, Navi Mumbai, and the southern and eastern suburbs, the new airport will often be the closer, faster option.

## The NRI angle

The roughly four-million-strong Indian American community treats Mumbai as one of its primary gateways home, and Maharashtrian, Gujarati and South Indian families routing through BOM have long absorbed CSMIA's congestion as a fact of life. A second international airport changes the calculus in three concrete ways.

First, redundancy. When one Mumbai airport is fogged in, slot-constrained or backed up, the region will no longer grind to a halt. Second, geography. NRIs with roots in Navi Mumbai, Panvel, Raigad and the Konkan belt — and those visiting family in Pune — will find NMIA materially closer than the trek across the city to CSMIA. Third, the long game: a 50-million-passenger international terminal is the kind of capacity that attracts new nonstop long-haul routes. The Gulf-first launch is the appetiser; the prize for the diaspora is a future BOM-area airport that can support direct flights to North America and Europe without the slot scarcity that has capped CSMIA's growth.

There is also a quiet bonus. NMIA recently landed on the Prix Versailles list of the World's Most Beautiful Airports 2026, recognised for its lotus-inspired architecture. After decades of treating Indian airports as something to be endured, the diaspora now has terminals worth photographing.

## What to do before you book

Through this summer and into the Diwali rush, assume CSMIA remains the hub for nearly all long-haul flights home. NMIA's July 15 start is Gulf short-haul first, so the travellers who benefit immediately are those connecting through Dubai, Abu Dhabi, Doha, Sharjah or Muscat — a huge share of the US-to-India market that already changes planes in the Gulf.

A few practical notes. Confirm your exact airport on the ticket: "Mumbai" will soon mean two distinct airports with no quick transfer between them, and arriving at the wrong one is a missed-flight risk. If your itinerary splits across CSMIA and NMIA, leave generous connection time and check baggage rules carefully. And watch the phased rollout: as carriers add NMIA routes, fares on competitive Gulf sectors should soften, which is good news for families booking multiple seats home.

The bigger story is structural. Mumbai's airport monopoly is ending, and for a diaspora that flies BOM in large numbers every winter, more capacity eventually means more choice, more direct routes and less time spent stranded at a single overloaded terminal."""

# ============================================================================
# ARTICLE 2 — Vietnam weighs visa-free for Indians as Thailand reverses course
# ============================================================================
body2 = """Southeast Asia's visa map is being redrawn, and Indian travellers are at the centre of it. As Thailand quietly walks back the visa-free entry that fuelled an Indian tourism boom, Vietnam is moving in the opposite direction — actively weighing visa-free access for Indian passport holders as it chases one of Asia's fastest-growing outbound markets.

The contrast is stark. After a Cabinet resolution on May 19, 2026, Thailand ended the 60-day visa-free arrangement for Indian tourists that had been in place for two years. Indian visitors now face either an e-visa or a Visa on Arrival, with a 2,000-baht VOA fee that industry groups warn will hit large group bookings hardest. That matters because India is one of Thailand's strongest inbound markets: arrivals rose from 2.2 million in 2024 to more than 2.5 million in 2025, with projections above 3 million in 2026 — driven heavily by destination weddings in Phuket, Krabi and Phang Nga. Tourism coalitions in the Andaman provinces have publicly demanded a reversal, fearing a multi-billion-baht hit to the high-value wedding and MICE segments.

Vietnam sees an opening. The country welcomed roughly 750,000 Indian tourists last year, and its tourism ministry has signalled it wants both more Indian visitors and higher-spending ones. Visa-free entry for Indians — which would follow similar liberalisation by Sri Lanka and, until recently, Thailand — has been floated at the highest levels. For now, Indian passport holders still need an e-visa (valid up to 90 days, single or multiple entry) or a visa on arrival, and the easy 30-day exemption on Phu Quoc island remains the simplest legal shortcut. But the direction of travel is clear.

## The NRI angle

For Indian Americans, Southeast Asia is the natural "halfway" holiday — a place to meet parents flying from India, host a destination wedding, or break up the long haul home with a few days of beaches and food. Which country makes entry painless increasingly decides where those trips, and that spending, land.

A crucial point many NRIs miss: your US visa or green card does not unlock Vietnam or Thailand the way it unlocks Mexico, several Caribbean nations or parts of Latin America. Indian passport holders are judged on the Indian passport for Southeast Asian entry, so the e-visa paperwork applies regardless of US residency. That makes the policy direction in Hanoi and Bangkok directly relevant to diaspora planning, not an abstraction.

The practical takeaway for 2026: if you are organising a large family gathering or a wedding, Vietnam's trajectory is friendlier and its costs lower, while Thailand has just added a fee and a step. Vietnam's air connectivity is also expanding fast — Vietnamese carriers are opening new international routes, including long-haul links to Europe and the US — which makes multi-city itineraries combining a Vietnam leg with an India trip more feasible than they were even a year ago.

## What to watch

Three things will determine whether Vietnam becomes the diaspora's new default. First, whether Hanoi converts the visa-free proposal into actual policy for Indian passport holders, or keeps the relatively painless e-visa as the standard. Second, whether Thailand reverses its May decision under pressure from the Andaman tourism lobby — a restoration of the 30- or 60-day exemption would reset the competition overnight. Third, fees: the difference between a free entry and a 2,000-baht-per-head VOA charge is trivial for a couple but meaningful for a 200-guest wedding party.

For now, the smart move is flexibility. Book refundable where you can, confirm the current entry rule the week you fly rather than the month you book, and remember that Phu Quoc's no-visa-needed exemption gives Vietnam a genuine edge for a quick beach reset. The broader lesson for NRIs is that Southeast Asia's visa rules are now a moving target — and the country that keeps the door easiest open is the one that will win the diaspora's holidays."""

# ============================================================================
# ARTICLE 3 — India's 2026 immigration rules and mixed-nationality NRI families
# ============================================================================
body3 = """A set of amendments to India's immigration rules, notified on June 1, 2026, has flown largely under the radar — but they reshape the compliance fine print for exactly the kind of cross-border family that defines the modern diaspora. The Immigration and Foreigners (Amendment) Rules, 2026 tighten registration deadlines for long-staying foreign nationals and, importantly for NRIs, rewrite the reporting rules for children born in India to a foreign or mixed-nationality parent.

For Indian Americans, the relevant phrase is "foreign national." A US citizen of Indian origin, an OCI cardholder's American spouse, and an American-born child are all foreign nationals in the eyes of Indian immigration law, even when one parent holds an Indian passport. That is why these technical-sounding changes deserve a closer read before the next long winter trip home.

## What actually changed

The headline change is the removal of the 14-day grace period for registration. Previously, a foreign national who overstayed the permitted period had a short cushion before registration became mandatory. That cushion is gone. Now, foreign nationals on visas allowing a maximum 180-day stay who intend to remain beyond that window must register with the Foreigners Registration Officer (FRO) before the 180-day period expires — not after. The same applies to longer-validity visas that cap any single stay at 180 days: register before day 180 if you plan to stay longer, whether continuously or cumulatively across the calendar year. Extensions beyond 180 days will be granted only in "emergent circumstances," a deliberately narrow standard.

The second change is more welcome, and directly relevant to mixed families. The amendment introduces an exception to the child-reporting requirement: where either parent is an Indian citizen and intends for the child to retain Indian citizenship, the parents no longer have to notify the FRO of the child's birth in India. Under the earlier framework, that notification was required. At the same time, a new obligation appears at the other end — if a child born in India later acquires foreign citizenship while still living in India, the parents must inform the FRO within 30 days.

## The NRI angle

Most diaspora visits run well under 180 days, so for the typical three-week trip home, nothing changes. The rules bite for a specific and growing group: NRIs who spend extended stretches in India — retirees splitting the year between countries, professionals on long sabbaticals, parents who base themselves in India for several months to care for ageing relatives, and anyone settling in for a half-year or longer.

For those travellers, the disappearance of the 14-day grace period is the practical headline. The safe rule is simple: if you hold a foreign passport and there is any chance you will cross the 180-day line, register with the FRO before you hit it, not after. Treat 180 days as a hard wall, not a soft target, because the new "emergent circumstances" test for extensions leaves little room for casual overstays.

The child-reporting change is genuinely good news for the many diaspora couples where one spouse is an Indian citizen. A baby born during a stay in India, where the family intends the child to keep Indian citizenship, no longer triggers an FRO notification — one less piece of bureaucracy at an already busy moment. But the flip side matters too: if your India-born child later takes US citizenship while living in India, the clock starts on a 30-day reporting duty.

## What to do

Three steps. First, know your visa's stay limit — OCI cardholders have broad freedoms, but foreign-passport-holding family members on standard visas do not, and the 180-day rule turns on the visa's terms. Second, if a long stay is likely, calendar the 180-day mark and register early; the grace period that used to forgive a late filing is gone. Third, keep documentation of citizenship intentions for India-born children, because the new exception and the new 30-day rule both turn on which citizenship the child holds and when.

None of this should deter a long visit home. But the diaspora's defining feature — families and children split across passports — is precisely what these amendments touch, and a few minutes of planning now avoids an awkward conversation with an FRO later."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Mumbai's Second Airport Goes International on July 15 — Starting With the Gulf Routes NRIs Use Most",
        "subheadline": "Navi Mumbai International Airport opens overseas operations with short-haul Gulf flights, easing the congestion that has long plagued the diaspora's trips home.",
        "slug": make_slug("navi-mumbai-airport-international-flights-july-15-gulf-nri"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "A second Mumbai international airport gives the four-million-strong US diaspora redundancy when CSMIA backs up, a closer gateway for those with roots in Navi Mumbai and Pune, and the capacity that could eventually attract direct long-haul routes home.",
        "tags": ["travel", "airlines", "airports", "mumbai", "nri"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Curly Tales — NMIA To Start International Flights From July 15", "url": "https://curlytales.com/india/trending/nmia-to-start-international-flights-from-july-initial-operations-to-serve-the-gulf-region/"},
            {"name": "The Times of India (via Curly Tales) — NMIA international and cargo operations", "url": "https://timesofindia.indiatimes.com/"},
        ]),
        "score_total": 80,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/62/Navi_Mumbai_Airport_%2896252%29.jpg/3840px-Navi_Mumbai_Airport_%2896252%29.jpg",
        "image_caption": "The lotus-inspired terminal of Navi Mumbai International Airport, set to begin international operations on July 15, 2026.",
        "image_attribution": "Wikimedia Commons",
        "body": body1,
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Vietnam Courts Indian Travelers Just as Thailand Slams the Door — and the Diaspora's Wedding Trips Are Up for Grabs",
        "subheadline": "Hanoi is weighing visa-free entry for Indian passport holders even as Bangkok ends its 60-day exemption, redrawing where NRI families take their Southeast Asia holidays.",
        "slug": make_slug("vietnam-visa-free-indians-thailand-reversal-nri-southeast-asia"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "Southeast Asia is the diaspora's natural halfway holiday and destination-wedding hub, and because a US visa does not unlock Vietnam or Thailand for Indian passport holders, which country keeps entry easiest directly shapes where NRI families spend and gather.",
        "tags": ["travel", "visa", "vietnam", "thailand", "nri"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Travel And Tour World — Thailand Tourism Under Pressure as Visa Policy Shift Hits Indian Wedding Travel", "url": "https://www.travelandtourworld.com/"},
            {"name": "Vietcetera — Vietnam Considers Visa-Free Entry For Indians Following Sri Lanka, Thailand", "url": "https://vietcetera.com/"},
            {"name": "Wego Travel Blog — Vietnam Visa-Free Countries 2026 and Phu Quoc Rules", "url": "https://blog.wego.com/"},
        ]),
        "score_total": 76,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/7/79/Ha_Long_Bay_in_2019.jpg",
        "image_caption": "Limestone karsts rise over Vietnam's Ha Long Bay, one of the destinations drawing growing numbers of Indian travelers.",
        "image_attribution": "Wikimedia Commons",
        "body": body2,
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India Just Tightened Its Stay Rules — Why NRI Families With US-Citizen Spouses and Kids Should Read the Fine Print",
        "subheadline": "New June 2026 amendments scrap the 14-day registration grace period and rewrite birth-reporting rules for children of mixed-nationality couples.",
        "slug": make_slug("india-immigration-amendment-rules-2026-180-day-fro-mixed-family-nri"),
        "category": "travel",
        "vertical": "immigration",
        "diaspora_angle": "The diaspora's defining trait is families split across passports, and these amendments touch exactly that group — foreign-passport spouses and children on long stays in India now face a hard 180-day registration wall and rewritten birth-reporting rules.",
        "tags": ["travel", "visa", "immigration", "oci", "nri"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Bar and Bench — India's 2026 Immigration Rules: Stricter registration and new reporting for children of foreign nationals", "url": "https://www.barandbench.com/leading-questions/indias-2026-immigration-rules-stricter-registration-and-new-reporting-for-children-of-foreign-nationals"},
            {"name": "Ministry of Home Affairs — Immigration and Foreigners (Amendment) Rules, 2026", "url": "https://www.mha.gov.in/"},
        ]),
        "score_total": 74,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a3/Indian_Passport_03.jpg/1280px-Indian_Passport_03.jpg",
        "image_caption": "An Indian passport; new 2026 immigration rules reshape registration and child-reporting duties for foreign nationals staying long-term in India.",
        "image_attribution": "Wikimedia Commons",
        "body": body3,
    },
]

# Word count sanity check
for art in articles:
    wc = len(art["body"].split())
    print(f"  · {art['slug']} — {wc} words")
    if wc < 400:
        print(f"    ⚠️ WARNING: under 400 words!")

print("---- inserting ----")
for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

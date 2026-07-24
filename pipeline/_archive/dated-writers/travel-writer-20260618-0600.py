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
        "headline": "Air India Is Putting Its Newest A350 on the New York Run — and the Old US Cabins Are Finally Going Away",
        "subheadline": "The widebody that defines the airline's relaunch now flies Delhi to JFK and Newark, pushing upgraded interiors onto 60% of Air India's US flights.",
        "slug": make_slug("air-india-a350-delhi-new-york-newark-us-cabins-nri"),
        "category": "travel",
        "vertical": "aviation",
        "diaspora_angle": "For the hundreds of thousands of Indian Americans flying the Delhi–New York corridor every year, the A350 swap means the difference between Air India's tired old seats and a genuinely competitive flat-bed cabin on the longest leg of the trip home.",
        "tags": ["travel", "airlines", "air india", "a350", "new york"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Indian Eye", "url": "https://theindianeye.com/"},
            {"name": "Airways Magazine", "url": "https://airwaysmag.com/"},
            {"name": "ch-aviation", "url": "https://www.ch-aviation.com/"}
        ]),
        "score_total": 80,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/49/%28GBR-London%29_Air_India_Airbus_A350-941_VT-JRB_%40_EGLL_2025-06-18.jpg/1280px-%28GBR-London%29_Air_India_Airbus_A350-941_VT-JRB_%40_EGLL_2025-06-18.jpg",
        "image_caption": "An Air India Airbus A350-900 on approach, the widebody now being rolled out on Delhi–New York and Newark routes",
        "image_attribution": "Wikimedia Commons",
        "body": """Air India is deploying its flagship Airbus A350 on the Delhi–New York JFK and Delhi–Newark routes, the airline confirmed this week — a move that finally brings its best long-haul cabin to the single busiest corridor between India and the United States.

For the Indian diaspora, this is the upgrade that has been promised since the Tata Group took the airline back in January 2022. Until now, the carrier's flagship transatlantic and US flights leaned on older, refurbished Boeing 777s and 787s, with inconsistent seats and entertainment systems that lagged Gulf and European rivals. The A350 changes the math.

## What is actually changing

The A350-900 is the aircraft Air India built its relaunch identity around: lie-flat business seats with direct aisle access, a dedicated premium economy cabin, larger overhead bins, quieter cabins and new inflight entertainment screens. By moving it onto the Delhi–New York pair, the airline says roughly 60 percent of all its US flights will now feature new or upgraded cabin interiors.

That is the number worth circling. Air India operates around 51 weekly flights to the United States, serving New York JFK, Newark, Washington Dulles, Chicago O'Hare and San Francisco. Getting the majority of those flights onto refreshed cabins removes the gamble passengers have lived with for years — booking Air India and not knowing until boarding whether you would get a modern flat bed or a decade-old recliner.

## Why New York first

New York is not a sentimental choice. The New York metro and the broader tri-state area hold one of the densest Indian American populations in the country, and the Delhi–New York market is among the highest-yield routes Air India flies. Putting the newest hardware where the most premium-paying NRIs are concentrated is a straightforward commercial decision.

It also matters because of how punishing the route has become. With Pakistani airspace closed to Indian carriers, Air India's Delhi–New York flights now route over a longer northern path, pushing block times well past 15 hours — around two hours longer than before the closure. On a flight that long, the difference between an old cabin and an A350 is not a luxury; it is the difference between arriving wrecked and arriving functional.

## The catch NRIs should plan around

A few realities temper the excitement. First, aircraft assignments on Air India have a history of changing at short notice — equipment swaps for maintenance or operational reasons can still drop an older jet onto a flight that was sold as an A350. Travellers who care about the cabin should check the aircraft type close to departure and again at check-in.

Second, the longer airspace-driven routing means the schedule is tighter than the route maps suggest. Connections at Delhi onward to Tier-2 cities — Hyderabad, Ahmedabad, Kochi, Amritsar — should be built with generous buffers, because a delayed ultra-long-haul arrival cascades fast.

Third, Mumbai travellers are not part of this particular upgrade. Air India runs three-class Boeing 777-300ERs on Mumbai–JFK and Mumbai–Newark, with eight first-class suites and 40 business beds. Those are strong cabins in their own right, but they are a different product from the A350, and the experience between the two India gateways is not identical.

## The bigger picture

The deployment is part of Air India's Vihaan.AI transformation, the multi-year plan to drag the carrier's fleet and service up to global standard. The airline has committed to a 250-strong Airbus order and is steadily inducting new widebodies, but retrofitting a legacy fleet takes years, and the US network has been at the back of the queue while Europe and domestic routes were sorted first.

For Indian Americans who have spent the last few years quietly defaulting to Emirates, Qatar Airways or United for the trip home, the A350 on New York is the first concrete reason in a while to give the national carrier another look. The nonstop convenience was always there. Now the cabin is starting to match it.

The advice for the summer and Diwali booking rush: if you are flying Delhi–New York, search specifically for A350-operated flights, lock in early, and treat the aircraft type as part of the fare you are paying for — not an afterthought."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Thailand Just Made Itself More Expensive for Indian Travelers — and the Wedding Season Is About to Feel It",
        "subheadline": "Bangkok scrapped 60-day visa-free entry for Indians and added a fee-based e-visa, and the Andaman tourism lobby warns of an 8-billion-baht hit to the Indian wedding market.",
        "slug": make_slug("thailand-india-visa-change-wedding-season-nri-cost"),
        "category": "travel",
        "vertical": "visa-policy",
        "diaspora_angle": "Thailand has long been the default, low-friction destination wedding and group-travel pick for Indian families on both sides of the ocean — and the new fee-and-paperwork regime hits exactly the big multi-guest trips that NRI families fly in for.",
        "tags": ["travel", "visa", "thailand", "weddings"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/"},
            {"name": "VisaVerge", "url": "https://www.visaverge.com/"}
        ]),
        "score_total": 74,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0f/Banana_beach_Phuket_2017_-_02.jpg/1280px-Banana_beach_Phuket_2017_-_02.jpg",
        "image_caption": "Banana Beach in Phuket, Thailand, one of the Andaman-coast destinations central to the Indian wedding-tourism market",
        "image_attribution": "Wikimedia Commons",
        "body": """Thailand has quietly made itself harder and costlier to visit for Indian passport holders, and the country's own tourism industry is sounding the alarm. After removing the 60-day visa-free entry that Indians had enjoyed, Bangkok has shifted to an e-visa and Visa on Arrival system carrying an added fee of around 2,000 baht — and a coalition of 13 private-sector tourism organisations across the Andaman region now warns the change could cost Thailand more than 8 billion baht, concentrated in the high-value Indian wedding and group-travel segment.

For the Indian diaspora, this is not abstract policy. Thailand has been the path-of-least-resistance destination for the kind of large, multi-day, multi-guest events that NRI families specialise in: destination weddings, milestone birthdays, extended-family reunions where relatives fly in from the US, the Gulf, the UK and India all at once.

## What changed

Until recently, Indians could enter Thailand visa-free for up to 60 days — an unusually generous window that made it easy to plan long celebrations and tack on a holiday. That window is gone. Travellers now face an e-visa application or Visa on Arrival, plus the new fee. The friction is twofold: the direct cost, and the planning overhead of getting paperwork and approvals lined up for a large group with fixed event dates.

The Andaman lobby — representing operators across Phuket, Krabi and Phang Nga — has laid out a tiered set of demands. First, restore visa-exemption rights for Indian tourists for at least 30 days on a reciprocity basis. Failing that, waive the Visa on Arrival fee for Indians and expand e-visa capacity. They have also floated a dedicated Group Wedding Visa with decisions issued within three working days, and asked Thailand's foreign ministry to negotiate a full bilateral visa-exemption agreement by the third quarter of 2026.

## Why the wedding market is the pressure point

Destination weddings are uniquely lucrative and uniquely sensitive to this kind of change. A single Indian wedding can mean dozens of hotel rooms held for a week, catering, local transport, event services and extended pre- and post-event stays by guests. That is precisely the segment that moves on certainty: planners book venues a year out, and they will not gamble a 200-guest event on visa friction when neighbouring countries are courting them.

That competition is real. Malaysia, Vietnam and the UAE have all leaned into visa-easy positioning for Indian travellers, and Malaysia in particular has been overtaking Thailand as a favourite for exactly this reason. When the default option adds cost and paperwork, the marginal wedding party shifts elsewhere — and once a planner has run a smooth event in Langkawi or Da Nang, the loyalty follows.

## What it means for NRIs planning a trip

If you are an Indian American with a Thailand trip or event on the calendar, a few practical points:

- Build in the visa step. The era of showing up with just a passport is over for now. Apply for the e-visa well ahead, and factor the fee into per-guest budgets you share with family.
- Watch the policy track. The Andaman coalition's push, and Thailand's own 33-million-arrivals target for 2026, create real pressure for Bangkok to soften the rules. A reversal or fee waiver is plausible before peak season — so confirm the current regime close to your travel date rather than relying on what was true last year.
- Price the alternatives honestly. If your event is still flexible, it is worth pricing Malaysia and Vietnam side by side. Both offer comparable beaches and resort infrastructure with lighter entry requirements for Indians right now.
- US visa holders have other levers. NRIs on US visas already enjoy easier access to several destinations; for a beach-and-celebration trip, that can widen the shortlist beyond Southeast Asia entirely.

The broader story is that visa policy has become a competitive weapon across Asia, and Indian travellers — among the fastest-growing and highest-spending outbound markets in the world — are the prize everyone is fighting over. Thailand's bet is that its beaches and brand are strong enough to absorb the friction. Its own tourism industry is not convinced. For NRI families planning the next big celebration, the smart move is to keep options open until Bangkok shows its hand."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "If You Renew an Indian Passport or OCI in the UAE, Your Service Center Is About to Change",
        "subheadline": "From July 1, Al Hind Tours and Travels takes over Indian passport, visa and OCI processing across the UAE, replacing BLS International and SGIVS Global.",
        "slug": make_slug("india-uae-passport-oci-service-provider-al-hind-nri"),
        "category": "travel",
        "vertical": "consular-services",
        "diaspora_angle": "The UAE holds one of the largest overseas Indian communities on earth, and passport, OCI and PCC renewals are routine chores for millions there — so a provider switch reshapes where they file, how they book, and how long it takes.",
        "tags": ["travel", "visa", "uae", "oci", "passport"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Travel + Leisure Asia", "url": "https://www.travelandleisureasia.com/"},
            {"name": "Travelobiz", "url": "https://travelobiz.com/"},
            {"name": "Gulf Business", "url": "https://gulfbusiness.com/"}
        ]),
        "score_total": 72,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/18341554/pexels-photo-18341554.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "The Dubai skyline at twilight; the UAE hosts one of the world's largest overseas Indian communities",
        "image_attribution": "Pexels",
        "body": """Indians in the United Arab Emirates are about to file their passport and consular paperwork through a new company. From July 1, 2026, Al Hind Tours and Travels LLC takes over Indian passport, visa, OCI and related consular services across the UAE, the Embassy of India in Abu Dhabi has confirmed — ending a long run by incumbent BLS International and SGIVS Global.

The change matters because of scale. The UAE is home to one of the largest overseas Indian populations anywhere, and the affected services are the ones that touch nearly every family: passport renewals, visa applications, Overseas Citizen of India (OCI) cards, Police Clearance Certificates (PCC), surrender certificates, Global Entry Programme verification and document attestation. These are not edge cases; they are the routine bureaucratic chores of expatriate life.

## The timeline

The handover is staged to avoid a cliff edge. BLS International and SGIVS Global will continue to accept and process applications until June 30, 2026. Any application submitted on or after July 1 will be handled through Al Hind's centres. Crucially, anything filed before the cutover stays with the existing providers under the current system — so applications already in the pipeline are not disrupted.

The appointment followed a competitive tender. According to official notices and local reporting, financial bids from four shortlisted firms — Al Hind, DU Digital Global, SGIVS Global and VFS Global — were opened on March 30, with Al Hind declared the lowest financial bidder and awarded the contract. The embassy has said it will ensure a smooth transition and continue to provide accessible, high-quality consular services to the Indian community.

## Why diaspora families should pay attention now

For NRIs in the UAE — and for the broader Indian American community with relatives, business or property ties there — the practical effects are concentrated in the first few weeks of the switch. Provider changes rarely alter eligibility rules or processing requirements. What they do change is the operational layer: where you go, how you book an appointment, what the fees are, and how fast the queue moves.

That operational layer is exactly where things wobble during a transition. New centre locations, fresh appointment-booking systems and re-staffed counters can mean tighter availability and slower turnaround in the early days, even when the underlying rules are unchanged. Anyone with a time-sensitive need — a passport expiring before a planned trip, an OCI card required for a child's travel, a PCC needed for a job or immigration filing — should plan around that.

## What to do

A few concrete steps:

- If your renewal can be done before June 30, consider filing it now through BLS or SGIVS rather than waiting for the new system to settle.
- If you already hold an appointment with BLS or SGIVS before the cutover, keep it — proceed as planned.
- If your timeline runs into July, hold off on booking until Al Hind publishes its centre locations, appointment procedures, fees, operating hours and support contacts. Those details are expected to roll out in the weeks ahead.
- Use only official channels. Updates will come through the Embassy of India in Abu Dhabi and the Consulate General of India in Dubai. Avoid third-party agents promising shortcuts during a transition window — that is precisely when misinformation and overcharging tend to spike.

## The wider context

Consular outsourcing transitions are not new across the Gulf, but they are consequential because of how many people they touch. For the Indian community in the UAE, the documents handled here are the connective tissue of cross-border life — the OCI card that lets a child enter India without a visa, the PCC that unlocks a green-card or citizenship step, the passport renewal that keeps a family mobile.

The good news is that the rules themselves are not changing, only the company administering them. The risk is purely timing. NRIs who treat the July 1 switch as a deadline rather than a footnote — and who get ahead of it where they can — will sail through. Those who leave a critical renewal to chance in the transition weeks may find the queue longer than they bargained for."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"OK  {art['slug']}")
    except Exception as e:
        print(f"ERR {art['slug']}: {e}")

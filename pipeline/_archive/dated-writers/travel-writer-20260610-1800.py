#!/usr/bin/env python3
"""Travel writer – 2026-06-10 18:00 UTC batch"""
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
    # ─── ARTICLE 1: Ladakh Tourism Boom ───
    {
        "id": str(uuid.uuid4()),
        "headline": "Ladakh Just Recorded Its Biggest Tourism Surge in History — and NRIs Planning a Summer Trip Should Book Now",
        "subheadline": "Visitor arrivals jumped 44 percent in five months and May alone saw a 121 percent spike, overwhelming hotels and homestays across the territory.",
        "slug": make_slug("ladakh-record-tourism-boom-nri-summer-booking"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "NRIs visiting family in north India often tack on a Ladakh trip — but this summer, the window between booking and sold-out is the narrowest it has ever been.",
        "tags": ["travel", "ladakh", "tourism", "india", "adventure"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Travel and Tour World", "url": "https://www.travelandtourworld.com/news/article/xag5jc72haxn/"},
            {"name": "Agoda / Travel and Tour World", "url": "https://www.travelandtourworld.com/news/article/indian-travellers-abandon-crowded-cities/"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8b/Pangong_Tso_2.jpg/1280px-Pangong_Tso_2.jpg",
        "image_caption": "Pangong Tso lake in eastern Ladakh, one of the territory's most visited landmarks",
        "image_attribution": "Wikimedia Commons",
        "body": """Between January and May 2026, the high-altitude territory of Ladakh welcomed 117,546 visitors — a 44 percent surge over the 81,827 who arrived during the same window last year. The numbers alone are striking. The speed at which they materialised is extraordinary.

May was the inflection point. A record 72,834 visitors flooded into the region in a single month, up 121 percent from 32,927 in May 2025. Hotels, homestays, and adventure camps hit historic occupancy highs. Local guides were stretched thin. Airlines scrambled to add frequency on Leh routes. For a territory that spent most of 2025 reeling from floods, terror threats, and social unrest, the turnaround has been nothing short of dramatic.

## What's Driving the Surge

Three forces converged this year. First, India's domestic travel market is booming. Domestic arrivals — which account for the vast majority of Ladakh's visitors — climbed 46 percent, crossing the one-lakh mark. Second, the region's infrastructure recovery has been faster than expected. Vital overland highways severed by the 2025 Jammu & Kashmir floods were restored, and tightened security protocols helped rebuild confidence after the Pahalgam attack. Third, a sophisticated "Destination Ladakh" marketing blitz — social media campaigns, travel vlogger partnerships, and visibility at global travel expos — reached millions of potential travelers.

International visitors contributed too, with a 15.5 percent rise. The primary source markets: the United States, Thailand, and Vietnam.

## The Agoda Numbers Confirm It

Separately, data from digital travel platform Agoda shows accommodation searches for Leh have surged 143 percent year-on-year. Mumbai residents are leading the charge with a 158 percent jump, followed by Delhi at 140 percent and Hyderabad at 106 percent. The data confirms what anyone trying to book a Leh guesthouse this month already knows: availability is vanishing fast.

Kasol and McLeod Ganj are riding the same wave. Searches for Kasol are up 90 percent, driven largely by Mumbai and Kolkata travellers. McLeod Ganj has seen a 171 percent surge from Hyderabad alone. The broader story is clear: Indian travellers are trading beaches and cities for mountains, trekking trails, and cool air.

## Why NRIs Should Pay Attention

If you are visiting family in Delhi, Chandigarh, or anywhere in northern India this summer, a Ladakh detour is probably on your list. It should be — the Markha Valley and Nubra Valley treks are world-class, Pangong Tso is as surreal as the photos suggest, and the food and monastery culture are genuinely worth the altitude.

But the logistics are tighter than ever. Peak season runs June through September, and the surge means accommodation in Leh town is booking out weeks in advance. A few practical notes for NRI families planning a trip:

**Book early, book directly.** Leh hotels and homestays listed on platforms like Agoda and MakeMyTrip are filling fast. For boutique properties and high-altitude camps, booking directly often gets you better rates and confirmed availability.

**Fly, don't drive — at least one way.** The Manali-Leh highway is spectacular but gruelling (about 12 hours by road). With airlines adding flights into Kushok Bakula Rimpochee Airport, flying into Leh and road-tripping out (or vice versa) is the smartest split.

**Altitude is real.** Leh sits at 3,500 metres. Give yourself a full acclimatisation day before any trekking or driving to higher passes. AMS (acute mountain sickness) is the single biggest trip-killer for visitors who fly in and try to do too much on day one.

**Check permits.** Indian citizens with valid ID can access most areas, but Pangong Tso, Nubra Valley, and Tso Moriri require Inner Line Permits, available online or at the DC office in Leh. OCI cardholders face additional restrictions in some border areas — confirm before you commit.

The territory that nearly lost its tourism season in 2025 has come roaring back. The question for NRIs is not whether Ladakh is worth visiting this summer. It is whether you can still get a room."""
    },

    # ─── ARTICLE 2: India 180-Day Stay Rules Tightened ───
    {
        "id": str(uuid.uuid4()),
        "headline": "India Just Killed the 14-Day Grace Period for Foreign Visitors — and NRI Families Should Read the Fine Print",
        "subheadline": "New immigration rules require foreign nationals to register before hitting 180 days, not after. Visa extensions are now restricted to genuine emergencies only.",
        "slug": make_slug("india-180-day-stay-rule-tightened-nri-foreign-spouse"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "For the estimated 1.5 million NRIs married to non-Indian spouses — and the many more who host foreign friends and family for extended India visits — this rule change creates a compliance trap that did not exist two weeks ago.",
        "tags": ["travel", "visa", "india", "immigration", "nri"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "VisaVerge", "url": "https://visaverge.com/immigration/india-foreigner-registration-rules-2026/"},
            {"name": "Travelobiz", "url": "https://travelobiz.com/india-tightens-180-day-stay-rules-for-foreign-visitors-makes-visa-extensions-harder/"},
            {"name": "Bharat Horizon", "url": "https://bharathorizon.com/india-tightens-visa-rules-180-day-visitors-must-register-before-expiry/"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/4922356/pexels-photo-4922356.jpeg",
        "image_caption": "An open passport displaying travel stamps — the kind of documentation foreign visitors to India must now manage more carefully",
        "image_attribution": "Pexels",
        "body": """India's Ministry of Home Affairs quietly amended the Immigration and Foreigners Rules on June 1, 2026 — and the change, buried in a Gazette notification, has immediate implications for anyone bringing a non-Indian spouse, partner, or friend to India for an extended stay.

The core shift is simple but consequential: the 14-day grace period for foreign nationals to register with immigration authorities after completing 180 days in India has been abolished. Under the old rules, a foreign visitor who crossed the 180-day mark could still register within the following two weeks. That buffer is gone. Registration must now be completed *before* the 180-day period expires.

## What Changed, Precisely

The amended Rule 12 replaces the earlier language — "within fourteen days after the expiry of one hundred and eighty days of his arrival in India" — with a harder deadline: "any time before the expiry of the said period of one hundred and eighty days."

The practical difference matters. Under the old regime, a foreign spouse visiting family in India could arrive, settle in, and address the paperwork after the 180-day mark if needed. The grace period absorbed the inevitable bureaucratic delays — FRRO appointments, document gathering, form submissions. Now, every day past 180 without prior registration is a compliance violation.

The government also tightened visa extension rules. Permission to stay beyond 180 days will now be granted "only in emergent circumstances" — a phrase that replaces what was previously a more routine administrative process. The message is clear: India wants foreign visitors to treat their visa duration as a hard boundary, not a starting point for negotiation.

## Who This Affects

The amended rules apply across the board: tourists, students, employees, medical visitors, researchers, volunteers, and — critically for the diaspora — foreign spouses and family members of Indian citizens and NRIs.

Consider the scenario that plays out in thousands of NRI households every year. An American, British, or Canadian spouse accompanies their Indian-origin partner for an extended family visit — a few months with the in-laws in Bengaluru, a wedding season in Jaipur, a summer with the kids in Kerala. On a standard tourist visa, these visits regularly stretch toward the 180-day window. The old grace period gave these families a safety net. That net is now gone.

Employers, universities, hospitals, and even hotels that host foreign nationals also bear compliance consequences. A missed registration deadline can create cascading problems: complications with visa extensions, exit clearance issues, and flags in the system that affect future travel to India.

## What NRIs Need to Do

If you have a foreign-national family member currently in India on a long-stay visit, check their arrival date and start the registration process immediately if they are anywhere near the 150-day mark. Do not wait.

**Know the portal.** Registration is handled through the Bureau of Immigration's online foreigner registration portal or via the FRRO mobile app. The process requires passport details, visa information, proof of address in India, and a photograph. Start early — the system is not known for its speed.

**Calendar the deadline.** Count 180 days from the date of arrival stamped in the passport. Mark a reminder at day 150. If there is any possibility of staying past 180, begin the registration process by then at the latest.

**Understand the extension reality.** Visa extensions are no longer routine. If your family member's visit may exceed the visa period, explore options before arrival — not after. A longer-validity visa at the outset is better than an emergency extension request that may be denied.

**Birth registration exemption.** One bright spot in the amended rules: if a child is born in India to a couple where one parent is an Indian citizen and they wish to retain Indian citizenship for the child, the requirement to notify the FRRO within 30 days has been waived.

## The Bigger Picture

India's immigration apparatus has been moving steadily toward stricter compliance for several years. The DigiYatra biometric system at airports, the e-Arrival Card for inbound visitors, and now the 180-day registration tightening all point in the same direction: a country that is digitising its borders and reducing discretionary leniency.

For the millions of NRIs whose lives bridge two countries — and whose families often include non-Indian members navigating India's visa system — these are not abstract policy changes. They are the kind of rules that, if missed, turn a family visit into a bureaucratic nightmare. Read the fine print. Set the calendar alert. Start the paperwork early."""
    },

    # ─── ARTICLE 3: EU EES System Impact on NRI Travelers ───
    {
        "id": str(uuid.uuid4()),
        "headline": "Europe's New Biometric Border System Is Live — and NRIs Flying to Schengen This Summer Could Face Six-Hour Lines",
        "subheadline": "The EU's Entry/Exit System has tripled passport processing times across 29 countries. With IATA warning of record delays, here's what Indian travelers need to know before boarding.",
        "slug": make_slug("eu-ees-biometric-border-nri-schengen-summer-delays"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "Indian passport holders already face longer Schengen processing than visa-free nationals. The EES adds a new biometric layer on top — making NRIs among the hardest-hit travelers at European borders this summer.",
        "tags": ["travel", "europe", "schengen", "visa", "nri", "airport"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Travel and Tour World", "url": "https://www.travelandtourworld.com/news/article/wttc-warns-europe-ees/"},
            {"name": "The Travel", "url": "https://www.thetravel.com/iata-warns-american-travelers-6-hour-airport-lines-europe-ees/"},
            {"name": "Travel and Tour World", "url": "https://www.travelandtourworld.com/news/article/spain-joins-eu-ees-biometric/"},
            {"name": "LinkedIn / EES Analysis", "url": "https://www.linkedin.com/pulse/entry-exit-system-biometric-border-worth-cost/"}
        ]),
        "score_total": 80,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/2612113/pexels-photo-2612113.jpeg",
        "image_caption": "Travelers queue at an airport terminal — a scene likely to become more common at European borders this summer",
        "image_attribution": "Pexels",
        "body": """If you hold an Indian passport and have a European summer trip on the calendar, prepare for the longest immigration queues of your life.

The European Union's Entry/Exit System — EES — is now fully operational across all 29 Schengen countries, and its first full summer season is shaping up to be a stress test for airports, airlines, and the 41 million non-EU visitors expected to cross European borders in the coming months. The International Air Transport Association (IATA) has warned that processing delays could stretch to six hours at peak times. One-third of surveyed travelers say they would reconsider visiting Europe altogether if waits regularly exceed three to four hours.

For Indian nationals, who already undergo Schengen visa checks before they even board, the EES adds another layer of friction at the border itself.

## How It Works

EES replaces the traditional passport stamp with a digital record. Every non-EU traveler entering the Schengen Area — whether on a visa or visa-free — must now provide biometric data: fingerprints and a facial scan. The information is stored centrally for up to three years (five years for overstay flags) and checked against security databases on entry and exit.

The system began a phased rollout in October 2025 and reached full implementation in April 2026. Between October and April, it registered over 52 million border crossings. Entry was refused more than 27,000 times, including to nearly 700 individuals flagged as security threats.

Those numbers sound impressive until you do the math. That is a 0.05 percent refusal rate — a massive biometric apparatus processing tens of millions of law-abiding travelers to intercept a fraction measured in per-mille. The security argument is real, but the operational cost is enormous.

## The Delay Problem

Here is the number that matters to anyone standing in a queue at Charles de Gaulle or Schiphol: processing time per passenger has gone from 20–25 seconds under the old stamp system to 70–90 seconds with EES. That sounds manageable until three transatlantic flights land within the same hour.

IATA's warning is not hypothetical. At major hubs like Barcelona, Amsterdam, Milan, Brussels, and Paris, border control staffing has not kept pace with the new processing demands. Technical glitches with biometric kiosks and central IT connectivity have compounded the problem. Dover, the busiest Channel crossing between the UK and France, is bracing for particularly severe congestion as car and ferry passengers face the same biometric checks.

A survey of 2,500 travelers from four major markets (US, UK, Canada, Australia) found that 33 percent would be less likely to visit Schengen countries if extended waits become routine. Among British travelers, that figure rises to 39 percent. The WTTC estimates that persistent delays could put up to 41 million arrivals and $45 billion in tourism revenue at risk.

## Why NRIs Get Hit Hardest

Most American, British, Canadian, and Australian passport holders enter the Schengen Area visa-free. Their EES interaction is limited to the biometric registration at the border itself — annoying, but a one-time process per trip.

Indian passport holders face a double burden. First, the Schengen visa application: documents, appointments, processing fees, and a refusal rate that runs well above the global average for many consulates. Then, upon arrival in Europe, the EES biometric registration on top of the standard visa verification. Each layer adds time. Each layer adds friction.

For NRI families who hold Indian passports — or who are traveling with Indian-passport-holding parents or relatives — the cumulative delays this summer could be significant.

## What You Can Do

The EU has introduced the **Travel to Europe** mobile app, which allows visitors to pre-register passport data and upload a selfie within 72 hours of travel. Pre-registration does not replace the border check, but it can reduce time at the kiosk. Download it before you fly.

**Arrive early.** Not the usual "two hours before international" early. Add a full extra hour on top, especially if landing at a major hub during peak hours (10 AM to 2 PM local time is typically worst).

**Avoid peak hubs if you can.** Smaller Schengen entry points — Helsinki, Ljubljana, Tallinn — tend to have shorter queues than Barcelona, Amsterdam, or Paris CDG. If your final destination is flexible, routing through a less congested airport could save hours.

**Keep biometric-ready documents accessible.** You will need your passport and boarding pass at the kiosk. Glasses, hats, and face coverings will need to come off for the facial scan. Have everything ready before you reach the booth.

**Build buffer into connections.** If you are connecting through a Schengen hub from a non-Schengen origin — say, flying London to Delhi via Frankfurt — the EES check happens at your first Schengen entry point. A tight 90-minute connection that used to work may no longer be safe. Book minimum two-hour layovers.

## The Bigger Picture

The EES is not going away. Europe has committed to digital borders, and the system will only get more embedded over time. The first summer is always the worst — kiosks will be upgraded, staffing will improve, and the pre-registration app will gain adoption. But for travelers crossing European borders in June, July, and August 2026, the disruption is real and immediate.

If Europe is on your summer itinerary, plan accordingly. Download the app. Arrive early. And pack your patience alongside your passport."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

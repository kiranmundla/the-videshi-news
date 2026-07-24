#!/usr/bin/env python3
"""Travel writer — June 26, 2026 evening run.

Two articles:
1. Navi Mumbai International Airport launching international flights July 15
2. India resumes Bangladesh tourist visas after two-year freeze
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
    r = requests.post(
        f"{SB_URL}/rest/v1/{table}", headers=HEADERS, json=data, timeout=30
    )
    r.raise_for_status()
    return r.json()


now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def make_slug(base):
    slug = base.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug.strip())
    return slug[:70].rstrip("-") + "-" + datetime.now().strftime("%Y%m%d")


# ── Article 1: Navi Mumbai International Airport ──────────────────────────

art1_body = """Mumbai's second airport is about to cross an inflection point. Navi Mumbai International Airport — the Zaha Hadid-designed greenfield hub that opened its domestic terminal last Christmas — will launch its first international passenger flights on July 15, with Air India Express operating services to Abu Dhabi.

The move gives the Mumbai Metropolitan Region a second international gateway for the first time, easing pressure on the perpetually congested Chhatrapati Shivaji Maharaj International Airport (CSMIA) and opening a new corridor between western India and the Gulf.

## The Launch Details

Air India Express will be the first carrier to fly international passengers out of Navi Mumbai. The airline has confirmed two weekly flights to Abu Dhabi starting July 15, operating on Wednesdays and Fridays, with a third Sunday frequency added from July 29. IndiGo is also expected to launch international services from the airport, though specific routes and dates have not yet been announced.

International cargo will begin simultaneously, with freighter operations ramping up to 18 weekly flights. The airport's initial international focus is on short-haul Gulf routes — a deliberate choice, given the massive India-UAE passenger corridor and the comparatively lighter regulatory lift required for regional operations.

NMIA Chairman Captain BVJK Sharma said at the BCBA Logistics Conclave in Mumbai that customs authorities have already inspected the airport, with remaining approvals being processed. A trade notice from customs is expected around July 5.

## From Zero to 20,000 Passengers a Day

The airport has scaled remarkably since its December 2025 launch. What began with 46 daily flights now stands at 149 daily departures and arrivals, connecting 46 domestic destinations. The airport handles roughly 20,000 passengers daily and has crossed 2 million total since opening. By year-end, authorities expect 50,000 daily passengers and 300 daily flights.

Air India's wider group plans for NMIA are ambitious: 55 daily departures by mid-2026, including up to five international flights, scaling to 60 daily departures by winter. Campbell Wilson, Air India's CEO, has publicly positioned NMIA not just as a point-to-point connector but as "one of the country's key global transit hubs for passengers and cargo."

The airport's proposed Terminal 2, originally designed for 30 million passengers annually, is being redesigned as a 50-million-passenger facility. "We are planning a bigger terminal," Sharma said. "We will open up in parts based on demand and supply."

## Why This Matters for the Diaspora

Mumbai is the default homecoming airport for a vast swathe of the Indian diaspora — Maharashtrians, Gujaratis, Goans, and South Indians who connect through CSMIA for the last leg home. And CSMIA is, by any measure, at capacity. It operates from a single main runway handling over 900 movements a day, making it one of the world's busiest single-runway commercial airports. Delays cascade. Slots are scarce. Airlines have struggled to add frequencies on high-demand routes.

A second international airport fundamentally changes this calculus. For NRIs in the Gulf — the UAE alone is home to an estimated 3.5 million Indians — the NMIA–Abu Dhabi service offers a second routing option into the Mumbai region, potentially at lower fares. Air India Express is already listing Navi Mumbai–Dubai connecting fares from ₹12,788 on aggregator platforms, competitive with CSMIA-origin flights.

For the broader diaspora, NMIA's international ramp-up is a story to watch. Gulf routes are the opening play; long-haul connections to Europe, North America, and East Asia will follow as the airport builds traffic and earns the certifications needed for extended operations. The Zaha Hadid-designed terminal — with its iconic lotus-inspired roof and expansive, naturally lit interiors — signals that this is not a budget overflow facility but a serious international hub in the making.

Connectivity infrastructure is catching up, too. The Mumbai Trans Harbour Link (MTHL), opened in 2024, connects Navi Mumbai to South Mumbai in roughly 20 minutes by road. Metro and suburban rail links are in various stages of planning and construction, and coastal road projects will further reduce access times from across the Mumbai Metropolitan Region.

For NRI families flying into Mumbai this summer, it is worth checking whether Navi Mumbai options exist for outbound or connecting segments. The airport is still early-stage, but it is growing faster than anyone's blueprint anticipated."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Mumbai's Second Airport Is About to Go International — and the Gulf Routes Land First",
    "subheadline": "Navi Mumbai International Airport will launch its first overseas passenger flights to Abu Dhabi on July 15, giving the congested Mumbai Metropolitan Region a second international gateway just seven months after opening.",
    "slug": make_slug("navi-mumbai-airport-international-flights-july-gulf-nri"),
    "category": "travel",
    "vertical": "aviation",
    "diaspora_angle": "NRIs flying through Mumbai — one of the diaspora's busiest gateways home — finally get a second international airport option, starting with Gulf routes that serve the 3.5 million Indians in the UAE.",
    "tags": ["travel", "airports", "aviation", "Mumbai", "NMIA", "NRI", "Air India Express"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com/economy/logistics/navi-mumbai-airport-launch-international-flights-from-july-15/article69353052.ece"},
        {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/corporate/navi-mumbai-airport-to-launch-international-operations-on-july-15"},
        {"name": "Further Arabia", "url": "https://furtherarabia.com/navi-mumbai-abu-dhabi-air-india-express/"},
        {"name": "Air India Newsroom", "url": "https://www.airindia.com/in/en/about-us/newsroom/air-india-group-unveils-robust-plan-for-operations-from-navi-mumbai-international-airport.html"},
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/62/Navi_Mumbai_Airport_%2896252%29.jpg/1280px-Navi_Mumbai_Airport_%2896252%29.jpg",
    "image_caption": "The Zaha Hadid-designed terminal at Navi Mumbai International Airport",
    "image_attribution": "Wikimedia Commons",
    "body": art1_body,
}

# ── Article 2: India resumes Bangladesh tourist visas ─────────────────────

art2_body = """India will resume tourist visa services for Bangladeshi nationals on June 28, ending a nearly two-year freeze that began when Sheikh Hasina's government fell in August 2024. The announcement, made by India's new High Commissioner to Bangladesh, Dinesh Trivedi, at a media briefing in Dhaka on Thursday, marks the most tangible step yet in the slow normalization of India-Bangladesh relations under Prime Minister Tarique Rahman's government.

For the Bengali diaspora scattered across the United States — concentrated in the New York-New Jersey metro, Houston, the Dallas-Fort Worth corridor, and the Bay Area — the thaw quietly reopens something more personal than a diplomatic channel: the family corridor between Kolkata and Dhaka.

## What Froze, and Why

The visa suspension was one of several measures India took after the August 2024 political upheaval in Bangladesh. The fall of Hasina, a long-time Indian ally, and the subsequent interim government's adversarial posture toward New Delhi led to a broad cooling of bilateral ties. Tourist visas were among the first casualties.

Medical visas and certain categories of business travel were processed on a case-by-case basis, but the mass tourist channel — used by hundreds of thousands of Bangladeshis visiting India annually for everything from Durga Puja pilgrimages to medical treatment in Kolkata hospitals — went effectively dark.

The political landscape has since shifted. Rahman's elected government, inaugurated in February, has sought to recalibrate Bangladesh's relationships with both India and China. Trivedi's visa announcement was timed with Rahman's meeting with Chinese Premier Li Qiang in Beijing, where China pledged deeper cooperation on trade, infrastructure, and supply chains — a signal that India is accelerating practical gestures to match diplomatic engagement.

## The Kolkata-Dhaka Corridor

The India-Bangladesh border is one of South Asia's busiest people-to-people crossings. The Petrapole-Benapole land border — roughly 80 kilometers from Kolkata — handles millions of crossings annually in normal times. Kolkata's Netaji Subhas Chandra Bose International Airport serves as the primary air gateway, with multiple daily flights to Dhaka, Chittagong, and Sylhet.

The visa freeze disrupted all of this. Medical tourism, which drives a significant portion of Bangladeshi travel to India — particularly to hospitals in Kolkata, Chennai, and Vellore — slowed to a trickle. Religious pilgrimages to Kolkata's Kalighat and Dakshineswar temples, a fixture of the Bengali Hindu calendar on both sides of the border, were curtailed. Cultural exchange — literary festivals, theatrical collaborations, academic conferences — went quiet.

The resumption of tourist visas does not instantly restore pre-2024 volumes. Visa processing infrastructure needs to ramp back up, and applicants will face the usual queue at Indian missions in Dhaka and Chittagong. But the signal is considerable: India is reopening, and the corridor is coming back to life.

## The NRI Dimension

This matters to the Indian American community in ways the headline does not capture. Bengali Americans — among the larger South Asian sub-communities in the US — often maintain extended family networks that span both Kolkata and Dhaka. Partition-era migrations, intermarriage, and shared cultural traditions mean that a single family's Durga Puja gathering might draw relatives from Jackson Heights, Salt Lake (Kolkata), and Dhanmondi (Dhaka).

During the visa freeze, NRIs planning India visits could not easily coordinate family reunions that included Bangladeshi relatives. A Kolkata wedding that would normally draw guests from Dhaka had to proceed without them. A medical consultation at a Kolkata hospital that a Bangladeshi relative needed became a bureaucratic ordeal rather than a routine border crossing.

With tourist visas resuming June 28, these barriers drop. NRIs flying to Kolkata this autumn — and the festive season from Durga Puja through Diwali is peak travel time — can once again plan gatherings that include family from across the border.

The diplomatic context remains delicate. India's decision is as much about countering China's courtship of the Rahman government as it is about people-to-people ties. But for the Bengali diaspora, the geopolitics is secondary. What matters is that the corridor between Kolkata and Dhaka is open again — just in time for pujo season."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "India Reopens Tourist Visas for Bangladesh After a Two-Year Freeze — and the Kolkata–Dhaka Corridor Exhales",
    "subheadline": "Starting June 28, India will issue tourist visas to Bangladeshi nationals again, ending a suspension rooted in the fall of Sheikh Hasina. For the Bengali diaspora in the US, the thaw reopens a cross-border family lifeline just ahead of pujo season.",
    "slug": make_slug("india-resumes-bangladesh-tourist-visas-kolkata-dhaka-nri"),
    "category": "travel",
    "vertical": "immigration",
    "diaspora_angle": "Bengali Americans with family networks spanning Kolkata and Dhaka can once again plan cross-border reunions, as India's tourist visa resumption reopens the busiest people-to-people corridor in South Asia.",
    "tags": ["travel", "visa", "India", "Bangladesh", "NRI", "Bengali diaspora", "Kolkata"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "The Hindu Business Line / Bloomberg", "url": "https://www.thehindubusinessline.com/news/india-to-resume-bangladesh-tourist-visas-after-two-year-pause/article69413937.ece"},
        {"name": "Ministry of External Affairs, India", "url": "https://www.mea.gov.in/"},
    ]),
    "score_total": 72,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/c/cb/Howrah_bridge_at_night.jpg",
    "image_caption": "Howrah Bridge over the Hooghly River in Kolkata, the closest Indian gateway to Bangladesh",
    "image_attribution": "Wikimedia Commons",
    "body": art2_body,
}


# ── Insert ────────────────────────────────────────────────────────────────

articles = [art1, art2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

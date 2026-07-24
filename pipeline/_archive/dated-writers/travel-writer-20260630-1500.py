#!/usr/bin/env python3
"""
Travel Writer — 2026-06-30 15:00 PDT
3 articles: Passport fee hike, Germany/France transit visa drop, SWISS Bengaluru-Zurich launch
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


# ─────────────────────────────────────────────
# ARTICLE 1: Passport Fee Hike from July 1
# ─────────────────────────────────────────────

article1_body = """India's Ministry of External Affairs notified revised passport fees on June 20, replacing Schedule IV of the Passports Rules, 1980. The new rates take effect on July 1, and they apply to every passport application filed from that date — fresh, renewal, or replacement, normal or Tatkal.

The headline numbers: a standard 36-page passport for adults now costs ₹2,500, up from ₹1,500 — a 67 per cent increase. The 60-page booklet, favoured by frequent travellers who burn through visa pages, rises to ₹3,500. Tatkal fees climb even more steeply: ₹5,000 for a 36-page passport and ₹6,000 for 60 pages.

## What the new fee table looks like

| Category | Normal | Tatkal |
|---|---|---|
| Adult 36-page (fresh/renewal) | ₹2,500 | ₹5,000 |
| Adult 60-page (fresh/renewal) | ₹3,500 | ₹6,000 |
| Minor (under 18) 36-page | ₹1,750 | ₹4,250 |
| Lost/damaged replacement 36-page | ₹5,000 | ₹7,500 |
| Lost/damaged replacement 60-page | ₹6,000 | ₹8,500 |
| Minor lost/damaged 36-page | ₹4,250 | ₹6,750 |

The sharpest sting is in the replacement column. If your parent in India loses a passport — or it gets damaged in the monsoon — the normal-track replacement is now ₹5,000, more than triple the earlier fee. The Tatkal replacement route hits ₹7,500.

## Why NRIs should pay attention now

For the roughly 4.4 million Indian Americans, passport renewals are rarely just personal errands. They are family logistics. Thousands of NRIs manage the renewal process for aging parents and in-laws remotely, often relying on the Tatkal pathway when a trip comes together quickly or a passport is close to expiry. That Tatkal pathway just got 43 per cent more expensive.

The timing also compounds. India's new OCI rules, which took effect in May, introduced a USD 25 late-update penalty for cardholders who fail to upload new passport details within three months of issuance. Fresh OCI registration itself jumped to USD 275. So an NRI family renewing a parent's passport, updating their own OCI record, and perhaps getting a minor child's first passport is looking at meaningfully higher costs across the board.

## What hasn't changed

Passport validity remains the same — 10 years for adults, five for minors. The application process, including the Passport Seva portal and regional Passport Seva Kendras, is unchanged. The fee hike does not affect consular services at Indian missions abroad; separate fee schedules apply for NRIs applying from the US, UK, or elsewhere.

## The bottom line

If anyone in your family needs a passport renewal and is not in a rush, the window to file at the old rate has already closed — the notification was gazetted on June 20 and allows no grace period past July 1. For NRIs planning India trips later this year, factor the new costs into the family logistics budget. And if you haven't updated your OCI record after your last passport renewal, the three-month clock is ticking on that USD 25 penalty too."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "India's Passport Fees Jump Tomorrow — Here's the New Price List for Every NRI Family",
    "subheadline": "A standard passport costs 67 per cent more from July 1, Tatkal fees climb to ₹5,000, and the replacement penalty has more than tripled — just as OCI costs are rising too.",
    "slug": make_slug("india-passport-fee-hike-july-nri-family-guide"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "Millions of NRIs manage passport renewals for parents in India remotely; the Tatkal pathway many rely on just got 43% costlier, and new OCI update penalties add to the financial burden.",
    "tags": ["travel", "passport", "visa", "india", "nri", "fees"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Storyboard18", "url": "https://storyboard18.com/"},
        {"name": "Outlook Business", "url": "https://outlookbusiness.com/"},
        {"name": "Patna Press", "url": "https://patnapress.com/"},
        {"name": "LatestLY / ANI", "url": "https://latestly.com/"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a3/Indian_Passport_03.jpg/1280px-Indian_Passport_03.jpg",
    "image_caption": "An Indian passport booklet — fees for fresh applications and renewals rise sharply from July 1",
    "image_attribution": "Wikimedia Commons",
    "body": article1_body,
}


# ─────────────────────────────────────────────
# ARTICLE 2: Germany & France Drop Transit Visa
# ─────────────────────────────────────────────

article2_body = """For years, Indian passport holders transiting through Frankfurt or Paris needed an Airport Transit Visa — the Type A Schengen visa — even if they never set foot outside the terminal. That requirement added roughly €60 in fees plus service charges, five to fifteen working days of processing, and an appointment at a visa centre, all to sit in a departure lounge for three hours.

Both hurdles are now gone. France scrapped its transit visa for Indian nationals on April 10. Germany followed on June 3, after the decision was published in the Federal Law Gazette a day earlier. The German move came out of discussions between Prime Minister Narendra Modi and Chancellor Friedrich Merz during the latter's visit to India in January.

## What has actually changed

Indian travellers can now connect through any French or German airport — including the major hubs at Frankfurt, Munich, and Paris Charles de Gaulle — without a transit visa, provided they stay airside and are heading to a destination outside the Schengen zone. The exemption is automatic; no separate application is needed. Just a valid passport and an onward boarding pass.

The policy does not, however, allow entry into France or Germany. If your layover requires you to clear immigration, change airports, collect checked baggage, or stay overnight, you still need the appropriate Schengen visa. And if your final destination is within the Schengen area, the standard visa requirements apply.

## Why this matters for NRIs on the US–India corridor

Frankfurt is Lufthansa's fortress hub, and Charles de Gaulle is Air France's. Together, they handle an enormous share of one-stop traffic between North America and India. The Lufthansa Group alone operates more than 70 weekly flights between India and Europe, and it explicitly welcomed the German decision as a way to make journeys "via key German hubs more seamless for Indian passengers."

For NRIs in the US, the practical impact is straightforward: routing through Frankfurt or Munich no longer requires a separate visa application weeks in advance. That makes Lufthansa, SWISS, and Austrian Airlines meaningfully more convenient as alternatives to the Gulf carriers or nonstop options.

The timing is not accidental. Lufthansa is deploying its new Allegris premium cabins on Boeing 787-9 services from Delhi and Hyderabad. SWISS is launching a new nonstop Bengaluru–Zurich service five times weekly from October, with First Class on every flight. And extra capacity is being added on the Delhi–Zurich and Mumbai–Munich corridors. The transit visa removal clears a friction point just as the Lufthansa Group is scaling up its India capacity.

## The broader pattern

India has been steadily negotiating transit visa waivers across Europe. The Germany and France exemptions follow similar moves by the UAE and other Gulf states years ago, which made Dubai and Doha the default connecting hubs for Indian travellers partly because of the zero-visa-hassle factor. Europe is now levelling that playing field.

For Indian passport holders, who still face Schengen visa requirements for actual entry into EU countries, the transit waivers are a practical improvement rather than a transformation. But for the millions of NRIs who fly between the US and India several times a year, one fewer visa application — and one fewer appointment, fee, and processing delay — adds up quickly."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "Frankfurt and Paris Just Got Easier — Germany and France Drop Transit Visas for Indian Passports",
    "subheadline": "Indian travellers can now connect through Europe's two biggest hub airports without a transit visa, and the Lufthansa Group is scaling up India capacity to take advantage.",
    "slug": make_slug("germany-france-drop-transit-visa-indian-passport-nri"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "NRIs flying between the US and India routinely transit through Frankfurt or Paris — the transit visa removal saves time, money, and paperwork on every trip.",
    "tags": ["travel", "visa", "germany", "france", "europe", "airlines", "lufthansa", "nri"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "TravelBiz Monitor", "url": "https://travelbizmonitor.com/"},
        {"name": "Outlook Traveller", "url": "https://outlooktraveller.com/"},
        {"name": "LiveMint", "url": "https://www.livemint.com/"},
        {"name": "Breaking Travel News", "url": "https://breakingtravelnews.com/"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/14/Airport%2C_Frankfurt_%28P1180126%29.jpg/1280px-Airport%2C_Frankfurt_%28P1180126%29.jpg",
    "image_caption": "Frankfurt Airport terminal — Indian travellers can now transit through Germany without a visa",
    "image_attribution": "Wikimedia Commons",
    "body": article2_body,
}


# ─────────────────────────────────────────────
# ARTICLE 3: SWISS Bengaluru-Zurich Launch
# ─────────────────────────────────────────────

article3_body = """Swiss International Air Lines will begin nonstop flights between Bengaluru and Zurich on October 28, operating five times a week with First Class on every departure. It is the airline's first route to southern India and its third Indian destination after Delhi and Mumbai.

The schedule is built for the business corridor. The westbound LX 141 departs Bengaluru at 4:50 AM and lands in Zurich at 10:50 AM the same day — early enough to connect onward to London, Frankfurt, or Amsterdam before lunch. The eastbound LX 140 leaves Zurich at 1:20 PM and arrives in Bengaluru at 2:55 AM the next morning. Flights operate daily except Tuesdays and Thursdays from Bengaluru, and daily except Mondays and Wednesdays from Zurich.

## Why Bengaluru, and why now

Bengaluru is not just India's tech capital — it is the Lufthansa Group's fastest-growing market in southern India. With Frankfurt and Munich services already running through Lufthansa, SWISS becomes the group's third European gateway from the city. Kevin Markette, the group's senior director for South Asia, called the launch a response to "strong demand from business travellers, the technology sector, premium leisure customers, and the growing Indian diaspora across Europe."

The airline is deploying its award-winning service across all three cabins, including the premium SWISS Senses cabin product on its expanding A350 fleet. Zurich Airport, meanwhile, serves as a compact, efficient hub with short minimum connection times — a contrast to the sprawling terminals at Frankfurt or Heathrow that eat up transfer time.

## The NRI connection

For the estimated 150,000-plus Indian Americans with roots in Karnataka and surrounding states, Bengaluru has always been an awkward city to reach from the US. Most itineraries routed through Delhi or Mumbai, adding a domestic connection and hours of travel time. SWISS's Zurich link changes the calculus: a Bay Area tech worker flying home to Bengaluru can now connect through Zurich with a single ticket and a 90-minute layover, reaching 60-plus European and North American destinations through the Lufthansa Group network.

Bengaluru's Kempegowda International Airport has also scaled rapidly, now connecting 78 domestic destinations. For NRIs whose families are in Mysuru, Mangaluru, Hubli, or Coimbatore, the one-stop domestic transfer after an international arrival in Bengaluru is often smoother than the Delhi or Mumbai alternative.

## The bigger picture

SWISS's entry is part of a broader European push into India. The Lufthansa Group now operates more than 70 weekly flights on India–Europe routes. Lufthansa is rolling out its new Allegris cabins on 787-9 services from Delhi and Hyderabad. Extra A380 capacity is coming on the Mumbai–Munich corridor. And Germany's recent removal of transit visa requirements for Indian nationals — effective June 3 — has cleared one of the last friction points for passengers connecting through German airports.

Air India and IndiGo are expanding in the opposite direction, adding European routes of their own. But for now, SWISS's Bengaluru launch represents something Indian flyers rarely get on southern India routes: a premium product with First Class, competitive connections, and the quiet efficiency that Swiss aviation does well.

Bookings are open on swiss.com and through travel agencies. The winter timetable runs from October 25, 2026, through March 27, 2027."""

article3 = {
    "id": str(uuid.uuid4()),
    "headline": "SWISS Is Bringing First Class to Bengaluru — and Bookings Are Open Now",
    "subheadline": "Five weekly nonstops to Zurich from October mean southern India's tech capital finally gets a premium European gateway — with First Class on every flight.",
    "slug": make_slug("swiss-bengaluru-zurich-nonstop-first-class-nri"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "For the 150,000+ Indian Americans with Karnataka roots, SWISS's Zurich link means connecting to Bengaluru through a compact hub instead of routing through Delhi or Mumbai.",
    "tags": ["travel", "airlines", "swiss", "bengaluru", "zurich", "europe", "lufthansa", "nri"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "SWISS Newsroom", "url": "https://newsroom.swiss.com/"},
        {"name": "Breaking Travel News", "url": "https://breakingtravelnews.com/"},
        {"name": "LatestLY / ANI", "url": "https://latestly.com/"},
        {"name": "SWISS.com", "url": "https://www.swiss.com/"}
    ]),
    "score_total": 75,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fd/HB-JNB_Boeing_777-300_Swissair_LHR_4.11.20.jpg/1280px-HB-JNB_Boeing_777-300_Swissair_LHR_4.11.20.jpg",
    "image_caption": "A SWISS Boeing 777-300 — the airline will launch Bengaluru-Zurich nonstops from October with First Class service",
    "image_attribution": "Wikimedia Commons",
    "body": article3_body,
}


# ─────────────────────────────────────────────
# INSERT ALL
# ─────────────────────────────────────────────

articles = [article1, article2, article3]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['headline'][:80]}...")
        print(f"   slug: {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"   Response: {e.response.text[:300]}")

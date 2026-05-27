#!/usr/bin/env python3
"""Travel writer — 2026-05-27 22:00 UTC run."""

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


# ─── ARTICLE 1 ───────────────────────────────────────────────────────

article1_body = """Air India just posted its worst annual loss since the Tata Group bought it back from the government in 2022 — and the number is staggering enough to make every NRI who flies the airline regularly sit up.

The carrier reported a net loss of ₹220 billion ($2.4 billion) for the fiscal year ending March 31, 2026, according to people familiar with the matter cited by Reuters. That figure blew past an internal estimate of $1.6 billion that had circulated in January, and it raises hard questions about the pace and viability of the airline's five-year turnaround plan.

## A Year of Compounding Disasters

The fiscal year actually started well. Air India posted operating profits in the opening weeks of April 2025. Then, in rapid succession, three external shocks hit.

First, Pakistan closed its airspace to Indian carriers in May 2025 following a brief military conflict. That forced Air India's North America and Europe flights onto longer, costlier routes — with fuel stops in Vienna and Copenhagen adding hours and millions in costs. The ban, now in its sixth consecutive week of the latest enforcement phase, is bleeding the airline roughly ₹200 million per day. Total cost from the airspace closure alone: over ₹8.2 billion, according to The Diplomatic Insight.

Second, a Boeing 787 Dreamliner crash near Ahmedabad in June 2025 killed more than 240 people. The disaster forced service reductions on both international and domestic routes and inflicted reputational damage that the airline is still working to contain.

Third, the ongoing Iran-driven conflict in the Middle East — a region that accounts for roughly 16% of Air India's total capacity — sent jet fuel prices surging past $150 per barrel. Flights to Europe and North America were diverted onto even longer routes, compounding the Pakistan airspace problem.

On top of all this, U.S. tariffs on Indian goods and tighter foreign-worker visa approvals have dampened passenger demand on the airline's most important revenue routes.

## The Turnaround Plan Is Under Siege

Air India's ambitious five-year transformation strategy, codenamed "Vihaan," was supposed to return the airline to profitability by 2027. The carrier has ordered more than 500 new aircraft, launched a $400 million cabin retrofit of its Dreamliner fleet, and opened its first international lounge at SFO.

But the numbers tell a different story. Technical incidents hit their highest recorded rate in at least 14 months in January 2026 — 1.09 per 1,000 flights, up from 0.26 in December 2024. India's civil aviation ministry told lawmakers that 82.5% of the 166 Air India aircraft analyzed since January 2025 had recurring technical defects, compared with 36.5% for IndiGo.

CEO Campbell Wilson announced last week that he intends to step down later in 2026, without naming a successor or a specific date.

## What This Means for the 4 Million NRIs Who Fly to India

Air India flies more nonstop routes between the US and India than any other carrier — Newark, SFO, Chicago, JFK, Washington Dulles, Seattle, and Dallas. For the Indian diaspora, it has been the default choice for two decades.

But the airline has already cut 22% of its domestic flights for June through August. It has trimmed international routes too, and Reuters noted that those cuts "have created room for foreign airlines to add more flights to and from India." Tata Group and Singapore Airlines, which holds a 25.1% stake, are in talks for a capital injection — but the size may fall short of the carrier's full requirements.

For NRIs, the practical implications are blunt: expect fewer seats, higher fares, and continued reliability concerns on Air India this summer. The carrier's financial distress may also slow the rollout of new routes and cabin upgrades that the diaspora has been waiting for.

The one silver lining: foreign carriers like Cathay Pacific, Singapore Airlines, and Emirates are stepping into the gaps, adding India frequencies as Air India pulls back. Competition may cushion the fare impact — but for NRIs loyal to nonstop service on Air India, the alternative is a connection through Hong Kong, Singapore, or an increasingly disrupted Dubai.

Tata Group bet $2 billion on turning Air India around. Three years in, the bill has more than doubled — and the diaspora that depends on this airline is watching the meter run."""


article2_body = """As India's two largest carriers retreat from international routes under the weight of $150-a-barrel jet fuel and a Pakistan airspace ban, a quieter story is unfolding on the tarmac: foreign airlines are moving in.

Reuters reported this week that Air India's cuts to its international schedule "have created room for foreign airlines to add more flights to and from India." IndiGo, meanwhile, has slashed 17% of its planned international capacity for the summer. The withdrawal is the most significant opening for foreign carriers into India's aviation market in years — and NRIs stand to benefit.

## Cathay Pacific's India Push

Cathay Pacific has been the most aggressive mover. The Hong Kong-based carrier has resumed nonstop flights to three Indian tech hubs — Chennai (three times weekly), Hyderabad (three times weekly, on Mondays, Thursdays, and Sundays), and Bengaluru. It also resumed nonstop Hong Kong–Seattle service in March 2026, creating a two-stop routing (Indian city → Hong Kong → Seattle or SFO) that undercuts Gulf hub alternatives by avoiding Middle East airspace entirely.

Hong Kong International Airport, which reopened its expanded Terminal 2 on May 27, handled 5.74 million passengers in March 2026 — a 19.6% year-on-year increase. Europe-linked traffic is rising as passengers reroute away from Dubai and Doha.

For NRIs in the Pacific Northwest and California, the Cathay Pacific routing via Hong Kong is emerging as a real contender: shorter total travel time than routing through the Gulf, and no exposure to Iranian or Pakistani airspace closures.

## Singapore Airlines Doubles Down

Singapore Airlines is also repositioning. The carrier has been increasing non-Gulf service to Europe, routing more traffic through Changi Airport as Dubai's hub role diminishes. SIA holds a 25.1% stake in Air India through the Vistara merger, giving it a unique strategic position: it benefits from Air India's traffic when the Indian carrier is healthy, and captures it directly when Air India pulls back.

The two airlines currently codeshare on 61 routes across 20 countries, but Air India's record $2.4 billion annual loss now casts uncertainty over the pace of that commercial expansion.

For NRIs flying to Europe or Southeast Asia, Singapore Airlines via Changi offers what Gulf carriers increasingly cannot: routing that avoids the conflict zones that have turned Middle East hubs into scheduling minefields.

## The Numbers Behind the Shift

ICRA, the Indian credit rating agency, projects that international passenger traffic to and from India will grow 7–10% in FY2026, reaching 82–85 million. But domestic traffic growth is at its post-COVID low — just 4–6% — as airlines cut capacity. The divergence matters: international demand remains strong even as Indian carriers shrink supply.

That gap is precisely what foreign airlines are filling. Philippine Airlines, Vietnam Airlines, and Cebu Pacific have also adjusted Asian routes, while Emirates and Qatar Airways — despite scaling back some Gulf services — maintain strong India connectivity due to the sheer size of the diaspora corridor.

The net effect for NRIs is more options, though not necessarily cheaper ones. Jet fuel prices have pushed fares up across all carriers, and the wider routings add flight time. But the competition from foreign carriers should prevent the fare spikes from becoming a monopoly tax.

## What NRIs Should Do This Summer

If you are booking India flights for June through August, the playbook has changed:

**Check Cathay Pacific via Hong Kong.** Nonstop to Chennai, Hyderabad, and Bengaluru, with connections to US West Coast cities. Avoids Gulf and Pakistan airspace.

**Check Singapore Airlines via Changi.** Strong connections to South India and Europe. The SIA-Air India codeshare means you may be able to book through to smaller Indian cities on a single ticket.

**Book flexible fares.** Airlines are adjusting schedules weekly. A non-refundable ticket on a route that gets cut is a guaranteed headache.

**Watch for Akasa Air domestically.** India's fastest-growing budget carrier has been expanding even as IndiGo and Air India contract. For the last-leg domestic connection — say, Delhi to Lucknow or Bengaluru to Kochi — Akasa is increasingly the reliable, affordable option.

The era of the Gulf hub as the default NRI transit point is not over, but it is being seriously challenged for the first time in a decade. For the 4 million Indian Americans who fly home regularly, the competition is welcome — even if the circumstances that created it are not."""


articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Air India Just Posted a $2.4 Billion Loss — and Every NRI Route Is Now on the Table",
        "subheadline": "A Pakistan airspace ban, a fatal crash, and the Iran war have turned Tata's turnaround bet into the airline's worst financial year since privatization. Here's what it means for diaspora travelers.",
        "slug": make_slug("air-india-24-billion-loss-tata-turnaround-nri-routes"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "Air India flies more US-India nonstop routes than any carrier. Its record loss means fewer seats, higher fares, and delayed upgrades on the routes 4 million NRIs depend on most.",
        "tags": ["travel", "airlines", "air india", "tata group", "nri"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/world/india/air-india-indigo-cut-domestic-capacity-new-indian-express-reports-2026-05-27/"},
            {"name": "Bangladesh Monitor", "url": "https://www.bangladeshmonitor.com.bd/news-details/indias-national-carrier-posts-record-annual-loss-seeks-capital-injection-from-investors"},
            {"name": "The Diplomatic Insight", "url": "https://thediplomaticinsight.com/air-india-rs8-2b-loss-pak-airspace-ban/"}
        ]),
        "score_total": 85,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/4/45/VT-JRF_%40_JFK%2C_2024-11-04.png",
        "body": article1_body.strip()
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Foreign Airlines Are Quietly Feasting on India's Aviation Crisis — and NRIs Are the Prize",
        "subheadline": "As Air India and IndiGo slash international flights, Cathay Pacific, Singapore Airlines, and other foreign carriers are expanding India routes at the fastest pace in years.",
        "slug": make_slug("foreign-airlines-india-aviation-crisis-cathay-singapore-nri"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "Foreign carriers are adding India routes as Air India and IndiGo retreat, giving NRIs more options through Hong Kong and Singapore hubs that avoid Gulf and Pakistan airspace disruptions.",
        "tags": ["travel", "airlines", "cathay pacific", "singapore airlines", "nri"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/world/india/air-india-indigo-cut-domestic-capacity-new-indian-express-reports-2026-05-27/"},
            {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/9p6sj555avpe/"},
            {"name": "ICRA", "url": "https://www.icra.in/"},
            {"name": "Cathay Pacific Newsroom", "url": "https://news.cathaypacific.com/"}
        ]),
        "score_total": 78,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/9/9a/Singapore_Airlines_Airbus_A350-941_F-WZFD_to_9V-SMF.jpg",
        "body": article2_body.strip()
    },
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

print(f"\nDone. Published {len(articles)} articles at {now}")

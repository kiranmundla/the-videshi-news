#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-06-28 05:00 PDT run."""

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


now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def make_slug(base):
    slug = base.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug.strip())
    return slug[:70].rstrip("-") + "-" + datetime.now().strftime("%Y%m%d")


# ── Article 1 ──────────────────────────────────────────────────────────
art1_body = """Amazon CEO Andy Jassy flew into New Delhi last week and left with a photograph next to Prime Minister Narendra Modi — and a freshly inked commitment to pour another $13 billion into India's AI and cloud infrastructure. The announcement, made on June 25, lifts Amazon's total planned investment in India to $48 billion between 2026 and 2030, and cements AWS as the country's most aggressive hyperscaler.

The fresh capital is earmarked almost entirely for expanding AWS data centre capacity in Mumbai and Hyderabad, where Amazon plans to offer startups, enterprises, and government agencies access to custom AI chips, managed AI services, and developer tooling. Amazon's total AI and cloud infrastructure commitment through 2030 now exceeds $21 billion — roughly the GDP of Iceland.

## A three-way hyperscaler land grab

Amazon's cheque is the latest in a dizzying sequence of Big Tech bets on Indian data centres. Microsoft's Satya Nadella pledged $17.5 billion for cloud and AI infrastructure last December — the company's single largest investment anywhere in Asia. Google followed with a $15 billion plan to build a 1-gigawatt AI hub in Andhra Pradesh. Together, the three American hyperscalers have now committed more than $53 billion to Indian AI and cloud infrastructure, a figure that would have seemed absurd even two years ago.

The race reflects hard-nosed arithmetic. India's cloud market is expanding at roughly 25% a year, driven by a combination of enterprise digitisation, government procurement of AI services, and a startup ecosystem that now runs almost entirely on cloud rails. With over 900 million internet users and a government aggressively pushing digital public infrastructure — from UPI to DigiLocker to ONDC — the demand for compute capacity is structural, not speculative.

## What this means for Indian tech workers

For the estimated 40,000-plus Indians who work at Amazon globally, a significant number of them on H-1B visas, the investment signals job security. AWS India has been on a hiring spree, with openings for AI deployment engineers, solutions architects, and data centre operations staff listed across Mumbai, Hyderabad, and Bengaluru. The company said it plans to open 20 new fulfilment centres and over 100 last-mile delivery stations within 2026 alone — a pipeline that implies thousands of new positions, though Amazon has not disclosed specific headcount targets.

For NRIs weighing a return to India, the calculus is shifting. AWS's India infrastructure now rivals what was available only in Northern Virginia or Dublin five years ago. Indian engineers building on AWS no longer need to be in Seattle to access the frontier stack — a meaningful change for those whose green card backlogs stretch decades.

## The quick-commerce subplot

Beyond cloud, Amazon is also throwing money at India's quick-commerce war. Amazon Now, its ultra-fast delivery service first developed in India, has reportedly seen orders double every quarter since launch. Jassy called it Amazon India's fastest-growing business unit and said the company plans to expand it to over 300 cities. The service puts Amazon in direct competition with Flipkart, Blinkit, and Zepto in a market where ten-minute grocery delivery has become table stakes.

## The bigger picture

Jassy's rhetoric during the trip was carefully calibrated. He cited Amazon's priorities as "democratising access to AI, digitising small businesses, creating jobs, and enabling exports" — language that maps almost verbatim onto the Modi government's stated economic objectives. He invoked the Prime Minister's vision of a "Viksit and Atmanirbhar Bharat" — developed and self-reliant India — a rhetorical flourish that would not have appeared in an Amazon press release even two years ago.

Amazon's cumulative investment in India since 2010 now exceeds $88 billion. For a country that accounts for a fraction of the company's global revenue, that figure reflects less a current return on investment than a long bet on where the next 500 million digital consumers will come from. For Indian Americans who built their careers in Amazon's Seattle headquarters, it is also an implicit acknowledgement that the market they left behind is now large enough to command the company's single biggest international infrastructure push."""

art1_sources = json.dumps([
    {"name": "The Bridge Chronicle", "url": "https://www.thebridgechronicle.com/tech/amazon-ceo-pm-modi-13-billion-india-ai-cloud-investment-mp99"},
    {"name": "The Register", "url": "https://www.theregister.com/paas-and-iaas/2026/06/25/amazon-pours-another-13b-into-indias-ai-and-cloud-infrastructure/5262067"},
    {"name": "TechCrunch", "url": "https://techcrunch.com/2026/06/25/amazon-ups-india-bet-with-fresh-13b-ai-infrastructure-investment/"},
    {"name": "Barron's", "url": "https://www.barrons.com/articles/why-amazon-is-investing-another-13-billion-in-indias-ai-data-centers/"},
])

# ── Article 2 ──────────────────────────────────────────────────────────
art2_body = """India's ambitious semiconductor programme has a new adversary, and it is not China or TSMC pricing. It is the war in West Asia.

Tata Electronics' $11 billion fabrication plant in Dholera, Gujarat — the crown jewel of India's chip-making ambitions — could face fresh delays as supply chain disruptions from the Middle East conflict ripple through the speciality materials that fabs cannot function without, The Economic Times reported on Sunday. Specialty gases, high-purity chemicals, and critical metals are caught in shipping bottlenecks that have pushed up both costs and lead times.

## The materials nobody talks about

Semiconductor fabrication is an exercise in chemical precision. A modern fab consumes dozens of specialty inputs — helium for cooling and leak detection, bromine for etching, high-purity sulphuric acid for wafer cleaning, and rare earth elements for polishing. Many of these materials are sourced from or shipped through the Middle East.

Qatar, which supplies roughly a third of the world's helium, was forced to halt liquefied natural gas production earlier in the conflict after Iranian strikes on the Ras Laffan industrial complex. Helium is a byproduct of LNG, so when LNG stops, so does helium. Spot prices for the gas more than doubled in the early months of the war. The closure of the Strait of Hormuz further choked shipping lanes through which an estimated 40% of global sulphur exports pass.

The Wall Street Journal reported that established global chipmakers — TSMC, Samsung, SK Hynix — largely weathered the disruption thanks to long-term supply contracts, diversified supplier networks, and on-site storage caverns built over decades. Air Liquide signed a fresh deal to supply industrial gases to SK Hynix; Samsung tapped Air Products for a facility in South Korea. TSMC said it expected no significant production impact.

## India's fabs are not TSMC

The problem is that India's semiconductor projects do not have the luxury of decades-old supplier relationships or massive on-site inventories. Tata Electronics is building India's first commercial chip fab from scratch, with technology licensed from Taiwan's Powerchip Semiconductor Manufacturing Company (PSMC). The facility was initially supposed to produce its first wafer by the end of 2026. That was already pushed to mid-2027 after rare earth supply concerns surfaced last year. The West Asia disruptions now threaten to push that timeline back further.

Micron's assembly and testing facility in Sanand, Gujarat, has also faced construction delays, missing its original end-of-2025 commercial production target. Other projects in the pipeline — CG Power-Renesas-Star, Kaynes Semicon, and the HCL-Foxconn project near Jewar — are in various stages of planning and construction, all of them vulnerable to the same supply chain pressures.

## The NRI investor's dilemma

India's semiconductor push has generated enormous excitement among NRI investors and diaspora professionals. The India Semiconductor Mission's $10 billion incentive programme, combined with state-level subsidies that can cover up to 70% of project costs, made the narrative irresistible: India would finally move from designing chips to making them.

That narrative is not dead, but it is getting a reality check. For the roughly 20% of the world's chip designers who work in India for multinational corporations — at Qualcomm's Hyderabad centre, Intel's Bengaluru campus, AMD's design hubs — the fab delays mean the gap between where chips are designed and where they are manufactured remains wide. For NRI semiconductor professionals who had been weighing a return to India to work in manufacturing, the timeline uncertainty adds a new variable to an already complex decision.

A UBS report published last week projected that India's semiconductor end-demand revenues would double from $54 billion in 2025 to $108 billion by 2030, growing at a 15% compound annual growth rate — faster than the global market. The demand side, in other words, is not the problem. The supply side is.

## What happens next

Industry experts caution that the West Asia disruptions are a stress test, not a death blow. Some bottlenecks have already eased. India's government has been pushing for alternative supply routes and has signed critical mineral agreements with Australia, Chile, and several African nations. Tata Electronics has finalised most of its initial vendor partners on PSMC's recommendation and is building out a dedicated supply-chain team.

But the episode exposes a structural vulnerability that India will have to solve if it wants to be taken seriously as a chip-manufacturing nation. Fabs do not just need subsidies and engineers — they need guaranteed access to a global supply chain of exotic materials, most of which are produced in a handful of countries, many of them in geopolitically unstable regions. The race to build chips in India was always going to be hard. The Middle East just made it harder."""

art2_sources = json.dumps([
    {"name": "Inshorts / Economic Times", "url": "https://inshorts.com/en/news/india-s-chip-projects-face-delays-amid-west-asia-conflict--report-1782629544924"},
    {"name": "Wall Street Journal", "url": "https://www.wsj.com/finance/why-the-middle-east-helium-supply-shock-didnt-hit-chip-makers-471585a0"},
    {"name": "Communications Today", "url": "https://communicationstoday.co.in/west-asia-crisis-a-war-far-from-fabs-is-rattling-the-chip-supply-chain/"},
    {"name": "Livemint", "url": "https://www.livemint.com/technology/tata-aims-to-roll-out-india-made-chips-by-mid-2027-but-rare-earths-crisis-could-derail-plan-11726008421014.html"},
    {"name": "The Indian EYE / UBS", "url": "https://theindianeye.com/by-2030-india-to-double-semiconductor-demand-at-usd-108-billion/"},
])

# ── Articles array ─────────────────────────────────────────────────────
articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Amazon Just Dropped Another $13 Billion on India. The Hyperscaler Land Grab Is Getting Serious.",
        "subheadline": "Andy Jassy's latest pledge lifts Amazon's total India commitment to $48 billion by 2030, making AWS the country's most aggressive cloud and AI infrastructure investor.",
        "slug": make_slug("amazon-jassy-13-billion-india-ai-aws-data-centre"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Amazon employs tens of thousands of Indians on H-1B visas globally. AWS India's infrastructure build-out creates high-paying engineering roles and makes returning to India more attractive for NRI cloud architects.",
        "tags": ["amazon", "aws", "ai-infrastructure", "india-investment", "andy-jassy", "hyperscaler", "data-centre"],
        "urgency": "medium",
        "sources": art1_sources,
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/0/07/Andy_Jassy.jpg",
        "image_caption": "Amazon CEO Andy Jassy, who announced the $13 billion investment after meeting PM Modi in New Delhi",
        "image_attribution": "Wikimedia Commons",
        "body": art1_body,
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "A War Far From Gujarat Is Threatening India's Chip Ambitions",
        "subheadline": "Supply chain disruptions from the West Asia conflict are delaying specialty gases and metals critical to Tata Electronics' Dholera fab, raising fresh doubts about India's semiconductor timeline.",
        "slug": make_slug("west-asia-conflict-india-semiconductor-dholera-delays"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "NRI semiconductor professionals considering a return to India's chip industry face new timeline uncertainty. Diaspora investors bullish on Tata Group's fab ambitions should factor in geopolitical supply risks.",
        "tags": ["semiconductor", "tata-electronics", "dholera", "west-asia", "supply-chain", "india-semiconductor-mission", "chip-fab"],
        "urgency": "medium",
        "sources": art2_sources,
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/cf/Silicon_wafer_researcher.jpg/1280px-Silicon_wafer_researcher.jpg",
        "image_caption": "A researcher inspects a silicon wafer in a semiconductor fabrication cleanroom",
        "image_attribution": "Wikimedia Commons",
        "body": art2_body,
    },
]

# ── Insert ─────────────────────────────────────────────────────────────
for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}  —  {art['headline']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

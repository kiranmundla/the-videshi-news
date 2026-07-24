#!/usr/bin/env python3
"""Videshi Technology Writer — 2 July 2026, 2:00 PM PT"""

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
# ARTICLE 1: Micron Record Quarter
# Beat: A (Indian-Origin Tech Leaders)
# ─────────────────────────────────────────────

article1_body = """Sanjay Mehrotra has spent his career building memory chips. Last week, his company proved that memory is where the money is.

Micron Technology reported fiscal third-quarter revenue of $41.5 billion — a 346 percent increase over the same period a year earlier, and roughly $5.5 billion above what Wall Street had expected. Earnings per share came in at $25.11, crushing the consensus estimate by nearly 18 percent. Gross margins widened to 85 percent, up from 37.7 percent a year ago. The company generated $25.4 billion in operating cash flow in a single quarter.

These are not normal numbers for a chipmaker. They are not normal numbers for any company. For context, Micron's quarterly revenue a year ago was $9.3 billion. The company has more than quadrupled in twelve months.

## The AI memory crunch

The explanation is straightforward, even if the scale is not. Every AI data centre in the world runs on memory — dynamic random-access memory (DRAM) for computation and NAND flash for storage. The explosive build-out of AI infrastructure by hyperscalers like Microsoft, Google, Amazon, and Meta has created a global shortage of both.

Micron's data centre revenues alone exceeded $25 billion in the quarter, an annualised run rate above $100 billion. High-bandwidth memory (HBM), the specialised chips that sit on top of Nvidia and AMD's AI accelerators, has become the single most constrained component in the entire AI supply chain. Micron now has 16 multi-year strategic customer agreements in place, including $22 billion in upfront cash commitments — non-cancellable, take-or-pay contracts that insulate the company from the boom-bust cycles that have historically plagued chipmakers.

Management warned that demand would continue to outstrip supply beyond 2027. The company is spending $27 billion on capital expenditure this fiscal year — nearly double last year — and expects to exceed $40 billion in fiscal 2027.

## The Mehrotra playbook

Mehrotra, who was born in Kanpur and studied at the Indian Institute of Technology (IIT) Delhi before moving to the United States for graduate work at Stanford, co-founded SanDisk in 1988 and led it until its $19 billion acquisition by Western Digital in 2016. He took over Micron in 2017, inheriting a company that was profitable but cyclical and technologically behind Samsung and SK Hynix in key product categories.

His strategy has been patient and capital-intensive: invest in next-generation memory architectures, push into high-value segments like HBM and enterprise SSDs, and lock in long-term customer commitments to smooth out the cycles. It is now paying off in a way few predicted. Micron's stock is up over 300 percent in 2026 alone.

## What this means for India

The results carry a specific resonance for India's semiconductor ambitions. Micron is the only major Western chipmaker currently building a facility on Indian soil — a semiconductor assembly and test plant in Gujarat's Sanand district, backed by up to $2.75 billion in incentives under the India Semiconductor Mission. The Gujarat plant is expected to begin production in 2025 and eventually create thousands of engineering jobs.

If Mehrotra's Micron is now the most profitable chipmaker in the world, India's bet on attracting it starts to look less like industrial policy and more like good timing. The Gujarat facility will not manufacture the HBM chips driving these record numbers — that requires leading-edge fabrication technology that India does not yet possess. But it will handle the assembly, testing, and packaging that turns raw wafers into finished products, a growing bottleneck as memory demand explodes.

For NRI investors who have watched Micron's stock soar, the question is whether the company can sustain this trajectory. The Q4 guidance suggests it can: management expects $50 billion in revenue next quarter, implying full-year sales approaching $130 billion. That would make Micron, led by an IIT Delhi alumnus, one of the twenty largest companies in the world by revenue.

The semiconductor cycle has not been repealed. But Mehrotra may have found a way to ride it differently."""


article1 = {
    "id": str(uuid.uuid4()),
    "headline": "Sanjay Mehrotra's Micron Just Posted $41 Billion in a Single Quarter. The AI Memory Shortage Is That Bad.",
    "subheadline": "The IIT Delhi alumnus delivered the most explosive earnings report in semiconductor history, with revenue up 346 percent and margins wider than most software companies.",
    "slug": make_slug("micron-mehrotra-41b-record-quarter-ai-memory-hbm"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Micron CEO Sanjay Mehrotra, born in Kanpur and an IIT Delhi alumnus, leads a company building a semiconductor facility in Gujarat — India's first major memory chip investment — while delivering record-breaking earnings driven by AI demand.",
    "tags": ["micron", "sanjay-mehrotra", "semiconductors", "ai", "hbm", "india-semiconductor-mission", "gujarat"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Motley Fool", "url": "https://www.fool.com/investing/2026/07/02/micron-technology-has-fantastic-news-for-ai-stock/"},
        {"name": "Zacks Investment Research", "url": "https://www.zacks.com/stock/news/2564132/microns-data-center-business-booms-is-more-upside-left"},
        {"name": "NBC Palm Springs", "url": "https://nbcpalmsprings.com/2026/07/02/ai-stocks-roar-back-after-microns-massive-earnings-beat/"},
        {"name": "MarketBeat", "url": "https://www.marketbeat.com/stocks/NASDAQ/MU/earnings/"}
    ]),
    "score_total": 88,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/d/de/Sanjay_Mehrotra_2025_%28cropped%29.jpg",
    "image_caption": "Sanjay Mehrotra, CEO of Micron Technology and co-founder of SanDisk",
    "image_attribution": "Wikimedia Commons",
    "body": article1_body.strip()
}


# ─────────────────────────────────────────────
# ARTICLE 2: Tata Communications Leadership Overhaul
# Beat: C (Indian Tech Ecosystem)
# ─────────────────────────────────────────────

article2_body = """Tata Communications has replaced nearly its entire C-suite in five months. The question is whether the new team can stop the fires — figuratively and, as it turns out, literally.

On June 30, the company named Rupesh Chokshi as its new chief technology officer, replacing Genius Wong, who resigned citing personal reasons. Chokshi arrives from Akamai Technologies, where he served as senior vice president and general manager of application security, and before that held senior leadership positions at AT&T. On the same day, Tata Communications appointed Vivek Srivastava as executive vice president and business head for cloud and cyber security services.

These are not isolated personnel moves. In May, the company installed Ganesh Lakshminarayanan as its new chief executive. In February, it brought in a new chief financial officer. In the span of less than half a year, virtually every senior leadership role at one of India's most important digital infrastructure companies has changed hands.

## The fire that exposed a fragile backbone

The management overhaul has unfolded against the backdrop of a crisis that few in the Indian diaspora would have expected from a Tata Group company. On June 5, a fire broke out in a battery room on the third floor of Tata Communications' data centre facility at Next-Gen Tower in Delhi's Greater Kailash-I. Two firefighters sustained burn injuries. The blaze was contained by morning, but the damage to the building's infrastructure was extensive.

Within days, the consequences rippled outward. Google Cloud reported that its services across Delhi, Mumbai, and Chennai were experiencing network disruptions and elevated latency — the company's traffic had been routed through the affected facility. Tata Communications confirmed that it activated business continuity protocols and that "a majority of the data for affected customers has been successfully recovered," though some cases required further validation and rebuilding.

For a company that bills itself as the connective tissue of India's digital economy — managing undersea cables, cloud connectivity, and enterprise networking for multinational clients — a fire in a single Delhi facility should not cascade into a multi-city cloud disruption. The incident raised pointed questions about redundancy, power backup design, and physical infrastructure standards at Indian data centres.

## Building for the AI age

The new leadership team inherits a company in the middle of an ambitious expansion. Tata Communications is accelerating investment in AI-ready digital infrastructure, cloud connectivity platforms, and subsea network capacity. In partnership with Microsoft, it is building the I2SEA submarine cable — a 3,600-kilometre undersea fibre-optic link connecting India to Singapore — aimed at meeting surging demand for low-latency data transfer between Indian and Southeast Asian markets.

The company is also expanding its cybersecurity and managed services portfolio, which explains the creation of the new cloud and cyber security division under Srivastava. As Indian enterprises and government agencies move critical workloads to the cloud, the demand for managed security services is growing faster than the available supply of qualified providers.

## What NRIs should watch

For Indian Americans tracking the Tata Group's sprawling portfolio, Tata Communications occupies an unusual position. It is not a consumer brand like Tata Motors or a headline-grabbing play like Tata Electronics' semiconductor foray. It is plumbing — the cables, data centres, and managed services that everything else runs on.

The leadership overhaul suggests that the Tata Group's upper management recognised the gap between ambition and execution at the company. Chokshi's background in application security at Akamai — a firm synonymous with content delivery and cybersecurity infrastructure at massive scale — signals a deliberate shift toward building resilience, not just capacity.

The stock has underperformed this year, weighed down by the data centre fire and management turnover. But the fundamentals of the business — growing enterprise cloud adoption, India's data centre buildout, and the subsea cable expansion — remain strong. The question for investors is whether the new team can execute before the next crisis tests the company's backbone again."""


article2 = {
    "id": str(uuid.uuid4()),
    "headline": "Tata Communications Has Replaced Nearly Every Top Executive in Five Months. A Data Centre Fire Explains Why.",
    "subheadline": "A battery room blaze in Delhi knocked out Google Cloud across three cities. Now a new CTO from Akamai and an entirely new leadership team are tasked with rebuilding confidence in India's digital backbone.",
    "slug": make_slug("tata-communications-leadership-overhaul-data-centre-fire"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Tata Communications' infrastructure crisis and leadership overhaul matters to NRI investors and professionals who depend on India's digital backbone — from enterprise cloud services to the subsea cables connecting Indian and global markets.",
    "tags": ["tata-communications", "data-center", "india-infrastructure", "google-cloud", "cybersecurity", "tata-group"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/business/indias-tata-communications-names-new-chief-technology-officer-2026-06-30/"},
        {"name": "ScanX Trade", "url": "https://scanx.trade/news/tata-communications-appoints-rupesh-chokshi-and-vivek-srivastava-as-evps/"},
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/info-tech/fire-at-third-party-data-centre-hits-google-cloud-services-in-delhi-mumbai-chennai/article69663483.ece"},
        {"name": "VarIndia", "url": "https://varindia.com/news/fire-breaks-out-at-tata-communications-office-in-delhi"}
    ]),
    "score_total": 72,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/17489151/pexels-photo-17489151.jpeg",
    "image_caption": "Server racks inside a modern data centre facility",
    "image_attribution": "Pexels",
    "body": article2_body.strip()
}


# ─────────────────────────────────────────────
# INSERT
# ─────────────────────────────────────────────

articles = [article1, article2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

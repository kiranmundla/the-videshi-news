#!/usr/bin/env python3
"""Technology writer for The Videshi — 2026-07-12 02:00 AM PT run."""

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
    # ── Article 1: Cult.fit IPO ──────────────────────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "India's Biggest Fitness Unicorn Just Filed for IPO. Myntra's Co-Founder Is Betting the Gym Can Go Public.",
        "subheadline": "Cult.fit's draft papers reveal a nearly $2 billion fitness empire with nearly a million paid members — and losses that have not fully disappeared.",
        "slug": make_slug("cultfit-ipo-mukesh-bansal-fitness-unicorn-sebi"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "NRI investors eyeing India's consumer tech IPO pipeline should watch Cult.fit closely — the Myntra co-founder-led company is testing whether India's growing wellness economy can support a public listing at a time when Jio Platforms and NSE are also queuing up.",
        "tags": ["indian-startup", "ipo", "fitness-tech", "cult-fit", "consumer-tech"],
        "urgency": "medium",
        "score_total": 75,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/3768868/pexels-photo-3768868.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
        "image_caption": "A group fitness class in a modern studio — the kind of experience Cult.fit is betting can scale across 700-plus centres in India",
        "image_attribution": "Pexels",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/markets/deals/indian-fitness-firm-cultfit-files-ipo-2026-07-08/"},
            {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/markets/cultfit-ipo-explained-what-the-drhp-reveals-about-the-companys-risks"},
            {"name": "Inc42", "url": "https://inc42.com/buzz/from-elevate-education-to-aukera-indian-startups-raised-72-mn-this-week/"}
        ]),
        "body": """Mukesh Bansal co-founded Myntra, sold it to Flipkart for roughly $330 million, and then decided to fix how India exercises. Eight years and more than $720 million in private capital later, his fitness platform Cult.fit has filed its Draft Red Herring Prospectus with SEBI, setting the stage for one of the most closely watched consumer tech listings of the year.

The numbers tell a story of a company that has grown fast and spent faster. Cult.fit's proposed IPO comprises a fresh issue of shares worth up to ₹950 crore (about $100 million) and an offer for sale of up to 17.86 crore equity shares by existing shareholders including Temasek, Tata Digital, Accel and Kalaari Capital. Media reports peg the total issue size at ₹3,500–4,000 crore, valuing the company at roughly $2 billion.

## A Million Paying Members, Still No Net Profit

Revenue crossed ₹1,700 crore in FY26, growing 40% year-on-year. More importantly, the company turned adjusted EBITDA-positive in the final quarter of the fiscal year, recording ₹144.8 crore in adjusted EBITDA for the full year. Net losses, meanwhile, have narrowed sharply — from ₹888.5 crore in FY24 to ₹251.9 crore in FY26 — but profitability at the bottom line remains elusive.

Cult.fit now operates 708 fitness centres across India with 987,000 paid members as of March 2026. About 69% of those centres are franchised or marketplace gyms, a model that lets Cult.fit expand without burning capital on real estate but limits its operational control over service quality.

## The Risks the DRHP Reveals

The draft papers flag several concerns that analysts are already scrutinising. Geographic concentration is sharp: Delhi-NCR, Mumbai, Bengaluru and Hyderabad account for more than 90% of fitness services revenue, up from 85.5% two years ago. That concentration is deepening, not diversifying.

Auditors flagged recurring issues with data controls at premium fitness centres and wellness studios. Backups of books of account relating to sales were not maintained daily in FY24, FY25 and FY26, and auditors could not verify whether audit trails in third-party point-of-sale software had been enabled throughout the year. The company expects to eliminate its dependence on these third-party systems by FY27.

Litigation adds another layer of risk. About ₹55 crore in cases are pending against the company's subsidiaries, while approximately ₹488 crore in cases are pending against its directors. Subsidiary businesses including Cultsport (fitness products) and Cultfit Healthcare continued posting losses in the range of ₹18–33 crore annually.

## Why NRIs Should Pay Attention

The IPO advisory bench alone signals the stakes. Axis Capital, Goldman Sachs, Jefferies, JM Financial and Morgan Stanley are managing the book — a lineup typically reserved for marquee offerings.

For Indian Americans who have watched India's consumer internet companies struggle on public markets (Paytm's post-IPO wipeout remains fresh memory), Cult.fit represents a different thesis: a hybrid physical-digital business riding India's shift toward preventive healthcare and organised fitness. Bansal himself, a serial entrepreneur with a proven exit, brings credibility that pure-play app companies often lack.

The listing comes alongside an already busy IPO calendar. Jio Platforms and the National Stock Exchange of India are expected to test investor appetite later this year. CarDekho's parent Girnar Software and enterprise AI firm C5i have also filed or are preparing to file draft papers.

India's fitness market is still in its early innings — organised gym penetration is a fraction of what it is in the United States. The question is whether Cult.fit can convert its brand recognition and app-led distribution into sustainable unit economics before the public markets demand profitability, not just growth.

The board has been strengthened ahead of the listing with heavyweight independent directors including Kalpana Morparia (former Chairman, JPMorgan South and Southeast Asia), Arun M. Kumar (former Chairman and CEO, KPMG India), and Pragya Misra (OpenAI India's public policy head). That lineup suggests the company is preparing for serious institutional scrutiny.

Cult.fit's DRHP is under SEBI review. A final timeline for the public offering has not been announced."""
    },

    # ── Article 2: Yotta $150M AI Infrastructure ──────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "Yotta Just Raised $150 Million to Become India's Answer to the American AI Data Centre Boom",
        "subheadline": "The Hiranandani-backed AI infrastructure company has hit a ₹37,000 crore valuation and is deploying NVIDIA's most powerful GPUs at a pace that could make India a serious player in the global AI compute race.",
        "slug": make_slug("yotta-150-million-ai-data-centre-nvidia-gpu-india"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "For NRI tech professionals and investors watching the AI infrastructure buildout in the US, Yotta represents a parallel story in India — a bet that sovereign AI compute capacity will become as strategically important as oil reserves, with pre-IPO and public listing plans that could open a direct investment window.",
        "tags": ["ai-infrastructure", "data-center", "nvidia", "yotta", "indian-startup"],
        "urgency": "medium",
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/17489151/pexels-photo-17489151.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
        "image_caption": "Server racks in a modern data centre — the kind of GPU-dense infrastructure Yotta is building across India for AI workloads",
        "image_attribution": "Pexels",
        "sources": json.dumps([
            {"name": "The Mileage", "url": "https://themileage.in/ai-infrastructure-firm-yotta-secures-150-million-funding/"},
            {"name": "Mango People News", "url": "https://mangopeoplenews.com/nxtra-who-yotta-just-raised-150-million/"},
            {"name": "LiveMint", "url": "https://www.livemint.com/technology/tech-news/indian-firm-yotta-to-build-2-billion-data-centre-with-nvidias-blackwell-chips-11740382605830.html"}
        ]),
        "body": """While Microsoft, Google and Amazon pour tens of billions into American AI data centres, a quieter bet is taking shape in India. Yotta Data Services, the Hiranandani family-backed AI infrastructure company, has raised approximately $150 million in fresh growth capital from non-institutional investors, valuing the company at around ₹37,000 crore (roughly $4.4 billion).

The entire raise is primary capital — no promoter sell-down — and every dollar is going directly into expanding Yotta's AI infrastructure. For a company that most people outside India's enterprise cloud market have never heard of, the valuation is striking.

## The GPU Arms Race, Indian Edition

Yotta's pitch rests on a simple premise: India cannot afford to rent all of its AI compute from American hyperscalers. As government agencies, banks, insurers and defence organisations increasingly need to process data on Indian soil — using Indian-language models, under Indian data sovereignty rules — somebody has to build the physical infrastructure to host those workloads.

That somebody, Yotta argues, is itself. The company has been deploying NVIDIA H100 GPUs and is preparing for Blackwell-generation chips across its data centre campuses near Delhi, Mumbai and Navi Mumbai. NVIDIA itself is anchoring Asia's first DGX Cloud supercluster within Yotta's infrastructure, committing about 10,300 GPUs under a four-year contract valued at approximately $1 billion, according to reports.

Yotta's total GPU footprint is expected to grow from about 40,000 today to more than 75,000 over the next two years. For context, most Indian enterprises currently access high-end GPU compute through AWS or Azure — Yotta is building the case that a domestically owned alternative is both strategically necessary and commercially viable.

## The Tachyon Deal and US Expansion

In a move that signals Yotta's ambitions beyond India, its parent company Nidar Infrastructure signed a binding memorandum of understanding with Tachyon Corporation to anchor the Nakota AI Data Campus in the United States. The 15-year commitment is expected to generate approximately $2.34 billion in revenue from the initial 100 MW deployment, with the campus designed to support up to 1 GW at full build-out.

This is not an Indian company content to serve its home market. Yotta, through Nidar, already trades on Nasdaq following a SPAC merger that valued it at $2.75 billion. The $150 million fundraise is explicitly labelled pre-IPO capital, and the company has confirmed that its IPO plans remain on track, though it has not announced a timeline. Reports suggest it is targeting $600–900 million in combined pre-IPO and IPO capital at a valuation of $4–6 billion.

## Where the Money Goes

The fresh capital will fund three priorities simultaneously. First, accelerating GPU cluster build-out — the high-density racks required for AI workloads demand different cooling, power and floor-loading specifications than conventional enterprise data centres. Second, geographic expansion into Chennai, Hyderabad and Bengaluru, where demand from enterprise clients and Global Capability Centres is growing fastest but supply remains tight. Third, building Yotta's cloud and AI platform layer — moving beyond pure colocation toward managed AI services and sovereign cloud capabilities for clients who cannot place workloads on foreign-owned platforms.

## The Diaspora Angle

For Indian Americans working in AI infrastructure at companies like NVIDIA, Google Cloud or AWS, Yotta's trajectory is worth watching for two reasons. One, it is creating a parallel career pipeline for engineers who want to work on cutting-edge GPU infrastructure while based in India or involved in India-linked ventures. Two, as a Nasdaq-listed entity (through Nidar), it offers a direct investment exposure to India's AI infrastructure buildout that does not require navigating Indian capital markets.

India's installed GPU compute capacity has grown from near-zero to over 34,000 GPUs in two years, according to government officials. Yotta claims a significant share of that capacity and is positioned alongside the India AI Mission, supporting foundational Indian-language AI models like Bhashini, Sarvam and BharatGen.

The demand is real. More than 500 Indian startups have applied for access to affordable GPU compute through government programmes, and many have not yet received allocations. Whether Yotta can build fast enough to capture that demand — and whether the economics of domestically hosted AI compute can compete with the scale advantages of American hyperscalers — will determine whether India's AI infrastructure story is a footnote or a chapter of its own."""
    },
]


if __name__ == "__main__":
    for art in articles:
        try:
            result = sb_post("p2_articles", art)
            print(f"✅ {art['slug']}")
        except Exception as e:
            print(f"❌ {art['slug']}: {e}")

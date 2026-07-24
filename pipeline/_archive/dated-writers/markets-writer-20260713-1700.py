#!/usr/bin/env python3
"""Markets & Finance writer — 2026-07-13 17:00 PT run."""

import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

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
        "headline": "HCLTech Beats Q1 Estimates as AI Revenue Surges 62% — India's Third-Largest IT Firm Signals the Sector's Pivot Is Real",
        "subheadline": "A $2.4 billion bookings quarter, 20% profit growth, and $171 million in advanced AI revenue give NRI investors the clearest sign yet that India's beaten-down IT sector is finding its footing.",
        "slug": make_slug("hcltech-q1-fy27-earnings-beat-ai-revenue-62-percent-nri"),
        "category": "markets-finance",
        "vertical": "markets-finance",
        "diaspora_angle": "HCLTech is a core holding for NRI investors in Indian IT — down 23% YTD but rallying 10% in July. The AI revenue surge and bookings rebound signal a structural floor, not just a dead-cat bounce. With the rupee down 9% in Q1, dollar-denominated returns for NRI portfolios are under pressure, but the earnings quality is improving.",
        "tags": ["markets", "finance", "nri-investing", "hcltech", "indian-it", "ai", "earnings"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/indias-hcltech-beats-first-quarter-revenue-estimates-financial-services-strength-2026-07-13/"},
            {"name": "HCLTech Investor Relations", "url": "https://www.hcltech.com/investors"},
            {"name": "Reuters — Indian shares recoup losses", "url": "https://www.reuters.com/world/india/indian-shares-open-lower-renewed-mideast-fighting-dampens-sentiment-2026-07-14/"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d0/C_Vijayakumar_%281%29.jpg/1280px-C_Vijayakumar_%281%29.jpg",
        "image_caption": "HCLTech CEO C Vijayakumar, who has led the company since 2016",
        "image_attribution": "Wikimedia Commons",
        "body": """HCLTech delivered a beat-and-raise quarter on Monday that will make NRI investors reconsider the obituaries they've been writing for Indian IT all year.

India's third-largest IT services exporter posted consolidated revenue of ₹34,579 crore ($3.65 billion) for the April–June quarter, a 13.94% jump from a year ago that topped the street's estimate of ₹34,350 crore. Net profit climbed 20.3% to ₹4,624 crore, again ahead of the ₹4,512 crore consensus. And the number that will stick in every analyst's deck: advanced AI revenue hit $171 million, surging 62.1% year-on-year in constant currency and 10.6% sequentially.

## The Bookings Rebound

What caught the market's attention was the total contract value of new deal wins: $2.4 billion, up sharply from $1.9 billion in the preceding quarter and $1.8 billion a year ago. For a company that limped into FY27 with bookings at three-quarter lows after flagging two U.S. clients pulling back on discretionary spend, this is a meaningful turnaround.

Financial services, technology, and retail verticals drove the beat. The banking segment, in particular, benefited from continued deal momentum that also powered rival TCS's revenue surprise last week. HCLTech's EBIT margin came in at 16.9%, up 39 basis points sequentially despite absorbing 62 basis points in restructuring costs — a sign that the company is trimming fat even as it ramps new capabilities.

Revenue per employee rose to $65.5K per annum, up 3.3% year-on-year, which matters more than headline headcount numbers. In an industry where AI threatens to compress project timelines and squeeze per-engineer billing, higher revenue per head suggests HCLTech is extracting more value from a leaner workforce rather than simply adding bodies.

## AI — From Buzzword to P&L Line

The $171 million in advanced AI revenue — encompassing agentic AI, AI engineering, and generative AI services — now represents roughly 4.7% of quarterly revenue. That's modest in absolute terms, but the growth trajectory is steep. A year ago, that figure sat near $106 million. CEO C Vijayakumar has been positioning HCLTech as an AI-native services company, and the numbers are starting to back the narrative.

Earlier on Monday, LTIMindtree — another Tata Group IT company — announced a partnership with Anthropic to accelerate enterprise adoption of Claude, the AI model. The deal sent IT stocks soaring 3.6% to a one-month high and underscored a sector-wide pivot: Indian IT firms are no longer just talking about AI disruption — they're booking revenue from it.

## What NRI Investors Should Watch

For the diaspora investor sitting in New Jersey or Dallas with HCLTech in their Indian equity portfolio, the numbers tell a nuanced story.

The bad news: Indian IT stocks are still down nearly 23% for the year. The rupee's 9% depreciation against the dollar in Q1 has boosted INR revenue but eroded dollar-denominated returns. HCLTech's FY27 guidance of 1–4% constant-currency revenue growth reflects management's caution about macro headwinds — discretionary spending remains soft, and two client-specific ramp-downs flagged last quarter haven't fully resolved.

The good news: the July rally of 10.3% across the Nifty IT index suggests the market is pricing in an earnings floor. HCLTech stock itself jumped 4.9% on Monday ahead of results. New bookings are accelerating. AI revenue is real and growing at triple-digit rates. And with the company declaring a ₹12 per share dividend and maintaining free cash flow conversion at 99% of net income, the balance sheet is sound.

J.P. Morgan reiterated its year-end Nifty target of 27,000 last week — implying 11.5% upside — partly on the strength of an improving IT earnings season. With TCS already beating estimates and HCLTech following suit, the question for NRI investors shifts from "is the sector in trouble?" to "is the worst already priced in?"

Infosys and Wipro report later this month. If they confirm the pattern, the re-rating trade in Indian IT could accelerate. For NRIs who've been underweight the sector since February's AI-panic selloff, HCLTech's quarter is a data point worth weighing before the next tranche lands."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "TCS Reshuffles Its Top Brass and Creates Five New Business Units — Here's What the AI-Era Overhaul Means for NRI Investors",
        "subheadline": "India's largest IT services company splits its American banking unit in two, carves out a dedicated US West Coast business, and bets big on ServiceNow and autonomous operations as AI threatens to reshape the $315 billion sector.",
        "slug": make_slug("tcs-leadership-reshuffle-five-business-units-ai-era-nri"),
        "category": "markets-finance",
        "vertical": "markets-finance",
        "diaspora_angle": "TCS is the single largest Indian IT stock by market cap (~$145B) and a staple in NRI equity portfolios. The reorganization — splitting the BFSI Americas unit, creating a US West Coast business group, and building a standalone ServiceNow practice — directly targets the American market where most NRIs live and work. Understanding the strategic pivot is essential for anyone holding or considering TCS shares.",
        "tags": ["markets", "finance", "nri-investing", "tcs", "indian-it", "ai", "leadership", "tata-group"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/indias-tcs-rejigs-leadership-team-creates-new-business-units-2026-07-13/"},
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/info-tech/tcs-announces-new-global-business-units-amid-ai-led-transformation/article69794123.ece"},
            {"name": "Reuters — TCS bags ABB contract", "url": "https://www.reuters.com/technology/indias-tcs-bags-multi-million-contract-industrial-giant-abb-2026-07-14/"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/85/Tata_Consultancy_Services_Madhapur_Hyderabad.jpg/1280px-Tata_Consultancy_Services_Madhapur_Hyderabad.jpg",
        "image_caption": "TCS campus in Madhapur, Hyderabad — headquarters of the company's sprawling operations",
        "image_attribution": "Wikimedia Commons",
        "body": """When a 600,000-person company rewires its org chart on a Sunday, it's not housekeeping — it's a signal. And TCS just sent one.

In a series of internal memos issued over the weekend, CEO K Krithivasan and COO Aarthi Subramanian announced the most significant leadership reshuffle at Tata Consultancy Services in years. The company carved out five new business groups, split its most important American vertical in half, and shuffled senior executives across cybersecurity, lifesciences, and media — all in response to what management sees as AI's accelerating disruption of the $315 billion Indian IT services industry.

## The Big Moves

The headline restructuring is the division of BFSI Americas — TCS's largest and most profitable unit — into two separate business groups. Banking, which accounts for a third of TCS's overall revenue and is anchored in the North American market that generates nearly half of all sales, will now have dedicated leaders for the US West (Rakesh Kumar) and US East (Mohan Veeturi). The previous head, Susheel Vasudevan, moves to a strategic role reporting directly to the CEO.

Manmeet Chhabra, who led TCS's Canadian banking operations, becomes the company's new Country Head for Canada — a signal that TCS views the Canadian market as large enough to warrant its own leadership structure.

Beyond the BFSI split, TCS created five entirely new business groups:

- **ServiceNow Practice** — A standalone unit built around the enterprise workflow platform, reflecting the growing demand for AI-powered automation
- **US West Coast** — A dedicated group targeting Silicon Valley's tech ecosystem and AI-native companies
- **Travel & Transport** — Separated out from broader verticals as travel-tech spending recovers
- **Energy & Utility** — Capitalizing on the energy transition's digital infrastructure needs
- **Global Autonomous Businesses** — The most forward-looking of the five, focused on self-operating enterprise systems

New leadership was also installed across cybersecurity (Kumar Narayanan), UK and Europe lifesciences (Ganesa Vaikuntam), and communication and media verticals.

## Why It Matters: The AI Squeeze Is Real

These moves don't happen in a vacuum. India's IT services sector is staring down a structural challenge: AI tools are shortening project timelines, reducing the need for large engineering teams, and giving clients leverage to demand lower prices. The sector's market capitalization has shed $100 billion since February.

TCS's response is strategic segmentation. Rather than running a monolithic operation where AI-related work competes for attention with legacy maintenance contracts, the company is isolating growth bets — ServiceNow, autonomous operations, US West Coast tech clients — in dedicated units with their own P&L accountability.

The ServiceNow practice is particularly telling. TCS signed a multi-year partnership with ServiceNow earlier this year to embed agentic AI into enterprise workflows. Now it's giving the practice its own leadership and business group status — a bet that the ServiceNow platform will become a primary channel for delivering AI services to Fortune 500 clients.

## The Earnings Backdrop

The reshuffle comes days after TCS beat quarterly revenue estimates for the April–June period. Revenue jumped 14% year-on-year to ₹72,275 crore ($7.58 billion), driven by banking clients and a weaker rupee. The company added 9,300 employees — its highest intake in over three years — even as AI-related job loss fears persist across the industry.

On Monday, TCS sealed a multi-million dollar contract with Swiss-Swedish industrial giant ABB to design and run its global network as an AI-driven service. The deal, an extension of a 20-year partnership, is exactly the kind of AI-infrastructure work the restructured TCS is positioning to capture at scale.

TCS shares rose 5.4% on Monday, their best single-day gain in weeks.

## What NRI Investors Should Read Into This

For NRI shareholders — and TCS is a staple in virtually every India-focused portfolio — three things stand out.

First, the US West Coast business group is a direct play for the AI-native market. Silicon Valley companies are the biggest buyers and builders of AI infrastructure, and TCS is creating a dedicated team to go after that spend. This is where the growth will come from, and NRI investors in the Bay Area, Seattle, and Austin will recognize many of these clients.

Second, splitting BFSI Americas signals that the unit had grown too large for one leader. Banking remains TCS's bread and butter, and the East-West division should enable faster decision-making on deals that often involve regulatory complexity across different US jurisdictions.

Third, the "Global Autonomous Businesses" unit is the most speculative bet — self-operating enterprise systems are still nascent — but it positions TCS ahead of rivals in what could be the next decade's defining IT services category.

Krithivasan has now made his AI-era thesis clear: segment, specialize, and give each growth vector its own leadership. Whether the $145 billion company can execute across five new units and a split banking division simultaneously is the question NRI investors should track through the rest of FY27."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

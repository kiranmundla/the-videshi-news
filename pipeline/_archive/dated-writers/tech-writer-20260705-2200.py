#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-07-05 22:00 PDT run."""

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


articles = [
    # ── Article 1: US-India Pax Silica / Anthropic AI Access ──
    {
        "id": str(uuid.uuid4()),
        "headline": "Washington Is Quietly Deciding Which AI India Gets to Use. Delhi Is at the Table.",
        "subheadline": "A closed-door roundtable at the 2nd Pax Silica Summit brought together Indian and American officials to negotiate semiconductor supply chains, critical minerals — and access to Anthropic's frontier models.",
        "slug": make_slug("us-india-pax-silica-anthropic-ai-access-semiconductor"),
        "category": "technology",
        "vertical": "geopolitics",
        "diaspora_angle": "The US-India AI partnership shapes which frontier models Indian companies and engineers can access, affects semiconductor job creation in India, and positions Indian Americans at the nexus of the world's most consequential tech relationship.",
        "tags": ["us-india", "pax-silica", "ai-policy", "semiconductors", "anthropic", "frontier-ai", "critical-minerals"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "The Indian Eye", "url": "https://theindianeye.com/2026/06/26/india-and-us-hold-roundtable-to-build-ai-together/"},
            {"name": "The Indian Eye", "url": "https://theindianeye.com/2026/06/26/envoy-gor-cites-india-us-partnership-as-crucial-for-building-trusted-ai/"},
            {"name": "U.S. Department of State", "url": "https://www.state.gov/joint-statement-on-the-u-s-india-ai-opportunity-partnership/"},
            {"name": "U.S. Embassy India", "url": "https://in.usembassy.gov/united-states-and-india-sign-strategic-critical-minerals-cooperation-framework/"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/f/f0/Jacob-Helberg-photo_2025.jpg",
        "image_caption": "Jacob Helberg, US Under Secretary of State for Economic Affairs, who leads the Pax Silica initiative",
        "image_attribution": "Wikimedia Commons",
        "body": """The most consequential technology negotiations between Washington and New Delhi are not happening at product launches or earnings calls. They are happening in closed rooms, between diplomats and engineers, over questions that sound abstract until you realise they will determine the shape of India's AI economy for the next decade.

On Friday, the Indian Embassy in Washington hosted a closed-door roundtable alongside the US-India Strategic Partnership Forum (USISPF) and the Silverado Policy Accelerator. The meeting — part of the 2nd Pax Silica Summit — brought together Ambassador Vinay Mohan Kwatra, MeitY Secretary S. Krishnan, and US Deputy Under Secretary of Commerce Bill Guidera with executives from Indian and American semiconductor and AI companies. The Department of Energy sent its own representative, Deputy Assistant Secretary Christopher Saldana, signalling that the discussions ranged well beyond software.

"Securing the foundations of AI together!" the Indian Embassy declared on X, which is diplomat-speak for: we are negotiating who builds the chips, who mines the minerals, and who gets to run the models.

## The Anthropic Question

The most revealing detail from the summit came not from the official readout but from US Under Secretary of Economic Affairs Jacob Helberg, who confirmed that Washington and New Delhi are engaged in what he called "sensitive national security discussions" about releasing advanced AI models — specifically, Anthropic's frontier systems — to India.

Helberg described a "gradual, measured approach" to making models like Anthropic's Fable available to trusted partners. "We continue to have ongoing conversations about this topic with our Indian friends," he said, adding that the discussions touch on critical infrastructure protection, including power grids. "Both sides really understand each other's perspectives."

The subtext is significant. The United States now treats access to frontier AI models the way it once treated nuclear technology or advanced weapons systems — as a strategic asset to be shared selectively with allies. India is firmly in the "trusted partner" category, but the pace of access is being calibrated against national security risks that neither side is willing to discuss publicly.

## The Pax Silica Architecture

The roundtable sits within a broader architecture that has been assembled with remarkable speed. Launched in December 2025 by Helberg's office at the State Department, Pax Silica is designed to secure the entire AI value chain — from lithium and rare earth mining through chip fabrication to model deployment — within a coalition of allied nations. India became the 10th signatory in February 2026 at the AI Impact Summit in New Delhi, joining Australia, Japan, South Korea, Singapore, the UK, Israel, the UAE, Greece, and Qatar.

In May, the partnership went further. Secretary of State Marco Rubio and External Affairs Minister S. Jaishankar signed a bilateral Critical Minerals Framework in New Delhi, committing both nations to secure supply chains for the rare earths and minerals that underpin semiconductor manufacturing. The Quad — the US, Japan, Australia, and India — simultaneously announced a $20 billion critical minerals initiative covering mining, processing, and recycling.

Helberg called the India-US relationship "one of the single-most consequential bilateral relationships in the world in the 21st century." That language, from a senior State Department official at a technology summit, is not casual.

## What This Means for the Diaspora

For Indian Americans working in AI and semiconductor industries, these negotiations are not abstract geopolitics. They shape which tools Indian startups can access, which chips get manufactured in Gujarat and Dholera, and whether the next generation of AI infrastructure runs on American models or forces India to build its own from scratch.

India's semiconductor workforce requirements are staggering — IT Minister Ashwini Vaishnaw has estimated one million new skilled professionals will be needed. Indian engineers in the US are already designing two-nanometre chips, and Pax Silica creates a formal channel for that expertise to flow back without the friction that has historically slowed technology transfer.

For NRI investors, the semiconductor supply chain is becoming an investable thesis. Tata Electronics is building a fab in Dholera. Micron's $2.75 billion Gujarat facility is under construction. CG Semi, backed by the Murugappa Group, is pursuing advanced packaging. These projects all depend on exactly the kind of supply chain security and raw materials access that the Pax Silica framework is designed to guarantee.

The risk, of course, is that "gradual and measured" becomes a euphemism for slow. India's sovereign AI ambitions — represented by Sarvam's recent $234 million unicorn round and the government's IndiaAI Mission — require access to frontier models now, not after years of diplomatic calibration. Whether Washington's pace matches New Delhi's appetite will define the relationship's next chapter.""",
    },

    # ── Article 2: India as Safe Haven from AI Trade ──
    {
        "id": str(uuid.uuid4()),
        "headline": "Wall Street's Hottest New Trade: Betting on India Because It Missed the AI Bubble",
        "subheadline": "As AI-heavy markets in South Korea and Taiwan crater, global investors are pouring back into Indian equities. The irony: India's lack of exposure to the AI trade is now its greatest selling point.",
        "slug": make_slug("india-safe-haven-ai-stock-selloff-blackrock-investors"),
        "category": "technology",
        "vertical": "markets",
        "diaspora_angle": "NRI investors with portfolios split between US tech stocks and Indian equities are watching a historic rotation unfold — India's market resilience during the global AI selloff creates both a hedging opportunity and a rebalancing signal.",
        "tags": ["india-markets", "ai-trade", "nri-investors", "blackrock", "nifty-50", "emerging-markets", "portfolio-strategy"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/markets/investors-looking-for-shelter-from-ai-storm-are-turning-to-india/article69775284.ece"},
            {"name": "Reuters", "url": "https://www.reuters.com/markets/asia/indian-shares-outperform-asia-oil-drops-it-rebounds-2026-07-03/"},
            {"name": "Reuters", "url": "https://www.reuters.com/markets/asia/global-funds-revisit-indian-stocks-oil-rupee-risks-recede-2026-06-30/"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/BSE_building_at_Dalal_Street.JPG/1280px-BSE_building_at_Dalal_Street.JPG",
        "image_caption": "The Bombay Stock Exchange building on Dalal Street, Mumbai",
        "image_attribution": "Wikimedia Commons",
        "body": """For the better part of 2026, India has been the market that global fund managers loved to abandon. Too expensive. Too dependent on oil imports. Too far from the AI gold rush that was minting fortunes in Seoul and Taipei.

Then the AI trade cracked.

On July 3, as South Korea's tech-heavy KOSPI nosedived nearly 8 per cent and Asian markets broadly tumbled 2.4 per cent, the Nifty 50 rose 0.71 per cent. The BSE Sensex climbed 0.75 per cent. India, the market everyone left behind, was suddenly the one still standing.

"Tech volatility has prompted a search for alternatives, with India ending June with roughly 3 per cent outperformance and up 7 per cent from the lows in early June," Macquarie wrote in a note to clients. For a market that had been beaten down all year, the turnaround has been swift.

## From Pariah to Shelter

The numbers tell a story of dramatic reversal. Average allocations to India among emerging market funds dropped below 10 per cent in April — the lowest since early 2021, down from a peak of 17.5 per cent in August 2024, according to Copley Fund Research. Overseas investors had fled, citing stretched valuations, a cratering rupee, and sky-high oil prices during the Iran crisis.

Now the tide is visibly turning. Exchange data shows daily selling by global funds has slowed markedly. Inflows into US-listed India-focused exchange-traded funds turned positive last week for the first time in over a month, according to analysis by Elara Capital.

"Two key headwinds have eased," said Todd McClone, a portfolio manager at William Blair Investment Management, which oversees about $65 billion. "India is among the most oversold markets we track. This macro improvement, alongside a more attractive valuation premium, strengthens the case to act."

Ben Powell, BlackRock Investment Institute's chief investment strategist for the Middle East and Asia Pacific, framed the rotation in starkly contrarian terms. "India was held back earlier this year by higher energy prices, elevated valuations and limited exposure to the AI trade," Powell said. "As those pressures have eased, investors may look beyond AI-heavy markets. That could put India back on investors' radar as a differentiated opportunity within emerging markets."

Read that again: India's lack of exposure to the AI trade — the very thing that made it unfashionable six months ago — is now its selling point.

## The AI Unwind Explained

The mechanics are straightforward. Markets in South Korea and Taiwan had become proxies for the AI hardware boom, driven by Samsung, SK Hynix, and TSMC. When concerns about stretched valuations and the sustainability of AI capital expenditure triggered a correction in late June, these markets fell hardest. South Korea's KOSPI has shed over 15 per cent from its peak.

India, by contrast, has virtually no direct exposure to AI hardware manufacturing. Its technology sector is dominated by IT services companies — TCS, Infosys, Wipro, HCL — that are going through their own existential reckoning with AI-driven deflation, but whose share prices had already been beaten down by 30 per cent or more this year. In a strange twist, the sector that investors had punished became the one with room to recover.

When the Nifty IT index surged 4.6 per cent on July 3 — leading all sectors — analysts attributed it to value buying after six consecutive sessions of declines. The stocks had simply fallen enough.

## The Oil Tailwind

Falling crude prices are amplifying the rotation. Brent crude dropped below $71 per barrel after Qatar signalled positive progress in indirect talks between Iran and the United States. India imports nearly 90 per cent of its crude requirements, making oil the single most consequential macro variable for its markets, affecting everything from growth and inflation to forex reserves and the fiscal deficit.

"The drop in oil prices is the single biggest factor for India," said G. Chokkalingam, founder and head of research at Equinomics Research. "It impacts growth, inflation, forex reserves, fiscal deficit — everything."

A stabilising rupee has also helped. After hitting record lows in May, the currency has firmed, improving returns for foreign-currency holders who had been doubly punished by falling asset prices and a weakening exchange rate.

## What NRI Investors Should Watch

For Indian Americans with portfolios split between US technology stocks and Indian equities, the current moment presents a genuine hedging dynamic. The AI correction that hurts Nvidia and Microsoft holdings in a US brokerage account is the same force pushing capital into Indian markets through a different channel.

Kruti Shah, a quantitative analyst at Equirus Securities, sees a "bullish undertone" in the Nifty 50 and favours call spreads to bet on further gains, noting that the upcoming earnings season — TCS reports later this month, Infosys on July 23 — may offer positive surprises.

The longer-term question is whether India can build its own AI economy fast enough to participate in the next leg of the trade, not just benefit from the current unwind. A data-centre tax exemption through 2047, Microsoft and Google both building massive compute facilities on Indian soil, and Nvidia signing up India's Yotta as a DSX partner all suggest the foundations are being laid.

But for now, India's appeal is simpler and more old-fashioned: it is a large, growing economy with improving macro fundamentals, a stabilising currency, and stock prices that have already absorbed a year's worth of bad news. In a world where the AI trade is suddenly risky, that combination looks remarkably attractive.""",
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

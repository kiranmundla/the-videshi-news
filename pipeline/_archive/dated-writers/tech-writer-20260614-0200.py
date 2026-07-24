#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-06-14 02:00 AM batch"""

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


# ─────────────────────────────────────────────────────────────────────
# ARTICLE 1: SpaceX IPO + India Starlink Freeze
# ─────────────────────────────────────────────────────────────────────

art1_body = """SpaceX priced its Nasdaq debut at $135 per share on Thursday, raising a record $75 billion and landing a $1.75 trillion valuation that dwarfs every previous American IPO. By the time Indian markets opened on Friday morning, retail investors in Mumbai, Bangalore, and the Bay Area were already scrambling to find a way in.

They will have to be patient. India, one of the largest untapped satellite broadband markets on the planet, froze final security approvals for Starlink's commercial launch just days before the listing. The timing is not accidental.

## The Hold

Indian security agencies withheld the clearances Starlink needs to begin operations, despite the company having already secured a Global Mobile Personal Communication by Satellite licence last year and completing demonstrations reviewed by both telecom authorities and a dedicated security panel. The concern is not technical compliance. It is control.

Reports indicate that India's intelligence apparatus grew uneasy after Starlink terminals were used in the Iran conflict zone, raising questions about how much sovereignty New Delhi can exercise over a US-based communications operator when geopolitical pressure mounts. Starlink remains effectively locked out of both China and India — the world's two largest populations — which does not break the long-term thesis but does raise visible execution risk at the worst possible moment for SpaceX's public debut.

## Indian Investors Want In Anyway

The freeze has done nothing to dampen enthusiasm among Indian retail investors. Vested Finance, a global investing platform popular with Indian professionals, reported "unprecedented" traffic once the SpaceX ticker went live on its Nasdaq feed. Borderless, a rival platform, estimated that if IPO allocations had been available to Indian retail investors directly, demand could have topped $50–100 million.

RBI data shows the trend is structural: remittances under the Liberalised Remittance Scheme for foreign equity investment grew 56% year-on-year to $2.7 billion in FY26. SpaceX is the kind of marquee listing that accelerates that flow.

The valuation, however, is not for the faint-hearted. Morningstar pegs fair value at $63 per share — roughly 53% below the IPO price. SpaceX reported a Q1 2026 net loss of $4.28 billion and an accumulated deficit of $41.3 billion. The AI infrastructure segment alone is burning approximately $2.5 billion per quarter with no clear payback path yet. Aswath Damodaran, the NYU professor whose valuations are not famous for generosity, estimated SpaceX worth about 28% below the offering price.

## Why It Matters for NRIs

For the Indian professional in Silicon Valley who has watched Musk's companies from a front-row seat, SpaceX represents both aspiration and caution. The company employs thousands of engineers, and its Starlink division has become the dominant broadband player in rural America. But the $26 trillion AI addressable market that SpaceX's underwriters pitched to investors is, as Damodaran bluntly put it, "a theoretical projection, not a pipeline, not a contract."

Meanwhile, the Starlink question in India remains unresolved. If New Delhi does eventually grant approval, Starlink could transform connectivity in rural India — a development that would directly affect NRI families with roots outside tier-one cities. If it doesn't, the freeze becomes another data point in the growing tension between sovereign technology control and American tech platforms.

Elon Musk is now the world's first trillionaire, with his net worth crossing $1.1 trillion. The question for Indian investors is simpler: at $1.75 trillion, are you buying a leader, or funding one?"""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "SpaceX's Record $75 Billion IPO Lands at $1.75 Trillion. India Just Froze Starlink.",
    "subheadline": "Indian retail investors are rushing to buy on platforms like Vested and Borderless, even as New Delhi blocks Starlink's commercial launch over security concerns tied to the Iran conflict.",
    "slug": make_slug("spacex-ipo-starlink-india-freeze-indian-investors"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Indian retail investors are pouring money into SpaceX through LRS-enabled platforms, but Starlink's India freeze raises questions about connectivity for NRI families and sovereign tech control.",
    "tags": ["spacex", "starlink", "ipo", "india", "elon-musk", "indian-investors"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com"},
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/info-tech/india-freezes-starlink-spacex-ipo/article69684215.ece"},
        {"name": "Livemint", "url": "https://www.livemint.com/market/stock-market-news/spacex-ipo-can-indians-invest-11718192723591.html"},
        {"name": "AInvest", "url": "https://www.ainvest.com/news/spacex-ipo-valuation-test/"}
    ]),
    "score_total": 85,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/586061/pexels-photo-586061.png?auto=compress&cs=tinysrgb&h=650&w=940",
    "image_caption": "A rocket launches from a spaceport against a dark cloudy sky",
    "image_attribution": "Pexels",
    "body": art1_body
}


# ─────────────────────────────────────────────────────────────────────
# ARTICLE 2: India IT Stocks Bloodbath + BlackRock Contrarian View
# ─────────────────────────────────────────────────────────────────────

art2_body = """The Nifty IT index has lost 27% of its value this year. TCS, Wipro, HCL Tech, and L&T Mindtree all hit fresh 52-week lows last week. Foreign investors have pulled a record $30 billion out of Indian equities in 2026, with the money flowing instead to South Korea and Taiwan, where semiconductor and memory stocks have surged on the AI trade.

By every surface metric, India's technology sector is in crisis. But two of the world's most influential fund managers now say the market has gone too far.

## The Bull Case From Unlikely Places

BlackRock, the planet's largest asset manager with $14 trillion under management, called India's equity market "over-punished" for lacking a direct AI play. Natasha Sarkaria, the firm's EMEA investment strategy lead, told Reuters that India remains one of BlackRock's "highest-conviction, medium- to long-term emerging-market trades."

The argument is not that India's IT services sector is fine. It plainly isn't. Analysts estimate that generative AI could cause 2–3% annual revenue deflation in traditional IT services over the next couple of years, as automation reduces the need for human labour in coding, application maintenance, and legacy system modernisation. Wipro has fallen 15.5% in seven sessions. Infosys has shed 12.3%. These are not rounding errors.

What BlackRock sees instead is the broader economy. India's GDP grew 7.8% in the March quarter, and the Reserve Bank maintains a 6.6–6.9% growth forecast for FY27. Demographics, infrastructure spending, and financials remain structural tailwinds that the IT selloff has dragged down indiscriminately.

## Picks and Shovels

Abhay Laijawala, CIO for India at Lighthouse Canton, a $5 billion wealth management firm, put the thesis most sharply: India's absence from the AI trade is actually an "advantage of absence."

The logic works like this. South Korea and Taiwan are now dangerously concentrated in semiconductor and memory names — TSMC, Samsung, SK Hynix. When sector concentration reaches those levels, Laijawala argued, investors "fatally underprice the possibility that a risk could emerge from outside the core business model." Both markets have already logged foreign outflows in June as positioning concerns mount.

India, by contrast, offers a deep universe of listed companies tied to the *next phase* of AI spending: power generation, data centres, electrical equipment, cooling systems, engineering, and capital goods. "We have plenty of picks and shovels," Laijawala told Reuters.

A TradingView analysis identified Indian industrial and infrastructure companies already benefiting from the trillions being deployed globally to build AI data centres. The thesis is that India's role in the AI era will not come through building the next NVIDIA — it will come through supplying the physical infrastructure that NVIDIA's customers need.

## What NRI Investors Should Watch

For the Indian professional in the US holding Infosys or TCS in their portfolio — or in their parents' demat accounts back home — the immediate picture is painful. The Nifty IT index has fallen 11.5% in just ten days since June 2. Kotak Securities' Sumit Pokharna noted that "productivity improvements in software engineering are occurring much faster than in non-software domains," which is the polite way of saying AI is eating IT services faster than those companies can adapt.

But the contrarian case deserves attention. India's market cap has slipped below Taiwan's and South Korea's for the first time, and its MSCI Emerging Markets weight has dropped from 12.82% in February to 10.87% in May. If BlackRock is right that the rotation has gone too far, a reversal would disproportionately benefit NRI investors with exposure to Indian equities.

The question is timing. Analysts suggest a cyclical recovery could emerge as early as September. Until then, the picks-and-shovels thesis remains just that — a thesis looking for a catalyst."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "India's IT Stocks Have Lost 27% This Year. BlackRock Says the Market Has It Wrong.",
    "subheadline": "Foreign investors have pulled a record $30 billion from Indian equities, but the world's largest asset manager and Lighthouse Canton argue India's 'absence' from the AI trade is being mispriced.",
    "slug": make_slug("india-it-stocks-crash-blackrock-lighthouse-canton-ai-advantage"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "NRI investors holding TCS, Infosys, or Wipro are watching portfolios bleed — but BlackRock and Lighthouse Canton say the picks-and-shovels AI infrastructure play makes India a contrarian buy.",
    "tags": ["indian-it", "blackrock", "nifty-it", "tcs", "infosys", "wipro", "ai-disruption", "investment"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/markets/asia/india-likely-past-peak-outflows-ai-gap-its-advantage-lighthouse-canton-says-2026-06-12/"},
        {"name": "Reuters", "url": "https://www.reuters.com/markets/asia/ai-oil-worries-have-over-punished-india-masked-long-term-investment-case-blackrock-2026-06-11/"},
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/markets/nifty-it-falls-most-ai-concerns/article69672346.ece"},
        {"name": "TradingView", "url": "https://www.tradingview.com/news/te_news:456981:0/"},
        {"name": "Outlook Money", "url": "https://www.outlookmoney.com/invest/nifty-it-crash-analysis-june-2026"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/16594725/pexels-photo-16594725.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
    "image_caption": "Financial trading screen with colorful charts and market data",
    "image_attribution": "Pexels",
    "body": art2_body
}


# ─────────────────────────────────────────────────────────────────────
# ARTICLE 3: India's Sovereign AI Debate After Anthropic Ban
# ─────────────────────────────────────────────────────────────────────

art3_body = """When the US Commerce Department ordered Anthropic to suspend its most powerful AI models for all foreign nationals on Thursday, the immediate reaction in India was predictable: alarm, frustration, calls to customer support. By Friday morning, the conversation had shifted to something more fundamental. A growing chorus of India's technology leaders is now arguing that the Anthropic episode proves the country needs its own AI — and needs it fast.

## "Globalization Is Dead"

Zoho founder Sridhar Vembu did not mince words. "Technology is the ultimate weapon. National sovereignty, national security, all of it is now about technology," he wrote on X. Then came the blunter assessment: "Globalization is dead and Bharat must find her own way ahead."

Vembu's prescription was specific. He urged Indian organisations to embrace smaller, open-source models — both Indian-built and Chinese — rather than depending on American frontier systems that can be switched off with a single government directive. The Anthropic ban, which covers Claude Fable 5 and Mythos 5 across all foreign nationals including those living and working inside the United States, made his point with uncomfortable clarity.

Mohandas Pai, the former Infosys CFO turned investor, went further. Responding to Vembu on X, Pai called for a ₹500 billion ($5 billion) annual government fund for AI and deep tech, alongside a ₹2 trillion ($21 billion) credit guarantee programme to support cloud infrastructure, hardware, and semiconductor development. For context, India's existing IndiaAI Mission, approved in 2024, allocated just ₹103.72 billion ($1.2 billion) over five years. Pai's proposal would dwarf it by an order of magnitude.

## The Infrastructure Gap

The ambition is not matched by the current reality. India remains a relatively small player in frontier model development. Only a handful of startups are pursuing foundational AI models. Sarvam AI, which released open-source models earlier this year and was recently invited to sit alongside OpenAI's Sam Altman and Google DeepMind's Demis Hassabis at the G7 summit, is the most visible. But Krutrim, Ola's high-profile AI venture, has already pivoted away from foundational model development toward cloud and infrastructure services — a tacit acknowledgement of how expensive the frontier game really is.

Hemant Mohapatra of Lightspeed India put a number on it: building a competitive foundational AI model from scratch costs between $250 million and $600 million. That is before compute costs, which are themselves constrained by the US AI Diffusion Framework that classifies India as a Tier 2 country, limiting access to advanced AI chips and cloud computing resources.

## The TCS Paradox

The sovereign AI debate unfolds against a peculiar backdrop. Just days before the Anthropic ban, TCS announced a major partnership with Anthropic itself — creating a dedicated business unit to deploy Claude across its enterprise clients and providing Claude to 50,000 of its own employees. Anthropic has described India as its "second-largest market."

The irony is hard to miss. India's largest IT services company is simultaneously building its business around an American AI provider and watching that provider get its most powerful models yanked by the American government. The TCS-Anthropic partnership remains intact — the ban covers only Fable 5 and Mythos 5, not earlier Claude models — but the episode has made the dependency structure painfully visible.

Srikanth Velamakanni, the Nasscom chairman, struck a measured tone, saying "managing this AI progress and making sure that AI is used responsibly requires coordinated global efforts." But the operative word in India's technology circles has shifted from "coordinated" to "sovereign."

## What NRIs Should Watch

For Indian engineers building with Claude or GPT at American companies, the ban introduces a new professional risk: your citizenship could determine which tools you can use at work. Dean Ball, a former White House official, noted that the order effectively means "you should expect to have to prove your citizenship to use Anthropic models." For H-1B holders, that is not a theoretical concern.

For those watching India's technology trajectory, the Anthropic episode may prove to be a catalyst. The sovereign AI argument has existed for years, but it has lacked urgency. It no longer does."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "Anthropic's Ban Lit a Fire Under India's Sovereign AI Movement. Here's Who's Fanning It.",
    "subheadline": "Zoho's Vembu calls globalization dead. Mohandas Pai demands a ₹500 billion AI fund. And TCS just partnered with the very company whose models got pulled.",
    "slug": make_slug("india-sovereign-ai-debate-vembu-pai-anthropic-ban"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "H-1B holders building with Claude may soon need to prove citizenship to access frontier models. India's sovereign AI push is no longer academic — it's a professional and national security reality for NRIs.",
    "tags": ["sovereign-ai", "anthropic", "sridhar-vembu", "zoho", "india-ai", "sarvam-ai", "mohandas-pai"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "TechCrunch", "url": "https://techcrunch.com/2026/06/13/as-anthropic-suspends-access-to-new-models-india-debates-ai-future/"},
        {"name": "Storyboard18", "url": "https://www.storyboard18.com/how-it-works/globalization-is-dead-zoho-sridhar-vembu-urges-india-to-back-open-source-ai-48293.htm"},
        {"name": "Reuters", "url": "https://www.reuters.com/technology/anthropic-disables-most-advanced-ai-models-us-order-2026-06-13/"},
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/info-tech/tech-experts-pitch-for-sovereign-ai/article69691537.ece"}
    ]),
    "score_total": 80,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/17483849/pexels-photo-17483849.png?auto=compress&cs=tinysrgb&h=650&w=940",
    "image_caption": "Abstract visualization of a neural network representing AI technology",
    "image_attribution": "Pexels",
    "body": art3_body
}


# ─────────────────────────────────────────────────────────────────────
# INSERT ALL
# ─────────────────────────────────────────────────────────────────────

articles = [art1, art2, art3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

#!/usr/bin/env python3
"""Videshi Tech Writer — 2026-06-28 14:00 PT run. Three articles."""

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
    return slug[:70].rstrip('-') + "-20260628"

# ─────────────────────────────────────────────────────────
# ARTICLE 1: Vishal Sikka / Hang Ten Systems
# ─────────────────────────────────────────────────────────
art1_body = """Vishal Sikka spent three years running Infosys, the company that wrote the playbook for Indian IT outsourcing. Now he wants to tear that playbook up.

Hang Ten Systems, Sikka's new Palo Alto-based startup, closed a $32 million seed round this week led by Mayfield, with strategic investment from Aramco Ventures and a group of angel investors. Yahoo co-founder Jerry Yang has joined the board. The company is already delivering AI-native projects for Siemens Gamesa Renewable Energy and Fresenius — two names that, not long ago, would have been prime targets for the traditional outsourcing sales machine Sikka once oversaw.

## The Thesis: AI Breaks the Old Economics

Hang Ten's pitch is deceptively simple: generative AI has made it possible to build, modify, and operate enterprise software at a fraction of the cost and time that traditional IT services firms charge. The startup uses agentic code generation, a reusable skills library, and domain expertise in finance, HR, and product development to deliver what Indian IT giants do with armies of engineers — but with far fewer people.

"Every single enterprise will be transformed by AI," Sikka said in the company's launch statement. "A few are already reaping massive benefits, building in days what used to take years. But most are stuck at the starting line, or worse, and the gap is widening every day."

The founding team reads like a reunion of Sikka's previous stops. Co-founders include CTO Navin Budhiraja, chief design officer Sanjay Rajagopalan, and SVP of Forward Deployed Engineering Tao Liu — all veterans of SAP, Infosys, or Sikka's prior venture VianAI. The band is back together, but the instrument has changed.

## Why This Matters to Indian Tech Workers

The $500 billion global IT services industry employs millions of Indian engineers, both in India and on H-1B visas in the United States. Companies like TCS, Infosys, Wipro, and HCL Tech built their businesses on the "body shop" model — billing by the hour, scaling by adding headcount. AI-native competitors like Hang Ten threaten to collapse that margin structure.

The timing is particularly awkward. Accenture's latest guidance cut — lowering FY26 revenue growth to 3–4% from 4–5% — has already rattled Indian IT stocks this month. Analysts at Motilal Oswal warned last week that "a new, platformised AI-native vendor template will emerge," citing OpenAI's DeployCo and Anthropic's services company as credible blueprints for the next-generation system integrator.

Sikka's former employer is squarely in the crosshairs. Infosys shares fell over 7% after the Accenture warning. For the roughly 300,000 Indian tech workers in the U.S. on employer-sponsored visas, any structural shift in the IT services model carries employment risk far beyond quarterly earnings.

## The Irony, and the Opportunity

There is a certain poetry in an Indian-born technologist who once ran India's most iconic IT company now building the tool that could disrupt it. But Sikka would argue the disruption was coming regardless — better to ride the wave than be swept by it.

For NRI engineers and investors watching from the Bay Area, the signal is clear: the model that brought hundreds of thousands of Indians to Silicon Valley is under existential pressure. The winners in the next chapter may not scale by headcount at all."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "The Man Who Ran Infosys Just Raised $32 Million to Make It Obsolete",
    "subheadline": "Vishal Sikka's new AI startup Hang Ten Systems wants to do what Indian IT giants do with thousands of engineers — but with agentic code generation and a fraction of the people.",
    "slug": make_slug("vishal-sikka-hang-ten-ai-infosys-it-services"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Former Infosys CEO building AI-native IT services threatens the outsourcing model that employs millions of Indian engineers and sustains hundreds of thousands of H-1B jobs in the US.",
    "tags": ["ai", "enterprise-ai", "indian-tech-leaders", "it-services", "startups", "infosys", "h1b"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Mitrade", "url": "https://www.mitrade.com/insights/news/live-news/article-8-11006220260625"},
        {"name": "The Mainstream", "url": "https://themainstream.co.in/hang-ten-systems-secures-32-million-seed-funding/"},
        {"name": "Analytics Insight", "url": "https://www.analyticsinsight.net/startup-news-today/vishal-sikkas-enterprise-ai-startup-hang-ten-raises-32-million"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/62/VishalSikkaSapphireOrlando2010.jpg/3840px-VishalSikkaSapphireOrlando2010.jpg",
    "image_caption": "Vishal Sikka, former Infosys CEO and founder of Hang Ten Systems",
    "image_attribution": "Wikimedia Commons",
    "body": art1_body.strip()
}

# ─────────────────────────────────────────────────────────
# ARTICLE 2: Accenture Guidance Cut / Indian IT Reckoning
# ─────────────────────────────────────────────────────────
art2_body = """Accenture cut its full-year revenue growth forecast to 3–4%, down from 4–5%, and Indian IT stocks did the rest. The Nifty IT Index plunged over 5% in a single session. TCS shed more than 5%. Infosys dropped over 7%. For an industry that employs over five million people in India and sustains the largest pipeline of H-1B workers to the United States, this was not just a bad day on the Dalal Street. It was a warning shot.

## The Numbers Behind the Panic

Accenture CEO Julie Sweet attributed the cut to a $90 million revenue shortfall and $100 million in impact from the Middle East conflict, which has disrupted client spending in key sectors. The company's managed services revenue — the outsourcing business that directly competes with Indian IT firms — grew just 5% year-on-year, with deal signings decelerating as clients freeze budgets in the face of geopolitical uncertainty.

Global IT spending still exceeds $6 trillion in 2026, but the money is flowing in unfamiliar directions. Cybersecurity and AI compliance mandates are eating into traditional infrastructure and maintenance budgets — the bread and butter of TCS, Infosys, Wipro, and HCL Tech. Citi analysts noted that the Nifty IT index trades at a premium compared to Accenture's own valuation, suggesting Indian IT stocks may have further to fall.

## The AI Threat No One Wants to Name

The more alarming signal came not from Accenture's earnings call but from a Motilal Oswal report published the same week. The brokerage warned that "a new, platformised AI-native vendor template will emerge," naming OpenAI's DeployCo and Anthropic's services company as the first credible blueprints for next-generation system integrators.

JP Morgan's analysts were blunter: AI remains a net headwind for the industry, with the adoption cycle likely to pass through three phases — deflation, digestion, and reflation — before AI services revenue grows large enough to offset the drag from AI-driven productivity gains. The painful "digestion" phase, they warned, could extend beyond FY29.

This is the paradox Indian IT companies face: AI is the future of enterprise technology, but adopting it aggressively means cannibalising the labour-intensive model that generates their margins. Nasscom projects a $400 billion AI services market, but it is far from clear that the companies built on billing by the engineer-hour are the ones who will capture it.

## What This Means for NRIs

For the estimated 300,000 Indian IT professionals working in the United States on H-1B and L-1 visas, this is personal. The top Indian IT firms — TCS, Infosys, Wipro, Cognizant, HCL Tech — are among the largest H-1B sponsors in the country. Any structural decline in their US revenue directly affects hiring, visa renewals, and the career trajectories of workers whose immigration status depends on employer sponsorship.

The downstream effects are already visible. India's tech job market hit a 28-month low earlier this month. For returning H-1B workers — those whose visas were not renewed or whose roles were eliminated — the domestic market offers little relief.

Nomura's latest note projects that West Asia conflict disruptions will weigh on deal bookings through Q2 FY27, with "indirect impact likely to continue as it is unclear how quickly spending behaviour will normalise." For NRI investors holding Indian IT stocks, the calculus has shifted: this is no longer a cyclical dip to buy. It may be a structural transition to endure."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "Accenture's Growth Warning Just Wiped Billions Off Indian IT. The Real Threat Is Deeper.",
    "subheadline": "A revenue guidance cut sent TCS and Infosys into freefall. But the bigger danger is an AI-native competitor class that could reshape who builds enterprise software — and who gets laid off first.",
    "slug": make_slug("accenture-guidance-cut-indian-it-stocks-ai-threat"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Indian IT stocks crashed after Accenture's guidance cut, threatening H-1B employment pipelines and NRI portfolios as AI-native vendors emerge to displace the traditional outsourcing model.",
    "tags": ["it-services", "infosys", "tcs", "accenture", "ai-disruption", "h1b", "indian-it", "stock-market"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "AInvest", "url": "https://www.ainvest.com/news/accentures-revenue-growth-guidance-cut-sends-shockwaves-through-tech-industry/"},
        {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com/info-tech/indian-it-faces-fy27-guidance-cut-risk-as-ai-geopolitics-cloud-demand/"},
        {"name": "Reuters", "url": "https://www.reuters.com/markets/asia/indian-shares-rise-reliance-it-rebound-mideast-hopes-lift-sentiment-2026-06-22/"}
    ]),
    "score_total": 85,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/210607/pexels-photo-210607.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "Stock market trading screens displaying real-time market data",
    "image_attribution": "Pexels",
    "body": art2_body.strip()
}

# ─────────────────────────────────────────────────────────
# ARTICLE 3: Jio Platforms IPO — H2 2026
# ─────────────────────────────────────────────────────────
art3_body = """Mukesh Ambani has been promising to take Jio Platforms public since 2019. Seven years and multiple postponements later, the listing finally appears imminent — and its implications for NRI investors stretch well beyond a single stock ticker.

Jio Platforms is set to launch India's largest-ever IPO in the second half of 2026, with plans to raise approximately ₹37,700 crore (roughly $4.5 billion) by selling a 2.5% stake. At the Jefferies-estimated valuation of $180 billion, this would dwarf Hyundai Motor India's $3.3 billion listing in 2024, the current record holder.

## From Offer-for-Sale to Fresh Fundraising

In a significant pivot reported by Reuters in May, Jio Platforms dropped earlier plans that would have allowed existing investors — including Meta, Google, and Vista Equity Partners — to exit through the IPO. Instead, the listing has become a pure fundraising exercise. "Investors were not keen to sell and wanted to stay invested for the long term," a source told Reuters.

The decision speaks to confidence in Jio's trajectory, but it also means the IPO float will be slim. A 2.5% free float on a $180–240 billion company creates pricing tension by design — limited supply, enormous demand. The listing structure hinges on a proposed SEBI regulation change, still awaiting finance ministry approval, that would reduce the minimum IPO share from 5% to 2.5% for large companies.

## What Jio Actually Is Now

Most diaspora Indians know Jio as the company that upended Indian telecom with free data in 2016, amassing over 500 million subscribers. But the company Ambani is bringing public in 2026 is a different beast.

Jio Platforms now encompasses the telecom operator, JioSaavn (music streaming), JioMart (e-commerce), JioCinema (video), a $100 million AI joint venture with Meta, a Google Cloud partnership for a dedicated Jamnagar data region, and an AI unit that Ambani announced at last year's AGM. About 75–80% of revenue still comes from telecom, but the valuation premium rests on Jio's transformation into a digital services and AI platform.

At the Reliance AGM on June 19, brokerages noted that Jio Platforms and Reliance's new energy business are the primary growth drivers justifying the conglomerate's premium valuation. The AGM arrived after Reliance reported record FY26 revenue of ₹11.76 lakh crore and net profit of ₹95,754 crore.

## The NRI Investment Calculus

For the estimated 4.5 million Indian-Americans and millions more NRIs in the UK, Canada, and the Gulf, Jio's listing poses a practical question: how to participate.

NRIs can invest in Indian IPOs through Portfolio Investment Scheme (PIS) accounts linked to NRE or NRO demat accounts, but the process is notoriously cumbersome — multiple KYC requirements, FEMA compliance, and bank-specific restrictions. For US-based NRIs, the additional layer of FATCA reporting requirements and potential capital gains tax complexity in both jurisdictions makes the calculation more involved than simply clicking "apply."

The alternative is waiting for Jio to eventually list ADRs in the United States, but Reliance has given no indication of a dual listing.

Jio is not the only blockbuster in India's H2 2026 pipeline. The National Stock Exchange (₹30,000 crore), Zepto (₹8,010 crore), and Acko (₹2,831 crore) are all lined up. But Jio is the one that defines whether India's capital markets can absorb a $180 billion tech listing — and whether NRIs get a real seat at the table when they do."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "Ambani's $180 Billion Jio IPO Is Finally Happening. NRIs Have a Seat Problem.",
    "subheadline": "India's largest-ever listing is set for the second half of 2026. For Indian-Americans eager to invest, the real challenge is not the valuation — it's the paperwork.",
    "slug": make_slug("jio-platforms-ipo-h2-2026-nri-investors"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Jio's IPO is India's most-anticipated listing of the decade, and NRIs face practical investment hurdles including PIS account requirements, FEMA compliance, and FATCA reporting that may limit their participation.",
    "tags": ["ipo", "jio", "reliance", "mukesh-ambani", "nri-investing", "india-tech", "telecom"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/business/ambanis-reliance-jio-considers-25-public-offering-2026-india-ipo-sources-say-2026-01-09/"},
        {"name": "Reuters", "url": "https://www.reuters.com/business/ambanis-jio-platforms-ipo-pivots-pure-fundraising-no-investor-exits-sources-say-2026-05-12/"},
        {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com/companies/reliance-agm-2026-jio-ipo-ai-push-ambani-leaders-under-spotlight/article69705982.ece"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/6/69/Mukesh_Ambani.jpg",
    "image_caption": "Mukesh Ambani, chairman of Reliance Industries and the driving force behind the Jio Platforms IPO",
    "image_attribution": "Wikimedia Commons",
    "body": art3_body.strip()
}

# ─────────────────────────────────────────────────────────
# INSERT
# ─────────────────────────────────────────────────────────
articles = [art1, art2, art3]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-06-09 21:00 UTC batch."""

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
# ARTICLE 1: AI Job Cuts
# ─────────────────────────────────────────────

art1_body = """AI just became the single biggest reason American companies fire people. And the workers most exposed are the ones who built the technology in the first place.

New data from outplacement firm Challenger, Gray & Christmas shows that U.S. employers announced 97,006 job cuts in May 2026 — the highest May total since the onset of COVID-19 in 2020. Artificial intelligence was cited as the primary reason for 38,579 of those cuts, accounting for 40 percent of all announced layoffs. It marked the third consecutive month that AI topped the layoff ledger.

The trajectory is striking. AI-related cuts climbed from 7 percent of all layoffs in January to 10 percent in February, 25 percent in March, 26 percent in April, and now 40 percent in May. Through the first five months of 2026, companies have attributed 87,714 job cuts to AI adoption — already exceeding the combined total of the previous two years (54,836 in 2025 and 12,742 in 2024).

## The Tech Sector Is Ground Zero

Technology companies bore the heaviest losses. The sector announced 38,242 cuts in May alone, its highest monthly total since August 2024. Year-to-date, tech layoffs have surged 66 percent to 123,653, running at nearly three times the rate of the next most-affected industry.

"The labor market is being reshaped by technology in real time," said Andy Challenger, chief revenue officer of Challenger, Gray & Christmas. "AI isn't yet the jobpocalypse some predicted. Like spreadsheets and email before it, the technology will ultimately make workers more productive — but our data shows companies are already acting on it."

## Why Indian Tech Workers Should Pay Attention

For the roughly 600,000 Indian nationals working in the United States on H-1B visas — the majority of whom are employed in technology — these numbers carry a particular weight. An H-1B worker who loses their job has exactly 60 days to find new sponsorship, transfer to another visa category, or leave the country. When the sector shedding the most jobs is the same one that employs the most visa holders, the math gets uncomfortable fast.

The pressure isn't confined to Silicon Valley. Oracle announced 30,000 global layoffs this month, with India absorbing an estimated 12,000. TCS Chairman N. Chandrasekaran told shareholders on the same day this data dropped that TCS expects to have as many AI agents as employees — half a million of each — and that hiring across the industry will slow accordingly. TCS headcount fell by more than 23,000 on a net basis in the fiscal year ended March 2026.

## The Paradox

The same technology that is eliminating roles is also creating new ones — but not in equal measure, and not for the same people. Companies are restructuring around AI, not simply layering it on top of existing teams. Roles in prompt engineering, AI infrastructure, and model fine-tuning are growing. Traditional software testing, junior development, and IT support are contracting.

For NRI professionals navigating this transition, the calculus is straightforward: the 60-day clock doesn't care about your skill upgrade timeline. Those with AI-adjacent expertise have leverage; those without it face a tightening window in a market where the very act of automation is being used as corporate justification for headcount reduction.

The open question, as Challenger put it, is not whether AI changes the workforce. It's how fast."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "AI Is Now America's Top Reason for Firing People. H-1B Workers Are Watching the Clock.",
    "subheadline": "U.S. employers cut 97,000 jobs in May. AI was cited in 40 percent of them — the highest share ever recorded. For Indian tech workers on visas, the 60-day grace period has never felt shorter.",
    "slug": make_slug("ai-top-reason-us-job-cuts-h1b-workers-60-day-clock"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Indian H-1B visa holders make up the largest share of the tech workforce being cut. The 60-day grace period to find new sponsorship creates existential pressure when the entire sector is shedding jobs, and TCS just warned hiring will slow across Indian IT.",
    "tags": ["ai", "layoffs", "h-1b", "tech-jobs", "indian-tech-workers", "automation"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Fox Business", "url": "https://www.foxbusiness.com/economy/ai-remains-top-reason-us-job-cuts-third-straight-month"},
        {"name": "Challenger, Gray & Christmas (via Outlook Business)", "url": "https://outlookbusiness.com/corporate/ai-overtakes-all-other-reasons-for-us-job-cuts-as-layoffs-surge-in-2026"},
        {"name": "Reuters (TCS)", "url": "https://www.reuters.com/technology/indias-tcs-chair-says-ai-agents-may-equal-headcount-dampen-hiring-2026-06-09/"}
    ]),
    "score_total": 85,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/6806092/pexels-photo-6806092.jpeg",
    "image_caption": "Empty desks at a technology company office following workforce reductions",
    "image_attribution": "Pexels",
    "body": art1_body,
}

# ─────────────────────────────────────────────
# ARTICLE 2: Cerebras IPO Analyst Coverage
# ─────────────────────────────────────────────

art2_body = """Cerebras Systems went public last month at $185 a share. By its second day of trading, the stock had nearly doubled to $350. Then it fell 36 percent. Now Wall Street is telling everyone to buy the dip.

Nine brokerages initiated coverage on Cerebras (CBRS) on Monday, and the consensus is unambiguous: the company that builds the world's largest commercial chip has a first-mover advantage that rivals cannot easily replicate. Morgan Stanley, Citigroup, Barclays, UBS, Wedbush, Mizuho, and Rosenblatt all issued buy-equivalent ratings with price targets ranging from $250 to $340 — implying 10 to 50 percent upside from Friday's close of roughly $226.

The Cerebras pitch rests on one bet: that the next chapter of AI isn't about training models. It's about running them.

## The Inference Pivot

For three years, the AI industry has been obsessed with training — the computationally expensive process of teaching models to understand language, images, and reasoning. NVIDIA dominated that era. Now the action is shifting to inference: the moment a trained model generates an answer, writes code, or produces an image for an actual user. Inference demands speed and low latency above all else.

Cerebras' Wafer-Scale Engine (WSE-3) is purpose-built for that shift. It packs 4 trillion transistors and 900,000 cores onto a single wafer the size of a dinner plate, with 21 petabytes per second of memory bandwidth. The company claims it runs inference workloads 21 times faster and at one-third the cost of NVIDIA's DGX B200 Blackwell GPU.

"We view Cerebras as one of the most differentiated AI infrastructure companies, built around the industry's only commercially deployed wafer-scale processor," wrote Morgan Stanley analyst Joseph Moore, who set a $250 price target. "This is a unique chance to invest in an AI processor company with a first-mover advantage against NVIDIA."

## The OpenAI Anchor

What turns Cerebras from a speculative hardware play into a serious contender is its customer list. In December 2025, OpenAI signed a multi-year deal worth over $10 billion for 750 megawatts of Cerebras compute capacity through 2028. AWS has also committed to deploying Cerebras systems. Those two contracts anchor a $24.6 billion order backlog.

But concentration is the risk. The OpenAI deal accounts for the bulk of that backlog. Real, recognized revenue from the past year is approximately $510 million, with 86 percent of it coming from a single government-linked ecosystem in the UAE — G42 and the related MBZUAI research university. The company trades at roughly 225 times earnings.

"The backlog is not revenue — and that's the whole problem," one independent analysis noted. "A backlog is a contract, not an invoice."

## Why NRI Investors Should Watch

Cerebras is not yet a mainstream portfolio name, but the dynamics it represents — the inference revolution, the challenge to NVIDIA's monopoly, the economics of real-time AI — will shape the tech sector that employs hundreds of thousands of Indian engineers and in which NRI portfolios are heavily concentrated.

If Cerebras delivers on its OpenAI and AWS commitments, it validates an alternative architecture for AI computing that could disrupt the GPU-centric model that has driven NVIDIA's $3 trillion market cap. If it doesn't, the stock is priced for perfection that may never arrive.

Citigroup's $340 target is the most bullish. Morgan Stanley's $250 is the most conservative. The truth, as with most things in semiconductor investing, will be found somewhere between the transistors."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "Cerebras Just IPO'd at $44 Billion. Nine Analysts Say Buy the Dip.",
    "subheadline": "Wall Street initiated coverage on the dinner-plate-sized chip company with buy ratings across the board. The OpenAI deal, the inference bet, and the NVIDIA challenge are all priced in. Or are they?",
    "slug": make_slug("cerebras-ipo-44-billion-nine-analysts-buy-inference"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "NRI investors with heavy exposure to AI and semiconductor stocks need to understand Cerebras as a potential disruptor to NVIDIA's dominance. The inference revolution it represents will also reshape the compute economics that Indian AI startups like Sarvam AI depend on.",
    "tags": ["cerebras", "ipo", "ai-chips", "nvidia", "openai", "inference", "semiconductor"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Barchart", "url": "https://www.barchart.com/story/news/32966345/analysts-flood-cerebras-systems-cbrs-with-buy-calls"},
        {"name": "CoinCentral", "url": "https://coincentral.com/cerebras-cbrs-stock-dropped-30-from-its-ipo-high-wall-street-just-said-buy/"},
        {"name": "The Street (Morgan Stanley)", "url": "https://www.thestreet.com/technology/morgan-stanley-sets-first-ever-cerebras-stock-price-target"},
        {"name": "AInvest (Cerebras analysis)", "url": "https://ainvest.com/news/cerebras-fell-42-from-its-ipo-high-the-narrative-is-the-real-trap/"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/e/eb/12-inch_silicon_wafer.jpg",
    "image_caption": "A 12-inch silicon wafer — Cerebras builds its processors on entire wafers rather than cutting them into individual chips",
    "image_attribution": "Wikimedia Commons",
    "body": art2_body,
}

# ─────────────────────────────────────────────
# ARTICLE 3: OpenAI IPO / $4 Trillion Wave
# ─────────────────────────────────────────────

art3_body = """OpenAI has filed its confidential S-1 with the SEC, setting the stage for what could be the most consequential technology IPO since Google went public in 2004. But this time, it won't be alone on the runway.

Within weeks of each other, three companies — SpaceX, Anthropic, and OpenAI — are expected to debut on public markets at a combined valuation exceeding $4 trillion. SpaceX leads, with shares set to begin trading on June 12 at a valuation of approximately $1.77 trillion and a target raise of $75 billion. Anthropic filed its own confidential S-1 last week at an estimated $965 billion valuation. OpenAI's filing, which followed Monday, puts it at roughly $1 trillion based on recent private funding rounds.

To put that in context: there are currently only 11 companies in the entire S&P 500 with market capitalizations above $1 trillion. Three more are about to join, none of which has ever posted a sustained annual profit.

## The Numbers That Don't Add Up (Yet)

OpenAI loses approximately $1.22 for every $1 of revenue it generates. The company is projected to spend roughly $600 billion by the end of the decade to maintain its AI infrastructure. ChatGPT serves over 900 million weekly users, but the economic model behind that usage remains, to put it charitably, aspirational.

Anthropic is the exception — barely. The Claude maker is expected to post a small operating profit in Q2 2026 thanks to a quarter-over-quarter revenue doubling, with an annualized run rate of $47 billion. But its spending trajectory suggests profitability won't last.

SpaceX is the outlier with actual cash flow. Its Starlink satellite internet business is the fastest-growing telecom company in history, and its rocket launch division holds a near-monopoly on heavy launches. Goldman Sachs projects SpaceX revenue reaching $322 billion by 2030. But even SpaceX trades at 100 times trailing revenue.

## The Historical Warning

Barron's analysis of 30 major technology IPOs over the past 15 years, compiled by Truist Wealth, found that they averaged a maximum decline of 55 percent in the first year of trading. Forward returns were negative at the six-month mark as well.

The Indian market offers its own cautionary tale. Reliance Power's record ₹11,700 crore IPO in January 2008 preceded a 55 percent crash in the Nifty 50 within the year. Coal India's ₹15,475 crore offering in October 2010 was followed by a 28 percent correction.

"The coming IPO wave may dampen forward market returns, mute further multiple expansion, and possibly interrupt sector trends," wrote strategists at BCA Research.

## The NRI Portfolio Problem

For Indian Americans with significant exposure to technology stocks — which describes most NRI portfolios — the $4 trillion listing wave presents a concrete allocation question. These three IPOs will absorb an estimated $150 to $200 billion in primary capital. That money has to come from somewhere: existing positions in NVIDIA, Microsoft, Google, and the broader tech basket.

Fund managers warn of a liquidity squeeze. "With these mega IPOs and all that new issuance, will investors absorb all of this new stock supply?" asked Ron Albahary, chief investment officer at LNW. The risk isn't that SpaceX or Anthropic are bad companies. The risk is that their sheer size crowds out everything else.

Investment bankers have reportedly advised OpenAI and Anthropic that the first large AI company to list publicly could shape how investors value the entire category. The race to go first isn't vanity. It's strategy.

For NRI investors, the practical question is simpler: do you sell part of your existing tech position to buy into the IPO, or do you let the dust settle and buy the six-month dip that history says is coming?"""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "OpenAI Just Filed for an IPO. A $4 Trillion Listing Wave Is About to Hit.",
    "subheadline": "SpaceX, Anthropic, and OpenAI are heading to public markets within weeks of each other. The combined valuation rivals the GDP of Germany. History says mega-IPOs end badly for early buyers.",
    "slug": make_slug("openai-ipo-filing-spacex-anthropic-4-trillion-listing-wave"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "NRI portfolios are heavily concentrated in the same tech stocks that will compete for capital with these mega-IPOs. The $150-$200 billion in primary issuance could trigger a liquidity squeeze across NVIDIA, Microsoft, and Google — the backbone of most Indian American investment accounts.",
    "tags": ["openai", "ipo", "spacex", "anthropic", "ai-investing", "markets", "nri-investors"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "CoinCentral", "url": "https://coincentral.com/sam-altmans-openai-files-confidential-ipo-as-ai-listing-race-accelerates/"},
        {"name": "Barron's", "url": "https://www.barrons.com/articles/openai-spacex-anthropic-ipo-stock-markets-4-trillion"},
        {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com/portfolio/stock-fundamental-analysis-data/spacex-anthropic-openai-can-rewrite-history-for-megacap-ipos/article69660742.ece"},
        {"name": "Motley Fool", "url": "https://www.fool.com/investing/2026/06/09/spacex-anthropic-openai-gargantuan-ipos/"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/5/5a/Meeting_with_Masayoshi_Son_and_Sam_Altman_%28February_3%2C_2025%29_%283x4_cropped_on_Altman%29.jpg",
    "image_caption": "OpenAI CEO Sam Altman, whose company just filed a confidential S-1 for a public listing",
    "image_attribution": "Wikimedia Commons",
    "body": art3_body,
}

# ─────────────────────────────────────────────
# INSERT ALL
# ─────────────────────────────────────────────

articles = [art1, art2, art3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

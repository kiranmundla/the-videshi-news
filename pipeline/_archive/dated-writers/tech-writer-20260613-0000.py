#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-06-13 00:00 UTC batch"""

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
# ARTICLE 1: Forbes 250 + Midas List
# ─────────────────────────────────────────────

article1_body = """Twenty-seven Indian-origin leaders appear on the Forbes list of America's 250 Most Successful Immigrants, released this week to mark the country's 250th anniversary. Separately, 17 Indian Americans have been named to the 2026 Forbes Midas List of the world's top 100 venture capitalists. Together, the two lists amount to a data-point that is hard to ignore: Indians now occupy a disproportionately large share of the commanding heights of American business, technology, and finance.

The timing, of course, is exquisite. These recognitions arrive in the same month that a new congressional bill proposes to eliminate the H-1B lottery, end Optional Practical Training, and sever the pathway from work visa to green card. The juxtaposition is not subtle: the same immigration pipeline that produced Sundar Pichai, Satya Nadella, and Vinod Khosla is the one legislators are trying to dismantle.

## The Forbes 250

The immigrant list reads like a who's who of corporate America. Vinod Khosla, the Pune-born co-founder of Sun Microsystems and founder of Khosla Ventures, ranks 14th overall — the highest-placed Indian-origin leader. Naval Ravikant, co-founder of AngelList and early investor in Uber and Twitter, sits at 27th.

The technology cohort alone is staggering: Google CEO Sundar Pichai, Microsoft CEO Satya Nadella, IBM Chairman Arvind Krishna, Adobe CEO Shantanu Narayen, Palo Alto Networks CEO Nikesh Arora, Micron CEO Sanjay Mehrotra, and Confluent co-founder Neha Narkhede all made the cut. Outside tech, Nobel laureate Abhijit Banerjee, former PepsiCo chief Indra Nooyi, philanthropist Neerja Sethi, and TV host Padma Lakshmi round out the Indian contingent.

The overall top five — Schwarzenegger, Musk, Jensen Huang, Sergey Brin, and Rupert Murdoch — are a reminder that immigration has been the silent engine of American economic supremacy for centuries. Forbes itself noted that companies tied to immigrant founders and CEOs, including Nvidia, Google, AMD, DoorDash, Zoom, Databricks, Snowflake, Anthropic, and Perplexity, now collectively represent trillions of dollars in market value.

## The Midas List

The venture capital side of the ledger is equally striking. Khosla tops the 2026 Forbes Midas List at No. 1 worldwide — his 19th appearance on the ranking and a return to the summit he first occupied in 2001, when the list was inaugurated. Forbes credited his early investment in OpenAI, made in 2019 when the company was still a nonprofit research lab, as the primary driver.

"The technologies change. The game doesn't," Khosla said. "Most important breakthroughs look unreasonable at first, until entrepreneurs make them inevitable."

Behind Khosla, Eric Vishria of Benchmark (an early backer of Cerebras) placed third, Shardul Shah of Index Ventures tenth, Saurabh Gupta of DST Global fifteenth, and Ravi Mhatre of Lightspeed sixteenth. Further down: Hemant Taneja of General Catalyst (19th), Navin Chaddha of Mayfield (51st), Asheem Chandna of Greylock (73rd), and Salil Deshpande of Uncorrelated Ventures (100th). In total, 17 of the world's top 100 VCs are of Indian origin — a community that represents roughly 1.4 per cent of the American population holding 17 per cent of the seats at venture capital's most exclusive table.

Indiaspora, the leading diaspora network, noted the selection reflects "the growing and indispensable role Indian Americans play in the startup ecosystems powering Silicon Valley and entrepreneurship hubs around the world."

## The Irony at the Gate

The uncomfortable subtext is difficult to miss. These lists celebrate the fruits of a system that allowed ambitious immigrants — many of whom arrived on student visas and graduated through H-1B sponsorship — to build careers, found companies, and eventually run them. The proposed legislation moving through Congress would functionally close that pipeline for the next generation.

For Indian Americans currently working in tech, the Forbes lists are a source of community pride. But for the graduate student at IIT Bombay weighing an American MBA against a Bangalore startup, or the H-1B holder at Google nervously checking USCIS processing times, the message is more complicated: the door that was open for Pichai and Nadella may not stay open forever.

*Sources: Forbes, Global Net News, Gulte, Indiaspora*"""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "Twenty-Seven Indians Made Forbes' List of America's Most Successful Immigrants. The Timing Is Pointed.",
    "subheadline": "Forbes names 27 Indian-origin leaders among America's 250 most successful immigrants and 17 Indian Americans among the world's top 100 venture capitalists — the same month a bill threatens to gut H-1B.",
    "slug": make_slug("forbes-250-immigrants-midas-list-indian-americans-vc"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "The lists celebrate Indian immigrant success in American tech and VC while new legislation threatens the very immigration pipeline that produced these leaders — a direct tension for every NRI family with ties to the H-1B system.",
    "tags": ["indian-americans", "forbes", "venture-capital", "vinod-khosla", "silicon-valley", "immigration"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Forbes", "url": "https://www.forbes.com/lists/midas/"},
        {"name": "Global Net News", "url": "https://globalnet.news/17-persons-of-indian-origin-on-forbes-list-2026/"},
        {"name": "Gulte", "url": "https://www.gulte.com/news/27-indians-shine-in-forbes-us-immigrant-list"},
        {"name": "India Tribune", "url": "https://www.indiatribune.com/from-pune-to-silicon-valley-vinod-khoslas-openai-gamble-powers-a-historic-return-to-the-top/"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f7/2024-03-14_SXSW_Vinod-Khosla_08741.jpg/3840px-2024-03-14_SXSW_Vinod-Khosla_08741.jpg",
    "image_caption": "Vinod Khosla at SXSW 2024, now ranked No. 1 on the Forbes Midas List",
    "image_attribution": "Wikimedia Commons",
    "body": article1_body,
}


# ─────────────────────────────────────────────
# ARTICLE 2: Indian IT stocks crash
# ─────────────────────────────────────────────

article2_body = """The Nifty IT index has lost 27 per cent of its value in six months. On Thursday, TCS, Wipro, HCL Technologies, and LTIMindtree all hit fresh 52-week lows. Infosys fell nearly 3 per cent in a single session. The sector is now the worst performer on Dalal Street, and the reason is not a recession, a regulatory crackdown, or a currency shock. It is a chatbot.

Specifically, it is Claude Fable 5 — Anthropic's latest AI model, released earlier this month — and the capabilities it demonstrated in software engineering. According to Sumit Pokharna of Kotak Securities, the new model delivers "AI-generated code quality approaching human levels and potentially surpassing it within the next year." For an industry that bills tens of billions of dollars a year for application development and maintenance, the implications are existential.

## The Numbers

India's IT services sector is worth roughly $315 billion in annual revenue. TCS alone employs over 600,000 people. Infosys, Wipro, HCL Technologies, and Tech Mahindra together employ another million. The industry is the largest private-sector employer in India and the single biggest reason for the Indian middle class's integration into the global knowledge economy.

The Nifty IT index closed at 27,821 on Thursday, down from 31,117 just eleven days earlier — an 11.5 per cent collapse in under two weeks. TCS shares have fallen over 32 per cent since January. The broader selloff was amplified by a global tech rout driven by hot US inflation data and pre-IPO fund reallocation, but the Indian IT decline has been deeper and more sustained than the broader market.

## Why Fable 5 Matters

The concern is not that AI will replace Indian software engineers overnight. It is that AI will reduce the number of billable hours required per project, compressing revenue per contract even as the work gets done. This is what analysts call "revenue deflation" — the same output, fewer hours, lower bills.

Pokharna noted that "productivity improvements in software engineering are occurring much faster than in non-software domains," which puts companies with heavy exposure to application development and maintenance (ADM) contracts at greatest risk. Among the big five, Infosys has the highest ADM exposure. HCL Technologies, with its larger infrastructure and engineering services portfolio, has somewhat less.

Persistent Systems, a mid-cap favourite among NRI investors, has one of the highest application development exposures of any listed IT firm and has been hit particularly hard.

## The TCS Pivot

TCS Chairman N. Chandrasekaran addressed the question directly at the company's annual general meeting this week. "If the company has half a million employees, the day is not far when the company will have half a million AI agents," he said. The company signed a partnership with Anthropic on Thursday to deploy Claude across 50,000 associates, joining Infosys, which struck a similar deal in February.

The message is clear: the big IT firms are not fighting AI. They are trying to absorb it before it absorbs them. TCS has said it will not lay off staff en masse but will hire less. Net headcount fell by 23,000 in the fiscal year ended March 2026. The company cut 12,000 jobs last July alone.

## What It Means for NRIs

For the Indian engineer in Hyderabad or the H-1B holder at an IT services company in New Jersey, the anxiety is concrete. If AI shrinks the number of projects that require human developers, the pipeline of L-1 and H-1B transfers from Indian IT companies to US clients could slow. For NRI investors, the portfolio damage is already real — TCS, Infosys, and Wipro are staples of Indian equity portfolios, and the sector's 27 per cent decline in six months has wiped out years of returns.

The broader question — whether India's IT industry can transition from a labour-arbitrage model to an AI-augmented one fast enough — will determine the fortunes of millions. The answer is not yet clear. What is clear is that the market has stopped giving it the benefit of the doubt.

*Sources: The Hindu BusinessLine, Reuters, LiveMint, Kotak Securities*"""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "India's IT Sector Has Lost 27 Per Cent in Six Months. Claude Fable 5 Was the Last Straw.",
    "subheadline": "TCS, Infosys, Wipro, and HCL all hit 52-week lows as analysts warn that AI-generated code is compressing billable hours — threatening the revenue model that built India's tech middle class.",
    "slug": make_slug("india-it-stocks-crash-ai-disruption-claude-fable"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "NRI investors hold TCS/Infosys/Wipro as portfolio staples, and H-1B workers at IT services companies face shrinking transfer pipelines as AI reduces the headcount these firms deploy to US clients.",
    "tags": ["indian-it", "tcs", "infosys", "wipro", "ai-disruption", "nifty-it", "anthropic"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/markets/it-rout-infosys-hcl-tech-tcs-shares-fall-as-nifty-it-declines-3-on-global-tech-selloff/article71087975.ece"},
        {"name": "Reuters", "url": "https://www.reuters.com/technology/indias-tcs-partners-with-anthropic-drive-enterprise-ai-scaling-2026-06-12/"},
        {"name": "LiveMint", "url": "https://www.livemint.com/market/stock-market-news/infosys-hcl-tech-tcs-tumble-amid-global-tech-selloff-heres-whats-plaguing-indian-it-stocks-11749629447141.html"},
        {"name": "Reuters", "url": "https://www.reuters.com/technology/indias-tcs-chair-says-ai-agents-may-equal-headcount-dampen-hiring-2026-06-10/"}
    ]),
    "score_total": 85,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/35638668/pexels-photo-35638668.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "A financial professional reviews stock market data on multiple screens",
    "image_attribution": "Pexels",
    "body": article2_body,
}


# ─────────────────────────────────────────────
# ARTICLE 3: Anthropic vs OpenAI IPO race
# ─────────────────────────────────────────────

article3_body = """Two AI companies filed for initial public offerings within seven days of each other this month. Anthropic went first, submitting a confidential S-1 to the SEC on June 1. OpenAI followed on June 8. Between them, they carry private-market valuations of roughly $1.8 trillion. And for reasons that go well beyond stock tickers, the Indian tech diaspora has an outsized stake in both.

This is not simply a Wall Street spectacle. It is a structural event that will shape how AI is priced, who controls its economics, and which companies — from TCS in Mumbai to Khosla Ventures in Menlo Park — profit or suffer as the technology matures.

## The Valuations

Anthropic closed its Series H round on May 28 at a valuation of $965 billion, overtaking OpenAI's $852 billion post-money valuation from March. The reversal was swift: as recently as January, OpenAI was considered the clear frontrunner in both market position and investor confidence. That changed when Anthropic's Q1 revenue came in at $4.8 billion, trailing OpenAI's $5.7 billion, but with a trajectory that has Wall Street paying closer attention.

Anthropic projects $10.9 billion in Q2 2026 revenue — more than doubling in a single quarter — and expects to post its first-ever operating profit of $559 million. OpenAI, by contrast, reported a $6.95 billion non-GAAP operating loss in Q1, with an annualised burn rate of roughly $28 billion. CEO Greg Brockman has testified that the company plans to spend $50 billion on compute this year and $600 billion cumulatively through 2030.

## The Infrastructure Divide

The divergence is not about who has the better model. It is about who pays less to serve each token.

Anthropic committed over $100 billion to AWS custom silicon over ten years in April, locking in capacity on Amazon's Trainium chip family. The bet is that custom silicon — designed specifically for Anthropic's model architecture — can serve inference at a fraction of the cost of renting Nvidia GPUs on the open market. Andy Jassy, Amazon's CEO, has called the cost advantage "significant."

OpenAI's approach is different: it buys compute from multiple cloud providers at market rates, an approach that offers flexibility but no structural cost advantage. When you are generating hundreds of billions of tokens per quarter, the per-token margin difference between custom silicon and open-market GPUs is the difference between profit and a multi-billion-dollar hole.

## The Indian Angle

The IPO race touches the Indian tech ecosystem at multiple points.

Vinod Khosla's early bet on OpenAI — the first institutional cheque, written in 2019 — is the single most valuable venture investment of the decade and the reason he tops the 2026 Forbes Midas List. His return on that investment will be crystallised by OpenAI's IPO pricing. For the 17 Indian-origin investors on the Midas List, the AI IPO cycle represents either generational wealth creation or the moment the music stops.

On the services side, TCS signed a strategic partnership with Anthropic this week; Infosys did the same in February. Both are betting that Claude will become a core tool in their delivery model — even as Claude's capabilities threaten to shrink the billable hours those companies sell. It is the corporate equivalent of buying the weapon that is pointed at you.

For Indian AI researchers — many of whom work at OpenAI, Anthropic, Google DeepMind, and Meta AI — the IPOs will determine whether their equity grants, often a significant share of total compensation, convert into real wealth. Anthropic's Bangalore office, announced earlier this year, is already hiring engineers whose stock options will vest at whatever price the public market assigns.

## What Happens Next

Both companies have told investors they are targeting IPOs in the second half of 2026, possibly as early as September. The banker conflict alone is unusual: it is rare for two direct rivals of this size to seek capital from the same underwriters simultaneously. Reuters reports that some advisers are navigating "increasingly complex relationships" with both firms.

The public-market test will be brutal. OpenAI's $852 billion valuation prices in a resolution to its unit economics problem that has not yet appeared in the numbers. Anthropic's $965 billion valuation prices in revenue growth that needs to sustain a pace no enterprise software company has ever maintained. One of them will be right. The odds that both are — at these prices — are slim.

For the Indian engineer at either company, the NRI investor watching from Bangalore, or the TCS project manager deploying Claude in a client engagement, the question is the same: which side of this trade do you want to be on?

*Sources: Reuters, ainvest, The Street, Outlook Business, CNBC*"""

article3 = {
    "id": str(uuid.uuid4()),
    "headline": "Anthropic and OpenAI Are Racing to Wall Street. One of Them Is About to Turn a Profit.",
    "subheadline": "Both AI labs filed for IPOs this month at a combined $1.8 trillion valuation. Their infrastructure economics have diverged sharply — and Indian tech has skin in the game on both sides.",
    "slug": make_slug("anthropic-openai-ipo-race-indian-tech-stake"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Vinod Khosla's OpenAI bet is the decade's biggest VC win, TCS and Infosys are partnering with both labs, and Indian AI researchers at these companies hold equity grants whose value depends on IPO pricing.",
    "tags": ["openai", "anthropic", "ipo", "ai", "vinod-khosla", "tcs", "indian-tech"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/technology/anthropic-v-openai-behind-bitter-battle-future-ai-2026-06-11/"},
        {"name": "ainvest", "url": "https://www.ainvest.com/news/openai-anthropic-racing-ipo-turn-profit-watching-2606/"},
        {"name": "The Street", "url": "https://www.thestreet.com/technology/openai-makes-ipo-decision-amid-anthropic-spacex-fervor"},
        {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/corporate/openai-plans-steep-ai-price-cuts-to-beat-anthropic-as-both-race-toward-ipo"}
    ]),
    "score_total": 88,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/5/5a/Meeting_with_Masayoshi_Son_and_Sam_Altman_%28February_3%2C_2025%29_%283x4_cropped_on_Altman%29.jpg",
    "image_caption": "OpenAI CEO Sam Altman, whose company filed for an IPO on June 8 at an $852 billion valuation",
    "image_attribution": "Wikimedia Commons",
    "body": article3_body,
}


# ─────────────────────────────────────────────
# INSERT ALL
# ─────────────────────────────────────────────

articles = [article1, article2, article3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

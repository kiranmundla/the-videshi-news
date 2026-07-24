#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-06-07 12:00 UTC batch"""

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
    # ──────────────────────────────────────────────
    # ARTICLE 1: $1.3 Trillion Chip Selloff
    # ──────────────────────────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "Wall Street's AI Chip Trade Just Lost $1.3 Trillion in a Single Day",
        "subheadline": "Broadcom's cautious guidance and a scorching jobs report combined to trigger the worst semiconductor rout since the pandemic. For NRI investors loaded with chip stocks, the timing is brutal.",
        "slug": make_slug("chip-selloff-1-3-trillion-broadcom-nvidia-nri-investors"),
        "category": "technology",
        "vertical": "technology",
        "is_editorial": False,
        "diaspora_angle": "Indian Americans hold massive exposure to semiconductor stocks through direct investment, 401(k)s, and RSU compensation at NVIDIA, AMD, Intel, Broadcom, and Micron. The selloff directly hits NRI portfolios and the equity component of H-1B tech workers' total compensation.",
        "tags": ["semiconductor", "nvidia", "broadcom", "micron", "amd", "stock-market", "nri-investors", "wall-street"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/chip-selloff-erases-over-1-trillion-stock-market-value-2026-06-06/"},
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/markets/ai-chip-stocks-lose-13-trillion-as-nvidia-amd-and-micron-lead-semiconductor-selloff/article69658432.ece"},
            {"name": "Barron's", "url": "https://www.barrons.com/articles/jobs-report-solar-ai-stocks-interest-rates-2026-06-06"},
            {"name": "Seeking Alpha", "url": "https://seekingalpha.com/news/4455189-over-1t-erased-as-chip-selloff-impacts-nvidia-broadcom"},
            {"name": "Detroit Free Press / Benzinga", "url": "https://www.freep.com/story/money/business/2026/06/06/how-a-semiconductor-ceos-stock-guidance-dragged-ai-down-this-week/90420115007/"}
        ]),
        "score_total": 85,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/534216/pexels-photo-534216.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Stock market trading data on a digital display screen",
        "image_attribution": "Pexels",
        "body": """The semiconductor sector — the backbone of the AI trade that minted fortunes across Silicon Valley and Dalal Street alike — suffered its worst single-day rout since the onset of the Covid-19 pandemic on Friday, erasing roughly $1.3 trillion in market capitalisation.

The Philadelphia Semiconductor Index (SOX) plunged 10.3% on Friday alone, its deepest one-day decline since March 2020. Over two sessions — Thursday and Friday combined — the index shed 12%, a slide not seen since the "Liberation Day" tariff shock of April 2025. The carnage was broad, indiscriminate, and fast.

## What Triggered the Selloff

Two catalysts collided within 24 hours.

First, Broadcom. The custom AI chip giant reported second-quarter results on Wednesday evening that beat consensus on both revenue and profit. CEO Hock Tan guided next-quarter sales to $29.4 billion, above the Street's $28.6 billion estimate. So far, so good. But Tan kept Broadcom's full-year AI semiconductor revenue forecast unchanged at "in excess of $100 billion" — the same figure he had offered before. For a market that had priced in a raise, standing pat read as a disappointment. Broadcom's stock collapsed 12.6% on Thursday and another 7.9% on Friday, a cumulative two-day wipeout of nearly 20%.

Then came Friday morning's May jobs report. Payrolls rose 172,000, double the 85,000 consensus, with March and April revised upward by a combined 93,000. Unemployment held at 4.3%. Layered on top of April CPI running at 3.8% year-over-year — the hottest reading since May 2023 — the data flipped the rate narrative. Money markets now nearly fully price a Federal Reserve rate hike by year-end. Good economic news had become very bad market news.

## The Damage, by the Numbers

NVIDIA, the world's most valuable chipmaker and the poster child of the AI supercycle, fell approximately 6%, shaving more than $300 billion from its market capitalisation. Sanjay Mehrotra's Micron — which had just crossed the trillion-dollar threshold this week — tumbled 13%, erasing roughly $150 billion in value. Marvell Technology, which Jensen Huang had recently called "the next trillion-dollar company," gave back 17%. AMD dropped nearly 11%. Intel, despite being up 170% year-to-date, shed 14% over the week.

Even the S&P 500 fell 2.6%, while the Nasdaq 100 dropped over 4%. Bitcoin plunged below $60,000, its worst weekly decline since the FTX collapse in November 2022.

## Why NRI Investors Should Pay Attention

The semiconductor selloff is not an abstraction for Indian Americans. It hits where they live — quite literally.

Tens of thousands of Indian tech professionals working at NVIDIA, AMD, Intel, Broadcom, Micron, and Qualcomm hold significant portions of their compensation in restricted stock units (RSUs). A 10-13% single-day drop in their employer's stock translates directly into a smaller paycheck. For H-1B workers whose financial planning revolves around equity vesting schedules — saving for down payments, funding children's education, planning eventual green card expenses — the volatility is more than academic.

NRI investors with heavy US tech exposure, whether through direct holdings or index funds like the QQQ or SOXX ETF, saw portfolios shrink materially on a Friday afternoon. The VanEck Semiconductor ETF (SMH) plunged over 9% in a single session. Anyone holding individual chip names fared worse.

## Perspective: Still Up 73% This Year

The critical context: even after Friday's bloodbath, the PHLX chip index remains up roughly 73% year-to-date. NVIDIA is still near historic highs. The AI infrastructure buildout has not stopped — Broadcom's own revenue beat confirms that. What changed is the market's willingness to pay for perfection.

"You've had a lot of people here that were just blindly buying the dip," said Dennis Dick, a proprietary trader at Triple D Trading. "Blindly buying the dip had been winning you money, but that ended today."

The Federal Reserve's June 16-17 policy meeting — the first chaired by new Fed Chair Kevin Warsh — will be the next inflection point. Warsh was appointed amid President Trump's push for lower rates, but stronger economic data may tie his hands. If the market begins pricing in sustained higher interest rates, the multiple compression in chip stocks could have more room to run.

For Indian professionals and investors riding the AI wave, the message is uncomfortable but not unfamiliar: the trade is not broken, but the easy money phase may be over."""
    },

    # ──────────────────────────────────────────────
    # ARTICLE 2: H-1B Crackdown Crashes Dallas Housing
    # ──────────────────────────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "Indian Tech Workers Powered Dallas's Housing Boom. Now They're Leaving, and Prices Are Cratering.",
        "subheadline": "The H-1B crackdown, 123,000 tech layoffs, and a $100,000 visa fee have turned North Texas suburbs from the hottest real estate market in America into a cautionary tale for Indian homebuyers.",
        "slug": make_slug("h1b-crackdown-dallas-housing-indian-tech-workers-frisco"),
        "category": "technology",
        "vertical": "technology",
        "is_editorial": False,
        "diaspora_angle": "Tens of thousands of Indian H-1B workers and their families bought homes in Frisco, Prosper, and Celina. They are now the population most directly affected by the housing correction — facing underwater mortgages, 60-day visa clocks after layoffs, and the question of whether to sell at a loss or wait it out.",
        "tags": ["h1b-visa", "dallas-housing", "indian-tech-workers", "frisco-texas", "real-estate", "immigration", "layoffs"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "New York Post", "url": "https://nypost.com/2026/06/05/real-estate/trumps-crackdown-on-h1b-visa-abuse-sends-dallas-home-prices-down/"},
            {"name": "Bloomberg", "url": "https://www.bloomberg.com/news/features/2026-06-05/h-1b-visa-crackdown-hits-dallas-fort-worth-housing-market"},
            {"name": "Gulte", "url": "https://www.gulte.com/trends/195432/trumps-h-1b-curbs-shake-texas-real-estate"},
            {"name": "QUE.com", "url": "https://que.com/h-1b-crackdown-slows-texas-real-estate-boom-for-indian-workers/"},
            {"name": "Redfin / CBRE Group", "url": "https://www.redfin.com/"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/32519068/pexels-photo-32519068.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A for-sale sign stands in front of a suburban home",
        "image_attribution": "Pexels",
        "body": """For nearly a decade, the suburbs north of Dallas were the promised land for Indian tech workers on H-1B visas. Good schools, new construction, and a corporate corridor that attracted more company headquarters than anywhere else in America between 2018 and 2025. Frisco's Indian-born population surged from 6% in the early 2010s to nearly 20% by the mid-2020s. Collin County's Indian-born residents averaged over 116,000 annually, up from 70,000 in the prior five-year period.

Now that engine is sputtering — and the data is stark.

Home prices in Collin County fell nearly 9% year-over-year as of February, more than double the 4% decline across the broader Dallas-Fort Worth metro, according to Redfin data published this week in a Bloomberg investigation. At Tradition Homes, a luxury builder in North Texas, South Asian buyers once accounted for 70% of sales. That figure has fallen below 30%, even as 125 high-end homes sit unsold.

## The Policy Squeeze

The reversal traces directly to Washington. The Trump administration has imposed a $100,000 fee on new H-1B petitions — a measure that effectively priced out the staffing firms and mid-tier tech contractors that were the largest sponsors of Indian workers in markets like Dallas. The Department of Housing and Urban Development barred non-permanent residents, including H-1B holders, from accessing FHA-insured mortgages starting May 2025. FHA loan volume to non-permanent residents collapsed from 6% in April to virtually zero by late summer.

The administration raised minimum salary thresholds, launched "Project Firewall" to target employer abuse, and directed the programme to prioritise the highest-paid applicants. Texas Governor Greg Abbott ordered a freeze on new H-1B petitions by state agencies. Texas Attorney General Ken Paxton issued investigative demands to nearly 30 North Texas businesses suspected of visa fraud.

Meanwhile, the tech industry has shed over 123,000 jobs since January 2026, with artificial intelligence consistently cited as the primary driver. The twin pressures of visa restrictions and layoffs have created a self-reinforcing exodus.

## The Human Cost

The Bloomberg investigation surfaced stories that will be painfully familiar to Indian families across the DFW metroplex.

Ravi Vavilala, an Indian-born naturalized citizen, bought a five-bedroom home in Celina for $895,000 in late 2023. Laid off from his IT job in March, he listed the house, cut the price multiple times, and is now asking $873,000 — below what he paid. Before showings, he moves his religious items out of sight. "Because the market is very slow, I want to attract all types of buyers," he told Bloomberg.

Neeraj Gupta, a real estate agent who came to Dallas on an H-1B in 2000, says his phone now rings with sellers, not buyers. Some clients are absorbing monthly rental losses of $300 to $1,500 while waiting for the market to turn. "Some of them said, 'I have seen enough: Just sell it — I don't care,'" he said. One client, a senior IT director holding two Frisco homes each worth over $1 million, is weighing a return to India. Another financed an $800,000 property almost entirely with debt; the house is now worth less than the loan.

Immigration attorney Sharadha Kodem, practising out of Frisco, described client anxiety unlike anything in her career. Many who bought in remote suburbs while working remotely are now being ordered back to offices in Dallas — or told to relocate to Seattle or San Francisco. Those laid off face a 60-day window to find a new employer sponsor before their visa status lapses.

## A Bellwether, Not an Outlier

The Dallas correction is a preview, not an anomaly. The federal government granted nearly 32,000 new H-1B approvals in the Dallas area during the Biden administration — more than Silicon Valley, Seattle, San Francisco, or Washington, DC. Only the New York City metro ranked higher.

But the same dynamics are building elsewhere. Analysts project home prices in Seattle's H-1B-dense neighbourhoods could cool 2% to 5% as new tech hiring contracts. New Jersey, California, and Virginia face similar exposure.

"These H-1B visas are the No. 1 converters of potential homebuyers to actual homebuyers," said Florida International University professor Eli Beracha. "But when you get fewer people receiving H-1B visas, you get an immediate negative surprise because you have housing that has already been built for those people sitting on the market."

Housing analyst Alex Barron of Housing Research Center posed the question hanging over every developer in North Texas: "Who is there to replace them?"

For the tens of thousands of Indian families who planted roots in Frisco, Prosper, and Celina, the answer matters more than the market. It's about whether the American bet — the visa, the mortgage, the school district, the life — still adds up."""
    },

    # ──────────────────────────────────────────────
    # ARTICLE 3: RAMpocalypse — AI Starving Consumer Memory
    # ──────────────────────────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "AI Data Centres Are Hoarding the World's Memory Chips. Your Next Laptop Will Pay the Price.",
        "subheadline": "DDR5 prices have surged 4-5x, SSDs have doubled, and vendors are restarting DDR4 production lines they thought were retired. Welcome to the RAMpocalypse.",
        "slug": make_slug("rampocalypse-ddr5-price-surge-ai-memory-shortage"),
        "category": "technology",
        "vertical": "technology",
        "is_editorial": False,
        "diaspora_angle": "Indian Americans shopping for laptops — whether for college-bound children, work-from-home setups, or relatives visiting from India — face sticker shock. India's own consumer electronics market and burgeoning gaming industry are also hit. Micron's Gujarat fab, led by Sanjay Mehrotra, is focused on HBM for AI, not consumer DRAM — underscoring the supply trade-off.",
        "tags": ["memory-chips", "ddr5", "ram-shortage", "ai-infrastructure", "consumer-tech", "micron", "samsung", "pc-building"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "WCCFTech", "url": "https://wccftech.com/several-vendors-increasing-production-ddr4-platforms-ddr5-prices-make-pc-building-unfeasible/"},
            {"name": "MarketBeat", "url": "https://www.marketbeat.com/originals/ntdoy-sony-ttwo-stocks-are-facing-headwinds-from-the-memory-shortage/"},
            {"name": "Barron's", "url": "https://www.barrons.com/articles/micron-stock-falls-nvidia-memory-chip-hbm-2026-06-05"},
            {"name": "KED Global", "url": "https://www.kedglobal.com/memory-chip-market"},
            {"name": "Gizmodo / Computex 2026 Coverage", "url": "https://gizmodo.com/live-updates-from-computex-2026-2000618029"}
        ]),
        "score_total": 72,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/19716297/pexels-photo-19716297.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Close-up of a DDR memory module on a computer motherboard",
        "image_attribution": "Pexels",
        "body": """If you have been putting off buying a new laptop, the bad news is that waiting has made it worse. The global memory market — DRAM and NAND flash, the silicon that determines how much your computer can do at once and how fast it stores data — has entered what the PC enthusiast community has grimly dubbed the "RAMpocalypse."

DDR5 memory, the current standard for new PCs and laptops, is selling for four to five times what it cost 18 months ago. SSD prices have roughly doubled in the same period. Building a halfway decent desktop PC for under $1,000 has become, in the estimation of hardware site WCCFTech, effectively infeasible.

## The Culprit: AI's Insatiable Appetite

The cause is not a traditional supply-demand mismatch. It is a structural reallocation. The world's three major memory manufacturers — Samsung, SK Hynix, and Micron — are diverting an ever-larger share of their fabrication capacity toward High Bandwidth Memory (HBM), the specialised DRAM that sits atop NVIDIA's AI accelerators and powers every major data centre buildout from Santa Clara to Singapore.

HBM commands far higher margins than the conventional DDR5 that goes into your laptop or the NAND that fills your SSD. When hyperscalers like Microsoft, Google, Amazon, and Meta are willing to pay premium prices and sign multi-year supply agreements, the economic logic for chipmakers is straightforward: prioritise the customer willing to pay the most.

Research firm TrendForce projects the crowding-out effect will intensify through 2027, as each new generation of HBM requires larger die sizes while demand continues to surge. "This will provide suppliers with strong justification for raising HBM prices and strengthen their pricing power," TrendForce analysts wrote this week. A senior Samsung Electronics executive stated plainly that on-device AI and data-centre expansion will drive a "prolonged memory shortage."

The shortage is expected to persist into 2028.

## Consumers and Gamers Caught in the Crossfire

The downstream effects are already visible. At Computex 2026 in Taipei this week — the annual showcase of the PC industry — the mood around consumer pricing was notably subdued. Gizmodo described "skyrocketing" memory costs as a threat to the entire personal computing industry, even as NVIDIA, Intel, AMD, and Qualcomm unveiled powerful new processors designed to bring AI to desktops and laptops.

The gaming industry is feeling the pinch acutely. DRAM and NAND are critical components in console manufacturing, and prices have doubled year-over-year. Sony, Nintendo, and Take-Two Interactive are all navigating higher bill-of-materials costs. MarketBeat flagged all three as stocks facing "headwinds from the memory shortage," noting that hyperscalers are "siphoning supply from companies accustomed to a cyclical business."

Perhaps the most telling signal: motherboard vendors are restarting DDR4-compatible production lines. According to Tom's Hardware, over half a dozen manufacturers are ramping output of DDR4 motherboards — a technology generation they had been phasing out — because consumers cannot afford DDR5 platforms. AMD's older AM4 socket has surged back to roughly 40% of CPU platform popularity, with budget chips like the Ryzen 5500 and Ryzen 5800XT sitting in Amazon's top-10 best sellers.

## The India Angle

For Indian Americans, the squeeze manifests in multiple ways. Parents shopping for a college-bound student's laptop are confronting $200-$400 premiums on the same specs that cost far less a year ago. NRIs visiting India with gift electronics — a cultural staple — find fewer bargains to pack. India's own consumer electronics market, the world's fastest-growing smartphone and laptop segment, faces imported component costs that will push retail prices higher.

There is a deeper irony. Micron's $2.75 billion semiconductor fabrication facility in Gujarat — the marquee investment championed by CEO Sanjay Mehrotra and Prime Minister Modi — is focused on advanced packaging and assembly for HBM and other AI-grade chips. It is good industrial policy and a genuine milestone for India's semiconductor ambitions. But it will produce precisely zero of the consumer DRAM that Indian (or Indian American) buyers need to afford a reasonable laptop.

The memory market is a zero-sum game right now, and AI is winning. Everyone who does not run a data centre is on the losing side.

## What to Do

For practical purposes: if you need a new PC and your budget is tight, a DDR4 platform remains a viable option. Prices are elevated but manageable compared to DDR5. Avoid buying more storage than you need — SSD prices are unlikely to drop until HBM demand plateaus, which no analyst expects before late 2027 at the earliest.

And if you hold Micron or Samsung stock, the memory shortage is the opposite of a problem. It is, quite literally, why Sanjay Mehrotra's company just joined the trillion-dollar club."""
    },
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

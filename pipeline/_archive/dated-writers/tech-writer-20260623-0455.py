#!/usr/bin/env python3
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# Load env
env_file = Path.home() / ".env.supabase"
if not env_file.exists():
    env_file = Path.home() / "workspace" / ".env.supabase"
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
        "headline": "A Trillion Dollars Vanished From the Nasdaq in a Day. The Engineers Who Built the AI Boom Have the Most to Lose.",
        "subheadline": "Tuesday's tech wreck wiped more than $1 trillion off the Nasdaq 100 as investors finally asked whether the debt-funded AI buildout can pay for itself. For Indian techies whose net worth, RSUs and job security ride on these stocks, the reckoning is personal.",
        "slug": make_slug("nasdaq-trillion-dollar-ai-selloff-bubble-fears-indian-tech-workers-rsu"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Tens of thousands of Indian engineers at Nvidia, Google, Microsoft and Micron hold much of their compensation in the very AI stocks now in freefall — a correction that hits their RSUs, mortgages and visa-tethered job security harder than almost anyone.",
        "tags": ["ai", "stock-market", "nvidia", "micron", "indian-tech", "silicon-valley"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters — Nasdaq 100 set to shed over $1 trillion", "url": "https://www.reuters.com/markets/us/"},
            {"name": "Barron's — The 'Tech Wreck' Forces Wall Street to Ask How Much Upside Is Left", "url": "https://www.barrons.com/"},
            {"name": "Investor's Business Daily — AI Stocks In A Bubble? Comparisons To 1999 Appear", "url": "https://www.investors.com/"}
        ]),
        "score_total": 86,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/35118208/pexels-photo-35118208.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A candlestick chart showing a sharp downward trend on a stock market display",
        "image_attribution": "Pexels",
        "body": """The number that flashed across trading desks on Tuesday morning was almost abstract: the Nasdaq 100 was on pace to erase more than $1 trillion in market value in a single session. By the open, futures tracking the index had dropped 2.5%, Nvidia and Alphabet were each down around 3%, and the chipmakers that have powered this year's rally — Intel, AMD, Marvell — were bleeding 5% to 7%. Even Elon Musk's freshly public SpaceX slid below a $2 trillion valuation for the first time since its debut, having shed more than $600 billion in three sessions.

This is the selloff the market spent a year pretending it would never see.

## What broke

For months, the bullish story wrote itself: artificial intelligence demand was insatiable, the hyperscalers would spend whatever it took, and the companies selling chips and memory into that buildout were minting money. The story was true. It is still partly true. What changed on Tuesday was the price of believing it.

Two things converged. First, the U.S. Federal Reserve under new Chair Kevin Warsh has turned hawkish — traders now expect 50 basis points of rate hikes by December, up from a single quarter-point move just two weeks ago. Higher borrowing costs matter enormously here, because Big Tech has become one of the largest issuers of corporate debt on earth, floating roughly $120 billion of bonds in 2025 and more than $150 billion so far in 2026 to fund the AI buildout. SpaceX tapping the bond market for at least $20 billion was the spark that reminded everyone how much of this expansion is financed, not self-funded.

Second, the comparisons to 1999 have started in earnest. DataTrek Research notes the S&P 500 technology sector just outpaced the broader index by the widest margin since January 2000 — the eve of the dot-com collapse. Strategist Ed Yardeni points out that the gap between tech's expected long-term earnings growth and the rest of the market is now wider than it was at the 2000 peak. Put technology and communication services together and they account for 47% of the entire S&P 500. When a market is that concentrated, a sentiment shift does not stay contained.

## Why this lands differently for Indian techies

For an Indian engineer at Nvidia in Santa Clara, a data-center architect at Google, or a memory designer at Micron in Boise, this is not a CNBC chyron. It is their balance sheet.

Compensation at these firms is heavily weighted toward restricted stock units that vest over years. When the share price triples — as Micron's did this year, up more than 300% before Tuesday's 8% drop — paper wealth balloons and people make real decisions on the back of it: Bay Area down payments, parents' medical bills in India, the second kid's college fund. A correction does not just dent a portfolio; it resets the assumptions a whole household was built on. The engineer who joined Micron 18 months ago and watched the stock rocket is now watching options pricing imply a swing of up to 12% in either direction around Wednesday's earnings.

Then there is the job itself. H-1B and L-1 holders do not have the luxury of riding out a downturn from the sidelines. A layoff starts a 60-day clock to find a new sponsor or leave the country. The Indian diaspora has spent this year watching Oracle cut 21,000 roles and citing AI as the reason, while Nvidia did the opposite and doubled down on Indian hiring. A market that suddenly punishes AI capex spending threatens exactly the budgets that fund those teams.

## The Micron test

Wednesday's Micron earnings, due after the close, have become the market's referendum. Analysts expect blowout numbers — revenue near $36 billion, up some 280% year-on-year, with high-bandwidth memory for AI accelerators sold out through the end of the calendar year. Sanjay Mehrotra's company is, by the fundamentals, one of the strongest stories in the entire complex.

That is precisely the problem. If a company posting 1,000% earnings growth still sells off, it tells you the move is no longer about fundamentals — it is about how much investors are willing to pay for them, and at what cost of capital. For the diaspora professionals whose careers and savings are wired into this trade, the lesson of this week is an old one, relearned the hard way: the build was real, the demand was real, and none of that prevents a repricing when the money gets expensive.

## What's next

Thursday's PCE inflation print — the Fed's preferred gauge, expected near 4.1% — will either calm the rate fears or pour fuel on them. Beyond that, watch whether the selling stays in chips and hyperscalers or spreads into the Indian IT services names that already had a brutal week. The diaspora's exposure runs through both: the U.S. tech stocks in their brokerage accounts, and the Infosys and TCS shares many still hold back home. For once, both sides of the ledger are pointing the same way."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India Is Pouring Billions Into Deep Tech. Its Most Ambitious Founders Are Still Buying One-Way Tickets to America.",
        "subheadline": "A 24-year-old Bengaluru founder building DNA-based data storage just shut her India operation to move to San Francisco — even as Premji Invest, Nvidia and Temasek shovel money into Indian deep tech. The contradiction is the whole story.",
        "slug": make_slug("india-deep-tech-funding-surge-founders-relocate-us-biocompute-reverse-brain-drain"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "The 'should I build in India or move to the Valley' question that has defined a generation of NRI founders is being answered in real time — and the answer reveals what the diaspora's home country still cannot offer its boldest builders.",
        "tags": ["deep-tech", "startups", "indian-tech", "venture-capital", "brain-drain", "silicon-valley"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Mint — BioCompute founder reveals why they are relocating to US from Bengaluru", "url": "https://www.livemint.com/companies/"},
            {"name": "Reuters — Upscale AI valued at $2 billion after funding extension", "url": "https://www.reuters.com/technology/"},
            {"name": "Mint — Indian deep-tech to see funding surge amid sovereign push: Celesta's Viswanathan", "url": "https://www.livemint.com/companies/"}
        ]),
        "score_total": 78,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/8442543/pexels-photo-8442543.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A scientist in protective gear examining samples in a research laboratory",
        "image_attribution": "Pexels",
        "body": """Anagha Rajesh is 24, and she has just done the thing that India's startup establishment spends conferences insisting nobody needs to do anymore. She is shutting her Bengaluru lab and moving to San Francisco.

Her company, BioCompute, is not a food-delivery clone or a payments wrapper. It is trying to store digital data inside DNA — packing vast archives into biological molecules instead of silicon and spinning disks. Over two years she raised more than ₹5 crore from investors including the 1517 Fund and built what she says is India's first end-to-end DNA data-storage prototype. Then she decided India was the wrong place for the next chapter. "India ke paas paise ki kummi nahi hai," she wrote — India is not short of money. The problem, she explained, was everything around the money.

Her exit is a single data point. But it lands in the same week that the headlines screamed the opposite story.

## The money is here now

On Monday, Upscale AI — an AI-networking infrastructure company — closed a $190 million extension that valued it at $2 billion, with Azim Premji's Premji Invest leading and Nvidia, Salesforce Ventures and Singapore's Temasek piling in. India minted its second AI unicorn, Sarvam, on the back of a $234 million round anchored by HCLTech. Mukesh Ambani filed the paperwork for what would be India's largest-ever IPO at Jio Platforms. Veteran investor Arun Viswanathan of Celesta Capital, who sits on the board of the India Semiconductor Mission, is closing a fresh ₹2,000-crore deep-tech fund and says a second $15-billion tranche of chip incentives is coming.

By the numbers, this is the most capital-rich moment Indian deep tech has ever seen. The India Deep-Tech Alliance alone has committed nearly $3 billion. So why are the boldest founders still leaving?

## What capital cannot buy

The gap Rajesh is describing is not financial; it is infrastructural and cultural. DNA data storage needs specialized wet-lab equipment, a dense ecosystem of synthetic-biology suppliers, and — crucially — early customers willing to pay for something that does not yet fully exist. That ecosystem is thick in the San Francisco Bay Area and thin almost everywhere else. It is the same complaint Postman's founders made years ago: the early adopters who will pay for a frontier product are clustered on America's coasts.

This is the quiet asymmetry behind the diaspora's existence. India produces an extraordinary volume of technical talent and, increasingly, the capital to back it. What it has struggled to manufacture is the surrounding tissue — the suppliers, the risk-tolerant first customers, the regulatory clarity, the second and third engineer who has already done the hard thing once. For deep tech especially, where the science is unforgiving and the timelines are long, that tissue is the whole game.

## Why NRIs should watch this closely

For the Indian American reading this from Fremont or Edison, Rajesh's move is a mirror. Many in the diaspora made the same calculation a decade or two ago, and the standard narrative has been that the calculation is reversing — that "reverse brain drain" is pulling talent home as India's ecosystem matures. This week complicates that comfort.

The truth is more interesting than either triumphalism or despair. India is now genuinely competitive for whole categories of company: consumer fintech, SaaS sold back into the West, sovereign AI models trained for Indian languages and government procurement. The Anthropic export ban on foreign nationals turned sovereign AI from a slogan into a procurement requirement overnight, and Indian firms are positioned to capture it. For those businesses, staying home is now the smart move.

But for the most science-intensive, infrastructure-hungry frontier bets — DNA storage, novel semiconductors, certain classes of robotics — the Valley's gravitational pull is undiminished. The diaspora's role, then, is shifting from "people who left" to a bridge: NRI founders who keep R&D in San Francisco while building engineering teams in Bengaluru, NRI investors writing checks into Indian deep tech from Sand Hill Road, and operators who can credibly tell a 24-year-old whether her specific company belongs in Koramangala or SoMa.

## What's next

Watch where Rajesh's next round comes from — if Indian capital follows her to San Francisco, it confirms that the money has globalized faster than the ecosystem. Watch, too, whether India's semiconductor and deep-tech missions start funding the unglamorous middle layer: the suppliers, the shared fabrication facilities, the testbeds. Cash, this week proved, is no longer the constraint. The harder, slower work of building everything that surrounds the cash is. Until that exists, the most ambitious tickets will keep being one-way."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India Taxes Crypto at 30% and Calls It Compliance, Not a Ban. For NRIs Holding Bitcoin, the Fine Print Is Brutal.",
        "subheadline": "Parliament has confirmed there is no plan to ban crypto — or to properly regulate it. Instead India runs a punishing tax-and-surveillance regime while betting its real money on UPI and the digital rupee. Diaspora investors are caught in the middle.",
        "slug": make_slug("india-crypto-30-percent-tax-tds-penalties-nri-investors-upi-digital-rupee"),
        "category": "technology",
        "vertical": "fintech",
        "diaspora_angle": "NRIs who buy or transfer crypto involving Indian platforms or rupee accounts face a 30% tax, 1% TDS on every trade and new per-day penalties — while the diaspora's everyday money increasingly rides on the UPI rails New Delhi is promoting instead.",
        "tags": ["crypto", "fintech", "upi", "india-regulation", "bitcoin", "nri-investors"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Analytics Insight — Is India Open for Crypto? The 2026 Regulation Reality", "url": "https://www.analyticsinsight.net/"},
            {"name": "CoinDesk — India crypto budget 2026: traders to face a $545 penalty for lapse", "url": "https://www.coindesk.com/"},
            {"name": "Mint — ITR filing 2026: report your cryptocurrency gains, tax rules explained", "url": "https://www.livemint.com/money/"}
        ]),
        "score_total": 72,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/7267491/pexels-photo-7267491.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A stack of Bitcoin cryptocurrency coins on a reflective surface",
        "image_attribution": "Pexels",
        "body": """India has perfected a strange middle path on cryptocurrency: it will neither bless it nor kill it. In March 2026, Parliament confirmed there was no proposal under consideration either to fully regulate virtual digital assets as a product class or to ban them outright. Crypto in India is legal to hold, legal to trade, and legally treated as something the state would clearly prefer you did not touch.

If that sounds contradictory, the numbers make it concrete. India levies a flat 30% tax on gains from virtual digital assets, plus a 4% cess, with no distinction between short- and long-term holdings and no ability to offset losses against other income. On top of that sits a 1% tax deducted at source on every transfer — a mechanism designed less to raise revenue than to create a paper trail on every wallet movement. And from April 2026, a new penalty regime took effect: ₹200 per day for reporting entities that fail to file required statements, and a flat ₹50,000 — roughly $545 — for incorrect or unrectified disclosures.

## Compliance as policy

What India has built is not regulation in the sense of consumer protection or licensing. It is a compliance-and-surveillance framework bolted onto an asset class the government still refuses to formally recognize. By March 2026, 54 virtual-digital-asset service providers had registered with the Financial Intelligence Unit under anti-money-laundering rules, while enforcement agencies had shut down 53 non-compliant crypto websites and apps. Tax collected from the sector jumped to ₹437 crore in FY24 from ₹269 crore the year before — more from tightening the screws than from any boom in legitimate activity.

The strategic logic becomes clear when you look at what India is promoting instead. New Delhi's monetary energy is pouring into home-grown rails: UPI, which just went live at a Paris department store, and the digital rupee (e₹), the central-bank digital currency the RBI wants to use for settlement. These give the state exactly what private crypto denies it — full visibility, domestic control, and no exposure to dollar-denominated stablecoins. An external shock like the Strait of Hormuz oil-import scare only sharpens that instinct toward monetary sovereignty.

## Why this matters to the diaspora

For NRIs, the crypto question is not abstract, because so many straddle two financial systems. An Indian American who funds an Indian exchange account, transfers tokens to family back home, or holds assets that touch the rupee can find themselves inside India's tax net in ways that are easy to trigger and painful to unwind. The 1% TDS applies to transfers, not just sales — meaning ordinary portfolio rebalancing on an Indian platform leaks value on every move. The new penalties mean a missed disclosure is not a slap on the wrist; it compounds at ₹200 a day.

The cross-border complexity is the real trap. A trade that is a simple capital-gains event in the United States can be a 30%-plus taxable transfer the moment it routes through Indian infrastructure, and the diaspora's instinct to keep one foot in each country is exactly what creates the exposure. Tax professionals increasingly advise NRIs to keep crypto activity cleanly on one side of the border rather than letting it straddle both.

Meanwhile, the rails the diaspora actually uses every day are moving the other way. UPI's international expansion means an NRI in London or Singapore can increasingly pay an Indian merchant or send money home through a system that is fast, nearly free, and — not coincidentally — fully domestic. India's bet is that for the 1.4 billion people it serves and the millions abroad who transact with them, programmable digital-rupee settlement and UPI-native products will simply make private crypto irrelevant, without ever needing a ban.

## What's next

The Revenue Secretary has said a new direct tax code will be released within six months for stakeholder consultation, and the crypto industry will lobby hard to soften the 1% TDS that it argues has pushed trading volume offshore. Do not expect a dramatic reversal; the entire architecture of taxation, AML registration and penalties points toward continuity, not liberalization. For diaspora investors, the practical guidance is unglamorous but firm: treat any India-touching crypto activity as fully reportable, keep meticulous records, and assume the surveillance framework will only tighten. The era of the gray zone is over — India has decided crypto can exist, as long as it can watch every transaction."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

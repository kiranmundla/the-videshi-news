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
        "headline": "Adobe's Indian-Born CEO Bet the Company on Selling Software. On His Way Out, He's Giving It Away.",
        "subheadline": "Shantanu Narayen built Creative Cloud into a subscription juggernaut. His parting move \u2014 a freemium, AI-first Adobe \u2014 will define what the next Indian-American who runs it inherits.",
        "slug": make_slug("adobe-shantanu-narayen-freemium-firefly-ai-pivot-nri-creative"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Adobe is one of the largest employers of Indian engineers and creative professionals in the Bay Area, and its succession question is a live test of whether the diaspora's grip on Silicon Valley's top jobs outlasts the executives who built it.",
        "tags": ["adobe", "shantanu-narayen", "ai", "indian-tech", "silicon-valley", "firefly"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Motley Fool", "url": "https://www.fool.com/investing/2026/06/22/this-software-stock-could-soar-74-over-the-next-yea/"},
            {"name": "MarketBeat \u2014 Adobe Q2 2026 Earnings", "url": "https://www.marketbeat.com/stocks/NASDAQ/ADBE/earnings/"},
            {"name": "Barchart", "url": "https://www.barchart.com/story/news/adobe-stock-fans-mark-your-calendars-for-june-11"},
            {"name": "Constellation Research", "url": "https://www.constellationr.com/blog-news/adobe-reports-strong-q1-adds-firefly-subscriptions"},
        ]),
        "score_total": 76,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/0/01/Shantanu_Narayen_-_the_CEO_of_Adobe_Inc.jpg",
        "image_caption": "Adobe CEO Shantanu Narayen, who announced his retirement in 2026 after nearly two decades leading the company.",
        "image_attribution": "Wikimedia Commons",
        "body": """Shantanu Narayen spent eighteen years teaching the software industry a single, ruthless lesson: people will pay every month, forever, for tools they cannot work without. He took Adobe from a company that sold Photoshop in a shrink-wrapped box to one that rented it out as Creative Cloud, and in doing so turned a mature design-software maker into a machine that mints recurring revenue. The stock rose roughly tenfold along the way. Now, on his way out the door, the Hyderabad-born chief executive is quietly dismantling the very logic he built his career on.

On Adobe's second-quarter earnings call this month, Narayen laid out a strategy that would have been heresy a decade ago. "AI-first applications that will serve broader audiences need to provide free, intuitive onboarding that drives usage and monetization through paywalls," he told analysts. Translated: Adobe is going freemium. Give the tools away, hook the next generation of creators raised on free AI apps, and charge them later. For a company whose entire valuation rests on locked-in subscribers, this is a gamble dressed up as inevitability.

## A transition on multiple fronts

The timing is fraught. Narayen announced his retirement earlier this year and is staying on only until the board finds a successor. Then, alongside the Q2 results, finance chief Dan Durn announced his own departure, effective June 15 \u2014 leaving both the corner office and the CFO's chair in flux at exactly the moment Adobe is asking investors to trust a strategic U-turn.

The numbers underneath are not the problem. Adobe reported earnings of $5.96 a share on revenue of $6.62 billion for the quarter, both ahead of Wall Street, with sales up nearly 13% year on year. Firefly, Adobe's generative-AI engine, crossed $250 million in annual recurring revenue, and AI-first ARR tripled. The company is buying marketing-software maker Semrush for $1.9 billion and authorized a $25 billion buyback running through 2030. This is not a business in distress.

The market is unconvinced anyway. Adobe shares have fallen nearly 28% this year, trading around $197 \u2014 levels that prompted investor Michael Burry to call the stock a "fat pitch." J.P. Morgan cut its price target from $420 to $340, warning that the freemium shift creates "short-term ARR headwinds" even as it opens long-term upside. The fear is simple: generative AI lets anyone produce a passable image or video without ever opening Photoshop, and Adobe is now betting it can convert free AI users into paying ones faster than rivals can make Adobe irrelevant.

## Why the diaspora should watch the succession, not just the strategy

For Indian Americans, the more interesting story is who comes next. Adobe under Narayen has been one of the largest employers of Indian-origin engineers, designers, and product leaders in the Bay Area \u2014 a company where an H-1B holder could see someone who shared their accent and their immigrant arc sitting at the very top. That is not a small thing. Representation at the CEO level shapes who gets sponsored, who gets promoted, and who believes the ceiling is reachable.

Narayen's exit lands amid a broader generational handoff in the Indian-American executive class. The Pichais and Nadellas are now veterans, not insurgents. The question for the diaspora is whether the pipeline behind them is deep enough that the next Adobe CEO is also one of their own \u2014 or whether the era of Indian-origin leaders ascending to run America's marquee software firms was a moment rather than a structure.

For the tens of thousands of Indian professionals who hold Adobe stock through grants and 401(k)s, the freemium bet is also a personal balance-sheet question. A successful transition to AI-first monetization could re-rate a beaten-down stock; a botched one, executed by a leadership team still settling in, could prolong the pain.

## What's next

Adobe reports fiscal Q3 on September 10, the first real checkpoint on whether free users are converting to paid at a rate that justifies the strategy. The board's choice of Narayen's successor will arrive on its own timeline, but it will be read closely \u2014 in Bangalore as much as in San Jose \u2014 as a signal of how durable the diaspora's hold on Silicon Valley's commanding heights really is."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Apple Spent 15 Years Escaping Intel. Now It's Quietly Going Back \u2014 and the Reason Sits in a Memory-Chip Shortage.",
        "subheadline": "A tentative Apple-Intel foundry deal is being sold as a US manufacturing win. For Indian engineers and NRI investors, the real signal is how fragile the chip supply chain has become.",
        "slug": make_slug("apple-intel-foundry-deal-18a-tsmc-chip-supply-nri-investors"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Indian engineers staff the chip-design and supply-chain teams at Apple, Intel, TSMC, and Micron, and India's own fab ambitions live or die by exactly the foundry economics this deal exposes \u2014 making it required reading for NRIs in semiconductors and the investors tracking them.",
        "tags": ["apple", "intel", "semiconductor", "tsmc", "chips", "indian-tech"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/apple-intel-chip-deal-makes-strategic-sense-production-years-away-2026-06-24/"},
            {"name": "Barchart", "url": "https://www.barchart.com/story/news/intel-will-design-manufacture-chips-for-apple"},
            {"name": "MarketBeat", "url": "https://www.marketbeat.com/stocks/NASDAQ/AAPL/"},
            {"name": "The Motley Fool", "url": "https://www.fool.com/investing/2026/06/23/apple-intel-historic-chip-partnership/"},
        ]),
        "score_total": 78,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/3665442/pexels-photo-3665442.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A silicon wafer under inspection; Apple is exploring using Intel's 18A-P process for lower-end Mac and iPad chips.",
        "image_attribution": "Pexels",
        "body": """For a decade and a half, the defining engineering achievement of Apple's silicon team was getting away from Intel. The company ditched Intel processors for its own ARM-based M-series chips, built at Taiwan's TSMC, and the payoff was dramatic: a MacBook Air with no fan that still beat Intel on benchmarks. So the news that Apple is now exploring having Intel manufacture some of its chips reads, at first, like a plot twist. Look closer and it is something more revealing \u2014 a confession about how strained the world's chip supply has become.

The reported deal is narrow. Analysts including Ming-Chi Kuo describe Apple's M7 system-on-chip, built on Intel's 18A-P process, powering the MacBook Air and entry-level iPad Pro, with mass production targeted for late 2027. Intel will not touch the iPhone 18 Pro Max or the flagship M-series Macs. TSMC keeps more than 90% of Apple's overall chip supply. As one analyst put it bluntly to Reuters, with Intel's unproven foundry record this is "a shotgun wedding."

## The shortage doing the talking

What makes Apple even consider it is pain on two fronts. The first is memory pricing: surging costs for the memory chips that go into every iPhone and Mac have squeezed margins so hard that Tim Cook \u2014 a CEO famous for never saying anything alarming \u2014 has publicly called the situation "unsustainable" and warned price increases are "unavoidable." The second is concentration risk. Nearly all of Apple's advanced silicon comes from TSMC, whose lines are being fought over by Nvidia and AMD for AI chips, driving up prices and bottleneck risk for everyone else.

Intel, for its part, needs the validation more than the volume. The US government took an $8.9 billion stake in the company in 2025, and the stock has since risen roughly 440%, landing Tesla as a foundry customer in April and now, possibly, Apple. CEO Lip-Bu Tan is promising a tenfold shareholder return over five to ten years. But Intel trades at 123 times forward earnings, and the Apple arrangement is, in the words of one analyst, "a signal win, not a revenue story yet." No firm volume commitments have been disclosed. Volume production of Apple-designed chips is unlikely before late 2027.

## Why this lands hard in the diaspora

Strip away the stock-ticker drama and this is a story about the supply chain that Indian engineers quietly run. Indian-origin technologists sit in the chip-design, packaging, and supply teams at Apple, Intel, TSMC, and Micron \u2014 the latter led by Sanjay Mehrotra, whose memory business is at the center of the very shortage pushing Apple toward Intel. When the industry reshuffles where chips get made, it reshuffles where those careers are anchored.

There is a sharper angle for anyone tracking India's own semiconductor bet. New Delhi has staked billions on becoming a chipmaking nation, with Tata's fabs and Micron's Gujarat plant as the marquee projects. The Apple-Intel saga is a live lesson in how brutal foundry economics are: even Intel, with US government money, advanced tooling, and decades of manufacturing history, is treated as a risky bet that may not deliver volume for years. India's fabs are starting from far behind. The realistic near-term play \u2014 the one Indian policymakers increasingly acknowledge \u2014 is chip design and packaging, not bleeding-edge fabrication. Apple's hedging tells you why.

## What's next

The deal remains exploratory; no purchase agreement has been signed. The checkpoints to watch are Intel's qualification of its 18A-P node \u2014 not promising early data, but proven yields \u2014 and any disclosure of actual Apple volume. For NRI investors, the cleaner read may be Micron and TSMC: the shortage that is driving Apple to diversify is, for the memory and foundry incumbents, simply a seller's market with no end in sight. The chip cycle is not cooling. It is just getting more crowded."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Ola Electric Once Owned Half of India's Electric Scooter Market. The Companies That Took It Are the Boring Ones.",
        "subheadline": "As India's EV two-wheeler race shifts from land-grab to profit, the quiet operators \u2014 Ather, TVS, Bajaj \u2014 are winning. For NRI investors, that change of rules is the whole story.",
        "slug": make_slug("india-ev-two-wheeler-race-ola-electric-ather-tvs-bajaj-nri-investors"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "India's listed EV makers \u2014 Ola Electric and Ather among them \u2014 are increasingly in NRI portfolios, and the sector's pivot from market-share blitz to margin discipline changes which of these stocks is actually worth owning.",
        "tags": ["ev", "ola-electric", "ather-energy", "india-startups", "nri-investors", "clean-energy"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/business/autos-transportation/indias-ola-electric-invest-2085-million-ev-cell-tech-units-2026-05-15/"},
            {"name": "Mint", "url": "https://www.livemint.com/market/stock-market-news/investors-are-betting-on-ola-electrics-hail-mary-pass"},
            {"name": "Storyboard18", "url": "https://www.storyboard18.com/how-it-works/ola-electric-ather-shift-focus-to-profitability"},
            {"name": "Trade Brains", "url": "https://tradebrains.in/features/ev-stock-jumps-amara-raja-ather-energy-lithium-ion-cells/"},
        ]),
        "score_total": 72,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/4678065/pexels-photo-4678065.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "An electric scooter charging; India's e-two-wheeler market is shifting from volume growth to profitability.",
        "image_attribution": "Pexels",
        "body": """In early 2025, Ola Electric looked like the future of Indian transport. It held 48.6% of the electric two-wheeler market, ran flashy launches, and carried the swagger of a startup that had decided to win by moving faster than anyone else. A year and a half later, that swagger is gone. TVS, Bajaj, and the studiously unglamorous Ather Energy have taken the lead, and the company that once defined the category is the one fighting to recover. The reversal is a lesson in what happens when an industry stops rewarding speed and starts rewarding the boring stuff: margins, distribution, and cash.

The shift is visible in the numbers. In FY26, Ather sold 2.63 lakh electric two-wheelers, up 69% year on year, lifting its market share to 18.6% from 11.5% and narrowing its EBITDA margin from minus 19% to minus 3%. TVS sold 3.71 lakh units, up 33%. Ather is now opening stores at a pace of more than one a day, targeting over 1,100 outlets by March 2027. Ola, by contrast, is shrinking its network from roughly 4,000 stores to around 700 \u2014 a brutal admission that it expanded faster than it could support.

## From land-grab to discipline

The whole sector has changed its religion. India's EV two-wheeler makers spent years chasing volume at any cost; now Ola, Ather, and TVS are all reporting improved unit economics as they prioritize profitability over share. Ola did post a genuine bright spot \u2014 its first cash-flow-positive quarter in Q4 FY26, with automotive gross margin jumping to 38.5% from 18.4% a year earlier. But it remains loss-making at the EBITDA line, and the market is no longer grading on ambition alone.

What investors are actually buying, when they bid Ola's stock up nearly 60% over two months, is not the scooter business. It is the bet that Ola can build a vertically integrated EV ecosystem \u2014 its own battery cells, powertrains, and software under the "Bharat Cell" initiative. As Mint put it, this is a "Hail Mary": a scooter maker is valued on sales and margins, but an integrated battery-and-platform company is valued on future prospects. The catch is that building a battery ecosystem is far harder than selling scooters, and the execution risk is enormous. Meanwhile the cell economics are getting more contested across the board \u2014 this week Amara Raja Energy & Mobility announced a tie-up with Ather to co-develop lithium-ion cells, a reminder that everyone is racing to localize the most expensive part of the vehicle.

## Why NRIs should care

For the Indian diaspora, the EV two-wheeler race is no longer a curiosity \u2014 it is an investable, and increasingly volatile, slice of the India growth story. Ola Electric and Ather both trade on Indian exchanges, and NRI investors who can buy Indian equities have real exposure to which of these companies survives the shakeout. The sector's pivot reframes the question entirely. The old question was "who is selling the most scooters?" The new one is "who is making money on each one, and who has the balance sheet to fund a battery business without burning out?"

There is a macro tailwind worth weighing too. With oil prices having spiked during the recent Gulf conflict, the Indian government has renewed its push toward fuel conservation and EV adoption to cut the country's crude import bill \u2014 a structural reason to expect electric two-wheelers to keep gaining share over the medium term, regardless of which brand wins. For an NRI deciding whether to add an India EV name to a portfolio, the sector tailwind is the easy part. Picking the company that converts that tailwind into profit is the hard one \u2014 and right now the quiet operators, not the loudest disruptor, are answering it best.

## What's next

Watch Ola's coming quarterly results for whether the cash-flow-positive moment was a turning point or a one-off, and watch Ather's store-expansion pace against its losses. The next phase of India's EV story will be written less in launch-event theatrics and more in gross-margin tables \u2014 the kind of reading the diaspora's investors are going to have to get comfortable with."""
    },
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"\u2705 {art['slug']}")
    except Exception as e:
        print(f"\u274c {art['slug']}: {e}")

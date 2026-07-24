#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-07-01 14:00 PT run."""
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

# ────────────────────────────────────────────────────────────────────────
# ARTICLE 1: SK Hynix Nasdaq Listing vs Micron
# ────────────────────────────────────────────────────────────────────────
art1_body = """Micron Technology has had the American memory market to itself for a long time. Not any more.

SK Hynix, the South Korean chipmaker that controls roughly 60 per cent of the global high-bandwidth memory (HBM) market, plans to list American depositary receipts on the Nasdaq as early as July 10. The offering could raise up to $29.4 billion — the largest Korean ADR listing on a US exchange. If all goes to plan, SK Hynix will trade on the same screens as Micron, Nvidia, and the rest of the AI hardware complex.

For Sanjay Mehrotra, Micron's Indian-origin CEO who has steered the Boise chipmaker through the most profitable stretch in its history, the timing is both flattering and threatening. Micron just reported a blowout quarter — $41.5 billion in revenue, up 346 per cent year-on-year, with earnings of $25.11 per share crushing estimates by $4. The company guided for roughly $50 billion next quarter, with gross margins approaching an extraordinary 81 per cent.

## The stock tells a different story

Despite those numbers, Micron shares fell more than 10 per cent on Wednesday, sliding from a record high of $1,255 reached after the June 24 earnings print. The retreat isn't about Micron's results — it's about what happens when the market's only US-listed pure-play memory stock gets direct competition on the same exchange.

SK Hynix isn't small. Its market capitalisation now exceeds $1 trillion, and its shares have risen more than 300 per cent in 2026 alone, overtaking Samsung to become South Korea's most valuable company. It dominates HBM — the specialised memory chips stacked vertically to feed Nvidia's AI accelerators — and is now pivoting toward conventional DDR5 DRAM, where analysts forecast margins of up to 90 per cent due to acute shortages.

The ADR proceeds are earmarked for new fabrication lines, additional HBM packaging capacity in Cheongju, and purchases of EUV lithography equipment. In other words, SK Hynix is raising American capital to build the capacity that will compete directly with Mehrotra's Micron.

## What this means for NRI investors

Indian tech investors have been enthusiastic about Micron, and not just because of Mehrotra. The company's $2.75 billion semiconductor facility in Gujarat — India's first operational chip packaging plant — has turned Micron into a proxy bet on India's semiconductor ambitions. The stock's 850 per cent gain over the past twelve months has been one of the defining trades of the AI era.

But SK Hynix's arrival on the Nasdaq changes the arithmetic. Index-fund managers and ETF constructors who previously had only Micron as a liquid US memory play will now have an alternative. If SK Hynix enters US semiconductor benchmarks, passive flows that once went entirely to Micron will be split.

Mizuho has raised its Micron target to $1,375, and the analyst consensus remains overwhelmingly bullish — 36 out of 39 analysts rate it a Buy or Strong Buy. But the bears have two new talking points: SK Hynix's listing, and reports that Apple is separately lobbying Washington to source DRAM from Chinese chipmaker CXMT, potentially easing the very supply crunch that has given Micron its pricing power.

Memory markets are cyclical, and the current cycle has been spectacularly kind to Mehrotra and his shareholders. The question is whether SK Hynix's Nasdaq debut marks the beginning of the end of that cycle — or merely gives American investors a second way to bet on it."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "SK Hynix Is Coming to Nasdaq on July 10. Mehrotra's Micron Just Lost Its American Monopoly.",
    "subheadline": "The South Korean chipmaker that dominates high-bandwidth memory plans a $29 billion ADR listing — arriving on the same exchange as Micron, and directly in the sightlines of every NRI portfolio that rode the AI memory trade.",
    "slug": make_slug("sk-hynix-nasdaq-adr-micron-mehrotra-hbm-memory"),
    "category": "technology",
    "vertical": "semiconductors",
    "diaspora_angle": "NRI investors who bet on Micron for its Indian CEO and Gujarat fab now face a second memory stock on Nasdaq that could split passive index flows and compress Micron's valuation premium.",
    "tags": ["semiconductors", "sk-hynix", "micron", "sanjay-mehrotra", "nasdaq", "hbm", "ai-infrastructure", "nri-investing"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "The Motley Fool", "url": "https://www.fool.com/investing/2026/06/30/why-micron-technologys-stock-could-fall-after-july/"},
        {"name": "DigitalToday Korea", "url": "https://www.digitaltoday.co.kr/news/articleView.html?idxno=637845"},
        {"name": "CoinDesk", "url": "https://www.coindesk.cc/sk-hynix-stock-soars-13-on-microns-blockbuster-results-and-nasdaq-debut-announcement"},
        {"name": "Barron's", "url": "https://www.barrons.com/articles/micron-stock-price-memory-chip-prices-98f3c4c1"},
        {"name": "Marketbeat", "url": "https://www.marketbeat.com/instant-alerts/micron-technology-nasdaqmu-shares-gap-down-following-insider-selling-2026-07-01/"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/d/de/Sanjay_Mehrotra_2025_%28cropped%29.jpg",
    "image_caption": "Micron CEO Sanjay Mehrotra at a 2025 event",
    "image_attribution": "Wikimedia Commons",
    "body": art1_body.strip()
}

# ────────────────────────────────────────────────────────────────────────
# ARTICLE 2: Apple Lobbying for Chinese CXMT Memory Chips
# ────────────────────────────────────────────────────────────────────────
art2_body = """Apple just raised prices on MacBooks and iPads by as much as 25 per cent. Then it started lobbying the White House to buy memory chips from a company the Pentagon says is connected to the Chinese military.

The Financial Times reported last week that Apple has approached the US Commerce Department for clearance to purchase DRAM from ChangXin Memory Technologies, or CXMT — a Chinese chipmaker currently on the Pentagon's Section 1260H list, the government's register of companies believed to have ties to the People's Liberation Army. The move is Apple's most explicit acknowledgement yet that soaring memory prices are squeezing its hardware margins hard enough to warrant a geopolitical gamble.

## The memory price crunch

The numbers explain the urgency. DRAM contract prices rose roughly 3 per cent in June alone, according to KeyBanc analyst John Vinh, and NAND flash was up 2.4 per cent. These are not one-off spikes. The AI infrastructure boom has consumed so much memory capacity — Nvidia's AI accelerators alone require vast quantities of high-bandwidth memory — that conventional DRAM and NAND for consumer devices have been left in structural shortage.

"Meaningful capacity is not expected until 2027, which still will not be meaningful enough to close the gap," Vinh wrote in a research note.

For Apple, which ships hundreds of millions of iPhones, iPads, and Macs annually, every dollar per gigabyte of DRAM matters at scale. The company's recent price hikes — the first major across-the-board increases in years — suggest that the memory cost pressure has breached the level Apple is willing to absorb internally. Rosenblatt Securities analyst Barton Crockett warned that the price hikes "may not be pricing in the full impact of higher memory costs," creating risk to September-quarter margin guidance and raising questions about iPhone 18 pricing.

## The CXMT gamble

CXMT is China's leading DRAM producer and a centrepiece of Beijing's drive toward semiconductor self-sufficiency. The company has built multiple fabrication plants with government backing, but it remains dependent on certain Western equipment that falls under export controls — a circular problem that limits how fast it can scale.

Apple first approached the Commerce Department more than a month ago, according to the FT, and has since expanded its lobbying to other parts of the Trump administration. The political headwinds are obvious: approving a deal with a company on the Pentagon's military-linked list would be difficult for any administration, particularly one that has intensified semiconductor export restrictions on China.

Loop Capital, however, sees a potential upside for Apple shareholders. If approved, access to CXMT's DRAM would give Apple a fourth major memory supplier alongside Samsung, SK Hynix, and Micron — increasing Apple's bargaining leverage and potentially improving hardware margins over time.

## Why NRIs should watch this closely

The Apple-CXMT story sits at the intersection of three things Indian tech professionals care about deeply: the AI supply chain that employs tens of thousands of them, the semiconductor geopolitics that India is now a part of (via Micron's Gujarat fab and India's broader chip ambitions), and the consumer tech pricing that affects every product they buy.

If Apple succeeds, it signals that even the world's most valuable company cannot escape the AI memory crunch without diversifying into politically fraught supply chains. If it fails, memory prices stay elevated — good news for Micron and its Indian CEO Sanjay Mehrotra, but bad news for anyone buying an iPhone 18 in September.

Either way, the era of cheap memory is over. The AI boom broke that market, and the consequences are now showing up in the price of your MacBook."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "Apple Is Lobbying Washington to Buy Chips from a Blacklisted Chinese Company. The Price Tag Explains Why.",
    "subheadline": "Memory costs are soaring so fast that Apple raised Mac and iPad prices by up to 25 per cent — and is now asking the Trump administration for clearance to source DRAM from CXMT, a Chinese chipmaker on the Pentagon's military-linked list.",
    "slug": make_slug("apple-cxmt-chinese-memory-chips-lobbying-dram"),
    "category": "technology",
    "vertical": "semiconductors",
    "diaspora_angle": "The AI memory crunch affects every NRI in tech — from Micron's Gujarat fab and Indian chip ambitions to the iPhone 18 pricing that hits every consumer's wallet.",
    "tags": ["apple", "cxmt", "semiconductors", "dram", "memory-chips", "china", "supply-chain", "micron", "ai-infrastructure"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Investor's Business Daily", "url": "https://www.investors.com/news/technology/why-apple-wants-to-use-banned-chinese-memory-chips/"},
        {"name": "Marketbeat", "url": "https://www.marketbeat.com/originals/aapl-stock-lobbies-for-chinese-memory-chips-to-ease-supply-pressure/"},
        {"name": "Barron's", "url": "https://www.barrons.com/articles/micron-stock-price-memory-chip-prices-98f3c4c1"},
        {"name": "Barchart", "url": "https://www.barchart.com/story/news/32893159/apples-china-memory-push-could-be-a-win-for-aapl-stock"},
        {"name": "WebProNews", "url": "https://www.webpronews.com/apple-struggles-to-use-chinese-dram-chips-in-iphones-amid-us-china-tensions/"}
    ]),
    "score_total": 80,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/6636474/pexels-photo-6636474.jpeg",
    "image_caption": "RAM sticks and microprocessors on a motherboard — the components at the centre of the global memory shortage",
    "image_attribution": "Pexels",
    "body": art2_body.strip()
}

# ────────────────────────────────────────────────────────────────────────
# ARTICLE 3: Central Bankers' AI Anxiety at Sintra
# ────────────────────────────────────────────────────────────────────────
art3_body = """The world's most powerful central bankers spent three days in the hills of Portugal this week. Every conversation came back to the same subject: artificial intelligence.

At the European Central Bank's annual forum in Sintra — the gathering where the architects of global monetary policy go to think aloud — AI wasn't a side panel or a breakout session. It was the dominant theme, weaving its way into discussions about immigration, bank supervision, climate policy, and financial stability. Even the debut of Kevin Warsh, the new Federal Reserve chairman, was upstaged.

"This is the biggest time of consequence to each of our economies, I think, in our lifetime," Warsh told the forum. "Who knew when the internet was born that the internet was going to create a million and a half jobs as Uber drivers? We are in the first to second inning of this revolution."

## The bubble comparison nobody wanted to hear

The Bank for International Settlements, the central bank of central banks, released a report drawing explicit parallels between the current AI investment boom and some of the worst asset-price busts in history — the British railway mania of the 1840s, the roaring 1920s, and the dotcom crash.

"The scale and pace of the current AI investment boom accompanied by expectations of large productivity payoffs bear resemblance to these precedents, highlighting potential downside risks in the near term," the BIS warned.

Torsten Slok at Apollo Global Management put it more bluntly: "If AI overdelivers, it will impact financial stability. If AI underdelivers, it will impact financial stability." The heads-you-lose-tails-you-lose framing wasn't lost on the audience.

Capital expenditure by the hyperscalers — Amazon, Microsoft, Google, Meta — is estimated at around $725 billion this year, according to BNP Paribas, nearly double the level seen in mid-2025. That spending alone has added roughly one percentage point to US GDP, creating an economy that is partly running on the assumption that AI returns will justify the investment. If that assumption cracks, the correction reaches far beyond Silicon Valley.

## AI-driven market manipulation

University of Pennsylvania professor Itay Goldstein presented research showing that AI trading algorithms can coordinate on manipulative price paths — inflating bubbles, crashing them, and profiting in both directions in ways that current regulations classify as illegal collusion but struggle to detect or prevent.

"These algorithms indeed manage to achieve this kind of manipulation, creating bubbles leading to crashes," Goldstein told the forum. The implication for financial supervisors is uncomfortable: the tools they use to police markets may not work against AI systems that can move faster than any human regulator.

IMF official Tobias Adrian raised a parallel concern about agentic AI in banking. As AI systems begin making loan decisions autonomously, their reasoning becomes opaque. "How do supervisors assess those kind of agentic loan decisions? They are a little bit black box," he said.

## The Indian tech worker's dilemma

For the estimated 300,000 Indian H-1B workers in the US technology sector, the Sintra conversation carries a specific anxiety. The AI boom that employs them — and that has produced the hiring surges, the stock grants, and the green-card backlogs that define their American lives — is the same boom that central bankers now compare to the dotcom crash.

Indians accounted for nearly 70 per cent of all approved H-1B petitions in FY25, according to USCIS data, and the overwhelming majority work in AI-adjacent roles at companies whose valuations are built on the very spending the BIS now flags as potentially unsustainable. If hyperscaler capex contracts, the layoff cycle that has already claimed over 110,000 tech jobs in 2026 could accelerate — and for H-1B holders, losing a job triggers a 60-day clock to find new sponsorship or leave the country.

NRI portfolios are similarly exposed. The Nasdaq has returned roughly 11 per cent this year, but the gains are concentrated in a handful of AI-linked names. A correction in those stocks wouldn't just trim retirement accounts — it would undermine the wealth that many diaspora families are building for their children's education, US property purchases, and eventual return-to-India plans.

Bank of Canada Governor Tiff Macklem tried to offer perspective: "The internet proved to be better than anybody imagined, created whole new businesses, but we still got the dotcom bubble. It doesn't mean there can't be a period where the market gets ahead of itself."

That may be the most honest framing available. AI is real. The revolution is real. But so is the possibility that the market has priced in the revolution before it has actually arrived."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "The World's Central Bankers Just Held a Meeting. Every Conversation Was About AI.",
    "subheadline": "At the ECB's annual Sintra forum, the architects of global monetary policy compared the AI investment boom to the dotcom crash and the railway mania of the 1840s. For NRI tech workers and investors, the warning is personal.",
    "slug": make_slug("ecb-sintra-central-bankers-ai-bubble-dotcom-nri"),
    "category": "technology",
    "vertical": "ai-economy",
    "diaspora_angle": "Indian H-1B workers make up 70 per cent of US tech visa holders and NRI portfolios are heavily concentrated in AI stocks — both are directly exposed if central bankers are right about an AI-driven correction.",
    "tags": ["ai", "central-banks", "ecb", "federal-reserve", "dotcom-bubble", "financial-stability", "h1b", "nri-investing", "kevin-warsh"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/technology/artificial-intelligence/ai-hopes-fears-dominate-global-central-bank-meet-2026-07-01/"},
        {"name": "BIS Annual Report 2026", "url": "https://www.bis.org/publ/arpdf/ar2026e.htm"},
        {"name": "Marketwatch / Nomura", "url": "https://www.marketwatch.com/story/overlooked-bottlenecks-and-hyperscalers-forced-to-keep-spending-will-keep-the-chip-stock-rally-alive-says-nomura-team-fcb6e42a"},
        {"name": "Zacks", "url": "https://www.zacks.com/stock/news/2472817/tsmc-vs-nvidia-which-ai-semiconductor-stock-should-you-buy-in-july"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/3/37/Official_portrait_of_Kevin_M._Warsh.jpg",
    "image_caption": "Federal Reserve Chairman Kevin Warsh at the ECB Sintra forum, where he called the AI revolution the biggest economic event of our lifetime",
    "image_attribution": "Wikimedia Commons",
    "body": art3_body.strip()
}

# ── Insert ──────────────────────────────────────────────────────────────
articles = [art1, art2, art3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

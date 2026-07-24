#!/usr/bin/env python3
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
        "headline": "Nikesh Arora Held 800 Sales Meetings in 12 Weeks. The AI Cyberthreat He's Selling Against Is Bigger Than His Stock.",
        "subheadline": "Palo Alto Networks just posted 31% revenue growth and record demand as enterprises scramble to defend AI systems. For the diaspora's huge security workforce, it is the rare tech segment still hiring into the AI wave.",
        "slug": make_slug("nikesh-arora-palo-alto-networks-ai-cybersecurity-demand-surge-nri"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Cybersecurity is the rare corner of US tech still expanding headcount through the AI shakeout, and it sits under one of the highest-paid Indian-origin CEOs in the Valley — a real signal for diaspora engineers weighing where their skills stay durable.",
        "tags": ["cybersecurity", "indian-tech", "ai", "palo-alto-networks", "nikesh-arora"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Mint — Palo Alto Networks on India AI cyber threats", "url": "https://www.livemint.com/companies/news/indias-largest-corporates-mature-against-ai-cyber-threats-palo-alto-networks-11718000000000.html"},
            {"name": "The Motley Fool — AI supercharges Palo Alto's growth", "url": "https://www.fool.com/investing/2026/06/24/artificial-intelligence-ai-supercharged-cybersecurity-stock/"},
            {"name": "CoinCentral — IBM, Palo Alto, Red Hat cyber partnership", "url": "https://coincentral.com/ibm-teams-up-with-palo-alto-and-red-hat-to-fight-cyber-threats/"}
        ]),
        "score_total": 78,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ea/Nikesh_Arora_TechCrunch_Disrupt_2015.jpg/330px-Nikesh_Arora_TechCrunch_Disrupt_2015.jpg",
        "image_caption": "Palo Alto Networks chairman and CEO Nikesh Arora speaking at TechCrunch Disrupt",
        "image_attribution": "Wikimedia Commons",
        "body": """When a software company tells analysts it booked as many sales meetings in twelve weeks as it did in an entire previous year, two things are usually true: a genuine panic is underway among its customers, and the company selling the cure is having a very good quarter. Both apply to Palo Alto Networks, the cybersecurity giant run by Nikesh Arora, one of the highest-paid executives of Indian origin in Silicon Valley.

On the company's most recent post-earnings call, Arora told brokerages the firm had "held 800 client meetings and has 400 more pending in 12 weeks — that's the number of meetings we had all of last year." The driver is not a clever new product so much as a new species of fear. As enterprises rush to deploy AI agents, copilots and models across their operations, they are discovering that each one is a fresh attack surface — and that the same AI is now arming the attackers.

### The numbers behind the noise

Palo Alto's fiscal third-quarter revenue rose 31% year over year to roughly $3 billion. More telling than revenue was its remaining performance obligations — the value of signed contracts not yet delivered — which jumped 36% to $18.4 billion. When that backlog grows faster than revenue, it means a company is winning more business than it can physically fulfil. Its Prisma AIRS platform, built to secure AI apps, agents and models, went from a standing start to more than 300 customers in a year and is, in management's words, "the fastest scaling product in our history."

The stock has followed, up more than 60% in 2026 and trading near record highs around $290. Even Arora has tried to cool the temperature, telling one podcast that AI token prices "should be one-tenth of current levels" — an unusual admission from a CEO whose own margins benefit from the boom.

### Why the diaspora should pay attention

For the hundreds of thousands of Indian engineers in American tech, the cybersecurity story matters for an unglamorous reason: it is one of the few large segments still adding people while the rest of the industry sheds them. Oracle disclosed AI-related cuts that fell hardest on its India workforce; consulting firms are warning that AI is cannibalising the routine coding and testing that staffed a generation of H-1B careers. Security is moving the other way. Defending AI systems is labour-intensive, hard to automate away, and chronically short of skilled people — exactly the profile of work that protects a visa-dependent career.

It is also a field with deep Indian-origin leadership at the very top. Arora, a Delhi-born IIT and Northeastern graduate who ran Google's commercial business and briefly led SoftBank before taking over Palo Alto in 2018, presides over one of the most valuable cybersecurity franchises in the world. That visibility matters for the next cohort of diaspora professionals deciding which corner of tech to bet a green-card-length career on.

### The India angle is widening too

The growth is not confined to America. Palo Alto executives say India's largest corporates are maturing fast against AI-driven threats, helped by some of the world's strictest financial-sector technology rules. The company plans to invest heavily in local service providers and partners over the next three years, framing India's aggressive tech regulation — on data sovereignty, resilience and financial reporting — as a tailwind rather than a hurdle. For NRIs running cross-border businesses, that regulatory rigour cuts both ways: more compliance cost, but a more defensible digital economy back home.

This week the company also tied itself closer to another Indian-led giant. On June 24, Palo Alto announced a three-way partnership with IBM and Red Hat, integrating its virtual-patching technology with IBM's open-source security initiative. IBM chief Arvind Krishna said the deal gives clients "immediate, automated resilience against emerging threats" — two Indian-origin CEOs effectively pooling defences against the AI threat landscape both are racing to monetise.

### What's next

The bull case is straightforward: AI adoption keeps minting new attack surfaces, and someone has to guard them. The bear case is the one Arora himself keeps flagging — that AI costs collapse, commoditising parts of the stack and compressing the premium pricing the sector enjoys today. For a diaspora engineer, the practical read is simpler than the stock debate. In a year when "AI is coming for your job" has become the industry's background hum, the work of stopping AI from being weaponised is, for now, hiring."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Apple Just Raised MacBook Prices and Blamed a Memory Shortage. The Diaspora's Next India Trip Just Got More Useful.",
        "subheadline": "A chip-memory squeeze dubbed 'RAMageddon' pushed Apple to lift iPad and Mac prices for the first time mid-cycle, wiping $250 billion off its value. The same crunch is minting record profits at Indian-led Micron.",
        "slug": make_slug("apple-macbook-ipad-price-hike-memory-shortage-ramageddon-nri"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Higher US device prices change the household math for NRIs who already shuttle gadgets between India and America, while the memory shortage driving them is fattening the profits of Indian-led Micron and its planned Gujarat fab.",
        "tags": ["apple", "semiconductors", "memory-chips", "micron", "indian-tech"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters — Apple raises MacBook, iPad prices as memory costs skyrocket", "url": "https://www.reuters.com/technology/apple-raises-prices-macbooks-ipads-memory-costs-skyrocket-2026-06-25/"},
            {"name": "Reuters — Micron pitches AI deals as cure for memory's boom-bust cycle", "url": "https://www.reuters.com/technology/micron-joins-rivals-pitching-ai-deals-2026-06-25/"},
            {"name": "Reuters — Asian shares fall as Apple price hikes dent tech optimism", "url": "https://www.reuters.com/markets/asian-shares-fall-apple-price-hikes-2026-06-26/"}
        ]),
        "score_total": 80,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/11237834/pexels-photo-11237834.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A modern laptop on a desk, the kind of device hit by rising memory and storage costs",
        "image_attribution": "Pexels",
        "body": """Apple has spent years insisting it could absorb component costs that buckled lesser rivals. On Thursday, it stopped pretending. The company raised prices on iPads and MacBooks mid-cycle — a near-unheard-of move — and pinned the blame squarely on a runaway shortage of memory chips. "We have never seen a component price increase this much, this quickly," Apple said, adding that it had "shielded our customers from these increases so far" but had now run out of room.

The numbers are stark. A MacBook Air with 512GB of storage jumped to $1,299 from $1,099. A MacBook Pro with a terabyte rose to $1,999 from $1,699. Even the entry-level MacBook Neo, launched in March at $599 to chase Windows and Chromebook buyers, climbed to $699 — erasing the price edge it was built to wield. Apple also lifted prices on the HomePod and Apple TV. Investors flinched: the stock fell nearly 6%, shaving roughly $250 billion off Apple's market value and dragging Nasdaq futures down with it.

### 'RAMageddon'

The culprit is a memory crunch some analysts have started calling "RAMageddon." Prices for DRAM — the memory in virtually every modern device — rose as much as 98% in the first quarter of 2026 and are set to climb another 58% to 63% this quarter, according to industry tracker TrendForce. The cause is the same insatiable demand reshaping all of tech: AI data centres. Memory makers have prioritised high-margin orders from the likes of Nvidia, leaving phone and PC manufacturers scrapping over what's left.

Research firm IDC now expects the smartphone market to suffer its biggest-ever annual decline, near 14%, with PCs down 11.3%. Apple's iPhone was spared this round, but analysts are blunt that its hike "is coming." Rivals without Apple's supply-chain muscle may have to raise prices even more sharply; Dell fell more than 8% on the news.

### The Indian-led company on the other side of the trade

Here is the twist that makes this a diaspora story. The shortage crushing Apple is enriching Micron Technology, the memory giant run by Sanjay Mehrotra, the Kanpur-born engineer who co-founded SanDisk before taking Micron's helm. Micron's shares surged almost 16% to a record high this week after it told Wall Street that customers including Nvidia had committed $22 billion in long-term "take-or-pay" deals to lock in supply. "Micron tells us where the profits are. Apple tells us where the inflation is," as one fund chief put it.

Micron also said supplies will stay tight until at least 2027 — meaning the device-price pain is not a one-quarter event. For the diaspora, that long shadow lands in two specific places. First is Micron's $2.75 billion assembly-and-test plant in Sanand, Gujarat, India's most advanced operating semiconductor facility and a magnet for returning Indian chip engineers. A structural memory boom is precisely the demand backdrop that makes such a fab — and the careers attached to it — more durable, not less.

### Why it hits the NRI household

The second place it lands is the kitchen table. For Indian American families, gadgets are rarely a purely local purchase. The well-worn ritual of buying a MacBook in the US for a cousin in Bengaluru, or hauling an iPad back from a Diwali trip home, runs on a price gap between the two markets. A $200 jump on a US MacBook narrows that arbitrage and changes the arithmetic of which side of the ocean is the better place to buy. With Indian import duties and a weak rupee already in the mix, the calculus that has guided diaspora tech-shopping for two decades suddenly needs redoing.

### What's next

Apple was strategic in its timing, announcing hikes well before its autumn iPhone launch so the headlines at the event highlight new features, not new prices. But the broader signal is hard to miss: the AI build-out is no longer a story confined to data centres and chip stocks. It is now reaching into the price of the laptop a college-bound diaspora kid carries to campus — and into the bottom line of the Indian-led company quietly cashing in on the squeeze."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India Just Processed 23 Billion Digital Payments in a Single Month. The Number Should Worry Visa and Mastercard.",
        "subheadline": "UPI handled Rs 29.9 lakh crore in May alone, up nearly 19% in a year, as PhonePe holds 46% of the market. For NRIs, the rails they use to send money home are quietly becoming a global export.",
        "slug": make_slug("upi-23-billion-transactions-may-2026-phonepe-npci-nri-payments"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "UPI is the plumbing NRIs increasingly use to pay, split bills and send money across the India-US corridor, and its international push means the diaspora may soon scan the same QR codes abroad that they use back home.",
        "tags": ["fintech", "upi", "digital-payments", "phonepe", "indian-tech"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Analytics Insight — Best UPI apps and NPCI May 2026 data", "url": "https://www.analyticsinsight.net/fintech/best-upi-apps-for-digital-payments-in-india"},
            {"name": "The Hindu BusinessLine — BHIM transaction volumes triple", "url": "https://www.thehindubusinessline.com/money-and-banking/bhim-payments-app-transaction-volumes-more-than-triple-in-one-year/article69000000.ece"},
            {"name": "Reuters — Meta's $900m CRED bet and India payments", "url": "https://www.reuters.com/breakingviews/mark-zuckerberg-tries-buy-payments-redemption-2026-06-24/"}
        ]),
        "score_total": 74,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/37594390/pexels-photo-37594390.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A contactless mobile payment being made with a smartphone",
        "image_attribution": "Pexels",
        "body": """A single statistic from India's National Payments Corporation tells you how far the country's financial plumbing has outrun the rest of the world. In May 2026, the Unified Payments Interface — UPI — processed 23.2 billion transactions worth Rs 29.9 lakh crore, roughly $360 billion, in one month. That is close to 19% growth in a year, on a base that was already the largest real-time payments system on earth. The figure dwarfs anything Visa or Mastercard run through comparable rails domestically, and it is achieved largely without their networks taking a cut.

For a system that did not exist a decade ago, the dominance is remarkable. PhonePe, the Walmart-backed app, now controls about 46.2% of the UPI market. Google Pay holds 32.7%. Between them, two apps move the bulk of a nation's everyday money — from roadside chai stalls to luxury showrooms — at a marginal cost to the consumer of essentially zero.

### Why this is a diaspora story, not just an India story

For NRIs, UPI has quietly become infrastructure they touch constantly, even from abroad. The system increasingly underpins the India end of the remittance corridor — the money flowing from New Jersey, the Bay Area and London back to family accounts in India, a flow that runs into the tens of billions of dollars a year. Where that money once arrived through slow, fee-heavy wire transfers, it now lands in seconds in accounts that can immediately spend it via a QR code. NPCI has been steadily wiring UPI to non-resident bank accounts and to overseas markets, meaning the diaspora may soon scan the same codes in Singapore, the Gulf or even parts of the US that they already use in Mumbai.

That matters because it inverts a long-standing relationship. For years, Indian consumers adopted American payment technology — cards, then PayPal-style wallets. UPI is one of the first cases of the traffic running the other way: an Indian-built public utility being exported as a template, with countries from France to the UAE signing on. For diaspora professionals in fintech, it is also a hiring story, as the engineering talent that built these rails becomes a sought-after export in its own right.

### The land grab is intensifying

The competitive stakes just rose sharply. Meta announced a $900 million investment in CRED, the Bengaluru credit-card-rewards startup, valuing it at roughly $4.5 billion and installing founder Kunal Shah as the global head of WhatsApp. The move is widely read as Meta's attempt to finally crack Indian payments through WhatsApp's vast user base — a market where Walmart's PhonePe and Alphabet's Google Pay already dominate. India's regulators, wary of US Big Tech concentration even as they welcome competition, are reportedly already fielding calls to review the deal.

Meanwhile the state-backed BHIM app, often dismissed as an also-ran, said its transaction volumes more than tripled in a year, built around support for 15-plus regional languages and low-connectivity rural use. The contest is no longer just about who owns the urban consumer; it is about reaching the next few hundred million users in towns and villages where the diaspora's extended families often still live.

### The catch

Dominance brings scrutiny. Regulators have long worried about two private apps controlling nearly 80% of a critical public utility, and have repeatedly floated — then delayed — market-share caps that would force PhonePe and Google Pay to slow their own growth. Any such cap would reshape the sector overnight, with implications for the valuations of PhonePe, which has paused its planned IPO, and rivals like Razorpay, which has confidentially filed for a roughly $600 million listing.

### What's next

The trajectory is clear even if the league table is not. UPI's volumes keep compounding, its international footprint keeps widening, and the biggest names in global tech — Meta included — keep paying up to get inside it. For the diaspora, the practical upshot is that the rails connecting their two financial lives are getting faster, cheaper and more global. The system that started as a way for Indians to split a dinner bill is on its way to becoming one of India's most consequential technology exports."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-06-05 21:00 UTC batch"""
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


# ─────────────────────────────────────────────────────────
# ARTICLE 1: Chip Selloff Erases $1 Trillion
# ─────────────────────────────────────────────────────────

article1_body = """The numbers are hard to read without flinching. On Friday, the PHLX semiconductor index plunged nearly 8.5 per cent in a single session — its deepest one-day loss since the "Liberation Day" tariff selloff of April 2025. Across the chip sector, more than $1 trillion in market capitalisation evaporated. NVIDIA fell 6.2 per cent, shedding over $300 billion. Micron Technology tumbled 11 per cent, erasing $127 billion. AMD lost 10.5 per cent. Marvell Technology gave back 12 per cent.

The catalyst was Broadcom. The custom AI chipmaker reported quarterly results on Wednesday that beat on revenue and profit, but its forward guidance left the market cold: $16 billion in projected AI chip revenue for the next quarter, versus the $17.2 billion analysts had modelled. The company kept its fiscal 2027 outlook at $100 billion, unchanged. AVGO stock dropped 12.6 per cent on Thursday, then slid another 7.5 per cent on Friday. Its two-day loss totalled 19 per cent.

## The jobs report didn't help

Adding fuel to the fire, Friday morning's U.S. jobs data came in stronger than expected. The 10-year Treasury yield jumped seven basis points to 4.54 per cent, and traders promptly repriced the odds of a Federal Reserve rate *hike* in 2026. The Nasdaq composite fell 4 per cent — its worst session in over a year. The S&P 500 shed 2.3 per cent.

"You've had a lot of people here that were just blindly buying the dip," said Dennis Dick, a proprietary trader at Triple D Trading. "Blindly buying the dip had been winning you money, but that ended today."

## Why Indian tech workers should care

For the roughly 400,000 Indian-origin engineers working across Silicon Valley, Seattle, and Austin, this selloff hits where it hurts: restricted stock units. RSU vesting schedules at NVIDIA, AMD, Micron, and Broadcom are the de facto compensation floor for H-1B workers. A 6 to 13 per cent single-day decline in the stock underlying your compensation package is not an abstraction — it is a pay cut, timed to a week where layoff announcements already topped 38,000 across the tech sector in May alone.

Meanwhile, Senator Elizabeth Warren has invited NVIDIA CEO Jensen Huang to testify before the Senate Banking Committee on June 11. The subject: a reported loophole that may have allowed Chinese entities, including Alibaba, to acquire NVIDIA's restricted Blackwell AI chips by routing purchases through Malaysia and Singapore. If the loophole is closed with new export controls, NVIDIA's top line takes a hit. If it isn't, Washington's semiconductor hawks will escalate. Either way, the company's India-based engineering teams — numbering in the thousands across Bengaluru and Hyderabad — face strategic uncertainty.

## The bigger picture

Even after Friday's bloodletting, the PHLX chip index remains up 75 per cent year to date. The iShares Semiconductor ETF (SOXX) has nearly doubled in 2026 compared to the S&P 500's 11 per cent gain. The market is not collapsing — it is recalibrating. Broadcom's guidance gap was narrow. NVIDIA's Vera Rubin chips remain on track for volume shipments in Q3. TSMC's CEO has been publicly saying AI chip demand will outstrip supply for years.

For NRI investors who loaded up on chip stocks during the AI euphoria, Friday's lesson is one that no Computex keynote can teach: valuation discipline still applies, even in a structural bull market. The question is whether this is a buying opportunity or the start of something uglier. Morgan Stanley's Joseph Moore thinks it is the former — "relative risk/reward in an increasingly crowded semis opportunity set looks attractive," he wrote. But the next data point is the Fed meeting on June 17. Until then, portfolios are exposed."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "The Chip Selloff Just Erased $1 Trillion. Your RSUs Felt Every Dollar.",
    "subheadline": "Broadcom's soft AI guidance, a hot jobs report, and rate-hike fears combined to deliver the Nasdaq's worst day in over a year. Indian engineers' stock compensation bore the brunt.",
    "slug": make_slug("chip-selloff-trillion-rsu-indian-engineers-broadcom"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Indian tech workers in the US hold significant RSU compensation in chip stocks like NVIDIA, AMD, and Micron. A single-day 6-13% decline directly impacts take-home pay, compounding anxiety amid 123,000+ tech layoffs in 2026.",
    "tags": ["semiconductors", "nvidia", "broadcom", "rsu", "indian-tech-workers", "stock-market"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/markets/chip-selloff-erases-over-1-trillion-stock-market-value-2026-06-05/"},
        {"name": "Investor's Business Daily", "url": "https://www.investors.com/market-trend/stock-market-today/nasdaq-sinks-4-rate-hike-worries-nvidia-falls-chip-sell-off/"},
        {"name": "Barron's", "url": "https://www.barrons.com/articles/nvidia-stock-price-rtx-spark-computex-2026/"},
        {"name": "StockTwits", "url": "https://stocktwits.com/news/article/nvda-intc-amd-mu-major-chip-stocks-fall-for-second-day/"}
    ]),
    "score_total": 85,
    "status": "published",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/534216/pexels-photo-534216.jpeg",
    "image_caption": "Stock market trading screens displaying market data",
    "image_attribution": "Pexels",
    "is_editorial": False,
    "body": article1_body,
}


# ─────────────────────────────────────────────────────────
# ARTICLE 2: Innefu Labs $30M Series B
# ─────────────────────────────────────────────────────────

article2_body = """A New Delhi-based cybersecurity startup you have probably never heard of just raised $30 million to build what it calls "sovereign AI" for national defence. If that phrase sounds like government-contractor jargon, look closer: Innefu Labs is one of the few Indian companies whose software sits inside the country's terrorism data fusion centre, predictive policing platforms, and revenue intelligence operations.

The Series B round, led by Singapore-based Panthera Growth Partners through its second fund backed by institutional investors from India, the EU, and the US, positions the 15-year-old company for an initial public offering. It is a rare outcome for an Indian deep-tech firm in a market that has historically rewarded consumer apps and fintech plays.

## What Innefu actually does

Founded in 2010 by Tarun Wig and Abhishek Sharma, Innefu develops AI-powered systems for defence, intelligence, law enforcement, and enterprise security. Its client list includes India's defence and intelligence agencies, financial institutions, and Fortune 500 companies. The startup claims over 100 installations across the Indian subcontinent, the Middle East, and Southeast Asia.

Its products span intelligence fusion centres, open-source intelligence tools, and predictive policing systems — the kind of infrastructure that India's security establishment has been building out aggressively as cyber threats escalate. The company holds a growing pipeline of contracts exceeding ₹100 crore.

"The next wave of technological leadership will belong to nations that own their intelligence capabilities," Wig said in a statement. "Innefu is committed to ensuring that India stands at the forefront of that transformation."

## The sovereign AI thesis

The $30 million will fund three priorities: expanding Innefu's proprietary agentic AI platform, establishing a dedicated robotics and physical AI division, and building domain-specific language models designed for high-security environments. That last item — sovereign LLMs — is where the strategic bet gets interesting.

Most of the world's AI models are built by American companies, trained on English-language data, and hosted on US cloud infrastructure. For a country's intelligence apparatus, that dependency is a liability. India's defence procurement bureaucracy has been quietly pushing for AI systems that run on Indian infrastructure, trained on Indian data, governed by Indian rules. Innefu is positioning itself as the vendor that can deliver exactly that.

Shilpa Kulkarni, Panthera's founder and managing director, said the investment was based on Innefu's "proprietary technology, deep domain expertise, and a proven track record in high-stakes, mission-critical environments."

## The diaspora angle

For NRI tech professionals — especially the thousands working at Palantir, Booz Allen Hamilton, Raytheon, and other US defence contractors — Innefu's trajectory is instructive. India is building its own defence-tech ecosystem, and it is doing so with a level of ambition that would have been unthinkable a decade ago. The Narendra Modi government's push for self-reliance in defence (Atmanirbhar Bharat) has created a market that rewards companies willing to build sensitive technology domestically rather than license it from abroad.

For those contemplating a return to India, defence tech is emerging as a legitimate career path — one that didn't exist five years ago. Innefu's path to IPO, if it gets there, would be among the first for an Indian cybersecurity pure-play. That alone makes it worth watching.

The broader context is equally compelling. India's cybersecurity market is projected to exceed $6 billion by 2028, driven by a surge in state-sponsored cyberattacks, the digitisation of government services, and the growing adoption of AI in critical infrastructure. Companies like Innefu, which combine deep government relationships with genuine AI capability, sit at the intersection of national security and venture-scale returns — a combination that, until recently, was exclusively an American story."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "India's Cybersecurity Startup Innefu Labs Just Raised $30 Million. Its Client Is the State.",
    "subheadline": "The 15-year-old Delhi company builds AI for India's intelligence agencies and defence apparatus. A Singapore-backed Series B now puts it on the path to an IPO.",
    "slug": make_slug("innefu-labs-30m-series-b-sovereign-ai-cybersecurity-india"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Indian defence-tech is emerging as a real career path for NRI engineers at US contractors like Palantir and Raytheon. Innefu's IPO trajectory signals India's growing sovereign AI ambitions and offers NRI investors exposure to a sector that didn't exist five years ago.",
    "tags": ["cybersecurity", "indian-startups", "defense-tech", "sovereign-ai", "funding"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "YourStory", "url": "https://yourstory.com/2026/06/innefu-labs-raises-30m-series-b-panthera"},
        {"name": "Inc42", "url": "https://inc42.com/buzz/cybersecurity-startup-innefu-labs-raises-30-mn-from-panthera-growth-partners/"},
        {"name": "Entrepreneur India", "url": "https://india.entrepreneur.com/article/innefu-labs-raises-usd-30-mn-in-series-b/"},
        {"name": "HDFC Sky", "url": "https://www.hdfcsky.com/blog/ai-firm-innefu-labs-bags-usd-30-million-in-funding/"}
    ]),
    "score_total": 72,
    "status": "published",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/1181354/pexels-photo-1181354.jpeg",
    "image_caption": "Server infrastructure in a secure data centre facility",
    "image_attribution": "Pexels",
    "is_editorial": False,
    "body": article2_body,
}


# ─────────────────────────────────────────────────────────
# ARTICLE 3: Nikesh Arora / Palo Alto Networks Q3
# ─────────────────────────────────────────────────────────

article3_body = """Nikesh Arora has a credibility problem, and it is the best kind: his numbers keep getting better, and Wall Street keeps selling the stock anyway.

Palo Alto Networks reported fiscal third-quarter revenue of $3 billion on Tuesday, up 31 per cent year over year, beating analyst estimates by nearly $60 million. Adjusted earnings came in at $0.85 per share, above consensus. Next-generation security annual recurring revenue hit $8.13 billion, up 60 per cent. Remaining performance obligations — essentially the backlog of contracted future revenue — swelled to $18.4 billion, a 36 per cent jump.

The stock dropped 5.6 per cent.

## Buy the rumour, sell the IIT grad

The arithmetic is straightforward. Palo Alto shares had surged 79 per cent in the 30 trading days before the earnings call — the biggest pre-earnings run in at least 13 years, according to Jefferies. At those levels, even a strong quarter becomes a sell-the-news event. Organic annual recurring revenue growth of 28 per cent, while healthy, came in fractionally below what some portfolio managers had hoped for. In a market this frothy, fractions matter.

Still, the underlying story is one of the most impressive in enterprise software. Arora, who left SoftBank in 2018 after a bruising exit as Masayoshi Son's heir apparent, has methodically rebuilt his reputation by turning Palo Alto from a firewall company into the most aggressive platform play in cybersecurity.

## The AI-and-cybersecurity feedback loop

The quarter's standout metric was less about revenue and more about urgency. Arora told analysts that "the latest advancements at the AI frontier have increased the level of urgency around cybersecurity, and redefined the shape of the industry for the coming years."

Translation: every company deploying AI models — from OpenAI's API consumers to enterprises running internal fine-tuned LLMs — needs to secure the data pipelines, endpoints, and inference infrastructure that those models depend on. AI creates new attack surfaces, and Palo Alto is positioning itself as the company that protects them.

Unit 42, the company's elite threat-intelligence and consulting arm, launched Frontier AI Defense during the quarter. Within six weeks, it had logged over 800 customer meetings. A single deal with a leading US power producer was worth $80 million. Another, with a global consulting firm using Palo Alto's Prisma AIRS platform, came in above $20 million.

Arora confirmed a target of 40 per cent adjusted free cash flow margin by fiscal year 2028. UBS raised its price target to $300. Evercore ISI went to $375 with a Buy rating.

## The IIT Varanasi kid in the room

Arora's arc is one of the more improbable in Indian-American corporate history. Born in Ghaziabad, educated at IIT Varanasi (now IIT BHU) and Northeastern University, he rose through the ranks at T-Mobile, Putnam Investments, and Google, where he served as chief business officer and was widely seen as a potential CEO candidate. His three years at SoftBank — where he was paid over $200 million, an amount that itself became a controversy — ended with an abrupt resignation in 2016.

Taking the CEO chair at Palo Alto Networks in 2018, Arora inherited a company that was respected but stagnating. His bet on "platformisation" — consolidating dozens of point security products into a single integrated platform — was met with scepticism. Seven years later, the market cap has crossed $250 billion. Palo Alto is the most valuable pure-play cybersecurity company on earth.

For Indian engineers working in cybersecurity at CrowdStrike, Fortinet, or Zscaler, Arora's trajectory is both aspirational and instructive. He did not get to $250 billion by playing it safe. He got there by making an unpopular bet on integration over best-of-breed, then executing relentlessly until the numbers made the argument for him.

His next challenge: proving that a cybersecurity company can sustain 30 per cent revenue growth while expanding margins. Friday's chip-led selloff dragged Palo Alto down 2.6 per cent alongside everything else. The market, once again, isn't paying for perfection. Arora, one suspects, is fine with that."""

article3 = {
    "id": str(uuid.uuid4()),
    "headline": "Nikesh Arora's Palo Alto Networks Just Hit $3 Billion in a Quarter. The Stock Still Fell.",
    "subheadline": "The IIT Varanasi grad has turned a firewall company into a $250 billion cybersecurity platform. Wall Street's response to his best quarter yet was to take profits.",
    "slug": make_slug("nikesh-arora-palo-alto-networks-3b-quarter-cybersecurity"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Nikesh Arora's journey from IIT Varanasi to running the world's most valuable cybersecurity company is an instructive arc for Indian-American tech professionals. His platformisation bet mirrors the integration-over-fragmentation instinct that many Indian engineering leaders bring to enterprise tech.",
    "tags": ["nikesh-arora", "palo-alto-networks", "cybersecurity", "indian-ceo", "earnings"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Palo Alto Networks IR", "url": "https://www.stocktitan.net/press-releases/PANW/palo-alto-networks-q3-revenue-rises-31-to-3b/"},
        {"name": "MarketWatch", "url": "https://www.marketwatch.com/story/palo-alto-networks-earnings-show-ai-brings-new-urgency-to-cybersecurity/"},
        {"name": "Seeking Alpha", "url": "https://seekingalpha.com/article/palo-alto-networks-panw-q3-2026-earnings-call-transcript"},
        {"name": "CoinCentral", "url": "https://coincentral.com/palo-alto-networks-panw-stock-drops-6-after-strong-earnings/"}
    ]),
    "score_total": 78,
    "status": "published",
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/e/ea/Nikesh_Arora_TechCrunch_Disrupt_2015.jpg",
    "image_caption": "Nikesh Arora, CEO of Palo Alto Networks, at TechCrunch Disrupt",
    "image_attribution": "Wikimedia Commons",
    "is_editorial": False,
    "body": article3_body,
}


# ─────────────────────────────────────────────────────────
# PUBLISH
# ─────────────────────────────────────────────────────────

articles = [article1, article2, article3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

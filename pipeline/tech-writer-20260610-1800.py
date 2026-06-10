#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-06-10 18:00 UTC run"""
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
    # ── ARTICLE 1: Nikesh Arora / Palo Alto Networks ──
    {
        "id": str(uuid.uuid4()),
        "headline": "Nikesh Arora's Palo Alto Networks Just Hit a $10 Billion Run Rate. He's Not Done.",
        "subheadline": "A record quarter, a new identity security platform, a 57% stock rally, and a fresh Indian CMO — the former SoftBank president is quietly building cybersecurity's most complete empire.",
        "slug": make_slug("nikesh-arora-palo-alto-10-billion-idira-cybersecurity"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Arora is one of the highest-profile Indian-origin CEOs in Silicon Valley. For the tens of thousands of Indian engineers working in cybersecurity — and NRI investors holding PANW stock — his transformation of Palo Alto Networks into an AI-era platform company is both career inspiration and portfolio fuel.",
        "tags": ["nikesh-arora", "palo-alto-networks", "cybersecurity", "indian-ceo", "ai-security"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Motley Fool", "url": "https://www.fool.com/investing/2026/06/08/why-palo-alto-networks-stock-skyrocketed-57-last-month/"},
            {"name": "CoinCentral", "url": "https://coincentral.com/palo-alto-networks-panw-stock-analysts-bullish-insiders-selling/"},
            {"name": "GlobeNewsWire", "url": "https://www.globenewswire.com/news-release/2026/06/09/palo-alto-networks-idira-identity-security/"},
            {"name": "MarketBeat", "url": "https://www.marketbeat.com/stocks/NASDAQ/PANW/earnings/"},
            {"name": "Marketing Interactive", "url": "https://www.marketing-interactive.com/palo-alto-networks-names-new-cmo"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/e/ea/Nikesh_Arora_TechCrunch_Disrupt_2015.jpg",
        "image_caption": "Nikesh Arora, Chairman and CEO of Palo Alto Networks",
        "image_attribution": "Wikimedia Commons",
        "body": """There is a running joke in cybersecurity circles that Nikesh Arora does not do small quarters. The former Google executive and SoftBank president just proved it again.

Palo Alto Networks reported fiscal Q3 2026 revenue of $3 billion, up 31.1% year-over-year and comfortably ahead of the $2.94 billion consensus. Earnings per share landed at $0.85, beating the Street's $0.79 estimate. The company now expects full-year EPS of $3.77 to $3.79, and its annual revenue run rate has crossed $10 billion for the first time.

The stock responded accordingly. PANW shares rose 57.1% in May alone — more than ten times the S&P 500's 5.2% gain — before pulling back modestly in June. Year-to-date, the stock is still up roughly 48%. At a market cap north of $220 billion, Palo Alto Networks is now the world's most valuable pure-play cybersecurity company by a significant margin.

## The Idira Bet

What makes this quarter interesting is not just the revenue beat. On May 12, Arora unveiled Idira, a next-generation identity security platform that may define Palo Alto's next chapter. In a world where AI agents, machine identities, and human users coexist on the same networks, traditional always-on access is a liability. Idira replaces it with dynamic privilege — access granted just-in-time and revoked in real time.

The platform secures every identity class — human, machine, and AI agent — from a single control plane. Its AI engine surfaces hidden entitlements and unmanaged accounts, recommends least-privilege configurations, and remediates automatically. Arora pointed out on the earnings call that attackers move in 72 minutes; defenders historically took days. Idira is designed to close that gap.

Two weeks later, Palo Alto closed its acquisition of Portkey, an AI gateway company specializing in regulating agentic AI interactions, monitoring token usage, and blocking malicious AI exploits. The Portkey deal, initially announced in April, plugs directly into the Idira thesis: if AI agents are the new workforce, someone has to police them.

## The Indian Pipeline

There is another dimension worth watching. In March, Palo Alto Networks appointed KP Unnikrishnan as chief marketing officer — its first Indian-origin CMO. Unnikrishnan spent nearly a decade at the company, most recently running marketing for Asia-Pacific and Japan, and now reports directly to Arora. The appointment signals both the depth of Indian talent inside the company and Arora's comfort building his leadership bench from within.

For Indian cybersecurity professionals in the Bay Area and beyond, Palo Alto's rise under Arora offers a template. Next-Generation Security ARR jumped 60% year-over-year to exceed $8 billion. Remaining performance obligations grew 36% to $18.4 billion — a figure that signals strong forward revenue visibility and, by extension, hiring stability.

## The Catch

On a GAAP basis, the quarter was messier. Palo Alto reported a net loss of $177 million, compared to a $262 million profit a year ago, dragged down by acquisition-related costs tied to CyberArk and Chronosphere. Non-GAAP net income came in at $684 million. And insiders, including executives, sold over $17.9 million in stock during the quarter — not unusual after a 57% run, but worth noting.

Analysts remain broadly bullish. FBN Securities upgraded PANW to a "strong buy," and the consensus price target sits around $306. But some commentators argue the stock has run too far too fast, and that the AI cybersecurity premium is already priced in.

For NRI investors holding PANW or considering a position, the question is not whether Arora can execute. That much he has proven. The question is whether the market will keep paying a premium for cybersecurity's most aggressive acquirer — or whether the next few quarters need to show that Idira, Portkey, and the rest of the platform can generate returns, not just headlines."""
    },

    # ── ARTICLE 2: Global semiconductor market $300B quarterly ──
    {
        "id": str(uuid.uuid4()),
        "headline": "The Chip Industry Just Broke $300 Billion in a Single Quarter. India Is Barely in the Frame.",
        "subheadline": "AI-fueled memory demand sent global semiconductor revenue to a record, with NAND up 96% in Q1 2026. For Indian engineers building the chips and NRI investors holding the stocks, the boom is real — but India's share of it remains vanishingly small.",
        "slug": make_slug("semiconductor-market-300-billion-quarterly-memory-ai-boom"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Tens of thousands of Indian engineers work at TSMC suppliers, memory giants SK Hynix and Micron, and design houses across the semiconductor stack. NRI portfolios are heavily exposed to chip stocks. Meanwhile, India's own fab story — Tata Dholera, Micron Gujarat — is still years from production. This market milestone frames the gap between where Indian talent sits and where Indian manufacturing stands.",
        "tags": ["semiconductor", "ai-chips", "memory", "tsmc", "nri-investors", "india-fab"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "AInvest", "url": "https://ainvest.com/news/semiconductor-market-surpasses-300bn-quarterly-revenue-1q26/"},
            {"name": "Reuters", "url": "https://www.reuters.com/technology/taiwan-may-exports-hit-second-highest-value-by-month-strong-ai-demand-2026-06-09/"},
            {"name": "EMSNow", "url": "https://emsnow.com/india-accelerates-semiconductor-display-ambitions-new-approvals-ai-infrastructure/"},
            {"name": "Barchart / TSMC Analysis", "url": "https://www.barchart.com/story/news/37684990/taiwan-semi-posts-better-than-expected-earnings"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/36169774/pexels-photo-36169774.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
        "image_caption": "Close-up of electronic microchips on a circuit board",
        "image_attribution": "Pexels",
        "body": """The global semiconductor industry just did something it has never done before. Quarterly revenue topped $300 billion in Q1 2026, driven by an 80% sequential surge in memory revenue that Omdia calls the steepest climb since it started tracking the market in 2002.

The numbers are staggering. NAND revenue alone hit $48 billion, up 96% quarter-over-quarter. DRAM followed suit. Non-memory chips, by contrast, grew just over 2%. The divergence tells a clear story: AI infrastructure is consuming memory at a pace that chip factories cannot match, and the resulting supply-demand imbalance — what the industry has taken to calling "memflation" — is repricing the entire semiconductor stack.

Gartner now projects the global chip market will reach $1.3 trillion in annual revenue in 2026, a 64% year-over-year increase. The World Semiconductor Trade Statistics organization has its own forecast north of $1 trillion. Either way, the industry is growing at a rate not seen since the early days of the smartphone revolution, and AI is the engine.

## Taiwan Keeps Winning

Taiwan's May export data, released on June 9, reinforced the geography of this boom. Exports jumped 51.7% year-over-year to $78.48 billion — the second-highest monthly figure on record, crushing analyst expectations of 37.9%. Electronic component exports surged 66.9%. Information products rose 118%.

TSMC, the foundry that makes the advanced chips powering NVIDIA, Apple, and AMD, reported Q1 revenue of $35.9 billion, up 40.6% year-over-year, and guided for $39 billion to $40.2 billion in Q2. The company raised its full-year guidance and now expects revenue to grow more than 30% in dollar terms for 2026.

For Indian engineers at these companies — and there are thousands working on chip design, verification, and process engineering at TSMC's ecosystem of suppliers, at Synopsys and Cadence in the Bay Area, at Micron's Hyderabad design center, at Intel's Bangalore campus — this is the most favorable hiring and compensation environment in years.

## India's Paradox

The paradox is that India, which supplies a disproportionate share of the world's chip design talent, barely registers in the manufacturing data. Tata Electronics' Dholera fab, the most ambitious of India's semiconductor projects, is still under construction. Micron's Gujarat ATMP (assembly, test, and packaging) facility broke ground in 2023 but is not yet at volume production. The IISc semiconductor training fab opened last week, but training engineers is different from shipping wafers.

India's new approvals — Mini/Micro LED GaN fabrication and large-scale packaging capacity — signal ambition. But ambition and output are different things. In a quarter where the world shipped $300 billion worth of chips, India's contribution was negligible.

## The NRI Portfolio Question

For NRI investors, the semiconductor boom presents both opportunity and concentration risk. Many are heavily exposed through NVDA, TSM, AVGO, MU, and INTC. The SOXX semiconductor ETF is up sharply this year, but the same AI demand that drives revenue also drives volatility — the $1.3 trillion chip rout earlier this month, followed by a Monday bounce, was a reminder that these stocks move fast in both directions.

The memory subsector, in particular, rewards early entry and punishes late arrivals. SK Hynix and Samsung have expanded capacity, but HBM (high-bandwidth memory) for AI training remains supply-constrained, supporting prices. The question is how long "memflation" lasts before new capacity catches up.

For Indian Americans watching both their portfolios and their home country's industrial ambitions, the $300 billion quarter is a milestone that invites mixed emotions. The talent is Indian. The profits are not — at least not yet."""
    },

    # ── ARTICLE 3: India-US tech diplomacy — Ambassador Kwatra ──
    {
        "id": str(uuid.uuid4()),
        "headline": "India's Ambassador Just Ran a Tech Diplomacy Blitz in Washington. Quantum and Physical AI Were on the Table.",
        "subheadline": "Vinay Kwatra met with Walmart, the Special Competitive Studies Project, and counter-terrorism officials in a single sweep — signaling that India-US tech cooperation is moving from talking points to trade routes.",
        "slug": make_slug("india-us-tech-diplomacy-kwatra-quantum-physical-ai"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "India-US tech ties directly shape the diaspora's professional and investment landscape. Deeper cooperation on AI, quantum, and supply chains could mean more cross-border roles, expanded R&D centers in India, and better regulatory frameworks for NRIs working at the intersection of both economies.",
        "tags": ["india-us-relations", "ai-policy", "quantum-computing", "tech-diplomacy", "vinay-kwatra"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "ANI / Nordot", "url": "https://nordot.app/indian-envoy-vinay-kwatra-meets-us-corporate-tech-leaders/"},
            {"name": "NewKerala", "url": "https://www.newkerala.com/news/2026/indian-envoy-kwatra-meets-us-leaders-ai-supply-chain.html"},
            {"name": "Daily Prabhat", "url": "https://dailyprabhat.com/indian-envoy-vinay-kwatra-meets-us-corporate-and-tech-leaders/"}
        ]),
        "score_total": 72,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/1/13/Ambassador_Vinay_Mohan_Kwatra_Indian_Foreign_Service.png",
        "image_caption": "Vinay Mohan Kwatra, India's Ambassador to the United States",
        "image_attribution": "Wikimedia Commons",
        "body": """If you want to understand where India-US technology cooperation is headed, skip the joint statements and watch the meeting calendars. On June 9, India's Ambassador to the United States, Vinay Mohan Kwatra, conducted a rapid-fire series of engagements with American corporate and technology leaders that covered supply chains, AI, quantum computing, and counterterrorism — all in one sweep.

Kwatra met first with Chris Nicholas, the President and CEO of Walmart, to discuss the retail giant's expanding investments in India and its long-term supply chain strategy. Walmart's India footprint is substantial — it owns Flipkart, employs tens of thousands through its technology centers in Bangalore and Chennai, and has been deepening its sourcing from Indian manufacturers. The meeting, Kwatra noted on X, focused on "building resilient supply chains" — language that, in the current geopolitical climate, is diplomatic shorthand for diversifying away from China.

The more future-facing meeting came with Ylli Bajraktari, president and CEO of the Special Competitive Studies Project, a Washington think tank focused on the intersection of technology and national competitiveness. Bajraktari is scheduled to visit New Delhi for the India-US Forum, and the conversation with Kwatra centered on "the trajectory of advanced technologies including Quantum, and the future of AI, including Physical AI."

## Why Physical AI Matters

The phrase "Physical AI" is worth pausing on. In Silicon Valley, it refers to AI systems that interact with the real world — robotics, autonomous vehicles, smart manufacturing, drone navigation. NVIDIA's Jensen Huang has made Physical AI a central pillar of the company's strategy, and India's manufacturing ambitions, from semiconductors to defense, depend on mastering it.

For the Indian diaspora, the diplomatic interest in Physical AI signals that New Delhi sees a path beyond software services. India produces the engineers who design AI systems; the question has always been whether India can also build the factories, robots, and infrastructure that deploy them. A bilateral framework around Physical AI and quantum computing could accelerate that transition.

## The Supply Chain Angle

Kwatra's meeting with Walmart's Nicholas carries its own significance. India has become the world's fastest-growing alternative manufacturing base for American companies seeking supply chain resilience. Apple's iPhone assembly in Tamil Nadu, Google Pixel production in India, and Walmart's sourcing diversification all point in the same direction.

For Indian Americans working in supply chain management, procurement, and logistics at these companies, the diplomatic runway is real. Bilateral trade in goods and services exceeded $200 billion in 2025, and both governments are pushing to deepen technology transfer frameworks — particularly in semiconductors, where India's new fab projects at Dholera and Gujarat depend on American equipment and IP.

## The Counterterrorism Sidebar

Kwatra also met with Sebastian Gorka, a senior US counterterrorism official, to discuss global terrorism threats. The meeting underscores that India-US technology cooperation is not limited to commercial interests. Cybersecurity, surveillance technology, and intelligence-sharing frameworks all run through the same diplomatic channels.

## What It Means for the Corridor

For the hundreds of thousands of Indian tech professionals living in the United States, these meetings are not abstract. A stronger India-US technology corridor means more cross-border roles, more R&D centers in Indian cities, and a more predictable regulatory environment for NRIs who split their professional lives between both countries.

The India-US Forum, where Bajraktari is heading next, will test whether this week's meetings translate into concrete frameworks. But the direction is clear: India's ambassador is not just managing a relationship — he is negotiating a technology partnership that will shape where Indian engineers work, what they build, and how their home country fits into the global AI supply chain."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-06-30 05:00 PT run. 3 articles."""

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


# ────────────────────────────────────────────────────────────────────
# ARTICLE 1: India joins 35-nation Pax Silica pact
# Beat: Semiconductor Geopolitics / Global Tech with Diaspora Angle
# ────────────────────────────────────────────────────────────────────

art1_body = """\
When 35 nations endorsed a joint statement on AI supply chains at the second Pax Silica Summit in Washington last week, India was at the table — not as an observer, but as a country that increasingly considers semiconductor sovereignty a matter of national strategy.

The summit, hosted by the US State Department on June 26, produced the Joint Statement on AI Opportunity: a framework committing signatories to build trusted, resilient supply chains for the chips, critical minerals, and compute infrastructure that underpin artificial intelligence. India's delegation, led by S. Krishnan, Secretary of the Ministry of Electronics and Information Technology (MeitY), held bilateral discussions with US officials and industry leaders on the summit's sidelines.

"The opportunity before the United States and India extends from chips to neural networks," India's Ambassador to the US, Vinay Kwatra, said at a roundtable co-hosted by the Indian Embassy and the US-India Strategic Partnership Forum (USISPF). "India's mission-based approach across semiconductors, AI, and quantum technologies, combined with America's innovation ecosystem, creates enormous potential for collaboration."

## More Than a Handshake

The diplomatic language papers over some hard economic facts. India's semiconductor industry is still embryonic — the country's first modern fab, Tata Electronics' Dholera facility, is years from volume production. Yet India has approved 12 semiconductor projects under the India Semiconductor Mission, representing a pipeline of nearly ₹1.64 lakh crore (roughly $19.5 billion). Its second-phase Semiconductor Mission 2.0 aims to build out chip fabrication, packaging, design capabilities, and equipment manufacturing.

On the compute side, the IndiaAI Mission has assembled a shared national facility with more than 45,000 GPUs — a resource pool for AI startups, universities, and indigenous foundation models like those being developed by Sarvam AI and Krutrim.

Nine new countries and the European Union joined the Pax Silica initiative on the summit's sidelines, including Germany, the Netherlands, and Argentina. The expanding roster reflects a global anxiety about supply-chain concentration: more than 90 percent of the world's advanced chips are fabricated in Taiwan and South Korea, a geographical bottleneck that makes policymakers and CEOs equally nervous.

## What the US Wants from India

Washington's interest is not philanthropic. As export controls tighten around China — with Taiwan and Malaysia both seizing smuggled Nvidia chips in recent weeks — the US needs alternative partners who can absorb technology transfer without leaking it eastward. India, with its English-speaking engineering workforce, democratic governance, and growing electronics manufacturing base (now the country's third-largest export sector at approximately ₹13 lakh crore), fits the brief.

"India is positioning itself as a trusted and resilient partner in the global technology supply chain," Krishnan said. "Our electronics manufacturing ecosystem has expanded dramatically, semiconductor fabrication is now becoming a reality, and the next phase of our Semiconductor Mission will build on this momentum."

USISPF President Mukesh Aghi was blunter: "Microchips and critical minerals have become the elixir of the modern economy."

## The NRI Calculus

For the estimated 4.4 million Indian Americans, the deepening US-India chip alliance carries career and investment implications in both directions.

In the US, Indian engineers already constitute a significant share of the semiconductor workforce at companies like Intel, Qualcomm, Broadcom, and NVIDIA. Stronger bilateral frameworks could expand that pipeline — more exchange programs, easier visa pathways for chip-sector workers, and joint R&D ventures that create roles on both sides of the Pacific.

In India, the semiconductor buildout is creating an entirely new job category. The government estimates the industry will need 85,000 skilled semiconductor professionals by 2027. For NRI engineers weighing a return, or for diaspora investors eyeing the next infrastructure play, India's chip ambitions are starting to look like more than a PowerPoint presentation.

The Pax Silica pact does not guarantee any of this. International frameworks rarely do. But it moves India from the periphery of the global chip conversation — where it has lingered for decades — closer to the centre. Whether it stays there depends less on summits and more on whether Dholera's clean rooms actually produce working silicon.
"""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "India Just Signed a 35-Nation Pact to Secure AI's Silicon Supply Chain. Here's What It Actually Means.",
    "subheadline": "At the second Pax Silica Summit in Washington, India committed to building trusted chip and critical-mineral pipelines alongside the US, EU, and 32 other countries — a move that could reshape careers and investments for the diaspora.",
    "slug": make_slug("india-pax-silica-35-nation-chip-ai-supply-chain"),
    "category": "technology",
    "vertical": "semiconductor-geopolitics",
    "diaspora_angle": "Indian-American chip engineers at Intel, Qualcomm, and NVIDIA stand to benefit from deeper US-India semiconductor cooperation, while India's 85,000-job chip workforce target creates new return-to-India career paths and investment opportunities for NRIs.",
    "tags": ["semiconductors", "india-us-relations", "ai-supply-chain", "pax-silica", "chip-manufacturing"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "The Bridge Chronicle", "url": "https://www.thebridgechronicle.com/news/nation/india-joins-us-led-ai-supply-chain-pact-34-nations"},
        {"name": "IANS", "url": "https://ianslive.in/"},
        {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/"},
        {"name": "The Indian EYE", "url": "https://theindianeye.com/"}
    ]),
    "score_total": 72,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/45/V11-wafer-dc328.jpg/1280px-V11-wafer-dc328.jpg",
    "image_caption": "A semiconductor wafer — the silicon foundation of the AI supply chain India is now helping to secure",
    "image_attribution": "Wikimedia Commons",
    "body": art1_body.strip()
}


# ────────────────────────────────────────────────────────────────────
# ARTICLE 2: Nikesh Arora / Palo Alto Networks record quarter
# Beat: Indian-Origin Tech Leaders / Cybersecurity
# ────────────────────────────────────────────────────────────────────

art2_body = """\
When Palo Alto Networks stock cratered below $148 earlier this year on fears that AI would devour the cybersecurity industry, Nikesh Arora did something few CEOs bother to do: he bought $10 million of his own company's shares on the open market.

On Monday, those shares were worth roughly $22.5 million. Palo Alto's stock surged 9.1 percent to $332 — touching its all-time high — as investors digested a fiscal third-quarter report that demolished nearly every estimate Wall Street had put forward.

## The Numbers

Revenue hit $3 billion for the quarter, up 31 percent year-over-year and ahead of the $2.94 billion consensus. Earnings per share came in at $0.85, beating estimates by $0.06. Next-Generation Security annual recurring revenue — the metric Arora has trained analysts to watch — reached $8.13 billion, up 60 percent. Adjusted free cash flow surged 57 percent to $910 million.

The numbers behind the numbers are more telling. XSIAM, the company's AI-powered security operations platform, surpassed $600 million in ARR, doubling year-over-year. Prisma AIRS, its AI application security offering, tripled its customer base sequentially to over 300. And next-generation firewall bookings jumped nearly 40 percent — the strongest hardware quarter in a decade at a company that has been aggressively pivoting to software.

## The Platformization Bet

The engine underneath all of this is what Arora calls "platformization" — convincing enterprises to consolidate their patchwork of security tools onto Palo Alto's unified platform. The company added 110 platformized customers in Q3 alone, bringing the total to roughly 2,280.

"The market was a bit skeptical," Arora said in a post-earnings interview, "but we have steadily proven over the last two years that customers who platformize are spending more money with us and have a very high retention rate."

That skepticism was not unfounded. When Anthropic disclosed Claude Mythos — a model it deemed too powerful to release due to its cybersecurity capabilities — the entire security sector sold off. Investors feared that if AI models could find and exploit vulnerabilities autonomously, traditional security vendors would become obsolete. Palo Alto's stock plunged, and Arora stepped in with his personal chequebook.

His counter-argument is simple: AI makes attacks faster and cheaper, which makes companies more desperate for protection, not less. Around 1,000 companies have reached out to Palo Alto in the past two months alone, Arora said, "to talk about their cyber posture, cyber infrastructure, and how we can help them get through this period of living the future with frontier AI models being cyber-capable."

## The Man from Ghaziabad

Arora's trajectory — IIT Varanasi to Boston Consulting Group, then Google's chief business officer, then SoftBank's president, now a $248 billion cybersecurity empire — is the kind of CV that Indian parents dream about and career counselors find implausible.

But the more consequential fact for the diaspora is what Arora's success means for the cybersecurity industry's hiring pipeline. Palo Alto Networks employs thousands of engineers in India and Israel. As AI-driven threats proliferate, demand for security professionals is rising faster than supply. Indian engineers — both in the US and in India — are disproportionately well-positioned to fill those roles.

Arora also made headlines last week as part of the consortium — alongside Satya Nadella, Sundar Pichai, and other tech executives — that acquired the London Spirit cricket team in The Hundred league for £145 million. When you run a company worth a quarter-trillion dollars and still have bandwidth for cricket investments, the playbook is clearly working.

## What Zacks and the Street Think

Analysts have Palo Alto outperforming the broader security sector by 14 percentage points over six months. Revenue is expected to keep growing in Q4 as the CyberArk and Chronosphere integrations mature and platformization gains compound. The stock trades at a P/E ratio of 272, which is either a sign of irrational exuberance or a reasonable price for a company growing revenue at 31 percent with near-40 percent free cash flow margins. Probably a bit of both.

For NRI investors who have tracked Indian-origin CEOs as a portfolio strategy — Nadella at Microsoft, Pichai at Alphabet, Krishna at IBM — Arora's Palo Alto Networks now offers the clearest case study in cybersecurity. The question is no longer whether platformization works. It is whether anything can slow it down.
"""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "Arora's Palo Alto Networks Just Hit a $3 Billion Quarter. Then Its Stock Hit an All-Time High.",
    "subheadline": "The Indian-origin CEO bought $10 million of his own stock when it crashed on AI fears. It has since more than doubled. Palo Alto's record Q3 shows why cybersecurity is the AI boom's biggest beneficiary.",
    "slug": make_slug("nikesh-arora-palo-alto-3-billion-quarter-all-time-high"),
    "category": "technology",
    "vertical": "cybersecurity",
    "diaspora_angle": "Arora, an IIT Varanasi alumnus, leads the most valuable cybersecurity company in the world — a sector where Indian engineers are in surging demand. NRI investors tracking Indian-origin CEO-led stocks now have a cybersecurity entry point alongside Nadella's Microsoft and Pichai's Alphabet.",
    "tags": ["nikesh-arora", "palo-alto-networks", "cybersecurity", "indian-ceo", "ai-security", "earnings"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "The Wall Street Journal", "url": "https://www.wsj.com/business/earnings/palo-alto-networks-revenue-rises-as-customers-beef-up-cyber-defenses-2c72e24e"},
        {"name": "MarketBeat", "url": "https://www.marketbeat.com/stocks/NASDAQ/PANW/earnings/"},
        {"name": "Morningstar", "url": "https://www.morningstar.com/news/marketwatch/20260602346/palo-alto-networks-ceo-sends-a-message-through-his-10-million-stock-purchase"},
        {"name": "Zacks Investment Research", "url": "https://www.zacks.com/"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/e/ea/Nikesh_Arora_TechCrunch_Disrupt_2015.jpg",
    "image_caption": "Nikesh Arora, Chairman and CEO of Palo Alto Networks, at a technology conference",
    "image_attribution": "Wikimedia Commons",
    "body": art2_body.strip()
}


# ────────────────────────────────────────────────────────────────────
# ARTICLE 3: Amazon $48B India investment
# Beat: Global Tech with Diaspora Angle
# ────────────────────────────────────────────────────────────────────

art3_body = """\
Amazon CEO Andy Jassy flew to New Delhi last week and did something that usually takes a boardroom slideshow and three rounds of negotiations: he told Prime Minister Narendra Modi that Amazon would invest $48 billion in India over the next five years. Then he posted about it on X, as one does after committing the GDP of a small country to data centres in Mumbai and Hyderabad.

The number is staggering not because of the headline figure — tech CEOs have been tossing around billions in India pledges like confetti at a Holi party — but because of how quickly it escalated. In December 2025, Amazon announced $35 billion for India through 2030. Six months later, Jassy tacked on another $13 billion, mostly earmarked for AI and cloud infrastructure. Total: $48 billion between 2026 and 2030, with $21 billion specifically dedicated to expanding Amazon Web Services capacity.

## The Hyperscaler Land Rush

Amazon is not alone. Microsoft committed $17.5 billion to Indian cloud and AI infrastructure in December — its largest-ever investment in Asia. Google pledged $15 billion in October for data centres in southern India. Add them up, and the three biggest hyperscalers have earmarked roughly $80 billion for Indian compute capacity in the space of eight months.

Why? India's 1.4 billion people are ravenous consumers of data, AI chatbots, and cloud-hosted applications. AWS already sells AI and machine learning tools to Indian enterprises and government entities. The demand, by all accounts, is outrunning supply.

"India is becoming such a significant cloud and AI hub around the world," Jassy said, "and we have so much demand here that we're continuing to invest in the country on the cloud side and the AI side as well."

The Indian government, for its part, has sweetened the pot. A new policy offers long-term tax breaks to hyperscalers that use India-based data centres for global operations — a direct play to make the country a regional compute hub, not just a domestic one.

## Beyond Data Centres

Amazon's India bet extends well past server racks. The company plans to launch more than 20 fulfilment centres and over 100 delivery stations across India this year, with a deliberate push into smaller cities. It is also charging into quick commerce — the 10-to-30-minute delivery market that Blinkit, Zepto, and Swiggy Instamart have turned into India's hottest consumer battleground.

Jassy outlined several targets through 2030: supporting 3.8 million jobs (up from 2.8 million in 2024), enabling $80 billion in cumulative e-commerce exports, extending AI tools to 15 million small businesses, and providing AI education to 4 million government school students. Amazon's cumulative investment in India from 2010 to 2030 will exceed $88 billion.

"Prime Minister's vision over the last 12 years is just remarkable," Jassy said after the meeting. "And when I have the good fortune to spend time with him, he has so many ideas for how to continue to make the country better on every dimension."

## The Diaspora Calculation

For Indian Americans, the hyperscaler deluge in India represents at least three things.

First, jobs. AWS's Indian operations already employ tens of thousands of engineers, and a $21 billion cloud buildout means that number will grow substantially. For NRI professionals in cloud computing, DevOps, and AI — fields where Indians in the US already dominate — the expansion creates career opportunities that stretch across both countries.

Second, investment exposure. Amazon stock gives NRI investors direct participation in India's cloud growth story without the currency risk and regulatory complexity of buying Indian equities. Every dollar AWS makes in India flows through the same AMZN share price.

Third, and most practically, the infrastructure itself. A more capable AWS region in Mumbai and Hyderabad means faster, cheaper, and more reliable cloud services for Indian startups — many of which are founded by diaspora entrepreneurs or serve diaspora customers.

Walmart-backed Flipkart, Amazon's chief rival, announced its own aggressive quick-commerce expansion on the same day. The competition ensures that neither company can coast. For India's digital economy, and for the NRIs watching it from afar, that is probably the best possible outcome.
"""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "Amazon Just Bet $48 Billion on India. Jassy Flew to Delhi to Tell Modi Personally.",
    "subheadline": "The largest tech investment commitment to India — ever — includes $21 billion for AI and cloud infrastructure alone. Amazon, Microsoft, and Google have collectively earmarked $80 billion for Indian compute capacity in eight months.",
    "slug": make_slug("amazon-48-billion-india-jassy-modi-aws-ai-cloud"),
    "category": "technology",
    "vertical": "big-tech-india",
    "diaspora_angle": "AWS's $21 billion cloud expansion creates thousands of new cloud/AI roles for Indian-American engineers, while Amazon stock offers NRI investors direct exposure to India's booming digital economy without the complexity of Indian equities.",
    "tags": ["amazon", "aws", "india-investment", "andy-jassy", "ai-infrastructure", "cloud-computing", "modi"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "The Wall Street Journal", "url": "https://www.wsj.com/business/amazon-to-invest-additional-13-billion-in-india-by-2030-f81e0c20"},
        {"name": "Barron's", "url": "https://www.barrons.com/articles/amazon-stock-india-ai-data-centers-d49f343d"},
        {"name": "Press Trust of India", "url": "https://nordot.app/"},
        {"name": "CNBC TV18", "url": "https://www.cnbctv18.com/"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/0/07/Andy_Jassy.jpg",
    "image_caption": "Amazon CEO Andy Jassy, who met Prime Minister Narendra Modi in New Delhi to announce the $48 billion investment",
    "image_attribution": "Wikimedia Commons",
    "body": art3_body.strip()
}


# ────────────────────────────────────────────────────────────────────
# Insert all
# ────────────────────────────────────────────────────────────────────

articles = [art1, art2, art3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

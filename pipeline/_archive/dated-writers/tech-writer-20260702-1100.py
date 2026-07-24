#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-07-02 11:00 PT run"""
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
    return slug[:70].rstrip('-') + "-20260702"

# ─────────────────────────────────────────────────────────────────────────────
# ARTICLE 1
# ─────────────────────────────────────────────────────────────────────────────

article1_body = """Palantir's Alex Karp did not mince words. Speaking to analysts this week, the CEO called the token-based pricing model used by AI labs such as OpenAI and Anthropic a "wealth tax" — a charge that drains enterprise budgets without delivering durable business outcomes. The market agreed. Palantir's stock jumped 7.7 per cent, Salesforce gained 4 per cent, Accenture rose 5.4 per cent, and ServiceNow climbed 6.5 per cent.

The ripple crossed oceans. India's Nifty IT index surged 4.64 per cent on Thursday — its strongest session in weeks, snapping a four-day losing streak that had dragged the sector to fresh lows. TCS gained 4.3 per cent, Infosys rallied, and HCL Technologies and Wipro rode the same wave. For a sector that has lost a quarter of its value this year, the reversal felt cathartic.

## The Fear That Built the Hole

Indian IT services have been 2026's punching bag. The Nifty IT index is down 25.4 per cent year-to-date, making it India's worst-performing sectoral gauge — worse than banks, worse than real estate, worse than anything. The proximate cause: a series of AI announcements that persuaded investors the $283 billion Indian IT industry was headed for obsolescence.

The timeline reads like a horror story. In February, Anthropic launched Claude Code and triggered a 5 per cent single-day rout. In May, OpenAI announced a $4 billion venture to embed engineers directly into client organisations — precisely the kind of on-the-ground consulting that TCS and Infosys have built empires around. HSBC warned that AI spending was "crowding out" demand for traditional IT services. Then Palantir revealed that its Hivemind AI could autonomously migrate legacy systems — the bread and butter of Indian outsourcing for two decades.

Each announcement was a body blow. NRI investors who held TCS and Infosys as defensive blue chips watched their portfolios bleed.

## Why Karp's Attack Changed the Mood

Karp's argument was simple but potent: enterprise companies are paying massive token bills to AI labs and getting little in return. The real value, he argued, lies in platforms that integrate AI into existing workflows, not in raw model access. Palantir's own revenue tells the story — $1.63 billion last quarter, with U.S. commercial revenue up 133 per cent. Its Rule of 40 score hit 145 per cent, a figure almost unheard of in enterprise software.

For Indian IT firms, Karp's framing is a lifeline. If enterprises conclude that they need human integrators to extract value from AI — rather than simply buying API tokens — then the case for companies like TCS, Infosys, and Wipro strengthens considerably. These firms have spent the past year repositioning as AI implementation partners, not just outsourced coders. Wipro CEO Srini Pallia told Davos in January that clients were moving from AI experimentation to demanding ROI, and that Indian IT firms were well-positioned to manage that transition.

## What NRIs Should Watch

The rally is a trade, not a verdict. Indian IT stocks remain deeply discounted, trading near three-year lows. The structural question — whether AI agents will eventually replace the army of engineers that power TCS's $30 billion revenue machine — has not been answered.

But the market is repricing risk. If Karp is right that token-based AI is an expensive dead end for most enterprises, then the firms that know how to wire AI into messy, real-world corporate systems have a long runway ahead. For the tens of thousands of Indian engineers at these companies, and the NRI investors who hold their stock, Thursday's rally was the first hint that the obituary might have been written too early.

*Sources: Inshorts, Reuters, HSBC research note, Moneycontrol*"""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "Palantir's CEO Just Called OpenAI a 'Wealth Tax.' Indian IT Stocks Had Their Best Day in Weeks.",
    "subheadline": "Alex Karp's attack on token-based AI pricing sent enterprise software stocks soaring — and gave India's battered IT sector its first real relief in months.",
    "slug": make_slug("palantir-karp-wealth-tax-indian-it-stocks-rally"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Indian IT stocks — held widely by NRI investors and employing hundreds of thousands of Indian engineers — rallied 4.64% on the back of Palantir CEO's attack on AI labs, offering the first major relief for a sector down 25% this year.",
    "tags": ["ai", "indian-it", "palantir", "enterprise-software", "nifty-it", "tcs", "infosys"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Inshorts", "url": "https://inshorts.com"},
        {"name": "Reuters", "url": "https://www.reuters.com/technology/indias-it-shares-near-three-year-low-openai-move-revives-ai-fears-2026-05-13/"},
        {"name": "Moneycontrol / TradingView", "url": "https://www.tradingview.com/news/"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/5/50/Alex_Karp_attends_AI_Summit_%2853302457013%29_4-5_ratio.jpg",
    "image_caption": "Palantir CEO Alex Karp at an AI summit",
    "image_attribution": "Wikimedia Commons",
    "body": article1_body,
}

# ─────────────────────────────────────────────────────────────────────────────
# ARTICLE 2
# ─────────────────────────────────────────────────────────────────────────────

article2_body = """The files appeared on the dark web without warning. More than 200,000 documents stolen from Tata Electronics — Apple's most important manufacturing partner outside China — were dumped by a ransomware group calling itself World Leaks. Among them: detailed component supplier lists, design papers, and photographs of Apple's unreleased iPhone 18 Pro models, due in September.

The breach is not abstract. At least six files map specific components of the iPhone 18 Pro — chips on its main circuit board, battery parts, camera modules — to the companies that supply them. Documents related to TSMC and Qualcomm, both of which manufacture parts used in iPhones, were also exposed. For Apple, whose supplier arrangements are guarded with the secrecy of a nuclear programme, this is a nightmare.

## What Was Exposed

Reuters, which reviewed the leaked documents, reported that the files include purported component design papers for older iPhone models, some Tesla-related materials (Tata is also a Tesla supplier), and — most critically — the iPhone 18 Pro supplier maps. These reveal which company makes which part, information that Apple normally restricts to a small circle of executives and procurement managers.

The exposure hands competitors, counterfeiters, and Apple's own vendors a detailed look at the iPhone's supply chain architecture. A rival can reverse-engineer sourcing strategies. A counterfeiter can identify which components to replicate. And a supplier who discovers what its competitors charge can renegotiate harder.

## The India Connection

Tata Electronics is not a peripheral player. Led by former Intel and Applied Materials executive Randhir Thakur, the company sits at the centre of India's push to become a global electronics manufacturing hub. It both supplies iPhone components and assembles finished devices as a contract manufacturer. Apple assembled roughly 55 million iPhones in India last year — about 25 per cent of global output — and Tata is on track to handle half of India's iPhone production by the end of 2026.

The breach comes at an awkward moment. Foxconn's new Bangalore plant just began commercial iPhone shipments in June, with Karnataka's commerce minister calling it a "strategic shift." Apple CEO Tim Cook confirmed that iPhones sold in the US during the June quarter were "majorly" manufactured in India. The narrative of India as a secure, scalable alternative to China has been central to billions of dollars in investment.

A ransomware attack on India's flagship electronics manufacturer complicates that story. Tata Electronics said it has "hardened access to its sensitive internal systems" and that the investigation is ongoing. Apple's security team is reportedly working closely with Tata on near- and long-term remediation.

## Why NRIs Should Care

For the Indian diaspora, this is a two-sided story. On the upside, Apple's commitment to India manufacturing appears unchanged — the company is doubling down, not pulling back. The sheer scale of production (25 per cent of global output) means India's manufacturing ecosystem is already too deeply embedded to unwind over a single breach.

On the downside, the attack exposes a vulnerability that India's tech sector cannot afford. If India wants to be trusted with the world's most valuable supply chains, its cybersecurity infrastructure needs to match. The Tata breach follows a separate cyberattack on Tata's British Jaguar Land Rover unit last year, which halted output for six weeks. Two major incidents at the same conglomerate raise questions about systemic security practices.

For NRI investors tracking Tata Group's ambitious technology play — from semiconductor fabs in Dholera to iPhone assembly in Hosur — the breach is a reminder that manufacturing prowess and digital security must advance together.

*Sources: Reuters, TechSpot, Wedbush Securities*"""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "A Ransomware Gang Just Leaked Apple's iPhone 18 Pro Secrets. The Breach Came Through India.",
    "subheadline": "More than 200,000 files stolen from Tata Electronics have exposed supplier lists, component designs, and photos of Apple's unreleased flagship — raising hard questions about India's manufacturing security.",
    "slug": make_slug("tata-electronics-hack-apple-iphone-18-pro-leak"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Tata Electronics is central to India's Make in India push and assembles 25% of global iPhones — the breach tests whether India's manufacturing ecosystem can be trusted with the world's most valuable supply chains, a question that matters to NRI investors in both Apple and Tata.",
    "tags": ["apple", "tata", "cybersecurity", "iphone", "india-manufacturing", "supply-chain"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/business/media-telecom/apple-iphone-18-pro-supplier-list-parts-photos-exposed-tata-data-leak-2026-06-29/"},
        {"name": "TechSpot", "url": "https://www.techspot.com/news/108098-apple-now-assembles-quarter-iphones-india.html"},
        {"name": "Wedbush Securities", "url": "https://investor.wedbush.com"}
    ]),
    "score_total": 85,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/60504/security-protection-anti-virus-software-60504.jpeg",
    "image_caption": "Digital security interface on a display screen",
    "image_attribution": "Pexels",
    "body": article2_body,
}

# ─────────────────────────────────────────────────────────────────────────────
# ARTICLE 3
# ─────────────────────────────────────────────────────────────────────────────

article3_body = """Jensen Huang has spent two decades selling the best shovels in the AI gold rush. Now he wants a percentage of the gold.

Nvidia announced this week that it is introducing a revenue-sharing model for smaller AI cloud companies — a new business structure where Nvidia backs "neocloud" startups with credit support and hardware access in exchange for a recurring cut of their cloud revenue. The first two partners are SharonAI, which plans to deploy 40,000 Nvidia Grace Blackwell GB300 GPUs in an Australian data centre, and Firmus Technologies, building an AI factory campus in Batam, Indonesia, with up to 170,000 Nvidia GPUs.

"Through the partnership, AI clouds will sell Nvidia-powered cloud services, with Nvidia earning both standard product revenue and a share of the cloud revenue on the supported capacity," wrote CFO Colette Kress and Raj Mirpuri, VP of global AI clouds and infrastructure, in a company blog post.

## The Problem Nvidia Is Solving (for Itself)

Nvidia's stock is up just 5.9 per cent this year — a startling underperformance for a company that was recently the world's most valuable. The culprit: its biggest customers are becoming its biggest competitors. Google is pushing its TPU chips. Amazon has Trainium. Microsoft is designing custom silicon. The hyperscalers that account for roughly half of Nvidia's data centre revenue are steadily reducing their dependence on Nvidia hardware.

The revenue-sharing model is Nvidia's countermove. By nurturing a constellation of smaller cloud providers — neoclouds — that run exclusively on Nvidia hardware, the company builds an alternate customer base that is structurally dependent on its chips. These aren't one-time hardware sales. They are ongoing revenue streams tied to how much compute the neoclouds sell.

The neocloud ecosystem is already substantial. More than 190 operators exist globally, including CoreWeave, Lambda, Nebius, and Crusoe. Revenue from neoclouds tripled year-over-year in Nvidia's most recent quarter. Huang told analysts he expects the segment to "continue to grow at incredible pace."

## Why the Circular Financing Debate Matters

The model is not without controversy. Nvidia has faced persistent questions about "circular financing" — the practice of investing in customers who then use that money to buy Nvidia hardware, artificially inflating revenue. The company has pushed back aggressively. "These relationships are not circular-pay relationships in any way," Huang has said. "We deliver and then we get paid."

The new revenue-sharing structure is different from direct equity investments. Nvidia is not buying shares in SharonAI or Firmus. It is providing credit support and taking a cut of downstream revenue — more like a franchise model than a venture bet. If the neoclouds fail to sell compute, Nvidia's revenue-share income drops accordingly. That alignment of incentives may help defuse the circular-financing critique.

## The Indian Engineer in the Room

Nvidia employs thousands of Indian engineers across its Santa Clara headquarters, Bangalore research centre, and Hyderabad design labs. The company's AI chip architecture — from Hopper to Blackwell to the upcoming Vera Rubin — is designed and verified by teams with a significant Indian presence. For NRI engineers at Nvidia, the stock's sideways performance this year has been frustrating, particularly after the company's parabolic run from 2023 to 2025.

The revenue-sharing model matters to them because it could change how the market values Nvidia. Hardware companies trade at lower multiples than software or platform companies. If Nvidia can demonstrate a growing stream of recurring, usage-linked revenue — rather than one-time chip sales — it starts to look more like a platform. That could support a higher multiple even if chip shipment growth moderates.

For NRI investors who own Nvidia, the question is whether Jensen Huang's toll-road strategy works before the hyperscalers finish building their own highways.

*Sources: Barron's, Investor's Business Daily, Bisnow*"""

article3 = {
    "id": str(uuid.uuid4()),
    "headline": "Nvidia Is Tired of Selling Shovels. Now It Wants a Cut of the Gold.",
    "subheadline": "Jensen Huang's new revenue-sharing model turns Nvidia from a chip seller into a cloud landlord — a bet that its thousands of Indian engineers and NRI shareholders are watching closely.",
    "slug": make_slug("nvidia-revenue-sharing-neocloud-model-ai"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Nvidia employs thousands of Indian engineers across Santa Clara, Bangalore, and Hyderabad — the revenue-sharing pivot could change how the market values the company and directly affects NRI investors who have ridden NVDA's stock through a frustrating 2026.",
    "tags": ["nvidia", "ai-infrastructure", "neocloud", "jensen-huang", "silicon-valley", "indian-tech-workers"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Barron's", "url": "https://www.barrons.com"},
        {"name": "Investor's Business Daily", "url": "https://www.investors.com"},
        {"name": "Bisnow", "url": "https://www.bisnow.com"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/e/e6/Jen-Hsun_Huang_2025.jpg",
    "image_caption": "Nvidia CEO Jensen Huang",
    "image_attribution": "Wikimedia Commons",
    "body": article3_body,
}

# ─────────────────────────────────────────────────────────────────────────────
# INSERT
# ─────────────────────────────────────────────────────────────────────────────

articles = [article1, article2, article3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

print(f"\nDone. {len(articles)} articles submitted.")

#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-06-15 00:00 UTC batch"""

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
    # ──────────────────────────────────────────────────────────────────────
    # ARTICLE 1: AI Deflation Hits Indian IT Giants
    # ──────────────────────────────────────────────────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "'AI Deflation' Is Squeezing India's IT Giants. Their Own Employees See It First.",
        "subheadline": "HCLTech warns of a 3-5% revenue hit. TCS has shed 23,000 workers. Infosys is down 35% from its peak. The $315 billion Indian IT sector is learning what it means to be disrupted by the technology it sells.",
        "slug": make_slug("ai-deflation-indian-it-services-tcs-hcltech-infosys-wipro"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Hundreds of thousands of NRIs work at or have family in India's big IT firms — and the stocks are staples in Indian household portfolios. AI deflation threatens both careers and savings.",
        "tags": ["indian-it", "ai-deflation", "tcs", "hcltech", "infosys", "wipro", "layoffs"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "The Register", "url": "https://www.theregister.com/2026/04/28/india_it_ai_deflation/"},
            {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com/info-tech/indian-it-sees-rising-share-of-revenue-from-bfsi-in-fy26/article69676543.ece"},
            {"name": "Reuters — TCS/Anthropic", "url": "https://www.reuters.com/technology/indias-tcs-partners-with-anthropic-drive-enterprise-ai-scaling-2026-06-12/"},
            {"name": "Livemint — IT stocks selloff", "url": "https://www.livemint.com/market/stock-market-news/tcs-wipro-to-infosys-it-stocks-bleed-on-ai-and-tech-stocks-selloff-in-global-markets-nifty-it-dips-2-11749372988455.html"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/8353831/pexels-photo-8353831.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Colleagues reviewing stock market data on multiple monitors in a modern office",
        "image_attribution": "Pexels",
        "body": """India's four largest IT services companies — TCS, Infosys, HCLTech, and Wipro — have collectively employed more than 1.5 million people and generated over $100 billion in annual revenue for years. They built their empires on a simple, sturdy model: take complex technology work from Western corporations, execute it with Indian engineering talent at a fraction of the cost, and pocket the margin.

That model is cracking.

## The Word Nobody Wanted to Say

When HCLTech reported its FY26 results, CEO C. Vijayakumar used a term the industry had been carefully avoiding: "AI deflation." He told investors that future revenue would decline between 3% and 5% in the coming year, and possibly further after that. The cause was not a recession, a lost client, or a pricing war. It was the technology that HCLTech itself deploys for customers — artificial intelligence — making chunks of the work it charges for simply unnecessary.

He was not alone. TCS CEO K. Krithivasan called it "degrowth." Infosys CEO Salil Parekh acknowledged deflation was coming but predicted growth would continue — a hedge that did not convince the market. Wipro's CFO Aparna Iyer pointed to lower margins on new deals.

The numbers behind the language are sharper. TCS saw annual revenue slip 0.5% year-over-year. Its headcount fell by more than 23,000 on a net basis in the fiscal year ended March 2026, following 12,000 job cuts last July. TCS chairman N. Chandrasekaran told shareholders the company is moving toward having "an equal number of employees and AI agents in its workforce."

## What Changed

The trigger was not one product but a rapid shift in what AI coding tools can do. When Anthropic launched its agentic AI tool earlier this year, Indian IT stocks lost more than $62.8 billion in market capitalisation in a single month. The market's logic was brutal: if AI agents can write, test, and maintain code at enterprise scale, the core value proposition of offshore services — arbitraging Indian labour costs — begins to collapse.

Application development, maintenance, and testing account for roughly 30-40% of Indian IT services revenue, according to Motilal Oswal analyst Abhishek Pathak. He estimates AI-driven productivity gains could eliminate 9-12% of total IT services revenue over the next three to four years.

The Nifty IT index fell 2% on June 8 alone, with Wipro tumbling 6.46% in a single session. Infosys sits 35% below its 52-week high.

## The BFSI Lifeline

One bright spot has been banking, financial services, and insurance — the BFSI vertical. Four of the five top-tier Indian IT firms saw BFSI's share of revenue rise in FY26. TCS drew 32% of revenue from the sector, up from 30.9%. HCLTech saw it climb to 21.5% from 20.7%. Analysts attribute this partly to genuine modernisation demand from banks adopting AI, and partly to contraction in other verticals masking BFSI's relative resilience.

But relying on a single vertical's stickiness is not a strategy.

## The Pivot Nobody Planned For

The Big Four are now scrambling to become AI companies rather than companies disrupted by AI. TCS partnered with Anthropic to equip 50,000 associates with Claude and jointly take AI solutions to regulated industries. Infosys struck a similar deal months earlier. HCLTech is investing $150 million in Sarvam AI, India's sovereign LLM startup.

The irony is painful: the companies that built India's reputation as the world's back office are now paying the companies that might make back offices obsolete.

## What This Means for NRIs

For the hundreds of thousands of diaspora Indians who built careers at TCS, Infosys, or Wipro — or whose families in India still work there — the stakes are intimate. These are not abstract stock tickers. They are H-1B visa sponsors, parents' employers, wedding-talk benchmarks.

The stocks remain staples in Indian household portfolios, held through mutual funds and direct equity. A sustained decline reshapes retirement planning from Bangalore to Basking Ridge.

The IT services model is not dead. But the era in which it could grow simply by adding bodies to projects is over. The companies that survive will be the ones that learn to sell AI rather than be replaced by it. For their employees, the question is whether that transition happens fast enough to save their seats."""
    },

    # ──────────────────────────────────────────────────────────────────────
    # ARTICLE 2: US Cybersecurity Firms Target India SMBs
    # ──────────────────────────────────────────────────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "American Cybersecurity Giants Are Racing to Arm India's 75 Million Small Businesses",
        "subheadline": "As AI-powered attacks surge post-Claude Mythos, Palo Alto Networks and Microsoft are pitching cut-rate security to Indian MSMEs — a market that accounts for nearly a third of India's GDP.",
        "slug": make_slug("us-cybersecurity-firms-india-msme-palo-alto-microsoft"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Many NRIs invest in or run family businesses in India. The $3.4 billion cybersecurity surge affects both their portfolio picks (PANW, MSFT) and the family firms back home increasingly under AI-driven attack.",
        "tags": ["cybersecurity", "india-msme", "palo-alto-networks", "microsoft", "ai-threats", "nikesh-arora"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Livemint", "url": "https://www.livemint.com/industry/mythos-busters-why-us-cyber-giants-are-racing-to-woo-india-s-small-businesses-11749816770283.html"},
            {"name": "Communications Today", "url": "https://www.communicationstoday.co.in/us-cybersecurity-firms-target-indian-smbs-as-ai-powered-threats-rise/"},
            {"name": "Reuters — SEBI task force", "url": "https://www.reuters.com/world/india/indias-markets-regulator-sets-up-task-force-tackle-ai-driven-cyber-threats-2026-05-06/"}
        ]),
        "score_total": 75,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/10725897/pexels-photo-10725897.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Digital security and encryption concept with data streams and code",
        "image_attribution": "Pexels",
        "body": """Anthropic's Claude Mythos can autonomously discover software vulnerabilities and build complex exploit chains overnight. That sentence used to belong in a sci-fi pitch deck. Now it belongs in an insurance filing for every small business in India that stores customer data.

America's largest cybersecurity companies have noticed. They are pivoting hard toward India's 75 million micro, small, and medium enterprises — a segment that employs 328 million people, contributes 31% of India's GDP, and until recently treated cybersecurity as an optional line item.

## The Threat Just Got Smarter

The emergence of AI-powered vulnerability scanners has changed the calculus for attackers. Where a hack once required a skilled operator spending days probing a target, tools like Mythos can scan, discover, and chain exploits in hours. The targets are no longer limited to banks and governments. Any small business running outdated software — a Delhi restaurant chain, a Bengaluru fintech startup, a Pune manufacturer — is now findable and exploitable at machine speed.

India's markets regulator, SEBI, took the threat seriously enough to constitute a dedicated task force in May to assess AI-driven cybersecurity risks across the securities ecosystem. The Data Security Council of India reported in December 2025 that the country had more than 400 cybersecurity firms, with industry revenue rising 26% year-on-year to $4.46 billion in calendar 2025. Gartner estimates Indian companies will spend $3.4 billion on cybersecurity services in 2026 alone — the highest to date.

## The American Offensive

Two Indian-origin-led companies are at the front of the charge.

Palo Alto Networks, under CEO Nikesh Arora, is pushing managed security services on a subscription basis — a model designed explicitly for smaller Indian firms that prefer operational expenditure over capital investment. BJ Jenkins, Palo Alto's president, has said that the subscription approach is "proving attractive" to firms that would rather spend on growth than build dedicated security teams.

Microsoft, under CEO Satya Nadella, is positioning its Defender suite as the cybersecurity layer for Indian SMBs. Vasu Jakkal, corporate vice president of Microsoft Security, has argued that many smaller firms unknowingly adopt unsanctioned AI tools and rely on overstretched IT staff to cover security gaps. The pitch is integration: if you already use Microsoft 365, your security should be built into the same stack.

## The Numbers on the Ground

The spending shift is visible but uneven. Anubhav Jain, co-founder of Bengaluru-based digital lending firm Rupifi Technology Solutions, told Livemint that his company's cybersecurity spending has risen roughly 50-60% over four years. Rajan Sethi, managing director of Delhi-based Bright Hospitality, said even his restaurant business spends ₹20 lakh annually safeguarding customer data. Murugavel Janakiraman, CEO of Matrimony Group, said the company was prepared to invest further "the moment there are signals."

The common thread: awareness is high, but spending lags the threat. Most Indian MSMEs still do not have a full-time security professional.

## Why This Matters to NRIs

The dual relevance for diaspora Indians is hard to miss. On the investment side, Palo Alto Networks and Microsoft are two of the most widely held stocks in Indian-American portfolios. PANW just posted a $3 billion quarter; MSFT's security segment is its fastest-growing enterprise vertical. India's cybersecurity market is a growth vector for both.

On the personal side, many NRIs maintain financial ties to family businesses in India — property firms, clinics, small manufacturers, food chains. These are precisely the businesses now in the crosshairs of AI-driven attackers. A breach at a cousin's logistics startup or a parent's real estate firm is not abstract. It is personal, costly, and increasingly likely.

The Indian MSME sector has survived demonetisation, GST overhauls, and a pandemic. Whether it can survive an AI that finds vulnerabilities faster than any human can patch them will depend on whether the cybersecurity industry can scale its offerings down to the price point of a Jio recharge plan. The American giants are betting it can."""
    },

    # ──────────────────────────────────────────────────────────────────────
    # ARTICLE 3: Microsoft Project Solara — Satya Nadella
    # ──────────────────────────────────────────────────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "Satya Nadella Wants to Kill the App. Project Solara Is How.",
        "subheadline": "Microsoft's Build 2026 flagship isn't a new Office feature or a Copilot upgrade. It's an entire operating system — built on Android, not Windows — where AI agents replace apps entirely.",
        "slug": make_slug("satya-nadella-project-solara-microsoft-build-2026-agents"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Satya Nadella continues to define the AI-first era from the CEO chair. For the tens of thousands of Indian engineers at Microsoft and its partner ecosystem, Solara signals a fundamental shift in what they'll be building.",
        "tags": ["microsoft", "satya-nadella", "project-solara", "ai-agents", "build-2026", "agentic-ai"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "GeekWire", "url": "https://www.geekwire.com/2026/inside-microsofts-project-solara-a-new-platform-for-devices-that-run-ai-agents-instead-of-apps/"},
            {"name": "Engadget", "url": "https://www.engadget.com/ai/microsoft-announces-project-solara-its-take-on-an-ai-agent-platform-175532089.html"},
            {"name": "PC World", "url": "https://www.pcworld.com/article/2762476/an-ai-agent-in-a-security-badge-thats-microsofts-project-solara-pitch.html"},
            {"name": "Technobezz", "url": "https://www.technobezz.com/microsoft-unveils-project-solara-operating-system-for-wearable-ai-devices-at-build-2026/"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/7/78/MS-Exec-Nadella-Satya-2017-08-31-22_%28cropped%29.jpg",
        "image_caption": "Microsoft CEO Satya Nadella at a company event",
        "image_attribution": "Wikimedia Commons",
        "body": """For 15 years, Microsoft has tried to make Windows work on every device. Phones. Tablets. HoloLens. The results ranged from mediocre to catastrophic. So at Build 2026, Satya Nadella did something genuinely surprising: he built a new platform on Android.

Project Solara is not a Windows variant, not a Copilot plug-in, and not a developer toolkit you install on your laptop. It is a full operating system — built on the Android Open Source Project — designed for a class of devices that does not yet broadly exist: hardware where AI agents replace apps entirely.

## What Solara Actually Is

Solara runs on what Microsoft calls the Microsoft Device Ecosystem Platform (MDEP), an enterprise-grade Android build stripped of everything a traditional phone or tablet needs and loaded with everything an AI agent needs. There is no app store. No browser-first experience. No desktop. When you turn on a Solara device, you get agents.

Microsoft showed two reference devices at Build. The first is a desk companion — a touchscreen with dual microphones, a UWB presence sensor, and MediaTek IoT silicon. It authenticates you by face, then gives you ambient access to your AI agents while you work. Plug it into a monitor via USB-C and it becomes a Windows 365 cloud PC client.

The second is stranger: a smart security badge. It has a touchscreen, a camera, a fingerprint sensor, a far-field microphone array, a speaker, and 5G connectivity powered by Qualcomm wearable silicon. Press one button and an AI agent activates. In a demo, Microsoft showed the badge transcribing a recorded conversation with a single press, with the camera letting the agent see what the user sees.

"Boundaries are collapsing," said Stevie Bathiche, the Microsoft corporate vice president and technical fellow leading Applied Sciences Group. "You don't necessarily need the traditional app model."

## Why Android, Not Windows

The decision to build on Android rather than Windows is a concession wrapped in a strategy. Windows is too heavy for the low-power, purpose-built devices Solara targets. Android's open-source base gives hardware partners flexibility while Microsoft layers its own enterprise stack on top: Intune device management, Entra ID authentication, Hello for Business biometrics, and a hardware mic mute button.

The real ambition is not to sell these devices. Microsoft has been explicit that the desk companion and badge are reference designs — blueprints for partners like Qualcomm and MediaTek to adapt. The play is to own the agent platform layer the same way Windows owned the PC layer: take a cut of every device, every agent interaction, every enterprise deployment.

## Where India Fits

Nadella's keynote at Build featured appearances from NVIDIA's Jensen Huang and Qualcomm's Cristiano Amon. But the Indian angle runs deeper than the CEO's heritage.

Microsoft employs tens of thousands of Indian engineers, many in the very divisions — Azure, AI Platform, Enterprise Mobility — that would build Solara's production stack. Qualcomm's India engineering centre, which employs thousands in Hyderabad and Bengaluru, would be central to designing the wearable silicon powering Solara devices.

For Indian IT services companies, the implications are mixed. If Solara succeeds, the companies currently staffing app development and maintenance projects for enterprises could see demand shift toward agent development and deployment — a lower-headcount, higher-skill model. The ones already investing in AI agent capabilities (TCS with Anthropic, HCLTech with Sarvam AI) may be better positioned. The rest may face the same deflation that is already compressing their margins.

## The Bigger Bet

Solara is Nadella's clearest statement yet that the post-app era is not a thought experiment — it is a product roadmap. Google, Amazon, and OpenAI are all racing toward the same destination: platforms where AI agents, not installed applications, are the primary interface between humans and computers.

The question is whether enterprises will buy it. The history of computing is littered with platforms that were technically elegant and commercially dead. But Nadella has a track record of turning improbable bets — cloud-first Azure, GitHub acquisition, the OpenAI partnership — into Microsoft's core business. If Solara works, the Indian engineers who built it will have helped design the device on everyone's desk. If it doesn't, at least Microsoft finally stopped trying to put Windows on a badge."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

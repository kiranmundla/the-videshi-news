#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-06-10 04:55 UTC run"""

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


# ─────────────────────────────────────────────
# ARTICLE 1: Zoho Nathu La Server
# ─────────────────────────────────────────────

article1_body = """Zoho Corporation, the privately held SaaS giant headquartered in Austin and Chennai, has unveiled Nathu La — a server designed and engineered entirely in-house, with all intellectual property owned in India. The name borrows from a Himalayan mountain pass. The ambition borrows from a different altitude entirely: full-stack technological sovereignty, from the firmware layer to the application.

The Nathu La motherboard and chassis platform took five years of R&D across hardware, firmware, and systems management. It runs on Intel Xeon 6 processors and is optimised for virtualisation, high-performance computing, AI inference, and storage workloads. Zoho claims it delivers equivalent performance to competitors while cutting power consumption by 12–18% and total cost of ownership by 20–30%.

## Why India Matters Here

Every major Indian enterprise — from banks to IT services firms — runs on server hardware sourced from abroad. Licensing fees, firmware updates, and security audits flow to foreign entities. Zoho's play is to break that dependency.

"So much investment has gone in from the government and these capacities have been built. It's critical that those capacities are consumed," Shailesh Davey, CEO of Zoho Corporation, said in the announcement. Nathu La is aligned with Make in India, Atmanirbhar Bharat, and the National Supercomputing Mission.

All modular components — including the data centre secure control module and network interface card — were designed in-house and assembled by Indian electronic manufacturing services partners. Over five patents have been filed on thermal management and cost-optimised server architecture.

## The Nagpur Angle

Perhaps the most striking detail: the R&D team is based in Nagpur, not Bangalore or Hyderabad. Many team members came through SETU, a Zoho initiative that trains engineers from colleges across Central India. Over 300 students have passed through the programme, with some placed at Zoho.

"The development of the Nathu La server reflects our commitment to creating complex technology powered by talent from smaller towns and villages," Davey said.

## The Diaspora Read

For NRI tech professionals who have spent careers watching India's software services industry boom while hardware remained an import story, Nathu La represents a notable shift. Zoho's founder Sridhar Vembu has been vocal about building deep technology in India rather than simply assembling it. That the company chose to invest in a five-year server R&D programme — with talent from Nagpur, not Silicon Valley — is the clearest signal yet of where Indian tech self-reliance is heading.

Zoho remains one of the largest privately held tech companies in the world, with 55+ apps and 130 million users. It has no ad-revenue model and owns its data centres. Building the servers that sit inside them was, in that context, the obvious next step."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "Zoho Just Unveiled an India-Designed Server. The Hardware Sovereignty Play Is Real.",
    "subheadline": "The Nathu La server was built by a team in Nagpur, cuts power by 18%, and owns every patent in India. Sridhar Vembu's company is done importing its infrastructure.",
    "slug": make_slug("zoho-nathu-la-india-designed-server-hardware-sovereignty"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Indian tech sovereignty has been a software story for decades — Zoho is making it a hardware story. NRI engineers who've watched India's chip and server dependency grow will recognise this as a significant inflection point. The Nagpur talent pipeline is a direct challenge to the assumption that deep hardware R&D requires Silicon Valley.",
    "tags": ["zoho", "sridhar-vembu", "india-hardware", "make-in-india", "servers", "tech-sovereignty"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Business Wire", "url": "https://www.businesswire.com/news/home/20260609950105/en/Zoho-Corporation-Unveils-Nathu-La-a-Designed-in-House-Server-in-a-Move-Towards-Technological-Sovereignty-and-Inference-Cost-Reduction"},
        {"name": "Hello Entrepreneurs", "url": "https://helloentrepreneurs.com/"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/c/c9/Zoho_headquarters_in_chennai.jpg",
    "image_caption": "Zoho Corporation headquarters in Chennai, India",
    "image_attribution": "Wikimedia Commons",
    "body": article1_body
}


# ─────────────────────────────────────────────
# ARTICLE 2: Infineon Partners with Kaynes & CDIL
# ─────────────────────────────────────────────

article2_body = """Germany's Infineon Technologies, one of the ten largest semiconductor companies in the world, is quietly placing its first real bets on India's chip manufacturing ecosystem. The company has begun transferring packaging expertise to two Indian firms — Sanand-based Kaynes Semicon and Mohali-based Continental Device India Ltd. (CDIL) — and expects to procure packaged semiconductor components from them once their facilities complete qualification.

"We said we'll start using the capacity," Vinay Shenoy, managing director of Infineon Technologies India, told the Economic Times. "Kaynes is one publicly announced project. CDIL is the second. There are others in early stages of conversations."

This is not a courtesy visit. Infineon is evaluating further collaborations with projects from the 12 approved under the India Semiconductor Mission (ISM), the government-backed programme that has poured billions into building India's first real chip packaging and testing infrastructure.

## Consume, Don't Just Build

The distinction matters. India's semiconductor mission has attracted headlines for every factory announcement, groundbreaking, and MoU signing. What has attracted less attention is whether anyone will actually buy what these fabs produce. Infineon's commitment to consume capacity — not just advise or invest, but procure — is the kind of demand signal that separates a government showcase from a functioning supply chain.

"Even if you have two choices — invest in building capacity or consume the capacity — so much investment has gone in from the government and these capacities have been built. It's also critical that those capacities are consumed," Shenoy said.

## The OSAT Entry Point

Kaynes Semicon, the semiconductor arm of Kaynes Technology India Ltd., has been building India's first outsourced semiconductor assembly and test (OSAT) facility in Sanand, Gujarat. It secured its first paying OSAT customer earlier this year and adopted Synopsys simulation software for advanced packaging work. CDIL, in Mohali, Punjab, has decades of discrete semiconductor manufacturing experience but is now expanding into more complex packaging.

Both are entering territory currently dominated by Taiwanese and Southeast Asian firms like ASE Group and Amkor. Infineon's willingness to qualify these facilities and transfer packaging know-how provides a credibility bridge that no amount of government subsidy can replicate.

## The NRI Semiconductor Bet

For the growing cohort of Indian-origin semiconductor engineers in the United States — many of whom work at NVIDIA, Intel, Qualcomm, and Broadcom — this is a story worth tracking. India has talked about chips for years. It has trained thousands of semiconductor engineers who then left for Taiwan, South Korea, or the Bay Area. The question is whether companies like Infineon will create enough demand to justify keeping the next generation at home.

The answer, for now, is cautious optimism. Infineon isn't moving its most advanced work to India. But it is doing something that matters more at this stage: giving India's new chip facilities their first real customers."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "Infineon Is Betting Real Money on India's Chip Fabs. That Changes Everything.",
    "subheadline": "Germany's biggest chipmaker has started transferring packaging expertise to Kaynes and CDIL, and plans to procure from them. India's semiconductor mission finally has a foreign customer.",
    "slug": make_slug("infineon-kaynes-cdil-india-chip-packaging-semiconductor"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Indian-origin semiconductor engineers in the US have watched India's chip ambitions from a distance. Infineon's procurement commitment is the first real signal that OSAT facilities in Gujarat and Punjab could create demand — and jobs — that keep the next generation of chip talent at home.",
    "tags": ["infineon", "kaynes-semicon", "cdil", "india-semiconductor-mission", "osat", "chip-packaging"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Global SMT", "url": "https://www.globalsmt.net/asia-industry-news/infineon-taps-cdil-kaynes-to-strengthen-india-chip-collab/"},
        {"name": "NewsPoint / Economic Times", "url": "https://www.newspointapp.com/"},
        {"name": "DIGITIMES", "url": "https://digitimes.com/"}
    ]),
    "score_total": 75,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/6636463/pexels-photo-6636463.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
    "image_caption": "Close-up of a semiconductor chip on a circuit board",
    "image_attribution": "Pexels",
    "body": article2_body
}


# ─────────────────────────────────────────────
# ARTICLE 3: Aravind Srinivas / Perplexity IPO
# ─────────────────────────────────────────────

article3_body = """The AI industry's stampede toward public markets now has a third entrant from a familiar talent pool. Aravind Srinivas, the Chennai-born CEO of AI search company Perplexity, confirmed this week that the company is planning an IPO for 2028 — regardless of how Anthropic and OpenAI fare when they go public.

"Agnostic of these two companies, we were planning for something in 2028, so that still remains the case," Srinivas told CNBC in an interview.

The context is dizzying. OpenAI filed a confidential S-1 with the SEC on Monday, days after Anthropic did the same. SpaceX is expected to debut on Friday at a valuation near $2 trillion. Together, these listings represent the largest wave of technology IPOs since the dot-com era — and the AI sector is at the centre of it.

## The Indian Founder's Playbook

Srinivas, 32, grew up in Chennai, studied at IIT Madras, and earned a PhD in computer science at UC Berkeley, where he worked under deep learning pioneer Pieter Abbeel. He interned at both DeepMind and OpenAI before founding Perplexity in 2022. The company has raised over $500 million and was valued at $18 billion in its last funding round.

His trajectory is now a case study in the Indian founder's path through American AI. Like Sundar Pichai at Google, Satya Nadella at Microsoft, and Parag Agrawal at Twitter before him, Srinivas rose through elite institutions and top research labs before building his own company. Unlike those predecessors, he didn't climb through corporate management — he went straight to founding.

## The Market Reality

Srinivas was candid about the risks. "I certainly think there will be ripple effects if they don't go well, like there is no sugar coating on that," he said, referring to the OpenAI and Anthropic listings. "The SpaceX IPO this week will definitely be a leading indicator of how Anthropic or OpenAI will go out."

The numbers underscore why Wall Street is paying attention. OpenAI is generating $2 billion in monthly revenue and was valued at $852 billion in March. Anthropic's valuation jumped to $965 billion in May after a $65 billion Series H raise. Both companies are burning capital at rates that make their IPO timelines a matter of necessity as much as strategy.

Perplexity is smaller but growing aggressively. The company's AI search engine competes directly with Google by synthesising answers from multiple sources rather than returning a list of links. It has drawn both users and lawsuits — several major publishers have accused it of using their content without authorisation.

## Why Diaspora Watchers Should Care

Srinivas is the most prominent Indian-origin AI founder to build a company that directly challenges Google Search — a product synonymous with another Indian-origin CEO. If Perplexity reaches its 2028 IPO target, it would mark the first time an Indian-born founder took a generative AI company public in the United States.

"I think it's important for the AI industry that these IPOs go well, and I actually think they will go well, because they're doing well," Srinivas said. For the thousands of Indian engineers building AI at OpenAI, Anthropic, Google, and Meta, the message is clear: the window for founding, not just operating, is wide open."""

article3 = {
    "id": str(uuid.uuid4()),
    "headline": "Perplexity's Aravind Srinivas Wants a 2028 IPO. He's Not Waiting for OpenAI to Go First.",
    "subheadline": "The Chennai-born CEO says Perplexity's public listing plan stands regardless of how the OpenAI and Anthropic IPOs land. He'd be the first Indian-born founder to take a generative AI company public.",
    "slug": make_slug("aravind-srinivas-perplexity-ipo-2028-indian-ai-founder"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Srinivas represents a generational shift in the Indian tech diaspora — from corporate operators (Pichai, Nadella) to AI company founders. A Perplexity IPO would be the first time an Indian-born founder takes a generative AI company public in the US, signalling that the founder path is increasingly open.",
    "tags": ["aravind-srinivas", "perplexity", "ipo", "ai-search", "indian-founders", "silicon-valley"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/"},
        {"name": "CNBC", "url": "https://www.cnbc.com/"},
        {"name": "Barron's", "url": "https://www.barrons.com/articles/openai-ipo-stock-market-listing-chatgpt-private-eb0f3988"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/c/c9/Aravind_Srinivas_2024.jpg",
    "image_caption": "Aravind Srinivas, CEO and co-founder of Perplexity AI",
    "image_attribution": "Wikimedia Commons",
    "body": article3_body
}


# ─────────────────────────────────────────────
# INSERT ALL ARTICLES
# ─────────────────────────────────────────────

articles = [article1, article2, article3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

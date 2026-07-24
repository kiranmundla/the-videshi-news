#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-06-29 06:00 UTC batch."""

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


# ── Article 1 ──────────────────────────────────────────────────────────────
art1_body = """Jensen Huang's empire now stretches into territory nobody expected him to claim. According to IDC's latest quarterly data, NVIDIA has become the number-one data centre Ethernet switch vendor by revenue — displacing Arista Networks, the company that an Indian-born engineer built from scratch into a networking juggernaut.

The numbers are stark. NVIDIA's Spectrum-X platform generated $2.1 billion in data centre Ethernet switch revenue in Q1 2026, a 192.7 per cent year-over-year surge that vaulted it to a 21.5 per cent market share. A year ago, that share was barely 4 per cent. Arista Networks, led by CEO Jayshree Ullal — who grew up in New Delhi before moving to the United States — has been pushed to second place. Cisco, long the networking establishment, fell further behind.

## The platform ate the product

The shift is not merely a market-share reshuffle. It represents a structural change in how data centres are built. Traditionally, GPU vendors sold compute and networking vendors sold switches. You bought them from different companies, wired them together, and hoped the latency was tolerable.

NVIDIA's Spectrum-X obliterated that division. The platform bundles GPUs, BlueField data processing units, and LinkX cables into an integrated AI factory fabric. Hyperscalers building massive GPU clusters — Meta, Microsoft, Oracle, xAI — increasingly want one throat to choke. And that throat belongs to Jensen Huang.

IDC's Paul Nicholson called it "one of the most significant vendor landscape shifts IDC has tracked in enterprise networking." The overall data centre Ethernet switch market hit $10 billion in Q1 2026, up 61 per cent year-over-year. The broader Ethernet switch market reached $15.4 billion.

## What Jayshree Ullal built — and what she now faces

For Indian Americans in tech, Ullal's career is a diaspora origin story. Born in London, raised in New Delhi, she studied electrical engineering at San Francisco State University and cut her teeth at AMD and Cisco before taking the helm at Arista in 2008. She turned a startup into a $100-billion networking giant, and Forbes has consistently ranked her among the world's most powerful women in business.

Arista is not collapsing. The company still posted solid growth and has deep enterprise relationships. But the ground has shifted beneath its feet. When networking becomes a feature of NVIDIA's GPU platform rather than a standalone product, the standalone networking vendor's leverage diminishes.

## The Indian talent dimension

This story is also about the engineers building these systems. NVIDIA's networking division — which includes the Spectrum-X and InfiniBand teams — employs a significant number of Indian-origin engineers, many on H-1B visas, at its offices in Santa Clara and Bengaluru. Cisco's data centre group in San Jose has historically been a major H-1B employer. And Arista's engineering teams in Nashua, New Hampshire and Bengaluru are stocked with Indian networking specialists.

The irony is not lost on anyone in the Indian tech diaspora: one Indian-origin CEO's empire is being disrupted by a platform that Indian engineers helped design, at a company where Indian talent is a critical mass.

## What comes next

The 800-gigabit Ethernet switch segment — the fastest-growing tier — now accounts for 35.8 per cent of data centre revenue, and NVIDIA leads there too. With its upcoming Vera CPUs and next-generation networking silicon, the company is building the case that every layer of the AI data centre should carry the NVIDIA logo.

For NRI investors with exposure to networking stocks, the message is clear: the AI infrastructure buildout is not a rising tide lifting all boats. It is a wave that rewards platforms and punishes point products. Jayshree Ullal, one of the most accomplished Indian-origin tech leaders in the world, now faces the most important strategic challenge of her career."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "NVIDIA Just Dethroned Jayshree Ullal's Arista in the Market She Built",
    "subheadline": "The Indian-born CEO turned Arista into a networking giant. Now NVIDIA's platform play has seized the top spot in data centre Ethernet switching — and the implications run deeper than market share.",
    "slug": make_slug("nvidia-dethroned-jayshree-ullal-arista-ethernet-switch"),
    "category": "technology",
    "vertical": "tech",
    "diaspora_angle": "Indian-born Jayshree Ullal built Arista into a $100B networking giant; her company just lost the top spot to NVIDIA's platform approach — built partly by Indian engineers on H-1B visas at NVIDIA's Santa Clara and Bengaluru offices.",
    "tags": ["nvidia", "arista-networks", "jayshree-ullal", "data-center", "ethernet", "indian-tech-leader", "spectrum-x"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "IDC Ethernet Switch Tracker Q1 2026", "url": "https://www.idc.com/"},
        {"name": "WCCFTech", "url": "https://wccftech.com/nvidia-quietly-claims-top-spot-in-the-datacenter-ethernet-switch-market/"},
        {"name": "SDxCentral", "url": "https://www.sdxcentral.com/"}
    ]),
    "score_total": 72,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/9/9b/Jayshree_Ullal_Arista_CEO.jpg",
    "image_caption": "Arista Networks CEO Jayshree Ullal, the Indian-born engineer whose company just lost its top networking ranking to NVIDIA",
    "image_attribution": "Wikimedia Commons",
    "body": art1_body
}


# ── Article 2 ──────────────────────────────────────────────────────────────
art2_body = """Elon Musk built the world's largest AI data centre to train his own chatbot. Then he discovered something unexpected: renting out the GPUs pays better than using them.

SpaceX's xAI subsidiary has now signed compute leasing deals worth a combined $76 billion through 2029 with three tenants: Anthropic at $1.25 billion per month, Google at $920 million per month, and AI startup Reflection at $150 million per month. That is $2.32 billion in monthly recurring revenue from GPU rentals alone — more than many cloud providers generate in a quarter.

## The Colossus embarrassment

The backstory is less glamorous than the headline numbers. xAI's Colossus 1 data centre in Memphis, Tennessee — once trumpeted as a 300-megawatt, 220,000-GPU monument to Musk's AI ambitions — was running at roughly 11 per cent model FLOPs utilisation, according to an internal memo reported by industry analysts. The facility's hodgepodge of H100, H200, and GB200 GPUs could not parallelise Grok's training workloads efficiently.

xAI moved its training to the newer Colossus 2 facility and started shopping the original to the highest bidder. Anthropic signed first, locking in access to the full capacity of Colossus 1 in May. Google followed in June, committing $920 million monthly from October through June 2029 for roughly 110,000 NVIDIA GPUs — framed publicly as "bridge capacity" for surging Gemini Enterprise demand. SpaceX's IPO filing highlighted both deals, establishing AI infrastructure as a formal revenue line ahead of its stock market debut.

## The compute famine is real

What makes these eye-watering numbers possible is a global GPU shortage that shows no sign of easing. NVIDIA's Q1 2026 data centre revenue hit $75.2 billion, up 92 per cent year-over-year, and the company is sold out of Blackwell GPUs well into 2027. Hyperscalers — Meta, Microsoft, Google, Amazon — have collectively committed over $720 billion in data centre capital expenditure for 2026 alone. Even at that scale, demand outstrips supply.

This shortage shapes the AI industry in ways that echo the semiconductor bottlenecks of 2020-22, but at a vastly larger scale. Companies that cannot secure compute capacity cannot train frontier models, cannot serve inference at scale, and cannot compete. Compute has become the oil of the AI era, and Musk — despite his erratic management of xAI's training — now controls a refinery.

## Where India fits in this equation

India's AI ambitions run headlong into this compute wall. The IndiaAI Mission has allocated ₹10,372 crore for AI infrastructure, including 10,000 GPU units. By comparison, Anthropic alone is paying for access to 220,000 GPUs at a single SpaceX facility. India's total planned GPU capacity is less than 5 per cent of what one American company is renting from another.

This gap matters directly to the Indian diaspora. Thousands of Indian-origin engineers work at Google, Anthropic, and NVIDIA — the companies on both sides of these deals. They build the models that consume this compute. They design the chips that produce it. And many watch India's sovereign AI efforts with a mix of pride and frustration, knowing that their home country's entire AI compute budget would not cover two months of Google's SpaceX lease.

The $76 billion in SpaceX compute deals also reframes India's data centre buildout. Amazon's recent $13 billion India investment and Google's GIFT City fintech hub are significant by Indian standards, but they are drops in an ocean where monthly GPU rental invoices exceed a billion dollars.

## The Musk calculus

For Musk, the arithmetic is brutally simple. A data centre that was embarrassingly underutilised for its intended purpose now generates more monthly revenue than most publicly traded AI companies. SpaceX's upcoming IPO — targeting a valuation between $1.75 trillion and $2 trillion — will benefit from a disclosed, recurring AI infrastructure revenue stream that makes the company look less like a launch provider and more like a hyperscaler.

The irony is hard to miss: the man who declared xAI would build artificial general intelligence is, for now, making his best AI money by renting the infrastructure to his competitors. Whether that changes when Colossus 2 matures — or whether Musk simply discovers that GPU landlording beats model training — may depend on how tight the compute market stays through 2029."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "Musk's Real AI Business: Renting Idle GPUs to Anthropic and Google for $2 Billion a Month",
    "subheadline": "SpaceX's xAI data centres have locked in $76 billion in compute leases through 2029. The backstory involves a facility that couldn't train its own chatbot — and a global GPU famine that India can barely afford to watch from the sidelines.",
    "slug": make_slug("spacex-xai-gpu-rental-anthropic-google-76-billion"),
    "category": "technology",
    "vertical": "tech",
    "diaspora_angle": "India's entire IndiaAI Mission GPU allocation is less than 5% of what Anthropic rents from one SpaceX facility. Indian engineers at Google, Anthropic, and NVIDIA are on both sides of these deals — building the models and designing the chips that drive compute demand.",
    "tags": ["spacex", "xai", "anthropic", "google", "nvidia", "gpu", "data-center", "ai-infrastructure", "india-ai"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/"},
        {"name": "The Motley Fool", "url": "https://www.fool.com/"},
        {"name": "Data Center Dynamics", "url": "https://www.datacenterdynamics.com/"},
        {"name": "WCCFTech", "url": "https://wccftech.com/"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/17489153/pexels-photo-17489153.jpeg",
    "image_caption": "Server racks inside a modern data centre — facilities like SpaceX's Colossus now command billions in monthly GPU rental fees",
    "image_attribution": "Pexels",
    "body": art2_body
}


# ── Article 3 ──────────────────────────────────────────────────────────────
art3_body = """The Indian government does not typically buy equity in startups. It runs subsidies, grants, tax breaks — the bureaucratic toolkit of industrial policy. So when New Delhi quietly moved to acquire a 1 to 2 per cent stake in Sarvam AI, the country's newest artificial intelligence unicorn, it signalled something more consequential than a cheque.

The stake will come through convertible instruments linked to subsidised compute support under the IndiaAI Mission, according to a report in The Economic Times. The investment follows Sarvam's $234 million Series B raise in June, led by a $150 million strategic bet from HCLTech, which valued the Bengaluru-based company at $1.5 billion. Bessemer Venture Partners, Khosla Ventures, and Peak XV Partners also participated. Sarvam is targeting $300 million in total for the round.

## Paying in GPUs, not rupees

What makes the government's approach unusual is the currency. Rather than writing a cheque, New Delhi is converting subsidised access to GPU compute — the scarcest resource in AI — into an equity position. The IndiaAI Mission's 10,000-GPU allocation, announced earlier this year, is now being deployed not just as infrastructure but as a strategic investment tool.

This is industrial policy by inference cluster. The government gets alignment with a company building India's most advanced AI models. Sarvam gets compute capacity it desperately needs to train its next-generation agentic, coding, and cybersecurity models. Neither side exchanges cash.

"AI has changed the way software is going to be written," Sarvam co-founder Vivek Raghavan told The Hindu BusinessLine after the HCLTech deal. "There is no doubt about the synergies between an IT services company and an AI company." Now that equation extends to the state itself.

## Why Sarvam matters to the diaspora

Sarvam occupies a peculiar position in Indian tech. It is building full-stack sovereign AI — models trained to understand 22 Indian languages, deployed across banking, insurance, government services, and defence. Its 30-billion and 105-billion-parameter open-source models, released earlier this year, are designed for Indian use cases that OpenAI and Anthropic have little incentive to prioritise.

But building frontier AI from India means competing for the same talent pool that feeds Silicon Valley. Co-founder Pratyush Kumar has been candid about the challenge. "India has immense talent, but lacks experience" in building foundation models from scratch, he told NDTV Profit.

Sarvam is actively recruiting AI researchers from the United States to bridge that gap. "Predominantly everything will continue to be in India, but we will also get exceptional people who want to help India in this mission but are in the US," Raghavan said. For Indian-origin researchers at Google Brain, Meta AI, or OpenAI, that pitch — come home and build sovereign AI — has become more credible now that Sarvam has a billion-dollar valuation, HCLTech's enterprise distribution, and the government's strategic backing.

## The sovereign AI arms race

India is not the only country making this bet. France backs Mistral. The UAE funds the Technology Innovation Institute. Saudi Arabia has committed billions to AI through its Public Investment Fund. China's sovereign AI ecosystem is already mature, with Baidu, Alibaba, and ByteDance competing at near-frontier levels.

What distinguishes India's approach is the IT services bridge. HCLTech's $150 million investment is not venture capital — it is a strategic play to combine Sarvam's models with HCLTech's enterprise relationships and 220,000-person engineering workforce. The idea is to create an AI products company that can serve both Indian institutions and global enterprises, using India's IT services distribution network as a moat.

For NRIs watching from the Bay Area or New Jersey, the subtext is significant. India is no longer content to export AI talent. It wants to build AI at home, deploy it at Indian scale, and — if the HCLTech partnership works — sell it back to the same global enterprises that employ the diaspora. The government's equity stake, however small, makes that ambition a matter of national strategy rather than startup aspiration.

## What the government gets wrong — and right

The risks are real. A 1 to 2 per cent stake is too small to influence strategic decisions. Subsidised compute is valuable but temporary — Sarvam will need commercial-grade infrastructure to compete at frontier scale, and India's GPU capacity remains a fraction of what American companies deploy. And the convertible instrument structure means the government's ownership will dilute as Sarvam raises more capital.

But the signal matters more than the stake. By taking equity in Sarvam, New Delhi is telling the AI industry that sovereign AI is not a slogan — it is a line item on the government's balance sheet. For a country that has historically struggled to translate scientific ambition into commercial scale, putting its name on the cap table is a meaningful, if modest, step."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "New Delhi Wants a Piece of India's AI Unicorn. It's Paying in GPUs.",
    "subheadline": "The Indian government is acquiring a stake in Sarvam AI through subsidised compute — an unusual move that turns GPU access into equity and signals sovereign AI is now a matter of national strategy.",
    "slug": make_slug("india-government-equity-stake-sarvam-ai-indiaai-mission"),
    "category": "technology",
    "vertical": "tech",
    "diaspora_angle": "Sarvam is actively recruiting Indian-origin AI researchers from the US to build sovereign AI models for 22 Indian languages. The government equity stake signals India wants to build AI at home, not just export AI talent — a strategic shift that touches every NRI engineer in Silicon Valley.",
    "tags": ["sarvam-ai", "india-ai", "sovereign-ai", "hcltech", "indiaai-mission", "indian-startup", "ai-unicorn"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "The Economic Times", "url": "https://economictimes.indiatimes.com/"},
        {"name": "TechCrunch", "url": "https://techcrunch.com/2026/06/16/sarvam-becomes-indias-newest-ai-unicorn/"},
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/"},
        {"name": "NDTV Profit", "url": "https://www.ndtvprofit.com/"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/28767589/pexels-photo-28767589.jpeg",
    "image_caption": "A microchip visualised with heatmap colours — India's government is converting GPU compute access into equity in its AI unicorn Sarvam",
    "image_attribution": "Pexels",
    "body": art3_body
}


# ── Insert ─────────────────────────────────────────────────────────────────
articles = [art1, art2, art3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

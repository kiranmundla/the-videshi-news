#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-07-01 08:00 PDT run."""

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

# ──────────────────────────────────────────────
# ARTICLE 1: CG Semi — India's First Commercial Chip Shipment
# ──────────────────────────────────────────────

art1_body = """India has shipped its first commercial batch of semiconductor chips from a domestic facility — and if you blinked, you might have missed it.

On June 19, CG Semi's Sanand facility in Gujarat dispatched a consignment of packaged and tested microcontrollers to Kuala Lumpur. The chips, assembled for Japan's Renesas Electronics, are destined for automotive and industrial applications. It is a quiet milestone for a country that, until four years ago, had no semiconductor manufacturing infrastructure to speak of.

## From pilot line to production floor

CG Semi is a joint venture between CG Power (part of the century-old Murugappa Group), Renesas Electronics America, and Thailand's Stars Microelectronics. The partners have committed ₹7,500 crore ($900 million) to the Sanand campus, which houses an Outsourced Semiconductor Assembly and Test (OSAT) facility — the kind of operation where silicon dies arrive from foundries abroad and are assembled, packaged, tested, and shipped as finished chips.

The first plant, G1, was inaugurated in August 2025 with a peak capacity of 500,000 units per day. A second facility, G2, located three kilometres away, is under construction and expected to come online by late 2026, scaling combined output to roughly 14.5 million units daily. Together, the two plants are projected to create more than 5,000 direct and indirect jobs.

To get production-ready, CG Semi sent hundreds of Indian engineers and technicians to Malaysia for three months of hands-on training — a detail that underscores both the ambition and the knowledge gap India is racing to close.

## The bigger picture

India now has 12 semiconductor projects approved under the India Semiconductor Mission, with proposed investments totalling roughly ₹1.64 lakh crore ($20 billion). The marquee bet is Tata Electronics' fabrication facility in Dholera, Gujarat, built with ASML lithography equipment. Micron's assembly and test plant, also in Sanand, inaugurated its first phase earlier this year. A silicon carbide compound fab by SiCSem is taking shape in Odisha.

But it is OSAT — the lower end of the chip value chain — where India is likeliest to gain traction first. Former NITI Aayog member Arvind Virmani has argued that the country should build strength in packaging and testing before chasing advanced fabrication, which requires the kind of capital, talent density, and ecosystem maturity that Taiwan, South Korea, and the United States have spent decades cultivating.

CG Semi's chairman, Vellayan Subbiah, frames it more bluntly: "Semiconductors are the new steel — essential for building India's economic and technological security."

## Why this matters to the diaspora

For the tens of thousands of Indian-origin engineers working in the semiconductor industry across Silicon Valley, Austin, and Hsinchu, CG Semi's first shipment is not just a headline — it is the beginning of a supply chain that could eventually pull talent and capital back to India. Micron CEO Sanjay Mehrotra, himself an Indian-American, has urged semiconductor equipment and materials suppliers to "deepen and expand your footprint in India, closer to where the action is."

The opportunity is tangible. NRI professionals with OSAT, EDA, or design experience are precisely the people India's chip ecosystem needs to attract. And for diaspora investors watching the space, CG Power's stock has already quadrupled since the Semiconductor Mission's launch.

India is not making cutting-edge 3-nanometre chips. It is packaging microcontrollers for cars and refrigerators. But every semiconductor power started somewhere — and on June 19, India started shipping."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "India Just Shipped Its First Semiconductor Chips. They Went to Malaysia.",
    "subheadline": "CG Semi's Gujarat plant dispatched its first commercial consignment of packaged microcontrollers for Renesas — a quiet milestone in India's $20 billion chip ambition.",
    "slug": make_slug("india-first-semiconductor-chip-shipment-cg-semi-sanand"),
    "category": "technology",
    "vertical": "semiconductor",
    "diaspora_angle": "Indian-origin semiconductor engineers across Silicon Valley and Austin now have a domestic chip ecosystem beginning to take shape — one that could pull NRI talent and investment back home.",
    "tags": ["semiconductor", "india-manufacturing", "cg-semi", "renesas", "sanand", "make-in-india"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Communications Today", "url": "https://www.communicationstoday.co.in/india-ships-1st-semicon-chips-from-sanand-to-malaysia/"},
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/info-tech/indias-1st-pilot-line-for-semiconductors-becomes-operational-in-gujarat-cg-semis-plant-to-roll-out-initial-make-in-india-chip/article68580050.ece"},
        {"name": "Livemint", "url": "https://www.livemint.com/technology/tech-news/where-does-india-stand-in-its-chip-ambitions-11749464780043.html"}
    ]),
    "score_total": 80,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/36169774/pexels-photo-36169774.jpeg?auto=compress&cs=tinysrgb&w=1200",
    "image_caption": "Close-up of electronic microchips on a circuit board",
    "image_attribution": "Pexels",
    "body": art1_body.strip()
}

# ──────────────────────────────────────────────
# ARTICLE 2: Raja Koduri's Oxmiq Raises $35M
# ──────────────────────────────────────────────

art2_body = """Raja Koduri spent a decade building Intel's graphics chip division. Now he wants to do something arguably harder: break Nvidia's stranglehold on AI computing — not by out-spending it, but by out-licensing it.

On Wednesday, Koduri's startup Oxmiq announced a $35 million funding round, bringing its total raised to $60 million. The investors include MediaTek, Pegatron Venture Capital, and the Samsung Catalyst Fund. The company, based in Campbell, California, is building licensable chip architecture designed to make AI hardware dramatically cheaper and faster to develop.

## The Arm of AI

The pitch is elegantly simple. Today, building a cutting-edge AI chip costs upwards of $500 million and takes years. Companies must design separate graphics processors, central processors, and tensor engines, then stitch them together. Oxmiq's plan is to collapse all three into a single block of intellectual property that can be licensed to anyone — much the way Arm Holdings provides the core designs inside nearly every smartphone on the planet.

"We would want to be the Arm of this next era," Koduri told Reuters.

The company's architecture, called OXCORE, scales from a single core for robotics and edge AI to thousands of cores for data-centre workloads. A chiplet system called OXQUILT lets customers configure their own ratios of compute, memory, and interconnect. And critically, Oxmiq has built a compatibility layer that allows software written for Nvidia's CUDA — the de facto standard for AI programming — to run on non-Nvidia hardware without code modification.

That last detail matters enormously. CUDA's software ecosystem is the moat that keeps hyperscalers and AI labs locked into Nvidia's hardware. If Oxmiq's compatibility layer works as advertised, it could lower the barrier for companies like Broadcom, Marvell, and MediaTek to offer competitive AI silicon — and give their customers a reason to diversify.

## A career built across continents

Koduri's résumé reads like a map of the global semiconductor industry's Indian diaspora. Born in Andhra Pradesh, he studied at IIT Kharagpur before moving to the United States to work at AMD, where he led the development of Radeon graphics. He then spent time at Apple working on GPU architecture before joining Intel as chief architect and senior vice president in 2017. At Intel, he oversaw the Arc GPU programme and the company's push into discrete graphics and AI accelerators.

He left Intel in 2023 and briefly co-founded Mihira Visual Labs with Baahubali producer Shobu Yarlagadda and director S.S. Rajamouli — a cinematic AI venture — before turning full-time to Oxmiq. He now serves as a strategic advisor to Mihira while Yarlagadda runs the day-to-day.

## Why this matters to the diaspora

Koduri's journey — from IIT to Intel's C-suite to founding a company that could reshape AI hardware economics — is a familiar arc for Indian-American semiconductor professionals, but the stakes here are unusually high. The AI chip market is projected to exceed $200 billion by 2028, and it is almost entirely dominated by one company. If Oxmiq succeeds in building a licensing model that works, it will not just create a new business — it will expand the market for the thousands of Indian-origin chip designers, architects, and verification engineers who currently work inside the Nvidia-Intel-AMD triopoly.

MediaTek, one of Oxmiq's backers, already employs significant Indian engineering talent. A more open chip-IP ecosystem would accelerate hiring at companies across the supply chain — from Hyderabad design centres to Bay Area startups.

The $60 million Oxmiq has raised is modest by AI-industry standards; OpenAI raises that in a day. But the licensing-first approach means Oxmiq avoids the capital-intensive trap of actually manufacturing chips. It is a bet that the next era of AI hardware will be defined not by who builds the biggest GPU, but by who builds the best blueprint."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "Intel's Former Chief Architect Raised $60 Million to Break Nvidia's Lock on AI. His Weapon Is a Blueprint.",
    "subheadline": "Raja Koduri's startup Oxmiq wants to be the Arm of artificial intelligence — licensing unified chip IP so anyone can build competitive AI hardware without spending $500 million.",
    "slug": make_slug("raja-koduri-oxmiq-35m-ai-chip-arm-nvidia"),
    "category": "technology",
    "vertical": "semiconductor",
    "diaspora_angle": "Koduri's IIT-to-Intel-to-founder arc represents the Indian semiconductor diaspora at its most ambitious — and a more open AI chip ecosystem would expand opportunities for thousands of Indian-origin chip designers.",
    "tags": ["raja-koduri", "oxmiq", "ai-chips", "nvidia", "semiconductor", "indian-diaspora", "startup"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/world/asia-pacific/startup-oxmiq-raises-35-million-build-chip-architecture-lower-cost-ai-2026-07-01/"},
        {"name": "Reuters (Aug 2025 seed round)", "url": "https://www.reuters.com/technology/chip-startup-oxmiq-launches-gpu-tech-license-2025-08-05/"},
        {"name": "BusinessWire", "url": "https://www.businesswire.com/news/home/20250805467291/en/Oxmiq-Labs-Inc.%E2%84%A2-Re-Architecting-the-GPU-Stack-From-Atoms-to-Agents%E2%84%A2"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/2105927/pexels-photo-2105927.jpeg?auto=compress&cs=tinysrgb&w=1200",
    "image_caption": "High-resolution macro shot of a CPU chip with gold pins",
    "image_attribution": "Pexels",
    "body": art2_body.strip()
}

# ──────────────────────────────────────────────
# ARTICLE 3: Ford Rehires 350 Engineers After AI Fails
# ──────────────────────────────────────────────

art3_body = """Ford Motor Company just earned its best quality ranking in 16 years. The fix was not a better algorithm. It was 350 engineers who had already left.

The automaker has quietly rehired roughly 350 veteran engineers — many of them former employees, others recruited from suppliers — over the past three years after discovering that its AI-powered quality-control systems were producing worse results, not better ones. Ford now tops the 2026 J.D. Power Initial Quality Study among mainstream brands, its highest finish since 2010.

The admission came from the top. "We had been relying more and more on automated quality systems," Kumar Galhotra, Ford's Indian-American chief operating officer, told Bloomberg. "We brought back technical specialists … They hunt for failure points before a part ever reaches the plant floor."

## The automation trap

Ford's AI bet was not small. The company has shed 5,300 salaried positions since 2020, partly on the assumption that automation could absorb the work. It installed 900 AI-powered cameras on production lines to detect defects and leaned on algorithmic systems for design validation. CEO Jim Farley said as recently as June 2025 that AI could replace "literally half" of white-collar workers in the United States.

A year later, the company's own leadership conceded the opposite. Charles Poon, Ford's vice president of vehicle hardware engineering, told Bloomberg: "Mistakenly, we thought that by just introducing artificial intelligence and ingesting the design requirements that we had, that would produce a high-quality product."

The problem was not the technology itself but what the technology was trained on. When veteran engineers left — taking decades of tacit knowledge about failure modes, material behaviour, and design trade-offs — the AI systems lost the very expertise they needed to function. The algorithms could parse design documents. They could not replicate the intuition of an engineer who had watched a particular seal fail in humidity testing across three product cycles.

## The costly lesson

Ford's warranty and recall costs have been staggering — the company has spent billions in recent years on quality-related expenses. Farley said the rehiring initiative has already generated savings worth "hundreds and hundreds of millions of dollars." Ford is targeting $1 billion in total cost reductions for 2026.

The returning engineers are not just fixing vehicles. They are retraining the AI systems, leading mandatory troubleshooting meetings, and mentoring younger staff. The goal, Galhotra said, is a hybrid model where experienced humans programme and supervise the automated tools — not the other way around.

## Why Indian tech workers should pay attention

This is not just a story about cars. It is a data point in the most consequential debate facing the global tech workforce: whether AI will replace engineers or augment them.

Galhotra — born in India, educated at the Indian Institute of Technology — is one of the most senior Indian-origin executives in the American auto industry. His public admission that Ford over-rotated on AI carries weight in boardrooms from Dearborn to Bengaluru.

For the estimated 300,000 Indian-origin engineers working across American industry on H-1B and L-1 visas, Ford's reversal is quietly reassuring. The narrative that AI would eliminate the need for experienced technical talent — and by extension, the visa sponsorships that keep that talent in the country — just took a hit. Domain expertise, the kind built over years of hands-on work, turns out to be exactly what AI needs to function.

India's IT services giants — TCS, Infosys, Wipro, HCL Tech — should be watching closely too. These companies have bet their growth strategies on selling AI transformation to Western manufacturers and enterprises. Ford's experience suggests that the real value proposition is not "replace your engineers with AI" but "use your engineers to make AI work." That is a harder sell, but a more honest one.

The lesson from Dearborn is uncomfortable but clear: the grey-bearded engineer Ford fired is the same person Ford had to pay to come back. AI without institutional knowledge is just expensive pattern-matching. The humans are not optional."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "Ford's AI Replaced Its Best Engineers. Then Ford Had to Hire Them All Back.",
    "subheadline": "Indian-American COO Kumar Galhotra admits the automaker over-relied on automation — and the 350 veteran engineers it rehired just delivered Ford's best quality ranking in 16 years.",
    "slug": make_slug("ford-ai-failed-rehires-engineers-galhotra"),
    "category": "technology",
    "vertical": "ai-automation",
    "diaspora_angle": "Ford COO Kumar Galhotra — an IIT graduate and one of Detroit's most senior Indian-origin executives — publicly admitted AI cannot replace domain expertise, a reassuring data point for 300,000 Indian engineers in the US on H-1B visas.",
    "tags": ["ford", "ai", "automation", "kumar-galhotra", "engineers", "h1b", "indian-diaspora", "manufacturing"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "People", "url": "https://people.com/ford-hires-over-300-engineers-including-former-employees-after-finding-ai-couldnt-replicate-their-work-12010429"},
        {"name": "Memeburn", "url": "https://memeburn.com/ford-ai-quality-control-engineers-2026/"},
        {"name": "Madhyamam", "url": "https://madhyamamonline.com/technology/ford-rehires-350-veteran-engineers-after-ai-falls-short-on-quality-checks-1533129"},
        {"name": "Bloomberg (via Livemint)", "url": "https://www.livemint.com/companies/ford-says-ai-failed-to-match-human-expertise-rehires-350-engineers-only-as-good-as-its-training-11782809340090.html"}
    ]),
    "score_total": 85,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/19233057/pexels-photo-19233057.jpeg?auto=compress&cs=tinysrgb&w=1200",
    "image_caption": "Robotic arms assembling a vehicle on a modern automotive production line",
    "image_attribution": "Pexels",
    "body": art3_body.strip()
}

# ──────────────────────────────────────────────
# INSERT ALL
# ──────────────────────────────────────────────

articles = [art1, art2, art3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']} — {art['headline']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

print(f"\nDone. {len(articles)} articles submitted for review.")

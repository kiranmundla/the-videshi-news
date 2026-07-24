#!/usr/bin/env python3
"""Technology writer — 2026-07-04 06:00 PDT run.
3 articles: Oxmiq/Raja Koduri chip startup, I-2SEA undersea cable, India-Japan AI/semiconductor pacts.
"""
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
    # ── Article 1: Raja Koduri's Oxmiq raises $35M ──
    {
        "id": str(uuid.uuid4()),
        "headline": "Intel's Former Chief Architect Just Raised $60 Million to Build a GPU That Doesn't Need Nvidia.",
        "subheadline": "Raja Koduri's Oxmiq wants to license AI chip blueprints the way Arm licenses phone processors. Samsung, MediaTek and Pegatron are backing the bet.",
        "slug": make_slug("raja-koduri-oxmiq-ai-chip-gpu-arm-series-a"),
        "category": "technology",
        "vertical": "semiconductors",
        "diaspora_angle": "An Indian-origin semiconductor veteran is leading one of the most ambitious AI chip startups in Silicon Valley — a signal that Indian engineers are not just running Big Tech but founding the companies that could reshape its supply chain.",
        "tags": ["semiconductors", "ai-chips", "indian-tech-leaders", "silicon-valley", "startups"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/startup-oxmiq-raises-35-million-build-chip-architecture-lower-cost-ai-2026-07-02/"},
            {"name": "BusinessWire", "url": "https://www.businesswire.com/news/home/20260702"},
            {"name": "YourStory", "url": "https://yourstory.com/2026/07/raja-koduris-oxmiq-labs-bags-35m-in-series-a-funding"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/6755078/pexels-photo-6755078.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
        "image_caption": "Closeup of a microchip on a circuit board, representing the AI silicon architecture Oxmiq is building",
        "image_attribution": "Pexels",
        "body": """Raja Koduri spent three decades inside the semiconductor industry's biggest names. As Intel's chief architect and a senior executive at AMD before that, the Hyderabad-born engineer shaped the graphics processors that power everything from gaming rigs to supercomputers. Now he wants to blow up the model he helped build.

Oxmiq, the Campbell, California startup Koduri founded after leaving Intel, closed a $35 million Series A this week, bringing its total capital to $60 million. The round was co-led by Samsung Catalyst Fund and Fundomo, with MediaTek, AM Intelligence Labs, Pegatron Venture Capital, and Morgan Creek Digital among the investors. The backers read like a who's who of the companies that would benefit most from breaking Nvidia's grip on AI compute.

## The Pitch: One Core Instead of Three Chips

The conventional AI system splits its workload across three distinct pieces of silicon — a GPU for parallel computation, a CPU for orchestration, and a tensor engine for the matrix math that makes deep learning work. Building all three, plus the software to run them, can cost hundreds of millions of dollars and take years.

Oxmiq's answer is OxCore, a licensable GPU architecture that collapses all three engines into a single design. Think of it as a blueprint that chipmakers and AI infrastructure builders can license, customise, and manufacture without undertaking a full chip programme from scratch.

"We would want to be the Arm of this next era," Koduri told Reuters — a reference to the British firm whose chip designs run in virtually every smartphone on the planet. Where Arm licenses CPU cores, Oxmiq wants to license integrated GPU-plus-tensor-plus-CPU cores purpose-built for AI.

The architecture is already running on FPGAs, with live demonstrations available to potential licensees. OxCore was designed for near-memory compute — placing processing power physically closer to the data it needs, which slashes the energy wasted moving bits across a chip.

## Why It Matters for the Diaspora

Koduri is arguably the most senior Indian-origin semiconductor executive to make the leap from corporate leadership to startup founder in this AI cycle. His roster — IIT Bombay, AMD's graphics division, Apple's GPU team, Intel's accelerated computing group — traces a career path that thousands of Indian engineers in the Bay Area aspire to.

But the significance goes beyond biography. The AI chip market is expected to exceed $200 billion by 2030, yet it remains dominated by a handful of incumbents. Nvidia controls roughly 80 per cent of AI training chips. Broadcom, Marvell, and MediaTek lead the custom silicon business. If Oxmiq's licensing model works, it could open the door for smaller players — including Indian semiconductor startups riding the India Semiconductor Mission — to design competitive AI chips without billion-dollar budgets.

The timing is deliberate. "Token demand is outpacing the world's ability to build infrastructure to serve it," Oxmiq said in its announcement. As every major cloud provider, sovereign AI programme, and enterprise scrambles for compute, the bottleneck is increasingly not money but silicon IP. A licensable architecture that collapses three chip programmes into one could be the unlock.

## The Road Ahead

Oxmiq plans to use the Series A to finish its first batch of licensable intellectual property and hire engineers. Koduri has signalled the company will also enter the custom chip market, putting it in direct competition with Broadcom and Marvell — firms with multibillion-dollar revenues and established customer relationships.

For NRI investors and tech professionals tracking the semiconductor space, the bet is straightforward: if AI compute stays expensive, the industry needs more chip designers, not just more fabs. Koduri is betting that a $60 million startup with the right architecture can matter as much as a $60 billion incumbent with the wrong one."""
    },

    # ── Article 2: I-2SEA undersea cable ──
    {
        "id": str(uuid.uuid4()),
        "headline": "Microsoft and Tata Are Laying a 3,600-Kilometre Cable Under the Indian Ocean. The AI Race Demands It.",
        "subheadline": "The I-2SEA submarine cable will connect India's data centre clusters in Hyderabad and Chennai to Singapore, promising the lowest-latency AI corridor in the region by late 2029.",
        "slug": make_slug("microsoft-tata-i2sea-undersea-cable-india-singapore-ai"),
        "category": "technology",
        "vertical": "infrastructure",
        "diaspora_angle": "The cable lands at Machilipatnam — the same Andhra Pradesh coast where Google and Meta are building data centres — and will power the AI cloud services that NRIs in Southeast Asia and India increasingly depend on for work and daily life.",
        "tags": ["ai-infrastructure", "undersea-cable", "microsoft", "tata-communications", "india-data-centers"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/microsoft-partners-with-singapores-lightstorm-build-india-southeast-asia-undersea-2026-07-02/"},
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/info-tech/lightstorms-new-high-speed-subsea-cable-to-connect-indias-east-coast-to-malaysia-and-singapore/article69753283.ece"},
            {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/economy-and-policy/microsoft-led-consortium-to-build-ai-ready-undersea-cable-for-india"}
        ]),
        "score_total": 80,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/4508751/pexels-photo-4508751.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
        "image_caption": "Server racks inside a modern data centre, the kind of infrastructure the I-2SEA cable is designed to serve",
        "image_attribution": "Pexels",
        "body": """Ninety-five per cent of the world's internet traffic travels through submarine cables thinner than a garden hose. India has 17 of them. By 2029, it will have at least one more — and this one is built specifically for the artificial intelligence era.

A consortium led by Lightstorm, a Singapore-based connectivity platform, announced this week that it will construct the I-2SEA submarine cable, a 3,600-kilometre fibre-optic link connecting India's east coast to Singapore and Malaysia. The partners include Microsoft, Tata Communications, Singapore Telecommunications (Singtel), Japan's NEC Corporation, and Singapore's ASEAN Cableship.

The cable is designed from the ground up for AI training and inference workloads, cloud computing, and hyperscale data flows. It is expected to go live in the fourth quarter of 2029.

## The Route and the Logic

I-2SEA will have dual landings in India: one at Machilipatnam in Andhra Pradesh — offering the shortest subsea path to Hyderabad — and a second at South Chennai. Both cities are emerging as major data centre corridors. Machilipatnam sits on the same stretch of coast where Google's parent Alphabet and Meta have announced data centre campuses as part of a combined $32.5 billion investment in India.

The cable will then run to Kuala Lumpur and Singapore, the region's dominant cloud interconnect hub. Lightstorm says it will deliver latencies 10–15 per cent lower than any existing cable on the India–Singapore route — a margin that matters enormously for AI training workloads, where milliseconds compound into hours of wasted compute across thousands of GPUs.

"Based on whether you're calculating from the East or West Coast up to Singapore or Malaysia, the latencies with this cable will be about 10-15 percent lower than any other cable that is currently running in this ASEAN route," Amajit Gupta, Lightstorm's CEO, told The Hindu BusinessLine.

## India's Data Centre Boom

The announcement lands in the middle of an infrastructure sprint that is reshaping India's digital economy. Microsoft alone has committed $17.5 billion to India — its largest-ever investment in Asia. Alphabet is spending $15 billion on three data centre campuses in Visakhapatnam. Meta, Amazon, and OpenAI are adding capacity of their own.

India's operational data centre capacity currently stands at 1.4 gigawatts. Macquarie Equity Research estimates it could double by 2027 and grow fivefold by 2030 if planned projects are fast-tracked. Synergy Research Group projects India will account for 3 per cent of the world's data centre capacity within five years, up from 1.3 per cent today.

But data centres are only as useful as the pipes that connect them. India currently has 960 terabits per second in maximum submarine cable capacity, and at least 10 additional cables have been publicly announced. I-2SEA will plug directly into Lightstorm's 30,000-kilometre terrestrial fibre network, connecting over 80 data centres across Hyderabad, Chennai, Mumbai, Delhi, Bengaluru, and Kolkata.

## What NRIs Should Watch

For Indian professionals in Singapore, Malaysia, and across Southeast Asia, the cable means faster, more reliable access to AI services and cloud platforms hosted in India. For NRI investors, the infrastructure buildout represents one of the largest capital commitments global tech firms have ever made in the country.

Lightstorm, the majority owner of I-2SEA and an I Squared Capital-backed company, is planning an IPO in India by mid-2027, with reports suggesting a valuation target of up to $1.5 billion. That would make it one of India's first pure-play AI infrastructure companies to go public.

Tata Communications, already one of the world's largest submarine cable operators through its ownership of legacy networks, extends its infrastructure lead with this deal. For the Tata Group — which is simultaneously building India's first advanced semiconductor fab at Dholera, Gujarat — the I-2SEA partnership is another piece of a vertically integrated technology stack that stretches from silicon to submarine fibre.

The consortium did not disclose the investment size. But in a market where a single trans-Pacific cable can cost $300–500 million, the I-2SEA project represents a significant bet on India's digital future — one backed by some of the world's most powerful technology companies."""
    },

    # ── Article 3: India-Japan AI/semiconductor pacts ──
    {
        "id": str(uuid.uuid4()),
        "headline": "India and Japan Just Signed Their Biggest Tech Pact in a Decade. Semiconductors Are at the Centre.",
        "subheadline": "PM Modi and Japan's Takaichi sealed agreements on AI, chip manufacturing and critical minerals — with Japanese firms already partnering with Tata Electronics to build India's semiconductor supply chain.",
        "slug": make_slug("india-japan-ai-semiconductor-pact-modi-takaichi-summit"),
        "category": "technology",
        "vertical": "semiconductors",
        "diaspora_angle": "Japan's commitment to India's semiconductor ecosystem — from ROHM's silicon MOSFETs to Tokyo Electron's packaging technology — could create thousands of high-skill engineering jobs, offering NRI chip professionals a viable 'return to India' path for the first time.",
        "tags": ["india-japan", "semiconductors", "ai", "geopolitics", "tata-electronics"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/world/india-japan-sign-pacts-ai-metals-energy-after-modi-takaichi-talks-2026-07-02/"},
            {"name": "Livemint", "url": "https://www.livemint.com/news/india/india-japan-expected-to-announce-plans-to-deepen-cooperation-in-ai-semiconductor-11751374901825.html"},
            {"name": "Communications Today", "url": "https://communicationstoday.co.in/indias-chip-ambitions-get-japanese-support-before-modi-takaichi-talks/"},
            {"name": "DevDiscourse", "url": "https://www.devdiscourse.com/article/international/futuristic-and-limitless-partnership-india-japan-sign-agreements-on-economic-security-ai-defence-says-pm-modi"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/5/5f/The_official_portrait_of_Shri_Narendra_Modi%2C_the_Prime_Minister_of_the_Republic_of_India.jpg",
        "image_caption": "Prime Minister Narendra Modi, who signed bilateral agreements with Japan's PM Sanae Takaichi on AI and semiconductors",
        "image_attribution": "Wikimedia Commons",
        "body": """When Narendra Modi stood beside Sanae Takaichi in New Delhi on Thursday and declared that "Japan's precision technology and India's software capabilities will give new momentum to global AI development," the subtext was unmistakable. India needs chips. Japan can help build them. And both countries need each other more than ever.

The 16th India-Japan Annual Summit, held during Takaichi's first visit to India as Prime Minister, produced a stack of agreements covering artificial intelligence, semiconductor manufacturing, battery technology, critical minerals, defence co-development, and a joint economic security roadmap. At least 10 memoranda of understanding were signed across sectors.

But the centrepiece was technology — specifically, semiconductors and AI.

## The Chip Deal

Even before Takaichi landed in Delhi, major Japanese firms had begun placing bets on India's semiconductor ambitions. ROHM Co., a Kyoto-based chipmaker, announced a partnership with Tata Electronics to develop advanced silicon MOSFETs. Tokyo Electron, one of the world's largest semiconductor equipment makers, agreed to provide technological know-how for backend packaging, assembly, and testing at Tata's facilities.

These are not abstract memoranda. They are the kind of hands-on industrial collaboration that India's Semiconductor Mission 2.0 was designed to attract. The Union government is expected to approve an outlay of Rs 1.25 lakh crore (roughly $15 billion) for the programme, which supports greenfield chip fabs, advanced packaging plants, and workforce development. Twelve projects have already been approved, including Tata Electronics' fabrication plant at Dholera, Gujarat — which received Japanese investment commitments alongside Taiwanese partner PSMC.

India hosts around 1,400 Japanese companies today, compared with 30,000 in China. Modi's pitch at the India-Japan Economic Forum was pointed: he called for Japan's investment in India to cross 10 trillion yen over the next decade and for the number of Japanese companies in India to double in the same period.

## Why Japan Is Pivoting

Japan's urgency is driven by the same forces rattling every advanced economy. The United States has turned inward with tariffs and "America First" industrial policy. China, Japan's largest trading partner but also its strategic rival, is weaponising rare earth exports and building semiconductor self-sufficiency at speed. The CHIPS Act and its equivalents have turned chip manufacturing into a geopolitical contest.

For Japan, India offers something China increasingly does not: a growing market with aligned strategic interests, English-speaking engineering talent, and a government actively subsidising the semiconductor supply chain. Bilateral trade between the two countries reached $27.5 billion in fiscal year 2025-26. Japanese investment in India totalled $3.2 billion between April and December 2025.

Japan is already among India's largest infrastructure investors, backing the Mumbai-Ahmedabad high-speed rail corridor and a recent $1.6 billion deal for a 20 per cent stake in Yes Bank. The technology pacts signed this week add a new dimension — one where Japanese equipment expertise meets Indian engineering scale.

## The AI Layer

Beyond semiconductors, the two countries agreed to collaborate on artificial intelligence research and deployment. Modi framed the partnership as one where Japan's hardware precision and India's software depth could jointly shape the next generation of AI — a pointed claim given that India's GCC (global capability centre) ecosystem now houses over 2,100 centres employing half a million people, many of them doing AI and data work for multinational firms.

The summit also produced agreements on battery manufacturing, EV ecosystem development, mineral exploration for rare earths, and medical devices — all areas where supply chain resilience has become a national security concern for both countries.

## What It Means for NRIs

For Indian semiconductor professionals in the US and Japan — and there are tens of thousands — the India-Japan partnership creates a plausible path that did not exist three years ago. If Tata's Dholera fab reaches production with Japanese technology partners, and if the advanced packaging ecosystem scales alongside it, India will need experienced chip engineers. Many of them currently work at Intel, TSMC, Samsung, and GlobalFoundries offices in Arizona, Oregon, Texas, and Kumamoto.

The broader signal is structural. India's chip ambitions have been talked about for two decades. What has changed is that the money is committed, the fabs are under construction, and now the technology partners are named. Japan's bet on India is not theoretical — it is showing up in signed equipment deals and factory floors.

For NRI investors, Tata Electronics (a Tata Sons subsidiary) is not publicly listed, but the semiconductor supply chain it is building — from chip fabs to subsea cables to AI data centres — is one of the most consequential industrial plays in India today. Watch the ecosystem, not just the ticker."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-06-05 04:55 UTC run"""

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


# --- ARTICLE 1: Microsoft $3B India AI Investment ---

article1_body = """Satya Nadella flew into Bengaluru this week carrying a number large enough to stop a room: $3 billion, earmarked for cloud and AI infrastructure across India over the next two years. It is Microsoft's biggest single investment in the country, and it arrived wrapped in a broader promise to train ten million Indians in AI skills by 2030.

The announcement came from the stage at the Microsoft AI Tour, barely a day after Nadella met Prime Minister Narendra Modi in New Delhi to discuss technology strategy. The timing was deliberate. India is now Microsoft's second-largest developer community on GitHub — and is projected to become the largest by 2028, overtaking the United States. The $3 billion is a bet that those developers will build on Azure rather than anywhere else.

## The infrastructure play

Microsoft already operates three data centre regions in India. A fourth is scheduled to go live later this year. The fresh capital will expand capacity across all four, creating what Puneet Chandok, president of Microsoft India, called "a scalable AI computing ecosystem" for the country's startup and research communities.

The investment is separate from Microsoft's previously announced $80 billion global data centre spend for fiscal 2025, a distinction the company was careful to make. India gets its own cheque.

For NRIs watching from the Bay Area or New Jersey, the signal is hard to miss. Microsoft is not simply selling cloud subscriptions in India — it is building the physical backbone for AI development, the kind of infrastructure that makes "return to India" conversations at Diwali parties slightly less hypothetical.

## The skilling gambit

The training commitment — ten million people in five years, delivered through the second edition of Microsoft's ADVANTA(I)GE India programme — is both philanthropic and strategic. Every developer trained on Azure is a developer less likely to default to AWS or Google Cloud when launching a product. The programme covers AI fundamentals, cloud engineering, and advanced model deployment, and will be delivered through partnerships with Indian universities and state governments.

India's AI startup scene has exploded in the past eighteen months, with companies like Sarvam AI and Krutrim raising nine-figure rounds. But most still rely on international cloud providers for compute. Microsoft is positioning itself as the provider of choice by planting infrastructure close to where the demand is growing fastest.

## Why NRIs should care

The subtext runs deeper than cloud pricing. For the roughly 4.5 million Indian-origin professionals working in American tech, Microsoft's India push creates a parallel track. Engineers who have spent a decade building expertise on Azure and Copilot in Redmond now have a market where that expertise is in acute demand — and where Microsoft is spending billions to make the ecosystem viable.

Nadella, who grew up in Hyderabad before moving to the United States for graduate school, rarely plays the diaspora card explicitly. But the optics of an Indian-born CEO writing the largest technology cheque in Indian history are not lost on anyone. "India is rapidly becoming a leader in AI innovation," he said in Bengaluru, in a sentence that could just as easily have come from a venture capitalist's pitch deck.

The question is whether $3 billion is enough. India's AI compute demand is growing faster than any single company can build data centres. Amazon Web Services and Google Cloud are both expanding their Indian footprints aggressively, and homegrown players like Yotta are racing to fill gaps. Microsoft's advantage is that it arrived with both infrastructure and an installed base of developers who already know the tools.

For the Indian American engineer evaluating a transfer to Bengaluru or Hyderabad, the calculation just tilted a few degrees. The infrastructure is coming. The jobs are coming. The question is no longer whether India's AI moment is real, but whether it will arrive faster than the next H-1B renewal."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "Satya Nadella Just Wrote India a $3 Billion Cheque for AI. It's Microsoft's Biggest Bet on the Country Yet.",
    "subheadline": "The investment covers new data centres, expanded Azure capacity, and a promise to train ten million Indians in AI skills by 2030 — all announced days after Nadella met Modi in Delhi.",
    "slug": make_slug("satya-nadella-microsoft-3-billion-india-ai-investment"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Microsoft's largest-ever India investment creates a parallel career track for Indian-origin engineers in the US — Azure and Copilot expertise built in Redmond now has a booming market in Bengaluru and Hyderabad. For NRIs, it shifts the 'return to India' calculation.",
    "tags": ["microsoft", "satya-nadella", "india-ai", "cloud-infrastructure", "indian-tech"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "The Indian EYE", "url": "https://theindianeye.com/to-make-india-ai-first-satya-nadella-announces-usd-3-billion-investment-by-microsoft/"},
        {"name": "China Daily Asia", "url": "https://www.chinadailyasia.com/article/475123"},
        {"name": "Forbes India", "url": "https://www.forbesindia.com/article/explainers/satya-nadella-3-billion-investment-microsoft-cloud-ai-infrastructure-india/95633/1"},
        {"name": "Livemint", "url": "https://www.livemint.com/companies/news/microsofts-renewed-windows-push-a-shot-in-the-arm-for-indias-ai-developers-11780482554302.html"}
    ]),
    "score_total": 85,
    "status": "published",
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/78/MS-Exec-Nadella-Satya-2017-08-31-22_%28cropped%29.jpg/330px-MS-Exec-Nadella-Satya-2017-08-31-22_%28cropped%29.jpg",
    "image_caption": "Satya Nadella, Chairman and CEO of Microsoft",
    "image_attribution": "Wikimedia Commons",
    "body": article1_body.strip(),
    "is_editorial": False,
}


# --- ARTICLE 2: NVIDIA RTX Spark AI PC ---

article2_body = """Jensen Huang stood on the Computex stage in Taipei this week and did something NVIDIA has not attempted in over a decade: he pitched a PC chip. The RTX Spark is an ARM-based superchip that combines a 20-core Grace CPU, a Blackwell RTX GPU, and up to 128 gigabytes of unified memory in a package thin enough for a 14-millimetre laptop. It delivers one petaflop of AI performance — roughly the processing power that filled a server rack five years ago.

Laptops built on RTX Spark will ship this autumn from Dell, HP, Lenovo, and Microsoft's Surface line. Microsoft simultaneously unveiled the Surface Laptop Ultra, its most powerful Surface device ever, powered entirely by the new chip. On stage, Huang ran Forza Horizon 6 at 100 frames per second in 1440p — on battery, on Windows, on ARM.

The gaming demos were impressive. The AI pitch was more consequential.

## The on-device AI argument

RTX Spark can run AI models with up to 120 billion parameters locally, without touching the cloud. That is large enough to handle sophisticated coding assistants, document analysis, image generation, and multi-step agent workflows entirely on the device. No API calls. No subscriptions. No data leaving the machine.

"For forty years, you launched apps. Click. Type," Huang told the crowd. His argument is that the next era of computing is agentic — your laptop doesn't run applications so much as it runs AI agents that orchestrate applications on your behalf. RTX Spark is designed to be the hardware that makes that shift possible at the personal level.

NVIDIA built the chip in collaboration with MediaTek, which designed the custom CPU cores, and Microsoft, which optimised its Prism x86-to-ARM emulator specifically for the platform. The three-way collaboration means RTX Spark machines can run legacy Windows software through emulation while handling AI workloads natively — a combination that has historically been the weak point of ARM-based PCs.

## India's opening

For India's semiconductor ecosystem, the timing matters. The RTX Spark was designed in part by NVIDIA's growing engineering teams in Bengaluru and Hyderabad, and MediaTek operates significant design centres in the country. As NVIDIA scales production, the demand for chip designers, verification engineers, and AI software developers trained in ARM architectures will intensify.

Ashok Chandak, president of IESA and SEMI India, noted that while Intel and AMD will continue to dominate mainstream PCs, NVIDIA is well-positioned in premium AI PCs. India, he argued, can participate through its strengths in chip design, embedded software, AI development, and semiconductor R&D — with the opportunity lying in contributing to the global AI-PC ecosystem rather than manufacturing processors domestically.

The numbers are still niche. Premium AI PCs are expected to ship 20 to 40 million units annually by 2030, serving developers, engineers, and designers rather than the mass market. Total AI-capable PCs could hit 250 to 300 million units. But for an Indian engineer at NVIDIA earning between ₹1.3 crore and ₹3.4 crore annually on an H-1B visa — or contemplating a move back to the company's India operations — the RTX Spark represents a product line that did not exist six months ago and now needs an army of people to build.

## What changes

NVIDIA's data centre business generated $75.2 billion in its most recent quarter. A laptop chip line, even a wildly successful one, is a rounding error. But the strategic intent is not about laptop revenue. It is about owning the platform layer for personal AI — the same way NVIDIA came to own the platform layer for data centre AI.

If the bet works, every developer running local AI models will be running them on NVIDIA silicon. If it doesn't, the company still has the most profitable chip business in history to fall back on. For Indian tech professionals — the largest cohort of H-1B workers in the United States and one of NVIDIA's most aggressively recruited talent pools — it opens yet another surface area of work at a company that cannot hire fast enough."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "NVIDIA's RTX Spark Puts a Petaflop in a Laptop. Indian Engineers Helped Build It.",
    "subheadline": "The ARM-based superchip, unveiled at Computex 2026, runs 120-billion-parameter AI models locally and ships this autumn in devices from Dell, HP, Lenovo, and Microsoft.",
    "slug": make_slug("nvidia-rtx-spark-petaflop-laptop-ai-pc-computex"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "RTX Spark was co-designed by NVIDIA's India engineering teams in Bengaluru and Hyderabad, with MediaTek's Indian design centres contributing the CPU cores. For Indian H-1B engineers at NVIDIA — the company's fastest-growing visa cohort — it creates an entirely new product line to build careers around.",
    "tags": ["nvidia", "rtx-spark", "ai-pc", "computex-2026", "semiconductor", "indian-engineers"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "The Motley Fool", "url": "https://www.fool.com/investing/2026/06/04/nvidia-wants-to-reinvent-the-pc-intel-amd-qualcomm/"},
        {"name": "Gizmodo", "url": "https://gizmodo.com/two-years-after-copilot-nvidia-is-shoving-ai-into-pcs-again-2000607952"},
        {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com/info-tech/nvidias-ai-pc-push-may-open-opportunities-for-indias-semicon-ecosystem/article69650291.ece"},
        {"name": "MakeUseOf", "url": "https://www.makeuseof.com/makeuseof-computex-2026-picks/"}
    ]),
    "score_total": 82,
    "status": "published",
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/e/e6/Jen-Hsun_Huang_2025.jpg",
    "image_caption": "Jensen Huang, CEO of NVIDIA, who unveiled RTX Spark at Computex 2026",
    "image_attribution": "Wikimedia Commons",
    "body": article2_body.strip(),
    "is_editorial": False,
}


# --- ARTICLE 3: Indian Chip Startups at Bharat Innovates France ---

article3_body = """India still imports the vast majority of the semiconductors it uses. Three startups selected to represent the country at Bharat Innovates 2026 — a deep-tech showcase running 14 to 16 June in Nice, France — are trying to change that, one chip at a time.

VerveSemi, AGNIT Semiconductors, and Netrasemi were picked by the Ministry of Education to make the trip. Each occupies a different niche in the semiconductor stack, and together they represent the best evidence yet that India's chip ambitions have moved beyond government press releases and into functioning silicon.

## What each company builds

Netrasemi, founded in 2020 in Kerala, designs Edge AI system-on-chip processors built on TSMC's 12-nanometre node. Its chips target smart cameras, IoT devices, and embedded vision systems — the kind of silicon that powers India's booming surveillance and smart-city infrastructure. The company has moved its flagship chip into production, with samples in the hands of three customers running pilots. Commercial volumes are expected by mid-2027. Netrasemi raised ₹107 crore ($12.5 million) in a Series A led by Zoho and Unicorn India Ventures, and is doubling its engineering workforce to 166.

VerveSemi, based in Noida and founded in 2017, builds analog signal-chain integrated circuits — the less glamorous but essential components that sit between sensors and processors in virtually every electronic device. The company has raised $10.1 million across multiple rounds. Co-founder Pratap Narayan Singh framed the opportunity bluntly: India imports chips on a massive scale, and building domestically is the natural next step.

AGNIT Semiconductors operates in one of the most strategically sensitive corners of chipmaking: gallium nitride (GaN) components used in defence applications. The company has three pilots running with defence public sector units and private firms, with volumes expected to reach 5,000 to 10,000 chips within nine months. GaN chips are critical for drone communications, electronic jammers, and radio systems — areas where India's military has been eager to reduce dependence on foreign suppliers.

## The policy machinery behind them

None of these startups would exist in their current form without the India Semiconductor Mission, launched in December 2021, and the Design-Linked Incentive scheme that followed. The DLI provides funding for chip design work; the Production Linked Incentive scheme backs manufacturing. Between them, they have done something that seemed unlikely five years ago: they made "I'm building a semiconductor company in India" a sentence that investors take seriously.

The journey from prototype to production in semiconductors typically takes three to four years. Indian startups are compressing that timeline, but they still face a fundamental market problem. Without deliberate government procurement policies that give Indian buyers a reason to source locally, cheaper Taiwanese and Chinese alternatives will continue to dominate. The government's ban on uncertified Chinese CCTV cameras opened a window for domestic chip companies; the industry wants similar signals across telecom, automotive, and defence.

## Why NRIs are watching

For Indian Americans working in semiconductor design at Qualcomm in San Diego, Intel in Hillsboro, or NVIDIA in Santa Clara, these startups represent something unfamiliar: a domestic Indian chip industry that actually ships products. The talent pipeline is thin — India produces plenty of chip designers but has had nowhere for them to build careers without moving abroad. Companies like Netrasemi and VerveSemi are beginning to change that equation.

The showcase in Nice is modest by global standards — three startups at an educational technology event, not a booth at Computex. But it comes at a moment when the geopolitics of semiconductors have never been more favourable for India. The world is actively looking for alternatives to Taiwan-concentrated supply chains. India has the engineers. It is starting to have the companies. Whether it can build the manufacturing base to match remains the $180 billion question — the figure NITI Aayog recently estimated the country needs to invest to build a full semiconductor industry.

For now, three startups are packing their chips for France. It is a small step, but it is made of silicon."""

article3 = {
    "id": str(uuid.uuid4()),
    "headline": "Three Indian Chip Startups Are Taking India's Silicon Story to France",
    "subheadline": "VerveSemi, AGNIT Semiconductors, and Netrasemi will showcase homegrown chips at Bharat Innovates 2026 in Nice — the latest sign that India's semiconductor ambitions are producing actual products.",
    "slug": make_slug("indian-chip-startups-france-bharat-innovates-vervesemi-agnit"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "For Indian Americans working in semiconductor design at Qualcomm, Intel, or NVIDIA, these startups represent a domestic Indian chip industry that actually ships products — and a potential career path that doesn't require leaving India.",
    "tags": ["semiconductor", "indian-startups", "vervesemi", "agnit", "netrasemi", "india-semiconductor-mission"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "YourStory", "url": "https://yourstory.com/2026/06/3-indian-semiconductor-startups-are-taking-indias-chip-story-to-france"},
        {"name": "Communications Today", "url": "https://communicationstoday.co.in/indias-semiconductor-moment-from-diplomatic-frameworks-to-factory-floors/"},
        {"name": "TechGig", "url": "https://content.techgig.com/technology-unplugged/5-indian-semiconductor-startups-powering-indias-100-billion-chip-mission/articleshow/115048825.cms"},
        {"name": "Nishith Desai Associates (IDTA Report)", "url": "https://www.nishithdesai.com/Category/33/Information-Technology/33/1/AllContent/4982/15/AI-Deep-Tech.html"}
    ]),
    "score_total": 72,
    "status": "published",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/6755078/pexels-photo-6755078.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "Microchips and circuits on a circuit board, representative of the semiconductor components Indian startups are designing",
    "image_attribution": "Pexels",
    "body": article3_body.strip(),
    "is_editorial": False,
}


# --- INSERT ALL ---

articles = [article1, article2, article3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

print(f"\nDone. {len(articles)} articles processed.")

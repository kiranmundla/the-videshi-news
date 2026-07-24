#!/usr/bin/env python3
"""Technology writer — 2026-07-09 06:00 PT run.
Three articles: Skyroot space unicorn, SambaNova $1B inference chips, HrdWyr AI edge chips.
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


# ── Article 1: Skyroot Aerospace ──────────────────────────────────────────

skyroot_body = """India's private space race just produced its first unicorn. Skyroot Aerospace, the Hyderabad-based rocket startup founded by two former ISRO scientists, has closed a $60 million funding round that values the company at $1.1 billion — making it the most well-funded private space venture in the country.

The round was co-led by Sherpalo Ventures, the investment firm of Ram Shriram, and Singapore's sovereign wealth fund GIC. BlackRock, Arkam Ventures, Playbook Partners, the Shanghvi Family Office, and the founders of renewable energy giant Greenko Group also participated.

## The Shriram connection

Shriram's involvement is the detail that matters most for the diaspora. The Indian-American billionaire, who was among Google's earliest investors and has served on Alphabet's board since its founding, is doubling down on Indian deep tech after years of quietly building positions in the country's startup ecosystem.

"I've believed in the Skyroot team since the early days," Shriram said in a statement. "Skyroot is building the foundational infrastructure for access to space with the best cost-to-performance ratio."

His co-lead alongside a sovereign wealth fund of GIC's calibre sends a clear signal to NRI investors: India's space-tech sector is no longer a science project. It is an asset class.

## What Skyroot actually does

Founded in 2018 by Pawan Kumar Chandana and Naga Bharath Daka, both alumni of the Indian Space Research Organisation, Skyroot builds small satellite launch vehicles. The company made history in November 2022 with the launch of Vikram-S, India's first privately developed rocket, under its aptly named Mission Prarambh — Hindi for "the beginning."

The fresh capital will fund high-cadence launches of its Vikram-1 orbital rocket, scale manufacturing capacity, and bankroll the development of Vikram-2, a heavier vehicle with a cryogenic upper stage capable of placing one-tonne payloads into orbit. Chandana has called the upcoming Vikram-1 launch "India's first private orbital rocket."

## Why NRIs should pay attention

India's space economy is projected to reach $44 billion by 2033, according to the Indian Space Association, up from roughly $8 billion today. The government's 2020 decision to open the sector to private companies has unleashed a wave of startups — Agnikul Cosmos, Pixxel, Dhruva Space — but Skyroot is the first to cross the billion-dollar threshold.

For diaspora investors, the opportunity goes beyond sentiment. Skyroot's total funding now exceeds $160 million, and a listing — likely on Indian exchanges — could be on the horizon within the next two to three years if the company hits its launch cadence targets. The combination of GIC, BlackRock, and Shriram on the cap table suggests the institutional scaffolding for a public offering is already being built.

India's space-tech sector is also increasingly intertwined with the semiconductor and AI ecosystems that NRI professionals inhabit daily. Small satellite constellations generate vast amounts of Earth observation data that feed into agriculture, logistics, defence, and climate modelling — sectors where India's AI startups are already building products.

## The bigger picture

Skyroot's unicorn moment coincides with a broader shift in India's technology ambitions. The country now has three operational chip plants, a rapidly growing AI talent pipeline, and — with Skyroot — a credible private launch capability. For a generation of Indian engineers who built their careers at SpaceX, Blue Origin, and Rocket Lab in the West, the pull of building something comparable at home just got considerably stronger.

The question is no longer whether India can compete in private space. It is how quickly the ecosystem can scale to match the ambition."""

skyroot_sources = json.dumps([
    {"name": "The Indian Eye", "url": "https://theindianeye.com/skyroot-aerospace-becomes-indias-first-space-tech-unicorn/"},
    {"name": "Reuters", "url": "https://www.reuters.com/technology/"},
    {"name": "Indian Space Association", "url": "https://www.indianspaceassociation.com/"}
])

# ── Article 2: SambaNova $1B raise ────────────────────────────────────────

sambanova_body = """The AI chip race just got its biggest challenger to Nvidia since AMD. SambaNova Systems, the Palo Alto-based semiconductor startup, has raised $1 billion in a Series F round led by General Atlantic, pushing its valuation to $11 billion — more than double its $5.1 billion mark from 2021.

The round included Seligman Ventures, T. Rowe Price Associates, Capital Group, BlackRock, Intel Capital, and the Qatar Investment Authority. It brings SambaNova's total funding to roughly $2.5 billion, making it one of the most heavily capitalised AI chip companies in the world.

## Inference is the game now

SambaNova builds custom chips, hardware systems, and cloud services tailored specifically for inference — the process by which trained AI models respond to queries in real time. If training is the expensive upfront cost of building an AI brain, inference is the ongoing electricity bill that keeps the lights on. It is where the money is, and where Nvidia's dominance is most vulnerable.

JPMorgan Chase, one of the largest employers of Indian-American technologists on Wall Street, has already selected SambaNova as its inference infrastructure partner. The bank will deploy SambaNova's SN40 and SN50 systems for on-premises AI inference — a telling choice for an institution that processes millions of transactions daily and cannot afford the latency of cloud-based alternatives.

## The Intel angle

Intel's deepening entanglement with SambaNova is the subplot worth watching. Intel CEO Lip-Bu Tan serves as SambaNova's executive chairman, and Intel Capital's stake now sits at approximately 9 per cent after a $35 million investment in February that received US antitrust clearance in May. The chipmaker had previously explored acquiring SambaNova outright for roughly $1.6 billion, but those talks stalled.

For the tens of thousands of Indian engineers employed at Intel — the company holds over 2,000 approved H-1B petitions annually — this is not abstract corporate strategy. Intel's bet on inference through SambaNova represents a strategic pivot that could reshape headcount, project allocation, and career trajectories within the company.

## What this means for India's AI startups

The timing is pointed. Just days ago, reports highlighted that India's AI startups cannot buy enough GPUs to compete globally, with compute scarcity emerging as a binding constraint on the country's AI ambitions. SambaNova's pitch — faster, cheaper inference at scale — speaks directly to this bottleneck.

If SambaNova's SN50 chip delivers on its promise of dramatically lower cost-per-query compared to Nvidia's GPUs, the implications for India are significant. Startups like Sarvam AI, Krutrim, and BharatGPT, which have been rationing compute, could deploy models at a fraction of the current cost. Enterprise adoption of AI across Indian banks, hospitals, and government agencies — where latency and data sovereignty matter — would accelerate.

The inference market is expected to surpass training in total chip spend by 2027, according to multiple industry forecasts. SambaNova is betting that the next phase of the AI race will not be won by the company with the most powerful training cluster, but by the one offering the cheapest, fastest way to serve a billion queries.

## The investment case for NRIs

SambaNova at $11 billion is almost certainly on an IPO trajectory. General Atlantic, T. Rowe Price, and Capital Group are exactly the kind of crossover investors who position ahead of public offerings. For NRI investors who rode the Nvidia wave and are looking for the next AI infrastructure play, SambaNova's single-minded focus on inference — combined with Intel's backing and JPMorgan's endorsement — presents one of the more compelling pre-IPO bets in the semiconductor space.

The AI chip landscape is fracturing. OpenAI has its Jalapeno chip with Broadcom. Anthropic is weighing its own silicon. DeepSeek in China is building custom inference chips. SambaNova's $1 billion war chest is its answer to all of them — and the inference wars are just beginning."""

sambanova_sources = json.dumps([
    {"name": "Reuters", "url": "https://www.reuters.com/technology/sambanova-raises-1-billion-funding-round-2026-07-08/"},
    {"name": "Intellectia.ai", "url": "https://intellectia.ai/"},
    {"name": "The Information", "url": "https://www.theinformation.com/"}
])

# ── Article 3: HrdWyr AI chips ────────────────────────────────────────────

hrdwyr_body = """India's semiconductor ambitions have so far been measured in fabs — packaging plants in Sanand, assembly lines in Dholera, the political photo ops of a chip rolling off a production line. But the higher-value, higher-margin end of the semiconductor business is not in manufacturing. It is in design. And a Bengaluru startup just raised $13 million to prove India can compete there too.

HrdWyr, founded by veteran semiconductor engineer Ramamurthy Sivakumar, has closed a Series A round led by Ideaspring Capital with participation from Singularity AMC, Avatar Growth Capital, and Persistent Systems, the Indian IT services firm that has been aggressively pivoting toward deeper technology bets. The company builds AI-native System-on-Chip processors — custom silicon designed from the ground up for edge computing, where AI models run directly on devices rather than in distant data centres.

## Why edge, not cloud

The conventional AI stack sends data to the cloud, processes it on Nvidia GPUs, and returns the result. It works for ChatGPT prompts from a laptop in Palo Alto. It does not work for an electric vehicle navigating Bengaluru traffic at 60 kilometres per hour, or a factory floor robot that cannot tolerate 200 milliseconds of latency, or a smart thermostat that should not be uploading your home's temperature data to a server farm in Virginia.

Edge AI chips process data locally, on the device itself, with dramatically lower power consumption and near-zero latency. This is the market HrdWyr is targeting — and it is growing fast. Industry estimates put the edge AI chip market at $30 billion by 2028.

"The real power of AI will be unlocked as we enter the era of Physical AI, where advanced intelligence seamlessly integrates with real-world systems," Sivakumar said. "This inflection point demands a fundamental rethinking of how computing systems are conceived, architected, and deployed."

## The Persistent Systems connection

The most telling name on HrdWyr's cap table is Persistent Systems. The Pune-based IT services company, which just made headlines with its $1.4 billion acquisition of Germany's Nagarro, has been quietly building a portfolio of deep-tech investments. Its backing of HrdWyr signals a thesis that India's IT industry — which built its $315 billion empire on software services — is now reaching into the hardware layer.

Dr Anand Deshpande, Persistent's founder and managing director, put it plainly: "AI-led transformation is driving a fundamental shift in how the technology stack is built, with increasing convergence between semiconductors, data, and intelligent software systems."

For the tens of thousands of Indian engineers at Persistent, TCS, Infosys, and their peers who have spent careers writing code that runs on other people's chips, this convergence is potentially career-altering.

## The diaspora angle

HrdWyr's leadership team brings more than 250 years of combined semiconductor experience across India, the United States, Europe, and Israel. This is not a coincidence. India's fabless chip design ecosystem is being built, in large part, by engineers who cut their teeth at Qualcomm, Intel, Texas Instruments, and Broadcom in the West, and are now channelling that expertise back home.

The company has already partnered with boAt, the Indian audio and wearable brand that has become a household name among young Indians globally. If HrdWyr's chips end up inside the next generation of boAt earbuds, it would mark one of the first times a consumer product used by millions of NRIs runs on Indian-designed silicon.

## The bigger semiconductor picture

India's Semiconductor Mission, launched in 2021, has so far delivered three operational OSAT and packaging plants. But the government's long-term vision — articulated repeatedly by Prime Minister Modi — extends to chip design and eventually fabrication. HrdWyr represents the design layer, and at $13 million in Series A funding, it is still early. The question is whether India's fabless chip design ecosystem can scale to produce companies that compete with the likes of MediaTek, Marvell, and Qualcomm.

The odds are long. But the talent pool is deep, the capital is arriving, and the strategic logic is sound. India cannot be a serious AI power if it depends entirely on foreign silicon. HrdWyr is a small bet that the dependency will not last."""

hrdwyr_sources = json.dumps([
    {"name": "Analytics Insight", "url": "https://www.analyticsinsight.net/news/startup-semiconductor-startup-hrdwyr-advances-ai-native-chip-design-with-fresh-13-million-funding"},
    {"name": "Persistent Systems", "url": "https://www.persistent.com/"},
    {"name": "India Semiconductor Mission", "url": "https://www.indiasmconductormission.com/"}
])

# ── Build articles list ───────────────────────────────────────────────────

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "India's First Space-Tech Unicorn Just Landed. A Google Founding Investor Put Up the Money.",
        "subheadline": "Skyroot Aerospace hits $1.1 billion after a $60 million round co-led by Ram Shriram's Sherpalo and Singapore's GIC, signalling that India's private rocket sector is ready for institutional capital.",
        "slug": make_slug("skyroot-aerospace-unicorn-ram-shriram-space-india"),
        "category": "technology",
        "vertical": "space-tech",
        "diaspora_angle": "Ram Shriram, the Indian-American billionaire who was among Google's earliest investors, co-led the round — a signal that diaspora capital is fuelling India's deepest tech bets beyond SaaS.",
        "tags": ["space-tech", "skyroot", "ram-shriram", "india-startup", "unicorn", "gic"],
        "urgency": "medium",
        "sources": skyroot_sources,
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/9/90/Vikram-S_rocket%27s_Mission_Prarambh_04.webp",
        "image_caption": "Skyroot Aerospace's Vikram-S rocket during Mission Prarambh, India's first private rocket launch",
        "image_attribution": "Wikimedia Commons",
        "body": skyroot_body,
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The Startup JPMorgan Chose Over Nvidia for AI Inference Just Raised $1 Billion.",
        "subheadline": "SambaNova Systems hits $11 billion after a General Atlantic-led round, with Intel's CEO as chairman and BlackRock on the cap table. The inference chip wars are officially here.",
        "slug": make_slug("sambanova-billion-inference-chips-nvidia-jpmorgan"),
        "category": "technology",
        "vertical": "ai-chips",
        "diaspora_angle": "Intel — which sponsors over 2,000 H-1B workers annually — owns 9% of SambaNova, and JPMorgan, a top employer of Indian-American technologists, is its anchor customer. Cheaper inference chips could also unlock AI deployment for India's compute-starved startups.",
        "tags": ["ai-chips", "sambanova", "nvidia", "inference", "jpmorgan", "intel", "semiconductor"],
        "urgency": "medium",
        "sources": sambanova_sources,
        "score_total": 76,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/37052613/pexels-photo-37052613.jpeg",
        "image_caption": "Close-up of a microprocessor circuit board, the battleground for AI inference chip startups challenging Nvidia",
        "image_attribution": "Pexels",
        "body": sambanova_body,
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India Has Three Chip Plants. Now a Bengaluru Startup Wants to Design the Chips That Go Inside Them.",
        "subheadline": "HrdWyr raises $13 million to build AI-native edge processors, backed by Persistent Systems and a team with 250 years of semiconductor experience from Intel, Qualcomm, and Texas Instruments.",
        "slug": make_slug("hrdwyr-india-ai-chip-design-edge-persistent"),
        "category": "technology",
        "vertical": "semiconductors",
        "diaspora_angle": "HrdWyr's leadership draws on semiconductor experience from Intel, Qualcomm, and TI in the US — a reverse brain drain that could put Indian-designed silicon inside consumer products used by millions of NRIs.",
        "tags": ["semiconductors", "india-chips", "edge-ai", "hrdwyr", "persistent-systems", "make-in-india"],
        "urgency": "low",
        "sources": hrdwyr_sources,
        "score_total": 68,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/2105927/pexels-photo-2105927.jpeg",
        "image_caption": "Close-up of a processor chip, representative of India's growing semiconductor design ambitions",
        "image_attribution": "Pexels",
        "body": hrdwyr_body,
    },
]

# ── Insert ────────────────────────────────────────────────────────────────

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

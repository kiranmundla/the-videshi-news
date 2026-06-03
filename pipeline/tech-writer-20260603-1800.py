#!/usr/bin/env python3
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# Load env
env_file = Path.home() / "workspace" / ".env.supabase"
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
    # ── Article 1: Nikesh Arora / Palo Alto Networks Q3 Earnings ──
    {
        "id": str(uuid.uuid4()),
        "headline": "Nikesh Arora's Palo Alto Networks Just Hit $3 Billion in a Quarter. AI Is the Reason.",
        "subheadline": "The Indian-origin CEO reported 31% revenue growth and $8.1 billion in next-gen security ARR, as enterprises scramble to lock down their AI deployments before someone else does.",
        "slug": make_slug("nikesh-arora-palo-alto-networks-q3-ai-cybersecurity"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Nikesh Arora, one of the highest-profile Indian-origin CEOs in American tech, is running the company that has become the default security layer for enterprise AI. For Indian cybersecurity professionals in the US, this quarter signals a hiring tailwind — Palo Alto added 800 customer engagements for its AI defense unit in six weeks. For NRI investors, the stock's path from $200B to $250B in market cap is a direct bet on whether Indian leadership can capture the AI security premium before CrowdStrike, Zscaler, or anyone else does.",
        "tags": ["nikesh-arora", "palo-alto-networks", "cybersecurity", "ai-security", "indian-ceo", "earnings"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "MarketWatch", "url": "https://www.marketwatch.com/"},
            {"name": "Morningstar", "url": "https://www.morningstar.com/"},
            {"name": "Palo Alto Networks Press Release", "url": "https://www.paloaltonetworks.com/"},
            {"name": "The Motley Fool", "url": "https://www.fool.com/"}
        ]),
        "score_total": 85,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/e/ea/Nikesh_Arora_TechCrunch_Disrupt_2015.jpg",
        "body": """Palo Alto Networks reported fiscal third-quarter results on Tuesday that beat Wall Street on every metric that matters, and the message from CEO Nikesh Arora was blunt: AI is rewriting the rules of cybersecurity faster than most enterprises can keep up.

Revenue hit $3.0 billion for the quarter ended April 30, up 31% year over year and ahead of the $2.94 billion analysts had expected. Next-Generation Security annual recurring revenue — the metric Arora has staked his strategy on — reached $8.1 billion, a 60% leap from a year ago. Remaining performance obligations, the clearest signal of locked-in future revenue, expanded 36% to $18.4 billion.

## The AI security thesis, validated

"The latest advancements at the AI frontier have increased the level of urgency around cybersecurity, and redefined the shape of the industry for the coming years," Arora said in the earnings release. It is a characteristically restrained statement from a CEO who has spent three years methodically turning Palo Alto from a firewall vendor into a platform company.

The logic is straightforward. Every enterprise deploying large language models, agentic workflows, and AI-driven automation is simultaneously expanding its attack surface at a rate that legacy point solutions cannot defend. Arora's pitch — consolidate your security stack on one platform, or watch the gaps multiply — is landing with increasing force. The company closed an $80 million deal with a leading US power producer and a $20 million-plus agreement with a global consulting firm, both centred on its Prisma AIRS offering for AI infrastructure.

Perhaps the most telling number: Palo Alto's new Unit 42 Frontier AI Defense service, launched during the quarter, generated over 800 customer meetings in its first six weeks. Arora revealed that the company used partnerships with frontier AI labs to complete the equivalent of a year's worth of penetration testing in less than three weeks — using AI to stress-test AI.

## Guidance raised, market cap crosses $200 billion

The company lifted its full-year revenue guidance to $11.42–$11.43 billion, up from the prior range of $11.28–$11.31 billion. Fourth-quarter revenue is projected between $3.35 billion and $3.36 billion, above the $3.28 billion consensus. Adjusted free cash flow margin held steady, with CFO Dipak Golechha reaffirming the path to 40% by fiscal 2028.

Last week, Palo Alto's market capitalisation crossed $200 billion for the first time. Even after a modest 3% dip in extended trading on Tuesday — the market's reflexive response to a stock that has run hard — the implied valuation sits above $250 billion. Arora, who joined the company in 2018 after a long stint at Google and SoftBank, has now overseen a roughly tenfold increase in the stock.

## What this means for Indian tech professionals

For the thousands of Indian-origin cybersecurity professionals working in the US — from SOC analysts at Fortune 500 firms to threat researchers at startups — Arora's results are a signal flare. The AI security market is entering its high-growth phase, and the company with the most comprehensive platform is being led by someone who took the same IIT-to-Silicon-Valley path that many of them did.

More practically, Palo Alto's aggressive hiring for its AI defense and platformisation initiatives means a widening funnel of roles for security engineers, AI researchers, and platform architects — disproportionately filled by Indian professionals on H-1B and L-1 visas. When the company with the largest cybersecurity market cap is expanding headcount while others are cutting, the signal matters.

For NRI investors tracking the Magnificent Seven and beyond, Palo Alto's trajectory offers a different kind of AI bet. Not a chip company riding training demand, not a cloud hyperscaler spending $80 billion on data centres, but the company that sells the locks and alarm systems to everyone building those data centres. The question is whether Arora can sustain 30%-plus growth as the base gets larger. His Q3 numbers suggest the answer, for now, is yes."""
    },

    # ── Article 2: Agnikul Cosmos 3D-Printed Rocket Engine Quick-Start ──
    {
        "id": str(uuid.uuid4()),
        "headline": "Agnikul Cosmos Just Quick-Started a 3D-Printed Rocket Engine in 18.85 Seconds. No One Else Has Done This.",
        "subheadline": "The Chennai startup founded by IIT Madras engineers has demonstrated a rapid ignition capability for its Agnite engine, moving India's private space industry closer to the kind of launch frequency that makes commercial spaceflight viable.",
        "slug": make_slug("agnikul-cosmos-3d-printed-engine-quick-start-india-space"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Agnikul's founders are IIT Madras alumni, and the company has attracted talent from the Indian diaspora — engineers who left ISRO and global aerospace firms to build something from scratch in Chennai. For NRIs watching India's deep-tech ecosystem from afar, this is the kind of milestone that used to happen only at SpaceX or Rocket Lab. The broader significance: India now has two private rocket companies (Agnikul and Skyroot, the country's first space-tech unicorn at $1.1 billion) approaching orbital capability. For diaspora investors and engineers considering a return, space tech is becoming one of India's most credible deep-tech verticals.",
        "tags": ["agnikul-cosmos", "india-space", "3d-printing", "iit-madras", "rocket-engine", "deep-tech", "skyroot"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Inshorts", "url": "https://inshorts.com/en/news/chennai-based-agnikul-quickstarts-3d-printed-rocket-engine-in-1885-sec"},
            {"name": "3Druck.com", "url": "https://3druck.com/en/"},
            {"name": "Analytics Insight", "url": "https://www.analyticsinsight.net/"},
            {"name": "TechSpot", "url": "https://www.techspot.com/"}
        ]),
        "score_total": 72,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/586032/pexels-photo-586032.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "body": """Chennai-based Agnikul Cosmos announced on Tuesday that it has successfully demonstrated a quick-start capability for its Agnite rocket engine, reaching steady state in 18.85 seconds. The engine is a single-piece, fully 3D-printed semi-cryogenic unit — the only one of its kind in the world — and the test represents a critical step toward the kind of rapid, repeatable launch operations that separate experimental rocketry from commercial spaceflight.

The milestone matters more than it might seem. Quick-start capability — the ability to ignite an engine and reach operational thrust quickly — is one of the prerequisites for launch-on-demand services, where customers need their satellite in orbit within days, not months. "From here on, the acceleration of engines to reach steady state will likely consume lesser and lesser fuel," the company said in its announcement.

## The IIT Madras connection

Agnikul was founded in 2017 by Srinath Ravichandran, Moin SPM, and Professor Satyanarayanan R. Chakravarthy from IIT Madras's National Centre for Combustion Research and Development. The company emerged from the institute's deep expertise in propulsion and combustion, and it has stayed true to a first-principles approach: build the engine yourself, from one piece of metal, using additive manufacturing.

The Agnite engine uses liquid propellant — sub-cooled oxygen and kerosene — which distinguishes it from the solid-fuel motors used in most traditional launch vehicles. The entire unit is manufactured as a single component from Inconel, a nickel-chromium superalloy, using large-format additive manufacturing (LFAM). No welding. No assembly of dozens of machined parts. One piece, straight from the printer to the test stand.

This is not purely academic. The manufacturing approach has direct commercial implications. Traditional rocket engines require months of machining, welding, and assembly. A 3D-printed single-piece engine can, in principle, be produced in days. For a company targeting affordable small-satellite launch services — payloads of 30 to 300 kilograms to low Earth orbit — unit economics depend on how fast you can make engines and how quickly you can turn around between launches.

## The broader Indian space race

Agnikul is not alone. Skyroot Aerospace, founded in Hyderabad by former ISRO engineers, became India's first space-tech unicorn after raising $60 million at a $1.1 billion valuation. Skyroot launched Vikram-S, India's first privately built rocket, in 2022 and is now preparing Vikram-1 for an orbital mission. Together, the two companies have created something that did not exist five years ago: a credible private launch industry in India, supported by the regulatory infrastructure that IN-SPACe and the Indian Space Research Organisation have built.

The quick-start test follows another milestone from the previous month, when Agnikul synchronously ignited three semi-cryogenic engines — a cluster test that validates the propulsion architecture for its full Agnibaan orbital vehicle. The two-stage Agnibaan is designed to carry up to 300 kg to 700 km altitude, with a mobile launchpad called Dhanush that can operate from multiple spaceports.

## Why NRIs should care

For the Indian diaspora, the significance is layered. At the engineering level, Agnikul and Skyroot are attracting talent that would previously have gone to SpaceX, Blue Origin, or Rocket Lab. Ravichandran himself has spoken about building "original space-worthy hardware in India" — not licence-manufactured, not assembled from imported kits, but designed and built from scratch in Chennai.

At the investment level, India's space-tech sector is projected to reach $13 billion by 2025, according to the Indian Space Association. The combination of low labour costs, deep engineering talent, and growing government support makes it one of the few deep-tech verticals where India has a genuine structural advantage.

For NRI investors and returning professionals, the message is increasingly clear: India's private space industry is no longer an aspiration. It is an engineering reality, producing hardware that works, tested in real fire. The next milestone — an orbital launch — will determine whether that engineering reality becomes a commercial one."""
    },

    # ── Article 3: NVIDIA RTX Spark vs Qualcomm AI PCs ──
    {
        "id": str(uuid.uuid4()),
        "headline": "NVIDIA Just Invaded Qualcomm's AI PC Territory. Thousands of Indian Engineers Are Caught in the Crossfire.",
        "subheadline": "Jensen Huang's RTX Spark chip, unveiled at Computex alongside MediaTek, delivers 100+ TOPS and threatens to undo Qualcomm's hard-won Windows-on-Arm advantage — a shift that ripples directly through Hyderabad, Bengaluru, and San Diego.",
        "slug": make_slug("nvidia-rtx-spark-qualcomm-ai-pc-indian-engineers"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Qualcomm employs tens of thousands of engineers in India — in Hyderabad, Bengaluru, Chennai, and Noida — many of them working on the Snapdragon chip platform that NVIDIA's RTX Spark now directly threatens. In San Diego, Indian-origin engineers on H-1B visas form a significant portion of Qualcomm's US workforce. If Qualcomm loses share in the AI PC market it helped create, the downstream effects on hiring, project allocation, and visa sponsorship will be felt disproportionately by Indian professionals on both sides of the Pacific.",
        "tags": ["nvidia", "qualcomm", "rtx-spark", "ai-pc", "computex", "snapdragon", "indian-engineers", "h1b"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Stocktwits", "url": "https://stocktwits.com/"},
            {"name": "AInvest", "url": "https://www.ainvest.com/"},
            {"name": "MarketBeat", "url": "https://www.marketbeat.com/"},
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/"}
        ]),
        "score_total": 80,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c9/Jensen_Huang_at_Computex_Taipei_20100531.jpg/1280px-Jensen_Huang_at_Computex_Taipei_20100531.jpg",
        "body": """Computex 2026 was supposed to be Qualcomm's moment. CEO Cristiano Amon took the stage in Taipei, unveiled a new data-centre brand called Dragonfly, and declared 2026 "the year of agents." Hours later, Jensen Huang walked onto his own stage, announced the RTX Spark — NVIDIA's first Arm-based Windows PC processor — and effectively told the market that the AI PC category Qualcomm helped pioneer now belongs to everyone.

Qualcomm's stock dropped 7% the next morning. It had rallied 40% in May on AI optimism. The correction was swift and specific: investors decided that Amon's keynote was a "menu with no food" — branding without specifications — while Huang's came with full specs, confirmed launch partners (Dell, HP, Lenovo, Microsoft), and a shipping window for autumn.

## What RTX Spark actually threatens

The numbers tell the story. NVIDIA's RTX Spark delivers over 100 TOPS (trillion operations per second) of AI compute on-device. Qualcomm's current flagship, the Snapdragon X Elite, offers 45 TOPS. That is not a marginal gap. It is a generational one.

RTX Spark is co-developed with MediaTek and runs on Arm architecture — the same foundation Qualcomm has spent years building its Windows-on-Arm ecosystem around. But NVIDIA brings something Qualcomm cannot match: a software ecosystem that millions of developers, gamers, and AI researchers already trust. CUDA, the parallel computing framework that runs on NVIDIA GPUs, is the de facto standard for AI workloads. Porting that ecosystem to an Arm-based laptop chip gives RTX Spark a developer advantage that no amount of Snapdragon benchmark improvements can replicate overnight.

Amon deferred all substantive Dragonfly details to Qualcomm's Investor Day on June 24. The market read that as a signal that the product is not ready. When your competitor ships specs and partners in the same week you ship a logo, the gap in execution is visible.

## The Indian workforce in the crosshairs

This is not an abstract semiconductor rivalry. Qualcomm operates major R&D centres across India — in Hyderabad, Bengaluru, Chennai, and Noida — employing tens of thousands of engineers who work on Snapdragon chip design, modem development, and the AI inference stack. In San Diego, the company's headquarters, Indian-origin engineers on H-1B and L-1 visas make up a substantial portion of the design and software teams.

If NVIDIA captures a meaningful share of the AI PC market, the ripple effects are direct. Qualcomm's project pipeline for Snapdragon AI-optimised chips could slow. Teams in Hyderabad working on next-generation NPU architectures might see reduced headcount or frozen budgets. In San Diego, visa-dependent engineers face a particularly precarious calculus: Qualcomm's 60-day grace period becomes very real when projects get deprioritised.

The India centres are not at immediate risk — they serve Qualcomm's broader portfolio, including 5G modems, automotive chips, and IoT — but the AI PC division was the growth story that justified expansion. If that growth story now has a credible competitor with deeper software moats, the expansion plans slow.

## Qualcomm's Dragonfly counterplay

Amon's keynote was not without substance, even if the market dismissed it. He laid out a vision for "agentic AI" distributed across cloud and edge devices, arguing that AI agents will drive token demand from 31.7 billion per 10-second window in 2026 to 1.27 trillion in 2030. He showed a coding demonstration where distributed AI reduced token usage by 60%. And Dragonfly, when it materialises, will mark Qualcomm's first serious entry into the data-centre market that NVIDIA has dominated for a decade.

The problem is timing. NVIDIA ships RTX Spark this autumn. Qualcomm talks about Dragonfly at an investor day three weeks away. In semiconductors, execution eats vision for breakfast.

## The NRI investor angle

For diaspora investors holding Qualcomm stock — and many do, given the company's Indian engineering roots and consistent dividend — the question is whether the 40% May rally was premature. At current prices, the market is pricing in a successful data-centre pivot that Qualcomm has not yet demonstrated. NVIDIA's entry into AI PCs does not kill Qualcomm's mobile and automotive businesses, which remain strong. But it does narrow the upside case.

The broader lesson is one the Indian tech workforce has absorbed before: in Silicon Valley, yesterday's moat becomes today's commodity faster than anyone expects. Qualcomm built the Windows-on-Arm market. NVIDIA just showed it can take it."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

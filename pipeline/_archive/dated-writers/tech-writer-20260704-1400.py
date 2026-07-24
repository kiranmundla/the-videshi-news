#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-07-04 14:00 PT run"""
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
    {
        "id": str(uuid.uuid4()),
        "headline": "Every Big Tech Giant Wants a Data Centre in India. The Government Just Made It Tax-Free Until 2047.",
        "subheadline": "Microsoft is committing $17.5 billion, Google $15 billion, and even OpenAI is scouting sites. India's data centre capacity could grow tenfold in a decade — and its zero-tax policy is the reason the world is showing up.",
        "slug": make_slug("india-data-centre-boom-microsoft-google-zero-tax-2047"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Pichai's Google and Nadella's Microsoft are leading the biggest infrastructure bet on India in a generation — creating thousands of high-skill jobs, investment opportunities in data centre REITs, and a new reason for NRI engineers to consider returning.",
        "tags": ["data-centers", "microsoft", "google", "india-tech", "ai-infrastructure", "nri-investment"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Barron's", "url": "https://www.barrons.com/articles/ai-data-centers-india-75425e19"},
            {"name": "Reuters", "url": "https://www.reuters.com/technology/microsoft-partners-singapores-lightstorm-build-india-southeast-asia-undersea-cable-2026-07-03/"},
            {"name": "Goldman Sachs via The Indian Eye", "url": "https://theindianeye.com/india-poised-for-rapid-data-centre-growth-driven-by-ai-demand-demographics-proximity-to-middle-east-goldman-sachs/"},
            {"name": "Nomura Research", "url": "https://www.barrons.com/articles/ai-data-centers-india-75425e19"},
            {"name": "Reuters — Yotta", "url": "https://www.reuters.com/technology/indias-yotta-build-2-billion-ai-hub-with-nvidias-blackwell-chips-2026-02-19/"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5d/BalticServers_data_center.jpg/1280px-BalticServers_data_center.jpg",
        "image_caption": "Server racks inside a modern data centre facility",
        "image_attribution": "Wikimedia Commons",
        "body": """India is no longer just exporting the engineers who build the cloud. It is becoming the cloud.

In the past eighteen months, virtually every major American technology company has announced plans to build data centres on Indian soil. Microsoft has committed $17.5 billion — its largest investment anywhere in Asia. Alphabet, led by Chennai-born Sundar Pichai, is pouring $15 billion into three sprawling data centre campuses in Visakhapatnam, a coastal city in Andhra Pradesh. Meta, Amazon, and OpenAI have all staked out sites of their own.

The sums are large enough to reshape the country's infrastructure map. But what is accelerating the rush is something more unusual: policy.

## Zero Tax Until 2047

In February, India declared that overseas services provided by foreign companies operating data centres within its borders would attract zero taxes — not for five years, or ten, but until 2047. It was a signal calibrated for the long game, and Silicon Valley heard it clearly.

"Work with India and deliver for all," Prime Minister Narendra Modi said at an AI summit in June. The message was neither subtle nor ambiguous.

The incentives go beyond tax holidays. State governments are offering discounted land, expedited approvals, and dedicated power allocations. Unlike in the United States, where communities are waging fierce local battles against data centre construction — forcing public hearings, environmental reviews, and sometimes outright bans — Indian projects move through the planning process with far less friction.

"The importance of India to major cloud providers is definitely on the rise," says John Dinsdale, chief analyst at Synergy Research Group.

## From 1.3% to 3% of Global Capacity

The numbers tell the story. India currently accounts for roughly 1.3 per cent of the world's data centre capacity. That will rise to 3 per cent within five years, according to Dinsdale. "That may not sound like a big shift, but these are percentages of enormous numbers," he notes.

Nomura projects that India's data centre capacity will grow tenfold over the next decade. Macquarie's equity research arm estimates operational capacity could double from the current 1.4 gigawatts by 2027, and increase fivefold by 2030 if planned projects are fast-tracked.

Goldman Sachs, in a report released this week, flagged India's demographics, AI demand, and proximity to the Middle East as key factors driving growth.

## The Nvidia Connection

India's Yotta Data Services — part of the Hiranandani Group — is building one of Asia's largest AI computing hubs, a $2 billion project deploying over 20,000 of Nvidia's latest Blackwell Ultra GPUs. Yotta is one of only six Nvidia reference architecture platform partners globally and the only one in Asia-Pacific. Nvidia itself is anchoring a DGX Cloud supercluster within Yotta's infrastructure under a four-year, $1 billion contract.

"India's AI ambition is just not possible unless this infra comes to India," Yotta CEO Sunil Gupta told Reuters.

The company's total GPU footprint will rise from about 40,000 today to more than 75,000 over the next two years. It is planning a pre-IPO and public listing worth $1 to $1.2 billion.

## Why the Diaspora Should Pay Attention

For the Indian American technology professional, this is not an abstract infrastructure story. It is several things at once.

First, it is a jobs story. Data centre construction, cloud engineering, AI infrastructure management — these are precisely the roles that Indian engineers in the Bay Area, Seattle, and New Jersey already fill for American hyperscalers. Every new Indian campus creates high-skill positions that did not exist five years ago.

Second, it is an investment story. With India's data centre market projected to hit $38 billion globally by 2025 and $172 billion by 2032, the sector is creating a new asset class. Indian data centre REITs and operators like Yotta, CtrlS, and NTT India are expected to tap public markets in the coming years.

Third, it is a proximity story. Indians are already the second-largest users of ChatGPT and Claude globally. Latency matters — data centres must be closer to customers to reduce delay — and India's domestic demand for AI services is growing faster than almost anywhere else.

And fourth, for the NRI engineer weighing whether the American dream still makes sense in the age of $100,000 H-1B fees, India's emergence as a global AI infrastructure hub offers a credible alternative that simply did not exist a decade ago.

The runway is being built. The question, for millions of Indians on both sides of the Pacific, is who will be on the planes."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Pichai's Google Just Admitted Its Climate Goals Are Slipping. Amazon's Numbers Are Worse.",
        "subheadline": "Sustainability reports released this week show Google's emissions up 25 per cent and Amazon's up 16 per cent in a single year. The AI data centre buildout is burning through net-zero pledges faster than anyone expected.",
        "slug": make_slug("google-amazon-ai-emissions-surge-climate-goals-pichai"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Pichai's Google and Jassy's Amazon are the two largest employers of Indian tech workers in the US, and both are now building massive data centres in India — raising questions about whether India's own water-stressed, coal-heavy grid can handle the AI buildout without repeating these environmental mistakes.",
        "tags": ["ai", "google", "amazon", "climate", "data-centers", "sundar-pichai", "sustainability"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "TechCrunch", "url": "https://techcrunch.com/2026/07/02/a-warning-sign-about-ais-real-cost-courtesy-of-google-and-amazon/"},
            {"name": "Bloomberg Law", "url": "https://news.bloomberglaw.com/environment-and-energy/big-techs-carbon-emissions-spike-with-runaway-growth-of-ai"},
            {"name": "Barron's", "url": "https://www.barrons.com/articles/ai-big-tech-climate-goals-8ebc0e01"},
            {"name": "WSJ", "url": "https://www.wsj.com/business/energy-oil/ai-data-centers-far-more-water-most-tech-giants-report-91c21a7d"},
            {"name": "Google Sustainability Report 2025", "url": "https://sustainability.google/"},
            {"name": "Amazon Sustainability Report 2025", "url": "https://sustainability.aboutamazon.com/"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b3/Google_Servers.jpg/1280px-Google_Servers.jpg",
        "image_caption": "Google server racks inside one of the company's data centres",
        "image_attribution": "Wikimedia Commons",
        "body": """The two most powerful Indian-origin executives in American technology released their companies' environmental report cards this week. Neither will be framing the results.

Google, led by CEO Sundar Pichai, disclosed that its total greenhouse gas emissions rose 25 per cent in 2025 — an 82 per cent increase since its 2019 baseline. Amazon, whose cloud division AWS remains the backbone of half the internet, reported a 16 per cent jump, emitting roughly 81 million metric tons of carbon dioxide equivalent last year. That is roughly the same as putting 19 million petrol-powered cars on the road.

The culprit, in both cases, is not a mystery. It is artificial intelligence — and the vast, power-hungry data centres needed to run it.

## The Climate Moonshot Gets Harder

Google has one of the most ambitious climate goals in corporate America: sourcing all its power on every grid where it operates with clean energy, 24 hours a day, 7 days a week, by 2030. Not just matching dirty power in one region with clean credits in another — actual, real-time decarbonisation.

The AI buildout has made that goal, by the company's own admission, nearly impossible.

"While we remain deeply committed to sustainability, reaching our climate moonshot is getting harder," Google said in its report. The company's electricity consumption jumped 37 per cent in a single year. Without its record-setting investments in nuclear, batteries, and renewable energy, Google's carbon footprint would have been five times larger.

Amazon, which targets net zero by 2040, faces a similar wall. "To meet strong customer demand, in 2025 we added more data center capacity globally than any other company, including more than 1.2 gigawatt in Q4 alone," it wrote. The company now has more than 700 wind and solar projects globally — and its emissions are still climbing.

Microsoft, which has pledged to go carbon-negative by 2030, is reportedly considering scaling back that commitment amid its own AI spending surge. Meta, despite a 2030 net-zero target, spent $135 billion on data centre buildout this year alone.

## The Hidden Cost: Water and Supply Chains

The carbon problem is only the most visible layer. A Wall Street Journal investigation published this week revealed that AI data centres consume far more water than tech companies publicly disclose.

Google uses around three times as much water indirectly — through the electricity it consumes and the hardware it purchases — as it does directly in cooling its data centres. Meta's indirect water use reached 19 billion gallons in 2024, more than 20 times its direct usage. Amazon claims its data centres use water seven times more efficiently than the industry average, but that figure also excludes indirect consumption.

Then there is Scope 3 — emissions from the supply chain. Semiconductor manufacturing is extraordinarily energy-intensive, and most leading-edge chip factories sit in Asia, where electrical grids remain dominated by fossil fuels. The chemicals used in chipmaking are potent greenhouse gases, thousands of times more warming than CO2. As companies binge on GPUs and memory chips, these upstream emissions are ballooning.

Google's Scope 3 emissions have doubled since 2019. "A good chunk is probably data centers," TechCrunch reported.

## The Regulatory Gap

This spring, activist investors at Amazon, Alphabet, and Meta filed shareholder proposals demanding companies explain how they reconcile surging AI energy demands with their climate pledges. None of the proposals won majority support.

The European Union, meanwhile, is moving in the opposite direction. A draft proposal dated 30 June would weaken planned data centre climate rules, allowing operators to use broader energy certificates — including some tied to nuclear power — to offset emissions from gas-powered facilities. The lobbying effort, led by Amazon Web Services and Microsoft, appears to be working.

Morgan Stanley estimates that hyperscalers will spend $800 billion on capital expenditures in 2026 — roughly equal to what every other non-tech company in the S&P 500 spent on capex combined last year.

## What This Means for India

This is where the story becomes directly relevant to the Indian diaspora.

Google is building three massive data centre campuses in Visakhapatnam. Microsoft has committed $17.5 billion to Indian infrastructure. Amazon, Meta, and OpenAI are all scouting Indian sites. Yotta is constructing a $2 billion Nvidia-powered AI hub near Delhi.

India already faces severe water stress in many of the regions where data centres are being built. Its electrical grid remains heavily dependent on coal — roughly 70 per cent of generation. The country declared zero taxes on foreign data centre operators until 2047, but has not announced corresponding environmental requirements.

If Google cannot hit its climate targets on an American grid that is 40 per cent clean — and with billions in decarbonisation investments — the arithmetic for India's coal-heavy grid is considerably grimmer.

For the NRI investor tracking AI infrastructure as the next great opportunity, the emissions numbers are not a reason to divest. But they are a reason to ask harder questions: about water, about grid composition, about whether India's data centre gold rush comes with environmental guardrails. The companies building in India are the same ones admitting, this week, that they cannot yet solve the problem at home.

The AI boom's environmental bill is no longer hypothetical. Pichai's own company just put the receipt on the table."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

#!/usr/bin/env python3
"""Technology writer — 2026-07-07 06:00 PDT run"""
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


# ── ARTICLE 1: Nadella-Pichai-Arora consortium buys London Spirit ──

art1_body = """A consortium of 11 Indian-origin tech billionaires, led by Palo Alto Networks CEO Nikesh Arora, has acquired a 49 per cent stake in London Spirit — the Lord's-based franchise in The Hundred, England's 100-ball cricket league. The deal values the team at £295 million.

The buyer list reads like a who's-who of Silicon Valley's Indian-origin power elite: Microsoft CEO Satya Nadella, Alphabet CEO Sundar Pichai, Adobe CEO Shantanu Narayen, and Times Internet vice-chairman Satyan Gajwani are all part of the consortium, which has been formalised under Cricket Investor Holdings Limited.

## A Four-Hour Auction

The deal was anything but smooth. An online auction stretched to nearly four hours, with the consortium fending off bids from groups affiliated with Manchester United and Chelsea FC in the English Premier League. The fiercest competition came from Sanjiv Goenka, owner of IPL franchise Lucknow Super Giants, who had been widely expected to prevail.

Instead, the tech consortium — initially dismissed as rank outsiders — outbid everyone. The ECB's 49 per cent stake alone fetched £145 million, a figure that stunned cricket administrators. The Marylebone Cricket Club retains the other 51 per cent.

"This historic news comes at the conclusion of ECB's sales process," said MCC Chair Mark Nicholas. "All those we spoke to were so eager to be a part of what we do."

## Follow the Money — and the Pattern

This is not the first time these names have appeared in cricket's ownership columns. Nadella and Narayen are existing investors in Major League Cricket in the United States, where Washington Freedom — another MLC-linked team — separately secured Welsh Fire for £65 million on the same day.

The Hundred's privatisation has already delivered over £300 million from four teams sold, with four more franchises to go under the hammer next week. Mukesh Ambani's Reliance Industries has already bought the Oval Invincibles. Goenka is expected to bid aggressively for Manchester Originals.

The Indian billionaire influx into English cricket mirrors what happened in the IPL two decades ago — only now the capital is flowing in the other direction, from Silicon Valley and Mumbai into London, Birmingham, and Cardiff.

## Why NRIs Should Care

For Indian Americans in tech, this is more than a sports story. The leaders who run their companies — and in many cases, decide their H-1B sponsorship and stock options — are now personally invested in growing cricket globally. The sport that many NRIs grew up watching on doordarshan is being reshaped by the same people who reshaped the internet.

It also signals a generational shift in how Indian tech wealth is being deployed. The previous generation of Indian billionaires bought IPL teams. This generation is buying into English cricket, American cricket, and the global franchise ecosystem — treating the sport less as a passion project and more as an asset class.

The ECB's total haul is now tracking well above its £350 million target. For a sport that started in England but found its commercial soul in India, the circle is closing — underwritten by the most powerful Indian-origin executives on the planet."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Nadella, Pichai and Arora Just Bought a Cricket Team at Lord's. They Paid £145 Million.",
    "subheadline": "An 11-strong consortium of Indian-origin tech billionaires has acquired a 49% stake in London Spirit, beating IPL owners in a four-hour auction that signals how Silicon Valley wealth is reshaping global cricket.",
    "slug": make_slug("nadella-pichai-arora-london-spirit-cricket-lords"),
    "category": "technology",
    "vertical": "tech-leaders",
    "diaspora_angle": "The CEOs who run the companies employing tens of thousands of Indian H-1B workers are now personally invested in globalising cricket — the sport that defined the NRI childhood.",
    "tags": ["satya-nadella", "sundar-pichai", "nikesh-arora", "cricket", "the-hundred", "london-spirit", "silicon-valley"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Cricbuzz", "url": "https://m.cricbuzz.com/cricket-news/133291/microsft-head-google-ceo-til-vc-in-consortium-that-bags-london-spirit"},
        {"name": "Sky Sports", "url": "https://www.skysports.com/cricket/news/12123/13367891/the-hundred-investors-tom-brady-chelseas-todd-boehly-ipl-team-owners-and-big-businesses-all-secure-stakes"},
        {"name": "Front Office Sports", "url": "https://frontofficesports.com/google-microsoft-adobe-ceos-buy-stakes-in-cricket-league/"},
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/news/sports/googles-pichai-joins-tech-ceos-in-bids-for-london-cricket-team/article69268948.ece"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/7/77/Lords-Cricket-Ground-Pavilion-06-08-2017.jpg",
    "image_caption": "The Pavilion at Lord's Cricket Ground in London, home of London Spirit",
    "image_attribution": "Wikimedia Commons",
    "body": art1_body
}


# ── ARTICLE 2: DeepSeek is designing its own AI inference chip ──

art2_body = """DeepSeek, the Chinese AI lab that sent Nvidia's stock into freefall earlier this year, is now building its own semiconductor. The company is developing a custom inference chip — designed to run trained models, not train new ones — in a move that could reduce its dependence on both Nvidia and Huawei, according to three people familiar with the effort.

The project is still at an early stage, Reuters reports. DeepSeek has been reaching out to chip-design partners, foundries, and memory companies, and has quietly hired chip-design engineers without posting jobs publicly. The effort began roughly a year ago.

## Why Inference, Not Training

The choice to target inference rather than training is strategically sharp. As AI applications spread from chatbots to enterprise automation, the industry's compute demand is tilting heavily toward inference — the process of running a model to generate answers, rather than the one-off process of building it.

Inference chips can be smaller, cheaper, and more power-efficient than the general-purpose GPUs needed for training. For DeepSeek, which gained global fame by building models that rival OpenAI's at a fraction of the cost, designing a chip optimised specifically for running its own models could compound that efficiency advantage.

## The Bigger Semiconductor Chess Game

DeepSeek's chip push arrives in an already crowded and increasingly geopolitical semiconductor landscape. Huawei's Ascend 950 series currently commands roughly half of China's estimated $50 billion domestic AI chip market, a dominance built largely on the back of U.S. export bans that blocked Chinese firms from buying Nvidia's most advanced processors.

But Huawei's grip is loosening. Alibaba and Baidu have both developed their own AI chips and are gaining share. DeepSeek entering the race would add another well-funded competitor — and one with a unique advantage: intimate knowledge of its own model architecture, allowing it to design silicon that maps precisely to the workloads it needs to run.

The company's first embrace of outside capital — a reported $7 billion funding round valuing it between $52 and $59 billion — suggests the resources are there.

## What This Means for India's Chip Ambitions

For Indian semiconductor professionals and NRI investors watching the chip wars, DeepSeek's move underscores a widening gap. China now has multiple AI companies designing custom silicon — Huawei, Alibaba, Baidu, and potentially DeepSeek. India, despite ambitious fab plans from Tata Electronics in Dholera and Micron in Gujarat, has no domestic AI chip design house of comparable scale.

The contrast is instructive. India's semiconductor strategy has focused on manufacturing — building fabs, attracting foreign chipmakers, and training engineers. China's ecosystem is now vertically integrating from model to silicon, with AI companies designing the chips that run their own software.

For the thousands of Indian-origin engineers working in chip design at Nvidia, Qualcomm, Intel, and AMD, the geopolitical realignment of semiconductor supply chains is not abstract. It shapes which teams get funded, which projects get greenlit, and ultimately which careers have a runway.

DeepSeek's chip may be years from production. But the decision to build one is already a signal: the era of renting Nvidia's GPUs as a neutral utility is ending, and the companies that control their own inference silicon will set the terms of the next phase of AI."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "DeepSeek Is Building Its Own AI Chip. Nvidia and Huawei Should Both Be Worried.",
    "subheadline": "The Chinese AI lab that shocked Silicon Valley with its low-cost models is now designing a custom inference chip — a move that could reshape the semiconductor supply chain Indian engineers depend on.",
    "slug": make_slug("deepseek-ai-inference-chip-nvidia-huawei-india"),
    "category": "technology",
    "vertical": "semiconductors",
    "diaspora_angle": "Thousands of Indian-origin chip designers at Nvidia, Qualcomm, and Intel are caught in the geopolitical realignment DeepSeek's move accelerates — and India's own fab ambitions look modest by comparison.",
    "tags": ["deepseek", "ai-chips", "nvidia", "huawei", "semiconductors", "india-chip-ambitions", "china-ai"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/world/china/chinas-deepseek-developing-its-own-ai-chip-sources-say-2026-07-07/"},
        {"name": "Reuters — Big Chinese tech firms scramble for Huawei chips", "url": "https://www.reuters.com/technology/big-chinese-tech-firms-scramble-secure-huawei-ai-chips-after-deepseek-v4-launch-2026-04-29/"},
        {"name": "Towards AI — DeepSeek V4 on Huawei Chips", "url": "https://pub.towardsai.net/deepseek-v4-just-launched-on-huawei-chips-first-no-nvidia-required-2b9f0cd8e1e2"}
    ]),
    "score_total": 80,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/6477199/pexels-photo-6477199.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
    "image_caption": "Close-up of a microchip circuit board — DeepSeek is designing custom inference silicon",
    "image_attribution": "Pexels",
    "body": art2_body
}


# ── ARTICLE 3: India's GPU market is being rewired by scarcity ──

art3_body = """India imports nearly all of its high-end AI chips. That dependency is now reshaping how the country's AI startups build, compete, and survive.

A new analysis by Inc42 lays out the structural challenge: lead times for the latest Nvidia GPUs stretch to 36–52 weeks for enterprise buyers, with some orders pushed into 2027. Hyperscalers — Microsoft, Google, Amazon, Meta — are locking up the overwhelming majority of Nvidia's newest shipments through long-term purchase agreements, leaving smaller Indian AI companies to fight over what remains.

## The Tiered Market

What has emerged is a two-track system. Older-generation GPUs like the H100 are becoming easier to source, but Nvidia has declared the H100 end-of-sale and is concentrating production on newer architectures. Indian cloud providers report that while the situation is "more predictable" than the chaos of 2024, large deployments still require reservations months in advance.

"AI infrastructure has become a strategic resource rather than an on-demand purchase," says Sunil Gupta, co-founder of Yotta, one of India's largest data centre operators. "Large enterprises and model builders are now planning their compute requirements several quarters ahead."

The bottlenecks are not limited to chips. Memory components — particularly the high-bandwidth memory (HBM) critical to AI inference — carry even longer lead times than the processors they support. New factories from SK Hynix, Samsung, and Micron are not expected to add significant capacity until 2027 or 2028.

## Scarcity as Strategy

Indian AI startups are adapting by getting creative. Voice AI company Murf.AI divides its compute between scheduled training and continuous real-time inference, reserving guaranteed capacity ahead of training runs rather than relying on the spot market. Enterprise AI startup Nurix, operating a fleet of just 15–22 GPUs, segments workloads so inference runs during peak hours and fine-tuning happens off-peak.

CoRover, which builds conversational AI, routes 80 per cent of its tasks to lightweight architectures that do not require GPU-heavy inference — sourcing capacity from Google Cloud, Yotta, NxtGen, and the government's IndiaAI Mission, with peak usage reaching around 1,200 GPUs.

The common thread: Indian startups are treating GPU efficiency as a competitive weapon, not just a constraint. Software optimisation is replacing brute-force scaling. Mixed fleets of old and new hardware are the norm.

## The Sovereign Compute Question

Industry leaders frame this as more than a procurement problem. Ashok Chandak, president of the India Electronics and Semiconductor Association, argues that GPU allocation is a sovereign security issue. India's IndiaAI Mission has allocated $1.25 billion toward building a national compute grid, but the scale remains modest against the $770 billion hyperscalers are expected to pour into global data centre infrastructure this year alone — a 74 per cent jump from 2025.

For NRI engineers and investors watching India's AI ecosystem from afar, the GPU shortage is a useful lens for understanding which startups can actually build and which are running on demos. The Indian companies that survive this compute drought — by optimising harder, designing smarter architectures, and securing creative supply agreements — may end up building more resilient AI businesses than their better-funded Silicon Valley counterparts.

The question is whether India's AI ambition can outrun its hardware constraints before the next generation of chips arrives."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "India's AI Startups Can't Buy Enough GPUs. So They're Learning to Build Without Them.",
    "subheadline": "With Nvidia's newest chips locked up by hyperscalers and lead times stretching past a year, Indian AI companies are turning scarcity into a competitive advantage through radical software optimisation.",
    "slug": make_slug("india-gpu-shortage-ai-startups-compute-scarcity"),
    "category": "technology",
    "vertical": "indian-tech",
    "diaspora_angle": "NRI engineers and investors tracking India's AI ecosystem should watch which startups survive the compute drought — they may build more resilient businesses than their better-funded Valley counterparts.",
    "tags": ["india-ai", "gpu-shortage", "nvidia", "semiconductors", "yotta", "indiaai-mission", "startups"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Inc42", "url": "https://inc42.com/features/why-indias-ai-boom-is-running-on-a-waiting-list/"},
        {"name": "Reuters — Indian IT firms face muted Q1", "url": "https://www.reuters.com/technology/indian-it-firms-face-muted-q1-ai-shift-weak-demand-weigh-2026-07-06/"},
        {"name": "The Indian Eye — U.S.-India AI Innovation", "url": "https://theindianeye.com/forging-the-next-wave-of-ai-innovation/"}
    ]),
    "score_total": 75,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/17489151/pexels-photo-17489151.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
    "image_caption": "Server racks in a data centre — India's AI startups face severe GPU supply constraints",
    "image_attribution": "Pexels",
    "body": art3_body
}


# ── INSERT ALL ──

articles = [art1, art2, art3]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

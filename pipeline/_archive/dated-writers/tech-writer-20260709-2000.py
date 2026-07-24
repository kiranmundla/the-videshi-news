#!/usr/bin/env python3
"""Technology writer — July 9, 2026 8:00 PM PT run"""
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
    # --- ARTICLE 1: Google Vizag AI Hub Groundbreaking ---
    {
        "id": str(uuid.uuid4()),
        "headline": "Google Just Broke Ground on Its Biggest AI Hub Outside America. The Location: Vizag.",
        "subheadline": "Sundar Pichai's $15 billion bet on Visakhapatnam will bring gigawatt-scale compute, three subsea cables, and a new digital corridor between India and the United States.",
        "slug": make_slug("google-vizag-ai-hub-groundbreaking-pichai-subsea"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Indian Americans at Google and other Big Tech firms will work on AI systems powered by Vizag's compute. NRIs from Andhra Pradesh watch their home state become a global tech hub.",
        "tags": ["google", "sundar-pichai", "vizag", "india-ai", "data-center", "subsea-cable", "infrastructure"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "The Indian Eye", "url": "https://theindianeye.com/sundar-pichai-apprises-pm-modi-about-googles-first-ever-ai-hub-in-visakhapatnam/"},
            {"name": "The Indian Eye", "url": "https://theindianeye.com/google-breaks-ground-for-india-ai-hub-in-visakhapatnam/"},
            {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com/info-tech/google-unveils-india-america-sub-sea-cable-initiative-to-boost-ai-connectivity/article69240116.ece"},
            {"name": "Barron's", "url": "https://www.barrons.com/articles/india-data-center-hub-microsoft-google-meta-b15ce4d4"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/c/c3/Sundar_Pichai_-_2023_%28cropped%29.jpg",
        "image_caption": "Google and Alphabet CEO Sundar Pichai at a 2023 event",
        "image_attribution": "Wikimedia Commons",
        "body": """When Sundar Pichai broke ground on Google's new AI hub in Visakhapatnam this week, he was not just pouring ceremonial concrete. He was planting a flag in what may become Asia's most consequential piece of AI infrastructure — a $15 billion complex that will house gigawatt-scale compute, a new international subsea cable gateway, and the backbone of a digital corridor between the United States and India.

The announcement, made at Google's "Bharat AI Shakti" event in New Delhi, represents the company's largest investment in India's digital future and its biggest AI hub outside the United States. Pichai discussed the project directly with Prime Minister Narendra Modi, calling it "a landmark development" that would "accelerate AI innovation and drive growth across the country."

## What Vizag Gets

The hub, developed in partnership with AdaniConneX and Nxtra by Airtel, will comprise three data centre campuses capable of delivering one gigawatt of compute power — enough to run some of the world's most demanding AI workloads. Three subsea cables will land in Vizag, creating a new international gateway that Google says will serve as a "digital backbone connecting different parts of India."

Thomas Kurian, CEO of Google Cloud, described it as "an inflection point for the country's AI-native future." Jeet Adani, Director of the Adani Group, put it more bluntly: "Nearly 1 GW in a single location signals that shift."

The investment is part of a five-year plan running from 2026 to 2030. Andhra Pradesh Chief Minister N. Chandrababu Naidu called the hub "a cornerstone of our growing tech corridor."

## The Subsea Play

Perhaps more significant than the data centres themselves is what connects them to the rest of the world. Google simultaneously announced the India-America Connect initiative, a set of new subsea cable routes linking the United States, India, and multiple locations across the Southern Hemisphere.

Pichai framed these cables as infrastructure for a new kind of trade. "Combined with our existing cable systems, this initiative will significantly expand the digital trade routes and serve as a literal bridge between our two countries," he said.

The cables are not mere pipes for consumer internet. They are designed to carry the massive data flows required by AI workloads, cloud services, and cross-border enterprise computing. As India becomes the world's second-largest user base for ChatGPT and Claude AI, the demand for low-latency connectivity between Indian data centres and global AI models is becoming operationally critical.

## Why NRIs Should Watch

For Indian Americans in technology — and there are well over 300,000 of them at major tech companies — this investment reshapes the geography of where their work gets done. Google's AI models, trained partly on Vizag's compute, will power products used by billions. Engineers in Mountain View and Bengaluru will share workloads across a subsea link designed for AI-scale traffic.

For NRIs from Andhra Pradesh, the transformation is more personal. Vizag, long known as the "City of Destiny" for its port and steel industry, is being repositioned as a global technology hub. The jobs created — in data centre operations, network engineering, AI development, and energy infrastructure — could alter migration patterns for a generation of Telugu-speaking engineers.

India's broader data centre ambitions are accelerating. Microsoft has committed $17.5 billion. Meta, Amazon, and OpenAI are all adding capacity. Nomura estimates India's data centre footprint will grow tenfold over the next decade, from 1.3 per cent of global capacity to roughly 3 per cent. The government has declared zero taxes until 2047 on overseas services by foreign companies operating data centres in India.

## The Skilling Dimension

Google is coupling its infrastructure investment with workforce development. Pichai announced that the company would train 10 million Indians through its AI Skill House initiative and partner with Wadhwani AI to deliver a Google AI certificate programme for students and early-career professionals.

The Gemini app, Google's flagship AI product, is already available in 10 Indian languages. Circle to Search and Google Lens are used more in India than anywhere else in the world.

The message to India's tech ecosystem is unmistakable: the AI future is being physically built in India, not just consumed there. For the diaspora watching from abroad, the question is no longer whether India can compete in AI infrastructure. It is whether they want a seat at the table when the compute switches on."""
    },

    # --- ARTICLE 2: Indian IT Perfect Storm ---
    {
        "id": str(uuid.uuid4()),
        "headline": "India's $315 Billion IT Industry Is Staring Down Its Worst Year in a Decade. The Reckoning Has Arrived.",
        "subheadline": "The Nifty IT index has cratered 28 per cent in 2026. JPMorgan sees no recovery. Nomura calls it a 'perfect storm.' And earnings season starts now.",
        "slug": make_slug("india-it-sector-perfect-storm-nifty-q1-earnings"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "NRI investors who hold TCS, Infosys, Wipro, and HCLTech stocks have watched a quarter of their value evaporate. Hundreds of thousands of Indians working at these firms face slower hiring and AI-driven restructuring.",
        "tags": ["indian-it", "nifty-it", "tcs", "infosys", "wipro", "hcltech", "ai-disruption", "earnings"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/indian-it-firms-face-muted-q1-ai-shift-weak-demand-weigh-2026-07-06/"},
            {"name": "Reuters", "url": "https://www.reuters.com/technology/indias-tcs-chair-says-ai-agents-may-equal-headcount-dampen-hiring-2026-06-09/"},
            {"name": "Reuters", "url": "https://www.reuters.com/technology/ai-hiring-outpaces-overall-it-recruitment-india-report-shows-2026-07-04/"},
            {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/corporate/tcs-adds-9279-employees-in-q1-highest-quarterly-hiring-in-over-a-year"}
        ]),
        "score_total": 80,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/28682349/pexels-photo-28682349.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
        "image_caption": "Stock trading charts on a digital display showing market trends",
        "image_attribution": "Pexels",
        "body": """India's information technology sector, the engine that powered an entire generation of middle-class wealth and skilled immigration to America, is having its most punishing year since the pandemic. The Nifty IT index has plunged 28 per cent in 2026 — the worst performance of any major sector on India's exchanges — even as the benchmark Nifty 50 has gained nearly 7 per cent.

The numbers tell one story. The mood inside India's biggest brokerages tells another, darker one.

"Indian IT firms are in a perfect storm," Nomura wrote in its Q1 earnings preview, with Middle East conflict-led uncertainty compounding AI-driven pricing pressure. JPMorgan has projected that revenue growth for India's top IT firms will stay below 3 to 4 per cent for "the foreseeable future." Citi expects a fourth consecutive year of subdued growth.

Earnings season kicks off now, with TCS reporting on July 9, Infosys on July 10, HCLTech on July 13, and Wipro on July 16. Analysts are bracing for disappointment.

## The Illusion of Growth

On the surface, India's top six IT companies are expected to report around 14 per cent year-on-year revenue growth in rupee terms, with net profits rising 12 to 13 per cent. Respectable numbers — until you strip out the sharp depreciation of the rupee.

In constant-currency terms, which measure actual business performance rather than exchange rate windfalls, the companies are expected to post a mere 2.8 per cent revenue growth. The April-to-June quarter is traditionally a strong one for Indian IT, boosted by higher billing days and new project starts. This year, analysts expect a slow start that pushes back any hopes of a meaningful recovery.

TCS has already reported: ₹72,275 crore in revenue and ₹13,349 crore in net profit, with constant-currency growth of just 0.4 per cent sequentially. The company added 9,279 employees — its strongest quarterly hiring in over a year — but the order book of $9.5 billion reflects a sector investing in talent while waiting for demand to catch up.

## The AI Squeeze

At the heart of the downturn is a structural challenge that no amount of cost optimisation can fix. AI is rewriting the economics of the IT services business model itself.

India's IT industry was built on labour arbitrage: hire thousands of engineers at a fraction of Western salaries to build and maintain software systems. AI agents, code generation tools, and automated testing platforms are now compressing that model from both ends — reducing the hours billed per project and giving Western clients the option to do more with smaller, AI-augmented teams.

TCS Chairman N. Chandrasekaran made the implications explicit at the company's annual general meeting last month: "If the company has half a million employees, the day is not far when the company will have half a million AI agents. The company's employees and AI agents will work together."

He was not threatening layoffs. TCS is still hiring. But Chandrasekaran was signalling that the industry's headcount-driven growth model is being replaced by something fundamentally different — and the market is pricing that transition aggressively.

## Two Speeds in the Labour Market

The data on India's tech labour market confirms the split. AI-specific hiring rose 16 per cent year-on-year in June, while overall IT jobs declined 3 per cent, according to Naukri's monthly JobSpeak report. Across all 14 sectors tracked by the portal, AI and machine learning roles grew 25 per cent.

The divergence is telling. Companies are not stopping investment — they are redirecting it. Traditional roles in testing, maintenance, and application management are shrinking. Roles in AI engineering, prompt design, MLOps, and data architecture are growing. For the hundreds of thousands of Indian engineers on H-1B and L-1 visas at these companies, the message is adapt or be restructured.

## What NRI Investors Should Watch

The earnings reports over the next two weeks will reveal more than revenue beats or misses. Watch for three things.

First, **annual guidance revisions**. Brokerages expect Infosys and HCLTech to narrow or trim the upper end of their full-year revenue growth forecasts. If they cut below 3 per cent, it signals the industry has accepted that recovery is not coming in fiscal 2027.

Second, **AI revenue disclosures**. TCS said its AI-related revenue crossed $2.6 billion. Whether peers can show similar traction will determine if AI is a genuine revenue line or just a talking point for earnings calls.

Third, **deal pipeline quality**. HCLTech's $1.14 billion AI deal with a European firm last week — its biggest in three years — suggests that AI-native contracts exist. The question is whether they can arrive fast enough to offset the erosion in traditional services revenue.

For NRIs who built retirement portfolios around Infosys and TCS, the sector's 28 per cent drawdown is more than a market correction. It is a repricing of the industry's future. The IT services model that sent a million Indians to America may survive. But it will not look the same."""
    },

    # --- ARTICLE 3: SK Hynix Nasdaq Listing ---
    {
        "id": str(uuid.uuid4()),
        "headline": "The World's Biggest AI Memory Chipmaker Lists on Nasdaq Tomorrow. Sanjay Mehrotra's Micron Just Got Company.",
        "subheadline": "SK Hynix's $28 billion offering was seven times oversubscribed. For NRI investors in the AI trade, it opens a door that was locked until now.",
        "slug": make_slug("sk-hynix-nasdaq-listing-micron-mehrotra-ai-memory"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Indian-American investors gain direct Nasdaq access to the dominant HBM supplier for the first time. Micron CEO Sanjay Mehrotra, one of the most prominent Indian-origin semiconductor executives, now faces his biggest rival on his home exchange.",
        "tags": ["sk-hynix", "nasdaq", "micron", "sanjay-mehrotra", "memory-chips", "hbm", "ai-infrastructure", "chipflation"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Investopedia", "url": "https://www.investopedia.com/sk-hynix-us-listing-test-memory-stock-appetite-11740037"},
            {"name": "Barron's", "url": "https://www.barrons.com/articles/sk-hynix-us-listing-micron-stock-gap-ba7e9f1f"},
            {"name": "Reuters", "url": "https://www.reuters.com/technology/sk-hynix-close-28-billion-adr-bookbuild-wednesday-oversubscription-source-says-2026-07-09/"},
            {"name": "MarketWatch", "url": "https://www.marketwatch.com/story/sk-hynix-raises-26-5-billion-in-u-s-offering-what-to-know-about-the-stock-eff32ff5"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/38361204/pexels-photo-38361204.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
        "image_caption": "SK Hynix DRAM memory chips on a circuit board",
        "image_attribution": "Pexels",
        "body": """On Friday morning, when the Nasdaq opens for business, a new ticker will flash across trading screens: SKHY. South Korea's SK Hynix, the company that manufactures more than half the world's high-bandwidth memory chips — the component without which no Nvidia GPU can function — will begin trading in the United States for the first time.

The offering raised $26.5 billion at a price of $149 per American Depositary Share, making it the most lucrative U.S. listing by a foreign company in history. Demand was more than seven times the available shares. U.S. institutional orders started at $200 million and the largest exceeded $1 billion. Baillie Gifford, Coatue Management, and Situational Awareness Partners — the last founded by a former OpenAI researcher — committed a combined $7 billion.

For American investors, and for the hundreds of thousands of Indian Americans working in the semiconductor and AI industries, this listing removes a barrier that has been quietly frustrating. Until now, buying SK Hynix required navigating South Korean trading rules and currency exposure. Now it sits on the same exchange as Nvidia, AMD, and one very interesting competitor: Micron Technology, led by Indian-American CEO Sanjay Mehrotra.

## The Memory Bottleneck

To understand why this matters, you need to understand the bottleneck. Every major AI data centre in the world runs on Nvidia GPUs. Every Nvidia GPU requires high-bandwidth memory — HBM — to function. SK Hynix controls more than 60 per cent of the global HBM market. It is, in the most literal sense, the company that memory-enables the AI revolution.

The economics are staggering. SK Hynix's revenue tripled to roughly $34.5 billion and its profit quintupled to $26.5 billion in the first quarter alone. Samsung's operating profit rose 19-fold last quarter. Micron's profit margins climbed to nearly 85 per cent from 38 per cent a year earlier. The AI boom has turned memory chipmakers into the most profitable companies on the planet.

Stock performance has followed. SK Hynix shares are up 235 per cent in 2026. Samsung has risen 130 per cent. Micron is up 250 per cent. The Kospi, South Korea's benchmark index, has gained 91 per cent this year, almost entirely on the backs of its two chip giants.

## Mehrotra vs the Korean Giants

The listing sets up a direct valuation comparison that Wall Street has been waiting for. SK Hynix's Korean shares trade at approximately 8 times forward earnings. Micron trades at 13.5 times. That gap — suggesting as much as 40 per cent upside for SK Hynix on a relative basis — is exactly the kind of arbitrage institutional investors will try to exploit.

For Sanjay Mehrotra, born in Kanpur and co-founder of SanDisk before taking the helm at Micron, the competitive dynamic just intensified. Micron is the third-largest memory maker behind Samsung and SK Hynix, and it has historically traded at a premium to its Korean peers precisely because it was the easiest way for U.S. investors to play the memory cycle. That convenience premium may now compress.

Analysts at Bank of America estimate that memory will represent 35 to 40 per cent of the $1.5 trillion Big Tech companies are projected to spend on cloud and AI infrastructure in 2027. With additional capacity not expected to come online until at least mid-2028, the supply crunch could extend the memory cycle for another 18 months.

## 'Chipflation' Is Real

The memory boom has a flip side that touches consumers directly. Morgan Stanley analysts have coined the term "chipflation" to describe the macroeconomic impact of soaring chip and memory prices. PC prices have risen 20 to 40 per cent year-on-year across comparable product lines. Apple has raised MacBook prices. Global PC shipments fell 3.6 per cent in the second quarter, partly because consumers are pulling purchases forward before prices climb further.

For NRI tech workers buying laptops, upgrading phones, or speccing out home servers, the cost of the AI boom is showing up in their credit card statements. The irony is that the same demand driving their employers' share prices is inflating the price of every device they own.

## What NRI Investors Should Know

SK Hynix's ADRs will trade under the ticker SKHY on the Nasdaq. Each ADR represents one-tenth of a common share. The listing includes the issuance of new shares — roughly 2.5 per cent of the existing share count — which could create modest selling pressure in the first few sessions.

The investment case is straightforward but directional. If you believe AI infrastructure spending is durable and the HBM shortage will persist through 2027, SK Hynix at 8 times earnings offers a cheaper entry than Micron at 13.5 times. If you believe the memory cycle is nearing its peak — and Samsung's post-earnings stock dump suggests some investors do — then any memory position carries cyclical risk.

Daniel Newman, CEO of research firm Futurum Group, framed the trade-off precisely: "SK Hynix is the purer AI play, which cuts both ways. Its revenue mix is more concentrated in HBM and in Nvidia specifically. In a downturn, customer concentration becomes a liability."

For Indian Americans in the chip industry — at Micron's Boise headquarters, at Nvidia's Santa Clara campus, at Intel's Oregon fabs — the listing is not abstract. It is the company that supplies the most critical component in their products, arriving on their home exchange, priced for a bet they make every day at work: that AI demand is not slowing down."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

#!/usr/bin/env python3
"""Technology writer — 2026-07-15 02:00 PT run"""

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
    # ============================================================
    # Article 1: SEMI Semiconductor Equipment Forecast + India Fabs
    # ============================================================
    {
        "id": str(uuid.uuid4()),
        "headline": "The World Will Spend $166 Billion on Chip-Making Gear This Year. India Has 12 Fab Projects Ready to Absorb the Wave.",
        "subheadline": "SEMI's mid-year forecast shows a 23 percent jump in global semiconductor equipment spending, driven by insatiable AI demand. With a dozen greenlit projects worth over $20 billion, India is angling for a real piece of the buildout.",
        "slug": make_slug("semi-166-billion-chip-equipment-forecast-india-fabs"),
        "category": "technology",
        "vertical": "semiconductors",
        "diaspora_angle": "Indian-origin SEMI President Ajit Manocha is steering the global chip equipment body during the biggest spending surge in semiconductor history. NRI engineers and investors are watching India's 12 greenlit fab projects as career and investment opportunities.",
        "tags": ["semiconductors", "india-semiconductor-mission", "ajit-manocha", "semi", "ai-chips", "tata-electronics", "micron-india"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "SEMI Mid-Year Forecast via DevDiscourse", "url": "https://www.devdiscourse.com/article/business/3950255-record-growth-in-semiconductor-equipment-spending-a-boon-for-india"},
            {"name": "SEMI Official Year-End 2025 Forecast", "url": "https://www.semi.org/en/news-media-press-releases/semi-press-releases/global-semiconductor-equipment-sales-projected-to-reach-a-record-of-156-billion-in-2027-semi-reports"},
            {"name": "Inc42 — India GPU Market", "url": "https://inc42.com/features/how-indias-gpu-market-is-being-rewired/"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f9/Wafer_20110212.jpg/1280px-Wafer_20110212.jpg",
        "image_caption": "A semiconductor silicon wafer used in chip manufacturing",
        "image_attribution": "Wikimedia Commons",
        "body": """The global semiconductor equipment industry is about to have its biggest year ever — and the numbers are not close.

SEMI, the industry association that tracks chip-making machinery spending worldwide, released its mid-year forecast this week projecting global semiconductor equipment sales of $165.9 billion in 2026. That is a 23.2 percent jump from the prior year and a sharp upward revision from SEMI's own year-end 2025 forecast of $145 billion. By 2028, the association expects spending to reach $229.5 billion, extending what would be five consecutive years of growth.

The acceleration is almost entirely AI-driven. Wafer fab equipment — the machines that etch, deposit, and lithograph circuits onto silicon — will account for $143.9 billion of the total. Semiconductor test equipment, meanwhile, is forecast to surge 31 percent to $15.3 billion as manufacturers expand capacity for AI-grade chips that require more rigorous validation.

"AI is a major accelerator for demand in more efficient chips," said Ajit Manocha, president and CEO of SEMI, in remarks accompanying the forecast. Manocha, an Indian-origin executive who previously led GlobalFoundries, has steered SEMI through what has become the most capital-intensive period in semiconductor history.

## Where India Fits

For Indian Americans tracking the semiconductor landscape, the timing matters. India has greenlit 12 semiconductor manufacturing projects with combined investment commitments exceeding $20 billion, backed by the Semicon India Programme and the Electronics Manufacturing Clusters initiative. The projects span the spectrum from assembly and packaging to full-scale wafer fabrication.

Tata Electronics is building India's first commercial semiconductor fab in Dholera, Gujarat. Micron Technology, led by Indian-origin CEO Sanjay Mehrotra, is constructing an assembly and test facility in the same state. CG Power and ISMC have additional projects in various stages of approval.

Ashok Chandak, president of SEMI India, said the global investment surge aligns directly with India's ambitions. "This is about bolstering domestic manufacturing capabilities, innovation, and high-value employment opportunities," he said.

## The AI Demand Engine

The spending boom reflects a structural shift in how chips are designed and consumed. AI workloads — from training frontier large language models to running inference at the edge — require specialised silicon that is far more complex and expensive to produce than conventional processors. High-bandwidth memory, advanced packaging, and leading-edge logic nodes at 3nm and below are all seeing capacity build-outs.

The test equipment surge is particularly telling. As AI chips grow more complex, the cost of a defective unit rises dramatically — a single NVIDIA H200 GPU retails for over $30,000. Manufacturers are investing in more sophisticated testing to catch failures before expensive packaging.

China, Taiwan, and South Korea remain the dominant spenders, but the geographic distribution is shifting. The U.S. CHIPS Act has catalysed domestic fab construction, and India's incentive programmes are drawing attention from equipment suppliers looking for the next growth market.

## What It Means for the Diaspora

For the estimated 300,000-plus Indian engineers working in the global semiconductor industry — a figure that includes significant populations in the Bay Area, Austin, and the Pacific Northwest — the spending surge translates directly into job security and career opportunity. Semiconductor design, process engineering, and equipment maintenance roles are expanding faster than the talent pipeline can fill them.

For NRI investors, the equipment makers themselves offer exposure: Applied Materials, ASML, Lam Research, KLA, and Tokyo Electron are the primary beneficiaries of a $166 billion spending year. India's own publicly traded semiconductor companies, while smaller, are attracting fresh institutional interest.

The forecast also adds weight to India's long-term semiconductor ambitions. Building a chip fab is a decade-long commitment. The fact that global equipment spending is accelerating — not plateauing — gives India's dozen projects a more favourable backdrop than sceptics assumed when they were announced. The equipment will need to go somewhere. India is making the case that some of it should go there."""
    },

    # ============================================================
    # Article 2: Apple Stock Record / AI Strategy
    # ============================================================
    {
        "id": str(uuid.uuid4()),
        "headline": "Apple Is the Best-Performing Magnificent Seven Stock of 2026. Its Secret: Not Spending Billions on AI.",
        "subheadline": "While Microsoft, Meta, and Alphabet pour cash into data centres with no clear return date, Apple pays Google for AI access and channels its energy into a foldable iPhone. Wall Street is rewarding the restraint.",
        "slug": make_slug("apple-stock-record-not-spending-on-ai-google-gemini"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Apple employs tens of thousands of Indian engineers and is one of the most widely held stocks among NRI investors. Its AI strategy shift — outsourcing to Google Gemini rather than building its own models — directly affects Indian AI researchers' career calculations and diaspora investment portfolios.",
        "tags": ["apple", "google", "gemini", "ai-spending", "foldable-iphone", "magnificent-seven", "nri-investors", "tim-cook"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "MacRumors / Bloomberg", "url": "https://www.macrumors.com/2026/07/13/apple-stock-record-territory/"},
            {"name": "Barron's — Apple and Google AI Ties", "url": "https://www.barrons.com/articles/apple-google-ai-partnership-openai-lawsuit-51752513600"},
            {"name": "Reuters — OpenAI Hardware Speaker", "url": "https://www.reuters.com/technology/openais-first-hardware-device-will-be-speaker-bloomberg-news-reports-2026-07-15/"}
        ]),
        "score_total": 80,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/f/f7/Tim_Cook_March_2026_%28cropped_2%29.jpg",
        "image_caption": "Apple CEO Tim Cook, whose company has become the top-performing Magnificent Seven stock of 2026",
        "image_attribution": "Wikimedia Commons",
        "body": """Every other mega-cap tech company is spending as if the future depends on building more data centres. Apple looked at the bill and decided to let someone else pay it. So far, the market is saying that was the right call.

Apple shares closed at $315.32 on Friday, up 16 percent for the year and within touching distance of their all-time high of $317.40 set in early June. That makes AAPL the best-performing stock among the so-called Magnificent Seven — ahead of Microsoft, Amazon, Alphabet, Meta, Nvidia, and Tesla. The rally has added nearly $600 billion in market value since June 25, when a price increase on Macs, iPads, and HomePods triggered the stock's worst single-day drop in over a year.

The rebound tells a story about investor sentiment that goes well beyond Apple. Wall Street is growing uneasy about the sums being deployed into AI infrastructure. Microsoft plans to spend $80 billion on data centres in fiscal 2025 alone. Meta, Alphabet, and Amazon are each committing comparable amounts. The returns remain speculative. Revenue from AI products at these companies, while growing, is nowhere near the scale needed to justify the capital outlay.

Apple's approach is different. Rather than build its own frontier AI models or construct purpose-built data centres, Apple is paying Google for access to Gemini — Google's most capable AI system. The revamped Siri, unveiled at WWDC in June alongside iOS 27 and macOS Golden Gate, runs on Apple Foundation Models built in partnership with Google and powered by Gemini. Apple announced in January that its next generation of foundation models would be based on Google's technology and cloud infrastructure.

## The OpenAI Split

The Google partnership has become even more strategically important in light of Apple's dramatic break with OpenAI. Apple filed a lawsuit against OpenAI last week, accusing two former Apple employees — now at OpenAI, including its chief hardware officer — of stealing trade secrets related to unreleased devices and manufacturing processes. OpenAI has denied the allegations, but analysts say the commercial relationship between the two companies is effectively over.

"I think the Apple-OpenAI partnership is over," said D.A. Davidson analyst Gil Luria. "Apple took an aggressive and rare step, fully knowing this would be the consequence." The fallout plays directly into Google's hands, deepening a relationship that already includes the estimated $20 billion annual search deal on Safari.

For Indian engineers at both companies, the implications are practical. Apple's AI research teams in Cupertino and Hyderabad now have a clearer mandate: build on Google's infrastructure rather than compete with it. Indian researchers at OpenAI, meanwhile, face uncertainty about how the hardware division will proceed under legal scrutiny.

## The Foldable Factor

Beyond AI strategy, investors are watching Apple's first foldable iPhone, expected in September. Nikkei reported this month that Apple told suppliers to prepare for 10 million units — up from an earlier forecast of seven to eight million. A foldable at Apple's typical price premium would meaningfully expand the company's average selling price.

The device matters for India's Apple ecosystem too. Apple's India manufacturing has expanded rapidly, with Foxconn and Tata Electronics assembling iPhones in Tamil Nadu and Karnataka. A foldable adds complexity and value to that supply chain.

## Why NRIs Should Watch

Apple is one of the most widely held individual stocks among Indian American investors, according to brokerage surveys. For those with AAPL in their portfolios, the current thesis is straightforward: Apple is capturing AI's consumer benefits without bearing its infrastructure costs. Whether that advantage holds depends on Google continuing to offer competitive access — and on Apple Intelligence features being compelling enough to drive hardware upgrades.

The memory chip cost problem has not gone away. The price hikes on Macs and iPads in June were driven by soaring DRAM and NAND prices, partly caused by AI-driven demand for high-bandwidth memory. Apple has hinted that further increases could follow, including on iPhones. For now, though, investors are looking past cost pressures and toward a product cycle — foldable iPhone, smarter Siri, deeper Google integration — that none of the other Magnificent Seven stocks can match.

Apple made a bet that it could ride the AI wave without building the wave machine. At $315 a share, the market agrees."""
    },

    # ============================================================
    # Article 3: India Data Centre Investment Surge
    # ============================================================
    {
        "id": str(uuid.uuid4()),
        "headline": "India Pulled In $1.56 Billion in Data Centre Investment in Six Months. That Is Seven Times Last Year's Pace.",
        "subheadline": "Amazon just committed $13 billion more, HCLTech is building its own AI data centres, and AI spending is projected to grow 39 percent annually through 2030. India's digital infrastructure buildout is accelerating faster than anyone expected.",
        "slug": make_slug("india-data-center-156-billion-investment-surge-h1-2026"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "NRI investors and technologists are watching India's data centre boom as both an investment opportunity and a signal of the country's deepening role in global AI infrastructure. The surge also creates high-paying jobs for Indians returning from the US.",
        "tags": ["india-data-centers", "amazon-india", "aws", "hcltech", "airtel-nxtra", "ai-infrastructure", "digital-india", "nri-investment"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com/info-tech/india-data-centres-attract-156-billion-foreign-capital/article69797012.ece"},
            {"name": "Madhyamam — Amazon $13B India Investment", "url": "https://madhyamamonline.com/en/tech/amazon-to-invest-additional-13-billion-in-india-for-ai-and-cloud-expansion"},
            {"name": "The Register — HCLTech AI Datacenters", "url": "https://www.theregister.com/2026/07/15/hcltech_ai_datacenter/"},
            {"name": "Communications Today", "url": "https://www.communicationstoday.co.in/india-draws-1-56b-in-digital-infra-investments-in-h1-2026/"}
        ]),
        "score_total": 76,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/37730212/pexels-photo-37730212.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Server racks inside a modern data centre facility",
        "image_attribution": "Pexels",
        "body": """Six months ago, India's data centre investment story was still largely about announcements and intentions. Now the money is arriving.

Foreign investors poured $1.56 billion into India's data centre and digital infrastructure ecosystem in the first half of 2026, according to data tracked by Tracxn. That is nearly seven times the $111 million invested across the entire digital infrastructure ecosystem in the first half of 2025. Data centres alone attracted $738 million in foreign capital during the period.

The biggest single deal was Airtel's Nxtra Data, the data centre arm of Bharti Airtel, which landed $710 million from global investors. But the broader trend is being driven by hyperscalers — Amazon, Google, Microsoft, and their peers — racing to build AI-ready compute capacity in one of the world's fastest-growing digital economies.

## Amazon Goes Bigger

Amazon made the most dramatic move. After CEO Andy Jassy met Prime Minister Narendra Modi in New Delhi, the company announced an additional $13 billion investment in India for AI and cloud infrastructure, taking its total planned spend between 2026 and 2030 to $48 billion. AWS will expand data centre capacity in Mumbai and Hyderabad, providing access to custom AI chips, managed AI services, and cloud developer tools.

The numbers are staggering by any measure. Amazon's cumulative investments in India between 2010 and 2030 will exceed $88 billion. The company says it has digitised 12 million small businesses, enabled over $20 billion in e-commerce exports, and supported 2.8 million jobs in the country.

For Indian Americans who built careers at Amazon and AWS — and there are tens of thousands — the India expansion creates a reverse funnel. Senior roles in cloud architecture, AI operations, and data centre engineering are opening in Hyderabad and Mumbai, and AWS is actively recruiting NRIs willing to relocate. The salary gap between US and India data centre roles, while still significant, is narrowing for senior technical positions.

## HCLTech Enters the Arena

Perhaps the most unexpected development came from HCLTech. The IT services giant, fresh off a strong quarterly earnings report that included $171 million in AI revenue and a record $2.4 billion in new bookings, announced it will build its own AI data centres.

CEO C. Vijayakumar framed the move as a play for India's sovereign AI ecosystem. "This will position us as a key enabler of India's sovereign AI ecosystem, expanding our presence in the fastest-growing market among largest economies," he said. HCL is already in advanced discussions with clients for committed consumption from day one.

The move is unusual. IT services companies have historically rented compute capacity from hyperscalers rather than building their own infrastructure. HCLTech's decision signals that the margins in AI infrastructure — not just AI services — are attractive enough to justify the capital expenditure. It also reflects growing demand from Indian enterprises and government agencies that want AI infrastructure on sovereign soil, not in a foreign cloud region.

## The Numbers Behind the Boom

IDC's Rajiv Ranjan, associate research director for cloud and data centres, expects India's AI spending to grow at a compound annual rate of 39 percent from 2025 to 2030. Public cloud spending is projected to expand at 23 percent over the same period. By 2028-2030, Ranjan estimates that 30 to 40 percent of AI deployments will take place outside the public cloud — in private data centres, edge locations, and sovereign facilities.

India's data centre expansion is now outpacing growth in Southeast Asian markets including Malaysia, Singapore, Indonesia, and Thailand. IT Minister Ashwini Vaishnaw has said total data centre investments will exceed $200 billion, though he has not specified the timeline.

## What It Means for the Diaspora

For NRI investors, India's data centre buildout offers exposure through multiple channels. Bharti Airtel, which owns Nxtra, is publicly traded and its stock has benefited from the data centre narrative. The Nifty IT index, despite a rough 2026, contains companies like HCLTech that are pivoting toward infrastructure revenue. Real estate investment trusts focused on data centre properties are also emerging in India's capital markets.

For Indian technologists in the US, the career calculus is shifting. A decade ago, returning to India meant accepting lower compensation for less interesting work. Today, building AI infrastructure in Hyderabad or Mumbai — for Amazon, Google, or HCLTech — is among the most technically demanding work available anywhere. The $1.56 billion that flowed into India in the first half of this year is not just capital. It is a statement about where the next generation of computing infrastructure will be built."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['headline'][:80]}...")
        print(f"   slug: {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

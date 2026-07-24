#!/usr/bin/env python3
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
        "headline": "Blackstone-Backed AirTrunk Just Pledged $30 Billion to Build India's AI Backbone. The Race for Compute Is On.",
        "subheadline": "Australia's largest data centre operator plans 5 gigawatts of capacity across India, joining a stampede of hyperscaler investment that now exceeds $250 billion in commitments.",
        "slug": make_slug("airtrunk-30-billion-india-data-center-ai-infrastructure"),
        "category": "technology",
        "vertical": "technology",
        "is_editorial": False,
        "diaspora_angle": "NRI investors and professionals tracking India's data infrastructure boom — the country is becoming a global AI compute hub with massive implications for tech careers, return-to-India decisions, and cross-border investment opportunities.",
        "tags": ["data-centers", "ai-infrastructure", "india-tech", "airtrunk", "blackstone", "reliance", "adani"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/"},
            {"name": "TechCrunch", "url": "https://techcrunch.com/"},
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/37730212/pexels-photo-37730212.jpeg",
        "image_caption": "Server racks inside a modern data centre facility",
        "image_attribution": "Pexels",
        "body": """Something extraordinary is happening in Indian real estate, and it has nothing to do with housing. The commodity being hoarded is not square footage but megawatts — and the buyers are not developers but the largest technology companies on earth.

AirTrunk, Australia's biggest data centre operator, announced on Friday that it will invest $30 billion to build 5 gigawatts of new data centre capacity across India by 2030. The company's CEO, Robin Khuda, delivered the news after a meeting with Prime Minister Narendra Modi, calling India "one of the world's most compelling destinations for technology investment."

The scale of the commitment is staggering. Five gigawatts is roughly the power consumption of a mid-sized European country. AirTrunk, backed by Blackstone and the Canada Pension Plan Investment Board, entered India just two months ago through its acquisition of Lumina CloudInfra. It already has 600 megawatts of capacity under development in Mumbai, Chennai, and Hyderabad. The new investment will expand that footprint dramatically.

## The Wall of Capital

AirTrunk is hardly alone. What was a trickle of data centre investment a year ago has become a flood. Amazon has committed $12.7 billion for cloud infrastructure in India through 2030. Alphabet is spending roughly $15 billion on an AI infrastructure hub in Visakhapatnam. Anant Raj signed a $2.6 billion MoU for data centres in Haryana. And the domestic heavyweights are not sitting out: Reliance Industries and Adani Group committed approximately $110 billion and $100 billion respectively earlier this year across AI and digital infrastructure.

Total commitments now exceed a quarter-trillion dollars — a figure that would have been dismissed as fantasy five years ago.

The catalyst is straightforward: India's tax holiday for foreign companies delivering cloud services through domestic data centres, extended through 2047 in the Union Budget. Combined with a large technical workforce, relatively cheap renewable energy, and government coordination that global executives describe as unusually efficient, the incentive structure has tipped.

## The NRI Investment Angle

For Indian Americans watching from Cupertino and Jersey City, the data centre boom is creating an entirely new asset class in India. The "picks and shovels" companies — firms that build, power, and cool these facilities — are already rallying on the Bombay Stock Exchange. Nomura analysts note that foreign institutional shareholding in Indian industrials hit a two-year high at 14% as of March, driven precisely by AI infrastructure plays.

Hitachi Energy India, ABB India, and Cummins India have emerged as indirect beneficiaries. Their order books are swelling with two-to-four-year backlogs from data centre buildouts, creating what Nomura calls "an enviable seller's market."

## The Bottleneck

Not everyone is cheering. India's data centre ambitions face a fundamental constraint: power. Deloitte estimates that data centre buildouts in the Asia Pacific region could require tens of additional terawatt-hours of electricity by decade's end. India's grid, while improving, was not designed for clusters of facilities each consuming hundreds of megawatts.

Water is another concern. Large-scale cooling systems are thirsty, and many proposed sites sit in water-stressed regions. Land acquisition, environmental clearances, and grid connectivity remain the unglamorous variables that will determine whether $250 billion in commitments becomes $250 billion in operational capacity.

The fiscal math is also tightening. India's FY27 deficit target of 4.3% of GDP leaves limited room for additional incentives if the tax holiday proves insufficient. Investment analysts warn that the gap between announced commitments and commissioned capacity could be wide.

## What Comes Next

For the 4.5 million Indians working in the American technology sector, the data centre buildout is reshaping the calculus of return migration. AI infrastructure jobs — from site engineering to cloud architecture — are being created at scale in Hyderabad, Chennai, and Mumbai. The roles require precisely the skills that NRI professionals have spent a decade accumulating at AWS, Google Cloud, and Azure.

The question is whether India can deliver on the operational execution as impressively as it has delivered on the deal-signing. The capital is committed. The policies are in place. Now comes the hard part: pouring concrete, pulling fibre, and plugging in."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Intel Just Made Its First Major Bet on India's Chip Ecosystem. The $3.3 Billion Facility Will Make What Goes Under the Processor.",
        "subheadline": "A glass-core substrate manufacturing plant in Odisha, backed by Intel's process expertise, marks the chipmaker's first significant participation in India's semiconductor mission.",
        "slug": make_slug("intel-odisha-semiconductor-substrate-india-chip-ecosystem"),
        "category": "technology",
        "vertical": "technology",
        "is_editorial": False,
        "diaspora_angle": "NRI semiconductor engineers and investors tracking India's push into the chip supply chain — Intel's Odisha move creates career pathways for returning professionals and opens a new investment corridor in India's industrial east.",
        "tags": ["semiconductor", "intel", "india-semiconductor-mission", "odisha", "chip-manufacturing", "advanced-packaging"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/"},
            {"name": "DIGITIMES Asia", "url": "https://digitimes.com/"},
            {"name": "DQ India", "url": "https://www.dqindia.com/"},
            {"name": "All India Radio News", "url": "https://airnews.in/"}
        ]),
        "score_total": 78,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/2105927/pexels-photo-2105927.jpeg",
        "image_caption": "Close-up of a semiconductor chip with gold pins",
        "image_attribution": "Pexels",
        "body": """For all the noise about India becoming a semiconductor powerhouse, one conspicuous absence has haunted the narrative: Intel. The world's most storied chipmaker had been notably missing from a parade of commitments by TSMC, Applied Materials, Lam Research, and Tokyo Electron. That changed last week.

Intel, along with U.S.-based 3D Glass Solutions, signed a memorandum of understanding with the Odisha state government to build an advanced packaging glass-core substrate manufacturing facility in the Bhubaneswar-Khurda corridor. The project carries an estimated investment of $3.3 billion and represents, by the government's own description, "one of the largest high-technology manufacturing investments in the country."

Union IT Minister Ashwini Vaishnaw and Odisha Chief Minister Mohan Charan Majhi witnessed the signing alongside Intel CEO Lip-Bu Tan. The symbolism was not lost on anyone: Intel's new chief, who took the helm in March, chose India for one of his first major partnership announcements.

## What Substrates Actually Do

To understand why this matters, you need to understand what sits between a silicon chip and the circuit board it connects to. That layer — the substrate — is the unsung translator of the semiconductor world. It routes electrical signals, manages power delivery, and handles the thermal stress that modern processors generate. Without it, the most advanced chip in the world is just an expensive piece of silicon with nowhere to go.

Glass-core substrates are the next frontier. Unlike traditional organic substrates, glass offers superior dimensional stability, tighter interconnect pitch, and better electrical performance at high frequencies — precisely the properties demanded by AI processors, high-performance computing chips, and next-generation telecom equipment.

India currently accounts for less than 5% of global substrate production. The Odisha facility aims to change that with output of roughly 70,000 glass panels annually, 50 million assembled units, and nearly 13,000 advanced 3D heterogeneous integration modules.

## The Bigger Picture

Intel's entry does not exist in isolation. It arrives alongside a cascade of semiconductor moves across India's eastern and southern states. Andhra Pradesh recently announced its first project under the India Semiconductor Mission — an Outsourced Semiconductor Assembly and Test facility by Advanced System In Package Technologies in Visakhapatnam, backed by a ₹2,388-crore investment. Tata Electronics and ASML signed their own MoU. Applied Materials, Lam Research, and Merck Electronics have all committed to Indian operations.

The India Semiconductor Mission, launched in 2023 with an initial pledge of roughly ₹25,000 crore, has evolved from a policy document into a genuine pipeline. The Odisha project alone was approved under ISM in August 2025, with central government fiscal support of ₹799 crore and additional state support of approximately ₹400 crore. Phase one targets commercial production by August 2028, with full build-out by 2030-31.

## The NRI Engineer's Calculation

For the thousands of Indian-origin engineers working at Intel's facilities in Chandler, Hillsboro, and Penang, the Odisha announcement creates a new variable in career planning. Intel will provide "technology know-how and process expertise" — corporate language for deploying experienced engineers to stand up the facility. The project is expected to generate over 1,800 direct high-skilled jobs, with significant indirect employment in the broader ecosystem.

The Bhubaneswar-Khurda corridor is not Bangalore or Hyderabad. It lacks the established tech ecosystem, the international schools, and the social infrastructure that make return migration palatable for families accustomed to American suburbs. But it offers something those saturated metros increasingly cannot: affordable land, government attention, and the chance to build something foundational rather than incremental.

## Reality Check

Optimism should be tempered by the timeline. The consortium must secure land allocation and environmental clearances by September before construction can begin. First shipments are not expected until 2031. India's track record on large industrial projects — characterised by delays in land acquisition, power connectivity, and bureaucratic clearance — gives reason for caution.

The technology transfer question also looms. Intel is providing process expertise and licensing, not building its own fab. The actual manufacturing will be executed by 3DGS through its Indian subsidiary, Heterogeneous Integration Packaging Solutions. Whether the technology transfer is deep enough to build indigenous capability, or shallow enough to create permanent dependency, remains to be seen.

Still, the signal is unmistakable. Intel, under new leadership, has decided that India's semiconductor story is real enough to attach its name and its engineering resources to. For an industry built on decade-long bets, that counts for something."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Nikesh Arora's Palo Alto Networks Hit $3 Billion in Revenue. He Just Declared the 'SaaS-Pocalypse' Dead.",
        "subheadline": "The Indian-origin CEO's cybersecurity empire crossed $200 billion in market value as AI-driven threats prove that more intelligence means more work for defenders, not less.",
        "slug": make_slug("nikesh-arora-palo-alto-networks-3-billion-revenue-saas"),
        "category": "technology",
        "vertical": "technology",
        "is_editorial": False,
        "diaspora_angle": "Indian-origin CEO Nikesh Arora leading one of the most valuable cybersecurity companies in the world — career signal for NRI professionals considering cybersecurity, and investment thesis for diaspora investors watching the AI security trade.",
        "tags": ["cybersecurity", "nikesh-arora", "palo-alto-networks", "indian-tech-leaders", "ai-security"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Wall Street Journal", "url": "https://www.wsj.com/"},
            {"name": "MarketWatch", "url": "https://www.marketwatch.com/"},
            {"name": "Barron's", "url": "https://www.barrons.com/"},
            {"name": "Motley Fool", "url": "https://www.fool.com/"}
        ]),
        "score_total": 76,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/e/ea/Nikesh_Arora_TechCrunch_Disrupt_2015.jpg",
        "image_caption": "Nikesh Arora, CEO of Palo Alto Networks, at TechCrunch Disrupt",
        "image_attribution": "Wikimedia Commons",
        "body": """Six months ago, the narrative was bleak. AI would automate cybersecurity into irrelevance. Software companies would be cannibalised by models that could detect and respond to threats faster than any human team. Cybersecurity stocks were in the doldrums, and analysts were writing obituaries for the sector.

Nikesh Arora had a different view. And this week, the numbers proved him right.

Palo Alto Networks, the cybersecurity giant led by the Indian-born CEO since 2018, reported fiscal third-quarter revenue of $3 billion — up 31% year-over-year and ahead of Wall Street's estimate of $2.94 billion. Adjusted earnings came in at 85 cents per share, beating the consensus of 80 cents. The company raised its full-year revenue guidance to $11.42-$11.43 billion.

On the earnings call, Arora delivered a line that will echo across the industry: "We officially declare the SaaS-Pocalypse for cybersecurity dead."

## The AI Paradox

The logic is counterintuitive but increasingly undeniable. AI does not reduce the need for cybersecurity. It dramatically increases it.

Every AI agent deployed in an enterprise network is a new attack surface. Every large language model processing sensitive data is a potential exfiltration vector. Every autonomous workflow that bypasses human review is an opportunity for adversaries using the same AI tools to find and exploit vulnerabilities at machine speed.

Palo Alto's response has been what Arora calls "platformisation" — consolidating disparate security tools into a single unified platform that can respond to AI-powered threats with its own AI. The company has made five AI-related acquisitions in the past year, including CyberArk for approximately $25 billion (rebranded as Idira for AI agent identity security) and Portkey for AI-specific cybersecurity.

The strategy is working. Next-Generation Security annual recurring revenue jumped 60% to $8.1 billion. Remaining performance obligations — a forward-looking indicator of locked-in revenue — rose 36% to $18.4 billion. The company's market capitalisation crossed $200 billion for the first time, and the stock has nearly doubled since April.

## The Anthropic Connection

In a move that underscores the convergence of AI and security, Palo Alto has been using Anthropic's Mythos model — the same AI that has drawn Pentagon and NSA interest — to scan its own products for vulnerabilities. The results have been dramatic: the company's May "Patch Wednesday" security advisories disclosed 26 CVEs, far exceeding typical monthly disclosures.

Rather than a sign of weakness, Palo Alto is framing this as proof of concept. Finding vulnerabilities before adversaries do is the entire point. "The latest advancements at the AI frontier have increased the level of urgency around cybersecurity," Arora told investors.

## The Arora Story

Nikesh Arora's trajectory is a particular kind of Indian success story — one that took a more circuitous route than the IIT-to-Silicon Valley pipeline. Born in Ghaziabad, Uttar Pradesh, he studied at the Indian Institute of Technology Varanasi before heading to Northeastern University and Boston College. He spent 10 years at Google, rising to Chief Business Officer and earning a reputation as one of the most commercially minded executives in the company's history.

A detour to SoftBank as president and chief operating officer under Masayoshi Son ended after two years. Then came Palo Alto Networks in 2018, and the reinvention that has defined his legacy. Under Arora, the company's revenue has more than tripled. Its strategic pivot from hardware firewalls to cloud-native, AI-powered security has been one of the most successful transformations in enterprise software.

His compensation — consistently among the highest in corporate America — has drawn scrutiny. But the stock performance has largely silenced critics: an investor who bought Palo Alto shares when Arora took over has seen a return of roughly 400%.

## What NRIs Should Watch

For Indian professionals in cybersecurity — and there are tens of thousands across the United States — Arora's success reinforces a career thesis. Cybersecurity is not being disrupted by AI; it is being supercharged by it. Companies are hiring, not firing. Palo Alto alone has expanded headcount significantly, and Arora explicitly noted on the earnings call that "AI is not taking jobs away."

For NRI investors, the cybersecurity sector presents an interesting hedge against the broader AI volatility that hammered Nasdaq last week. While chip stocks cratered on Broadcom's guidance miss, cybersecurity names held firm. The thesis is simple: regardless of which AI company wins the model race, every one of them needs to be secured.

Arora, characteristically, put it more bluntly. "Six months ago, cybersecurity stocks were doomed because AI was going to protect every one of us and we were all out of a job," he told Jim Cramer on CNBC's Mad Money. "Suddenly, we're hiring more people."

The SaaS-Pocalypse, it turns out, was not a prophecy. It was a buying opportunity."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

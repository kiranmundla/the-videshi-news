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
        "headline": "Wall Street Asked If Arista's AI Boom Was Over. Jayshree Ullal Just Lifted the Bet to 1.6 Terabits.",
        "subheadline": "Arista Networks grew revenue 35% to $2.7 billion as hyperscalers wired their AI data centres with its switches. The Indian-origin CEO is now selling the plumbing for the next wave.",
        "slug": make_slug("jayshree-ullal-arista-networks-ai-networking-1-6-terabit-data-center-nri"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Arista is one of Silicon Valley's quietest wealth machines for Indian-American engineers and investors, and its fortunes now ride entirely on whether the AI data-centre build-out keeps going.",
        "tags": ["ai", "indian-tech", "silicon-valley", "data-centers", "arista"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Zacks Analyst Blog", "url": "https://www.zacks.com/stock/news/2026/06/24/top-analyst-reports-arista-networks"},
            {"name": "Arista Networks Q1 2026 Results (Business Wire)", "url": "https://www.businesswire.com/news/home/arista-networks-q1-2026-results"},
            {"name": "MarketBeat", "url": "https://www.marketbeat.com/stocks/NYSE/ANET/"}
        ]),
        "score_total": 74,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/9/9b/Jayshree_Ullal_Arista_CEO.jpg",
        "image_caption": "Jayshree Ullal, chairperson and CEO of Arista Networks",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": """For a few weeks this spring, the market started to wonder whether Arista Networks had peaked. The stock slipped, analysts published the inevitable "is it still a buy?" notes, and insiders — including CEO Jayshree Ullal herself — trimmed holdings under pre-arranged plans. Then the numbers landed, and the doubt looked premature.

Arista grew first-quarter revenue 35% year over year to $2.7 billion, with operating margins near 48% and a customer net promoter score of 89 — the kind of figure most enterprise vendors never see. Over the past six months its shares have climbed roughly 33% even as the broader software industry fell 17%. The reason is simple: when a hyperscaler builds an AI data centre, the GPUs get the headlines, but the switches that move data between them are increasingly Arista's.

## The plumbing of the AI boom

Ullal, who was born in London, raised in New Delhi and runs Arista from Santa Clara, has spent nearly two decades turning a networking startup into one of Silicon Valley's most valuable infrastructure firms. The current pitch is "Arista 2.0" — extending from cloud switching into campus networking, routing and what the company calls AI fabrics, the dense internal networks that connect thousands of chips inside a single training cluster.

The roadmap is now explicitly about staying ahead of the curve. Arista is gaining traction in 800-gigabit deployments and has begun talking up 1.6-terabit platforms designed for rack-scale AI systems. It also announced an XPO standard meant to cut networking racks by up to 75% and floor space by 44% versus traditional optics — a direct answer to the power and real-estate crunch every data-centre operator now faces.

## Why an NRI should care

This is not abstract. Arista is one of the quieter engines of Indian-American wealth creation in tech. On the 2025 Hurun India Rich List, Ullal ranked as the richest Indian professional manager in the world, ahead of Satya Nadella and Sundar Pichai, on the strength of her Arista stake. Thousands of engineers — a large share of them of Indian origin — hold the company's stock through RSUs that have compounded for years.

That concentration cuts both ways. Arista's growth is tightly coupled to a handful of cloud customers and to one assumption: that the AI capital-expenditure wave keeps rolling. Management itself flags customer concentration and a premium valuation as risks, and rivals from Cisco to optical specialist Ciena are circling the same AI-networking budgets. The recent wobble in the stock was a reminder that "picks and shovels" companies are only as durable as the gold rush they serve.

For the Bay Area engineer weighing an offer, or the NRI investor deciding whether to trim a position that has quietly become a large chunk of the portfolio, the calculus is the same one facing the whole AI trade. The fundamentals are real — 35% growth is not a mirage. But Arista is now priced for a build-out that has to continue at full tilt. Ullal is betting it will, and she is putting the company's roadmap where her mouth is, selling the 1.6-terabit future before anyone has finished buying the 800-gig present.

## What's next

Watch the next earnings print for one number above all: the order backlog and guidance for AI-fabric deployments. If hyperscaler capex holds, Arista's supply-constrained problem is a good one to have. If the trillion-dollar Nasdaq jitters of recent weeks harden into actual spending cuts, the company that sells the plumbing will feel it fast — and so will every diaspora engineer whose net worth is denominated in ANET shares."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Every IT Firm Says AI Will Shrink Its Workforce. At Infosys's AGM, Nandan Nilekani Said the Opposite.",
        "subheadline": "Infosys sees a $300-400 billion AI-services market by decade's end and plans to keep hiring 20,000 freshers a year — a sharp break from the layoff narrative gripping the rest of tech.",
        "slug": make_slug("infosys-agm-nandan-nilekani-salil-parekh-ai-services-400-billion-fresher-hiring-nri"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "For the millions of Indians and NRIs whose careers run through Infosys and its peers, the company is making the contrarian case that AI is a tailwind for IT services jobs, not their executioner.",
        "tags": ["ai", "indian-tech", "it-services", "infosys", "jobs"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Storyboard18", "url": "https://www.storyboard18.com/how-it-works/infosys-sees-400-billion-ai-services-opportunity-plans-to-maintain-fresher-hiring"},
            {"name": "Microsoft Source Asia", "url": "https://news.microsoft.com/source/asia/2026/06/03/infosys-tcs-wipro-microsoft-365-copilot/"},
            {"name": "Livemint", "url": "https://www.livemint.com/companies/news/top-it-firms-h1b-visas-slump-40-percent"}
        ]),
        "score_total": 76,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/6/62/Nandan_M._Nilekani.jpg",
        "image_caption": "Nandan Nilekani, co-founder and chairman of Infosys",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": """The mood music in technology this summer is grim. Oracle disclosed 21,000 job cuts and named AI as the cause. Accenture had its worst week on record on fears that AI will gut IT services. Cognizant's own research says AI can already handle $4.5 trillion of US work tasks. Into that gloom, Infosys used its 45th annual general meeting to make an almost defiant argument: AI will not replace companies like ours, and we are going to keep hiring.

Chairman Nandan Nilekani put a number on the optimism. "By the end of the decade, we see a $300-400 billion opportunity in AI-first services," he told shareholders. His logic is that enterprises are buying AI faster than they can actually deploy it, and that gap — the messy work of cleaning data, rebuilding processes and wiring agents into legacy systems — is exactly what a services firm gets paid to close. "AI will not replace companies like ours," he said. "It will amplify those who move with purpose and adapt with speed."

## The hiring signal

CEO Salil Parekh backed the words with a plan. Infosys hired around 20,000 freshers in FY26, lifting its workforce to roughly 325,000, and expects a similar intake in FY27. That is striking at a moment when peers are freezing campus hiring. Parekh said the company is now running about 4,800 AI projects, that nearly 90% of its clients are "AI-aware," and that its annualised AI-services revenue has crossed $1 billion — about 5.5% of total revenue. Infosys has built around 600 AI agents internally and is expanding a pool of "forward-deployed engineers" who sit inside client operations.

The company laid out six service lines it thinks will drive growth: AI strategy and agent development; preparing enterprise data for models; reimagining business processes with agents; modernising legacy tech estates; designing AI-enabled products; and securing responsible AI deployment. The throughline is that AI creates more integration work, not less.

## Why this matters to the diaspora

No industry is more entangled with the Indian diaspora than IT services. India's six largest firms employ about 1.9 million people, and for decades the path from a Bengaluru or Hyderabad campus to a US client site — and often to a green card — ran through exactly these companies. That path is narrowing. H-1B approvals for the top six Indian IT firms fell 40% this year to about 11,041, with TCS hardest hit; Infosys was the only one to gain. The firms are responding by shifting more work offshore and hiring locally in the US.

So Nilekani's framing carries weight beyond a shareholder meeting. If AI genuinely expands the services pie, it cushions the blow of tighter visas — more of the work can be done from India, and the headcount keeps growing even as the US pipeline shrinks. If he is wrong, and AI compresses billable hours the way the skeptics fear, the diaspora's most reliable career ladder gets shakier at both ends at once.

There are reasons for caution. The same week Infosys talked up hiring, it and its peers also confirmed they have scaled Microsoft 365 Copilot to over 300,000 employees combined — a tool whose entire selling point is doing more with fewer people. Reconciling "AI makes our own staff more productive" with "we will keep hiring 20,000 freshers" is the central tension in the whole IT-services story.

## What's next

The real test comes with quarterly results and the FY27 guidance. Watch whether Infosys's AI revenue keeps compounding past that $1 billion run-rate, and whether the fresher intake actually materialises or quietly slips. For now, the second-largest of India's IT giants has planted a flag on the optimistic side of the AI-and-jobs debate — and a lot of diaspora careers are riding on whether it is right."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "For 30 Years India Guarded Its Workhorse Rocket. It Just Decided to Hand the Keys to Private Firms.",
        "subheadline": "IN-SPACe has invited private companies to take over the PSLV — the rocket that launched Chandrayaan and 104 satellites at once. Only Indian-controlled firms qualify.",
        "slug": make_slug("isro-pslv-technology-transfer-private-sector-in-space-small-satellite-launch-nri"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "India's privatising space sector is opening up to NRI capital and returning engineers just as the global small-satellite launch market explodes — but the Indian-ownership rule sets clear terms for who can play.",
        "tags": ["space-tech", "indian-tech", "isro", "startups", "deeptech"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Trade Brains", "url": "https://tradebrains.in/govt-plans-isro-pslv-rocket-technology-transfer-to-private-sector/"},
            {"name": "TechCrunch", "url": "https://techcrunch.com/2026/05/skyroot-india-space-tech-unicorn/"},
            {"name": "Livemint", "url": "https://www.livemint.com/news/india/isro-five-commercial-small-rocket-launches-fy27"}
        ]),
        "score_total": 72,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/8/8f/PSLV-C50%2C_CMS-01-_Lift-off_003.jpg",
        "image_caption": "An ISRO PSLV rocket lifts off from Sriharikota",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": """For three decades, the Polar Satellite Launch Vehicle was India's crown jewel and its closely held secret. Built, tested and flown entirely by government scientists, the PSLV put Chandrayaan on its way to the Moon, launched a record 104 satellites in a single flight, and carried payloads for more than 30 countries across over 50 missions. Now the government is preparing to do something that would have been unthinkable not long ago: hand the rocket over to private industry.

Pawan Goenka, who heads IN-SPACe — the body that regulates private space activity in India — confirmed that an Expression of Interest has gone out to transfer PSLV technology to private firms. His one condition was blunt: only companies that are majority-owned and controlled by Indians will qualify. No exceptions.

## Why give away the crown jewel

The logic is volume. The global small-satellite launch market is growing fast, and the United States and China are already ahead. ISRO, launching a handful of rockets a year, cannot scale to meet that demand alone. Privatising the PSLV is a bet that Indian companies can industrialise a proven design — turning a national programme into an actual industry. India's space sector generated about $8.4 billion in annual revenue last year, roughly 2% of the global market; government estimates put it at $44 billion, or about 8% of the world total, by 2033.

The timing dovetails with a private sector that is suddenly real. Skyroot Aerospace, founded by former ISRO engineers, became India's first space-tech unicorn after a $60 million raise at a $1.1 billion valuation, and is preparing the maiden orbital flight of its Vikram-1 rocket from Sriharikota. Agnikul Cosmos, incubated at IIT Madras, has flown a vehicle powered by the world's first single-piece 3D-printed rocket engine. ISRO itself plans five commercial SSLV missions in FY27. The PSLV handover would give these and other firms a flight-proven heavy-lifter to build a launch business around, rather than starting from a blank sheet.

## The diaspora angle

The Indian-ownership rule is the part NRIs should read closely. India is courting global capital and talent for its space ambitions — Ram Shriram, the Sherpalo Ventures founder and Alphabet board member, has joined Skyroot's board, and BlackRock-affiliated funds backed its latest round. But Goenka's "majority-owned and controlled by Indians" line draws a clear boundary: foreign and diaspora money is welcome, foreign control is not. For NRI investors and returning engineers, that means the opportunity is real but structured — minority stakes, technical partnerships and founder roles for those willing to relocate, rather than outright ownership from abroad.

That structure mirrors a broader pattern. India is pouring billions into deep tech, yet many of its most ambitious founders still buy one-way tickets to America for capital and customers. Space is one of the few sectors where the pull may run the other way: the hardware has to be built in India, the launchpads are in India, and the regulatory regime explicitly rewards Indian control. For a diaspora engineer who cut their teeth at a US aerospace firm, a privatised PSLV ecosystem is a rare reason to consider the flight home.

## What's next

The EOI is only the opening move; the terms of technology transfer, the qualifying criteria and the eventual winners will determine whether this becomes a genuine industry or a controlled experiment. Watch for Skyroot's Vikram-1 orbital attempt, expected imminently — a success would prove an Indian private company can reach orbit, and make the case for trusting private hands with the PSLV that much stronger."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

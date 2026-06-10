#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-06-10 15:00 UTC batch"""
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
    # -------------------------------------------------------------------
    # ARTICLE 1: India freezes Starlink approvals
    # -------------------------------------------------------------------
    {
        "id": str(uuid.uuid4()),
        "headline": "India Just Froze Starlink's Launch. The Iran War Is the Reason.",
        "subheadline": "Bloomberg reports that India's security agencies have withheld final clearances for Musk's satellite internet service. Starlink says the story is wrong. Either way, rural broadband for 1.4 billion people is stuck.",
        "slug": make_slug("india-freezes-starlink-approvals-iran-war-security"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "NRIs who hoped Starlink would bring reliable internet to their families in rural India face an indefinite wait. The freeze also stalls Jio and Airtel satellite partnerships, affecting diaspora-backed telecom investments.",
        "tags": ["starlink", "india-telecom", "spacex", "elon-musk", "satellite-internet", "iran-war", "jio", "airtel"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Bloomberg", "url": "https://news.bloombergtax.com/daily-tax-report/starlink-india-launch-hits-roadblock-before-spacex-ipo-1"},
            {"name": "Livemint", "url": "https://www.livemint.com/news/india/india-starlink-approval-on-hold-security-concerns-iran-conflict-elon-musk-satellite-broadband-11749504073700.html"},
            {"name": "Storyboard18", "url": "https://www.storyboard18.com/digital/starlink-says-india-launch-plans-remain-on-track-rejects-reports-of-approval-delays-58920.htm"},
            {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com/info-tech/in-active-talks-with-indian-govt-received-encouraging-feedback-starlink/article69671234.ece"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3f/Starlink_Satellites_Imaged_from_CTIO.jpg/1280px-Starlink_Satellites_Imaged_from_CTIO.jpg",
        "image_caption": "Starlink satellite constellation trails photographed from the Cerro Tololo observatory",
        "image_attribution": "Wikimedia Commons",
        "body": """For over a year, Elon Musk's Starlink has been inching toward commercial launch in India — securing a Global Mobile Personal Communication by Satellite licence, setting up ten gateways with a hub in Mumbai, and sending senior executives to meet government ministers. On Tuesday, Bloomberg reported that the inch just turned into a wall.

India's security agencies under the Ministry of Home Affairs have withheld the final clearances Starlink needs to begin selling satellite broadband to Indian consumers, according to people familiar with the matter. The trigger: reports that Starlink terminals were used during the Iran conflict despite the service never being licensed there.

## The Security Calculus

For New Delhi, the Iran episode crystallised a dormant fear. Starlink is a US-owned, globally operated network of over 6,000 low-earth-orbit satellites. It can beam internet to any patch of land with a $499 terminal. That capability is commercially thrilling and strategically terrifying — especially for a country that jealously guards its telecommunications perimeter.

Indian officials are now asking a pointed question: if a geopolitical crisis erupts and Washington's interests diverge from New Delhi's, can Starlink guarantee it will comply with Indian security requirements? The company has submitted affidavits claiming it meets local data-storage rules, but the broader sovereignty question remains unanswered.

The freeze does not only affect Musk. It has stalled a satellite-spectrum pricing proposal that the Department of Telecommunications had already finalised but never sent to the Union Cabinet for approval. That means Bharti Airtel's partnership with Eutelsat OneWeb and Reliance Jio's satellite plans are also stuck in regulatory limbo.

## Starlink Pushes Back

Hours after the Bloomberg report went live, Lauren Dreyer, Starlink's Vice President of Business Operations, took to X to call the story "misleading" and based on "unsubstantiated claims from anonymous sources."

"We have worked with the Government through all of the required regulatory and compliance processes in a transparent and responsible manner," Dreyer wrote. She added that Starlink had developed a "bespoke deployment model" for India designed to meet the country's sovereign technology and security requirements.

The company says it has received "nothing but encouraging feedback" from authorities on its potential to connect remote and underserved regions — the kind of villages where NRI families still struggle with patchy BSNL connections and power cuts that take down mobile towers.

## What This Means for the Diaspora

The Indian diaspora has a direct stake in this standoff, and not just because some of them work at SpaceX.

For NRIs with family in Tier-3 towns, tribal belts, and the rural northeast, Starlink represented the most plausible path to reliable internet. Mobile coverage remains spotty outside urban India, and BSNL's 4G rollout has been glacially slow. Satellite broadband — whether from Starlink, OneWeb, or Jio's satellite arm — was supposed to close that gap.

The freeze also has investment implications. Airtel and Jio are among the most widely held Indian stocks in NRI portfolios. Both companies have bet significant resources on satellite partnerships. If spectrum allocation is delayed indefinitely, those partnerships become expensive liabilities rather than growth catalysts.

Then there is the SpaceX IPO. Bloomberg's reporting explicitly frames the India freeze as a roadblock arriving "before SpaceX IPO." Starlink's addressable market shrinks meaningfully without India — the world's second-largest telecom market by subscribers. For NRI investors eyeing the SpaceX listing, India's regulatory mood matters.

## The Bigger Picture

India's caution is not irrational. The country has a history of asserting telecom sovereignty, from banning Huawei equipment to requiring local data storage. Satellite internet, by its nature, complicates that control — signals bypass terrestrial infrastructure entirely.

But caution carried too far becomes paralysis. India added 100 million internet users between 2023 and 2025, yet over 400 million Indians remain offline. Every month that satellite broadband stays frozen is a month those people wait.

The government faces a genuine dilemma: open the door to Starlink and accept the sovereignty risk, or keep it shut and accept the connectivity cost. For now, the door is shut. The question is whether anyone — Musk, Modi, or the market — has enough leverage to force it open."""
    },
    # -------------------------------------------------------------------
    # ARTICLE 2: Tata Electronics $30B semiconductor play
    # -------------------------------------------------------------------
    {
        "id": str(uuid.uuid4()),
        "headline": "Tata Electronics Wants a $30 Billion Chip Empire. The Dholera Fab Is Just the Start.",
        "subheadline": "From a Gujarat wafer fab to advanced packaging in Assam, the Tata Group is building India's most ambitious semiconductor play. For NRI engineers in the chip industry, the career calculus just changed.",
        "slug": make_slug("tata-electronics-30-billion-semiconductor-empire-india"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Thousands of Indian-origin engineers work at Intel, TSMC, Micron, and Samsung fabs worldwide. Tata's $30B play creates a credible return-to-India path in semiconductor manufacturing for the first time, plus a new investment thesis for NRI portfolios tracking India's industrial ambitions.",
        "tags": ["tata-electronics", "semiconductor", "india-chip-fab", "dholera", "manufacturing", "nri-career"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "EMSNow", "url": "https://www.emsnow.com/india-accelerates-semiconductor-and-display-ambitions-with-new-approvals-ai-infrastructure-expansion/"},
            {"name": "DIGITIMES", "url": "https://www.digitimes.com/news/a20260522PD200/tata-semiconductor-assam-india.html"},
            {"name": "DIGITIMES", "url": "https://www.digitimes.com/news/a20250916PD208/tata-electronics-rare-earth-semiconductor-delay.html"},
            {"name": "DIGITIMES", "url": "https://www.digitimes.com/news/a20250507PD210/fujifilm-semiconductor-materials-india-tata.html"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/4/46/Natarajan_Chandrasekaran_-_India_Economic_Summit_2011.jpg",
        "image_caption": "Natarajan Chandrasekaran, chairman of Tata Sons, at the India Economic Summit",
        "image_attribution": "Wikimedia Commons",
        "body": """When Natarajan Chandrasekaran took the helm of Tata Sons in 2017, the conglomerate was synonymous with steel, software services, and salt. Semiconductors did not feature in anyone's projection. Nine years later, Tata Electronics is targeting a $30 billion business built on wafer fabrication, advanced packaging, and electronics services — a figure that would make it one of the largest chip enterprises outside the established East Asian foundry belt.

The ambition is real. The question is whether it can survive contact with the physics of chipmaking.

## The Dholera Fab

The centrepiece is a 300mm wafer fabrication facility in Dholera, Gujarat, built with technology transfer from Taiwan's Powerchip Semiconductor Manufacturing Corporation (PSMC). Construction began in 2024, and the first chips are targeted for mid-2027 — a timeline that has always looked aggressive and now faces a new headwind.

A DIGITIMES report flagged that rare earth shortages could delay the Dholera fab's rollout. Semiconductor-grade rare earths are controlled by a handful of Chinese and Australian suppliers, and India's domestic refining capacity remains negligible. If Tata cannot secure these materials on schedule, the mid-2027 target slips — potentially by a year or more.

Still, the infrastructure around Dholera is taking shape. Japan's Fujifilm is building a semiconductor materials factory in Gujarat specifically to supply the Tata fab with photoresists and specialty chemicals. That a Japanese materials giant is willing to build India-specific capacity signals genuine confidence in the project's trajectory.

## Beyond Wafers: The Assam OSAT Plant

What makes Tata's play unusual is its breadth. Most newcomers to chipmaking start with one thing — a fab, or a packaging plant, or a design house. Tata is doing all three simultaneously.

Its Outsourced Semiconductor Assembly and Test (OSAT) facility in Jagiroad, Assam, is nearing production readiness. This plant will handle the back end of chipmaking: taking finished silicon wafers and packaging them into the chips that go into phones, cars, and data centres. OSAT is less glamorous than wafer fabrication, but it is where margins are more forgiving and where India's labour cost advantage matters most.

Qualcomm has been in active discussions with Tata about leveraging this Assam capacity. If a deal materialises, it would give Tata a major anchor customer and validate India's packaging capabilities for the global supply chain.

## The $30 Billion Question

Building a $30 billion semiconductor business requires three things India has never demonstrated at scale: sustained capital commitment over decades, a trained workforce numbering in the tens of thousands, and yields high enough to compete with TSMC and Samsung.

On capital, Tata appears committed. The Dholera fab alone is estimated at $11 billion with government subsidies under the India Semiconductor Mission covering roughly half. Adding the Assam OSAT plant, the electronics manufacturing services business (which already assembles iPhones for Apple), and planned expansions, the $30 billion envelope becomes plausible over a 10-15 year horizon.

On workforce, the challenge is acute. India produces plenty of electrical engineering graduates but almost none with cleanroom experience. Tata has been recruiting process engineers from TSMC, Intel, and GlobalFoundries — many of them Indian-origin professionals in their 30s and 40s who see a chance to return home without abandoning their career specialisation.

On yields, only time will tell. PSMC's technology transfer covers 28nm and 40nm process nodes — mature technologies by global standards, but exactly the nodes that dominate automotive, IoT, and industrial chip demand. These are the chips the world is actually short of, not the cutting-edge 3nm processors that grab headlines.

## What NRIs Should Watch

For the estimated 15,000 Indian-origin engineers working in semiconductor fabs across Arizona, Oregon, Taiwan, and South Korea, Tata's buildout represents something that did not exist five years ago: a reason to go back.

The compensation gap remains wide. A senior process engineer at Intel's Chandler fab earns $180,000-250,000; Tata's Dholera salaries are reportedly in the $60,000-90,000 range. But the career trajectory is different. Early employees at a greenfield fab in a country with no existing fab ecosystem can write their own roles in ways that a 30-year veteran plant never permits.

For NRI investors, the play is indirect. Tata Electronics is not publicly listed, but its success would lift Tata Motors (EV demand drives chip consumption), TCS (manufacturing IT), and the broader Tata Group valuation. It would also validate the India Semiconductor Mission's subsidy model, potentially unlocking further government support for the sector.

The $30 billion target is aspirational, not guaranteed. But for the first time, India's semiconductor ambitions have a corporate backer with the balance sheet, the political connections, and the operational seriousness to make them plausible. Whether Tata can execute is the story of the next decade."""
    },
    # -------------------------------------------------------------------
    # ARTICLE 3: Tech Mahindra + NVIDIA sovereign AI
    # -------------------------------------------------------------------
    {
        "id": str(uuid.uuid4()),
        "headline": "Tech Mahindra and NVIDIA Built a Sovereign AI Lab. It Speaks Bhojpuri.",
        "subheadline": "Project Indus 2.0 is an LLM trained on Hindi and dozens of its dialects. Backed by NVIDIA's enterprise stack, it is India's most serious attempt at AI that works for the 600 million people Silicon Valley's models ignore.",
        "slug": make_slug("tech-mahindra-nvidia-sovereign-ai-project-indus-hindi"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "For NRI engineers building LLMs at Google and Meta, Project Indus 2.0 poses a professional question: could India-specific AI become a career track? For NRIs sending money home via UPI or using Hindi banking apps, sovereign AI determines whether those services actually work in their parents' dialect.",
        "tags": ["tech-mahindra", "nvidia", "sovereign-ai", "project-indus", "hindi-llm", "agentic-ai", "indian-languages"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "SAMENA Council", "url": "https://www.samenacouncil.org/news/tech-mahindra-announces-ai-center-of-excellence-powered-by-nvidia-ai-enterprise-and-omniverse-platforms"},
            {"name": "TechCrunch (via Owler)", "url": "https://www.owler.com/reports/reliance/nvidia-deepens-india-ai-drive-with-new-partnerships/1749514099120"},
            {"name": "CentralCharts", "url": "https://www.centralcharts.com/en/news/4717750-mimik-and-tech-mahindra-unveil-a-pioneering-agentic-ai-production-center"}
        ]),
        "score_total": 75,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/e/e6/Jen-Hsun_Huang_2025.jpg",
        "image_caption": "NVIDIA CEO Jensen Huang, whose enterprise AI stack powers Tech Mahindra's new Center of Excellence",
        "image_attribution": "Wikimedia Commons",
        "body": """The large language models that dominate global AI — GPT-4, Claude, Gemini — are extraordinarily capable in English. They are passable in standard Hindi. They are functionally useless in Bhojpuri, Dogri, Maithili, and the dozens of other Hindi dialects spoken by hundreds of millions of Indians who will never type a prompt in English.

Tech Mahindra just made a bet that this gap is not merely a social problem but a commercial one. The company has launched a Center of Excellence in Pune and Hyderabad, powered by NVIDIA's AI Enterprise stack, to build sovereign AI applications for the Indian market. The centrepiece is Project Indus 2.0 — an advanced language model trained on Hindi and its dialect family, designed to serve retail, banking, healthcare, and citizen services.

## What "Sovereign AI" Actually Means

The term "sovereign AI" gets thrown around loosely. In this case, it means something specific: language models that are trained on Indian linguistic data, run on infrastructure that can be governed by Indian regulations, and serve use cases where foreign-built models fall short.

Project Indus 2.0, built using NVIDIA NeMo, goes beyond standard Hindi. It handles Bhojpuri (spoken by roughly 50 million people across UP, Bihar, and Jharkhand), Dogri (concentrated in Jammu), Maithili (Bihar's second language), and other dialects that mainstream AI simply does not cover. The model is designed for real-world deployment: a bank's voice assistant that understands a farmer in Gorakhpur, or a healthcare chatbot that can triage symptoms described in Maithili.

This is not an academic exercise. India's digital public infrastructure — UPI, Aadhaar, DigiLocker — has created a vast base of digitally active citizens who interact with government and financial services primarily in their regional dialect, not in the standardised Hindi that Delhi bureaucrats use. For AI to be useful to these people, it has to speak the way they actually speak.

## The NVIDIA Stack

The technical architecture matters because it determines whether Indus 2.0 is a research demo or a deployable product. Tech Mahindra is using the full NVIDIA AI Enterprise platform: NeMo for model training and customisation, NIM microservices for inference deployment, and RAPIDS for data processing. The CoE also leverages NVIDIA Omniverse for industrial digital twins — a separate capability aimed at manufacturing and automotive clients.

"Built with NVIDIA technology, Tech Mahindra's Center of Excellence will accelerate the development and adoption of sovereign AI LLMs and applications tailored for India's diverse industries and linguistic landscape," said John Fanelli, NVIDIA's VP of Enterprise Software.

The partnership is commercially structured, not philanthropic. NVIDIA gets a showcase deployment for its enterprise AI stack in one of the world's fastest-growing AI markets. Tech Mahindra gets differentiated IP that competitors like TCS, Infosys, and Wipro do not yet have. For NVIDIA, which has been deepening its India footprint through partnerships with Reliance, Tata, and multiple state governments, Tech Mahindra is one node in a broader strategy to make India an NVIDIA-stack economy.

## The Agentic AI Layer

Project Indus 2.0 is only half the story. Tech Mahindra is also using the NVIDIA NIM Agent Blueprint to build AI virtual assistants for call centres — a market where the company has tens of thousands of employees and where the economics of automation are brutally clear.

The agentic AI play extends further. Tech Mahindra separately partnered with mimik to launch an Agentic AI Production Center — an operational hub for designing, deploying, and scaling AI agents that run on edge devices (cars, drones, industrial sensors) without constant cloud connectivity. This is physical AI, not chatbot AI, and it targets the automotive and telecom sectors where Tech Mahindra's engineering services business already operates.

Atul Soneja, Tech Mahindra's COO, framed the strategy explicitly: "We are redefining the boundaries of AI innovation. Collaborating with NVIDIA, we are setting a new benchmark for enterprise-grade AI development by seamlessly integrating GenAI, industrial AI and sovereign large language models."

## Why NRIs Should Pay Attention

For the tens of thousands of Indian-origin engineers building LLMs at Google, Meta, OpenAI, and Anthropic, Project Indus 2.0 represents a professionally interesting question. India-specific AI — models that work in languages and dialects that global models ignore — could become a distinct career track, not just a CSR project.

For NRIs whose parents navigate UPI, banking apps, and government portals in Hindi or its dialects, the quality of sovereign AI directly affects their daily experience. A voice assistant that actually understands Awadhi is the difference between a working service and a frustrating one.

And for investors watching Indian IT services, Tech Mahindra's AI play is a differentiation story. The company's stock has underperformed TCS and Infosys over the past two years. If sovereign AI and agentic AI generate real enterprise revenue — not just press releases — it could change the narrative.

The gap between global AI and India's linguistic reality is wide. Tech Mahindra and NVIDIA are betting it is also profitable. That bet will take years to prove, but the CoE is running, the model is training, and for the first time, Bhojpuri has a seat at the AI table."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

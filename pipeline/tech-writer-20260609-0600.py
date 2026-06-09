#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-06-09 06:00 UTC"""
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


# ─────────────────────────────────────────────
# ARTICLE 1: Shantanu Narayen stepping down from Adobe
# ─────────────────────────────────────────────

article1_body = """Shantanu Narayen is doing what almost no Indian-origin tech CEO has done in Silicon Valley: leaving on his own terms, with the company in better shape than he found it.

After 18 years as chief executive of Adobe, Narayen announced in March that he would step down once a successor is named, transitioning to chairman of the board. The search, led by lead independent director Frank Calderoni, is weighing both internal heavyweights and external "AI-first" candidates from companies like Google and OpenAI.

## The Numbers That Define a Tenure

When Narayen took over in December 2007, Adobe was a $3.4 billion desktop software company with about 7,000 employees. Today it generates over $25 billion in annual revenue and employs more than 30,000 people. Its stock has risen more than sixfold over that period, comfortably outpacing the S&P 500.

His signature move — the 2011 shift from perpetual software licences to cloud subscriptions — was arguably the most consequential business model transformation in enterprise software history. Creative Cloud turned Photoshop, Premiere Pro, and Illustrator from one-time purchases into a recurring revenue engine that now accounts for the vast majority of Adobe's top line.

## The AI Chapter

Narayen's final act has been steering Adobe into the generative AI era. Firefly, the company's commercially-safe AI model trained exclusively on licensed content, has crossed $250 million in ending annual recurring revenue. AI-first ARR tripled year-over-year in the most recent quarter, with video generation consumption rising eightfold and audio generation doubling.

Jensen Huang, NVIDIA's CEO, recently said Adobe's opportunity has expanded "100 to 1,000 times" thanks to AI — a bullish endorsement as Firefly runs on NVIDIA's stack. Famed investor Michael Burry has called the stock a "fat pitch," pointing to Firefly's enterprise integrations as a moat that competitors will struggle to replicate.

Still, the market hasn't been convinced. Adobe shares are down roughly 27% year-to-date, trading near three-year lows. The $20 billion Figma acquisition collapsed under regulatory pressure in 2023, leaving a gap in Adobe's collaborative design strategy just as AI-native rivals proliferated.

## The Successor Question

The heir apparent is widely considered to be David Wadhwani, president of Digital Media, who has been the public face of Adobe's AI integration strategy. Another strong internal candidate is Anil Chakravarthy, president of Customer Experience Orchestration. Industry insiders say the board is also looking externally for an "AI-first" leader.

Meanwhile, Adobe is not standing still. The company recently announced a $1.9 billion acquisition of Semrush to bolster its digital marketing capabilities, along with a massive $25 billion stock repurchase programme. Q2 FY2026 earnings land on June 11 — a report that will test whether Firefly's growth trajectory can reverse the stock's slide.

## Why This Matters to Indian Tech Professionals

Narayen, who grew up in Hyderabad and studied electronics at Osmania University before earning graduate degrees at Bowling Green State and UC Berkeley, represents a particular archetype in the Indian diaspora: the IIT-to-boardroom pipeline that produced Sundar Pichai, Satya Nadella, and Arvind Krishna. His departure leaves a visible gap in that constellation.

For the tens of thousands of Indian professionals who work at Adobe or compete with its products, the successor choice will signal where the company — and the broader creative software industry — heads next. Whether the board picks another Indian-origin leader or breaks the pattern, the decision will ripple through Silicon Valley's most powerful network."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "Shantanu Narayen Is Leaving Adobe. He Turned a $1 Billion Company Into a $25 Billion AI Empire.",
    "subheadline": "After 18 years, Adobe's Indian-origin CEO is stepping aside as the company searches for an AI-era successor. His Q2 earnings on June 11 will test whether Firefly can reverse the stock's slide.",
    "slug": make_slug("shantanu-narayen-adobe-ceo-stepping-down-firefly-successor"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Narayen — from Hyderabad to running the world's largest creative software company — is departing after an 18-year tenure that redefined enterprise software. His exit leaves a gap in the Indian-origin CEO constellation alongside Pichai, Nadella, and Krishna. The successor choice will signal whether Silicon Valley's most powerful network keeps its grip on the creative economy.",
    "tags": ["adobe", "shantanu-narayen", "indian-ceo", "firefly-ai", "silicon-valley", "leadership"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "TechSpot", "url": "https://www.techspot.com/news/107236-adobe-ceo-step-down-after-18-years-investors.html"},
        {"name": "Storyboard18", "url": "https://www.storyboard18.com/brand-marketing/adobe-ceo-shantanu-narayen-to-step-down-after-nearly-two-decades-58430.htm"},
        {"name": "Barchart", "url": "https://www.barchart.com/story/news/32836479/dear-adobe-stock-fans-mark-your-calendars-for-june-11"},
        {"name": "The Register", "url": "https://www.theregister.com/2026/03/13/adobe_ceo_shantanu_narayen_to/"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/0/01/Shantanu_Narayen_-_the_CEO_of_Adobe_Inc.jpg",
    "image_caption": "Shantanu Narayen, chairman and CEO of Adobe Inc.",
    "image_attribution": "Wikimedia Commons",
    "body": article1_body
}


# ─────────────────────────────────────────────
# ARTICLE 2: Nikesh Arora / Palo Alto Networks
# ─────────────────────────────────────────────

article2_body = """Six months ago, the consensus on Wall Street was that artificial intelligence would gut the cybersecurity industry. Nikesh Arora just put that thesis in the ground.

Palo Alto Networks reported fiscal Q3 2026 revenue of $3 billion, up 31% year-over-year and comfortably ahead of the $2.94 billion analysts had expected. Adjusted earnings per share hit $0.85, beating the $0.80 consensus. The stock has nearly doubled since April, and the company's market capitalisation crossed the $200 billion threshold for the first time in May.

"We officially declare the SaaS-Pocalypse for cybersecurity dead," Arora said on the earnings call — a pointed rebuttal to months of analyst hand-wringing about whether AI-native startups would render legacy security vendors obsolete.

## AI Is Creating More Work, Not Less

The irony is rich. The same frontier AI models that were supposed to kill cybersecurity are now its biggest growth engine. Anthropic's Claude Mythos — a model so powerful the company initially declined to release it — has triggered a scramble among enterprises to reassess their security posture.

More than 1,000 companies have contacted Palo Alto in the past two months alone, Arora said, "to talk about their cyber posture, cyber infrastructure, and how we can help them get through this period of living the future with frontier AI models being cyber-capable."

Next-Generation Security annual recurring revenue jumped 60% to exceed $8 billion. Remaining performance obligations — essentially the company's backlog — grew 36% to $18.4 billion, giving it the kind of forward revenue visibility that most software companies can only envy.

## Project Glasswing: Turning AI Against Itself

Palo Alto is not just selling protection against AI threats. It is using AI to find its own vulnerabilities. Under a collaboration called Project Glasswing, the company deployed Anthropic's Mythos model to scan its own products — a move that uncovered 26 previously unknown security flaws in a single "Patch Wednesday" cycle, far exceeding its typical monthly disclosures.

The company's "platformisation" strategy — persuading customers to consolidate fragmented security tools into a single Palo Alto platform — is also accelerating, with more than 110 platformisations completed during the quarter. Customers who platformise spend more and have higher retention rates, Arora said.

On a GAAP basis, the quarter was messier. The company reported a net loss of $177 million, compared to a $262 million profit a year ago, dragged down by acquisition-related costs from the $25 billion CyberArk deal that closed in February. But investors are clearly looking through the noise: the stock gained 65% in May alone.

## From Lucknow to the $200 Billion Club

Arora, who grew up in Lucknow and studied at the Indian Institute of Technology Varanasi (BHU) before joining Boston Consulting Group, has had one of the most unorthodox career paths in tech. He spent a decade at Google rising to chief business officer, then a brief, controversial stint as SoftBank's president and COO under Masayoshi Son.

When he took over Palo Alto Networks in 2018, the company's market cap was under $20 billion. Today it is worth eleven times that. For Indian-origin professionals working in cybersecurity — one of the fastest-growing specialisations for H-1B holders — Arora's ascent from IIT Varanasi to the helm of a $200 billion company is both a roadmap and a reminder of what is at stake as AI reshapes every corner of enterprise technology."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "Nikesh Arora Just Declared Cybersecurity's AI Apocalypse Dead. His $200 Billion Company Proves It.",
    "subheadline": "Palo Alto Networks beat every metric, the stock nearly doubled since April, and 1,000 companies called in two months. The Indian-origin CEO says frontier AI is cybersecurity's biggest tailwind, not its death sentence.",
    "slug": make_slug("nikesh-arora-palo-alto-networks-cybersecurity-ai-boom"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Nikesh Arora — IIT BHU to the helm of a $200B cybersecurity giant — just delivered one of the strongest earnings reports in enterprise software. For Indian tech workers anxious about AI replacing their jobs, Palo Alto's results prove that AI creates more work for cybersecurity professionals, not less. The company's stock has nearly doubled, making Arora one of the most valuable Indian-origin CEOs in America.",
    "tags": ["palo-alto-networks", "nikesh-arora", "cybersecurity", "ai", "indian-ceo", "earnings"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Wall Street Journal", "url": "https://www.wsj.com/business/earnings/palo-alto-networks-revenue-rises-as-customers-beef-up-cyber-defenses-e6c614bc"},
        {"name": "MarketWatch", "url": "https://www.marketwatch.com/story/palo-alto-networks-earnings-show-ai-brings-new-urgency-to-cybersecurity-but-stock-still-dips-c104c8eb"},
        {"name": "Barron's", "url": "https://www.barrons.com/articles/palo-alto-networks-stock-price-earnings-ai-e4ef05b0"},
        {"name": "AInvest", "url": "https://www.ainvest.com/news/palo-alto-networks-ai-driven-security-testing-a-potential-game-changer-for-cybersecurity-vendors-2606081615/"}
    ]),
    "score_total": 85,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/e/ea/Nikesh_Arora_TechCrunch_Disrupt_2015.jpg",
    "image_caption": "Nikesh Arora, chairman and CEO of Palo Alto Networks",
    "image_attribution": "Wikimedia Commons",
    "body": article2_body
}


# ─────────────────────────────────────────────
# ARTICLE 3: India's Deep-Tech Showcase in France
# ─────────────────────────────────────────────

article3_body = """India is sending 120 deep-tech ventures to Nice, France, next week. This is not a trade mission. It is a statement of intent.

Bharat Innovates 2026, running from June 14 to 16 as part of the India-France Year of Innovation, will showcase research-backed startups across 13 frontier sectors — from space and semiconductors to advanced computing, defence, and Industry 4.0. The initiative, led by the Ministry of Education, is designed to place Indian deep tech before global investors and strategic partners at a moment when the country's ambitions have moved well past software services.

## Space: From Government Monopoly to Private Rocket Engines

Among the companies being highlighted is Agnikul Cosmos, the IIT Madras-incubated startup that built the world's first single-piece 3D-printed semi-cryogenic rocket engine. Its Agnibaan vehicle, capable of delivering 30 to 300 kilogrammes to low earth orbit, launched from India's first private launchpad at Sriharikota — a facility that would have been unthinkable a decade ago.

Agnikul is not alone. Skyroot Aerospace, headquartered in Hyderabad, is preparing for its first orbital launch using the Vikram-I rocket and recently signed a memorandum of understanding with Axiom Space to explore logistics corridors between commercial space stations and Indian launch capability. Pixxel, another Bengaluru startup, is building hyperspectral earth observation satellites. And the Indian Space Research Organisation is gearing up for Gaganyaan G-1, the uncrewed test flight of India's first human-rated spacecraft, with a humanoid robot named Vyommitra on board.

The reforms under IN-SPACe, India's space regulator, have unlocked private participation that is beginning to resemble the early SpaceX era in the United States. The difference: India's startups are building on indigenous technology, not importing it.

## The Institutional Engine Behind the Startups

What makes Bharat Innovates significant is not just the companies but the institutional infrastructure producing them. IIT Madras climbed 47 places to 180 in the QS World University Rankings 2026, while IIT Delhi reached its best-ever 123rd position. India now ranks fourth globally by institutions represented in the rankings, and is the fastest-growing higher education system in the G20 over the past decade.

The Foundation for Innovation and Technology Transfer at IIT Delhi has been building structured pathways connecting research, startups, policy, and global markets. The India AI Summit held earlier this year at MIT Media Lab in Boston, co-organised with FITT, signalled a maturing innovation diplomacy that pairs academic excellence with commercial ambition.

## From BharatGen to Sovereign Silicon

The showcase arrives at a particularly charged moment for India's tech sovereignty narrative. The government launched three sovereign AI models earlier this year — from Sarvam AI, Gnani.ai, and the IIT Bombay-led BharatGen consortium — under the ₹10,000 crore IndiaAI Mission. BharatGen's stack includes Param-2, a 17-billion-parameter multilingual foundation model trained across 22 Indian languages; Shrutam, a speech-to-text engine in 12 languages; and DocBodh, a multilingual document understanding framework.

On the hardware side, Tata Electronics is building India's first commercial semiconductor fab in three decades at Dholera, Gujarat, with technology transfer from Taiwan's PSMC. The $11 billion project, with 50% central government subsidies, aims for 50,000 wafers per month by late 2027.

## The NRI Investment Angle

For Indian diaspora professionals and investors, the Bharat Innovates showcase represents something that has been missing from India's tech story for decades: foundational technology, not just services built on someone else's platform. India's space startups are designing their own engines. Its AI labs are training their own models. Its semiconductor mission is fabricating its own chips.

The question is no longer whether India can build deep tech. It is whether the capital, talent, and strategic patience will hold long enough for these ventures to compete globally. Nice is where 120 of them will make their case."""

article3 = {
    "id": str(uuid.uuid4()),
    "headline": "India Is Sending 120 Deep-Tech Startups to France. This Is Not a Trade Mission.",
    "subheadline": "Bharat Innovates 2026 will showcase 3D-printed rocket engines, sovereign AI models, and semiconductor ambitions to global investors. For once, India's tech story is not about services.",
    "slug": make_slug("india-bharat-innovates-deep-tech-france-space-ai-semiconductor"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "India's deep-tech ecosystem has matured beyond IT services. Bharat Innovates showcases space startups building indigenous rocket engines, sovereign AI models trained on 22 Indian languages, and a $11 billion semiconductor fab. For NRI investors and diaspora professionals, this is the moment to reassess India's technology capabilities — the country is building foundational tech, not just outsourcing it.",
    "tags": ["india-deep-tech", "bharat-innovates", "agnikul-cosmos", "space-tech", "semiconductor", "sovereign-ai", "isro"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "YourStory", "url": "https://yourstory.com/2026/06/bharat-innovates-2026-iit-madras-agnikul-cosmos-3d-rocket"},
        {"name": "EE Times", "url": "https://www.eetimes.com/india-ai-summit-from-it-services-to-sovereign-ai-and-silicon/"},
        {"name": "BizzBuzz", "url": "https://www.bizzbuzz.news/technology/india-launches-three-sovereign-ai-models-sundar-pichai-lauds-local-innovation-1373969"},
        {"name": "Digitimes", "url": "https://www.digitimes.com/news/a20240911PD219/tata-electronics-semiconductors-partnership-india.html"}
    ]),
    "score_total": 75,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a3/TVD1_launch_03.jpg/1280px-TVD1_launch_03.jpg",
    "image_caption": "An ISRO test vehicle lifts off from Sriharikota, India's primary spaceport",
    "image_attribution": "Wikimedia Commons",
    "body": article3_body
}


# ─────────────────────────────────────────────
# INSERT ALL ARTICLES
# ─────────────────────────────────────────────

articles = [article1, article2, article3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

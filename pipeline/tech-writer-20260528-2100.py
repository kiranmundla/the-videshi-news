#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-05-28 21:00 UTC run"""
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

# Verify images return 200
def verify_image(url):
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                          headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            return url
        # Try GET if HEAD fails
        r = requests.get(url, timeout=10, stream=True, allow_redirects=True,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct:
            return url
    except Exception as e:
        print(f"  ⚠️ Image verify failed for {url}: {e}")
    return None

articles = [
    # ── Article 1: IBM Quantum ──
    {
        "id": str(uuid.uuid4()),
        "headline": "Arvind Krishna's IBM Is Betting $10 Billion That Quantum Computing's Moment Has Arrived",
        "subheadline": "The Indian-born CEO is staking a decade of credibility on building the world's first fault-tolerant quantum computer by 2029 — with a billion-dollar chip factory to match.",
        "slug": make_slug("arvind-krishna-ibm-10-billion-quantum-computing"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Arvind Krishna joins the rarefied club of Indian-origin CEOs making trillion-dollar technology bets. For Indian quantum researchers and IIT graduates eyeing the field, IBM's commitment signals a new wave of hiring and R&D investment.",
        "tags": ["quantum-computing", "ibm", "arvind-krishna", "indian-ceo", "chips"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/ibm-plans-10-billion-investment-large-scale-quantum-computer-by-2029-2026-05-28/"},
            {"name": "Barron's", "url": "https://www.barrons.com/articles/ibm-quantum-computing-investment"},
            {"name": "WinBuzzer", "url": "https://winbuzzer.com/2026/05/28/ibms-new-roadmap-targets-quantum-computing-by-2029/"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/3/30/Arvind_Krishna_in_2025_%28cropped%29.jpg",
        "image_caption": "Arvind Krishna, CEO of IBM, is leading a $10 billion quantum computing push.",
        "body": """When Sanjay Mehrotra took Micron past the trillion-dollar mark last week, the narrative was familiar: another Indian-born engineer ascending to the summit of American capitalism. Arvind Krishna's play is different. The IBM chief executive is not riding a market wave — he is trying to create one.

On Thursday, IBM disclosed plans to invest more than $10 billion in quantum computing over five years, the largest single commitment any company has made to the technology. The goal: build the world's first large-scale, fault-tolerant quantum computer by 2029, a machine capable of running complex calculations reliably and without the crippling error rates that have plagued the field for decades.

## The Starling Gamble

IBM calls the target system Starling. It will use 200 logical qubits and perform 20,000 times more operations than any quantum computer in existence today. A successor, Blue Jay, would scale to 2,000 logical qubits by 2033. The technical linchpin is a breakthrough in quantum error correction — a new code called qLDPC that IBM says reduces the number of physical qubits needed by 90 percent.

That matters because the fundamental challenge of quantum computing has never been raw qubit counts but making those qubits reliable enough to do useful work. IBM has deployed more than 90 quantum systems to date — more than all other industry players combined — but none has yet delivered the kind of computational advantage that would justify the hype cycle the industry has endured.

## Washington's Bet

Krishna's timing is no accident. The announcement followed a Trump administration decision to take $2 billion in equity stakes across nine quantum computing companies. IBM is set to receive half that funding for a new venture called Anderon — the first dedicated quantum chip manufacturing facility in the United States. IBM is contributing $1 billion of its own to Anderon, which will also offer chipmaking technology to outside customers.

The White House's motivation is straightforward: China. Beijing has poured billions into quantum research, and the fear in Washington is that whoever achieves quantum advantage first gains the ability to break conventional encryption, model new materials, and simulate molecular interactions at speeds classical computers cannot touch. For the administration, this is the new front in the technology cold war, and Krishna is the general it has chosen.

## What NRIs Should Watch

For the Indian diaspora, the story operates on multiple levels. Krishna, who grew up in Andhra Pradesh and earned his PhD at the University of Illinois, is now the Indian-origin CEO making arguably the most consequential technology bet of the decade. His peers — Pichai at Alphabet, Nadella at Microsoft, Mehrotra at Micron — are competing in markets that already exist. Krishna is trying to will a market into being.

The $10 billion commitment will also mean significant hiring. IBM already employs thousands of researchers in India through its labs in Bangalore and Delhi. Quantum computing requires expertise in condensed matter physics, cryogenics, error correction algorithms, and quantum software — fields where IITs and IISc have quietly built strong research programs. IBM's quantum network already includes the Indian Institute of Science, and the investment could accelerate the pipeline of Indian researchers into the global quantum workforce.

For NRI investors, the calculation is more nuanced. IBM shares rose 1.7 percent on the news, a muted reaction for a $10 billion commitment. The market is hedging because quantum computing has been "five to ten years away" for the past twenty years. Over 325 Fortune 500 companies use IBM's quantum systems today, but mostly for research and exploration, not production workloads. The revenue inflection point — when companies start paying serious money for quantum advantage — remains speculative.

## The Competitive Landscape

Krishna is not operating in a vacuum. Google's Sycamore chip achieved quantum supremacy in 2019, though the result was narrow and contested. Microsoft recently announced its own quantum breakthroughs using topological qubits. Amazon is building quantum hardware through its Center for Quantum Computing. Each is pursuing a different technical approach, and there is no consensus on which will win.

IBM's advantage is scale and persistence. It has been in the quantum game since the 1990s and has the manufacturing infrastructure to produce quantum chips at volumes no startup can match. Anderon gives it a dedicated fab — a factory specifically designed for quantum processors, not repurposed from classical chip production.

Whether $10 billion is enough to cross the finish line is the trillion-dollar question. But for Arvind Krishna, the son of Andhra Pradesh who now commands one of America's oldest technology companies, the bet is existential. If Starling works, IBM's relevance in the AI era is secured. If it doesn't, the company will have spent a decade and a fortune chasing a mirage.

Krishna, characteristically, is not hedging. "We have a realistic path," IBM's roadmap states. In quantum computing, that passes for bravado."""
    },

    # ── Article 2: OpenAI AI Phone ──
    {
        "id": str(uuid.uuid4()),
        "headline": "OpenAI Is Building an AI Phone. Every App Developer in Bangalore Should Be Paying Attention.",
        "subheadline": "The ChatGPT maker is partnering with Qualcomm and MediaTek to build an AI-native smartphone by 2028 — one that replaces apps with agents and could upend the mobile economy India helped build.",
        "slug": make_slug("openai-ai-phone-qualcomm-mediatek-india-developers"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Qualcomm employs over 15,000 engineers in Hyderabad who may work on the AI phone's silicon. Meanwhile, India's massive app development workforce faces an existential question: if AI agents replace apps, what happens to the millions of developers who build them?",
        "tags": ["openai", "qualcomm", "mediatek", "ai-phone", "indian-developers", "smartphone"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/world/china/bytedance-developing-custom-cpu-chips-support-ai-rollout-sources-say-2026-05-28/"},
            {"name": "GSMArena", "url": "https://www.gsmarena.com/kuo_openai_smartphone_custom_chipset-news-66311.php"},
            {"name": "TechnoSports", "url": "https://technosports.co.in/qualcomm-openai-ai-smartphones-by-2028/"},
            {"name": "BitRss", "url": "https://bitrss.com/news/834512/qualcomm-qcom-shares-soar-11-as-openai-smartphone-chip-partnership-emerges"}
        ]),
        "score_total": 80,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/8294749/pexels-photo-8294749.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
        "image_caption": "OpenAI's planned AI-native smartphone aims to replace traditional apps with AI agents.",
        "body": """Sam Altman has been telegraphing this move for years. Now the details are concrete: OpenAI is working with Qualcomm and MediaTek to develop custom chipsets for an AI-native smartphone, with mass production targeted for 2028. Luxshare, the Chinese contract manufacturer, is the sole system co-design partner. Final specifications are expected by late 2026 or early 2027.

The device will not be another Android phone with a chatbot bolted on. According to analyst Ming-Chi Kuo, the phone will use AI agents instead of traditional apps — a "task stream" interface where users describe what they want and the phone's on-device and cloud-based models figure out how to deliver it. No app stores. No download buttons. Just agents that negotiate with services on the user's behalf.

Qualcomm's stock surged 11 percent on the news. But the more consequential reaction is happening 8,000 miles away.

## Hyderabad's Stake in the Game

Qualcomm's largest engineering centre outside the United States sits in Hyderabad, where more than 15,000 engineers design the Snapdragon processors that power most of the world's Android phones. MediaTek, the Taiwanese chipmaker that is Qualcomm's primary rival in mobile silicon, also maintains a growing India design team. Between them, thousands of Indian chip designers will likely contribute to the AI phone's custom silicon.

That is the good news for India's semiconductor talent. The bad news is what the phone's design philosophy implies for everyone else.

## The App Economy's Existential Moment

India has roughly 27 million software developers, according to recent GitHub data — the largest developer population outside the United States, and growing faster than anywhere else. A significant fraction of that workforce builds mobile applications. The app economy — from ride-hailing to food delivery to fintech — is the economic engine that transformed Bangalore from a mid-tier city into a global technology hub.

OpenAI's vision attacks the app economy at its foundation. If AI agents can book flights, order food, manage finances, and navigate bureaucracy without dedicated apps, the economic model that sustains millions of Indian developers is in question. Not immediately — the 2028 timeline and the $999 price point suggest an early-adopter product, not a mass-market disruption. But the direction is clear.

The pattern is familiar to anyone who watched the smartphone revolution itself. When the iPhone launched in 2007, it did not immediately kill Nokia. It took years. But the companies that understood what was happening early — and repositioned — survived. The ones that didn't are case studies in business school textbooks.

## India's Two-Sided Problem

For Indian consumers, the AI phone poses a different question. India is the world's second-largest smartphone market by volume, but the average selling price hovers around $200 — roughly a fifth of the projected $999 for OpenAI's device. If AI-native phones remain premium products, India risks being on the wrong side of a new digital divide: a world where wealthy users interact with AI agents while everyone else taps icons on glass.

The counter-argument is that AI phone capabilities will eventually trickle down, just as smartphone features did. Qualcomm already sells AI-capable Snapdragon chips across price tiers, and MediaTek's entire business model is built on bringing flagship features to mid-range devices. The question is how fast.

## What the Diaspora Should Watch

For NRIs working at Qualcomm, MediaTek, or the dozens of chip design firms in Hyderabad and Bangalore, the OpenAI partnership represents a career-defining project. Building silicon for an AI-first operating system requires fundamentally different design priorities — more on-device inference capability, lower latency, tighter integration between neural processing units and traditional CPU cores. These are the engineers who will shape how the next generation of computing feels.

For NRI investors, the Qualcomm stock surge is a signal but not a verdict. OpenAI has never manufactured hardware at scale. Its previous device ventures — including an ill-defined collaboration with Jony Ive — have produced more rumours than products. The 2028 timeline is ambitious for a company that currently makes software.

And for Indian startup founders building the next generation of apps, the message is more urgent: start thinking about agents. The companies that learn to build AI-native services — not just mobile apps with ChatGPT integrations — will define the next platform era. The ones that don't will join the long list of businesses that bet their futures on a platform that moved on without them.

OpenAI's phone may never ship. But the idea it represents — that apps are a transitional technology between websites and agents — is already reshaping how the smartest money in Silicon Valley thinks about software. Bangalore cannot afford to ignore that shift."""
    },

    # ── Article 3: Airlines racing to India tech hubs ──
    {
        "id": str(uuid.uuid4()),
        "headline": "American Airlines and Southwest Are Racing to Double Their India Tech Teams. They're Not Alone.",
        "subheadline": "Airlines, retailers, and truck makers are all expanding India technology hubs — a signal that the GCC boom is spreading far beyond banking and Big Tech.",
        "slug": make_slug("american-airlines-southwest-india-gcc-tech-hubs"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "The expansion of GCCs beyond tech and finance into airlines, retail, and manufacturing creates new career pathways for Indian engineers — and a counter-narrative to the AI job-loss fears dominating headlines.",
        "tags": ["gcc", "american-airlines", "southwest-airlines", "india-tech", "careers", "outsourcing"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/business/aerospace-defense/american-airlines-plans-double-india-tech-hub-staff-sources-say-2026-05-28/"},
            {"name": "Reuters", "url": "https://www.reuters.com/technology/global-firms-bring-more-work-in-house-india-hubs-ai-boost-2026-05-28/"},
            {"name": "Nasscom-Zinnov Report 2026", "url": "https://nasscom.in/gcc-report-2026"}
        ]),
        "score_total": 72,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/35461987/pexels-photo-35461987.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
        "image_caption": "Airlines are joining the rush to build technology capability centres in India.",
        "body": """American Airlines plans to double the headcount at its India technology hub to about 800 employees by early next year. Southwest Airlines announced last week that it will expand its Hyderabad global capability centre to roughly 1,000 employees over the next few years. These are not the names you expect to see competing for engineering talent in Bangalore and Hyderabad. That is precisely the point.

The global capability centre boom — India's quiet transformation from back-office outsourcing destination to integrated technology hub — has traditionally been a story about banks and technology companies. JPMorgan Chase, Goldman Sachs, Google, Microsoft: these are the names that fill the glossy reports from Nasscom. But the latest wave of GCC expansion is being driven by companies that, until recently, would have seemed unlikely candidates for India engineering teams.

## Beyond Banking and Big Tech

India now hosts more than 2,100 global capability centres employing 2.36 million people and generating nearly $100 billion in annual revenue, according to a 2026 Nasscom-Zinnov report. The workforce remains the country's greatest strength, but the character of the work is changing.

At the Reuters India Summit in Bangalore this week, executives from Kimberly-Clark, Target, and Daimler Truck described how their India hubs have moved beyond routine tasks to own core functions — engineering, product development, analytics, and increasingly, AI-driven innovation. Target operates its Bangalore centre as an "integrated headquarters" aligned with global strategy, not as a cost-saving satellite office.

American Airlines' decision to double its India team reflects the same logic. The airline is not offshoring call centre work. It is building a technology hub that handles core operational systems — the kind of work that, a decade ago, would have been done exclusively at its Fort Worth headquarters.

## AI Is Accelerating the Shift

The twist is that artificial intelligence, widely feared as a threat to Indian jobs, is actually accelerating GCC expansion. Executives at the Reuters summit described how AI is helping their India teams produce more work per person — a productivity gain that makes it economical to bring work in-house rather than contracting it to outsourcing firms like TCS, Infosys, or Wipro.

"The number of IPs, the patents and the trade secrets created by GCCs in India is already increasing," said Radhakrishnan Kodakkal, head of Daimler Truck Innovation Center India. "AI would accelerate it."

This is the underappreciated side of the AI story. While headlines focus on the jobs AI will destroy, GCCs are using the technology to justify expanding their India operations — taking work that was previously scattered across outsourcing vendors and consolidating it under one roof, with fewer but higher-skilled workers.

## The Outsourcing Squeeze

For India's traditional IT services firms, this is an uncomfortable development. If multinationals can use AI to make their in-house India teams more productive, the economic case for large outsourcing contracts weakens. The data supports the trend: companies at the summit spoke about hiring for AI specialists, data scientists, and product engineers rather than the large-batch application maintenance teams that were the bread and butter of Indian outsourcing.

TeamLease Services' chief strategy officer noted that firms are being advised to keep 20 to 30 percent of their workforce on outsourced or variable models — a hedge against uncertainty, but also a signal that the era of massive, multi-year outsourcing contracts may be winding down.

TCS has already shed roughly 25,000 employees in the first three quarters of fiscal 2026. Infosys is trying to pivot toward AI-driven consulting. The question is whether India's IT services giants can reinvent themselves fast enough to avoid being squeezed between their own clients' GCCs on one side and hyperscaler AI platforms on the other.

## What This Means for NRIs

For Indian Americans working in technology, the GCC expansion creates an interesting career arbitrage. Senior engineers and product managers with US experience are increasingly sought by GCCs that want to replicate Silicon Valley workflows. Some NRIs are taking the reverse path — returning to India for leadership roles at GCCs that offer competitive compensation by local standards and the chance to build something from scratch.

The American Airlines and Southwest expansions also signal that India's GCC story has legs beyond the current AI hype cycle. Airlines are not investing in India tech hubs because of a passing trend. They are doing it because the economics of maintaining aging internal systems in the US — with Fort Worth and Dallas salaries — no longer make sense when they can build capable teams in Hyderabad at a fraction of the cost.

The irony is thick. India spent decades as the world's back office. Now it is becoming something closer to the world's second headquarters — a place where core technology decisions are made, not just executed. For the 2.36 million people working in GCCs, and the millions more who aspire to, the message is clear: the work is getting harder, the pay is getting better, and the outsourcing model your parents' generation built is being replaced by something more ambitious.

Whether that ambition will survive the next AI disruption cycle is another question entirely. But for now, American Airlines is hiring in Hyderabad, and that says more about India's technological trajectory than any Nasscom slide deck ever could."""
    },
]

# Verify images and publish
for art in articles:
    img = verify_image(art["image_url"])
    if img:
        print(f"✅ Image OK: {art['slug']}")
    else:
        print(f"⚠️ Image failed, keeping URL anyway: {art['slug']}")
    try:
        sb_post("p2_articles", art)
        print(f"✅ Published: {art['slug']} — {art['headline']}")
    except Exception as e:
        print(f"❌ Failed: {art['slug']}: {e}")

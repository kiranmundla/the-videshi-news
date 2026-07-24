#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-06-30 14:00 PDT run. Inserts 3 articles."""

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


now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def make_slug(base):
    slug = base.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug.strip())
    return slug[:70].rstrip("-") + "-20260630"


articles = [
    # ─── ARTICLE 1: Adobe CEO Succession ────────────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "Narayen Is Leaving Adobe. Both Candidates to Replace Him Are Also Indian.",
        "subheadline": "After 18 years, Adobe's Hyderabad-born CEO is stepping down — and the two frontrunners to succeed him, David Wadhwani and Anil Chakravarthy, are also of Indian origin. The diaspora's grip on American enterprise software is tightening.",
        "slug": make_slug("adobe-narayen-wadhwani-chakravarthy-ceo-succession-indian"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Indian-origin executives dominate Adobe's C-suite — outgoing CEO Narayen and both leading successors are of Indian descent, extending the diaspora's leadership pipeline in enterprise software alongside Nadella at Microsoft and Pichai at Google.",
        "tags": ["adobe", "shantanu-narayen", "indian-ceo", "enterprise-software", "ai"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Morningstar / MarketWatch", "url": "https://www.morningstar.com/news/marketwatch/20260609446/adobe-needs-a-new-ceo-to-make-bold-ai-moves-and-its-choice-could-be-revealed-on-thursday"},
            {"name": "TheStreet", "url": "https://www.thestreet.com/technology/adobes-outgoing-ceo-makes-big-bet-on-the-future"},
            {"name": "Bloomberg Law", "url": "https://news.bloomberglaw.com/tech-and-telecom-law/adobe-eyes-two-internal-leaders-ai-outsiders-for-ceo-role"},
            {"name": "Reuters", "url": "https://www.reuters.com/technology/adobe-announces-ceo-transition-2026-03-12/"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/0/01/Shantanu_Narayen_-_the_CEO_of_Adobe_Inc.jpg",
        "image_caption": "Shantanu Narayen, Adobe's outgoing CEO, who has led the company for 18 years",
        "image_attribution": "Wikimedia Commons",
        "body": """For 18 years, Shantanu Narayen has been the only chief executive Adobe has known in its modern era. Born in Hyderabad, educated at Osmania University and the University of California at Berkeley, he joined the San Jose company in 1998 and took the corner office in 2007. Under his watch, Adobe abandoned shrink-wrapped software for the cloud, grew its valuation tenfold, and made Photoshop, Illustrator, and Premiere Pro as essential to creative professionals as electricity.

Now he is leaving. And the race to replace him looks remarkably like the one that produced him.

## The Two Frontrunners

According to Bloomberg, the board has shortlisted two internal candidates. Both are of Indian origin. David Wadhwani, president of Adobe's creativity and productivity unit — the division that houses Photoshop, Lightroom, and the Firefly generative AI suite — is widely considered the heir apparent. Before Adobe, Wadhwani ran AppDynamics, which he sold to Cisco for $3.7 billion. The other contender is Anil Chakravarthy, president of customer experience orchestration, who previously served as CEO of Informatica.

Adobe has also retained Heidrick & Struggles to screen external candidates, particularly leaders with deep AI experience. Names from Google and OpenAI have been floated. But Piper Sandler analyst Billy Fitzsimmons told MarketWatch that the appointment is "largely expected" to come from within.

If either Wadhwani or Chakravarthy gets the nod, Adobe will have had two consecutive Indian-origin CEOs — joining the pattern set by Satya Nadella at Microsoft, Sundar Pichai at Alphabet, Arvind Krishna at IBM, and Nikesh Arora at Palo Alto Networks. For the Indian diaspora in Silicon Valley, this is no longer a feel-good anecdote. It is an established career ladder.

## Narayen's Parting Gambit

The outgoing CEO is not leaving quietly. On Adobe's Q2 FY2026 earnings call on June 11, Narayen unveiled a strategy that shook Wall Street: he is giving software away for free.

Adobe is redirecting web traffic away from paid sign-up flows and into free, no-paywall experiences across Acrobat, Express, and Firefly. Planned price increases for Creative Cloud have been deferred. The logic, Narayen argued, echoes Adobe's most consequential decision — making Acrobat Reader free in the 1990s, which created one of the most durable distribution networks in software history.

"This will give us singular clarity," Narayen told analysts, describing the bet as deliberate.

The numbers suggest the clarity is working, at least on reach. Acrobat and Express monthly active users surpassed 850 million, growing roughly 20 per cent year-over-year. Creative freemium users — the cohort using Firefly, Premiere Pro, Photoshop, and Lightroom without paying — grew from 50 million to 90 million in the same period.

## The Problem the Next CEO Inherits

Investors are less enthused. Adobe's stock has fallen more than 30 per cent this year, dragging its market capitalisation to roughly $81 billion. The company trades at about $205 a share, down from nearly $393 at its 52-week high.

The pressure is not just cyclical. OpenAI, Anthropic, and a proliferating class of AI-native design tools are eroding the moat Adobe spent two decades building. Canva, once dismissed as a consumer toy, now serves enterprises. Generative AI has made professional-grade image and video creation accessible to people who have never opened Photoshop. The failed $20 billion Figma acquisition in 2023 — blocked by regulators — left a hole in Adobe's collaborative design strategy that still has not been filled.

This is the company the next CEO inherits: massive distribution, slowing revenue growth, a stock market in revolt, and an AI transition that could either reinforce Adobe's dominance or render it irrelevant.

## What NRIs Should Watch

For Indian Americans in the technology industry, the Adobe succession is more than a boardroom shuffle. It is a test of whether the Indian-origin leadership model — typically characterised by operational rigour, consensus-building, and long institutional tenure — can survive an era that rewards speed, risk-taking, and willingness to cannibalise existing products.

Narayen's free-software gambit suggests he understands the moment. Whether his successor does too will determine whether Adobe remains the creative backbone of the internet, or becomes the next cautionary tale of a monopoly that moved too slowly."""
    },

    # ─── ARTICLE 2: AWS Forward-Deployed AI Engineers ─────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "Amazon Is Spending $1 Billion to Embed AI Engineers Inside Your Company. The Talent Pool Is Heavily Indian.",
        "subheadline": "AWS's new forward-deployed engineering unit will send pods of AI specialists directly to enterprise clients. With Amazon cutting 30,000 corporate jobs while hiring thousands for this initiative, the shift has implications for Indian tech workers on both sides.",
        "slug": make_slug("aws-1-billion-forward-deployed-ai-engineers-india"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Amazon's massive Indian workforce — both in the US on H-1B visas and in India — makes the diaspora the largest talent pool for this new high-demand role. The initiative also signals which AI jobs are safe from automation and which are not.",
        "tags": ["amazon", "aws", "ai-engineering", "h1b", "enterprise-ai", "forward-deployed"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/amazons-aws-commits-1-billion-toward-new-unit-embedded-ai-engineers-2026-06-30/"},
            {"name": "LinkedIn (Box CEO Aaron Levie)", "url": "https://www.linkedin.com/in/levie/"}
        ]),
        "score_total": 75,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/4508751/pexels-photo-4508751.jpeg",
        "image_caption": "Server racks inside a modern cloud data center",
        "image_attribution": "Pexels",
        "body": """Amazon Web Services on Tuesday announced it is creating a new division dedicated to what Silicon Valley calls "forward-deployed engineers" — AI specialists who embed directly with enterprise clients for 45-day stints to help them adopt artificial intelligence. The initial commitment: $1 billion.

The concept is not new. Palantir Technologies has operated a forward-deployed engineering model for over a decade, and Salesforce, Anthropic, and Google Cloud run their own versions. What is new is the scale. AWS plans to employ "thousands" in the unit, hiring externally and redeploying internal staff to fill the roles.

"We have a ton of demand for customers who are asking for our help to really drive agentic AI patterns in their workflows," Francessca Vasquez, AWS vice president of frontier AI engineering and services, told Reuters.

## The Hottest Job in Tech

Forward-deployed engineers are a hybrid species: part consultant, part developer, part diplomat. They parachute into a client's organisation, navigate its internal politics, understand its data, and write production-grade code that makes AI models deliver real results — not just impressive demos.

Box CEO Aaron Levie called the role "about to become one of the most in-demand jobs in tech" in a LinkedIn post in May. The numbers bear him out. Demand for forward-deployed engineers and similar positions grew 42-fold between 2023 and 2025, according to a LinkedIn workforce report.

The appeal is straightforward. Enterprises have spent billions on AI licences but struggle to extract value. McKinsey estimated last year that fewer than 15 per cent of enterprise AI projects reach production. Forward-deployed engineers exist to close that gap — and companies are willing to pay dearly for the service.

## Where India Fits

Amazon employs tens of thousands of Indian-origin engineers, both in the United States and at its sprawling campuses in Hyderabad, Bangalore, and Chennai. Indians are the single largest demographic in Amazon's US technical workforce on H-1B visas, and the company's India operations house some of its most sophisticated AI and machine learning teams.

This talent base makes the diaspora the natural recruiting ground for the new unit. Forward-deployed engineering demands deep technical skill, strong communication, and the ability to operate in unfamiliar corporate environments — precisely the profile that has propelled Indian engineers to leadership positions across American technology companies.

But there is an uncomfortable subtext. Amazon announced the new unit even as it has cut more than 30,000 corporate jobs since October. The message embedded in the arithmetic is clear: the company is not hiring fewer people. It is hiring different people. The jobs being eliminated are the ones AI is replacing — routine coding, testing, project management. The jobs being created are the ones that make AI work inside organisations that cannot figure it out alone.

For Indian tech workers in the United States, this creates a fork in the road. Those with the skills to embed with clients, diagnose problems, and ship working AI systems are entering one of the strongest job markets in a decade. Those whose work consists primarily of writing boilerplate code or managing Jira boards are watching their roles shrink.

## The Broader Shift

AWS's move reflects a pattern playing out across cloud computing. Microsoft has deployed thousands of its own AI specialists through its Customer Success organisation. Google Cloud has expanded its AI consulting arm. Accenture, the world's largest IT services company, has hired more than 60,000 people specifically to deploy AI at enterprise clients.

For Indian IT services companies — TCS, Infosys, Wipro, HCL Tech — the forward-deployed model is both a threat and an opportunity. A threat because it positions hyperscalers as direct competitors for the implementation work that has been the bread and butter of Indian outsourcing for two decades. An opportunity because these firms employ some of the largest pools of AI-trained engineers in the world and can offer forward-deployed services at a fraction of AWS's cost.

The initial customers for AWS's unit include the National Basketball Association and Ricoh, the Japanese electronics company. Success, Vasquez said, will be measured by how quickly clients develop new products or skills — not by how many hours the engineers log.

It is a model built for speed. For Indian engineers who have spent careers optimising for depth, the transition to breadth-first, client-facing AI work may be the most consequential career decision of the decade."""
    },

    # ─── ARTICLE 3: Marvell Technology AI Surge ──────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "Marvell's Stock Just Jumped 7%. Its Largest Lab Outside California Is in India.",
        "subheadline": "As the chip company races to build the optical backbone of AI data centres, its biggest R&D hub in India is designing the connectivity silicon that Nvidia, Amazon, and Microsoft need to keep their GPU clusters running.",
        "slug": make_slug("marvell-technology-ai-surge-india-rd-hub-optical"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Marvell's largest global R&D hub outside its California HQ is in India, making Indian engineers central to the design of connectivity chips that power the world's AI data centres — a story of diaspora engineering influence at the hardware layer.",
        "tags": ["marvell", "semiconductors", "ai-infrastructure", "india-rd", "optical-interconnect", "chips"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "MarketBeat", "url": "https://www.marketbeat.com/stocks/NASDAQ-MRVL/news/"},
            {"name": "The Motley Fool", "url": "https://www.fool.com/investing/2026/06/28/marvell-stock-is-soaring-is-it-too-late-to-buy/"},
            {"name": "Hindu Business Line", "url": "https://www.thehindubusinessline.com/info-tech/nvidia-and-marvell-ceos-highlight-role-of-connectivity-in-powering-next-generation-ai-infra/article69640252.ece"},
            {"name": "Data Center Dynamics", "url": "https://www.datacenterdynamics.com/en/news/nvidia-broadcom-form-group-to-standardize-optical-interconnects-for-next-gen-ai-clusters/"}
        ]),
        "score_total": 73,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/6755078/pexels-photo-6755078.jpeg",
        "image_caption": "A semiconductor chip mounted on a printed circuit board",
        "image_attribution": "Pexels",
        "body": """The AI boom has minted obvious winners: Nvidia for GPUs, Micron for memory, TSMC for fabrication. But the less obvious winner — the company building the wiring between all those chips — has been quietly compounding returns of its own.

Marvell Technology's stock surged more than 7 per cent on Tuesday, pushing the chipmaker's market capitalisation past $243 billion. Bank of America raised its price target on the stock to $365. UBS followed with its own upgrade, citing improving prospects in data centre CXL networking and next-generation connectivity products. Erste Group lifted its FY2028 earnings estimate. The consensus on Wall Street is unusually aligned: Marvell is positioned to benefit from AI infrastructure spending for years to come.

## The Plumbing Problem

To understand why, consider what happens inside a modern AI data centre. Thousands of GPUs — each costing tens of thousands of dollars — must communicate with one another at terabit speeds. Training a large language model requires these chips to exchange staggering volumes of data, and even a small bottleneck in the network can idle millions of dollars' worth of hardware.

This is Marvell's business. The company designs custom silicon, optical transceivers, and switching chips that move data between processors. Its products connect everything from server components inside a single rack to geographically distributed data centre campuses. In a world obsessed with the compute layer, Marvell operates at the connectivity layer — and the connectivity layer is becoming the binding constraint.

Matt Murphy, Marvell's CEO, put the problem bluntly at a recent industry event. "Going forward, even the connections within the rack will become optical, and the whole industry knows this is coming," he said. Copper cables, which have served data centres for decades, are hitting physical limits. At terabit data speeds, they suffer severe signal degradation, escalating power requirements, and extreme heat generation. The future, Murphy argued, is all-optical.

## Two Acquisitions That Tell the Story

Marvell has backed that thesis with two recent acquisitions. It agreed to buy Celestial AI, which developed a photonic fabric technology platform designed for scale-up optical interconnect — essentially using light instead of electricity to move data between chips. It also acquired XConn Technologies, a provider of advanced PCIe and CXL switching silicon that links AI accelerators, GPUs, CPUs, and memory modules inside high-performance servers.

Together, these deals position Marvell as a full-stack connectivity provider for AI clusters: electrical switching at the chip level, optical transport at the rack and campus level, and the software to manage it all. The company's first-quarter fiscal 2027 results underscored the momentum. Revenue rose 27.6 per cent year-over-year. Operating cash flow nearly doubled to a record $638.8 million.

Nvidia, notably, is both a competitor and a collaborator. The two companies are founding members of the OCI-MSA, a newly formed consortium that includes Broadcom and aims to standardise optical interconnect specifications for AI clusters. "By equipping best-in-class compute with state-of-the-art optics, the OCI-MSA can deliver the scale and performance required by the next era of super-intelligence," said Nvidia networking SVP Gilad Shainer.

## India's Role in the Machine

What gets less attention is where much of this technology is designed. Marvell's largest global research and development hub outside its Santa Clara headquarters is in India. The centre — which spans multiple cities — employs thousands of engineers working on the very connectivity silicon that Amazon, Microsoft, and Google need to scale their AI infrastructure.

For Indian engineers in the semiconductor industry, this is a quietly significant story. While headlines focus on fab construction in Gujarat (Tata Electronics, Micron) and the political theatre of chip nationalism, Marvell's India operation represents something different: design leadership at the frontier of a technology transition. These are not engineers assembling components. They are designing the chips that determine how fast the world's most expensive computing clusters can think.

NRI investors who have piled into Nvidia should note the arithmetic. Marvell's stock has risen from a 52-week low of $61 to nearly $300, a gain of roughly 380 per cent. Bank of America's $365 target implies another 23 per cent of upside. The bet is not on Marvell replacing Nvidia. It is on Marvell selling the plumbing to everyone Nvidia sells GPUs to — and to Nvidia itself.

The chips may get the glory. The wires get the margins."""
    },
]


for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

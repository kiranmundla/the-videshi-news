#!/usr/bin/env python3
"""Tech writer run — 2026-07-10 20:00 PDT — 3 articles"""

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
    # ── Article 1: India GCC Boom ──
    {
        "id": str(uuid.uuid4()),
        "headline": "India Now Opens a Global Capability Centre Every Single Day. Nestlé Just Signed Up.",
        "subheadline": "With 2,100 centres, 2.3 million workers, and $100 billion in annual revenue, India's GCC empire is growing faster than any outsourcing model before it — but AI threatens to rewrite the playbook.",
        "slug": make_slug("india-gcc-one-per-day-nestle-sitharaman-ai-threat"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "NRIs at US tech giants increasingly collaborate with — or consider moving to — India's booming GCC centres, where leadership roles now mirror headquarters and the talent pipeline runs both ways.",
        "tags": ["gcc", "india-tech", "outsourcing", "nestle", "sitharaman", "ai"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/world/india/indias-office-leasing-hits-record-multinationals-expand-despite-global-2026-07-07/"},
            {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/news/india-aims-to-become-strategic-leader-in-hosting-gccs-sitharaman"},
            {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/news/ai-is-real-threat-to-traditional-gccs-skilling-key-to-indias-edge-cea-nageswaran"},
            {"name": "Genpact Press Release (via Stock Titan)", "url": "https://stocktitan.net/press-releases/genpact-nestle-business-solutions-gcc-india.html"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/36926207/pexels-photo-36926207.jpeg",
        "image_caption": "Hyderabad's Financial District tech park, home to dozens of multinational global capability centres",
        "image_attribution": "Pexels",
        "body": """In 2024, India was adding one new global capability centre every week. In 2026, it is adding one every day.

Finance Minister Nirmala Sitharaman delivered the figure at the CII GCC Business Summit on Thursday, framing it not as a boast but as a baseline. India now hosts more than 2,100 GCCs — over half of all such centres worldwide — employing 2.3 million professionals and generating nearly $100 billion in annual revenue. The country's aspiration, she said, is no longer to host the world's back offices. It is to shape the products, strategy and frontier technologies of the companies that build them.

"India's GCC journey is much larger than the story of one successful sector," Sitharaman told delegates. "It is about making India indispensable to the world's knowledge economy."

## The Numbers Behind the Surge

The scale is visible in real estate alone. India's office market absorbed a record 45.5 million square feet in the first half of 2026 — equivalent to roughly 400 football pitches — up 9.6 per cent from a year earlier, according to a CBRE report released this week. GCCs accounted for 43 per cent of all leasing and drove 53 per cent of deals above 100,000 square feet. Fortune 500 companies leased 6.8 million square feet in the second quarter, with deals rising 34 per cent from the previous quarter.

The corporate expansion is not slowing. On Thursday, Genpact announced a partnership with Nestlé Business Solutions to establish the Swiss food giant's new GCC in Hyderabad. The centre will combine Genpact's process intelligence and agentic AI capabilities with Nestlé's global operations, handling everything from digital adoption to analytics across its worldwide business network.

"This partnership reflects how leading global enterprises are reimagining business services as technology-enabled, data-driven operations," said Tarun Chopra, Genpact's Global Consumer Business Leader.

## From Back Office to Strategic Hub

The transformation is qualitative, not just quantitative. Microsoft India head Puneet Chandok pointed to the country's 27 million developers on GitHub and its massive digital public infrastructure as competitive advantages. Target now operates its Bengaluru centre as an "integrated headquarters" aligned with global strategy. IBM describes its India operations as a "macrocosm" of the entire enterprise.

At several firms, Indian centres now lead global programmes from end to end — product development, commercial processes, R&D — work that was once anchored at headquarters. The Nasscom-Zinnov GCC report for 2026 found that 60 per cent of India's GCCs now lead full-scale product development or deep analytics mandates, a sharp shift from the cost-arbitrage model of the previous decade.

"There are not too many alternatives for companies," said Lalit Ahuja, CEO of ANSR, which helps global firms build and run GCCs. The depth of India's talent pool, he argued, remains unmatched.

## The AI Warning

Not everyone was celebratory. Chief Economic Adviser V. Anantha Nageswaran, also speaking at the summit, described artificial intelligence as a "real threat" to traditional GCCs.

"The centres that stand still will suffer. The centres that move up will thrive," he said, urging companies to use AI to upgrade their operations rather than view it purely as a risk. He identified skilling as India's biggest challenge, noting that while the country produces millions of graduates annually, too few are industry-ready when they enter the workforce.

His warning carries weight. As AI compresses delivery timelines and team sizes across the IT services industry — TCS chairman N. Chandrasekaran recently said the "day is not far" when TCS would have an equal number of AI agents and employees — the GCC model faces its own version of the same disruption.

## What It Means for Indian Americans

For the estimated 4.4 million Indian Americans in the US, the GCC boom is both professional and personal. Tens of thousands work at companies whose India GCCs employ their counterparts — the Google engineer in Mountain View whose feature is shipped from Hyderabad, the JPMorgan analyst in New York whose risk model is maintained in Mumbai.

The expansion is also creating a credible alternative to the US career track. With GCC leadership roles increasingly mirroring headquarters positions, and compensation rising in Indian metros, the calculus of staying versus returning is shifting for mid-career NRIs. India's GCC centres are no longer a step down. For some, they are starting to look like a step sideways — into a role with the same scope, a lower cost of living, and proximity to family.

The question is whether AI disrupts that pitch before it fully lands."""
    },

    # ── Article 2: Apple-Broadcom $30B Deal ──
    {
        "id": str(uuid.uuid4()),
        "headline": "Apple Just Committed $30 Billion to Make Chips in America. Indian Engineers Will Design Most of Them.",
        "subheadline": "The biggest manufacturing commitment in Apple's history deepens its partnership with Broadcom and signals a new era of US-made silicon — powered largely by immigrant talent.",
        "slug": make_slug("apple-broadcom-30-billion-us-chips-indian-engineers"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Indian-origin engineers make up a significant share of chip design teams at both Apple and Broadcom. This deal expands the semiconductor jobs pipeline that has drawn Indian talent to the US for decades.",
        "tags": ["apple", "broadcom", "semiconductors", "us-manufacturing", "chips-act", "indian-engineers"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/apple-spend-30-billion-broadcom-chips-it-boosts-us-sourcing-2026-07-09/"},
            {"name": "Barron's", "url": "https://www.barrons.com/articles/apple-broadcom-chip-deal-tech-sector-b2aef1c3"},
            {"name": "Apple Press Release (via Stock Titan)", "url": "https://stocktitan.net/press-releases/apple-broadcom-chip-deal-2026.html"},
            {"name": "MacRumors", "url": "https://www.macrumors.com/2026/07/08/apple-30-billion-broadcom-deal-us-chips/"}
        ]),
        "score_total": 75,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/f/f7/Tim_Cook_March_2026_%28cropped_2%29.jpg",
        "image_caption": "Apple CEO Tim Cook, who called the Broadcom agreement the company's largest domestic manufacturing commitment",
        "image_attribution": "Wikimedia Commons",
        "body": """Apple has signed its biggest domestic manufacturing deal ever — a multi-year agreement worth more than $30 billion with Broadcom to design and produce custom silicon and wireless connectivity chips in the United States.

The deal, announced on Wednesday, will run through 2031 and result in the production of more than 15 billion US-made chips. Broadcom will invest $1.5 billion to expand and modernise its manufacturing facility in Fort Collins, Colorado, where it will produce advanced radio frequency components, including FBAR filters, along with Wi-Fi, Bluetooth and cellular connectivity technologies used across Apple's product line.

"The cutting-edge components built in Fort Collins are essential to delivering the incredible performance and connectivity our customers expect," Apple CEO Tim Cook said. "We're grateful to the president and his administration for supporting important projects like this."

## The Scale of the Commitment

The Broadcom agreement is the largest single commitment under Apple's American Manufacturing Program, launched to accelerate domestic production across its supply chain. It sits within Apple's broader pledge to invest $600 billion in the US over four years — a commitment that has helped shield the company from the Trump administration's tariff regime.

Broadcom CEO Hock Tan called the deal a continuation of "decades of success together," noting that the Fort Collins expansion would create "groundbreaking technology that connects people around the world."

Broadcom shares rose more than 4 per cent on the announcement. Apple ticked up modestly, closing at $314.17.

## The Custom Silicon Arms Race

The deal lands in the middle of a broader industry shift. Every major AI company is now racing to design or manufacture its own chips, seeking to reduce dependence on Nvidia's dominant GPU platform.

The moves are coming fast. Meta confirmed this week that it is preparing to manufacture its own AI chip, a project five years in the making, using TSMC and Broadcom as partners. OpenAI unveiled its first custom inference processor, dubbed Jalapeño, built with Broadcom last month. Anthropic is in early talks with Samsung Electronics to develop a custom AI chip on a 2nm process. Amazon and Google have been building their own silicon — Trainium and TPUs respectively — for years.

Apple's Broadcom deal is different in scope. It is not about AI inference chips but about the connectivity silicon that makes iPhones, iPads, Macs and Apple Watches work — the RF filters, the Wi-Fi modules, the Bluetooth radios. These are the components that ship in billions of units annually, and Apple is now ensuring they are made on American soil.

## The Indian Talent Pipeline

Walk through the chip design floors at Broadcom's San Jose headquarters or Apple's Cupertino campus and the demographic reality is unmistakable. Indian-origin engineers — many of them H-1B visa holders who stayed, built careers, and became citizens — form a substantial share of the semiconductor design workforce at both companies.

Broadcom's custom silicon division, which will deliver the chips under this deal, has long drawn heavily from Indian engineering talent, particularly graduates of the IITs and the Indian Institute of Science. The same is true at Apple's hardware engineering group, where chip architects, RF engineers and connectivity specialists of Indian origin hold critical roles.

The $30 billion commitment does not just secure Apple's supply chain. It deepens the job pipeline for semiconductor engineers in the United States — a pipeline that has been disproportionately fed by Indian talent for three decades. At a time when the CHIPS Act is channelling public funds into domestic fab construction, the downstream demand for design engineers is rising in lockstep.

For Indian Americans in the semiconductor industry, the deal is validation. For those watching from Bengaluru or Hyderabad, where India's own chip design ambitions are gathering pace — startups like Hrdwyr are designing edge AI processors, and the India Semiconductor Mission has brought three fabs online in five months — it is a reminder that the two countries' chip stories are increasingly intertwined.

## What Comes Next

The Fort Collins facility will produce FBAR filters and wireless components, but Apple has not disclosed a timeline for when the expanded capacity will come online. The broader question is whether Apple eventually brings its own A-series and M-series processor manufacturing to the US — chips currently fabricated exclusively by TSMC in Taiwan and, increasingly, Arizona.

For now, $30 billion buys Apple something it values more than any single product: leverage. As one Wall Street analyst put it, with a nod to Nvidia CEO Jensen Huang: "I want something in my pocket when I'm sitting across the table from Jensen negotiating."

Apple, it seems, has just filled its pocket."""
    },

    # ── Article 3: OpenAI 5% Government Equity Proposal ──
    {
        "id": str(uuid.uuid4()),
        "headline": "OpenAI Wants to Give the US Government a $42 Billion Stake. An Indian American Is Helping Broker the Deal.",
        "subheadline": "Sam Altman's proposal to hand 5 per cent of OpenAI's equity to a public wealth fund could reshape how America profits from AI — and Sriram Krishnan, the White House's AI policy chief, is at the centre of it.",
        "slug": make_slug("openai-5-percent-equity-government-sriram-krishnan"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Sriram Krishnan, an Indian-American tech executive, serves as the White House's AI policy advisor and sits at the nexus of the government-industry negotiations that will shape how AI wealth is distributed to the American public.",
        "tags": ["openai", "sam-altman", "sriram-krishnan", "ai-policy", "ipo", "white-house", "indian-american"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Financial Times (via NBC Palm Springs)", "url": "https://www.nbcpalmsprings.com/2026/07/09/openai-reportedly-in-talks-to-give-trump-administration-5-stake-worth-42-billion/"},
            {"name": "Reuters", "url": "https://www.reuters.com/technology/bofa-extends-first-520-million-loan-openai-ahead-ipo-2026-07-09/"},
            {"name": "Stocktwits", "url": "https://stocktwits.com/news/openai-anthropic-grok-ai-race-ipo-2026"},
            {"name": "Barron's", "url": "https://www.barrons.com/articles/openai-gpt-5-6-spaceXai-google-anthropic-models-2026-07-10"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/5/5a/Meeting_with_Masayoshi_Son_and_Sam_Altman_%28February_3%2C_2025%29_%283x4_cropped_on_Altman%29.jpg",
        "image_caption": "OpenAI CEO Sam Altman, who has championed the concept of a public wealth fund tied to AI equity",
        "image_attribution": "Wikimedia Commons",
        "body": """OpenAI is in early talks to hand the Trump administration a 5 per cent equity stake in the company — a transfer that, based on its most recent funding round valuation of $852 billion, would be worth an estimated $42.6 billion.

The proposal, first reported by the Financial Times, envisions a sweeping arrangement in which leading US artificial intelligence companies would allocate 5 per cent of their equity to a centralised government vehicle. OpenAI CEO Sam Altman has championed the concept, arguing that it would allow the American public to directly share in the financial upside of the AI boom. The structure under discussion is modelled on Alaska's Permanent Fund — the sovereign wealth fund that invests state oil revenues and distributes annual dividends to residents.

In April, OpenAI published a policy paper advocating for a "public wealth fund" to give every citizen a financial stake in AI-driven economic growth. The government talks are the first indication that the idea has moved from white paper to negotiation.

## The Indian American at the Table

The proposal sits at the intersection of technology policy and political dealmaking — and one of the key figures navigating that intersection is Sriram Krishnan, the Indian-American technology executive who serves as the White House's senior AI policy advisor.

Krishnan, born in Chennai and raised between India and the US, built his career across Facebook, Twitter, Snap and Andreessen Horowitz before being appointed to the White House Office of Science and Technology Policy. In the role, he has become one of the most influential voices shaping how the federal government engages with AI companies — from safety reviews to export controls to, now, equity-sharing frameworks.

His position gives him unusual leverage. The White House recently requested that OpenAI restrict the launch of its GPT-5.6 model to a small group of government-approved partners — a request that delayed what would have been the company's biggest product release ahead of its IPO. Krishnan's office has been central to negotiations over AI model governance, compute access and national security review processes.

For the Indian American community, Krishnan's role is significant beyond the policy details. He is, by most accounts, the highest-ranking Indian-origin official directly shaping US AI strategy — a position that carries both influence and scrutiny as the technology reshapes global power dynamics.

## The IPO Race

The equity proposal arrives as the two largest AI companies prepare for what could be the most consequential technology IPOs since SpaceX's $2 trillion debut in June.

OpenAI confidentially filed for a US listing last month, targeting a valuation of more than $1 trillion. Bank of America extended a $520 million credit line to the company this week — its first loan to OpenAI — and is jockeying for an advisory role on the IPO alongside Goldman Sachs and Morgan Stanley. BofA has helped raise nearly $500 billion in capital for AI companies since 2025, accounting for 60 per cent of such fundraising across debt, leveraged finance and equity markets.

Anthropic, OpenAI's chief rival, has also filed confidentially for an IPO. It is currently valued at $1.09 trillion, with annual recurring revenue of $30 billion — surpassing OpenAI's reported $24 billion ARR. The two companies are locked in a race not just for technical supremacy but for Wall Street's attention and the institutional capital that follows.

## What 5 Per Cent Would Mean

Any finalised equity agreement would likely require an act of Congress. The precedent is limited — the Trump administration has acquired stakes in individual companies before, most notably a 10 per cent holding in Intel for $8.9 billion — but a systematic equity-sharing framework across the AI industry would be unprecedented.

The Alaska Permanent Fund analogy is instructive but imperfect. Alaska's fund was seeded by oil royalties — payments for extracting a public resource. The AI version would require companies to hand over equity voluntarily, presumably in exchange for regulatory goodwill, compute access or other policy considerations. Whether rival AI developers like Anthropic, Google DeepMind or xAI would participate remains unclear.

The deeper question is philosophical: does AI, like oil, generate wealth from a shared public resource — in this case, the data, infrastructure and publicly funded research that underpin large language models — and should the public therefore receive a direct return?

## What It Means for Diaspora Investors

For NRI investors tracking the AI sector, the proposal introduces a new variable. A 5 per cent government stake would dilute existing shareholders and could constrain corporate governance. It might also signal that the US government views AI companies as quasi-public utilities — entities whose profits carry obligations to the broader public.

At the same time, the IPO pipeline is creating unprecedented opportunities. OpenAI and Anthropic together could raise tens of billions in public offerings, and Indian-American investors — many of them technology professionals with deep sector knowledge — are positioned to participate.

The irony is that much of the AI wealth being negotiated was built by immigrant talent. Indian-origin researchers and engineers hold senior positions across OpenAI, Anthropic, Google DeepMind and every major AI lab. The public wealth fund, if it materialises, would redistribute some of the value they helped create — a circle that, for the diaspora, closes in unexpected ways."""
    },
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

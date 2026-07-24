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

def verify_image(url):
    """Check image URL returns 200 with image content type and >5KB."""
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            return url
        # Try GET if HEAD didn't work
        r = requests.get(url, timeout=10, stream=True, allow_redirects=True,
                        headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct:
            return url
    except Exception as e:
        print(f"  ⚠️ Image verify failed for {url}: {e}")
    return None

# ─────────────────────────────────────────────────
# ARTICLE 1: Broadcom Q2 Earnings Results
# ─────────────────────────────────────────────────
art1_image = verify_image("https://upload.wikimedia.org/wikipedia/commons/c/c5/Hock_Tan_2022.png")
if not art1_image:
    art1_image = verify_image("https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Hock_Tan_2022.png/330px-Hock_Tan_2022.png")

art1_body = """Broadcom just delivered the kind of quarter that would make most CEOs uncork champagne. Instead, the market reached for the sell button.

The semiconductor and infrastructure software giant reported fiscal second-quarter revenue of $22.19 billion, up 48 per cent year over year, narrowly beating Wall Street's consensus estimate of $22.13 billion. Adjusted earnings came in at $2.44 per share, above the $2.40 analysts had expected. Operating margins hit a record 67 per cent.

None of it was enough. Broadcom shares dropped more than 12 per cent in after-hours trading, erasing roughly $270 billion in market capitalisation in minutes. The stock had climbed 38 per cent year-to-date through market close, and investors who loaded up ahead of the print decided to take profits rather than ride the momentum.

## The AI Engine

The headline number was AI semiconductor revenue: $10.8 billion for the quarter, up 143 per cent from a year ago. CEO Hock Tan said the result came in above his own forecast, driven by accelerating demand for custom AI accelerators and AI networking products. Broadcom now counts six major customers for its custom AI silicon — Google, Meta, Anthropic, and OpenAI among the named four, with two additional unnamed clients and three more in active engagement.

The Google relationship deepened further this quarter. Tan disclosed a long-term agreement to develop and supply multiple generations of TPU chips and AI networking infrastructure. "It's a very, very strong agreement," he told analysts. "It's a commitment that is very substantial in dollars."

For the current quarter ending August, Broadcom guided revenue to $29.4 billion — 84 per cent growth year over year — comfortably above the $28.25 billion Street estimate. AI semiconductor revenue alone is expected to reach $16 billion, representing more than 200 per cent growth from the prior year. The company's 2027 outlook for AI semiconductor revenue of $100 billion-plus was reiterated without change.

## What NRIs Should Watch

Broadcom's results carry direct implications for Indian tech professionals in the United States. The company's San Jose headquarters and design centres across California, Texas, and India employ thousands of Indian engineers in chip design, verification, and software development roles. The custom AI accelerator business — where Broadcom designs bespoke silicon for hyperscalers — is among the most technically demanding work in the semiconductor industry, and Indian talent forms a significant share of those teams.

The Google TPU deal is particularly relevant. Sundar Pichai's Alphabet, which just announced an $80 billion equity raise partly to fund AI infrastructure, is betting its compute future on custom silicon designed in large part by engineers at both Google and Broadcom. The intersection of these two companies creates a dense employment corridor for Indian chip designers and verification engineers.

For NRI investors, the after-hours selloff presents a familiar paradox. Broadcom delivered record revenue, record margins, and record free cash flow, then guided above expectations for the next quarter. The sell-the-news reaction reflects the bruising reality of a stock that had already priced in perfection. Hock Tan, the Malaysian-born CEO who transformed Broadcom from a mid-tier chipmaker into a $2.3 trillion behemoth through relentless acquisitions and operational discipline, has navigated these moments before. The question is whether the market's AI appetite remains large enough to absorb a company growing this fast.

## The Bigger Picture

Broadcom's quarter confirms what the semiconductor industry has been whispering for months: the custom AI chip market is not slowing down; it is accelerating. Every major hyperscaler is now designing its own silicon rather than relying solely on Nvidia's GPUs, and Broadcom is the company that actually builds those designs into working chips.

The $100 billion AI revenue target for 2027 — a number that seemed ambitious six months ago — now looks conservative if current growth rates hold. For the Indian engineers designing these chips, and the NRI investors tracking the AI infrastructure buildout, Broadcom's earnings report was less a disappointment than a reminder: the market has learned to expect miracles, and merely beating estimates is no longer enough."""

# ─────────────────────────────────────────────────
# ARTICLE 2: NVIDIA H-1B Hiring Surge
# ─────────────────────────────────────────────────
art2_image = verify_image("https://upload.wikimedia.org/wikipedia/commons/e/e6/Jen-Hsun_Huang_2025.jpg")
if not art2_image:
    art2_image = verify_image("https://upload.wikimedia.org/wikipedia/commons/thumb/e/e6/Jen-Hsun_Huang_2025.jpg/330px-Jen-Hsun_Huang_2025.jpg")

art2_body = """At a time when Big Tech is collectively tightening the visa pipeline, one company is swimming against the current. Nvidia, the world's most valuable company by market capitalisation, secured roughly 1,200 H-1B visa certifications in the first two quarters of fiscal 2026 — a 20 per cent increase from approximately 1,000 during the same period last year.

The contrast with its peers is stark. Google's approved H-1B hires fell from 5,100 to about 2,200, a 57 per cent decline. Amazon dropped from 6,100 to roughly 4,300. Meta, which spent much of 2025 restructuring around its AI ambitions, has slowed its foreign hiring pipeline considerably. The message from Silicon Valley's largest employers is unmistakable: even as they pour billions into AI infrastructure, they are doing it with fewer sponsored workers.

## The Nvidia Exception

What makes Nvidia's expansion noteworthy is not just its direction but its scale of compensation. Federal filings reviewed by multiple outlets reveal base salary levels that dwarf industry norms: software engineers earning up to $391,000, research scientists up to $356,500, hardware engineering managers around $350,000, and director-level positions approaching $489,000 — all before stock grants and performance bonuses that can multiply total compensation severalfold.

These numbers are not decorative. Under the current H-1B system, the US Citizenship and Immigration Services uses a weighted lottery that prioritises petitions tied to higher prevailing wages. Nvidia's salary levels place its applications squarely in the highest wage tiers, making its workers among the most likely to clear the selection hurdle. In a system that increasingly rewards well-compensated roles, Nvidia's ability to pay puts it at a structural advantage over employers offering more modest packages.

Jensen Huang, the Taiwanese-American founder and CEO, has repeatedly acknowledged the role of immigrant talent in building Nvidia's dominance. The company's GPU architecture, its CUDA software ecosystem, and its expanding portfolio of AI models and robotics platforms were all built by teams that are disproportionately international — and disproportionately Indian.

## Why Indian Professionals Should Pay Attention

Indians account for 71 to 73 per cent of all approved H-1B beneficiaries in the United States, according to USCIS data. When a company like Nvidia expands its visa sponsorships, the statistical probability is that a significant share of those 1,200 certifications will go to Indian engineers, researchers, and product managers.

But the broader picture is more complicated. The 60-day grace period — the window within which a laid-off H-1B holder must secure new sponsorship or leave the country — has become the most anxiety-inducing provision in American immigration law for Indian tech workers. With companies like Google and Amazon cutting back on both headcount and sponsorships simultaneously, the universe of available landing spots for displaced workers is shrinking.

A new $100,000 overseas filing surcharge, introduced in recent policy changes, adds another layer of cost that discourages smaller employers from sponsoring H-1B transfers. The green card process, already bottlenecked for Indian nationals by per-country limits, has been further complicated by a recent USCIS memo that may require some H-1B holders to leave the United States for consular processing — a step that can separate families and interrupt employment.

## The Two-Speed Market

What is emerging is a two-speed labour market for Indian tech talent in America. At one end sit companies like Nvidia: flush with cash, desperate for AI expertise, and willing to pay stratospheric salaries to attract the best engineers in the world. At the other sit the thousands of H-1B workers at companies undergoing AI-driven restructurings, where layoff rounds and sponsorship freezes create rolling waves of immigration anxiety.

The irony is not subtle. The very technology that Nvidia builds — the AI chips and software that power large language models, autonomous systems, and agentic computing — is the force driving layoffs at the companies that buy those chips. Nvidia sells the tools of disruption and then hires the engineers displaced by that disruption, at salaries their former employers would never have matched.

For Indian engineers weighing their next move, the calculus is clear. Nvidia is not merely hiring; it is building a talent moat around the most consequential technology of the decade. The question is whether the American immigration system will remain hospitable enough to let them walk through the door."""

# ─────────────────────────────────────────────────
# ARTICLE 3: India-US Semiconductor Partnership
# ─────────────────────────────────────────────────
art3_image = verify_image("https://images.pexels.com/photos/36169774/pexels-photo-36169774.jpeg?auto=compress&cs=tinysrgb&h=650&w=940")

art3_body = """For years, the India-US technology relationship was measured in H-1B visas and outsourcing contracts. That framing is rapidly becoming obsolete. The bilateral semiconductor and artificial intelligence partnership — formalised under the TRUST Initiative and the PAX Silica Declaration — has moved from strategic dialogue to industrial execution, with concrete projects, joint R&D agreements, and a shared supply chain architecture that both governments now describe as irreversible.

The acceleration was evident during US Secretary of State Marco Rubio's recent visit to India, where semiconductor cooperation topped the agenda alongside defence procurement and critical minerals. Senior officials from both governments told IANS that the partnership's velocity has surprised even its architects. What began as a 2025 vision statement from Prime Minister Narendra Modi and President Donald Trump has, within eighteen months, produced tangible outcomes across defence, commercial, and research domains.

## The TRUST Architecture

The TRUST Initiative — Transforming the Relationship Utilizing Strategic Technologies — is the umbrella under which the semiconductor collaboration operates. Unlike previous bilateral tech agreements that produced communiqués and little else, TRUST has been structured around deliverables.

The Shakti Semiconductor Fab, one of the partnership's anchor projects, is developing compound semiconductors for electric vehicles and aerospace applications. Compound semiconductors — made from materials like gallium nitride and silicon carbide rather than standard silicon — are critical for power electronics, 5G infrastructure, and military systems. India's existing semiconductor programme under the India Semiconductor Mission has focused primarily on conventional silicon; the Shakti project extends the ambition into materials that command higher margins and strategic importance.

American companies are embedding themselves in the execution chain. General Atomics, better known for its Predator drones, is partnering with Indian entities to validate chip designs. Synopsys, which provides the electronic design automation tools used by virtually every chipmaker on earth, is working with 3rdiTech and other Indian firms to train engineering talent and accelerate design cycles.

## PAX Silica and the Supply Chain Bet

India's accession to PAX Silica — a selective international network aimed at de-risking semiconductor supply chains — marks a strategic inflection. The declaration commits member nations to reducing dependence on adversarial states for critical minerals and foundational silicon. For India, it is both a badge of credibility and a binding obligation to align its mineral extraction and processing policies with allied standards.

The timing is deliberate. As US-China tensions over semiconductor exports intensify, Washington is actively building an alternative supply architecture that routes around Chinese control of rare earth processing and chip assembly. India, with its emerging fab ecosystem — Tata's $11 billion Dholera plant, Micron's $2.7 billion Gujarat packaging facility, and the recently approved HCL-Foxconn OSAT unit near Jewar — is being positioned as a trusted node in that network.

## The AI Infrastructure Roadmap

Beyond semiconductors, the two governments are developing an AI Infrastructure Roadmap to address financing, power, and scaling constraints for US-origin AI systems deployed in India. American tech companies want access to India's rapidly growing AI market, and India wants the computational infrastructure that currently exists only in a handful of countries.

The roadmap is expected to address three bottlenecks: power availability for large-scale data centres, financing mechanisms for compute infrastructure that Indian companies and institutions cannot yet afford independently, and regulatory alignment to enable cross-border data flows required for AI training and inference.

## What It Means for the Diaspora

For NRIs in the technology sector, the India-US semiconductor partnership opens a different kind of opportunity than the traditional Silicon Valley career path. Indian engineers and executives who built their expertise at American chip companies — Intel, Qualcomm, AMD, Broadcom, Nvidia — are now being courted to bring that knowledge back, either through direct roles at Indian fab projects or through advisory and consulting arrangements.

The Design-Linked Incentive scheme, which has already approved around two dozen companies for government support, is creating a pipeline of chip design startups that need the precise skills Indian engineers have honed over decades in the American semiconductor industry. The $92 million raised by Indian semiconductor startups in the first five months of 2026 — four times the entire 2025 total — suggests that venture capital is beginning to take the sector seriously.

The question that remains is execution. India has announced six semiconductor plants under the India Semiconductor Mission, but none is yet operational. The gap between cabinet approval and commercial production has historically been measured in years, not months. The TRUST partnership adds American technical expertise and commercial pressure to compress that timeline, but whether it succeeds will depend on whether India can deliver the infrastructure — power, water, roads, trained technicians — that chip fabs demand.

For the diaspora, it is a bet worth watching. The country that exported its best chip engineers for forty years is now asking them to come back and build what they spent their careers helping others build. The money, the policy framework, and the geopolitical momentum are all pointing in the same direction. The missing ingredient is time."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Broadcom Just Delivered Record AI Revenue of $10.8 Billion. The Market Took $270 Billion Off Its Value Anyway.",
        "subheadline": "Hock Tan's chip giant beat on every metric — revenue, earnings, guidance — but after-hours investors decided perfection was priced in. For Indian engineers designing custom AI silicon, the real story is the Google TPU deal.",
        "slug": make_slug("broadcom-q2-ai-revenue-record-stock-selloff"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Broadcom employs thousands of Indian chip designers and verification engineers across its custom AI accelerator business. The deepening Google TPU partnership intersects directly with Sundar Pichai's AI infrastructure buildout, creating dense employment corridors for NRI semiconductor talent.",
        "tags": ["broadcom", "ai-chips", "hock-tan", "earnings", "custom-silicon", "google-tpu", "indian-engineers"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Investors Business Daily", "url": "https://www.investors.com/news/technology/broadcom-stock-avgo-fiscal-q2-2026-earnings/"},
            {"name": "Wall Street Journal", "url": "https://www.wsj.com/business/earnings/broadcom-shares-slide-despite-jump-in-revenue-on-ai-chip-demand-7731ee89"},
            {"name": "MarketWatch", "url": "https://www.marketwatch.com/story/broadcoms-stock-falls-despite-accelerating-ai-chip-growth-7731ee89"},
            {"name": "MarketBeat", "url": "https://www.marketbeat.com/stocks/NASDAQ/AVGO/earnings/"}
        ]),
        "score_total": 85,
        "status": "published",
        "published_at": now,
        "image_url": art1_image or "",
        "body": art1_body,
        "is_editorial": False
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Nvidia Is Hiring 1,200 H-1B Workers While Google and Amazon Slash Theirs. The Salaries Start at $350,000.",
        "subheadline": "The world's most valuable company is expanding visa sponsorships by 20 per cent as its biggest customers cut back by half. For the 71 per cent of H-1B holders who are Indian, it is creating a two-speed labour market.",
        "slug": make_slug("nvidia-h1b-hiring-surge-google-amazon-cuts-indian"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Indians hold 71-73% of all H-1B visas in the US. Nvidia's hiring expansion at record salaries creates the most lucrative pathway for Indian AI talent, even as layoffs at Google, Amazon, and Meta force thousands of H-1B holders into the 60-day grace period scramble.",
        "tags": ["nvidia", "h1b-visa", "indian-tech-workers", "hiring", "layoffs", "silicon-valley", "immigration"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "American Bazaar", "url": "https://www.americanbazaaronline.com/2026/06/02/nvidia-tackles-tech-layoffs-with-high-paying-ai-hiring/"},
            {"name": "VisaVerge", "url": "https://www.visaverge.com/news/nvidia-h1b-hiring-rises-as-100k-fee-bites-fy-2026/"},
            {"name": "Inshorts", "url": "https://inshorts.com/en/news/nvidia-expands-h1b-hiring-amid-job-loss-reports-due-to-ai"},
            {"name": "News Ei Samay", "url": "https://www.newseisamay.com/us-news/nvidia-ramps-up-h-1b-hiring-amid-layoffs/"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": art2_image or "",
        "body": art2_body,
        "is_editorial": False
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India and America Are Now Building Chips Together. The TRUST Initiative Just Went From Paper to Factory Floor.",
        "subheadline": "The bilateral semiconductor partnership has moved from strategic dialogue to industrial execution, with compound chip fabs, AI infrastructure roadmaps, and a supply chain pact that both governments call irreversible.",
        "slug": make_slug("india-us-trust-semiconductor-partnership-industrial"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "NRI semiconductor engineers at Intel, Qualcomm, and Broadcom are being courted to bring decades of American chip expertise back to India's emerging fab ecosystem. The TRUST Initiative and PAX Silica create a structured pathway for diaspora talent to participate in India's semiconductor buildout.",
        "tags": ["india-us-relations", "semiconductor", "trust-initiative", "pax-silica", "chip-fab", "diaspora-talent", "modi-trump"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "IANS", "url": "https://ianslive.in/news/india-us-tech-partnership-in-semiconductors-ai-enters-industrial-phase/"},
            {"name": "Communications Today", "url": "https://communicationstoday.co.in/indias-chip-designers-are-finally-building-for-themselves/"},
            {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com/info-tech/hcl-foxconn-welcome-cabinet-approval-of-semiconductor-unit-in-up/article69184560.ece"},
            {"name": "Analytics Insight", "url": "https://www.analyticsinsight.net/semiconductor/semiconductor-dreams-can-india-build-a-chip-industry-from-scratch"}
        ]),
        "score_total": 78,
        "status": "published",
        "published_at": now,
        "image_url": art3_image or "",
        "body": art3_body,
        "is_editorial": False
    }
]

for art in articles:
    if not art["image_url"]:
        print(f"⚠️  No verified image for {art['slug']}, inserting without image")
        del art["image_url"]
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

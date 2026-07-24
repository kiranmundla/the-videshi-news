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
        "headline": "A Federal Judge Just Killed Trump's $100K H-1B Fee. Congress Wants to Bring It Back.",
        "subheadline": "The ruling is a reprieve for Indian tech workers and their employers — but the PROTECT Act could codify the fee into law, and the DOJ is already appealing.",
        "slug": make_slug("h1b-100k-fee-struck-down-protect-act-appeal-indian-tech"),
        "category": "technology",
        "vertical": "immigration",
        "diaspora_angle": "Indian nationals account for roughly 72% of all H-1B visa approvals. The $100K fee had already frozen hiring pipelines across Silicon Valley; its removal reopens doors, but the legislative push to revive it means the threat hasn't passed.",
        "tags": ["h-1b", "immigration", "tech-workers", "silicon-valley", "indian-diaspora"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "USA Today", "url": "https://www.usatoday.com/story/news/politics/2026/06/08/trumps-100000-fee-h1b-visas-struck-down-judge/84100789007/"},
            {"name": "Wall Street Journal", "url": "https://www.wsj.com/politics/policy/judge-strikes-down-trump-administrations-100-000-h-1b-visa-fee-06b0df2a"},
            {"name": "Daily Caller", "url": "https://dailycaller.com/2026/06/10/mike-kennedy-h1b-visa-fee-trump-american-workers-immigrants/"},
            {"name": "Analytics Insight", "url": "https://www.analyticsinsight.net/artificial-intelligence/trumps-100k-h-1b-visa-fee-back-in-court-legal-fight-puts-tech-hiring-in-spotlight"}
        ]),
        "score_total": 88,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9c/2023_H-1B_admissions_by_place_of_birth.svg/1280px-2023_H-1B_admissions_by_place_of_birth.svg.png",
        "image_caption": "H-1B visa admissions by country of birth — India dominates with over 70% of all approvals",
        "image_attribution": "Wikimedia Commons",
        "body": """The $100,000 question that has haunted every Indian engineer's immigration attorney since last September just got an answer — for now.

On June 8, U.S. District Judge Leo Sorokin in Boston ruled that the Trump administration's $100,000 fee on new H-1B visa applications was an unauthorized tax, vacating the policy in its entirety. "The substance and application of the $100,000 payment reveal that it is a tax, regardless of what the payment is called," Sorokin wrote in his 42-page ruling. Under Article I of the Constitution, only Congress can levy taxes — and Congress never gave the executive branch that authority.

The ruling was an unambiguous win for the coalition of 20 Democratic state attorneys general who brought the suit, arguing the fee hurt their ability to staff publicly funded universities, schools, and hospitals. It was also a quiet exhale for thousands of Indian families whose visa petitions had been frozen by the fee's sheer cost.

## The Numbers Tell the Story

Before Trump's September 2025 proclamation, H-1B application fees typically ranged from $2,000 to $5,000 depending on company size and petition type. The fifty-fold increase to $100,000 had an immediate chilling effect: as of February 2026, USCIS had received just 85 payments at the new rate. For context, the program issues 85,000 visas annually.

The big tech companies — Amazon, Meta, Microsoft, Google — that are the largest H-1B sponsors could absorb the cost. The real damage fell on mid-tier employers, IT services firms, and universities that simply stopped petitioning. Indian-origin workers, who account for roughly 72% of all H-1B approvals, bore the brunt disproportionately.

## The Counterattack Is Already Under Way

The reprieve may be short-lived. Within 24 hours of Sorokin's ruling, Republican Utah Rep. Mike Kennedy introduced the PROTECT Act, which seeks to codify the $100,000 fee through Congressional legislation — neatly sidestepping the constitutional objection that sank the executive order.

"We needed somebody in Congress to actually take care of this," Kennedy told the Daily Caller News Foundation. His bill would require any H-1B applicant to pay "either prevailing rates or $100,000 at a base," while compelling employers to document that they sought American workers first.

The Department of Justice has also announced it will appeal, pointing to a separate ruling by Judge Beryl Howell in Washington, D.C., who sided with the administration in a challenge brought by the U.S. Chamber of Commerce. That split between federal courts could eventually push the issue to an appeals court — or even the Supreme Court.

## What This Means for Indian Tech Workers

For the roughly 600,000 Indians currently holding H-1B status in the United States, and the tens of thousands who apply each year, the legal landscape remains treacherous. The fee is dead today, but three separate paths could revive it: the DOJ's appeal, the PROTECT Act's legislative route, or a new executive action.

Meanwhile, the broader H-1B ecosystem continues to tighten. Anthropic, OpenAI, and NVIDIA have ramped up visa applications as AI talent demand surges, but legacy IT services firms — TCS, Infosys, Wipro — are simultaneously cutting headcount as AI reshapes their business models. The visa program that once served as the primary pipeline for Indian engineering talent to reach the United States is being squeezed from both ends: immigration policy on one side, AI disruption on the other.

The one certainty is that this fight is far from settled. Indian tech professionals would do well to keep their immigration attorneys on speed dial — and perhaps a Plan B in Bengaluru."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Razorpay Just Filed for a $600 Million IPO. India's Payments War Is About to Go Public.",
        "subheadline": "The fintech giant's confidential filing targets a $5–6 billion valuation — well below its 2021 peak — as Indian startups rush to prove they can survive the public markets.",
        "slug": make_slug("razorpay-ipo-confidential-filing-600-million-valuation"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Razorpay processes $180 billion in annual payments including cross-border UPI transactions — making it the invisible plumbing behind every NRI's Swiggy order, Zerodha trade, or Zomato delivery. Its IPO is a litmus test for whether India's fintech boom can deliver public-market returns to diaspora investors.",
        "tags": ["razorpay", "ipo", "fintech", "india-startups", "upi", "payments"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/world/india/indias-razorpay-files-ipo-papers-confidentially-2026-06-15/"},
            {"name": "Storyboard18 / CNBC-TV18", "url": "https://www.storyboard18.com/how-it-works/razorpay-may-file-confidential-drhp-next-week-for-2026-ipo-cnbc-tv18-72028.htm"},
            {"name": "Entrepreneur India", "url": "https://india.entrepreneur.com/article/razorpay-plans-confidential-ipo-filing/"},
            {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/markets/razorpay-kicks-off-ipo-preparations-for-rs4500cr-listing-invites-bank-pitches"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/4226272/pexels-photo-4226272.jpeg",
        "image_caption": "A contactless digital payment being processed via smartphone — the kind of transaction Razorpay powers billions of annually",
        "image_attribution": "Pexels",
        "body": """Razorpay, the Bengaluru-based payments infrastructure company that quietly processes the money behind a significant chunk of India's digital economy, has confidentially filed its draft red herring prospectus with India's market regulator. The filing, confirmed by a newspaper advertisement on Monday, sets the stage for what could be one of India's largest fintech IPOs this year.

The numbers are substantial but sobering. The proposed offering is expected to raise between $500 million and $700 million — split roughly evenly between a fresh issue of shares and an offer-for-sale by existing investors — at a valuation of $5 billion to $6 billion. That's a meaningful haircut from the $7.5 billion peak Razorpay hit during its last private round in 2021, when easy money still flowed freely and fintech valuations floated on optimism rather than fundamentals.

## The Business Behind the Buzz

Founded in 2014 by IIT Roorkee alumni Harshil Mathur and Shashank Kumar, Razorpay has grown from a payments gateway into a sprawling financial services platform. It now processes roughly $180 billion in total payment volume annually — up from $150 billion in 2023 and $100 billion the year before — handling everything from credit card swipes and UPI transfers to buy-now-pay-later transactions and cross-border settlements.

The company's consolidated revenue surged 65% year-on-year to ₹3,783 crore ($407 million) in FY25, with gross profit reaching ₹1,277 crore. But the bottom line tells a more complicated story: Razorpay posted a net loss of ₹1,209 crore, largely driven by ESOP expenses and the one-time costs of shifting its legal domicile back to India from the United States — a "reverse flip" completed in May 2025 that cost approximately $150 million in taxes.

Axis Capital, Kotak, JPMorgan, and Citi are advising on the offering. The investor roster reads like a who's who of global venture capital: GIC, Y Combinator, Tiger Global, Peak XV Partners (formerly Sequoia India), and Lightspeed.

## Why NRI Investors Should Pay Attention

Razorpay's IPO is more than a single company going public. It's a referendum on whether India's post-2020 startup generation can actually deliver returns in the public markets — a question that has haunted the ecosystem since Paytm's disastrous 2021 listing wiped out billions in investor wealth.

The early signals are mixed. Swiggy's 2024 listing held up reasonably well; Zomato has become the rare Indian tech IPO that actually rewarded public-market investors. But public-market appetite for loss-making startups has cooled dramatically. Investors are demanding profitability timelines, not just growth narratives.

For the diaspora, there's also a more practical dimension. Razorpay powers the payment infrastructure for platforms that NRIs use constantly — Swiggy, Zomato, Zerodha, Hostinger, Airbnb India, and thousands of smaller merchants. Its cross-border payments licence from the Reserve Bank of India, obtained to handle inward and outward remittances, puts it directly in the flow of the $125 billion that the Indian diaspora sends home annually.

## The Competitive Landscape

Razorpay enters the public markets into a knife fight. PayU, backed by Naspers/Prosus, is a formidable rival in enterprise payments. Paytm, despite its post-IPO stumbles, retains massive consumer reach. Pine Labs and Cashfree compete aggressively on merchant onboarding. And PhonePe, now valued at $12 billion after its own reverse flip and Walmart-backed spin-out, looms as the payments behemoth that hasn't gone public yet.

Mathur has spoken about AI as the next frontier for payments — "a technological shift, like the way UPI was," he told CNBC-TV18 in 2025. Whether that vision translates into the kind of margin expansion that public-market investors demand remains the central question.

The confidential filing route means the full prospectus won't become public until closer to the listing date, which is expected later in 2026. Until then, the market will be left to parse tea leaves — and Razorpay's backers will be left hoping that this time, India's fintech promise actually pays off."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Zoho Built Its Own Server in Nagpur. It Took Five Years and a Mountain Pass's Name.",
        "subheadline": "The 'Nathu La' platform — designed entirely in India on Intel Xeon 6 chips — cuts power consumption by 18% and ownership costs by 30%, marking Zoho's entry into the sovereign hardware race.",
        "slug": make_slug("zoho-nathu-la-server-india-designed-sovereign-hardware"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Zoho serves 100 million users worldwide, including tens of thousands of Indian-origin small business owners in the US. Its move into India-designed hardware signals that Indian tech sovereignty is no longer just a government talking point — it's being built by private companies, with IP owned entirely in India.",
        "tags": ["zoho", "india-hardware", "sovereign-tech", "data-center", "make-in-india", "intel"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "YourStory", "url": "https://yourstory.com/2026/06/zoho-unveils-made-in-india-server-nathu-la"},
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/info-tech/zoho-launches-its-own-designed-in-india-server-nathu-la/article69655432.ece"},
            {"name": "Morningstar / BusinessWire", "url": "https://www.morningstar.com/news/business-wire/20260609494283/zoho-corporation-unveils-nathu-la-a-designed-in-house-server-in-a-move-towards-technological-sovereignty-and-inference-cost-reduction"},
            {"name": "TechCircle", "url": "https://www.techcircle.in/2026/06/12/its-a-wrap-news-this-week-jun-8-12"}
        ]),
        "score_total": 75,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/37730212/pexels-photo-37730212.jpeg",
        "image_caption": "Server racks in a modern data centre — Zoho's Nathu La platform aims to replace imported hardware with India-designed alternatives",
        "image_attribution": "Pexels",
        "body": """There is something quietly radical about naming a server after a Himalayan mountain pass. Nathu La — the 14,140-foot crossing between Sikkim and Tibet, once a critical artery on the old Silk Road — carries connotations of sovereignty, strategic passage, and the kind of geographic ambition that India has spent decades trying to project. It's a lot of weight for a piece of data centre hardware to bear. But Zoho, the Chennai-based SaaS company that has spent two decades doing things its own way, clearly chose the name with intent.

The Nathu La server platform, unveiled this month, is the product of five years of R&D at Zoho's facility in Nagpur — not Bengaluru, not Hyderabad, but the central Indian city better known for oranges than for chip design. The server runs on Intel Xeon 6 processors and is built for the workloads that actually matter in 2026: AI inference, high-performance computing, virtualisation, and storage. Zoho claims it delivers equivalent performance to imported alternatives with 12–18% lower power consumption and 20–30% lower total cost of ownership.

## The Full Stack, All the Way Down

What makes Nathu La notable isn't just the performance claims — it's the ownership structure. Every modular component, including the DC-SCM (Data Centre Secure Control Module) and the NIC (Network Interface Card), was designed in-house by Zoho's hardware engineering team. Assembly was handled by Indian electronic manufacturing services partners. Five patents have been filed covering thermal management and cost-optimised server architecture.

"We are proud to build a server system that is truly designed in India and taking a step towards creating sovereign technology," said Shailesh Davey, CEO of Zoho Corp. The emphasis on sovereignty is deliberate. India's digital infrastructure has expanded at a breakneck pace, but the server hardware underpinning it has historically been sourced from abroad — Dell, HPE, Supermicro — with Indian enterprises paying royalties and licensing fees to foreign entities.

Zoho now joins an extremely short list of technology companies globally that control the full stack from hardware to application layer. The company already runs its own data centres, builds its own software across 55+ products, and famously rejects external venture capital. Adding custom server hardware to that list is the logical extension of a corporate philosophy that prizes self-sufficiency above all else.

## The Nagpur Factor

Zoho's decision to build this in Nagpur rather than a traditional tech hub is a statement in itself. The Nagpur centre was established in 2020 specifically for R&D projects, and its engineering team was recruited and trained locally — an extension of Zoho founder Sridhar Vembu's long-standing commitment to building technology talent in India's smaller cities and rural areas.

"The development of the Nathu La server reflects our commitment to creating complex technology powered by talent from smaller towns and villages," Davey said. For a company whose founder moved his own office from Chennai to the village of Tenkasi in Tamil Nadu, this isn't corporate social responsibility theatre. It's operational doctrine.

Ramprakash Ramamoorthy, Zoho's Director of AI, told The Hindu BusinessLine that the company plans to deploy 2,000 Nathu La servers by the end of 2026 across various configurations, powering services like Zoho Mail and Zoho Meeting. The platform is not being commercialised at this stage — Zoho is building these servers for its own use, not to compete with Dell or HPE in the enterprise market.

## Why This Matters Beyond Zoho

India's server imports have been rising sharply as AI workloads drive demand for compute infrastructure. In 2023, the Indian government announced import restrictions on compute devices including servers, explicitly signalling that it wanted domestic alternatives. Nathu La is one answer to that call — built not by a government-backed consortium or a defence contractor, but by a private SaaS company in Nagpur that decided it could do the job itself.

For the Indian diaspora watching from the US, UK, and Canada, the message is clear: the "Make in India" push in technology has moved beyond assembly plants for iPhones and into the design of the computational infrastructure itself. The IP is Indian. The patents are Indian. The talent is Indian. And if Zoho's claims about cost and efficiency hold up at scale, the economics might actually work.

The server is named after a mountain pass. The ambition is to build a road that didn't exist before."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

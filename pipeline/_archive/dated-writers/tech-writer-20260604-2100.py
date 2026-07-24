#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-06-04 21:00 UTC run"""

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

# =========================================================================
# ARTICLE 1: NVIDIA H-1B Hiring Surge
# =========================================================================

art1_headline = "NVIDIA Is Hiring More H-1B Workers Than Ever. Google and Amazon Are Doing the Opposite."
art1_subheadline = "Jensen Huang's chipmaker secured 1,200 visa certifications in six months, up 20 per cent, while Alphabet and Amazon slashed theirs by nearly 40 per cent. For Indian engineers, NVIDIA is now the clearest bet in a tightening market."
art1_slug = make_slug("nvidia-h1b-hiring-surge-google-amazon-cuts-indian-engineers")
art1_body = """The American tech industry is telling two contradictory stories about its need for foreign talent. At one end stands NVIDIA, which secured certification for approximately 1,200 H-1B positions during the first two quarters of its fiscal year 2026 — a 20 per cent increase from the roughly 1,000 approvals during the same period a year earlier. At the other end stand Alphabet and Amazon, which cut their certified H-1B hires by nearly 40 per cent during the same window, dropping from 5,100 to around 2,200 and from 6,100 to roughly 4,300 respectively.

The divergence is not accidental. It maps almost perfectly onto who is winning, and who is restructuring, in the age of artificial intelligence.

## The NVIDIA Exception

NVIDIA's hiring surge arrives at a moment when the company is the undisputed gatekeeper of AI infrastructure. Its GPUs power the training clusters at OpenAI, Anthropic, Google DeepMind, and virtually every frontier lab on the planet. Revenue has followed: the chipmaker's data centre business now generates more in a single quarter than most semiconductor companies produce in a year.

That growth requires people. Federal labour filings reveal exactly how much NVIDIA is willing to pay for them. Base salaries for AI researchers range from approximately $120,000 to $410,000. Architecture directors can earn up to $560,000 in base pay alone, before stock awards, bonuses, and other incentives are factored in. Software engineering directors sit in a range of $450,000 to $540,000. Even entry-level verification engineers start above $135,000.

CEO Jensen Huang, who was born in Taiwan, has repeatedly emphasised the role immigrant talent plays in the company's success. When the Trump administration imposed a new $100,000 fee on H-1B applications last year, Huang wrote to employees that NVIDIA would absorb the cost entirely: "We built our company with extraordinary people from around the world. We will continue to sponsor H-1B applicants and cover all associated fees."

## The Other Side of the Valley

The contrast with NVIDIA's peers is stark. Google's parent Alphabet reduced its certified H-1B hiring to approximately 2,200 positions from 5,100 a year ago. Amazon's declined to roughly 4,300 from 6,100. Both companies have embarked on aggressive restructuring as they shift resources toward AI, eliminating roles in legacy divisions while building out model-training and cloud-inference teams.

The cutbacks are not limited to these two. Across the broader tech sector, companies that once accounted for thousands of annual H-1B sponsorships — including Meta, Salesforce, and several enterprise-software firms — have either slowed or paused their foreign-hiring pipelines.

## What This Means for Indian Engineers

The numbers carry particular weight for Indian professionals, who account for 71 to 73 per cent of all approved H-1B beneficiaries. For years, the typical career path for an Indian engineer arriving in America ran through a consulting firm or a mid-tier technology company before graduating to a FAANG employer. That funnel is narrowing.

Under current immigration rules, H-1B holders who lose their jobs have 60 days to find a new sponsoring employer or face the prospect of leaving the country. With Alphabet and Amazon pulling back their sponsorship volumes, the practical universe of available positions has shrunk meaningfully, even as demand for AI skills has never been higher.

NVIDIA, in this context, is becoming more than just a chip company. For a growing number of Indian engineers, it is the single most reliable gateway to a career in American AI — one of the few large employers that is simultaneously expanding its workforce, paying top-of-market salaries, and publicly committing to continued visa sponsorship.

## The Legislative Shadow

This corporate divergence arrives against a backdrop of legislative uncertainty. Representative Chip Roy of Texas introduced the American White-Collar Worker Jobs Act on 4 June, which would replace the current H-1B lottery with wage-based selection, require employers to demonstrate good-faith efforts to hire American workers first, and prevent companies that have recently conducted layoffs from sponsoring new H-1B workers. The bill would also end the Optional Practical Training programme entirely.

Whether the bill advances or dies in committee, the direction of travel in Washington is clear. For Indian professionals weighing their options, the window for building a career through the H-1B system may be narrower than it appears — making the employers who are still actively hiring all the more critical.

NVIDIA, for now, is the biggest name on that shrinking list."""

art1_sources = json.dumps([
    {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/corporate/nvidia-defies-us-visa-slowdown-offers-crores-to-global-talent"},
    {"name": "Inshorts / NDTV", "url": "https://inshorts.com/en/news/nvidia-expands-h1b-hiring-amid-job-loss-reports-due-to-ai"},
    {"name": "Business Insider (via Outlook Business)", "url": "https://www.outlookbusiness.com/corporate/nvidia-defies-us-visa-slowdown-offers-crores-to-global-talent"},
    {"name": "Rep. Chip Roy press release", "url": "https://roy.house.gov/media/press-releases/rep-roy-introduces-legislation-end-h-1b-abuse-protect-american-tech-workers"}
])

# =========================================================================
# ARTICLE 2: NITI Aayog Semiconductor Roadmap
# =========================================================================

art2_headline = "India Says It Needs $180 Billion to Build a Chip Industry. NITI Aayog Just Published the Roadmap."
art2_subheadline = "A new government report targets a $120–150 billion semiconductor value chain by 2035 and admits that 90 to 95 per cent of India's chip demand is currently met by imports. For NRI engineers and investors, it is the most detailed signal yet on where the opportunities lie."
art2_slug = make_slug("niti-aayog-semiconductor-roadmap-180-billion-india-chip-industry")
art2_body = """India's ambitions in semiconductor manufacturing have moved from aspiration to blueprint. NITI Aayog, the government's policy think tank, has released a detailed roadmap titled "Future of India's Semiconductor Industry" that sets explicit targets, acknowledges uncomfortable gaps, and lays out the capital required to close them.

The headline number: India needs between $135 billion and $180 billion in cumulative investment over the next decade to build a globally competitive semiconductor ecosystem spanning design, fabrication, advanced packaging, materials, and supporting infrastructure. The government, the report argues, should commit at least one-third of that total to de-risk projects and anchor long-term investor confidence.

## The Starting Point Is Blunt

The roadmap does not sugarcoat India's current position. Nearly 90 to 95 per cent of the country's semiconductor demand is met through imports, leading to large foreign-exchange outflows and supply-chain vulnerabilities that the Gulf conflict has made viscerally clear. India's own semiconductor market is projected to reach approximately $200 billion by 2035, against a global market expected to exceed $1.5 trillion. But capturing value domestically is another matter entirely.

The report is structured around five mutually reinforcing pillars: pioneering frontier research and design intellectual property; policy and investment to mobilise long-horizon capital; production focused on advanced packaging and compound semiconductors; people across the full semiconductor talent pyramid; and partnerships with trusted nations and global industry.

## Where the Money Goes

India Semiconductor Mission 2.0, announced in the Union Budget 2026, marks the shift from ecosystem creation to ecosystem deepening. The first phase concluded with approvals for six projects — including Tata Electronics' $11 billion fabrication facility in Dholera (Gujarat), Micron's $2.7 billion assembly and test plant in Sanand, and the HCL-Foxconn display driver chip unit near Jewar airport. Crystal Matrix and Suchi Semicon were the final two approvals.

The second phase targets domestic production of semiconductor equipment and materials, full-stack Indian semiconductor intellectual property, and stronger supply chains. The roadmap sets specific goals: positioning India as a leading global destination for advanced packaging and outsourced semiconductor assembly and test operations, emerging as a major supplier of wide-bandgap semiconductors like silicon carbide and gallium nitride, and creating more than 100 advanced semiconductor design IPs.

## The Talent Equation

India already supplies roughly 20 per cent of global semiconductor design talent, with over 35,000 engineers engaged in chip design. But the NITI Aayog report notes an uncomfortable truth: this talent is predominantly employed by established international fabless companies rather than Indian design firms, reflecting a lack of indigenous agency in the semiconductor design space.

For the estimated 50,000-plus Indian semiconductor professionals currently working abroad — at TSMC, Intel, Qualcomm, NVIDIA, Broadcom, and other chipmakers — the roadmap represents the most detailed articulation yet of what a return-to-India career in semiconductors might look like. The targets for compound semiconductor manufacturing and advanced packaging, in particular, map closely to the skills that diaspora engineers have spent decades building in the United States, Taiwan, and South Korea.

## What NRI Investors Should Watch

The investment thesis is clearer than it has been at any point in India's chip story. With government subsidies covering up to 50 per cent of fabrication costs and ISM 2.0 explicitly targeting equipment and materials companies, the opportunity extends beyond the headline fab projects into a broader supply-chain ecosystem.

India's chip design startup ecosystem has already attracted $92 million in funding in the first five months of 2026, four times the total for all of 2025. The NITI Aayog roadmap suggests this is just the opening chapter. The government is signalling, in unusually specific terms, that it wants India to set standards and shape supply chains rather than merely participate in them.

Whether India can execute on that ambition remains an open question. The country has no operational commercial fab today, and the Tata Electronics facility in Dholera is not expected to reach full monthly capacity of 50,000 wafers until late 2026 at the earliest. The gap between policy ambition and factory-floor reality is still measured in years. But the roadmap, at minimum, gives that ambition a price tag — and that is further than India has gone before."""

art2_sources = json.dumps([
    {"name": "Communications Today", "url": "https://www.communicationstoday.co.in/niti-aayog-releases-future-of-indias-semiconductor-industry-roadmap/"},
    {"name": "CXOToday", "url": "https://www.cxotoday.com/news-analysis/india-should-target-a-150bn-chipmaking-ecosystem-by-2035-to-play-the-ai-game/"},
    {"name": "Communications Today (market projections)", "url": "https://www.communicationstoday.co.in/indias-semiconductor-market-200b-by-2035-niti-aayog/"},
    {"name": "Autona News", "url": "https://www.autonainews.com/technology/india-semiconductor-industry-targets-150b-value-chain"}
])

# =========================================================================
# ARTICLE 3: Apple Siri on NVIDIA Blackwell via Google Cloud
# =========================================================================

art3_headline = "Apple's New Siri Will Run on NVIDIA Chips Inside Google's Cloud. The Irony Writes Itself."
art3_subheadline = "Reports confirm that the overhauled Siri, expected at WWDC on 8 June, will process complex queries on NVIDIA Blackwell B200 GPUs hosted by Google Cloud — a three-company supply chain that no one at Apple would have predicted five years ago."
art3_slug = make_slug("apple-siri-nvidia-blackwell-google-cloud-wwdc-2026")
art3_body = """The most vertically integrated company in technology is about to ship its most important AI product on someone else's chips, inside someone else's cloud, running someone else's model. And it might be the smartest move Apple has made in years.

Multiple reports, most recently from The Information on 4 June, confirm that when Apple launches its rebuilt Siri at WWDC on 8 June, complex queries that cannot be handled on-device will be routed to Google Cloud, where they will run on a licensed version of Google's Gemini model, processed on NVIDIA's Blackwell B200 data centre GPUs. Apple has approved NVIDIA's hardware-based confidential compute feature for this arrangement, which encrypts data as it is being processed on the chips.

## How It Works

The architecture splits Siri's intelligence into two tiers. Lightweight tasks — setting timers, basic lookups, simple device controls — will continue to run locally on Apple silicon, as they do today. The new capability sits in the second tier: conversational reasoning, multi-step task planning, document summarisation, and agentic workflows that require the kind of compute no smartphone or laptop can deliver.

For those queries, Apple will tap into Google's fleet of Blackwell B200 GPUs. Bloomberg's Mark Gurman has described the underlying model as a 1.2 trillion-parameter system, far larger than the cloud model currently behind Apple Intelligence. Apple reportedly tried to get a modified version of Gemini running on its own Private Cloud Compute servers, which use Mac-series chips, but found it ran too slowly.

The company is expected to retain the Private Cloud Compute branding despite the fundamental change in where the compute actually happens. Apple is also said to be training a smaller, distilled version of Gemini capable of running locally on Apple hardware, and has considered acquiring Liquid AI, a Massachusetts startup focused on efficient on-device AI inference.

## The Three-Company Stack

The arrangement creates a supply chain with no precedent in Apple's history. Sundar Pichai's Google provides the model and the cloud infrastructure. Jensen Huang's NVIDIA provides the chips. Apple provides the distribution — roughly 2.2 billion active devices worldwide — and the user experience. Apple is reportedly paying Google approximately $1 billion annually for access.

For a company that once designed its own screws to avoid depending on third parties, this is a remarkable concession. But the economics are hard to argue with. Google and Microsoft have collectively committed over $100 billion to AI infrastructure this year alone. Apple, which has focused its capital on consumer devices and share buybacks, simply does not have the data-centre footprint to run a frontier model at the scale Siri requires.

## The Indian Angle

The three companies sitting at the core of this arrangement — Alphabet, NVIDIA, and Apple — are among the largest employers of Indian engineering talent in the United States. Sundar Pichai, Alphabet's CEO, is Indian-born. NVIDIA's AI research teams are heavily staffed by Indian professionals, as the company's expanding H-1B hiring indicates. Apple's hardware and silicon engineering divisions in Cupertino employ thousands of Indian-origin engineers.

This is also Tim Cook's final WWDC before John Ternus assumes the CEO role in September. Cook framed the Google partnership positively in Apple's most recent earnings call: "The collaboration with Google is going well. We are happy with where things are."

For India's own AI ecosystem, the arrangement is instructive. Apple chose not to build its own frontier model, instead licensing one from a company with deeper AI research capabilities. It chose not to build its own GPU fleet, instead renting one from a company with deeper hardware expertise. The lesson for Indian technology companies is not that Apple is weak, but that even the world's most valuable company has decided that trying to do everything yourself in AI is a losing strategy.

WWDC begins on Monday. The rebuilt Siri, whenever it ships to devices in the autumn, will be the most widely distributed AI product in history. And it will run, at least in part, on chips designed by NVIDIA, hosted by Google, and sold through Apple. Every company in that chain employs thousands of Indians. The supply chain of intelligence, as it turns out, looks a lot like the supply chain of Silicon Valley itself."""

art3_sources = json.dumps([
    {"name": "The Information (via MacRumors)", "url": "https://www.macrumors.com/2026/06/04/apple-siri-nvidia-blackwell-chips/"},
    {"name": "The Information (via 9to5Mac)", "url": "https://9to5mac.com/2026/06/04/report-details-apples-plan-to-use-nvidia-chips-for-the-gemini-powered-siri/"},
    {"name": "Motley Fool", "url": "https://www.fool.com/investing/2026/06/02/apples-wwdc-is-june-8-heres-the-1-announcement-th/"},
    {"name": "TechCrunch", "url": "https://techcrunch.com/2026/06/04/what-to-expect-from-wwdc-2026/"}
])

# =========================================================================
# Articles array
# =========================================================================

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": art1_headline,
        "subheadline": art1_subheadline,
        "slug": art1_slug,
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Indian engineers hold 71-73% of all H-1B visas. NVIDIA's hiring surge and top-of-market salaries make it the most critical employer for Indian AI talent, while cutbacks at Google and Amazon narrow the options. The Chip Roy bill threatens the entire pipeline.",
        "tags": ["nvidia", "h-1b-visa", "indian-engineers", "silicon-valley", "ai-hiring", "immigration"],
        "urgency": "high",
        "sources": art1_sources,
        "score_total": 85,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/e/e6/Jen-Hsun_Huang_2025.jpg",
        "image_caption": "NVIDIA CEO Jensen Huang at a company event in 2025",
        "image_attribution": "Wikimedia Commons",
        "body": art1_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": art2_headline,
        "subheadline": art2_subheadline,
        "slug": art2_slug,
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Over 50,000 Indian semiconductor professionals work abroad. The roadmap targets compound semiconductors and advanced packaging — skills diaspora engineers have built at TSMC, Intel, and Broadcom. Investment opportunities are emerging in India's chip design startup ecosystem, which raised $92M in five months.",
        "tags": ["india-semiconductor", "niti-aayog", "chip-manufacturing", "nri-investment", "dholera-fab", "ism-2"],
        "urgency": "medium",
        "sources": art2_sources,
        "score_total": 78,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/36169774/pexels-photo-36169774.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
        "image_caption": "Closeup of microchips on a circuit board, the building blocks of the semiconductor industry",
        "image_attribution": "Pexels",
        "body": art2_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": art3_headline,
        "subheadline": art3_subheadline,
        "slug": art3_slug,
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Alphabet (led by Indian-born Sundar Pichai), NVIDIA (expanding H-1B hiring of Indian engineers), and Apple (thousands of Indian-origin engineers in Cupertino) are the three pillars of the new Siri stack. The arrangement mirrors how Indian talent underpins Silicon Valley's AI infrastructure.",
        "tags": ["apple", "wwdc-2026", "siri", "nvidia-blackwell", "google-gemini", "ai-infrastructure"],
        "urgency": "medium",
        "sources": art3_sources,
        "score_total": 75,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/f/f7/Tim_Cook_March_2026_%28cropped_2%29.jpg",
        "image_caption": "Apple CEO Tim Cook, who will deliver his final WWDC keynote on 8 June before handing the role to John Ternus",
        "image_attribution": "Wikimedia Commons",
        "body": art3_body
    },
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

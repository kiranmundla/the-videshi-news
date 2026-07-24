#!/usr/bin/env python3
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

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
        "headline": "India Sees a Million Empty Chip Jobs. Its Minister Wants Indian Graduates to Fill Them — Worldwide.",
        "subheadline": "Ashwini Vaishnaw says the global semiconductor industry is short a million skilled workers by 2032. For NRIs in the chip business, that is a hiring market about to tilt their way.",
        "slug": make_slug("india-semiconductor-talent-shortage-vaishnaw-million-jobs-nri-chip"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Indian-origin engineers already staff the design floors at Nvidia, AMD, Qualcomm and Micron; a structural global talent crunch hands them leverage on pay and mobility just as India builds its own pipeline to feed the same shortage.",
        "tags": ["semiconductor", "india-tech", "chips", "h1b", "indian-engineers", "vaishnaw"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "IANS Live", "url": "https://www.ianslive.in/"},
            {"name": "Outlook Business — C2i tape-out", "url": "https://www.outlookbusiness.com/"},
            {"name": "Zacks — ASML/Tata Dholera fab", "url": "https://www.zacks.com/"}
        ]),
        "score_total": 76,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/3/35/Ashwini_Vaishnaw_cropped.jpg",
        "image_caption": "Union Electronics and IT Minister Ashwini Vaishnaw, who oversees India's semiconductor mission.",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": """India's electronics minister put a startling number on the table this week. Speaking in Patna on Friday, Ashwini Vaishnaw said the global semiconductor industry — worth roughly $800 billion today and on course to cross $1 trillion within a year — will need about a million more skilled professionals by 2032, and is already short by close to that figure right now.

That is not a footnote. It is the single most important fact about where the chip industry is heading, and it lands squarely on the desks of the Indian-origin engineers who already crowd the design floors at Nvidia, AMD, Qualcomm, Intel and Micron.

## A shortage, not a glut

For two years the tech narrative for the diaspora has been defensive: layoffs, AI restructuring, the H-1B clock. Semiconductors run against that current. Designing and verifying advanced chips is hard, slow-to-train work, and the people who can do it are scarce. Vaishnaw's framing — a worldwide deficit of skilled hands — describes a labour market tilting toward the worker, not the employer.

That matters for an Indian engineer in Santa Clara or Austin in a concrete way. Scarcity is leverage: on compensation, on the freedom to switch employers, and on the bargaining power that makes visa sponsorship a cost a company will swallow rather than a favour it grants. In a field with a million empty seats, the firm needs the engineer more than the engineer needs any one firm.

## India wants to be the supplier

Vaishnaw's pitch was that India should fill the gap. He said nearly 75,000 students have already moved through semiconductor-design programmes, with a target of lifting that to 500,000, and argued that Indian graduates should "immediately find opportunities in the industry" anywhere in the world. The government, he said, is building both design capability and, as fabs come online, manufacturing skills.

The groundwork is visible. In May, ASML signed an agreement to supply lithography gear to Tata Electronics' $11 billion fab in Dholera, Gujarat. Bengaluru startup C2i Semiconductors recently taped out a power-management chip for AI data centres — conceived, architected and verified entirely in India, a first for a country that has historically done design services rather than original silicon. The India Semiconductor Mission says its design-linked incentive scheme has now backed 105 companies.

## Why the diaspora should read this carefully

There are two ways this plays for Indian Americans, and they pull in different directions.

The optimistic read: a deeper Indian chip-design base widens the talent network the diaspora already anchors. More fabs and more design houses in India mean more cross-border roles, more startups to advise or invest in, and a credible "return option" for engineers weighing a move home.

The cautious read: if India trains half a million chip designers who will work for Indian wages, some of the routine design and verification work currently done in the US migrates east — the same pattern that hollowed out parts of IT services. The senior architecture and leadership roles stay in Silicon Valley; the entry rungs may not.

The likeliest outcome sits between the two. A million-person shortage is too large to be solved by offshoring alone, which means demand stays strong on both shores for years. For an NRI already inside the chip business, the safe move is the obvious one: go deeper into the parts of the stack that are hardest to train for and hardest to relocate — advanced architecture, AI accelerator design, high-bandwidth memory, the physics-heavy work where a million empty chairs is a feature of your career, not a threat to it.

What India is really announcing is a bet that the world's chip talent will increasingly carry an Indian passport or an Indian degree. The diaspora is the proof of concept. The question for the next decade is whether the value follows the talent — or stays where the talent emigrates to."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Wipro Just Opened a Claude Lab in Bengaluru and Promised to Retrain 10,000 People. It Is Also Admitting What AI Does to Its Old Model.",
        "subheadline": "The IT giant is building a Center of Excellence around Anthropic's AI even as analysts warn the same technology is eating into the labour-heavy business that employs hundreds of thousands of Indians.",
        "slug": make_slug("wipro-anthropic-claude-ai-center-bengaluru-it-services-nri-jobs"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "The Indian IT services giants are the career ladder that brought a generation of NRIs to the US on H-1B and L-1 visas; their scramble to retrain around AI signals which skills will still earn that ticket — and which won't.",
        "tags": ["wipro", "anthropic", "claude", "indian-it", "ai", "it-services", "h1b"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters — Wipro AI center", "url": "https://www.reuters.com/"},
            {"name": "Reuters — Indian IT stocks tumble on Accenture", "url": "https://www.reuters.com/"}
        ]),
        "score_total": 74,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/7988079/pexels-photo-7988079.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Software engineers at work; India's IT services firms are racing to retrain staff around AI tools.",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": """Wipro said this week it has set up a Center of Excellence in Bengaluru built around Anthropic's Claude models, and that it will train 10,000 of its employees to use the technology over the next 18 months. On its face it is a routine corporate announcement. Read against the backdrop of the week, it is something closer to a confession.

That backdrop: on Friday, India's Nifty IT index dropped 5.6% after Accenture — the bellwether for the whole outsourcing trade — forecast quarterly sales below Wall Street expectations and trimmed its annual outlook. TCS, Infosys and HCL Tech all fell between 5% and 8%. The fear stalking the $315 billion Indian IT sector is simple: that AI tools can do the labour-intensive coding and support work the industry was built to sell cheaply, and that clients no longer need armies of people to get it.

## Building the thing that threatens you

Wipro's Claude lab is meant to answer that fear by joining it. The Center of Excellence is pitched at helping the firm scale enterprise AI for clients and rebuild applications and workflows with AI baked in. The point of retraining 10,000 staff is to move them up the value chain — from writing code to orchestrating the AI that writes it.

Wipro is not alone, and it is not even first. On June 11, TCS announced an alliance with Anthropic to drive enterprise AI adoption. HCLTech this month led a $150 million strategic investment in Indian AI startup Sarvam. The entire sector is sprinting to reposition itself from "we have the most people" to "we have the smartest deployment of machines."

## Why this is personal for the diaspora

For Indian Americans, the IT services firms are not abstract stock tickers. They are the on-ramp. TCS, Infosys, Wipro, HCL, Cognizant and the rest have for two decades been among the largest sponsors of H-1B and L-1 visas — the mechanism that moved a generation of Indian engineers from Pune and Hyderabad to New Jersey and the Bay Area. What these companies value determines who gets that ticket.

The signal in Wipro's announcement is unmistakable: the body-shopping model that staffed projects by the headcount is being retired in slow motion. Analysts at Jefferies told clients Wipro itself expects "compression in services revenue" in the coming quarters. The roles that survive — and the ones that earn a visa sponsorship in 2027 — are the AI-fluent ones: people who can architect, integrate and govern AI systems, not people who can be billed by the hour for routine development.

For an NRI mid-career inside one of these firms, the retraining wave is both a warning and an opening. The warning is that the old skills are depreciating fast. The opening is that the company is, for now, willing to pay to upgrade you — a window that tends to close once the cheaper option (hiring fresh AI-native graduates) matures.

## The deeper unease

There is an irony the market has already priced in. The Indian IT giants made their fortune by being the cheaper, scalable alternative to expensive Western labour. AI is now the cheaper, scalable alternative to them. Building a Claude lab does not resolve that tension; it manages it.

Whether Wipro's bet works depends on a question no press release can answer: can a company whose core competence was supplying people pivot to supplying intelligence faster than its clients learn to buy that intelligence directly from Anthropic, OpenAI or Google? The 10,000 employees being retrained in Bengaluru are, in effect, the experiment. So is the diaspora that the sector helped create."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "HCLTech Just Bought a Slice of India's Sovereign-AI Dream for $150 Million. The Buyer List Tells You Where the Money Now Flows.",
        "subheadline": "The IT major took a 10.5% stake in Sarvam AI at a $1.5 billion valuation, betting that 'made-in-India' models for regulated industries are the next export — not cheap code.",
        "slug": make_slug("hcltech-sarvam-ai-stake-sovereign-ai-india-nri-investors-models"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "NRI investors hunting India exposure beyond Flipkart and Swiggy now have a sovereign-AI thesis to track; HCLTech's bet signals which Indian deep-tech names the smart money — Bessemer, Khosla, Peak XV — is backing.",
        "tags": ["hcltech", "sarvam-ai", "sovereign-ai", "india-startups", "ai", "nri-investors"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters — HCLTech stake in Sarvam AI", "url": "https://www.reuters.com/"},
            {"name": "YourStory — startup roundup", "url": "https://yourstory.com/"}
        ]),
        "score_total": 73,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/17489163/pexels-photo-17489163.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "An AI data centre interior; Indian startups are racing to build sovereign models for regulated industries.",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": """HCLTech said it will acquire a 10.5% stake in Sarvam AI for 14.27 billion rupees — about $150.7 million — leading the generative-AI startup's Series B as a strategic investor. The round valued Sarvam at $1.5 billion and raised $234 million in a first close against a $300 million target. The co-lead was Bessemer Venture Partners, with existing backers Khosla Ventures and Peak XV Partners staying in.

Strip away the deal mechanics and the interesting part is the thesis. HCLTech, one of India's largest IT exporters, is not buying a consumer app or a quick-commerce play. It is buying into the idea that India can build its own foundation models — and sell them to governments and regulated industries that do not want to run their data through American or Chinese AI.

## The word that matters: sovereign

HCLTech was explicit about why. The investment, it said, will help it build language models and AI solutions for its global client base and "accelerate the development of sovereign AI solutions for governments and regulated industries." Sarvam will use HCLTech's funding to train next-generation models for agentic AI, coding and cybersecurity.

"Sovereign AI" — models trained, hosted and governed within a country's own borders — has gone from a policy slogan to a procurement requirement. Banks, defence ministries and health systems increasingly cannot, for legal or political reasons, send sensitive data to a model running on a foreign cloud. That creates a market for credible local alternatives, and India, with its vast data and a government pushing hard on the theme, wants Sarvam to be one.

## Why NRIs should be tracking this

For diaspora investors, the menu of "India tech" exposure has long been thin and consumer-heavy: Flipkart, Swiggy, Zomato, the payment names like Razorpay now lining up for IPOs. Deep tech — the harder, science-led category — has been almost impossible to access from a US brokerage account.

HCLTech's stake is a tell. When a listed Indian IT major puts $150 million into a model company, and Bessemer, Khosla and Peak XV stack in behind it, that is the smart money mapping where Indian AI value will accrue. NRIs cannot easily buy Sarvam directly, but they can buy HCLTech — which now offers a sliver of sovereign-AI upside on top of its services business — and they can watch which names this syndicate backs next as a guide to the broader thesis.

There is a return-to-India dimension too. Sarvam, and the cluster of model startups around it, are exactly the kind of company that can lure senior AI researchers home from American labs — with equity, autonomy and the pull of building something nationally significant. For the engineer in Mountain View weighing whether India's AI scene is real or hype, a $1.5 billion valuation led by a Tier-1 strategic and top-tier VCs is a data point that is getting harder to dismiss.

## The risk in the bet

None of this is guaranteed. India's model startups are years behind the frontier labs on raw capability, and "sovereign" can shade into "protected" — a market that exists because of regulation rather than because the product wins on merit. Microsoft partnered with Sarvam back in 2024 on voice AI without disclosing terms; strategic interest is real, but so is the gap between a promising model and a profitable one.

Still, the direction is clear. The Indian IT industry that built its fortune exporting cheap labour is trying to learn how to export intelligence instead. HCLTech's $150 million is a down payment on that pivot — and a signpost for the diaspora capital that wants to ride it."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"OK {art['slug']}")
    except Exception as e:
        print(f"FAIL {art['slug']}: {e}")

#!/usr/bin/env python3
"""Videshi Technology Writer — July 1, 2026 8:00 PM PDT run"""

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


# ─────────────────────────────────────────────────────────
# ARTICLE 1: Apple vs India CCI Antitrust
# ─────────────────────────────────────────────────────────
art1_body = """Apple has accused India's Competition Commission of building its antitrust case on borrowed arguments — and the regulator is not amused.

In a June 25 filing obtained by Reuters, Apple told the Competition Commission of India (CCI) that investigators had "copy-pasted" claims from rival companies rather than conducting independent analysis. The filing, Apple's sharpest legal salvo yet, asks the CCI to throw out its 2024 finding that the company engaged in "abusive conduct" on the iOS platform by mandating use of its own payment system.

The rivals in question include some of India's most prominent fintech companies. PhonePe, the Walmart-backed payments giant used by hundreds of millions of Indians — including the diaspora for cross-border transactions — and Paytm are among the domestic firms that brought complaints alongside Match, the parent company of Tinder.

## The 'Minuscule Player' Defence

Apple's legal strategy hinges on a counterintuitive argument: it is too small to be a monopolist in India. With less than 6 per cent of India's smartphone market — Android dominates the rest — Apple contends it cannot reasonably be accused of abusing a dominant position. The company warned that "forced alterations to Apple's carefully designed App Store could disrupt its integrated business model."

There is a precedent here, and it is not a comforting one for Apple. In 2023, Alphabet's Google mounted a nearly identical defence against CCI charges over its Android ecosystem, arguing that regulatory intervention risked stalling growth. Google lost. It was forced to allow third-party app stores and payment systems on Android devices in India.

Apple also accused the CCI of "blindly" replicating a graphic from a 2024 European Union ruling against the company, even though market conditions in India and Europe differ substantially. The company complained it was never given an opportunity to present oral evidence — a procedural courtesy it says Google was afforded.

## The $38 Billion Question

The financial stakes are staggering. India's antitrust penalty law, which took effect in 2024, allows fines of up to 10 per cent of a company's global turnover over the preceding three years. Apple has estimated its potential exposure at approximately $38 billion if the CCI calculates the penalty on global rather than Indian revenue. The company is separately challenging in a New Delhi court whether the law should apply retroactively to the 2022–2024 period under investigation.

Apple initially refused to supply global financial documents, agreeing to cooperate only in early June and ultimately submitting just its Indian turnover figures. The timing is notable: it filed the copy-pasting accusation on the same day it submitted those financials, June 25.

## Why NRIs Should Watch This

The dispute arrives at a moment when India is more important to Apple than ever. The country is on track to manufacture 26 per cent of the world's iPhones in 2026, up from 6 per cent four years ago. Apple's supply chain has rapidly shifted toward Indian factories operated by Foxconn and Tata Electronics.

For Indian-origin app developers and startup founders — many of whom build for the iOS ecosystem from both sides of the Pacific — the case could reshape how the App Store operates in one of the world's largest digital markets. A CCI victory might force Apple to open its payment rails, giving companies like PhonePe and Razorpay a path into the iOS transaction layer.

Senior CCI officials are scheduled to hold a closed-door hearing with all parties on July 21. If India's track record with Google is any guide, Apple's copy-paste argument may not be enough to avoid real consequences.
"""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Apple Tells India Its Antitrust Case Was 'Copy-Pasted.' The Fine Could Hit $38 Billion.",
    "subheadline": "In its sharpest legal filing yet, Apple accuses the CCI of recycling rivals' complaints rather than conducting independent analysis — but India's regulators have heard that argument before, from Google.",
    "slug": make_slug("apple-cci-antitrust-app-store-copy-pasted-38-billion"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Indian-origin iOS developers and fintech founders on both sides of the Pacific could see fundamental changes to how the App Store operates in India, while PhonePe — widely used by NRIs for cross-border payments — is among the complainants.",
    "tags": ["apple", "cci", "antitrust", "app-store", "india-regulation", "phonpe", "fintech"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/technology/apple-accuses-india-copy-pasting-rivals-claims-antitrust-investigation-2026-06-29/"},
        {"name": "9to5Mac", "url": "https://9to5mac.com/2026/06/29/apple-india-antitrust-case-copy-pasted/"},
        {"name": "MacRumors", "url": "https://www.macrumors.com/2026/06/29/apple-india-antitrust-copy-pasted/"},
        {"name": "Inc42", "url": "https://inc42.com/buzz/apple-alleges-cci-copy-pasted-rivals-claims-in-antitrust-probe/"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5a/Aerial_view_of_Apple_Park_dllu.jpg/1280px-Aerial_view_of_Apple_Park_dllu.jpg",
    "image_caption": "Aerial view of Apple Park in Cupertino, California — headquarters of a company now facing up to $38 billion in antitrust exposure in India",
    "image_attribution": "Wikimedia Commons",
    "body": art1_body.strip()
}


# ─────────────────────────────────────────────────────────
# ARTICLE 2: India's Independent AI Path
# ─────────────────────────────────────────────────────────
art2_body = """While Washington wrestles with how to restrict its most powerful AI models, New Delhi has decided to build its own.

A senior official in India's Ministry of Electronics and Information Technology revealed on Tuesday that the government is funding the development of 20 homegrown AI models under the IndiaAI Mission — and that the strategy deliberately sidesteps the arms race for frontier capability. India's models, the official said, currently offer 60 to 80 per cent of what the most advanced systems from OpenAI, Anthropic, and Google can do. For most commercial applications, that is more than enough.

The timing is pointed. The United States has been tightening controls on frontier AI models, including newer systems from Anthropic such as Fable 5 and Mythos 5, restricting their distribution worldwide. India's response is not to protest these restrictions but to render them less relevant by building alternatives.

## The Builders

India's AI stable is no longer a collection of slide decks. Bengaluru-based Sarvam AI, the IndiaAI Mission's first selectee, has already launched three foundational models with 3-billion, 30-billion, and 105-billion parameters — all accessible in 22 Indian languages and available through voice commands. Co-founder Vivek Raghavan has confirmed these will be fully open-sourced, a decision made after public pressure questioned why taxpayer-subsidised models remained proprietary.

The roster has expanded rapidly. Eleven entities are now selected: the original three startups — Sarvam AI, Gnani.ai (building a 14-billion-parameter voice model), and Gan AI (a 70-billion-parameter text-to-speech system) — plus eight newer picks including Tech Mahindra, Fractal Analytics, and an IIT Bombay consortium called BharatGen that unveiled a 17-billion-parameter model earlier this year. IIT Bombay is reportedly working toward a trillion-parameter model backed by nearly ₹989 crore (approximately $120 million) from the Mission.

The government's compute infrastructure is scaling to match. IndiaAI Mission CEO Abhishek Singh has said the plan includes deploying 38,000 GPUs across the country at subsidised rates, alongside 600 data labs.

## The China Question

One complication the official acknowledged: some Indian companies are adopting Chinese open-source AI models because they are cheaper. The security implications are not lost on the government. "The important thing that we have to realise is, especially companies which are using them, they should be concerned about whether what they use are safe," the official said.

The concern is not abstract. Chinese models trained on data that may include state-directed collection practices pose supply-chain risks for Indian enterprises handling sensitive financial, health, or government data. India's answer is not to ban them outright but to make domestic alternatives competitive enough that the cost argument disappears.

## Budget Backing

The Union Budget 2026-27 allocated ₹1,000 crore ($120 million) specifically for the IndiaAI Mission, covering sovereign foundational models, startup support, compute capacity, and responsible AI frameworks. The AI Governance Guidelines released in November 2025 deliberately avoid a standalone AI law, instead layering principles — trust, fairness, accountability, safety — over existing legal frameworks.

## Why This Matters to the Diaspora

For the Indian-origin engineers who dominate AI research teams at Google DeepMind, OpenAI, Anthropic, and Meta — and who have long wondered whether India could become more than a consumer of AI built elsewhere — this is a credibility test. The models are real. The open-source commitment gives NRI researchers and entrepreneurs a foundation to build on without licensing headaches.

For NRI investors watching India's tech ecosystem, the IndiaAI Mission represents a rare government bet that is producing tangible outputs rather than PowerPoint targets. The question is whether 60-to-80-per-cent capability, combined with linguistic and cultural specificity, can carve out a market that frontier models from San Francisco cannot easily serve.

India's AI strategy, the official emphasised, is about "tangible economic impact" — not chasing valuations. In a year when AI stocks have made and lost billions on hype alone, that may be the most contrarian bet in the sector.
"""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "India Is Building 20 AI Models to Rival ChatGPT. Its Strategy Is to Skip the Arms Race.",
    "subheadline": "As the US restricts its most powerful AI systems, India is funding homegrown open-source models that deliver 60-80% of frontier capability — and betting that's enough for most of the world.",
    "slug": make_slug("india-ai-mission-20-homegrown-models-open-source-frontier"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Indian-origin AI researchers at Google, OpenAI, and Anthropic now have open-source Indian models to build on, while NRI investors get exposure to a government-backed AI ecosystem producing tangible outputs.",
    "tags": ["india-ai", "indiaai-mission", "sarvam-ai", "open-source", "ai-sovereignty", "bharatgen"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/news/india-charts-independent-ai-path-backs-open-source-models-amid-us-restrictions/article71166535.ece"},
        {"name": "Inc42", "url": "https://inc42.com/buzz/indiaai-mission-fractal-tech-mahindra-llm-development/"},
        {"name": "YourStory", "url": "https://yourstory.com/2026/05/inside-india-push-building-indigenous-ai-models"},
        {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/enterprise/sarvam-ai-to-open-source-indiaai-missions-foundational-llms"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/17489163/pexels-photo-17489163.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "A modern data center server unit — the infrastructure India is racing to build for its sovereign AI ambitions",
    "image_attribution": "Pexels",
    "body": art2_body.strip()
}


# ─────────────────────────────────────────────────────────
# ARTICLE 3: AI Jobs — The Counternarrative
# ─────────────────────────────────────────────────────────
art3_body = """The AI jobs debate has a new dataset — and it complicates every side's argument.

A study released this week by Ramp and Revelio Labs, which track enterprise AI spending and workforce records from nearly 22,000 companies respectively, found that companies spending the most aggressively on artificial intelligence are growing their headcount faster than those that are not. "High-intensity adopters" — firms spending an average of $30 per employee per month on AI tools in their first three months of adoption — saw headcount increase by 10.2 per cent.

The growth was not confined to engineering. It showed up across sales, administration, customer service, finance, marketing, and scientist roles. The strongest job growth among heavy AI spenders was in the information sector, which includes software, internet, and media companies.

For Indians on H-1B visas at these very companies, the headline statistic might look reassuring. But the fine print is less comforting.

## The Asterisk

The researchers themselves acknowledge that the data skews heavily toward tech-forward, venture-backed firms — "ones that might have VC-backing and are growing fast anyway, making it difficult to say whether AI is contributing to the hiring or just showing up at companies that are expanding." In other words, AI could be a coincidence at companies that were already winning.

"This paper does not show that AI universally creates jobs," the authors write, "but it does counter claims that AI will lead to broad job losses."

## Meanwhile, the Layoffs Continue

The counterpoint is blunt. Through May 2026, companies announced that close to 90,000 job cuts were explicitly tied to AI, according to industry trackers. By some estimates, up to 15 per cent of US jobs could be eliminated by artificial intelligence over the next five years. The total tech layoff count for 2026 has already crossed 185,000.

Oracle confirmed it cut 21,000 employees — 13 per cent of its workforce — as it rerouted capital toward AI infrastructure. Meta, PayPal, and Cisco have announced workforce reductions while simultaneously increasing AI investment. The pattern is consistent: companies are not reducing overall spending. They are reallocating it away from human workers and toward compute, models, and automation.

For foreign nationals on H-1B visas, a layoff is not merely a career setback. It triggers a 60-day window to find another employer willing to sponsor a visa transfer, or leave the United States. Indians hold the largest share of H-1B visas, with over 730,000 active holders and 550,000 dependants.

## The EB-1A Escape Hatch

A quieter shift is underway among senior Indian tech professionals. Immigration advisors report growing interest in the EB-1A visa category — the "extraordinary ability" green card that does not require employer sponsorship. Unlike H-1B holders, EB-1A recipients control their own immigration status.

The logic is straightforward. If the industry that employs you is restructuring around AI, tying your legal right to remain in the country to a single employer is an increasingly precarious position. Senior engineers, data architects, and product leaders with patents, publications, or significant technical contributions are exploring EB-1A as a way to decouple their immigration status from corporate employment.

## The Shape of the New Workforce

The deeper question is not whether AI creates or destroys jobs, but which jobs it creates and which it destroys. The Ramp/Revelio data suggests that companies integrating AI deeply are building new kinds of roles — but those roles overwhelmingly favour experienced professionals who can manage and correct AI systems, not the entry-level positions that traditionally served as on-ramps for young engineers.

"Companies now want people who understand software well enough to catch the mistakes these AI agents make," one industry observer told Computerworld. "If companies only want people with five years of experience to manage AI agents today, who will have that experience five years from now?"

For Indian tech workers — who form the largest foreign workforce in Silicon Valley and whose career pipelines depend on entry-level H-1B placements — this structural shift may prove more consequential than any single quarter's layoff numbers. The jobs are not disappearing. They are changing shape. The question is whether the immigration system changes shape with them.
"""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "Companies Spending the Most on AI Are Hiring the Fastest. The Full Story Is More Complicated.",
    "subheadline": "A new study of 22,000 companies finds heavy AI adopters grew headcount 10%. But 185,000 tech workers lost jobs this year, and Indians on H-1B are the most exposed population of all.",
    "slug": make_slug("ai-jobs-hiring-ramp-revelio-h1b-indian-tech-workers"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Indians hold the largest share of H-1B visas and are disproportionately affected by AI-driven layoffs, while senior Indian engineers are increasingly pursuing EB-1A green cards to decouple their immigration status from volatile employers.",
    "tags": ["ai-jobs", "h1b", "layoffs", "eb1a", "indian-tech-workers", "silicon-valley"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "TechCrunch", "url": "https://techcrunch.com/2026/06/30/the-ai-jobs-debate-just-got-messier/"},
        {"name": "New York Post", "url": "https://nypost.com/2026/06/30/business/how-silicon-valley-is-preparing-for-the-jobless-ai-future-its-creating/"},
        {"name": "Analytics Insight", "url": "https://www.analyticsinsight.net/artificial-intelligence/the-ai-restructuring-shock-why-elite-tech-talents-are-decoupling-their-immigration-status-through-eb1a-experts-from-big-tech"},
        {"name": "Computerworld", "url": "https://www.computerworld.com/article/3968291/developers-on-h-1b-face-a-tighter-job-market-as-ai-shifts-hiring-priorities.html"}
    ]),
    "score_total": 76,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f3/Artificial_Intelligence_%26_AI_%26_Machine_Learning.jpg/1280px-Artificial_Intelligence_%26_AI_%26_Machine_Learning.jpg",
    "image_caption": "An illustration of artificial intelligence and machine learning — the technology reshaping both hiring and layoff patterns across Silicon Valley",
    "image_attribution": "Wikimedia Commons",
    "body": art3_body.strip()
}


# ─────────────────────────────────────────────────────────
# Insert all articles
# ─────────────────────────────────────────────────────────
articles = [art1, art2, art3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

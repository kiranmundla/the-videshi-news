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

# ---------------------------------------------------------------------------
body_sikka = """The man who once ran Infosys, the second-largest of India's outsourcing giants, has placed a bet against the business that made it. On Wednesday, Vishal Sikka unveiled Hang Ten Systems, a Palo Alto startup that has raised $32 million in seed funding to do enterprise software work with AI agents rather than armies of engineers. The round was led by Mayfield, with a strategic cheque from Aramco Ventures and a clutch of Silicon Valley angels. Yahoo co-founder Jerry Yang has joined the board.

The pitch is blunt. For three decades, firms like TCS, Infosys, Wipro and Cognizant built fortunes by renting out human labour: customizing, integrating and maintaining the software that runs large companies. Bill the client by the head, scale by hiring more heads. Sikka, who ran Infosys from 2014 to 2017 and spent twelve years on SAP's executive board before that, now argues the model is obsolete. Hang Ten promises software "built, changed, and run at a fraction of the cost and time, continuously," using agentic code generation, a reusable skills library and a bench of forward-deployed engineers.

## Context and background

This is Sikka's third act. After leaving Infosys amid a bruising boardroom feud with founder N.R. Narayana Murthy, he founded Vianai Systems, an enterprise-AI outfit he led until April 2026. Hang Ten, he says, is the company he built for the moment AI actually arrived. "AI is upon us all like a massive new wave," he wrote, explaining the surfing metaphor behind the name — to "hang ten" is to walk to the very front of the board and hang all ten toes off the nose. "When there are big waves around, it is time to surf."

The startup is not theoretical. Mayfield's Navin Chaddha says it already has customers a month after launch, including Siemens Gamesa Renewable Energy and the German healthcare group Fresenius.

## Current developments

Hang Ten lands in a market where the incumbents are scrambling in the same direction. Infosys, TCS and Wipro have all signed partnerships with Anthropic and OpenAI and spun up "AI-native" units; Wipro this week posted $10.5 billion in revenue and announced its own. The open question across the industry is whether AI expands the work to be done or simply guts the headcount-based pricing that pays for it. Sikka is wagering on the second outcome — and selling the disruption directly to the enterprises the IT majors serve.

The numbers underline the stakes. India's top five IT firms shed roughly 7,389 jobs in FY2026, reversing modest gains the year before. TCS alone announced plans to cut 12,000 roles. A staffing report pegged active tech-hiring demand at a 28-month low, with entry-level openings down 44% year over year.

## Diaspora impact

For the Indian diaspora, Hang Ten is uncomfortably close to home. The IT services industry is the single largest employer of Indian engineers, in Bengaluru and Hyderabad and on H-1B and L-1 visas in New Jersey, Texas and the Bay Area. A model that builds enterprise software with fewer people is a model that needs fewer of exactly those jobs. The H-1B pipeline that carried a generation of Indian engineers to America was built on the body-shop economics Sikka is now trying to dismantle.

But there is a flip side familiar to anyone who has watched the diaspora's founders. The person doing the dismantling is himself an Indian-origin executive, backed by Indian-American capital, building in Palo Alto. If agentic delivery is the future of enterprise software, the engineers who understand both the legacy systems and the new AI stack — disproportionately Indian — are the ones positioned to ride it. The threat and the opportunity wear the same face.

## What's next

Hang Ten says it is hiring across delivery, engineering, sales and leadership, and plans to expand globally. The harder test is whether agentic delivery holds up on the messy, regulated, decades-old systems that pay the IT majors' bills — and whether clients trust a one-month-old startup with them. If it works, expect the incumbents to copy it fast. If it does not, Sikka will have learned, again, how stubborn the old model is. Either way, the diaspora's engineers are about to find out which side of the wave they are standing on."""

# ---------------------------------------------------------------------------
body_indiaai = """India is about to do something few governments have tried: become an equity shareholder in a private AI startup, paid for not in cash but in graphics chips. Reports this week say New Delhi will take a 1-2% stake in Sarvam AI, the Bengaluru company that became the country's newest AI unicorn this month, in exchange for the compute infrastructure it lent the firm under the IndiaAI Mission.

The mechanism is unusual. Rather than a grant, the government allocated Sarvam access to subsidised GPUs and structured the support as compulsorily convertible debentures — debt that turns into equity. As Sarvam closes its $300 million Series B, those instruments convert, leaving a government body on the cap table of one of India's most-watched startups.

## Context and background

Sarvam was the first company picked, in April 2025, to build a sovereign foundational model under the ₹10,371 crore IndiaAI Mission. The brief: a large language model trained from scratch in India, fluent in Indian languages, run on Indian soil. The mission has since funded Soket AI, Gnani AI and Gan AI on similar terms, and is assembling a 10,000-plus GPU national cluster to wean the country off foreign cloud providers.

This month gave the strategy a private-market stamp of approval. Sarvam raised $234 million in the first close of its Series B at a $1.5 billion valuation, led by HCLTech's $150 million strategic investment for a 10.5% stake, with Bessemer Venture Partners, Khosla Ventures and Peak XV also in. Co-founder Vivek Raghavan says Sarvam's open-source models — a 30-billion and a 105-billion parameter variant — now handle around 10 million API calls a day, with usage tripling in three months.

## Current developments

The equity-for-compute arrangement reframes what the IndiaAI Mission is. It is no longer just a subsidy program; it is a sovereign investor taking upside in the companies it backs. Supporters argue this aligns incentives and gives high-R&D ventures resources they could not otherwise afford. Skeptics worry about the obvious: a government that is simultaneously a regulator, a customer and a shareholder. MeitY officials have signalled they want to shift from upfront grants toward milestone-based funding, with one analyst pushing for a public dashboard tracking adoption of sovereign models.

The timing is pointed. The news broke as Amazon CEO Andy Jassy toured India, and as a Wall Street analyst warned that India's dependence on foreign large language models is like flying a "fighter jet" it does not own. Sovereign AI is suddenly national-security language, not just startup language.

## Diaspora impact

For NRIs, this is a signal worth reading carefully. India is building an AI stack it intends to control — models, compute and now ownership — and it is doing so with a level of state involvement that looks nothing like Silicon Valley's venture model. Diaspora investors weighing Indian AI exposure, whether through HCLTech's stock or future Sarvam-adjacent vehicles, now have to price in a government co-shareholder whose goals are not purely financial.

For the diaspora's technologists, the pull is the other direction. Sarvam was founded by alumni of AI4Bharat at IIT Madras; the sovereign-AI push is creating frontier model research roles in Bengaluru that did not exist two years ago. For an Indian engineer in the Bay Area watching AI layoffs and a tightening H-1B regime, "go home and build the national model" is, for the first time, a credible career, not a consolation prize.

## What's next

The exact size of the government's stake will firm up as Sarvam's round closes the remaining $66 million. The deeper question is governance: how a state shareholder behaves when commercial and political interests diverge, and whether other IndiaAI-backed firms get the same treatment. India has decided it wants to own a piece of its AI future, literally. Whether that accelerates the ecosystem or tangles it in red tape is the experiment now running — and the diaspora has both money and talent riding on the answer."""

# ---------------------------------------------------------------------------
body_adobe = """Shantanu Narayen is spending his final act at Adobe writing cheques. The Indian-born chief executive, who announced earlier this year that he will step down once the company finds an AI-era successor, has just had Adobe agree to acquire Topaz Labs, an AI image- and video-enhancement company, and launch Firefly Foundry, an enterprise tool for building custom, brand-aligned AI models. For a boss on his way out, it is a remarkably forward-leaning send-off.

The Topaz deal, announced Thursday, is the eye-catching one. Topaz Labs has spent two decades building tools that sharpen detail, strip noise, restore old footage and upscale resolution — the unglamorous, essential plumbing of post-production. Its models, Astra for video upscaling and Wonder for image retouching, won the company an Emmy for production technology last year. Adobe already offered some Topaz tools inside Photoshop and Lightroom; now it is buying the whole company. The transaction is expected to close in the second half of 2026, pending regulatory approval.

## Context and background

The logic is defensive and offensive at once. Adobe's franchise — Photoshop, Premiere, Lightroom — is exactly the kind of software the market fears generative AI will hollow out. Narayen's answer has been to flood his own products with AI: Firefly's image, video and vector models, Firefly Services APIs for enterprises, and now an acquisition spree. The prize in Topaz is not just the enhancement models but its Neurostream technology, which runs large AI models locally on consumer hardware instead of the cloud. On-device AI is faster, cheaper and more private — and it lets Adobe avoid paying for every operation in cloud compute.

Narayen's record gives the moves weight. Since taking over in 2007, he steered Adobe through the wrenching 2013 shift from boxed software to Creative Cloud subscriptions, growing revenue from under $1 billion to over $25 billion. His decision to step down, announced in March, was read by analysts as a deliberate handoff before the "messy middle" of the AI transition.

## Current developments

The market is not fully convinced. Adobe's stock has slid to around $193, well off its highs, as investors fret that AI-first annual recurring revenue — which more than tripled year over year — still is not large enough to offset the decline in legacy products like standalone stock imagery. RBC called the Topaz deal a positive for Adobe's technology stack. Bulls argue the selloff is overdone and the company is "priced for too much bad news." The Topaz acquisition and Firefly Foundry are, in part, an attempt to prove the AI transition is real revenue, not just a narrative.

## Diaspora impact

Why should the Indian diaspora care? Two reasons. First, Adobe is one of the large Bay Area employers of Indian engineering talent, and a CEO succession at an Indian-led tech giant is a leadership story the community tracks closely — Narayen sits alongside Sundar Pichai, Satya Nadella and Arvind Krishna in the small club of Indian-origin chiefs running American technology bellwethers. Who replaces him, and whether the board reaches again for that profile, matters.

Second, the diaspora is full of the exact customers these tools target: NRI photographers, filmmakers, YouTubers and small studios who shoot weddings, festivals and family archives across two continents. On-device enhancement that restores a grainy 1990s wedding video or upscales footage shot on a phone in Mumbai is precisely the kind of feature that lands with a globally scattered, image-obsessed community. The flip side is cost: Adobe has said nothing about how Topaz's tools will be priced relative to Creative Cloud subscriptions, and creatives who already pay monthly are wary of another bill.

## What's next

Topaz products will remain available standalone, and CEO Eric Yang will stay on to lead the team. The bigger watch is Adobe's succession: the search committee, led by independent director Frank Calderoni, has not named a successor. Narayen's buying spree is setting the table for whoever inherits the company — loading it with AI assets and a clearer story to tell. For the diaspora, the question is both who gets the corner office and whether the tools that result are worth what Adobe will charge for them."""

# ---------------------------------------------------------------------------
articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "The Man Who Ran Infosys Now Wants AI to Replace the Work That Built It",
        "subheadline": "Vishal Sikka's new Palo Alto startup, Hang Ten, raised $32 million to deliver enterprise software with AI agents instead of armies of engineers — the exact model that employs hundreds of thousands of Indians.",
        "slug": make_slug("vishal-sikka-hang-ten-systems-ai-it-services-infosys-h1b-nri"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Hang Ten's AI-native delivery model directly threatens the IT-services jobs that built the Indian diaspora's H-1B pipeline — yet it is led by an Indian-origin ex-Infosys CEO and backed by Indian-American capital.",
        "tags": ["ai", "indian-tech", "it-services", "vishal-sikka", "h1b", "silicon-valley", "startups"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "TechCrunch", "url": "https://techcrunch.com/2026/06/24/former-infosys-chief-has-a-new-startup-that-wants-to-challenge-the-it-services-world/"},
            {"name": "Inc42", "url": "https://inc42.com/buzz/ex-infosys-ceo-vishal-sikkas-new-ai-venture-bags-32-mn/"},
            {"name": "Analytics Insight", "url": "https://www.analyticsinsight.net/news/vishal-sikkas-enterprise-ai-startup-hang-ten-raises-32-million"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/62/VishalSikkaSapphireOrlando2010.jpg/330px-VishalSikkaSapphireOrlando2010.jpg",
        "image_caption": "Vishal Sikka, former Infosys CEO and founder of Hang Ten Systems, speaking at a SAP event.",
        "image_attribution": "Wikimedia Commons",
        "body": body_sikka
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India's Government Is About to Become a Shareholder in Its Favorite AI Startup. The Bill Comes in GPUs.",
        "subheadline": "New Delhi will take a 1-2% stake in unicorn Sarvam AI in exchange for the compute it lent under the IndiaAI Mission — a sovereign-AI experiment NRI investors and engineers should watch closely.",
        "slug": make_slug("indiaai-mission-government-equity-stake-sarvam-sovereign-ai-nri"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "India is building an AI stack it intends to own outright — models, compute and now equity — reshaping how NRI investors price Indian AI exposure and giving diaspora engineers a credible reason to build the national model back home.",
        "tags": ["ai", "indian-tech", "sarvam-ai", "sovereign-ai", "indiaai-mission", "startups", "nri-investors"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "AInvest", "url": "https://www.ainvest.com/news/indiaai-mission-support-government-acquire-1-2-stake-sarvam-ai-startup-2606/"},
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/info-tech/hcltech-invests-1427-crore-as-a-lead-strategic-investor-in-sarvam-ai/article69695000.ece"},
            {"name": "TechCrunch", "url": "https://techcrunch.com/2026/06/15/sarvam-becomes-indias-newest-ai-unicorn-with-234-million-funding-round-led-by-hcltech/"}
        ]),
        "score_total": 80,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/3/35/Ashwini_Vaishnaw_cropped.jpg",
        "image_caption": "Ashwini Vaishnaw, India's electronics and IT minister, who oversees the IndiaAI Mission.",
        "image_attribution": "Wikimedia Commons",
        "body": body_indiaai
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Adobe's Outgoing Indian-Born CEO Is Spending His Last Act Buying AI",
        "subheadline": "Shantanu Narayen's Adobe snapped up Topaz Labs and launched Firefly Foundry, doubling down on AI even as the boss who built the company prepares to hand it over.",
        "slug": make_slug("adobe-topaz-labs-acquisition-firefly-foundry-shantanu-narayen-nri"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "A CEO succession at one of the few Adobe-scale companies run by an Indian-origin chief is a leadership story the diaspora tracks — and Topaz's on-device enhancement tools land squarely with NRI photographers, filmmakers and creators restoring footage across two continents.",
        "tags": ["ai", "adobe", "shantanu-narayen", "indian-origin-ceo", "firefly", "creative-tech", "m-and-a"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Business Wire", "url": "https://www.businesswire.com/news/home/20260625/en/Adobe-to-Acquire-Topaz-Labs"},
            {"name": "TechCrunch", "url": "https://techcrunch.com/2026/06/25/adobe-acquires-image-and-video-enhancement-tool-maker-topaz-labs/"},
            {"name": "DPReview", "url": "https://www.dpreview.com/news/adobe-upscales-its-ai-capabilities-with-topaz-labs-acquisition"}
        ]),
        "score_total": 74,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/01/Shantanu_Narayen_-_the_CEO_of_Adobe_Inc.jpg/330px-Shantanu_Narayen_-_the_CEO_of_Adobe_Inc.jpg",
        "image_caption": "Shantanu Narayen, chief executive of Adobe, who is steering the company through its AI transition before stepping down.",
        "image_attribution": "Wikimedia Commons",
        "body": body_adobe
    }
]

for art in articles:
    wc = len(art["body"].split())
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']} ({wc} words)")
    except Exception as e:
        print(f"❌ {art['slug']} ({wc} words): {e}")

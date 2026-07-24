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
        "headline": "Meta Just Hired an Indian Founder to Run WhatsApp. The $900 Million Beside It Tells You Why.",
        "subheadline": "Kunal Shah leaves CRED to lead the world's biggest messaging app, as Meta takes a 20% stake in his fintech and bets that India holds the key to WhatsApp's next chapter.",
        "slug": make_slug("kunal-shah-whatsapp-global-head-meta-900-million-cred-stake-nri"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "An Indian founder now runs the app that connects the diaspora to home — and Meta's bet that an India playbook can monetize WhatsApp globally puts NRI engineers and the India-first product thesis at the center of Silicon Valley.",
        "tags": ["whatsapp", "meta", "kunal-shah", "cred", "indian-tech", "fintech", "silicon-valley"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/metas-whatsapp-be-led-by-indian-startup-founder-kunal-shah-2026-06-22/"},
            {"name": "TechCrunch", "url": "https://techcrunch.com/2026/06/22/whatsapp-gets-new-chief-as-meta-taps-indias-cred-founder-kunal-shah/"},
            {"name": "Inc42", "url": "https://inc42.com/buzz/kunal-shah-leaves-cred-for-top-role-at-whatsapp/"},
            {"name": "Mint", "url": "https://www.livemint.com/companies/news/meta-appoints-kunal-shah-as-new-whatsapp-boss-cred-investment.html"}
        ]),
        "score_total": 88,
        "status": "review",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/8/83/Kunal_Shah_in_FreeCharge_T-Shirt_%28cropped%29.jpg",
        "image_caption": "Kunal Shah, founder of CRED, who will become the global head of Meta-owned WhatsApp.",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": """Will Cathcart ran WhatsApp for nearly seven years and grew it to three billion users. On Monday he announced his successor in a post on X: not a Meta lifer, not a Stanford product veteran, but Kunal Shah — the Bengaluru founder of a credit-card-rewards app that most Americans have never heard of.

The choice says less about Shah's résumé than about where Meta thinks WhatsApp's growth now lives.

**A leadership change with a price tag attached**

The announcement did not arrive alone. CRED, the fintech Shah founded in 2018, said it is raising about $900 million (₹8,550 crore) in a Series H round led by Meta. The deal hands Meta a roughly 20% minority stake and values CRED at about $4.5 billion post-money — a markdown from its 2022 peak, but a clean exit ramp for a founder stepping back from operations. Miten Sampat becomes interim CEO; Shah keeps his shares and, by his own account on X, hands Meta "no access to member data."

Strip away the corporate language and the structure is unusual. Meta is simultaneously buying into an Indian company and hiring its founder to run a global product. The two are not legally bundled, but they were announced in the same breath, and that is the point.

**Why India, why now**

WhatsApp's largest market is India, with more than 500 million users — a sixth of its global base. It is also where the app has most aggressively tried, and mostly failed, to become more than a messaging service. WhatsApp Pay has spent years stuck behind PhonePe and Google Pay in the UPI race. Business messaging, the feature Meta most wants to monetize, works best in markets where small merchants already live inside the app. India is the proof-of-concept Meta keeps pointing to.

Chris Cox, Meta's chief product officer, recruited Shah explicitly to find "an entrepreneur from a country where WhatsApp already enjoys deep user adoption," according to the company. Shah, 47, will relocate from Bangalore to Menlo Park. His mandate, per the announcements: advertising, subscriptions, and weaving AI agents into a service that has historically guarded its simplicity.

**What it means for the diaspora**

For Indian Americans, this is more than another desi-makes-good headline, and the WhatsApp angle is personal. WhatsApp is the connective tissue of the diaspora — the family group chat, the way parents in Pune reach children in New Jersey, the channel for everything from wedding logistics to election forwards. The person now deciding how ads, payments, and AI enter that space grew up building for exactly those users.

There is a structural signal too. The most coveted operating job at a FAANG product is going to a founder whose entire track record is in India. That extends a pattern — Pichai at Alphabet, Nadella at Microsoft, Arora at Palo Alto Networks — but flips its logic. Those leaders rose through global corporate ranks. Shah is being hired *because* of his India playbook, not despite it. For the Indian engineer in the Bay Area watching the C-suite, the message is that India-market expertise is now an exportable asset, not a regional specialty.

It is not without risk. Founders who thrive with full control often struggle inside a 70,000-person bureaucracy; the graveyard of acquired-founder hires is well populated. Shah is also stepping into a product whose monetization push has repeatedly bumped against its users' expectation that WhatsApp stay clean and private — a tension Cathcart never fully resolved.

**What to watch**

Three things. First, whether the CRED investment and the hire stay as separated as both sides insist, or whether Meta's payments ambitions quietly pull CRED's expertise into WhatsApp Pay. Second, how fast ads and AI agents arrive in chats, and how Indian and diaspora users react to a more commercial WhatsApp. Third, CRED itself — a founder-dependent company now run by an interim CEO while it eyes an eventual IPO.

For now, the symbolism is hard to miss. The app that carries the diaspora's daily conversations will be run by one of its own. Whether that proves to be sentiment or strategy depends entirely on what shows up in the chat window next."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India Has Its Second AI Unicorn. The Most Telling Part Is Who Wrote the $150 Million Cheque.",
        "subheadline": "Sarvam crossed a $1.5 billion valuation this week — but the headline is HCLTech leading the round, the largest bet an Indian IT giant has made on a homegrown foundation-model company.",
        "slug": make_slug("sarvam-ai-unicorn-hcltech-234-million-sovereign-llm-india-nri"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Sarvam's sovereign-AI thesis — models that read Indian documents and speak Indian languages — gives NRI investors and engineers a homegrown alternative to depending on US labs, days after a US export order briefly cut Indian users off from Anthropic's top models.",
        "tags": ["sarvam", "ai", "hcltech", "indian-tech", "startups", "sovereign-ai", "llm"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Entrepreneur India", "url": "https://www.entrepreneur.com/en-in/news-and-trends/ai-firm-sarvam-turns-unicorn-after-usd-234mn-series-b/"},
            {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/news/sarvam-ai-joins-unicorn-club-hcltech-buys-105"},
            {"name": "Medianama", "url": "https://www.medianama.com/2026/06/223-sarvam-234-million-ai-unicorn/"},
            {"name": "Mint", "url": "https://www.livemint.com/companies/news/indian-deep-tech-funding-surge-sovereign-push.html"}
        ]),
        "score_total": 80,
        "status": "review",
        "image_url": "https://images.pexels.com/photos/17489157/pexels-photo-17489157.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Server racks in a data center, the compute backbone for training large language models.",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": """On June 15, Sarvam announced the first close of its Series B: $234 million of a targeted $300 million round, at a $1.5 billion post-money valuation. That makes the two-year-old Bengaluru company India's newest AI unicorn — only the second after Ola's Krutrim.

The valuation is the headline. The lead investor is the story.

**HCLTech, not a venture fund**

The round was led not by a Silicon Valley growth fund but by HCLTech, which put in $150 million for a 10.46% stake — about ₹1,427 crore. That is the largest single bet an Indian IT services major has placed on a homegrown foundation-model company. Bessemer Venture Partners joined; existing backers Khosla Ventures and Peak XV followed on. Lightspeed, an early investor, sat this one out.

Why does an IT giant lead an AI startup's round? Because the two need each other. HCLTech has enterprise relationships and delivery muscle across banking, insurance, and government; Sarvam has the models. The plan, as both describe it, is to pair Sarvam's AI with HCLTech's reach and sell sovereign-AI systems to enterprises and the Indian state. For an industry watching Anthropic and OpenAI eat into its traditional coding-and-maintenance revenue, owning a piece of the model layer is a hedge.

**What Sarvam actually builds**

Founded in 2023 by Dr. Vivek Raghavan and Dr. Pratyush Kumar, Sarvam is a "full-stack" AI company — it trains models, runs inference infrastructure, and ships enterprise applications. Crucially, its models are built for India's realities rather than translated from English.

The company says its Sarvam 105B model matches or beats larger reasoning models on knowledge and agentic benchmarks, while a 30B version runs on consumer hardware at the edge. Sarvam Vision reads handwriting and Indian-language records, and is being used to digitize over 35 million pages of insurance forms and legacy land records. Its speech models transcribe more than 500,000 hours of audio a month, and its conversational platform now handles two million interactions a day — usage the company says doubled in two months. The new money targets a next frontier model aimed at agentic AI, coding, and cybersecurity.

**The timing is the argument**

Sarvam's raise landed three days after a US export order briefly cut Indian users off from Anthropic's top Claude models — a jolt that turned the abstract "sovereign AI" debate into a concrete one. The lesson many Indian enterprises drew: access is not ownership. A model you rent from a US lab can be switched off by a policy you do not control.

That is precisely the gap Sarvam is selling into. Co-founder Pratyush Kumar frames it bluntly — models that "understand our voices, read our documents, and serve intelligence at a cost every enterprise and government can afford." Sarvam's customers now skew toward high-stakes verticals: banking, gov-tech, defence, insurance. These are exactly the sectors where an Indian buyer is most nervous about depending on foreign infrastructure.

**What it means for the diaspora**

For NRI investors, Sarvam is a clean way to read where Indian deep-tech capital is flowing. The pattern is unmistakable: patient, strategic money — an IT major, not a quick-flip fund — backing infrastructure with non-discretionary demand. Skyroot raised $60 million at a $1.1 billion valuation in May; Sarvam followed in June. Both are research-heavy companies that a year ago would have struggled to find Indian capital willing to wait.

For Indian engineers abroad, there is a subtler pull. Sarvam is hiring for frontier model research in India, and its sovereign-AI pitch is the kind of mission that draws return-to-India talent — the researcher at a US lab who wants to build foundational models for a billion people rather than tune someone else's.

The hard part is still ahead. The frontier labs are racing on the exact terrain Sarvam just raised to enter: agentic coding, where OpenAI's GPT-5.6 and Google's Gemini 3.5 Pro are setting a bar measured in multi-hour task completion, not chatbot quality. A $1.5 billion valuation buys a seat at that table. It does not guarantee Sarvam can close the gap. But for the first time, an Indian company has the capital, the compute path, and a strategic partner to try."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Wipro Just Bet Its Future on Teaching 10,000 Engineers to Use Claude. Their Old Jobs Are the Reason.",
        "subheadline": "India's third-largest IT firm opened a Bengaluru center built entirely around Anthropic's AI — a defensive pivot as automation eats the labour-intensive model that employs hundreds of thousands.",
        "slug": make_slug("wipro-anthropic-claude-coe-bengaluru-10000-engineers-ai-reskill-nri"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Wipro's scramble to reskill 10,000 staff on Claude is the clearest signal yet of how AI is reshaping the H-1B and onshore careers of the Indian engineers who power the $315 billion IT services industry.",
        "tags": ["wipro", "anthropic", "claude", "indian-it", "ai", "reskilling", "h1b"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/indias-wipro-opens-ai-center-anthropics-claude-bengaluru-2026-06-16/"},
            {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/news/wipro-launches-ai-centre-of-excellence-anthropic-claude-train-10000"},
            {"name": "Storyboard18", "url": "https://www.storyboard18.com/how-it-works/wipro-launches-ai-centre-of-excellence-for-anthropics-claude.htm"}
        ]),
        "score_total": 74,
        "status": "review",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/a/a9/S3_and_S4_Building_SJP2_Wipro_Sarjapur_office_Photo_182805.jpg",
        "image_caption": "Wipro's office campus in Bengaluru, where the company opened its Applied AI Centre of Excellence.",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": """Wipro opened a new center at its Bengaluru innovation hub last week. It is not for a client and not for a product. It is built around a single outside company's AI: Anthropic's Claude.

The Applied AI Centre of Excellence, announced June 16, sits inside Wipro's newly formed AI-Native Business and Platforms Unit. Its most concrete commitment is a number — Wipro will train and certify 10,000 frontline delivery staff on Claude models over the next 18 months. CEO Srini Pallia called it "a fundamental shift in how we deliver."

It is also, read plainly, a company racing to retrain its workforce before the work disappears.

**The math the industry is staring at**

India's $315 billion IT services sector was built on a simple model: large teams of engineers writing, testing, and maintaining code for global clients, billed by the hour or the head. That model is exactly what generative AI compresses. When a coding assistant does in minutes what a team of junior engineers did in days, the headcount-driven business starts to wobble.

The market has already priced in the fear. In February, Indian IT firms collectively lost billions in value, partly after Anthropic launched an AI agent tool. Days before Wipro's announcement, the Nifty IT index fell 5.6% in a single session after Accenture flagged a weak outlook — TCS, Infosys, and HCLTech dropped 5% to 8%. The anxiety is not abstract.

**Why Claude, and why a "Centre of Excellence"**

Wipro's response is to stop fighting the tool and start selling it. The CoE will build AI-native platforms and industry-specific solutions for mortgage, healthcare, airlines, manufacturing, and consumer goods. Wipro is also deploying Claude across its own finance, HR, and sales functions — using itself as the test bed for what it plans to sell.

The reskilling pledge is the human core of it. Wipro says it is building a global pool of "Forward Deployed Engineers" trained on Claude — staff who sit inside client environments, combining business-process knowledge with hands-on model expertise. That phrase, borrowed from Anthropic's own playbook, describes a different job than the one most Wipro engineers were hired to do. The pivot is from writing code to orchestrating AI that writes it.

Wipro is not alone. On June 11, TCS announced an alliance with Anthropic to drive enterprise AI scaling. Days later, Wipro followed. The two largest moves in Indian IT this month both run through the same San Francisco lab.

**What it means for the diaspora**

For the Indian engineer — on an H-1B in Dallas, an L-1 in London, or onshore in Bengaluru — this is the most direct signal yet of how AI is reshaping the career. The traditional path was clear: join a services firm, get deployed to a US or UK client site, climb through delivery roles. AI is hollowing out the bottom of that ladder. Entry-level coding and testing work — the rungs that brought many to the diaspora in the first place — is the most automatable.

The reskilling drive is both threat and opportunity. The engineer who becomes a credible "Forward Deployed Engineer" — fluent in Claude, fluent in a client's business — is more valuable, not less. The one who stays in pure code-and-test work is the one most exposed. For the hundreds of thousands of Indians whose visa status is tied to a services-firm job, that distinction is not academic; it determines who keeps the role that keeps the visa.

There is a contradiction worth holding, too. While Wall Street panics about AI gutting IT jobs, Cognizant's Ravi Kumar said this month his firm — which employs 350,000 — is still hiring 20,000 graduates. The industry is shedding one kind of work and hiring for another at the same time. Wipro's 10,000-engineer pledge is a bet on which side of that line its people can move to.

**What to watch**

Whether "certify 10,000 on Claude" becomes a real capability or a press-release number. Whether AI-integration revenue grows fast enough to offset the services compression analysts expect. And whether the diaspora's engineers — the ones whose careers run through these firms — get reskilled or get restructured. The center in Bengaluru is where Wipro is placing its chips. The next few earnings calls will show whether the bet pays."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

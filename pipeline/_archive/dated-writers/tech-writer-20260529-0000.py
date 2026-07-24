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
    """Verify image URL returns valid image content."""
    try:
        r = requests.head(url, timeout=10, allow_redirects=True)
        ct = r.headers.get('Content-Type', '')
        cl = int(r.headers.get('Content-Length', 0))
        if r.status_code == 200 and 'image' in ct and cl > 5000:
            return url
        # Try GET if HEAD doesn't have Content-Length
        r = requests.get(url, timeout=10, stream=True, allow_redirects=True)
        chunk = r.raw.read(6000)
        if r.status_code == 200 and len(chunk) > 5000:
            return url
    except Exception as e:
        print(f"  ⚠️ Image verification failed for {url}: {e}")
    return None

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Google's $15 Billion Vizag Bet Pits AI Ambition Against India's Water Crisis",
        "subheadline": "The search giant's largest data center investment outside the US promises to transform a coastal Andhra Pradesh city — but farmers are being pushed off their land and rights groups warn the water math doesn't add up.",
        "slug": make_slug("google-vizag-data-center-ai-water-crisis"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "For NRIs from Andhra Pradesh, this is personal: your hometown is being remade to train the AI models you use at work in Mountain View. For diaspora investors, Google's India infrastructure bet could reshape the company's cost structure. And for anyone who sends money home, the water-vs-tech tradeoff playing out in Vizag previews a tension that will define India's next decade.",
        "tags": ["google", "data-center", "vizag", "ai-infrastructure", "andhra-pradesh", "water-crisis"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Wall Street Journal", "url": "https://www.wsj.com/tech/ai/big-subsidies-for-google-limited-water-for-locals-the-dilemma-of-ai-in-india-105a770e"},
            {"name": "Reuters", "url": "https://www.reuters.com/legal/litigation/ai-turbocharge-patent-creation-india-tech-hubs-executives-say-2026-05-27/"},
            {"name": "The Machine Maker", "url": "https://www.themachinemaker.com/news/airtel-google-ai-data-centre-visakhapatnam"},
            {"name": "Morgan Stanley Research", "url": "https://www.morganstanley.com/ideas/india-data-center-market-outlook"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/5480781/pexels-photo-5480781.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A modern data center server room — Google's Vizag facility will be India's first hub for training large-scale AI models.",
        "body": """In Visakhapatnam, a coastal city in Andhra Pradesh that most Indians call Vizag, a 42-year-old farmer named Pyla Kondamma is giving up the mango and cashew groves her family has tended for half a century. The government is compensating her — roughly $83,000 — but she is not celebrating. "How can we be happy about Google coming?" she told the Wall Street Journal. "We'll all be scattered."

What Google is building in Vizag is enormous. A $15 billion AI data center hub, developed in partnership with Adani Group and Bharti Airtel, spanning 600 acres across three sites — the equivalent of 454 football fields. When fully operational, it will consume electricity equal to what six million Indians use in a year. It will be Google's largest data center investment outside the United States, and India's first facility purpose-built for training and running large-scale AI models for a Western tech giant.

## The subsidy math

The Andhra Pradesh state government is not being shy about what it is offering. According to state planning documents reviewed by the WSJ, incentives include a 25% discount on water costs for a decade, a 25% land discount, reimbursement of electricity infrastructure costs, state tax waivers, and power price discounts. The total package: roughly $2.3 billion over 20 years.

For a city where some neighborhoods receive less than an hour of tap water daily, the water subsidy has drawn particular scrutiny. The World Resources Institute classifies Visakhapatnam as under "extremely high" water stress. Rights groups question whether the government can supply enough water to cool the data centers while keeping taps running for residents.

Google says the initial phase will use air cooling, which requires far less water than evaporative systems. The company has also pledged to replenish more freshwater than it consumes globally by 2030 — through lake restoration, wetland rehabilitation, and agricultural technology improvements. In Vizag specifically, it plans clean-drinking-water systems near the data centers, GPS navigation for local fishermen, and AI training for students.

## India's AI infrastructure race

The Vizag project doesn't exist in isolation. According to Morgan Stanley, India's data center capacity is forecast to grow fivefold to roughly 10 gigawatts over the next five years. Microsoft, Amazon, and Cognizant have collectively committed over $50 billion to Indian AI and cloud infrastructure, following Prime Minister Modi's meetings with tech CEOs.

The urgency is partly defensive. India's $64.6 billion global capability center industry — which hit revenue projections four years ahead of schedule, according to Nasscom — faces an existential question from AI. If AI can write code, analyze data, and handle customer service, what role do GCCs play next? By hosting the infrastructure that trains AI models, India is trying to remain indispensable even as the technology threatens some of the jobs that built its tech sector.

Anthropic, maker of the Claude chatbot, opened a Bengaluru office in February after discovering India was its second-largest global market. OpenAI's ChatGPT claims 100 million weekly users in the country. India is not just building AI infrastructure — it is consuming AI at a pace that surprises even Silicon Valley.

## What NRIs should watch

For diaspora professionals, the Vizag story is a microcosm of a larger tension. The data centers will create high-value jobs — an estimated 50,000 by 2028 — and catalyze an ecosystem that could turn Vizag into another Hyderabad or Bengaluru. Infosys and Cognizant have already announced plans for new offices there.

But the displacement is real. Farmers with no legal recourse are being moved off government-owned land they have cultivated for decades. "The government can evict you from what you thought was yours for so long," one farmer told the WSJ. "There are no legal rights to fight over it."

V.S. Krishna of the India-based Human Rights Forum called the project "a very, very troubling convergence of corporate power and full-state patronage." Offering billions in subsidies to one of the world's most profitable companies, he argued, is "very problematic."

For NRIs watching from abroad, the question is uncomfortable but unavoidable: the AI tools you use every day at your desks in Sunnyvale and Jersey City are increasingly being powered by infrastructure that displaces communities back home. Whether that tradeoff is worth it depends on whether the promised economic transformation actually reaches the people of Vizag — and not just the server racks."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India Is Claude's Second-Biggest Market. Every AI Lab Is Racing to Get In.",
        "subheadline": "Anthropic's Bengaluru office, an Indian-origin co-creator behind the $2.5 billion Claude Code product, and 100 million weekly ChatGPT users — India has become the most contested AI consumer market outside America.",
        "slug": make_slug("india-claude-second-biggest-market-anthropic-ai-labs"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Indian-origin engineers like Sid Bidasaria are building the AI tools that NRIs use daily — and the companies they work for are now racing to sell those tools back to India. For diaspora tech workers, this creates career opportunities on both sides of the Pacific. For NRI investors, India's emergence as a top-two AI consumer market signals a demand curve that hasn't been priced in.",
        "tags": ["anthropic", "claude", "ai-market", "india", "openai", "bengaluru", "indian-tech-leaders"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Inshorts / Moneycontrol", "url": "https://inshorts.com/en/news/anthropic-to-expand-claude-beyond-coding--indian-origin-co-creator-1779519218735"},
            {"name": "Storyboard18", "url": "https://www.storyboard18.com/technology/anthropic-opens-india-office-in-bengaluru-its-second-in-asia-68923.htm"},
            {"name": "Built In", "url": "https://builtin.com/articles/anthropic-bengaluru-office"},
            {"name": "Wall Street Journal", "url": "https://www.wsj.com/tech/ai/big-subsidies-for-google-limited-water-for-locals-the-dilemma-of-ai-in-india-105a770e"}
        ]),
        "score_total": 78,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/14314636/pexels-photo-14314636.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "India has quietly become the world's second-largest market for AI coding tools, catching Silicon Valley's attention.",
        "body": """When Anthropic, the AI safety company valued at $380 billion, announced that India ranked as the second-largest global market for Claude Code — its AI coding assistant — it confirmed something that Silicon Valley had been whispering about for months. India is not just where AI gets built. It is where AI gets used.

The numbers are striking. Claude Code, which crossed $2.5 billion in annualized revenue in February 2026, has found its most voracious users outside America in a country where the average software developer earns a fraction of their Bay Area counterpart. OpenAI's ChatGPT claims 100 million weekly users in India. Google's Gemini is embedded across the country's Android-dominant smartphone market. The battle for India's AI consumers has become one of the most consequential in the industry.

## The Indian-origin architects

Sid Bidasaria, one of Claude Code's co-creators and an Indian-origin engineer at Anthropic, told Moneycontrol in late May that the company is expanding beyond coding-focused tools into broader professional and knowledge-worker applications. Coding, he explained, was the first target because "results were easier to verify." Bidasaria is part of a growing cohort of Indian-origin leaders at Anthropic, a pattern that mirrors the broader Indian takeover of Silicon Valley's executive suites.

Anthropic opened its first India office in Bengaluru in February 2026 — its second in Asia after Tokyo — and appointed Irina Ghose as India Managing Director. The company doubled its India run rate since October 2025 and is hiring local engineers to serve enterprise customers, digital-native startups, and organizations like Air India and Cognizant.

The Bengaluru push includes improving Claude's training data across 10 Indian languages, through partnerships with Karya (a data-annotation nonprofit that pays rural workers above-market wages) and Digital Green (which works with smallholder farmers). If successful, this would give Claude a meaningful edge in a market where English is the professional lingua franca but not the first language for most users.

## The consumer market nobody expected

India's emergence as a top AI consumer market defies the conventional wisdom that AI products need wealthy, enterprise-heavy markets to scale. Indian developers and knowledge workers have adopted AI coding assistants at rates that rival — and in some categories exceed — their peers in Europe and Japan.

Several forces explain the surge. India's 27-million-strong developer workforce is the second-largest globally, behind only the United States. The cost of AI subscriptions, while not trivial in Indian rupee terms, is low relative to the productivity gains for a freelancer or startup founder. And India's coding culture — shaped by decades of IT services work and a hyper-competitive engineering education system — produces users who know exactly how to extract value from a code-generation tool.

The competitive dynamics are intensifying. Google, which has the deepest existing footprint through Android and Search, is building a $15 billion AI data center hub in Visakhapatnam. OpenAI has been aggressively pricing ChatGPT for the Indian market. Meta's open-source Llama models have found enthusiastic adoption among Indian startups building on tight budgets. And homegrown players like Sarvam AI and Ola's Krutrim are racing to build India-specific models that understand local context.

## What this means for NRIs

For Indian-origin engineers in Silicon Valley, the India consumer market creates a rare dual opportunity. The AI labs where they work are desperate for people who understand Indian users, Indian languages, and Indian enterprise workflows. Product roles, go-to-market positions, and partnerships teams focused on India are expanding at every major AI company.

For NRI investors, the signal is equally clear. India's AI consumption is growing faster than its AI production, meaning the companies best positioned are those building the infrastructure (cloud providers, chip makers) and the applications (enterprise AI, developer tools) that serve this demand. Anthropic's India-second revelation suggests the demand curve for AI tools in India hasn't been fully priced into most market analyses.

And for the millions of NRIs who use these tools daily at their desks in America — Claude for code reviews, ChatGPT for research, Gemini for email — there is a satisfying irony. The tools were built, in many cases, by Indian-origin engineers. And now the fastest-growing market for those tools is back home."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "TCS Shed 25,000 Jobs in Nine Months. It Also Doubled Its Fresher Intake.",
        "subheadline": "India's largest IT employer is hollowing out its middle while flooding the bottom with AI-trained graduates — a workforce pyramid inversion that signals what's coming for the entire outsourcing industry.",
        "slug": make_slug("tcs-25000-job-cuts-fresher-hiring-ai-pyramid"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "For NRIs with family at TCS, Infosys, or Wipro — and that's a lot of NRIs — these numbers are personal. For H-1B holders at Indian IT firms in the US, the restructuring raises questions about which onsite roles survive. And for diaspora investors, TCS's AI pivot is a test case for whether India's IT giants can transform without destroying their own value proposition.",
        "tags": ["tcs", "indian-it-services", "ai-layoffs", "fresher-hiring", "workforce-restructuring", "outsourcing"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Storyboard18", "url": "https://www.storyboard18.com/technology/tcs-headcount-falls-by-over-11000-in-q3fy26-doubles-fresher-hiring-67234.htm"},
            {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com/info-tech/tcs-headcount-plummets-in-fy26/article69179234.ece"},
            {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/technology/tcs-reduces-over-11000-staff-in-q3-as-restructuring-continues"},
            {"name": "Reuters", "url": "https://www.reuters.com/world/india/global-firms-bring-more-work-in-house-india-hubs-ai-boost-2026-05-26/"}
        ]),
        "score_total": 85,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/7988079/pexels-photo-7988079.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Indian IT services companies are restructuring their workforces around AI, cutting experienced staff while doubling entry-level hiring.",
        "body": """Tata Consultancy Services, India's largest IT employer, shed 25,816 employees in the first three quarters of FY26. In the same period, it doubled its fresh graduate intake and trained over 217,000 associates in advanced AI skills. These two facts are not contradictory. They are the strategy.

TCS is executing what amounts to a workforce pyramid inversion. The company is cutting experienced mid-level and senior staff — the people who cost the most and whose skills overlap most with what AI can now do — while flooding the bottom of the organization with cheaper, AI-native graduates who grew up treating large language models as a default tool rather than a novelty.

The Q3 numbers tell the story in sharp relief. Headcount fell by 11,151 in the quarter alone, bringing the total workforce to 582,163. Revenue rose 4.9% year-on-year to ₹67,087 crore. Net profit dropped 13.9% to ₹10,657 crore, weighed down by ₹2,128 crore in exceptional charges tied to India's new labor codes. But the AI business — the metric TCS wants investors to focus on — hit $1.8 billion in annualized revenue, up 17.3% quarter-on-quarter in constant currency terms.

## The middle is being eaten

The restructuring is not subtle, and it is not painless. Employee unions have demanded an independent audit of TCS's exit practices, alleging that some departures are being classified as "voluntary" when they are effectively forced. The National IT Employees Senate (NITES), which tracks layoffs across the sector, has flagged concerns about labor law compliance.

TCS's HR head, Sudeep Kunnumal, pushed back, saying the company remains on track to hire 40,000 freshers annually and that the headcount decline reflects "restructuring" rather than layoffs. CEO K. Krithivasan has framed the shift as making TCS "future-ready" — a phrase that has become the IT services industry's preferred euphemism for replacing humans with algorithms.

The pattern is not unique to TCS. HCL Tech reduced headcount in Q3. Infosys added a modest 5,043 employees but raised its revenue guidance, suggesting it too is learning to grow without proportional hiring. The entire Indian IT services sector — which employs over five million people — is converging on the same realization: AI makes it possible to deliver more work with fewer people, and the market rewards companies that act on that insight.

## The insourcing threat

Compounding the pressure is a structural shift in how global companies use their India operations. At a Reuters summit in Bengaluru last week, executives from Daimler Truck, Target, IBM, Novo Nordisk, and Workday described a clear trend: they are bringing more work in-house at their Indian global capability centers, reducing reliance on outsourcing partners like TCS, Infosys, and Wipro.

"We are able to do significantly more with the same set of people that we have because of the power that AI brings in," said Pratik Nath, managing director of Epsilon India.

This is the double bind for Indian IT services. AI makes their own operations more efficient — hence the growing AI revenue line — but it also makes their clients more self-sufficient. When a Kimberly-Clark can cut content creation from 24 days to two hours using an AI platform built by its own India team, the business case for outsourcing that work to TCS evaporates.

## The NRI calculus

For the Indian diaspora, TCS's restructuring is more than a business story. It is a family story. Millions of NRIs have siblings, cousins, parents, or classmates who work — or worked — at TCS, Infosys, Wipro, or one of the other IT services giants that powered India's middle-class boom over the past two decades.

The 25,000 jobs shed at TCS in nine months are disproportionately held by people in their thirties and forties — professionals with mortgages, children in school, and career expectations built on the assumption that IT services employment was stable if not spectacular. For H-1B holders at Indian IT firms in the United States, the restructuring raises a different anxiety: which onsite roles survive when the offshore model itself is being rearchitected around AI?

For diaspora investors — and TCS is among the most widely held Indian stocks globally — the question is whether the AI pivot produces sustainable margin expansion or merely delays a reckoning with shrinking outsourcing demand. At $1.8 billion in annualized AI revenue, TCS is demonstrating that it can sell AI services. Whether it can do so fast enough to offset the erosion of its traditional business remains the trillion-rupee question.

The 40,000 freshers TCS plans to hire this year will enter a company that looks fundamentally different from the one their predecessors joined. They will be expected to work alongside AI, not instead of it. The mid-level managers who once supervised their work are increasingly unnecessary. The pyramid that defined Indian IT for a generation — a vast base of junior engineers, a thick middle of project managers, a thin top of client partners — is being reshaped into something sharper and more precarious."""
    },
]

# Verify images
for art in articles:
    img = verify_image(art["image_url"])
    if not img:
        print(f"⚠️ Image failed for {art['slug']}, proceeding without")
        art["image_url"] = None

# Publish
for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

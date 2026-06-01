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

def validate_image(url):
    try:
        r = requests.head(url, timeout=10, allow_redirects=True)
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        return r.status_code == 200 and "image" in ct and cl > 5000
    except:
        return False

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Apple Just Handed Its Most Important Product to Sundar Pichai's AI. WWDC Will Show Whether That Was Genius or Surrender.",
        "subheadline": "Siri 2.0, rebuilt on Google's Gemini, debuts at Tim Cook's final WWDC on June 8. For thousands of Indian engineers at Apple and millions of Indian iOS developers, the stakes couldn't be higher.",
        "slug": make_slug("apple-wwdc-siri-gemini-pichai-tim-cook-indian-developers"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Thousands of Indian engineers at Apple face a shifting internal landscape as AI restructuring accelerates. Meanwhile, India's 6.5 million registered iOS developers must prepare for a fundamentally new Siri API. And the delicious irony: the assistant that defines the iPhone now runs on AI built by Chennai-born Sundar Pichai's company.",
        "tags": ["apple", "wwdc", "siri", "google-gemini", "sundar-pichai", "tim-cook", "ios-27", "indian-developers"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Barron's", "url": "https://www.barrons.com/articles/apple-stock-siri-wwdc-2026"},
            {"name": "Livemint", "url": "https://www.livemint.com/technology/tech-news/ios-27-release-date"},
            {"name": "NeuralWired", "url": "https://neuralwired.com/apple-intelligence-2026/"},
            {"name": "Inc.", "url": "https://www.inc.com/jason-aten/i-shipped-my-first-iphone-app-this-year-heres-what-i-most-hope-to-see-at-wwdc.html"},
            {"name": "Tom's Guide", "url": "https://www.tomsguide.com/news/wwdc-2026"}
        ]),
        "score_total": 85,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/12968298/pexels-photo-12968298.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "body": """When Apple's Worldwide Developers Conference opens on June 8 in Cupertino, Tim Cook will walk onstage for the last time as CEO. The moment would be significant on its own. But what makes WWDC 2026 genuinely consequential — for Apple, for Google, and for the tens of thousands of Indian professionals whose careers orbit both companies — is what powers the star of the show.

Siri 2.0 runs on Google's Gemini.

## The Deal That Rewrote the Rules

The Apple-Google AI partnership, announced in January 2026, was the kind of deal that would have been unthinkable three years ago. Bloomberg estimates the Gemini licence costs Apple roughly $1 billion per year. Other reports put it closer to $10 billion annually. Apple hasn't confirmed either figure.

What is confirmed: the Gemini model backing the new Siri runs under Apple's internal designation "Foundation Models v10" and uses a 1.2-trillion-parameter architecture — a dramatic leap from the 3-billion-parameter on-device model. Apple says user data stays on its own Private Cloud Compute servers, with Gemini's model weights hosted by Apple, not Google.

But Google Cloud CEO Thomas Kurian called Google Apple's "preferred cloud provider" at Google Cloud Next 2026. That phrasing — used by Google executives, not Apple — should make every enterprise IT team take note.

## What Siri 2.0 Actually Does

Leaked iOS 27 screenshots from Bloomberg's Mark Gurman show a standalone Siri app with a dark interface, a "Search or Ask" feature triggered from the Dynamic Island, and deep integration into Camera and Photos. Citi analyst Atif Malik predicts Siri will "handle multi-step requests, understand personal data, analyse on-screen content, generate emails using both web and device context, and complete actions across apps."

In plain English: Siri becomes an AI agent, not just a voice command parser. Apple's App Intents framework will let developers expose actions to Siri, enabling cross-app workflows that previously required opening each app individually. The developer beta drops immediately after the keynote.

## The Indian Engineer Equation

Apple employs thousands of Indian-origin engineers across its Silicon Valley campuses, particularly in machine learning, services, and chip design. The pivot to Gemini represents a strategic shift that could reshape internal teams. John Giannandrea, Apple's former AI chief, departed almost exactly when the Gemini deal was announced. The message to Apple's in-house AI talent — including a significant Indian contingent — is uncomfortable: two years and billions of dollars of internal development couldn't ship a working Siri upgrade.

Meanwhile, India has approximately 6.5 million registered Apple developers. For this community, iOS 27 represents both opportunity and disruption. The new App Intents API means apps that don't integrate with Siri's agent capabilities risk irrelevance. Apps that do could see dramatically higher engagement.

## The Pichai Paradox

There's a particular irony here that won't be lost on anyone in the Indian tech community. Siri — the product that arguably defined the modern smartphone assistant, the product Apple has guarded more jealously than almost any other — now runs on AI built under the leadership of Sundar Pichai, born in Madurai, educated at IIT Kharagpur.

Google gets a billion-dollar-plus annual revenue stream and validation that its AI is best-in-class. Apple gets an assistant that actually works. Indian professionals at both companies find themselves on the same team for the first time.

## Hardware and Leadership Transitions

WWDC will also preview M5-powered Mac Mini and Mac Studio, a potential "MacBook Ultra" with an OLED touchscreen on TSMC's 2nm process, and — most dramatically — Apple's first foldable iPhone, estimated at $2,000–$2,500. iOS 27 will drop support for iPhone 11 and earlier.

And then there's the leadership question. Tim Cook is expected to hand the CEO role to hardware chief John Ternus by September. For a company that has never had a non-white CEO despite its diverse engineering workforce, the transition invites familiar questions about representation at the very top.

## What to Watch

The developer beta on June 8 will be the first real test. If App Intents works as promised, WWDC 2026 becomes the most important developer event since the iPhone SDK launch in 2008. If Siri still stumbles on basic queries — well, Apple just spent a billion dollars to find out that some problems can't be solved by writing a cheque.

For the Indian tech professional, whether you're building iOS apps in Bengaluru, managing ML infrastructure in Cupertino, or investing in AAPL from Mumbai, the next seven days will tell you a great deal about where your next year is headed."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Meta Filed WARN Notices for 3,270 Bay Area Jobs Last Week. For Indian H-1B Workers, the Clock Starts Now.",
        "subheadline": "Mark Zuckerberg's 10% workforce reduction hits Menlo Park and Sunnyvale hardest. With a July 22 separation date and a 60-day grace period, thousands of visa holders face an impossible timeline.",
        "slug": make_slug("meta-warn-3270-bay-area-layoffs-h1b-july"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Meta is one of the largest H-1B employers in the Bay Area. Indian nationals hold a disproportionate share of these visas. The 60-day grace period after a July 22 separation date means affected H-1B workers must secure a new sponsored position by mid-September — peak vacation season, worst possible timing for job hunting in tech.",
        "tags": ["meta", "layoffs", "h1b", "bay-area", "warn-act", "silicon-valley", "immigration"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "New York Post", "url": "https://nypost.com/2026/05/31/business/silicon-valley-giant-meta-slashes-even-more-jobs-as-ai-boom-sparks-bloodbath/"},
            {"name": "Yahoo/AInvest", "url": "https://ainvest.com/news/mass-meta-layoffs-impact-over-3k-bay-area-workers"},
            {"name": "WARN Firehose (California)", "url": "https://warnfirehose.com/california"},
            {"name": "NBot WARN Monitor", "url": "https://nbot.ai"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/5499551/pexels-photo-5499551.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "body": """On May 22, Meta filed six separate WARN Act notices with California's Employment Development Department. The numbers, spread across multiple filings in what appears to be a deliberate structural choice, add up to 3,270 positions in the Bay Area alone: 2,212 at the Menlo Park headquarters, 313 at a separate Menlo Park facility, 252 in San Francisco, 338 in another Menlo Park filing, 81 in Fremont, and 74 in Los Angeles County.

The separation date for all filings: July 22, 2026.

## The Scale of the Cut

These Bay Area numbers are part of a broader global reduction of approximately 8,000 positions — nearly 10% of Meta's workforce. Additional WARN filings show 1,395 positions eliminated in Washington state across Bellevue, Seattle, and Redmond offices. The cuts are concentrated in engineering, particularly teams building business-facing AI products integrated across Facebook, Instagram, and WhatsApp.

"The changes we are implementing vary by team and include layoffs, open role closures, and moving thousands of employees to business critical priorities across the company," Meta spokesperson Tracy Clayton told reporters.

Mark Zuckerberg was more blunt in a May 20 memo to staff, first reported by The New York Times: "AI is the most consequential technology of our lifetimes. The companies that lead the way will define the next generation." He added that Meta would "reinvest the savings to support the growth of wearables" and AI tooling, with capital expenditures between $115 billion and $135 billion planned for AI infrastructure, including the Meta Superintelligence Labs.

## The H-1B Crisis Within the Crisis

Here is where the numbers become personal for the Indian diaspora.

Meta is among the top H-1B visa sponsors in the United States. Indian nationals receive approximately 72% of all H-1B visas issued annually. While Meta doesn't disclose the visa status of affected employees, the statistical probability is stark: a significant portion of the 3,270 Bay Area workers losing their jobs hold H-1B visas.

Under current immigration rules, H-1B holders who lose employment have a 60-day grace period to find a new sponsored position, transfer their visa, or change status. A July 22 separation date means the clock expires around September 20 — the tail end of summer, when hiring slows and decision-makers are on vacation.

Meta has said it provides specific layoff notices to H-1B employees with information about the grace period and options for internal transfer or relocation. But "options for internal transfer" ring hollow when 10% of the company is being shown the door simultaneously.

## The Broader Bloodbath

Meta's layoffs land in an already devastated job market. Tech layoffs in 2026 have now exceeded 178,000 year-to-date, according to WARN tracking data. California alone has seen 637 WARN notices affecting 38,331 workers this year, with Meta accounting for the single largest filing.

The same week Meta filed its notices, Intuit and its subsidiary Credit Karma filed for 1,027 positions across California and Nevada — despite reporting $631 million in revenue growth. Snap cut 247 in Santa Monica. NetApp eliminated 77 in the Bay Area. Webflow conducted abrupt layoffs that triggered potential WARN Act violation investigations.

A class-action law firm is already investigating Meta's WARN filings for potential violations — specifically whether adequate notice was provided given the timeline between the April announcement and the May filings.

## The AI Paradox

The cruel irony is that many of the engineers being laid off were building the very AI tools that are now cited as the reason for their termination. NBot's analysis of 2026 layoffs found that 99% of CEOs plan AI-related workforce reductions, while only 32% report having real AI capability deployed. That 67-point gap suggests many layoffs are budget-driven cuts dressed in AI language.

At Meta, the dynamic is more honest but no less brutal. The company genuinely is pivoting its engineering resources toward AI infrastructure, autonomous agents, and physical AI (wearables, AR glasses). The positions being eliminated — mid-level engineers on mature products, business tools teams, legacy platform maintenance — represent the old Meta. The new Meta wants fewer, more senior engineers working on frontier AI.

## What NRI Workers Should Do Right Now

For Indian-origin workers at Meta who received WARN notices, the timeline is compressed but not hopeless:

Activate your network immediately. The Indian tech diaspora in the Bay Area is one of the most connected professional communities in the world. LinkedIn messages from laid-off Meta engineers are already circulating with "open to work" flags. Former colleagues who moved to other companies in the last round of Meta layoffs are a direct pipeline.

Consult an immigration attorney before your separation date, not after. The 60-day grace period is a hard deadline, but there are strategies — filing for H-1B transfer, switching to B-1/B-2 status, exploring O-1 extraordinary ability petitions — that require preparation before the clock starts.

Consider whether this is the moment to explore opportunities in India. Bengaluru and Hyderabad are experiencing a hiring boom in AI roles, and the compensation gap for senior engineers has narrowed considerably. Several former Meta engineers from the 2023 layoff rounds are now in leadership positions at Indian unicorns.

The severance package — 16 weeks of base pay plus two additional weeks per year of employment — provides a financial cushion. Use it wisely. The July 22 date is not a surprise. The only surprise would be not being ready for it."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Jensen Huang Wants NVIDIA to Build the Brains for Every Humanoid Robot on Earth. The Geopolitics Are Already Messy.",
        "subheadline": "At Computex 2026, NVIDIA announced partnerships with Chinese robotics firm Unitree and unnamed US, European, and South Korean companies. Indian robotics researchers are watching closely — and Indian IT firms should be.",
        "slug": make_slug("nvidia-humanoid-robots-unitree-computex-india-ai"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Indian researchers at Stanford and UCSD are among the first users of NVIDIA-powered humanoid robots. India's deep tech ecosystem — from TCS's robotics practice to startups like Addverb and Miko — stands to benefit from commoditised robot hardware. And Indian-origin engineers are heavily represented in NVIDIA's physical AI division.",
        "tags": ["nvidia", "humanoid-robots", "computex", "unitree", "physical-ai", "india-robotics", "jensen-huang"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/nvidia-work-with-us-european-humanoid-robot-makers/"},
            {"name": "Seeking Alpha", "url": "https://seekingalpha.com/news/nvidia-highlights-agentic-physical-ai-computex"},
            {"name": "MarketWatch", "url": "https://www.marketwatch.com/story/intel-and-amd-shares-fall-as-nvidia-sets-its-sights-on-a-new-market"},
            {"name": "Investor's Business Daily", "url": "https://www.investors.com/news/technology/nvidia-stock-rtx-spark-pc-chip/"}
        ]),
        "score_total": 72,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/8566470/pexels-photo-8566470.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "body": """Jensen Huang's Computex 2026 keynote ran nearly three hours. He unveiled the RTX Spark PC chip, announced the Vera Rubin data centre GPU entering full production, and rattled competitors across three continents. But the announcement that may matter most in five years was the quietest: NVIDIA is building the standardised computing brain for humanoid robots.

And the geopolitics of that decision are already complicated.

## The Unitree Partnership

NVIDIA announced it is working with Unitree, China's leading humanoid robotics company, to create a standardised version of the H2 robot for academic researchers. The division of labour is deliberate: Unitree provides the body, Singapore-headquartered Sharpa provides the hands, and NVIDIA provides the computing platform — effectively the brain.

Researchers at Stanford University and the University of California San Diego are among the first institutions planning to use the machines. The robots will run on NVIDIA's Isaac and Cosmos platforms for physical AI simulation and training.

But there's a catch. US lawmakers have alleged that Unitree has extensive ties to the Chinese government and military. A bill has been introduced that would ban researchers receiving US government funding from using Unitree's robots. The dancing robots that were the centrepiece of China's Spring Festival gala earlier this year now sit at the intersection of academic research and national security policy.

## Hedging the Bet

NVIDIA executives told Reuters — on condition of anonymity — that the company plans to replicate the Unitree model with robotics firms in the US, South Korea, and Europe. They didn't name the partners. The strategy is transparent: NVIDIA wants to be the brain regardless of whose body the robot wears.

The cybersecurity angle is notable. All software updates for the robot's subsystems must flow through NVIDIA's chip, where code can be checked for authenticity. NVIDIA is positioning itself not just as a compute provider but as a trust layer — the entity that verifies what the robot's software is actually doing.

For a $5 trillion company, this is a new kind of moat. GPU dominance won data centres. The robotics play is about owning the intelligence layer of physical machines — factories, warehouses, hospitals, eventually homes.

## The Indian Angle: Research, Talent, and Industrial Opportunity

Indian researchers are already embedded in this ecosystem. Stanford's robotics labs have a significant Indian-origin presence, as does UCSD's Contextual Robotics Institute. The first wave of NVIDIA-powered humanoid robot research will, in part, be shaped by Indian-origin scientists.

At NVIDIA itself, the physical AI division — which builds the Isaac simulation platform, the Cosmos world model, and the Jetson edge computing hardware — employs a substantial number of Indian-origin engineers. The company's Pune and Bengaluru offices contribute to GPU software stack development that feeds directly into robotics applications.

But the bigger opportunity is industrial. India's robotics market, while still nascent compared to China, Japan, or South Korea, is growing rapidly. Addverb Technologies, backed by the Ambani family's Reliance Industries, builds autonomous mobile robots for warehouse logistics. Miko builds companion robots. TCS and Wipro both have robotics process automation practices that are expanding into physical robotics.

If NVIDIA succeeds in commoditising the robot brain — making it a standard component like an Intel chip in a PC — Indian manufacturers could focus on mechanical design, application software, and market-specific customisation. The parallel to the 1990s PC industry, where Taiwanese ODMs built hardware around Intel/Microsoft platforms while Indian IT firms built the software layer, is hard to miss.

## The Vera Rubin Update

The robotics announcement came alongside confirmation that NVIDIA's next-generation Vera Rubin data centre GPU platform is entering "full production," with first systems shipping this autumn. Early customers include Anthropic, OpenAI, SpaceX's xAI, Dell, Oracle, and CoreWeave.

For India's nascent AI infrastructure buildout — including Reliance's Jio AI cloud and Tata's planned AI supercomputing centres — Vera Rubin represents the next generation of hardware they'll need to procure. The platform's announced 1.8x improvement in task completion speed for AI agents could be particularly relevant for the agentic AI workloads that Indian IT services firms are racing to deploy for enterprise clients.

## What This Means for NRI Investors and Professionals

NVIDIA's stock rose more than 2% in pre-market trading on the Computex announcements, while AMD dropped 4%, Intel fell 6%, and Qualcomm plunged nearly 7%. For NRI investors with heavy exposure to US tech, the message is clear: the market believes NVIDIA's expansion into PCs and robotics is additive, not a distraction.

For Indian professionals in Silicon Valley's robotics and AI hardware ecosystem, the humanoid robot push creates a new category of roles: robot systems engineers, physical AI researchers, simulation specialists, and safety engineers. These positions combine hardware, software, and AI expertise in a way that maps well to the cross-disciplinary training many IIT and BITS graduates bring.

The question is whether India can move from being a talent exporter in robotics — sending its best researchers to Stanford and CMU — to being a robotics ecosystem builder. NVIDIA's move to standardise the robot brain, if it works, could lower the barrier to entry for Indian robotics companies the same way the ARM architecture lowered it for Indian mobile chip designers.

Jensen Huang's leather jacket is getting heavier. The bets are getting bigger. And for the Indian tech diaspora, the surface area of opportunity just expanded from data centres to the physical world."""
    }
]

for art in articles:
    img = art.get("image_url", "")
    if img and not validate_image(img):
        print(f"⚠️  Image validation failed for {art['slug']}, keeping URL anyway")
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

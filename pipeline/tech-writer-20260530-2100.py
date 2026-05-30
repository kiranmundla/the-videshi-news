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
        "headline": "Dell Just Posted the Best Quarter in Its History. AI Servers Did All the Heavy Lifting.",
        "subheadline": "Record $43.8 billion in revenue, AI orders up 757 per cent, and a stock that doubled in May — the Round Rock giant is now the picks-and-shovels play of the AI buildout.",
        "slug": make_slug("dell-record-ai-server-quarter-757-percent"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Dell employs thousands of Indian engineers across Texas, Bengaluru, and Hyderabad. As AI server demand reshapes the company, Indian hardware and infrastructure talent is at the centre of the buildout — and NRI investors who bought DELL early in 2026 are sitting on a 100% gain.",
        "tags": ["dell", "ai-servers", "earnings", "nvidia", "nri-investors"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Investopedia", "url": "https://www.investopedia.com/stock-market-today-05302026-12277048"},
            {"name": "Investor's Business Daily", "url": "https://www.investors.com/news/technology/dell-stock-dell-earnings-q1-2026/"},
            {"name": "MarketWatch", "url": "https://www.marketwatch.com/story/dell-stock-surges-33-percent-ai-server-revenue/"},
            {"name": "Reuters / Freep", "url": "https://www.freep.com/story/money/markets/2026/05/30/inflation-ai-rally-iran-deal/"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/5480781/pexels-photo-5480781.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "body": """The last time Dell Technologies delivered a quarter this dominant, Michael Dell was still trying to convince Wall Street that servers were a growth business. On Thursday, the company settled that argument with a sledgehammer.

Dell reported fiscal first-quarter revenue of $43.8 billion, an 88 per cent surge from a year earlier that obliterated analyst estimates of $35.7 billion. Adjusted earnings hit $4.86 per share — more than triple the year-ago figure and 64 per cent above consensus. The stock responded with a 33 per cent single-day rally on Friday, its largest ever, pushing shares to an all-time high of $429.

## The AI Engine

The numbers behind the headline are even more striking. AI-optimised server orders rocketed 757 per cent year-over-year to $16.1 billion. Dell exited the quarter with a backlog of $51.3 billion in AI hardware orders, a figure that dwarfs the entire annual revenue of most Fortune 500 technology companies.

"Demand continues to exceed supply, with memory as the primary constraint," said Chief Operating Officer Jeff Clarke. The company raised its full-year AI-server revenue guidance to $60 billion, a target that would have seemed absurd twelve months ago.

## Why the Street Went Wild

At least 15 analysts raised their price targets on Friday. JPMorgan's Samik Chatterjee moved his to $500 from $280, calling the results a report that "blew the socks off expectations." The AI buildout, which initially rewarded chip designers like Nvidia and Broadcom, is now flooding down to the companies that assemble, rack, and cool those chips — and Dell sits at the top of that supply chain.

The broader market took notice. Hewlett Packard Enterprise climbed 12.6 per cent to an all-time high. Super Micro Computer surged 11.6 per cent. IBM leaped 12.7 per cent. The AI trade is no longer just a semiconductor story.

## The Diaspora Angle

Dell's India operations span Bengaluru, Hyderabad, and Chennai, employing thousands of engineers across server design, cloud infrastructure, and enterprise services. As the company pivots from PCs to AI infrastructure, those roles are shifting too — from legacy hardware support to AI rack architecture, thermal engineering for GPU-dense systems, and software-defined networking.

For NRI investors who bought Dell stock earlier this year, the ride has been extraordinary: shares have more than doubled in May alone, posting a monthly gain of over 100 per cent. The company now trades at roughly 22 times forward earnings, a premium to its historical average but one that analysts say is justified by the AI backlog's visibility.

## What Comes Next

Dell guided fiscal Q2 revenue to $44.5 billion, another 49 per cent year-over-year increase, with earnings expected to more than double. The constraining factor is not demand but supply — specifically, high-bandwidth memory chips from Micron and SK Hynix that power Nvidia's AI accelerators.

The AI infrastructure buildout is entering a phase where the winners are not just the chip architects but the systems integrators who can deliver fully assembled, liquid-cooled AI racks at scale. Dell, with its $51 billion backlog and deep enterprise relationships, has positioned itself as the default partner for that job. For the tens of thousands of Indian engineers who build, test, and ship those systems, the company's transformation is not an abstraction — it is the daily work."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Sridhar Ramaswamy's Snowflake Just Landed a $6 Billion AWS Deal. The Stock Surged 37 Per Cent.",
        "subheadline": "The IIT Madras alumnus turned Snowflake CEO delivered the company's strongest quarter in years, ending the 'SaaSpocalypse' narrative for data platforms.",
        "slug": make_slug("sridhar-ramaswamy-snowflake-6-billion-aws-deal"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Sridhar Ramaswamy, an IIT Madras graduate who spent two decades at Google before leading Snowflake, is the latest Indian-origin CEO to deliver a market-defining quarter. Indian data engineers at companies using Snowflake — from JPMorgan to Walmart — are seeing their platform of choice become the default AI data layer.",
        "tags": ["snowflake", "sridhar-ramaswamy", "aws", "cloud", "indian-ceo", "ai"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/snowflake-jumps-aws-deal-upbeat-forecast-2026-05-29/"},
            {"name": "Wall Street Journal", "url": "https://www.wsj.com/tech/snowflake-stock-rally-ai-era-software/"},
            {"name": "Investopedia", "url": "https://www.investopedia.com/snowflake-stock-pops-40-percent-ai-12276834"},
            {"name": "Snowflake Earnings Release", "url": "https://www.snowflake.com/en/news/snowflake-reports-q1-fiscal-2027/"}
        ]),
        "score_total": 80,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/d/d7/2020588_Sridhar_Ramaswamy_38.jpg",
        "body": """For much of 2026, Wall Street had all but written off the enterprise software sector. The narrative was clean and cruel: AI would eat software. Subscription platforms were relics. The "SaaSpocalypse," as traders dubbed the rolling selloff that erased roughly $2 trillion from software valuations, seemed to have permanent victims.

Then Sridhar Ramaswamy's Snowflake reported earnings on Wednesday evening, and the narrative collapsed.

## The Numbers

Snowflake delivered first-quarter revenue that beat estimates, raised its full-year guidance, and announced a landmark $6 billion, five-year deal with Amazon Web Services. Shares surged 37 per cent on Thursday — the stock's best single day in history — erasing every loss accumulated since January.

The AWS agreement gives Snowflake guaranteed access to Amazon's Graviton chips at a time when compute capacity is severely constrained by the AI boom. More importantly, it deepens Snowflake's integration across AI workloads on AWS infrastructure, locking in the platform as the default data layer for enterprises scaling their AI deployments.

"AI is acting as a catalyst for customers to move to Snowflake with increasing urgency," wrote Gil Luria, head of technology research at D.A. Davidson, who raised his price target to $300.

## Ramaswamy's Quiet Revolution

Sridhar Ramaswamy grew up in India, graduated from IIT Madras, earned his PhD in computer science from Brown University, and spent twenty years at Google, where he ran the advertising business — the engine that generates over 80 per cent of Alphabet's revenue. When he took over as Snowflake CEO in early 2024, replacing the legendary Frank Slootman, the company was struggling to define its role in the AI era.

Ramaswamy bet that the real bottleneck in AI adoption was not compute power or model architecture but data management — the messy, unglamorous work of organising, governing, and serving the petabytes of enterprise data that AI models need to be useful. He embedded AI tools directly into Snowflake's platform: Cortex Code for building generative AI applications, Snowpark for deploying machine learning models, and Snowflake Intelligence, an AI agent that helps business users query data in natural language.

The results are now visible. Accounts using Snowflake Intelligence more than doubled quarter-over-quarter. AI-related usage is accelerating across the platform. William Blair analysts called it "a clear inflection for AI adoption."

## What This Means for the Indian Tech Workforce

Snowflake is one of the largest employers of Indian-origin data engineers in Silicon Valley, and its platform is deeply embedded in the data stacks of companies — JPMorgan, Capital One, Walmart, Pfizer — that collectively employ hundreds of thousands of Indian tech workers on H-1B and L-1 visas.

As Snowflake's AI tools gain traction, the job descriptions are changing. The traditional data engineer who wrote SQL queries and managed ETL pipelines is being supplemented by AI data engineers who build retrieval-augmented generation pipelines, fine-tune models on proprietary data, and govern AI-generated outputs. For Indian professionals who dominate the data engineering talent pool in the United States, this shift represents both an opportunity and a mandate to upskill.

Ramaswamy's success also extends a pattern that has become impossible to ignore. Three of the four most valuable data platform companies — Google (Pichai), Microsoft (Nadella), and now Snowflake (Ramaswamy) — are led by Indian-origin executives. The fourth, Amazon, was founded by Bezos but counts an enormous Indian engineering leadership bench. In the AI era, the data layer is where the real value accrues, and Indian technologists are running the show.

## The Market Signal

The Snowflake rally was not an isolated event. Datadog surged 68 per cent in May. MongoDB jumped 9.6 per cent on Thursday alone. The SaaSpocalypse thesis — that AI would render subscription software obsolete — is being revised in real time. The emerging consensus: platforms that sit at the intersection of data and AI are not victims of the revolution but its primary beneficiaries.

For NRI investors who sold software stocks during the panic, the lesson is expensive but clarifying: in a technology cycle defined by AI, the companies that control the data pipeline may matter more than the companies that build the models."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Shantanu Narayen Built a $250 Billion Empire at Adobe. Now He's Handing Over the Keys — and a New AI Assistant.",
        "subheadline": "Adobe's Firefly AI Assistant enters public beta as the company searches for a successor to its longest-serving Indian-origin CEO. The legacy and the question mark, in one quarter.",
        "slug": make_slug("shantanu-narayen-adobe-firefly-ai-assistant-successor"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Shantanu Narayen's 18-year run as Adobe CEO — transforming a boxed-software company into a cloud and AI giant — is one of the defining Indian-origin leadership stories in American tech. His succession, and whether Adobe picks another Indian-origin leader or an external AI-first candidate, will be closely watched by the diaspora.",
        "tags": ["adobe", "shantanu-narayen", "firefly", "ai-assistant", "indian-ceo", "creative-ai"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Adobe Press Release / BusinessWire", "url": "https://www.businesswire.com/news/home/20260415853653/en/"},
            {"name": "Sahm Capital", "url": "https://sahmcapital.com/adobes-ai-moment-nvidia-ceo-says-the-opportunity-just-skyrocketed/"},
            {"name": "FinancialContent / Markets", "url": "https://markets.financialcontent.com/postgazette/article/adobe-at-a-crossroads-ceo-shantanu-narayen-to-step-down/"},
            {"name": "Owler / TechnoBugg", "url": "https://www.owler.com/reports/adobe"}
        ]),
        "score_total": 72,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/0/01/Shantanu_Narayen_-_the_CEO_of_Adobe_Inc.jpg",
        "body": """Adobe's Firefly AI Assistant entered public beta this week, and the timing tells you everything about where the company stands. The product is the most ambitious AI launch in Adobe's history — a single conversational interface that orchestrates multi-step creative workflows across Photoshop, Premiere, Lightroom, Illustrator, and more. And the man who bet the company on this direction, CEO Shantanu Narayen, is preparing to step aside.

## The Last Act

Narayen announced in March that he would transition from CEO to Chairman of the Board, ending an 18-year tenure that ranks among the most transformative in enterprise software history. When he took over in 2007, Adobe sold shrink-wrapped boxes of Photoshop. By the time he leaves, the company will generate over $26 billion in annual revenue, nearly all of it from cloud subscriptions, with AI embedded in every major product.

The numbers alone justify the accolade. But the strategic decisions are what set Narayen apart. The 2011 pivot to Creative Cloud — a subscription model that Wall Street initially punished — grew Adobe's valuation by more than tenfold. The development of Firefly, trained exclusively on licensed content, gave Adobe a unique competitive moat in an AI landscape plagued by copyright lawsuits. And the decision to kill the $20 billion Figma acquisition in 2023, forced by regulators, freed up resources that Narayen redirected into agentic AI development.

"No company, no CEO has ever made a greater contribution to how the world tells stories than Adobe," Nvidia CEO Jensen Huang said at Adobe Summit earlier this year. He estimated Adobe's addressable opportunity had expanded "100 to 1,000 times" with AI.

## Firefly AI Assistant: The Product

The new Firefly AI Assistant is not a chatbot bolted onto existing tools. It is an agentic system — powered by what Adobe calls its "creative agent" — that can interpret natural language instructions and execute complex, multi-step creative workflows without requiring the user to switch between applications.

A designer can describe a desired outcome in plain English, and the assistant will orchestrate the right tools: generating an image in Firefly, refining it in Photoshop, colour-grading it in Lightroom, and compositing it into a video in Premiere. Adobe frames this as "agentic creativity" — the creator provides vision and judgment; the assistant handles orchestration and execution.

For the millions of Indian-origin graphic designers, video editors, UX professionals, and content creators who rely on Adobe's tools daily, this is a productivity leap that could redefine workflows. India is one of Adobe's largest markets by user count, and the creative freelancing economy — concentrated in cities like Bengaluru, Pune, Mumbai, and Hyderabad — runs almost entirely on the Creative Cloud stack.

## The Succession Question

The search for Narayen's replacement is being led by Lead Independent Director Frank Calderoni. Inside Adobe, the frontrunner is widely considered to be David Wadhwani, President of Digital Media and the public face of Adobe's AI integration strategy. Another strong internal candidate is Anil Chakravarthy, President of Customer Experience Orchestration, who represents the enterprise side of the business.

Industry observers note that the board is also evaluating external candidates — specifically "AI-first" leaders from companies like Google or OpenAI — who might push Adobe toward a more radical reinvention. The choice will signal whether Adobe sees itself as a creative tools company enhanced by AI, or an AI company that happens to make creative tools.

For the Indian-American tech community, the succession carries symbolic weight. Narayen, a Hyderabad native who studied at Osmania University and later earned an MBA from UC Berkeley, is part of the generation of Indian-origin executives — alongside Satya Nadella at Microsoft, Sundar Pichai at Alphabet, and Sanjay Mehrotra at Micron — who redefined what leadership in American technology looks like. Whether his successor continues that lineage will be watched closely.

## The Competitive Landscape

Adobe is not the only company chasing agentic creativity. Canva, armed with AI tools and a simpler interface, is rapidly gaining enterprise market share. Generative AI startups like Midjourney and Runway are eating into Adobe's creative monopoly from below. And the FTC lawsuit over Adobe's cancellation policies, which survived a motion to dismiss in 2025, adds regulatory risk to the transition.

But Narayen's final strategic gift to Adobe may prove durable: by training Firefly exclusively on licensed content, he has made Adobe the only commercially safe generative AI platform for large enterprises terrified of copyright litigation. In a world where a single AI-generated image can trigger a lawsuit, that safety guarantee is worth more than any feature.

The question now is whether Narayen's successor can build on that foundation as aggressively as he built it. The Firefly AI Assistant suggests the tools are ready. The leadership question remains open."""
    },
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
